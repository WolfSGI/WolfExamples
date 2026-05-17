from strawberry import Schema
from wolf.abc.resolvers.routing import Router
from wolf.app import Request, Response
from .meta import GraphQLView
from .definitions import (
    AuthorQuery, AuthorMutation, DocumentQuery, DocumentMutation
)


router = Router()


@router.register("/documents", methods=["GET", "POST"])
class Documents(GraphQLView):
    schema = Schema(query=DocumentQuery, mutation=DocumentMutation)


@router.register("/authors", methods=["GET", "POST"])
class Authors(GraphQLView):
    schema = Schema(query=AuthorQuery, mutation=AuthorMutation)
