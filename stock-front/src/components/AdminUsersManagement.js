import React, { useState, useEffect } from "react";
import api from "../api";
import { createUserByAdmin } from "../api";
import "../App.css";

const API_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

// Labels et descriptions des sous-rôles
const SUB_ROLES = [
  {
    value: "aucun",
    label: "👤 Utilisateur standard",
    description: "Accès complet : stock, retraits, calcul, historique, exports",
    color: "#667eea",
  },
  {
    value: "commercial",
    label: "💼 Commercial",
    description: "Stock, retraits, calcul échafaudage, historique, exports",
    color: "#28a745",
  },
  {
    value: "magasinier",
    label: "🏭 Magasinier",
    description: "Stock, retraits, exports uniquement",
    color: "#fd7e14",
  },
  {
    value: "chef_chantier",
    label: "🦺 Chef de chantier",
    description: "Stock, retraits, calcul échafaudage, historique, exports",
    color: "#dc3545",
  },
  {
    value: "gestionnaire_stock",
    label: "📦 Gestionnaire de stock",
    description: "Stock complet (ajout/suppression), retraits, historique, exports",
    color: "#6f42c1",
  },
];

const SubRoleBadge = ({ subRole }) => {
  const role = SUB_ROLES.find((r) => r.value === subRole) || SUB_ROLES[0];
  return (
    <span style={{
      background: role.color + "20",
      color: role.color,
      padding: "3px 10px",
      borderRadius: 12,
      fontSize: 12,
      fontWeight: 600,
      whiteSpace: "nowrap",
    }}>
      {role.label}
    </span>
  );
};

const AdminUsersManagement = ({ user }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [message, setMessage] = useState(null);
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [subRole, setSubRole] = useState("aucun");

  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => { loadUsers(); }, []);

  const loadUsers = async () => {
    setLoading(true);
    try {
      const response = await api.get("/admin/list-users-of-company");
      setUsers(response.data);
    } catch (err) {
      console.error("Erreur chargement users:", err);
      setMessage({ type: "error", text: "Erreur de chargement des utilisateurs" });
    } finally {
      setLoading(false);
    }
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const result = await createUserByAdmin({
        username,
        email,
        company_id: user.company_id,
        sub_role: subRole,
      });

      setMessage({
        type: "success",
        text: `✅ Utilisateur "${result.username}" créé avec le rôle ${SUB_ROLES.find(r => r.value === subRole)?.label} !\nMot de passe temporaire envoyé par email.`,
      });

      setUsername("");
      setEmail("");
      setSubRole("aucun");
      setShowCreate(false);
      loadUsers();
    } catch (err) {
      console.error(err);
      setMessage({
        type: "error",
        text: err.response?.data?.detail || "Erreur création utilisateur",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleDeleteUser = async (userId, userName) => {
    if (!window.confirm(`Supprimer l'utilisateur "${userName}" ?`)) return;
    try {
      const token = JSON.parse(localStorage.getItem("user")).access_token;
      const response = await fetch(`${API_URL}/admin/users/${userId}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });
      if (!response.ok) throw new Error("Erreur suppression");
      setMessage({ type: "success", text: `✅ Utilisateur "${userName}" supprimé.` });
      setUsers((prev) => prev.filter((u) => u.id !== userId));
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    }
  };

  const handleChangeSubRole = async (userId, userName, newSubRole) => {
    try {
      const token = JSON.parse(localStorage.getItem("user")).access_token;
      const response = await fetch(`${API_URL}/admin/users/${userId}/sub-role`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ sub_role: newSubRole }),
      });
      if (!response.ok) throw new Error("Erreur modification rôle");
      const roleLabel = SUB_ROLES.find(r => r.value === newSubRole)?.label;
      setMessage({ type: "success", text: `✅ Rôle de "${userName}" mis à jour : ${roleLabel}` });
      loadUsers();
    } catch (err) {
      setMessage({ type: "error", text: err.message });
    }
  };

  return (
    <div className="card">
      <div className="table-header">
        <h2>👥 Utilisateurs de l'entreprise</h2>
        <button onClick={() => setShowCreate(!showCreate)} className="btn-add">
          ➕ Créer un utilisateur
        </button>
      </div>

      {message && (
        <div className={`message ${message.type}`} style={{ whiteSpace: "pre-line" }}>
          {message.text}
          <button onClick={() => setMessage(null)} style={{ float: "right", background: "none", border: "none", cursor: "pointer", fontSize: 16 }}>✕</button>
        </div>
      )}

      {/* ===== FORMULAIRE CRÉATION ===== */}
      {showCreate && (
        <form onSubmit={handleCreateUser} className="ajout-form" style={{ flexDirection: "column" }}>
          <h4 style={{ color: "#667eea", marginBottom: 8 }}>➕ Nouvel utilisateur</h4>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 150 }}>
              <label style={{ display: "block", marginBottom: 4, fontWeight: 600, fontSize: 13 }}>Nom d'utilisateur *</label>
              <input
                type="text"
                placeholder="Ex: jean.dupont"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="input-ajout"
                style={{ width: "100%" }}
                required
              />
            </div>
            <div style={{ flex: 1, minWidth: 150 }}>
              <label style={{ display: "block", marginBottom: 4, fontWeight: 600, fontSize: 13 }}>Email *</label>
              <input
                type="email"
                placeholder="Ex: jean@entreprise.fr"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input-ajout"
                style={{ width: "100%" }}
                required
              />
            </div>
          </div>

          {/* Sélection du sous-rôle */}
          <div style={{ width: "100%" }}>
            <label style={{ display: "block", marginBottom: 8, fontWeight: 600, fontSize: 13 }}>
              🎭 Rôle et permissions *
            </label>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: 10 }}>
              {SUB_ROLES.map((role) => (
                <div
                  key={role.value}
                  onClick={() => setSubRole(role.value)}
                  style={{
                    padding: 12,
                    borderRadius: 8,
                    border: `2px solid ${subRole === role.value ? role.color : "#e0e0e0"}`,
                    background: subRole === role.value ? role.color + "10" : "white",
                    cursor: "pointer",
                    transition: "all 0.2s",
                  }}
                >
                  <div style={{ fontWeight: 700, fontSize: 14, color: role.color, marginBottom: 4 }}>
                    {role.label}
                  </div>
                  <div style={{ fontSize: 12, color: "#666" }}>{role.description}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Matrice des permissions pour le rôle sélectionné */}
          <div style={{ width: "100%", background: "#f8f9ff", padding: 12, borderRadius: 8, fontSize: 13 }}>
            <strong>Permissions pour {SUB_ROLES.find(r => r.value === subRole)?.label} :</strong>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginTop: 8 }}>
              {getPermissionsForRole(subRole).map(({ label, allowed }) => (
                <span key={label} style={{
                  padding: "3px 10px",
                  borderRadius: 12,
                  fontSize: 12,
                  background: allowed ? "#d4edda" : "#f8d7da",
                  color: allowed ? "#155724" : "#721c24",
                }}>
                  {allowed ? "✅" : "❌"} {label}
                </span>
              ))}
            </div>
          </div>

          <div style={{ display: "flex", gap: 10 }}>
            <button type="submit" className="btn-add" disabled={loading} style={{ flex: 2 }}>
              {loading ? "⏳ Création..." : "➕ Créer l'utilisateur"}
            </button>
            <button type="button" onClick={() => setShowCreate(false)} className="btn-reset" style={{ flex: 1 }}>
              Annuler
            </button>
          </div>
        </form>
      )}

      {loading && <p style={{ padding: 10, color: "#667eea" }}>⏳ Chargement...</p>}

      {/* ===== LISTE UTILISATEURS ===== */}
      {users.length === 0 ? (
        <div style={{ textAlign: "center", padding: 40, color: "#666" }}>
          <p style={{ fontSize: 36 }}>👥</p>
          <p>Aucun utilisateur créé pour votre entreprise</p>
        </div>
      ) : (
        <>
          {/* Vue MOBILE : cartes */}
          <div className="mobile-cards">
            {users.map((u) => (
              <div key={u.id} className="mobile-card">
                <div className="mobile-card-header">
                  <strong>{u.username}</strong>
                  <SubRoleBadge subRole={u.sub_role || "aucun"} />
                </div>
                <div className="mobile-card-body">
                  <span>📧 {u.email || "-"}</span>
                  <span>📅 {u.created_at ? new Date(u.created_at).toLocaleDateString("fr-FR") : "-"}</span>
                  <span>{u.first_login ? "⚠️ 1ère connexion en attente" : "✅ Connecté"}</span>
                </div>
                <div className="mobile-card-actions">
                  <select
                    value={u.sub_role || "aucun"}
                    onChange={(e) => handleChangeSubRole(u.id, u.username, e.target.value)}
                    style={{ padding: "6px 10px", borderRadius: 6, border: "1px solid #ddd", fontSize: 12, flex: 1 }}
                  >
                    {SUB_ROLES.map((r) => (
                      <option key={r.value} value={r.value}>{r.label}</option>
                    ))}
                  </select>
                  <button
                    onClick={() => handleDeleteUser(u.id, u.username)}
                    style={{ padding: "6px 12px", background: "#dc3545", color: "white", border: "none", borderRadius: 6, cursor: "pointer", fontSize: 12 }}
                  >
                    🗑️
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
                  <th>Rôle</th>
                  <th>Modifier le rôle</th>
                  <th>Créé le</th>
                  <th>Statut</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {users.map((u) => (
                  <tr key={u.id}>
                    <td>{u.id}</td>
                    <td><strong>{u.username}</strong></td>
                    <td>{u.email || "-"}</td>
                    <td><SubRoleBadge subRole={u.sub_role || "aucun"} /></td>
                    <td>
                      <select
                        value={u.sub_role || "aucun"}
                        onChange={(e) => handleChangeSubRole(u.id, u.username, e.target.value)}
                        style={{ padding: "5px 8px", borderRadius: 6, border: "1px solid #ddd", fontSize: 12 }}
                      >
                        {SUB_ROLES.map((r) => (
                          <option key={r.value} value={r.value}>{r.label}</option>
                        ))}
                      </select>
                    </td>
                    <td>{u.created_at ? new Date(u.created_at).toLocaleDateString("fr-FR") : "-"}</td>
                    <td>
                      {u.first_login
                        ? <span style={{ color: "orange", fontSize: 12 }}>⚠️ En attente</span>
                        : <span style={{ color: "green", fontSize: 12 }}>✅ Actif</span>
                      }
                    </td>
                    <td>
                      <button
                        onClick={() => handleDeleteUser(u.id, u.username)}
                        style={{ padding: "4px 10px", background: "#dc3545", color: "white", border: "none", borderRadius: 5, cursor: "pointer", fontSize: 12 }}
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
  );
};

// Matrice des permissions par rôle
function getPermissionsForRole(subRole) {
  const matrix = {
    aucun:              { "Voir stock": true,  "Retraits": true,  "Calcul éch.": true,  "Historique": true,  "Ajout articles": false, "Suppr. articles": false, "Exports": true  },
    commercial:         { "Voir stock": true,  "Retraits": true,  "Calcul éch.": true,  "Historique": true,  "Ajout articles": false, "Suppr. articles": false, "Exports": true  },
    magasinier:         { "Voir stock": true,  "Retraits": true,  "Calcul éch.": false, "Historique": false, "Ajout articles": false, "Suppr. articles": false, "Exports": true  },
    chef_chantier:      { "Voir stock": true,  "Retraits": true,  "Calcul éch.": true,  "Historique": true,  "Ajout articles": false, "Suppr. articles": false, "Exports": true  },
    gestionnaire_stock: { "Voir stock": true,  "Retraits": true,  "Calcul éch.": false, "Historique": true,  "Ajout articles": true,  "Suppr. articles": true,  "Exports": true  },
  };
  const perms = matrix[subRole] || matrix.aucun;
  return Object.entries(perms).map(([label, allowed]) => ({ label, allowed }));
}

export default AdminUsersManagement;
