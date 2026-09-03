import pathlib
from time import sleep
from wolf.app.resolvers import RouteResolver
from wolf.app import Application
from ZODB.FileStorage import FileStorage
from ZODB import Connection, DB
from wolf.app.render import html
from . import middleware


HERE = pathlib.Path(__file__).parent.resolve()


app = Application(
    resolver=RouteResolver(),
    middlewares=(
        middleware.TransactionMiddleware(),
    )
)

app.use(
    middleware.ZODB(db=DB(
        FileStorage(str(HERE / "example.fs"))
    )),
)


@app.resolver.router.register('/')
@html
def long_task(request):
    print("sleeping")
    sleep(5)
    conn = request.get(Connection)
    print(f'Now i have an active connection {conn}')
    return """<html>
  <head>
    <link rel="icon"
    href="https://zany.sh/favicon.svg?text=zodb" />
  </head>
  <body>Task done.</body>
</html>"""
