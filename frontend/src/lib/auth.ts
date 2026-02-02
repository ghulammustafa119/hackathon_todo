// Better Auth client integration
// This file sets up the auth client for the frontend
import { LoginResponse } from '@/types/auth';

interface LoginCredentials {
  email: string;
  password: string;
}

interface RegisterData {
  email: string;
  password: string;
}

interface LoginResult {
  success: boolean;
  user?: { email: string };
  error?: string;
}

interface LogoutResult {
  success: boolean;
}

interface RegisterResult {
  success: boolean;
  user?: any;
  error?: string;
}

class AuthClient {
  private baseURL: string;
  private token: string | null;

  constructor() {
    this.baseURL = process.env.BETTER_AUTH_URL || 'http://localhost:8000/api/auth';
    this.token = null;
  }

  // Initialize auth state from localStorage or cookies
  async init() {
    const storedToken = typeof window !== 'undefined'
      ? localStorage.getItem('auth_token')
      : null;

    if (storedToken) {
      this.token = storedToken;

      // If token exists in localStorage but not in cookies, sync it
      if (typeof window !== 'undefined') {
        await fetch('/api/auth/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ token: storedToken }),
        });
      }
    }
  }

  // Login user
  async login(credentials: LoginCredentials): Promise<LoginResult> {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data: LoginResponse = await response.json();
        this.token = data.token; // Backend now returns token in the expected format

        if (typeof window !== 'undefined') {
          localStorage.setItem('auth_token', this.token);

          // Also set the token in a cookie for middleware access
          await fetch('/api/auth/token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ token: this.token }),
          });
        }

        return { success: true, user: { email: credentials.email } }; // Return minimal user data
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || error.message }; // Backend returns detail field
      }
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // Logout user
  async logout(): Promise<LogoutResult> {
    try {
      // Call the logout endpoint (optional, since we just clear the token client-side)
      await fetch(`${this.baseURL}/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${this.token}`,
          'Content-Type': 'application/json',
        },
      }).catch(() => {}); // Ignore logout endpoint errors, just clear local state

      this.token = null;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');

        // Also clear the token cookie
        await fetch('/api/auth/token', {
          method: 'DELETE',
        });
      }

      return { success: true };
    } catch (error: any) {
      // Even if there's an error, clear the local token
      this.token = null;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');

        // Also clear the token cookie
        await fetch('/api/auth/token', {
          method: 'DELETE',
        });
      }

      return { success: true }; // Still return success to allow UI transition
    }
  }

  // Register user
  async register(userData: RegisterData): Promise<RegisterResult> {
    try {
      const response = await fetch(`${this.baseURL}/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        // Note: Registration doesn't automatically log in user in our backend
        // So we don't set the token here
        return { success: true, user: data };
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || error.message };
      }
    } catch (error: any) {
      return { success: false, error: error.message };
    }
  }

  // Get current user
  async getCurrentUser() {
    if (!this.token) {
      return null;
    }

    try {
      const response = await fetch(`${this.baseURL}/user`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${this.token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        // Add the token to the user data for consistency
        return { ...userData, isAuthenticated: true };
      } else {
        // Token might be expired, clear it
        this.token = null;
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        return null;
      }
    } catch (error) {
      return null;
    }
  }

  // Check if user is authenticated
  isAuthenticated() {
    return !!this.token;
  }

  // Get auth token
  getToken() {
    return this.token;
  }
}

// Create a singleton instance
const authClient = new AuthClient();

// Note: Since init is now async, consumers should await the authClient to be ready
// Or call init() manually when needed
// For now, we'll call it without awaiting, but components using auth should be aware
authClient.init().catch(console.error);

export default authClient;