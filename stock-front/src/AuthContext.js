import React, { createContext, useState } from "react";
import { login as apiLogin } from "./api";
import { saveTokens, clearTokens } from "./api/axios";

export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(
    localStorage.getItem("access_token") ? { username: "user" } : null
  );

  const login = async (username, password) => {
    const data = await apiLogin(username, password);
    saveTokens(data.access_token, data.refresh_token);
    setUser({ username });
  };

  const logout = () => {
    clearTokens();
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};
