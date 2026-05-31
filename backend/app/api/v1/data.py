from fastapi import APIRouter, Depends

from backend.app.config import Settings, get_settings
from backend.app.schemas.detection import GenerateDataRequest, GenerateDataResponse
from backend.app.services.data_generator import SyntheticDataGenerator

router = APIRouter()


@router.post("/data/generate", response_model=GenerateDataResponse)
async def generate_synthetic_data(
    payload: GenerateDataRequest,
    settings: Settings = Depends(get_settings),
) -> GenerateDataResponse:
    """Generate synthetic reactor sensor data with optional anomaly injection (FR-01..FR-05)."""
    generator = SyntheticDataGenerator(settings)
    result = generator.generate(
        duration_days=payload.duration_days,
        frequency_hz=payload.frequency_hz,
        inject_anomalies=payload.inject_anomalies,
        output_filename=payload.output_filename,
    )
    return GenerateDataResponse(**result)
