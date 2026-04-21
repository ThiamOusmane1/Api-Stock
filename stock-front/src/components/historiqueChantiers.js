/* eslint-disable react-hooks/exhaustive-deps */
import React, { useState, useEffect } from "react";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import "../App.css";

const API_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

const HistoriqueChantiers = () => {
  const [chantiers, setChantiers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [filterDate, setFilterDate] = useState("");
  const [filterNom, setFilterNom] = useState("");

  const showMessage = (type, text, duration = 3000) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), duration);
  };

  // Charger les chantiers
  // eslint-disable-next-line react-hooks/exhaustive-deps
  useEffect(() => {
    loadChantiers();
  }, []);

  const loadChantiers = async () => {
    setLoading(true);
    try {
      const token = JSON.parse(localStorage.getItem("user")).access_token;
      const response = await fetch(`${API_URL}/chantiers/`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Erreur lors de la récupération des chantiers");
      }

      const data = await response.json();
      setChantiers(data);
    } catch (err) {
      console.error(err);
      showMessage("error", "Impossible de charger l'historique des chantiers");
    } finally {
      setLoading(false);
    }
  };

  // Supprimer un chantier
  const deleteChantier = async (id, nom) => {
    if (!window.confirm(`Confirmer la suppression du chantier "${nom}" ?`)) {
      return;
    }

    try {
      const token = JSON.parse(localStorage.getItem("user")).access_token;
      const response = await fetch(`${API_URL}/chantiers/${id}`, {
        method: "DELETE",
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error("Erreur lors de la suppression");
      }

      setChantiers((prev) => prev.filter((c) => c.id !== id));
      showMessage("success", `Chantier "${nom}" supprimé avec succès`);
    } catch (err) {
      console.error(err);
      showMessage("error", "Erreur lors de la suppression du chantier");
    }
  };

  // Filtrer les chantiers
  const chantiersFiltres = chantiers.filter((c) => {
    const matchNom = c.nom_chantier
      .toLowerCase()
      .includes(filterNom.toLowerCase());
    const matchDate = filterDate
      ? new Date(c.date_creation).toLocaleDateString("fr-FR").includes(filterDate)
      : true;
    return matchNom && matchDate;
  });

  // Export Excel
  const exportExcel = () => {
    if (!chantiersFiltres.length) {
      showMessage("error", "Aucun chantier à exporter");
      return;
    }

    const ws = XLSX.utils.json_to_sheet(
      chantiersFiltres.map((c) => ({
        "Nom du chantier": c.nom_chantier,
        "Date de création": new Date(c.date_creation).toLocaleDateString("fr-FR"),
        "Hauteur (m)": c.hauteur || "-",
        "Longueur (m)": c.longueur || "-",
        "Largeur (m)": c.largeur || "-",
        "Configuration": c.niveaux_travail || "-",
        "Durée (jours)": c.duree_location || "-",
        "Poids total (kg)": c.poids_total || "-",
      }))
    );
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Chantiers");
    XLSX.writeFile(wb, "Historique_Chantiers.xlsx");
    showMessage("success", "Export Excel réussi");
  };

  // Export PDF
  const exportPDF = () => {
    if (!chantiersFiltres.length) {
      showMessage("error", "Aucun chantier à exporter");
      return;
    }

    const doc = new jsPDF();
    doc.text("Historique des chantiers", 14, 20);
    doc.autoTable({
      startY: 25,
      head: [
        [
          "Nom",
          "Date",
          "Dimensions",
          "Config",
          "Durée",
          "Poids (kg)",
        ],
      ],
      body: chantiersFiltres.map((c) => [
        c.nom_chantier,
        new Date(c.date_creation).toLocaleDateString("fr-FR"),
        `${c.hauteur || "-"}×${c.longueur || "-"}×${c.largeur || "-"}m`,
        c.niveaux_travail || "-",
        c.duree_location ? `${c.duree_location}j` : "-",
        c.poids_total || "-",
      ]),
    });
    doc.save("Historique_Chantiers.pdf");
    showMessage("success", "Export PDF réussi");
  };

  return (
    <div className="card">
      <div className="table-header">
        <h2>📊 Historique des chantiers</h2>
        <button
          onClick={() => window.history.back()}
          style={{
            padding: "8px 16px",
            backgroundColor: "#6c757d",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          ← Retour
        </button>
      </div>

      {/* Message */}
      {message && (
        <div
          style={{
            padding: 10,
            marginBottom: 15,
            borderRadius: 5,
            backgroundColor:
              message.type === "success"
                ? "#d4edda"
                : message.type === "error"
                ? "#f8d7da"
                : "#fff3cd",
            color:
              message.type === "success"
                ? "#155724"
                : message.type === "error"
                ? "#721c24"
                : "#856404",
          }}
        >
          {message.text}
        </div>
      )}

      {/* Filtres */}
      <div
        style={{
          display: "flex",
          gap: 10,
          marginBottom: 15,
          padding: 10,
          backgroundColor: "#f8f9fa",
          borderRadius: 5,
        }}
      >
        <input
          type="text"
          placeholder="🔍 Rechercher par nom..."
          value={filterNom}
          onChange={(e) => setFilterNom(e.target.value)}
          style={{ flex: 1, padding: 8, borderRadius: 4, border: "1px solid #ddd" }}
        />
        <input
          type="text"
          placeholder="📅 Filtrer par date (jj/mm/aaaa)..."
          value={filterDate}
          onChange={(e) => setFilterDate(e.target.value)}
          style={{ flex: 1, padding: 8, borderRadius: 4, border: "1px solid #ddd" }}
        />
        <button
          onClick={() => {
            setFilterNom("");
            setFilterDate("");
          }}
          style={{
            padding: "8px 16px",
            backgroundColor: "#6c757d",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          Réinitialiser
        </button>
      </div>

      {/* Actions */}
      <div style={{ marginBottom: 15, display: "flex", gap: 10 }}>
        <button
          onClick={exportExcel}
          style={{
            padding: "8px 16px",
            backgroundColor: "#28a745",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          📊 Export Excel
        </button>
        <button
          onClick={exportPDF}
          style={{
            padding: "8px 16px",
            backgroundColor: "#dc3545",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          📄 Export PDF
        </button>
        <button
          onClick={loadChantiers}
          style={{
            padding: "8px 16px",
            backgroundColor: "#007bff",
            color: "white",
            border: "none",
            borderRadius: 4,
            cursor: "pointer",
          }}
        >
          🔄 Actualiser
        </button>
      </div>

      {/* Loading */}
      {loading && <p>Chargement...</p>}

      {/* Tableau */}
      {!loading && (
        <>
          <p style={{ marginBottom: 10, color: "#666" }}>
            <strong>{chantiersFiltres.length}</strong> chantier(s) trouvé(s)
          </p>

          <div className="table-container">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nom du chantier</th>
                  <th>Date de création</th>
                  <th>Dimensions (H×L×l)</th>
                  <th>Configuration</th>
                  <th>Durée (jours)</th>
                  <th>Poids total (kg)</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {chantiersFiltres.length === 0 ? (
                  <tr>
                    <td colSpan="8" style={{ textAlign: "center", padding: 20 }}>
                      Aucun chantier trouvé
                    </td>
                  </tr>
                ) : (
                  chantiersFiltres.map((c) => (
                    <tr key={c.id}>
                      <td>{c.id}</td>
                      <td>
                        <strong>{c.nom_chantier}</strong>
                      </td>
                      <td>
                        {new Date(c.date_creation).toLocaleDateString("fr-FR", {
                          day: "2-digit",
                          month: "2-digit",
                          year: "numeric",
                          hour: "2-digit",
                          minute: "2-digit",
                        })}
                      </td>
                      <td>
                        {c.hauteur && c.longueur && c.largeur
                          ? `${c.hauteur}m × ${c.longueur}m × ${c.largeur}m`
                          : "-"}
                      </td>
                      <td>
                        {c.niveaux_travail === "tous" && "Tous les niveaux"}
                        {c.niveaux_travail === "dernier" && "Dernier niveau"}
                        {c.niveaux_travail?.startsWith("liste:") &&
                          `Niveaux ${c.niveaux_travail.replace("liste:", "")}`}
                        {!c.niveaux_travail && "-"}
                      </td>
                      <td>{c.duree_location || "-"}</td>
                      <td>
                        {c.poids_total ? (
                          <strong>{c.poids_total.toFixed(2)}</strong>
                        ) : (
                          "-"
                        )}
                      </td>
                      <td>
                        <button
                          onClick={() => deleteChantier(c.id, c.nom_chantier)}
                          style={{
                            padding: "4px 8px",
                            backgroundColor: "#dc3545",
                            color: "white",
                            border: "none",
                            borderRadius: 4,
                            cursor: "pointer",
                            fontSize: "0.9em",
                          }}
                        >
                          🗑️ Supprimer
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Statistiques */}
          {chantiersFiltres.length > 0 && (
            <div
              style={{
                marginTop: 20,
                padding: 15,
                backgroundColor: "#e7f3ff",
                borderRadius: 5,
                border: "1px solid #b3d9ff",
              }}
            >
              <h4 style={{ margin: "0 0 10px 0" }}>📊 Statistiques</h4>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
                <div>
                  <strong>Total chantiers :</strong> {chantiersFiltres.length}
                </div>
                <div>
                  <strong>Poids total cumulé :</strong>{" "}
                  {chantiersFiltres
                    .reduce((sum, c) => sum + (c.poids_total || 0), 0)
                    .toFixed(2)}{" "}
                  kg
                </div>
                <div>
                  <strong>Durée moyenne :</strong>{" "}
                  {chantiersFiltres.filter((c) => c.duree_location).length > 0
                    ? (
                        chantiersFiltres.reduce(
                          (sum, c) => sum + (c.duree_location || 0),
                          0
                        ) / chantiersFiltres.filter((c) => c.duree_location).length
                      ).toFixed(1)
                    : "-"}{" "}
                  jours
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default HistoriqueChantiers;
