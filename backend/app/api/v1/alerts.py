from fastapi import APIRouter, Query, Request

from backend.app.schemas.detection import AlertRecord, AlertsResponse

router = APIRouter()


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    request: Request,
    limit: int = Query(100, ge=1, le=1000, description="Max alerts to return (FR-21)"),
) -> AlertsResponse:
    """Return recent alert history."""
    influx = request.app.state.influx
    alerts = await influx.get_alerts(limit=limit)
    return AlertsResponse(alerts=alerts, total=len(alerts))
