import { createContext, useContext, useEffect, useMemo, useState } from "react";
import type { AuthUser, LoginRequest } from "../models/Auth";
import { authService } from "../services/authService";

interface AuthContextValue {
  user: AuthUser | null;
  token: string | null;
  loadingAuth: boolean;
  isAuthenticated: boolean;
  login: (data: LoginRequest) => Promise<void>;
  logout: () => void;
  hasPermission: (path: string) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem("accessToken"));
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  const logout = () => {
    localStorage.removeItem("accessToken");
    setToken(null);
    setUser(null);
  };

  const login = async (data: LoginRequest) => {
    const response = await authService.login(data);

    if (!response.isSuccess || !response.result) {
      throw new Error(response.Message || "No se pudo iniciar sesión.");
    }

    localStorage.setItem("accessToken", response.result.accessToken);
    setToken(response.result.accessToken);
    setUser(response.result.user);
  };

  const hasPermission = (path: string) => {
    if (path === "/") return true;
    return (user?.menuOptions.some((item) => item.statusMenuOption && item.pathMenuOption === path) ?? false);
  };

  useEffect(() => {
    const loadCurrentUser = async () => {
      const storedToken = localStorage.getItem("accessToken");

      if (!storedToken) {
        setLoadingAuth(false);
        return;
      }

      try {
        const response = await authService.me();

        if (!response.isSuccess || !response.result) {
          logout();
          return;
        }

        localStorage.setItem("accessToken", response.result.accessToken);
        setToken(response.result.accessToken);
        setUser(response.result.user);
      } catch {
        logout();
      } finally {
        setLoadingAuth(false);
      }
    };

    loadCurrentUser();
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      token,
      loadingAuth,
      isAuthenticated: Boolean(token && user),
      login,
      logout,
      hasPermission,
    }),
    [user, token, loadingAuth]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);

  if (!context) {
    throw new Error("useAuth debe usarse dentro de AuthProvider.");
  }

  return context;
}