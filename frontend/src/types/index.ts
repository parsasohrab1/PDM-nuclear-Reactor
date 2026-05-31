export interface SensorReading {
  timestamp: string;
  temp_c: number;
  pressure_bar: number;
  neutron_flux: number;
  vibration_ms2: number;
}

export interface PredictResponse {
  anomaly_label: number;
  reconstruction_error: number;
  confidence_score: number;
  probable_cause?: string | null;
  affected_sensors: string[];
}

export interface AlertRecord {
  id: string;
  timestamp: string;
  anomaly_label: number;
  reconstruction_error: number;
  confidence_score: number;
  probable_cause?: string | null;
  affected_sensors: string[];
}

export interface ChartPoint {
  time: string;
  value: number;
}
