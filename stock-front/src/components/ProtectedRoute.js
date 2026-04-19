import { useContext } from "react";
import { Navigate } from "react-router-dom";
import { AuthContext } from "../AuthContext";

const ProtectedRoute = ({ children }) => {
  const { user, loading } = useContext(AuthContext);

  // ⏳ ON ATTEND LA FIN DU CHARGEMENT
  if (loading) {
    return <div>Chargement...</div>; // ou spinner
  }

  // ❌ Pas connecté
  if (!user) {
    return <Navigate to="/login" replace />;
  }

  // ✅ Connecté
  return children;
};

export default ProtectedRoute;