import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_BACKEND_API_URL || "http://localhost:8001/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor for JWT injection
apiClient.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token"); // Assuming token is stored in localStorage
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
apiClient.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Centralized error handling logic
    if (error.response) {
      // The request was made and the server responded with a status code
      // that falls out of the range of 2xx
      console.error("API Error Response:", error.response.data);
      console.error("Status:", error.response.status);
      console.error("Headers:", error.response.headers);

      // You might want to trigger a global error notification here
      // e.g., using a toast library or a global state management
      // if (error.response.status === 401) {
      //   // Handle unauthorized, e.g., redirect to login
      // }
      // if (error.response.status === 403) {
      //   // Handle forbidden
      // }
    } else if (error.request) {
      // The request was made but no response was received
      console.error("API Error Request:", error.request);
    } else {
      // Something happened in setting up the request that triggered an Error
      console.error("API Error Message:", error.message);
    }
    return Promise.reject(error);
  }
);

export default apiClient;
