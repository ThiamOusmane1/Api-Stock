import React, {
  createContext,
  useState,
  useEffect,
  useRef,
  useCallback,
} from "react";
import { login as apiLogin, getCurrentUser } from "./api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  /* ======================= CONFIG ======================= */
  const SESSION_DURATION = 2 * 60 * 60 * 1000; // 2 heures
  const INACTIVITY_LIMIT = 30 * 60 * 1000; // 30 minutes
  const inactivityTimer = useRef(null);

  /* ======================= LOGOUT ======================= */
  const logout = useCallback(() => {
    console.log("🚪 [AuthContext] Déconnexion");
    localStorage.removeItem("user");
    setUser(null);
  }, []);

  /* ======================= INACTIVITÉ ======================= */
  const resetInactivityTimer = useCallback(() => {
    if (inactivityTimer.current) {
      clearTimeout(inactivityTimer.current);
    }

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

        if (!storedUserStr) {
          setUser(null);
          return;
        }

        const storedUser = JSON.parse(storedUserStr);

        // ⏰ Session expirée
        if (storedUser.expiresAt && storedUser.expiresAt < Date.now()) {
          console.log("⏰ [AuthContext] Session expirée");
          localStorage.removeItem("user");
          setUser(null);
          return;
        }

        if (!storedUser.access_token) {
          setUser(null);
          return;
        }

        // 🔐 Vérifier token côté backend
        const userData = await getCurrentUser();

        const fullUser = { ...storedUser, ...userData };
        setUser(fullUser);
        resetInactivityTimer();

        console.log("✅ [AuthContext] Session restaurée");
      } catch (error) {
        console.error("❌ [AuthContext] Erreur chargement session", error);
        localStorage.removeItem("user");
        setUser(null);
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

      // 1️⃣ Login → token
      const loginData = await apiLogin(username, password);

      // 2️⃣ Sauvegarde immédiate du token
      localStorage.setItem("user", JSON.stringify(loginData));

      // 3️⃣ Récupération user
      const userData = await getCurrentUser();

      const fullUser = {
        ...loginData,
        ...userData,
        expiresAt: Date.now() + SESSION_DURATION,
      };

      localStorage.setItem("user", JSON.stringify(fullUser));
      setUser(fullUser);
      resetInactivityTimer();

      console.log("✅ [AuthContext] Login réussi:", userData.username);
      return fullUser;
    } catch (error) {
      console.error("❌ [AuthContext] Erreur login:", error);
      localStorage.removeItem("user");
      setUser(null);
      throw error;
    }
  };

  /* ======================= SURVEILLANCE ACTIVITÉ ======================= */
  useEffect(() => {
    if (!user) return;

    const events = ["mousemove", "keydown", "click", "scroll"];

    events.forEach((event) =>
      window.addEventListener(event, resetInactivityTimer)
    );

    resetInactivityTimer();

    return () => {
      events.forEach((event) =>
        window.removeEventListener(event, resetInactivityTimer)
      );
      if (inactivityTimer.current) {
        clearTimeout(inactivityTimer.current);
      }
    };
  }, [user, resetInactivityTimer]);

  /* ======================= RENDER ======================= */
  if (loading) {
    return null; // ou loader si tu veux
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};
