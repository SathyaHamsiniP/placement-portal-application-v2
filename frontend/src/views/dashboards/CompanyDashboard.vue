<template>
  <div class="app-container">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="companyMenu"
      :username="stats?.company_name || username"
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
            <div class="avatar-circle-company me-3">{{ (stats?.company_name || username)?.[0]?.toUpperCase() }}</div>
            <div class="profile-text text-start">
              <div class="fw-bold text-dark small leading-tight">{{ stats?.company_name || (username + ' Inc.') }}</div>
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
                <h4 class="fw-bold mb-0 text-dark">{{ stats?.company_name || (username + ' Inc.') }}</h4>
                <p class="text-muted small text-uppercase tracking-widest mb-0">{{ stats?.industry || 'SOFTWARE' }} | MANAGEMENT CENTER</p>
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
                  <button @click="activeTab = 'jobs'" class="list-group-item list-group-item-action border-0 rounded-3 small d-flex justify-content-between align-items-center">
                    <span><i class="bi bi-briefcase me-3 text-primary"></i> Manage All Jobs</span>
                    <i class="bi bi-chevron-right text-muted-extra"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Management Units -->
        <div v-else class="management-root">
          <div class="fluid-card min-vh-75">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <div>
                <h4 v-if="!selectedJob" class="fw-bold mb-1">{{ activeMenuLabel }}</h4>
                <div v-else class="d-flex align-items-center">
                  <button @click="selectedJob = null" class="btn btn-link p-0 me-3"><i class="bi bi-arrow-left fs-4 text-dark"></i></button>
                  <h4 class="fw-bold mb-1">Applicants: {{ selectedJob.title }}</h4>
                </div>
                <p class="text-muted extra-small mb-0">Track and manage your recruitment pipeline</p>
              </div>
              <div class="d-flex align-items-center gap-2">
                <span v-if="exportStatus" class="extra-small text-muted">{{ exportStatus }}</span>
                <button @click="exportCSV" :disabled="exportLoading" class="btn btn-sm btn-outline-dark rounded-3 px-3 extra-small" style="min-width:130px">
                  <i class="bi bi-file-earmark-arrow-down me-1"></i>
                  {{ exportLoading ? 'Exporting...' : 'Export CSV' }}
                </button>
              </div>
            </div>

            <!-- Manage Jobs Table -->
            <div v-if="activeTab === 'jobs' && !selectedJob" class="table-responsive mt-4">
              <table class="table table-hover align-middle border-top">
                <thead class="text-muted extra-small text-uppercase fw-bold">
                  <tr><th>ID</th><th>Role Details</th><th>Approval</th><th>Applications</th><th class="text-end">Actions</th></tr>
                </thead>
                <tbody class="small fw-medium">
                  <tr v-for="job in jobsData" :key="job.id">
                    <td>#{{ job.id }}</td>
                    <td><div class="fw-bold text-dark">{{ job.title }}</div><div class="extra-small text-muted">{{ job.salary }}</div></td>
                    <td><span :class="['badge rounded', job.verified ? 'bg-success-soft text-success' : 'bg-warning-soft text-warning']">{{ job.verified ? 'Verified' : 'Pending' }}</span></td>
                    <td><button @click="viewApplicants(job)" class="btn btn-link btn-sm p-0">{{ job.applications_count }} Received</button></td>
                    <td class="text-end">
                      <button @click="viewApplicants(job)" class="btn btn-sm btn-outline-dark rounded-3 px-3 me-2" style="min-width: 140px">Manage Candidates</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Applicants Details View -->
            <div v-if="selectedJob" class="applicants-list mt-4">
              <table class="table table-hover align-middle border-top">
                <thead class="text-muted extra-small text-uppercase fw-bold">
                  <tr><th>Student</th><th>Branch / CGPA</th><th>Status</th><th>Applied Date</th><th class="text-end">Action</th></tr>
                </thead>
                <tbody class="small fw-medium">
                  <tr v-for="app in applicants" :key="app.id">
                    <td>
                      <button @click="viewStudentProfile(app)" class="btn btn-link p-0 fw-bold text-dark text-decoration-underline extra-small">{{ app.student_name }}</button>
                      <div class="extra-small text-muted">{{ app.roll_number }}</div>
                    </td>
                    <td>{{ app.branch }} | {{ app.cgpa }}</td>
                    <td><span :class="['badge rounded', app.status === 'Applied' ? 'bg-light text-dark' : 'bg-primary-soft text-primary']">{{ app.status }}</span></td>
                    <td class="extra-small text-muted">{{ new Date(app.applied_at).toLocaleDateString() }}</td>
                    <td class="text-end">
                      <button @click="openStatusModal(app)" class="btn btn-sm btn-outline-dark rounded-3 px-3" style="min-width: 140px">Update Status</button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Post Job View -->
            <div v-if="activeTab === 'post-job'" class="post-job-form mx-auto" style="max-width: 800px;">
              <!-- ... Form (same as before) ... -->
              <form @submit.prevent="handlePostJob">
                <div class="row g-4 mt-2">
                  <div class="col-md-12"><label class="form-label fw-bold small">Job Title</label>
                    <input v-model="jobForm.title" type="text" class="form-control rounded-3 border-light p-3" placeholder="e.g. Software Engineer" required></div>
                  <div class="col-md-6"><label class="form-label fw-bold small">Compensation</label>
                    <input v-model="jobForm.salary" type="text" class="form-control rounded-3 border-light p-3" placeholder="e.g. 10 LPA" required></div>
                  <div class="col-md-6"><label class="form-label fw-bold small">Deadline</label>
                    <input v-model="jobForm.deadline" type="date" class="form-control rounded-3 border-light p-3" required></div>
                  <div class="col-md-12"><label class="form-label fw-bold small">Description</label>
                    <textarea v-model="jobForm.description" class="form-control rounded-3 border-light p-3" rows="4" required></textarea></div>
                  <div class="col-12 text-center mt-4">
                    <button type="submit" class="btn btn-orange rounded-3 px-5 py-3 fw-bold">Submit Job</button>
                  </div>
                </div>
              </form>
            </div>
          </div>
        </div>
      </div>

      <!-- Status Update Modal -->
      <div v-if="showStatusModal" class="modal-overlay d-flex align-items-center justify-content-center">
        <div class="fluid-card shadow-lg" style="max-width: 500px;">
          <h5 class="fw-bold mb-3">Update Application Status</h5>
          <label class="small text-muted mb-2 d-block">Student: {{ currentApp.student_name }}</label>
          
          <select v-model="statusUpdate.status" class="form-select mb-4 p-3 rounded-3 border-light">
            <option value="Review Pending">Move to Review</option>
            <option value="Shortlisted">Shortlist Candidate</option>
            <option value="Interviewed">Mark as Interviewed</option>
            <option value="Offered">Extend Offer</option>
            <option value="Placed">Confirm Placement (Final)</option>
            <option value="Rejected">Reject Application</option>
          </select>
          
          <label class="small fw-bold mb-2 d-block">Corporate Feedback</label>
          <textarea v-model="statusUpdate.feedback" class="form-control mb-4 p-3 rounded-3 border-light" rows="3" placeholder="Provide feedback for the student..."></textarea>
          
          <div v-if="statusUpdate.status === 'Interviewed'" class="mb-4 text-start">
            <label class="small fw-bold mb-2 d-block">Interview Date & Time</label>
            <input v-model="statusUpdate.interview_date" type="datetime-local" class="form-control p-3 rounded-3 border-light" required />
          </div>
          
          <div class="d-flex gap-2">
            <button @click="showStatusModal = false" class="btn btn-light flex-fill rounded-3">Cancel</button>
            <button @click="submitStatusUpdate" class="btn btn-orange flex-fill rounded-3 fw-bold">Confirm Update</button>
          </div>
        </div>
      </div>

      <!-- Student Profile Modal -->
      <div v-if="showProfileModal" class="modal-overlay d-flex align-items-center justify-content-center">
        <div class="fluid-card shadow-lg" style="max-width:560px; width:100%; max-height:85vh; overflow-y:auto;">
          <div class="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h5 class="fw-bold mb-1">{{ studentProfile.full_name }}</h5>
              <div class="extra-small text-muted">{{ studentProfile.roll_number }} &nbsp;·&nbsp; {{ studentProfile.branch }} &nbsp;·&nbsp; {{ studentProfile.grad_year }}</div>
            </div>
            <button @click="showProfileModal = false" class="btn btn-light rounded-3 btn-sm"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="row g-3 mb-4">
            <div class="col-6 p-3 bg-light rounded-3 text-center">
              <div class="fw-bold fs-4 text-dark">{{ studentProfile.cgpa }}</div>
              <div class="extra-small text-muted">CGPA / 10.0</div>
            </div>
            <div class="col-6 p-3 bg-light rounded-3 text-center">
              <div class="fw-bold fs-4 text-dark">{{ (studentProfile.application_history || []).length }}</div>
              <div class="extra-small text-muted">Total Applications</div>
            </div>
          </div>
          <div class="mb-3" v-if="studentProfile.skills && studentProfile.skills.length">
            <div class="extra-small text-muted text-uppercase fw-bold mb-2">Skills</div>
            <div class="d-flex flex-wrap gap-2">
              <span v-for="s in studentProfile.skills" :key="s" class="badge bg-light text-dark border extra-small px-3 py-2">{{ s }}</span>
            </div>
          </div>
          <div class="mb-3" v-if="studentProfile.education_details">
            <div class="extra-small text-muted text-uppercase fw-bold mb-1">Education</div>
            <p class="extra-small text-dark mb-0">{{ studentProfile.education_details }}</p>
          </div>
          <div class="mb-4" v-if="studentProfile.experience">
            <div class="extra-small text-muted text-uppercase fw-bold mb-1">Experience</div>
            <p class="extra-small text-dark mb-0">{{ studentProfile.experience }}</p>
          </div>
          <div v-if="studentProfile.application_history && studentProfile.application_history.length">
            <div class="extra-small text-muted text-uppercase fw-bold mb-2">Application Track Record</div>
            <div class="table-responsive">
              <table class="table table-sm align-middle extra-small">
                <thead class="text-muted text-uppercase"><tr><th>Role</th><th>Company</th><th>Status</th><th>Applied</th></tr></thead>
                <tbody>
                  <tr v-for="h in studentProfile.application_history" :key="h.id">
                    <td class="fw-bold">{{ h.job_title }}</td>
                    <td>{{ h.company_name }}</td>
                    <td><span :class="['badge rounded', h.status === 'Placed' ? 'bg-success text-white' : h.status === 'Rejected' ? 'bg-danger text-white' : 'bg-light text-dark border']">{{ h.status }}</span></td>
                    <td class="text-muted">{{ new Date(h.applied_at).toLocaleDateString() }}</td>
                  </tr>
                </tbody>
              </table>
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
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { Line } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, CategoryScale, LinearScale, PointElement, LineElement, Filler)

const router = useRouter()
const route = useRoute()
const activeTab = ref(route.hash ? route.hash.substring(1) : 'dashboard')

watch(activeTab, (newTab) => {
  if (route.hash !== `#${newTab}`) {
    router.push({ hash: `#${newTab}` })
  }
})

watch(() => route.hash, (newHash) => {
  const tab = newHash ? newHash.substring(1) : 'dashboard'
  if (activeTab.value !== tab) {
    activeTab.value = tab
  }
})
const username = ref(localStorage.getItem('username'))
const stats = ref({ recruitment_status: {} })
const jobsData = ref([])
const selectedJob = ref(null)
const applicants = ref([])

// Modal States
const showStatusModal = ref(false)
const currentApp = ref(null)
const statusUpdate = ref({ status: 'Shortlisted', feedback: '', interview_date: '' })
const showProfileModal = ref(false)
const studentProfile = ref({})

const viewStudentProfile = async (app) => {
  try {
    const res = await axios.get(`http://127.0.0.1:5000/api/admin/student/${app.student_id}`, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    studentProfile.value = res.data
    showProfileModal.value = true
  } catch (err) { alert('Could not load student profile') }
}

const companyMenu = [
  { id: 'dashboard', label: 'Dashboard', icon: 'bi-grid-fill' },
  { id: 'post-job', label: 'Post Job', icon: 'bi-plus-circle-fill' },
  { id: 'jobs', label: 'Manage Jobs', icon: 'bi-list-ul' }
]

const jobForm = ref({ title: '', salary: '', deadline: '', description: '', allowed_branches: ['CSE'] })

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

const viewApplicants = async (job) => {
  selectedJob.value = job
  const res = await axios.get(`http://127.0.0.1:5000/api/company/applicants/${job.id}`, {
    headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
  })
  applicants.value = res.data
}

const openStatusModal = (app) => {
  currentApp.value = app
  statusUpdate.value = { status: app.status === 'Applied' ? 'Shortlisted' : app.status, feedback: '', interview_date: '' }
  showStatusModal.value = true
}

const submitStatusUpdate = async () => {
  try {
    await axios.post(`http://127.0.0.1:5000/api/company/application/update-status/${currentApp.value.id}`, statusUpdate.value, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    showStatusModal.value = false
    viewApplicants(selectedJob.value)
    refreshData()
  } catch (err) { alert('Error updating status') }
}

const handlePostJob = async () => {
  await axios.post('http://127.0.0.1:5000/api/company/post-job', jobForm.value, { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } })
  activeTab.value = 'jobs'; refreshData()
}

watch(activeTab, () => { selectedJob.value = null; refreshData() })
onMounted(refreshData)

const handleLogout = () => { localStorage.clear(); router.push('/login') }
const activeMenuLabel = computed(() => companyMenu.find(item => item.id === activeTab.value)?.label || 'Overview')

const trendChartData = { labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'], datasets: [{ label: 'Applications', borderColor: '#f97316', backgroundColor: 'rgba(249, 115, 22, 0.1)', data: [0, 0, 0, 0, 5, 2, 0, 0, 0, 0, 0, 0], borderWidth: 3, tension: 0.4, fill: true }]}
const trendChartOptions = { responsive: true, maintainAspectRatio: false, plugins: { legend: { display: false } }, scales: { y: { grid: { color: '#f1f5f9' }, min: 0, max: 10 }, x: { grid: { display: false } } } }

// ── CSV Export ─────────────────────────────────────────────────────────────────
const exportLoading = ref(false)
const exportStatus = ref('')

const exportCSV = async () => {
  exportLoading.value = true
  exportStatus.value = 'Starting export...'
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/jobs/export/company', {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    const taskId = res.data.task_id
    exportStatus.value = 'Processing...'
    const interval = setInterval(async () => {
      try {
        const poll = await axios.get(`http://127.0.0.1:5000/api/jobs/task/${taskId}`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
        })
        if (poll.data.status === 'SUCCESS') {
          clearInterval(interval)
          exportLoading.value = false
          const file = poll.data.result?.file
          exportStatus.value = file ? `Ready: ${file}` : 'Export complete!'
          if (file) {
            const dl = await axios.get(`http://127.0.0.1:5000/api/jobs/exports/${file}`, {
              headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
              responseType: 'blob'
            })
            const url = window.URL.createObjectURL(new Blob([dl.data]))
            const a = document.createElement('a'); a.href = url; a.download = file; a.click()
          }
        } else if (poll.data.status === 'FAILURE') {
          clearInterval(interval); exportLoading.value = false; exportStatus.value = 'Export failed.'
        }
      } catch { clearInterval(interval); exportLoading.value = false }
    }, 2000)
  } catch {
    exportStatus.value = 'Export failed.'
    exportLoading.value = false
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
.fluid-card { background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 1.5rem; border: 1px solid #f1f5f9; width: 100%; transition: transform 0.2s ease; }
.border-s-orange { border-left: 6px solid #f97316; }
.btn-orange { background-color: #f97316; color: white; border: none; }
.bg-success-soft { background: #d1fae5; }
.bg-warning-soft { background: #fffbeb; }
.bg-primary-soft { background: #eff6ff; }
.stats-value-small { font-size: 2.2rem; }
.stat-label { font-size: 0.7rem; font-weight: 700; text-transform: uppercase; color: #94a3b8; letter-spacing: 0.05em; margin-top: 0.5rem; }
.modal-overlay { position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(15, 23, 42, 0.4); backdrop-filter: blur(4px); z-index: 1000; }
@media (max-width: 1200px) { .main-workspace { margin-left: 0; width: 100vw; } }
</style>
