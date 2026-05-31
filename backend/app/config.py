from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = "PdM-Nuclear"
    app_env: str = "development"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    secret_key: str = "change-me"
    aes_encryption_key: str = "change-me-32-byte-key-for-aes256!!"

    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    influxdb_url: str = "http://localhost:8086"
    influxdb_token: str = "pdm-nuclear-dev-token"
    influxdb_org: str = "pdm-nuclear"
    influxdb_bucket: str = "sensor_data"
    influxdb_retention: str = "90d"

    anomaly_threshold_k: float = 3.0
    threshold_update_interval_hours: int = 24
    lstm_input_size: int = 64
    lstm_encoder_layers: str = "32,16"
    lstm_decoder_layers: str = "32,64"
    model_path: str = "data/models/lstm_autoencoder.h5"

    window_neutron_flux: int = 10
    window_temperature: int = 3600

    opcua_endpoint: str = "opc.tcp://localhost:4840"
    modbus_host: str = "localhost"
    modbus_port: int = 502

    backup_interval_hours: int = 24
    backup_path: str = "data/backups"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def encoder_layer_sizes(self) -> list[int]:
        return [int(x.strip()) for x in self.lstm_encoder_layers.split(",")]

    @property
    def decoder_layer_sizes(self) -> list[int]:
        return [int(x.strip()) for x in self.lstm_decoder_layers.split(",")]

    @property
    def project_root(self) -> Path:
        return Path(__file__).resolve().parents[2]


@lru_cache
def get_settings() -> Settings:
    return Settings()
