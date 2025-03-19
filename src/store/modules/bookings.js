import api from '@/services/api.service'

export default {
  state: {
    bookings: [],
    recentBookings: [],
    selectedBooking: null,
    loading: false,
    error: null
  },
  mutations: {
    SET_BOOKINGS(state, bookings) {
      state.bookings = bookings
    },
    SET_RECENT_BOOKINGS(state, bookings) {
      state.recentBookings = bookings
    },
    SET_SELECTED_BOOKING(state, booking) {
      state.selectedBooking = booking
    },
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    async fetchUserBookings({ commit, rootState }) {
      try {
        commit('SET_LOADING', true)
        
        let endpoint = '/customer/service-requests'
        if (rootState.auth.user && rootState.auth.user.role === 'professional') {
          endpoint = '/professional/service-requests'
        }
        
        const response = await api.get(endpoint)
        commit('SET_BOOKINGS', response.data)
        
        // Sort by date to get recent bookings
        const recent = [...response.data]
          .sort((a, b) => new Date(b.request_date) - new Date(a.request_date))
          .slice(0, 5) // Take top 5
          
        commit('SET_RECENT_BOOKINGS', recent)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to load bookings')
        throw error
      }
    },
    async fetchBookingDetails({ commit }, bookingId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.get(`/customer/service-requests/${bookingId}`)
        commit('SET_SELECTED_BOOKING', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to load booking details')
        throw error
      }
    },
    async createBooking({ commit, dispatch }, bookingData) {
      try {
        commit('SET_LOADING', true)
        const response = await api.post('/customer/service-requests', bookingData)
        commit('SET_LOADING', false)
        // Refresh bookings list after creation
        dispatch('fetchUserBookings')
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to create booking')
        throw error
      }
    },
    async cancelBooking({ commit, dispatch }, bookingId) {
      try {
        commit('SET_LOADING', true)
        await api.put(`/customer/service-requests/${bookingId}`, { status: 'cancelled' })
        commit('SET_LOADING', false)
        // Refresh bookings list after cancellation
        dispatch('fetchUserBookings')
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to cancel booking')
        throw error
      }
    }
  },
  getters: {
    allBookings: state => state.bookings,
    recentBookings: state => state.recentBookings,
    selectedBooking: state => state.selectedBooking,
    bookingsCount: state => state.bookings.length,
    upcomingBookingsCount: state => state.bookings.filter(b => 
      ['requested', 'assigned'].includes(b.status)
    ).length,
    completedBookingsCount: state => state.bookings.filter(b => 
      b.status === 'completed'
    ).length,
    bookingsLoading: state => state.loading,
    bookingsError: state => state.error
  }
}
