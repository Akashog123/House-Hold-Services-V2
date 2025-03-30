<template>
  <div class="service-detail">
    <div v-if="loading" class="d-flex justify-center align-center" style="min-height: 400px;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <div v-else-if="error" class="text-center pa-4">
      <v-alert type="error">{{ error }}</v-alert>
    </div>
    
    <template v-else-if="service">
      <v-btn icon color="primary" class="mb-4" @click="$router.go(-1)">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      
      <v-card class="mb-6">
        <div class="d-flex flex-wrap">
          <div class="service-image">
            <v-img
              :src="service.image_path || 'https://via.placeholder.com/600x400?text=Service'"
              height="400"
              width="100%"
              cover
            ></v-img>
          </div>
          
          <div class="service-info pa-6">
            <h1 class="text-h3 mb-2">{{ service.name }}</h1>
            
            <div class="d-flex align-center mb-4">
              <v-chip color="primary" class="mr-2">
                <v-icon left>mdi-currency-usd</v-icon>
                ${{ service.base_price }}
              </v-chip>
              
              <v-chip color="secondary">
                <v-icon left>mdi-clock-outline</v-icon>
                {{ service.avg_duration }} mins
              </v-chip>
            </div>
            
            <div class="service-description mb-6">
              <p>{{ service.description }}</p>
            </div>
          </div>
        </div>
      </v-card>
      
      <!-- Available Professionals Section -->
      <v-card class="mb-6">
        <v-card-title>Available Professionals</v-card-title>
        <v-card-text v-if="professionals.length > 0">
          <v-alert v-if="selectedProfessional" type="success" class="mb-4">
            You've selected {{ selectedProfessional.name }} to provide this service
          </v-alert>
          
          <div class="professionals-list">
            <v-row>
              <v-col v-for="pro in professionals" :key="pro.id" cols="12" md="6" lg="4">
                <v-card :class="{'selected-pro': selectedProfessional?.id === pro.id}" @click="selectProfessional(pro)">
                  <div class="d-flex">
                    <v-avatar size="80" class="ma-3">
                      <v-img :src="pro.avatar_url || 'https://via.placeholder.com/80?text=Pro'"></v-img>
                    </v-avatar>
                    <div class="py-3">
                      <div class="text-h6">{{ pro.name }}</div>
                      <div class="d-flex align-center">
                        <v-rating
                          :value="pro.rating"
                          color="amber"
                          dense
                          half-increments
                          readonly
                          size="18"
                        ></v-rating>
                        <span class="ml-1">({{ pro.reviews_count || 0 }})</span>
                      </div>
                      <div class="text-caption">{{ pro.experience || 'Professional' }}</div>
                    </div>
                  </div>
                </v-card>
              </v-col>
            </v-row>
          </div>
          
          <div class="text-center mt-4">
            <v-btn 
              color="primary"
              x-large
              :to="bookingRoute"
              :disabled="!selectedProfessional"
            >
              Book With Selected Professional
            </v-btn>
            <v-btn 
              color="secondary"
              x-large
              class="ml-2"
              :to="`/book-service?serviceId=${service.id}`"
            >
              Book Without Preference
            </v-btn>
          </div>
        </v-card-text>
        <v-card-text v-else class="text-center">
          <p>No professionals are currently available for this service.</p>
          <v-btn 
            color="primary"
            :to="`/book-service?serviceId=${service.id}`"
          >
            Continue With Booking
          </v-btn>
        </v-card-text>
      </v-card>
      
      <!-- Reviews Section -->
      <v-card v-if="reviews && reviews.length > 0" class="mt-6">
        <v-card-title>Customer Reviews</v-card-title>
        <v-card-text>
          <div class="avg-rating mb-4">
            <div class="d-flex align-center">
              <span class="text-h4 mr-2">{{ averageRating }}/5</span>
              <div>
                <v-rating
                  :value="averageRating"
                  color="amber"
                  dense
                  half-increments
                  readonly
                  size="20"
                ></v-rating>
                <div class="text-caption">{{ reviews.length }} reviews</div>
              </div>
            </div>
          </div>
          
          <v-divider></v-divider>
          
          <div v-for="(review, index) in reviews" :key="index" class="review-item py-4">
            <div class="d-flex justify-space-between align-center mb-2">
              <div class="d-flex align-center">
                <v-avatar size="36" class="mr-2">
                  <v-img :src="review.avatar_url || 'https://via.placeholder.com/36?text=User'"></v-img>
                </v-avatar>
                <div>
                  <div class="text-subtitle-1">{{ review.customer_name || 'Customer' }}</div>
                  <div class="text-caption">Professional: {{ review.professional_name }}</div>
                </div>
              </div>
              <div class="text-caption">{{ formatDate(review.created_at) }}</div>
            </div>
            <div>
              <v-rating
                :value="review.rating"
                color="amber"
                dense
                readonly
                size="16"
              ></v-rating>
            </div>
            <p class="mt-1">{{ review.comment || 'No comment provided.' }}</p>
            <v-divider v-if="index < reviews.length - 1"></v-divider>
          </div>
        </v-card-text>
      </v-card>
      
      <v-card v-else class="mt-6">
        <v-card-text class="text-center">
          No reviews yet for this service.
        </v-card-text>
      </v-card>
    </template>
  </div>
</template>

<script>
import api from '../../services/api.service'

export default {
  name: 'ServiceDetail',
  data() {
    return {
      service: null,
      professionals: [],
      selectedProfessional: null,
      reviews: [],
      loading: false,
      error: null
    }
  },
  computed: {
    averageRating() {
      if (!this.reviews || this.reviews.length === 0) return 0
      
      const sum = this.reviews.reduce((total, review) => total + review.rating, 0)
      return (sum / this.reviews.length).toFixed(1)
    },
    bookingRoute() {
      return `/book-service?serviceId=${this.service?.id}&professionalId=${this.selectedProfessional?.id}`
    }
  },
  methods: {
    async fetchServiceDetails() {
      this.loading = true
      this.error = null
      
      try {
        const serviceId = this.$route.params.id
        const response = await api.get(`/services/${serviceId}`)
        this.service = response.data
        
        // Fetch professionals for this service
        await this.fetchServiceProfessionals(serviceId)
        
        // Fetch reviews for this service
        await this.fetchServiceReviews(serviceId)
      } catch (err) {
        this.error = 'Failed to load service details: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    
    async fetchServiceProfessionals(serviceId) {
      try {
        const response = await api.get(`/services/${serviceId}/professionals`)
        this.professionals = response.data
      } catch (err) {
        console.error('Failed to fetch professionals:', err)
        // Not setting an error here as professionals are optional
        this.professionals = []
      }
    },
    
    async fetchServiceReviews(serviceId) {
      try {
        const response = await api.get(`/services/${serviceId}/reviews`)
        this.reviews = response.data
      } catch (err) {
        console.error('Failed to fetch reviews:', err)
        // Not setting an error here as reviews are optional
        this.reviews = []
      }
    },
    
    selectProfessional(professional) {
      if (this.selectedProfessional && this.selectedProfessional.id === professional.id) {
        // Deselect if already selected
        this.selectedProfessional = null
      } else {
        // Select new professional
        this.selectedProfessional = professional
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleDateString()
    }
  },
  created() {
    this.fetchServiceDetails()
  },
  watch: {
    '$route.params.id': {
      handler() {
        this.fetchServiceDetails()
      }
    }
  }
}
</script>

<style scoped>
.service-detail {
  padding: 20px;
}

.service-image {
  flex: 1;
  min-width: 300px;
}

.service-info {
  flex: 1;
  min-width: 300px;
}

@media (min-width: 960px) {
  .service-image {
    flex: 0 0 50%;
  }
  
  .service-info {
    flex: 0 0 50%;
  }
}

.professionals-list {
  margin-top: 20px;
}

.selected-pro {
  border: 2px solid var(--v-primary-base);
  box-shadow: 0 0 10px rgba(var(--v-primary-base), 0.5);
}

.review-item:last-child {
  border-bottom: none;
}

.v-card {
  transition: all 0.3s ease;
}

.v-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 5px 15px rgba(0,0,0,0.1);
  cursor: pointer;
}
</style>
