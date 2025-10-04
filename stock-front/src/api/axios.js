import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

function getAccessToken() {
  return localStorage.getItem("access_token");
}
function getRefreshToken() {
  return localStorage.getItem("refresh_token");
}
function saveTokens(access, refresh) {
  localStorage.setItem("access_token", access);
  localStorage.setItem("refresh_token", refresh);
}
function clearTokens() {
  localStorage.removeItem("access_token");
  localStorage.removeItem("refresh_token");
}

const api = axios.create({
  baseURL: API_URL,
});

// 🔹 Ajout automatique du token
api.interceptors.request.use(
  (config) => {
    const token = getAccessToken();
    if (token) config.headers["Authorization"] = `Bearer ${token}`;
    return config;
  },
  (error) => Promise.reject(error)
);

// 🔹 Gestion token expiré → refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;
      try {
        const refreshToken = getRefreshToken();
        if (refreshToken) {
          const res = await axios.post(`${API_URL}/refresh`, {
            refresh_token: refreshToken,
          });

          saveTokens(res.data.access_token, res.data.refresh_token);

          api.defaults.headers.common["Authorization"] =
            "Bearer " + res.data.access_token;

          return api(originalRequest);
        }
      } catch (err) {
        console.error("Refresh token failed:", err);
        clearTokens();
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

export default api;
export { getAccessToken, getRefreshToken, saveTokens, clearTokens };
