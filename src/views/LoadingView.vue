<template>
  <div class="loading-container">
    <v-progress-circular
      indeterminate
      color="primary"
      size="64"
    ></v-progress-circular>
    <div class="mt-4">Redirecting...</div>
  </div>
</template>

<script>
export default {
  name: 'LoadingView'
}
</script>

<style scoped>
.loading-container {
  height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}
</style>