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
                class="btn btn-danger w-100 mb-2" 
                @click="openRejectModal(professional)"
                :disabled="processingSingleRequest === professional.id"
              >
                <i class="bi bi-x-circle me-1"></i> Reject
              </button>
              
              <!-- Verification status indicator -->
              <div class="verification-status mt-2 text-center">
                <small v-if="isProfessionalApprovalReady(professional)" class="text-success">
                  <i class="bi bi-check-circle-fill me-1"></i> All documents verified
                </small>
                <small v-else class="text-warning">
                  <i class="bi bi-exclamation-circle-fill me-1"></i> Verification required
                </small>
                
                <!-- Document verification status details -->
                <div class="document-status-details mt-1" v-if="professional.documents_status">
                  <div class="d-flex flex-column small">
                    <span v-for="(verified, docType) in professional.documents_status" :key="docType"
                         :class="verified ? 'text-success' : 'text-muted'">
                      <i class="bi" :class="verified ? 'bi-check-circle-fill' : 'bi-circle'"></i>
                      {{ formatDocumentType(docType) }}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Documents Modal -->
    <div>
    <div class="modal" id="documentsModal" tabindex="-1" ref="documentsModalRef">
      <div class="modal-dialog modal-md">
        <div class="modal-content">
          <div class="modal-header bg-primary">
            <h5 class="modal-title text-white">Professional's Documents</h5>
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
                
                <div class="d-flex align-items-center justify-content-between">
                  <!-- Left column: Icon and filename -->
                  <div class="document-info d-flex align-items-center">
                    <i class="bi bi-file-earmark text-danger me-3" style="font-size: 2rem;"></i>
                    <p class="mb-0">{{ doc.filename }}</p>
                  </div>
                  
                  <!-- Right column: Action buttons -->
                  <div class="document-actions">
                    <button class="btn btn-sm btn-primary me-2" @click="openDocument(doc.id)">
                      <i class="bi bi-eye me-1"></i> View
                    </button>
                    <button 
                      class="btn btn-sm"
                      :class="doc.verified ? 'btn-success' : 'btn-outline-success'"
                      @click="toggleVerification(doc)"
                      :disabled="verifyingDocId === doc.id"
                    >
                      <span v-if="verifyingDocId === doc.id" class="spinner-border spinner-border-sm me-1"></span>
                      <i v-else class="bi" :class="doc.verified ? 'bi-check-circle-fill' : 'bi-check-circle'"></i>
                      {{ doc.verified ? 'Verified' : 'Verify' }}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
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
                placeholder="Enter reason for rejection (optional)"
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
    const verifyingDocId = ref(null);
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
            // Log the verification status for debugging
            console.log("Professional verification status:", professional.documents_verified);
            console.log("Professional documents status:", professional.documents_status);
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
    
    const openDocument = async (documentId) => {
      try {
        // Fetch the document with proper authorization through API service
        const response = await api.get(`/documents/${documentId}`, {
          responseType: 'blob', 
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}`
          }
        });
        
        // Create a blob URL from the response data
        const blob = new Blob([response.data], { type: response.headers['content-type']});
        const bloburl = window.URL.createObjectURL(blob);
        
        // Open the blob URL in a new tab
        window.open(bloburl, '_blank');
      } catch (err) {
        console.error('Failed to open document:', err);
        documentError.value = 'Failed to open document. Please try again.';
      }
    };
    
    const toggleVerification = async (document) => {
      try {
        // Set the current document as being verified
        verifyingDocId.value = document.id;
        documentError.value = null;
        
        // Call the API with the opposite of current verification status
        const response = await api.put(`/admin/documents/${document.id}/verify`, {
          verified: !document.verified
        });
        
        // Only update the UI after backend confirms the change
        if (response.data && response.data.document) {
          // Update the document in the array using the returned data
          const index = documents.value.findIndex(d => d.id === document.id);
          if (index !== -1) {
            documents.value[index].verified = response.data.document.verified;
          }
          
          // Update the professional's verification status if this was returned
          if (response.data.all_verified !== undefined && selectedProfessional.value) {
            const profIndex = pendingProfessionals.value.findIndex(p => p.id === selectedProfessional.value.id);
            if (profIndex !== -1) {
              pendingProfessionals.value[profIndex].documents_verified = response.data.all_verified;
              
              // Also update the documents_status for this document type
              if (pendingProfessionals.value[profIndex].documents_status) {
                pendingProfessionals.value[profIndex].documents_status[document.document_type] = 
                  response.data.document.verified;
              }
            }
          }
          
          showSuccessToast(
            `Document ${response.data.document.verified ? 'verified' : 'unverified'} successfully`
          );
        }
      } catch (err) {
        console.error('Failed to toggle document verification:', err);
        documentError.value = err.response?.data?.message || 'Failed to update document verification status';
      } finally {
        // Clear the verifying state regardless of success or failure
        verifyingDocId.value = null;
      }
    };

    // Check if all professional documents are verified before allowing approval
    const isProfessionalApprovalReady = (professional) => {
      console.log(`Checking approval readiness for professional ID ${professional.id}:`, professional);
      
      // Check if the professional object is valid
      if (!professional) {
        console.log("Invalid professional object");
        return false;
      }
      
      // First check: If the professional has explicit documents_verified flag, use that
      if (professional.documents_verified === true) {
        console.log(`Professional ${professional.id} has documents_verified=true flag`);
        return true;
      }
      
      // If we've loaded documents for this professional, check them directly
      if (
        selectedProfessional.value && 
        selectedProfessional.value.id === professional.id && 
        documents.value.length > 0
      ) {
        console.log(`Checking ${documents.value.length} documents for professional ${professional.id}`);
        
        // Check if all three required document types exist and are verified
        const requiredDocTypes = ['idProof', 'addressProof', 'qualification'];
        const verifiedDocs = {};
        
        // Initialize all document types as false first
        requiredDocTypes.forEach(type => {
          verifiedDocs[type] = false;
        });
        
        // Then mark the ones that are verified
        documents.value.forEach(doc => {
          console.log(`Document ${doc.id}, type: ${doc.document_type}, verified: ${doc.verified}`);
          if (requiredDocTypes.includes(doc.document_type)) {
            verifiedDocs[doc.document_type] = doc.verified === true;
          }
        });
        
        console.log("Verified status:", verifiedDocs);
        
        // Make sure all three document types exist and are verified
        const isReady = requiredDocTypes.every(type => verifiedDocs[type] === true);
        console.log(`Professional ${professional.id} approval readiness (based on documents): ${isReady}`);
        return isReady;
      }
      
      // Check if we have document status in the professional object
      if (professional.documents_status) {
        console.log("Documents status from API:", professional.documents_status);
        
        // Explicitly check all three required types
        const requiredTypes = ['idProof', 'addressProof', 'qualification'];
        const hasAllRequired = requiredTypes.every(type => 
          typeof professional.documents_status[type] !== 'undefined'
        );
        
        if (!hasAllRequired) {
          console.log("Missing one or more required document types");
          return false;
        }
        
        // Check if all required documents are verified
        const isReady = requiredTypes.every(type => 
          professional.documents_status[type] === true
        );
        
        console.log(`Professional ${professional.id} document status:`, 
                   requiredTypes.map(t => `${t}: ${professional.documents_status[t]}`).join(', '));
        console.log(`Professional ${professional.id} approval readiness (based on status): ${isReady}`);
        return isReady;
      }
      
      // By default, require checking documents first - not ready for approval
      console.log(`Professional ${professional.id} is not ready for approval (no status info available)`);
      return false;
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
      verifyingDocId,
      fetchPendingProfessionals,
      refreshData,
      viewDocuments,
      openDocument,
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
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  max-height: 100px;
}

.document-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.toast-container {
  z-index: 1090;
}

.verification-status {
  font-size: 0.8rem;
}

.document-status-details {
  font-size: 0.75rem;
  text-align: left;
  margin-left: 1.5rem;
}
</style>
