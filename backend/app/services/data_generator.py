from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

from backend.app.config import Settings

ANOMALY_PROFILES = {
    "A1": {"column": "temp_c", "count_per_month": 200, "description": "Sudden temperature rise"},
    "A2": {"column": "pressure_bar", "count_per_month": 150, "description": "Abnormal pressure oscillation"},
    "A3": {"column": "neutron_flux", "count_per_month": 100, "description": "Neutron flux drop"},
    "A4": {"column": "vibration_ms2", "count_per_month": 250, "description": "High-frequency vibration"},
}


class SyntheticDataGenerator:
    """Synthetic reactor data generator with anomaly injection (FR-01..FR-05)."""

    def __init__(self, settings: Settings):
        self.settings = settings
        self.output_dir = settings.project_root / "data" / "raw"

    def generate(
        self,
        duration_days: int = 30,
        frequency_hz: float = 1.0,
        inject_anomalies: bool = True,
        output_filename: str = "nuclear_reactor_synthetic_data.csv",
        start_time: datetime | None = None,
        duration_seconds: int | None = None,
    ) -> dict:
        interval_seconds = max(1, int(round(1 / frequency_hz)))
        total_seconds = duration_seconds if duration_seconds is not None else duration_days * 24 * 3600
        step_indices = np.arange(0, total_seconds, interval_seconds)
        n_records = len(step_indices)

        start = start_time or datetime(2025, 1, 1, 0, 0, 0)
        timestamps = [start + timedelta(seconds=int(t)) for t in step_indices]
        t_seconds = step_indices.astype(float)

        df = pd.DataFrame(
            {
                "timestamp": timestamps,
                "temp_c": self._normal_temperature(t_seconds),
                "pressure_bar": self._normal_pressure(t_seconds),
                "neutron_flux": [self._normal_neutron_flux(float(ts)) for ts in t_seconds],
                "vibration_ms2": self._normal_vibration(t_seconds),
            }
        )

        anomaly_indices: list[int] = []
        if inject_anomalies:
            np.random.seed(42)
            months = max(duration_days / 30, 1 / 30)
            anomaly_indices = self._inject_anomalies(df, n_records, months)

        df["label"] = 0
        if anomaly_indices:
            df.loc[anomaly_indices, "label"] = 1

        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.output_dir / output_filename
        df.to_csv(output_path, index=False)

        return {
            "status": "success",
            "records": len(df),
            "anomaly_rate": float(df["label"].mean()),
            "output_path": str(output_path),
        }

    @staticmethod
    def _normal_temperature(t: np.ndarray) -> np.ndarray:
        daily = 5 * np.sin(2 * np.pi * t / 86400)
        trend = 1e-6 * t
        noise = np.random.normal(0, 0.2, len(t))
        return 300 + daily + trend + noise

    @staticmethod
    def _normal_pressure(t: np.ndarray) -> np.ndarray:
        return 150 + 2 * np.sin(2 * np.pi * t / 43200) + np.random.normal(0, 0.1, len(t))

    @staticmethod
    def _normal_neutron_flux(t: float) -> int:
        base = 1000 + 0.5 * np.sin(2 * np.pi * t / 3600)
        return int(np.random.poisson(max(base, 1)))

    @staticmethod
    def _normal_vibration(t: np.ndarray) -> np.ndarray:
        return 0.5 * np.sin(2 * np.pi * t / 300) + np.random.normal(0, 0.05, len(t))

    def _inject_anomalies(self, df: pd.DataFrame, n_records: int, months: float) -> list[int]:
        indices: list[int] = []

        # A1: sudden temperature rise (+15 to +30°C)
        count_a1 = int(ANOMALY_PROFILES["A1"]["count_per_month"] * months)
        if count_a1 > 0:
            anom1 = np.random.choice(n_records, size=min(count_a1, n_records), replace=False)
            df.loc[anom1, "temp_c"] += np.random.uniform(15, 30, size=len(anom1))
            indices.extend(anom1.tolist())

        # A2: abnormal pressure oscillation (Gaussian +10)
        count_a2 = int(ANOMALY_PROFILES["A2"]["count_per_month"] * months)
        if count_a2 > 0:
            anom2 = np.random.choice(n_records, size=min(count_a2, n_records), replace=False)
            df.loc[anom2, "pressure_bar"] += np.random.normal(10, 2, size=len(anom2))
            indices.extend(anom2.tolist())

        # A3: neutron flux drop (×0.3)
        count_a3 = int(ANOMALY_PROFILES["A3"]["count_per_month"] * months)
        if count_a3 > 0:
            anom3 = np.random.choice(n_records, size=min(count_a3, n_records), replace=False)
            df.loc[anom3, "neutron_flux"] = (df.loc[anom3, "neutron_flux"] * 0.3).astype(int)
            indices.extend(anom3.tolist())

        # A4: high-frequency vibration (+0.8 to +1.5)
        count_a4 = int(ANOMALY_PROFILES["A4"]["count_per_month"] * months)
        if count_a4 > 0:
            anom4 = np.random.choice(n_records, size=min(count_a4, n_records), replace=False)
            df.loc[anom4, "vibration_ms2"] += np.random.uniform(0.8, 1.5, size=len(anom4))
            indices.extend(anom4.tolist())

        return list(set(indices))
