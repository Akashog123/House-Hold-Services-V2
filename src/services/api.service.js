import axios from 'axios'
import store from '@/store'
import authService from './auth.service'

// Flag to prevent multiple simultaneous refresh attempts
let isRefreshing = false;
// Store failed requests to retry after refresh
let failedQueue = [];

// Process failed queue - either retry with new token or reject all
const processQueue = (error, token = null) => {
  failedQueue.forEach(prom => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  },
  withCredentials: true
})

// Request interceptor
api.interceptors.request.use(
  config => {
    console.log(`DEBUG - API Request to: ${config.url}`);
    
    // Get token from the namespaced state using the getter
    const token = store.getters['auth/token'];
    console.log(`DEBUG - Token exists: ${!!token}`);
    
    if (token) {
      console.log(`DEBUG - Adding token to request headers (first 20 chars): ${token.substring(0, 20)}`);
      console.log(`DEBUG - Token type: ${typeof token}, length: ${token.length}`);
      config.headers.Authorization = `Bearer ${token}`;
      console.log(`DEBUG - Authorization header set: ${config.headers.Authorization.substring(0, 27)}...`);
    } else {
      console.log(`DEBUG - No token available, request will be unauthenticated`);
    }
    
    return config;
  },
  error => {
    console.error(`DEBUG - Request interceptor error:`, error);
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  response => {
    console.log(`DEBUG - Response from ${response.config.url}: Status ${response.status}`);
    return response;
  },
  async error => {
    console.error(`DEBUG - API Error: ${error.config?.url || 'unknown URL'}:`, error.response?.status, error.response?.data);
    
    const originalRequest = error.config;
    
    // Check if this is a 401 error, not a refresh request, and no retry has been attempted yet
    if (error.response?.status === 401 && 
        !originalRequest._retry && 
        !originalRequest.url?.includes('/auth/refresh')) {
      
      console.log('DEBUG - 401 Unauthorized response detected - Attempting to refresh token');
      
      // If token has expired explicitly, logout immediately
      if (error.response?.data?.msg === 'Token has expired') {
        console.log('DEBUG - Token explicitly reported as expired, logging out');
        await authService.logout();
        return Promise.reject(error);
      }
      
      // If already refreshing, add to queue
      if (isRefreshing) {
        console.log('DEBUG - Refresh already in progress, queuing request');
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
        .then(token => {
          console.log('DEBUG - Retrying with new token after refresh');
          originalRequest.headers['Authorization'] = `Bearer ${token}`;
          return api(originalRequest);
        })
        .catch(err => {
          console.log('DEBUG - Queued request rejected after refresh failure');
          return Promise.reject(err);
        });
      }
      
      originalRequest._retry = true;
      isRefreshing = true;
      
      try {
        // Try to refresh the token (with timeout to prevent hanging app)
        const refreshPromise = authService.refreshToken();
        const timeoutPromise = new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Refresh token timeout')), 5000)
        );
        
        const result = await Promise.race([refreshPromise, timeoutPromise]);
        
        if (result && result.token) {
          console.log('DEBUG - Token refreshed successfully, processing queue');
          processQueue(null, result.token);
          originalRequest.headers['Authorization'] = `Bearer ${result.token}`;
          isRefreshing = false;
          return api(originalRequest);
        } else {
          console.log('DEBUG - Token refresh returned invalid result, logging out');
          processQueue(new Error('Failed to refresh token'));
          await authService.logout();
          isRefreshing = false;
          return Promise.reject(error);
        }
      } catch (refreshError) {
        console.error('DEBUG - Token refresh failed:', refreshError);
        processQueue(refreshError);
        await authService.logout();
        isRefreshing = false;
        return Promise.reject(error);
      }
    }
    
    return Promise.reject(error);
  }
);

export default api
