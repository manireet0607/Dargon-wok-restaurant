import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import { api, getToken, setToken } from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(!!getToken());

  const logout = useCallback(() => {
    setToken(null);
    setUser(null);
  }, []);

  useEffect(() => {
    if (!getToken()) return;
    api.me().then(setUser).catch(logout).finally(() => setLoading(false));
  }, [logout]);

  useEffect(() => {
    window.addEventListener("dw:unauthorized", logout);
    return () => window.removeEventListener("dw:unauthorized", logout);
  }, [logout]);

  const value = useMemo(
    () => ({
      user,
      loading,
      isAdmin: user?.role === "admin",
      async login(email, password) {
        const res = await api.login({ email, password });
        setToken(res.access_token);
        setUser(res.user);
        return res.user;
      },
      async register(data) {
        const res = await api.register(data);
        setToken(res.access_token);
        setUser(res.user);
        return res.user;
      },
      logout,
    }),
    [user, loading, logout]
  );
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const useAuth = () => useContext(AuthContext);
