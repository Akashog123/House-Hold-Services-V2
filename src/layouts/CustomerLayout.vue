<template>
  <MainLayout>
    <slot></slot>
  </MainLayout>
</template>

<script>
import MainLayout from '@/layouts/MainLayout.vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';
import { onMounted } from 'vue';

export default {
  name: 'CustomerLayout',
  components: {
    MainLayout,
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    onMounted(() => {
      // Verify this is a customer user
      const user = store.getters['auth/user'];
      console.log('CustomerLayout mounted, checking user role:', user?.role);
      
      if (!user || user.role !== 'customer') {
        console.warn('Non-customer user tried to access customer layout. Redirecting...');
        // If not customer, redirect to appropriate dashboard
        if (user?.role === 'admin') {
          router.push('/admin/dashboard');
        } else if (user?.role === 'professional') {
          router.push('/professional/dashboard');
        } else {
          router.push('/login');
        }
      }
    });

    return {};
  }
};
</script>
