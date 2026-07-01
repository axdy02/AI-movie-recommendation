import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { authApi, preferencesApi } from "../api/endpoints.js";
import { clearStoredToken, getStoredToken, setStoredToken } from "../api/axios.js";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [bootstrapping, setBootstrapping] = useState(true);
  const [authError, setAuthError] = useState("");

  const refreshUser = useCallback(async () => {
    const currentUser = await authApi.me();
    setUser(currentUser);
    return currentUser;
  }, []);

  useEffect(() => {
    let active = true;
    async function bootstrap() {
      const token = getStoredToken();
      if (!token) {
        setBootstrapping(false);
        return;
      }
      try {
        setStoredToken(token);
        const currentUser = await authApi.me();
        if (active) setUser(currentUser);
      } catch {
        clearStoredToken();
        if (active) setUser(null);
      } finally {
        if (active) setBootstrapping(false);
      }
    }
    bootstrap();
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(
    async (payload) => {
      setAuthError("");
      const token = await authApi.login(payload);
      setStoredToken(token.access_token);
      return refreshUser();
    },
    [refreshUser],
  );

  const register = useCallback(
    async ({ preferences, ...payload }) => {
      setAuthError("");
      const response = await authApi.register(payload);
      const token = response.token || response;
      setStoredToken(token.access_token);
      const currentUser = response.user || (await refreshUser());
      setUser(currentUser);
      if (preferences) {
        await preferencesApi.update(currentUser.id, preferences);
      }
      return currentUser;
    },
    [refreshUser],
  );

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const value = useMemo(
    () => ({
      user,
      isAuthenticated: Boolean(user),
      isAdmin: user?.role === "admin",
      bootstrapping,
      authError,
      setAuthError,
      login,
      logout,
      refreshUser,
      register,
    }),
    [authError, bootstrapping, login, logout, refreshUser, register, user],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used inside AuthProvider.");
  }
  return context;
}
