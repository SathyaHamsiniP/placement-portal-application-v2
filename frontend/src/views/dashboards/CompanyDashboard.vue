<template>
  <div class="app-container">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="companyMenu"
      :username="username"
      role="Corporate Partner"
      @logout="handleLogout"
    />

    <main class="main-workspace no-scrollbar overflow-auto">
      <!-- Navbar -->
      <header class="top-navbar bg-white border-bottom px-4">
        <div class="navbar-content d-flex justify-content-between align-items-center w-100 h-100">
          <div class="brand-info">
            <h6 class="portal-title-left mb-0">Campus Placement Portal</h6>
          </div>
          <div class="user-profile-meta d-flex align-items-center">
            <div class="avatar-circle-company me-3">{{ username?.[0]?.toUpperCase() }}</div>
            <div class="profile-text text-start">
              <div class="fw-bold text-dark small leading-tight">{{ username }} Inc.</div>
              <div class="text-muted extra-small">Active Session</div>
            </div>
          </div>
        </div>
      </header>

      <div class="workspace-content p-4">
        
        <!-- Company Overview Tab -->
        <div v-if="activeTab === 'dashboard'" class="dashboard-root">
          <div class="fluid-card mb-4 mt-1 border-s-orange">
            <div class="d-flex justify-content-between align-items-center">
              <div>
                <h4 class="fw-bold mb-0 text-dark">{{ username }} Inc.</h4>
                <p class="text-muted small text-uppercase tracking-widest mb-0">SOFTWARE | MANAGEMENT CENTER</p>
              </div>
              <button @click="activeTab = 'post-job'" class="btn btn-orange rounded-pill px-4 shadow-sm fw-bold">Create New Job</button>
            </div>
          </div>

          <!-- Stats Row -->
          <div class="fluid-card mb-4">
            <div class="stats-grid-row d-flex text-center py-2">
              <div class="stat-col flex-fill">
                <h1 class="stats-value-small fw-bold mb-0 text-dark">{{ stats.jobs_posted || 0 }}</h1>
                <div class="stat-label">Jobs Posted</div>
              </div>
              <div class="stat-col flex-fill border-start">
                <h1 class="stats-value-small fw-bold mb-0 text-dark">{{ stats.active_applications || 0 }}</h1>
                <div class="stat-label">Active Applications</div>
              </div>
              <div class="stat-col flex-fill border-start">
                <h1 class="stats-value-small fw-bold mb-0 text-success">{{ stats.verified_jobs || 0 }}</h1>
                <div class="stat-label">Verified Job Posts</div>
              </div>
              <div class="stat-col flex-fill border-start">
                <h1 class="stats-value-small fw-bold mb-0 text-primary">0%</h1>
                <div class="stat-label">Placement Rate</div>
              </div>
            </div>
          </div>

          <!-- Charts Row -->
          <div class="row g-4">
            <div class="col-lg-8">
              <div class="fluid-card h-100">
                <div class="d-flex justify-content-between align-items-start mb-4">
                  <div>
                    <h5 class="fw-bold mb-1">Monthly Application Trend</h5>
                    <p class="text-muted extra-small mb-0">See the peak placement season</p>
                  </div>
                  <button class="btn btn-link text-muted p-0"><i class="bi bi-three-dots fs-5"></i></button>
                </div>
                <div class="chart-container" style="height: 380px;">
                  <Line :data="trendChartData" :options="trendChartOptions" />
                </div>
              </div>
            </div>

            <div class="col-lg-4">
              <div class="fluid-card mb-4 min-h-200">
                <h6 class="text-uppercase text-muted extra-small fw-bold tracking-widest mb-4">Recruitment Status</h6>
                <div class="row g-2">
                  <div v-for="(val, key) in stats.recruitment_status" :key="key" class="col-6">
                    <div class="status-box text-center p-3 rounded-3 bg-light-subtle border">
                      <div class="extra-small text-muted text-capitalize">{{ key.replace('_', ' ') }}</div>
                      <div class="fw-bold fs-4 text-dark">{{ val }}</div>
                    </div>
                  </div>
                </div>
              </div>

              <div class="fluid-card">
                <h6 class="text-uppercase text-muted extra-small fw-bold tracking-widest mb-4">Quick Navigation</h6>
                <div class="list-group list-group-flush gap-2">
                  <button @click="activeTab = 'shortlisted'" class="list-group-item list-group-item-action border-0 rounded-3 small d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-star me-3 text-primary"></i> Shortlisted List</span>
                    <i class="bi bi-chevron-right text-muted-extra"></i>
                  </button>
                  <button @click="activeTab = 'post-job'" class="list-group-item list-group-item-action border-0 rounded-3 small d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-gear me-3 text-primary"></i> Post New Vacancy</span>
                    <i class="bi bi-chevron-right text-muted-extra"></i>
                  </button>
                  <button @click="activeTab = 'jobs'" class="list-group-item list-group-item-action border-0 rounded-3 small d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-briefcase me-3 text-primary"></i> Manage All Jobs</span>
                    <i class="bi bi-chevron-right text-muted-extra"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Management Tables Area -->
        <div v-else class="management-root">
          <div class="fluid-card min-vh-75">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h4 class="fw-bold mb-1">{{ activeMenuLabel }}</h4>
                <p class="text-muted extra-small mb-0">Track and manage your recruitment pipeline</p>
              </div>
              <button v-if="activeTab === 'jobs'" @click="activeTab = 'post-job'" class="btn btn-orange rounded-pill px-4 small">+ Post New Role</button>
            </div>

            <!-- Manage Jobs Table -->
            <div v-if="activeTab === 'jobs'" class="table-responsive mt-4">
              <table class="table table-hover align-middle border-top">
                <thead class="text-muted extra-small text-uppercase fw-bold">
                  <tr><th>ID</th><th>Role Details</th><th>Approval</th><th>Compensation</th><th>Status</th><th>Applications</th><th class="text-end">Actions</th></tr>
                </thead>
                <tbody class="small fw-medium">
                  <tr v-for="job in jobsData" :key="job.id">
                    <td>#{{ job.id }}</td>
                    <td>
                      <div class="fw-bold text-dark">{{ job.title }}</div>
                      <div class="extra-small text-muted">Created: {{ job.created_at || 'Recent' }}</div>
                    </td>
                    <td>
                      <span :class="['badge rounded-pill px-3', job.verified ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning']">
                        {{ job.verified ? 'Verified' : 'Pending' }}
                      </span>
                    </td>
                    <td><div class="fw-bold text-dark">{{ job.salary }}</div><div class="extra-small text-muted">Remote / Hybrid</div></td>
                    <td>
                      <span :class="['badge rounded-pill px-3', job.status === 'Approved' ? 'bg-success-soft text-success' : 'bg-secondary-soft text-secondary']">
                        {{ job.status === 'Approved' ? 'Accepting Applications' : 'Closed' }}
                      </span>
                    </td>
                    <td><span class="badge border bg-light text-dark">{{ job.applications_count }} Received</span></td>
                    <td class="text-end">
                      <button class="btn btn-light rounded-circle shadow-none border me-1"><i class="bi bi-pencil small"></i></button>
                      <button class="btn btn-outline-orange rounded-pill px-3 me-1">Close</button>
                      <button class="btn btn-light rounded-circle shadow-none border text-danger"><i class="bi bi-trash small"></i></button>
                    </td>
                  </tr>
                </tbody>
              </table>
              <div v-if="jobsData.length === 0" class="text-center py-5">
                <i class="bi bi-briefcase display-4 text-light"></i>
                <p class="text-muted mt-3">You haven't posted any jobs yet.</p>
              </div>
            </div>

            <!-- Post Job View -->
            <div v-if="activeTab === 'post-job'" class="post-job-form mx-auto" style="max-width: 800px;">
              <form @submit.prevent="handlePostJob">
                <div class="row g-4 mt-2">
                  <div class="col-md-12">
                    <label class="form-label fw-bold small">Job Title</label>
                    <input v-model="jobForm.title" type="text" class="form-control rounded-3 border-light shadow-none p-3" placeholder="e.g. Senior Software Engineer" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-bold small">Compensation (Annual CTC)</label>
                    <input v-model="jobForm.salary" type="text" class="form-control rounded-3 border-light shadow-none p-3" placeholder="e.g. 12 - 15 LPA" required>
                  </div>
                  <div class="col-md-6">
                    <label class="form-label fw-bold small">Application Deadline</label>
                    <input v-model="jobForm.deadline" type="date" class="form-control rounded-3 border-light shadow-none p-3" required>
                  </div>
                  <div class="col-md-12">
                    <label class="form-label fw-bold small">Job Description</label>
                    <textarea v-model="jobForm.description" class="form-control rounded-3 border-light shadow-none p-3" rows="5" placeholder="Describe roles, responsibilities and requirements..." required></textarea>
                  </div>
                  <div class="col-12 text-center mt-5">
                    <button type="submit" class="btn btn-orange rounded-pill px-5 py-3 fw-bold shadow">Submit Job for Verification</button>
                  </div>
                </div>
              </form>
            </div>

            <!-- Applicants View placeholder -->
            <div v-if="activeTab === 'applicants'" class="text-center py-5">
              <i class="bi bi-people display-4 text-light"></i>
              <h5 class="text-muted mt-3">Select a job from 'Manage Jobs' to view specific applicants</h5>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import Sidebar from '../../components/Sidebar.vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler)

const router = useRouter()
const activeTab = ref('dashboard')
const username = ref(localStorage.getItem('username'))
const stats = ref({ recruitment_status: {} })
const jobsData = ref([])

const companyMenu = [
  { id: 'dashboard', label: 'Dashboard', icon: 'bi-grid-fill' },
  { id: 'post-job', label: 'Post Job', icon: 'bi-plus-circle-fill' },
  { id: 'jobs', label: 'Manage Jobs', icon: 'bi-list-ul' },
  { id: 'applicants', label: 'Applicants Across all Jobs', icon: 'bi-people-fill' },
  { id: 'shortlisted', label: 'Shortlisted', icon: 'bi-star-fill' }
]

const jobForm = ref({ title: '', salary: '', deadline: '', description: '', allowed_branches: ['CSE', 'ECE'] })

const refreshData = async () => {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }
  try {
    if (activeTab.value === 'dashboard') {
      const res = await axios.get('http://127.0.0.1:5000/api/company/stats', { headers })
      stats.value = res.data
    } else if (activeTab.value === 'jobs') {
      const res = await axios.get('http://127.0.0.1:5000/api/company/jobs', { headers })
      jobsData.value = res.data
    }
  } catch (err) { console.error('API Error:', err) }
}

const handlePostJob = async () => {
  try {
    await axios.post('http://127.0.0.1:5000/api/company/post-job', jobForm.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    alert('Job submitted successfully!')
    activeTab.value = 'jobs'
  } catch (err) { alert(err.response?.data?.message || 'Error posting job') }
}

watch(activeTab, refreshData)
onMounted(refreshData)

const handleLogout = () => { localStorage.clear(); router.push('/login') }
const activeMenuLabel = computed(() => companyMenu.find(item => item.id === activeTab.value)?.label || 'Overview')

// Mock Chart Data for Monthly Trend
const trendChartData = {
  labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  datasets: [{
    label: 'Applications',
    borderColor: '#f97316',
    backgroundColor: 'rgba(249, 115, 22, 0.1)',
    data: [0, 0, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0],
    borderWidth: 3, tension: 0.4, pointRadius: 5, fill: true
  }]
}

const trendChartOptions = {
  responsive: true,
  maintainAspectRatio: false,
  plugins: { legend: { display: false } },
  scales: {
    y: { grid: { color: '#f1f5f9' }, min: 0, max: 5 },
    x: { grid: { display: false } }
  }
}
</script>

<style scoped>
.app-container { display: flex; width: 100vw; min-height: 100vh; background-color: #f8fafc; overflow-x: hidden; }
.main-workspace { flex: 1; margin-left: 240px; display: flex; flex-direction: column; width: calc(100vw - 240px); }
.top-navbar { height: 75px; z-index: 10; display: flex; align-items: center; }
.portal-title-left { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #64748b; letter-spacing: 0.1rem; }

.avatar-circle-company { width: 42px; height: 42px; background-color: #0f172a; color: white; display: flex; align-items: center; justify-content: center; border-radius: 12px; font-weight: 800; }
.extra-small { font-size: 10px; }
.text-muted-extra { font-size: 10px; opacity: 0.3; }

.fluid-card { background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 1.5rem; border: 1px solid #f1f5f9; transition: transform 0.2s ease; width: 100%; }
.border-s-orange { border-left: 6px solid #f97316; }

.btn-orange { background-color: #f97316; color: white; border: none; }
.btn-orange:hover { background-color: #ea580c; color: white; }
.btn-outline-orange { border: 1px solid #f97316; color: #f97316; }
.btn-outline-orange:hover { background: #f97316; color: white; }

.bg-success-soft { background: #d1fae5; }
.bg-warning-soft { background: #fffbeb; }
.bg-secondary-soft { background: #f1f5f9; }

.stats-value-small { font-size: 2.2rem; }
.stat-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; margin-top: 0.5rem; }

.list-group-item:hover { background-color: #f8fafc; }
.tracking-widest { letter-spacing: 0.15em; }

@media (max-width: 1200px) { .main-workspace { margin-left: 0; width: 100vw; } }
</style>
