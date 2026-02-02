// Token management service
interface TokenPayload {
  sub?: string;
  user_id?: string;
  exp?: number;
  [key: string]: any;
}

class TokenService {
  // Store token in localStorage
  setToken(token: string) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Get token from localStorage
  getToken(): string | null {
    if (typeof window !== 'undefined') {
      return localStorage.getItem('auth_token');
    }
    return null;
  }

  // Remove token from localStorage
  removeToken() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
  }

  // Check if token exists
  hasToken(): boolean {
    return !!this.getToken();
  }

  // Decode JWT token to get user info (without verification)
  decodeToken(token: string | null): TokenPayload | null {
    if (!token) return null;

    try {
      // Remove 'Bearer ' prefix if present
      const actualToken = token.startsWith('Bearer ') ? token.slice(7) : token;

      // Split token and decode payload
      const parts = actualToken.split('.');
      if (parts.length !== 3) {
        return null;
      }

      const payload = parts[1];
      // Add padding if needed
      const paddedPayload = payload + '='.repeat((4 - payload.length % 4) % 4);

      const decodedPayload = atob(paddedPayload);
      return JSON.parse(decodedPayload);
    } catch (error) {
      console.error('Error decoding token:', error);
      return null;
    }
  }

  // Check if token is expired
  isTokenExpired(token: string | null): boolean {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return true; // If no expiration, consider expired
    }

    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  }

  // Get user ID from token
  getUserIdFromToken(token: string | null): string | null {
    const decoded = this.decodeToken(token);
    return decoded ? decoded.sub || decoded.user_id : null;
  }

  // Get token expiration time
  getTokenExpiration(token: string | null): number | null {
    const decoded = this.decodeToken(token);
    return decoded ? decoded.exp : null;
  }
}

// Create a singleton instance
const tokenService = new TokenService();

export default tokenService;