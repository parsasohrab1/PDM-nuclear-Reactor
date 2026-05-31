"""LSTM Autoencoder model definition (FR-10)."""

from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from tensorflow.keras import Model


def _import_tf():
    try:
        import tensorflow as tf
        from tensorflow.keras import Model, layers

        return tf, Model, layers
    except ImportError as exc:
        raise ImportError(
            "TensorFlow is required for ML features. Install with: pip install -r requirements-ml.txt"
        ) from exc


def build_lstm_autoencoder(
    input_size: int,
    encoder_layers: list[int],
    decoder_layers: list[int],
    n_features: int = 4,
) -> "Model":
    """
    Architecture per SRS:
    - Input: 64 timesteps
    - Encoder: 32 -> 16
    - Decoder: 32 -> 64
    """
    _, Model, layers = _import_tf()

    inputs = layers.Input(shape=(input_size, n_features), name="sensor_input")

    x = inputs
    for i, units in enumerate(encoder_layers):
        return_sequences = i < len(encoder_layers) - 1 or len(decoder_layers) > 0
        x = layers.LSTM(units, return_sequences=return_sequences, name=f"encoder_lstm_{i}")(x)

    for i, units in enumerate(decoder_layers[:-1]):
        x = layers.LSTM(units, return_sequences=True, name=f"decoder_lstm_{i}")(x)

    if decoder_layers:
        x = layers.LSTM(
            decoder_layers[-1],
            return_sequences=True,
            name="decoder_lstm_out",
        )(x)

    outputs = layers.TimeDistributed(layers.Dense(n_features), name="reconstruction")(x)

    model = Model(inputs=inputs, outputs=outputs, name="lstm_autoencoder")
    model.compile(optimizer="adam", loss="mse")
    return model


def save_model(model: Any, path: str | Path) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    model.save(path)


def load_model(path: str | Path) -> "Model":
    tf, _, _ = _import_tf()
    return tf.keras.models.load_model(path)
