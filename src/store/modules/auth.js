// Auth module for Vuex store
const state = () => ({
  token: null,
  user: null,
  error: null,
  loading: false
});

const getters = {
  isAuthenticated: state => !!state.token,
  token: state => state.token,
  user: state => state.user,
  userRole: state => state.user?.role || null,
  error: state => state.error,
  loading: state => state.loading
};

const actions = {
  // Add login action that works with the auth service
  async login({ commit }, credentials) {
    try {
      commit('SET_LOADING', true);
      commit('SET_ERROR', null);
      
      // Instead of importing auth service here, we'll use the one from the API directly
      // to avoid circular dependencies
      const response = await fetch(`/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(credentials)
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Login failed');
      }
      
      const data = await response.json();
      
      if (data && data.token) {
        // Store token in localStorage
        localStorage.setItem('auth_token', data.token);
        
        // Update store
        commit('SET_AUTH', { 
          token: data.token, 
          user: data.user 
        });
        
        return data;
      } else {
        throw new Error('Login failed: Invalid response');
      }
    } catch (error) {
      commit('SET_ERROR', error.message || 'Login failed');
      throw error;
    } finally {
      commit('SET_LOADING', false);
    }
  },
  
  // Add clearError action
  clearError({ commit }) {
    commit('SET_ERROR', null);
  },
  
  setAuth({ commit }, { token, user }) {
    commit('SET_AUTH', { token, user });
  },
  
  setUser({ commit }, user) {
    commit('SET_USER', user);
  },
  
  setError({ commit }, error) {
    commit('SET_ERROR', error);
  },
  
  setLoading({ commit }, loading) {
    commit('SET_LOADING', loading);
  },
  
  clearAuth({ commit }) {
    commit('CLEAR_AUTH');
  },
  
  // Load auth state from localStorage
  initAuth({ commit }) {
    const token = localStorage.getItem('auth_token');
    if (token) {
      commit('SET_AUTH', { token, user: null });
    }
  },
  
  logout({ commit }) {
    localStorage.removeItem('auth_token');
    commit('CLEAR_AUTH');
  }
};

const mutations = {
  SET_AUTH(state, { token, user }) {
    console.log('SET_AUTH mutation called with user:', user?.username || user?.email);
    state.token = token;
    if (user) state.user = user;
    state.error = null;
    console.log('Auth state after SET_AUTH:', state);
  },
  
  SET_USER(state, user) {
    state.user = user;
  },
  
  SET_ERROR(state, error) {
    state.error = error;
  },
  
  SET_LOADING(state, loading) {
    state.loading = loading;
  },
  
  CLEAR_AUTH(state) {
    state.token = null;
    state.user = null;
    state.error = null;
  }
};

export default {
  namespaced: true,
  state,
  getters,
  actions,
  mutations
};
