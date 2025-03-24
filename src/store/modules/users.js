import api from '@/services/api.service'

export default {
  state: {
    users: [],
    professionals: [],
    selectedUser: null,
    pendingApprovalCount: 0,
    loading: false,
    error: null
  },
  mutations: {
    SET_USERS(state, users) {
      state.users = users
    },
    SET_PROFESSIONALS(state, professionals) {
      state.professionals = professionals
    },
    SET_SELECTED_USER(state, user) {
      state.selectedUser = user
    },
    UPDATE_USER(state, updatedUser) {
      const index = state.users.findIndex(u => u.id === updatedUser.id)
      if (index !== -1) {
        state.users.splice(index, 1, updatedUser)
      }
    },
    SET_PENDING_APPROVAL_COUNT(state, count) {
      state.pendingApprovalCount = count
    },
    SET_LOADING(state, status) {
      state.loading = status
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    async fetchUsers({ commit }) {
      try {
        commit('SET_LOADING', true)
        const response = await api.get('/admin/users')
        commit('SET_USERS', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to load users')
        throw error
      }
    },
    async fetchProfessionals({ commit }) {
      try {
        commit('SET_LOADING', true)
        const response = await api.get('/admin/professionals')
        commit('SET_PROFESSIONALS', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to load professionals')
        throw error
      }
    },
    async fetchUserDetails({ commit }, userId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.get(`/admin/users/${userId}`)
        commit('SET_SELECTED_USER', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to load user details')
        throw error
      }
    },
    async fetchPendingApprovalCount({ commit }) {
      try {
        const response = await api.get('/admin/professionals', {
          params: { approved: 'false', active: 'true' }
        })
        
        const count = Array.isArray(response.data) ? response.data.length : 0
        commit('SET_PENDING_APPROVAL_COUNT', count)
        
        return count
      } catch (error) {
        console.error('Failed to fetch pending approval count:', error)
        return 0
      }
    },
    async approveUser({ commit, dispatch }, userId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.put(`/admin/approve/${userId}`)
        commit('UPDATE_USER', response.data)
        
        // Refresh pending approval count
        dispatch('fetchPendingApprovalCount')
        
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to approve user')
        throw error
      }
    },
    async rejectUser({ commit, dispatch }, userId) {
      try {
        commit('SET_LOADING', true)
        
        // Ensure we send an object as the second parameter
        const response = await api.put(`/admin/reject/${userId}`, {})
        
        commit('UPDATE_USER', response.data.user || response.data)
        
        // Refresh pending approval count
        dispatch('fetchPendingApprovalCount')
        
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to reject user')
        throw error
      }
    },
    async blockUser({ commit }, userId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.put(`/admin/block/${userId}`)
        commit('UPDATE_USER', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to block user')
        throw error
      }
    },
    async unblockUser({ commit }, userId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.put(`/admin/unblock/${userId}`)
        commit('UPDATE_USER', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to unblock user')
        throw error
      }
    }
  },
  getters: {
    allUsers: state => state.users,
    allProfessionals: state => state.professionals,
    selectedUser: state => state.selectedUser,
    usersLoading: state => state.loading,
    usersError: state => state.error,
    pendingApprovalCount: state => state.pendingApprovalCount,
    nonAdminUsers: state => {
      return state.users.filter(user => user.role !== 'admin');
    },
    professionalUsers: state => {
      return state.users.filter(user => user.role === 'professional');
    },
    customerUsers: state => {
      return state.users.filter(user => user.role === 'customer');
    }
  }
}
