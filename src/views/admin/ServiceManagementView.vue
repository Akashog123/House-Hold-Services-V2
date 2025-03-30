<template>
  <div class="service-management">
    <div class="d-flex justify-content-between align-items-center mb-4 page-header">
      <h3>Service Management</h3>
      <button class="btn btn-primary" @click="openCreateModal">
        <i class="bi bi-plus-lg me-2"></i>Add New Service
      </button>
    </div>

    <!-- Service List -->
    <div class="card">
      <div class="card-body">
        <div class="table-responsive">
          <table class="table table-hover">
            <thead>
              <tr>
                <th>Name</th>
                <th>Base Price</th>
                <th>Duration (mins)</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="service in services" :key="service.id">
                <td>{{ service.name }}</td>
                <td>₹{{ service.base_price }}/-</td>
                <td>{{ service.avg_duration }}</td>
                <td>
                  <span :class="getStatusBadgeClass(service.status || 'active')">
                    {{ service.status || 'active' }}
                  </span>
                </td>
                <td>
                  <button 
                    v-if="service.image_path" 
                    class="btn btn-sm btn-outline-info me-2"
                    @click="previewImage(service)"
                    title="Preview Image"
                  >
                    <i class="bi bi-eye"></i>
                  </button>
                  <button 
                    class="btn btn-sm me-2"
                    :class="service.status === 'inactive' ? 'btn-outline-success' : 'btn-outline-secondary'"
                    @click="toggleServiceStatus(service)"
                  >
                    <i :class="service.status === 'inactive' ? 'bi bi-check-circle' : 'bi bi-x-circle'"></i>
                    {{ service.status === 'inactive' ? 'Activate' : 'Deactivate' }}
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-primary me-2"
                    @click="editService(service)"
                  >
                    <i class="bi bi-pencil"></i>
                  </button>
                  <button 
                    class="btn btn-sm btn-outline-danger"
                    @click="confirmDelete(service)"
                  >
                    <i class="bi bi-trash"></i>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>

    <!-- Service Modal -->
    <div 
      class="modal fade" 
      id="serviceModal" 
      tabindex="-1"
      ref="serviceModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-white">
              {{ isEditing ? 'Edit Service' : 'Create New Service' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeModal"
            ></button>
          </div>
          <div class="modal-body">
            <div v-if="formError" class="alert alert-danger mb-3">
              {{ formError }}
            </div>
            <form @submit.prevent="saveService" class="needs-validation" novalidate>
              <div class="mb-3">
                <label class="form-label">Service Name * </label>
                <input 
                  v-model="serviceForm.name"
                  type="text"
                  class="form-control"
                  required
                  minlength="2"
                  maxlength="100"
                >
                <div class="invalid-feedback">
                  Please enter a service name (2-100 characters)
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Base Price (₹) *</label>
                <input 
                  v-model="serviceForm.base_price"
                  type="number"
                  step="0.01"
                  min="0"
                  class="form-control"
                  required
                >
                <div class="invalid-feedback">
                  Please enter a valid base price
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Duration (minutes) *</label>
                <input 
                  v-model="serviceForm.avg_duration"
                  type="number"
                  min="1"
                  class="form-control"
                  required
                >
                <div class="invalid-feedback">
                  Please enter a valid duration in minutes
                </div>
              </div>

              <div class="mb-3">
                <label class="form-label">Description</label>
                <textarea 
                  v-model="serviceForm.description"
                  class="form-control"
                  rows="3"
                  maxlength="500"
                ></textarea>
              </div>

              <div class="mb-3">
                <label class="form-label">Service Image</label>
                <input 
                  type="file"
                  class="form-control"
                  accept="image/*"
                  @change="handleImageChange"
                  ref="imageInput"
                >
                <small class="form-text text-muted">
                  Upload a reference image for this service (PNG, JPG, JPEG, GIF)
                </small>
                
                <!-- Preview current image -->
                <div v-if="imagePreview || (isEditing && serviceForm.image_path)" class="mt-2">
                  <div class="image-preview-container">
                    <img 
                      :src="imagePreview || getImageUrl(serviceForm.image_path)" 
                      alt="Service image preview" 
                      class="img-thumbnail service-image-preview"
                    >
                    <button 
                      type="button" 
                      class="btn btn-sm btn-danger remove-image-btn" 
                      @click="removeImage"
                    >
                      <i class="bi bi-x"></i>
                    </button>
                  </div>
                </div>
              </div>

              <div class="modal-footer">
                <button 
                  type="button" 
                  class="btn btn-secondary" 
                  @click="closeModal"
                >
                  Cancel
                </button>
                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  {{ isEditing ? 'Update' : 'Create' }}
                  <span v-if="loading" class="spinner-border spinner-border-sm ms-1" role="status"></span>
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Modal -->
    <div 
      class="modal fade" 
      id="deleteModal" 
      tabindex="-1"
      ref="deleteModal"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-white">Confirm Delete</h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeDeleteModal"
            ></button>
          </div>
          <div class="modal-body">
            <p>Are you sure you want to delete this service?</p>
            <p class="text-danger"><strong>This action cannot be undone.</strong></p>
          </div>
          <div class="modal-footer">
            <button 
              type="button" 
              class="btn btn-secondary" 
              @click="closeDeleteModal"
            >
              Cancel
            </button>
            <button 
              type="button" 
              class="btn btn-danger"
              :disabled="loading"
              @click="deleteService"
            >
              Delete
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Image Preview Modal -->
    <div 
      class="modal fade" 
      id="imagePreviewModal" 
      tabindex="-1"
      ref="imagePreviewModal"
    >
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title text-white">
              {{ previewService ? previewService.name : 'Image Preview' }}
            </h5>
            <button 
              type="button" 
              class="btn-close" 
              @click="closeImagePreviewModal"
            ></button>
          </div>
          <div class="modal-body text-center">
            <img 
              v-if="previewService && previewService.image_path" 
              :src="getImageUrl(previewService.image_path)"
              alt="Service image preview" 
              class="img-fluid service-preview-image"
            >
            <div v-else class="alert alert-info">
              No image available for this service.
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Toast container for notifications -->
    <div class="toast-container position-fixed bottom-0 end-0 p-3">
      <div 
        class="toast align-items-center text-white bg-success border-0" 
        role="alert"
        aria-live="assertive" 
        aria-atomic="true"
        ref="successToast"
      >
        <div class="d-flex">
          <div class="toast-body">
            {{ successMessage }}
          </div>
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { useStore } from 'vuex'
import adminService from '@/services/admin.service'
import { Modal, Toast } from 'bootstrap'

export default {
  name: 'ServiceManagementView',
  
  setup() {
    const router = useRouter()
    const store = useStore()

    const services = ref([])
    const loading = ref(false)
    const isEditing = ref(false)
    const currentServiceId = ref(null)
    const serviceModal = ref(null)
    const deleteModal = ref(null)
    const formError = ref(null)
    const successMessage = ref('')
    const successToast = ref(null)
    const imageInput = ref(null)
    const imagePreview = ref(null)
    const imageRemoved = ref(false)
    const imagePreviewModal = ref(null)
    const previewService = ref(null)

    const serviceForm = ref({
      name: '',
      base_price: '',
      avg_duration: '',
      description: '',
      image: null,
      image_path: ''
    })

    onMounted(() => {
      // Enhanced auth check
      console.log("ServiceManagementView mounted, checking auth")
      const token = store.getters['auth/token']
      const user = store.getters['auth/user']
      console.log("Auth token exists:", !!token)
      console.log("User exists:", !!user, "Role:", user?.role)
      
      if (!token || !user) {
        console.log("Not authenticated, redirecting to login")
        router.push('/login')
        return
      }

      if (user.role !== 'admin') {
        console.log("Not admin, redirecting to unauthorized")
        router.push('/unauthorized')
        return
      }
      
      // Continue with component setup
      fetchServices()
    })

    // Show success toast notification
    const showSuccessToast = (message) => {
      successMessage.value = message;
      nextTick(() => {
        if (successToast.value) {
          const toastInstance = new Toast(successToast.value);
          toastInstance.show();
        }
      });
    }

    const fetchServices = async () => {
      loading.value = true
      try {
        console.log("Fetching services from admin service")
        const response = await adminService.getAllServices()
        console.log("Services response:", response)
        
        if (Array.isArray(response.data)) {
          services.value = response.data
        } else {
          console.error("Unexpected services response format:", response)
          services.value = []
        }
        console.log("Processed services:", services.value)
      } catch (err) {
        console.error('Failed to fetch services:', err)
        // Add user feedback
        if (err.response?.status === 422) {
          // Handle validation errors
          const errorMessage = err.response.data.message || 'Validation error occurred'
          formError.value = errorMessage
        }
      } finally {
        loading.value = false
      }
    }

    const openCreateModal = () => {
      isEditing.value = false
      currentServiceId.value = null
      serviceForm.value = {
        name: '',
        base_price: '',
        avg_duration: '',
        description: '',
        image: null,
        image_path: ''
      }
      imagePreview.value = null
      imageRemoved.value = false
      
      // Make sure modal reference exists
      if (serviceModal.value) {
        console.log("Opening create modal");
        new Modal(serviceModal.value).show()
      } else {
        console.error("Service modal reference is null");
        formError.value = "System error: Could not open modal";
      }
    }

    const editService = (service) => {
      console.log("Edit service called with:", service);
      
      if (!service || !service.id) {
        console.error("Invalid service object:", service);
        formError.value = "Cannot edit: Invalid service data";
        return;
      }
      
      isEditing.value = true
      currentServiceId.value = service.id
      imagePreview.value = null
      imageRemoved.value = false
      
      // Create a new object for the form to avoid modifying the original service
      serviceForm.value = {
        name: service.name,
        base_price: service.base_price,
        avg_duration: service.avg_duration,
        description: service.description || '',
        status: service.status || 'active',
        image_path: service.image_path || '',
        image: null
      }
      
      // Make sure modal reference exists
      if (serviceModal.value) {
        console.log("Opening edit modal for service ID:", service.id);
        nextTick(() => {
          new Modal(serviceModal.value).show();
        });
      } else {
        console.error("Service modal reference is null");
        formError.value = "System error: Could not open modal";
      }
    }

    const closeModal = () => {
      const modalInstance = Modal.getInstance(serviceModal.value)
      if (modalInstance) {
        modalInstance.hide()
        // Reset form error and loading state when modal closes
        formError.value = null
        loading.value = false
      }
    }

    const validateForm = () => {
      formError.value = null
      
      if (!serviceForm.value.name?.trim()) {
        formError.value = 'Service name is required'
        return false
      }
      
      if (!serviceForm.value.base_price || serviceForm.value.base_price <= 0) {
        formError.value = 'Base price must be greater than 0'
        return false
      }
      
      if (!serviceForm.value.avg_duration || serviceForm.value.avg_duration < 1) {
        formError.value = 'Duration must be at least 1 minute'
        return false
      }
      
      return true
    }

    const saveService = async () => {
      if (!validateForm()) {
        return
      }

      loading.value = true
      formError.value = null
      
      try {
        console.log("Saving service:", isEditing.value ? "update" : "create");
        
        // Create a form data object with the form values and image if present
        const formData = new FormData();
        formData.append('name', serviceForm.value.name?.trim());
        formData.append('base_price', parseFloat(serviceForm.value.base_price) || 0);
        formData.append('description', serviceForm.value.description?.trim() || '');
        formData.append('avg_duration', parseInt(serviceForm.value.avg_duration) || 0);
        
        // Status is only relevant for updates
        if (isEditing.value && serviceForm.value.status) {
          formData.append('status', serviceForm.value.status);
        }
        
        // Add image if one is selected
        if (serviceForm.value.image) {
          formData.append('image', serviceForm.value.image);
        }
        
        // If image was removed, we need to handle that
        if (imageRemoved.value) {
          formData.append('remove_image', 'true');
        }
        
        let response;
        
        if (isEditing.value) {
          if (!currentServiceId.value) {
            throw new Error("Cannot update service: Missing service ID");
          }
          response = await adminService.updateService(currentServiceId.value, serviceForm.value)
          console.log(`Service ${currentServiceId.value} updated successfully`);
          showSuccessToast("Service updated successfully");
        } else {
          response = await adminService.createService(serviceForm.value)
          console.log("New service created successfully");
          showSuccessToast("New service created successfully");
        }
        
        console.log("Service operation response:", response);
        await fetchServices()
        closeModal()
      } catch (error) {
        console.error('Failed to save service:', error)
        if (error.response?.status === 401) {
          router.push('/login')
        } else if (error.response?.status === 422) {
          formError.value = error.response.data.message || 
                           Object.values(error.response.data.errors || {}).flat().join(', ') ||
                           'Validation error occurred'
        } else {
          formError.value = error.message || 'An error occurred while saving the service'
        }
      } finally {
        loading.value = false
      }
    }

    // Handle image selection
    const handleImageChange = (event) => {
      const file = event.target.files[0];
      if (!file) return;
      
      // Check if file is an image
      if (!file.type.startsWith('image/')) {
        formError.value = 'Please select an image file';
        return;
      }
      
      // Store the file for upload
      serviceForm.value.image = file;
      imageRemoved.value = false;
      
      // Create a preview
      const reader = new FileReader();
      reader.onload = e => {
        imagePreview.value = e.target.result;
      };
      reader.readAsDataURL(file);
    };
    
    // Remove the selected image
    const removeImage = () => {
      serviceForm.value.image = null;
      imagePreview.value = null;
      imageRemoved.value = true;
      
      // Clear the file input
      if (imageInput.value) {
        imageInput.value.value = '';
      }
    };
    
    // Get the URL for an image path
    const getImageUrl = (path) => {
      if (!path) return '';
      
      // Check if the path is already a full URL
      if (path.startsWith('http')) {
        return path;
      }
      
      // Otherwise, prepend the API base URL - using Vite's environment variables format
      return `${import.meta.env.VITE_API_URL || ''}${path}`;
    };

    const confirmDelete = (service) => {
      console.log("confirmDelete called for service:", service);
      if (!service || !service.id) {
        console.error("Invalid service object or missing ID:", service);
        return;
      }
      
      currentServiceId.value = service.id;
      console.log("Setting currentServiceId to:", currentServiceId.value);
      
      // Store the ID in the DOM element as a data attribute for backup
      if (deleteModal.value) {
        deleteModal.value.dataset.serviceId = service.id;
        console.log("Stored serviceId in dataset:", deleteModal.value.dataset.serviceId);
        nextTick(() => {
          new Modal(deleteModal.value).show();
        });
      } else {
        console.error("Delete modal reference is null");
        formError.value = "System error: Could not open delete confirmation";
      }
    }

    const closeDeleteModal = () => {
      const modalInstance = Modal.getInstance(deleteModal.value);
      if (modalInstance) {
        modalInstance.hide();
        // Reset loading state when modal closes
        loading.value = false;
      }
    }

    const deleteService = async () => {
      loading.value = true;
      formError.value = null;
      
      try {
        // Double-check the serviceId (backup from data attribute if needed)
        if (!currentServiceId.value && deleteModal.value?.dataset?.serviceId) {
          console.log("Recovering serviceId from dataset:", deleteModal.value.dataset.serviceId);
          currentServiceId.value = parseInt(deleteModal.value.dataset.serviceId);
        }
        
        if (!currentServiceId.value) {
          throw new Error("Service ID is missing. Cannot delete service.");
        }
        
        console.log("Deleting service with ID:", currentServiceId.value);
        const response = await adminService.deleteService(currentServiceId.value);
        console.log("Delete response:", response);
        
        // Remove service from the local list for instant UI update
        services.value = services.value.filter(s => s.id !== currentServiceId.value);
        
        // Show success message
        showSuccessToast(`Service deleted successfully`);
        console.log(`Service ID ₹{currentServiceId.value} deleted successfully`);
        
        closeDeleteModal();
      } catch (error) {
        console.error('Failed to delete service:', error);
        
        // Handle different error scenarios
        if (error.response?.status === 401) {
          console.log("Unauthorized: Redirecting to login");
          router.push('/login');
        } else if (error.response?.status === 403) {
          formError.value = 'You do not have permission to delete this service';
        } else if (error.response?.status === 404) {
          formError.value = 'Service not found';
          closeDeleteModal(); // Close modal for missing services
        } else if (error.response?.status === 422) {
          formError.value = 'Service cannot be deleted: it is being used by active bookings';
        } else {
          formError.value = error.message || 'Failed to delete service';
        }
      } finally {
        loading.value = false;
      }
    }

    const toggleServiceStatus = async (service) => {
      try {
        loading.value = true;
        formError.value = null;
  
        // Log initial state
        console.log(`Before toggle - Service ID: ${service.id}, Current status: ${service.status}`);
        
        // Toggle between active and inactive
        const newStatus = service.status === 'inactive' ? 'active' : 'inactive';
        console.log(`Status to be changed to: ${newStatus}`);
        
        // Create a properly formatted service update object with all required fields
        const updatedService = {
          name: service.name,
          base_price: parseFloat(service.base_price) || 0,
          description: service.description || '',
          avg_duration: parseInt(service.avg_duration) || 0,
          status: newStatus
        };
        
        console.log('Sending update to backend:', JSON.stringify(updatedService));
        const response = await adminService.updateService(service.id, updatedService);
        console.log('Full response from backend:', response);
        
        if (response.data) {
          console.log('Response data:', JSON.stringify(response.data));
          
          const returnedStatus = response.data.status;
          console.log(`Status returned from backend: ${returnedStatus}`);
          
          // Use the status from the response if available
          service.status = returnedStatus || newStatus;
        } else {
          service.status = newStatus;
        }
        
        console.log(`After update - Service ID: ${service.id}, New status: ${service.status}`);
        
        // Show success message
        showSuccessToast(`Service ${service.status === 'active' ? 'activated' : 'deactivated'} successfully`);
        
        // Refresh data from server to ensure consistency
        await fetchServices();
      } catch (error) {
        console.error('Failed to toggle service status:', error);
        formError.value = error.message || 'Failed to update service status';
      } finally {
        loading.value = false;
      }
    };

    const previewImage = (service) => {
      if (!service || !service.image_path) {
        console.warn("No image available to preview for service:", service);
        return;
      }
      
      previewService.value = service;
      
      // Make sure modal reference exists
      if (imagePreviewModal.value) {
        nextTick(() => {
          new Modal(imagePreviewModal.value).show();
        });
      } else {
        console.error("Image preview modal reference is null");
      }
    }

    const closeImagePreviewModal = () => {
      const modalInstance = Modal.getInstance(imagePreviewModal.value);
      if (modalInstance) {
        modalInstance.hide();
        // Reset preview service after modal closes
        setTimeout(() => {
          previewService.value = null;
        }, 300);
      }
    }

    const getStatusBadgeClass = (status) => {
      const classes = {
        active: 'badge bg-success',
        inactive: 'badge bg-danger',
        pending: 'badge bg-warning'
      }
      return classes[status] || 'badge bg-secondary'
    }

    return {
      services,
      loading,
      isEditing,
      serviceForm,
      serviceModal,
      deleteModal,
      formError,
      successToast,
      successMessage,
      imageInput,
      imagePreview,
      handleImageChange,
      removeImage,
      getImageUrl,
      openCreateModal,
      editService,
      closeModal,
      saveService,
      confirmDelete,
      closeDeleteModal,
      deleteService,
      getStatusBadgeClass,
      showSuccessToast,
      toggleServiceStatus,
      imagePreviewModal,
      previewService,
      previewImage,
      closeImagePreviewModal
    }
  }
}
</script>

<style scoped>
.service-management {
  padding: 1.5rem;
}

.table th {
  font-weight: 600;
}

.badge {
  font-weight: 500;
}

.modal-header {
  background-color: var(--primary);
  color: white;
}

.modal-header .btn-close {
  filter: brightness(0) invert(1);
}

/* Toast styles */
.toast-container {
  z-index: 9999;
}

.no-image {
  width: 50px;
  height: 50px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f0f0f0;
  border-radius: 4px;
  font-size: 10px;
  color: #666;
}

.image-preview-container {
  position: relative;
  display: inline-block;
}

.service-image-preview {
  max-width: 200px;
  max-height: 200px;
}

.remove-image-btn {
  position: absolute;
  top: 5px;
  right: 5px;
  border-radius: 50%;
  padding: 0.25rem 0.5rem;
}

/* Image preview modal styles */
.service-preview-image {
  max-height: 70vh;
  max-width: 100%;
}
</style>
