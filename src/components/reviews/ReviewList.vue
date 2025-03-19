<template>
  <div class="reviews-container">
    <div v-if="loading" class="text-center py-4">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <div v-else-if="error" class="error-message">{{ error }}</div>
    
    <div v-else-if="reviews.length === 0" class="text-center py-4 grey--text">
      No reviews yet
    </div>
    
    <div v-else>
      <div class="avg-rating mb-4" v-if="showAverageRating">
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
      
      <v-divider v-if="showAverageRating"></v-divider>
      
      <div v-for="(review, index) in reviews" :key="review.id || index" class="review-item py-4">
        <div class="d-flex justify-space-between align-center mb-2">
          <div class="d-flex align-center">
            <v-avatar size="36" color="grey lighten-1" class="mr-2">
              <span class="white--text">{{ getUserInitials(review) }}</span>
            </v-avatar>
            <span class="font-weight-medium">{{ review.user_name || 'Anonymous' }}</span>
          </div>
          <div class="text-caption">{{ formatDate(review.created_at) }}</div>
        </div>
        
        <div class="d-flex align-center mb-2">
          <v-rating
            :value="review.rating"
            color="amber"
            dense
            readonly
            size="16"
          ></v-rating>
          <span class="ml-2 grey--text text--darken-1">{{ review.rating }}/5</span>
        </div>
        
        <p>{{ review.comment || 'No comment provided.' }}</p>
        <v-divider v-if="index < reviews.length - 1" class="mt-4"></v-divider>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ReviewList',
  props: {
    reviews: {
      type: Array,
      default: () => []
    },
    loading: {
      type: Boolean,
      default: false
    },
    error: {
      type: String,
      default: ''
    },
    showAverageRating: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    averageRating() {
      if (!this.reviews || this.reviews.length === 0) return 0;
      const sum = this.reviews.reduce((total, review) => total + review.rating, 0);
      return (sum / this.reviews.length).toFixed(1);
    }
  },
  methods: {
    formatDate(dateStr) {
      if (!dateStr) return 'N/A';
      const date = new Date(dateStr);
      return date.toLocaleDateString();
    },
    getUserInitials(review) {
      const name = review.user_name || 'Anonymous';
      return name.split(' ')
        .map(n => n[0])
        .join('')
        .toUpperCase()
        .substring(0, 2);
    }
  }
}
</script>

<style scoped>
.review-item {
  border-radius: 4px;
  transition: background-color 0.2s;
}

.review-item:hover {
  background-color: rgba(0, 0, 0, 0.02);
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin: 10px 0;
}
</style>
