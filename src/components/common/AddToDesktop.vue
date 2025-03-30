<template>
  <div>
    <!-- Install prompt toast notification -->
    <div v-if="showInstallPrompt" class="position-fixed bottom-0 end-0 p-3" style="z-index: 1050">
      <div class="toast show install-prompt" role="alert" aria-live="assertive" aria-atomic="true">
        <div class="toast-header">
          <img src="/icons/logo-192.png" class="me-2" alt="HouseCare Logo" height="20">
          <strong class="me-auto">Add HouseCare to Desktop</strong>
          <button type="button" class="btn-close" @click="dismissPrompt"></button>
        </div>
        <div class="toast-body">
          <p>Install our app for quicker access and a better experience!</p>
          <div class="mt-2 d-flex justify-content-end">
            <button type="button" class="btn btn-secondary btn-sm me-2" @click="dismissPrompt">
              Not now
            </button>
            <button type="button" class="btn btn-primary btn-sm" @click="installApp">
              <i class="bi bi-download me-1"></i> Install
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- Install button in user menu (optional placement) -->
    <div v-if="showInstallButton" class="d-grid mt-2">
      <button @click="installApp" class="btn btn-outline-primary">
        <i class="bi bi-download me-2"></i>
        Add to Desktop
      </button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'AddToDesktop',
  data() {
    return {
      deferredPrompt: null,
      showInstallButton: false,
      showInstallPrompt: false
    }
  },
  mounted() {
    // Listen for the beforeinstallprompt event
    window.addEventListener('beforeinstallprompt', (e) => {
      // Prevent Chrome from automatically showing the prompt
      e.preventDefault();
      // Stash the event so it can be triggered later
      this.deferredPrompt = e;
      
      // Show the install button
      this.showInstallButton = true;
      
      // Check if we've shown the prompt recently
      const lastPrompt = localStorage.getItem('installPromptShown');
      const now = new Date().getTime();
      
      // Only show the prompt if we haven't shown it in the last 3 days
      if (!lastPrompt || now - parseInt(lastPrompt) > 3 * 24 * 60 * 60 * 1000) {
        // Wait a bit before showing the prompt
        setTimeout(() => {
          this.showInstallPrompt = true;
          localStorage.setItem('installPromptShown', now.toString());
        }, 3000);
      }
    });

    // Hide the install button and prompt when the app is installed
    window.addEventListener('appinstalled', () => {
      this.showInstallButton = false;
      this.showInstallPrompt = false;
      console.log('HouseCare PWA was installed');
    });
  },
  methods: {
    async installApp() {
      if (!this.deferredPrompt) return;
      
      // Show the install prompt
      this.deferredPrompt.prompt();
      
      // Wait for the user to respond to the prompt
      const { outcome } = await this.deferredPrompt.userChoice;
      console.log(`User response to the install prompt: ${outcome}`);
      
      // Clear the deferredPrompt variable since it can only be used once
      this.deferredPrompt = null;
      
      // Hide our custom UI
      this.showInstallButton = false;
      this.showInstallPrompt = false;
    },
    dismissPrompt() {
      this.showInstallPrompt = false;
    }
  }
}
</script>

<style scoped>
.install-prompt {
  max-width: 350px;
  box-shadow: 0 0.5rem 1rem rgba(0, 0, 0, 0.15);
}
</style>
