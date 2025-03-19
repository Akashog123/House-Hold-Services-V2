<template>
  <div class="bg-light min-vh-100 d-flex align-items-center">
    <!-- Background Elements -->
    <div class="bg-blur position-absolute">
      <div class="round-1"></div>
      <div class="round-2"></div>
    </div>
    
    <!-- Register Container -->
    <div class="container">
      <div class="row justify-content-center">
        <div class="col-md-8 col-lg-7">
          <div class="card shadow-sm border">
            <div class="card-body p-4 p-md-5">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="h3 mb-0">Register</h3>
                <img src="@/assets/logo.png" alt="Logo" class="register-logo" />
              </div>

              <form @submit.prevent="register" ref="form" class="needs-validation" novalidate>
                <!-- Role Selection -->
                <div class="mb-4">
                  <ul class="nav nav-pills nav-fill">
                    <li class="nav-item">
                      <button 
                        type="button"
                        class="nav-link"
                        :class="{ active: selectedRole === 'customer' }"
                        @click="selectedRole = 'customer'"
                      >
                        Customer
                      </button>
                    </li>
                    <li class="nav-item">
                      <button 
                        type="button"
                        class="nav-link"
                        :class="{ active: selectedRole === 'professional' }"
                        @click="selectedRole = 'professional'"
                      >
                        Service Professional
                      </button>
                    </li>
                  </ul>
                </div>

                <!-- Common Fields -->
                <div class="row g-3">
                  <!-- Username -->
                  <div class="col-12">
                    <label for="username" class="form-label">Username</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-person"></i></span>
                      <input
                        v-model="username"
                        type="text"
                        class="form-control"
                        id="username"
                        placeholder="Choose a username"
                        :class="{ 'is-invalid': usernameError }"
                        required
                      >
                      <div class="invalid-feedback">{{ usernameError }}</div>
                    </div>
                  </div>

                  <!-- Email -->
                  <div class="col-12">
                    <label for="email" class="form-label">Email Address</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-envelope"></i></span>
                      <input
                        v-model="email"
                        type="email"
                        class="form-control"
                        id="email"
                        placeholder="Enter email address"
                        :class="{ 'is-invalid': emailError }"
                        required
                      >
                      <div class="invalid-feedback">{{ emailError }}</div>
                    </div>
                  </div>

                  <!-- Full Name -->
                  <div class="col-12">
                    <label for="fullName" class="form-label">Full Name</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-person-vcard"></i></span>
                      <input
                        v-model="fullName"
                        type="text"
                        class="form-control"
                        id="fullName"
                        placeholder="Enter your full name"
                        :class="{ 'is-invalid': !fullName }"
                        required
                      >
                      <div class="invalid-feedback">Full name is required</div>
                    </div>
                  </div>

                  <!-- Password -->
                  <div class="col-12">
                    <label for="password" class="form-label">Password</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-lock"></i></span>
                      <input
                        v-model="password"
                        :type="showPassword ? 'text' : 'password'"
                        class="form-control"
                        id="password"
                        placeholder="Create a password"
                        :class="{ 'is-invalid': passwordError }"
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

                  <!-- Confirm Password -->
                  <div class="col-12">
                    <label for="confirmPassword" class="form-label">Confirm Password</label>
                    <div class="input-group">
                      <span class="input-group-text"><i class="bi bi-lock-check"></i></span>
                      <input
                        v-model="confirmPassword"
                        :type="showPassword ? 'text' : 'password'"
                        class="form-control"
                        id="confirmPassword"
                        placeholder="Confirm your password"
                        :class="{ 'is-invalid': confirmPasswordError }"
                        required
                      >
                      <button 
                        class="btn btn-outline-secondary" 
                        type="button"
                        @click="showPassword = !showPassword"
                      >
                        <i :class="showPassword ? 'bi bi-eye-slash' : 'bi bi-eye'"></i>
                      </button>
                      <div class="invalid-feedback">{{ confirmPasswordError }}</div>
                    </div>
                  </div>

                  <!-- Professional Fields -->
                  <template v-if="selectedRole === 'professional'">
                    <div class="col-12">
                      <hr class="my-3">
                      <h5>Professional Details</h5>
                    </div>
                    
                    <!-- Service Type Selection -->
                    <div class="col-12">
                      <label for="serviceType" class="form-label">Service Type *</label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-tools"></i></span>
                        <select 
                          v-model="serviceTypeId"
                          class="form-select"
                          id="serviceType"
                          required
                          :class="{ 'is-invalid': serviceTypeError }"
                        >
                          <option value="" disabled selected>Select your service type</option>
                          <option v-for="service in availableServices" :key="service.id" :value="service.id">
                            {{ service.name }}
                          </option>
                        </select>
                        <div class="invalid-feedback">{{ serviceTypeError }}</div>
                      </div>
                    </div>
                    
                    <!-- Experience Years -->
                    <div class="col-12 col-md-6">
                      <label for="experienceYears" class="form-label">Years of Experience</label>
                      <div class="input-group">
                        <span class="input-group-text"><i class="bi bi-calendar3"></i></span>
                        <input
                          v-model="experienceYears"
                          type="number"
                          class="form-control"
                          id="experienceYears"
                          min="0"
                          max="50"
                          placeholder="Years of Experience"
                        >
                      </div>
                    </div>
                    
                    <!-- Description -->
                    <div class="col-12">
                      <label for="description" class="form-label">Professional Description</label>
                      <textarea
                        v-model="description"
                        class="form-control"
                        id="description"
                        rows="3"
                        placeholder="Describe your services and expertise"
                      ></textarea>
                    </div>
                    
                    <!-- License Document Upload -->
                    <div class="col-12">
                      <label for="licenseDocument" class="form-label">
                        Verification Document / License *
                        <i class="bi bi-info-circle ms-1" data-bs-toggle="tooltip" title="Upload a valid license, certification, or ID proof for verification"></i>
                      </label>
                      <div class="input-group mb-1">
                        <span class="input-group-text"><i class="bi bi-file-earmark-check"></i></span>
                        <input
                          type="file"
                          class="form-control"
                          id="licenseDocument"
                          @change="handleFileUpload"
                          accept=".pdf,.jpg,.jpeg,.png"
                          required
                          :class="{ 'is-invalid': documentError }"
                        >
                        <div class="invalid-feedback">{{ documentError }}</div>
                      </div>
                      <div class="form-text">
                        Accepted formats: PDF, JPG, JPEG, PNG. Maximum size: 5MB
                      </div>
                      
                      <div v-if="selectedFile" class="alert alert-info mt-2 d-flex align-items-center">
                        <i class="bi bi-file-earmark me-2"></i>
                        <div>
                          <strong>{{ selectedFile.name }}</strong> 
                          <span class="ms-2">({{ formatFileSize(selectedFile.size) }})</span>
                        </div>
                      </div>
                    </div>
                    
                    <!-- Verification Notice -->
                    <div class="col-12">
                      <div class="alert alert-warning">
                        <i class="bi bi-exclamation-triangle me-2"></i>
                        Your account will require approval from our team before you can start providing services. This usually takes 1-2 business days.
                      </div>
                    </div>
                  </template>

                  <!-- Customer Fields -->
                  <template v-if="selectedRole === 'customer'">
                    <div class="col-12">
                      <hr class="my-3">
                      <h5>Contact Information</h5>
                    </div>
                    
                    <div class="col-12">
                      <label for="address" class="form-label">Address</label>
                      <input
                        v-model="address"
                        type="text"
                        class="form-control"
                        id="address"
                        placeholder="Enter your address"
                      >
                    </div>
                    
                    <div class="col-md-6">
                      <label for="pinCode" class="form-label">PIN Code</label>
                      <input
                        v-model="pinCode"
                        type="text"
                        class="form-control"
                        id="pinCode"
                        placeholder="Enter PIN code"
                      >
                    </div>
                    
                    <div class="col-md-6">
                      <label for="phoneNumber" class="form-label">Phone Number</label>
                      <input
                        v-model="phoneNumber"
                        type="tel"
                        class="form-control"
                        id="phoneNumber"
                        placeholder="Enter phone number"
                      >
                    </div>
                  </template>
                  
                  <!-- Error Message -->
                  <div v-if="error" class="col-12">
                    <div class="alert alert-danger">
                      {{ error }}
                    </div>
                  </div>
                  
                  <!-- Submit Button -->
                  <div class="col-12 mt-4">
                    <button 
                      type="submit" 
                      class="btn btn-primary w-100"
                      :disabled="loading"
                    >
                      <span v-if="loading" class="spinner-border spinner-border-sm me-2" role="status"></span>
                      Register
                    </button>
                  </div>
                  
                  <!-- Login Link -->
                  <div class="col-12 text-center mt-3">
                    <span>Already have an account? </span>
                    <router-link to="/login" class="text-primary">Login here</router-link>
                  </div>
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api.service';

export default {
  name: 'Register',
  
  setup() {
    const router = useRouter();
    
    // Form fields
    const username = ref('');
    const email = ref('');
    const password = ref('');
    const confirmPassword = ref('');
    const fullName = ref('');
    const selectedRole = ref('customer');
    const showPassword = ref(false);
    
    // Customer specific fields
    const address = ref('');
    const pinCode = ref('');
    const phoneNumber = ref('');
    
    // Professional specific fields
    const serviceTypeId = ref('');
    const experienceYears = ref(0);
    const description = ref('');
    const selectedFile = ref(null);
    const availableServices = ref([]);
    
    // Form validation
    const usernameError = ref('');
    const emailError = ref('');
    const passwordError = ref('');
    const confirmPasswordError = ref('');
    const serviceTypeError = ref('');
    const documentError = ref('');
    
    // Form state
    const loading = ref(false);
    const error = ref('');
    
    // Fetch available services for dropdown
    const fetchServices = async () => {
      try {
        const response = await api.get('/services');
        availableServices.value = response.data;
      } catch (err) {
        console.error('Error fetching services:', err);
        error.value = 'Failed to load service types. Please try again.';
      }
    };
    
    // Handle file upload
    const handleFileUpload = (event) => {
      const file = event.target.files[0];
      if (!file) {
        selectedFile.value = null;
        return;
      }
      
      // Validate file type
      const allowedTypes = ['application/pdf', 'image/jpeg', 'image/jpg', 'image/png'];
      if (!allowedTypes.includes(file.type)) {
        documentError.value = 'Invalid file type. Please upload PDF, JPG, or PNG.';
        selectedFile.value = null;
        event.target.value = ''; // Reset file input
        return;
      }
      
      // Validate file size (5MB max)
      const maxSize = 5 * 1024 * 1024; // 5MB in bytes
      if (file.size > maxSize) {
        documentError.value = 'File size exceeds 5MB limit.';
        selectedFile.value = null;
        event.target.value = ''; // Reset file input
        return;
      }
      
      documentError.value = ''; // Clear any previous errors
      selectedFile.value = file;
    };
    
    // Format file size for display
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 Bytes';
      
      const k = 1024;
      const sizes = ['Bytes', 'KB', 'MB', 'GB'];
      const i = Math.floor(Math.log(bytes) / Math.log(k));
      
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    };
    
    // Validate form
    const validateForm = () => {
      let isValid = true;
      
      // Reset errors
      usernameError.value = '';
      emailError.value = '';
      passwordError.value = '';
      confirmPasswordError.value = '';
      serviceTypeError.value = '';
      documentError.value = '';
      
      // Username validation
      if (!username.value.trim()) {
        usernameError.value = 'Username is required';
        isValid = false;
      } else if (username.value.length < 3) {
        usernameError.value = 'Username must be at least 3 characters';
        isValid = false;
      }
      
      // Email validation
      if (!email.value.trim()) {
        emailError.value = 'Email is required';
        isValid = false;
      } else if (!/^\S+@\S+\.\S+$/.test(email.value)) {
        emailError.value = 'Please enter a valid email address';
        isValid = false;
      }
      
      // Password validation
      if (!password.value) {
        passwordError.value = 'Password is required';
        isValid = false;
      } else if (password.value.length < 6) {
        passwordError.value = 'Password must be at least 6 characters';
        isValid = false;
      }
      
      // Confirm password validation
      if (password.value !== confirmPassword.value) {
        confirmPasswordError.value = 'Passwords do not match';
        isValid = false;
      }
      
      // Professional specific validations
      if (selectedRole.value === 'professional') {
        if (!serviceTypeId.value) {
          serviceTypeError.value = 'Please select a service type';
          isValid = false;
        }
        
        if (!selectedFile.value) {
          documentError.value = 'Verification document is required';
          isValid = false;
        }
      }
      
      return isValid;
    };
    
    // Register user
    const register = async () => {
      if (!validateForm()) {
        return;
      }
      
      loading.value = true;
      error.value = '';
      
      try {
        // Create form data for file upload
        const formData = new FormData();
        formData.append('username', username.value);
        formData.append('email', email.value);
        formData.append('password', password.value);
        formData.append('full_name', fullName.value);
        formData.append('role', selectedRole.value);
        
        // Add role-specific fields
        if (selectedRole.value === 'professional') {
          formData.append('service_type_id', serviceTypeId.value);
          formData.append('experience_years', experienceYears.value);
          formData.append('description', description.value);
          formData.append('verification_document', selectedFile.value);
        } else {
          formData.append('address', address.value);
          formData.append('pin_code', pinCode.value);
          formData.append('phone_number', phoneNumber.value);
        }
        
        const response = await api.post('/auth/register', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // Handle successful registration
        if (response.data.approval_required) {
          // Redirect to pending approval page
          router.push('/registration-success?approval=pending');
        } else {
          // Redirect to login
          router.push('/login?registered=true');
        }
      } catch (err) {
        console.error('Registration error:', err);
        if (err.response?.data?.msg) {
          error.value = err.response.data.msg;
        } else {
          error.value = 'Registration failed. Please try again.';
        }
      } finally {
        loading.value = false;
      }
    };
    
    onMounted(() => {
      fetchServices();
    });
    
    return {
      // Form fields
      username,
      email,
      password,
      confirmPassword,
      fullName,
      selectedRole,
      showPassword,
      address,
      pinCode,
      phoneNumber,
      serviceTypeId,
      experienceYears,
      description,
      selectedFile,
      availableServices,
      
      // Validation
      usernameError,
      emailError,
      passwordError,
      confirmPasswordError,
      serviceTypeError,
      documentError,
      
      // Form state
      loading,
      error,
      
      // Methods
      register,
      handleFileUpload,
      formatFileSize
    };
  }
}
</script>

<style scoped>
@import '@/assets/auth.css';

.register-logo {
  max-height: 60px;
  width: auto;
}

.nav-pills .nav-link {
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
}

.nav-pills .nav-link.active {
  background-color: var(--bs-primary);
}
</style>
