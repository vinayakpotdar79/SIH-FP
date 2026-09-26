import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { fetchCommodities, postRecommend } from "../api";
import RecommendationForm from "../components/RecommendationForm";
import ResultsPanel from "../components/ResultsPanel";

export default function RecommenderPage({ farmerMode }) {
  const { t } = useTranslation();
  const [commodities, setCommodities] = useState([]);
  const [values, setValues] = useState({
    commodityId: null,
    storageType: "ambient",
    desiredShelfLifeDays: 14,
    temperatureC: 27,
    relativeHumidityPct: 65,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCommodities()
      .then((data) => {
        setCommodities(data);
        if (data.length > 0) setValues((v) => ({ ...v, commodityId: data[0].id }));
      })
      .catch(() => setError("Could not load commodities. Is the backend running on http://localhost:8000?"));
  }, []);

  const handleSubmit = async () => {
    if (!values.commodityId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await postRecommend({
        commodity_id: values.commodityId,
        storage_type: values.storageType,
        desired_shelf_life_days: values.desiredShelfLifeDays,
        temperature_c: values.temperatureC,
        relative_humidity_pct: values.relativeHumidityPct,
      });
      setResult(data);
    } catch (e) {
      setError("Recommendation request failed. Is the backend running on http://localhost:8000?");
    } finally {
      setLoading(false);
    }
  };

  if (commodities.length === 0 && !error) {
    return <p>{t("loadingCommodities")}</p>;
  }

  return (
    <div>
      {error && <div className="error-banner">{error}</div>}
      <RecommendationForm
        commodities={commodities}
        values={values}
        onChange={setValues}
        farmerMode={farmerMode}
        loading={loading}
        onSubmit={handleSubmit}
      />
      {result && <ResultsPanel result={result} formValues={values} />}
    </div>
  );
}
