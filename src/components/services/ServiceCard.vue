<template>
  <!-- Only render the component if service has a valid ID -->
  <div v-if="isValidService" class="home-service-card" @mouseenter="hover = true" @mouseleave="hover = false">
    <!-- Only show ribbon if service has required properties and should show ribbon -->
    <div class="card-ribbon" v-if="shouldShowRibbon">Popular</div>
    <div class="card-image-container">
      <img 
        :src="getImageUrl" 
        :alt="service.name || 'Service'" 
        class="card-image"
        @error="handleImageError"
      >
      <div class="card-image-overlay" :class="{ 'show': hover }">
        <button class="btn-book-now" @click="bookService">
          Book Now
        </button>
      </div>
    </div>
    <div class="card-content">
      <div class="service-icon">
        <i :class="getServiceIcon(service.name || '')"></i>
      </div>
      <h3 class="service-title">{{ service.name || 'Unnamed Service' }}</h3>
      <p class="service-description">{{ service.description || 'No description available' }}</p>
      <div class="service-features">
        <div class="feature-item">
          <i class="bi bi-check-circle-fill feature-icon"></i>
          <span>Book easily within seconds.</span>
        </div>
        <div class="feature-item" v-if="service.avg_duration">
          <i class="bi bi-check-circle-fill feature-icon"></i>
          <span>{{ service.avg_duration }} minutes average service duration.</span>
        </div>
        <div class="feature-item">
          <i class="bi bi-check-circle-fill feature-icon"></i>
          <span>Professional Service</span>
        </div>
      </div>
      <div class="service-footer">
        <div class="service-price">₹{{ service.price || service.base_price || 0 }}</div>
        <button class="btn-service-details" @click="findProfessionals">
          Find Professionals<i class="bi bi-arrow-right"></i>
        </button>
      </div>
    </div>
  </div>
  <!-- Render nothing if service is invalid -->
</template>

<script>
export default {
  name: 'ServiceCard',
  props: {
    service: {
      type: Object,
      required: true,
      // Add a default factory function to ensure valid object
      default: () => ({
        id: null,
        name: 'Unnamed Service',
        description: 'No description available',
        base_price: 0,
        avg_duration: 0,
        status: 'active',
        image_path: ''
      })
    }
  },
  emits: ['book-service'],
  data() {
    return {
      hover: false
    }
  },
  computed: {
    isValidService() {
      // Only consider a service valid if it has an ID
      return this.service && this.service.id;
    },
    getImageUrl() {
      // Handle different image properties
      if (!this.service.image_path) return '';
      
      // Check if the path is already a full URL
      if (this.service.image_path.startsWith('http')) {
        return this.service.image_path;
      }
      
      // Otherwise, prepend the API base URL from environment variables
      return `${import.meta.env.VITE_API_URL || ''}${this.service.image_path}`;
    },
    shouldShowRibbon() {
      // Show ribbon for services that are featured or popular
      return this.service.popular || this.service.featured || 
             (this.service.reviews_count && this.service.reviews_count > 2);
    }
  },
  methods: {
    handleImageError(event) {
      // Set a fallback image if the image fails to load
      event.target.src = '/PlaceHolder.jpeg';
    },
    getServiceIcon(serviceName) {
      // Map service names to Bootstrap icons
      const iconMap = {
        'Cleaning': 'bi bi-droplet',
        'Plumbing': 'bi bi-wrench',
        'Electrical': 'bi bi-lightning',
        'Carpentry': 'bi bi-hammer',
        'Gardening': 'bi bi-flower1',
        'Painting': 'bi bi-brush',
        'Appliance Repairing': 'bi bi-tools',
        'Pest Control': 'bi bi-bug'
      };
      
      // Find a matching service name or use a default
      for (const [key, icon] of Object.entries(iconMap)) {
        if (serviceName.toLowerCase().includes(key.toLowerCase())) {
          return icon;
        }
      }
      return 'bi bi-house-gear'; // Default icon
    },
    bookService() {
      if (!this.isValidService) {
        console.error('Cannot book invalid service', this.service);
        return;
      }
      
      // Use named route for more reliable navigation
      this.$router.push({
        name: 'BookService',
        query: { serviceId: this.service.id }
      });
    },
    
    findProfessionals() {
      if (!this.isValidService) {
        console.error('Cannot find professionals for invalid service', this.service);
        return;
      }
      
      // Navigate to booking page to select professionals
      this.$router.push({
        name: 'BookService',
        query: { 
          serviceId: this.service.id,
          showProfessionals: 'true'
        }
      });
    }
  },
  created() {
    // Log to see what service data is being passed
    console.log('ServiceCard created with service:', this.service);
    // Enhanced debugging to help identify the source of invalid service data
    if (!this.isValidService) {
      console.warn('ServiceCard created with invalid service data:', this.service);
      console.warn('Component hierarchy:', this.$parent?.$options?.name);
      console.warn('Route path:', this.$route?.path);
      
      // Log the stack trace to help identify where this component is being used
      console.warn('Component instantiated from:', new Error().stack);
    }
  }
}
</script>

<style scoped>
.home-service-card {
  position: relative;
  overflow: hidden;
  background: white;
  border-radius: 12px;
  box-shadow: 0 6px 16px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  height: 100%;
  width: 100%;
  display: flex;
  flex-direction: column;
}

.home-service-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 12px 24px rgba(0, 0, 0, 0.1);
}

.card-ribbon {
  position: absolute;
  top: 15px;
  right: -30px;
  background: var(--bs-primary);
  color: white;
  padding: 5px 30px;
  transform: rotate(45deg);
  z-index: 10;
  font-size: 0.8rem;
  font-weight: 600;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
}

.card-image-container {
  position: relative;
  height: 180px;
  overflow: hidden;
}

.card-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.4s ease;
}

.home-service-card:hover .card-image {
  transform: scale(1.05);
}

.card-image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.card-image-overlay.show {
  opacity: 1;
}

.btn-book-now {
  background: var(--bs-primary);
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 30px;
  font-weight: 600;
  transition: all 0.2s ease;
  transform: translateY(20px);
  opacity: 0;
}

.home-service-card:hover .btn-book-now {
  transform: translateY(0);
  opacity: 1;
}

.btn-book-now:hover {
  background: #4361ee;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
}

.card-content {
  padding: 20px;
  position: relative;
  flex: 1;
  display: flex;
  flex-direction: column;
}

.service-icon {
  background: rgba(var(--bs-primary-rgb), 0.1);
  color: var(--bs-primary);
  width: 50px;
  height: 50px;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 1.5rem;
  position: absolute;
  top: -25px;
  right: 20px;
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
  border: 3px solid white;
}

.service-title {
  font-size: 1.25rem;
  font-weight: 700;
  margin-bottom: 10px;
  color: #333;
}

.service-description {
  color: #666;
  font-size: 0.9rem;
  margin-bottom: 15px;
  display: -webkit-box;
  line-clamp: 2;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.service-features {
  margin-bottom: 20px;
  flex-grow: 1;
}

.feature-item {
  display: flex;
  align-items: center;
  margin-bottom: 5px;
  font-size: 0.85rem;
}

.feature-icon {
  color: var(--bs-primary);
  margin-right: 8px;
  font-size: 0.8rem;
}

.service-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid #f0f0f0;
  padding-top: 15px;
  margin-top: auto;
}

.service-price {
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--bs-primary);
}

.btn-service-details {
  background: transparent;
  color: var(--bs-primary);
  border: none;
  font-size: 0.9rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  padding: 0;
}

.btn-service-details i {
  margin-left: 5px;
  transition: transform 0.2s ease;
}

.btn-service-details:hover i {
  transform: translateX(5px);
}

/* Media queries for responsive design */
@media (max-width: 767px) {
  .card-image-container {
    height: 160px;
  }
  
  .service-icon {
    width: 40px;
    height: 40px;
    font-size: 1.2rem;
    top: -20px;
  }
}

/* Add a media query for larger screens */
@media (min-width: 1200px) {
  .service-title {
    font-size: 1.4rem;
  }
  
  .service-description {
    font-size: 1rem;
  }
}
</style>
