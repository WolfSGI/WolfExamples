import pathlib
import orjson
from collections import defaultdict
from wolf.abc.resolvers.routing import Router, APIView
from wolf.app import Application
from wolf.app.request import Request
from wolf.app.response import Response
from wolf.rendering.resources import JSResource, CSSResource
from wolf.app.services.resources import Library
from wolf.app.render import html, json, renderer
from wolf.abc.resolvers import Params
from .storage import Storage, Uploader


router = Router()
HERE = pathlib.Path(__file__).parent.resolve()


filepond_css = CSSResource(
    "/filepond.css",
    root="https://unpkg.com/filepond@^4/dist",
    crossorigin="anonymous"
)

filepond_js = JSResource(
    "/filepond.js",
    root="https://unpkg.com/filepond@^4/dist",
    crossorigin="anonymous",
    bottom=True
)

library = Library('example', HERE / "static")
upload = library.bind('upload.js', dependencies=(filepond_css, filepond_js))


@router.register('/')
class Index(APIView):

    @html(resources=(upload,))
    @renderer(template='views/index', layout_name=None)
    def GET(self, request: Request):
        storage = request.get(Storage)
        result = defaultdict(list)
        for ticket, meta in storage:
            result[meta['field']].append({
                "id": ticket,
                "name": meta.get("filename"),
                "size": meta.get("size", 0),
                "type": meta.get("content_type", "application/octet-stream"),
            })
        return {
            "existing_files_json": orjson.dumps(result)
        }

    def POST(self, request: Request):
        pass

    def PUT(self, request: Request):
        data = request.data.form
        # metadata + file
        assert len(data) == 2
        field, metadata = data[0]
        field, fileobj = data[1]
        uploader = request.get(Uploader)
        metadata = orjson.loads(metadata)
        metadata.update({
            "field": field,
            "filename": fileobj.filename,
            "content_type": fileobj.content_type.decode("utf-8")
        })
        uid = uploader.upload(fileobj, **metadata)
        return Response(200, body=uid, headers={
            "Content-Type": "text/plain; charset=utf-8"
        })

    def DELETE(self, request: Request):
        storage = request.get(Storage)
        ticket = request.query.get('ticket')
        storage.delete(ticket)
        return Response(200)
