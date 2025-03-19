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
              :src="service.image || 'https://via.placeholder.com/600x400?text=Service'"
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
            
            <v-btn 
              color="primary" 
              x-large 
              block 
              :to="`/book-service?serviceId=${service.id}`"
            >
              Book This Service
            </v-btn>
          </div>
        </div>
      </v-card>
      
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
              <div>
                <v-rating
                  :value="review.rating"
                  color="amber"
                  dense
                  readonly
                  size="16"
                ></v-rating>
              </div>
              <div class="text-caption">{{ formatDate(review.created_at) }}</div>
            </div>
            <p>{{ review.comment || 'No comment provided.' }}</p>
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
        
        // Fetch reviews for this service if available
        await this.fetchServiceReviews(serviceId)
      } catch (err) {
        this.error = 'Failed to load service details: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
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

.review-item:last-child {
  border-bottom: none;
}
</style>
