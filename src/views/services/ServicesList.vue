<template>
  <div class="services-page">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3>Our Services</h3>
      
      <!-- Filter Toggle Button -->
      <button class="btn btn-primary text-white" type="button" @click="toggleFilters">
        <i class="bi bi-funnel"></i> Filters
      </button>
    </div>

    <!-- Search and Filter Controls -->
    <div class="filter-container mb-4" :class="{ 'filter-open': showFilters }">
      <div class="card">
        <div class="card-body">
          <div class="row g-3">
            <div class="col-12 col-md-3">
              <div class="form-group">
                <label for="searchInput">Service Name</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-search"></i></span>
                  <input 
                    type="text" 
                    id="searchInput"
                    class="form-control" 
                    v-model="filters.name"
                    placeholder="Search services" 
                    @input="applyFilters"
                  >
                </div>
              </div>
            </div>
            
            <div class="col-12 col-md-3">
              <div class="form-group">
                <label for="pincodeInput">Pincode</label>
                <div class="input-group">
                  <span class="input-group-text"><i class="bi bi-geo-alt"></i></span>
                  <input 
                    type="text" 
                    id="pincodeInput"
                    class="form-control" 
                    v-model="filters.pincode"
                    placeholder="Enter pincode" 
                    @input="applyFilters"
                  >
                </div>
              </div>
            </div>
            
            <div class="col-12 col-sm-6 col-md-3">
              <div class="form-group">
                <label for="minPriceInput">Min Price</label>
                <div class="input-group">
                  <span class="input-group-text">₹</span>
                  <input 
                    type="number" 
                    id="minPriceInput"
                    class="form-control" 
                    v-model.number="filters.minPrice"
                    min="0" 
                    placeholder="Min price" 
                    @input="applyFilters"
                  >
                </div>
              </div>
            </div>
            
            <div class="col-12 col-sm-6 col-md-3">
              <div class="form-group">
                <label for="maxPriceInput">Max Price</label>
                <div class="input-group">
                <span class="input-group-text">₹</span>
                <input 
                  type="number" 
                  id="maxPriceInput"
                  class="form-control" 
                  v-model.number="filters.maxPrice"
                  min="0" 
                  placeholder="Max price" 
                  @input="applyFilters"
                >
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-content-center my-5">
      <span class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </span>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger text-center my-4">
      {{ error }}
    </div>
    
    <!-- Empty State -->
    <div v-else-if="filteredServices.length === 0" class="alert alert-info text-center my-4">
      No services found matching your criteria.
    </div>

    <!-- Services List -->
    <div v-else class="row g-4">
      <div v-for="service in filteredServices" :key="service.id" class="col-sm-6 col-md-6 col-lg-4">
        <!-- Only render ServiceCard if service is valid -->
        <ServiceCard 
          v-if="service && service.id" 
          :service="service" 
          @book-service="bookService" 
        />
      </div>
    </div>
  </div>
</template>

<script>
import ServiceCard from '@/components/services/ServiceCard.vue'
import ServiceService from '@/services/service.service.js'
import { useRouter } from 'vue-router'

export default {
  name: 'ServicesList',
  components: {
    ServiceCard
  },
  setup() {
    const router = useRouter()
    
    const bookService = (service) => {
      router.push(`/book-service?serviceId=${service.id}`)
    }
    
    return {
      bookService
    }
  },
  data() {
    return {
      services: [],
      loading: false,
      error: null,
      filters: {
        name: '',
        minPrice: null,
        maxPrice: null,
        pincode: ''
      },
      showFilters: false
    }
  },
  computed: {
    filteredServices() {
      // Only include services with valid IDs in our filtered list
      return this.services
        .filter(service => service && service.id)
        .filter(service => {
          // Filter by name if provided (only if we're not already filtered by name on server)
          if (this.filters.name && !this.filters.pincode && 
              !service.name.toLowerCase().includes(this.filters.name.toLowerCase())) {
            return false
          }
          
          // Filter by min price if provided
          if (this.filters.minPrice !== null && service.base_price < this.filters.minPrice) {
            return false
          }
          
          // Filter by max price only if it's provided and greater than min price
          if (this.filters.maxPrice !== null && 
              this.filters.maxPrice > 0 && 
              (this.filters.minPrice === null || this.filters.maxPrice >= this.filters.minPrice) && 
              service.base_price > this.filters.maxPrice) {
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
        console.log('Fetching services from API...')
        
        let result;
        
        // Use dedicated search endpoint if pincode is provided
        if (this.filters.pincode) {
          console.log(`Searching services with pincode: ${this.filters.pincode}`);
          // Use the services/search endpoint which handles pin_code filtering
          result = await ServiceService.searchServices({
            pin_code: this.filters.pincode,
            name: this.filters.name
          });
        } else {
          // Use regular services endpoint for non-pincode filtering
          const params = {};
          if (this.filters.name) params.name = this.filters.name;
          if (this.filters.minPrice) params.min_price = this.filters.minPrice;
          if (this.filters.maxPrice) params.max_price = this.filters.maxPrice;
          
          result = await ServiceService.getAll(params);
        }
        
        const allServices = result.data || [];
        
        console.log(`Successfully loaded ${allServices.length} services`);
        
        if (allServices.length === 0) {
          this.error = "No services available at the moment";
          return;
        }
        
        // For pincode-filtered results, professionals are already verified by the backend
        if (this.filters.pincode) {
          console.log('Using server-filtered services by pincode:', allServices);
          this.services = allServices;
          
          if (this.services.length === 0) {
            this.error = "No services with available professionals in this area";
          }
        } else {
          // For regular searches, we still need to verify professionals
          const serviceChecks = allServices.map(async (service) => {
            const hasProfessionals = await ServiceService.hasAvailableProfessionals(service.id);
            return { service, hasProfessionals };
          });
          
          // Wait for all checks to complete
          const results = await Promise.all(serviceChecks);
          
          // Filter only services with at least one professional
          this.services = results
            .filter(result => result.hasProfessionals)
            .map(result => result.service);
          
          console.log(`Filtered to ${this.services.length} services with available professionals`);
          
          if (this.services.length === 0) {
            this.error = "No services with available professionals at the moment";
          }
        }
      } catch (err) {
        console.error('Error fetching services:', err)
        this.error = 'Failed to load services: ' + (err.message || 'Unknown error')
        this.services = []
      } finally {
        this.loading = false
      }
    },
    
    applyFilters() {
      // All filter changes should trigger a new fetch
      this.fetchServices();
    },
    
    bookService(service) {
      this.$router.push({
        name: 'BookService',
        query: { serviceId: service.id }
      });
    },
    
    toggleFilters() {
      this.showFilters = !this.showFilters;
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

/* Filter animation styles */
.filter-container {
  max-height: 0;
  overflow: hidden;
  opacity: 0;
  transition: max-height 0.3s ease-out, opacity 0.3s ease, margin 0.3s ease;
  margin-bottom: 0 !important;
}

.filter-container.filter-open {
  max-height: 300px; /* Set a value that's larger than your actual content */
  opacity: 1;
  margin-bottom: 1.5rem !important;
}
</style>
