import apiClient from "./api-client";

export const authClient = {
  register: async (email: string, password: string, username: string) => {
    const response = await apiClient.post("/auth/register", {
      email,
      password,
      username // Backend expects username field
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const loginData = new FormData();
    loginData.append('username', email);  // Backend expects 'username' field (but will treat as email)
    loginData.append('password', password);

    const response = await apiClient.post("/api/auth/token", loginData);
    return response.data;
  },

  logout: async () => {
    // For stateless JWTs, logout means clearing the client-side token
    // The backend doesn't need to do anything since tokens are stateless
    // We'll just return a success response
    return { success: true };
  },

  getProfile: async () => {
    const response = await apiClient.get("/users/me");
    return response.data;
  },

  refreshToken: async () => {
    // In a real implementation, you might have a refresh token endpoint
    // For now, we'll just return a method that could be used for token refresh
    // Currently, refresh endpoint doesn't exist in the backend
    throw new Error("Refresh token endpoint not implemented");
  }
};