<template>
  <div class="dashboard-wrapper d-flex">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="companyMenu"
      :username="username"
      role="Company Partner"
      @logout="handleLogout"
    />

    <div class="main-content flex-grow-1 p-4">
      <header class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-dark">{{ activeMenuLabel }}</h2>
        <div class="date text-muted">{{ currentDate }}</div>
      </header>

      <!-- Dashboard Overview -->
      <section v-if="activeTab === 'dashboard'">
        <div class="card border-0 shadow-sm p-5 text-center bg-white">
          <div class="icon-box bg-primary-soft text-primary mx-auto mb-4" style="width: 80px; height: 80px;">
            <i class="bi bi-rocket-takeoff fs-1"></i>
          </div>
          <h3 class="fw-bold">Welcome back, {{ username }}!</h3>
          <p class="text-muted">You can manage your recruitment drives and track applicants from your sidebar.</p>
          <div class="mt-4 d-flex justify-content-center gap-3">
            <button @click="activeTab = 'post-job'" class="btn btn-primary px-4">Post New Drive</button>
            <button @click="activeTab = 'jobs'" class="btn btn-outline-primary px-4">View My Jobs</button>
          </div>
        </div>
      </section>

      <!-- Other Tabs (Placeholders for now) -->
      <section v-else class="text-center py-5">
        <div class="card border-0 shadow-sm p-5">
          <i :class="`bi ${activeMenuIcon} mb-3 text-muted`" style="font-size: 4rem;"></i>
          <h4 class="text-muted">{{ activeMenuLabel }} coming soon</h4>
          <p>We are currently finalizing this feature.</p>
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

const companyMenu = [
  { id: 'dashboard', label: 'Overview', icon: 'bi-house' },
  { id: 'post-job', label: 'Post Job', icon: 'bi-plus-circle' },
  { id: 'jobs', label: 'My Postings', icon: 'bi-collection' },
  { id: 'applicants', label: 'Applicants', icon: 'bi-people' },
  { id: 'profile', label: 'Company Profile', icon: 'bi-building-gear' }
]

const activeMenuLabel = computed(() => {
  return companyMenu.find(item => item.id === activeTab.value)?.label || 'Dashboard'
})

const activeMenuIcon = computed(() => {
  return companyMenu.find(item => item.id === activeTab.value)?.icon || 'bi-app'
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

.icon-box {
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 20px;
}

.bg-primary-soft { background-color: rgba(13, 110, 253, 0.1); }

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
