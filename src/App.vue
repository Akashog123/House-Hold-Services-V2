<template>
  <div id="app">
    <main-layout v-if="!isLoading">
      <router-view />
    </main-layout>
    <div v-else class="loading-screen">
      <div class="spinner-border text-primary" role="status">
        <span class="visually-hidden">Loading...</span>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'
import MainLayout from '@/layouts/MainLayout.vue'

export default {
  name: 'App',
  
  components: {
    MainLayout
  },
  
  setup() {
    const store = useStore()
    // Fix: Use auth/loading instead of isAuthenticated
    const isLoading = computed(() => store.state.auth?.loading || false)
    
    onMounted(() => {
      // Initialize pending approvals count if user is admin
      if (store.getters['auth/isAuthenticated'] && store.getters['auth/user']?.role === 'admin') {
        store.dispatch('users/fetchPendingApprovalCount');
      }
    });

    return {
      isLoading
    }
  }
}
</script>

<style>
.loading-screen {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
}
</style>
