import apiClient from "./api-client";

export const authClient = {
  register: async (email: string, password: string, username: string) => {
    const response = await apiClient.post("/api/auth/register", {
      email,
      password,
      username // Backend expects username field
    });
    return response.data;
  },

  login: async (email: string, password: string) => {
    // Create form data for OAuth2PasswordRequestForm
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await apiClient.post("/api/auth/token", formData, {
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
    });
    // Store the token in localStorage for use in other API calls
    if (response.data && response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);

      // Get user profile to store user ID
      try {
        const profileResponse = await apiClient.get("/api/users/me");
        if (profileResponse.data && profileResponse.data.id) {
          localStorage.setItem('user', JSON.stringify(profileResponse.data));
        }
      } catch (error) {
        console.error("Error fetching user profile after login:", error);
      }
    }
    return response.data;
  },

  logout: async () => {
    // For stateless JWTs, logout means clearing the client-side token
    // The backend doesn't need to do anything since tokens are stateless
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    return { success: true };
  },

  getProfile: async () => {
    const response = await apiClient.get("/api/users/me");
    return response.data;
  },

  refreshToken: async () => {
    // In a real implementation, you might have a refresh token endpoint
    // For now, we'll just return a method that could be used for token refresh
    // Currently, refresh endpoint doesn't exist in the backend
    throw new Error("Refresh token endpoint not implemented");
  }
};