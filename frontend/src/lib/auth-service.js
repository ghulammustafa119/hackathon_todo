// Token management service
class TokenService {
  // Store token in localStorage
  setToken(token) {
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', token);
    }
  }

  // Get token from localStorage
  getToken() {
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
  hasToken() {
    return !!this.getToken();
  }

  // Decode JWT token to get user info (without verification)
  decodeToken(token) {
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
  isTokenExpired(token) {
    const decoded = this.decodeToken(token);
    if (!decoded || !decoded.exp) {
      return true; // If no expiration, consider expired
    }

    const currentTime = Math.floor(Date.now() / 1000);
    return decoded.exp < currentTime;
  }

  // Get user ID from token
  getUserIdFromToken(token) {
    const decoded = this.decodeToken(token);
    return decoded ? decoded.sub || decoded.user_id : null;
  }

  // Get token expiration time
  getTokenExpiration(token) {
    const decoded = this.decodeToken(token);
    return decoded ? decoded.exp : null;
  }
}

// Create a singleton instance
const tokenService = new TokenService();

export default tokenService;