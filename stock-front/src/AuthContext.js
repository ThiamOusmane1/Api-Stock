import React, { createContext, useState, useEffect } from "react";
import { login as apiLogin, getCurrentUser } from "./api";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // Charger l'utilisateur au démarrage
  useEffect(() => {
    const loadUser = async () => {
      try {
        const storedUserStr = localStorage.getItem("user");
        console.log("🔄 [AuthContext] Chargement depuis localStorage:", storedUserStr?.substring(0, 100) + "...");
        
        if (storedUserStr) {
          const storedUser = JSON.parse(storedUserStr);
          
          if (storedUser && storedUser.access_token) {
            console.log("✅ [AuthContext] Token trouvé, récupération user...");
            console.log("🔑 [AuthContext] Token:", storedUser.access_token.substring(0, 30) + "...");
            
            try {
              const userData = await getCurrentUser();
              console.log("✅ [AuthContext] User récupéré:", userData);
              
              const fullUser = { ...storedUser, ...userData };
              setUser(fullUser);
              console.log("✅ [AuthContext] User chargé avec succès");
            } catch (error) {
              console.error("❌ [AuthContext] Erreur getCurrentUser:", error.response?.status, error.response?.data);
              console.log("🧹 [AuthContext] Nettoyage localStorage");
              localStorage.removeItem("user");
              setUser(null);
            }
          } else {
            console.log("⚠️ [AuthContext] Pas de token dans le localStorage");
          }
        } else {
          console.log("ℹ️ [AuthContext] Aucun user dans localStorage");
        }
      } catch (error) {
        console.error("❌ [AuthContext] Erreur loadUser:", error);
        localStorage.removeItem("user");
        setUser(null);
      } finally {
        setLoading(false);
        console.log("✅ [AuthContext] Loading terminé");
      }
    };
    
    loadUser();
  }, []);

  const login = async (username, password) => {
    try {
      console.log("🔐 [AuthContext] Tentative login:", username);
      
      // Étape 1 : Login et récupération du token
      const loginData = await apiLogin(username, password);
      console.log("✅ [AuthContext] Login API réussi");
      console.log("🔑 [AuthContext] Token reçu:", loginData.access_token.substring(0, 30) + "...");
      
      // Sauvegarder le token IMMÉDIATEMENT pour l'intercepteur
      localStorage.setItem("user", JSON.stringify(loginData));
      console.log("💾 [AuthContext] Token sauvegardé dans localStorage");
      
      // Étape 2 : Récupérer les infos utilisateur avec le token
      console.log("📡 [AuthContext] Récupération des infos utilisateur...");
      const userData = await getCurrentUser();
      console.log("✅ [AuthContext] User data récupéré:", userData);
      
      // Étape 3 : Fusionner et sauvegarder
      const fullUser = { ...loginData, ...userData };
      localStorage.setItem("user", JSON.stringify(fullUser));
      setUser(fullUser);
      
      console.log("✅ [AuthContext] Login complet réussi pour:", userData.username);
      return fullUser;
      
    } catch (error) {
      console.error("❌ [AuthContext] Erreur login:", error);
      console.error("❌ [AuthContext] Détails:", error.response?.status, error.response?.data);
      
      // Nettoyer en cas d'erreur
      localStorage.removeItem("user");
      setUser(null);
      
      throw error;
    }
  };

  const logout = () => {
    console.log("🚪 [AuthContext] Déconnexion");
    localStorage.removeItem("user");
    setUser(null);
    console.log("✅ [AuthContext] Déconnexion réussie");
  };

  if (loading) {
    console.log("⏳ [AuthContext] Chargement en cours...");
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};