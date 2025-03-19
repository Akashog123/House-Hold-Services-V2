<template>
  <div class="settings-container">
    <h1>System Settings</h1>

      <div class="row">
        <div class="col-md-8">
          <!-- General Settings -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">General Settings</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="saveGeneralSettings">
                <div class="mb-3">
                  <label class="form-label">Site Name</label>
                  <input
                    type="text"
                    class="form-control"
                    v-model="generalSettings.siteName"
                  >
                </div>

                <div class="mb-3">
                  <label class="form-label">Contact Email</label>
                  <input
                    type="email"
                    class="form-control"
                    v-model="generalSettings.contactEmail"
                  >
                </div>

                <div class="mb-3">
                  <label class="form-label">Default Time Zone</label>
                  <select class="form-select" v-model="generalSettings.timezone">
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">Eastern Time</option>
                    <option value="America/Chicago">Central Time</option>
                    <option value="America/Denver">Mountain Time</option>
                    <option value="America/Los_Angeles">Pacific Time</option>
                  </select>
                </div>

                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  Save General Settings
                </button>
              </form>
            </div>
          </div>

          <!-- Notification Settings -->
          <div class="card mb-4">
            <div class="card-header">
              <h5 class="mb-0">Notification Settings</h5>
            </div>
            <div class="card-body">
              <form @submit.prevent="saveNotificationSettings">
                <div class="mb-3">
                  <div class="form-check">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      id="emailNotifications"
                      v-model="notificationSettings.emailEnabled"
                    >
                    <label class="form-check-label" for="emailNotifications">
                      Enable Email Notifications
                    </label>
                  </div>
                </div>

                <div class="mb-3">
                  <div class="form-check">
                    <input
                      type="checkbox"
                      class="form-check-input"
                      id="pushNotifications"
                      v-model="notificationSettings.pushEnabled"
                    >
                    <label class="form-check-label" for="pushNotifications">
                      Enable Push Notifications
                    </label>
                  </div>
                </div>

                <button 
                  type="submit" 
                  class="btn btn-primary"
                  :disabled="loading"
                >
                  Save Notification Settings
                </button>
              </form>
            </div>
          </div>
        </div>

        <div class="col-md-4">
          <!-- System Info -->
          <div class="card">
            <div class="card-header">
              <h5 class="mb-0">System Information</h5>
            </div>
            <div class="card-body">
              <p><strong>Version:</strong> {{ systemInfo.version }}</p>
              <p><strong>Last Updated:</strong> {{ formatDate(systemInfo.lastUpdated) }}</p>
              <p><strong>Environment:</strong> {{ systemInfo.environment }}</p>
              
              <div class="d-grid gap-2 mt-3">
                <button 
                  class="btn btn-secondary"
                  @click="checkUpdates"
                  :disabled="checkingUpdates"
                >
                  {{ checkingUpdates ? 'Checking...' : 'Check for Updates' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import api from '@/services/api.service.js'

export default {
  name: 'AdminSettings',

  setup() {
    const loading = ref(false)
    const checkingUpdates = ref(false)

    const generalSettings = ref({
      siteName: '',
      contactEmail: '',
      timezone: 'UTC'
    })

    const notificationSettings = ref({
      emailEnabled: true,
      pushEnabled: true
    })

    const systemInfo = ref({
      version: '1.0.0',
      lastUpdated: new Date(),
      environment: 'production'
    })

    const fetchSettings = async () => {
      try {
        const [generalResponse, notificationResponse, systemResponse] = await Promise.all([
          api.get('/admin/settings/general'),
          api.get('/admin/settings/notifications'),
          api.get('/admin/settings/system-info')
        ])

        generalSettings.value = generalResponse.data
        notificationSettings.value = notificationResponse.data
        systemInfo.value = systemResponse.data
      } catch (error) {
        console.error('Failed to fetch settings:', error)
      }
    }

    const saveGeneralSettings = async () => {
      if (loading.value) return

      loading.value = true
      try {
        await api.put('/admin/settings/general', generalSettings.value)
        alert('General settings saved successfully')
      } catch (error) {
        alert('Failed to save general settings')
      } finally {
        loading.value = false
      }
    }

    const saveNotificationSettings = async () => {
      if (loading.value) return

      loading.value = true
      try {
        await api.put('/admin/settings/notifications', notificationSettings.value)
        alert('Notification settings saved successfully')
      } catch (error) {
        alert('Failed to save notification settings')
      } finally {
        loading.value = false
      }
    }

    const checkUpdates = async () => {
      checkingUpdates.value = true
      try {
        const response = await api.get('/admin/settings/check-updates')
        if (response.data.updateAvailable) {
          alert(`Update available: version ${response.data.latestVersion}`)
        } else {
          alert('Your system is up to date')
        }
      } catch (error) {
        alert('Failed to check for updates')
      } finally {
        checkingUpdates.value = false
      }
    }

    const formatDate = (date) => {
      return new Date(date).toLocaleDateString()
    }

    onMounted(fetchSettings)

    return {
      loading,
      checkingUpdates,
      generalSettings,
      notificationSettings,
      systemInfo,
      saveGeneralSettings,
      saveNotificationSettings,
      checkUpdates,
      formatDate
    }
  }
}
</script>

<style scoped>
.settings-container {
  padding: 20px;
}

.card {
  margin-bottom: 20px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.card-header {
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}
</style>