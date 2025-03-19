<template>
  <CustomerLayout>
    <div class="customer-dashboard">
      <h1>Customer Dashboard</h1>
      
      <div class="dashboard-section service-request-section">
        <h2>My Service Requests</h2>
        
        <div v-if="loading" class="loading">Loading your service requests...</div>
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <div class="action-bar">
          <button @click="showCreateRequestModal = true" class="btn btn-primary">
            <v-icon start>mdi-plus</v-icon>
            New Service Request
          </button>
        </div>
        
        <table v-if="serviceRequests.length > 0" class="service-request-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Service</th>
              <th>Date Requested</th>
              <th>Professional</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="request in serviceRequests" :key="request.id" 
                :class="{ 'completed': request.status === 'completed', 
                         'cancelled': request.status === 'cancelled' }">
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
                  <button v-if="request.status === 'requested'"
                          @click="cancelRequest(request.id)" 
                          class="btn btn-danger btn-sm">
                    Cancel
                  </button>
                  <button @click="viewRequestDetails(request.id)" 
                          class="btn btn-info btn-sm">
                    View
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
        
        <div v-else-if="!loading" class="empty-state">
          You don't have any service requests yet. Create one to get started!
        </div>
      </div>
      
      <!-- Create Service Request Modal -->
      <v-dialog v-model="showCreateRequestModal" max-width="600px">
        <v-card>
          <v-card-title>Create New Service Request</v-card-title>
          <v-card-text>
            <div v-if="createRequestError" class="error-message">
              {{ createRequestError }}
            </div>
            
            <v-form @submit.prevent="createServiceRequest">
              <v-select
                v-model="newRequest.service_id"
                :items="availableServices"
                item-title="name"
                item-value="id"
                label="Select Service"
                required
              ></v-select>
              
              <v-textarea
                v-model="newRequest.notes"
                label="Additional Notes (optional)"
                rows="3"
              ></v-textarea>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn color="grey-darken-1" variant="text" @click="showCreateRequestModal = false">
              Cancel
            </v-btn>
            <v-btn 
              color="primary" 
              variant="elevated" 
              @click="createServiceRequest"
              :loading="creatingRequest"
            >
              Submit Request
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
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn 
              v-if="selectedRequest.status === 'requested'"
              color="error" 
              variant="text" 
              @click="confirmCancel"
            >
              Cancel Request
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
import api from '../../services/api.service';
import CustomerLayout from '@/layouts/CustomerLayout.vue';

export default {
  name: 'CustomerDashboard',
  components: {
    CustomerLayout
  },
  data() {
    return {
      serviceRequests: [],
      availableServices: [],
      loading: false,
      error: null,
      showCreateRequestModal: false,
      showRequestDetailsModal: false,
      selectedRequestId: null,
      selectedRequest: null,
      createRequestError: null,
      creatingRequest: false,
      newRequest: {
        service_id: null,
        notes: ''
      }
    };
  },
  created() {
    this.fetchServiceRequests();
    this.fetchAvailableServices();
  },
  methods: {
    async fetchServiceRequests() {
      this.loading = true;
      this.error = null;
      
      try {
        const response = await api.get('/customer/service-requests');
        this.serviceRequests = response.data;
      } catch (err) {
        this.error = 'Failed to load service requests: ' + (err.response?.data?.error || err.message);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchAvailableServices() {
      try {
        const response = await api.get('/services');
        this.availableServices = response.data;
      } catch (err) {
        console.error('Failed to load services:', err);
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
    
    async createServiceRequest() {
      if (!this.newRequest.service_id) {
        this.createRequestError = 'Please select a service';
        return;
      }
      
      this.creatingRequest = true;
      this.createRequestError = null;
      
      try {
        await api.post('/customer/service-requests', this.newRequest);
        this.showCreateRequestModal = false;
        this.newRequest = { service_id: null, notes: '' };
        await this.fetchServiceRequests();
      } catch (err) {
        this.createRequestError = 'Failed to create service request: ' + 
                                 (err.response?.data?.error || err.message);
      } finally {
        this.creatingRequest = false;
      }
    },
    
    async viewRequestDetails(requestId) {
      try {
        const response = await api.get(`/customer/service-requests/${requestId}`);
        this.selectedRequest = response.data;
        this.showRequestDetailsModal = true;
      } catch (err) {
        console.error('Failed to fetch request details:', err);
      }
    },
    
    async cancelRequest(requestId) {
      if (confirm('Are you sure you want to cancel this service request?')) {
        try {
          await api.put(`/customer/service-requests/${requestId}`, {
            status: 'cancelled'
          });
          await this.fetchServiceRequests();
        } catch (err) {
          this.error = 'Failed to cancel request: ' + (err.response?.data?.error || err.message);
        }
      }
    },
    
    confirmCancel() {
      if (confirm('Are you sure you want to cancel this service request?')) {
        this.cancelRequest(this.selectedRequest.id);
        this.showRequestDetailsModal = false;
      }
    }
  }
};
</script>

<style scoped>
.customer-dashboard {
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

.dashboard-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 30px;
}

.action-bar {
  margin-bottom: 20px;
}

.btn-primary {
  background-color: var(--primary);
  border-color: var(--primary);
  color: white;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-primary:hover {
  background-color: var(--primary-light);
  border-color: var(--primary-light);
}

.btn-primary:hover {
  background-color: var(--primary-light);
  border-color: var(--primary-light);
}

.service-request-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
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

tr.completed {
  background-color: #f8f9fa;
  color: #6c757d;
}

tr.cancelled {
  background-color: #f9f9f9;
  color: #999;
  text-decoration: line-through;
}

.action-buttons {
  display: flex;
  gap: 5px;
}

.btn-sm {
  padding: 3px 10px;
  font-size: 0.8rem;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}

.btn-info {
  background-color: #17a2b8;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
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
  padding: 30px;
  color: #666;
  font-style: italic;
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
