from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.api.v1.router import api_router
from backend.app.config import get_settings
from backend.app.services.influxdb import InfluxDBService


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    influx = InfluxDBService(settings)
    await influx.connect()
    app.state.influx = influx
    yield
    await influx.close()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        description="Predictive Maintenance for Nuclear Reactor - Anomaly Detection API",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router, prefix="/api/v1")

    @app.get("/health", tags=["health"])
    async def health_check():
        return {"status": "ok", "service": settings.app_name}

    return app


app = create_app()
