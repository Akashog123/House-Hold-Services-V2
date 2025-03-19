<template>
  <CustomerLayout>
    <div class="service-history-page">
      <h1>Service History</h1>
      
      <div v-if="loading" class="loading">Loading your service history...</div>
      <div v-if="error" class="error-message">{{ error }}</div>
      
      <!-- Filter Controls -->
      <div class="filter-controls">
        <div class="filter-group">
          <label>Filter by Status:</label>
          <select v-model="statusFilter">
            <option value="all">All Services</option>
            <option value="completed">Completed</option>
            <option value="cancelled">Cancelled</option>
            <option value="requested">Pending</option>
            <option value="assigned">In Progress</option>
          </select>
        </div>
        
        <div class="filter-group">
          <label>Sort by:</label>
          <select v-model="sortBy">
            <option value="date_desc">Date (Newest First)</option>
            <option value="date_asc">Date (Oldest First)</option>
            <option value="status">Status</option>
          </select>
        </div>
      </div>
      
      <!-- Service History Table -->
      <div class="history-table-container">
        <table v-if="filteredRequests.length > 0" class="service-history-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Service</th>
              <th>Date</th>
              <th>Professional</th>
              <th>Status</th>
              <th>Action</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in filteredRequests" 
                :key="request.id" 
                :class="request.status">
              <td>#{{ request.id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ formatDate(request.request_date) }}</td>
              <td>{{ request.professional_name || 'Not assigned' }}</td>
              <td>
                <span class="status-badge" :class="request.status">
                  {{ formatStatus(request.status) }}
                </span>
              </td>
              <td>
                <div class="action-buttons">
                  <button
                    v-if="request.status === 'completed' && !request.has_review"
                    @click="openReviewModal(request)"
                    class="btn-review"
                  >
                    Leave Review
                  </button>
                  <button
                    v-if="request.status === 'completed' && request.has_review"
                    @click="viewReview(request)"
                    class="btn-view-review"
                  >
                    View Review
                  </button>
                  <button
                    @click="viewRequestDetails(request.id)"
                    class="btn-details"
                  >
                    Details
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-else-if="!loading" class="empty-state">
          No service history found matching your filters.
        </div>
      </div>
      
      <!-- Review Modal -->
      <v-dialog v-model="showReviewModal" max-width="500px">
        <v-card v-if="selectedRequest">
          <v-card-title>
            Review Service: {{ selectedRequest.service_name }}
          </v-card-title>
          <v-card-text>
            <div class="review-form">
              <div class="form-group rating-group">
                <label>Rate your experience:</label>
                <div class="rating-stars">
                  <template v-for="n in 5" :key="n">
                    <v-icon
                      :color="n <= reviewForm.rating ? 'amber' : 'grey'"
                      @click="reviewForm.rating = n"
                    >
                      mdi-star
                    </v-icon>
                  </template>
                  <span class="rating-text">{{ reviewForm.rating }} / 5</span>
                </div>
              </div>
              
              <div class="form-group">
                <label for="reviewComment">Your Comments:</label>
                <v-textarea
                  id="reviewComment"
                  v-model="reviewForm.comment"
                  placeholder="Share your experience with this service..."
                  rows="4"
                ></v-textarea>
              </div>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="showReviewModal = false">
              Cancel
            </v-btn>
            <v-btn color="primary" variant="text" @click="submitReview" :loading="submittingReview">
              Submit Review
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      
      <!-- View Review Modal -->
      <v-dialog v-model="showViewReviewModal" max-width="500px">
        <v-card v-if="selectedReview">
          <v-card-title>
            Your Review for {{ selectedRequest?.service_name }}
          </v-card-title>
          <v-card-text>
            <div class="review-details">
              <div class="review-rating">
                <div class="rating-stars">
                  <template v-for="n in 5" :key="n">
                    <v-icon :color="n <= selectedReview.rating ? 'amber' : 'grey'">
                      mdi-star
                    </v-icon>
                  </template>
                  <span class="rating-value">{{ selectedReview.rating }} / 5</span>
                </div>
              </div>
              
              <div class="review-date">
                Submitted on {{ formatDate(selectedReview.created_at) }}
              </div>
              
              <div class="review-comment">
                <p>{{ selectedReview.comment || 'No comments provided.' }}</p>
              </div>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="primary" variant="text" @click="showViewReviewModal = false">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      
      <!-- Request Details Modal -->
      <v-dialog v-model="showRequestDetailsModal" max-width="700px">
        <v-card v-if="selectedRequest">
          <v-card-title>Service Request #{{ selectedRequest.id }}</v-card-title>
          <v-card-text>
            <div class="request-details">
              <div class="detail-row">
                <span class="detail-label">Service:</span>
                <span class="detail-value">{{ selectedRequest.service_name }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Status:</span>
                <span class="detail-value status-badge" :class="selectedRequest.status">
                  {{ formatStatus(selectedRequest.status) }}
                </span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Date Requested:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.request_date) }}</span>
              </div>
              <div class="detail-row">
                <span class="detail-label">Professional:</span>
                <span class="detail-value">{{ selectedRequest.professional_name || 'Not assigned yet' }}</span>
              </div>
              <div class="detail-row" v-if="selectedRequest.completion_date">
                <span class="detail-label">Completed on:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.completion_date) }}</span>
              </div>
              <div class="detail-row" v-if="selectedRequest.notes">
                <span class="detail-label">Notes:</span>
                <span class="detail-value">{{ selectedRequest.notes }}</span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn 
              v-if="selectedRequest.status === 'completed' && !selectedRequest.has_review" 
              color="success" 
              variant="text" 
              @click="openReviewModal(selectedRequest); showRequestDetailsModal = false"
            >
              Leave Review
            </v-btn>
            <v-btn color="primary" variant="text" @click="showRequestDetailsModal = false">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </CustomerLayout>
</template>

<script>
import CustomerLayout from '@/layouts/CustomerLayout.vue';
import api from '../../services/api.service';

export default {
  name: 'ServiceHistoryView',
  components: {
    CustomerLayout
  },
  data() {
    return {
      serviceRequests: [],
      loading: false,
      error: null,
      statusFilter: 'all',
      sortBy: 'date_desc',
      showReviewModal: false,
      showViewReviewModal: false,
      showRequestDetailsModal: false,
      selectedRequest: null,
      selectedReview: null,
      submittingReview: false,
      reviewForm: {
        rating: 5,
        comment: ''
      }
    };
  },
  computed: {
    filteredRequests() {
      let requests = [...this.serviceRequests];
      
      // Apply status filter
      if (this.statusFilter !== 'all') {
        requests = requests.filter(req => req.status === this.statusFilter);
      }
      
      // Apply sorting
      requests.sort((a, b) => {
        if (this.sortBy === 'date_desc') {
          return new Date(b.request_date) - new Date(a.request_date);
        } else if (this.sortBy === 'date_asc') {
          return new Date(a.request_date) - new Date(b.request_date);
        } else if (this.sortBy === 'status') {
          // Sort by status (completed, assigned, requested, cancelled)
          const statusOrder = { 'completed': 1, 'assigned': 2, 'requested': 3, 'cancelled': 4 };
          return statusOrder[a.status] - statusOrder[b.status];
        }
        return 0;
      });
      
      return requests;
    }
  },
  created() {
    this.fetchServiceHistory();
  },
  methods: {
    async fetchServiceHistory() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/customer/service-history');
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
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    },
    
    formatStatus(status) {
      const statusMap = {
        'requested': 'Requested',
        'assigned': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
      };
      return statusMap[status] || status;
    },
    
    async viewRequestDetails(requestId) {
      try {
        const response = await api.get(`/customer/service-requests/${requestId}`);
        this.selectedRequest = response.data;
        this.showRequestDetailsModal = true;
      } catch (err) {
        console.error('Failed to fetch request details:', err);
        this.error = 'Failed to load request details.';
      }
    },
    
    openReviewModal(request) {
      this.selectedRequest = request;
      this.reviewForm = {
        rating: 5,
        comment: ''
      };
      this.showReviewModal = true;
    },
    
    async submitReview() {
      if (this.reviewForm.rating < 1) {
        alert('Please select a rating.');
        return;
      }
      
      this.submittingReview = true;
      
      try {
        await api.post(`/customer/service-requests/${this.selectedRequest.id}/review`, {
          rating: this.reviewForm.rating,
          comment: this.reviewForm.comment
        });
        
        // Update the request in the list
        const index = this.serviceRequests.findIndex(r => r.id === this.selectedRequest.id);
        if (index !== -1) {
          this.serviceRequests[index].has_review = true;
        }
        
        this.showReviewModal = false;
        await this.fetchServiceHistory(); // Refresh data
        alert('Thank you for your review!');
      } catch (err) {
        this.error = 'Failed to submit review: ' + (err.response?.data?.error || err.message);
      } finally {
        this.submittingReview = false;
      }
    },
    
    async viewReview(request) {
      try {
        const response = await api.get(`/customer/service-requests/${request.id}/review`);
        this.selectedRequest = request;
        this.selectedReview = response.data;
        this.showViewReviewModal = true;
      } catch (err) {
        console.error('Failed to fetch review:', err);
        this.error = 'Failed to load review details.';
      }
    }
  }
};
</script>

<style scoped>
.service-history-page {
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  margin-bottom: 20px;
  background: white;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: bold;
  font-size: 0.9rem;
}

.filter-group select {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  min-width: 180px;
}

.history-table-container {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  overflow-x: auto;
}

.service-history-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.service-history-table th,
.service-history-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.service-history-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

tr.completed {
  background-color: #f8f9fa;
}

tr.cancelled {
  color: #999;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-review,
.btn-view-review,
.btn-details {
  padding: 5px 10px;
  font-size: 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-review {
  background-color: #28a745;
  color: white;
}

.btn-view-review {
  background-color: #17a2b8;
  color: white;
}

.btn-details {
  background-color: #6c757d;
  color: white;
}

.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.requested {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.assigned {
  background-color: #cce5ff;
  color: #004085;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.rating-stars {
  display: flex;
  align-items: center;
  gap: 5px;
  margin-top: 10px;
}

.rating-text,
.rating-value {
  margin-left: 10px;
  font-weight: bold;
}

.review-date {
  font-size: 0.9rem;
  color: #6c757d;
  margin: 10px 0;
}

.review-comment {
  margin-top: 15px;
  padding: 10px;
  background-color: #f8f9fa;
  border-radius: 4px;
}

.loading,
.empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.request-details {
  display: grid;
  gap: 10px;
}

.detail-row {
  display: grid;
  grid-template-columns: 150px 1fr;
  gap: 10px;
}

.detail-label {
  font-weight: bold;
  color: #6c757d;
}
</style>
