<template>
  <div class="analytics-container">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Analytics Dashboard</h3>
      <div class="d-flex gap-2">
        <!-- Export CSV button -->
        <button @click="showExportModal = true" class="btn btn-outline-primary">
          <i class="bi bi-file-earmark-arrow-down"></i> Export CSV Data
        </button>
        <!-- Simple timeframe selector -->
        <select v-model="timeframe" class="form-select w-auto">
          <option value="week">Last Week</option>
          <option value="month" selected>Last Month</option>
          <option value="year">Last Year</option>
        </select>
      </div>
    </div>

    <!-- Success Alert -->
    <div v-if="showSuccessAlert" class="alert alert-success alert-dismissible fade show" role="alert">
      <strong>Success!</strong> {{ alertMessage }}
      <button @click="showSuccessAlert = false" type="button" class="btn-close" aria-label="Close"></button>
    </div>

    <!-- Error Alert -->
    <div v-if="showErrorAlert" class="alert alert-danger alert-dismissible fade show" role="alert">
      <strong>Error!</strong> {{ alertMessage }}
      <button @click="showErrorAlert = false" type="button" class="btn-close" aria-label="Close"></button>
    </div>

    <div class="row">
      <div class="col-md-6 mb-4">
        <!-- Revenue Chart Card -->
        <div class="card">
          <div class="card-header bg-secondary">
            <h5 class="mb-0 text-white">Revenue of Service Professionals</h5>
          </div>
          <div class="card-body">
            <canvas ref="revenueChart"></canvas>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-4">
        <!-- User Growth Chart Card -->
        <div class="card">
          <div class="card-header bg-secondary">
            <h5 class="mb-0 text-white">User Growth</h5>
          </div>
          <div class="card-body">
            <canvas ref="userGrowthChart"></canvas>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-4">
        <!-- Services Usage Chart Card -->
        <div class="card">
          <div class="card-header bg-secondary">
            <h5 class="mb-0 text-white">Services Usage</h5>
          </div>
          <div class="card-body">
            <canvas ref="servicesUsageChart"></canvas>
          </div>
        </div>
      </div>
      <div class="col-md-6 mb-4">
        <!-- User Stats Chart Card -->
        <div class="card">
          <div class="card-header bg-secondary">
            <h5 class="mb-0 text-white">User Statistics (Professionals vs Customers)</h5>
          </div>
          <div class="card-body">
            <canvas ref="userStatsChart"></canvas>
          </div>
        </div>
      </div>
    </div>

    <!-- Export Confirmation Modal -->
    <div class="modal fade" :class="{ 'show d-block': showExportModal }" tabindex="-1" role="dialog">
      <div class="modal-dialog" role="document">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Export Services Data</h5>
            <button @click="showExportModal = false" type="button" class="btn-close" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>This will generate a CSV export of all completed service requests and will be emailed to the admin. Continue?</p>
          </div>
          <div class="modal-footer">
            <button @click="showExportModal = false" type="button" class="btn btn-secondary">Cancel</button>
            <button @click="exportServicesData" type="button" class="btn btn-primary" :disabled="exporting">
              <span v-if="exporting" class="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
              {{ exporting ? 'Processing...' : 'Export Data' }}
            </button>
          </div>
        </div>
      </div>
    </div>
    <div v-if="showExportModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script>
import { ref, onMounted, watch } from 'vue'
import AdminService from '@/services/admin.service'
import Chart from 'chart.js/auto'

export default {
  name: 'AdminAnalytics',
  setup() {
    const timeframe = ref('month')
    const revenueChart = ref(null)
    const userGrowthChart = ref(null)
    const servicesUsageChart = ref(null)
    const userStatsChart = ref(null)
    const revenueInstance = ref(null)
    const userGrowthInstance = ref(null)
    const servicesUsageInstance = ref(null)
    const userStatsInstance = ref(null)

    // Export related refs
    const showExportModal = ref(false)
    const exporting = ref(false)
    const showSuccessAlert = ref(false)
    const showErrorAlert = ref(false)
    const alertMessage = ref('')

    const fetchAndRenderCharts = async () => {
      try {
        // Revenue analytics
        const res1 = await AdminService.fetchRevenueAnalytics(timeframe.value)
        const revenueData = res1.data
        // User Growth analytics
        const res2 = await AdminService.fetchUserGrowthAnalytics()
        const growthData = res2.data
        // Services Usage analytics
        const res3 = await AdminService.fetchServicesUsageAnalytics()
        const usageData = res3.data
        // User Stats analytics
        const res4 = await AdminService.fetchUserStatsAnalytics()
        const statsData = res4.data

        // Render revenue chart (line)
        if(revenueInstance.value) revenueInstance.value.destroy()
        revenueInstance.value = new Chart(revenueChart.value, {
          type: 'line',
          data: {
            labels: revenueData.labels,
            datasets: [{
              label: 'Revenue (₹)',
              data: revenueData.data,
              borderColor: '#4CAF50',
              backgroundColor: '#4CAF5020',
              tension: 0.3,
              fill: true
            }]
          },
          options: {
            responsive: true,
            plugins: { title: { display: true, text: `Revenue (${timeframe.value})` } },
            scales: {
              y: {
                beginAtZero: true,
                ticks: { callback: value => '₹' + value }
              }
            }
          }
        })

        // Render user growth chart (bar)
        if(userGrowthInstance.value) userGrowthInstance.value.destroy()
        userGrowthInstance.value = new Chart(userGrowthChart.value, {
          type: 'bar',
          data: {
            labels: growthData.labels,
            datasets: [
              {
                label: 'Customers',
                data: growthData.customerData,
                backgroundColor: '#2196F3'
              },
              {
                label: 'Professionals',
                data: growthData.professionalData,
                backgroundColor: '#FF9800'
              }
            ]
          },
          options: { responsive: true, plugins: { title: { display: true, text: 'User Growth' } } }
        })

        // Render services usage chart (doughnut)
        if(servicesUsageInstance.value) servicesUsageInstance.value.destroy()
        servicesUsageInstance.value = new Chart(servicesUsageChart.value, {
          type: 'doughnut',
          data: {
            labels: usageData.labels,
            datasets: [{
              label: 'Services Usage',
              data: usageData.data,
              backgroundColor: usageData.labels.map(() => '#' + Math.floor(Math.random()*16777215).toString(16))
            }]
          },
          options: { responsive: true, plugins: { title: { display: true, text: 'Services Usage' } } }
        })

        // Render user stats chart (doughnut: distribution of professionals vs customers)
        console.log('statsData loaded from backend:', statsData);
        const totalProfessionals = Number(statsData.total_professionals) || 0;
        const totalCustomers = Number(statsData.total_customers) || 0;
        if(userStatsInstance.value) userStatsInstance.value.destroy();
        userStatsInstance.value = new Chart(userStatsChart.value, {
          type: 'doughnut',
          data: {
            labels: ['Professionals', 'Customers'],
            datasets: [{
              label: 'User Stats',
              data: [totalProfessionals, totalCustomers],
              backgroundColor: ['#9C27B0', '#03A9F4']
            }]
          },
          options: { responsive: true, plugins: { title: { display: true, text: 'User Statistics' } } }
        });

      } catch (error) {
        console.error('Error fetching analytics data:', error)
      }
    }

    // Export services data function
    const exportServicesData = async () => {
      exporting.value = true
      try {
        const response = await AdminService.exportServicesData()
        exporting.value = false
        showExportModal.value = false
        
        // Show success alert
        alertMessage.value = 'CSV data has been exported and sent to the admin email.'
        showSuccessAlert.value = true
        
        // Auto-hide alert after 6 seconds
        setTimeout(() => {
          showSuccessAlert.value = false
        }, 6000)
      } catch (error) {
        exporting.value = false
        showExportModal.value = false
        
        // Show error alert
        alertMessage.value = error.response?.data?.error || 'Failed to export data. Please try again.'
        showErrorAlert.value = true
        
        // Auto-hide alert after 6 seconds
        setTimeout(() => {
          showErrorAlert.value = false
        }, 6000)
      }
    }

    onMounted(fetchAndRenderCharts)
    watch(timeframe, fetchAndRenderCharts)

    return {
      timeframe,
      revenueChart,
      userGrowthChart,
      servicesUsageChart,
      userStatsChart,
      showExportModal,
      exporting,
      exportServicesData,
      showSuccessAlert,
      showErrorAlert,
      alertMessage
    }
  }
}
</script>

<style scoped>
.analytics-container {
  padding: 20px;
}
.card {
  margin-bottom: 20px;
}
/* Modal backdrop and styling */
.modal {
  background-color: rgba(0, 0, 0, 0.5);
}
</style>