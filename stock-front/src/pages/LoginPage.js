import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import { useNavigate } from "react-router-dom";
import "../App.css";

const LoginPage = () => {
  const { login } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    try {
      console.log("🔐 [LoginPage] Tentative de connexion...");
      const userData = await login(username, password);
      console.log("✅ [LoginPage] Connexion réussie:", userData);
      
      // Vérifier si c'est la première connexion
      if (userData.first_login) {
        console.log("⚠️ [LoginPage] Première connexion détectée, redirection...");
        navigate("/change-password");
      } else {
        console.log("✅ [LoginPage] Redirection vers dashboard");
        navigate("/");
      }
    } catch (err) {
      console.error("❌ [LoginPage] Erreur:", err);
      setError("Identifiants incorrects. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🏗️ Gestion Échafaudage</h1>
          <p>Connectez-vous à votre compte</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Nom d'utilisateur</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Entrez votre nom d'utilisateur"
              required
              disabled={loading}
              autoFocus
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Mot de passe</label>
            <input
              id="password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="Entrez votre mot de passe"
              required
              disabled={loading}
            />
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "Connexion..." : "Se connecter"}
          </button>
        </form>

        <div className="login-footer">
          <p className="text-muted">
            Vous n'avez pas de compte ? Contactez votre administrateur.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;