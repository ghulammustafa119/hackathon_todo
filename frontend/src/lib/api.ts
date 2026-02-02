// API service utilities for authenticated requests
import authClient from './auth';
import { Task } from '@/types/task';
import { LoginResponse } from '@/types/auth';

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.BACKEND_API_URL || 'http://localhost:8000/api';
  }

  // Helper method to make authenticated requests
  async makeRequest<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Add authorization header if user is authenticated
    const token = authClient.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    } as Record<string, string>;

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = {
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
  async getTasks(): Promise<Task[]> {
    return this.makeRequest<Task[]>('/tasks/'); // Add trailing slash to match backend route exactly
  }

  async createTask(taskData: Omit<Task, 'id' | 'created_at' | 'completed_at'>): Promise<Task> {
    return this.makeRequest<Task>('/tasks/', { // Add trailing slash to match backend route exactly
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId: string, taskData: Partial<Omit<Task, 'id' | 'created_at' | 'completed_at'>>): Promise<Task> {
    return this.makeRequest<Task>(`/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(taskId: string): Promise<void> {
    await this.makeRequest(`/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(taskId: string): Promise<Task> {
    return this.makeRequest<Task>(`/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }

  // Auth-related API methods
  async login(email: string, password: string): Promise<LoginResponse> {
    return this.makeRequest<LoginResponse>('/auth/login', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }

  async register(email: string, password: string): Promise<{ message: string }> {
    return this.makeRequest<{ message: string }>('/auth/register', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });
  }
}

// Create a singleton instance
const apiService = new ApiService();

export default apiService;