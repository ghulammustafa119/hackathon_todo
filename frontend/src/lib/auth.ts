// Better Auth client - ALL authentication goes through Better Auth
// JWT is stored in httpOnly cookie via /api/auth/session (never in localStorage)
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

// Auth wrapper that uses ONLY Better Auth for authentication
// JWT is persisted in a server-side httpOnly cookie, NOT localStorage
class AuthClientWrapper {
  // In-memory cache (lives only for current page session, not persisted client-side)
  private cachedToken: string | null = null;

  /**
   * Fetch JWT from Better Auth and store in httpOnly cookie via server route.
   */
  private async fetchAndStoreToken(): Promise<string | null> {
    try {
      const tokenResult = await authClient.token();
      if (tokenResult.data?.token) {
        const token = tokenResult.data.token;

        // Store in httpOnly cookie via server-side route
        await fetch("/api/auth/session", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ token }),
        });

        this.cachedToken = token;
        return token;
      }
    } catch (err) {
      console.warn("Failed to retrieve JWT from Better Auth:", err);
    }
    return null;
  }

  /**
   * Get JWT from httpOnly cookie via server route.
   * Falls back to in-memory cache if available.
   */
  async getTokenAsync(): Promise<string | null> {
    // Fast path: use in-memory cache
    if (this.cachedToken) return this.cachedToken;

    // Fetch from httpOnly cookie via server route
    if (typeof window === "undefined") return null;
    try {
      const res = await fetch("/api/auth/session", { method: "GET" });
      if (res.ok) {
        const data = await res.json();
        if (data.token) {
          this.cachedToken = data.token;
          return data.token;
        }
      }
    } catch {
      // Cookie not available
    }
    return null;
  }

  /**
   * Synchronous getter for backwards compatibility.
   * Uses in-memory cache only (populated after login or getTokenAsync).
   */
  getToken(): string | null {
    return this.cachedToken;
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
        // Get JWT and store in httpOnly cookie
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
        // After signup, Better Auth auto-logs in - get JWT
        await this.fetchAndStoreToken();
        return { success: true, user: result.data.user || result.data };
      }

      return { success: false, error: "Registration failed. Please try again." };
    } catch (err: any) {
      return { success: false, error: extractErrorMessage(err) };
    }
  }

  // Logout user - clear Better Auth session + httpOnly cookie
  async logout(): Promise<{ success: boolean }> {
    try {
      await authClient.signOut();
    } catch {
      // Ignore signout errors
    }

    this.cachedToken = null;

    // Clear httpOnly cookie via server route
    if (typeof window !== "undefined") {
      await fetch("/api/auth/session", { method: "DELETE" }).catch(() => {});
    }
    return { success: true };
  }

  // Get current user from Better Auth session
  async getCurrentUser() {
    try {
      const session = await authClient.getSession();
      if (session.data?.user) {
        // Ensure we have a JWT for backend API calls
        if (!this.cachedToken) {
          await this.fetchAndStoreToken();
        }
        return { ...session.data.user, isAuthenticated: true };
      }
    } catch {
      // Session not available
    }

    // No valid session - clear stale cookies
    this.cachedToken = null;
    if (typeof window !== "undefined") {
      await fetch("/api/auth/session", { method: "DELETE" }).catch(() => {});
    }
    return null;
  }

  isAuthenticated() {
    return !!this.cachedToken;
  }
}

// Create singleton instance
const authClientWrapper = new AuthClientWrapper();

export default authClientWrapper;
