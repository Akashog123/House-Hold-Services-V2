import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import store from './store'
import './assets/main.css'
import './assets/custom-styles.css'
import api from './services/api.service'

// Import Bootstrap JavaScript
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

// Add debug logging during app initialization
console.log("DEBUG - Application initializing")
console.log("DEBUG - Checking for stored tokens")

// Add this function to help debug component loading issues
window.addEventListener('unhandledrejection', function(event) {
  if (event.reason && event.reason.code === 'MODULE_NOT_FOUND') {
    console.error('Failed to load module:', event.reason);
  }
});

// Initialize auth state from localStorage if available, then start the app
const initApp = async () => {
  try {
    console.log("DEBUG - Initializing auth state")
    
    // Check if token exists in localStorage
    const token = localStorage.getItem('auth_token')
    console.log(`DEBUG - Token exists in localStorage: ${!!token}`)
    
    if (token) {
      // First check if token is expired before trying to use it
      try {
        const jwt = token.split('.')[1];
        const payload = JSON.parse(atob(jwt));
        const now = Date.now() / 1000;
        
        if (payload.exp < now) {
          console.log("DEBUG - Token is expired, removing it");
          localStorage.removeItem('auth_token');
          throw new Error("Token expired");
        }
        
        console.log("DEBUG - Setting token in store");
        await store.dispatch('auth/setAuth', { token, user: null });
        
        // Try to fetch user profile with token
        try {
          console.log("DEBUG - Fetching user profile");
          const response = await api.get('/auth/profile');
          console.log("DEBUG - User profile response:", response.data);
          await store.dispatch('auth/setUser', response.data);
        } catch (err) {
          console.error("DEBUG - Failed to fetch profile:", err);
          // If token is invalid, clear auth state
          localStorage.removeItem('auth_token');
          await store.dispatch('auth/clearAuth');
        }
      } catch (tokenError) {
        console.error("DEBUG - Token validation failed:", tokenError);
        localStorage.removeItem('auth_token');
      }
    }
    
    // Mount the app
    const app = createApp(App)
    app.config.globalProperties.$axios = api
    app.use(router)
    app.use(store)
    
    // Make router available globally for programmatic navigation
    window.router = router
    
    app.mount('#app')
    
  } catch (error) {
    console.error("DEBUG - Error during initialization:", error)
    
    // Even if initialization fails, start the app
    const app = createApp(App)
    app.config.globalProperties.$axios = api
    app.use(router)
    app.use(store)
    
    // Make router available globally for programmatic navigation
    window.router = router
    
    app.mount('#app')
  }
}

// Start the application
initApp()


