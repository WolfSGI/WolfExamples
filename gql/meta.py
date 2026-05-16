from typing import ClassVar
from strawberry.http import GraphQLHTTPResponse
from strawberry.http.ides import GraphQL_IDE
from strawberry.http.sync_base_view import SyncBaseHTTPView
from strawberry.http.typevars import Context, RootValue
from strawberry.schema.base import BaseSchema
from wolf.app import Request, Response
from .cross import WolfHTTPRequestAdapter


class GraphQLView(
    SyncBaseHTTPView[Request, Response, type[Response], Context, RootValue],
):
    schema: BaseSchema
    graphql_ide: GraphQL_IDE | None = "graphiql"
    allow_queries_via_get: bool = True
    multipart_uploads_enabled: bool = False
    request_adapter_class = WolfHTTPRequestAdapter

    def get_context(self, request: Request, response: Response) -> Context:
        return {"request": request, "response": response}  # type: ignore

    def get_root_value(self, request: Request) -> RootValue | None:
        return None

    def get_sub_response(self, request: Request) -> Response:
        return request.response_cls(200)

    def create_response(
        self,
        response_data: GraphQLHTTPResponse | list[GraphQLHTTPResponse],
        sub_response: type[Response],
    ) -> Response:

        return sub_response.to_json(
            200, response_data, headers={"Content-Type": "application/json"})

    def render_graphql_ide(self, request: Request) -> Response:
        return Response(200, self.graphql_ide_html)
