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
              <td>
                <span className="cost-tier">
                  {[1, 2, 3].map((tier) => (
                    <span key={tier} className={tier <= r.material.cost_tier ? "filled" : ""}>$</span>
                  ))}
                </span>
              </td>
              <td>
                <div className="eco-bar">
                  <div className="eco-bar-track">
                    <div className="eco-bar-fill" style={{ width: `${r.material.eco_score * 10}%` }} />
                  </div>
                  <span>{r.material.eco_score}/10</span>
                </div>
              </td>
              <td><span className={`check-icon ${r.material.recyclable ? "yes" : "no"}`}>{r.material.recyclable ? "✓" : "–"}</span></td>
              <td><span className={`check-icon ${r.material.biodegradable ? "yes" : "no"}`}>{r.material.biodegradable ? "✓" : "–"}</span></td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
