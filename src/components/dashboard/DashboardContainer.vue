<template>
  <div class="dashboard-container">
    <!-- Dashboard Header -->
    <div class="dashboard-header mb-3">
      <h1 class="h3">{{ title }}</h1>
      <slot name="header-actions"></slot>
    </div>

    <!-- Dashboard Content -->
    <div class="dashboard-content">
      <div class="row g-3">
        <slot></slot>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'DashboardContainer',
  props: {
    title: {
      type: String,
      required: true
    }
  }
}
</script>

<style scoped>
.dashboard-container {
  height: 100%;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-bottom: 1rem;
  border-bottom: 1px solid #dee2e6;
}

.dashboard-content {
  padding-top: 1rem;
}
</style>