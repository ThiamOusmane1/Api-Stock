import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import { useNavigate } from "react-router-dom";
import "../App.css";

const LoginPage = () => {
  const { login } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false); // 🆕 Œil
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);
  const [showForgot, setShowForgot] = useState(false); // 🆕 Mot de passe oublié
  const [forgotEmail, setForgotEmail] = useState("");
  const [forgotMessage, setForgotMessage] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      console.log("🔐 [LoginPage] Tentative de connexion...");
      const userData = await login(username, password);
      console.log("✅ [LoginPage] Connexion réussie:", userData);
      if (userData.first_login) {
        navigate("/change-password");
      } else {
        navigate("/");
      }
    } catch (err) {
      console.error("❌ [LoginPage] Erreur:", err);
      setError("Identifiants incorrects. Veuillez réessayer.");
    } finally {
      setLoading(false);
    }
  };

  const handleForgotPassword = (e) => {
    e.preventDefault();
    // Simule l'envoi — en prod tu peux appeler une vraie route API
    setForgotMessage(`Un email a été envoyé à votre administrateur pour réinitialiser le mot de passe du compte lié à ${forgotEmail}.`);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🏗️ Gestion Échafaudage</h1>
          <p>Connectez-vous à votre compte</p>
        </div>

        {!showForgot ? (
          /* ===== FORMULAIRE LOGIN ===== */
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
              {/* 🆕 Champ avec bouton œil */}
              <div style={{ position: "relative" }}>
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Entrez votre mot de passe"
                  required
                  disabled={loading}
                  style={{ paddingRight: 48 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: "absolute",
                    right: 12,
                    top: "50%",
                    transform: "translateY(-50%)",
                    background: "none",
                    border: "none",
                    cursor: "pointer",
                    fontSize: 20,
                    color: "#666",
                    padding: 4,
                  }}
                  tabIndex={-1}
                  title={showPassword ? "Masquer" : "Afficher"}
                >
                  {showPassword ? "🙈" : "👁️"}
                </button>
              </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? "⏳ Connexion..." : "Se connecter"}
            </button>

            {/* 🆕 Lien mot de passe oublié */}
            <div style={{ textAlign: "center", marginTop: 8 }}>
              <button
                type="button"
                onClick={() => { setShowForgot(true); setError(null); }}
                style={{
                  background: "none",
                  border: "none",
                  color: "#667eea",
                  cursor: "pointer",
                  fontSize: 14,
                  textDecoration: "underline",
                }}
              >
                🔑 Mot de passe oublié ?
              </button>
            </div>
          </form>
        ) : (
          /* ===== FORMULAIRE MOT DE PASSE OUBLIÉ ===== */
          <form onSubmit={handleForgotPassword} className="login-form">
            <div style={{ textAlign: "center", marginBottom: 16 }}>
              <p style={{ fontSize: 40 }}>🔑</p>
              <h3 style={{ marginBottom: 8 }}>Mot de passe oublié</h3>
              <p style={{ color: "#666", fontSize: 14 }}>
                Entrez votre email. Votre administrateur sera notifié pour réinitialiser votre mot de passe.
              </p>
            </div>

            {!forgotMessage ? (
              <>
                <div className="form-group">
                  <label htmlFor="forgotEmail">Votre email</label>
                  <input
                    id="forgotEmail"
                    type="email"
                    value={forgotEmail}
                    onChange={(e) => setForgotEmail(e.target.value)}
                    placeholder="votre@email.com"
                    required
                    autoFocus
                  />
                </div>

                <button type="submit" className="btn-primary">
                  📧 Envoyer la demande
                </button>
              </>
            ) : (
              <div style={{
                background: "#d4edda",
                color: "#155724",
                padding: 16,
                borderRadius: 8,
                fontSize: 14,
                textAlign: "center",
                lineHeight: 1.6,
              }}>
                ✅ {forgotMessage}
              </div>
            )}

            <button
              type="button"
              onClick={() => { setShowForgot(false); setForgotMessage(null); setForgotEmail(""); }}
              className="btn-secondary"
            >
              ← Retour à la connexion
            </button>
          </form>
        )}

        <div style={{ textAlign: "center", marginTop: 16 }}>
          <p style={{ color: "#999", fontSize: 13 }}>
            Pas de compte ? Contactez votre administrateur.
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
