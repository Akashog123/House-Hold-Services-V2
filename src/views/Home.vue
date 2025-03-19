<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section py-5 bg-primary">
      <div class="container">
        <div class="row align-items-center py-4">
          <div class="col-12 col-md-6">
            <h1 class="display-4 fw-bold text-white mb-4">
              Professional Home Services at Your Fingertips
            </h1>
            <p class="fs-5 text-white mb-4">
              Book trusted professionals for cleaning, repairs, maintenance, and more. Quality service guaranteed.
            </p>
            <div class="d-flex flex-wrap gap-3">
              <router-link 
                to="/register"
                class="btn btn-light btn-lg text-primary"
              >
                Get Started
                <i class="bi bi-arrow-right ms-2"></i>
              </router-link>
              <router-link 
                to="/login"
                class="btn btn-outline-light btn-lg"
              >
                Login
                <i class="bi bi-box-arrow-in-right ms-2"></i>
              </router-link>
              <router-link 
                to="/services"
                class="btn btn-outline-light btn-lg"
              >
                Services
                <i class="bi bi-box-arrow-in-right ms-2"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="services py-5">
      <div class="container">
        <div class="row">
          <div class="col-12 text-center mb-5">
            <h2 class="display-5 fw-bold mb-3">Our Services</h2>
            <p class="fs-5">Professional services for your home</p>
          </div>

          <!-- Loading Skeleton -->
          <template v-if="loading.services">
            <div v-for="n in 3" :key="n" class="col-12 col-md-4 mb-4">
              <div class="card h-100">
                <div class="placeholder-glow">
                  <div class="placeholder w-100" style="height: 200px"></div>
                </div>
                <div class="card-body">
                  <h5 class="card-title placeholder-glow">
                    <span class="placeholder col-6"></span>
                  </h5>
                  <p class="card-text placeholder-glow">
                    <span class="placeholder col-7"></span>
                    <span class="placeholder col-4"></span>
                    <span class="placeholder col-4"></span>
                  </p>
                </div>
              </div>
            </div>
          </template>

          <!-- Error State -->
          <div v-else-if="error.services" class="col-12">
            <div class="alert alert-danger text-center">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ error.services }}
            </div>
          </div>

          <!-- Empty State -->
          <div v-else-if="services.length === 0" class="col-12">
            <div class="text-center py-5">
              <div class="empty-state-icon mb-4">
                <i class="bi bi-clipboard2-x fs-1 text-muted"></i>
              </div>
              <h3 class="fs-4 text-muted">No Services Available</h3>
              <p class="text-muted">Check back later for available services</p>
            </div>
          </div>

          <!-- Actual Services -->
          <template v-else>
            <div v-for="service in services" :key="service.id" class="col-12 col-md-4 mb-4">
              <div class="card h-100">
                <div class="position-relative">
                  <!-- Image with fallback and loading skeleton -->
                  <div v-if="!service.imageLoaded" class="placeholder-glow">
                    <div class="placeholder w-100" style="height: 200px"></div>
                  </div>
                  <img 
                    :src="service.image" 
                    :alt="service.name"
                    class="card-img-top"
                    style="height: 200px; object-fit: cover;"
                    @load="service.imageLoaded = true"
                    @error="handleImageError($event, service)"
                    :class="{ 'd-none': !service.imageLoaded }"
                  >
                </div>
                <div class="card-body">
                  <h5 class="card-title">{{ service.name }}</h5>
                  <p class="card-text">{{ service.description }}</p>
                  <ul class="list-unstyled">
                    <li v-for="(feature, index) in service.features" :key="index">
                      <i class="bi bi-check2-circle text-primary me-2"></i>
                      {{ feature }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </template>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works py-5 bg-light">
      <div class="container">
        <div class="row">
          <div class="col-12 text-center mb-5">
            <h2 class="display-5 fw-bold mb-3">How It Works</h2>
            <p class="fs-5">Simple steps to get your home services</p>
          </div>

          <div 
            v-for="(step, index) in steps" 
            :key="index" 
            class="col-12 col-md-4"
          >
            <div class="text-center p-4">
              <div class="bg-primary rounded-circle d-inline-flex align-items-center justify-content-center mb-4" 
                   style="width: 80px; height: 80px;">
                <i :class="step.icon" class="text-white fs-3"></i>
              </div>
              <h3 class="fs-4 fw-bold mb-3">{{ step.title }}</h3>
              <p>{{ step.description }}</p>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section class="testimonials py-5" v-if="shouldShowTestimonialsSection">
      <div class="container">
        <div class="row">
          <div class="col-12 text-center mb-5">
            <h2 class="display-5 fw-bold mb-3">What Our Customers Say</h2>
            <p class="fs-5">Real feedback from satisfied customers</p>
          </div>

          <!-- Loading Skeleton -->
          <div class="col-12" v-if="loading.testimonials">
            <div class="testimonial-card mx-auto p-4 bg-white shadow-sm rounded-3" style="max-width: 800px;">
              <div class="text-center">
                <div class="placeholder-glow mb-4">
                  <span class="placeholder rounded-circle" style="width: 80px; height: 80px;"></span>
                </div>
                <div class="placeholder-glow mb-4">
                  <span class="placeholder col-4"></span>
                </div>
                <div class="placeholder-glow mb-4">
                  <span class="placeholder col-8"></span>
                  <span class="placeholder col-6"></span>
                  <span class="placeholder col-7"></span>
                </div>
                <div class="placeholder-glow">
                  <span class="placeholder col-4"></span>
                  <span class="placeholder col-3"></span>
                </div>
              </div>
            </div>
          </div>

          <!-- Error State -->
          <div class="col-12" v-else-if="error.testimonials">
            <div class="alert alert-danger text-center">
              <i class="bi bi-exclamation-triangle me-2"></i>
              {{ error.testimonials }}
            </div>
          </div>

          <!-- Empty State -->
          <div class="col-12" v-else-if="testimonials.length === 0">
            <div class="text-center py-5">
              <div class="empty-state-icon mb-4">
                <i class="bi bi-chat-square-quote fs-1 text-muted"></i>
              </div>
              <h3 class="fs-4 text-muted">No Testimonials Yet</h3>
              <p class="text-muted">Be the first to share your experience</p>
            </div>
          </div>

          <!-- Actual Testimonials -->
          <div class="col-12" v-else>
            <div id="testimonialCarousel" class="carousel slide" data-bs-ride="carousel">
              <div class="carousel-inner">
                <div 
                  v-for="(testimonial, index) in testimonials" 
                  :key="testimonial.id"
                  class="carousel-item"
                  :class="{ active: index === 0 }"
                >
                  <div class="testimonial-card mx-auto p-4 bg-white shadow-sm rounded-3" style="max-width: 800px;">
                    <div class="text-center">
                      <!-- Avatar with fallback and loading skeleton -->
                      <div v-if="!testimonial.avatarLoaded" class="placeholder-glow mb-4">
                        <span class="placeholder rounded-circle" style="width: 80px; height: 80px;"></span>
                      </div>
                      <img 
                        :src="testimonial.avatar" 
                        :alt="testimonial.name"
                        class="rounded-circle mb-4"
                        style="width: 80px; height: 80px; object-fit: cover;"
                        @load="testimonial.avatarLoaded = true"
                        @error="handleAvatarError($event, testimonial)"
                        :class="{ 'd-none': !testimonial.avatarLoaded }"
                      >
                      <!-- Rest of the testimonial content -->
                      <div class="mb-4">
                        <div class="text-warning">
                          <i v-for="n in 5" :key="n"
                             class="bi"
                             :class="n <= testimonial.rating ? 'bi-star-fill' : 'bi-star'"
                          ></i>
                        </div>
                      </div>
                      <p class="fst-italic mb-4">
                        "{{ testimonial.content }}"
                      </p>
                      <h4 class="fs-5 fw-bold mb-1">{{ testimonial.name }}</h4>
                      <p class="text-muted">{{ testimonial.location }}</p>
                      <p class="text-primary small">{{ testimonial.service_name }}</p>
                    </div>
                  </div>
                </div>
              </div>
              <button class="carousel-control-prev" type="button" data-bs-target="#testimonialCarousel" data-bs-slide="prev">
                <span class="carousel-control-prev-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Previous</span>
              </button>
              <button class="carousel-control-next" type="button" data-bs-target="#testimonialCarousel" data-bs-slide="next">
                <span class="carousel-control-next-icon" aria-hidden="true"></span>
                <span class="visually-hidden">Next</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- CTA Section -->
    <section class="cta-section py-5 bg-primary">
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-12 col-md-8 text-center">
            <h2 class="display-5 fw-bold text-white mb-4">
              Ready to Transform Your Home?
            </h2>
            <p class="fs-5 text-white mb-4">
              Join thousands of satisfied customers and experience the best in home services.
            </p>
            <div class="d-flex justify-content-center gap-3">
              <router-link
                to="/register"
                class="btn btn-light btn-lg text-primary"
              >
                Get Started Today
                <i class="bi bi-arrow-right ms-2"></i>
              </router-link>
            </div>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script>
import { ref, computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import ServiceService from '@/services/service.service'

export default {
  name: 'Home',

  setup() {
    const store = useStore()
    const services = ref([])
    const testimonials = ref([])
    const loading = ref({
      services: false,
      testimonials: false
    })
    const error = ref({
      services: null,
      testimonials: null
    })

    const handleImageError = (event, service) => {
      event.target.src = require('@/assets/images/services/default.jpg')
      service.imageLoaded = true
    }

    const handleAvatarError = (event, testimonial) => {
      event.target.src = require('@/assets/images/testimonials/default.jpg')
      testimonial.avatarLoaded = true
    }

    const isAuthenticated = computed(() => store.getters.isAuthenticated)
    const userRole = computed(() => store.getters.currentUser?.role)

    const fetchServices = async () => {
      loading.value.services = true
      error.value.services = null
      try {
        const response = await ServiceService.getAll()
        services.value = response.data.map(service => ({
          id: service.id,
          name: service.name,
          description: service.description,
          base_price: service.base_price,
          image: service.image_url || require('@/assets/images/services/default.jpg'),
          imageLoaded: false,
          features: [
            `Starting at $${service.base_price}`,
            `${service.avg_duration} mins avg.`,
            'Professional Service'
          ]
        }))
      } catch (err) {
        error.value.services = 'Failed to load services'
        console.error('Error fetching services:', err)
      } finally {
        loading.value.services = false
      }
    }

    const fetchTestimonials = async () => {
      loading.value.testimonials = true
      error.value.testimonials = null
      try {
        const professionals = await ServiceService.getPopular()
        const reviewPromises = professionals.data
          .slice(0, 3)
          .map(pro => ServiceService.getProfessionalProfile(pro.id))
        
        const reviewsData = await Promise.all(reviewPromises)
        
        testimonials.value = reviewsData
          .flatMap(response => response.data.reviews)
          .filter(review => review.comment)
          .slice(0, 5)
          .map(review => ({
            id: review.id,
            name: review.customer_name || 'Happy Customer',
            location: review.location || 'Verified Customer',
            content: review.comment,
            rating: review.rating,
            avatar: review.avatar_url || require('@/assets/images/testimonials/default.jpg'),
            avatarLoaded: false,
            service_name: review.service_name
          }))
      } catch (err) {
        error.value.testimonials = 'Failed to load testimonials'
        console.error('Error fetching testimonials:', err)
      } finally {
        loading.value.testimonials = false
      }
    }

    onMounted(() => {
      fetchServices()
      fetchTestimonials()
    })

    const steps = [
      {
        icon: 'bi bi-person-plus-fill',
        title: 'Create Account',
        description: 'Sign up in minutes with your basic details and preferences.'
      },
      {
        icon: 'bi bi-calendar-check-fill',
        title: 'Book Service',
        description: 'Choose your service and select a convenient time slot.'
      },
      {
        icon: 'bi bi-house-check-fill',
        title: 'Get Service',
        description: 'Our verified professional will arrive and complete the service.'
      }
    ]

    // New computed property to control testimonials section visibility
    const shouldShowTestimonialsSection = computed(() => {
      return loading.value.testimonials || error.value.testimonials || testimonials.value.length > 0
    })

    return {
      isAuthenticated,
      userRole,
      services,
      steps,
      testimonials,
      loading,
      error,
      handleImageError,
      handleAvatarError,
      shouldShowTestimonialsSection
    }
  }
}
</script>

<style scoped>
.hero-section {
  position: relative;
  overflow: hidden;
}

.testimonial-card {
  transition: transform 0.3s ease;
}

.carousel-control-prev,
.carousel-control-next {
  width: 5%;
}

.carousel-control-prev-icon,
.carousel-control-next-icon {
  background-color: rgba(0, 0, 0, 0.5);
  border-radius: 50%;
  padding: 1.5rem;
}

/* Add styles for placeholder animations */
.placeholder-glow .placeholder {
  animation: placeholder-wave 2s linear infinite;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
}

/* Fade transition for content */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.empty-state-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f8f9fa;
  border-radius: 50%;
}

.empty-state-icon i {
  opacity: 0.5;
}

@media (max-width: 768px) {
  .display-4 {
    font-size: 2.5rem;
  }
  
  .display-5 {
    font-size: 2rem;
  }
  
  .hero-section {
    padding: 2rem 0;
  }
}

/* Responsive adjustments for button group */
@media (max-width: 576px) {
  .gap-3 {
    gap: 0.5rem !important;
  }
  
  .btn-lg {
    padding: 0.5rem 1rem;
    font-size: 1rem;
  }
}
</style>
