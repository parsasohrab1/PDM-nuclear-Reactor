"""
Legacy standalone data generator script.

For production use, prefer the API endpoint:
  POST /api/v1/data/generate

Or import from backend:
  from backend.app.services.data_generator import SyntheticDataGenerator
"""

from backend.app.config import get_settings
from backend.app.services.data_generator import SyntheticDataGenerator


def main() -> None:
    settings = get_settings()
    generator = SyntheticDataGenerator(settings)
    result = generator.generate(
        duration_days=30,
        frequency_hz=1.0,
        inject_anomalies=True,
        output_filename="nuclear_reactor_synthetic_data.csv",
    )
    print(f"Records: {result['records']}")
    print(f"Anomaly rate: {result['anomaly_rate'] * 100:.2f}%")
    print(f"Output: {result['output_path']}")


if __name__ == "__main__":
    main()
