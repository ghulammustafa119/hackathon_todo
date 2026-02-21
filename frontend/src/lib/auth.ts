// Auth client that uses backend API directly for authentication

class AuthClientWrapper {
  private token: string | null;
  private backendURL: string;

  constructor() {
    this.token = null;
    this.backendURL =
      process.env.NEXT_PUBLIC_BACKEND_API_URL ||
      "http://localhost:8000/api";
    this.init();
  }

  async init() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  // Login user
  async login(credentials: {
    email: string;
    password: string;
  }): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      const response = await fetch(`${this.backendURL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
      });

      if (response.ok) {
        const data = await response.json();
        this.token = data.token;

        if (typeof window !== "undefined" && this.token) {
          localStorage.setItem("auth_token", this.token);
          await fetch("/api/auth/token", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token: this.token }),
          }).catch(() => {});
        }

        return { success: true, user: data.user || { email: credentials.email } };
      } else {
        const error = await response.json().catch(() => ({}));
        return {
          success: false,
          error: error.detail || error.message || "Login failed",
        };
      }
    } catch (error: any) {
      return { success: false, error: error.message || "Login failed" };
    }
  }

  // Register user
  async register(userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      const response = await fetch(`${this.backendURL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(userData),
      });

      if (response.ok) {
        const data = await response.json();
        return { success: true, user: data };
      } else {
        const error = await response.json().catch(() => ({}));
        return {
          success: false,
          error: error.detail || error.message || "Registration failed",
        };
      }
    } catch (error: any) {
      return { success: false, error: error.message || "Registration failed" };
    }
  }

  // Logout user
  async logout(): Promise<{ success: boolean }> {
    try {
      await fetch(`${this.backendURL}/auth/logout`, {
        method: "POST",
        headers: {
          Authorization: `Bearer ${this.token}`,
          "Content-Type": "application/json",
        },
      }).catch(() => {});
    } catch {
      // Ignore errors
    }

    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      await fetch("/api/auth/token", { method: "DELETE" }).catch(() => {});
    }
    return { success: true };
  }

  // Get current user
  async getCurrentUser() {
    if (!this.token) return null;

    try {
      const response = await fetch(`${this.backendURL}/auth/user`, {
        method: "GET",
        headers: { Authorization: `Bearer ${this.token}` },
      });

      if (response.ok) {
        const userData = await response.json();
        return { ...userData, isAuthenticated: true };
      } else {
        this.token = null;
        if (typeof window !== "undefined") {
          localStorage.removeItem("auth_token");
        }
        return null;
      }
    } catch {
      return null;
    }
  }

  isAuthenticated() {
    return !!this.token;
  }

  getToken() {
    return this.token;
  }
}

// Create singleton instance
const authClientWrapper = new AuthClientWrapper();

export default authClientWrapper;
