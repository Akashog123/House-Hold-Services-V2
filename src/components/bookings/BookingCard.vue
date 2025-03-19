<template>
  <div class="card mb-3">
    <div class="card-header d-flex justify-content-between align-items-center">
      <h6 class="mb-0">Booking #{{ booking.id }}</h6>
      <span :class="statusBadgeClass">{{ booking.status }}</span>
    </div>
    <div class="card-body">
      <div class="row">
        <div class="col-md-6">
          <p class="mb-1">
            <i class="bi bi-calendar3 me-2"></i>
            {{ formatDate(booking.date) }}
          </p>
          <p class="mb-1">
            <i class="bi bi-clock me-2"></i>
            {{ formatTime(booking.time) }}
          </p>
          <p class="mb-1">
            <i class="bi bi-geo-alt me-2"></i>
            {{ booking.address }}
          </p>
        </div>
        <div class="col-md-6">
          <p class="mb-1">
            <strong>Service:</strong> {{ booking.service.name }}
          </p>
          <p class="mb-1">
            <strong>Price:</strong> ${{ booking.service.price }}
          </p>
          <p class="mb-1" v-if="booking.professional">
            <strong>Professional:</strong> {{ booking.professional.name }}
          </p>
        </div>
      </div>
    </div>
    <div class="card-footer bg-white">
      <div class="d-flex justify-content-end gap-2">
        <button 
          v-if="canCancel"
          @click="$emit('cancel', booking)"
          class="btn btn-outline-danger"
        >
          Cancel
        </button>
        <button 
          v-if="canComplete"
          @click="$emit('complete', booking)"
          class="btn btn-success"
        >
          Mark Complete
        </button>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'BookingCard',
  props: {
    booking: {
      type: Object,
      required: true
    }
  },
  computed: {
    statusBadgeClass() {
      const classes = {
        pending: 'bg-warning',
        confirmed: 'bg-primary',
        completed: 'bg-success',
        cancelled: 'bg-danger'
      };
      return `badge ${classes[this.booking.status.toLowerCase()]}`;
    },
    canCancel() {
      return ['pending', 'confirmed'].includes(this.booking.status.toLowerCase());
    },
    canComplete() {
      return this.booking.status.toLowerCase() === 'confirmed';
    }
  },
  methods: {
    formatDate(date) {
      return new Date(date).toLocaleDateString();
    },
    formatTime(time) {
      return time;
    }
  }
}
</script>