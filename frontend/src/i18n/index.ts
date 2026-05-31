export type Lang = "fa" | "en";

const translations = {
  fa: {
    title: "داشبورد PdM-Nuclear",
    statusNormal: "وضعیت: نرمال",
    statusAlert: "هشدار آنومالی!",
    temperature: "دما (°C)",
    pressure: "فشار (bar)",
    neutronFlux: "شار نوترون",
    vibration: "لرزش (m/s²)",
    alertsHistory: "تاریخچه هشدارها",
    time: "زمان",
    confidence: "اطمینان",
    cause: "علت احتمالی",
    sensors: "سنسورها",
    noAlerts: "هنوز هشداری ثبت نشده است",
    langToggle: "English",
    backendOnline: "API متصل",
    backendOffline: "API قطع",
    alertPopup: "آنومالی تشخیص داده شد!",
  },
  en: {
    title: "PdM-Nuclear Dashboard",
    statusNormal: "Status: Normal",
    statusAlert: "Anomaly Alert!",
    temperature: "Temperature (°C)",
    pressure: "Pressure (bar)",
    neutronFlux: "Neutron Flux",
    vibration: "Vibration (m/s²)",
    alertsHistory: "Alert History",
    time: "Time",
    confidence: "Confidence",
    cause: "Probable Cause",
    sensors: "Sensors",
    noAlerts: "No alerts recorded yet",
    langToggle: "فارسی",
    backendOnline: "API Connected",
    backendOffline: "API Offline",
    alertPopup: "Anomaly Detected!",
  },
} as const;

export function t(lang: Lang, key: keyof (typeof translations)["fa"]): string {
  return translations[lang][key];
}
