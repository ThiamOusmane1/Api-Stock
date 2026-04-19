import React, { useState, useEffect, useContext } from "react";
import { AuthContext } from "../AuthContext";
import { fetchCompanies, createCompany, createAdmin, companyAction } from "../api"; // ✅ companyAction importé
import "../App.css";

const SuperAdminDashboard = ({ user }) => {
  const { logout } = useContext(AuthContext);
  const [currentTab, setCurrentTab] = useState("companies");
  const [companies, setCompanies] = useState([]);
  const [admins, setAdmins] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreateCompany, setShowCreateCompany] = useState(false);
  const [showCreateAdmin, setShowCreateAdmin] = useState(false);
  const [message, setMessage] = useState(null);

  // Form states
  const [companyName, setCompanyName] = useState("");
  const [adminUsername, setAdminUsername] = useState("");
  const [adminEmail, setAdminEmail] = useState("");
  const [selectedCompanyId, setSelectedCompanyId] = useState("");

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
      console.error("Erreur chargement entreprises:", err);
      setMessage({ type: "error", text: "Erreur de chargement des entreprises" });
    } finally {
      setLoading(false);
    }
  };

  const loadAdmins = async () => {
    try {
      const response = await fetch("http://127.0.0.1:8000/admin/list-admins", {
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
      
      setMessage({
        type: "success",
        text: `Administrateur "${result.username}" créé avec succès.
      Un email contenant les identifiants temporaires a été envoyé à ${result.email}.`,
      });
      
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

  // ✅ CORRIGÉ : Utilise la fonction companyAction d'api.js
  const handleCompanyAction = async (companyId, actionType) => {
    setLoading(true);
    try {
      // ✅ On utilise la fonction centralisée
      await companyAction(companyId, actionType);
      
      const actionLabels = {
        suspend: "suspendue",
        activate: "réactivée",
        terminate: "résiliée"
      };
      
      setMessage({ 
        type: "success", 
        text: `✅ Entreprise ${actionLabels[actionType]} avec succès` 
      });
      
      loadCompanies();
    } catch (err) {
      console.error("Erreur action entreprise:", err);
      setMessage({ 
        type: "error", 
        text: err.response?.data?.detail || "Erreur lors de l'action sur l'entreprise" 
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <div className="header-left">
          <h1>👑 Dashboard SUPERADMIN</h1>
          <p className="user-info">Bienvenue, <strong>{user.username}</strong></p>
        </div>
        <button onClick={logout} className="btn-logout">
          🚪 Déconnexion
        </button>
      </header>

      {/* Navigation */}
      <nav className="dashboard-nav">
        <button
          className={currentTab === "companies" ? "nav-btn active" : "nav-btn"}
          onClick={() => setCurrentTab("companies")}
        >
          🏢 Entreprises
        </button>
        <button
          className={currentTab === "admins" ? "nav-btn active" : "nav-btn"}
          onClick={() => setCurrentTab("admins")}
        >
          👨‍💼 Admins
        </button>
      </nav>

      {/* Message */}
      {message && (
        <div className={`message ${message.type}`} style={{ margin: "20px 40px" }}>
          {message.text}
          <button onClick={() => setMessage(null)} style={{ float: "right", background: "none", border: "none", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {/* Contenu */}
      <main className="dashboard-content">
        {/* ONGLET ENTREPRISES */}
        {currentTab === "companies" && (
          <div className="card">
            <div className="table-header">
              <h2>📋 Liste des entreprises</h2>
              <button
                onClick={() => setShowCreateCompany(!showCreateCompany)}
                className="btn-add"
              >
                ➕ Créer une entreprise
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
                  {loading ? "Création..." : "Créer"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateCompany(false)}
                  className="btn-reset"
                >
                  Annuler
                </button>
              </form>
            )}

            {loading && <p>⏳ Chargement...</p>}

            {companies.length === 0 ? (
              <p style={{ textAlign: "center", padding: "40px", color: "#666" }}>
                Aucune entreprise enregistrée
              </p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Nom de l'entreprise</th>
                      <th>Nombre d'admins</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {companies.map((company) => {
                      const companyAdmins = admins.filter(a => a.company_id === company.id);
                      return (
                        <tr key={company.id}>
                          <td>{company.id}</td>
                          <td><strong>{company.name}</strong></td>
                          <td>{companyAdmins.length}</td>
                          <td>
                            <button
                              onClick={() => handleCompanyAction(company.id, "suspend")}
                              className="btn-action"
                              style={{ fontSize: "12px", marginRight: "5px" }}
                              disabled={loading}
                            >
                              ⏸️ Suspendre
                            </button>
                            <button
                              onClick={() => handleCompanyAction(company.id, "activate")}
                              className="btn-action"
                              style={{ fontSize: "12px", marginRight: "5px" }}
                              disabled={loading}
                            >
                              ▶️ Réactiver
                            </button>
                            <button
                              onClick={() => handleCompanyAction(company.id, "terminate")}
                              className="btn-action terminate"
                              style={{ fontSize: "12px", backgroundColor: "#dc3545" }}
                              disabled={loading}
                            >
                              🗑️ Résilier
                            </button>
                            <button
                              onClick={() => {
                                setSelectedCompanyId(company.id);
                                setShowCreateAdmin(true);
                                setCurrentTab("admins");
                              }}
                              className="btn-add"
                              style={{ fontSize: "12px", padding: "6px 12px", marginLeft: "5px" }}
                            >
                              ➕ Créer un admin
                            </button>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {/* ONGLET ADMINS */}
        {currentTab === "admins" && (
          <div className="card">
            <div className="table-header">
              <h2>👨‍💼 Liste des admins</h2>
              <button
                onClick={() => setShowCreateAdmin(!showCreateAdmin)}
                className="btn-add"
              >
                ➕ Créer un admin
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
                    <option key={c.id} value={c.id}>
                      {c.name}
                    </option>
                  ))}
                </select>
                <button type="submit" className="btn-add" disabled={loading}>
                  {loading ? "Création..." : "Créer"}
                </button>
                <button
                  type="button"
                  onClick={() => setShowCreateAdmin(false)}
                  className="btn-reset"
                >
                  Annuler
                </button>
              </form>
            )}

            {admins.length === 0 ? (
              <p style={{ textAlign: "center", padding: "40px", color: "#666" }}>
                Aucun admin créé
              </p>
            ) : (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>ID</th>
                      <th>Username</th>
                      <th>Email</th>
                      <th>Entreprise</th>
                      <th>Date création</th>
                      <th>Première connexion</th>
                    </tr>
                  </thead>
                  <tbody>
                    {admins.map((admin) => (
                      <tr key={admin.id}>
                        <td>{admin.id}</td>
                        <td><strong>{admin.username}</strong></td>
                        <td>{admin.email || "-"}</td>
                        <td>{admin.company_name || "-"}</td>
                        <td>
                          {admin.created_at
                            ? new Date(admin.created_at).toLocaleDateString("fr-FR")
                            : "-"}
                        </td>
                        <td>
                          {admin.first_login ? (
                            <span style={{ color: "orange" }}>⚠️ Oui</span>
                          ) : (
                            <span style={{ color: "green" }}>✅ Non</span>
                          )}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
};

export default SuperAdminDashboard;