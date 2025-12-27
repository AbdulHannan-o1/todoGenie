"use client";

import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";

import { User } from '@/types/user';
import { authClient } from '@/lib/auth-client';
import apiClient from '@/lib/api-client';

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => Promise<void>;
  register: (email: string, password: string, fullName: string, username: string) => Promise<{ success: boolean; error?: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Attempt to load token and user from localStorage on initial load
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");

    if (storedToken && storedUser) {
      try {
        const parsedUser: User = JSON.parse(storedUser);
        setToken(storedToken);
        setUser(parsedUser);
        setIsAuthenticated(true);
      } catch (error) {
        console.error("Failed to parse user from localStorage", error);
        logout(); // Clear invalid data
      }
    }
    // Set loading to false after attempting to load from localStorage
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Call the auth API to get the JWT token
      const response = await authClient.login(email, password);
      const { access_token } = response;

      // Store the token in localStorage first so the interceptor can use it
      localStorage.setItem("token", access_token);

      let userData;
      try {
        userData = await authClient.getProfile();
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
        // Clear the token if profile fetch fails
        localStorage.removeItem("token");
        return { success: false, error: "Failed to fetch user profile" };
      }

      // Store user in localStorage and state
      localStorage.setItem("user", JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error: any) {
      console.error("Login error:", error);
      let errorMessage = "Login failed. Please try again.";

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      return { success: false, error: errorMessage };
    }
  };

  const register = async (email: string, password: string, fullName: string, username: string): Promise<{ success: boolean; error?: string }> => {
    try {
      // Register the user
      await authClient.register(email, password, username);

      // Log the user in automatically after registration
      const response = await authClient.login(email, password);
      const { access_token } = response;

      // Fetch user profile to get user details
      // Temporarily set the token in the API client to fetch user data
      const originalToken = apiClient.defaults.headers.common['Authorization'];
      apiClient.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;

      let userData;
      try {
        userData = await authClient.getProfile();
      } catch (error) {
        console.error("Failed to fetch user profile:", error);
        // Restore original token
        if (originalToken) {
          apiClient.defaults.headers.common['Authorization'] = originalToken;
        } else {
          delete apiClient.defaults.headers.common['Authorization'];
        }
        return { success: false, error: "Failed to fetch user profile" };
      }

      // Restore original token if it existed
      if (originalToken) {
        apiClient.defaults.headers.common['Authorization'] = originalToken;
      } else {
        delete apiClient.defaults.headers.common['Authorization'];
      }

      // Store token and user in localStorage and state
      localStorage.setItem("token", access_token);
      localStorage.setItem("user", JSON.stringify(userData));
      setToken(access_token);
      setUser(userData);
      setIsAuthenticated(true);

      return { success: true };
    } catch (error: any) {
      console.error("Registration error:", error);
      let errorMessage = "Registration failed. Please try again.";

      if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail;
      } else if (error.message) {
        errorMessage = error.message;
      }

      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      // Clear the auth client token if needed
      await authClient.logout();

      // Clear from localStorage
      localStorage.removeItem("token");
      localStorage.removeItem("user");

      // Clear state
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    } catch (error) {
      console.error("Logout error:", error);
      // Even if logout API call fails, clear local state
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      setToken(null);
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, token, isLoading, login, logout, register }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}