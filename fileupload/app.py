import pathlib
import structlog
from wolf.app import Application
from wolf.app.resolvers import RouteResolver
from wolf.app.services.resources import ResourceManager
from .views import router, library
from .storage import StorageService, Storage


logger = structlog.get_logger("example.upload")

# HELPER
HERE = pathlib.Path(__file__).parent.resolve()

# Application
app = Application(
    resolver=RouteResolver(router=router),
)

libraries = ResourceManager('/static')
libraries.add_library(library)


# Install all the services
app.use(
    libraries,
    StorageService(
        Storage('example', HERE / "uploads")
    ),
)
