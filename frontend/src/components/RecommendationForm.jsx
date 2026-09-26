import { useTranslation } from "react-i18next";

const STORAGE_OPTIONS = [
  { value: "ambient", labelKey: "storageAmbient", tempPreset: 27 },
  { value: "chilled", labelKey: "storageChilled", tempPreset: 4 },
  { value: "frozen", labelKey: "storageFrozen", tempPreset: -18 },
];

const HUMIDITY_PRESETS = [
  { value: 35, labelKey: "humidityLow" },
  { value: 65, labelKey: "humidityMedium" },
  { value: 92, labelKey: "humidityHigh" },
];

export default function RecommendationForm({ commodities, values, onChange, farmerMode, loading, onSubmit }) {
  const { t } = useTranslation();

  const handleStorageChange = (value) => {
    const preset = STORAGE_OPTIONS.find((o) => o.value === value);
    onChange({ ...values, storageType: value, temperatureC: preset ? preset.tempPreset : values.temperatureC });
  };

  return (
    <form
      className="card"
      onSubmit={(e) => {
        e.preventDefault();
        onSubmit();
      }}
    >
      <h2>{t("resultsTitle")}</h2>

      <div className="field">
        <label>{farmerMode ? t("commodityLabelFarmer") : t("commodityLabel")}</label>
        <select
          value={values.commodityId}
          onChange={(e) => onChange({ ...values, commodityId: Number(e.target.value) })}
        >
          {commodities.map((c) => (
            <option key={c.id} value={c.id}>{c.name}</option>
          ))}
        </select>
      </div>

      <div className="field">
        <label>{farmerMode ? t("storageLabelFarmer") : t("storageLabel")}</label>
        {farmerMode ? (
          <div className="pill-group">
            {STORAGE_OPTIONS.map((o) => (
              <button
                type="button"
                key={o.value}
                className={values.storageType === o.value ? "active" : ""}
                onClick={() => handleStorageChange(o.value)}
              >
                {t(o.labelKey)}
              </button>
            ))}
          </div>
        ) : (
          <select value={values.storageType} onChange={(e) => handleStorageChange(e.target.value)}>
            {STORAGE_OPTIONS.map((o) => (
              <option key={o.value} value={o.value}>{t(o.labelKey)}</option>
            ))}
          </select>
        )}
      </div>

      <div className="field">
        <label>{farmerMode ? t("shelfLifeLabelFarmer") : t("shelfLifeLabel")}</label>
        <input
          type="range"
          min="1"
          max="365"
          value={values.desiredShelfLifeDays}
          onChange={(e) => onChange({ ...values, desiredShelfLifeDays: Number(e.target.value) })}
        />
        <div className="range-value">{values.desiredShelfLifeDays} {t("days")}</div>
      </div>

      {!farmerMode && (
        <div className="field">
          <label>{t("temperatureLabel")}</label>
          <input
            type="number"
            value={values.temperatureC}
            onChange={(e) => onChange({ ...values, temperatureC: Number(e.target.value) })}
          />
        </div>
      )}

      <div className="field">
        <label>{farmerMode ? t("humidityLabelFarmer") : t("humidityLabel")}</label>
        {farmerMode ? (
          <div className="pill-group">
            {HUMIDITY_PRESETS.map((p) => (
              <button
                type="button"
                key={p.value}
                className={values.relativeHumidityPct === p.value ? "active" : ""}
                onClick={() => onChange({ ...values, relativeHumidityPct: p.value })}
              >
                {t(p.labelKey)}
              </button>
            ))}
          </div>
        ) : (
          <>
            <input
              type="range"
              min="20"
              max="100"
              value={values.relativeHumidityPct}
              onChange={(e) => onChange({ ...values, relativeHumidityPct: Number(e.target.value) })}
            />
            <div className="range-value">{values.relativeHumidityPct}%</div>
          </>
        )}
      </div>

      <button className="submit-btn" type="submit" disabled={loading}>
        {loading ? t("submitting") : t("submit")}
      </button>
    </form>
  );
}
