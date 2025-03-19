import { createStore } from 'vuex'
import auth from './modules/auth'

export default createStore({
  modules: {
    auth
  },
  state: {
    token: null,
    user: null
  },
  getters: {
    isAuthenticated: state => !!state.token,
    token: state => state.token,
    currentUser: state => state.user
  },
  mutations: {
    setToken(state, token) {
      state.token = token
    },
    setUser(state, user) {
      state.user = user
    }
  },
  actions: {
    logout({ commit }) {
      commit('setToken', null)
      commit('setUser', null)
    }
  }
});
