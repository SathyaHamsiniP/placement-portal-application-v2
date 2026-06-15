<template>
  <div class="app-container">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="adminMenu"
      :username="username"
      role="Administrator"
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
            <div class="avatar-circle me-3">{{ username?.[0]?.toUpperCase() }}</div>
            <div class="profile-text text-start">
              <div class="fw-bold text-dark small leading-tight">{{ username }}</div>
              <div class="text-muted extra-small">Administrator</div>
            </div>
          </div>
        </div>
      </header>

      <div class="workspace-content p-4">
        <!-- Overview Tab -->
        <div v-if="activeTab === 'dashboard'" class="dashboard-root">
          <!-- Stats Row -->
          <div class="fluid-card mb-4 mt-1">
            <div class="stats-grid-row d-flex text-center py-2">
              <div class="stat-col flex-fill">
                <h1 class="stats-value-small fw-bold mb-0 text-dark">{{ stats.total_students || 0 }}</h1>
                <div class="stat-label">Active Students</div>
              </div>
              <div class="stat-col flex-fill border-start">
                <h1 class="stats-value-small fw-bold mb-0 text-dark">{{ stats.total_companies || 0 }}</h1>
                <div class="stat-label">Partner Companies</div>
              </div>
              <div class="stat-col flex-fill border-start">
                <h1 class="stats-value-small fw-bold mb-0 text-primary">5%</h1>
                <div class="stat-label">Placement Rate</div>
              </div>
              <div class="stat-col flex-fill border-start">
                <h1 class="stats-value-small fw-bold mb-0 text-dark">{{ stats.total_jobs || 0 }}</h1>
                <div class="stat-label">Verified Jobs</div>
              </div>
            </div>
          </div>

          <!-- Line Chart -->
          <div class="row mb-4">
            <div class="col-12">
              <div class="fluid-card">
                <div class="d-flex justify-content-between align-items-start mb-4">
                  <div>
                    <h5 class="fw-bold mb-1">Placement Velocity</h5>
                    <p class="text-muted extra-small mb-0">Daily cumulative offers generated over the season</p>
                  </div>
                  <div class="sync-tag">Real-time Tracker</div>
                </div>
                <div class="chart-container" style="height: 380px;">
                  <Line :data="lineChartData" :options="lineChartOptions" />
                </div>
              </div>
            </div>
          </div>

          <!-- Bar & Doughnut -->
          <div class="row g-4">
            <div class="col-lg-7">
              <div class="fluid-card h-100">
                <div class="d-flex justify-content-between align-items-start mb-4">
                  <div>
                    <h5 class="fw-bold mb-1">Branch-wise Student Participation</h5>
                    <p class="text-muted extra-small">Applications distributed by department</p>
                  </div>
                </div>
                <div class="chart-container" style="height: 350px;">
                  <Bar :data="barChartData" :options="barChartOptions" />
                </div>
              </div>
            </div>
            <div class="col-lg-5">
              <div class="fluid-card h-100 text-center">
                <div class="text-start mb-4">
                  <h5 class="fw-bold mb-1">Job Market Diversity</h5>
                  <p class="text-muted extra-small">Industry distribution of partner companies</p>
                </div>
                <div class="chart-container d-flex align-items-center justify-content-center" style="height: 350px;">
                  <Doughnut :data="doughnutChartData" :options="doughnutChartOptions" />
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Management Units -->
        <div v-else class="management-root">
          <div class="fluid-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">{{ activeMenuLabel }}</h5>
              <div class="d-flex gap-2">
                <div v-if="activeTab !== 'approvals'" class="search-box position-relative">
                  <i class="bi bi-search position-absolute start-0 top-50 translate-middle-y ms-3 text-muted"></i>
                  <input type="text" v-model="searchQuery" class="form-control ps-5 rounded-pill border-light-subtle extra-small py-2" :placeholder="`Search ${activeTab}...`">
                </div>
                <button @click="refreshData" class="btn btn-light rounded-pill btn-sm px-3 shadow-none border">
                  <i class="bi bi-arrow-clockwise me-1"></i> Refresh
                </button>
              </div>
            </div>

            <!-- Management Table -->
            <div class="table-responsive">
              <table class="table table-hover align-middle border-top">
                <thead class="text-muted extra-small text-uppercase fw-bold">
                  <tr v-if="activeTab === 'students'">
                    <th>Name</th><th>Roll Number</th><th>Branch</th><th>Status</th><th class="text-end">Actions</th>
                  </tr>
                  <tr v-if="activeTab === 'companies'">
                    <th>Company Name</th><th>Industry</th><th>Verification</th><th>Status</th><th class="text-end">Actions</th>
                  </tr>
                  <tr v-if="activeTab === 'jobs'">
                    <th>Position Title</th><th>Company</th><th>Salary</th><th>Status</th><th class="text-end">Actions</th>
                  </tr>
                  <tr v-if="activeTab === 'applications'">
                    <th>Student</th><th>Job Title</th><th>Company</th><th>Submitted</th><th>Status</th>
                  </tr>
                  <tr v-if="activeTab === 'approvals'">
                    <th>Type</th><th>Name / Title</th><th>Entity</th><th>Requested Date</th><th class="text-end">Action</th>
                  </tr>
                </thead>
                <tbody class="small fw-medium">
                  <!-- Students -->
                  <template v-if="activeTab === 'students'">
                    <tr v-for="std in filteredData" :key="std.id">
                      <td><div class="d-flex align-items-center"><div class="avatar-sm me-2">{{ std.full_name[0] }}</div>{{ std.full_name }}</div></td>
                      <td>{{ std.roll_number }}</td>
                      <td><span class="badge bg-light text-dark border">{{ std.branch }}</span></td>
                      <td><span :class="['badge rounded-pill px-3', std.is_active ? 'bg-success-soft text-success' : 'bg-danger-soft text-danger']">{{ std.is_active ? 'Active' : 'Blacklisted' }}</span></td>
                      <td class="text-end"><button @click="toggleActive(std.user_id)" :class="['btn btn-sm rounded-pill px-3', std.is_active ? 'btn-outline-danger' : 'btn-outline-success']">{{ std.is_active ? 'Blacklist' : 'Activate' }}</button></td>
                    </tr>
                  </template>

                  <!-- Companies -->
                  <template v-if="activeTab === 'companies'">
                    <tr v-for="comp in filteredData" :key="comp.id">
                      <td>{{ comp.name }}</td><td>{{ comp.industry }}</td>
                      <td><span :class="['badge rounded-pill', comp.is_approved ? 'bg-success' : 'bg-warning']">{{ comp.is_approved ? 'Verified' : 'Pending' }}</span></td>
                      <td><span :class="['badge rounded-pill', comp.is_active ? 'bg-success-soft text-success' : 'bg-danger-soft text-danger']">{{ comp.is_active ? 'Enabled' : 'Deactivated' }}</span></td>
                      <td class="text-end">
                        <button v-if="!comp.is_approved" @click="approveCompany(comp.id)" class="btn btn-sm btn-success rounded-pill px-3 me-2">Approve</button>
                        <button @click="toggleActive(comp.user_id)" class="btn btn-sm btn-outline-danger rounded-pill px-3">Toggle Status</button>
                      </td>
                    </tr>
                  </template>

                  <!-- Jobs -->
                  <template v-if="activeTab === 'jobs'">
                    <tr v-for="job in filteredData" :key="job.id">
                      <td>{{ job.title }}</td><td>{{ job.company_name }}</td><td>{{ job.salary }}</td>
                      <td><span :class="['badge rounded-pill', job.status === 'Approved' ? 'bg-success' : 'bg-warning']">{{ job.status }}</span></td>
                      <td class="text-end">
                        <button v-if="job.status === 'Pending'" @click="approveJob(job.id)" class="btn btn-sm btn-success rounded-pill px-3 me-2">Verify</button>
                        <button class="btn btn-sm btn-outline-secondary rounded-pill px-3">View Applications</button>
                      </td>
                    </tr>
                  </template>

                  <!-- Applications -->
                  <template v-if="activeTab === 'applications'">
                    <tr v-for="app in filteredData" :key="app.id">
                      <td>{{ app.student_name }}</td><td>{{ app.job_title }}</td><td>{{ app.company_name }}</td>
                      <td class="extra-small text-muted">{{ new Date(app.applied_on).toLocaleDateString() }}</td>
                      <td><span class="badge bg-light text-dark border">{{ app.status }}</span></td>
                    </tr>
                  </template>

                  <!-- Pending Approvals -->
                  <template v-if="activeTab === 'approvals'">
                    <tr v-for="item in rawData" :key="item.id + item.type">
                      <td><span :class="['badge extra-small text-uppercase', item.type === 'company' ? 'bg-info-soft text-info' : 'bg-warning-soft text-warning']">{{ item.type }}</span></td>
                      <td>{{ item.name }}</td><td>{{ item.entity }}</td>
                      <td class="extra-small text-muted">Pending Review</td>
                      <td class="text-end">
                        <button @click="item.type === 'company' ? approveCompany(item.id) : approveJob(item.id)" class="btn btn-sm btn-primary rounded-pill px-3">Quick Approve</button>
                      </td>
                    </tr>
                  </template>
                </tbody>
              </table>

              <div v-if="filteredData.length === 0" class="text-center py-5">
                <i class="bi bi-search fs-2 text-light"></i>
                <p class="text-muted small mt-2">No pending items or search results.</p>
              </div>
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
import { Bar, Line, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ArcElement)

const router = useRouter()
const activeTab = ref('dashboard')
const username = ref(localStorage.getItem('username'))
const searchQuery = ref('')
const stats = ref({})
const rawData = ref([])

const adminMenu = [
  { id: 'dashboard', label: 'Overview', icon: 'bi-grid-fill' },
  { id: 'students', label: 'Students', icon: 'bi-people-fill' },
  { id: 'companies', label: 'Companies', icon: 'bi-building-fill' },
  { id: 'jobs', label: 'Job Postings', icon: 'bi-briefcase-fill' },
  { id: 'applications', label: 'Applications', icon: 'bi-file-earmark-text-fill' },
  { id: 'approvals', label: 'Pending Approvals', icon: 'bi-clock-fill' }
]

const refreshData = async () => {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }
  try {
    if (activeTab.value === 'dashboard') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/stats', { headers })
      stats.value = res.data
    } else if (activeTab.value === 'students') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/students', { headers })
      rawData.value = res.data
    } else if (activeTab.value === 'companies') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/companies', { headers })
      rawData.value = res.data
    } else if (activeTab.value === 'jobs') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/jobs', { headers })
      rawData.value = res.data
    } else if (activeTab.value === 'applications') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/applications', { headers })
      rawData.value = res.data
    } else if (activeTab.value === 'approvals') {
      const comps = await axios.get('http://127.0.0.1:5000/api/admin/companies', { headers })
      const jobs = await axios.get('http://127.0.0.1:5000/api/admin/jobs', { headers })
      const pendingComps = comps.data.filter(c => !c.is_approved).map(c => ({ ...c, type: 'company', entity: c.industry }))
      const pendingJobs = jobs.data.filter(j => j.status === 'Pending').map(j => ({ ...j, type: 'job', name: j.title, entity: j.company_name }))
      rawData.value = [...pendingComps, ...pendingJobs]
    }
  } catch (err) { console.error('API Error:', err) }
}

const toggleActive = async (userId) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/user/toggle-active/${userId}`, {}, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
  refreshData()
}

const approveCompany = async (id) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/company/approve/${id}`, {}, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
  refreshData()
}

const approveJob = async (id) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/job/approve/${id}`, {}, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
  refreshData()
}

const filteredData = computed(() => {
  if (!searchQuery.value) return rawData.value
  const q = searchQuery.value.toLowerCase()
  return rawData.value.filter(item => {
    if (activeTab.value === 'students') return item.full_name.toLowerCase().includes(q) || item.roll_number.includes(q)
    if (activeTab.value === 'companies') return item.name.toLowerCase().includes(q) || item.industry.toLowerCase().includes(q)
    if (activeTab.value === 'jobs') return item.title.toLowerCase().includes(q) || item.company_name.toLowerCase().includes(q)
    if (activeTab.value === 'applications') return item.student_name.toLowerCase().includes(q) || item.job_title.toLowerCase().includes(q)
    return true
  })
})

watch(activeTab, () => { searchQuery.value = ''; rawData.value = []; refreshData() })

const lineChartData = { labels: ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5', 'Week 6', 'Week 7', 'Week 8'], datasets: [{ label: 'Total Offers', borderColor: '#0d6efd', backgroundColor: 'rgba(13, 110, 253, 0.1)', data: [2, 11, 25, 48, 65, 82, 110, 145], borderWidth: 4, tension: 0.4, fill: true }] }
const barChartData = { labels: ['Chemical Eng.', 'Civil Eng.', 'Computer Sci.', 'Electrical Eng.', 'Mechanical Eng.'], datasets: [{ label: 'Students', backgroundColor: '#f97316', borderRadius: 8, data: [6, 8, 12, 10, 7], barThickness: 45 }] }
const doughnutChartData = { labels: ['IT/Software', 'Finance', 'Consulting', 'Core Engineering', 'EdTech'], datasets: [{ data: [45, 20, 15, 12, 8], backgroundColor: ['#0d6efd', '#f97316', '#10b981', '#6366f1', '#f43f5e'], borderWidth: 0 }] }
const chartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } } }
const lineChartOptions = { ...chartOptions, scales: { y: { grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } } }
const barChartOptions = { ...chartOptions, scales: { y: { grid: { color: '#f1f5f9' } }, x: { grid: { display: false } } } }
const doughnutChartOptions = { ...chartOptions, plugins: { legend: { display: true, position: 'bottom', labels: { usePointStyle: true, boxWidth: 10 } } }, cutout: '70%'}

onMounted(refreshData)
const handleLogout = () => { localStorage.clear(); router.push('/login') }
</script>

<style scoped>
.app-container { display: flex; width: 100vw; min-height: 100vh; background-color: #f8fafc; overflow-x: hidden; }
.main-workspace { flex: 1; margin-left: 240px; display: flex; flex-direction: column; width: calc(100vw - 240px); }
.top-navbar { height: 75px; z-index: 10; display: flex; align-items: center; }
.portal-title-left { font-size: 0.9rem; font-weight: 800; text-transform: uppercase; color: #334155; letter-spacing: 0.12rem; }
.avatar-circle { width: 42px; height: 42px; background-color: #0f172a; color: white; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 800; }
.avatar-sm { width: 32px; height: 32px; background: #e2e8f0; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: 700; color: #475569; }
.extra-small { font-size: 10px; }
.bg-success-soft { background: #d1fae5; }
.bg-danger-soft { background: #fee2e2; }
.bg-warning-soft { background: #fffbeb; }
.bg-info-soft { background: #f0f9ff; }
.fluid-card { background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 1.5rem; border: 1px solid #f1f5f9; transition: transform 0.2s ease; width: 100%; }
.search-box input { width: 300px; transition: all 0.3s ease; }
.search-box input:focus { width: 400px; border-color: #f97316; box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.1); }
.table th { border-bottom: 2px solid #f8fafc; }
.table tr:hover { background-color: #fcfdfe; }
.stat-label { font-size: 0.75rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; margin-top: 0.4rem; }
.sync-tag { font-size: 0.7rem; color: #64748b; background: #f8fafc; padding: 0.4rem 0.8rem; border-radius: 8px; border: 1px solid #e2e8f0; font-weight: 600; }
@media (max-width: 1200px) { .main-workspace { margin-left: 0; width: 100vw; } }
</style>
