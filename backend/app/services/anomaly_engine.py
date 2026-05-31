import logging
from pathlib import Path

import numpy as np
import pandas as pd

from backend.app.config import Settings, get_settings
from backend.app.models.lstm_autoencoder import build_lstm_autoencoder, load_model, save_model
from backend.app.schemas.detection import PredictResponse, RetrainResponse, SensorReading
from backend.app.services.explainer import infer_probable_cause
from backend.app.services.preprocessor import Preprocessor, SENSOR_COLUMNS

logger = logging.getLogger(__name__)

_engine_instance: "AnomalyEngine | None" = None


class AnomalyEngine:
    """
    Anomaly detection engine: LSTM Autoencoder + adaptive threshold (FR-10..FR-15).
    One-Class SVM hook reserved for ensemble extension.
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self.preprocessor = Preprocessor(
            window_neutron_flux=settings.window_neutron_flux,
            window_temperature=settings.window_temperature,
        )
        self.input_size = settings.lstm_input_size
        self.threshold_k = settings.anomaly_threshold_k
        self._threshold: float | None = None
        self._error_mean: float = 0.0
        self._error_std: float = 1.0
        self._model = None
        self._ml_available = True
        self._load_or_init_model()

    def _load_or_init_model(self) -> None:
        model_path = self.settings.project_root / self.settings.model_path
        if model_path.exists():
            try:
                self._model = load_model(model_path)
                logger.info("Loaded model from %s", model_path)
                return
            except ImportError as exc:
                self._ml_available = False
                logger.warning("ML stack unavailable: %s", exc)
                return
            except Exception as exc:
                logger.warning("Failed to load model: %s", exc)

        try:
            self._model = build_lstm_autoencoder(
                input_size=self.input_size,
                encoder_layers=self.settings.encoder_layer_sizes,
                decoder_layers=self.settings.decoder_layer_sizes,
            )
            logger.info("Initialized untrained LSTM autoencoder")
        except ImportError as exc:
            self._ml_available = False
            logger.warning("ML stack unavailable: %s", exc)

    def _readings_to_dataframe(self, window: list[SensorReading]) -> pd.DataFrame:
        return pd.DataFrame([r.model_dump() for r in window])

    def _pad_or_truncate(self, features: np.ndarray) -> np.ndarray:
        n_timesteps, n_features = features.shape
        if n_timesteps >= self.input_size:
            return features[-self.input_size :]
        pad = np.zeros((self.input_size - n_timesteps, n_features), dtype=np.float32)
        return np.vstack([pad, features])

    def _compute_mse(self, original: np.ndarray, reconstructed: np.ndarray) -> float:
        return float(np.mean((original - reconstructed) ** 2))

    def _adaptive_threshold(self, error: float) -> bool:
        """Adaptive threshold: μ + kσ (FR-13)."""
        if self._threshold is None:
            self._threshold = self._error_mean + self.threshold_k * self._error_std
        return error > self._threshold

    def _confidence_score(self, error: float) -> float:
        if self._threshold is None or self._threshold == 0:
            return min(100.0, error * 100)
        ratio = error / self._threshold
        return float(min(100.0, max(0.0, ratio * 50)))

    async def predict(self, window: list[SensorReading]) -> PredictResponse:
        if self._model is None:
            raise RuntimeError(
                "Anomaly model unavailable. Install ML deps: pip install -r requirements-ml.txt"
            )

        df = self._readings_to_dataframe(window)
        features = self.preprocessor.to_feature_matrix(df)
        padded = self._pad_or_truncate(features)
        batch = padded.reshape(1, self.input_size, len(SENSOR_COLUMNS))

        reconstructed = self._model.predict(batch, verbose=0)
        error = self._compute_mse(batch, reconstructed)
        is_anomaly = self._adaptive_threshold(error)

        sensor_values = {col: float(df[col].iloc[-1]) for col in SENSOR_COLUMNS}
        cause, affected = infer_probable_cause(sensor_values)

        return PredictResponse(
            anomaly_label=1 if is_anomaly else 0,
            reconstruction_error=error,
            confidence_score=self._confidence_score(error),
            probable_cause=cause if is_anomaly else None,
            affected_sensors=affected if is_anomaly else [],
        )

    async def retrain(self, data_path: str | None = None, epochs: int = 50) -> RetrainResponse:
        """Train on normal data only (label=0) (FR-11)."""
        if not self._ml_available:
            return RetrainResponse(
                status="error",
                message="ML stack not installed. Run: pip install -r requirements-ml.txt",
                model_path=None,
            )

        path = Path(data_path) if data_path else self.settings.project_root / "data/raw/nuclear_reactor_synthetic_data.csv"

        if not path.exists():
            return RetrainResponse(
                status="error",
                message=f"Training data not found: {path}. Generate data first via POST /api/v1/data/generate",
                model_path=None,
            )

        df = pd.read_csv(path, parse_dates=["timestamp"])
        normal_df = df[df["label"] == 0] if "label" in df.columns else df

        if len(normal_df) < self.input_size:
            return RetrainResponse(
                status="error",
                message=f"Insufficient normal samples ({len(normal_df)}). Need at least {self.input_size}.",
                model_path=None,
            )

        features = self.preprocessor.to_feature_matrix(normal_df)
        sequences = []
        for i in range(len(features) - self.input_size + 1):
            sequences.append(features[i : i + self.input_size])

        x_train = np.array(sequences, dtype=np.float32)
        self._model = build_lstm_autoencoder(
            input_size=self.input_size,
            encoder_layers=self.settings.encoder_layer_sizes,
            decoder_layers=self.settings.decoder_layer_sizes,
        )
        self._model.fit(x_train, x_train, epochs=epochs, batch_size=32, verbose=0)

        errors = []
        for seq in x_train[: min(1000, len(x_train))]:
            recon = self._model.predict(seq.reshape(1, self.input_size, len(SENSOR_COLUMNS)), verbose=0)
            errors.append(self._compute_mse(seq, recon[0]))

        self._error_mean = float(np.mean(errors))
        self._error_std = float(np.std(errors)) or 1.0
        self._threshold = self._error_mean + self.threshold_k * self._error_std

        model_path = self.settings.project_root / self.settings.model_path
        save_model(self._model, model_path)

        return RetrainResponse(
            status="success",
            message=f"Model trained on {len(x_train)} sequences. Threshold: {self._threshold:.6f}",
            model_path=str(model_path),
        )

    def update_threshold(self) -> None:
        """Recalculate adaptive threshold (called every 24h per FR-13)."""
        self._threshold = self._error_mean + self.threshold_k * self._error_std


def get_anomaly_engine() -> AnomalyEngine:
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = AnomalyEngine(get_settings())
    return _engine_instance
