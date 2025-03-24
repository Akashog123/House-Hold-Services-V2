<template>
  <div class="bg-light min-vh-100 d-flex align-items-center">
    <!-- Background Elements -->
    <div class="bg-blur position-absolute">
      <div class="round-1"></div>
      <div class="round-2"></div>
    </div>
    
    <div class="container py-5">
      <div class="row justify-content-center">
        <div class="col-md-8">
          <div class="card shadow-sm border">
            <div class="card-body p-4 p-md-5">
              <div class="d-flex justify-content-between align-items-center mb-4">
                <h3 class="h3 mb-0">Register</h3>
                <img src="@/assets/logo.png" alt="Logo" class="register-logo" />
              </div>
              
              <!-- Registration form -->
              <form @submit.prevent="register" class="needs-validation" novalidate>
                <!-- Role Selection -->
                <div class="mb-4">
                  <label class="form-label">I want to register as:</label>
                  <div class="d-flex gap-3">
                    <div class="form-check">
                      <input
                        v-model="role"
                        type="radio"
                        id="roleCustomer"
                        name="role"
                        value="customer"
                        class="form-check-input"
                      />
                      <label class="form-check-label" for="roleCustomer">
                        Customer
                      </label>
                    </div>
                    <div class="form-check">
                      <input
                        v-model="role"
                        type="radio"
                        id="roleProfessional"
                        name="role"
                        value="professional"
                        class="form-check-input"
                      />
                      <label class="form-check-label" for="roleProfessional">
                        Service Professional
                      </label>
                    </div>
                  </div>
                </div>
                
                <!-- Basic Information -->
                <div class="mb-3">
                  <label for="username" class="form-label">Username</label>
                  <input
                    v-model="formData.username"
                    type="text"
                    class="form-control"
                    id="username"
                    placeholder="Choose a username"
                    required
                  />
                  <div class="invalid-feedback">
                    Please choose a username.
                  </div>
                </div>

                <div class="mb-3">
                  <label for="email" class="form-label">Email</label>
                  <input
                    v-model="formData.email"
                    type="email"
                    class="form-control"
                    id="email"
                    placeholder="Enter your email"
                    required
                  />
                  <div class="invalid-feedback">
                    Please enter a valid email.
                  </div>
                </div>

                <div class="mb-3">
                  <label for="password" class="form-label">Password</label>
                  <input
                    v-model="formData.password"
                    type="password"
                    class="form-control"
                    id="password"
                    placeholder="Create a password"
                    required
                  />
                  <div class="invalid-feedback">
                    Please enter a password.
                  </div>
                </div>

                <div class="mb-4">
                  <label for="confirmPassword" class="form-label">Confirm Password</label>
                  <input
                    v-model="formData.confirmPassword"
                    type="password"
                    class="form-control"
                    id="confirmPassword"
                    placeholder="Confirm your password"
                    required
                  />
                  <div class="invalid-feedback">
                    Passwords do not match.
                  </div>
                </div>
                
                <!-- Customer specific fields -->
                <div v-if="role === 'customer'" class="mb-4">
                  <h5 class="mb-3">Customer Information</h5>
                  
                  <div class="mb-3">
                    <label for="fullName" class="form-label">Full Name</label>
                    <input
                      v-model="formData.fullName"
                      type="text"
                      class="form-control"
                      id="fullName"
                      placeholder="Enter your full name"
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="phone" class="form-label">Phone Number</label>
                    <input
                      v-model="formData.phoneNumber"
                      type="tel"
                      class="form-control"
                      id="phone"
                      placeholder="Enter your phone number"
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="address" class="form-label">Address</label>
                    <textarea
                      v-model="formData.address"
                      class="form-control"
                      id="address"
                      placeholder="Enter your address"
                      rows="3"
                    ></textarea>
                  </div>
                  
                  <div class="mb-3">
                    <label for="pinCode" class="form-label">PIN Code</label>
                    <input
                      v-model="formData.pinCode"
                      type="text"
                      class="form-control"
                      id="pinCode"
                      placeholder="Enter your PIN code"
                    />
                  </div>
                </div>
                
                <!-- Professional specific fields -->
                <div v-if="role === 'professional'" class="mb-4">
                  <h5 class="mb-3">Professional Information</h5>
                  
                  <div class="mb-3">
                    <label for="fullName" class="form-label">Full Name</label>
                    <input
                      v-model="formData.fullName"
                      type="text"
                      class="form-control"
                      id="fullName"
                      placeholder="Enter your full name"
                      required
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="phone" class="form-label">Phone Number</label>
                    <input
                      v-model="formData.phoneNumber"
                      type="tel"
                      class="form-control"
                      id="phone"
                      placeholder="Enter your phone number"
                      required
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="experience" class="form-label">Years of Experience</label>
                    <input
                      v-model="formData.experienceYears"
                      type="number"
                      min="0"
                      class="form-control"
                      id="experience"
                      placeholder="Enter years of experience"
                      required
                    />
                  </div>
                  
                  <div class="mb-3">
                    <label for="serviceType" class="form-label">Service Type</label>
                    <select
                      v-model="formData.serviceTypeId"
                      class="form-select"
                      id="serviceType"
                      required
                    >
                      <option value="" disabled selected>Select a service type</option>
                      <option v-for="service in services" :key="service.id" :value="service.id">
                        {{ service.name }}
                      </option>
                    </select>
                    <div class="invalid-feedback">
                      Please select a service type.
                    </div>
                  </div>
                  
                  <div class="mb-4">
                    <label for="description" class="form-label">Description</label>
                    <textarea
                      v-model="formData.description"
                      class="form-control"
                      id="description"
                      placeholder="Describe your services and expertise"
                      rows="3"
                      required
                    ></textarea>
                  </div>

                  <!-- Document Upload -->
                  <div class="mb-4">
                    <label class="form-label">Identity Verification</label>
                    <div class="document-upload p-3 bg-light border rounded">
                      <div class="mb-3">
                        <label for="idProof" class="form-label">ID Proof (Govt. ID)</label>
                        <input 
                          type="file" 
                          id="idProof" 
                          class="form-control"
                          @change="handleFileUpload($event, 'idProof')"
                          accept=".jpg,.jpeg,.png,.pdf"
                          required
                        />
                        <div class="form-text">Upload your government-issued ID (Aadhaar, PAN, Passport, etc.)</div>
                      </div>
                      
                      <div class="mb-3">
                        <label for="addressProof" class="form-label">Address Proof</label>
                        <input 
                          type="file" 
                          id="addressProof" 
                          class="form-control"
                          @change="handleFileUpload($event, 'addressProof')"
                          accept=".jpg,.jpeg,.png,.pdf"
                          required
                        />
                        <div class="form-text">Upload proof of address (utility bill, bank statement, etc.)</div>
                      </div>
                      
                      <div>
                        <label for="qualification" class="form-label">Qualification Certificate (Optional)</label>
                        <input 
                          type="file" 
                          id="qualification" 
                          class="form-control"
                          @change="handleFileUpload($event, 'qualification')"
                          accept=".jpg,.jpeg,.png,.pdf"
                        />
                        <div class="form-text">Upload any relevant qualification or training certificates</div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Error message -->
                <div v-if="error" class="alert alert-danger" role="alert">
                  {{ error }}
                </div>

                <!-- Submit Button -->
                <button
                  type="submit"
                  class="btn btn-primary w-100 py-2 mt-3"
                  :disabled="loading"
                >
                  <span v-if="loading" class="spinner-border spinner-border-sm me-2"></span>
                  Register
                </button>

                <!-- Login Link -->
                <div class="text-center mt-4">
                  <span class="text-muted">Already have an account? </span>
                  <router-link to="/login" class="text-primary text-decoration-none">
                    Login
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
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import api from '@/services/api.service';

export default {
  name: 'Register',
  
  setup() {
    const router = useRouter();
    const role = ref('customer');
    const loading = ref(false);
    const error = ref('');
    const services = ref([]);
    
    const formData = ref({
      username: '',
      email: '',
      password: '',
      confirmPassword: '',
      fullName: '',
      phoneNumber: '',
      address: '',
      pinCode: '',
      experienceYears: 0,
      serviceTypeId: '',
      description: '',
      documents: {
        idProof: null,
        addressProof: null,
        qualification: null
      }
    });
    
    // Fetch available services for professionals to choose from
    onMounted(async () => {
      try {
        const response = await api.get('/services');
        services.value = response.data;
      } catch (err) {
        console.error('Failed to fetch services:', err);
      }
    });
    
    const handleFileUpload = (event, docType) => {
      const file = event.target.files[0];
      if (file) {
        formData.value.documents[docType] = file;
      }
    };
    
    const validateForm = () => {
      // Reset error
      error.value = '';
      
      // Password validation
      if (formData.value.password !== formData.value.confirmPassword) {
        error.value = 'Passwords do not match';
        return false;
      }
      
      // Validate professional-specific requirements
      if (role.value === 'professional') {
        if (!formData.value.serviceTypeId) {
          error.value = 'Please select a service type';
          return false;
        }
        
        if (!formData.value.documents.idProof || !formData.value.documents.addressProof) {
          error.value = 'Please upload the required identity documents';
          return false;
        }
      }
      
      return true;
    };
    
    const register = async () => {
      if (!validateForm()) {
        return;
      }
      
      loading.value = true;
      
      try {
        // Create form data with files for upload
        const formDataToSend = new FormData();
        
        // Add basic registration details
        formDataToSend.append('username', formData.value.username);
        formDataToSend.append('email', formData.value.email);
        formDataToSend.append('password', formData.value.password);
        formDataToSend.append('role', role.value);
        formDataToSend.append('fullName', formData.value.fullName);
        
        // Use phoneNumber field name consistently
        formDataToSend.append('phoneNumber', formData.value.phoneNumber);
        
        // Add role-specific fields
        if (role.value === 'customer') {
          formDataToSend.append('address', formData.value.address);
          formDataToSend.append('pinCode', formData.value.pinCode);
        } else if (role.value === 'professional') {
          formDataToSend.append('experienceYears', formData.value.experienceYears);
          formDataToSend.append('serviceTypeId', formData.value.serviceTypeId);
          formDataToSend.append('description', formData.value.description);
          
          // Add document files
          if (formData.value.documents.idProof) {
            formDataToSend.append('idProof', formData.value.documents.idProof);
          }
          
          if (formData.value.documents.addressProof) {
            formDataToSend.append('addressProof', formData.value.documents.addressProof);
          }
          
          if (formData.value.documents.qualification) {
            formDataToSend.append('qualification', formData.value.documents.qualification);
          }
        }
        
        console.log('Sending registration data for role:', role.value);
        console.log('Using "phone" field for phoneNumber:', formData.value.phoneNumber);
        
        const response = await api.post('/auth/register', formDataToSend, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        });
        
        // Success: show different messages based on role
        if (role.value === 'professional') {
          // Redirect to success page with pending approval message
          router.push({
            path: '/registration-success',
            query: { 
              role: 'professional',
              pendingApproval: true 
            }
          });
        } else {
          // For customers, redirect to login
          router.push({
            path: '/login',
            query: { 
              registered: true 
            }
          });
        }
      } catch (err) {
        console.error('Registration error:', err);
        // Add more detailed error message handling
        if (err.response?.data?.message) {
          error.value = err.response.data.message;
        } else if (err.message?.includes('phone') || err.message?.includes('phone_number')) {
          error.value = 'Error with phone number format or field name. Please try again.';
          console.error('Phone field error details:', err);
        } else {
          error.value = 'Registration failed. Please try again.';
        }
      } finally {
        loading.value = false;
      }
    };
    
    return {
      role,
      loading,
      error,
      services,
      formData,
      handleFileUpload,
      register
    };
  }
};
</script>

<style scoped>
@import '@/assets/auth.css';

.register-logo {
  max-height: 60px;
  width: auto;
}

.document-upload {
  background-color: #f8f9fa;
  border-radius: 8px;
}
</style>
