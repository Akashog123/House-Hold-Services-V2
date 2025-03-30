<template>
  <div class="dashboard-wrapper">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h3>Professional Dashboard</h3>
        <button 
          class="btn btn-primary"
          :disabled="loading"
          @click="fetchServiceRequests"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>
          <span v-if="!loading">Refresh</span>
          <span v-else class="spinner-border spinner-border-sm" role="status"></span>
        </button>
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
    
    <!-- Stats Overview -->
    <div class="row g-4 mb-4">
      <div class="col-12 col-sm-6 col-lg-4">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-secondary bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-briefcase fs-4 text-primary"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">Assigned Jobs</h5>
            </div>
            <h3 class="card-title mb-0">{{ assignedRequests().length }}</h3>
          </div>
        </div>
      </div>
      
      <div class="col-12 col-sm-6 col-lg-4">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-success bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-check-circle fs-4 text-success"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">Completed Jobs</h5>
            </div>
            <h3 class="card-title mb-0">{{ completedRequests().length }}</h3>
          </div>
        </div>
      </div>
      
      <div class="col-12 col-sm-6 col-lg-4">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-info bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-list-task fs-4 text-info"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">Available Jobs</h5>
            </div>
            <h3 class="card-title mb-0">{{ availableRequests().length }}</h3>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Available Requests Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Available Service Requests</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-3">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Loading service requests...</p>
            </div>
            
            <div v-if="error" class="alert alert-danger" role="alert">{{ error }}</div>
            
            <div class="table-responsive">
              <table v-if="availableRequests().length > 0" class="table table-hover">
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
                  <tr v-for="request in availableRequests()" :key="request.id">
                    <td>#{{ request.id }}</td>
                    <td>{{ request.service_name }}</td>
                    <td>{{ request.customer_name }}</td>
                    <td>{{ formatDate(request.request_date) }}</td>
                    <td>
                      <div class="d-flex gap-2">
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
            </div>
            
            <div v-if="!loading && availableRequests().length === 0" class="text-center py-3">
              <p class="text-muted mb-0">No available service requests at the moment.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- My Assigned Requests Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">My Assigned Jobs</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table v-if="assignedRequests().length > 0" class="table table-hover">
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
                  <tr v-for="request in assignedRequests()" :key="request.id">
                    <td>#{{ request.id }}</td>
                    <td>{{ request.service_name }}</td>
                    <td>{{ request.customer_name }}</td>
                    <td>{{ formatDate(request.request_date) }}</td>
                    <td>
                      <div class="d-flex gap-2">
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
            </div>
            
            <div v-if="assignedRequests().length === 0" class="text-center py-3">
              <p class="text-muted mb-0">You don't have any assigned jobs yet.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Completed Requests Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header">
            <h5 class="mb-0">Completed Jobs History</h5>
          </div>
          <div class="card-body">
            <div class="table-responsive">
              <table v-if="completedRequests().length > 0" class="table table-hover">
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
                  <tr v-for="request in completedRequests()" :key="request.id">
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
            </div>
            
            <div v-if="completedRequests().length === 0" class="text-center py-3">
              <p class="text-muted mb-0">You haven't completed any jobs yet.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Request Details Modal (Bootstrap modal instead of v-dialog) -->
    <div class="modal fade" id="requestDetailsModal" tabindex="-1" ref="requestModal">
      <div class="modal-dialog modal-lg">
        <div class="modal-content" v-if="selectedRequest">
          <div class="modal-header">
            <h5 class="modal-title">Service Request #{{ selectedRequest.id }}</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
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
              <div class="detail-row" v-if="selectedRequest.assigned_date">
                <span class="detail-label">Accepted on:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.assigned_date) }}</span>
              </div>
              <div class="detail-row" v-if="selectedRequest.completed_on">
                <span class="detail-label">Completed on:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.completed_on) }}</span>
              </div>
              <div class="detail-row" v-if="selectedRequest.completion_date && !selectedRequest.completed_on">
                <span class="detail-label">Expected completion by:</span>
                <span class="detail-value">{{ formatDate(selectedRequest.completion_date) }}</span>
              </div>
              <div class="detail-row" v-if="selectedRequest.notes">
                <span class="detail-label">Customer Notes:</span>
                <span class="detail-value">{{ selectedRequest.notes }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <template v-if="selectedRequest.status === 'requested'">
              <button class="btn btn-success" @click="acceptRequest(selectedRequest.id); closeModal()">
                Accept
              </button>
            </template>
            <template v-else-if="selectedRequest.status === 'assigned'">
              <button class="btn btn-primary" @click="completeRequest(selectedRequest.id); closeModal()">
                Mark Complete
              </button>
              <button class="btn btn-danger" @click="rejectRequest(selectedRequest.id); closeModal()">
                Reject
              </button>
            </template>
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Error Toast -->
    <div class="toast-container position-fixed top-0 end-0 p-3">
      <div 
        class="toast align-items-center text-bg-danger border-0" 
        role="alert" 
        :class="{ 'show': error }"
      >
        <div class="d-flex">
          <div class="toast-body">
            {{ error }}
          </div>
          <button 
            type="button" 
            class="btn-close btn-close-white me-2 m-auto" 
            @click="error = null"
          ></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { Modal } from 'bootstrap';
import api from '../../services/api.service';

export default {
  name: 'ProfessionalDashboard',
  setup() {
    const serviceRequests = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const selectedRequest = ref(null);
    const requestModal = ref(null);
    let modal = null;

    // Initialize the modal on component mount
    onMounted(() => {
      modal = new Modal(document.getElementById('requestDetailsModal'));
    });

    const fetchServiceRequests = async () => {
      loading.value = true;
      error.value = null;
      
      try {
        const response = await api.get('/professional/service-requests');
        serviceRequests.value = response.data;
        console.log('Service Requests:', serviceRequests.value);
      } catch (err) {
        error.value = 'Failed to load service requests: ' + (err.response?.data?.error || err.message);
      } finally {
        loading.value = false;
      }
    };
    
    const viewRequestDetails = async (requestId) => {
      try {
        const response = await api.get(`/professional/service-requests/${requestId}`);
        selectedRequest.value = response.data;
        modal.show();
      } catch (err) {
        console.error('Failed to fetch request details:', err);
      }
    };
    
    const closeModal = () => {
      modal.hide();
    };
    
    const acceptRequest = async (requestId) => {
      try {
        await api.put(`/professional/service-requests/${requestId}`, {
          action: 'accept'
        });
        await fetchServiceRequests();
      } catch (err) {
        error.value = 'Failed to accept request: ' + (err.response?.data?.error || err.message);
      }
    };
    
    const rejectRequest = async (requestId) => {
      if (confirm('Are you sure you want to reject this service request?')) {
        try {
          await api.put(`/professional/service-requests/${requestId}`, {
            action: 'reject'
          });
          await fetchServiceRequests();
        } catch (err) {
          error.value = 'Failed to reject request: ' + (err.response?.data?.error || err.message);
        }
      }
    };
    
    const completeRequest = async (requestId) => {
      if (confirm('Are you sure you want to mark this service request as complete?')) {
        try {
          await api.put(`/professional/service-requests/${requestId}`, {
            action: 'complete'
          });
          await fetchServiceRequests();
        } catch (err) {
          error.value = 'Failed to complete request: ' + (err.response?.data?.error || err.message);
        }
      }
    };
    
    const formatDate = (dateStr) => {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
    };
    
    const formatStatus = (status) => {
      const statusMap = {
        'requested': 'Requested',
        'assigned': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
      };
      return statusMap[status] || status;
    };

    // Computed properties as functions using filter
    const availableRequests = () => {
      return serviceRequests.value.filter(req => req.status === 'requested');
    };
    
    const assignedRequests = () => {
      return serviceRequests.value.filter(req => req.status === 'assigned');
    };
    
    const completedRequests = () => {
      return serviceRequests.value.filter(req => req.status === 'completed');
    };

    // Fetch data on component creation
    fetchServiceRequests();

    return {
      serviceRequests,
      loading,
      error,
      selectedRequest,
      requestModal,
      availableRequests,
      assignedRequests,
      completedRequests,
      fetchServiceRequests,
      viewRequestDetails,
      closeModal,
      acceptRequest,
      rejectRequest,
      completeRequest,
      formatDate,
      formatStatus
    };
  }
};
</script>

<style scoped>
.dashboard-wrapper {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.stat-card {
  transition: transform 0.2s ease-in-out;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.stat-card:hover {
  transform: translateY(-4px);
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Status badge styles */
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

.toast {
  transition: opacity 0.3s ease-in-out;
  opacity: 0;
}

.toast.show {
  opacity: 1;
}

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard-wrapper {
    padding: 1rem;
  }
  
  .h2 {
    font-size: 1.5rem;
  }
  
  .card-title {
    font-size: 1.25rem;
  }
}
</style>
