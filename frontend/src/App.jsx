import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Route, Routes } from "react-router-dom";
import RecommenderPage from "./pages/RecommenderPage";
import PassportPage from "./pages/PassportPage";

export default function App() {
  const { t, i18n } = useTranslation();
  const [farmerMode, setFarmerMode] = useState(false);

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <h1>{t("appTitle")}</h1>
          <p>{t("appSubtitle")}</p>
        </div>
        <div className="header-controls">
          <div className="segmented">
            <button className={!farmerMode ? "active" : ""} onClick={() => setFarmerMode(false)}>{t("technicalMode")}</button>
            <button className={farmerMode ? "active" : ""} onClick={() => setFarmerMode(true)}>{t("farmerMode")}</button>
          </div>
          <div className="segmented">
            <button className={i18n.language === "en" ? "active" : ""} onClick={() => i18n.changeLanguage("en")}>EN</button>
            <button className={i18n.language === "hi" ? "active" : ""} onClick={() => i18n.changeLanguage("hi")}>हि</button>
          </div>
        </div>
      </header>

      <Routes>
        <Route path="/" element={<RecommenderPage farmerMode={farmerMode} />} />
        <Route path="/passport/:id" element={<PassportPage />} />
      </Routes>
    </div>
  );
}
