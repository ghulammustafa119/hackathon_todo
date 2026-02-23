// API service for authenticated requests to FastAPI backend
// JWT comes from httpOnly cookie via /api/auth/session (never localStorage)
import authClient from './auth';
import { Task } from '@/types/task';
import { extractErrorMessage } from './error-utils';

class ApiService {
  private baseURL: string;

  constructor() {
    this.baseURL = process.env.NEXT_PUBLIC_BACKEND_API_URL || 'http://localhost:8000/api';
  }

  /**
   * Get the JWT token - tries in-memory cache first, then httpOnly cookie.
   */
  private async getToken(): Promise<string | null> {
    // Fast path: in-memory cache
    const cached = authClient.getToken();
    if (cached) return cached;

    // Slow path: fetch from httpOnly cookie
    return authClient.getTokenAsync();
  }

  /**
   * Extract user ID from JWT payload (client-side decode, no verification).
   */
  private decodeUserId(token: string): string | null {
    try {
      const parts = token.split('.');
      if (parts.length !== 3) return null;
      const payload = JSON.parse(atob(parts[1].replace(/-/g, '+').replace(/_/g, '/')));
      return payload.sub || payload.user_id || null;
    } catch {
      return null;
    }
  }

  /**
   * Make an authenticated request to FastAPI.
   * Handles 401 globally: logs out and throws clear error.
   */
  async makeRequest<T = any>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${this.baseURL}${endpoint}`;

    const token = await this.getToken();
    const headers = {
      'Content-Type': 'application/json',
      ...options.headers,
    } as Record<string, string>;

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    const config: RequestInit = { headers, ...options };

    const response = await fetch(url, config);

    // Global 401 handler: auto-logout + redirect
    if (response.status === 401) {
      await authClient.logout();
      if (typeof window !== 'undefined') {
        window.location.href = '/login';
      }
      throw new Error('Session expired. Please log in again.');
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new Error(extractErrorMessage(errorData) || `Request failed (${response.status})`);
    }

    return await response.json();
  }

  // --- Task CRUD using /api/{user_id}/tasks ---

  private async requireUserId(): Promise<string> {
    const token = await this.getToken();
    if (!token) throw new Error('Not authenticated');
    const userId = this.decodeUserId(token);
    if (!userId) throw new Error('Invalid session');
    return userId;
  }

  async getTasks(filters?: Record<string, string>): Promise<Task[]> {
    const userId = await this.requireUserId();
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
    const userId = await this.requireUserId();
    return this.makeRequest<Task>(`/${userId}/tasks`, {
      method: 'POST',
      body: JSON.stringify(taskData),
    });
  }

  async updateTask(taskId: string, taskData: Partial<Omit<Task, 'id' | 'created_at' | 'completed_at'>>): Promise<Task> {
    const userId = await this.requireUserId();
    return this.makeRequest<Task>(`/${userId}/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(taskData),
    });
  }

  async deleteTask(taskId: string): Promise<void> {
    const userId = await this.requireUserId();
    await this.makeRequest(`/${userId}/tasks/${taskId}`, {
      method: 'DELETE',
    });
  }

  async toggleTaskCompletion(taskId: string): Promise<Task> {
    const userId = await this.requireUserId();
    return this.makeRequest<Task>(`/${userId}/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  }

  // --- Audit Log ---

  async getTaskEvents(taskId: string): Promise<any[]> {
    const userId = await this.requireUserId();
    return this.makeRequest<any[]>(`/${userId}/tasks/${taskId}/events`);
  }

  // --- Notifications ---

  async getNotifications(): Promise<any[]> {
    const userId = await this.requireUserId();
    return this.makeRequest<any[]>(`/${userId}/notifications`);
  }

  async markNotificationRead(notificationId: string): Promise<void> {
    const userId = await this.requireUserId();
    await this.makeRequest(`/${userId}/notifications/${notificationId}/read`, {
      method: 'PATCH',
    });
  }
}

const apiService = new ApiService();
export default apiService;
