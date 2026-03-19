import axios from "axios";

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1",
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const storage = localStorage.getItem("auth-storage");
    if (storage) {
      try {
        const { state } = JSON.parse(storage);
        if (state?.accessToken) {
          config.headers.Authorization = `Bearer ${state.accessToken}`;
        }
      } catch {
        // ignore parse errors
      }
    }
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== "undefined") {
      const storage = localStorage.getItem("auth-storage");
      if (storage) {
        try {
          const parsed = JSON.parse(storage);
          parsed.state.accessToken = null;
          parsed.state.refreshToken = null;
          parsed.state.user = null;
          parsed.state.isAuthenticated = false;
          localStorage.setItem("auth-storage", JSON.stringify(parsed));
        } catch {
          localStorage.removeItem("auth-storage");
        }
      }
      window.location.href = "/login";
    }
    return Promise.reject(error);
  }
);

export default api;
