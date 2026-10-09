from backend.connectors import ConnectorRegistry

from backend.connectors.databases import (
    SQLConnector,
    SQLiteConnector,
)

from backend.connectors.files import (
    CSVConnector,
    ExcelConnector,
    JSONConnector,
)

from backend.connectors.web import RESTConnector


ConnectorRegistry.register("csv", CSVConnector)
ConnectorRegistry.register("xlsx", ExcelConnector)
ConnectorRegistry.register("json", JSONConnector)
ConnectorRegistry.register("sql", SQLConnector)
ConnectorRegistry.register("sqlite", SQLiteConnector)
ConnectorRegistry.register("rest", RESTConnector)
