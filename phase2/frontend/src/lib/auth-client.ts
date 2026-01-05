import apiClient from "./api-client";

export const authClient = {
  register: async (email: string, password: string) => {
    const response = await apiClient.post("/auth/register", { email, password });
    return response.data;
  },

  login: async (email: string, password: string) => {
    const response = await apiClient.post("/auth/login", { email, password });
    return response.data;
  },

  logout: async () => {
    const response = await apiClient.post("/auth/logout");
    return response.data;
  },

  getProfile: async () => {
    const response = await apiClient.get("/users/me");
    return response.data;
  },
};
