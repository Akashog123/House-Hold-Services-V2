<template>
  <div class="booking-detail">
    <h1 class="text-h4 mb-4">Booking Details</h1>
    
    <div v-if="loading" class="d-flex justify-center align-center" style="min-height: 300px;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <div v-else-if="error" class="text-center pa-4">
      <v-alert type="error">{{ error }}</v-alert>
    </div>
    
    <template v-else-if="booking">
      <v-btn icon color="primary" class="mb-4" @click="$router.go(-1)">
        <v-icon>mdi-arrow-left</v-icon>
      </v-btn>
      
      <v-card class="mb-6">
        <v-card-title class="d-flex justify-space-between">
          <span>Service Request #{{ booking.id }}</span>
          <v-chip
            :color="getStatusColor(booking.status)"
            class="text-capitalize"
          >
            {{ booking.status }}
          </v-chip>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" md="6">
              <h3 class="text-h6 mb-3">Service Information</h3>
              
              <v-list dense>
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-hammer-wrench</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ booking.service_name }}</v-list-item-title>
                    <v-list-item-subtitle>Service Name</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item v-if="booking.service_price">
                  <v-list-item-icon>
                    <v-icon>mdi-currency-usd</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>${{ booking.service_price }}</v-list-item-title>
                    <v-list-item-subtitle>Service Price</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item v-if="booking.service_duration">
                  <v-list-item-icon>
                    <v-icon>mdi-clock-outline</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ booking.service_duration }} minutes</v-list-item-title>
                    <v-list-item-subtitle>Estimated Duration</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              
              <v-divider class="my-4"></v-divider>
              
              <h3 class="text-h6 mb-3">Timeline</h3>
              
              <v-timeline dense>
                <v-timeline-item
                  small
                  color="success"
                >
                  <div class="d-flex justify-space-between">
                    <strong>Requested</strong>
                    <span>{{ formatDate(booking.request_date) }}</span>
                  </div>
                </v-timeline-item>
                
                <v-timeline-item
                  v-if="booking.assignment_date"
                  small
                  color="info"
                >
                  <div class="d-flex justify-space-between">
                    <strong>Assigned</strong>
                    <span>{{ formatDate(booking.assignment_date) }}</span>
                  </div>
                </v-timeline-item>
                
                <v-timeline-item
                  v-if="booking.completion_date"
                  small
                  color="primary"
                >
                  <div class="d-flex justify-space-between">
                    <strong>Completed</strong>
                    <span>{{ formatDate(booking.completion_date) }}</span>
                  </div>
                </v-timeline-item>
                
                <v-timeline-item
                  v-if="booking.cancellation_date"
                  small
                  color="error"
                >
                  <div class="d-flex justify-space-between">
                    <strong>Cancelled</strong>
                    <span>{{ formatDate(booking.cancellation_date) }}</span>
                  </div>
                </v-timeline-item>
              </v-timeline>
            </v-col>
            
            <v-col cols="12" md="6">
              <h3 class="text-h6 mb-3">Professional Information</h3>
              
              <v-list dense v-if="booking.professional_name">
                <v-list-item>
                  <v-list-item-icon>
                    <v-icon>mdi-account</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ booking.professional_name }}</v-list-item-title>
                    <v-list-item-subtitle>Name</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
                
                <v-list-item v-if="booking.professional_phone">
                  <v-list-item-icon>
                    <v-icon>mdi-phone</v-icon>
                  </v-list-item-icon>
                  <v-list-item-content>
                    <v-list-item-title>{{ booking.professional_phone }}</v-list-item-title>
                    <v-list-item-subtitle>Contact Number</v-list-item-subtitle>
                  </v-list-item-content>
                </v-list-item>
              </v-list>
              
              <div v-else class="text-center pa-4 grey--text">
                No professional assigned yet
              </div>
              
              <v-divider class="my-4"></v-divider>
              
              <h3 class="text-h6 mb-3">Notes</h3>
              
              <v-card outlined class="pa-4" v-if="booking.notes">
                <p>{{ booking.notes }}</p>
              </v-card>
              
              <div v-else class="text-center pa-4 grey--text">
                No notes provided
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-divider></v-divider>
        
        <v-card-actions>
          <v-spacer></v-spacer>
          
          <v-btn 
            v-if="booking.status === 'requested' || booking.status === 'assigned'"
            color="error" 
            text 
            @click="confirmCancelBooking"
          >
            <v-icon left>mdi-cancel</v-icon>
            Cancel Booking
          </v-btn>
          
          <v-btn 
            v-if="booking.status === 'completed' && !booking.has_review" 
            color="success" 
            text
            @click="openReviewDialog"
          >
            <v-icon left>mdi-star</v-icon>
            Leave Review
          </v-btn>
          
          <v-btn 
            v-if="booking.status === 'completed' && booking.has_review" 
            color="info" 
            text
            @click="viewReview"
          >
            <v-icon left>mdi-eye</v-icon>
            View Review
          </v-btn>
        </v-card-actions>
      </v-card>
      
      <!-- Review Dialog -->
      <v-dialog v-model="showReviewDialog" max-width="500">
        <v-card>
          <v-card-title>
            Leave a Review for {{ booking.service_name }}
          </v-card-title>
          <v-card-text>
            <v-form ref="reviewForm">
              <v-rating
                v-model="reviewForm.rating"
                color="amber"
                hover
                size="40"
                label="Rate your experience"
              ></v-rating>
              
              <v-textarea
                v-model="reviewForm.comment"
                label="Your comments (optional)"
                rows="4"
              ></v-textarea>
            </v-form>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="showReviewDialog = false">Cancel</v-btn>
            <v-btn 
              color="primary" 
              @click="submitReview"
              :loading="submittingReview"
            >
              Submit Review
            </v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
      
      <!-- View Review Dialog -->
      <v-dialog v-model="showViewReviewDialog" max-width="500">
        <v-card v-if="reviewData">
          <v-card-title>Your Review</v-card-title>
          <v-card-text>
            <div class="mb-4">
              <v-rating
                :value="reviewData.rating"
                color="amber"
                readonly
                size="30"
              ></v-rating>
              <div class="mt-2 text-body-1">{{ reviewData.comment || 'No comment provided.' }}</div>
            </div>
            <div class="grey--text text-caption">
              Submitted on {{ formatDate(reviewData.created_at) }}
            </div>
          </v-card-text>
          <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn text @click="showViewReviewDialog = false">Close</v-btn>
          </v-card-actions>
        </v-card>
      </v-dialog>
    </template>
  </div>
</template>

<script>
import api from '../../services/api.service'

export default {
  name: 'BookingDetail',
  data() {
    return {
      booking: null,
      loading: false,
      error: null,
      showReviewDialog: false,
      showViewReviewDialog: false,
      reviewData: null,
      submittingReview: false,
      reviewForm: {
        rating: 5,
        comment: ''
      }
    }
  },
  created() {
    this.fetchBookingDetails()
  },
  methods: {
    async fetchBookingDetails() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get(`/customer/service-requests/${this.$route.params.id}`)
        this.booking = response.data
      } catch (err) {
        this.error = 'Failed to load booking details: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    },
    
    getStatusColor(status) {
      switch (status.toLowerCase()) {
        case 'completed':
          return 'success'
        case 'assigned':
          return 'primary'
        case 'requested':
        case 'pending':
          return 'warning'
        case 'cancelled':
          return 'error'
        default:
          return 'grey'
      }
    },
    
    confirmCancelBooking() {
      if (confirm('Are you sure you want to cancel this booking?')) {
        this.cancelBooking()
      }
    },
    
    async cancelBooking() {
      try {
        await api.put(`/customer/service-requests/${this.booking.id}`, {
          status: 'cancelled'
        })
        // Update the local booking status
        this.booking.status = 'cancelled'
        // Set the cancellation date
        this.booking.cancellation_date = new Date().toISOString()
      } catch (err) {
        this.error = 'Failed to cancel booking: ' + (err.response?.data?.error || err.message)
      }
    },
    
    openReviewDialog() {
      this.showReviewDialog = true
    },
    
    async submitReview() {
      if (!this.booking) return
      
      this.submittingReview = true
      
      try {
        await api.post(`/customer/service-requests/${this.booking.id}/review`, {
          rating: this.reviewForm.rating,
          comment: this.reviewForm.comment
        })
        
        // Update the booking status to include review
        this.booking.has_review = true
        this.showReviewDialog = false
        
        // Refresh review data to display the new review
        await this.fetchReviewData()
      } catch (err) {
        this.error = 'Failed to submit review: ' + (err.response?.data?.error || err.message)
      } finally {
        this.submittingReview = false
      }
    },
    
    async viewReview() {
      await this.fetchReviewData()
      this.showViewReviewDialog = true
    },
    
    async fetchReviewData() {
      try {
        const response = await api.get(`/customer/service-requests/${this.booking.id}/review`)
        this.reviewData = response.data
      } catch (err) {
        this.error = 'Failed to load review: ' + (err.response?.data?.error || err.message)
      }
    }
  }
}
</script>

<style scoped>
.booking-detail {
  padding: 20px;
}
</style>
