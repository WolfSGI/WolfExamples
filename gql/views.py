from strawberry import Schema
from wolf.abc.resolvers.routing import Router
from wolf.app import Request, Response
from .meta import GraphQLView
from .definitions import DocumentQuery, AuthorQuery, AuthorMutation


router = Router()


@router.register("/documents", methods=["GET", "POST"])
class Documents(GraphQLView):
    schema = Schema(query=DocumentQuery)

    def __call__(self, request) -> Response:
        return self.run(request=request)


@router.register("/authors", methods=["GET", "POST"])
class Authors(GraphQLView):
    schema = Schema(query=AuthorQuery, mutation=AuthorMutation)

    def __call__(self, request) -> Response:
        return self.run(request=request)
