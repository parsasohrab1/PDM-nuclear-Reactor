from datetime import datetime

from pydantic import BaseModel, Field


class SensorReading(BaseModel):
    timestamp: datetime
    temp_c: float = Field(..., ge=250, le=350, description="Core temperature (°C)")
    pressure_bar: float = Field(..., ge=140, le=160, description="Coolant pressure (bar)")
    neutron_flux: int = Field(..., ge=800, le=1200, description="Neutron flux (relative units)")
    vibration_ms2: float = Field(..., ge=0.1, le=2.0, description="Vibration acceleration (m/s²)")


class PredictRequest(BaseModel):
    window: list[SensorReading] = Field(..., min_length=1)


class PredictResponse(BaseModel):
    anomaly_label: int = Field(..., description="0=normal, 1=anomaly")
    reconstruction_error: float
    confidence_score: float = Field(..., ge=0, le=100)
    probable_cause: str | None = None
    affected_sensors: list[str] = Field(default_factory=list)


class AlertRecord(BaseModel):
    id: str
    timestamp: datetime
    anomaly_label: int
    reconstruction_error: float
    confidence_score: float
    probable_cause: str | None = None
    affected_sensors: list[str] = Field(default_factory=list)


class AlertsResponse(BaseModel):
    alerts: list[AlertRecord]
    total: int


class RetrainRequest(BaseModel):
    data_path: str | None = Field(None, description="Path to CSV training data")
    epochs: int = Field(50, ge=1, le=500)


class RetrainResponse(BaseModel):
    status: str
    message: str
    model_path: str | None = None


class GenerateDataRequest(BaseModel):
    duration_days: int = Field(30, ge=1, le=365)
    frequency_hz: float = Field(1.0, ge=0.1, le=10.0)
    inject_anomalies: bool = True
    output_filename: str = "nuclear_reactor_synthetic_data.csv"


class GenerateDataResponse(BaseModel):
    status: str
    records: int
    anomaly_rate: float
    output_path: str
