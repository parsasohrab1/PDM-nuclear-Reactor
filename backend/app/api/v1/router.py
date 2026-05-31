from fastapi import APIRouter

from backend.app.api.v1 import alerts, data, model, predict

api_router = APIRouter()
api_router.include_router(predict.router, tags=["predict"])
api_router.include_router(alerts.router, tags=["alerts"])
api_router.include_router(model.router, tags=["model"])
api_router.include_router(data.router, tags=["data"])
