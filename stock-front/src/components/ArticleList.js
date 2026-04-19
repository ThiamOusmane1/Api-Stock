import React, { useEffect, useMemo, useState, useCallback  } from "react";
import { fetchArticles, createArticle } from "../api";
import Message from "./Message";
import * as XLSX from "xlsx";
import jsPDF from "jspdf";
import "jspdf-autotable";
import { v4 as uuidv4 } from "uuid";
import "../App.css";

/* ====================== SYNONYMES / UTILITAIRES ====================== */
const SYNONYMES = {
  poteau: ["poteau", "montant", "standard", "upright"],
  moise: ["moise", "lisse", "longitudinale", "ledger"],
  transverse: ["transverse", "entretoise", "traverse", "transom"],
  diagonale: ["diagonale", "contrevent", "brace", "amarage", "amarres"],
  plancher: ["plancher", "plateau", "deck", "platform"],
  trappe: ["trappe", "trappe d'accès", "hatch"],
  plinthe: ["plinthe", "toe board", "toeboard"],
  gardeCorps: ["garde-corps", "gc", "guardrail", "lisse de protection"],
  embase: ["embase pivotante", "embase à vérin", "embase standard"],
  socle: ["socle réglable", "socle inclinable", "socle tubulaire", "vérin de socle", "pointe de socle"],
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
  const showMessage = (type, text, duration = 3000) => {
  setMessage({ type, text });
  setTimeout(() => {
    setMessage(null);
  }, duration);
};
  const [search, setSearch] = useState("");
  const [showStock, setShowStock] = useState(false);
  const [echafaudage, setEchafaudage] = useState([]);
  const [modalOpen, setModalOpen] = useState(false);
  const [collapsedCats, setCollapsedCats] = useState({});
  // 🆕 NOUVEAUX ÉTATS POUR LA CONFIGURATION CLIENT
  const [niveauxTravail, setNiveauxTravail] = useState("tous");
  const [niveauxCustom, setNiveauxCustom] = useState("");
  const [metaData, setMetaData] = useState(null);
  const poidsTotal = echafaudage.reduce(
  (sum, a) => sum + (a.poids_total || 0),  // ✅ Utilise le poids déjà calculé
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
        ? data.map((a) => ({ ...a, utilisé: 0, uuid: uuidv4() }))
        : []
    );
  } catch (err) {
    console.error(err);
    showMessage(
      "error",
      "Impossible de récupérer la liste des articles."
    );
  } finally {
    setLoading(false);
  }
}, []);
  useEffect(() => {
    loadArticles();
  }, [refresh, loadArticles]);

  /* ------------------------- AJOUT ARTICLE ------------------------- */
  const handleAddArticle = async () => {
    const nom = document.getElementById("nomArticle").value;
    const description = document.getElementById("descArticle").value;
    const longueur =
      parseFloat(document.getElementById("longArticle").value) || null;
    const largeur =
      parseFloat(document.getElementById("largArticle").value) || null;
    const hauteur =
      parseFloat(document.getElementById("hautArticle").value) || null;
    const quantite = parseInt(document.getElementById("qtyArticle").value) || 0;
    const poids =
      parseFloat(document.getElementById("poidsArticle").value) || null;

    if (!nom || quantite <= 0) {
      showMessage("error", "Nom et quantité requis");
      return;
    }

    if (!window.confirm(`Confirmer l'ajout de ${nom} (${quantite}) ?`)) return;

    try {
      const newArticle = await createArticle({
        nom,
        description,
        longueur,
        largeur,
        hauteur,
        quantite,
        poids,
      });
      setArticles((prev) => [
        ...prev,
        { ...newArticle, utilisé: 0, uuid: uuidv4() },
      ]);
      showMessage("success", "Article ajouté avec succès.");
      [
        "nomArticle",
        "descArticle",
        "longArticle",
        "largArticle",
        "hautArticle",
        "qtyArticle",
        "poidsArticle",
      ].forEach((id) => (document.getElementById(id).value = ""));
    } catch (err) {
      console.error(err);
      showMessage("error", "Erreur lors de l'ajout de l'article");
    }
  };

/* ------------------------- SUPPRESSION ARTICLE PERMANENTE ------------------------- */
const removeArticle = async (id) => {
  const article = articles.find((a) => a.id === id);
  
  if (!window.confirm(`⚠️ Confirmer la suppression DÉFINITIVE de "${article.nom}" ?\n\nCette action est irréversible.`)) {
    return;
  }

  setLoading(true);
  
  try {
    // ✅ Appel API backend pour suppression permanente
    const token = JSON.parse(localStorage.getItem("user")).access_token;
    const response = await fetch(`http://127.0.0.1:8000/articles/${id}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Erreur lors de la suppression");
    }

    // ✅ Suppression en local uniquement si succès backend
    setArticles((prev) => prev.filter((a) => a.id !== id));
    showMessage(
      "success",
  `    ✅ Article "${article.nom}" supprimé définitivement de la base de données.`
);

  } catch (err) {
    console.error("Erreur suppression:", err);
    showMessage(
      "error",
      `❌ Erreur : ${err.message}`
);

  } finally {
    setLoading(false);
  }
};

  /* ------------------------- FILTRE + CATÉGORIE ------------------------- */
  const filteredArticles = useMemo(
    () =>
      articles.filter(
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
  // 🆕 RÉCUPÉRER LES INFOS CHANTIER
  const nomChantier = document.getElementById("nomChantier").value.trim();
  const dureeLocation = parseInt(document.getElementById("dureeLocation").value) || null;

  if (!h || !l || !w) {
    showMessage(
      "error",
      "Veuillez entrer Hauteur, Longueur et Largeur valides."
    );
    return;
  }

  // 🆕 Construire la valeur de niveaux_travail
  let niveauxTravailValue = niveauxTravail;
  if (niveauxTravail === "custom" && niveauxCustom.trim()) {
    niveauxTravailValue = `liste:${niveauxCustom.trim()}`;
  }

  setLoading(true);

  try {
    const token = JSON.parse(localStorage.getItem("user")).access_token;
    const response = await fetch("http://127.0.0.1:8000/calcul/", {
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

    if (!response.ok) {
      throw new Error("Erreur lors du calcul");
    }

    const data = await response.json();

    console.log("✅ Réponse backend:", data);

    const recap = data.pieces.map((p) => ({
      id: p.article_id,
      nom: p.nom,
      utilisé: p.quantite_utilisee,
      longueur: p.longueur,
      largeur: p.largeur,
      hauteur: p.hauteur,
      poids: p.poids_unitaire,
      poids_total: p.poids_total_ligne,
      uuid: uuidv4(),
    }));

    setEchafaudage(recap);
    setMetaData(data.meta); // 🆕 AJOUTÉ
    setModalOpen(true);

    document.getElementById("echafHauteur").value = "";
    document.getElementById("echafLongueur").value = "";
    document.getElementById("echafLargeur").value = "";
    document.getElementById("nomChantier").value = "";
    document.getElementById("dureeLocation").value = "";

    if (data.ajustements && data.ajustements.length > 0) {
      showMessage(
        "warning",
        `Calcul avec ajustements: ${data.ajustements.join(" ; ")}`
      );
    } else {
      showMessage(
        "success",
        `Calcul réussi - ${data.meta.nb_niveaux} niveaux, ${data.meta.nb_travees} travées`
      );
    }
  } catch (err) {
    console.error("❌ Erreur calcul:", err);
    showMessage(
      "error",
      "Erreur lors du calcul de l'échafaudage"
    );
  } finally {
    setLoading(false);
  }
};

  /* ------------------------- EXPORT ------------------------- */
  const exportExcel = () => {
    if (!echafaudage.length) {
      showMessage("error", "Aucun récap à exporter");
      return;
    }
    const ws = XLSX.utils.json_to_sheet(
      echafaudage.map((a) => ({
        Nom: a.nom,
        Quantité: a.utilisé,
        Longueur: a.longueur,
        Largeur: a.largeur,
        Hauteur: a.hauteur,
        Poids: a.poids,
      }))
    );
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, "Echafaudage");
    XLSX.writeFile(wb, "Echafaudage.xlsx");
  };

  const exportPDF = () => {
    if (!echafaudage.length) {
      showMessage("error", "Aucun récap à exporter");
      return;
    }
    const doc = new jsPDF();
    doc.text("Liste des pièces pour l'échafaudage", 14, 20);
    doc.autoTable({
      startY: 25,
      head: [["Nom", "Quantité", "Longueur", "Largeur", "Hauteur", "Poids"]],
      body: echafaudage.map((a) => [
        a.nom,
        a.utilisé,
        a.longueur || "-",
        a.largeur || "-",
        a.hauteur || "-",
        a.poids || "-",
      ]),
    });
    doc.save("Echafaudage.pdf");
  };

  const resetUtilise = () => {
    setArticles((prev) => prev.map((a) => ({ ...a, utilisé: 0 })));
    setEchafaudage([]);
    showMessage("info", 'Champ "utilisé" remis à zéro.');
  };

  /* ------------------------- RENDER ------------------------- */
  return (
    <div className="card">
      <div className="table-header">
        <h2>Stock d’échafaudages</h2>
        <div style={{ display: "flex", gap: 10, alignItems: "center" }}>
      {/* 🆕 BOUTON HISTORIQUE */}
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
            placeholder="Rechercher..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="input-search"
          />
        </div>
      </div>

      <Message type={message?.type} text={message?.text} />
      {loading && <p>Chargement des articles...</p>}

      {/* Ajout article */}
      <h3>Ajouter un article</h3>
      <div className="ajout-form">
        {[
          "nomArticle",
          "descArticle",
          "longArticle",
          "largArticle",
          "hautArticle",
          "qtyArticle",
          "poidsArticle",
        ].map((id, i) => (
          <input
            key={id}
            id={id}
            type={i < 2 || id === "poidsArticle" ? "text" : "number"}
            step={i > 1 && i < 5 ? "0.01" : undefined}
            placeholder={id.replace(/Article/, "")}
            className="input-ajout"
          />
        ))}
        <button className="btn-add" onClick={handleAddArticle}>
          Ajouter
        </button>
      </div>

      {/* Stock par catégorie */}
      <button
        className="toggle-stock"
        onClick={() => setShowStock((prev) => !prev)}
      >
        {showStock ? "Masquer le stock" : "Afficher le stock"}
      </button>
      {showStock &&
        Object.entries(articlesParCategorie).map(([cat, list]) => (
          <div key={cat} className="categorie-block">
            <h4
              onClick={() =>
                setCollapsedCats((prev) => ({ ...prev, [cat]: !prev[cat] }))
              }
              style={{ cursor: "pointer" }}
            >
              {cat.toUpperCase()} {collapsedCats[cat] ? "▼" : "▲"}
            </h4>
            {!collapsedCats[cat] && (
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      {[
                        "ID",
                        "Nom",
                        "Description",
                        "Quantité",
                        "Utilisé",
                        "Longueur",
                        "Largeur",
                        "Hauteur",
                        "Poids",
                        "Action",
                      ].map((th) => (
                        <th key={th}>{th}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {list.map((a) => (
                      <tr key={a.uuid}>
                        <td>{a.id || "-"}</td>
                        <td>{a.nom}</td>
                        <td>{a.description || "-"}</td>
                        <td>{a.quantite}</td>
                        <td>{a.utilisé || 0}</td>
                        <td>{a.longueur || "-"}</td>
                        <td>{a.largeur || "-"}</td>
                        <td>{a.hauteur || "-"}</td>
                        <td>{a.poids || "-"}</td>
                        <td>
                          <button onClick={() => removeArticle(a.id)} className="btn-remove">
                           ❌
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        ))}

      {/* 🆕 Calcul avec configuration client */}
    <h3>Calcul échafaudage</h3>
    <div className="calcul-form">
          {/* 🆕 INFORMATIONS CHANTIER */}
      <div style={{ 
        marginBottom: 15, 
        padding: 10, 
        border: "1px solid #ddd", 
        borderRadius: 5,
        backgroundColor: "#f9f9f9"
      }}>
        <h4 style={{ margin: "0 0 10px 0" }}>🏗️ Informations chantier</h4>
        
        <label style={{ display: "block", marginBottom: 10 }}>
          <strong>Nom du chantier :</strong>
          <input
            id="nomChantier"
            type="text"
            placeholder="Ex: Rénovation Immeuble A"
            style={{ marginLeft: 10, padding: 5, width: 300 }}
          />
        </label>

        <label style={{ display: "block" }}>
          <strong>Durée de location prévisionnelle :</strong>
          <input
            id="dureeLocation"
            type="number"
            min="1"
            placeholder="En jours"
            style={{ marginLeft: 10, padding: 5, width: 100 }}
          />
          <span style={{ marginLeft: 5, fontSize: "0.9em", color: "#666" }}>jours</span>
        </label>
      </div>
      <input id="echafHauteur" type="number" step="0.01" placeholder="Hauteur (m)" />
      <input id="echafLongueur" type="number" step="0.01" placeholder="Longueur (m)" />
      <input id="echafLargeur" type="number" step="0.01" placeholder="Largeur (m)" />

      {/* 🆕 Configuration niveaux de travail */}
      <div style={{ 
        marginTop: 15, 
        padding: 10, 
        border: "1px solid #ddd", 
        borderRadius: 5,
        backgroundColor: "#f9f9f9"
      }}>
        <h4 style={{ margin: "0 0 10px 0" }}>📋 Configuration client</h4>
        
        <label style={{ display: "block", marginBottom: 10 }}>
          <strong>Niveaux de travail (planchers) :</strong>
          <select
            value={niveauxTravail}
            onChange={(e) => setNiveauxTravail(e.target.value)}
            style={{ marginLeft: 10, padding: 5, minWidth: 250 }}
          >
            <option value="tous">Tous les niveaux (standard)</option>
            <option value="dernier">Dernier niveau uniquement (toiture)</option>
            <option value="custom">Niveaux personnalisés</option>
          </select>
        </label>

        {niveauxTravail === "custom" && (
          <div style={{ marginLeft: 20, marginBottom: 10 }}>
            <input
              type="text"
              placeholder="Ex: 2,4,5 (niveaux avec planchers)"
              value={niveauxCustom}
              onChange={(e) => setNiveauxCustom(e.target.value)}
              style={{ padding: 5, width: 280 }}
            />
            <div style={{ fontSize: "0.85em", color: "#666", marginTop: 5 }}>
              💡 Saisissez les numéros de niveaux séparés par des virgules
            </div>
          </div>
        )}

      </div>

      <div style={{ marginTop: 10 }}>
        <button className="btn-calc" onClick={handleCalculEchafaudage}>
          Calculer échafaudage
        </button>
        <button
          className="btn-reset"
          style={{ marginLeft: 10 }}
          onClick={resetUtilise}
        >
          Réinitialiser utilisé
        </button>
      </div>
    </div>

      {/* MODALE RÉCAP */}
      {modalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Articles utilisés pour l'échafaudage</h3>
            {/* 🆕 Affichage de la configuration client */}
            {metaData && (
              <div style={{ 
                background: "#e8f4f8", 
                padding: 12, 
                borderRadius: 5, 
                marginBottom: 15,
                fontSize: "0.9em",
                border: "1px solid #b3d9e6"
              }}>
                {/* 🆕 INFORMATIONS CHANTIER */}
              {(metaData.nom_chantier || metaData.duree_location) && (
                <div style={{ 
                  background: "#fff3cd", 
                  padding: 12, 
                  borderRadius: 5, 
                  marginBottom: 15,
                  border: "1px solid #ffc107"
                }}>
                  {metaData.nom_chantier && (
                    <div style={{ marginBottom: 5 }}>
                      <strong>🏗️ Chantier :</strong> {metaData.nom_chantier}
                    </div>
                  )}
                  {metaData.duree_location && (
                    <div>
                      <strong>📅 Durée prévisionnelle :</strong> {metaData.duree_location} jour(s)
                    </div>
                  )}
                </div>
              )}
                <div style={{ marginBottom: 5 }}>
                  <strong>📋 Configuration :</strong> 
                  {metaData.configuration_client === "tous" && " Tous les niveaux"}
                  {metaData.configuration_client === "dernier" && " Dernier niveau uniquement"}
                  {metaData.configuration_client?.startsWith("liste:") && 
                    ` Niveaux ${metaData.liste_niveaux_travail?.join(", ") || "personnalisés"}`}
                </div>
                <div style={{ marginBottom: 5 }}>
                  <strong>🏗️ Planchers :</strong> {metaData.nb_niveaux_travail} niveau(x) de travail
                  {metaData.nb_niveaux_travail < metaData.nb_niveaux && 
                    ` + ${metaData.nb_niveaux - metaData.nb_niveaux_travail} niveau(x) de circulation`}
                </div>
                <div>
                  <strong>🛡️ Sécurité :</strong> Conforme normes EN 12810 ✅
                  <span style={{ marginLeft: 5, fontSize: "0.85em", color: "#666" }}>
                    (GC sur tous les niveaux ≥1)
                  </span>
                </div>
              </div>
            )}
            <table>
              <thead>
                <tr>
                  {[
                    "Nom",
                    "Quantité utilisée",
                    "Longueur",
                    "Largeur",
                    "Hauteur",
                    "Poids unitaire",  
                    "Poids total",     
                  ].map((th) => (
                    <th key={th}>{th}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {echafaudage.map((a) => (
                  <tr key={a.uuid + "-modal"}>
                    <td>{a.nom}</td>
                    <td>{a.utilisé}</td>
                    <td>{a.longueur || "-"}</td>
                    <td>{a.largeur || "-"}</td>
                    <td>{a.hauteur || "-"}</td>
                    <td>{a.poids || "-"} kg</td>                      {/* 🆕 Poids unitaire */}
                    <td><strong>{a.poids_total || "-"} kg</strong></td>  {/* 🆕 Poids total */}
                  </tr>
                ))}
              </tbody>
            </table>
            <p>
              <strong>Poids total : {poidsTotal} kg</strong>
            </p>
            <div style={{ marginTop: 8 }}>
              <button className="btn-export" onClick={exportExcel}>
                Exporter Excel
              </button>
              <button
                className="btn-export"
                style={{ marginLeft: 8 }}
                onClick={exportPDF}
              >
                Exporter PDF
              </button>
              <button style={{ marginLeft: 8 }} onClick={() => setModalOpen(false)}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ArticleList;
