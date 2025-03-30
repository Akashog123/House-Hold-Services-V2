<template>
  <div class="user-management">
    <!-- Page Header -->
    <div class="d-flex justify-content-between align-items-center mb-4 page-header">
      <h3>User Management</h3>
    </div>
    
    <!-- Alert for pending approvals -->
    <div v-if="pendingApprovals > 0" class="alert alert-warning mb-4">
      <div class="d-flex justify-content-between align-items-center">
        <span>
          <i class="bi bi-exclamation-triangle-fill me-2"></i>
          <strong>{{ pendingApprovals }}</strong> professional registration(s) pending approval
        </span>
        <router-link to="/admin/approvals" class="btn btn-sm btn-primary">
          View Pending Approvals
        </router-link>
      </div>
    </div>
    
    <!-- User filter controls -->
    <div class="card mb-4">
      <div class="card-body">
        <div class="row g-3">
          <div class="col-12 col-md-4">
            <label class="form-label fw-bold">Filter by Type:</label>
            <select v-model="userTypeFilter" class="form-select">
              <option value="all">All Users</option>
              <option value="professional">Professionals</option>
              <option value="customer">Customers</option>
            </select>
          </div>
          
          <div class="col-12 col-md-4">
            <label class="form-label fw-bold">Status:</label>
            <select v-model="userStatusFilter" class="form-select">
              <option value="all">All</option>
              <option value="approved">Approved</option>
              <option value="pending">Pending Approval</option>
              <option value="blocked">Blocked</option>
            </select>
          </div>
          
          <div class="col-12 col-md-4">
            <label class="form-label fw-bold">Search:</label>
            <input type="text" v-model="searchQuery" placeholder="Search username..." class="form-control" />
          </div>
        </div>
      </div>
    </div>
    
    <!-- User List -->
    <div class="card">
      <div class="card-body">
        <div v-if="loading" class="d-flex justify-content-center py-5">
          <div class="spinner-border" role="status">
            <span class="visually-hidden">Loading users...</span>
          </div>
        </div>
        
        <div v-if="error" class="alert alert-danger">{{ error }}</div>
        
        <div class="table-responsive">
          <table v-if="!loading && !error && filteredUsers.length > 0" class="table table-hover">
            <thead>
              <tr>
                <th>Username</th>
                <th>Email</th>
                <th>Role</th>
                <th>Status</th>
                <th>Created</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'table-light': !user.is_active }">
                <td>{{ user.username }}</td>
                <td>{{ user.email }}</td>
                <td>{{ user.role }}</td>
                <td>
                  <span v-if="!user.is_active" class="badge bg-danger">Blocked</span>
                  <span v-else-if="user.is_approved" class="badge bg-success">Approved</span>
                  <span v-else class="badge bg-info" style="width: 9ch;">Pending</span>
                </td>
                <td>{{ formatDate(user.created_at) }}</td>
                <td>
                  <div class="d-flex gap-2">
                    
                    <button 
                      v-if="(user.role === 'professional' || user.role === 'customer') && user.is_approved && user.is_active" 
                      class="btn btn-sm btn-secondary" 
                      @click="blockUser(user.id)">
                      Block
                    </button>
                    <button 
                      v-if="!user.is_active && user.is_approved" 
                      class="btn btn-sm btn-success" 
                      @click="unblockUser(user.id)">
                      Unblock
                    </button>

                    <button 
                      v-if="user.role === 'professional' && user.is_approved" 
                      class="btn btn-sm btn-primary" 
                      @click="viewDocuments(user.id)"
                      :disabled="loading || user.documents_count === 0"
                      title="View Documents"
                    >
                      <i class="bi bi-file-earmark-text"></i>
                    </button>

                    <button 
                      v-if="user.role === 'professional' && user.is_approved"
                      class="btn btn-sm btn-primary ratings-btn"
                      :id="`ratings-btn-${user.id}`"
                      data-bs-toggle="popover"
                      data-bs-trigger="hover focus"
                      data-bs-html="true"
                      data-bs-custom-class="reviews-popover hover-popover"
                      title="Ratings & Reviews"
                      data-bs-content="Loading reviews..."
                      @mouseover="initializeReviewsPopover(user.id)">
                      <i class="bi bi-star-fill text-warning"></i>
                    </button>

                    <router-link 
                      v-if="user.role === 'professional' && !user.is_approved" 
                      class="btn btn-sm btn-warning"
                      style="width: 6ch;"
                      :to="{ path: '/admin/approvals', query: { professional_id: user.id }}"
                      title="View"
                    >
                      View
                    </router-link>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
        
        <div v-if="!loading && !error && filteredUsers.length === 0" class="text-center py-5">
          <i class="bi bi-search fs-2 text-muted mb-3"></i>
          <p class="text-muted">No users found matching your filters.</p>
        </div>
      </div>
    </div>

    <!-- Documents Modal -->
    <div class="modal fade" id="documentsModal" tabindex="-1" ref="documentsModalRef">
      <div class="modal-dialog modal-md">
        <div class="modal-content">
          <div class="modal-header bg-primary">
            <h5 class="modal-title text-white">Professional's Documents</h5>
            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
          </div>
          <div class="modal-body">
            <div v-if="loadingDocuments" class="text-center py-5">
              <div class="spinner-border" role="status">
                <span class="visually-hidden">Loading...</span>
              </div>
            </div>
            
            <div v-else-if="documentError" class="alert alert-danger">
              {{ documentError }}
            </div>
            
            <div v-else-if="documents.length === 0" class="text-center py-4">
              <i class="bi bi-file-earmark-x display-6 text-muted"></i>
              <p class="mt-3">No documents available</p>
            </div>
            
            <div v-else>
              <div v-for="doc in documents" :key="doc.id" class="document-item mb-4">
                <div class="d-flex justify-content-between align-items-center mb-2">
                  <h6 class="mb-0 text-capitalize">
                    <i class="bi bi-file-earmark me-1"></i>
                    {{ formatDocumentType(doc.document_type) }}
                  </h6>
                  <span class="badge" :class="doc.verified ? 'bg-success' : 'bg-warning'">
                    {{ doc.verified ? 'Verified' : 'Not Verified' }}
                  </span>
                </div>
                
                <div class="document-preview p-2 border border-2 border-secondary-subtle rounded">
                  <div class="d-flex justify-content-center my-2">
                    <button @click="viewDocument(doc.id)" class="btn btn-sm btn-primary">
                      <i class="bi bi-eye me-1"></i> View Document
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Hidden templates for popover content -->
    <div style="display: none;">
      <div id="reviews-popover-template">
        <div class="reviews-summary mb-2">
          <div class="d-flex align-items-center mb-1">
            <strong class="me-2">Rating:</strong>
            <div class="ratings-stars">
              <template v-for="i in 5" :key="i">
                <i class="bi" :class="i <= Math.round(popoverData.averageRating) ? 'bi-star-fill text-warning' : 'bi-star'"></i>
              </template>
            </div>
            <span class="ms-1">{{ popoverData.averageRating }}/5</span>
          </div>
          <div><strong>Total Reviews:</strong> {{ popoverData.totalReviews }}</div>
        </div>
        
        <div v-if="popoverData.reviews.length" class="reviews-list">
          <hr>
          <div v-for="(review, index) in popoverData.reviews" :key="index" :class="index > 0 ? 'mt-3' : ''">
            <div class="d-flex align-items-center">
              <div class="ratings-stars">
                <template v-for="i in 5" :key="i">
                  <i class="bi" :class="i <= review.rating ? 'bi-star-fill text-warning' : 'bi-star'"></i>
                </template>
              </div>
              <small class="ms-1 text-muted">{{ formatReviewDate(review.created_at) }}</small>
            </div>
            <div class="review-comment">{{ review.comment || 'No comment provided.' }}</div>
          </div>
          
          <div class="popover-pagination mt-3 d-flex justify-content-between align-items-center">
            <button class="btn btn-sm btn-outline-secondary" 
                    :disabled="popoverData.currentPage === 1"
                    @click="changePopoverPage(popoverData.currentPage - 1)">
              <i class="bi bi-chevron-left"></i>
            </button>
            <span>Page {{ popoverData.currentPage }} of {{ popoverData.totalPages }}</span>
            <button class="btn btn-sm btn-outline-secondary" 
                    :disabled="popoverData.currentPage === popoverData.totalPages"
                    @click="changePopoverPage(popoverData.currentPage + 1)">
              <i class="bi bi-chevron-right"></i>
            </button>
          </div>
        </div>
        <div v-else class="text-center py-2">
          <p class="mb-0">No reviews found.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import api from '@/services/api.service.js'
import adminService from '@/services/admin.service.js'
const Modal = window.bootstrap?.Modal
const Popover = window.bootstrap?.Popover

export default {
  name: 'UserManagementView',
  data() {
    return {
      users: [],
      loading: false,
      error: null,
      userTypeFilter: 'all',
      userStatusFilter: 'all',
      searchQuery: '',
      documents: [],
      loadingDocuments: false,
      documentError: null,
      documentsModalRef: null,
      documentsModal: null,
      popoverData: {
        averageRating: 0,
        totalReviews: 0,
        reviews: [],
        currentPage: 1,
        totalPages: 1,
        professionalId: null
      },
      popovers: {},
      currentProfessionalId: null
    }
  },
  created() {
    this.fetchUsers()
  },
  mounted() {
    // Initialize Bootstrap modal when component is mounted
    this.documentsModalRef = this.$refs.documentsModalRef
    if (this.documentsModalRef) {
      this.documentsModal = new Modal(this.documentsModalRef)
    }
  },
  computed: {
    filteredUsers() {
      console.log('Filtering users, total before filter:', this.users.length)
      // Always exclude admin users from the list
      return this.users.filter(user => {
        // First exclude admin users
        if (user.role === 'admin') {
          console.log('Filtering out admin user:', user.username)
          return false;
        }
        
        // Filter by user type
        if (this.userTypeFilter !== 'all' && user.role !== this.userTypeFilter) {
          return false;
        }
        
        // Filter by status
        if (this.userStatusFilter === 'approved' && (!user.is_approved || !user.is_active)) {
          return false;
        }
        if (this.userStatusFilter === 'pending' && (user.is_approved || !user.is_active)) {
          return false;
        }
        if (this.userStatusFilter === 'blocked' && user.is_active) {
          return false;
        }
        
        // Filter by search query
        if (this.searchQuery && !user.username.toLowerCase().includes(this.searchQuery.toLowerCase())) {
          return false;
        }
        
        return true;
      });
    },
    pendingApprovals() {
      return this.users.filter(user => 
        user.role === 'professional' && !user.is_approved && user.is_active
      ).length
    }
  },
  methods: {
    async fetchUsers() {
      this.loading = true
      this.error = null
      
      try {
        const response = await api.get('/admin/users')
        console.log('Fetched users:', response.data)
        
        // Double-check: filter out any admin users that might have slipped through
        this.users = response.data.filter(user => user.role !== 'admin')
        console.log('Users after admin filtering:', this.users.length)
      } catch (err) {
        this.error = 'Failed to load users: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loading = false
      }
    },
    
    formatDate(dateString) {
      if (!dateString) return 'N/A'
      const date = new Date(dateString)
      return date.toLocaleDateString()
    },
    
    async blockUser(userId) {
      if (confirm('Are you sure you want to block this user?')) {
        try {
          this.loading = true
          await api.put(`/admin/block/${userId}`)
          await this.fetchUsers()
          this.loading = false
        } catch (err) {
          this.error = 'Failed to block user: ' + (err.response?.data?.error || err.message)
          this.loading = false
        }
      }
    },
    
    async unblockUser(userId) {
      try {
        this.loading = true
        await api.put(`/admin/unblock/${userId}`)
        await this.fetchUsers()
        this.loading = false
      } catch (err) {
        this.error = 'Failed to unblock user: ' + (err.response?.data?.error || err.message)
        this.loading = false
      }
    },
    
    // Document methods
    async viewDocuments(userId) {
      this.loadingDocuments = true
      this.documentError = null
      this.documents = []
      
      if (this.documentsModal) {
        this.documentsModal.show()
      }
      
      try {
        const response = await api.get(`/admin/users/${userId}/documents`)
        this.documents = response.data
      } catch (err) {
        console.error('Failed to fetch documents:', err)
        this.documentError = 'Failed to load documents: ' + (err.response?.data?.error || err.message)
      } finally {
        this.loadingDocuments = false
      }
    },
    
    formatDocumentType(type) {
      if (!type) return 'Document'
      
      // Convert camelCase or snake_case to readable format
      return type
        .replace(/([A-Z])/g, ' $1') // Insert space before capital letters
        .replace(/_/g, ' ')         // Replace underscores with spaces
        .replace(/^\w/, c => c.toUpperCase()) // Capitalize first letter
    },
    
    async viewDocument(documentId) {
      try {
        // Instead of directly opening a URL, we need to fetch the document through 
        // the API service which will include the JWT in the headers
        const response = await api.get(`/documents/${documentId}`, {
          responseType: 'blob',
          headers: {
            Authorization: `Bearer ${localStorage.getItem('auth_token')}` // Ensure JWT is included
          }
        });
        
        // Create a blob URL from the response data
        const blob = new Blob([response.data], { type: response.headers['content-type'] });
        const blobUrl = window.URL.createObjectURL(blob);
        
        // Open the blob URL in a new window
        window.open(blobUrl, '_blank');
      } catch (err) {
        console.error('Failed to view document:', err);
        alert('Failed to open document: ' + err.message);
      }
    },

    // Ratings methods
    initializeReviewsPopover(professionalId) {
      this.popoverData.professionalId = professionalId;
      this.popoverData.currentPage = 1;
      
      // Create or get the popover instance
      const btnId = `ratings-btn-${professionalId}`;
      const btnElement = document.getElementById(btnId);
      
      if (!btnElement) return;
      
      // Fetch reviews data
      this.fetchPopoverReviews(professionalId, 1).then(() => {
        // Update popover content with template
        const popoverInstance = this.popovers[btnId] || new Popover(btnElement, {
          container: 'body',
          html: true,
          sanitize: false,
          trigger: 'hover focus',
          delay: { show: 300, hide: 400 }, // Add delay to prevent accidental hiding
          content: () => {
            return this.renderPopoverContent();
          }
        });
        
        this.popovers[btnId] = popoverInstance;
        
        // Force update the popover content if it's already shown
        if (btnElement.getAttribute('aria-describedby')) {
          popoverInstance.update();
        }
      });
    },
    
    renderPopoverContent() {
      // Create a temporary element to render the template with Vue bindings
      const template = document.getElementById('reviews-popover-template');
      if (!template) return 'Error loading reviews';
      
      // Clone the template content
      const content = template.cloneNode(true);
      
      // Replace placeholders with actual data
      content.innerHTML = content.innerHTML
        .replace(/{{ popoverData.averageRating }}/g, this.popoverData.averageRating.toFixed(1))
        .replace(/{{ popoverData.totalReviews }}/g, this.popoverData.totalReviews)
        .replace(/{{ popoverData.currentPage }}/g, this.popoverData.currentPage)
        .replace(/{{ popoverData.totalPages }}/g, this.popoverData.totalPages);
      
      // Add reviews to the content
      const reviewsList = content.querySelector('.reviews-list');
      if (reviewsList && this.popoverData.reviews.length) {
        let reviewsHtml = '';
        this.popoverData.reviews.forEach((review, index) => {
          // Generate stars for ratings
          let starsHtml = '';
          for (let i = 1; i <= 5; i++) {
            starsHtml += `<i class="bi ${i <= review.rating ? 'bi-star-fill text-warning' : 'bi-star'}"></i>`;
          }
          
          reviewsHtml += `
            <div class="${index > 0 ? 'mt-3' : ''}">
              <div class="d-flex align-items-center">
                <div class="ratings-stars">${starsHtml}</div>
                <small class="ms-1 text-muted">${this.formatReviewDate(review.created_at)}</small>
              </div>
              <div class="review-comment">${review.comment || 'No comment provided.'}</div>
            </div>
          `;
        });
        
        const reviewsContainer = reviewsList.querySelector('.reviews-list > div');
        if (reviewsContainer) {
          reviewsContainer.innerHTML = reviewsHtml;
        }
      }
      
      // Set up pagination event listeners
      setTimeout(() => {
        const prevBtn = document.querySelector('.popover .popover-pagination button:first-child');
        const nextBtn = document.querySelector('.popover .popover-pagination button:last-child');
        
        if (prevBtn) {
          prevBtn.addEventListener('click', () => this.changePopoverPage(this.popoverData.currentPage - 1));
        }
        if (nextBtn) {
          nextBtn.addEventListener('click', () => this.changePopoverPage(this.popoverData.currentPage + 1));
        }
      }, 100);
      
      return content.innerHTML;
    },
    
    async fetchPopoverReviews(professionalId, page) {
      try {
        const response = await api.get(`/admin/professionals/${professionalId}/reviews`, {
          params: { page, per_page: 3 } // Show fewer reviews in popover
        });
        
        this.popoverData = {
          ...this.popoverData,
          averageRating: response.data.averageRating,
          totalReviews: response.data.totalReviews,
          reviews: response.data.reviews,
          currentPage: page,
          totalPages: Math.ceil(response.data.totalReviews / 3),
          professionalId
        };
      } catch (err) {
        console.error('Error fetching reviews for popover:', err);
        this.popoverData.reviews = [];
      }
    },
    
    async changePopoverPage(page) {
      if (page < 1 || page > this.popoverData.totalPages) return;
      
      await this.fetchPopoverReviews(this.popoverData.professionalId, page);
      
      // Update the active popover if one exists
      const btnId = `ratings-btn-${this.popoverData.professionalId}`;
      const popoverInstance = this.popovers[btnId];
      
      if (popoverInstance) {
        // Force update the popover content
        popoverInstance.setContent({ '.popover-body': this.renderPopoverContent() });
      }
    },
    
    formatReviewDate(dateString) {
      if (!dateString) return '';
      const date = new Date(dateString);
      return date.toLocaleDateString();
    },

    getRatingsSummary(user) {
      return `${user.average_rating ? user.average_rating.toFixed(1) : 'N/A'}/5 (${user.total_reviews || 0} reviews)`;
    }
  }
}
</script>

<style scoped>
.user-management {
  padding: 1.5rem;
  max-width: 1600px;
  margin: 0 auto;
}

.page-header h3 {
  margin-bottom: 0;
  color: #2c3e50;
}

.modal-header {
  background-color: var(--bs-primary);
  color: white;
}

.modal-header .btn-close {
  filter: brightness(0) invert(1);
}

.toast-container {
  z-index: 9999;
}

.table tr:hover {
  background-color: rgba(0, 0, 0, 0.03);
}

.reviews-popover {
  max-width: 300px;
}

/* Add hover popover specific styles */
.hover-popover {
  pointer-events: auto !important;
}

/* Create a hover area to prevent popover from closing immediately */
:deep(.popover.hover-popover) {
  pointer-events: auto !important;
}

:deep(.popover.hover-popover:hover) {
  visibility: visible;
  opacity: 1;
}

/* Add a small gap between button and popover for smoother hovering */
:deep(.popover.hover-popover::before) {
  content: '';
  position: absolute;
  top: -10px;
  left: 0;
  right: 0;
  height: 10px;
}

.ratings-btn {
  position: relative;
}

.ratings-stars {
  display: inline-flex;
  align-items: center;
}

.ratings-stars .bi {
  font-size: 0.8rem;
  margin-right: 1px;
}

.review-comment {
  font-size: 0.875rem;
  white-space: normal;
  word-break: break-word;
  max-height: 60px;
  overflow-y: auto;
}

.popover-pagination .btn {
  padding: 0.1rem 0.4rem;
  font-size: 0.75rem;
}

/* Override Bootstrap's popover styles */
:deep(.popover) {
  max-width: 320px;
}

:deep(.popover-body) {
  padding: 0.75rem;
}

@media (max-width: 768px) {
  .user-management {
    padding: 1rem;
  }
}
</style>
