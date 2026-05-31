from fastapi import APIRouter, Depends

from backend.app.schemas.detection import RetrainRequest, RetrainResponse
from backend.app.services.anomaly_engine import AnomalyEngine, get_anomaly_engine

router = APIRouter()


@router.post("/model/retrain", response_model=RetrainResponse)
async def retrain_model(
    payload: RetrainRequest,
    engine: AnomalyEngine = Depends(get_anomaly_engine),
) -> RetrainResponse:
    """Request model retraining on new data (FR-24, NFR-14)."""
    result = await engine.retrain(data_path=payload.data_path, epochs=payload.epochs)
    return result
