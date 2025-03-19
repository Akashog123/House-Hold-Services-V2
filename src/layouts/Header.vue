<template>
  <header class="navbar navbar-dark bg-primary shadow-sm">
    <div class="container-fluid">
      <!-- Left side - Brand and Toggle -->
      <div class="d-flex align-items-center">
        <button 
          v-if="isAuthenticated"
          class="btn btn-link text-white me-3 d-md-none" 
          @click="$emit('toggle-sidebar')"
        >
          <i class="bi bi-list fs-4"></i>
        </button>
        <router-link to="/" class="navbar-brand d-flex align-items-center me-auto">
          <img src="@/assets/logo.png" alt="Logo" class="logo me-2">
          <span class="fw-bold">HouseCare</span>
        </router-link>
      </div>
      
      <!-- Right side - Auth or User Menu -->
      <div class="d-flex">
                <!-- Show these only for authenticated users -->
        <div class="dropdown" v-if="isAuthenticated" ref="userDropdownRef">
          <button 
            class="btn btn-primary dropdown-toggle d-flex align-items-center"
            type="button" 
            id="userDropdown"
            data-bs-toggle="dropdown"
            aria-expanded="false"
          >
            <span class="me-2 d-none d-sm-inline">{{ username }}</span>
            <i class="bi bi-person-circle fs-5"></i>
          </button>
          <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="userDropdown">
            <li>
              <router-link class="dropdown-item" :to="profileLink">
                <i class="bi bi-person me-2"></i> Profile
              </router-link>
            </li>
            <li>
              <router-link class="dropdown-item" :to="settingsLink">
                <i class="bi bi-gear me-2"></i> Settings
              </router-link>
            </li>
            <li><hr class="dropdown-divider"></li>
            <li>
              <a class="dropdown-item" href="#" @click.prevent="logout">
                <i class="bi bi-box-arrow-right me-2"></i> Logout
              </a>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </header>
</template>

<script>
import { computed, ref, onMounted, onUnmounted } from 'vue'
import { useStore } from 'vuex'
import { useRouter } from 'vue-router'
import authService from '@/services/auth.service'
import { Dropdown } from 'bootstrap'

export default {
  name: 'AppHeader',
  
  emits: ['toggle-sidebar'],
  
  setup() {
    const store = useStore()
    const router = useRouter()
    const userDropdownRef = ref(null)
    let dropdownInstance = null

    // Check if user is authenticated
    const isAuthenticated = computed(() => {
      const authState = store.getters['auth/isAuthenticated']
      console.log('Header - Auth state:', authState)
      return authState
    })

    // Get the username
    const username = computed(() => {
      const user = store.getters['auth/user']
      return user ? (user.username || user.email || 'User') : 'User'
    })

    // Get user role
    const userRole = computed(() => {
      const user = store.getters['auth/user']
      console.log('Header - User role:', user?.role)
      return user?.role || null
    })

    // Determine profile and settings links based on role
    const profileLink = computed(() => {
      switch (userRole.value) {
        case 'admin': return '/admin/profile'
        case 'professional': return '/professional/profile'
        case 'customer': return '/customer/profile'
        default: return '/profile'
      }
    })

    const settingsLink = computed(() => {
      switch (userRole.value) {
        case 'admin': return '/admin/settings'
        case 'professional': return '/professional/settings'
        case 'customer': return '/customer/settings'
        default: return '/settings'
      }
    })

    // Logout function
    const logout = async () => {
      try {
        console.log('Logging out...')
        await authService.logout()
        console.log('Logged out successfully')
        router.push('/login')
      } catch (error) {
        console.error('Logout error:', error)
      }
    }

    // Initialize dropdown when component is mounted
    onMounted(() => {
      if (userDropdownRef.value) {
        console.log("Initializing Bootstrap dropdown")
        const dropdownBtn = userDropdownRef.value.querySelector('[data-bs-toggle="dropdown"]')
        if (dropdownBtn) {
          dropdownInstance = new Dropdown(dropdownBtn)
        }
      }
    })

    // Clean up when component is unmounted
    onUnmounted(() => {
      if (dropdownInstance) {
        // No dispose method in Bootstrap 5, the garbage collector handles it
        dropdownInstance = null
      }
    })

    return {
      isAuthenticated,
      username,
      userRole,
      profileLink,
      settingsLink,
      logout,
      userDropdownRef
    }
  }
}
</script>

<style scoped>
.logo {
  height: 30px;
  width: auto;
}

.navbar-brand {
  font-size: 1.25rem;
}

.dropdown-menu {
  min-width: 200px;
}

.dropdown-item {
  padding: 0.5rem 1rem;
}

.dropdown-item i {
  width: 20px;
}
</style>
