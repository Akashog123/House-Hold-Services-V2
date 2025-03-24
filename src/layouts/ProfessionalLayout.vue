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
  name: 'ProfessionalLayout',
  components: {
    MainLayout,
  },
  setup() {
    const store = useStore();
    const router = useRouter();

    onMounted(() => {
      // Verify this is a professional user
      const user = store.getters['auth/user'];
      console.log('ProfessionalLayout mounted, checking user role:', user?.role);
      
      if (!user || user.role !== 'professional') {
        console.warn('Non-professional user tried to access professional layout. Redirecting...');
        // If not professional, redirect to appropriate dashboard
        if (user?.role === 'admin') {
          router.push('/admin/dashboard');
        } else if (user?.role === 'customer') {
          router.push('/customer/dashboard');
        } else {
          router.push('/login');
        }
      }
    });

    return {};
  }
};
</script>
