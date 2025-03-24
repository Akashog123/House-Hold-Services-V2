<template>
  <div class="approvals-container">
    <h3>Professional Approvals</h3>
      
      <div v-if="loading" class="loading-state">
        <div class="spinner-border text-primary" role="status">
          <span class="visually-hidden">Loading...</span>
        </div>
      </div>

      <div v-else-if="error" class="alert alert-danger" role="alert">
        {{ error }}
      </div>

      <div v-else>
        <div v-if="professionals.length === 0" class="empty-state">
          No pending approval requests.
        </div>

        <div v-else class="professionals-list">
          <div v-for="professional in professionals" :key="professional.id" class="professional-card">
            <div class="professional-info">
              <h3>{{ professional.name }}</h3>
              <p><strong>Email:</strong> {{ professional.email }}</p>
              <p><strong>Services:</strong> {{ professional.services?.join(', ') || 'None specified' }}</p>
              <p><strong>Registration Date:</strong> {{ formatDate(professional.created_at) }}</p>
            </div>

            <div class="actions">
              <button 
                class="btn btn-success" 
                @click="approveProfessional(professional.id)"
                :disabled="loading"
              >
                Approve
              </button>
              <button 
                class="btn btn-danger" 
                @click="rejectProfessional(professional.id)"
                :disabled="loading"
              >
                Reject
              </button>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/services/api.service.js'

export default {
  name: 'ApprovalsView',

  setup() {
    const professionals = ref([])
    const loading = ref(false)
    const error = ref(null)
    const route = useRoute()
    const router = useRouter()

    const fetchProfessionals = async () => {
      loading.value = true
      error.value = null
      
      try {
        // Check if we have a specific professional_id in query params
        const professionalId = route.query.professional_id
        
        if (professionalId) {
          // Fetch specific professional details
          const response = await api.get(`/admin/users/${professionalId}`)
          
          // Only add to the list if this professional needs approval
          if (response.data && response.data.role === 'professional' && !response.data.is_approved) {
            professionals.value = [response.data]
          } else {
            professionals.value = []
            error.value = 'The specified professional does not require approval or was not found.'
          }
        } else {
          // Fetch all pending professionals
          const response = await api.get('/admin/professionals', {
            params: { approved: 'false', active: 'true' }
          })
          professionals.value = response.data
        }
      } catch (err) {
        error.value = 'Failed to load professionals: ' + (err.response?.data?.error || err.message)
      } finally {
        loading.value = false
      }
    }

    const approveProfessional = async (id) => {
      try {
        loading.value = true
        await api.put(`/admin/approve/${id}`)
        
        // If we came from user management view with a specific professional,
        // redirect back to user management after approval
        if (route.query.professional_id) {
          router.push('/admin/users')
        } else {
          // Otherwise refresh the list
          await fetchProfessionals()
        }
      } catch (err) {
        error.value = 'Failed to approve professional: ' + (err.response?.data?.error || err.message)
      } finally {
        loading.value = false
      }
    }

    const rejectProfessional = async (id) => {
      try {
        loading.value = true
        await api.put(`/admin/reject/${id}`, {})
        
        // If we came from user management view with a specific professional,
        // redirect back to user management after rejection
        if (route.query.professional_id) {
          router.push('/admin/users')
        } else {
          // Otherwise refresh the list
          await fetchProfessionals()
        }
      } catch (err) {
        error.value = 'Failed to reject professional: ' + (err.response?.data?.error || err.message)
      } finally {
        loading.value = false
      }
    }

    const formatDate = (dateString) => {
      if (!dateString) return 'N/A'
      return new Date(dateString).toLocaleDateString()
    }

    onMounted(fetchProfessionals)

    return {
      professionals,
      loading,
      error,
      approveProfessional,
      rejectProfessional,
      formatDate
    }
  }
}
</script>

<style scoped>
.approvals-container {
  padding: 20px;
}

.loading-state {
  display: flex;
  justify-content: center;
  padding: 40px;
}

.empty-state {
  text-align: center;
  padding: 40px;
  color: #666;
}

.professionals-list {
  display: grid;
  gap: 20px;
  margin-top: 20px;
}

.professional-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  background: white;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.professional-info h3 {
  margin: 0 0 10px 0;
}

.professional-info p {
  margin: 5px 0;
}

.actions {
  display: flex;
  gap: 10px;
}

.btn {
  padding: 8px 16px;
  border-radius: 4px;
  border: none;
  cursor: pointer;
}

.btn-success {
  background: #28a745;
  color: white;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>