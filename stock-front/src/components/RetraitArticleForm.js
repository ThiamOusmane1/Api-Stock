import React, { useState, useEffect } from 'react';
import Message from './Message';
import '../App.css';

const API_URL = process.env.REACT_APP_API_BASE_URL || 'http://127.0.0.1:8000';

const RetraitArticleForm = ({ onArticleRetire }) => {
  const [nomArticle, setNomArticle] = useState('');
  const [quantite, setQuantite] = useState('');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [allArticles, setAllArticles] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  // Charger la liste des articles pour l'autocomplétion
  useEffect(() => {
    const fetchArticleNames = async () => {
      try {
        const token = JSON.parse(localStorage.getItem('user')).access_token;
        const response = await fetch(`${API_URL}/articles/noms`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (response.ok) {
          const data = await response.json();
          setAllArticles(data);
        }
      } catch (err) {
        console.error('Erreur chargement articles:', err);
      }
    };
    fetchArticleNames();
  }, []);

  // Filtrer les suggestions
  const handleNomChange = (value) => {
    setNomArticle(value);
    if (value.length >= 2) {
      const filtered = allArticles.filter((nom) =>
        nom.toLowerCase().includes(value.toLowerCase())
      );
      setSuggestions(filtered.slice(0, 8));
      setShowSuggestions(true);
    } else {
      setSuggestions([]);
      setShowSuggestions(false);
    }
  };

  const selectSuggestion = (nom) => {
    setNomArticle(nom);
    setSuggestions([]);
    setShowSuggestions(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setMessage(null);

    if (!nomArticle || !quantite) {
      setMessage({ type: 'error', text: 'Veuillez renseigner le nom de l\'article et la quantité.' });
      return;
    }

    if (parseInt(quantite) <= 0) {
      setMessage({ type: 'error', text: 'La quantité doit être supérieure à 0.' });
      return;
    }

    setLoading(true);
    try {
      const token = JSON.parse(localStorage.getItem('user')).access_token;

      // ✅ CORRIGÉ : POST /retraits/ avec nom_article dans le body
      const response = await fetch(`${API_URL}/retraits/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          nom_article: nomArticle,
          quantite: parseInt(quantite),
        }),
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erreur lors du retrait');
      }

      const data = await response.json();

      setMessage({
        type: 'success',
        text: `✅ Retrait effectué !
📦 Article : ${data.nom_article}
📉 Quantité retirée : ${data['quantité_retirée'] || data.quantite_retiree || parseInt(quantite)}
📊 Stock restant : ${data.stock_restant}
⚖️ Poids total retiré : ${data.poids_total} kg`,
      });

      setNomArticle('');
      setQuantite('');
      if (onArticleRetire) onArticleRetire();

    } catch (err) {
      console.error('Erreur lors du retrait :', err);
      setMessage({
        type: 'error',
        text: err.message || "Impossible d'effectuer le retrait. Vérifiez le nom ou la quantité.",
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="table-header">
        <h2>📤 Retirer un Article</h2>
      </div>

      <Message type={message?.type} text={message?.text} />

      <form onSubmit={handleSubmit} className="ajout-form" style={{ flexDirection: 'column' }}>

        {/* Nom article avec autocomplétion */}
        <div style={{ position: 'relative', width: '100%' }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 600, fontSize: 14 }}>
            Nom de l'article *
          </label>
          <input
            type="text"
            value={nomArticle}
            onChange={(e) => handleNomChange(e.target.value)}
            onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
            onFocus={() => nomArticle.length >= 2 && setShowSuggestions(true)}
            placeholder="Ex: Poteau 2m, Moise 3.07m..."
            className="input-ajout"
            style={{ width: '100%' }}
            autoComplete="off"
            required
          />

          {/* Liste de suggestions */}
          {showSuggestions && suggestions.length > 0 && (
            <div style={{
              position: 'absolute',
              top: '100%',
              left: 0,
              right: 0,
              background: 'white',
              border: '2px solid #667eea',
              borderRadius: '0 0 8px 8px',
              zIndex: 100,
              maxHeight: 200,
              overflowY: 'auto',
              boxShadow: '0 4px 12px rgba(0,0,0,0.15)',
            }}>
              {suggestions.map((nom, idx) => (
                <div
                  key={idx}
                  onMouseDown={() => selectSuggestion(nom)}
                  style={{
                    padding: '10px 14px',
                    cursor: 'pointer',
                    fontSize: 14,
                    borderBottom: '1px solid #f0f0f0',
                    transition: 'background 0.15s',
                  }}
                  onMouseEnter={(e) => e.target.style.background = '#f8f9ff'}
                  onMouseLeave={(e) => e.target.style.background = 'white'}
                >
                  📦 {nom}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Quantité */}
        <div style={{ width: '100%' }}>
          <label style={{ display: 'block', marginBottom: 6, fontWeight: 600, fontSize: 14 }}>
            Quantité à retirer *
          </label>
          <input
            type="number"
            value={quantite}
            onChange={(e) => setQuantite(e.target.value)}
            placeholder="Ex: 10"
            className="input-ajout"
            style={{ width: '100%' }}
            min="1"
            required
          />
        </div>

        {/* Bouton */}
        <button
          type="submit"
          className="btn-calc"
          disabled={loading}
          style={{ width: '100%', marginTop: 4 }}
        >
          {loading ? '⏳ Retrait en cours...' : '📤 Effectuer le retrait'}
        </button>
      </form>
    </div>
  );
};

export default RetraitArticleForm;
