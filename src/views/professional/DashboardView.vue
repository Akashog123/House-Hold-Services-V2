<template>
  <ProfessionalLayout>
    <div class="professional-dashboard">
      <h1>Professional Dashboard</h1>
      
      <div class="dashboard-stats">
        <div class="stat-card">
          <div class="stat-value">{{ assignedRequests.length }}</div>
          <div class="stat-label">Assigned Jobs</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ completedRequests.length }}</div>
          <div class="stat-label">Completed Jobs</div>
        </div>
        <div class="stat-card">
          <div class="stat-value">{{ availableRequests.length }}</div>
          <div class="stat-label">Available Jobs</div>
        </div>
      </div>
      
      <!-- Available Requests Section -->
      <div class="dashboard-section">
        <h2>Available Service Requests</h2>
        
        <div v-if="loading" class="loading">Loading service requests...</div>
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <table v-if="availableRequests.length > 0" class="service-request-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Service</th>
              <th>Customer</th>
              <th>Date Requested</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in availableRequests" :key="request.id">
              <td>#{{ request.id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ request.customer_name }}</td>
              <td>{{ formatDate(request.request_date) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="acceptRequest(request.id)" class="btn btn-success btn-sm">
                    Accept
                  </button>
                  <button @click="viewRequestDetails(request.id)" class="btn btn-info btn-sm">
                    Details
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-else-if="!loading" class="empty-state">
          No available service requests at the moment.
        </div>
      </div>
      
      <!-- My Assigned Requests Section -->
      <div class="dashboard-section">
        <h2>My Assigned Jobs</h2>
        
        <table v-if="assignedRequests.length > 0" class="service-request-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Service</th>
              <th>Customer</th>
              <th>Date Requested</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in assignedRequests" :key="request.id">
              <td>#{{ request.id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ request.customer_name }}</td>
              <td>{{ formatDate(request.request_date) }}</td>
              <td>
                <div class="action-buttons">
                  <button @click="completeRequest(request.id)" class="btn btn-primary btn-sm">
                    Mark Complete
                  </button>
                  <button @click="rejectRequest(request.id)" class="btn btn-danger btn-sm">
                    Reject
                  </button>
                  <button @click="viewRequestDetails(request.id)" class="btn btn-info btn-sm">
                    Details
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-else class="empty-state">
          You don't have any assigned jobs yet.
        </div>
      </div>
      
      <!-- Completed Requests Section -->
      <div class="dashboard-section">
        <h2>Completed Jobs History</h2>
        
        <table v-if="completedRequests.length > 0" class="service-request-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Service</th>
              <th>Customer</th>
              <th>Completed Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in completedRequests" :key="request.id">
              <td>#{{ request.id }}</td>
              <td>{{ request.service_name }}</td>
              <td>{{ request.customer_name }}</td>
              <td>{{ formatDate(request.completion_date) }}</td>
              <td>
                <button @click="viewRequestDetails(request.id)" class="btn btn-info btn-sm">
                  Details
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-else class="empty-state">
          You haven't completed any jobs yet.
        </div>
      </div>
      
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
                <span class="detail-label">Customer:</span>
                <span class="detail-value">{{ selectedRequest.customer_name }}</span>
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
              <div class="detail-row" v-if="selectedRequest.completion_date">
                <span class="detail-label">Completed on:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.completion_date) }}</span>
              </div>
              <div class="detail-row" v-if="selectedRequest.notes">
                <span class="detail-label">Customer Notes:</span>
                <span class="detail-value">{{ selectedRequest.notes }}</span>
              </div>
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <template v-if="selectedRequest.status === 'requested'">
              <v-btn color="success" variant="text" @click="acceptRequest(selectedRequest.id); showRequestDetailsModal = false">
                Accept
              </v-btn>
            </template>
            <template v-else-if="selectedRequest.status === 'assigned' && selectedRequest.is_assigned_to_me">
              <v-btn color="primary" variant="text" @click="completeRequest(selectedRequest.id); showRequestDetailsModal = false">
                Mark Complete
              </v-btn>
              <v-btn color="error" variant="text" @click="rejectRequest(selectedRequest.id); showRequestDetailsModal = false">
                Reject
              </v-btn>
            </template>
            <v-btn color="grey-darken-1" variant="text" @click="showRequestDetailsModal = false">
              Close
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </div>
  </ProfessionalLayout>
</template>

<script>
import api from '../../services/api.service';
import ProfessionalLayout from '@/layouts/ProfessionalLayout.vue';

export default {
  name: 'ProfessionalDashboard',
  components: {
    ProfessionalLayout
  },
  data() {
    return {
      serviceRequests: [],
      loading: false,
      error: null,
      showRequestDetailsModal: false,
      selectedRequest: null
    };
  },
  computed: {
    availableRequests() {
      return this.serviceRequests.filter(req => 
        req.status === 'requested' && !req.is_assigned_to_me
      );
    },
    assignedRequests() {
      return this.serviceRequests.filter(req => 
        req.status === 'assigned' && req.is_assigned_to_me
      );
    },
    completedRequests() {
      return this.serviceRequests.filter(req => 
        req.status === 'completed' && req.is_assigned_to_me
      );
    }
  },
  created() {
    this.fetchServiceRequests();
  },
  methods: {
    async fetchServiceRequests() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/professional/service-requests');
        this.serviceRequests = response.data;
      } catch (err) {
        this.error = 'Failed to load service requests: ' + (err.response?.data?.error || err.message);
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
        const response = await api.get(`/professional/service-requests/${requestId}`);
        this.selectedRequest = response.data;
        this.showRequestDetailsModal = true;
      } catch (err) {
        console.error('Failed to fetch request details:', err);
      }
    },
    
    async acceptRequest(requestId) {
      try {
        await api.put(`/professional/service-requests/${requestId}`, {
          action: 'accept'
        });
        await this.fetchServiceRequests();
      } catch (err) {
        this.error = 'Failed to accept request: ' + (err.response?.data?.error || err.message);
      }
    },
    
    async rejectRequest(requestId) {
      if (confirm('Are you sure you want to reject this service request?')) {
        try {
          await api.put(`/professional/service-requests/${requestId}`, {
            action: 'reject'
          });
          await this.fetchServiceRequests();
        } catch (err) {
          this.error = 'Failed to reject request: ' + (err.response?.data?.error || err.message);
        }
      }
    },
    
    async completeRequest(requestId) {
      if (confirm('Are you sure you want to mark this service request as complete?')) {
        try {
          await api.put(`/professional/service-requests/${requestId}`, {
            action: 'complete'
          });
          await this.fetchServiceRequests();
        } catch (err) {
          this.error = 'Failed to complete request: ' + (err.response?.data?.error || err.message);
        }
      }
    }
  }
};
</script>

<style scoped>
.professional-dashboard {
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 15px;
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.stat-card {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  text-align: center;
}

.stat-value {
  font-size: 2.5rem;
  font-weight: bold;
  color: #4caf50;
}

.stat-label {
  font-size: 1rem;
  color: #666;
  margin-top: 5px;
}

.dashboard-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.service-request-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 15px;
}

.service-request-table th,
.service-request-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
}

.service-request-table th {
  background-color: #f5f5f5;
  font-weight: 600;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 5px 10px;
  font-size: 0.8rem;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-success {
  background-color: #28a745;
  color: white;
}

.btn-primary {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
}

.btn-primary:hover {
  background-color: var(--primary-light);
  border-color: var(--primary-light);
}

.btn-outline-primary {
  color: var(--primary);
  border-color: var(--primary);
}

.btn-outline-primary:hover {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
}

.loading {
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

.empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
  font-style: italic;
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
