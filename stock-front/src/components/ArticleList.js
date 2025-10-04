import React, { useEffect, useMemo, useState } from "react";
import { fetchArticles, createOrUpdateArticle } from "../api";
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
  diagonale: ["diagonale", "contrevent", "brace"],
  plancher: ["plancher", "plateau", "deck", "platform", "trappe"],
  plinthe: ["plinthe", "toe board", "toeboard"],
  gardeCorps: ["garde-corps", "gc", "guardrail", "lisse de protection"],
  embase: ["embase", "pied", "base jack", "socle"],
  cale: ["cale", "shim", "bloc"],
};

const detectCategorie = (nom) => {
  if (!nom) return "autres";
  const lower = nom.toLowerCase();
  for (const [cat, mots] of Object.entries(SYNONYMES)) {
    if (mots.some((m) => lower.includes(m))) return cat;
  }
  return "autres";
};

/* ====================== ALGORITHME GREEDY (corrigé) ====================== */
function greedyPartition(longueur, moises = [0.75, 1, 1.5, 2, 2.5, 3]) {
  let reste = longueur;
  const segments = [];
  const sorted = [...moises].sort((a, b) => b - a);

  while (reste > 1e-6) {
    let choix = null;
    for (const m of sorted) {
      if (m <= reste + 1e-9) {
        choix = m;
        break;
      }
    }
    if (!choix) choix = sorted[sorted.length - 1];
    segments.push(choix);
    reste -= choix;
    if (segments.length > 2000) break; // sécurité
  }
  return segments;
}

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

  /* ------------------------- CHARGEMENT ARTICLES ------------------------- */
  const loadArticles = async () => {
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
      setMessage({
        type: "error",
        text: "Impossible de récupérer la liste des articles.",
      });
    } finally {
      setLoading(false);
    }
  };
  useEffect(() => {
    loadArticles();
  }, [refresh]);

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
      setMessage({ type: "error", text: "Nom et quantité requis" });
      return;
    }

    if (!window.confirm(`Confirmer l'ajout de ${nom} (${quantite}) ?`)) return;

    try {
      const newArticle = await createOrUpdateArticle({
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
      setMessage({ type: "success", text: "Article ajouté avec succès." });
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
      setMessage({ type: "error", text: "Erreur lors de l'ajout de l'article" });
    }
  };

  /* ------------------------- SUPPRESSION ARTICLE ------------------------- */
  const removeArticle = (uuid) => {
    const article = articles.find((a) => a.uuid === uuid);
    if (!window.confirm(`Confirmer la suppression de ${article.nom} ?`)) return;

    setArticles((prev) => prev.filter((a) => a.uuid !== uuid));
    setMessage({ type: "info", text: "Article retiré du stock localement." });
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
  const STANDARD_HEIGHT = 2.0;
  const MOISES_DISPO = [0.75, 1, 1.5, 2, 2.5, 3];
  const DECK_DISPO = [0.75, 1, 1.5]; // largeurs standard

  const calculBesoinEchafaudage = (hauteur, longueur, largeur) => {
    const niveaux = Math.ceil(hauteur / STANDARD_HEIGHT);
    const travées = greedyPartition(longueur, MOISES_DISPO);

    let largeurChoisie =
      DECK_DISPO.find((d) => d === largeur) ||
      DECK_DISPO.filter((d) => d <= largeur).pop() ||
      largeur;

    const besoins = {};
    const nbCadres = travées.length + 1;
    besoins.embase = nbCadres * 2;
    besoins.cale = nbCadres * 2;
    besoins.poteau = nbCadres * 2 * niveaux;
    besoins.moise = travées.length * 2 * niveaux;
    besoins.transverse = travées.length * niveaux;
    besoins.diagonale = Math.ceil(travées.length / 2) * niveaux;
    besoins.plancher = travées.length * niveaux;
    besoins.plinthe = besoins.plancher;
    besoins.gardeCorps = travées.length * niveaux * 2;

    return {
      besoins,
      meta: { niveaux, travées, nbCadres, largeurChoisie },
    };
  };

  const handleCalculEchafaudage = () => {
    const h = parseFloat(document.getElementById("echafHauteur").value);
    const l = parseFloat(document.getElementById("echafLongueur").value);
    const w = parseFloat(document.getElementById("echafLargeur").value);

    if (!h || !l || !w) {
      setMessage({
        type: "error",
        text: "Veuillez entrer Hauteur, Longueur et Largeur valides.",
      });
      return;
    }

    const { besoins, meta } = calculBesoinEchafaudage(h, l, w);

    const recap = [];
    const ajustements = [];

    setArticles((prev) =>
      prev.map((a) => {
        const cat = detectCategorie(a.nom);
        if (besoins[cat]) {
          let utilise = 0;
          if (a.quantite >= besoins[cat]) {
            utilise = besoins[cat];
          } else {
            utilise = a.quantite;
            ajustements.push(
              `${a.nom} (besoin: ${besoins[cat]}, dispo: ${a.quantite})`
            );
          }
          recap.push({ ...a, utilisé: utilise, uuid: a.uuid });
          return { ...a, utilisé: utilise, quantite: a.quantite - utilise };
        }
        return { ...a, utilisé: 0 };
      })
    );

    setEchafaudage(recap);
    setModalOpen(true);

    document.getElementById("echafHauteur").value = "";
    document.getElementById("echafLongueur").value = "";
    document.getElementById("echafLargeur").value = "";

    if (ajustements.length) {
      setMessage({
        type: "warning",
        text: `Calcul ajusté: ${ajustements.join(" ; ")}`,
      });
    } else {
      setMessage({
        type: "success",
        text: `Calcul OK — niveaux:${meta.niveaux}, travées:${meta.travées.length}, cadres:${meta.nbCadres}`,
      });
    }
  };

  const poidsTotal = echafaudage.reduce(
    (sum, a) => sum + (a.poids || 0) * (a.utilisé || 0),
    0
  );

  /* ------------------------- EXPORT ------------------------- */
  const exportExcel = () => {
    if (!echafaudage.length) {
      setMessage({ type: "error", text: "Aucun récap à exporter" });
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
      setMessage({ type: "error", text: "Aucun récap à exporter" });
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
    setMessage({ type: "info", text: 'Champ "utilisé" remis à zéro.' });
  };

  /* ------------------------- RENDER ------------------------- */
  return (
    <div className="card">
      <div className="table-header">
        <h2>Stock d’échafaudages</h2>
        <input
          type="text"
          placeholder="Rechercher..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="input-search"
        />
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
                          <button
                            onClick={() => removeArticle(a.uuid)}
                            className="btn-remove"
                          >
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

      {/* Calcul */}
      <h3>Calcul échafaudage</h3>
      <div className="calcul-form">
        <input id="echafHauteur" type="number" step="0.01" placeholder="Hauteur (m)" />
        <input id="echafLongueur" type="number" step="0.01" placeholder="Longueur (m)" />
        <input id="echafLargeur" type="number" step="0.01" placeholder="Largeur (m)" />
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
            <table>
              <thead>
                <tr>
                  {[
                    "Nom",
                    "Quantité utilisée",
                    "Longueur",
                    "Largeur",
                    "Hauteur",
                    "Poids",
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
                    <td>{a.poids || "-"}</td>
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
