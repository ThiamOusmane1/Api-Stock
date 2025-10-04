import React, { useState } from "react";
import { createOrUpdateArticle } from "../api";
import Message from "./Message";

const ArticleForm = ({ onSuccess }) => {
  const [nom, setNom] = useState("");
  const [quantite, setQuantite] = useState("");
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await createOrUpdateArticle({ nom, quantite: Number(quantite) });
      setMessage({ type: "success", text: "✅ Article enregistré !" });
      setNom("");
      setQuantite("");
      onSuccess();
    } catch (err) {
      setMessage({ type: "error", text: "❌ Erreur lors de l’enregistrement" });
    }
  };

  return (
    <div className="card">
      <h3>Ajouter / Modifier un Article</h3>
      <Message {...message} />
      <form onSubmit={handleSubmit}>
        <label>Nom :</label>
        <input value={nom} onChange={(e) => setNom(e.target.value)} required />

        <label>Quantité :</label>
        <input
          type="number"
          value={quantite}
          onChange={(e) => setQuantite(e.target.value)}
          required
        />

        <button type="submit">💾 Enregistrer</button>
      </form>
    </div>
  );
};

export default ArticleForm;
