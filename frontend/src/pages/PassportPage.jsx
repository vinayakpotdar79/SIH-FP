import { useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { fetchPassport } from "../api";

export default function PassportPage() {
  const { id } = useParams();
  const [passport, setPassport] = useState(null);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchPassport(id).then(setPassport).catch(() => setError("Passport not found."));
  }, [id]);

  if (error) return <div className="card error-banner">{error}</div>;
  if (!passport) return <p>Loading...</p>;

  const top = passport.result.recommendations[0];

  return (
    <div className="card">
      <h2>{passport.commodity_name}</h2>
      <p style={{ color: "var(--text-secondary)" }}>Generated {new Date(passport.created_at).toLocaleString()}</p>
      {top && (
        <>
          <h3>{top.material.name}</h3>
          <div className="stat-row">
            <span>OTR: <strong>{top.material.otr_min}-{top.material.otr_max}</strong> cc/m2/day</span>
            <span>WVTR: <strong>{top.material.wvtr_min}-{top.material.wvtr_max}</strong> g/m2/day</span>
            <span>Predicted shelf life: <strong>{top.predicted_shelf_life_days} days</strong></span>
          </div>
          <ul className="reasons-list">
            {top.reasons.map((reason, i) => <li key={i}>{reason}</li>)}
          </ul>
        </>
      )}
    </div>
  );
}
