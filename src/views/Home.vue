<template>
  <div class="home-page">
    <!-- Hero Section -->
    <section class="hero-section">
      <div class="hero-bg">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
        <div class="shape shape-3"></div>
      </div>
      <div class="container">
        <div class="row align-items-center min-vh-75">
          <div class="col-lg-6 hero-content">
            <h1 class="hero-title">Professional Home Services at Your Fingertips</h1>
            <p class="hero-description">Book trusted professionals for cleaning, repairs, maintenance, and more. Quality service guaranteed.</p>
            <div class="hero-buttons">
              <router-link to="/register" class="btn btn-primary btn-lg">
                Get Started
                <i class="bi bi-arrow-right ms-2"></i>
              </router-link>
              <router-link to="/login" class="btn btn-outline-primary btn-lg">
                Login
                <i class="bi bi-box-arrow-in-right ms-2"></i>
              </router-link>
              <router-link to="/services" class="btn btn-outline-primary btn-lg">
                Services
                <i class="bi bi-grid ms-2"></i>
              </router-link>
            </div>
          </div>
          <div class="col-lg-6 d-none d-lg-block">
            <div class="hero-image">
              <!-- Replace missing SVG with inline SVG or placeholder image -->
              <div class="hero-illustration">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 500 500" width="100%" height="100%">
                  <circle cx="250" cy="250" r="200" fill="#f0f4ff" />
                  <path d="M280,350 L350,280 L380,310 L380,350 Z" fill="#4a6bff" />
                  <rect x="120" y="120" width="200" height="140" rx="10" fill="white" stroke="#4a6bff" stroke-width="4" />
                  <rect x="150" y="160" width="140" height="10" rx="5" fill="#e6e9f4" />
                  <rect x="150" y="190" width="140" height="10" rx="5" fill="#e6e9f4" />
                  <rect x="150" y="220" width="80" height="10" rx="5" fill="#e6e9f4" />
                  <path d="M200,300 L350,300 L350,350 Q350,360 340,360 L210,360 Q200,360 200,350 Z" fill="white" stroke="#4a6bff" stroke-width="4" />
                  <circle cx="220" cy="330" r="15" fill="#4a6bff" />
                  <circle cx="270" cy="330" r="15" fill="#4a6bff" />
                  <circle cx="320" cy="330" r="15" fill="#4a6bff" />
                </svg>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Services Section -->
    <section class="services-section">
      <div class="container">
        <div class="section-header text-center">
          <span class="section-subtitle">What We Offer</span>
          <h2 class="section-title">Our Services</h2>
          <p class="section-description">Professional services for your home needs</p>
        </div>

        <!-- Loading Skeleton -->
        <div v-if="loading.services" class="row g-4">
          <div v-for="n in 6" :key="n" class="col-sm-6 col-md-4 col-lg-3">
            <div class="service-card-skeleton">
              <div class="skeleton-img"></div>
              <div class="skeleton-content">
                <div class="skeleton-title"></div>
                <div class="skeleton-text"></div>
                <div class="skeleton-text short"></div>
                <div class="skeleton-footer">
                  <div class="skeleton-price"></div>
                  <div class="skeleton-button"></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Error State -->
        <div v-else-if="error.services" class="error-container">
          <div class="error-icon">
            <i class="bi bi-exclamation-triangle"></i>
          </div>
          <h3 class="error-title">Oops! Something went wrong</h3>
          <p class="error-message">{{ error.services }}</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="services.length === 0" class="empty-container">
          <div class="empty-icon">
            <i class="bi bi-clipboard2-x"></i>
          </div>
          <h3 class="empty-title">No Services Available</h3>
          <p class="empty-message">Check back later for available services</p>
        </div>

        <!-- Actual Services -->
        <div v-else class="row g-4">
          <div v-for="service in services" :key="service.id" class="col-sm-6 col-md-4 col-lg-3">
            <HomeServiceCard 
              :service="service" 
              @book-service="bookService"
            />
          </div>
        </div>
      </div>
    </section>

    <!-- How It Works -->
    <section class="how-it-works-section">
      <div class="container">
        <div class="section-header text-center">
          <span class="section-subtitle">Simple Process</span>
          <h2 class="section-title">How It Works</h2>
          <p class="section-description">Get your home services in three simple steps</p>
        </div>

        <div class="process-container">
          <div class="row">
            <div v-for="(step, index) in steps" :key="index" class="col-md-4">
              <div class="process-card">
                <div class="process-number">{{ index + 1 }}</div>
                <div class="process-icon">
                  <i :class="step.icon"></i>
                </div>
                <h3 class="process-title">{{ step.title }}</h3>
                <p class="process-description">{{ step.description }}</p>
              </div>
            </div>
          </div>
          <div class="process-line d-none d-md-block"></div>
        </div>
      </div>
    </section>

    <!-- Testimonials Section -->
    <section v-if="shouldShowTestimonialsSection" class="testimonials-section">
      <div class="container">
        <div class="section-header text-center">
          <span class="section-subtitle">Client Feedback</span>
          <h2 class="section-title">What Our Customers Say</h2>
          <p class="section-description">Real feedback from satisfied customers</p>
        </div>

        <!-- Loading Skeleton -->
        <div v-if="loading.testimonials" class="testimonial-skeleton">
          <div class="skeleton-avatar"></div>
          <div class="skeleton-stars"></div>
          <div class="skeleton-text"></div>
          <div class="skeleton-text"></div>
          <div class="skeleton-name"></div>
          <div class="skeleton-location"></div>
        </div>

        <!-- Error State -->
        <div v-else-if="error.testimonials" class="error-container">
          <div class="error-icon">
            <i class="bi bi-exclamation-triangle"></i>
          </div>
          <h3 class="error-title">Oops! Something went wrong</h3>
          <p class="error-message">{{ error.testimonials }}</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="testimonials.length === 0" class="empty-container">
          <div class="empty-icon">
            <i class="bi bi-chat-square-quote"></i>
          </div>
          <h3 class="empty-title">No Testimonials Yet</h3>
          <p class="empty-message">Be the first to share your experience</p>
        </div>

        <!-- Actual Testimonials -->
        <div v-else class="testimonials-slider">
          <div id="testimonialCarousel" class="carousel slide" data-bs-ride="carousel">
            <div class="carousel-indicators">
              <button 
                v-for="(_, index) in testimonials" 
                :key="'indicator-' + index"
                type="button" 
                data-bs-target="#testimonialCarousel" 
                :data-bs-slide-to="index" 
                :class="{ active: index === 0 }" 
                :aria-current="index === 0 ? 'true' : 'false'"
                :aria-label="'Slide ' + (index + 1)"
              ></button>
            </div>
            
            <div class="carousel-inner">
              <div 
                v-for="(testimonial, index) in testimonials" 
                :key="testimonial.id"
                class="carousel-item"
                :class="{ active: index === 0 }"
              >
                <div class="testimonial-card">
                  <div class="testimonial-content">
                    <div class="testimonial-quote">
                      <i class="bi bi-quote"></i>
                    </div>
                    <p class="testimonial-text">{{ testimonial.content }}</p>
                    <div class="testimonial-rating">
                      <i v-for="n in 5" :key="n"
                        class="bi"
                        :class="n <= testimonial.rating ? 'bi-star-fill' : 'bi-star'"
                      ></i>
                    </div>
                  </div>
                  <div class="testimonial-author">
                    <div class="testimonial-avatar">
                      <img 
                        :src="testimonial.avatar" 
                        :alt="testimonial.name"
                        @error="handleAvatarError($event, testimonial)"
                      >
                    </div>
                    <div class="testimonial-info">
                      <h4 class="testimonial-name">{{ testimonial.name }}</h4>
                      <p class="testimonial-location">{{ testimonial.location }}</p>
                      <span class="testimonial-service">{{ testimonial.service_name }}</span>
                    </div>
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
    </section>

    <!-- CTA Section -->
    <section class="cta-section">
      <div class="cta-bg">
        <div class="shape shape-1"></div>
        <div class="shape shape-2"></div>
      </div>
      <div class="container">
        <div class="row justify-content-center">
          <div class="col-lg-8">
            <div class="cta-content text-center">
              <h2 class="cta-title">Ready to Transform Your Home?</h2>
              <p class="cta-description">Join thousands of satisfied customers and experience the best in home services.</p>
              <router-link to="/register" class="btn btn-light btn-lg">
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
import { useRouter } from 'vue-router'
import ServiceService from '@/services/service.service'
import HomeServiceCard from '@/components/services/HomeServiceCard.vue'
import placeholderImage from '/PlaceHolder.jpeg'

export default {
  name: 'Home',
  components: {
    HomeServiceCard
  },

  setup() {
    const store = useStore()
    const router = useRouter()
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
      event.target.src = placeholderImage
      service.imageLoaded = true
    }

    const handleAvatarError = (event, testimonial) => {
      event.target.src = placeholderImage
      testimonial.avatarLoaded = true
    }

    const isAuthenticated = computed(() => store.getters.isAuthenticated)
    const userRole = computed(() => store.getters.currentUser?.role)

    // Add a helper function to get image URLs consistently
    const getImageUrl = (imagePath) => {
      if (!imagePath) return '/PlaceHolder.jpeg';
      
      // Check if the path is already a full URL
      if (imagePath.startsWith('http')) {
        return imagePath;
      }
      
      // Otherwise, prepend the API base URL
      return `${import.meta.env.VITE_API_URL || ''}${imagePath}`;
    };

    const fetchServices = async () => {
      loading.value.services = true
      error.value.services = null
      try {
        const response = await ServiceService.getAll()
        const processedServices = response.data.map(service => ({
          ...service,
          image_path: getImageUrl(service.image_path),
          price: service.price || service.base_price
        }))
        services.value = processedServices.map(service => ({
          id: service.id,
          name: service.name,
          description: service.description,
          base_price: service.base_price,
          image_path: service.image_path,
          imageLoaded: false,
          features: [
            `Starting at ₹${service.base_price}`,
            `${service.avg_duration} minutes average time taken.`,
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
        console.log('Fetched professionals:', professionals.data)
        testimonials.value = professionals.data
          .filter(review => review.comment)
          .map(review => ({
            id: review.id,
            name: review.customer_name || 'Happy Customer',
            location: review.location || 'Verified Customer',
            content: review.comment,
            rating: review.rating,
            avatar: review.avatar_url || placeholderImage,
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

    const truncateText = (text, length) => {
      if (!text) return ''
      return text.length > length ? text.substring(0, length) + '...' : text
    }

    const bookService = (service) => {
      router.push(`/book-service?serviceId=${service.id}`)
    }

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
      shouldShowTestimonialsSection,
      truncateText,
      bookService,
      getImageUrl  // Make the helper available to the template
    }
  }
}
</script>

<style scoped>
/* Base Styles */
.section-header {
  margin-bottom: 3rem;
}

.section-subtitle {
  display: inline-block;
  font-size: 0.875rem;
  text-transform: uppercase;
  letter-spacing: 2px;
  font-weight: 600;
  color: var(--bs-primary);
  margin-bottom: 0.75rem;
}

.section-title {
  font-size: 2.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: #333;
}

.section-description {
  font-size: 1.1rem;
  color: #666;
  max-width: 700px;
  margin: 0 auto;
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 6rem 0;
  overflow: hidden;
  background-color: #f8f9fa;
}

.hero-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.shape {
  position: absolute;
  border-radius: 50%;
  opacity: 0.1;
}

.hero-section .shape-1 {
  width: 300px;
  height: 300px;
  background: var(--bs-primary);
  top: -100px;
  right: -100px;
}

.hero-section .shape-2 {
  width: 200px;
  height: 200px;
  background: var(--bs-info);
  top: 50%;
  left: -100px;
}

.hero-section .shape-3 {
  width: 150px;
  height: 150px;
  background: var(--bs-success);
  bottom: -50px;
  right: 20%;
}

.min-vh-75 {
  min-height: 75vh;
}

.hero-content {
  position: relative;
  z-index: 1;
}

.hero-title {
  font-size: 3.5rem;
  font-weight: 800;
  line-height: 1.2;
  margin-bottom: 1.5rem;
  color: #333;
}

.hero-description {
  font-size: 1.25rem;
  color: #555;
  margin-bottom: 2rem;
  max-width: 600px;
}

.hero-buttons {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.hero-buttons .btn {
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
}

.hero-buttons .btn-primary {
  background: linear-gradient(135deg, var(--bs-primary), #4a6bff);
  border: none;
}

.hero-buttons .btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
  color: white;
}

.hero-buttons .btn-outline-primary {
  color: var(--bs-primary);
  border-color: var(--bs-primary);
  background: transparent;
}

.hero-buttons .btn-outline-primary:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
}

.hero-image {
  position: relative;
  z-index: 1;
  text-align: center;
}

.hero-image img {
  max-width: 90%;
  animation: float 6s ease-in-out infinite;
}

.hero-illustration {
  max-width: 500px;
  margin: 0 auto;
  animation: float 6s ease-in-out infinite;
}

@keyframes float {
  0% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-15px);
  }
  100% {
    transform: translateY(0px);
  }
}

/* Services Section */
.services-section {
  padding: 6rem 0;
  background-color: #fff;
}

.service-card-skeleton {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  height: 100%;
}

.skeleton-img {
  height: 180px;
  background: #eee;
  border-radius: 12px 12px 0 0;
  position: relative;
  overflow: hidden;
}

.skeleton-img::after,
.skeleton-title::after,
.skeleton-text::after,
.skeleton-price::after,
.skeleton-button::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  animation: shimmer 1.5s infinite;
}

@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.skeleton-content {
  padding: 1.5rem;
}

.skeleton-title {
  height: 20px;
  background: #eee;
  margin-bottom: 1rem;
  position: relative;
  overflow: hidden;
  width: 70%;
  border-radius: 4px;
}

.skeleton-text {
  height: 14px;
  background: #eee;
  margin-bottom: 8px;
  position: relative;
  overflow: hidden;
  border-radius: 4px;
}

.skeleton-text.short {
  width: 60%;
}

.skeleton-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 1rem;
}

.skeleton-price {
  height: 16px;
  width: 60px;
  background: #eee;
  position: relative;
  overflow: hidden;
  border-radius: 4px;
}

.skeleton-button {
  height: 36px;
  width: 80px;
  background: #eee;
  position: relative;
  overflow: hidden;
  border-radius: 6px;
}

/* Error and Empty States */
.error-container,
.empty-container {
  text-align: center;
  padding: 4rem 1rem;
  max-width: 600px;
  margin: 0 auto;
}

.error-icon,
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1.5rem;
  display: inline-block;
  width: 100px;
  height: 100px;
  line-height: 100px;
  border-radius: 50%;
}

.error-icon {
  color: var(--bs-danger);
  background-color: rgba(var(--bs-danger-rgb), 0.1);
}

.empty-icon {
  color: var(--bs-secondary);
  background-color: rgba(var(--bs-secondary-rgb), 0.1);
}

.error-title,
.empty-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.error-message,
.empty-message {
  color: #666;
}

/* How It Works Section */
.how-it-works-section {
  padding: 6rem 0;
  background-color: #f8f9fa;
  position: relative;
}

.process-container {
  position: relative;
  padding: 3rem 0 1rem;
}

.process-line {
  position: absolute;
  top: 100px;
  left: 20%;
  right: 20%;
  height: 3px;
  background: linear-gradient(90deg, var(--bs-primary), var(--bs-info));
  z-index: 1;
}

.process-card {
  position: relative;
  z-index: 2;
  background: #fff;
  border-radius: 12px;
  padding: 2rem;
  text-align: center;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 100%;
}

.process-card:hover {
  transform: translateY(-10px);
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.1);
}

.process-number {
  position: absolute;
  top: -20px;
  left: 50%;
  transform: translateX(-50%);
  width: 40px;
  height: 40px;
  background: var(--bs-primary);
  color: #fff;
  font-weight: 700;
  border-radius: 50%;
  line-height: 40px;
  font-size: 1.25rem;
}

.process-icon {
  font-size: 2.5rem;
  color: var(--bs-primary);
  margin-bottom: 1.5rem;
  height: 100px;
  width: 100px;
  line-height: 100px;
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  border-radius: 50%;
  margin: 0 auto 1.5rem;
}

.process-title {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 1rem;
}

.process-description {
  color: #666;
}

/* Testimonials Section */
.testimonials-section {
  padding: 6rem 0;
  background-color: #fff;
}

.testimonial-skeleton {
  max-width: 700px;
  margin: 0 auto;
  padding: 2rem;
  border-radius: 12px;
  background: #fff;
  box-shadow: 0 6px 15px rgba(0, 0, 0, 0.05);
  text-align: center;
}

.skeleton-avatar {
  width: 80px;
  height: 80px;
  background: #eee;
  border-radius: 50%;
  margin: 0 auto 1rem;
  position: relative;
  overflow: hidden;
}

.skeleton-avatar::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  animation: shimmer 1.5s infinite;
}

.skeleton-stars {
  height: 20px;
  width: 120px;
  background: #eee;
  margin: 0 auto 1.5rem;
  position: relative;
  overflow: hidden;
  border-radius: 4px;
}

.skeleton-stars::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
  animation: shimmer 1.5s infinite;
}

.testimonials-slider {
  max-width: 800px;
  margin: 0 auto;
}

.testimonial-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.05);
  overflow: hidden;
  padding: 2rem;
  margin: 1rem;
}

.testimonial-content {
  text-align: center;
  margin-bottom: 2rem;
}

.testimonial-quote {
  font-size: 2rem;
  color: rgba(var(--bs-primary-rgb), 0.2);
  margin-bottom: 1rem;
}

.testimonial-text {
  font-size: 1.1rem;
  color: #555;
  font-style: italic;
  margin-bottom: 1.5rem;
}

.testimonial-rating {
  color: #ffc107;
  font-size: 1.2rem;
}

.testimonial-author {
  display: flex;
  align-items: center;
  justify-content: center;
}

.testimonial-avatar {
  width: 70px;
  height: 70px;
  border-radius: 50%;
  overflow: hidden;
  margin-right: 1rem;
  border: 3px solid rgba(var(--bs-primary-rgb), 0.2);
}

.testimonial-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.testimonial-info {
  text-align: left;
}

.testimonial-name {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 0.25rem;
}

.testimonial-location {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 0.25rem;
}

.testimonial-service {
  color: var(--bs-primary);
  font-size: 0.85rem;
  font-weight: 600;
}

.carousel-indicators {
  bottom: -40px;
}

.carousel-indicators button {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin: 0 5px;
  background-color: rgba(var(--bs-primary-rgb), 0.3);
}

.carousel-indicators button.active {
  background-color: var(--bs-primary);
}

.carousel-control-prev,
.carousel-control-next {
  width: 40px;
  height: 40px;
  background-color: var(--bs-primary);
  border-radius: 50%;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.7;
}

.carousel-control-prev {
  left: -20px;
}

.carousel-control-next {
  right: -20px;
}

.carousel-control-prev:hover,
.carousel-control-next:hover {
  opacity: 1;
}

/* CTA Section */
.cta-section {
  padding: 6rem 0;
  background: linear-gradient(135deg, var(--bs-primary), #4a6bff);
  position: relative;
  overflow: hidden;
}

.cta-bg {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 0;
}

.cta-section .shape-1 {
  width: 300px;
  height: 300px;
  background: rgba(255, 255, 255, 0.1);
  top: -100px;
  right: -100px;
}

.cta-section .shape-2 {
  width: 200px;
  height: 200px;
  background: rgba(255, 255, 255, 0.1);
  bottom: -100px;
  left: -50px;
}

.cta-content {
  position: relative;
  z-index: 1;
}

.cta-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 1rem;
}

.cta-description {
  color: rgba(255, 255, 255, 0.9);
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.cta-section .btn {
  padding: 0.75rem 1.5rem;
  font-weight: 600;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.cta-section .btn:hover {
  transform: translateY(-3px);
  box-shadow: 0 8px 15px rgba(0, 0, 0, 0.1);
}

/* Responsive */
@media (max-width: 991px) {
  .hero-title {
    font-size: 2.5rem;
  }
  
  .section-title {
    font-size: 2rem;
  }
  
  .process-line {
    display: none;
  }
  
  .process-card {
    margin-bottom: 2rem;
  }
}

@media (max-width: 767px) {
  .hero-section,
  .services-section,
  .how-it-works-section,
  .testimonials-section,
  .cta-section {
    padding: 4rem 0;
  }
  
  .hero-buttons {
    flex-direction: column;
    width: 100%;
  }
  
  .hero-buttons .btn {
    width: 100%;
  }
  
  .carousel-control-prev,
  .carousel-control-next {
    display: none;
  }
  
  .process-card {
    padding: 1.5rem;
  }
}

@media (max-width: 576px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-description {
    font-size: 1rem;
  }
  
  .section-title {
    font-size: 1.75rem;
  }
  
  .section-description {
    font-size: 1rem;
  }
  
  .cta-title {
    font-size: 1.75rem;
  }
}
</style>
