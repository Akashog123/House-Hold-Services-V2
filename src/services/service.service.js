import api from './api.service';

class ServiceService {
  // Get all services with better error handling and validation
  async getAll(params = {}) {
    try {
      console.log('ServiceService: Getting all services with params:', params);
      const response = await api.get('/services', { params });
      
      // Validate the response structure
      if (!response || !response.data) {
        console.error('ServiceService: Invalid response from API', response);
        return { data: [] };
      }
      
      if (!Array.isArray(response.data)) {
        console.error('ServiceService: Response data is not an array', response.data);
        return { data: [] };
      }
      
      // Process services to ensure all have required properties
      const processedServices = response.data
        .filter(service => service && service.id) // Only include services with valid IDs
        .map(service => ({
          id: service.id,
          name: service.name || 'Unnamed Service',
          base_price: service.base_price || 0,
          description: service.description || 'No description available',
          status: service.status || 'active',
          image_path: service.image_path || '',
          ...service
        }));
      
      console.log(`ServiceService: Processed ${processedServices.length} valid services out of ${response.data.length}`);
      
      return { ...response, data: processedServices };
    } catch (error) {
      console.error('ServiceService: Error getting services', error);
      // Return empty array instead of throwing to avoid breaking components
      return { data: [] };
    }
  }
  
  // Get all available services (active only)
  getAvailableServices() {
    return api.get('/services', { params: { include_inactive: false } });
  }
  
  // Get service by id - fixed to avoid redirect loop
  async getById(id) {
    try {
      console.log(`ServiceService: Getting service details for ID ${id}`);
      
      // Use the main services endpoint instead of the specific ID endpoint
      const response = await api.get('/services');
      
      // Validate the response structure
      if (!response || !response.data) {
        console.error('ServiceService: Invalid response from API', response);
        return { data: null };
      }
      
      if (!Array.isArray(response.data)) {
        console.error('ServiceService: Services data is not an array', response.data);
        return { data: null };
      }
      
      // Find the matching service in the array
      const service = response.data.find(s => s.id === parseInt(id));
      
      if (!service) {
        console.error(`ServiceService: Service with ID ${id} not found in response`);
        return { data: null };
      }
      
      // Process the service to ensure it has all required properties
      const processedService = {
        id: service.id,
        name: service.name || 'Unnamed Service',
        base_price: service.base_price || 0,
        description: service.description || 'No description available',
        status: service.status || 'active',
        image_path: service.image_path || '',
        ...service
      };
      
      console.log(`ServiceService: Successfully found service with ID ${id}`);
      return { data: processedService };
    } catch (error) {
      console.error(`ServiceService: Error getting service with ID ${id}:`, error);
      return { data: null };
    }
  }
  
  // Get popular services with validation and fallback
  async getPopular() {
    try {
      console.log('ServiceService: Getting popular services');
      const response = await api.get('/services/popular');
      
      // Validate and process response
      if (!response || !response.data || !Array.isArray(response.data)) {
        console.error('ServiceService: Invalid popular services response', response);
        return { data: [] };
      }
      
      // Process and validate each service
      const processedServices = response.data
        .filter(service => service && service.id)
        .map(service => ({
          id: service.id,
          base_price: service.base_price || 0,
          description: service.description || 'No description available',
          status: service.status || 'active',
          ...service
        }));
      
      return { ...response, data: processedServices };
    } catch (error) {
      console.error('ServiceService: Error getting popular services, falling back to regular services', error);
      
      // Fallback to regular services if popular endpoint fails
      return this.getAll();
    }
  }
  
  // Search services
  async searchServices(params = {}) {
    try {
      console.log('ServiceService: Searching services with params:', params);
      const response = await api.get('/services/search', { params });
      
      // Validate the response structure
      if (!response || !response.data) {
        console.error('ServiceService: Invalid response from search API', response);
        return { data: [] };
      }
      
      if (!Array.isArray(response.data)) {
        console.error('ServiceService: Search response is not an array', response.data);
        return { data: [] };
      }
      
      // Debug the raw response
      console.log('ServiceService: Raw search response:', response.data);
      
      // Process services to ensure all have required properties
      const processedServices = response.data
        .filter(service => service && service.id) // Only include services with valid IDs
        .map(service => ({
          id: service.id,
          name: service.name || 'Unnamed Service',
          base_price: service.base_price || 0,
          description: service.description || 'No description available',
          status: service.status || 'active',
          image_path: service.image_path || '',
          available_professionals: service.available_professionals || 0,
          ...service
        }));
      
      console.log(`ServiceService: Search returned ${processedServices.length} services:`, processedServices);
      return { ...response, data: processedServices };
    } catch (error) {
      console.error('ServiceService: Error searching services', error);
      // Return empty array instead of throwing to avoid breaking components
      return { data: [] };
    }
  }
  
  // Get professional profile with reviews
  getProfessionalProfile(professionalId) {
    return api.get(`/professionals/${professionalId}`);
  }
  
  // Get professionals available for a service
  async getServiceProfessionals(serviceId) {
    try {
      console.log(`ServiceService: Getting professionals for service ${serviceId}`);
      const response = await api.get(`/services/${serviceId}/professionals`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        }
      });
      
      // Validate the response
      if (!response || !response.data) {
        console.error('ServiceService: Invalid response for professionals', response);
        return { data: [] };
      }
      
      if (!Array.isArray(response.data)) {
        console.error('ServiceService: Professionals data is not an array', response.data);
        return { data: [] };
      }
      
      // Process and enhance professional data
      const processedProfessionals = response.data
        .filter(pro => pro && pro.id) // Filter out invalid professionals
        .map(pro => ({
          id: pro.id,
          name: pro.username || pro.full_name || `Professional #${pro.id}`,
          average_rating: pro.average_rating || 0,
          total_reviews: pro.total_reviews || 0,
          experience_years: pro.experience_years || 0,
          ...pro
        }));
      
      console.log(`ServiceService: Found ${processedProfessionals.length} professionals for service ${serviceId}`);
      return { ...response, data: processedProfessionals };
    } catch (error) {
      console.error(`ServiceService: Error getting professionals for service ${serviceId}`, error);
      // Return empty array instead of throwing to avoid breaking components
      return { data: [] };
    }
  }
  
  // Check if a service has at least one professional available
  async hasAvailableProfessionals(serviceId) {
    try {
      console.log(`ServiceService: Checking if service ${serviceId} has available professionals`);
      const result = await this.getServiceProfessionals(serviceId);
      return result.data && result.data.length > 0;
    } catch (error) {
      console.error(`ServiceService: Error checking professionals for service ${serviceId}:`, error);
      return false; // Assume no professionals on error
    }
  }
  
  // Get service reviews
  getServiceReviews(serviceId) {
    return api.get(`/services/${serviceId}/reviews`);
  }
  
  // Get professional details
  getProfessionalDetails(professionalId) {
    return api.get(`/professionals/${professionalId}`);
  }
  
  // Get professional reviews
  getProfessionalReviews(professionalId) {
    return api.get(`/professionals/${professionalId}/reviews`);
  }
}

export default new ServiceService();
