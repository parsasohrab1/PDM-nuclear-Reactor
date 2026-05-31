import axios from "axios";
import type { AlertRecord, PredictResponse, SensorReading } from "../types";

const api = axios.create({
  baseURL: "/api/v1",
  timeout: 10000,
});

export async function fetchAlerts(limit = 100): Promise<AlertRecord[]> {
  const { data } = await api.get<{ alerts: AlertRecord[] }>("/alerts", {
    params: { limit },
  });
  return data.alerts;
}

export async function predict(window: SensorReading[]): Promise<PredictResponse> {
  const { data } = await api.post<PredictResponse>("/predict", { window });
  return data;
}

export async function generateData(durationDays = 1): Promise<void> {
  await api.post("/data/generate", {
    duration_days: durationDays,
    frequency_hz: 1,
    inject_anomalies: true,
  });
}

export async function checkHealth(): Promise<boolean> {
  try {
    const { data } = await axios.get("/health");
    return data.status === "ok";
  } catch {
    return false;
  }
}
