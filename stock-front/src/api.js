import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
});

// Intercepteur pour ajouter le token JWT à chaque requête
api.interceptors.request.use(
  (config) => {
    const userStr = localStorage.getItem("user");
    if (userStr) {
      try {
        const user = JSON.parse(userStr);
        if (user && user.access_token) {
          config.headers.Authorization = `Bearer ${user.access_token}`;
        }
      } catch (e) {
        console.error("Erreur parsing user:", e);
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// ======================= AUTHENTIFICATION =======================
export const login = async (username, password) => {
  const formData = new URLSearchParams();
  formData.append("username", username);
  formData.append("password", password);
  
  const response = await api.post("/auth/login", formData, {
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
  });
  return response.data;
};

export const getCurrentUser = async () => {
  const response = await api.get("/users/me");
  return response.data;
};

// ======================= ENTREPRISES =======================
export const fetchCompanies = async () => {
  const response = await api.get("/entreprises");
  return response.data;
};

export const createCompany = async (name) => {
  const response = await api.post("/entreprises", { nom: name });
  return response.data;
};

// ======================= ARTICLES =======================
export const fetchArticles = async () => {
  const response = await api.get("/articles");
  return response.data;
};

export const createArticle = async (article) => {
  const response = await api.post("/articles", article);
  return response.data;
};

export const updateArticle = async (id, article) => {
  const response = await api.put(`/articles/${id}`, article);
  return response.data;
};

export const deleteArticle = async (id) => {
  const response = await api.delete(`/articles/${id}`);
  return response.data;
};

export const updateArticleQuantity = async (id, quantite) => {
  const response = await api.put(`/articles/${id}`, { quantite });
  return response.data;
};

// ======================= RETRAITS =======================
export const retirerArticle = async (articleId, quantite) => {
  const response = await api.post(`/retraits/${articleId}`, { quantite });
  return response.data;
};

export const fetchRetraits = async () => {
  const response = await api.get("/retraits");
  return response.data;
};

// ======================= CALCULATEUR ÉCHAFAUDAGE =======================
export const calculerEchafaudage = async (hauteur, longueur, largeur) => {
  const response = await api.post("/calcul/", {
    hauteur,
    longueur,
    largeur,
    apply_to_stock: false
  });
  return response.data;
};

export const appliquerAllocation = async (pieces) => {
  const response = await api.post("/calcul/", { 
    hauteur: 0,
    longueur: 0, 
    largeur: 0,
    apply_to_stock: true,
    pieces 
  });
  return response.data;
};

// ======================= UTILISATEURS (ADMIN) =======================
export const fetchUsers = async () => {
  const response = await api.get("/users");
  return response.data;
};

export const createUser = async (userData) => {
  const response = await api.post("/users", userData);
  return response.data;
};

export const deleteUser = async (id) => {
  const response = await api.delete(`/users/${id}`);
  return response.data;
};

// ======================= GESTION ADMIN/USER (NOUVEAUX) =======================
export const createAdmin = async (adminData) => {
  const response = await api.post("/admin/create-admin", adminData);
  return response.data;
};

export const createUserByAdmin = async (userData) => {
  const response = await api.post("/admin/create-user", userData);
  return response.data;
};

export const changePassword = async (oldPassword, newPassword) => {
  const response = await api.post("/auth/change-password", {
    old_password: oldPassword,
    new_password: newPassword,
  });
  return response.data;
};

export default api;