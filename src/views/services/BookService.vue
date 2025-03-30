<template>
  <div class="book-service">
    <!-- Loading State -->
    <div v-if="loading" class="d-flex justify-content-center my-5">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
    
    <!-- Error State -->
    <div v-else-if="error" class="alert alert-danger" role="alert">
      {{ error }}
    </div>
    
    <div v-else class="booking-container">
      <!-- Booking Steps Progress -->
      <div class="booking-progress mb-5">
        <div class="progress">
          <div class="progress-bar" role="progressbar" 
               :style="{ width: `${(currentStep - 1) * 50}%` }" 
               aria-valuenow="0" aria-valuemin="0" aria-valuemax="100"></div>
        </div>
        <div class="booking-steps">
          <div class="booking-step" :class="{ 'active': currentStep >= 1, 'completed': currentStep > 1 }">
            <div class="step-number">1</div>
            <div class="step-label">Service Details</div>
          </div>
          <div class="booking-step" :class="{ 'active': currentStep >= 2, 'completed': currentStep > 2 }">
            <div class="step-number">2</div>
            <div class="step-label">Additional Information</div>
          </div>
          <div class="booking-step" :class="{ 'active': currentStep >= 3 }">
            <div class="step-number">3</div>
            <div class="step-label">Confirmation</div>
          </div>
        </div>
      </div>
      
      <!-- Step 1: Service Details -->
      <div v-if="currentStep === 1" class="card mb-4">
        <div class="card-body">
          <div v-if="selectedService">
            <!-- Service Details -->
            <div class="row">
              <div class="col-12 col-md-6 mb-4">
                <h3 class="section-heading mb-3">
                  <i class="bi bi-info-circle me-2"></i>
                  Service Information
                </h3>
                <div class="service-details p-3 h-100">
                  <h4 class="mb-3">{{ selectedService.name }}</h4>
                  <div class="d-flex gap-2 mb-3">
                    <span class="badge bg-primary">
                      ₹{{ selectedService.base_price }}
                    </span>
                    <span class="badge bg-secondary">
                      <i class="bi bi-clock me-1"></i>
                      {{ selectedService.avg_duration }} minutes
                    </span>
                  </div>
                  <p>{{ selectedService.description }}</p>
                </div>
              </div>
              
              <!-- Professional selection button -->
              <div v-if="professionals.length > 0" class="col-12 col-md-6">
                <h3 class="section-heading mb-3">
                  <i class="bi bi-person-badge me-2"></i>
                  Professional Selection
                </h3>
                
                <div class="d-flex align-items-center">
                  <button 
                    type="button" 
                    class="btn btn-outline-primary"
                    @click="openProfessionalsModal"
                  >
                    <i class="bi bi-people me-2"></i>
                    Select a Professional
                  </button>
                  
                  <div v-if="bookingForm.professionalId" class="selected-pro-badge ms-3">
                    <span class="badge bg-success">
                      Selected: {{ professionals.find(p => p.id === bookingForm.professionalId)?.name || 'No Preference' }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-else class="alert alert-info mt-2">
            No service selected. Please go back and select a service.
          </div>
        </div>
        <div class="card-footer">
          <button 
            class="btn btn-primary"
            @click="currentStep = 2"
            :disabled="!selectedService"
          >
            Continue <i class="bi bi-arrow-right"></i>
          </button>
        </div>
      </div>
      
      <!-- Step 2: Additional Information -->
      <div v-if="currentStep === 2" class="card mb-4">
        <div class="card-body">
          <div class="mb-3">
            <label for="completionDateInput" class="form-label">When do you need this service?</label>
            <div class="date-input-wrapper" @click="$refs.dateInput.showPicker && $refs.dateInput.showPicker()">
              <input 
                id="completionDateInput" 
                type="date" 
                class="form-control" 
                v-model="bookingForm.completionDate"
                required
                :min="minDate"
                ref="dateInput"
              >
            </div>
            <div class="form-text">Select the date when you would like the service to be completed.</div>
          </div>
          
          <div class="mb-3">
            <label for="notesTextarea" class="form-label">Notes</label>
            <textarea 
              id="notesTextarea" 
              class="form-control" 
              v-model="bookingForm.notes"
              placeholder="Add any specific requirements or instructions"
              rows="4"
            ></textarea>
            <div class="form-text">Include any details that might help the service professional.</div>
          </div>
        </div>
        <div class="card-footer d-flex justify-content-between">
          <button type="button" class="btn btn-outline-secondary" @click="currentStep = 1">
            <i class="bi bi-arrow-left me-1"></i> Back
          </button>
          <button type="button" class="btn btn-primary" @click="currentStep = 3">
            Continue <i class="bi bi-arrow-right ms-1"></i>
          </button>
        </div>
      </div>
      
      <!-- Step 3: Confirmation -->
      <div v-if="currentStep === 3" class="card mb-4">
        <div class="card-body">
          <div class="confirmation-details">
            <div class="row">
              <!-- Left Column -->
              <div class="col-12 col-md-6">
                <div class="mb-4">
                  <h6 class="fw-bold mb-2">Selected Service</h6>
                  <p class="mb-0">{{ selectedService ? selectedService.name : 'No service selected' }}</p>
                </div>
                
                <div v-if="bookingForm.professionalId" class="mb-4">
                  <h6 class="fw-bold mb-2">Selected Professional</h6>
                  <p class="mb-0">{{ professionals.find(p => p.id === bookingForm.professionalId)?.name || 'Professional' }}</p>
                </div>
              </div>
              
              <!-- Right Column -->
              <div class="col-12 col-md-6">
                <div class="mb-4">
                  <h6 class="fw-bold mb-2">Requested Date</h6>
                  <p class="mb-0">{{ formatDate(bookingForm.completionDate) }}</p>
                </div>
                
                <div class="mb-4">
                  <h6 class="fw-bold mb-2">Your Notes</h6>
                  <p class="mb-0">{{ bookingForm.notes || 'No additional notes provided.' }}</p>
                </div>
              </div>
            </div>
            
            <hr class="my-4">
          </div>
        </div>
        <div class="card-footer d-flex justify-content-between">
          <button type="button" class="btn btn-outline-secondary" @click="currentStep = 2">
            <i class="bi bi-arrow-left me-1"></i> Back
          </button>
          <button 
            type="button" 
            class="btn btn-success" 
            @click="submitBooking"
            :disabled="submitting"
          >
            <span v-if="submitting">
              <span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span>
              Processing...
            </span>
            <span v-else>
              <i class="bi bi-check2-circle me-1"></i> Confirm Booking
            </span>
          </button>
        </div>
      </div>
    </div>
    
    <!-- Professionals Selection Modal -->
    <div class="modal fade" id="professionalsModal" tabindex="-1" aria-labelledby="professionalsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-lg modal-dialog-scrollable p-5">
        <div class="modal-content">
          <div class="modal-header bg-primary">
            <h5 class="modal-title text-white" id="professionalsModalLabel">Select a Professional</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p class="text-muted small mb-3">Choose from our qualified professionals or select "No preference" to have one assigned automatically.</p>
            
            <div class="professional-cards">
              <div class="pro-cards-grid">
                <!-- Professional cards -->
                <div class="pro-card-item" v-for="pro in professionals" :key="pro.id">
                  <div class="card h-100 professional-card" 
                       :class="{'selected': bookingForm.professionalId === pro.id}"
                       @click="selectProfessional(pro.id)">
                    <div class="card-body">
                      <div class="d-flex">
                        <div class="professional-avatar me-3">
                          <i class="bi bi-person-circle"></i>
                        </div>
                        <div>
                          <h6 class="mb-1">{{ pro.name }}</h6>
                          <div class="d-flex align-items-center mb-1">
                            <div class="stars me-2">
                              <i v-for="i in 5" :key="i" 
                                 :class="['bi', i <= Math.round(pro.rating || 0) ? 'bi-star-fill' : 'bi-star']"></i>
                            </div>
                            <span class="small text-muted">
                              {{ pro.rating || 'New' }} ({{ pro.reviews_count || 0 }} reviews)
                            </span>
                            <button 
                              v-if="pro.reviews_count > 0" 
                              class="btn btn-sm btn-link p-0 ps-2" 
                              @click.stop="viewProfessionalReviews(pro)"
                            >
                              <i class="bi bi-chat-quote"></i> View
                            </button>
                          </div>
                          <div class="small text-muted" v-if="pro.experience_years">
                            <i class="bi bi-briefcase me-1"></i> {{ pro.experience_years }} years experience
                          </div>
                        </div>
                      </div>
                    </div>
                    <div class="selected-indicator">
                      <i class="bi bi-check-circle-fill"></i> Selected
                    </div>
                  </div>
                </div>
                
                <!-- No preference option -->
                <div class="pro-card-item">
                  <div class="card h-100 professional-card no-preference-card"
                      :class="{'selected': bookingForm.professionalId === null}"
                      @click="selectProfessional(null)">
                    <div class="card-body">
                      <div class="d-flex align-items-center">
                        <div class="professional-avatar me-3">
                          <i class="bi bi-shuffle"></i>
                        </div>
                        <div>
                          <h6 class="mb-1">No Preference</h6>
                          <p class="small text-muted mb-0">Let us assign the best available professional for you</p>
                        </div>
                      </div>
                    </div>
                    <div class="selected-indicator">
                      <i class="bi bi-check-circle-fill"></i> Selected
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Success Modal -->
    <div class="modal fade" id="successModal" tabindex="-1" aria-labelledby="successModalLabel" aria-hidden="true">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header bg-success text-white">
            <h5 class="modal-title text-white" id="successModalLabel">Booking Successful!</h5>
            <button type="button" class="btn-close btn-close-white" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>Your service request has been submitted successfully. You can track the status of your request in your dashboard.</p>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-primary" @click="goToDashboard">
              Go to Dashboard
            </button>
            <button type="button" class="btn btn-secondary" @click="goToServices">
              Book Another Service
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Professional Reviews Modal -->
    <div class="modal fade" id="reviewsModal" tabindex="-1" aria-labelledby="reviewsModalLabel" aria-hidden="true">
      <div class="modal-dialog modal-dialog-centered">
        <div class="modal-content">
          <div class="modal-header bg-secondary">
            <h5 class="modal-title text-white" id="reviewsModalLabel">
              Reviews for {{ selectedProfessional ? selectedProfessional.name : 'Professional' }}
            </h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingReviews" class="text-center py-3">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading reviews...</span>
              </div>
            </div>
            
            <div v-else-if="reviewsError" class="alert alert-danger">
              {{ reviewsError }}
            </div>
            
            <div v-else-if="professionalReviews.length === 0" class="text-center py-3">
              <p class="text-muted mb-0">No reviews available for this professional.</p>
            </div>
            
            <div v-else>
              <div class="review-container">
                <div class="review-item" v-for="(review, index) in paginatedReviews" :key="index">
                  <div class="review-header d-flex justify-content-between align-items-center mb-2">
                    <div class="review-rating">
                      <i v-for="star in 5" :key="star" 
                         :class="['bi', star <= review.rating ? 'bi-star-fill' : 'bi-star']"></i>
                    </div>
                    <div class="review-date text-muted small">
                      {{ formatReviewDate(review.created_at) }}
                    </div>
                  </div>
                  <div class="review-content">
                    <p class="mb-1">{{ review.comment || 'No comment provided.' }}</p>
                    <p class="review-author text-muted small mb-0">
                      - {{ review.customer_name || 'Anonymous' }}
                    </p>
                  </div>
                </div>
              </div>
              
              <!-- Pagination -->
              <div class="reviews-pagination d-flex justify-content-between align-items-center mt-3">
                <button 
                  class="btn btn-sm btn-outline-primary" 
                  :disabled="currentReviewPage === 1"
                  @click="currentReviewPage--"
                >
                  <i class="bi bi-chevron-left"></i> Previous
                </button>
                
                <div class="pagination-info">
                  Page {{ currentReviewPage }} of {{ totalReviewPages }}
                </div>
                
                <button 
                  class="btn btn-sm btn-outline-primary" 
                  :disabled="currentReviewPage >= totalReviewPages"
                  @click="currentReviewPage++"
                >
                  Next <i class="bi bi-chevron-right"></i>
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.service';
import bookingService from '@/services/booking.service';
import ServiceService from '@/services/service.service';
import { Modal } from 'bootstrap';

export default {
  data() {
    return {
      currentStep: 1,
      service: null,
      professionals: [],
      loading: false,
      error: null,
      submitting: false,
      successModal: null,
      professionalsModal: null,
      reviewsModal: null,
      bookingForm: {
        serviceId: null,
        professionalId: null,
        completionDate: this.getTomorrowDate(),
        notes: ''
      },
      // Reviews related data
      selectedProfessional: null,
      professionalReviews: [],
      loadingReviews: false,
      reviewsError: null,
      currentReviewPage: 1,
      reviewsPerPage: 3
    };
  },
  computed: {
    selectedService() {
      return this.service;
    },
    minDate() {
      // Set minimum date to today
      const today = new Date();
      return today.toISOString().split('T')[0];
    },
    // Reviews pagination
    paginatedReviews() {
      // Ensure professionalReviews is always an array before calling slice
      if (!Array.isArray(this.professionalReviews)) {
        return [];
      }
      
      const start = (this.currentReviewPage - 1) * this.reviewsPerPage;
      const end = start + this.reviewsPerPage;
      return this.professionalReviews.slice(start, end);
    },
    totalReviewPages() {
      // Ensure professionalReviews is always an array before calculating pages
      if (!Array.isArray(this.professionalReviews)) {
        return 1;
      }
      return Math.ceil(this.professionalReviews.length / this.reviewsPerPage);
    }
  },
  methods: {
    async fetchService() {
      this.loading = true;
      this.error = null;
      
      try {
        // Get serviceId from the URL query parameter
        const serviceId = this.$route.query.serviceId;
        
        if (!serviceId) {
          this.error = "No service selected. Please go back and select a service.";
          return;
        }
        
        // Fetch the specific service by ID
        const response = await ServiceService.getById(parseInt(serviceId));
        
        if (!response.data || !response.data.id) {
          this.error = "The requested service couldn't be found.";
          return;
        }
        
        // Set the service and form data
        this.service = response.data;
        this.bookingForm.serviceId = response.data.id;
        
        // Check if service is active
        if (this.service.status === 'inactive') {
          this.error = "The selected service is currently unavailable.";
          return;
        }
        
        console.log("Service loaded:", this.service);
        
        // Fetch professionals for this service
        await this.fetchProfessionals(this.service.id);
        
        // Set professional if provided in URL
        const professionalId = this.$route.query.professionalId;
        if (professionalId) {
          this.bookingForm.professionalId = parseInt(professionalId);
        }
        
        // Show professionals dialog if requested
        if (this.$route.query.showProfessionals === 'true' && this.professionals.length > 0) {
          setTimeout(() => {
            this.openProfessionalsModal();
          }, 500);
        }
      } catch (err) {
        this.error = 'Failed to load service: ' + (err.response?.data?.error || err.message);
        console.error('Error loading service:', err);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchProfessionals(serviceId) {
      try {
        const result = await ServiceService.getServiceProfessionals(serviceId);
        
        if (!result.data || !Array.isArray(result.data)) {
          console.error('Invalid professionals data format', result.data);
          this.professionals = [];
          return;
        }
        
        this.professionals = result.data.map(pro => ({
          id: pro.id,
          name: pro.username || `Professional #${pro.id}`,
          rating: pro.average_rating || 0,
          reviews_count: pro.total_reviews || 0,
          experience_years: pro.experience_years || 0,
          ...pro
        }));
        
        console.log(`Loaded ${this.professionals.length} professionals for service ${serviceId}`);
      } catch (err) {
        console.error('Failed to load professionals:', err);
        this.professionals = [];
      }
    },
    
    async submitBooking() {
      this.submitting = true;
      this.error = null;
      
      try {
        console.log("Submitting booking with data:", {
          service_id: this.bookingForm.serviceId,
          professional_id: this.bookingForm.professionalId,
          completion_date: this.bookingForm.completionDate,
          notes: this.bookingForm.notes
        });
        
        const result = await bookingService.createBookingWithProfessional({
          service_id: this.bookingForm.serviceId,
          professional_id: this.bookingForm.professionalId || null,
          completion_date: this.bookingForm.completionDate,
          notes: this.bookingForm.notes || '',
          auto_assign: this.bookingForm.professionalId === null
        });
        
        console.log("Booking submission successful:", result);
        
        this.successModal.show();
      } catch (err) {
        this.error = 'Failed to submit booking: ' + (err.response?.data?.error || err.message);
        console.error('Booking submission error:', err);
      } finally {
        this.submitting = false;
      }
    },
    
    goToDashboard() {
      this.successModal.hide();
      this.$router.push('/customer/dashboard');
    },
    
    goToServices() {
      this.successModal.hide();
      this.currentStep = 2;
      this.bookingForm = {
        serviceId: null,
        professionalId: null,
        notes: ''
      };
      this.$router.push('/services');
    },
    
    initModal() {
      const successModalEl = document.getElementById('successModal');
      if (successModalEl) {
        this.successModal = new Modal(successModalEl, {
          backdrop: 'static',
          keyboard: false
        });
      }
      
      const professionalsModalEl = document.getElementById('professionalsModal');
      if (professionalsModalEl) {
        this.professionalsModal = new Modal(professionalsModalEl);
      }
      
      const reviewsModalEl = document.getElementById('reviewsModal');
      if (reviewsModalEl) {
        this.reviewsModal = new Modal(reviewsModalEl);
      }
    },
    
    openProfessionalsModal() {
      if (this.professionalsModal) {
        this.professionalsModal.show();
      }
    },
    
    selectProfessional(professionalId) {
      this.bookingForm.professionalId = professionalId;
    },
    
    async viewProfessionalReviews(professional) {
      this.selectedProfessional = professional;
      this.professionalReviews = [];
      this.loadingReviews = true;
      this.reviewsError = null;
      this.currentReviewPage = 1;
      
      // Show modal first for better UX
      if (this.reviewsModal) {
        this.reviewsModal.show();
      }
      
      try {
        // Fix the API path to ensure it's properly prefixed
        const response = await api.get(`/professionals/${this.selectedProfessional.id}`);
        console.log('Professional reviews response:', response.data);
        
        // Extract the reviews array from the professional object
        if (response.data && response.data.reviews.length > 0) {
          this.professionalReviews = response.data.reviews;
        } else {
          // If reviews is not found or not an array, set to empty array
          this.professionalReviews = [];
          this.reviewsError = 'No reviews available for this professional.';
        }
      } catch (err) {
        console.error('Failed to load reviews:', err);
        this.reviewsError = 'Failed to load reviews: ' + (err.response?.data?.error || err.message);
        this.professionalReviews = [];
      } finally {
        this.loadingReviews = false;
      }
    },
    
    getTomorrowDate() {
      const tomorrow = new Date();
      tomorrow.setDate(tomorrow.getDate() + 1);
      return tomorrow.toISOString().split('T')[0];
    },
    
    formatDate(dateString) {
      if (!dateString) return 'Not specified';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        weekday: 'long', 
        year: 'numeric', 
        month: 'long', 
        day: 'numeric' 
      });
    },
    
    formatReviewDate(dateString) {
      if (!dateString) return 'Unknown date';
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric' 
      });
    }
  },
  mounted() {
    this.initModal();
  },
  created() {
    this.fetchService();
  },
  watch: {
    '$route.query.serviceId': function() {
      this.fetchService();
    }
  }
};
</script>

<style scoped>
.book-service {
  padding: 1.5rem;
  max-width: 1000px;
  margin: 0 auto;
}

.booking-progress {
  position: relative;
  margin-bottom: 2rem;
}

.progress {
  height: 6px;
  background-color: #e9ecef;
  margin-bottom: 2rem;
}

.booking-steps {
  display: flex;
  justify-content: space-between;
  position: absolute;
  top: -10px;
  width: 100%;
}

.booking-step {
  display: flex;
  flex-direction: column;
  align-items: center;
  position: relative;
  width: 33.333%;
}

.step-number {
  width: 30px;
  height: 30px;
  background-color: #dee2e6;
  color: #6c757d;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  margin-bottom: 8px;
  border: 2px solid white;
  transition: all 0.3s ease;
}

.step-label {
  font-size: 0.875rem;
  color: #6c757d;
  text-align: center;
  transition: all 0.3s ease;
}

.booking-step.active .step-number {
  background-color: var(--bs-primary);
  color: white;
}

.booking-step.active .step-label {
  color: var(--bs-primary);
  font-weight: 600;
}

.booking-step.completed .step-number {
  background-color: #28a745;
  color: white;
}

.card {
  border: none;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: white;
  border-bottom: 1px solid rgba(0, 0, 0, 0.05);
  padding: 1rem 1.5rem;
}

.card-footer {
  background-color: white;
  border-top: 1px solid rgba(0, 0, 0, 0.05);
  padding: 1rem 1.5rem;
}

.confirmation-details {
  padding: 0.5rem;
}

.professional-cards {
  margin-bottom: 1.5rem;
}

.professional-card {
  cursor: pointer;
  border: 2px solid transparent;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.professional-card:hover {
  border-color: var(--bs-primary);
  transform: translateY(-3px);
}

.professional-card.selected {
  border-color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.professional-avatar {
  width: 50px;
  height: 50px;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.5rem;
  color: var(--bs-primary);
}

.no-preference-card .professional-avatar {
  background-color: rgba(var(--bs-secondary-rgb), 0.1);
  color: var(--bs-secondary);
}

.stars {
  color: #ffc107;
  font-size: 0.8rem;
}

.selected-indicator {
  position: absolute;
  top: 10px;
  right: 10px;
  background-color: var(--bs-primary);
  color: white;
  padding: 3px 8px;
  font-size: 0.75rem;
  border-radius: 20px;
  opacity: 0;
  transform: translateX(20px);
  transition: all 0.2s ease;
}

.professional-card.selected .selected-indicator {
  opacity: 1;
  transform: translateX(0);
}

.accordion-button::after {
  margin-left: auto;
}

.accordion-button:not(.collapsed) {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
  color: var(--bs-primary);
}

.accordion-button:focus {
  box-shadow: none;
  border-color: rgba(var(--bs-primary-rgb), 0.25);
}

/* Add spacing for the selected badge */
.accordion-button .badge {
  margin-left: auto;
  margin-right: 2rem;
}

@media (max-width: 768px) {
  .step-label {
    font-size: 0.75rem;
  }
  
  .booking-steps {
    top: -12px;
  }
  
  .accordion-button {
    padding: 0.75rem;
  }
  
  .accordion-button .badge {
    margin-right: 1.5rem;
  }
}

/* New styles for direct display sections */
.section-heading {
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--bs-primary);
  display: flex;
  align-items: center;
}

.service-details {
  background-color: #f8f9fa;
  border-radius: 0.5rem;
  border-left: 4px solid var(--bs-primary);
}

.selected-pro-badge {
  font-size: 0.9rem;
}

/* Professional cards in modal */
.pro-cards-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
}

.pro-card-item {
  display: flex;
}

.professional-card {
  flex: 1;
  height: 100%;
  display: flex;
  flex-direction: column;
  margin-bottom: 1rem;
}

.professional-card .card-body {
  flex: 1;
}

/* Ensure modal has good size */
.modal-lg {
  max-width: 800px;
}

/* Reviews Modal Styles */
.review-container {
  max-height: 400px;
}

.review-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
  margin-bottom: 10px;
}

.review-item:last-child {
  border-bottom: none;
}

.review-rating {
  color: #ffc107;
}

.review-content {
  padding: 8px 0;
}

.reviews-pagination {
  border-top: 1px solid #eee;
  padding-top: 15px;
}

.pagination-info {
  font-size: 0.9rem;
  color: #6c757d;
}
</style>
