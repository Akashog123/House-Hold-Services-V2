<template>
  <div 
    class="alert"
    :class="alertClass"
    role="alert"
  >
    <div class="d-flex align-items-center">
      <i :class="iconClass" class="me-2"></i>
      <div>{{ message }}</div>
    </div>
    <button 
      v-if="dismissible"
      type="button" 
      class="btn-close" 
      @click="$emit('dismiss')"
    ></button>
  </div>
</template>

<script>
export default {
  name: 'Alert',
  props: {
    type: {
      type: String,
      default: 'info',
      validator: value => ['success', 'info', 'warning', 'danger'].includes(value)
    },
    message: {
      type: String,
      required: true
    },
    dismissible: {
      type: Boolean,
      default: true
    }
  },
  computed: {
    alertClass() {
      return {
        [`alert-${this.type}`]: true,
        'alert-dismissible': this.dismissible,
        'fade show': true
      };
    },
    iconClass() {
      const icons = {
        success: 'bi bi-check-circle',
        info: 'bi bi-info-circle',
        warning: 'bi bi-exclamation-triangle',
        danger: 'bi bi-x-circle'
      };
      return icons[this.type];
    }
  }
}
</script>