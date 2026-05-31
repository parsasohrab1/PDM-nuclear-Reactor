import { useCallback, useEffect, useRef, useState } from "react";
import { checkHealth, fetchAlerts, predict } from "./api/client";
import { AlertsTable } from "./components/AlertsTable";
import { SensorChart } from "./components/SensorChart";
import { t, type Lang } from "./i18n";
import type { AlertRecord, ChartPoint, SensorReading } from "./types";

const MAX_POINTS = 60;

function generateMockReading(): SensorReading {
  const now = new Date();
  return {
    timestamp: now.toISOString(),
    temp_c: 300 + Math.random() * 5,
    pressure_bar: 150 + Math.random() * 2,
    neutron_flux: Math.floor(980 + Math.random() * 40),
    vibration_ms2: 0.4 + Math.random() * 0.2,
  };
}

function appendPoint(prev: ChartPoint[], value: number): ChartPoint[] {
  const next = [...prev, { time: new Date().toLocaleTimeString(), value }];
  return next.slice(-MAX_POINTS);
}

function playAlertBeep() {
  try {
    const ctx = new AudioContext();
    const oscillator = ctx.createOscillator();
    const gain = ctx.createGain();
    oscillator.connect(gain);
    gain.connect(ctx.destination);
    oscillator.frequency.value = 880;
    gain.gain.value = 0.1;
    oscillator.start();
    setTimeout(() => {
      oscillator.stop();
      ctx.close();
    }, 300);
  } catch {
    // Audio not available
  }
}

export default function App() {
  const [lang, setLang] = useState<Lang>("fa");
  const [alerts, setAlerts] = useState<AlertRecord[]>([]);
  const [isAnomaly, setIsAnomaly] = useState(false);
  const [showPopup, setShowPopup] = useState(false);
  const [backendOnline, setBackendOnline] = useState(false);
  const [tempData, setTempData] = useState<ChartPoint[]>([]);
  const [pressureData, setPressureData] = useState<ChartPoint[]>([]);
  const [neutronData, setNeutronData] = useState<ChartPoint[]>([]);
  const [vibrationData, setVibrationData] = useState<ChartPoint[]>([]);
  const windowRef = useRef<SensorReading[]>([]);

  const refreshAlerts = useCallback(async () => {
    try {
      const data = await fetchAlerts(100);
      setAlerts(data);
    } catch {
      // Backend may be offline during dev
    }
  }, []);

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = lang === "fa" ? "rtl" : "ltr";
  }, [lang]);

  useEffect(() => {
    const tick = async () => {
      const online = await checkHealth();
      setBackendOnline(online);

      const reading = generateMockReading();
      windowRef.current = [...windowRef.current, reading].slice(-64);

      setTempData((p) => appendPoint(p, reading.temp_c));
      setPressureData((p) => appendPoint(p, reading.pressure_bar));
      setNeutronData((p) => appendPoint(p, reading.neutron_flux));
      setVibrationData((p) => appendPoint(p, reading.vibration_ms2));

      if (online && windowRef.current.length >= 10) {
        try {
          const result = await predict(windowRef.current);
          const anomaly = result.anomaly_label === 1;
          setIsAnomaly(anomaly);
          if (anomaly) {
            setShowPopup(true);
            playAlertBeep();
            setTimeout(() => setShowPopup(false), 5000);
          }
        } catch {
          // Prediction may fail before model is trained
        }
      }

      await refreshAlerts();
    };

    tick();
    const interval = setInterval(tick, 1000);
    return () => clearInterval(interval);
  }, [refreshAlerts]);

  return (
    <div className="app-shell">
      {showPopup && <div className="alert-popup">{t(lang, "alertPopup")}</div>}

      <header className="header">
        <h1>{t(lang, "title")}</h1>
        <div className="header-actions">
          <span className={`status-badge ${isAnomaly ? "alert" : ""}`}>
            {isAnomaly ? t(lang, "statusAlert") : t(lang, "statusNormal")}
          </span>
          <span className="status-badge">
            {backendOnline ? t(lang, "backendOnline") : t(lang, "backendOffline")}
          </span>
          <button
            className="secondary lang-toggle"
            onClick={() => setLang(lang === "fa" ? "en" : "fa")}
          >
            {t(lang, "langToggle")}
          </button>
        </div>
      </header>

      <section className="grid-charts">
        <SensorChart title={t(lang, "temperature")} data={tempData} color="#f6ad55" />
        <SensorChart title={t(lang, "pressure")} data={pressureData} color="#63b3ed" />
        <SensorChart title={t(lang, "neutronFlux")} data={neutronData} color="#68d391" />
        <SensorChart title={t(lang, "vibration")} data={vibrationData} color="#b794f4" />
      </section>

      <section className="card alerts-panel">
        <h2>{t(lang, "alertsHistory")}</h2>
        <AlertsTable alerts={alerts} lang={lang} />
      </section>
    </div>
  );
}
