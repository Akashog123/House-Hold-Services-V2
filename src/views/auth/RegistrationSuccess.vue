<template>
  <div class="bg-light min-vh-100 d-flex align-items-center">
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-sm border">
            <div class="card-body p-4 p-md-5 text-center">
              <div v-if="isPending" class="mb-4">
                <div class="registration-icon pending mb-4">
                  <i class="bi bi-clock-history"></i>
                </div>
                <h2 class="h3 mb-3">Registration Pending Approval</h2>
                <p class="text-muted mb-4">
                  Thank you for registering as a service professional. Your account is pending approval from our team.
                </p>
                <div class="alert alert-info">
                  <i class="bi bi-info-circle me-2"></i>
                  We'll review your verification documents and approve your account within 1-2 business days. You'll receive an email notification when your account is approved.
                </div>
              </div>
              
              <div v-else class="mb-4">
                <div class="registration-icon success mb-4">
                  <i class="bi bi-check-circle"></i>
                </div>
                <h2 class="h3 mb-3">Registration Successful!</h2>
                <p class="text-muted mb-4">
                  Your account has been created successfully. You can now log in to access our services.
                </p>
              </div>
              
              <div class="d-grid gap-3">
                <router-link to="/login" class="btn btn-primary">
                  Go to Login
                </router-link>
                <router-link to="/" class="btn btn-outline-secondary">
                  Back to Home
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'RegistrationSuccess',
  
  computed: {
    isPending() {
      return this.$route.query.approval === 'pending';
    }
  }
}
</script>

<style scoped>
.registration-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 100px;
  height: 100px;
  border-radius: 50%;
  font-size: 3rem;
}

.registration-icon.success {
  background-color: rgba(25, 135, 84, 0.1);
  color: #198754;
}

.registration-icon.pending {
  background-color: rgba(13, 110, 253, 0.1);
  color: #0d6efd;
}
</style>
