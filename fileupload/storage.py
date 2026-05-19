import tempfile
import uuid
import orjson
import sfdb
from typing import BinaryIO, Iterator, Iterable
from contextlib import contextmanager
from pathlib import Path
from ticketed_filestore.meta import FileInfo
from ticketed_filestore.fs import BushyStorage, FlatStorage
from wolf.app.pluggability import Installable


class Storage(BushyStorage):

    def __init__(self, namespace: str, root: Path, algorithm='md5'):
        root.mkdir(mode=0o755, parents=True, exist_ok=True)
        self.db = sfdb.Database(filename=root / 'store.db')
        super().__init__(namespace, root, algorithm=algorithm)

    def store(
            self,
            data: BinaryIO | Iterable[bytes],
            ticket: str | None = None,
            **metadata
    ) -> FileInfo:
        fileinfo = super().store(data, ticket=ticket, **metadata)
        self.db[ticket] = fileinfo.metadata
        return fileinfo

    def delete(self, ticket: str):
        result = super().delete(ticket)
        del self.db[ticket]
        return result

    def __iter__(self):
        yield from self.db

    def get_info(self, ticket: str):
        return self.db[ticket]


class Uploader(dict[Path, dict]):

    def __init__(self, path: Path, storage: Storage):
        self._path = path
        self.storage = storage
        super().__init__()

    def upload(self, binary: BinaryIO, **metadata):
        uid = self.storage.new_ticket()
        path = self._path / uid
        self[uid] = metadata
        with path.open('wb+') as target:
            for block in iter(lambda: binary.read(4096), b""):
                size = target.write(block)
        return uid

    def persist(self):
        for uid, metadata in self.items():
            path = self._path / uid
            with path.open('rb') as target:
                self.storage.store(target, ticket=uid, **metadata)


class StorageService(Installable):

    def __init__(self, storage: Storage):
        self.storage = storage

    def install(self, application):
        application.services.register_value(Storage, self.storage)
        application.services.register_factory(Uploader, self.uploader)

    @contextmanager
    def uploader(self) -> Iterator[Storage]:
        with tempfile.TemporaryDirectory() as tmpdirname:
            uploader = Uploader(Path(tmpdirname), self.storage)
            try:
                yield uploader
            except Exception:
                # maybe log.
                raise
            else:
                uploader.persist()
            finally:
                uploader.clear()
