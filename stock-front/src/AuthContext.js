import React, {
  createContext,
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import { login as apiLogin, getCurrentUser } from "./api";

export const AuthContext = createContext();

const API_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

// ✅ Récupérer les permissions depuis l'API
const fetchPermissions = async (token) => {
  try {
    const response = await fetch(`${API_URL}/me/permissions`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (response.ok) return await response.json();
  } catch (err) {
    console.error("❌ Erreur chargement permissions:", err);
  }
  // Permissions par défaut si erreur
  return {
    sub_role: "aucun",
    voir_stock: true,
    faire_retraits: true,
    calcul_echafaudage: true,
    historique_chantiers: true,
    ajouter_articles: false,
    supprimer_articles: false,
    export_pdf_excel: true,
    gerer_utilisateurs: false,
  };
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [permissions, setPermissions] = useState(null); // 🆕 Permissions
  const [loading, setLoading] = useState(true);

  const SESSION_DURATION = 2 * 60 * 60 * 1000; // 2 heures
  const INACTIVITY_LIMIT = 30 * 60 * 1000; // 30 minutes
  const inactivityTimer = useRef(null);

  /* ======================= LOGOUT ======================= */
  const logout = useCallback(() => {
    console.log("🚪 [AuthContext] Déconnexion");
    localStorage.removeItem("user");
    setUser(null);
    setPermissions(null); // 🆕 Réinitialiser les permissions
  }, []);

  /* ======================= INACTIVITÉ ======================= */
  const resetInactivityTimer = useCallback(() => {
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    inactivityTimer.current = setTimeout(() => {
      console.log("⏰ [AuthContext] Déconnexion par inactivité");
      logout();
    }, INACTIVITY_LIMIT);
  }, [logout, INACTIVITY_LIMIT]);

  /* ======================= CHARGEMENT SESSION ======================= */
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUserStr = localStorage.getItem("user");
        if (!storedUserStr) { setUser(null); return; }

        const storedUser = JSON.parse(storedUserStr);

        if (storedUser.expiresAt && storedUser.expiresAt < Date.now()) {
          console.log("⏰ [AuthContext] Session expirée");
          localStorage.removeItem("user");
          setUser(null);
          return;
        }

        if (!storedUser.access_token) { setUser(null); return; }

        // Vérifier token côté backend
        const userData = await getCurrentUser();
        const fullUser = { ...storedUser, ...userData };
        setUser(fullUser);

        // 🆕 Charger les permissions
        const perms = await fetchPermissions(storedUser.access_token);
        setPermissions(perms);
        console.log("✅ [AuthContext] Permissions chargées:", perms.sub_role);

        resetInactivityTimer();
        console.log("✅ [AuthContext] Session restaurée");
      } catch (error) {
        console.error("❌ [AuthContext] Erreur chargement session", error);
        localStorage.removeItem("user");
        setUser(null);
        setPermissions(null);
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, [resetInactivityTimer]);

  /* ======================= LOGIN ======================= */
  const login = async (username, password) => {
    try {
      console.log("🔐 [AuthContext] Tentative login:", username);

      // 1 — Login → token
      const loginData = await apiLogin(username, password);
      localStorage.setItem("user", JSON.stringify(loginData));

      // 2 — Récupération user
      const userData = await getCurrentUser();

      const fullUser = {
        ...loginData,
        ...userData,
        expiresAt: Date.now() + SESSION_DURATION,
      };

      localStorage.setItem("user", JSON.stringify(fullUser));
      setUser(fullUser);

      // 🆕 3 — Charger les permissions
      const perms = await fetchPermissions(loginData.access_token);
      setPermissions(perms);
      console.log("✅ [AuthContext] Permissions:", perms.sub_role);

      resetInactivityTimer();
      console.log("✅ [AuthContext] Login réussi:", userData.username);
      return fullUser;
    } catch (error) {
      console.error("❌ [AuthContext] Erreur login:", error);
      localStorage.removeItem("user");
      setUser(null);
      setPermissions(null);
      throw error;
    }
  };

  /* ======================= SURVEILLANCE ACTIVITÉ ======================= */
  useEffect(() => {
    if (!user) return;
    const events = ["mousemove", "keydown", "click", "scroll"];
    events.forEach((event) => window.addEventListener(event, resetInactivityTimer));
    resetInactivityTimer();
    return () => {
      events.forEach((event) => window.removeEventListener(event, resetInactivityTimer));
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    };
  }, [user, resetInactivityTimer]);

  if (loading) return null;

  return (
    <AuthContext.Provider value={{ user, permissions, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
