import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from backend.app.config import Settings
from backend.app.schemas.detection import AlertRecord, PredictResponse

logger = logging.getLogger(__name__)


def _import_influx():
    try:
        from influxdb_client import InfluxDBClient, Point
        from influxdb_client.client.write_api import ASYNCHRONOUS

        return InfluxDBClient, Point, ASYNCHRONOUS
    except ImportError as exc:
        raise ImportError(
            "influxdb-client is required for persistent storage. "
            "Install with: pip install influxdb-client"
        ) from exc


class InfluxDBService:
    """InfluxDB integration for time-series storage (FR-23)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self._client: Any = None
        self._write_api = None
        self._query_api = None
        self._Point = None
        self._memory_alerts: list[AlertRecord] = []

    async def connect(self) -> None:
        try:
            InfluxDBClient, Point, ASYNCHRONOUS = _import_influx()
            self._Point = Point
            self._client = InfluxDBClient(
                url=self.settings.influxdb_url,
                token=self.settings.influxdb_token,
                org=self.settings.influxdb_org,
            )
            self._write_api = self._client.write_api(write_options=ASYNCHRONOUS)
            self._query_api = self._client.query_api()
            logger.info("Connected to InfluxDB at %s", self.settings.influxdb_url)
        except ImportError as exc:
            logger.warning("InfluxDB client not installed, using in-memory fallback: %s", exc)
            self._client = None
        except Exception as exc:
            logger.warning("InfluxDB unavailable, using in-memory fallback: %s", exc)
            self._client = None

    async def close(self) -> None:
        if self._client:
            self._client.close()

    async def write_sensor_reading(
        self,
        temp_c: float,
        pressure_bar: float,
        neutron_flux: int,
        vibration_ms2: float,
        label: int = 0,
    ) -> None:
        if not self._write_api or not self._Point:
            return

        point = (
            self._Point("sensor_readings")
            .tag("source", "synthetic")
            .field("temp_c", temp_c)
            .field("pressure_bar", pressure_bar)
            .field("neutron_flux", float(neutron_flux))
            .field("vibration_ms2", vibration_ms2)
            .field("label", label)
            .time(datetime.now(timezone.utc))
        )
        self._write_api.write(
            bucket=self.settings.influxdb_bucket,
            org=self.settings.influxdb_org,
            record=point,
        )

    async def write_alert(self, result: PredictResponse) -> None:
        alert = AlertRecord(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(timezone.utc),
            anomaly_label=result.anomaly_label,
            reconstruction_error=result.reconstruction_error,
            confidence_score=result.confidence_score,
            probable_cause=result.probable_cause,
            affected_sensors=result.affected_sensors,
        )
        self._memory_alerts.insert(0, alert)
        self._memory_alerts = self._memory_alerts[:1000]

        if not self._write_api or not self._Point:
            return

        point = (
            self._Point("alerts")
            .tag("severity", "critical" if result.anomaly_label == 1 else "info")
            .field("anomaly_label", result.anomaly_label)
            .field("reconstruction_error", result.reconstruction_error)
            .field("confidence_score", result.confidence_score)
            .field("probable_cause", result.probable_cause or "")
            .field("affected_sensors", ",".join(result.affected_sensors))
            .time(alert.timestamp)
        )
        self._write_api.write(
            bucket=self.settings.influxdb_bucket,
            org=self.settings.influxdb_org,
            record=point,
        )

    async def get_alerts(self, limit: int = 100) -> list[AlertRecord]:
        if self._query_api and self._client:
            try:
                query = f'''
                from(bucket: "{self.settings.influxdb_bucket}")
                  |> range(start: -30d)
                  |> filter(fn: (r) => r._measurement == "alerts")
                  |> sort(columns: ["_time"], desc: true)
                  |> limit(n: {limit})
                '''
                tables = self._query_api.query(query, org=self.settings.influxdb_org)
                alerts = self._parse_alert_tables(tables)
                if alerts:
                    return alerts
            except Exception as exc:
                logger.warning("InfluxDB query failed, using memory fallback: %s", exc)

        return self._memory_alerts[:limit]

    @staticmethod
    def _parse_alert_tables(tables) -> list[AlertRecord]:
        records_by_time: dict[str, dict] = {}
        for table in tables:
            for record in table.records:
                ts = record.get_time().isoformat()
                if ts not in records_by_time:
                    records_by_time[ts] = {"timestamp": record.get_time(), "id": str(uuid.uuid4())}
                field = record.get_field()
                value = record.get_value()
                records_by_time[ts][field] = value

        alerts = []
        for data in records_by_time.values():
            affected_raw = data.get("affected_sensors", "")
            alerts.append(
                AlertRecord(
                    id=data["id"],
                    timestamp=data["timestamp"],
                    anomaly_label=int(data.get("anomaly_label", 0)),
                    reconstruction_error=float(data.get("reconstruction_error", 0)),
                    confidence_score=float(data.get("confidence_score", 0)),
                    probable_cause=data.get("probable_cause") or None,
                    affected_sensors=affected_raw.split(",") if affected_raw else [],
                )
            )
        return sorted(alerts, key=lambda a: a.timestamp, reverse=True)
