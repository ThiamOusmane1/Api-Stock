import React, { useState, useEffect } from "react";
import api from "../api";
import "../App.css";

const AdminUsersManagement = ({ user }) => {
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showCreate, setShowCreate] = useState(false);
  const [message, setMessage] = useState(null);
  
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");

  useEffect(() => {
    loadUsers();
  }, []);

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
      const result = await api.post("/admin/create-user", {
        username,
        email,
        company_id: user.company_id,
      });
      
      setMessage({
        type: "success",
        text: `Utilisateur "${result.username}" créé ! Mot de passe temporaire : ${result.temp_password} (envoyé par email à ${result.email})`,
      });
      
      setUsername("");
      setEmail("");
      setShowCreate(false);
      loadUsers();
    } catch (err) {
      setMessage({ type: "error", text: err.response?.data?.detail || "Erreur création utilisateur" });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="table-header">
        <h2>👥 Gestion des utilisateurs de votre entreprise</h2>
        <button
          onClick={() => setShowCreate(!showCreate)}
          className="btn-add"
        >
          ➕ Créer un utilisateur
        </button>
      </div>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
          <button onClick={() => setMessage(null)} style={{ float: "right", background: "none", border: "none", cursor: "pointer" }}>✕</button>
        </div>
      )}

      {showCreate && (
        <form onSubmit={handleCreateUser} className="ajout-form">
          <input
            type="text"
            placeholder="Nom d'utilisateur"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="input-ajout"
            required
          />
          <input
            type="email"
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="input-ajout"
            required
          />
          <button type="submit" className="btn-add" disabled={loading}>
            {loading ? "Création..." : "Créer"}
          </button>
          <button
            type="button"
            onClick={() => setShowCreate(false)}
            className="btn-reset"
          >
            Annuler
          </button>
        </form>
      )}

      {loading && <p>⏳ Chargement...</p>}

      {users.length === 0 ? (
        <p style={{ textAlign: "center", padding: "40px", color: "#666" }}>
          Aucun utilisateur créé pour votre entreprise
        </p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Username</th>
                <th>Email</th>
                <th>Date création</th>
                <th>Première connexion</th>
              </tr>
            </thead>
            <tbody>
              {users.map((u) => (
                <tr key={u.id}>
                  <td>{u.id}</td>
                  <td><strong>{u.username}</strong></td>
                  <td>{u.email || "-"}</td>
                  <td>
                    {u.created_at
                      ? new Date(u.created_at).toLocaleDateString("fr-FR")
                      : "-"}
                  </td>
                  <td>
                    {u.first_login ? (
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
  );
};

export default AdminUsersManagement;