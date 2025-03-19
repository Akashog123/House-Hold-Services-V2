import api from './api.service';

class ServiceService {
  // Get all services
  getAll(params = {}) {
    return api.get('/services', { params });
  }
  
  // Get service by id
  getById(id) {
    return api.get(`/services/${id}`);
  }
  
  // Get popular services
  getPopular() {
    return api.get('/services/popular');
  }
  
  // Search services
  searchServices(params = {}) {
    return api.get('/services/search', { params });
  }
  
  // Get professional profile with reviews
  getProfessionalProfile(professionalId) {
    return api.get(`/professionals/${professionalId}`);
  }
  
  // Get service reviews
  getServiceReviews(serviceId) {
    return api.get(`/services/${serviceId}/reviews`);
  }

    
  // Admin: Create service
  createService(serviceData) {
    return api.post('/admin/services', serviceData);
  }
  
  // Admin: Update service
  updateService(serviceId, serviceData) {
    return api.put(`/admin/services/${serviceId}`, serviceData);
  }
  
  // Admin: Delete service
  deleteService(serviceId) {
    return api.delete(`/admin/services/${serviceId}`);
  }
  
}

export default new ServiceService();
