import React, { useContext, useState } from "react";
import { AuthContext } from "../AuthContext";
import { useNavigate } from "react-router-dom";

const LoginPage = () => {
  const { login } = useContext(AuthContext);
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      await login(username, password);
      navigate("/");
    } catch (err) {
      setError("Identifiants invalides");
    }
  };

  return (
    <div className="card">
      <h2>Connexion</h2>
      {error && <p style={{ color: "red" }}>{error}</p>}
      <form onSubmit={handleSubmit}>
        <label>Utilisateur :</label>
        <input value={username} onChange={(e) => setUsername(e.target.value)} />

        <label>Mot de passe :</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <button type="submit">Se connecter</button>
      </form>
    </div>
  );
};

export default LoginPage;
