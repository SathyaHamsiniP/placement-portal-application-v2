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
                <h1 class="stats-value-small fw-bold mb-0 text-primary">{{ stats.placement_rate || 0 }}%</h1>
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

        <!-- Reports & Tasks Tab -->
        <div v-if="activeTab === 'reports'" class="reports-root">
          <div class="row g-4">
            <!-- Monthly Report Card -->
            <div class="col-md-6">
              <div class="fluid-card h-100">
                <div class="d-flex align-items-center mb-3">
                  <div class="report-icon-wrap me-3"><i class="bi bi-file-earmark-bar-graph-fill"></i></div>
                  <div>
                    <h6 class="fw-bold mb-0">Monthly Placement Report</h6>
                    <p class="text-muted extra-small mb-0">Generates an HTML summary of all placements and emails it to the admin.</p>
                  </div>
                </div>
                <div class="mb-3 extra-small text-muted"><i class="bi bi-clock me-1"></i>Scheduled: 1st of every month at 7:00 AM IST</div>
                <button @click="triggerReport" :disabled="reportTask.loading" class="btn btn-dark rounded-3 px-4 btn-sm w-100">
                  <i class="bi bi-play-fill me-1"></i>
                  {{ reportTask.loading ? 'Queuing...' : 'Trigger Now' }}
                </button>
                <div v-if="reportTask.taskId" class="mt-3">
                  <div class="d-flex justify-content-between extra-small text-muted mb-1">
                    <span>Task ID: <code class="text-dark">{{ reportTask.taskId.substring(0,12) }}...</code></span>
                    <span :class="reportTask.status === 'SUCCESS' ? 'text-success fw-bold' : reportTask.status === 'FAILURE' ? 'text-danger fw-bold' : 'text-warning fw-bold'">
                      {{ reportTask.status }}
                    </span>
                  </div>
                  <div class="progress" style="height:4px">
                    <div class="progress-bar bg-success" :style="{ width: reportTask.status === 'SUCCESS' ? '100%' : reportTask.status === 'FAILURE' ? '100%' : '60%' }"></div>
                  </div>
                  <p v-if="reportTask.status === 'SUCCESS'" class="text-success extra-small mt-2 mb-0"><i class="bi bi-check-circle me-1"></i>Report generated successfully!</p>
                  <p v-if="reportTask.status === 'FAILURE'" class="text-danger extra-small mt-2 mb-0"><i class="bi bi-x-circle me-1"></i>Task failed. Check Celery logs.</p>
                </div>
              </div>
            </div>
            <!-- Interview Reminders Card -->
            <div class="col-md-6">
              <div class="fluid-card h-100">
                <div class="d-flex align-items-center mb-3">
                  <div class="report-icon-wrap me-3" style="background:#fff7ed;color:#f97316"><i class="bi bi-bell-fill"></i></div>
                  <div>
                    <h6 class="fw-bold mb-0">Interview Reminders</h6>
                    <p class="text-muted extra-small mb-0">Sends email reminders to students with interviews scheduled in the next 24 hours.</p>
                  </div>
                </div>
                <div class="mb-3 extra-small text-muted"><i class="bi bi-clock me-1"></i>Scheduled: Every day at 8:00 AM IST</div>
                <button @click="triggerReminders" :disabled="reminderTask.loading" class="btn btn-outline-dark rounded-3 px-4 btn-sm w-100">
                  <i class="bi bi-send-fill me-1"></i>
                  {{ reminderTask.loading ? 'Queuing...' : 'Send Now' }}
                </button>
                <div v-if="reminderTask.taskId" class="mt-3">
                  <div class="d-flex justify-content-between extra-small text-muted mb-1">
                    <span>Task ID: <code class="text-dark">{{ reminderTask.taskId.substring(0,12) }}...</code></span>
                    <span :class="reminderTask.status === 'SUCCESS' ? 'text-success fw-bold' : reminderTask.status === 'FAILURE' ? 'text-danger fw-bold' : 'text-warning fw-bold'">
                      {{ reminderTask.status }}
                    </span>
                  </div>
                  <div class="progress" style="height:4px">
                    <div class="progress-bar bg-warning" :style="{ width: reminderTask.status === 'SUCCESS' ? '100%' : reminderTask.status === 'FAILURE' ? '100%' : '60%' }"></div>
                  </div>
                  <p v-if="reminderTask.status === 'SUCCESS'" class="text-success extra-small mt-2 mb-0"><i class="bi bi-check-circle me-1"></i>Reminders sent successfully!</p>
                  <p v-if="reminderTask.status === 'FAILURE'" class="text-danger extra-small mt-2 mb-0"><i class="bi bi-x-circle me-1"></i>Task failed. Check Celery logs.</p>
                </div>
              </div>
            </div>
            <!-- Info Card -->
            <div class="col-12">
              <div class="fluid-card" style="background:#f8fafc;border:1px dashed #e2e8f0">
                <p class="extra-small text-muted mb-0"><i class="bi bi-info-circle me-1"></i><strong>Note:</strong> These tasks run asynchronously via Celery. Make sure the Celery worker and Redis are running. Task status updates every 2 seconds automatically.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Management Units -->
        <div v-else-if="activeTab !== 'dashboard'" class="management-root">
          <div class="fluid-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">{{ activeMenuLabel }}</h5>
              <div class="d-flex gap-2">
                <div v-if="activeTab !== 'approvals'" class="search-box position-relative">
                  <i class="bi bi-search position-absolute start-0 top-50 translate-middle-y ms-3 text-muted"></i>
                  <input type="text" v-model="searchQuery" class="form-control ps-5 rounded-3 border-light-subtle extra-small py-2" :placeholder="`Search ${activeTab}...`">
                </div>
                <button @click="refreshData" class="btn btn-light rounded-3 btn-sm px-3 shadow-none border">
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
                <tbody class="small">
                  <!-- Students -->
                  <template v-if="activeTab === 'students'">
                    <!--
                    <tr v-for="std in filteredData" :key="std.id">
                      <td><div class="d-flex align-items-center"><div class="avatar-sm me-2">{{ std.full_name[0] }}</div>{{ std.full_name }}</div></td>
                      <td>{{ std.roll_number }}</td>
                      <td><span class="badge bg-light text-dark border rounded">{{ std.branch }}</span></td>
                      <td><span :class="['badge rounded px-3', std.is_active ? 'bg-success-soft text-success' : 'bg-danger-soft text-danger']">{{ std.is_active ? 'Active' : 'Blacklisted' }}</span></td>
                      <td class="text-end">
                        <button @click="toggleActive(std.user_id)" class="btn btn-sm btn-outline-dark rounded-3 px-3 me-2" style="min-width:90px">{{ std.is_active ? 'Blacklist' : 'Activate' }}</button>
                        <button @click="deleteStudent(std.id)" class="btn btn-sm btn-outline-danger rounded-3 px-3" style="min-width:80px">Delete</button>
                      </td>
                    </tr>
                    -->
                    <div class="fluid-card mb-4 mt-1" v-for="std in filteredData" :key="std.id">
                      <div class="stat-col flex-fill">
                        <h1 class="stats-value-small fw-bold mb-0 text-dark">{{ std.full_name }}</h1>
                        <div class="stat-label">{{ std.roll_number }}</div>
                        <div class="stat-label">{{ std.branch }}</div>
                        <div class="stat-label">{{ std.email }}</div>
                        <div class="stat-label">{{ std.is_active ? 'Active' : 'Blacklisted' }}</div>
                        
                      </div>
                    </div>
                  </template>

                  <!-- Companies -->
                  <template v-if="activeTab === 'companies'">
                    <tr v-for="comp in filteredData" :key="comp.id">
                      <td>{{ comp.name }}</td><td>{{ comp.industry }}</td>
                      <td><span :class="['badge rounded', comp.is_approved ? 'bg-success' : 'bg-warning']">{{ comp.is_approved ? 'Verified' : 'Pending' }}</span></td>
                      <td><span :class="['badge rounded', comp.is_active ? 'bg-success-soft text-success' : 'bg-danger-soft text-danger']">{{ comp.is_active ? 'Enabled' : 'Deactivated' }}</span></td>
                      <td class="text-end text-nowrap">
                        <button v-if="!comp.is_approved" @click="approveCompany(comp.id)" class="btn btn-sm btn-outline-dark rounded-3 px-3 me-2" style="min-width:90px">Approve</button>
                        <button @click="toggleActive(comp.user_id)" class="btn btn-sm btn-outline-dark rounded-3 px-3 me-2" style="min-width:90px">{{ comp.is_active ? 'Blacklist' : 'Activate' }}</button>
                        <button @click="deleteCompany(comp.id)" class="btn btn-sm btn-outline-danger rounded-3 px-3" style="min-width:80px">Delete</button>
                      </td>
                    </tr>
                  </template>

                  <!-- Jobs -->
                  <template v-if="activeTab === 'jobs'">
                    <tr v-for="job in filteredData" :key="job.id">
                      <td>{{ job.title }}</td><td>{{ job.company_name }}</td><td>{{ job.salary }}</td>
                      <td><span :class="['badge rounded', job.status === 'Approved' ? 'bg-success' : 'bg-warning']">{{ job.status }}</span></td>
                      <td class="text-end">
                        <button v-if="job.status === 'Pending'" @click="approveJob(job.id)" class="btn btn-sm btn-outline-dark rounded-3 px-3 me-2" style="min-width:90px">Verify</button>
                        <button @click="viewJob(job)" class="btn btn-sm btn-outline-dark rounded-3 px-3" style="min-width:90px">View</button>
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
                        <button @click="item.type === 'company' ? approveCompany(item.id) : approveJob(item.id)" class="btn btn-sm btn-outline-dark rounded-3 px-3" style="min-width:120px">Quick Approve</button>
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

      <!-- Job Detail Modal -->
      <div v-if="selectedJob" class="modal-overlay" @click.self="selectedJob = null">
        <div class="modal-card">
          <div class="modal-header-row">
            <div>
              <h5 class="fw-bold mb-0">{{ selectedJob.title }}</h5>
              <span class="text-muted extra-small">{{ selectedJob.company_name }}</span>
            </div>
            <button class="btn-close-modal" @click="selectedJob = null"><i class="bi bi-x-lg"></i></button>
          </div>
          <div class="modal-body-rows">
            <div class="modal-detail-row">
              <span class="detail-label">Salary</span>
              <span class="detail-value">{{ selectedJob.salary || '—' }}</span>
            </div>
            <div class="modal-detail-row">
              <span class="detail-label">Min CGPA</span>
              <span class="detail-value">{{ selectedJob.min_cgpa || 'No requirement' }}</span>
            </div>
            <div class="modal-detail-row">
              <span class="detail-label">Allowed Branches</span>
              <span class="detail-value">
                <span v-if="selectedJob.allowed_branches && selectedJob.allowed_branches.length">
                  <span v-for="b in selectedJob.allowed_branches" :key="b" class="branch-chip">{{ b }}</span>
                </span>
                <span v-else class="text-muted">All branches</span>
              </span>
            </div>
            <div class="modal-detail-row">
              <span class="detail-label">Deadline</span>
              <span class="detail-value">{{ selectedJob.deadline ? new Date(selectedJob.deadline).toLocaleDateString('en-IN', { day:'numeric', month:'long', year:'numeric' }) : '—' }}</span>
            </div>
            <div class="modal-detail-row">
              <span class="detail-label">Status</span>
              <span :class="['badge rounded px-3', selectedJob.status === 'Approved' ? 'bg-success' : 'bg-warning']">{{ selectedJob.status }}</span>
            </div>
            <div v-if="selectedJob.description" class="modal-detail-row flex-column align-items-start">
              <span class="detail-label mb-2">Description</span>
              <p class="mb-0 small text-secondary" style="line-height:1.6">{{ selectedJob.description }}</p>
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
import { Bar, Line, Doughnut } from 'vue-chartjs'
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ArcElement } from 'chart.js'

ChartJS.register(Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale, PointElement, LineElement, ArcElement)

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
const username = ref(sessionStorage.getItem('username'))
const searchQuery = ref('')
const stats = ref({})
const rawData = ref([])

// Reports & Tasks state
const reportTask = ref({ loading: false, taskId: null, status: null })
const reminderTask = ref({ loading: false, taskId: null, status: null })

const pollStatus = async (taskRef) => {
  if (!taskRef.value.taskId) return
  try {
    const res = await axios.get(`http://127.0.0.1:5000/api/jobs/task/${taskRef.value.taskId}`, {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    taskRef.value.status = res.data.status
    if (res.data.status === 'PENDING' || res.data.status === 'STARTED') {
      setTimeout(() => pollStatus(taskRef), 2000)
    }
  } catch (e) { taskRef.value.status = 'ERROR' }
}

const triggerReport = async () => {
  reportTask.value = { loading: true, taskId: null, status: null }
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/jobs/trigger/monthly-report', {}, {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    reportTask.value.taskId = res.data.task_id
    reportTask.value.status = 'PENDING'
    reportTask.value.loading = false
    pollStatus(reportTask)
  } catch (e) { reportTask.value = { loading: false, taskId: null, status: 'FAILURE' } }
}

const triggerReminders = async () => {
  reminderTask.value = { loading: true, taskId: null, status: null }
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/jobs/trigger/reminders', {}, {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    reminderTask.value.taskId = res.data.task_id
    reminderTask.value.status = 'PENDING'
    reminderTask.value.loading = false
    pollStatus(reminderTask)
  } catch (e) { reminderTask.value = { loading: false, taskId: null, status: 'FAILURE' } }
}

const adminMenu = [
  { id: 'dashboard', label: 'Overview', icon: 'bi-grid-fill' },
  { id: 'students', label: 'Students', icon: 'bi-people-fill' },
  { id: 'companies', label: 'Companies', icon: 'bi-building-fill' },
  { id: 'jobs', label: 'Job Postings', icon: 'bi-briefcase-fill' },
  { id: 'applications', label: 'Applications', icon: 'bi-file-earmark-text-fill' },
  { id: 'approvals', label: 'Pending Approvals', icon: 'bi-clock-fill' },
  { id: 'reports', label: 'Reports & Tasks', icon: 'bi-bar-chart-fill' }
]

const refreshData = async () => {
  const token = sessionStorage.getItem('token')
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
  await axios.post(`http://127.0.0.1:5000/api/admin/user/toggle-active/${userId}`, {}, { headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` } })
  refreshData()
}

const approveCompany = async (id) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/company/approve/${id}`, {}, { headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` } })
  refreshData()
}

const approveJob = async (id) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/job/approve/${id}`, {}, { headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` } })
  refreshData()
}

const deleteCompany = async (id) => {
  if (!confirm('Are you sure you want to completely delete this company?')) return
  await axios.delete(`http://127.0.0.1:5000/api/admin/company/${id}`, { headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` } })
  refreshData()
}

const deleteStudent = async (id) => {
  if (!confirm('Are you sure you want to completely delete this student?')) return
  await axios.delete(`http://127.0.0.1:5000/api/admin/student/${id}`, { headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` } })
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
const handleLogout = () => { sessionStorage.clear(); router.push('/login') }

// Job detail modal
const selectedJob = ref(null)
const viewJob = (job) => { selectedJob.value = job }
</script>

<style scoped>
.app-container { display: flex; width: 100vw; min-height: 100vh; background-color: #f8fafc; overflow-x: hidden; }
.main-workspace { flex: 1; margin-left: 0; margin-right: 240px; display: flex; flex-direction: column; width: calc(100vw - 240px); transition: all 0.3s ease; }
.top-navbar { position: fixed; height: 75px; z-index: 1000; display: flex; align-items: center; bottom: 0; left: 0; width: 100%; }
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
@media (max-width: 991px) { .main-workspace { margin-left: 80px; width: calc(100vw - 80px); } }
.report-icon-wrap { width: 40px; height: 40px; border-radius: 10px; background: #eff6ff; color: #3b82f6; display: flex; align-items: center; justify-content: center; font-size: 18px; flex-shrink: 0; }
.reports-root .fluid-card { transition: box-shadow 0.2s; }
.reports-root .fluid-card:hover { box-shadow: 0 4px 16px rgba(0,0,0,0.08); }
/* Job detail modal */
.modal-overlay { position: fixed; inset: 0; background: rgba(15,23,42,0.45); z-index: 1000; display: flex; align-items: center; justify-content: center; padding: 24px; backdrop-filter: blur(2px); }
.modal-card { background: #fff; border-radius: 20px; width: 100%; max-width: 520px; box-shadow: 0 20px 60px rgba(0,0,0,0.18); overflow: hidden; }
.modal-header-row { display: flex; justify-content: space-between; align-items: flex-start; padding: 24px 24px 16px; border-bottom: 1px solid #f1f5f9; }
.btn-close-modal { background: #f1f5f9; border: none; border-radius: 8px; width: 32px; height: 32px; cursor: pointer; display: flex; align-items: center; justify-content: center; color: #475569; transition: background 0.15s; }
.btn-close-modal:hover { background: #e2e8f0; }
.modal-body-rows { padding: 20px 24px 24px; display: flex; flex-direction: column; gap: 14px; }
.modal-detail-row { display: flex; align-items: center; gap: 12px; }
.detail-label { font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.08em; color: #94a3b8; min-width: 130px; }
.detail-value { font-size: 13px; color: #0f172a; font-weight: 500; }
.branch-chip { display: inline-block; background: #f1f5f9; color: #475569; border-radius: 6px; padding: 2px 8px; font-size: 11px; font-weight: 600; margin-right: 4px; margin-bottom: 4px; }
</style>
