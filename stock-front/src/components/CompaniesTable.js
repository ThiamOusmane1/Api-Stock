import React, { useEffect, useState } from "react";
import api from "../api";

const CompaniesTable = () => {
  const [companies, setCompanies] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    loadCompanies();
  }, []);

  const loadCompanies = async () => {
    setLoading(true);
    try {
      const response = await api.get("/entreprises");
      setCompanies(response.data);
    } catch (err) {
      console.error("Erreur chargement entreprises:", err);
      setMessage({ type: "error", text: "Erreur de chargement des entreprises" });
    } finally {
      setLoading(false);
    }
  };

  const handleAction = async (companyId, action) => {
    setLoading(true);
    try {
      let url = "";
      switch (action) {
        case "suspend":
          url = `/superadmin/companies/${companyId}/suspend`;
          break;
        case "activate":
          url = `/superadmin/companies/${companyId}/activate`;
          break;
        case "terminate":
          url = `/superadmin/companies/${companyId}/terminate`;
          break;
        default:
          return;
      }

      const res = await api.post(url);
      setMessage({ type: "success", text: res.data.message });
      loadCompanies(); // Recharger la liste
    } catch (err) {
      setMessage({
        type: "error",
        text: err.response?.data?.detail || "Erreur lors de l'action",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>🏢 Gestion des entreprises</h2>

      {message && (
        <div className={`message ${message.type}`}>
          {message.text}
          <button
            onClick={() => setMessage(null)}
            style={{ float: "right", background: "none", border: "none", cursor: "pointer" }}
          >
            ✕
          </button>
        </div>
      )}

      {loading && <p>⏳ Chargement...</p>}

      {companies.length === 0 ? (
        <p style={{ textAlign: "center", padding: "40px", color: "#666" }}>
          Aucune entreprise trouvée
        </p>
      ) : (
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Nom</th>
                <th>Status</th>
                <th>Date Suspension</th>
                <th>Date Résiliation</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {companies.map((c) => (
                <tr key={c.id}>
                  <td>{c.id}</td>
                  <td>{c.name}</td>
                  <td>{c.status}</td>
                  <td>{c.suspended_at ? new Date(c.suspended_at).toLocaleString() : "-"}</td>
                  <td>{c.terminated_at ? new Date(c.terminated_at).toLocaleString() : "-"}</td>
                  <td>
                    {c.status === "ACTIVE" && (
                      <button onClick={() => handleAction(c.id, "suspend")} className="btn-action">
                        Suspendre
                      </button>
                    )}
                    {c.status === "SUSPENDED" && (
                      <button onClick={() => handleAction(c.id, "activate")} className="btn-action">
                        Réactiver
                      </button>
                    )}
                    {c.status !== "TERMINATED" && (
                      <button onClick={() => handleAction(c.id, "terminate")} className="btn-action terminate">
                        Résilier
                      </button>
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

export default CompaniesTable;
