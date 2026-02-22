// Better Auth client - ALL authentication goes through Better Auth
// FastAPI backend is used ONLY for tasks/business logic
import { createAuthClient } from "better-auth/react";
import { jwtClient } from "better-auth/client/plugins";
import { extractErrorMessage } from "./error-utils";

// Create Better Auth client pointing to Next.js API routes
export const authClient = createAuthClient({
  baseURL:
    process.env.NEXT_PUBLIC_BETTER_AUTH_URL ||
    (typeof window !== "undefined" ? window.location.origin : "http://localhost:3000"),
  plugins: [jwtClient()],
});

/**
 * Set a simple cookie so Next.js middleware can check auth.
 * Not httpOnly so middleware can read it.
 */
function setAuthCookie(token: string) {
  if (typeof document !== "undefined") {
    const maxAge = 60 * 60 * 24 * 7; // 7 days
    const secure = window.location.protocol === "https:" ? ";Secure" : "";
    document.cookie = `auth_token=${token};path=/;max-age=${maxAge};SameSite=Lax${secure}`;
  }
}

function clearAuthCookie() {
  if (typeof document !== "undefined") {
    document.cookie = "auth_token=;path=/;max-age=0";
  }
}

// Auth wrapper that uses ONLY Better Auth for authentication
class AuthClientWrapper {
  private token: string | null;

  constructor() {
    this.token = null;
    this.init();
  }

  private async init() {
    if (typeof window !== "undefined") {
      this.token = localStorage.getItem("auth_token");
    }
  }

  /**
   * Fetch JWT from Better Auth and store in localStorage + cookie.
   * Returns the JWT string or null.
   */
  private async fetchAndStoreToken(): Promise<string | null> {
    try {
      const tokenResult = await authClient.token();
      if (tokenResult.data?.token) {
        this.token = tokenResult.data.token;
        if (typeof window !== "undefined") {
          localStorage.setItem("auth_token", this.token);
          setAuthCookie(this.token);
        }
        return this.token;
      }
    } catch (err) {
      console.warn("Failed to retrieve JWT from Better Auth:", err);
    }
    return null;
  }

  // Login user via Better Auth ONLY
  async login(credentials: {
    email: string;
    password: string;
  }): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      const result = await authClient.signIn.email({
        email: credentials.email,
        password: credentials.password,
      });

      if (result.error) {
        return { success: false, error: extractErrorMessage(result.error) };
      }

      if (result.data) {
        // Get JWT token for backend API calls
        await this.fetchAndStoreToken();
        return {
          success: true,
          user: result.data.user || { email: credentials.email },
        };
      }

      return { success: false, error: "Login failed. Please try again." };
    } catch (err: any) {
      return { success: false, error: extractErrorMessage(err) };
    }
  }

  // Register user via Better Auth ONLY
  async register(userData: {
    email: string;
    password: string;
    name: string;
  }): Promise<{ success: boolean; user?: any; error?: string }> {
    try {
      const result = await authClient.signUp.email({
        email: userData.email,
        password: userData.password,
        name: userData.name,
      });

      if (result.error) {
        return { success: false, error: extractErrorMessage(result.error) };
      }

      if (result.data) {
        // After signup, Better Auth also logs in the user - get JWT
        await this.fetchAndStoreToken();
        return { success: true, user: result.data.user || result.data };
      }

      return { success: false, error: "Registration failed. Please try again." };
    } catch (err: any) {
      return { success: false, error: extractErrorMessage(err) };
    }
  }

  // Logout user via Better Auth
  async logout(): Promise<{ success: boolean }> {
    try {
      await authClient.signOut();
    } catch {
      // Ignore signout errors
    }

    this.token = null;
    if (typeof window !== "undefined") {
      localStorage.removeItem("auth_token");
      clearAuthCookie();
    }
    return { success: true };
  }

  // Get current user from Better Auth session
  async getCurrentUser() {
    try {
      const session = await authClient.getSession();
      if (session.data?.user) {
        // Also ensure we have a JWT token for backend calls
        if (!this.token) {
          await this.fetchAndStoreToken();
        }
        return { ...session.data.user, isAuthenticated: true };
      }
    } catch {
      // Session not available
    }

    // No valid session - clear stale tokens
    if (this.token) {
      this.token = null;
      if (typeof window !== "undefined") {
        localStorage.removeItem("auth_token");
        clearAuthCookie();
      }
    }
    return null;
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
