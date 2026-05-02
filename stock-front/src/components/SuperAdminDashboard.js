import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../AuthContext";
import { fetchCompanies, createCompany, createAdmin, companyAction } from "../api";
import "../App.css";

const API_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

const SuperAdminDashboard = ({ user }) => {
  const { logout } = useContext(AuthContext);
  const [currentTab, setCurrentTab] = useState("companies");
  const [companies, setCompanies] = useState([]);
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateCompany, setShowCreateCompany] = useState(false);
  const [showCreateAdmin, setShowCreateAdmin] = useState(false);
  const [message, setMessage] = useState(null);
  const [companyName, setCompanyName] = useState("");
  const [adminUsername, setAdminUsername] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [selectedCompanyId, setSelectedCompanyId] = useState("");

  const tabs = [
    { id: "companies", label: "Entreprises", icon: "🏢" },
    { id: "admins", label: "Admins", icon: "👨‍💼" },
  ];

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    loadCompanies();
    loadAdmins();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const data = await fetchCompanies();
      setCompanies(data);
    } catch (err) {
      setMessage({ type: "error", text: "Erreur de chargement des entreprises" });
    } finally {
      setLoading(false);
    }
  };

  const loadAdmins = async () => {
    try {
      const response = await fetch(`${API_URL}/admin/list-admins`, {
        headers: {
          Authorization: `Bearer ${JSON.parse(localStorage.getItem("user")).access_token}`,
        },
      });
      const data = await response.json();
      setAdmins(data);
    } catch (err) {
      console.error("Erreur chargement admins:", err);
    }
  };

  const handleCreateCompany = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      await createCompany(companyName);
      setMessage({ type: "success", text: `Entreprise "${companyName}" créée !` });
      setCompanyName("");
      setShowCreateCompany(false);
      loadCompanies();
    } catch (err) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Erreur création entreprise" });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAdmin = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await createAdmin({
        username: adminUsername,
        email: adminEmail,
        company_id: parseInt(selectedCompanyId),
      });
      setMessage({ type: "success", text: `Admin "${result.username}" créé ! Email envoyé à ${result.email}.` });
      setAdminUsername("");
      setAdminEmail("");
      setSelectedCompanyId("");
      setShowCreateAdmin(false);
      loadAdmins();
    } catch (err) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Erreur création admin" });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteAdmin = async (adminId, adminName) => {
    if (!window.confirm(`Supprimer l'admin "${adminName}" ?`)) return;
    try {
      const response = await fetch(`${API_URL}/admin/users/${adminId}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${JSON.parse(localStorage.getItem("user")).access_token}`,
        },
      });
      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Erreur suppression");
      }
      setMessage({ type: "success", text: `Admin "${adminName}" supprimé` });
      loadAdmins();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    }
  };

  const handleCompanyAction = async (companyId, actionType) => {
    setLoading(true);
    try {
      await companyAction(companyId, actionType);
      const labels = { suspend: "suspendue", activate: "réactivée", terminate: "résiliée" };
      setMessage({ type: "success", text: `✅ Entreprise ${labels[actionType]}` });
      loadCompanies();
    } catch (err) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Erreur action entreprise" });
    } finally {
      setLoading(false);
    }
  };

  const statusBadge = (status) => {
    const styles = {
      active:     { background: "#d4edda", color: "#155724", padding: "2px 8px", borderRadius: 10, fontSize: 12 },
      suspended:  { background: "#fff3cd", color: "#856404", padding: "2px 8px", borderRadius: 10, fontSize: 12 },
      terminated: { background: "#f8d7da", color: "#721c24", padding: "2px 8px", borderRadius: 10, fontSize: 12 },
    };
    const labels = { active: "✅ Active", suspended: "⏸ Suspendue", terminated: "🗑️ Résiliée" };
    return <span style={styles[status] || styles.active}>{labels[status] || status}</span>;
  };

  return (
    <div className="dashboard-container">

      {/* ===== HEADER ===== */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>👑 SuperAdmin</h1>
          <p className="user-info"><strong>{user.username}</strong></p>
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

      {/* ===== MESSAGE ===== */}
      {message && (
        <div className={`message ${message.type}`} style={{ margin: "12px 20px" }}>
          {message.text}
          <button onClick={() => setMessage(null)} style={{ float: "right", background: "none", border: "none", cursor: "pointer", fontSize: 16 }}>✕</button>
        </div>
      )}

      {/* ===== CONTENU ===== */}
      <main className="dashboard-content">

        {/* ---- ONGLET ENTREPRISES ---- */}
        {currentTab === "companies" && (
          <div className="card">
            <div className="table-header">
              <h2>📋 Entreprises</h2>
              <button className="btn-add" onClick={() => setShowCreateCompany(!showCreateCompany)}>
                ➕ Nouvelle entreprise
              </button>
            </div>

            {showCreateCompany && (
              <form onSubmit={handleCreateCompany} className="ajout-form">
                <input
                  type="text"
                  placeholder="Nom de l'entreprise"
                  value={companyName}
                  onChange={(e) => setCompanyName(e.target.value)}
                  className="input-ajout"
                  required
                />
                <button type="submit" className="btn-add" disabled={loading}>
                  {loading ? "⏳..." : "Créer"}
                </button>
                <button type="button" onClick={() => setShowCreateCompany(false)} className="btn-reset">
                  Annuler
                </button>
              </form>
            )}

            {loading && <p style={{ padding: 10, color: "#666" }}>⏳ Chargement...</p>}

            {companies.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: "#666" }}>
                <p style={{ fontSize: 40, marginBottom: 10 }}>🏢</p>
                <p>Aucune entreprise enregistrée</p>
                <p style={{ fontSize: 13, marginTop: 5 }}>Créez votre première entreprise ci-dessus</p>
              </div>
            ) : (
              <>
                {/* Vue MOBILE : cartes */}
                <div className="mobile-cards">
                  {companies.map((company) => {
                    const nbAdmins = admins.filter((a) => a.company_id === company.id).length;
                    return (
                      <div key={company.id} className="mobile-card">
                        <div className="mobile-card-header">
                          <strong>{company.name}</strong>
                          {statusBadge(company.status)}
                        </div>
                        <div className="mobile-card-body">
                          <span>👨‍💼 {nbAdmins} admin(s)</span>
                        </div>
                        <div className="mobile-card-actions">
                          <button onClick={() => handleCompanyAction(company.id, "suspend")} className="btn-action" disabled={loading}>⏸ Suspendre</button>
                          <button onClick={() => handleCompanyAction(company.id, "activate")} className="btn-action" disabled={loading}>▶️ Réactiver</button>
                          <button onClick={() => handleCompanyAction(company.id, "terminate")} className="btn-action terminate" disabled={loading}>🗑️ Résilier</button>
                          <button
                            onClick={() => { setSelectedCompanyId(company.id); setShowCreateAdmin(true); setCurrentTab("admins"); }}
                            className="btn-add"
                            style={{ fontSize: 12, padding: "6px 12px" }}
                          >
                            ➕ Admin
                          </button>
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Vue DESKTOP : tableau */}
                <div className="table-container desktop-table">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Nom</th>
                        <th>Statut</th>
                        <th>Admins</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {companies.map((company) => {
                        const nbAdmins = admins.filter((a) => a.company_id === company.id).length;
                        return (
                          <tr key={company.id}>
                            <td>{company.id}</td>
                            <td><strong>{company.name}</strong></td>
                            <td>{statusBadge(company.status)}</td>
                            <td>{nbAdmins}</td>
                            <td>
                              <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                                <button onClick={() => handleCompanyAction(company.id, "suspend")} className="btn-action" disabled={loading}>⏸️ Suspendre</button>
                                <button onClick={() => handleCompanyAction(company.id, "activate")} className="btn-action" disabled={loading}>▶️ Réactiver</button>
                                <button onClick={() => handleCompanyAction(company.id, "terminate")} className="btn-action terminate" disabled={loading}>🗑️ Résilier</button>
                                <button
                                  onClick={() => { setSelectedCompanyId(company.id); setShowCreateAdmin(true); setCurrentTab("admins"); }}
                                  className="btn-add"
                                  style={{ fontSize: 12, padding: "6px 12px" }}
                                >
                                  ➕ Créer un admin
                                </button>
                              </div>
                            </td>
                          </tr>
                        );
                      })}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}

        {/* ---- ONGLET ADMINS ---- */}
        {currentTab === "admins" && (
          <div className="card">
            <div className="table-header">
              <h2>👨‍💼 Admins</h2>
              <button className="btn-add" onClick={() => setShowCreateAdmin(!showCreateAdmin)}>
                ➕ Nouvel admin
              </button>
            </div>

            {showCreateAdmin && (
              <form onSubmit={handleCreateAdmin} className="ajout-form">
                <input
                  type="text"
                  placeholder="Nom d'utilisateur"
                  value={adminUsername}
                  onChange={(e) => setAdminUsername(e.target.value)}
                  className="input-ajout"
                  required
                />
                <input
                  type="email"
                  placeholder="Email"
                  value={adminEmail}
                  onChange={(e) => setAdminEmail(e.target.value)}
                  className="input-ajout"
                  required
                />
                <select
                  value={selectedCompanyId}
                  onChange={(e) => setSelectedCompanyId(e.target.value)}
                  className="input-ajout"
                  required
                >
                  <option value="">-- Sélectionner une entreprise --</option>
                  {companies.map((c) => (
                    <option key={c.id} value={c.id}>{c.name}</option>
                  ))}
                </select>
                <button type="submit" className="btn-add" disabled={loading}>
                  {loading ? "⏳..." : "Créer"}
                </button>
                <button type="button" onClick={() => setShowCreateAdmin(false)} className="btn-reset">
                  Annuler
                </button>
              </form>
            )}

            {admins.length === 0 ? (
              <div style={{ textAlign: "center", padding: 40, color: "#666" }}>
                <p style={{ fontSize: 40, marginBottom: 10 }}>👨‍💼</p>
                <p>Aucun admin créé</p>
              </div>
            ) : (
              <>
                {/* Vue MOBILE : cartes */}
                <div className="mobile-cards">
                  {admins.map((admin) => (
                    <div key={admin.id} className="mobile-card">
                      <div className="mobile-card-header">
                        <strong>{admin.username}</strong>
                        {admin.first_login
                          ? <span style={{ color: "orange", fontSize: 12 }}>⚠️ 1ère connexion</span>
                          : <span style={{ color: "green", fontSize: 12 }}>✅ Actif</span>
                        }
                      </div>
                      <div className="mobile-card-body">
                        <span>📧 {admin.email || "-"}</span>
                        <span>🏢 {admin.company_name || <span style={{ color: "red" }}>⚠️ Sans entreprise</span>}</span>
                        <span>📅 {admin.created_at ? new Date(admin.created_at).toLocaleDateString("fr-FR") : "-"}</span>
                      </div>
                      <div className="mobile-card-actions">
                        <button
                          onClick={() => handleDeleteAdmin(admin.id, admin.username)}
                          style={{ padding: "8px 14px", backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 13 }}
                        >
                          🗑️ Supprimer
                        </button>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Vue DESKTOP : tableau */}
                <div className="table-container desktop-table">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Username</th>
                        <th>Email</th>
                        <th>Entreprise</th>
                        <th>Créé le</th>
                        <th>1ère connexion</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {admins.map((admin) => (
                        <tr key={admin.id}>
                          <td>{admin.id}</td>
                          <td><strong>{admin.username}</strong></td>
                          <td>{admin.email || "-"}</td>
                          <td>{admin.company_name || <span style={{ color: "red" }}>⚠️ Sans entreprise</span>}</td>
                          <td>{admin.created_at ? new Date(admin.created_at).toLocaleDateString("fr-FR") : "-"}</td>
                          <td>
                            {admin.first_login
                              ? <span style={{ color: "orange" }}>⚠️ Oui</span>
                              : <span style={{ color: "green" }}>✅ Non</span>
                            }
                          </td>
                          <td>
                            <button
                              onClick={() => handleDeleteAdmin(admin.id, admin.username)}
                              style={{ padding: "5px 12px", backgroundColor: "#dc3545", color: "white", border: "none", borderRadius: 5, cursor: "pointer", fontSize: 12 }}
                            >
                              🗑️ Supprimer
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </>
            )}
          </div>
        )}
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

export default SuperAdminDashboard;
