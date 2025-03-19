<template>
  <div class="card h-100 shadow-sm">
    <img 
      :src="service.image_url || '/default-service.jpg'" 
      class="card-img-top"
      :alt="service.name"
      style="height: 200px; object-fit: cover;"
    >
    <div class="card-body">
      <h5 class="card-title">{{ service.name }}</h5>
      <p class="card-text text-muted">{{ service.description }}</p>
      <div class="d-flex justify-content-between align-items-center">
        <span class="h5 mb-0">${{ service.price }}</span>
        <button 
          class="btn btn-primary"
          @click="$emit('book-service', service)"
        >
          Book Now
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ServiceCard',
  props: {
    service: {
      type: Object,
      required: true
    }
  }
}
</script>
