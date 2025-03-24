<template>
  <div class="bg-light min-vh-100 d-flex align-items-center">
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-6">
          <div class="card shadow-sm border">
            <div class="card-body p-4 p-md-5 text-center">
              <div class="success-icon mb-4">
                <i class="bi bi-check-circle-fill text-success"></i>
              </div>
              
              <h2 class="mb-4">Registration Successful!</h2>
              
              <!-- Different messages based on role -->
              <template v-if="isProfessional">
                <p class="lead mb-4">
                  Thank you for registering as a service professional. 
                  Your application has been submitted and is pending approval.
                </p>
                
                <div class="alert alert-info mb-4">
                  <p class="mb-0">
                    <i class="bi bi-info-circle me-2"></i>
                    Our team will review your application and verify your documents.
                    This process typically takes 24-48 hours.
                  </p>
                </div>
                
                <p>
                  You'll receive an email notification once your account is approved.
                </p>
              </template>
              
              <template v-else>
                <p class="lead mb-4">
                  Your account has been created successfully.
                  You can now login to access our services.
                </p>
              </template>
              
              <div class="mt-5">
                <router-link to="/login" class="btn btn-primary btn-lg px-4">
                  Go to Login
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
import { computed } from 'vue';
import { useRoute } from 'vue-router';

export default {
  name: 'RegistrationSuccess',
  
  setup() {
    const route = useRoute();
    
    const isProfessional = computed(() => {
      return route.query.role === 'professional' && route.query.pendingApproval === 'true';
    });
    
    return {
      isProfessional
    };
  }
};
</script>

<style scoped>
.success-icon {
  font-size: 5rem;
}

.card {
  border-radius: 15px;
}
</style>
