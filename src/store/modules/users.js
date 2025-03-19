import api from '@/services/api.service'

export default {
  state: {
    users: [],
    professionals: [],
    selectedUser: null,
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
    async approveUser({ commit }, userId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.put(`/admin/approve/${userId}`)
        commit('UPDATE_USER', response.data)
        commit('SET_LOADING', false)
        return response.data
      } catch (error) {
        commit('SET_LOADING', false)
        commit('SET_ERROR', error.response?.data?.message || 'Failed to approve user')
        throw error
      }
    },
    async rejectUser({ commit }, userId) {
      try {
        commit('SET_LOADING', true)
        const response = await api.put(`/admin/reject/${userId}`)
        commit('UPDATE_USER', response.data)
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
    pendingApprovalCount: state => state.users.filter(u => 
      u.role === 'professional' && !u.is_approved && u.is_active
    ).length,
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
