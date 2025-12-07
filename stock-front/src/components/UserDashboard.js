import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import RetraitArticleForm from "./RetraitArticleForm";
import "../App.css";

const UserDashboard = ({ user }) => {
  const { logout } = useContext(AuthContext);
  const [currentTab, setCurrentTab] = useState("retrait");

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>👤 Dashboard UTILISATEUR - {user.company_name}</h1>
          <p className="user-info">
            Bienvenue, <strong>{user.username}</strong>
          </p>
        </div>
        <button onClick={logout} className="btn-logout">
          🚪 Déconnexion
        </button>
      </header>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <button
          className={currentTab === "retrait" ? "nav-btn active" : "nav-btn"}
          onClick={() => setCurrentTab("retrait")}
        >
          📤 Effectuer un retrait
        </button>
      </nav>

      {/* Contenu */}
      <main className="dashboard-content">
        {currentTab === "retrait" && (
          <div>
            <RetraitArticleForm />
            <div className="card" style={{ marginTop: "20px" }}>
              <h3>ℹ️ Informations</h3>
              <p>Vous êtes connecté en tant qu'<strong>utilisateur</strong> de l'entreprise <strong>{user.company_name}</strong>.</p>
              <p>Vos permissions :</p>
              <ul>
                <li>✅ Effectuer des retraits d'articles</li>
                <li>⛔ Création/suppression d'articles (contactez votre administrateur)</li>
              </ul>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default UserDashboard;