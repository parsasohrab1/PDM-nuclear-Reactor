import numpy as np
import pandas as pd

SENSOR_COLUMNS = ["temp_c", "pressure_bar", "neutron_flux", "vibration_ms2"]


class Preprocessor:
    """Data preprocessing: interpolation, normalization, windowing (FR-07..FR-09)."""

    def __init__(
        self,
        window_neutron_flux: int = 10,
        window_temperature: int = 3600,
    ):
        self.window_neutron_flux = window_neutron_flux
        self.window_temperature = window_temperature
        self._min_values: dict[str, float] | None = None
        self._max_values: dict[str, float] | None = None

    def fit_min_max(self, df: pd.DataFrame) -> None:
        """Fit Min-Max scalers on normal training data."""
        self._min_values = {col: float(df[col].min()) for col in SENSOR_COLUMNS}
        self._max_values = {col: float(df[col].max()) for col in SENSOR_COLUMNS}

    def interpolate_missing(self, df: pd.DataFrame) -> pd.DataFrame:
        """Linear interpolation for missing values (FR-07)."""
        result = df.copy()
        for col in SENSOR_COLUMNS:
            result[col] = result[col].interpolate(method="linear", limit_direction="both")
        return result

    def normalize(self, df: pd.DataFrame) -> pd.DataFrame:
        """Min-Max normalization to [0, 1] (FR-08)."""
        if self._min_values is None or self._max_values is None:
            self.fit_min_max(df)

        result = df.copy()
        for col in SENSOR_COLUMNS:
            min_val = self._min_values[col]
            max_val = self._max_values[col]
            span = max_val - min_val
            if span == 0:
                result[col] = 0.0
            else:
                result[col] = (result[col] - min_val) / span
        return result

    def to_feature_matrix(self, df: pd.DataFrame) -> np.ndarray:
        """Convert sensor readings to feature matrix."""
        cleaned = self.interpolate_missing(df)
        normalized = self.normalize(cleaned)
        return normalized[SENSOR_COLUMNS].values.astype(np.float32)

    def get_window_size(self, primary_sensor: str = "neutron_flux") -> int:
        """Dynamic windowing based on sensor type (FR-09)."""
        if primary_sensor == "temp_c":
            return self.window_temperature
        return self.window_neutron_flux
