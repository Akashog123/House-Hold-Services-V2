import api from './api.service';

class UserService {
  // Admin: Get all users (excluding admins)
  async getAllUsers() {
    const response = await api.get('/admin/users');
    // Double-check filtering on client side
    return {
      ...response,
      data: response.data.filter(user => user.role !== 'admin')
    };
  }
  
  // Admin: Search users with filters (excluding admins)
  async searchUsers(filters = {}) {
    const response = await api.get('/admin/users', { params: filters });
    // Double-check filtering on client side
    return {
      ...response,
      data: response.data.filter(user => user.role !== 'admin')
    };
  }
  
  // Admin: Get user details by ID (with check for admin)
  async getUserById(userId) {
    const response = await api.get(`/admin/users/${userId}`);
    
    // Additional check on client side to prevent accessing admin data
    if (response.data && response.data.role === 'admin') {
      throw new Error('Administrator accounts cannot be managed through this interface');
    }
    
    return response;
  }
  
  // Admin: Get all professionals
  getAllProfessionals() {
    return api.get('/admin/professionals');
  }
  
  // Admin: Get all customers
  getAllCustomers() {
    return api.get('/admin/customers');
  }
  
  // Admin: Approve professional
  approveProfessional(userId) {
    return api.put(`/admin/approve/${userId}`);
  }
  
  // Admin: Reject professional
  rejectProfessional(userId) {
    return api.put(`/admin/reject/${userId}`);
  }
  
  // Admin: Block user
  blockUser(userId) {
    return api.put(`/admin/block/${userId}`);
  }
  
  // Admin: Unblock user
  unblockUser(userId) {
    return api.put(`/admin/unblock/${userId}`);
  }
  
  // Customer: Get profile
  getCustomerProfile() {
    return api.get('/customer/profile');
  }
  
  // Professional: Get profile
  getProfessionalProfile() {
    return api.get('/professional/profile');
  }
  
  // Customer: Update profile
  updateCustomerProfile(profileData) {
    return api.put('/customer/profile', profileData);
  }
  
  // Professional: Update profile
  updateProfessionalProfile(profileData) {
    return api.put('/professional/profile', profileData);
  }
  
  // Customer: Get service statistics
  getCustomerStats() {
    return api.get('/customer/service-stats');
  }
  
  // Professional: Get service statistics
  getProfessionalStats() {
    return api.get('/professional/stats');
  }
  
  // Customer: Update address
  updateCustomerAddress(addressData) {
    return api.put('/customer/address', addressData);
  }
}

export default new UserService();
