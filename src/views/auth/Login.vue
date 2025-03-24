<template>
  <div class="bg-light min-vh-100 d-flex align-items-center">
    <!-- Background Elements -->
    <div class="bg-blur position-absolute">
      <div class="round-1"></div>
      <div class="round-2"></div>
    </div>
    
    <!-- Login Container -->
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-6 col-lg-5">
          <div class="card shadow-sm border">
            <div class="card-body p-4 p-md-5">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="h3 mb-0">Login</h3>
                <img src="@/assets/logo.png" alt="Logo" class="login-logo" />
              </div>
              
              <form @submit.prevent="login" ref="form" class="needs-validation" novalidate>
                <!-- Username/Email Field -->
                <div class="mb-3">
                  <label for="userInput" class="form-label">Username/Email Address</label>
                  <input
                    v-model="userInput"
                    type="text"
                    class="form-control"
                    id="userInput"
                    autocomplete="username"
                    placeholder="Enter username or email address"
                    :class="{ 'is-invalid': userInputError }"
                    required
                  >
                  <div class="invalid-feedback">{{ userInputError }}</div>
                </div>

                <!-- Password Field -->
                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <div class="input-group">
                    <input
                      v-model="password"
                      :type="showPassword ? 'text' : 'password'"
                      class="form-control"
                      id="password"
                      placeholder="Enter your password"
                      autocomplete="current-password"
                      required
                    >
                    <button 
                      class="btn btn-outline-secondary" 
                      type="button"
                      @click="showPassword = !showPassword"
                    >
                      <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                    </button>
                    <div class="invalid-feedback">{{ passwordError }}</div>
                  </div>
                </div>

                <!-- Remember Me & Forgot Password -->
                <div class="d-flex justify-content-between align-items-center mb-4">
                  <div class="form-check">
                    <input
                      v-model="checkbox"
                      type="checkbox"
                      class="form-check-input"
                      id="keepSignedIn"
                    >
                    <label class="form-check-label" for="keepSignedIn">
                      Keep me signed in
                    </label>
                  </div>
                  <router-link to="/forgot-password" class="text-primary text-decoration-none">
                    Forgot Password?
                  </router-link>
                </div>

                <!-- Error Message -->
                <div v-if="error" class="alert alert-danger text-center mb-3">
                  {{ error }}
                </div>

                <!-- Submit Button -->
                <button
                  type="submit"
                  class="btn btn-primary w-100 mb-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Login
                </button>

                <!-- Register Link -->
                <div class="text-center">
                  <span class="text-muted">Don't have an account? </span>
                  <router-link to="/register" class="text-primary text-decoration-none">
                    Register
                  </router-link>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { mapState } from 'vuex'

export default {
  name: 'Login',
  data() {
    return {
      userInput: '',
      password: '',
      checkbox: false,
      showPassword: false,
      userInputError: '',
      passwordError: ''
    }
  },
  computed: {
    ...mapState({
      error: state => state.auth?.error || null,
      loading: state => state.auth?.loading || false
    })
  },
  methods: {
    validateForm() {
      let isValid = true
      this.userInputError = ''
      this.passwordError = ''

      if (!this.userInput) {
        this.userInputError = 'Username or Email is required'
        isValid = false
      } else if (this.userInput.includes('@')) {
        const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
        if (!emailPattern.test(this.userInput)) {
          this.userInputError = 'Invalid email format'
          isValid = false
        }
      } else {
        const usernamePattern = /^[a-zA-Z0-9_]{3,20}$/
        if (!usernamePattern.test(this.userInput)) {
          this.userInputError = 'Username must be 3-20 characters (letters, numbers, or _)'
          isValid = false
        }
      }

      if (!this.password) {
        this.passwordError = 'Password is required'
        isValid = false
      } else if (this.password.length < 6) {
        this.passwordError = 'Password must be at least 6 characters'
        isValid = false
      }

      return isValid
    },
    async login() {
      if (this.validateForm()) {
        try {
          const loginData = {
            userInput: this.userInput,
            password: this.password,
            keepSignedIn: this.checkbox
          }
          
          // Use the fixed auth/login action with the loginData
          const response = await this.$store.dispatch('auth/login', loginData)
          
          if (response && response.token) {
            const userRole = response.user.role
            console.log('Login successful. User role detected:', userRole);
            let dashboardPath
            
            switch(userRole) {
              case 'admin':
                dashboardPath = '/admin/dashboard'
                console.log('Redirecting to admin dashboard');
                break
              case 'professional':
                dashboardPath = '/professional/dashboard'
                console.log('Redirecting to professional dashboard');
                break
              case 'customer':
                dashboardPath = '/customer/dashboard'
                console.log('Redirecting to customer dashboard');
                break
              default:
                dashboardPath = '/'
                console.log('Unknown role, redirecting to home page');
            }
            
            await this.$router.push(dashboardPath)
          }
        } catch (error) {
          console.error('Login error details:', error)
          if (error.response) {
            switch (error.response.status) {
              case 401:
                this.userInputError = 'Invalid username or password'
                break
              case 404:
                this.userInputError = 'Server not found. Please try again later.'
                break
              default:
                this.userInputError = error.response.data.message || 'An error occurred during login'
            }
          } else {
            this.userInputError = error.message || 'Network error. Please check your connection.'
          }
        }
      }
    }
  },
  created() {
    this.$store.dispatch('auth/clearError')
  }
}
</script>

<style scoped>
@import '@/assets/auth.css';

.login-logo {
  max-height: 60px;
  width: auto;
}
</style>
