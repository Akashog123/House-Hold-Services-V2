<template>
  <div class="profile-container">
    <h3>Admin Profile</h3>

      <div class="card">
        <div class="card-body">
          <form @submit.prevent="updateProfile">
            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">First Name</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="profileForm.firstName"
                    required
                  >
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Last Name</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="profileForm.lastName"
                    required
                  >
                </div>
              </div>
            </div>

            <div class="mb-3">
              <label class="form-label">Email</label>
              <input
                type="email"
                class="form-control"
                v-model="profileForm.email"
                required
                disabled
              >
            </div>

            <div class="mb-3">
              <label class="form-label">Phone Number</label>
              <input
                type="tel"
                class="form-control"
                v-model="profileForm.phone"
              >
            </div>

            <hr>

            <h5 class="mb-3">Change Password</h5>
            <div class="mb-3">
              <label class="form-label">Current Password</label>
              <input
                type="password"
                class="form-control"
                v-model="passwordForm.currentPassword"
              >
            </div>

            <div class="row">
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">New Password</label>
                  <input
                    type="password"
                    class="form-control"
                    v-model="passwordForm.newPassword"
                  >
                </div>
              </div>
              <div class="col-md-6">
                <div class="mb-3">
                  <label class="form-label">Confirm New Password</label>
                  <input
                    type="password"
                    class="form-control"
                    v-model="passwordForm.confirmPassword"
                  >
                </div>
              </div>
            </div>

            <div class="d-flex justify-content-end gap-2">
              <button 
                type="button" 
                class="btn btn-secondary"
                @click="resetForm"
              >
                Reset
              </button>
              <button 
                type="submit" 
                class="btn btn-primary"
                :disabled="loading"
              >
                {{ loading ? 'Saving...' : 'Save Changes' }}
              </button>
            </div>
          </form>
        </div>
      </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api.service.js'

export default {
  name: 'AdminProfile',

  setup() {
    const loading = ref(false)
    const profileForm = ref({
      firstName: '',
      lastName: '',
      email: '',
      phone: ''
    })

    const passwordForm = ref({
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    })

    const fetchProfile = async () => {
      try {
        const response = await api.get('/admin/profile')
        const { firstName, lastName, email, phone } = response.data
        profileForm.value = { firstName, lastName, email, phone }
      } catch (error) {
        console.error('Failed to fetch profile:', error)
      }
    }

    const updateProfile = async () => {
      if (loading.value) return

      loading.value = true
      try {
        const payload = {
          ...profileForm.value
        }

        if (passwordForm.value.newPassword) {
          if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
            alert('New passwords do not match')
            return
          }
          payload.currentPassword = passwordForm.value.currentPassword
          payload.newPassword = passwordForm.value.newPassword
        }

        await api.put('/admin/profile', payload)
        alert('Profile updated successfully')
        passwordForm.value = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        }
      } catch (error) {
        alert('Failed to update profile: ' + (error.response?.data?.message || error.message))
      } finally {
        loading.value = false
      }
    }

    const resetForm = () => {
      fetchProfile()
      passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }
    }

    onMounted(fetchProfile)

    return {
      loading,
      profileForm,
      passwordForm,
      updateProfile,
      resetForm
    }
  }
}
</script>

<style scoped>
.profile-container {
  padding: 20px;
  max-width: 800px;
  margin: 0 auto;
}

.card {
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}
</style>