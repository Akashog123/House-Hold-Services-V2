import api from './api.service';
import authService from './auth.service';

class BookingService {
  // Get all bookings for current user
  async getUserBookings(params) {
    const user = authService.getCurrentUser();
    let endpoint = '/customer/service-requests';
    
    if (user && user.role === 'professional') {
      endpoint = '/professional/service-requests';
    }
    
    return api.get(endpoint, { params });
  }
  
  // Get booking details by id
  async getBookingDetails(bookingId) {
    const user = authService.getCurrentUser();
    let endpoint = `/customer/service-requests/${bookingId}`;
    
    if (user && user.role === 'professional') {
      endpoint = `/professional/service-requests/${bookingId}`;
    }
    
    return api.get(endpoint);
  }
  
  // Create a new booking with enhanced validation
  async createBooking(bookingData) {
    // Validate required fields
    if (!bookingData.service_id) {
      throw new Error('Service is required');
    }
    
    if (!bookingData.completion_date) {
      throw new Error('Completion date is required');
    }
    
    try {
      console.log("BookingService: Creating booking with data:", bookingData);
      const response = await api.post('/customer/service-requests', bookingData);
      console.log("BookingService: Booking created successfully:", response.data);
      return response.data;
    } catch (error) {
      console.error("BookingService: Error creating booking:", error);
      // Enhance error message with more details if available
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  }
  
  // Create a booking with professional assignment logic
  async createBookingWithProfessional(bookingData) {
    // Validate required fields
    if (!bookingData.service_id) {
      throw new Error('Service is required');
    }
    
    if (!bookingData.completion_date) {
      throw new Error('Completion date is required');
    }
    
    try {
      console.log("BookingService: Creating booking with professional assignment logic");
      
      // If no professional is selected and auto_assign is true,
      // try to get a list of available professionals
      if (!bookingData.professional_id && bookingData.auto_assign) {
        console.log("BookingService: No professional selected, attempting to auto-assign");
        
        try {
          // First, get available professionals for this service
          const profResponse = await api.get(`/services/${bookingData.service_id}/professionals`);
          
          if (profResponse.data && Array.isArray(profResponse.data) && profResponse.data.length > 0) {
            // If there's only one professional, choose them directly
            if (profResponse.data.length === 1) {
              const selectedPro = profResponse.data[0];
              console.log(`BookingService: Only one professional available. Auto-assigning professional ${selectedPro.id} (${selectedPro.name})`);
              bookingData.professional_id = selectedPro.id;
            } else {
              // Multiple professionals - use algorithm to select one
              const sortedProfessionals = [...profResponse.data].sort((a, b) => {
                // Sort by total reviews (ascending)
                const aReviews = a.total_reviews || 0;
                const bReviews = b.total_reviews || 0;
                
                if (aReviews === bReviews) {
                  // If tied, use rating as secondary sort (ascending - to give newer pros a chance)
                  return (a.average_rating || 0) - (b.average_rating || 0);
                }
                
                return aReviews - bReviews;
              });
              
              // Select the first professional from the sorted list
              const selectedPro = sortedProfessionals[0];
              console.log(`BookingService: Auto-assigning professional ${selectedPro.id} (${selectedPro.name})`);
              bookingData.professional_id = selectedPro.id;
            }
          } else {
            console.log("BookingService: No professionals available for auto-assignment");
          }
        } catch (err) {
          console.error("BookingService: Error fetching professionals for auto-assignment:", err);
          // Continue without auto-assignment if this fails
        }
      }
      
      // Remove the auto_assign flag before sending to the API
      const { auto_assign, ...dataToSend } = bookingData;
      
      // Create the booking - ensuring we're never setting an 'assigned' status
      // This allows the professional to accept/cancel the request
      const response = await api.post('/customer/service-requests', dataToSend);
      
      console.log("BookingService: Booking created successfully:", response.data);
      return response.data;
    } catch (error) {
      console.error("BookingService: Error creating booking:", error);
      // Enhance error message with more details if available
      if (error.response && error.response.data && error.response.data.error) {
        throw new Error(error.response.data.error);
      }
      throw error;
    }
  }
  
  // Update booking status
  async updateBookingStatus(bookingId, status) {
    const user = authService.getCurrentUser();
    
    if (user.role === 'customer') {
      return api.put(`/customer/service-requests/${bookingId}`, { status });
    } else if (user.role === 'professional') {
      return api.put(`/professional/service-requests/${bookingId}`, { action: status });
    } else {
      throw new Error('Unauthorized to update booking');
    }
  }
  
  // Update booking notes
  async updateBookingNotes(bookingId, notes) {
    return api.put(`/customer/service-requests/${bookingId}`, { notes });
  }
  
  // Update service request details
  async updateServiceRequest(bookingId, updateData) {
    return api.put(`/customer/service-requests/${bookingId}`, updateData);
  }
  
  // Complete a service request
  async completeServiceRequest(bookingId) {
    return api.put(`/customer/service-requests/${bookingId}/complete`);
  }
  
  // Submit a review for a completed service
  async submitReview(bookingId, reviewData) {
    if (!reviewData.rating || reviewData.rating < 1 || reviewData.rating > 5) {
      throw new Error('Rating must be between 1 and 5');
    }
    
    return api.post(`/customer/service-requests/${bookingId}/review`, {
      rating: reviewData.rating,
      comment: reviewData.comment || ''
    });
  }
  
  // Get a review for a service request
  async getReview(bookingId) {
    return api.get(`/customer/service-requests/${bookingId}/review`);
  }
  
  // Format booking status for display
  formatStatus(status) {
    const statusMap = {
      'requested': 'Requested',
      'assigned': 'In Progress',
      'completed': 'Completed',
      'cancelled': 'Cancelled'
    };
    return statusMap[status] || status;
  }
  
  // Get status color for UI
  getStatusColor(status) {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success';
      case 'assigned':
        return 'primary';
      case 'requested':
      case 'pending':
        return 'warning';
      case 'cancelled':
        return 'error';
      default:
        return 'grey';
    }
  }
}

export default new BookingService();
