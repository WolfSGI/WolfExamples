import pathlib
import vernacular
import http_session_file

import structlog
from redis import Redis
from rq import Queue

from wolf.app import Application
from wolf.app.middlewares import HTTPSession, NoAnonymous
from wolf.app.resolvers import RouteResolver
from wolf.app.services.auth import SessionAuthenticator
from wolf.app.services.flash import Flash
from wolf.app.services.post import PostOffice
from wolf.app.services.resources import ResourceManager
from wolf.app.services.translation import TranslationService
from html_resources.resources import JSResource, CSSResource
from html_resources.store import Filestore, Repository
from wolf.rendering.templates import Templates
from wolf.rendering.ui import UI
from wolf_sql import SQLDatabase

from . import register, login, views, actions, ui, folder, document, db, models  # noqa


logger = structlog.get_logger("example.routing")

# COMPILE PO FILES
vernacular.COMPILE = True

# HELPER
HERE = pathlib.Path(__file__).parent.resolve()


#### CONFIG OF THE APP
database_source = db.DBSource(
    title="SQL source",
    description="SQL users",
    actions=(db.Login, db.Fetch),
    usertype=models.Person
)


libraries = Repository()
libraries.add(
    Filestore.from_package_directory(
        'deform:static',
        'deform:static'
    )
)
libraries.add(
    Filestore.from_discovery(
        'example',
        HERE / 'static',
        restrict=('*.jpg', '*.ico')
    )
)

app = Application(
    resolver=RouteResolver(),
    middlewares=(
        HTTPSession(
            store=http_session_file.FileStore(
                HERE / 'sessions', 3000
            ),
            secret="secret",
            salt="salt",
            cookie_name="cookie_name",
            secure=False,
            TTL=3000
        ),
        NoAnonymous(
            login_url='/login',
            allowed_urls={'/register', '/test'}
        )
    )
)

app.use(
    ResourceManager(libraries, '/static'),
    PostOffice(
        path=HERE / 'test.mail'
    ),
    TranslationService.from_paths(
        paths=[HERE / 'translations'],
        default_domain="routing",
        accepted_languages=["fr", "en", "de"]
    ),
    UI(
        slots=ui.slots,
        subslots=ui.subslots,
        layouts=ui.layouts,
        templates=Templates('templates'),
        resources={
            CSSResource(
                "/bootstrap@5.0.2/dist/css/bootstrap.min.css",
                root="https://cdn.jsdelivr.net/npm",
                integrity="sha384-EVSTQN3/azprG1Anm3QDgpJLIm9Nao0Yz1ztcQTwFspd3yD65VohhpuuCOmLASjC",  # noqa
                crossorigin="anonymous"
            ),
            CSSResource(
                "/bootstrap-icons@1.11.1/font/bootstrap-icons.css",
                root="https://cdn.jsdelivr.net/npm",
                integrity="sha384-4LISF5TTJX/fLmGSxO53rV4miRxdg84mZsxmO8Rx5jGtp/LbrixFETvWa5a6sESd",  # noqa
                crossorigin="anonymous"
            ),
            JSResource(
                "/bootstrap@5.0.2/dist/js/bootstrap.bundle.min.js",
                root="https://cdn.jsdelivr.net/npm",
                bottom=True,
                integrity="sha384-MrcW6ZMFYlzcLA8Nl+NtUVF0sA7MsXsP1UyJoMp4YLEuNSfAP+JcXn/tWtIaxVXM",  # noqa
                crossorigin="anonymous"
            ),
            JSResource(
                "/jquery-3.7.1.min.js",
                root="https://code.jquery.com",
                integrity="sha256-/JqT3SQfawRcv/BIHPThkBvs0OEvtFFmqPF/lYI/Cxo=",  # noqa
                crossorigin="anonymous"
            )
        }
    ),
    SQLDatabase(
        url=f"sqlite:///{HERE / 'database.db'}",
        echo=True,
        registries=[models.sql_registry]
    ),
    SessionAuthenticator(
        sources={
            "sql": database_source,
        },
        user_key="user"
    ),
    Flash()
)

app.resolver.router |= (
    register.routes |
    login.routes |
    views.routes |
    folder.routes |
    document.routes
)
app.services.register_value(actions.Actions, actions.actions)


# Jobs queue
q = Queue(connection=Redis())
app.services.register_value(Queue, q)


#### Example of lifecycle events
@app.events.lifecycle.on_request.connect
def echo_request(app, *, request):
    logger.info(f"Request created: {request}")


@app.events.lifecycle.on_response.connect
def echo_response(app, *, response):
    logger.info(f"Response returned: {response}")
