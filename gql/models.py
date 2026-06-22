from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy.orm import registry


sql_registry = registry()


class Person(SQLModel, table=True, registry=sql_registry):
    id: int | None = Field(default=None, primary_key=True)
    email: str = Field(unique=True)
    name: str | None = None
    age: int
    documents: list["Document"] = Relationship(back_populates="author")


class Document(SQLModel, table=True, registry=sql_registry):
    id: int | None = Field(default=None, primary_key=True)
    title: str
    text: str
    category: str
    author_id: int = Field(foreign_key="person.id")
    author: Person = Relationship(back_populates="documents")
