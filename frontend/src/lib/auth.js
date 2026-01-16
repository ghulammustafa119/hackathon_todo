// Better Auth client integration
// This file sets up the Better Auth client for the frontend

// Create a basic auth client interface
class AuthClient {
  constructor() {
    this.baseURL = process.env.BETTER_AUTH_URL || 'http://localhost:8000/api/auth';
    this.token = null;
  }

  // Initialize auth state from localStorage or cookies
  init() {
    const storedToken = typeof window !== 'undefined'
      ? localStorage.getItem('auth_token')
      : null;

    if (storedToken) {
      this.token = storedToken;
    }
  }

  // Login user
  async login(credentials) {
    try {
      const response = await fetch(`${this.baseURL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.access_token; // Backend returns access_token, not token

        if (typeof window !== 'undefined') {
          localStorage.setItem('auth_token', this.token);
        }

        return { success: true, user: { email: credentials.email } }; // Return minimal user data
      } else {
        const error = await response.json();
        return { success: false, error: error.detail || error.message }; // Backend returns detail field
      }
    } catch (error) {
      return { success: false, error: error.message };
    }
  }

  // Logout user
  async logout() {
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
      }

      return { success: true };
    } catch (error) {
      // Even if there's an error, clear the local token
      this.token = null;
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
      }

      return { success: true }; // Still return success to allow UI transition
    }
  }

  // Register user
  async register(userData) {
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
    } catch (error) {
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
authClient.init();

export default authClient;