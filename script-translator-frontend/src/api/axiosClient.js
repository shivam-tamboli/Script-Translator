import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const axiosClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
});

axiosClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      const { status, data } = error.response;
      if (status === 400) {
        throw new Error(data.detail || 'Bad request');
      }
      if (status === 401) {
        throw new Error('API key required');
      }
      if (status === 404) {
        throw new Error('Resource not found');
      }
      if (status === 500) {
        throw new Error('Server error');
      }
    }
    throw new Error('Network error. Please check your connection.');
  }
);

export default axiosClient;
