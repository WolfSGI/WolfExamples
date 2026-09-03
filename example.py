from minicli import cli, run
from waitress import serve


@cli
def routing(host: str="0.0.0.0", port: int=8000):
    from routing.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def traject(host: str="0.0.0.0", port: int=8000):
    from traject.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def zodb(host: str="0.0.0.0", port: int=8000):
    from zodb.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def zodb_async(host: str="0.0.0.0", port: int=8000):
    from zodb_async.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def graphql(host: str="0.0.0.0", port: int=8000):
    from gql.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def upload(host: str="0.0.0.0", port: int=8000):
    from fileupload.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def all(host: str="0.0.0.0", port: int=8000):
    from wolf.app.nodes import Mapping
    from routing.app import app as routing_app
    from fileupload.app import app as upload_app
    from gql.app import app as graphql_app
    from zodb.app import app as zodb_app
    from traject.app import app as traject_app

    app = Mapping({
        "/routing": routing_app,
        "/upload": upload_app,
        "/graphql": graphql_app,
        "/traject": traject_app,
        "zodb": zodb_app,
    })

    for subapp in app.values():
        subapp.events.lifecycle.on_init.send('startup')

    serve(app, listen=f"{host}:{port}")


if __name__ == '__main__':
    run()
