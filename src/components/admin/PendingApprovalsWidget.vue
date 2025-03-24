<template>
  <div v-if="count > 0" class="approval-widget">
    <div class="card border-warning mb-4">
      <div class="card-body p-3">
        <div class="d-flex justify-content-between align-items-center">
          <div>
            <span class="badge bg-warning fs-6 me-2">{{ count }}</span>
            <span>professional registration{{ count > 1 ? 's' : '' }} pending approval</span>
          </div>
          <router-link :to="{ name: 'AdminApprovals' }" class="btn btn-sm btn-warning">
            Review
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'PendingApprovalsWidget',
  
  props: {
    count: {
      type: Number,
      default: 0
    }
  }
}
</script>

<style scoped>
.approval-widget {
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { opacity: 1; }
  50% { opacity: 0.8; }
  100% { opacity: 1; }
}
</style>
