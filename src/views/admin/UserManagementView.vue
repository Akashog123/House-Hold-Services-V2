<template>
    <h3>User Management</h3>
    
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
    <div class="filter-controls">
      <div class="filter-group">
        <label>Filter by Type:</label>
        <select v-model="userTypeFilter">
          <option value="all">All Users</option>
          <option value="professional">Professionals</option>
          <option value="customer">Customers</option>
        </select>
      </div>
      
      <div class="filter-group">
        <label>Status:</label>
        <select v-model="userStatusFilter">
          <option value="all">All</option>
          <option value="approved">Approved</option>
          <option value="pending">Pending Approval</option>
          <option value="blocked">Blocked</option>
        </select>
      </div>
      
      <div class="filter-group search">
        <label>Search:</label>
        <input type="text" v-model="searchQuery" placeholder="Search username..." />
      </div>
    </div>
    
    <!-- User List -->
    <div class="user-table-container">
      <div v-if="loading" class="loading">Loading users...</div>
      <div v-if="error" class="error">{{ error }}</div>
      
      <table v-if="!loading && !error && filteredUsers.length > 0" class="user-table">
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
          <tr v-for="user in filteredUsers" :key="user.id" :class="{ 'inactive': !user.is_active }">
            <td>{{ user.username }}</td>
            <td>{{ user.email }}</td>
            <td>{{ user.role }}</td>
            <td>
              <span v-if="!user.is_active" class="status blocked">Blocked</span>
              <span v-else-if="user.is_approved" class="status approved">Approved</span>
              <span v-else class="status pending">Pending</span>
            </td>
            <td>{{ formatDate(user.created_at) }}</td>
            <td>
              <div class="action-buttons">
                <!-- Documents button for professionals -->
                <button 
                  v-if="user.role === 'professional'" 
                  class="btn-info" 
                  @click="viewDocuments(user.id)"
                  :disabled="loading || user.documents_count === 0"
                  title="View Documents"
                >
                  <i class="bi bi-file-earmark-text"></i>
                </button>
              
                <!-- Replace approve/reject with View Application button -->
                <router-link 
                  v-if="user.role === 'professional' && !user.is_approved" 
                  class="btn-approve" 
                  :to="{ path: '/admin/approvals', query: { professional_id: user.id }}"
                  title="View Application"
                >
                  View Application
                </router-link>
                
                <button 
                    v-if="(user.role === 'professional' || user.role === 'customer') && user.is_approved && user.is_active" 
                  class="btn-block" 
                  @click="blockUser(user.id)"
                >
                  Block
                </button>
                <button 
                  v-if="!user.is_active" 
                  class="btn-unblock" 
                  @click="unblockUser(user.id)"
                >
                  Unblock
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
      
      <div v-if="!loading && !error && filteredUsers.length === 0" class="empty-state">
        No users found matching your filters.
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
                
                <div class="document-preview p-2 border rounded">
                  <div class="d-flex justify-content-center my-2">
                    <a :href="`/api/documents/${doc.id}`" target="_blank" class="btn btn-sm btn-primary">
                      <i class="bi bi-eye me-1"></i> View Document
                    </a>
                    <button 
                      class="btn btn-sm ms-2" 
                      :class="doc.verified ? 'btn-outline-success' : 'btn-success'" 
                      @click="toggleVerification(doc.id, !doc.verified)"
                    >
                      <i class="bi" :class="doc.verified ? 'bi-x-circle' : 'bi-check-circle'"></i>
                      {{ doc.verified ? 'Mark as Unverified' : 'Mark as Verified' }}
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
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/services/api.service.js'
import { Modal } from 'bootstrap'

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
      // Document related state
      documents: [],
      loadingDocuments: false,
      documentError: null,
      documentsModalRef: null,
      documentsModal: null
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
    
    async toggleVerification(documentId, verified) {
      try {
        await api.put(`/admin/documents/${documentId}/verify`, { verified })
        
        // Update the document in the local array
        const index = this.documents.findIndex(d => d.id === documentId)
        if (index !== -1) {
          this.documents[index].verified = verified
        }
      } catch (err) {
        console.error('Failed to update document verification:', err)
        this.documentError = 'Failed to update document: ' + (err.response?.data?.error || err.message)
      }
    }
  }
}
</script>

<style scoped>
h1 {
  margin-bottom: 20px;
  color: #2c3e50;
}

.filter-controls {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-bottom: 20px;
  background: #fff;
  padding: 15px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.filter-group label {
  font-weight: bold;
  font-size: 0.9rem;
}

.filter-group select, .filter-group input {
  padding: 8px 12px;
  border-radius: 4px;
  border: 1px solid #ddd;
  min-width: 150px;
}

.filter-group.search {
  flex-grow: 1;
}

.filter-group.search input {
  min-width: 200px;
}

.user-table-container {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  overflow-x: auto;
}

.user-table {
  width: 100%;
  border-collapse: collapse;
}

.user-table th, .user-table td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #eee;
}

.user-table th {
  background-color: #f5f5f5;
  font-weight: bold;
}

.user-table tr.inactive {
  background-color: #f9f9f9;
  color: #999;
}

.status {
  display: inline-block;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 0.8rem;
  font-weight: bold;
}

.status.approved {
  background-color: #d4edda;
  color: #155724;
}

.status.pending {
  background-color: #fff3cd;
  color: #856404;
}

.status.blocked {
  background-color: #f8d7da;
  color: #721c24;
}

.action-buttons {
  display: flex;
  gap: 5px;
  flex-wrap: wrap;
}

.btn-approve, .btn-reject, .btn-block, .btn-unblock {
  padding: 5px 10px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-approve {
  background-color: #28a745;
  color: white;
}

.btn-reject {
  background-color: #dc3545;
  color: white;
}

.btn-block {
  background-color: #6c757d;
  color: white;
}

.btn-unblock {
  background-color: #17a2b8;
  color: white;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 20px;
}

.empty-state {
  text-align: center;
  padding: 30px;
  color: #666;
  font-style: italic;
}

/* Additional styles for document section */
.btn-info {
  background-color: #17a2b8;
  color: white;
  border: none;
  padding: 5px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.8rem;
}

.btn-info:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.document-preview {
  background-color: #f8f9fa;
}
</style>
