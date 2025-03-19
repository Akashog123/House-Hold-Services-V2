<template>
  <div class="services-page">
    <h1 class="text-h4 mb-4">Our Services</h1>

    <!-- Search and Filter Controls -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="4">
            <v-text-field
              v-model="filters.name"
              label="Search services"
              prepend-icon="mdi-magnify"
              clearable
              @input="applyFilters"
            ></v-text-field>
          </v-col>
          <v-col cols="12" sm="8">
            <v-row>
              <v-col cols="6">
                <v-text-field
                  v-model.number="filters.minPrice"
                  label="Min Price"
                  type="number"
                  prepend-icon="mdi-currency-usd"
                  min="0"
                  @input="applyFilters"
                ></v-text-field>
              </v-col>
              <v-col cols="6">
                <v-text-field
                  v-model.number="filters.maxPrice"
                  label="Max Price"
                  type="number"
                  prepend-icon="mdi-currency-usd"
                  min="0"
                  @input="applyFilters"
                ></v-text-field>
              </v-col>
            </v-row>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>

    <div v-if="loading" class="d-flex justify-center">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <div v-else-if="error" class="text-center pa-4">
      <v-alert type="error">{{ error }}</v-alert>
    </div>
    
    <div v-else-if="filteredServices.length === 0" class="text-center pa-4">
      <v-alert type="info">No services found matching your criteria.</v-alert>
    </div>

    <v-row v-else>
      <v-col v-for="service in filteredServices" :key="service.id" cols="12" sm="6" md="4" lg="3">
        <v-card class="mx-auto h-100 d-flex flex-column" hover>
          <v-img
            :src="service.image || 'https://via.placeholder.com/300x150?text=Service'"
            height="150"
            cover
          ></v-img>
          
          <v-card-title>{{ service.name }}</v-card-title>
          
          <v-card-subtitle>
            <div class="d-flex align-center">
              <v-icon color="amber" small>mdi-currency-usd</v-icon>
              <span class="ml-1">${{ service.base_price }}</span>
              <v-divider vertical class="mx-2"></v-divider>
              <v-icon color="grey" small>mdi-clock-outline</v-icon>
              <span class="ml-1">{{ service.avg_duration }} mins</span>
            </div>
          </v-card-subtitle>
          
          <v-card-text class="flex-grow-1">
            <p>{{ truncateText(service.description, 100) }}</p>
          </v-card-text>
          
          <v-card-actions>
            <v-btn color="primary" :to="`/services/${service.id}`">View Details</v-btn>
            <v-spacer></v-spacer>
            <v-btn color="secondary" :to="`/book-service?serviceId=${service.id}`">Book Now</v-btn>
          </v-card-actions>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import api from '../../services/api.service'

export default {
  name: 'ServicesList',
  data() {
    return {
      services: [],
      loading: false,
      error: null,
      filters: {
        name: '',
        minPrice: null,
        maxPrice: null
      }
    }
  },
  computed: {
    filteredServices() {
      return this.services.filter(service => {
        // Filter by name if provided
        if (this.filters.name && !service.name.toLowerCase().includes(this.filters.name.toLowerCase())) {
          return false
        }
        
        // Filter by min price if provided
        if (this.filters.minPrice !== null && service.base_price < this.filters.minPrice) {
          return false
        }
        
        // Filter by max price if provided
        if (this.filters.maxPrice !== null && service.base_price > this.filters.maxPrice) {
          return false
        }
        
        return true
      })
    }
  },
  methods: {
    async fetchServices() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get('/services', {
          params: this.getQueryParams()
        })
        this.services = response.data
      } catch (err) {
        this.error = 'Failed to load services: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    
    getQueryParams() {
      const params = {}
      
      if (this.filters.name) {
        params.name = this.filters.name
      }
      
      if (this.filters.minPrice) {
        params.min_price = this.filters.minPrice
      }
      
      if (this.filters.maxPrice) {
        params.max_price = this.filters.maxPrice
      }
      
      return params
    },
    
    applyFilters() {
      this.fetchServices()
    },
    
    truncateText(text, length) {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }
  },
  created() {
    this.fetchServices()
  }
}
</script>

<style scoped>
.services-page {
  padding: 20px;
}

h1 {
  margin-bottom: 1.5rem;
}
</style>
