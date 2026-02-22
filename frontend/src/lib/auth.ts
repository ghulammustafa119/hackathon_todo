// Better Auth client integration with backend API fallback
// Uses Better Auth for session management when configured,
// falls back to backend API for authentication
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";
import { extractErrorMessage } from "./error-utils";

// Create Better Auth client (used when Better Auth is fully configured)
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL || (typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"),
  plugins: [jwtClient()],
});

// Auth wrapper that uses backend API for login/register
// and supports Better Auth when fully configured
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
    // Try Better Auth first
    try {
      const result = await authClient.signIn.email({
        email: credentials.email,
        password: credentials.password,
      });

      if (!result.error && result.data) {
        // Better Auth login succeeded, get JWT token for backend
        const tokenResult = await authClient.token();
        if (tokenResult.data?.token) {
          this.token = tokenResult.data.token;
          if (typeof window !== "undefined") {
            localStorage.setItem("auth_token", this.token);
            await fetch("/api/auth/token", {
              method: "POST",
              headers: { "Content-Type": "application/json" },
              body: JSON.stringify({ token: this.token }),
            }).catch(() => {});
          }
        }
        return { success: true, user: { email: credentials.email } };
      }
    } catch {
      // Better Auth not available, fall through to backend API
    }

    // Fallback: Use backend API directly
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
          error: extractErrorMessage(error),
        };
      }
    } catch (error: any) {
      return { success: false, error: extractErrorMessage(error) };
    }
  }

  // Register user
  async register(userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<{ success: boolean; user?: any; error?: string }> {
    // Try Better Auth first
    try {
      const result = await authClient.signUp.email({
        email: userData.email,
        password: userData.password,
        name: userData.name,
      });

      if (!result.error && result.data) {
        return { success: true, user: result.data };
      }
    } catch {
      // Better Auth not available, fall through to backend API
    }

    // Fallback: Use backend API directly
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
          error: extractErrorMessage(error),
        };
      }
    } catch (error: any) {
      return { success: false, error: extractErrorMessage(error) };
    }
  }

  // Logout user
  async logout(): Promise<{ success: boolean }> {
    try {
      await authClient.signOut();
    } catch {
      // Ignore Better Auth signout errors
    }

    // Also call backend logout
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

    // Try Better Auth session first
    try {
      const session = await authClient.getSession();
      if (session.data?.user) {
        return { ...session.data.user, isAuthenticated: true };
      }
    } catch {
      // Fall through to backend
    }

    // Fallback: verify via backend
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
