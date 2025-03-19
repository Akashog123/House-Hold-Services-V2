<template>
  <span class="status-badge" :class="status.toLowerCase()">
    {{ formattedStatus }}
  </span>
</template>

<script>
export default {
  name: 'BookingStatusBadge',
  props: {
    status: {
      type: String,
      required: true
    }
  },
  computed: {
    formattedStatus() {
      const statusMap = {
        'requested': 'Requested',
        'assigned': 'In Progress',
        'completed': 'Completed',
        'cancelled': 'Cancelled',
        'pending': 'Pending'
      };
      return statusMap[this.status.toLowerCase()] || this.status;
    }
  }
}
</script>

<style scoped>
.status-badge {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status-badge.requested {
  background-color: #fff3cd;
  color: #856404;
}

.status-badge.assigned {
  background-color: #cce5ff;
  color: #004085;
}

.status-badge.completed {
  background-color: #d4edda;
  color: #155724;
}

.status-badge.cancelled {
  background-color: #f8d7da;
  color: #721c24;
}

.status-badge.pending {
  background-color: #fff3cd;
  color: #856404;
}
</style>
