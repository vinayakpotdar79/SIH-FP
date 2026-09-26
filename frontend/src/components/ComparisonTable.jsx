import { useTranslation } from "react-i18next";

export default function ComparisonTable({ recommendations }) {
  const { t } = useTranslation();

  return (
    <div className="card">
      <h2>{t("comparisonTitle")}</h2>
      <table className="compare-table">
        <thead>
          <tr>
            <th></th>
            <th>{t("matchScore")}</th>
            <th>{t("predictedShelfLife")}</th>
            <th>{t("costTier")}</th>
            <th>{t("ecoScore")}</th>
            <th>{t("recyclable")}</th>
            <th>{t("biodegradable")}</th>
          </tr>
        </thead>
        <tbody>
          {recommendations.map((r) => (
            <tr key={r.material.id}>
              <td><strong>{r.material.name}</strong></td>
              <td>{r.score}</td>
              <td>{r.predicted_shelf_life_days} {t("days")}</td>
              <td>{"$".repeat(r.material.cost_tier)}</td>
              <td>{r.material.eco_score}/10</td>
              <td>{r.material.recyclable ? "✓" : "–"}</td>
              <td>{r.material.biodegradable ? "✓" : "–"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
