from backend.app.config import get_settings
from backend.app.services.data_generator import SyntheticDataGenerator


def test_generate_synthetic_data(tmp_path):
    settings = get_settings()
    generator = SyntheticDataGenerator(settings)
    generator.output_dir = tmp_path

    result = generator.generate(
        duration_seconds=3600,
        frequency_hz=1.0,
        inject_anomalies=True,
        output_filename="test_data.csv",
    )

    assert result["status"] == "success"
    assert result["records"] == 3600
    assert 0 <= result["anomaly_rate"] <= 1
    assert (tmp_path / "test_data.csv").exists()
