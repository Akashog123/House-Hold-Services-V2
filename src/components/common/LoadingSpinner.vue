<template>
  <div class="d-flex justify-content-center align-items-center" :style="containerStyle">
    <div class="spinner-border text-primary" role="status">
      <span class="visually-hidden">Loading...</span>
    </div>
  </div>
</template>

<script>
export default {
  name: 'LoadingSpinner',
  props: {
    fullHeight: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    containerStyle() {
      return this.fullHeight ? { height: 'calc(100vh - 200px)' } : { height: '100px' };
    }
  }
}
</script>