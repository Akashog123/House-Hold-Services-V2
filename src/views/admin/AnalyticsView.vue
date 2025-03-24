<template>
  <div class="analytics-container">
    <h3>Analytics Dashboard</h3>

      <!-- Revenue Chart -->
      <div class="card mb-4">
        <div class="card-header d-flex justify-content-between align-items-center">
          <h5 class="mb-0">Revenue Overview</h5>
          <select v-model="revenueTimeframe" class="form-select w-auto">
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="year">Last Year</option>
          </select>
        </div>
        <div class="card-body">
          <canvas ref="revenueChart"></canvas>
        </div>
      </div>

      <!-- User Growth & Service Usage -->
      <div class="row">
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">User Growth</h5>
            </div>
            <div class="card-body">
              <canvas ref="userGrowthChart"></canvas>
            </div>
          </div>
        </div>
        <div class="col-md-6">
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">Popular Services</h5>
            </div>
            <div class="card-body">
              <canvas ref="servicesChart"></canvas>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api.service.js'
import Chart from 'chart.js/auto'

export default {
  name: 'AdminAnalytics',

  setup() {
    const revenueTimeframe = ref('month')
    const revenueChart = ref(null)
    const userGrowthChart = ref(null)
    const servicesChart = ref(null)
    let charts = {}

    const fetchAnalyticsData = async () => {
      try {
        const [revenueData, userGrowthData, servicesData] = await Promise.all([
          api.get(`/admin/analytics/revenue/${revenueTimeframe.value}`),
          api.get('/admin/analytics/user-growth'),
          api.get('/admin/analytics/services-usage')
        ])

        updateCharts(revenueData.data, userGrowthData.data, servicesData.data)
      } catch (error) {
        console.error('Failed to fetch analytics data:', error)
      }
    }

    const updateCharts = (revenue, userGrowth, services) => {
      // Clean up existing charts
      Object.values(charts).forEach(chart => chart.destroy())

      // Revenue Chart
      charts.revenue = new Chart(revenueChart.value, {
        type: 'line',
        data: {
          labels: revenue.labels,
          datasets: [{
            label: 'Revenue',
            data: revenue.data,
            borderColor: '#4CAF50',
            tension: 0.1
          }]
        }
      })

      // User Growth Chart
      charts.userGrowth = new Chart(userGrowthChart.value, {
        type: 'bar',
        data: {
          labels: userGrowth.labels,
          datasets: [{
            label: 'New Users',
            data: userGrowth.data,
            backgroundColor: '#2196F3'
          }]
        }
      })

      // Services Chart
      charts.services = new Chart(servicesChart.value, {
        type: 'doughnut',
        data: {
          labels: services.labels,
          datasets: [{
            data: services.data,
            backgroundColor: [
              '#FF9800',
              '#9C27B0',
              '#E91E63',
              '#F44336',
              '#3F51B5'
            ]
          }]
        }
      })
    }

    onMounted(() => {
      fetchAnalyticsData()
    })

    return {
      revenueTimeframe,
      revenueChart,
      userGrowthChart,
      servicesChart
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

canvas {
  width: 100% !important;
  height: 300px !important;
}
</style>