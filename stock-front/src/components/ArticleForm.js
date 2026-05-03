import React, { useState } from "react";
import { createArticle } from "../api";
import Message from "./Message";
import "../App.css";

const ArticleForm = ({ onSuccess }) => {
  const [nom, setNom] = useState("");
  const [description, setDescription] = useState("");
  const [quantite, setQuantite] = useState("");
  const [poids, setPoids] = useState("");
  const [longueur, setLongueur] = useState("");
  const [largeur, setLargeur] = useState("");
  const [hauteur, setHauteur] = useState("");
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);

    if (!nom || !quantite) {
      setMessage({ type: "error", text: "Le nom et la quantité sont obligatoires." });
      return;
    }

    if (parseInt(quantite) < 0) {
      setMessage({ type: "error", text: "La quantité doit être positive ou nulle." });
      return;
    }

    if (!window.confirm(`Confirmer l'ajout de "${nom}" (${quantite} unités) ?`)) return;

    setLoading(true);
    try {
      await createArticle({
        nom: nom.trim(),
        description: description.trim() || null,
        quantite: parseInt(quantite),
        poids: poids ? parseFloat(poids) : null,
        longueur: longueur ? parseFloat(longueur) : null,
        largeur: largeur ? parseFloat(largeur) : null,
        hauteur: hauteur ? parseFloat(hauteur) : null,
      });

      setMessage({ type: "success", text: `✅ Article "${nom}" ajouté avec succès !` });

      // Vider le formulaire
      setNom("");
      setDescription("");
      setQuantite("");
      setPoids("");
      setLongueur("");
      setLargeur("");
      setHauteur("");

      if (onSuccess) onSuccess();

    } catch (err) {
      console.error("Erreur ajout article:", err);
      setMessage({
        type: "error",
        text: err.response?.data?.detail || "❌ Erreur lors de l'ajout de l'article.",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setNom("");
    setDescription("");
    setQuantite("");
    setPoids("");
    setLongueur("");
    setLargeur("");
    setHauteur("");
    setMessage(null);
  };

  return (
    <div className="card">
      <div className="table-header">
        <h2>➕ Ajouter un article</h2>
      </div>

      <Message type={message?.type} text={message?.text} />

      <form onSubmit={handleSubmit} className="ajout-form" style={{ flexDirection: "column" }}>

        {/* Informations principales */}
        <div style={{ width: "100%", padding: 14, background: "#f8f9ff", borderRadius: 8, border: "1px solid #e8ecff" }}>
          <h4 style={{ marginBottom: 12, color: "#667eea", fontSize: 14 }}>📋 Informations principales</h4>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <div style={{ flex: 2, minWidth: 200 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
                Nom de l'article *
              </label>
              <input
                type="text"
                value={nom}
                onChange={(e) => setNom(e.target.value)}
                placeholder="Ex: Poteau 2m, Moise 3.07m..."
                className="input-ajout"
                style={{ width: "100%" }}
                required
              />
            </div>

            <div style={{ flex: 1, minWidth: 120 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
                Quantité *
              </label>
              <input
                type="number"
                value={quantite}
                onChange={(e) => setQuantite(e.target.value)}
                placeholder="Ex: 100"
                className="input-ajout"
                style={{ width: "100%" }}
                min="0"
                required
              />
            </div>

            <div style={{ flex: 1, minWidth: 120 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
                Poids unitaire (kg)
              </label>
              <input
                type="number"
                value={poids}
                onChange={(e) => setPoids(e.target.value)}
                placeholder="Ex: 12.5"
                className="input-ajout"
                style={{ width: "100%" }}
                step="0.01"
                min="0"
              />
            </div>
          </div>

          <div style={{ marginTop: 10 }}>
            <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
              Description
            </label>
            <input
              type="text"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Ex: Poteau vertical 2.00m Ringlock - Layher Allround - EN12811"
              className="input-ajout"
              style={{ width: "100%" }}
            />
          </div>
        </div>

        {/* Dimensions */}
        <div style={{ width: "100%", padding: 14, background: "#f8f9ff", borderRadius: 8, border: "1px solid #e8ecff" }}>
          <h4 style={{ marginBottom: 12, color: "#667eea", fontSize: 14 }}>📐 Dimensions (optionnel)</h4>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 100 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
                Longueur (m)
              </label>
              <input
                type="number"
                value={longueur}
                onChange={(e) => setLongueur(e.target.value)}
                placeholder="Ex: 3.07"
                className="input-ajout"
                style={{ width: "100%" }}
                step="0.01"
                min="0"
              />
            </div>

            <div style={{ flex: 1, minWidth: 100 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
                Largeur (m)
              </label>
              <input
                type="number"
                value={largeur}
                onChange={(e) => setLargeur(e.target.value)}
                placeholder="Ex: 0.61"
                className="input-ajout"
                style={{ width: "100%" }}
                step="0.01"
                min="0"
              />
            </div>

            <div style={{ flex: 1, minWidth: 100 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>
                Hauteur (m)
              </label>
              <input
                type="number"
                value={hauteur}
                onChange={(e) => setHauteur(e.target.value)}
                placeholder="Ex: 2.00"
                className="input-ajout"
                style={{ width: "100%" }}
                step="0.01"
                min="0"
              />
            </div>
          </div>
        </div>

        {/* Boutons */}
        <div style={{ display: "flex", gap: 10, width: "100%", flexWrap: "wrap" }}>
          <button
            type="submit"
            className="btn-add"
            disabled={loading}
            style={{ flex: 2 }}
          >
            {loading ? "⏳ Ajout en cours..." : "➕ Ajouter l'article"}
          </button>
          <button
            type="button"
            className="btn-reset"
            onClick={handleReset}
            disabled={loading}
            style={{ flex: 1 }}
          >
            🔄 Réinitialiser
          </button>
        </div>
      </form>
    </div>
  );
};

export default ArticleForm;
