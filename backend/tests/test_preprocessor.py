import pandas as pd
import pytest

from backend.app.services.preprocessor import Preprocessor, SENSOR_COLUMNS


@pytest.fixture
def sample_df():
    return pd.DataFrame(
        {
            "temp_c": [300.0, 301.0, None, 303.0],
            "pressure_bar": [150.0, 150.5, 151.0, 151.5],
            "neutron_flux": [1000, 1001, 1002, 1003],
            "vibration_ms2": [0.5, 0.51, 0.52, 0.53],
        }
    )


def test_interpolate_missing(sample_df):
    preprocessor = Preprocessor()
    result = preprocessor.interpolate_missing(sample_df)
    assert result["temp_c"].isna().sum() == 0


def test_normalize_range(sample_df):
    preprocessor = Preprocessor()
    cleaned = preprocessor.interpolate_missing(sample_df)
    normalized = preprocessor.normalize(cleaned)
    for col in SENSOR_COLUMNS:
        assert normalized[col].min() >= 0.0
        assert normalized[col].max() <= 1.0


def test_window_size():
    preprocessor = Preprocessor(window_neutron_flux=10, window_temperature=3600)
    assert preprocessor.get_window_size("neutron_flux") == 10
    assert preprocessor.get_window_size("temp_c") == 3600
