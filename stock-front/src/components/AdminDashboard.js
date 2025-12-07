import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import ArticleList from "./ArticleList";
import RetraitArticleForm from "./RetraitArticleForm";
import AdminUsersManagement from "./AdminUsersManagement";
import "../App.css";

const AdminDashboard = ({ user }) => {
  const { logout } = useContext(AuthContext);
  const [currentTab, setCurrentTab] = useState("stock");

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🏢 Dashboard ADMIN - {user.company_name}</h1>
          <p className="user-info">
            Bienvenue, <strong>{user.username}</strong> (Administrateur)
          </p>
        </div>
        <button onClick={logout} className="btn-logout">
          🚪 Déconnexion
        </button>
      </header>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <button
          className={currentTab === "stock" ? "nav-btn active" : "nav-btn"}
          onClick={() => setCurrentTab("stock")}
        >
          📦 Gestion du Stock
        </button>
        <button
          className={currentTab === "retrait" ? "nav-btn active" : "nav-btn"}
          onClick={() => setCurrentTab("retrait")}
        >
          📤 Retrait d'Articles
        </button>
        <button
          className={currentTab === "users" ? "nav-btn active" : "nav-btn"}
          onClick={() => setCurrentTab("users")}
        >
          👥 Gestion Utilisateurs
        </button>
      </nav>

      {/* Contenu */}
      <main className="dashboard-content">
        {currentTab === "stock" && <ArticleList />}
        {currentTab === "retrait" && <RetraitArticleForm />}
        {currentTab === "users" && <AdminUsersManagement user={user} />}
      </main>
    </div>
  );
};

export default AdminDashboard;