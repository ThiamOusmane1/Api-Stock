import React, { useContext } from "react";
import ArticleList from "../components/ArticleList";
import { AuthContext } from "../AuthContext";

const Dashboard = () => {
  const { logout } = useContext(AuthContext);

  return (
    <div className="container">
      <h1>Gestion du Stock d’Échafaudages</h1>
      <button onClick={logout} style={{ float: "right" }}>
        🚪 Déconnexion
      </button>
      <ArticleList />
    </div>
  );
};

export default Dashboard;
