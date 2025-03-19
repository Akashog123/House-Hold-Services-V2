import apiClient from '@/services/api.service';
import store from '@/store';

const AUTH_ENDPOINTS = {
  LOGIN: '/auth/login',
  REGISTER: '/auth/register',
  PROFILE: '/auth/profile',
  REFRESH: '/auth/refresh'
}

class AuthService {
  // Authentication state checks
  checkAuth() {
    console.log("DEBUG - checkAuth called");
    const isAuthenticated = store.getters['auth/isAuthenticated'];
    const token = store.getters['auth/token'];
    console.log(`DEBUG - isAuthenticated: ${isAuthenticated}, token exists: ${!!token}`);
    console.log(`DEBUG - token type: ${typeof token}, first 20 chars: ${token?.substring(0, 20)}`);
    return isAuthenticated && token;
  }

  checkAdmin() {
    console.log("DEBUG - checkAdmin called");
    const user = store.getters['auth/user'];
    console.log(`DEBUG - user: ${JSON.stringify(user)}`);
    const isAdmin = user?.role === 'admin';
    console.log(`DEBUG - isAdmin: ${isAdmin}`);
    const isAuth = this.checkAuth();
    console.log(`DEBUG - checkAdmin result: ${isAdmin && isAuth}`);
    return isAdmin && isAuth;
  }

  getCurrentUser() {
    return store.getters['auth/user'];
  }

  // API methods
  async login(credentials) {
    console.debug('DEBUG - Login attempt with:', credentials.username);
    try {
      console.debug('DEBUG - Sending login request to server');
      const response = await apiClient.post(AUTH_ENDPOINTS.LOGIN, credentials);
      console.debug('DEBUG - Login response received');
      console.debug('DEBUG - Response status:', response.status);
      
      if (response.data.token) {
        console.debug('DEBUG - Token received (first 20 chars):', response.data.token.substring(0, 20));
        console.debug('DEBUG - User received:', JSON.stringify(response.data.user));
        
        // Store token in localStorage for persistence
        localStorage.setItem('auth_token', response.data.token);
        
        console.debug('DEBUG - About to store token in Vuex');
        await store.dispatch('auth/setAuth', {
          token: response.data.token,
          user: response.data.user
        });
        console.debug('DEBUG - Token stored in Vuex');
        
        return response.data;
      }
      
      throw new Error('No token received from server');
    } catch (error) {
      console.debug('DEBUG - Login error:', error);
      throw error;
    }
  }

  async register(userData) {
    const response = await apiClient.post(AUTH_ENDPOINTS.REGISTER, userData)
    return response.data
  }

  async getProfile() {
    const response = await apiClient.get(AUTH_ENDPOINTS.PROFILE)
    return response.data
  }

  async refreshToken() {
    console.debug('DEBUG - refreshToken called');
    try {
      const token = store.getters['auth/token'];
      console.debug('DEBUG - Current token exists:', !!token);
      
      if (!token) {
        throw new Error('No token available to refresh');
      }
      
      // Check if token is obviously expired
      if (this.isTokenExpired()) {
        console.debug('DEBUG - Token appears expired, skipping refresh attempt');
        throw new Error('Token has expired locally');
      }
      
      console.debug('DEBUG - Sending refresh token request');
      const response = await apiClient.post(AUTH_ENDPOINTS.REFRESH);
      
      console.debug('DEBUG - Refresh token response received');
      console.debug('DEBUG - New token received:', !!response.data.token);
      
      // Update localStorage with new token
      localStorage.setItem('auth_token', response.data.token);
      
      console.debug('DEBUG - Storing new token in Vuex');
      await store.dispatch('auth/setAuth', {
        token: response.data.token,
        user: store.getters['auth/user'] // Keep the current user data
      });
      
      return response.data;
    } catch (error) {
      console.error('Token refresh error:', error);
      
      // Clear auth data on refresh failure
      localStorage.removeItem('auth_token');
      await store.dispatch('auth/clearAuth');
      
      throw error;
    }
  }

  async logout() {
    console.log('LOGOUT CALLED - Stack trace:', new Error().stack);
    
    // Try to call logout endpoint if user is authenticated
    if (store.getters['auth/isAuthenticated']) {
      try {
        await apiClient.post('/auth/logout')
          .catch(err => console.error('Logout API error:', err));
      } catch (error) {
        console.error('Logout API call failed:', error);
        // Continue with local logout even if API call fails
      }
    }
    
    // Clear localStorage
    localStorage.removeItem('auth_token');
    
    // Clear Vuex store
    await store.dispatch('auth/clearAuth');
    
    // Redirect to login page if Vue router is available
    const router = window.router;
    if (router) {
      console.log('DEBUG - Redirecting to login after logout');
      setTimeout(() => router.push('/login'), 100);
    } else {
      console.warn('DEBUG - Router not available for redirect after logout');
      // Fallback to direct location change if router is not available
      window.location.href = '/login';
    }
  }

  // Initialize auth state from localStorage on app start
  async initAuth() {
    console.log("DEBUG - initAuth called");
    const token = localStorage.getItem('auth_token');
    
    if (!token) {
      console.log("DEBUG - No token in localStorage");
      return Promise.resolve();
    }
    
    console.log(`DEBUG - Found token in localStorage (first 20 chars): ${token.substring(0, 20)}`);
    
    try {
      // Check if token is expired
      if (this.isTokenExpired()) {
        console.log("DEBUG - Token is expired, removing it");
        localStorage.removeItem('auth_token');
        return Promise.resolve();
      }
      
      // Restore auth state from localStorage
      store.dispatch('auth/setAuth', { token, user: null });
      
      // Try to validate token by fetching the user profile
      console.log("DEBUG - Validating token by fetching user profile");
      try {
        // Use /auth/profile instead of /auth/me
        const response = await apiClient.get(AUTH_ENDPOINTS.PROFILE);
        console.log("DEBUG - Token validated successfully, user data:", response.data);
        store.dispatch('auth/setUser', response.data);
        return Promise.resolve(response.data);
      } catch (error) {
        console.error("DEBUG - Token validation failed:", error);
        // If profile fetch fails, clear the auth state
        localStorage.removeItem('auth_token');
        store.dispatch('auth/clearAuth');
        return Promise.resolve();
      }
    } catch (error) {
      console.error("DEBUG - Error during auth initialization:", error);
      return Promise.resolve();
    }
  }

  // Fetch current user profile
  async fetchUserProfile() {
    try {
      const response = await apiClient.get('/auth/me');
      store.dispatch('auth/setUser', response.data);
      return response.data;
    } catch (error) {
      // If fetching profile fails, log out
      console.error('Failed to fetch user profile:', error);
      this.logout();
      throw error;
    }
  }

  // Helper to check if the current token is expired
  isTokenExpired() {
    const token = store.getters['auth/token'];
    if (!token) return true;
    
    try {
      // Decode JWT payload
      const tokenParts = token.split('.');
      if (tokenParts.length !== 3) {
        console.error('Invalid token format');
        return true;
      }
      
      const base64Url = token.split('.')[1];
      const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
      const payload = JSON.parse(window.atob(base64));
      
      // Check if token is expired
      const now = Date.now() / 1000;
      const isExpired = payload.exp < now;
      console.debug(`DEBUG - Token expiration check: now=${now}, exp=${payload.exp}, isExpired=${isExpired}`);
      return isExpired;
    } catch (e) {
      console.error('Error decoding token:', e);
      return true;
    }
  }
}

export default new AuthService();
