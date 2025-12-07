import React, { useContext } from "react";
import { AuthContext } from "../AuthContext";
import SuperAdminDashboard from "../components/SuperAdminDashboard";
import AdminDashboard from "../components/AdminDashboard";
import UserDashboard from "../components/UserDashboard";
import "../App.css";

const Dashboard = () => {
  const { user } = useContext(AuthContext);

  if (!user) {
    return <div>Chargement...</div>;
  }

  console.log("👤 [Dashboard] User connecté:", user);
  console.log("🎭 [Dashboard] Rôle:", user.role);

  // Afficher le dashboard selon le rôle
  switch (user.role?.toLowerCase()) {
    case "superadmin":
      return <SuperAdminDashboard user={user} />;
    case "admin":
      return <AdminDashboard user={user} />;
    case "user":
      return <UserDashboard user={user} />;
    default:
      return (
        <div className="dashboard-container">
          <div className="card">
            <h1>Rôle inconnu</h1>
            <p>Votre rôle "{user.role}" n'est pas reconnu. Contactez l'administrateur.</p>
          </div>
        </div>
      );
  }
};

export default Dashboard;