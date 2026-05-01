import React, { useEffect, useMemo, useState, useCallback } from "react";
import { fetchArticles, createArticle } from "../api";
import Message from "./Message";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { v4 as uuidv4 } from "uuid";
import "../App.css";

const API_URL = process.env.REACT_APP_API_BASE_URL || "http://127.0.0.1:8000";

/* ====================== SYNONYMES / UTILITAIRES ====================== */
const SYNONYMES = {
  poteau: ["poteau", "montant", "standard", "upright"],
  moise: ["moise", "lisse", "longitudinale", "ledger"],
  transverse: ["transverse", "entretoise", "traverse", "transom"],
  diagonale: ["diagonale", "contrevent", "brace", "amarage", "amarres"],
  plancher: ["plancher", "plateau", "deck", "platform"],
  trappe: ["trappe", "trappe d'acces", "hatch"],
  plinthe: ["plinthe", "toe board", "toeboard"],
  gardeCorps: ["garde-corps", "gc", "guardrail", "lisse de protection"],
  embase: ["embase pivotante", "embase a verin", "embase standard"],
  socle: ["socle reglable", "socle inclinable", "socle tubulaire", "verin de socle", "pointe de socle"],
  cale: ["cale", "shim", "bloc"],
};

export const detectCategorie = (nom) => {
  if (!nom) return "autres";
  const lower = nom.toLowerCase();
  for (const [cat, mots] of Object.entries(SYNONYMES)) {
    if (mots.some((m) => lower.includes(m))) return cat;
  }
  return "autres";
};

/* ====================== COMPOSANT PRINCIPAL ====================== */
const ArticleList = ({ refresh }) => {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [search, setSearch] = useState("");
  const [showStock, setShowStock] = useState(false);
  const [echafaudage, setEchafaudage] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [collapsedCats, setCollapsedCats] = useState({});
  const [niveauxTravail, setNiveauxTravail] = useState("tous");
  const [niveauxCustom, setNiveauxCustom] = useState("");
  const [metaData, setMetaData] = useState(null);

  const showMessage = (type, text, duration = 3000) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), duration);
  };

  // ✅ CORRIGÉ : poids_total_ligne au lieu de poids_total
  const poidsTotal = echafaudage.reduce(
    (sum, a) => sum + (a.poids_total_ligne || 0),
    0
  );

  /* ------------------------- CHARGEMENT ARTICLES ------------------------- */
  const loadArticles = useCallback(async () => {
    setLoading(true);
    setMessage(null);
    try {
      const data = await fetchArticles();
      setArticles(
        Array.isArray(data)
          ? data.map((a) => ({ ...a, utilise: 0, uuid: uuidv4() }))
          : []
      );
    } catch (err) {
      console.error(err);
      showMessage("error", "Impossible de récupérer la liste des articles.");
    } finally {
      setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    loadArticles();
  }, [refresh, loadArticles]);

  /* ------------------------- AJOUT ARTICLE ------------------------- */
  const handleAddArticle = async () => {
    const nom = document.getElementById("nomArticle").value;
    const description = document.getElementById("descArticle").value;
    const longueur = parseFloat(document.getElementById("longArticle").value) || null;
    const largeur = parseFloat(document.getElementById("largArticle").value) || null;
    const hauteur = parseFloat(document.getElementById("hautArticle").value) || null;
    const quantite = parseInt(document.getElementById("qtyArticle").value) || 0;
    const poids = parseFloat(document.getElementById("poidsArticle").value) || null;

    if (!nom || quantite <= 0) {
      showMessage("error", "Nom et quantité requis");
      return;
    }

    if (!window.confirm(`Confirmer l'ajout de ${nom} (${quantite}) ?`)) return;

    try {
      const newArticle = await createArticle({ nom, description, longueur, largeur, hauteur, quantite, poids });
      setArticles((prev) => [...prev, { ...newArticle, utilise: 0, uuid: uuidv4() }]);
      showMessage("success", "Article ajouté avec succès.");
      ["nomArticle", "descArticle", "longArticle", "largArticle", "hautArticle", "qtyArticle", "poidsArticle"]
        .forEach((id) => (document.getElementById(id).value = ""));
    } catch (err) {
      console.error(err);
      showMessage("error", "Erreur lors de l'ajout de l'article");
    }
  };

  /* ------------------------- SUPPRESSION ARTICLE ------------------------- */
  const removeArticle = async (id) => {
    const article = articles.find((a) => a.id === id);
    if (!window.confirm(`⚠️ Confirmer la suppression DÉFINITIVE de "${article.nom}" ?\n\nCette action est irréversible.`)) return;

    setLoading(true);
    try {
      // ✅ CORRIGÉ : URL dynamique
      const token = JSON.parse(localStorage.getItem("user")).access_token;
      const response = await fetch(`${API_URL}/articles/${id}`, {
        method: "DELETE",
        headers: { Authorization: `Bearer ${token}` },
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || "Erreur lors de la suppression");
      }

      setArticles((prev) => prev.filter((a) => a.id !== id));
      showMessage("success", `✅ Article "${article.nom}" supprimé définitivement.`);
    } catch (err) {
      console.error("Erreur suppression:", err);
      showMessage("error", `❌ Erreur : ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  /* ------------------------- FILTRE + CATÉGORIE ------------------------- */
  const filteredArticles = useMemo(
    () => articles.filter(
      (a) =>
        a.nom?.toLowerCase().includes(search.toLowerCase()) ||
        a.description?.toLowerCase().includes(search.toLowerCase())
    ),
    [articles, search]
  );

  const articlesParCategorie = useMemo(() => {
    const groups = {};
    filteredArticles.forEach((a) => {
      const cat = detectCategorie(a.nom || "");
      if (!groups[cat]) groups[cat] = [];
      groups[cat].push(a);
    });
    return groups;
  }, [filteredArticles]);

  /* ------------------------- CALCUL ECHAFAUDAGE ------------------------- */
  const handleCalculEchafaudage = async () => {
    const h = parseFloat(document.getElementById("echafHauteur").value);
    const l = parseFloat(document.getElementById("echafLongueur").value);
    const w = parseFloat(document.getElementById("echafLargeur").value);
    const nomChantier = document.getElementById("nomChantier").value.trim();
    const dureeLocation = parseInt(document.getElementById("dureeLocation").value) || null;

    if (!h || !l || !w) {
      showMessage("error", "Veuillez entrer Hauteur, Longueur et Largeur valides.");
      return;
    }

    let niveauxTravailValue = niveauxTravail;
    if (niveauxTravail === "custom" && niveauxCustom.trim()) {
      niveauxTravailValue = `liste:${niveauxCustom.trim()}`;
    }

    setLoading(true);
    try {
      // ✅ CORRIGÉ : URL dynamique
      const token = JSON.parse(localStorage.getItem("user")).access_token;
      const response = await fetch(`${API_URL}/calcul/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          hauteur: h,
          longueur: l,
          largeur: w,
          apply_to_stock: false,
          niveaux_travail: niveauxTravailValue,
          nom_chantier: nomChantier,
          duree_location: dureeLocation,
        }),
      });

      if (!response.ok) throw new Error("Erreur lors du calcul");

      const data = await response.json();
      console.log("✅ Réponse backend:", data);

      // ✅ CORRIGÉ : mapping correct des champs de l'API
      const recap = data.pieces.map((p) => ({
        id: p.article_id,
        nom: p.nom,
        utilise: p.quantite_utilisee,       // ✅ sans accent
        longueur: p.longueur,
        largeur: p.largeur,
        hauteur: p.hauteur,
        poids_unitaire: p.poids_unitaire,   // ✅ nom correct
        poids_total_ligne: p.poids_total_ligne, // ✅ nom correct
        uuid: uuidv4(),
      }));

      setEchafaudage(recap);
      setMetaData(data.meta);
      setModalOpen(true);

      // Vider les champs
      ["echafHauteur", "echafLongueur", "echafLargeur", "nomChantier", "dureeLocation"]
        .forEach((id) => { document.getElementById(id).value = ""; });

      if (data.ajustements && data.ajustements.length > 0) {
        showMessage("warning", `Calcul avec ajustements: ${data.ajustements.join(" ; ")}`);
      } else {
        showMessage("success", `Calcul réussi - ${data.meta.nb_niveaux} niveaux, ${data.meta.nb_travees} travées`);
      }
    } catch (err) {
      console.error("❌ Erreur calcul:", err);
      showMessage("error", "Erreur lors du calcul de l'échafaudage");
    } finally {
      setLoading(false);
    }
  };

  /* ------------------------- EXPORT ------------------------- */
  const exportExcel = () => {
    if (!echafaudage.length) { showMessage("error", "Aucun récap à exporter"); return; }
    const ws = XLSX.utils.json_to_sheet(
      echafaudage.map((a) => ({
        Nom: a.nom,
        "Quantité utilisée": a.utilise,
        "Longueur (m)": a.longueur || "-",
        "Largeur (m)": a.largeur || "-",
        "Hauteur (m)": a.hauteur || "-",
        "Poids unitaire (kg)": a.poids_unitaire || "-",
        "Poids total (kg)": a.poids_total_ligne || "-",
      }))
    );
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Echafaudage");
    XLSX.writeFile(wb, "Echafaudage.xlsx");
  };

  const exportPDF = () => {
    if (!echafaudage.length) { showMessage("error", "Aucun récap à exporter"); return; }
    const doc = new jsPDF();
    doc.text("Liste des pièces pour l'échafaudage", 14, 20);
    doc.autoTable({
      startY: 25,
      head: [["Nom", "Qté", "Long.", "Larg.", "Haut.", "Poids/u (kg)", "Poids total (kg)"]],
      body: echafaudage.map((a) => [
        a.nom,
        a.utilise,
        a.longueur || "-",
        a.largeur || "-",
        a.hauteur || "-",
        a.poids_unitaire || "-",
        a.poids_total_ligne || "-",
      ]),
    });
    doc.text(`Poids total : ${poidsTotal.toFixed(2)} kg`, 14, doc.lastAutoTable.finalY + 10);
    doc.save("Echafaudage.pdf");
  };

  const resetUtilise = () => {
    setArticles((prev) => prev.map((a) => ({ ...a, utilise: 0 })));
    setEchafaudage([]);
    showMessage("info", 'Champ "utilisé" remis à zéro.');
  };

  /* ------------------------- RENDER ------------------------- */
  return (
    <div className="card">
      <div className="table-header">
        <h2>📦 Stock d'échafaudages</h2>
        <div style={{ display: "flex", gap: 10, alignItems: "center", flexWrap: "wrap" }}>
          <button
            onClick={() => window.location.href = "/historique-chantiers"}
            style={{
              padding: "8px 16px",
              backgroundColor: "#007bff",
              color: "white",
              border: "none",
              borderRadius: 4,
              cursor: "pointer",
              fontSize: "0.9em",
            }}
          >
            📊 Historique des chantiers
          </button>
          <input
            type="text"
            placeholder="🔍 Rechercher..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-search"
          />
        </div>
      </div>

      <Message type={message?.type} text={message?.text} />
      {loading && <p>⏳ Chargement...</p>}

      {/* Ajout article */}
      <h3 style={{ marginBottom: 10 }}>➕ Ajouter un article</h3>
      <div className="ajout-form">
        {[
          { id: "nomArticle", placeholder: "Nom *", type: "text" },
          { id: "descArticle", placeholder: "Description", type: "text" },
          { id: "longArticle", placeholder: "Longueur (m)", type: "number" },
          { id: "largArticle", placeholder: "Largeur (m)", type: "number" },
          { id: "hautArticle", placeholder: "Hauteur (m)", type: "number" },
          { id: "qtyArticle", placeholder: "Quantité *", type: "number" },
          { id: "poidsArticle", placeholder: "Poids (kg)", type: "number" },
        ].map(({ id, placeholder, type }) => (
          <input key={id} id={id} type={type} step="0.01" placeholder={placeholder} className="input-ajout" />
        ))}
        <button className="btn-add" onClick={handleAddArticle}>Ajouter</button>
      </div>

      {/* Stock par catégorie */}
      <button className="toggle-stock" onClick={() => setShowStock((prev) => !prev)}>
        {showStock ? "🙈 Masquer le stock" : "👁️ Afficher le stock"}
      </button>

      {showStock && Object.entries(articlesParCategorie).map(([cat, list]) => (
        <div key={cat} className="categorie-block">
          <h4
            onClick={() => setCollapsedCats((prev) => ({ ...prev, [cat]: !prev[cat] }))}
            style={{ cursor: "pointer" }}
          >
            {cat.toUpperCase()} {collapsedCats[cat] ? "▼" : "▲"} ({list.length})
          </h4>
          {!collapsedCats[cat] && (
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    {["ID", "Nom", "Description", "Quantité", "Long.", "Larg.", "Haut.", "Poids (kg)", "Action"].map((th) => (
                      <th key={th}>{th}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {list.map((a) => (
                    <tr key={a.uuid}>
                      <td>{a.id || "-"}</td>
                      <td><strong>{a.nom}</strong></td>
                      <td style={{ maxWidth: 150, overflow: "hidden", textOverflow: "ellipsis" }}>{a.description || "-"}</td>
                      <td><strong>{a.quantite}</strong></td>
                      <td>{a.longueur || "-"}</td>
                      <td>{a.largeur || "-"}</td>
                      <td>{a.hauteur || "-"}</td>
                      <td>{a.poids || "-"}</td>
                      <td>
                        <button onClick={() => removeArticle(a.id)} className="btn-remove">❌</button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      ))}

      {/* Calcul échafaudage */}
      <h3 style={{ marginTop: 20, marginBottom: 10 }}>🧮 Calcul échafaudage</h3>
      <div className="calcul-form">

        {/* Informations chantier */}
        <div style={{ width: "100%", padding: 15, border: "1px solid #ddd", borderRadius: 8, backgroundColor: "#f9f9f9", marginBottom: 10 }}>
          <h4 style={{ margin: "0 0 12px 0", color: "#667eea" }}>🏗️ Informations chantier</h4>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <div style={{ flex: 2, minWidth: 200 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>Nom du chantier</label>
              <input
                id="nomChantier"
                type="text"
                placeholder="Ex: Rénovation Immeuble A"
                className="input-ajout"
                style={{ width: "100%" }}
              />
            </div>
            <div style={{ flex: 1, minWidth: 120 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>Durée (jours)</label>
              <input
                id="dureeLocation"
                type="number"
                min="1"
                placeholder="Ex: 30"
                className="input-ajout"
                style={{ width: "100%" }}
              />
            </div>
          </div>
        </div>

        {/* Dimensions */}
        <div style={{ width: "100%", padding: 15, border: "1px solid #ddd", borderRadius: 8, backgroundColor: "#f9f9f9", marginBottom: 10 }}>
          <h4 style={{ margin: "0 0 12px 0", color: "#667eea" }}>📐 Dimensions</h4>
          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            <div style={{ flex: 1, minWidth: 100 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>Hauteur (m) *</label>
              <input id="echafHauteur" type="number" step="0.01" placeholder="Ex: 6" className="input-ajout" style={{ width: "100%" }} />
            </div>
            <div style={{ flex: 1, minWidth: 100 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>Longueur (m) *</label>
              <input id="echafLongueur" type="number" step="0.01" placeholder="Ex: 12" className="input-ajout" style={{ width: "100%" }} />
            </div>
            <div style={{ flex: 1, minWidth: 100 }}>
              <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>Largeur (m) *</label>
              <input id="echafLargeur" type="number" step="0.01" placeholder="Ex: 0.73" className="input-ajout" style={{ width: "100%" }} />
            </div>
          </div>
        </div>

        {/* Configuration niveaux */}
        <div style={{ width: "100%", padding: 15, border: "1px solid #ddd", borderRadius: 8, backgroundColor: "#f9f9f9", marginBottom: 10 }}>
          <h4 style={{ margin: "0 0 12px 0", color: "#667eea" }}>📋 Configuration client</h4>
          <label style={{ display: "block", marginBottom: 5, fontWeight: 600, fontSize: 13 }}>Niveaux de travail (planchers)</label>
          <select
            value={niveauxTravail}
            onChange={(e) => setNiveauxTravail(e.target.value)}
            className="input-ajout"
            style={{ width: "100%", marginBottom: 10 }}
          >
            <option value="tous">Tous les niveaux (standard)</option>
            <option value="dernier">Dernier niveau uniquement (toiture)</option>
            <option value="custom">Niveaux personnalisés</option>
          </select>
          {niveauxTravail === "custom" && (
            <div>
              <input
                type="text"
                placeholder="Ex: 2,4,5 (numéros de niveaux séparés par virgules)"
                value={niveauxCustom}
                onChange={(e) => setNiveauxCustom(e.target.value)}
                className="input-ajout"
                style={{ width: "100%" }}
              />
              <p style={{ fontSize: 12, color: "#666", marginTop: 5 }}>💡 Saisissez les numéros de niveaux séparés par des virgules</p>
            </div>
          )}
        </div>

        {/* Boutons calcul */}
        <div style={{ width: "100%", display: "flex", gap: 10, flexWrap: "wrap" }}>
          <button className="btn-calc" onClick={handleCalculEchafaudage} disabled={loading} style={{ flex: 1 }}>
            {loading ? "⏳ Calcul en cours..." : "🧮 Calculer l'échafaudage"}
          </button>
          <button className="btn-reset" onClick={resetUtilise} style={{ flex: 1 }}>
            🔄 Réinitialiser
          </button>
        </div>
      </div>

      {/* MODALE RÉCAP */}
      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 15 }}>
              <h3 style={{ margin: 0 }}>🏗️ Liste des pièces - Échafaudage</h3>
              <button onClick={() => setModalOpen(false)} style={{ background: "none", border: "none", fontSize: 20, cursor: "pointer" }}>✕</button>
            </div>

            {/* Meta infos */}
            {metaData && (
              <div style={{ background: "#e8f4f8", padding: 12, borderRadius: 8, marginBottom: 15, fontSize: 13, border: "1px solid #b3d9e6" }}>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(150px, 1fr))", gap: 8 }}>
                  <div><strong>🏗️ Travées :</strong> {metaData.nb_travees}</div>
                  <div><strong>📏 Niveaux :</strong> {metaData.nb_niveaux}</div>
                  <div><strong>⚓ Amarrages :</strong> {metaData.amarrages_calcules}</div>
                  <div><strong>🪜 Trappes :</strong> {metaData.trappes_acces}</div>
                  <div><strong>📐 Surface :</strong> {metaData.surface_facade_m2} m²</div>
                  <div><strong>⚖️ Poids :</strong> {metaData.poids_total} kg</div>
                  <div><strong>🛡️ EN 12810 :</strong> ✅ Conforme</div>
                </div>
              </div>
            )}

            {/* Tableau des pièces */}
            <div className="table-container">
              <table>
                <thead>
                  <tr>
                    <th>Nom de la pièce</th>
                    <th>Qté</th>
                    <th>Long. (m)</th>
                    <th>Larg. (m)</th>
                    <th>Haut. (m)</th>
                    <th>Poids/u (kg)</th>
                    <th>Poids total (kg)</th>
                  </tr>
                </thead>
                <tbody>
                  {echafaudage.map((a) => (
                    <tr key={a.uuid + "-modal"}>
                      <td><strong>{a.nom}</strong></td>
                      <td>{a.utilise}</td>
                      <td>{a.longueur || "-"}</td>
                      <td>{a.largeur || "-"}</td>
                      <td>{a.hauteur || "-"}</td>
                      <td>{a.poids_unitaire || "-"}</td>
                      <td><strong>{a.poids_total_ligne ? a.poids_total_ligne.toFixed(2) : "-"}</strong></td>
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr style={{ backgroundColor: "#f8f9ff" }}>
                    <td colSpan={6} style={{ fontWeight: 700, textAlign: "right", padding: "10px 14px" }}>
                      POIDS TOTAL :
                    </td>
                    <td style={{ fontWeight: 700, fontSize: 16, color: "#667eea" }}>
                      {poidsTotal.toFixed(2)} kg
                    </td>
                  </tr>
                </tfoot>
              </table>
            </div>

            <div style={{ marginTop: 15, display: "flex", gap: 10, flexWrap: "wrap" }}>
              <button className="btn-export" onClick={exportExcel}>📊 Exporter Excel</button>
              <button className="btn-export" onClick={exportPDF}>📄 Exporter PDF</button>
              <button className="btn-reset" onClick={() => setModalOpen(false)}>✕ Fermer</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticleList;
