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
  
  // Create a new booking
  async createBooking(bookingData) {
    return api.post('/customer/service-requests', bookingData);
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
  
  // Submit a review for a booking
  async submitReview(bookingId, reviewData) {
    return api.post(`/customer/service-requests/${bookingId}/review`, reviewData);
  }
  
  // Get review for a booking
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
