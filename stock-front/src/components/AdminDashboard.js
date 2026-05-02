import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import ArticleList from "./ArticleList";
import RetraitArticleForm from "./RetraitArticleForm";
import AdminUsersManagement from "./AdminUsersManagement";
import "../App.css";

const AdminDashboard = ({ user }) => {
  const { logout } = useContext(AuthContext);
  const [currentTab, setCurrentTab] = useState("stock");

  const tabs = [
    { id: "stock",   label: "Stock",   icon: "📦" },
    { id: "retrait", label: "Retrait", icon: "📤" },
    { id: "users",   label: "Équipe",  icon: "👥" },
  ];

  return (
    <div className="dashboard-container">

      {/* ===== HEADER ===== */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>🏢 {user.company_name || "Admin"}</h1>
          <p className="user-info">
            <strong>{user.username}</strong> · Administrateur
          </p>
        </div>
        <button onClick={logout} className="btn-logout">🚪 Déconnexion</button>
      </header>

      {/* ===== NAV DESKTOP ===== */}
      <nav className="dashboard-nav desktop-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={currentTab === tab.id ? "nav-btn active" : "nav-btn"}
            onClick={() => setCurrentTab(tab.id)}
          >
            {tab.icon} {tab.label}
          </button>
        ))}
      </nav>

      {/* ===== CONTENU ===== */}
      <main className="dashboard-content">
        {currentTab === "stock"   && <ArticleList />}
        {currentTab === "retrait" && <RetraitArticleForm />}
        {currentTab === "users"   && <AdminUsersManagement user={user} />}
      </main>

      {/* ===== NAV MOBILE FIXE EN BAS ===== */}
      <nav className="mobile-nav">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            className={currentTab === tab.id ? "mobile-nav-btn active" : "mobile-nav-btn"}
            onClick={() => setCurrentTab(tab.id)}
          >
            <span className="mobile-nav-icon">{tab.icon}</span>
            <span className="mobile-nav-label">{tab.label}</span>
          </button>
        ))}
      </nav>
    </div>
  );
};

export default AdminDashboard;
