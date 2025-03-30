import api from './api.service';
import authService from './auth.service';
import store from '@/store';

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
    return api.get('/admin/services', {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    })
      .then(response => {
        console.log("AdminService: Services fetched successfully", response.data)
        return response;
      })
      .catch(error => {
        console.error("AdminService: Error fetching services", error.response?.data || error.message)
        throw error
      })
  }

  // Updated to handle image upload
  createService(serviceData) {
    // Check admin privileges before proceeding
    if (!authService.checkAdmin()) {
      return Promise.reject(new Error('Unauthorized: Admin access required'))
    }

    // Use FormData for image upload
    const formData = new FormData();
    formData.append('name', serviceData.name?.trim());
    formData.append('base_price', parseFloat(serviceData.base_price) || 0);
    formData.append('description', serviceData.description?.trim() || '');
    formData.append('avg_duration', parseInt(serviceData.avg_duration) || 0);
    
    // Append image if provided
    if (serviceData.image && serviceData.image instanceof File) {
      formData.append('image', serviceData.image);
    }

    // Basic validation
    if (!serviceData.name?.trim()) {
      return Promise.reject(new Error('Service name is required'))
    }
    if (parseFloat(serviceData.base_price) <= 0) {
      return Promise.reject(new Error('Base price must be greater than 0'))
    }
    if (parseInt(serviceData.avg_duration) < 1) {
      return Promise.reject(new Error('Duration must be at least 1 minute'))
    }

    console.log("AdminService: Creating new service with image")
    
    // Use different content type when sending FormData
    return api.post('/admin/services', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${store.getters['auth/token']}`
      }
    });
  }

  // Updated to handle image upload
  updateService(serviceId, serviceData) {
    // Add admin check for consistency with other methods
    if (!authService.checkAdmin()) {
      return Promise.reject(new Error('Unauthorized: Admin access required'))
    }

    if (!serviceId) {
      return Promise.reject(new Error('Service ID is required for updates'))
    }

    // Use FormData for image upload
    const formData = new FormData();
    formData.append('name', serviceData.name?.trim());
    formData.append('base_price', parseFloat(serviceData.base_price) || 0);
    formData.append('description', serviceData.description?.trim() || '');
    formData.append('avg_duration', parseInt(serviceData.avg_duration) || 0);
    if (serviceData.status) {
      formData.append('status', serviceData.status);
    }
    
    // Append image if provided
    if (serviceData.image && serviceData.image instanceof File) {
      formData.append('image', serviceData.image);
    }

    // Basic validation
    if (!serviceData.name?.trim()) {
      return Promise.reject(new Error('Service name is required'))
    }
    if (parseFloat(serviceData.base_price) <= 0) {
      return Promise.reject(new Error('Base price must be greater than 0'))
    }
    if (parseInt(serviceData.avg_duration) < 1) {
      return Promise.reject(new Error('Duration must be at least 1 minute'))
    }

    console.log(`AdminService: Updating service ${serviceId} with data and possible image`);
    
    return api.put(`/admin/services/${serviceId}`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${store.getters['auth/token']}`
      }
    })
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
    if (!authService.checkAdmin()) {
      return Promise.reject(new Error('Unauthorized: Admin access required'))
    }
    
    if (!serviceId) {
      return Promise.reject(new Error('Service ID is required'))
    }
    
    return api.delete(`/admin/services/${serviceId}`, {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    });
  }

  getServiceById(serviceId) {
    if (!serviceId) {
      return Promise.reject(new Error('Service ID is required'))
    }
    
    return api.get(`/admin/services/${serviceId}`, {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    });
  }

  fetchRevenueAnalytics(timeframe) {
    return api.get(`/admin/analytics/revenue/${timeframe}`, {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    });
  }

  fetchUserGrowthAnalytics() {
    return api.get('/admin/analytics/user-growth', {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    });
  }

  fetchServicesUsageAnalytics() {
    return api.get('/admin/analytics/services-usage', {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    });
  }

  fetchUserStatsAnalytics() {
    return api.get('/admin/users/stats', {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    });
  }

  // Export completed services data as CSV
  exportServicesData() {
    return api.get('/admin/export-service-requests', {
      headers: { Authorization: `Bearer ${store.getters['auth/token']}` }
    })
      .then(response => {
        console.log("AdminService: Export service data triggered successfully")
        return response;
      })
      .catch(error => {
        console.error("AdminService: Error exporting service data", error.response?.data || error.message)
        throw error
      })
  }
}

export default new AdminService();