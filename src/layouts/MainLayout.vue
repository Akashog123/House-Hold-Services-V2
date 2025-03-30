<template>
  <div class="d-flex flex-column min-vh-100">
    <!-- Debug Info (remove in production) -->
    <div v-if="false" class="debug-info p-2 bg-warning">
      Auth: {{ isAuthenticated ? 'Yes' : 'No' }} | 
      Role: {{ userRole || 'None' }} |
      Admin: {{ isAdmin ? 'Yes' : 'No' }} |
      Professional: {{ isProfessional ? 'Yes' : 'No' }} |
      Customer: {{ isCustomer ? 'Yes' : 'No' }}
    </div>
    
    <!-- Header -->
    <app-header 
      @toggle-sidebar="toggleSidebar"
      class="header-fixed"
    />
    
    <!-- Main Content -->
    <main class="main-content">
      <div class="container-fluid h-100">
        <div class="row h-100">
          <!-- Sidebar - only show if authenticated -->
          <nav v-if="isAuthenticated" 
               class="sidebar bg-light"
               :class="{ 'show': isSidebarOpen }">
            <div class="position-sticky">
              <div class="sidebar-header p-3">
                <h5 class="mb-0">{{ sidebarTitle }}</h5>
              </div>
              <hr class="my-0">
              <ul class="nav flex-column p-2">
                <!-- Dashboard -->
                <li class="nav-item">
                  <router-link 
                    :to="dashboardRoute" 
                    class="nav-link d-flex align-items-center"
                    active-class="active"
                  >
                    <i class="bi bi-speedometer2 me-2"></i>
                    Dashboard
                  </router-link>
                </li>

                <!-- Admin Links -->
                <template v-if="isAdmin">
                  <li class="nav-item">
                    <router-link 
                      to="/admin/users" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-people me-2"></i>
                      User Management
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      to="/admin/services" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-grid me-2"></i>
                      Services
                    </router-link>
                  </li>
                                    <li class="nav-item">
                    <router-link 
                      to="/admin/analytics" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-graph-up me-2"></i>
                      Analytics
                    </router-link>
                  </li>
                </template>

                <!-- Professional Links -->
                <template v-if="isProfessional">
                  <li class="nav-item">
                    <router-link 
                      to="/professional/bookings" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-list-check me-2"></i>
                      Service Requests
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      to="/professional/history" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-clock-history me-2"></i>
                      Service History
                    </router-link>
                  </li>
                </template>

                <!-- Customer Links -->
                <template v-if="isCustomer">
                  <li class="nav-item">
                    <router-link 
                      to="/customer/bookings" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-calendar-check me-2"></i>
                      My Bookings
                    </router-link>
                  </li>
                  <li class="nav-item">
                    <router-link 
                      to="/customer/history" 
                      class="nav-link d-flex align-items-center"
                      active-class="active"
                    >
                      <i class="bi bi-clock-history me-2"></i>
                      Service History
                    </router-link>
                  </li>
                </template>
              </ul>
            </div>
          </nav>


          <!-- Content Area -->
          <div :class="contentClasses">
            <div class="content-wrapper">
              <slot />
            </div>
          </div>
        </div>
      </div>
    </main>
    <!-- Add to Desktop Component -->
    <AddToDesktop />
  </div>
</template>

<script>
import { computed, ref, onMounted, watch } from 'vue'
import { useStore } from 'vuex'
import { useRoute } from 'vue-router'
import AppHeader from '@/layouts/Header.vue'
import AddToDesktop from '@/components/common/AddToDesktop.vue'

export default {
  name: 'MainLayout',
  
  components: {
    AppHeader
  },
  
  setup() {
    const store = useStore()
    const route = useRoute()
    const isSidebarOpen = ref(false)

    // Get authentication state from store with enhanced debugging
    const isAuthenticated = computed(() => {
      const token = store.getters['auth/token']
      const authState = store.getters['auth/isAuthenticated']
      console.log('MainLayout - Auth state:', authState, 'Token exists:', !!token)
      return authState
    })
    
    // Get user and role with enhanced debugging
    const userRole = computed(() => {
      const user = store.getters['auth/user']
      console.log('MainLayout - User:', user, 'Token:', !!store.getters['auth/token'])
      return user?.role || null
    })
    
    // Role checks with more verbose logging for all roles
    const isAdmin = computed(() => {
      const user = store.getters['auth/user']
      const isAdminRole = user?.role === 'admin'
      console.log('MainLayout - Is Admin check:', isAdminRole, 'Role:', user?.role)
      return isAdminRole
    })
    
    const isProfessional = computed(() => {
      const role = userRole.value
      const isProfessionalRole = role === 'professional'
      console.log('MainLayout - Is Professional check:', isProfessionalRole, 'Role:', role)
      return isProfessionalRole
    })
    
    const isCustomer = computed(() => {
      const role = userRole.value
      const isCustomerRole = role === 'customer'
      console.log('MainLayout - Is Customer check:', isCustomerRole, 'Role:', role)
      return isCustomerRole
    })

    // Sidebar title based on role
    const sidebarTitle = computed(() => {
      if (isAdmin.value) return 'Admin Panel'
      if (isProfessional.value) return 'Professional Portal'
      if (isCustomer.value) return 'Customer Dashboard'
      return 'Dashboard'
    })

    // Dashboard route based on role
    const dashboardRoute = computed(() => {
      if (isAdmin.value) return '/admin/dashboard'
      if (isProfessional.value) return '/professional/dashboard'
      if (isCustomer.value) return '/customer/dashboard'
      return '/'
    })

    // Routes for common menu items
    const profileRoute = computed(() => {
      if (isAdmin.value) return '/admin/profile'
      if (isProfessional.value) return '/professional/profile'
      if (isCustomer.value) return '/customer/profile'
      return '/profile'
    })

    const settingsRoute = computed(() => {
      if (isAdmin.value) return '/admin/settings'
      if (isProfessional.value) return '/professional/settings'
      if (isCustomer.value) return '/customer/settings'
      return '/settings'
    })

    // Content area classes
    const contentClasses = computed(() => ({
      'col-md-9 col-lg-10 ms-sm-auto': isAuthenticated.value,
      'col-12': !isAuthenticated.value
    }))

    // Sidebar toggle
    const toggleSidebar = () => {
      isSidebarOpen.value = !isSidebarOpen.value
    }

    // Additional check to force auth initialization on component mount
    onMounted(() => {
      console.log('MainLayout mounted, checking auth state')
      // Initial auth check
      const token = localStorage.getItem('auth_token')
      console.log('Token in localStorage:', !!token)
      
      if (token && !isAuthenticated.value) {
        console.log('Token exists in localStorage but auth state is false, initializing auth')
        store.dispatch('auth/initAuth').then(() => {
          // After auth is initialized, force a component update
          console.log('Auth initialized, authenticated:', store.getters['auth/isAuthenticated'])
          console.log('User role after init:', store.getters['auth/user']?.role)
          
          // Force re-evaluation of role computeds
          const role = store.getters['auth/user']?.role
          console.log('User role detected:', role)
          console.log('Is professional:', role === 'professional')
          console.log('Is customer:', role === 'customer')
          console.log('Is admin:', role === 'admin')
        })
      }
    })

    // Watch route changes to check authentication and role
    watch(() => route.path, () => {
      console.log('Route changed to:', route.path)
      console.log('Auth state after route change:', isAuthenticated.value)
      console.log('Role after route change:', userRole.value)
    })

    return {
      isAuthenticated,
      userRole,
      isAdmin,
      isProfessional,
      isCustomer,
      isSidebarOpen,
      sidebarTitle,
      dashboardRoute,
      profileRoute,
      settingsRoute,
      contentClasses,
      toggleSidebar
    }
  }
}
</script>

<style scoped>
.header-fixed {
  position: fixed;
  top: 0;
  right: 0;
  left: 0;
  height: 56px;
  z-index: 1030;
}

.main-content {
  margin-top: 56px;
  min-height: calc(100vh - 56px);
}

.sidebar {
  position: fixed;
  top: 56px;
  bottom: 0;
  left: 0;
  width: 250px;
  z-index: 1020;
  overflow-y: auto;
  transition: transform 0.3s ease;
}

.content-wrapper {
  padding: 1.5rem;
  min-height: calc(100vh - 116px); /* accounting for header and footer */
}

.footer-fixed {
  position: fixed;
  bottom: 0;
  right: 0;
  left: 0;
  height: 60px;
  z-index: 1020;
}

/* Update content classes to account for sidebar */
:deep(.col-md-9),
:deep(.col-lg-10) {
  margin-left: 250px;
  width: calc(100% - 250px);
}

/* Mobile Responsive */
@media (max-width: 767.98px) {
  .sidebar {
    transform: translateX(-100%);
  }

  .sidebar.show {
    transform: translateX(0);
  }

  :deep(.col-md-9),
  :deep(.col-lg-10) {
    margin-left: 0;
    width: 100%;
  }
}

/* Update navigation styles */
.nav-link {
  color: #333;
  padding: 0.75rem 1rem;
  border-radius: 0.25rem;
  transition: all 0.2s ease-in-out;
}

.nav-link:hover {
  background-color: rgba(var(--bs-primary-rgb), 0.05);
  color: var(--bs-primary);
}

.nav-link.active {
  color: var(--bs-primary);
  background-color: rgba(var(--bs-primary-rgb), 0.1);
  font-weight: 500;
}

.nav-link i {
  width: 24px;
  text-align: center;
}

/* Add styles for auth links */
.auth-links {
  display: flex;
  justify-content: center;
  width: 100%;
}

/* Debug info styling */
.debug-info {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 9999;
  font-size: 12px;
  color: #000;
  text-align: center;
}
</style>