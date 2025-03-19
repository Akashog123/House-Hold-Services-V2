<template>
  <div class="bookings-page">
    <h1 class="text-h4 mb-4">My Bookings</h1>
    
    <!-- Filter Controls -->
    <v-card class="mb-6">
      <v-card-text>
        <v-row>
          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="statusFilter"
              :items="statusOptions"
              label="Filter by Status"
              outlined
              @change="fetchBookings"
            ></v-select>
          </v-col>
          <v-col cols="12" sm="6" md="4">
            <v-select
              v-model="sortBy"
              :items="sortOptions"
              label="Sort by"
              outlined
              @change="fetchBookings"
            ></v-select>
          </v-col>
        </v-row>
      </v-card-text>
    </v-card>
    
    <div v-if="loading" class="d-flex justify-center align-center" style="min-height: 300px;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <div v-else-if="error" class="text-center pa-4">
      <v-alert type="error">{{ error }}</v-alert>
    </div>
    
    <div v-else-if="bookings.length === 0" class="text-center pa-4">
      <v-alert type="info">
        No bookings found matching your criteria.
        <div class="mt-4">
          <v-btn color="primary" to="/services">Browse Services</v-btn>
        </div>
      </v-alert>
    </div>
    
    <template v-else>
      <v-card v-for="booking in bookings" :key="booking.id" class="mb-4">
        <v-card-title>
          <div>
            <div class="text-h6">{{ booking.serviceName }}</div>
            <div class="text-subtitle-2 grey--text">Booking #{{ booking.id }}</div>
          </div>
          <v-spacer></v-spacer>
          <v-chip
            :color="getStatusColor(booking.status)"
            small
            class="text-capitalize"
          >
            {{ booking.status }}
          </v-chip>
        </v-card-title>
        
        <v-card-text>
          <v-row>
            <v-col cols="12" sm="6">
              <div class="mb-2">
                <v-icon small class="mr-1">mdi-calendar</v-icon>
                <span>Date Requested: {{ formatDate(booking.requestDate) }}</span>
              </div>
              <div v-if="booking.completionDate" class="mb-2">
                <v-icon small class="mr-1">mdi-calendar-check</v-icon>
                <span>Date Completed: {{ formatDate(booking.completionDate) }}</span>
              </div>
              <div v-if="booking.professionalName" class="mb-2">
                <v-icon small class="mr-1">mdi-account</v-icon>
                <span>Professional: {{ booking.professionalName }}</span>
              </div>
            </v-col>
            <v-col cols="12" sm="6">
              <div v-if="booking.notes" class="mb-2">
                <strong>Notes:</strong>
                <p class="mt-1">{{ booking.notes }}</p>
              </div>
            </v-col>
          </v-row>
        </v-card-text>
        
        <v-card-actions>
          <v-btn 
            v-if="booking.status === 'pending' || booking.status === 'requested'" 
            color="error" 
            text 
            @click="confirmCancelBooking(booking.id)"
          >
            Cancel Booking
          </v-btn>
          <v-spacer></v-spacer>
          <v-btn 
            v-if="booking.status === 'completed' && !booking.hasReview" 
            color="primary" 
            text 
            @click="openReviewDialog(booking)"
          >
            Leave Review
          </v-btn>
          <v-btn 
            v-if="booking.status === 'completed' && booking.hasReview" 
            color="info" 
            text 
            @click="viewReview(booking.id)"
          >
            View Review
          </v-btn>
          <v-btn 
            :to="`/bookings/${booking.id}`" 
            color="secondary" 
            text
          >
            Details
          </v-btn>
        </v-card-actions>
      </v-card>
      
      <!-- Review Dialog -->
      <v-dialog v-model="showReviewDialog" max-width="500">
        <v-card v-if="selectedBooking">
          <v-card-title>
            Leave a Review for {{ selectedBooking.serviceName }}
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
              Submitted on {{ formatDate(reviewData.createdAt) }}
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
  name: 'BookingsList',
  data() {
    return {
      bookings: [],
      loading: false,
      error: null,
      statusFilter: 'all',
      sortBy: 'date_desc',
      statusOptions: [
        { text: 'All Bookings', value: 'all' },
        { text: 'Pending', value: 'pending' },
        { text: 'Requested', value: 'requested' },
        { text: 'In Progress', value: 'assigned' },
        { text: 'Completed', value: 'completed' },
        { text: 'Cancelled', value: 'cancelled' }
      ],
      sortOptions: [
        { text: 'Date (Newest First)', value: 'date_desc' },
        { text: 'Date (Oldest First)', value: 'date_asc' },
        { text: 'Status', value: 'status' }
      ],
      showReviewDialog: false,
      showViewReviewDialog: false,
      selectedBooking: null,
      reviewData: null,
      submittingReview: false,
      reviewForm: {
        rating: 5,
        comment: ''
      }
    }
  },
  created() {
    // Get filter from URL query params if available
    const { filter } = this.$route.query
    if (filter) {
      this.statusFilter = filter
    }
    
    this.fetchBookings()
  },
  methods: {
    async fetchBookings() {
      this.loading = true
      this.error = null
      
      try {
        const params = {}
        if (this.statusFilter !== 'all') {
          params.status = this.statusFilter
        }
        
        const response = await api.get('/customer/service-requests', { params })
        this.bookings = response.data
        
        // Apply sorting
        this.sortBookings()
      } catch (err) {
        this.error = 'Failed to load bookings: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    
    sortBookings() {
      this.bookings.sort((a, b) => {
        if (this.sortBy === 'date_desc') {
          return new Date(b.requestDate) - new Date(a.requestDate)
        } else if (this.sortBy === 'date_asc') {
          return new Date(a.requestDate) - new Date(b.requestDate)
        } else if (this.sortBy === 'status') {
          const statusOrder = { 'completed': 1, 'assigned': 2, 'requested': 3, 'cancelled': 4 }
          return statusOrder[a.status] - statusOrder[b.status]
        }
        return 0
      })
    },
    
    formatDate(dateStr) {
      if (!dateStr) return 'N/A'
      const date = new Date(dateStr)
      return date.toLocaleDateString()
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
    
    confirmCancelBooking(bookingId) {
      if (confirm('Are you sure you want to cancel this booking?')) {
        this.cancelBooking(bookingId)
      }
    },
    
    async cancelBooking(bookingId) {
      try {
        await api.put(`/customer/service-requests/${bookingId}`, {
          status: 'cancelled'
        })
        
        // Update the booking in the list
        const index = this.bookings.findIndex(b => b.id === bookingId)
        if (index !== -1) {
          this.bookings[index].status = 'cancelled'
        }
      } catch (err) {
        this.error = 'Failed to cancel booking: ' + (err.response?.data?.error || err.message)
      }
    },
    
    openReviewDialog(booking) {
      this.selectedBooking = booking
      this.showReviewDialog = true
      this.reviewForm = {
        rating: 5,
        comment: ''
      }
    },
    
    async submitReview() {
      if (!this.selectedBooking) return
      
      this.submittingReview = true
      
      try {
        await api.post(`/customer/service-requests/${this.selectedBooking.id}/review`, {
          rating: this.reviewForm.rating,
          comment: this.reviewForm.comment
        })
        
        // Update the booking in the list
        const index = this.bookings.findIndex(b => b.id === this.selectedBooking.id)
        if (index !== -1) {
          this.bookings[index].hasReview = true
        }
        
        this.showReviewDialog = false
      } catch (err) {
        this.error = 'Failed to submit review: ' + (err.response?.data?.error || err.message)
      } finally {
        this.submittingReview = false
      }
    },
    
    async viewReview(bookingId) {
      try {
        const response = await api.get(`/customer/service-requests/${bookingId}/review`)
        this.reviewData = response.data
        this.showViewReviewDialog = true
      } catch (err) {
        this.error = 'Failed to load review: ' + (err.response?.data?.error || err.message)
      }
    }
  }
}
</script>

<style scoped>
.bookings-page {
  padding: 20px;
}

h1 {
  margin-bottom: 1.5rem;
}
</style>
