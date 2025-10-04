import React, { useState } from 'react';
import { retirerArticle } from '../api';
import Message from './Message';

const RetraitArticleForm = ({ onArticleRetire }) => {
  const [articleId, setArticleId] = useState('');
  const [quantite, setQuantite] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);

    if (!articleId || !quantite) {
      setMessage({ type: 'error', text: 'Veuillez renseigner l’ID et la quantité.' });
      return;
    }

    setLoading(true);
    try {
      const response = await retirerArticle(articleId, quantite);

      // Affichage complet et clair pour l’utilisateur
      setMessage({
        type: 'success',
        text: `✅ Retrait effectué !
Article : ${response.nom_article}
Quantité retirée : ${response.quantite_retirée}
Stock restant : ${response.stock_restant}
Poids total retiré : ${response.poids_total} kg`
      });

      setArticleId('');
      setQuantite('');

      if (onArticleRetire) onArticleRetire();

    } catch (err) {
      console.error('Erreur lors du retrait :', err);
      setMessage({
        type: 'error',
        text: "Impossible d'effectuer le retrait. Vérifiez l’ID ou la quantité."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <h2>Retirer un Article</h2>
      <Message type={message?.type} text={message?.text} />
      <form onSubmit={handleSubmit}>
        <label>Nom de l'article :</label>
        <input
          type="text"
          value={articleId}   //  articleId mais c’est le nom
          onChange={(e) => setArticleId(e.target.value)}
        />

        <label>Quantité à retirer :</label>
        <input
          type="number"
          value={quantite}
          onChange={e => setQuantite(e.target.value)}
          min="1"
        />

        <button type="submit" disabled={loading}>
          {loading ? 'Retrait en cours...' : 'Retirer'}
        </button>
      </form>
    </div>
  );
};

export default RetraitArticleForm;
