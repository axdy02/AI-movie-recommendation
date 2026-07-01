import axios from "axios";

export const API_BASE_URL = (
  import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"
).replace(/\/$/, "");

export const USE_MOCKS = import.meta.env.VITE_USE_MOCKS === "true";

const TOKEN_KEY = "ai_movie_access_token";

export const apiClient = axios.create({
  baseURL: `${API_BASE_URL}/api/v1`,
  timeout: 12000,
  headers: {
    "Content-Type": "application/json",
  },
});

export const rootClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 8000,
});

export function getStoredToken() {
  return window.sessionStorage.getItem(TOKEN_KEY);
}

export function setStoredToken(token) {
  if (token) {
    window.sessionStorage.setItem(TOKEN_KEY, token);
    apiClient.defaults.headers.common.Authorization = `Bearer ${token}`;
    return;
  }
  clearStoredToken();
}

export function clearStoredToken() {
  window.sessionStorage.removeItem(TOKEN_KEY);
  delete apiClient.defaults.headers.common.Authorization;
}

apiClient.interceptors.request.use((config) => {
  const token = getStoredToken();
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error.response?.data?.detail;
    const message =
      typeof detail === "string" ? detail : error.message || "Request failed.";
    return Promise.reject(new Error(message));
  },
);
