<template>
  <div class="professional-approval">
    <div class="d-flex justify-content-between align-items-center mb-4">
      <h3 class="mb-0">
        {{ isSingleProfessional ? 'Professional Application Review' : 'Professional Approval Requests' }}
      </h3>
      <div>
        <router-link 
          :to="{ path: '/admin/dashboard' }"
          @click.prevent="$router.go(-1)"
          class="btn btn-outline-secondary me-2"
        >
          <i class="bi bi-arrow-left me-1"></i> Back
        </router-link>
        <button 
          class="btn btn-outline-primary" 
          @click="refreshData"
          :disabled="loading"
        >
          <i class="bi bi-arrow-clockwise me-1"></i> Refresh
        </button>
      </div>
    </div>
    
    <!-- Display content based on whether viewing all or single professional -->
    <div class="card mb-4">
      <div class="card-body">
        <!-- Loading state -->
        <div v-if="loading" class="d-flex justify-content-center py-5">
          <div class="spinner-border text-primary" role="status">
            <span class="visually-hidden">Loading...</span>
          </div>
        </div>
        
        <!-- Error state -->
        <div v-else-if="error" class="alert alert-danger">
          {{ error }}
        </div>
        
        <!-- Empty state -->
        <div v-else-if="pendingProfessionals.length === 0" class="text-center py-5">
          <i class="bi bi-check-circle display-4 text-success"></i>
          <h4 class="mt-3">No pending approval requests</h4>
          <p class="text-muted">
            {{ isSingleProfessional ? 'The specified professional does not require approval.' : 'All professional applications have been processed' }}
          </p>
        </div>
        
        <!-- List of pending professionals -->
        <div v-else class="professionals-list">
          <div v-for="professional in pendingProfessionals" :key="professional.id" class="professional-card mb-3 p-3 border rounded">
            <div class="row">
              <div class="col-md-8">
                <h5 class="mb-1">{{ professional.full_name || professional.username }}</h5>
                <p class="mb-0 text-muted">{{ professional.email }}</p>
                <p class="mb-2"><small class="text-muted">Registered on {{ formatDate(professional.created_at) }}</small></p>
                
                <div class="mb-2">
                  <span class="badge bg-primary me-2">{{ professional.service_name || 'No service selected' }}</span>
                  <span class="badge bg-secondary">{{ professional.experience_years }} years experience</span>
                </div>
                
                <p class="description mb-3">
                  {{ professional.description || 'No description provided' }}
                </p>
                
                <!-- Document badges -->
                <div class="documents mb-3">
                  <span class="badge bg-success me-2" v-if="professional.documents_count > 0">
                    <i class="bi bi-file-earmark-check me-1"></i> {{ professional.documents_count }} Documents Uploaded
                  </span>
                  <span class="badge bg-danger" v-else>
                    <i class="bi bi-file-earmark-x me-1"></i> No Documents
                  </span>
                </div>
              </div>
              
              <div class="col-md-4 text-md-end">
                <button 
                  class="btn btn-outline-primary mb-2 w-100" 
                  @click="viewDocuments(professional)"
                  :disabled="professional.documents_count === 0"
                >
                  <i class="bi bi-file-earmark-text me-1"></i> View Documents
                </button>
                <button 
                  class="btn btn-success mb-2 w-100" 
                  @click="approveProfessional(professional.id)"
                  :disabled="processingSingleRequest === professional.id || !isProfessionalApprovalReady(professional)"
                  :title="!isProfessionalApprovalReady(professional) ? 'All documents must be verified before approval' : ''"
                >
                  <span v-if="processingSingleRequest === professional.id" class="spinner-border spinner-border-sm me-1"></span>
                  <i v-else class="bi bi-check-circle me-1"></i> Approve
                </button>
                <button 
                  class="btn btn-danger w-100" 
                  @click="openRejectModal(professional)"
                  :disabled="processingSingleRequest === professional.id"
                >
                  <i class="bi bi-x-circle me-1"></i> Reject
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Documents Modal -->
    <div class="modal fade" id="documentsModal" tabindex="-1" ref="documentsModalRef">
      <div class="modal-dialog modal-lg">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Professional Documents</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingDocuments" class="text-center py-5">
              <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Loading documents...</span>
              </div>
            </div>
            
            <div v-else-if="documentError" class="alert alert-danger">
              {{ documentError }}
            </div>
            
            <div v-else-if="documents.length === 0" class="text-center py-4">
              <i class="bi bi-file-earmark-x display-4 text-muted"></i>
              <p class="mt-3">No documents available</p>
            </div>
            
            <div v-else>
              <div v-for="doc in documents" :key="doc.id" class="document-item mb-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="mb-0 text-capitalize">
                    <i class="bi bi-file-earmark me-1"></i>
                    {{ formatDocumentType(doc.document_type) }}
                  </h6>
                  <span class="text-muted small">Uploaded: {{ formatDate(doc.uploaded_at) }}</span>
                </div>
                
                <div class="document-preview p-2 border rounded">
                  <!-- Show image preview if it's an image file -->
                  <img 
                    v-if="isImageFile(doc.filename)"
                    :src="getDocumentUrl(doc)"
                    class="img-fluid mb-2 mx-auto d-block"
                    style="max-height: 300px;"
                    alt="Document Preview"
                  />
                  
                  <!-- Show PDF or other file info -->
                  <div v-else class="text-center py-3">
                    <i class="bi bi-file-earmark-pdf display-4 text-danger"></i>
                    <p class="mb-0 mt-2">{{ doc.filename }}</p>
                  </div>
                  
                  <div class="d-flex justify-content-center my-2">
                    <button class="btn btn-sm btn-primary" @click="openDocument(doc)">
                      <i class="bi bi-eye me-1"></i> View Full Document
                    </button>
                    <button 
                      class="btn btn-sm ms-2"
                      :class="doc.verified ? 'btn-success' : 'btn-outline-success'"
                      @click="toggleVerification(doc)"
                    >
                      <i class="bi" :class="doc.verified ? 'bi-check-circle-fill' : 'bi-check-circle'"></i>
                      {{ doc.verified ? 'Verified' : 'Mark as Verified' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Reject Modal -->
    <div class="modal fade" id="rejectModal" tabindex="-1" ref="rejectModalRef">
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">Reject Professional Application</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <p>You are about to reject this professional's application. Please provide a reason:</p>
            <div class="mb-3">
              <label for="rejectionReason" class="form-label">Rejection Reason</label>
              <textarea 
                v-model="rejectionReason" 
                class="form-control" 
                id="rejectionReason" 
                rows="3"
                placeholder="Example: Incomplete documentation, qualification mismatch, etc."
              ></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
            <button 
              type="button" 
              class="btn btn-danger" 
              @click="rejectProfessional"
              :disabled="processingSingleRequest"
            >
              <span v-if="processingSingleRequest" class="spinner-border spinner-border-sm me-1"></span>
              Reject Application
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Success Toast -->
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
          <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, onMounted, nextTick, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { Modal, Toast } from 'bootstrap';
import api from '@/services/api.service';

export default {
  name: 'ProfessionalApprovalView',
  
  setup() {
    // State
    const pendingProfessionals = ref([]);
    const loading = ref(false);
    const error = ref(null);
    const documents = ref([]);
    const loadingDocuments = ref(false);
    const documentError = ref(null);
    const selectedProfessional = ref(null);
    const processingSingleRequest = ref(null);
    const rejectionReason = ref('');
    const successMessage = ref('');
    
    // Router
    const route = useRoute();
    const router = useRouter();
    
    // Computed properties
    const isSingleProfessional = computed(() => {
      return !!route.query.professional_id;
    });
    
    // DOM refs
    const documentsModalRef = ref(null);
    const documentsModal = ref(null);
    const rejectModalRef = ref(null);
    const rejectModal = ref(null);
    const successToast = ref(null);
    
    // Initialize Bootstrap components
    onMounted(() => {
      // Initialize modals
      if (documentsModalRef.value) {
        documentsModal.value = new Modal(documentsModalRef.value);
      }
      
      if (rejectModalRef.value) {
        rejectModal.value = new Modal(rejectModalRef.value);
      }
      
      // Fetch data
      fetchPendingProfessionals();
    });
    
    // Methods
    const fetchPendingProfessionals = async () => {
      loading.value = true;
      error.value = null;
      pendingProfessionals.value = [];
      
      try {
        // Check if we have a specific professional_id in query params
        const professionalId = route.query.professional_id;
        let response;
        
        if (professionalId) {
          // Get a single professional with document verification status
          response = await api.get('/admin/professionals', {
            params: { 
              approved: 'false',
              active: 'true',
              include_verification: 'true'
            }
          });
          
          const professional = response.data.find(p => p.id == professionalId);
          if (professional) {
            pendingProfessionals.value = [professional];
          } else {
            error.value = 'The specified professional was not found or does not require approval.';
          }
        } else {
          // Get all pending professionals with document verification status
          response = await api.get('/admin/professionals', {
            params: { 
              approved: 'false',
              active: 'true',
              include_verification: 'true'
            }
          });
          pendingProfessionals.value = response.data || [];
        }
      } catch (err) {
        console.error('Failed to fetch pending professionals:', err);
        error.value = err.response?.data?.message || 'Failed to load pending professionals';
      } finally {
        loading.value = false;
      }
    };

    const refreshData = () => {
      fetchPendingProfessionals();
    };
    
    const viewDocuments = async (professional) => {
      selectedProfessional.value = professional;
      loadingDocuments.value = true;
      documentError.value = null;
      documents.value = [];
      
      if (documentsModal.value) {
        documentsModal.value.show();
      }
      
      try {
        const response = await api.get(`/admin/users/${professional.id}/documents`);
        documents.value = response.data;
      } catch (err) {
        console.error('Failed to fetch documents:', err);
        documentError.value = err.response?.data?.message || 'Failed to load documents';
      } finally {
        loadingDocuments.value = false;
      }
    };
    
    const openDocument = (document) => {
      // Open document in a new tab
      const documentUrl = getDocumentUrl(document);
      window.open(documentUrl, '_blank');
    };
    
    const getDocumentUrl = (document) => {
      // In a real application, this would be a URL to the document
      // For now, we'll assume it's served from a static path
      return `/api/documents/${document.id}`;
    };
    
    const isImageFile = (filename) => {
      if (!filename) return false;
      const ext = filename.split('.').pop().toLowerCase();
      return ['jpg', 'jpeg', 'png', 'gif'].includes(ext);
    };
    
    const toggleVerification = async (document) => {
      try {
        const response = await api.put(`/admin/documents/${document.id}/verify`, {
          verified: !document.verified
        });
        
        // Update the document in the array
        const index = documents.value.findIndex(d => d.id === document.id);
        if (index !== -1) {
          documents.value[index].verified = !document.verified;
        }
        
        // Update the professional's verification status if this was returned
        if (response.data.all_verified !== undefined && selectedProfessional.value) {
          const profIndex = pendingProfessionals.value.findIndex(p => p.id === selectedProfessional.value.id);
          if (profIndex !== -1) {
            pendingProfessionals.value[profIndex].documents_verified = response.data.all_verified;
          }
        }
        
        showSuccessToast(`Document ${documents.value[index].verified ? 'verified' : 'unverified'} successfully`);
      } catch (err) {
        console.error('Failed to toggle document verification:', err);
        documentError.value = err.response?.data?.message || 'Failed to update document verification status';
      }
    };

    // Check if all professional documents are verified before allowing approval
    const isProfessionalApprovalReady = (professional) => {
      // If the professional has documents_verified flag, use that
      if (professional.documents_verified) {
        return true;
      }
      
      // If the documents are currently loaded for this professional, check directly
      if (selectedProfessional.value && selectedProfessional.value.id === professional.id && documents.value.length > 0) {
        // All documents must be verified
        return documents.value.every(doc => doc.verified);
      }
      
      // By default, require checking documents first if they exist but aren't verified
      return professional.documents_count === 0;
    };
    
    const approveProfessional = async (professionalId) => {
      processingSingleRequest.value = professionalId;
      try {
        await api.put(`/admin/approve/${professionalId}`);
        
        showSuccessToast('Professional approved successfully');
        
        // If we came from user management, redirect back after a short delay
        if (isSingleProfessional.value) {
          setTimeout(() => {
            router.push('/admin/users');
          }, 1500);
        } else {
          // Otherwise remove from the list
          pendingProfessionals.value = pendingProfessionals.value.filter(p => p.id !== professionalId);
        }
      } catch (err) {
        console.error('Failed to approve professional:', err);
        // Improve error message to handle document verification errors
        if (err.response?.data?.error?.includes('unverified documents')) {
          error.value = 'Cannot approve: All documents must be verified first';
        } else {
          error.value = err.response?.data?.message || 'Failed to approve professional';
        }
      } finally {
        processingSingleRequest.value = null;
      }
    };
    
    const openRejectModal = (professional) => {
      selectedProfessional.value = professional;
      rejectionReason.value = '';
      
      if (rejectModal.value) {
        rejectModal.value.show();
      }
    };
    
    const rejectProfessional = async () => {
      try {
        if (rejectModal.value) {
          rejectModal.value.hide();
        }
        
        processingSingleRequest.value = selectedProfessional.value?.id;
        
        // Add rejection reason in request body
        await api.put(`/admin/reject/${selectedProfessional.value.id}`, {
          rejection_reason: rejectionReason.value
        });
        
        showSuccessToast('Professional application rejected');
        
        // If we came from user management, redirect back after a short delay
        if (isSingleProfessional.value) {
          setTimeout(() => {
            router.push('/admin/users');
          }, 1500);
        } else {
          // Otherwise refresh the list
          await fetchPendingProfessionals();
        }
      } catch (err) {
        console.error('Failed to reject professional:', err);
        error.value = err.response?.data?.message || 'Failed to reject professional';
      } finally {
        processingSingleRequest.value = null;
        rejectionReason.value = '';
      }
    };
    
    const formatDate = (dateString) => {
      if (!dateString) return 'N/A';
      const date = new Date(dateString);
      return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
    };
    
    const formatDocumentType = (type) => {
      if (!type) return 'Document';
      
      // Convert camelCase or snake_case to readable format
      return type
        .replace(/([A-Z])/g, ' $1') // Insert space before capital letters
        .replace(/_/g, ' ')         // Replace underscores with spaces
        .replace(/^\w/, c => c.toUpperCase()); // Capitalize first letter
    };
    
    const showSuccessToast = (message) => {
      successMessage.value = message;
      
      // Initialize and show toast
      nextTick(() => {
        if (successToast.value) {
          const toast = new Toast(successToast.value);
          toast.show();
        }
      });
    };
    
    return {
      pendingProfessionals,
      loading,
      error,
      documents,
      loadingDocuments,
      documentError,
      selectedProfessional,
      documentsModalRef,
      rejectModalRef,
      processingSingleRequest,
      rejectionReason,
      successMessage,
      successToast,
      isSingleProfessional,
      fetchPendingProfessionals,
      refreshData,
      viewDocuments,
      openDocument,
      getDocumentUrl,
      isImageFile,
      toggleVerification,
      approveProfessional,
      openRejectModal,
      rejectProfessional,
      formatDate,
      formatDocumentType,
      isProfessionalApprovalReady
    };
  }
};
</script>

<style scoped>
.professional-approval {
  padding: 1.5rem;
}

.professional-card {
  transition: all 0.2s ease;
}

.professional-card:hover {
  background-color: #f8f9fa;
  box-shadow: 0 0.125rem 0.25rem rgba(0, 0, 0, 0.075);
}

.description {
  max-height: 100px;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  line-clamp: 3;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
}

.document-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.toast-container {
  z-index: 1090;
}
</style>
