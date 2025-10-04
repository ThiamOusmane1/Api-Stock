import React from "react";
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import { AuthProvider } from "./AuthContext";
import ProtectedRoute from "./components/ProtectedRoute";
import LoginPage from "./pages/LoginPage";
import Dashboard from "./pages/Dashboard";

function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          <Route path="/login" element={<LoginPage />} />
          <Route
            path="/"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;
