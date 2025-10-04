import api from "./axios";

// Auth
export async function login(username, password) {
  const res = await api.post("/login", { username, password });
  return res.data;
}

// Articles
export async function fetchArticles() {
  const res = await api.get("/articles/");
  return res.data;
}

export async function createOrUpdateArticle(article) {
  const res = await api.post("/articles/", article);
  return res.data;
}

export async function deleteArticle(id) {
  const res = await api.delete(`/articles/${id}`);
  return res.data;
}

// Retraits
export async function fetchRetraits() {
  const res = await api.get("/retraits/");
  return res.data;
}

export async function retirerArticle(articleId, quantite) {
  const res = await api.post(`/articles/${articleId}/retrait`, { quantite });
  return res.data;
}
