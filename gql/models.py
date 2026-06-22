from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.orm import registry


sql_registry = registry()


class GQLModel(SQLModel, registry=sql_registry):
    pass


class Person(GQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    name: str | None = None
    age: int
    documents: list["Document"] = Relationship(back_populates="author")


class Document(GQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    text: str
    category: str
    author_id: int = Field(foreign_key="person.id")
    author: Person = Relationship(back_populates="documents")
