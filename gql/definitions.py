import strawberry
from sqlmodel import Session, select
from . import models


@strawberry.type
class Person:
    id: int
    email: str
    name: str | None
    age: int

    instance: strawberry.Private[models.Person]

    @strawberry.field
    def documents(self) -> list["Document"]:
        return [Document.from_instance(doc) for doc in self.instance.documents]

    @classmethod
    def from_instance(cls, instance: models.Person):
        return cls(
            id=instance.id,
            email=instance.email,
            name=instance.name,
            age=instance.age,
            instance=instance
        )


@strawberry.type
class Document:
    id: int
    title: str
    text: str
    category: str

    instance: strawberry.Private[models.Document]

    @strawberry.field
    def author(self) -> Person:
        return Person.from_instance(self.instance.author)

    @classmethod
    def from_instance(cls, instance: models.Document):
        return cls(
            id=instance.id,
            title=instance.title,
            text=instance.text,
            category=instance.category,
            instance=instance,
        )


@strawberry.type
class AuthorQuery:

    @strawberry.field
    def authors(self, info: strawberry.Info) -> list[Person]:
        request = info.context["request"]
        sqlsession = request.get(Session)
        statement = select(models.Person)
        authors = sqlsession.exec(statement).all()
        return [Person.from_instance(author) for author in authors]


@strawberry.type
class AuthorMutation:

    @strawberry.mutation
    def add_author(
            self, info: strawberry.Info, email: str, name: str | None, age: int
    ) -> Person:
        request = info.context["request"]
        sqlsession = request.get(Session)
        author = models.Person(
            name=name,
            email=email,
            age=age
        )
        sqlsession.add(author)
        sqlsession.commit()
        sqlsession.refresh(author)
        return Person.from_instance(author)


@strawberry.type
class DocumentQuery:

    @strawberry.field
    def documents(
            self, info: strawberry.Info, category: str | None
    ) -> list[Document]:
        request = info.context["request"]
        sqlsession = request.get(Session)
        statement = select(models.Document)
        if category:
            statement = statement.filter(models.Document.category==category)
        documents = sqlsession.exec(statement).all()
        return [Document.from_instance(doc) for doc in documents]


@strawberry.type
class DocumentMutation:

    @strawberry.mutation
    def add_document(
            self, info: strawberry.Info,
            author_id: int,
            title: str,
            text: str,
            category: str
    ) -> Document:
        request = info.context["request"]
        sqlsession = request.get(Session)
        document = models.Document(
            author_id=author_id,
            title=title,
            text=text,
            category=category
        )
        sqlsession.add(document)
        sqlsession.commit()
        sqlsession.refresh(document)
        return Document.from_instance(document)
