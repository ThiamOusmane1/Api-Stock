import React, { useState } from "react";
import { useAuth } from "../AuthContext";

const LoginPage = () => {
  const { login } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
    } catch (err) {
      setError("❌ Identifiants invalides");
    }
  };

  return (
    <div className="card">
      <h2>Connexion</h2>
      {error && <p className="message error">{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>Nom d’utilisateur :</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />
        <label>Mot de passe :</label>
        <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
        <button type="submit">Se connecter</button>
      </form>
    </div>
  );
};

export default LoginPage;
