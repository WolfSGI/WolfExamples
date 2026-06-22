import pathlib
import structlog
from wolf.app import Application
from wolf.app.resolvers import RouteResolver
from wolf_sql import SQLDatabase
from .views import router
from .models import sql_registry


logger = structlog.get_logger("example.graphql")

# HELPER
HERE = pathlib.Path(__file__).parent.resolve()


app = Application(
    resolver=RouteResolver(router=router),
)

app.use(
    SQLDatabase(
        url=f"sqlite:///{HERE / 'database.db'}",
        echo=True,
        registries=[sql_registry]
    ),
)
