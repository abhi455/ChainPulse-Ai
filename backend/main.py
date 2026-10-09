from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.sessions import SessionMiddleware

from backend.api.middleware import RequestIDMiddleware
from backend.api.routes import (
    ai_router,
    auth_router,
    decisions_router,
    demand_router,
    forecasting_router,
    intelligence_router,
    inventory_router,
    organizations_router,
    products_router,
    simulations_router,
    suppliers_router,
)
from backend.api.routes.bullwhip import router as bullwhip_router
from backend.api.routes.dashboard import router as dashboard_router
from backend.api.routes.data_connections import router as data_connections_router
from backend.api.routes.connection_metadata import router as connection_metadata_router
from backend.api.routes.ingestion import router as ingestion_router
from backend.api.routes.uploads import router as uploads_router
from backend.api.routes.data_import import router as data_import_router
from backend.api.routes.risk import router as risk_router
from backend.api.routes.reports import router as reports_router
from backend.api.routes.pipeline import router as pipeline_router
from backend.api.routes.canonical_import import router as canonical_import_router
from config.settings import APP_ENV, APP_NAME, APP_VERSION

import os
from backend.api.routes.auth_oauth import router as oauth_router


app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
    description="ChainPulse AI supply-chain intelligence platform",
    docs_url="/docs",
    redoc_url="/redoc",
)



app.add_middleware(RequestIDMiddleware)

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "CHAINPULSE_SESSION_SECRET",
        "change-this-session-secret-in-production",
    ),
    https_only=APP_ENV == "production",
    same_site="lax",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["System"])
def root():
    return {
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
        "status": "running",
    }


@app.get("/api/v1/health", tags=["System"])
def health():
    return {
        "status": "healthy",
        "application": APP_NAME,
        "version": APP_VERSION,
        "environment": APP_ENV,
    }


@app.exception_handler(Exception)
async def global_exception_handler(
    request: Request,
    exc: Exception,
):
    request_id = getattr(
        request.state,
        "request_id",
        None,
    )

    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "type":
                    "internal_server_error",
                "message":
                    "An unexpected server error occurred.",
                "request_id":
                    request_id,
            }
        },
    )


app.include_router(
    ai_router,
    prefix="/api/v1",
)

app.include_router(
    auth_router,
    prefix="/api/v1",
)

app.include_router(
    oauth_router,
    prefix="/api/v1",
)

app.include_router(
    bullwhip_router,
    prefix="/api/v1",
)

app.include_router(
    dashboard_router,
    prefix="/api/v1",
)

app.include_router(
    decisions_router,
    prefix="/api/v1",
)

app.include_router(
    demand_router,
    prefix="/api/v1",
)

app.include_router(
    forecasting_router,
    prefix="/api/v1",
)

app.include_router(
    intelligence_router,
    prefix="/api/v1",
)

app.include_router(
    inventory_router,
    prefix="/api/v1",
)

app.include_router(
    organizations_router,
    prefix="/api/v1",
)

app.include_router(
    products_router,
    prefix="/api/v1",
)

app.include_router(
    risk_router,
    prefix="/api/v1",
)

app.include_router(
    simulations_router,
    prefix="/api/v1",
)

app.include_router(
    suppliers_router,
    prefix="/api/v1",
)


app.include_router(data_connections_router, prefix="/api/v1")




app.include_router(ingestion_router, prefix="/api/v1")



app.include_router(uploads_router, prefix="/api/v1")


app.include_router(data_import_router, prefix="/api/v1")


app.include_router(connection_metadata_router, prefix="/api/v1")


app.include_router(reports_router, prefix="/api/v1")
app.include_router(pipeline_router, prefix="/api/v1")
app.include_router(canonical_import_router, prefix="/api/v1")

# =====================================================
# =====================================================
