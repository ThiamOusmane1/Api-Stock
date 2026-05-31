import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import RetraitArticleForm from "./RetraitArticleForm";
import ArticleList from "./ArticleList";
import HistoriqueChantiers from "./historiqueChantiers";
import "../App.css";

// Labels des sous-rôles
const SUB_ROLE_LABELS = {
  aucun:              { label: "Utilisateur",           icon: "👤", color: "#667eea" },
  commercial:         { label: "Commercial",            icon: "💼", color: "#28a745" },
  magasinier:         { label: "Magasinier",            icon: "🏭", color: "#fd7e14" },
  chef_chantier:      { label: "Chef de chantier",      icon: "🦺", color: "#dc3545" },
  gestionnaire_stock: { label: "Gestionnaire de stock", icon: "📦", color: "#6f42c1" },
};

const UserDashboard = ({ user }) => {
  const { logout, permissions } = useContext(AuthContext);
  const [currentTab, setCurrentTab] = useState("retrait");

  // Récupérer le label du sous-rôle
  const subRoleInfo = SUB_ROLE_LABELS[user.sub_role || "aucun"] || SUB_ROLE_LABELS.aucun;

  // Construire les onglets selon les permissions
  const tabs = [];

  if (permissions?.faire_retraits !== false) {
    tabs.push({ id: "retrait", label: "Retrait", icon: "📤" });
  }

  if (permissions?.voir_stock !== false) {
    tabs.push({ id: "stock", label: "Stock", icon: "📦" });
  }

  if (permissions?.calcul_echafaudage) {
    tabs.push({ id: "calcul", label: "Calcul", icon: "🧮" });
  }

  if (permissions?.historique_chantiers) {
    tabs.push({ id: "historique", label: "Historique", icon: "📊" });
  }

  // Si aucun onglet disponible (cas extrême)
  if (tabs.length === 0) {
    tabs.push({ id: "info", label: "Infos", icon: "ℹ️" });
  }

  // S'assurer que le tab courant est valide
  const validTab = tabs.find(t => t.id === currentTab) ? currentTab : tabs[0].id;

  return (
    <div className="dashboard-container">

      {/* ===== HEADER ===== */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>{subRoleInfo.icon} {user.company_name || "Mon espace"}</h1>
          <p className="user-info">
            <strong>{user.username}</strong> ·{" "}
            <span style={{ color: subRoleInfo.color, fontWeight: 600 }}>
              {subRoleInfo.label}
            </span>
          </p>
        </div>
        <button onClick={logout} className="btn-logout">🚪</button>
      </header>

      {/* ===== NAV DESKTOP ===== */}
      {tabs.length > 1 && (
        <nav className="dashboard-nav desktop-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={validTab === tab.id ? "nav-btn active" : "nav-btn"}
              onClick={() => setCurrentTab(tab.id)}
            >
              {tab.icon} {tab.label}
            </button>
          ))}
        </nav>
      )}

      {/* ===== CONTENU ===== */}
      <main className="dashboard-content">

        {/* Retrait */}
        {validTab === "retrait" && permissions?.faire_retraits !== false && (
          <RetraitArticleForm />
        )}

        {/* Stock */}
        {validTab === "stock" && permissions?.voir_stock !== false && (
          <ArticleList />
        )}

        {/* Calcul échafaudage */}
        {validTab === "calcul" && permissions?.calcul_echafaudage && (
          <ArticleList />
        )}

        {/* Historique chantiers */}
        {validTab === "historique" && permissions?.historique_chantiers && (
          <HistoriqueChantiers />
        )}

        {/* Infos / Accès refusé */}
        {validTab === "info" && (
          <div className="card" style={{ textAlign: "center", padding: 40 }}>
            <p style={{ fontSize: 48, marginBottom: 16 }}>🔒</p>
            <h3>Accès limité</h3>
            <p style={{ color: "#666", marginTop: 8 }}>
              Contactez votre administrateur pour obtenir des accès.
            </p>
          </div>
        )}

        {/* Carte infos permissions */}
        <div className="card" style={{ marginTop: 16 }}>
          <h3 style={{ marginBottom: 12 }}>
            {subRoleInfo.icon} Vos accès —{" "}
            <span style={{ color: subRoleInfo.color }}>{subRoleInfo.label}</span>
          </h3>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(160px, 1fr))", gap: 8 }}>
            {[
              { key: "voir_stock",           label: "Voir le stock",        icon: "📦" },
              { key: "faire_retraits",       label: "Retraits",             icon: "📤" },
              { key: "calcul_echafaudage",   label: "Calcul échafaudage",   icon: "🧮" },
              { key: "historique_chantiers", label: "Historique chantiers", icon: "📊" },
              { key: "ajouter_articles",     label: "Ajouter articles",     icon: "➕" },
              { key: "supprimer_articles",   label: "Supprimer articles",   icon: "🗑️" },
              { key: "export_pdf_excel",     label: "Export PDF/Excel",     icon: "📄" },
            ].map(({ key, label, icon }) => {
              const allowed = permissions?.[key] !== false && permissions?.[key];
              return (
                <div
                  key={key}
                  style={{
                    padding: "8px 12px",
                    borderRadius: 8,
                    background: allowed ? "#d4edda" : "#f8d7da",
                    color: allowed ? "#155724" : "#721c24",
                    fontSize: 13,
                    fontWeight: 500,
                  }}
                >
                  {icon} {allowed ? "✅" : "❌"} {label}
                </div>
              );
            })}
          </div>
        </div>
      </main>

      {/* ===== NAV MOBILE FIXE EN BAS ===== */}
      {tabs.length > 0 && (
        <nav className="mobile-nav">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              className={validTab === tab.id ? "mobile-nav-btn active" : "mobile-nav-btn"}
              onClick={() => setCurrentTab(tab.id)}
            >
              <span className="mobile-nav-icon">{tab.icon}</span>
              <span className="mobile-nav-label">{tab.label}</span>
            </button>
          ))}
        </nav>
      )}
    </div>
  );
};

export default UserDashboard;
