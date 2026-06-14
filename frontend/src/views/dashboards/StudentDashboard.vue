<template>
  <div class="dashboard-wrapper d-flex">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="studentMenu"
      :username="username"
      role="Student"
      @logout="handleLogout"
    />

    <div class="main-content flex-grow-1 p-4">
      <header class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-dark">{{ activeMenuLabel }}</h2>
        <div class="date text-muted">{{ currentDate }}</div>
      </header>

      <!-- Dashboard Overview -->
      <section v-if="activeTab === 'dashboard'">
        <div class="card border-0 shadow-sm p-4 mb-4 bg-primary text-white dashboard-glance">
          <div class="row align-items-center">
            <div class="col-8">
              <h1 class="fw-bold">Level Up Your Career!</h1>
              <p class="mb-0 opacity-75">Check out the latest job postings and start your applications today.</p>
            </div>
            <div class="col-4 text-end">
              <img src="https://cdn-icons-png.flaticon.com/512/3281/3281289.png" alt="Career" class="img-fluid" style="height: 100px;">
            </div>
          </div>
        </div>
        
        <div class="row g-4">
          <div class="col-md-8">
            <div class="card border-0 shadow-sm p-4 h-100">
              <h5 class="fw-bold mb-3">Recent Placements In Campus</h5>
              <p class="text-muted small">Stay inspired by your peers' success.</p>
              <hr>
              <div class="text-center py-4">
                <i class="bi bi-stars fs-1 text-warning mb-2"></i>
                <p>New placements being updated soon!</p>
              </div>
            </div>
          </div>
          <div class="col-md-4">
            <div class="card border-0 shadow-sm p-4 h-100 bg-light">
              <h5 class="fw-bold mb-3">Application Status</h5>
              <div class="text-center py-5">
                <h2 class="fw-bold">0</h2>
                <span class="text-muted">Active Applications</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Other Tabs -->
      <section v-else class="text-center py-5">
        <div class="card border-0 shadow-sm p-5">
          <i :class="`bi ${activeMenuIcon} mb-3 text-muted`" style="font-size: 4rem;"></i>
          <h4 class="text-muted">{{ activeMenuLabel }} coming soon</h4>
          <p>This section is being populated with your data.</p>
        </div>
      </section>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '../../components/Sidebar.vue'

const router = useRouter()
const activeTab = ref('dashboard')
const username = ref(localStorage.getItem('username'))

const studentMenu = [
  { id: 'dashboard', label: 'Home', icon: 'bi-house-door' },
  { id: 'jobs', label: 'Available Jobs', icon: 'bi-briefcase' },
  { id: 'applications', label: 'My Applications', icon: 'bi-send' },
  { id: 'placements', label: 'Offer Letters', icon: 'bi-patch-check' },
  { id: 'profile', label: 'My Profile', icon: 'bi-person-circle' }
]

const activeMenuLabel = computed(() => {
  return studentMenu.find(item => item.id === activeTab.value)?.label || 'Dashboard'
})

const activeMenuIcon = computed(() => {
  return studentMenu.find(item => item.id === activeTab.value)?.icon || 'bi-app'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>

<style scoped>
.dashboard-wrapper {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.main-content {
  margin-left: 260px;
  transition: all 0.3s ease;
}

.dashboard-glance {
  border-radius: 20px;
  background: linear-gradient(135deg, #0d6efd 0%, #00d2ff 100%);
}

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
