from fastapi import APIRouter, Depends, Request

from backend.app.schemas.detection import PredictRequest, PredictResponse
from backend.app.services.anomaly_engine import AnomalyEngine, get_anomaly_engine

router = APIRouter()


@router.post("/predict", response_model=PredictResponse)
async def predict(
    payload: PredictRequest,
    request: Request,
    engine: AnomalyEngine = Depends(get_anomaly_engine),
) -> PredictResponse:
    """Receive a data window and return anomaly detection result (FR-10..FR-15)."""
    result = await engine.predict(payload.window)

    if result.anomaly_label == 1 and hasattr(request.app.state, "influx"):
        await request.app.state.influx.write_alert(result)

    return result
