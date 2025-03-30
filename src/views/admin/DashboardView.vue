<template>
  <div class="dashboard-wrapper">
    <!-- Page Header -->
    <div class="row mb-4">
      <div class="col-12 d-flex justify-content-between align-items-center">
        <h3>Dashboard Overview</h3>
        <button 
          class="btn btn-primary"
          :disabled="loading"
          @click="fetchDashboardData"
        >
          <i class="bi bi-arrow-clockwise me-2"></i>
          <span v-if="!loading">Refresh Data</span>
          <span v-else>
            <span class="spinner-border spinner-border-sm" role="status"></span>
            Loading...
          </span>
        </button>
      </div>
    </div>

    <!-- Notifications Section -->
    <div class="row mb-4" v-if="pendingApprovals > 0">
      <div class="col-12">
        <div class="card border-warning">
          <div class="card-body">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h5 class="card-title mb-0">
                  <i class="bi bi-exclamation-triangle-fill text-warning me-2"></i>
                  Pending Approvals
                </h5>
                <p class="card-text mt-2 mb-0">
                  {{ pendingApprovals }} professional registration(s) awaiting your review
                </p>
              </div>
              <router-link to="/admin/approvals" class="btn btn-warning">
                Review Approvals
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats Overview -->
    <div class="row g-4">
      <div 
        v-for="stat in stats" 
        :key="stat.title"
        class="col-12 col-sm-6 col-lg-3"
      >
        <div class="card h-100 stat-card">
          <div class="card-body">
            <div class="d-flex align-items-center mb-3">
              <div :class="`icon-wrapper bg-${stat.color} bg-opacity-10 rounded-circle p-3 me-3`">
                <i :class="`bi ${stat.icon} fs-4 text-${stat.color}`"></i>
              </div>
              <h6 class="card-subtitle mb-0 text-muted">{{ stat.title }}</h6>
            </div>
            <div class="d-flex justify-content-between align-items-center">
              <h2 class="card-title mb-0">{{ stat.value }}</h2>
              <div v-if="stat.trend !== undefined || stat.highlight">
                <span 
                  class="badge"
                  :class="[
                    stat.highlight && stat.value !== '0' ? 'text-bg-warning' : 
                    stat.trend >= 0 ? 'text-bg-success' : 'text-bg-danger'
                  ]"
                >
                  <i v-if="stat.trend !== undefined" 
                    class="bi"
                    :class="stat.trend >= 0 ? 'bi-arrow-up' : 'bi-arrow-down'"
                  ></i>
                  {{ Math.abs(stat.trend) }}%
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    </div>

    <!-- Error Toast -->
    <div class="toast-container position-fixed top-0 end-0 p-3">
      <div 
        class="toast align-items-center text-bg-danger border-0" 
        role="alert" 
        :class="{ 'show': showError }"
      >
        <div class="d-flex">
          <div class="toast-body">
            {{ errorMessage }}
          </div>
          <button 
            type="button" 
            class="btn-close btn-close-white me-2 m-auto" 
            @click="showError = false"
          ></button>
        </div>
      </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api.service.js'

export default {
  name: 'AdminDashboard',
  
  setup() {
    const loading = ref(false)
    const showError = ref(false)
    const errorMessage = ref('')
    
    const stats = ref([
      {
        title: 'Customers',
        value: '0',
        trend: 0,
        icon: 'bi-people-fill',
        color: 'secondary'
      },
      {
        title: 'Professionals',
        value: '0',
        trend: 0,
        icon: 'bi-person-fill-gear',
        color: 'info'
      },
      {
        title: 'Active Services',
        value: '0',
        trend: 0,
        icon: 'bi-tools',
        color: 'success'
      },
      {
        title: 'Pending Approvals',
        value: '0',
        trend: 0,
        icon: 'bi-clock',
        color: 'warning'
      },
      {
        title: "Professional's Revenues",
        value: '₹0',
        trend: 0,
        icon: 'bi-currency-dollar',
        color: 'info'
      }
    ])

    // Add a computed property for pending approvals
    const pendingApprovals = ref(0)
    
    const fetchDashboardData = async () => {
      loading.value = true
      try {
        const [usersResponse, servicesResponse, professionalsResponse, revenueResponse] = await Promise.all([
          api.get('/admin/users/stats'),                    
          api.get('/admin/services'), 
          api.get('/admin/professionals', { 
            params: { approved: 'false', active: 'true' } // Explicitly request pending approvals
          }),
          api.get('/admin/analytics/revenue')
        ])

        console.log('Dashboard API responses:', {
          users: usersResponse.data,
          services: servicesResponse.data,
          professionals: professionalsResponse.data,
          revenue: revenueResponse.data
        });

        // Handle customer count with safety checks
        if (usersResponse.data && typeof usersResponse.data.total_customers !== 'undefined') {
          stats.value[0].value = String(usersResponse.data.total_customers);
          stats.value[0].trend = usersResponse.data.customer_growth || 0;
        } else {
          // Fallback if data doesn't match expected structure
          stats.value[0].value = '0';
          stats.value[0].trend = 0;
        }

        // Handle professional count with safety checks
        if (usersResponse.data && typeof usersResponse.data.total_professionals !== 'undefined') {
          stats.value[1].value = String(usersResponse.data.total_professionals);
          stats.value[1].trend = usersResponse.data.professional_growth || 0;
        } else {
          // Fallback if data doesn't match expected structure
          stats.value[1].value = '0';
          stats.value[1].trend = 0;
        }

        // Handle services data with safety checks
        if (servicesResponse.data && servicesResponse.data.total_active_services) {
          stats.value[2].value = String(servicesResponse.data.total_active_services);
          stats.value[2].trend = servicesResponse.data.service_growth || 0;
        } else {
          // Parse service data from the actual response structure
          const serviceData = servicesResponse.data?.data || servicesResponse.data || [];
          const serviceCount = Array.isArray(serviceData) ? serviceData.length : 0;
          stats.value[2].value = String(serviceCount);
          stats.value[2].trend = 0;
        }

        // Handle pending approvals data safely
        const pendingProfessionals = Array.isArray(professionalsResponse.data) ? professionalsResponse.data : [];
        stats.value[3].value = String(pendingProfessionals.length);
        
        // If this value is greater than 0, make it noticeable
        if (pendingProfessionals.length > 0) {
          stats.value[3].highlight = true;
        }

        // Handle revenue data safely
        if (revenueResponse.data && typeof revenueResponse.data.total_revenue !== 'undefined') {
          const totalRevenue = parseFloat(revenueResponse.data.total_revenue) || 0;
          stats.value[4].value = `₹${totalRevenue.toFixed(2)}`;
          stats.value[4].trend = revenueResponse.data.revenue_growth || 0;
        } else {
          stats.value[4].value = '₹0.00';
          stats.value[4].trend = 0;
        }

        // Handle pending approvals count
        if (Array.isArray(professionalsResponse.data)) {
          pendingApprovals.value = professionalsResponse.data.length
          
          // Update the "Pending Approvals" stat card
          const pendingApprovalsIndex = stats.value.findIndex(stat => stat.title === 'Pending Approvals')
          if (pendingApprovalsIndex !== -1) {
            stats.value[pendingApprovalsIndex].value = String(pendingApprovals.value)
            // Highlight if there are pending approvals
            if (pendingApprovals.value > 0) {
              stats.value[pendingApprovalsIndex].highlight = true
            }
          }
        }

      } catch (error) {
        console.error('Dashboard data fetch error:', error);
        errorMessage.value = 'Failed to load dashboard data';
        showError.value = true;
        
        // Reset stats to default values to prevent further errors
        stats.value = stats.value.map(stat => ({
          ...stat,
          value: stat.title.includes("Professional's Revenues") ? '₹0.00' : '0',
          trend: 0
        }));
      } finally {
        loading.value = false;
      }
    }

    onMounted(() => {
      fetchDashboardData()
    })

    return {
      loading,
      stats,
      showError,
      errorMessage,
      fetchDashboardData,
      pendingApprovals
    }
  }
}
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

.action-card {
  transition: all 0.2s ease-in-out;
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}

.icon-wrapper {
  width: 48px;
  height: 48px;
  display: flex;
  align-items: center;
  justify-content: center;
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
