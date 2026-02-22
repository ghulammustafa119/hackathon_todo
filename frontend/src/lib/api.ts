// API service utilities for authenticated requests to FastAPI backend
// FastAPI is used ONLY for tasks/business logic - NOT for auth
import authClient from './auth';
import tokenService from './auth-service';
import { Task } from '@/types/task';
import { extractErrorMessage } from './error-utils';

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000/api';
  }

  // Get user ID by decoding the stored JWT token
  private getUserId(): string | null {
    const token = authClient.getToken();
    return tokenService.getUserIdFromToken(token);
  }

  // Helper method to make authenticated requests to FastAPI
  async makeRequest<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    // Get JWT token from Better Auth (stored in localStorage)
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

      // Handle 401 Unauthorized - token expired or invalid
      if (response.status === 401) {
        await authClient.logout();
        throw new Error('Authentication required. Please log in again.');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(extractErrorMessage(errorData) || `HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error(`API request failed: ${endpoint}`, error);
      throw error;
    }
  }

  // Task CRUD methods using /api/{user_id}/tasks pattern
  async getTasks(filters?: Record<string, string>): Promise<Task[]> {
    const userId = this.getUserId();
    if (!userId) throw new Error('User not authenticated');
    let endpoint = `/${userId}/tasks`;
    if (filters) {
      const params = new URLSearchParams();
      for (const [key, value] of Object.entries(filters)) {
        if (value) params.append(key, value);
      }
      const qs = params.toString();
      if (qs) endpoint += `?${qs}`;
    }
    return this.makeRequest<Task[]>(endpoint);
  }

  async createTask(taskData: Omit<Task, 'id' | 'created_at' | 'completed_at'>): Promise<Task> {
    const userId = this.getUserId();
    if (!userId) throw new Error('User not authenticated');
    return this.makeRequest<Task>(`/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId: string, taskData: Partial<Omit<Task, 'id' | 'created_at' | 'completed_at'>>): Promise<Task> {
    const userId = this.getUserId();
    if (!userId) throw new Error('User not authenticated');
    return this.makeRequest<Task>(`/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(taskId: string): Promise<void> {
    const userId = this.getUserId();
    if (!userId) throw new Error('User not authenticated');
    await this.makeRequest(`/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(taskId: string): Promise<Task> {
    const userId = this.getUserId();
    if (!userId) throw new Error('User not authenticated');
    return this.makeRequest<Task>(`/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }
}

// Create a singleton instance
const apiService = new ApiService();

export default apiService;
