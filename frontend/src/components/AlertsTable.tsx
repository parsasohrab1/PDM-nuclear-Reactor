import type { AlertRecord } from "../types";
import type { Lang } from "../i18n";
import { t } from "../i18n";

interface AlertsTableProps {
  alerts: AlertRecord[];
  lang: Lang;
}

export function AlertsTable({ alerts, lang }: AlertsTableProps) {
  if (alerts.length === 0) {
    return <div className="empty-state">{t(lang, "noAlerts")}</div>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>{t(lang, "time")}</th>
          <th>{t(lang, "confidence")}</th>
          <th>{t(lang, "cause")}</th>
          <th>{t(lang, "sensors")}</th>
        </tr>
      </thead>
      <tbody>
        {alerts.map((alert) => (
          <tr key={alert.id}>
            <td>{new Date(alert.timestamp).toLocaleString(lang === "fa" ? "fa-IR" : "en-US")}</td>
            <td>{alert.confidence_score.toFixed(1)}%</td>
            <td>{alert.probable_cause ?? "-"}</td>
            <td>{alert.affected_sensors.join(", ") || "-"}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
