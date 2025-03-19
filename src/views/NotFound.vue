<template>
  <div class="not-found">
    <div class="container text-center">
      <div class="row justify-content-center">
        <div class="col-12 col-sm-8 col-md-6">
          <div class="card mt-5">
            <div class="card-body p-5">
              <h1 class="display-4 text-primary mb-4">
                404 - Page Not Found
              </h1>
              <h5 class="mb-4">
                The page you are looking for does not exist or has been moved.
              </h5>
              <div>
                <router-link 
                  to="/" 
                  class="btn btn-primary btn-lg"
                >
                  Return to Home
                </router-link>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'NotFound'
}
</script>

<style scoped>
.not-found {
  min-height: calc(100vh - 56px);
  padding: 2rem 0;
  background-color: var(--bs-light);
}

.card {
  border-radius: 1rem;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}
</style>
