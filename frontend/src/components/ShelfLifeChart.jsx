import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import {
  Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis, CartesianGrid, ReferenceDot,
} from "recharts";
import { api } from "../api";

const SERIES_COLOR = "#2a78d6";
const GRIDLINE = "#e1e0d9";
const MUTED = "#898781";
const TEXT_SECONDARY = "#52514e";

export default function ShelfLifeChart({ commodityId, materialId, storageType, relativeHumidityPct, currentTemperature }) {
  const { t } = useTranslation();
  const [data, setData] = useState([]);

  useEffect(() => {
    if (!commodityId || !materialId) return;
    api.post("/api/shelf-life-curve", {
      commodity_id: commodityId,
      material_id: materialId,
      storage_type: storageType,
      relative_humidity_pct: relativeHumidityPct,
    }).then((res) => setData(res.data));
  }, [commodityId, materialId, storageType, relativeHumidityPct]);

  if (data.length === 0) return null;

  const currentPoint = data.reduce((closest, point) => (
    Math.abs(point.temperature_c - currentTemperature) < Math.abs(closest.temperature_c - currentTemperature)
      ? point : closest
  ), data[0]);

  return (
    <div>
      <h3 style={{ fontSize: "0.95rem", marginBottom: 8 }}>{t("shelfLifeChartTitle")}</h3>
      <ResponsiveContainer width="100%" height={220}>
        <LineChart data={data} margin={{ top: 8, right: 16, bottom: 0, left: 0 }}>
          <CartesianGrid stroke={GRIDLINE} vertical={false} />
          <XAxis
            dataKey="temperature_c"
            tick={{ fontSize: 12, fill: MUTED }}
            axisLine={{ stroke: GRIDLINE }}
            tickLine={false}
            label={{ value: "°C", position: "insideBottomRight", offset: -4, fill: MUTED, fontSize: 12 }}
          />
          <YAxis
            tick={{ fontSize: 12, fill: MUTED }}
            axisLine={false}
            tickLine={false}
            width={36}
          />
          <Tooltip
            contentStyle={{ fontSize: 12, borderRadius: 8, border: "1px solid " + GRIDLINE }}
            formatter={(value) => [`${value} ${t("days")}`, t("predictedShelfLife")]}
            labelFormatter={(label) => `${label}°C`}
          />
          <Line
            type="monotone"
            dataKey="predicted_shelf_life_days"
            stroke={SERIES_COLOR}
            strokeWidth={2}
            dot={false}
            activeDot={{ r: 5 }}
          />
          <ReferenceDot
            x={currentPoint.temperature_c}
            y={currentPoint.predicted_shelf_life_days}
            r={5}
            fill={SERIES_COLOR}
            stroke="white"
            strokeWidth={2}
          />
        </LineChart>
      </ResponsiveContainer>
      <div style={{ fontSize: "0.8rem", color: TEXT_SECONDARY }}>
        {t("predictedShelfLife")} @ {currentTemperature}°C: <strong>{currentPoint.predicted_shelf_life_days} {t("days")}</strong>
      </div>
    </div>
  );
}
