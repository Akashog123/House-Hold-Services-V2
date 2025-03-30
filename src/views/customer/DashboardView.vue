<template>
  <div class="dashboard-wrapper">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h3>Customer Dashboard</h3>
        <div>
          <router-link to="/services" class="btn btn-primary">
            <i class="bi bi-plus-lg me-2"></i> Book a Service
          </router-link>
        </div>
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
      <div class="col-12 col-sm-6 col-lg-3">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-warning bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-hourglass-split fs-4 text-warning"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">Requested</h5>
            </div>
            <h3 class="card-title mb-0">{{ requestedServices.length }}</h3>
          </div>
        </div>
      </div>
      
      <div class="col-12 col-sm-6 col-lg-3">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-secondary bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-gear-wide-connected fs-4 text-primary"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">In Progress</h5>
            </div>
            <h3 class="card-title mb-0">{{ inProgressServices.length }}</h3>
          </div>
        </div>
      </div>
      
      <div class="col-12 col-sm-6 col-lg-3">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-success bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-check-circle fs-4 text-success"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">Completed</h5>
            </div>
            <h3 class="card-title mb-0">{{ completedServices.length }}</h3>
          </div>
        </div>
      </div>   
      
      <div class="col-12 col-sm-6 col-lg-3">
        <div class="card h-100 stat-card">
          <div class="card-body d-flex flex-column align-items-center text-center">
            <div class="d-flex align-items-center mb-3">
              <div class="icon-wrapper bg-danger bg-opacity-10 rounded-circle p-3 me-2">
                <i class="bi bi-x-circle fs-4 text-danger"></i>
              </div>
              <h5 class="card-subtitle text-muted mb-0">Cancelled</h5>
            </div>
            <h3 class="card-title mb-0">{{ cancelledServices.length }}</h3>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Recent Bookings Section -->
    <div class="row mb-4">
      <div class="col-12">
        <div class="card">
          <div class="card-header d-flex justify-content-between align-items-center">
            <h5 class="mb-0">Recent Bookings</h5>
          </div>
          <div class="card-body">
            <div v-if="loading" class="text-center py-3">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
              <p class="mt-2">Loading service requests...</p>
            </div>
            
            <div class="table-responsive">
              <table v-if="recentBookings.length > 0" class="table table-hover">
                <thead>
                  <tr>
                    <th>Service</th>
                    <th>Booking Date</th>
                    <th>Completion Date</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="request in recentBookings" :key="request.id">
                    <td>{{ request.service_name }}</td>
                    <td>
                      {{ formatDate(request.request_date) }}
                    </td>
                    <td>
                      {{ formatDate(request.completion_date) }}
                    </td>
                    <td>
                      <span class="status-badge" :class="request.status">
                        {{ formatStatus(request.status) }}
                      </span>
                    </td>
                    <td>
                      <router-link :to="`/customer/bookings?id=${request.id}`" class="btn btn-sm btn-primary">
                        Details
                      </router-link>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            
            <div v-if="!loading && recentBookings.length === 0" class="text-center py-3">
              <p class="text-muted mb-0">You don't have any bookings yet.</p>
              <router-link to="/services" class="btn btn-primary mt-3">
                Book Your First Service
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '../../services/api.service';
export default {
  name: 'CustomerDashboard',
  data() {
    return {
      serviceRequests: [],
      availableServices: [],
      loading: false,
      error: null,
      showCreateRequestModal: false,
      showRequestDetailsModal: false,
      selectedRequest: null,
      createRequestError: null,
      creatingRequest: false,
      newRequest: {
        service_id: null,
        notes: ''
      }
    };
  },
  computed: {
    requestedServices() {
      return this.serviceRequests.filter(req => req.status === 'requested');
    },
    inProgressServices() {
      return this.serviceRequests.filter(req => req.status === 'assigned');
    },
    completedServices() {
      return this.serviceRequests.filter(req => req.status === 'completed');
    },
    cancelledServices() {
      return this.serviceRequests.filter(req => req.status === 'cancelled');
    },
    recentBookings() {
      // Return the 5 most recent bookings
      return [...this.serviceRequests]
        .sort((a, b) => new Date(b.request_date) - new Date(a.request_date))
        .slice(0, 4);
    }
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
      return date.toLocaleDateString();
    },
    
    formatStatus(status) {
      const statusMap = {
        'requested': 'Requested',
        'assigned': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled'
      };
      return statusMap[status] || status;
    }
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

/* Responsive adjustments */
@media (max-width: 768px) {
  .dashboard-wrapper {
    padding: 1rem;
  }
  
  .card-title {
    font-size: 1.25rem;
  }
}
</style>
