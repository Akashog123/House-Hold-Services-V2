import api from '@/services/api.service'
import axios from 'axios'

export default {
  state: {
    services: [],
    popularServices: [],
    loading: false,
    error: null
  },
  mutations: {
    SET_SERVICES(state, services) {
      state.services = services
    },
    SET_POPULAR_SERVICES(state, services) {
      state.popularServices = services
    },
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    async fetchServices({ commit }) {
      try {
        commit('SET_LOADING', true)
        const response = await api.get('/services')
        commit('SET_SERVICES', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to load services')
        throw error
      }
    },
    async fetchPopularServices({ commit }) {
      try {
        commit('SET_LOADING', true)
        // Assuming the API has an endpoint for popular services
        // If not, we could apply some client-side logic to determine popularity
        const response = await api.get('/services/popular')
        commit('SET_POPULAR_SERVICES', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        // Fallback: if no specific endpoint exists, use regular services
        try {
          const response = await api.get('/services')
          // Sort by some criteria to determine "popularity" (e.g., rating, price)
          const popular = [...response.data]
            .sort((a, b) => b.rating - a.rating)
            .slice(0, 3) // Take top 3
          
          commit('SET_POPULAR_SERVICES', popular)
          commit('SET_LOADING', false)
          return popular
        } catch (fallbackError) {
          commit('SET_LOADING', false)
          commit('SET_ERROR', fallbackError.response?.data?.message || 'Failed to load popular services')
          throw fallbackError
        }
      }
    },
    // Fetch all services (for service type dropdown in registration)
    async fetchAllServices({ commit }) {
      try {
        const response = await axios.get('/api/services')
        return response
      } catch (error) {
        console.error('Error fetching services:', error)
        throw error
      }
    }
  },
  getters: {
    allServices: state => state.services,
    popularServices: state => state.popularServices,
    servicesCount: state => state.services.length,
    servicesLoading: state => state.loading,
    servicesError: state => state.error
  }
}
