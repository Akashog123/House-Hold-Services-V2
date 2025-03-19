<template>
  <div class="book-service">
    <h1 class="text-h4 mb-4">Book a Service</h1>
    
    <div v-if="loading" class="d-flex justify-center align-center" style="min-height: 300px;">
      <v-progress-circular indeterminate color="primary"></v-progress-circular>
    </div>
    
    <div v-else-if="error" class="text-center pa-4">
      <v-alert type="error">{{ error }}</v-alert>
    </div>
    
    <template v-else>
      <v-stepper v-model="currentStep">
        <v-stepper-header>
          <v-stepper-step :complete="currentStep > 1" step="1">
            Select Service
          </v-stepper-step>
          
          <v-divider></v-divider>
          
          <v-stepper-step :complete="currentStep > 2" step="2">
            Additional Information
          </v-stepper-step>
          
          <v-divider></v-divider>
          
          <v-stepper-step step="3">Confirmation</v-stepper-step>
        </v-stepper-header>
        
        <v-stepper-items>
          <!-- Step 1: Select Service -->
          <v-stepper-content step="1">
            <v-card class="mb-4">
              <v-card-title>Select a Service</v-card-title>
              <v-card-text>
                <v-select
                  v-model="bookingForm.serviceId"
                  :items="services"
                  item-text="name"
                  item-value="id"
                  label="Choose a service"
                  :rules="[v => !!v || 'Service is required']"
                  required
                ></v-select>
                
                <div v-if="selectedService" class="mt-4">
                  <h3 class="text-h6">Selected Service Details</h3>
                  <div class="d-flex align-center mt-2">
                    <v-chip color="primary" class="mr-2">
                      <v-icon left>mdi-currency-usd</v-icon>
                      ${{ selectedService.base_price }}
                    </v-chip>
                    <v-chip color="secondary">
                      <v-icon left>mdi-clock-outline</v-icon>
                      {{ selectedService.avg_duration }} mins
                    </v-chip>
                  </div>
                  <p class="mt-2">{{ selectedService.description }}</p>
                </div>
              </v-card-text>
              <v-card-actions>
                <v-btn
                  color="primary"
                  @click="currentStep = 2"
                  :disabled="!bookingForm.serviceId"
                >
                  Continue
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
          
          <!-- Step 2: Additional Information -->
          <v-stepper-content step="2">
            <v-card class="mb-4">
              <v-card-title>Additional Information</v-card-title>
              <v-card-text>
                <v-textarea
                  v-model="bookingForm.notes"
                  label="Notes (optional)"
                  hint="Provide any specific instructions or requirements"
                  rows="4"
                ></v-textarea>
              </v-card-text>
              <v-card-actions>
                <v-btn text @click="currentStep = 1">Back</v-btn>
                <v-spacer></v-spacer>
                <v-btn color="primary" @click="currentStep = 3">Continue</v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
          
          <!-- Step 3: Confirmation -->
          <v-stepper-content step="3">
            <v-card>
              <v-card-title>Confirm Your Booking</v-card-title>
              <v-card-text>
                <div v-if="selectedService">
                  <h3 class="text-h6 mb-2">Service Details</h3>
                  <p><strong>Service:</strong> {{ selectedService.name }}</p>
                  <p><strong>Price:</strong> ${{ selectedService.base_price }}</p>
                  <p><strong>Duration:</strong> {{ selectedService.avg_duration }} mins</p>
                  
                  <v-divider class="my-4"></v-divider>
                  
                  <h3 class="text-h6 mb-2">Your Notes</h3>
                  <p>{{ bookingForm.notes || 'No additional notes provided.' }}</p>
                </div>
              </v-card-text>
              <v-card-actions>
                <v-btn text @click="currentStep = 2">Back</v-btn>
                <v-spacer></v-spacer>
                <v-btn 
                  color="success" 
                  @click="submitBooking"
                  :loading="submitting"
                >
                  Confirm Booking
                </v-btn>
              </v-card-actions>
            </v-card>
          </v-stepper-content>
        </v-stepper-items>
      </v-stepper>
    </template>
    
    <!-- Success Dialog -->
    <v-dialog v-model="showSuccessDialog" max-width="500">
      <v-card>
        <v-card-title class="text-h5 success--text">
          Booking Successful!
        </v-card-title>
        <v-card-text>
          Your service request has been submitted successfully. You can track the status of your request in your dashboard.
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="primary" text @click="goToDashboard">
            Go to Dashboard
          </v-btn>
          <v-btn color="secondary" text @click="goToServices">
            Book Another Service
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import api from '../../services/api.service'

export default {
  name: 'BookService',
  data() {
    return {
      currentStep: 1,
      services: [],
      loading: false,
      error: null,
      submitting: false,
      showSuccessDialog: false,
      bookingForm: {
        serviceId: null,
        notes: ''
      }
    }
  },
  computed: {
    selectedService() {
      if (!this.bookingForm.serviceId) return null
      return this.services.find(service => service.id === this.bookingForm.serviceId)
    }
  },
  methods: {
    async fetchServices() {
      this.loading = true
      this.error = null
      
      try {
        // Only fetch active services for booking
        const response = await api.get('/services', {
          params: { include_inactive: false }
        })
        this.services = response.data
        
        // If serviceId is provided in query params, preselect it
        const serviceId = this.$route.query.serviceId
        if (serviceId) {
          // Verify the service is in the active list
          const selectedService = this.services.find(s => s.id === parseInt(serviceId))
          if (selectedService) {
            this.bookingForm.serviceId = parseInt(serviceId)
          } else {
            // Service might be inactive
            this.error = "The selected service is currently unavailable"
          }
        }
      } catch (err) {
        this.error = 'Failed to load services: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    
    async submitBooking() {
      if (!this.bookingForm.serviceId) {
        this.error = 'Please select a service'
        return
      }
      
      this.submitting = true
      
      try {
        await api.post('/customer/service-requests', {
          service_id: this.bookingForm.serviceId,
          notes: this.bookingForm.notes
        })
        
        // Show success dialog
        this.showSuccessDialog = true
        this.submitting = false
      } catch (err) {
        this.error = 'Failed to submit booking: ' + (err.response?.data?.error || err.message)
        this.submitting = false
      }
    },
    
    goToDashboard() {
      this.$router.push('/dashboard')
    },
    
    goToServices() {
      this.showSuccessDialog = false
      this.currentStep = 1
      this.bookingForm = {
        serviceId: null,
        notes: ''
      }
    }
  },
  created() {
    this.fetchServices()
  }
}
</script>

<style scoped>
.book-service {
  padding: 20px;
}
</style>
