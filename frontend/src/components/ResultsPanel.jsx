import { useTranslation } from "react-i18next";
import ShelfLifeChart from "./ShelfLifeChart";
import ComparisonTable from "./ComparisonTable";
import QrPassport from "./QrPassport";

export default function ResultsPanel({ result, formValues }) {
  const { t } = useTranslation();
  const topMaterial = result.recommendations[0];

  return (
    <div>
      <div className="card">
        <h2>{t("whyTitle")}</h2>
        <ul className="reasons-list">
          {result.requirement_reasons.map((reason, i) => <li key={i}>{reason}</li>)}
        </ul>
      </div>

      <div className="card">
        <h2>{t("resultsTitle")}</h2>
        {result.recommendations.map((rec, i) => (
          <div className="material-card" key={rec.material.id}>
            <div className="material-card-header">
              <h3>
                <span className={`badge rank-${i}`}>#{i + 1}</span>
                {rec.material.name}
              </h3>
              <span>{t("matchScore")}: <strong>{rec.score}</strong></span>
            </div>
            <div className="stat-row">
              <span>OTR: <strong>{rec.material.otr_min}-{rec.material.otr_max}</strong> cc/m2/day</span>
              <span>WVTR: <strong>{rec.material.wvtr_min}-{rec.material.wvtr_max}</strong> g/m2/day</span>
              <span>{t("predictedShelfLife")}: <strong>{rec.predicted_shelf_life_days} {t("days")}</strong></span>
            </div>
            <ul className="reasons-list">
              {rec.reasons.map((reason, j) => <li key={j}>{reason}</li>)}
            </ul>
          </div>
        ))}
      </div>

      {topMaterial && (
        <div className="card">
          <ShelfLifeChart
            commodityId={result.commodity.id}
            materialId={topMaterial.material.id}
            storageType={formValues.storageType}
            relativeHumidityPct={formValues.relativeHumidityPct}
            currentTemperature={formValues.temperatureC}
          />
        </div>
      )}

      <div className="card">
        <h2>{t("mapTitle")}</h2>
        {result.map_info.applicable ? (
          <>
            <div className="stat-row">
              <span>O<sub>2</sub>: <strong>{result.map_info.o2_pct[0]}-{result.map_info.o2_pct[1]}%</strong></span>
              <span>CO<sub>2</sub>: <strong>{result.map_info.co2_pct[0]}-{result.map_info.co2_pct[1]}%</strong></span>
              <span>{t("predictedShelfLife")}: <strong>{result.map_info.temperature_adjusted_days} {t("days")}</strong></span>
            </div>
            <ul className="reasons-list">
              {result.map_info.reasons.map((reason, i) => <li key={i}>{reason}</li>)}
            </ul>
          </>
        ) : (
          <p style={{ color: "var(--text-secondary)" }}>{t("mapNotApplicable")}</p>
        )}
      </div>

      <ComparisonTable recommendations={result.recommendations} />

      <QrPassport qrDataUri={result.qr_data_uri} passportId={result.passport_id} />
    </div>
  );
}
