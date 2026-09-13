// src/api/client.js

import axios from "axios";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ||
  "http://127.0.0.1:8000/api/v1";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 120000,
  headers: {
    Accept: "application/json",
  },
});

apiClient.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error)
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const normalizedError = {
      status: error.response?.status ?? null,
      message:
        error.response?.data?.detail ||
        error.response?.data?.message ||
        error.message ||
        "An unexpected server error occurred.",
      data: error.response?.data ?? null,
    };

    return Promise.reject(normalizedError);
  }
);

export default apiClient;