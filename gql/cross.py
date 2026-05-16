from cross_web.request._base import FormData, SyncHTTPRequestAdapter
from wolf.abc.resolvers import Params


class WolfHTTPRequestAdapter(SyncHTTPRequestAdapter):

    def __init__(self, request) -> None:
        self.request = request

    @property
    def query_params(self):
        return self.request.query

    @property
    def path_params(self):
        return self.request.get(Params, default={})

    @property
    def body(self):
        breakpoint()
        return self.request.environ['wsgi.input'].read()

    @property
    def method(self):
        return self.request.method

    @property
    def headers(self):
        return self.request.environ

    @property
    def post_data(self):
        return self.request.data.form

    @property
    def files(self):
        return self.request.data.form

    def get_form_data(self) -> FormData:
        return FormData(
            files=self.request.data.form,
            form=self.request.data.form,
        )

    @property
    def content_type(self):
        return self.request.content_type

    @property
    def url(self) -> str:
        return self.request.uri()

    @property
    def cookies(self):
        return {
            name: str(cookie)
            for name, cookie in self.request.cookies.items()
        }
