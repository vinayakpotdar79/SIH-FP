import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export const api = axios.create({ baseURL: API_BASE });

export const fetchCommodities = () => api.get("/api/commodities").then((r) => r.data);
export const fetchMaterials = () => api.get("/api/materials").then((r) => r.data);
export const postRecommend = (payload) => api.post("/api/recommend", payload).then((r) => r.data);
export const fetchPassport = (id) => api.get(`/api/passport/${id}`).then((r) => r.data);
