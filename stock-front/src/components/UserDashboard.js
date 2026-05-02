import React, { useContext } from "react";
import { AuthContext } from "../AuthContext";
import RetraitArticleForm from "./RetraitArticleForm";
import "../App.css";

const UserDashboard = ({ user }) => {
  const { logout } = useContext(AuthContext);

  return (
    <div className="dashboard-container">

      {/* ===== HEADER ===== */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>👤 {user.company_name || "Mon espace"}</h1>
          <p className="user-info">
            <strong>{user.username}</strong> · Utilisateur
          </p>
        </div>
        <button onClick={logout} className="btn-logout">🚪 Déconnexion</button>
      </header>

      {/* ===== NAV DESKTOP ===== */}
      <nav className="dashboard-nav desktop-nav">
        <button className="nav-btn active">📤 Retrait d'articles</button>
      </nav>

      {/* ===== CONTENU ===== */}
      <main className="dashboard-content">
        <RetraitArticleForm />

        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginBottom: 10 }}>ℹ️ Vos permissions</h3>
          <p style={{ color: "#666", fontSize: 14, marginBottom: 8 }}>
            Connecté en tant qu'<strong>utilisateur</strong> de <strong>{user.company_name}</strong>.
          </p>
          <ul style={{ paddingLeft: 20, fontSize: 14, lineHeight: 2 }}>
            <li>✅ Effectuer des retraits d'articles</li>
            <li>⛔ Création/suppression d'articles (contacter votre administrateur)</li>
          </ul>
        </div>
      </main>

      {/* ===== NAV MOBILE FIXE EN BAS ===== */}
      <nav className="mobile-nav">
        <button className="mobile-nav-btn active">
          <span className="mobile-nav-icon">📤</span>
          <span className="mobile-nav-label">Retrait</span>
        </button>
      </nav>
    </div>
  );
};

export default UserDashboard;
