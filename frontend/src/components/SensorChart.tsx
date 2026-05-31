import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { ChartPoint } from "../types";

interface SensorChartProps {
  title: string;
  data: ChartPoint[];
  color: string;
}

export function SensorChart({ title, data, color }: SensorChartProps) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <ResponsiveContainer width="100%" height={180}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#24324a" />
          <XAxis dataKey="time" hide />
          <YAxis stroke="#9fb3d1" fontSize={11} />
          <Tooltip
            contentStyle={{
              background: "#121c2d",
              border: "1px solid #24324a",
              borderRadius: 8,
            }}
          />
          <Line
            type="monotone"
            dataKey="value"
            stroke={color}
            strokeWidth={2}
            dot={false}
            isAnimationActive={false}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
