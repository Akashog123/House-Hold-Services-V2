import api from './api.service'
import authService from './auth.service'
import store from '@/store'

class AdminService {
  constructor() {
    // Properly check auth state with namespaced store
    this.api = api;
    
    // Check if user is admin in constructor - only log warning, don't block
    if (!(store.getters['auth/token'] && 
          store.getters['auth/user'] && 
          store.getters['auth/user'].role === 'admin')) {
      console.warn('Warning: AdminService initialized without admin privileges');
    }
  }

  // Service Management
  getAllServices() {
    console.log("AdminService: Calling getAllServices endpoint")
    return api.get('/admin/services')
      .then(response => {
        console.log("AdminService: Services fetched successfully", response.data)
        return response;
      })
      .catch(error => {
        console.error("AdminService: Error fetching services", error.response?.data || error.message)
        throw error
      })
  }

  createService(serviceData) {
    // Check admin privileges before proceeding
    if (!authService.checkAdmin()) {
      return Promise.reject(new Error('Unauthorized: Admin access required'))
    }

    const payload = {
      name: serviceData.name?.trim(),
      base_price: parseFloat(serviceData.base_price) || 0,
      description: serviceData.description?.trim() || '',
      avg_duration: parseInt(serviceData.avg_duration) || 0,
      status: 'active' // Add default status
    }

    // Validate payload before sending
    if (!payload.name) {
      return Promise.reject(new Error('Service name is required'))
    }
    if (payload.base_price <= 0) {
      return Promise.reject(new Error('Base price must be greater than 0'))
    }
    if (payload.avg_duration < 1) {
      return Promise.reject(new Error('Duration must be at least 1 minute'))
    }

    console.log("AdminService: Creating new service with data:", payload)
    return api.post('/admin/services', payload)
  }

  updateService(serviceId, serviceData) {
    // Add admin check for consistency with other methods
    if (!authService.checkAdmin()) {
      return Promise.reject(new Error('Unauthorized: Admin access required'))
    }

    if (!serviceId) {
      return Promise.reject(new Error('Service ID is required for updates'))
    }

    const payload = {
      name: serviceData.name?.trim(),
      base_price: parseFloat(serviceData.base_price) || 0,
      description: serviceData.description?.trim() || '',
      avg_duration: parseInt(serviceData.avg_duration) || 0,
      status: serviceData.status || 'active'
    }

    // Validate payload before sending
    if (!payload.name) {
      return Promise.reject(new Error('Service name is required'))
    }
    if (payload.base_price <= 0) {
      return Promise.reject(new Error('Base price must be greater than 0'))
    }
    if (payload.avg_duration < 1) {
      return Promise.reject(new Error('Duration must be at least 1 minute'))
    }

    console.log(`AdminService: Updating service ${serviceId} with data:`, payload);
    
    return api.put(`/admin/services/${serviceId}`, payload)
      .then(response => {
        console.log(`AdminService: Service ${serviceId} updated successfully, response:`, response.data);
        return response;
      })
      .catch(error => {
        console.error(`AdminService: Error updating service ${serviceId}:`, error.response?.data || error.message);
        throw error;
      });
  }

  deleteService(serviceId) {
    // Add admin check for consistency with other methods
    if (!authService.checkAdmin()) {
      return Promise.reject(new Error('Unauthorized: Admin access required'))
    }
    
    console.log(`AdminService: Starting deleteService with ID: ${serviceId}, type: ${typeof serviceId}`);
    
    if (!serviceId) {
      console.error("AdminService: No serviceId provided to deleteService");
      return Promise.reject(new Error('Service ID is required'));
    }
    
    console.log(`AdminService: Deleting service with ID ${serviceId}`);
    return api.delete(`/admin/services/${serviceId}`)
      .then(response => {
        console.log(`AdminService: Service ${serviceId} deleted successfully`);
        return response;
      })
      .catch(error => {
        console.error(`AdminService: Error deleting service ${serviceId}`, error.response?.data || error.message);
        throw error;
      });
  }

  getServiceById(serviceId) {
    if (!serviceId) {
      return Promise.reject(new Error('Service ID is required'))
    }
    
    return api.get(`/admin/services/${serviceId}`)
  }
}

export default new AdminService()