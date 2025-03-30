<template>
  <div class="bg-containerBg position-relative ma-0 pa-0 full-height">
    <!-- Background Elements -->
    <div class="bg-blur">
      <div class="round-1"></div>
      <div class="round-2"></div>
    </div>
    
    <!-- Forgot Password Container -->
    <div class="login-wrapper d-flex align-center justify-center">
      <v-card elevation="0" variant="outlined" rounded="lg" class="loginBox bg-surface">
        <v-card-text class="pa-sm-10 pa-6">
          <div class="d-flex justify-space-between align-center">
            <h3 class="text-h4 text-center mb-0">This page is deprecated...</h3>
            <img src="@/assets/logo.png" alt="Logo" class="login-logo" />
          </div>
          
          <div v-if="!submitSuccess">
            <div class="text-body-2 my-4">
              This page is deprecated currently.
            </div>
            
            <v-form @submit.prevent="submitForgotPassword" ref="form" class="mt-4 loginForm">
              <div class="mb-6">
                <v-text-field
                  v-model="email"
                  label="Email"
                  placeholder="Enter your email address"
                  name="email"
                  type="email"
                  :rules="emailRules"
                  density="comfortable"
                  required
                  hide-details="auto"
                  variant="outlined"
                  color="primary"
                ></v-text-field>
              </div>
              
              <div v-if="error" class="error-message red--text mt-3 text-center">
                {{ error }}
              </div>
              
              <v-btn
                color="primary"
                :loading="loading"
                block
                class="mt-5"
                variant="flat"
                size="large"
                rounded="md"
                :disabled="loading"
                type="submit"
                @click="submitForgotPassword"
              >
                Submit
              </v-btn>
            </v-form>
          </div>
          
          <div v-else class="text-center mt-4">
            <v-icon color="success" size="64" class="mb-4">mdi-check-circle</v-icon>
            <h3 class="text-h6">Request Submitted</h3>
            <p class="mt-2">
              If an account exists with the email address you entered, you will receive password reset instructions.
            </p>
          </div>
          
          <div class="text-center mt-4">
            <router-link to="/login" class="link-hover text-primary text-decoration-none">
              Back to Login
            </router-link>
          </div>
        </v-card-text>
      </v-card>
    </div>
  </div>
</template>

<script>
import { mapGetters } from 'vuex'

export default {
  name: 'ForgotPassword',
  data() {
    return {
      email: '',
      submitSuccess: false,
      emailRules: [
        v => !!v || 'Email is required',
        v => /.+@.+\..+/.test(v) || 'Email must be valid'
      ]
    }
  },
  computed: {
    ...mapGetters(['error', 'loading'])
  },
  methods: {
    async submitForgotPassword() {
      if (this.$refs.form.validate()) {
        try {
          await this.$store.dispatch('forgotPassword', this.email)
          this.submitSuccess = true
        } catch (error) {
          console.error('Password reset request error:', error)
        }
      }
    }
  },
  created() {
    this.$store.dispatch('clearError')
  }
}
</script>

<style scoped>
@import '@/assets/auth.css';
</style>
