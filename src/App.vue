<template>
  <div class="app">
    <MainLayout v-if="needsMainLayout">
      <router-view />
    </MainLayout>
    <router-view v-else />
  </div>
</template>

<script>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useStore } from 'vuex';
import MainLayout from './layouts/MainLayout.vue';

export default {
  name: 'App',
  components: {
    MainLayout
  },
  setup() {
    const route = useRoute();
    const store = useStore();
    
    // Determine if we need to wrap the current route in MainLayout
    const needsMainLayout = computed(() => {
      const isAuthenticated = store.getters['auth/isAuthenticated'];
      
      // Public routes that don't need MainLayout
      const publicRoutes = ['/login', '/register', '/registration-success', '/forgot-password', '/reset-password'];
      
      // Don't apply MainLayout to public routes
      if (publicRoutes.some(path => route.path.startsWith(path))) {
        return false;
      }
      
      // Home page is special case - only show MainLayout if authenticated
      if (route.path === '/') {
        return isAuthenticated;
      }
      
      // Apply MainLayout to all other routes
      return true;
    });

    return {
      needsMainLayout
    };
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
