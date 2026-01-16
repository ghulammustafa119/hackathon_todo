// API service utilities for authenticated requests
import authClient from './auth';

class ApiService {
  constructor() {
    this.baseURL = process.env.BACKEND_API_URL || 'http://localhost:8000/api';
  }

  // Helper method to make authenticated requests
  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;

    // Add authorization header if user is authenticated
    const token = authClient.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config = {
      headers,
      ...options,
    };

    try {
      const response = await fetch(url, config);

      // Handle 401 Unauthorized responses
      if (response.status === 401) {
        // Token might be expired, logout user
        await authClient.logout();
        throw new Error('Authentication required. Please log in again.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Task-related API methods
  async getTasks() {
    return this.makeRequest('/tasks');
  }

  async createTask(taskData) {
    return this.makeRequest('/tasks', {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId, taskData) {
    return this.makeRequest(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(taskId) {
    return this.makeRequest(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(taskId) {
    return this.makeRequest(`/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }
}

// Create a singleton instance
const apiService = new ApiService();

export default apiService;