const API_URL = "http://localhost:8000";

// Gestion du token avec localStorage
export const getToken = () => localStorage.getItem("token");
export const setToken = (t) => localStorage.setItem("token", t);
export const clearToken = () => localStorage.removeItem("token");

// Helper fetch avec Auth
const authFetch = async (url, options = {}) => {
  const headers = { ...(options.headers || {}), "Content-Type": "application/json" };
  const token = getToken();
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${API_URL}${url}`, { ...options, headers });
  if (!res.ok) {
    const msg = await res.text().catch(() => res.statusText);
    throw new Error(msg);
  }
  return await res.json();
};

/* ---------------- AUTH ---------------- */
export const login = async (username, password) => {
  const res = await fetch(`${API_URL}/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: new URLSearchParams({ username, password }),
  });
  if (!res.ok) throw new Error("Identifiants invalides");
  const data = await res.json();
  setToken(data.access_token);
  return data;
};

export const logout = () => {
  clearToken();
};

/* ---------------- ARTICLES ---------------- */
export const fetchArticles = () => authFetch("/articles/");
export const createOrUpdateArticle = (article) =>
  authFetch("/articles/", { method: "POST", body: JSON.stringify(article) });
export const deleteArticle = (id) =>
  authFetch(`/articles/${id}`, { method: "DELETE" });

/* ---------------- RETRAITS ---------------- */
export const fetchRetraits = () => authFetch("/retraits/");
export const retirerArticle = (id, quantite) =>
  authFetch(`/articles/${id}/retrait`, {
    method: "POST",
    body: JSON.stringify({ quantite }),
  });
