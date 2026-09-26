import { useTranslation } from "react-i18next";

export default function QrPassport({ qrDataUri, passportId }) {
  const { t } = useTranslation();

  return (
    <div className="card">
      <h2>{t("passportTitle")}</h2>
      <div className="qr-box">
        <img src={qrDataUri} alt="Packaging passport QR code" />
        <div>
          <p style={{ margin: "0 0 6px", color: "var(--text-secondary)", fontSize: "0.88rem" }}>{t("passportHint")}</p>
          <code style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>#{passportId}</code>
        </div>
      </div>
    </div>
  );
}
