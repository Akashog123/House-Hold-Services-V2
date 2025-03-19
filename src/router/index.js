import { createRouter, createWebHistory } from 'vue-router'
import store from '@/store'

const routes = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    beforeEnter: (to, from, next) => {
      const isAuthenticated = store.getters['auth/isAuthenticated']
      const userRole = store.getters['auth/user']?.role
      if (isAuthenticated) {
        switch(userRole) {
          case 'admin':
            next('/admin/dashboard')
            break
          case 'professional':
            next('/professional/dashboard')
            break
          case 'customer':
            next('/customer/dashboard')
            break
          default:
            next()
        }
     } else {
        next()
      }
    }
  },
  { path: '/login',
    name: 'Login',
    component: () => import('@/views/auth/Login.vue'),
    meta: { requiresGuest: true },
    // Add beforeEnter to debug login page access
    beforeEnter: (to, from, next) => {
      console.log('DEBUG - Login route beforeEnter')
      const isAuthenticated = store.getters['auth/isAuthenticated']
      console.log('DEBUG - isAuthenticated:', isAuthenticated)
      
      // Only redirect if user is actually authenticated
      if (isAuthenticated) {
        const userRole = store.getters['auth/user']?.role
        console.log('DEBUG - Authenticated user role:', userRole)
        
        // Redirect to appropriate dashboard
        switch(userRole) {
          case 'admin':
            next('/admin/dashboard')
            break
          case 'professional':
            next('/professional/dashboard')
            break
          case 'customer':
            next('/customer/dashboard')
            break
          default:
            next('/')
        }
      } else {
        // If not authenticated, allow access to login
        next()
      }
    }
  },
  { path: '/register',
    name: 'Register',
    component: () => import('@/views/auth/Register.vue'),
    meta: { requiresGuest: true }
  },
  { path: '/registration-success',
    name: 'RegistrationSuccess',
    component: () => import('@/views/auth/RegistrationSuccess.vue'),
    meta: { requiresGuest: true }
  },
  { path: '/unauthorized',
    name: 'Unauthorized',
    component: () => import('@/views/NotFound.vue')
  },
  { path: '/services',
    name: 'Services',
    component: () => import('@/components/services/ServiceCard.vue')
  },
  { path: '/forgot-password',
    name: 'ForgotPassword',
    component: () => import('@/views/auth/ForgotPassword.vue'),
    meta: { requiresGuest: true }
  },
  // Admin routes
  { path: '/admin',
    meta: { requiresAuth: true, requiresAdmin: true },
    children: [
      { path: '',
        name: 'AdminDashboard',
        redirect: { name: 'AdminDashboard' }
      },
      { path: 'dashboard',
        name: 'AdminDashboard',
        component: () => import('@/views/admin/DashboardView.vue')
      },
      { path: 'services',
        name: 'ServiceManagement',
        component: () => import('@/views/admin/ServiceManagementView.vue')
      },
      { path: 'users',
        name: 'UserManagement',
        component: () => import('@/views/admin/UserManagementView.vue')
      },
      { path: 'analytics',
        name: 'Analytics',
        component: () => import('@/views/admin/AnalyticsView.vue')
      },
      { path: 'settings',
        name: 'AdminSettings',
        component: () => import('@/views/admin/SettingsView.vue')
      },
      { path: 'profile',
        name: 'AdminProfile',
        component: () => import('@/views/admin/ProfileView.vue')
      },
      { path: 'approvals',
        name: 'AdminApprovals',
        component: () => import('@/views/admin/ApprovalsView.vue')
      }
    ]
  },
  { path: '/professional',
    meta: { requiresAuth: true, requiresProfessional: true },
    children: [
      {
        path: 'dashboard',
        name: 'ProfessionalDashboard',
        component: () => import('@/views/professional/DashboardView.vue')
      } // Fix: Added missing closing bracket
    ]
  }, 
  { path: '/customer',
    meta: { requiresAuth: true, requiresCustomer: true },
    children: [
      {
        path: 'dashboard',
        name: 'CustomerDashboard',
        component: () => import('@/views/customer/DashboardView.vue')
      }
      // Other customer routes...
    ]
  }
]
const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  console.log('-------- Router Navigation --------');
  console.log('From:', from.path, 'To:', to.path);
  
  // Access auth token and user through namespaced state
  const isAuthenticated = store.getters['auth/isAuthenticated'];
  const userRole = store.getters['auth/user']?.role;
  
  // For debugging - remove in production
  console.log('Navigation guard:', { isAuthenticated, userRole, to: to.path });
  console.log('isAuthenticated:', isAuthenticated, 'userRole:', userRole);
  console.log('Auth token exists:', !!store.getters['auth/token']);
  console.log('User in store:', store.getters['auth/user']);
  console.log('localStorage token:', !!localStorage.getItem('auth_token'));

  // Check for routes requiring authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!isAuthenticated) {
      next('/login');
      return;
    }
    
    // Role-based route protection
    if (to.matched.some(record => record.meta.requiresAdmin) && userRole !== 'admin') {
      next('/unauthorized');
      return;
    }
    
    if (to.matched.some(record => record.meta.requiresProfessional) && userRole !== 'professional') {
      next('/unauthorized');
      return;
    }
    
    if (to.matched.some(record => record.meta.requiresCustomer) && userRole !== 'customer') {
      next('/unauthorized');
      return;
    }
  }
  
  // Check for guest-only routes
  if (to.matched.some(record => record.meta.requiresGuest) && isAuthenticated) {
    // Only redirect if actually authenticated
    if (userRole) {
      // Redirect to appropriate dashboard
      switch(userRole) {
        case 'admin':
          next('/admin/dashboard');
          break;
        case 'professional':
          next('/professional/dashboard');
          break;
        case 'customer':
          next('/customer/dashboard');
          break;
        default:
          next('/');
      }
      return;
    }
  }

  next();
});

export default router
