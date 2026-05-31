import React, { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";
import api from "../api";
import "../App.css";

const ChangePasswordPage = () => {
  const { user, logout } = useContext(AuthContext);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // 🆕 États pour afficher/masquer les mots de passe
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);

  const validatePassword = (password) => {
    if (password.length < 8) return "Le mot de passe doit contenir au moins 8 caractères";
    if (!/[A-Z]/.test(password)) return "Le mot de passe doit contenir au moins une majuscule";
    if (!/[a-z]/.test(password)) return "Le mot de passe doit contenir au moins une minuscule";
    if (!/[0-9]/.test(password)) return "Le mot de passe doit contenir au moins un chiffre";
    return null;
  };

  // 🆕 Force du mot de passe
  const getPasswordStrength = (password) => {
    if (!password) return null;
    let score = 0;
    if (password.length >= 8) score++;
    if (password.length >= 12) score++;
    if (/[A-Z]/.test(password)) score++;
    if (/[a-z]/.test(password)) score++;
    if (/[0-9]/.test(password)) score++;
    if (/[^A-Za-z0-9]/.test(password)) score++;
    if (score <= 2) return { label: "Faible", color: "#dc3545", width: "33%" };
    if (score <= 4) return { label: "Moyen", color: "#ffc107", width: "66%" };
    return { label: "Fort", color: "#28a745", width: "100%" };
  };

  const strength = getPasswordStrength(newPassword);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");

    if (newPassword !== confirmPassword) {
      setError("Les mots de passe ne correspondent pas");
      return;
    }

    const validationError = validatePassword(newPassword);
    if (validationError) {
      setError(validationError);
      return;
    }

    if (newPassword === oldPassword) {
      setError("Le nouveau mot de passe doit être différent de l'ancien");
      return;
    }

    setLoading(true);
    try {
      await api.post("/auth/change-password", {
        old_password: oldPassword,
        new_password: newPassword,
      });
      alert("✅ Mot de passe changé avec succès ! Vous allez être redirigé.");
      logout();
      navigate("/login");
    } catch (err) {
      console.error("Erreur changement mot de passe:", err);
      setError(err.response?.data?.detail || "Erreur lors du changement de mot de passe");
    } finally {
      setLoading(false);
    }
  };

  // Composant champ mot de passe avec œil
  const PasswordInput = ({ id, value, onChange, placeholder, show, onToggle, autoFocus }) => (
    <div style={{ position: "relative" }}>
      <input
        id={id}
        type={show ? "text" : "password"}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        required
        disabled={loading}
        autoFocus={autoFocus}
        style={{ paddingRight: 48, width: "100%" }}
      />
      <button
        type="button"
        onClick={onToggle}
        tabIndex={-1}
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
        title={show ? "Masquer" : "Afficher"}
      >
        {show ? "🙈" : "👁️"}
      </button>
    </div>
  );

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>🔒 Changement de mot de passe obligatoire</h1>
          <p>Bienvenue <strong>{user?.username}</strong>, veuillez changer votre mot de passe temporaire</p>
        </div>

        <form onSubmit={handleSubmit} className="login-form">

          {/* Mot de passe temporaire */}
          <div className="form-group">
            <label htmlFor="oldPassword">Mot de passe temporaire</label>
            <PasswordInput
              id="oldPassword"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              placeholder="Votre mot de passe temporaire"
              show={showOld}
              onToggle={() => setShowOld(!showOld)}
              autoFocus
            />
          </div>

          {/* Nouveau mot de passe */}
          <div className="form-group">
            <label htmlFor="newPassword">Nouveau mot de passe</label>
            <PasswordInput
              id="newPassword"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              placeholder="Minimum 8 caractères"
              show={showNew}
              onToggle={() => setShowNew(!showNew)}
            />
            <small style={{ color: "#666", fontSize: 12 }}>
              Doit contenir : majuscule, minuscule, chiffre (min. 8 caractères)
            </small>

            {/* 🆕 Jauge de force du mot de passe */}
            {newPassword && strength && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                  <span style={{ color: "#666" }}>Force :</span>
                  <span style={{ color: strength.color, fontWeight: 600 }}>{strength.label}</span>
                </div>
                <div style={{ height: 6, background: "#e0e0e0", borderRadius: 3, overflow: "hidden" }}>
                  <div style={{
                    height: "100%",
                    width: strength.width,
                    background: strength.color,
                    borderRadius: 3,
                    transition: "width 0.3s, background 0.3s",
                  }} />
                </div>
              </div>
            )}
          </div>

          {/* Confirmer mot de passe */}
          <div className="form-group">
            <label htmlFor="confirmPassword">Confirmer le nouveau mot de passe</label>
            <PasswordInput
              id="confirmPassword"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              placeholder="Confirmez votre mot de passe"
              show={showConfirm}
              onToggle={() => setShowConfirm(!showConfirm)}
            />
            {/* 🆕 Indicateur de correspondance */}
            {confirmPassword && (
              <small style={{
                fontSize: 12,
                color: newPassword === confirmPassword ? "#28a745" : "#dc3545",
                marginTop: 4,
                display: "block"
              }}>
                {newPassword === confirmPassword ? "✅ Les mots de passe correspondent" : "❌ Les mots de passe ne correspondent pas"}
              </small>
            )}
          </div>

          {error && <div className="error-message">{error}</div>}

          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? "⏳ Changement en cours..." : "🔐 Changer le mot de passe"}
          </button>

          <button type="button" onClick={logout} className="btn-secondary" disabled={loading}>
            🚪 Se déconnecter
          </button>
        </form>
      </div>
    </div>
  );
};

export default ChangePasswordPage;
