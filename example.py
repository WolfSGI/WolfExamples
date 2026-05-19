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
def graphql(host: str="0.0.0.0", port: int=8000):
    from gql.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


@cli
def upload(host: str="0.0.0.0", port: int=8000):
    from fileupload.app import app
    app.events.lifecycle.on_init.send('startup')
    serve(app, listen=f"{host}:{port}")


if __name__ == '__main__':
    run()
