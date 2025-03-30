<template>
  <div class="bookings-wrapper">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h3 class="page-title">Service History</h3>
      </div>
    </div>

    <!-- Error Message -->
    <div v-if="error" class="row mb-4">
      <div class="col-12">
        <div class="alert alert-danger" role="alert">
          {{ error }}
        </div>
      </div>
    </div>
    
    <!-- Filter Controls -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="filter-panel p-3">
          <div class="d-flex flex-column flex-md-row align-items-md-center">
            <div class="filter-label me-md-3 mb-2 mb-md-0">
              <i class="bi bi-funnel me-2"></i>Filters:
            </div>
            
            <div class="filter-buttons d-flex flex-wrap mb-3 mb-md-0 me-md-auto">
              <button 
                @click="applyQuickFilter('all')" 
                class="filter-btn me-2 mb-2" 
                :class="{'active': statusFilter === 'all'}"
              >
                All History
              </button>
              <button 
                @click="applyQuickFilter('completed')" 
                class="filter-btn me-2 mb-2" 
                :class="{'active': statusFilter === 'completed'}"
              >
                <i class="bi bi-check-circle me-1"></i>Completed
              </button>
              <button 
                @click="applyQuickFilter('cancelled')" 
                class="filter-btn me-2 mb-2" 
                :class="{'active': statusFilter === 'cancelled'}"
              >
                <i class="bi bi-x-circle me-1"></i>Cancelled
              </button>
            </div>
            
            <div class="sort-control d-flex align-items-center">
              <label for="sortBy" class="me-2 text-nowrap">Sort by:</label>
              <select 
                id="sortBy"
                class="form-select form-select-sm"
                v-model="sortBy"
                @change="applyFilters"
              >
                <option value="date_desc">Newest First</option>
                <option value="date_asc">Oldest First</option>
                <option value="status">Status</option>
              </select>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Loading Indicator -->
    <div v-if="loading" class="text-center py-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
      <p class="mt-3">Loading your service history...</p>
    </div>
    
    <!-- No History Message -->
    <div v-else-if="filteredRequests.length === 0" class="text-center py-5">
      <div class="empty-state">
        <i class="bi bi-clock-history display-1 text-muted"></i>
        <h5 class="mt-3">No Service History Found</h5>
        <p class="text-muted">You don't have any completed or cancelled services matching your filter criteria.</p>
        <router-link to="/services" class="btn btn-primary mt-3">
          Book a Service
        </router-link>
      </div>
    </div>
    
    <!-- History List -->
    <div v-else class="row">
      <div class="col-12">
        <div v-for="request in filteredRequests" :key="request.id" class="booking-card mb-4">
          <div class="booking-card-inner">
            <div class="booking-header">
              <div class="service-info">
                <div class="service-icon">
                  <i class="bi bi-tools"></i>
                </div>
                <div>
                  <h5 class="service-name mb-0">{{ request.service_name }}</h5>
                  <p class="booking-id mb-0">#{{ request.id }}</p>
                </div>
              </div>
              <div class="status-container">
                <span class="status-badge" :class="request.status">
                  <i :class="getStatusIcon(request.status)" class="me-1"></i>
                  {{ formatStatus(request.status) }}
                </span>
              </div>
            </div>
            
            <div class="booking-body">
              <div class="row g-3">
                <div class="col-md-7">
                  <div class="booking-details">
                    <div class="detail-row">
                      <div class="detail-icon">
                        <i class="bi bi-calendar-date"></i>
                      </div>
                      <div class="detail-content">
                        <div class="detail-label">Date Requested</div>
                        <div class="detail-value">{{ formatDate(request.request_date) }}</div>
                      </div>
                    </div>
                    
                    <div class="detail-row" v-if="request.completed_on">
                      <div class="detail-icon">
                        <i class="bi bi-calendar-check"></i>
                      </div>
                      <div class="detail-content">
                        <div class="detail-label">Completed on</div>
                        <div class="detail-value">{{ formatDate(request.completed_on) }}</div>
                      </div>
                    </div>
                    
                    <div class="detail-row" v-if="request.cancelled_on">
                      <div class="detail-icon">
                        <i class="bi bi-calendar-x"></i>
                      </div>
                      <div class="detail-content">
                        <div class="detail-label">Cancelled On</div>
                        <div class="detail-value">{{ formatDate(request.cancelled_on) }}</div>
                      </div>
                    </div>
                    
                    <div class="detail-row" v-if="request.professional_name">
                      <div class="detail-icon">
                        <i class="bi bi-person"></i>
                      </div>
                      <div class="detail-content">
                        <div class="detail-label">Professional</div>
                        <div class="detail-value">{{ request.professional_name }}</div>
                      </div>
                    </div>
                    
                    <div class="detail-row" v-if="request.cancelled_by">
                      <div class="detail-icon">
                        <i class="bi bi-person"></i>
                      </div>
                      <div class="detail-content">
                        <div class="detail-label">Cancelled By</div>
                        <div class="detail-value">{{ request.cancelled_by }}</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <div class="col-md-5">
                  <div v-if="request.notes" class="notes-section">
                    <h6 class="notes-title"><i class="bi bi-card-text me-2"></i>Notes</h6>
                    <p class="notes-text">{{ request.notes }}</p>
                  </div>
                  <div v-else class="notes-section notes-empty">
                    <p class="mb-0 text-muted"><i class="bi bi-card-text me-2"></i>No additional notes</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="booking-footer">
              <button 
                v-if="request.status === 'completed' && !request.has_review"
                @click="openReviewDialog(request)" 
                class="btn btn-outline-success btn-sm me-2"
              >
                <i class="bi bi-star me-1"></i> Review
              </button>
              <button 
                v-if="request.status === 'completed' && request.has_review"
                @click="viewReview(request.id)" 
                class="btn btn-outline-secondary btn-sm me-2"
              >
                <i class="bi bi-eye me-1"></i> View Review
              </button>
              <button 
                v-if="request.status === 'completed'"
                @click="openReopenConfirmModal(request)" 
                class="btn btn-outline-primary btn-sm me-2"
              >
                <i class="bi bi-arrow-repeat me-1"></i> Reopen
              </button>
              <button 
                @click="viewRequestDetails(request.id)" 
                class="btn btn-primary btn-sm"
              >
                <i class="bi bi-info-circle me-1"></i> Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Review Dialog -->
    <div class="modal fade" id="reviewModal" tabindex="-1" aria-labelledby="reviewModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="reviewModalLabel">Leave a Review</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <form @submit.prevent="submitReview">
              <div class="mb-3">
                <label for="rating" class="form-label">Rating</label>
                <div class="rating-stars">
                  <i v-for="star in 5" :key="star" 
                     :class="['bi', star <= reviewForm.rating ? 'bi-star-fill' : 'bi-star']"
                     @click="reviewForm.rating = star"></i>
                </div>
              </div>
              <div class="mb-3">
                <label for="comment" class="form-label">Comments</label>
                <textarea 
                  id="comment" 
                  class="form-control" 
                  v-model="reviewForm.comment"
                  rows="3"
                  placeholder="Share your experience with this service"
                ></textarea>
              </div>
            </form>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary" 
              @click="submitReview"
              :disabled="submittingReview"
            >
              <span v-if="submittingReview" class="spinner-border spinner-border-sm me-1" role="status"></span>
              Submit Review
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- View Review Dialog -->
    <div class="modal fade" id="viewReviewModal" tabindex="-1" aria-labelledby="viewReviewModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="viewReviewModalLabel">Your Review</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="reviewData">
            <div class="mb-3">
              <label class="form-label">Rating</label>
              <div class="rating-stars">
                <i v-for="star in 5" :key="star" 
                   :class="['bi', star <= reviewData.rating ? 'bi-star-fill' : 'bi-star']"></i>
              </div>
            </div>
            <div class="mb-3">
              <label class="form-label">Your Comments</label>
              <p>{{ reviewData.comment || 'No comments provided.' }}</p>
            </div>
            <div class="mb-3">
              <label class="form-label">Submitted On</label>
              <p>{{ formatDate(reviewData.created_at) }}</p>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Request Details Modal -->
    <div class="modal fade" id="detailsModal" tabindex="-1" aria-labelledby="detailsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="detailsModalLabel">Service Details</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body" v-if="selectedRequest">
            <div class="row">
              <div class="col-md-6">
                <h6>Service Information</h6>
                <div class="detail-card mb-3">
                  <p><strong>Service:</strong> {{ selectedRequest.service_name }}</p>
                  <p v-if="selectedRequest.service_price">
                    <strong>Price:</strong> ₹{{ selectedRequest.service_price }}
                  </p>
                  <p v-if="selectedRequest.service_duration">
                    <strong>Duration:</strong> {{ selectedRequest.service_duration }} minutes
                  </p>
                </div>
                
                <h6>Timeline</h6>
                <div class="timeline mb-3">
                  <div class="timeline-item">
                    <div class="timeline-badge bg-secondary"></div>
                    <div class="timeline-content">
                      <p class="mb-0"><strong>Requested</strong></p>
                      <p class="text-muted mb-0">{{ formatDate(selectedRequest.request_date) }}</p>
                    </div>
                  </div>
                  
                  <div class="timeline-item" v-if="selectedRequest.assigned_date">
                    <div class="timeline-badge bg-info"></div>
                    <div class="timeline-content">
                      <p class="mb-0"><strong>Accepted by Professional</strong></p>
                      <p class="text-muted mb-0">{{ formatDate(selectedRequest.assigned_date) }}</p>
                    </div>
                  </div>
                  
                  <div class="timeline-item" v-if="selectedRequest.completed_on">
                    <div class="timeline-badge bg-success"></div>
                    <div class="timeline-content">
                      <p class="mb-0"><strong>Completed</strong></p>
                      <p class="text-muted mb-0">{{ formatDate(selectedRequest.completed_on) }}</p>
                    </div>
                  </div>
                  
                  <div class="timeline-item" v-if="selectedRequest.cancelled_on">
                    <div class="timeline-badge bg-danger"></div>
                    <div class="timeline-content">
                      <p class="mb-0"><strong>Cancelled</strong></p>
                      <p class="text-muted mb-0">{{ formatDate(selectedRequest.cancelled_on) }}</p>
                    </div>
                  </div>
                </div>
              </div>
              
              <div class="col-md-6">
                <h6>Additional Notes</h6>
                <div class="detail-card">
                  <p v-if="selectedRequest.notes">{{ selectedRequest.notes }}</p>
                  <p v-else class="text-muted">No additional notes provided.</p>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Reopen Confirmation Modal -->
    <div class="modal fade" id="reopenConfirmModal" tabindex="-1" aria-labelledby="reopenConfirmModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title" id="reopenConfirmModalLabel">Reopen Service Request</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to reopen this completed service request?</p>
            <p>This will change the status from <strong>Completed</strong> to <strong>In Progress</strong>.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-primary"
              @click="reopenServiceRequest"
              :disabled="submittingStatusChange"
            >
              <span v-if="submittingStatusChange" class="spinner-border spinner-border-sm me-1" role="status"></span>
              Yes, Reopen
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.service';
import bookingService from '@/services/booking.service';
import { Modal } from 'bootstrap';

export default {
  name: 'ServiceHistoryView',
  data() {
    return {
      serviceRequests: [],
      loading: false,
      error: null,
      statusFilter: 'all',
      sortBy: 'date_desc',
      reviewModal: null,
      viewReviewModal: null,
      detailsModal: null,
      reopenConfirmModal: null,
      selectedRequest: null,
      reviewData: null,
      reviewForm: {
        rating: 5,
        comment: ''
      },
      submittingReview: false,
      submittingStatusChange: false
    }
  },
  computed: {
    filteredRequests() {
      // Get all completed and cancelled services first
      let filtered = this.serviceRequests.filter(req => 
        req.status === 'completed' || req.status === 'cancelled'
      );
      
      // Apply status filter if not set to 'all'
      if (this.statusFilter !== 'all') {
        filtered = filtered.filter(req => req.status === this.statusFilter);
      }
      
      // Apply sorting
      filtered.sort((a, b) => {
        if (this.sortBy === 'date_desc') {
          return new Date(b.request_date) - new Date(a.request_date);
        } else if (this.sortBy === 'date_asc') {
          return new Date(a.request_date) - new Date(b.request_date);
        } else if (this.sortBy === 'status') {
          const statusOrder = { 'completed': 1, 'cancelled': 2 };
          return statusOrder[a.status] - statusOrder[b.status];
        }
        return 0;
      });
      
      return filtered;
    }
  },
  created() {
    const { filter } = this.$route.query;
    if (filter) {
      this.statusFilter = filter;
    }
    
    this.fetchServiceRequests();
  },
  mounted() {
    this.initModals();
  },
  methods: {
    initModals() {
      const reviewModalEl = document.getElementById('reviewModal');
      if (reviewModalEl) {
        this.reviewModal = new Modal(reviewModalEl);
      }
      
      const viewReviewModalEl = document.getElementById('viewReviewModal');
      if (viewReviewModalEl) {
        this.viewReviewModal = new Modal(viewReviewModalEl);
      }
      
      const detailsModalEl = document.getElementById('detailsModal');
      if (detailsModalEl) {
        this.detailsModal = new Modal(detailsModalEl);
      }
      
      const reopenConfirmModalEl = document.getElementById('reopenConfirmModal');
      if (reopenConfirmModalEl) {
        this.reopenConfirmModal = new Modal(reopenConfirmModalEl);
      }
    },
    
    async fetchServiceRequests() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/customer/service-requests');
        this.serviceRequests = response.data;
      } catch (err) {
        this.error = 'Failed to load service history: ' + (err.response?.data?.error || err.message);
      } finally {
        this.loading = false;
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      return new Intl.DateTimeFormat('en-IN', {
        timeZone: 'Asia/Kolkata',
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      }).format(date);
    },
    
    formatStatus(status) {
      const statusMap = {
        'completed': 'Completed',
        'cancelled': 'Cancelled'
      };
      return statusMap[status] || status;
    },
    
    applyFilters() {
      this.$router.replace({
        query: { 
          ...this.$route.query,
          filter: this.statusFilter
        }
      });
    },
    
    async viewRequestDetails(requestId) {
      try {
        const response = await bookingService.getBookingDetails(requestId);
        this.selectedRequest = response.data;
        this.detailsModal.show();
      } catch (err) {
        this.error = 'Failed to load service details: ' + (err.response?.data?.error || err.message);
      }
    },
    
    openReviewDialog(request) {
      this.selectedRequest = request;
      this.reviewForm = {
        rating: 5,
        comment: ''
      };
      this.reviewModal.show();
    },
    
    async submitReview() {
      if (!this.selectedRequest) return;
      
      this.submittingReview = true;
      
      try {
        await bookingService.submitReview(this.selectedRequest.id, {
          rating: this.reviewForm.rating,
          comment: this.reviewForm.comment
        });
        
        const index = this.serviceRequests.findIndex(r => r.id === this.selectedRequest.id);
        if (index !== -1) {
          this.serviceRequests[index].has_review = true;
        }
        
        this.reviewModal.hide();
        await this.fetchServiceRequests();
      } catch (err) {
        this.error = 'Failed to submit review: ' + (err.response?.data?.error || err.message);
      } finally {
        this.submittingReview = false;
      }
    },
    
    async viewReview(requestId) {
      try {
        const response = await bookingService.getReview(requestId);
        this.reviewData = response.data;
        this.viewReviewModal.show();
      } catch (err) {
        this.error = 'Failed to load review: ' + (err.response?.data?.error || err.message);
      }
    },
    
    applyQuickFilter(status) {
      this.statusFilter = status;
      this.applyFilters();
    },
    
    getStatusIcon(status) {
      const icons = {
        'completed': 'bi-check-circle',
        'cancelled': 'bi-x-circle'
      };
      return icons[status] || 'bi-question-circle';
    },

    openReopenConfirmModal(request) {
      this.selectedRequest = request;
      this.reopenConfirmModal.show();
    },
    
    async reopenServiceRequest() {
      if (!this.selectedRequest) return;
      
      this.submittingStatusChange = true;
      this.error = null;
      
      try {
        await bookingService.updateServiceRequest(this.selectedRequest.id, {
          status: 'assigned'
        });
        
        // Update the local data
        const index = this.serviceRequests.findIndex(r => r.id === this.selectedRequest.id);
        if (index !== -1) {
          this.serviceRequests[index].status = 'assigned';
          this.serviceRequests[index].completed_on = null;
        }
        
        this.reopenConfirmModal.hide();
        
        // Refresh the data to ensure everything is up to date
        await this.fetchServiceRequests();
      } catch (err) {
        this.error = 'Failed to reopen service request: ' + (err.response?.data?.error || err.message);
      } finally {
        this.submittingStatusChange = false;
      }
    }
  }
};
</script>

<style scoped>
.bookings-wrapper {
  padding: 1.5rem;
  max-width: 1200px;
  margin: 0 auto;
}

.page-title {
  font-weight: 600;
  color: #333;
  margin-bottom: 0;
}

/* Filter Panel */
.filter-panel {
  background-color: #f8f9fa;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  position: relative;
}

.filter-label {
  font-weight: 600;
  color: #495057;
}

.filter-btn {
  border: 1px solid #dee2e6;
  background-color: white;
  color: #495057;
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  font-size: 0.875rem;
  transition: all 0.2s ease;
}

.filter-btn:hover {
  background-color: #f1f3f5;
}

.filter-btn.active {
  background-color: #e9ecef;
  border-color: #6c757d;
  font-weight: 500;
}

.sort-control select {
  min-width: 140px;
  border-radius: 4px;
}

/* Booking Cards */
.booking-card {
  transition: all 0.2s ease;
  margin-bottom: 1.25rem;
}

.booking-card-inner {
  background-color: white;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.booking-card-inner:hover {
  transform: translateY(-5px);
  box-shadow: 0 8px 16px rgba(0,0,0,0.1);
}

.booking-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid rgba(0,0,0,0.05);
}

.service-info {
  display: flex;
  align-items: center;
}

.service-icon {
  width: 40px;
  height: 40px;
  background-color: rgba(13, 110, 253, 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: #0d6efd;
  margin-right: 0.75rem;
}

.service-name {
  font-weight: 600;
  color: #333;
  margin-bottom: 0.25rem;
}

.booking-id {
  font-size: 0.875rem;
  color: #6c757d;
}

.booking-body {
  padding: 1.25rem;
  background-color: white;
}

.booking-footer {
  padding: 0.75rem 1.25rem;
  background-color: #f8f9fa;
  border-top: 1px solid rgba(0,0,0,0.05);
  display: flex;
  justify-content: flex-end;
}

/* Status badges */
.status-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.35rem 0.75rem;
  border-radius: 20px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.status-badge.completed {
  background-color: #e6fff0;
  color: #155724;
  border: 1px solid #c3e6cb;
}

.status-badge.cancelled {
  background-color: #f8f9fa;
  color: #6c757d;
  border: 1px solid #dee2e6;
}

/* Booking Details */
.booking-details {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.detail-row {
  display: flex;
  align-items: flex-start;
}

.detail-icon {
  width: 32px;
  height: 32px;
  background-color: #f8f9fa;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 0.75rem;
  color: #6c757d;
}

.detail-label {
  font-size: 0.75rem;
  color: #6c757d;
  margin-bottom: 0.25rem;
}

.detail-value {
  font-weight: 500;
  color: #212529;
}

/* Notes section */
.notes-section {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1rem;
  height: 100%;
  border-left: 3px solid #dee2e6;
}

.notes-title {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: #495057;
}

.notes-text {
  white-space: pre-line;
  margin-bottom: 0;
  font-size: 0.875rem;
}

.notes-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6c757d;
  border-left-color: #e9ecef;
}

/* Empty state */
.empty-state {
  padding: 3rem 1rem;
  text-align: center;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}

/* Rating stars */
.rating-stars {
  font-size: 1.5rem;
  color: #ffc107;
  cursor: pointer;
}

.rating-stars i {
  margin-right: 5px;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .bookings-wrapper {
    padding: 1rem;
  }
  
  .booking-header {
    flex-direction: column;
    align-items: flex-start;
  }
  
  .status-container {
    margin-top: 0.5rem;
  }
  
  .booking-body {
    padding: 1rem;
  }
  
  .booking-footer {
    padding: 0.75rem 1rem;
    flex-wrap: wrap;
  }
  
  .booking-footer button {
    margin-bottom: 0.5rem;
  }
  
  .service-icon {
    width: 32px;
    height: 32px;
    font-size: 1rem;
  }
}

/* Detail cards (used in modal) */
.detail-card {
  background-color: #f8f9fa;
  border-radius: 5px;
  padding: 15px;
  margin-bottom: 15px;
}

/* Timeline styling (used in modal) */
.timeline {
  position: relative;
  padding-left: 30px;
}

.timeline:before {
  content: '';
  position: absolute;
  left: 10px;
  top: 0;
  bottom: 0;
  width: 2px;
  background-color: #e9ecef;
}

.timeline-item {
  position: relative;
  margin-bottom: 20px;
}

.timeline-badge {
  position: absolute;
  left: -30px;
  width: 20px;
  height: 20px;
  border-radius: 50%;
  text-align: center;
  z-index: 1;
}

.timeline-content {
  padding-left: 10px;
  padding-bottom: 10px;
}
</style>
