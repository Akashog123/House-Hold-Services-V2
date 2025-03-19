<template>
  <ProfessionalLayout>
    <div class="profile-page">
      <h1>My Professional Profile</h1>
      
      <div class="profile-container">
        <div v-if="loading" class="loading">Loading profile data...</div>
        <div v-if="error" class="error-message">{{ error }}</div>
        
        <div v-if="profileData && !loading" class="profile-grid">
          <div class="profile-section basic-info">
            <h2>Basic Information</h2>
            
            <form @submit.prevent="updateBasicInfo">
              <div class="form-group">
                <label for="username">Username</label>
                <input type="text" id="username" v-model="profileData.username" disabled />
              </div>
              
              <div class="form-group">
                <label for="fullName">Full Name</label>
                <input type="text" id="fullName" v-model="profileForm.fullName" />
              </div>
              
              <div class="form-group">
                <label for="email">Email Address</label>
                <input type="email" id="email" v-model="profileForm.email" />
              </div>
              
              <div class="form-group">
                <label for="phone">Phone Number</label>
                <input type="tel" id="phone" v-model="profileForm.phone" />
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn-primary" :disabled="updatingProfile">
                  {{ updatingProfile ? 'Saving...' : 'Save Changes' }}
                </button>
              </div>
            </form>
          </div>
          
          <div class="profile-section stats">
            <h2>Service Statistics</h2>
            
            <div class="stats-grid">
              <div class="stat-item">
                <div class="stat-value">{{ stats.completed }}</div>
                <div class="stat-label">Completed Jobs</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.active }}</div>
                <div class="stat-label">Active Jobs</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.totalEarnings }}</div>
                <div class="stat-label">Total Earnings</div>
              </div>
              <div class="stat-item">
                <div class="stat-value">{{ stats.rating }}/5</div>
                <div class="stat-label">Rating</div>
              </div>
            </div>
          </div>
          
          <div class="profile-section services">
            <h2>My Services</h2>
            
            <div class="services-list">
              <div v-if="availableServices.length === 0" class="empty-state">
                No services available. Please check back later.
              </div>
              
              <div v-for="service in availableServices" :key="service.id" class="service-item">
                <div class="service-name">{{ service.name }}</div>
                <div class="service-price">${{ service.base_price }}</div>
                <div class="service-duration">{{ service.avg_duration }} min</div>
              </div>
            </div>
          </div>
          
          <div class="profile-section account">
            <h2>Account Settings</h2>
            
            <form @submit.prevent="changePassword" class="password-form">
              <div class="form-group">
                <label for="currentPassword">Current Password</label>
                <input type="password" id="currentPassword" v-model="passwordForm.currentPassword" required />
              </div>
              
              <div class="form-group">
                <label for="newPassword">New Password</label>
                <input type="password" id="newPassword" v-model="passwordForm.newPassword" required />
              </div>
              
              <div class="form-group">
                <label for="confirmPassword">Confirm New Password</label>
                <input type="password" id="confirmPassword" v-model="passwordForm.confirmPassword" required />
              </div>
              
              <div class="form-actions">
                <button type="submit" class="btn-primary" :disabled="changingPassword">
                  {{ changingPassword ? 'Updating...' : 'Change Password' }}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  </ProfessionalLayout>
</template>

<script>
import ProfessionalLayout from '@/layouts/ProfessionalLayout.vue';
import api from '../../services/api.service';

export default {
  name: 'ProfileView',
  components: {
    ProfessionalLayout
  },
  data() {
    return {
      profileData: null,
      loading: false,
      error: null,
      updatingProfile: false,
      changingPassword: false,
      profileForm: {
        fullName: '',
        email: '',
        phone: ''
      },
      passwordForm: {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      },
      availableServices: [],
      stats: {
        completed: 0,
        active: 0,
        totalEarnings: '$0',
        rating: 0
      }
    };
  },
  created() {
    this.fetchProfileData();
    this.fetchAvailableServices();
    this.fetchStats();
  },
  methods: {
    async fetchProfileData() {
      this.loading = true;
      try {
        const response = await api.get('/professional/profile');
        this.profileData = response.data;
        
        // Initialize form with existing data
        this.profileForm = {
          fullName: this.profileData.full_name || '',
          email: this.profileData.email || '',
          phone: this.profileData.phone || ''
        };
      } catch (err) {
        this.error = 'Failed to load profile: ' + (err.response?.data?.error || err.message);
      } finally {
        this.loading = false;
      }
    },
    
    async fetchAvailableServices() {
      try {
        const response = await api.get('/services');
        this.availableServices = response.data;
      } catch (err) {
        console.error('Failed to load services:', err);
      }
    },
    
    async fetchStats() {
      try {
        const response = await api.get('/professional/stats');
        if (response.data) {
          this.stats = response.data;
        }
      } catch (err) {
        console.error('Failed to load stats:', err);
        // Use mock data as fallback
        this.stats = {
          completed: 12,
          active: 3,
          totalEarnings: '$950',
          rating: 4.8
        };
      }
    },
    
    async updateBasicInfo() {
      this.updatingProfile = true;
      try {
        await api.put('/professional/profile', {
          full_name: this.profileForm.fullName,
          email: this.profileForm.email,
          phone: this.profileForm.phone
        });
        
        // Update local profile data
        this.profileData.full_name = this.profileForm.fullName;
        this.profileData.email = this.profileForm.email;
        this.profileData.phone = this.profileForm.phone;
        
        alert('Profile updated successfully!');
      } catch (err) {
        this.error = 'Failed to update profile: ' + (err.response?.data?.error || err.message);
      } finally {
        this.updatingProfile = false;
      }
    },
    
    async changePassword() {
      if (this.passwordForm.newPassword !== this.passwordForm.confirmPassword) {
        this.error = 'New passwords do not match!';
        return;
      }
      
      this.changingPassword = true;
      try {
        await api.put('/professional/change-password', {
          current_password: this.passwordForm.currentPassword,
          new_password: this.passwordForm.newPassword
        });
        
        // Reset form
        this.passwordForm = {
          currentPassword: '',
          newPassword: '',
          confirmPassword: ''
        };
        
        alert('Password changed successfully!');
      } catch (err) {
        this.error = 'Failed to change password: ' + (err.response?.data?.error || err.message);
      } finally {
        this.changingPassword = false;
      }
    }
  }
};
</script>

<style scoped>
.profile-page {
  padding: 20px;
}

h1 {
  color: #2c3e50;
  margin-bottom: 20px;
}

h2 {
  color: #2c3e50;
  margin-bottom: 15px;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
}

.profile-container {
  margin-top: 20px;
}

.profile-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.profile-section {
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  font-weight: bold;
  margin-bottom: 5px;
}

.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.form-group input:disabled {
  background-color: #f5f5f5;
}

.form-actions {
  margin-top: 20px;
}

.btn-primary {
  background-color: #4caf50;
  color: white;
  border: none;
  padding: 10px 15px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.btn-primary:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 15px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 8px;
}

.stat-value {
  font-size: 2rem;
  font-weight: bold;
  color: #4caf50;
}

.stat-label {
  margin-top: 5px;
  font-size: 0.9rem;
  color: #6c757d;
}

.services-list {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

.service-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.service-name {
  font-weight: bold;
}

.service-price {
  color: #4caf50;
  font-weight: bold;
}

.loading {
  text-align: center;
  padding: 20px;
  color: #666;
}

.error-message {
  background-color: #f8d7da;
  color: #721c24;
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 15px;
}

.empty-state {
  text-align: center;
  padding: 20px;
  color: #666;
  font-style: italic;
}
</style>
