<template>
  <div class="dashboard-wrapper d-flex">
    <!-- Sidebar -->
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="adminMenu"
      :username="username"
      role="Administrator"
      @logout="handleLogout"
    />

    <!-- Main Content -->
    <div class="main-content flex-grow-1 p-4">
      <header class="d-flex justify-content-between align-items-center mb-4">
        <h2 class="fw-bold text-dark">{{ activeMenuLabel }}</h2>
        <div class="date text-muted">{{ currentDate }}</div>
      </header>

      <!-- Stats Overview (Only in Dashboard tab) -->
      <section v-if="activeTab === 'dashboard'" class="mb-5">
        <div class="row g-4">
          <div class="col-md-3" v-for="(stat, index) in statsCards" :key="index">
            <div class="card border-0 shadow-sm overflow-hidden h-100">
              <div class="card-body p-4 d-flex align-items-center">
                <div :class="`icon-box bg-${stat.color}-soft text-${stat.color} me-3`">
                  <i :class="`bi ${stat.icon} fs-3`"></i>
                </div>
                <div>
                  <h6 class="text-muted mb-1">{{ stat.label }}</h6>
                  <h3 class="mb-0 fw-bold">{{ stats[stat.key] || 0 }}</h3>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Dynamic Tab Content -->
      <div class="content-section">
        <!-- Companies Management -->
        <div v-if="activeTab === 'companies'" class="card border-0 shadow-sm p-4">
          <div class="d-flex justify-content-between mb-4 flex-wrap gap-3">
            <h4 class="fw-bold mb-0">Registered Companies</h4>
            <input v-model="companySearch" type="text" class="form-control w-auto" placeholder="Search companies...">
          </div>
          <div class="table-responsive">
            <table class="table table-hover align-middle">
              <thead class="table-light">
                <tr>
                  <th>Company Name</th>
                  <th>Industry</th>
                  <th>Status</th>
                  <th>Email</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="company in filteredCompanies" :key="company.id">
                  <td class="fw-bold text-primary">{{ company.name }}</td>
                  <td>{{ company.industry }}</td>
                  <td>
                    <span :class="`badge rounded-pill ${company.is_approved ? 'bg-success' : 'bg-warning'}`">
                      {{ company.is_approved ? 'Approved' : 'Pending' }}
                    </span>
                  </td>
                  <td class="text-muted small">{{ company.email }}</td>
                  <td>
                    <div class="d-flex gap-2">
                      <button v-if="!company.is_approved" @click="approveCompany(company.id)" class="btn btn-success btn-sm px-3">Approve</button>
                      <button @click="toggleUserStatus(company.user_id)" :class="`btn btn-sm px-3 ${company.is_active ? 'btn-outline-danger' : 'btn-outline-success'}`">
                        {{ company.is_active ? 'Deactivate' : 'Activate' }}
                      </button>
                      <button @click="deleteCompany(company.id)" class="btn btn-link text-danger btn-sm"><i class="bi bi-trash"></i></button>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Jobs Management -->
        <div v-if="activeTab === 'jobs'" class="card border-0 shadow-sm p-4">
          <div class="d-flex justify-content-between mb-4">
            <h4 class="fw-bold">Job Postings Control</h4>
            <input v-model="jobSearch" type="text" class="form-control w-auto" placeholder="Filter jobs...">
          </div>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>Job Title</th>
                  <th>Posted By</th>
                  <th>Status</th>
                  <th>Deadline</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="job in filteredJobs" :key="job.id">
                  <td class="fw-bold">{{ job.title }}</td>
                  <td>{{ job.company_name }}</td>
                  <td>
                    <span :class="`badge rounded-pill ${getStatusBadge(job.status)}`">{{ job.status }}</span>
                  </td>
                  <td>{{ new Date(job.deadline).toLocaleDateString() }}</td>
                  <td>
                    <button v-if="job.status === 'Pending'" @click="approveJob(job.id)" class="btn btn-success btn-sm px-4">Accept</button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Students Management -->
        <div v-if="activeTab === 'students'" class="card border-0 shadow-sm p-4">
          <div class="d-flex justify-content-between mb-4">
            <h4 class="fw-bold">Student Database</h4>
            <input v-model="studentSearch" type="text" class="form-control w-auto" placeholder="Search students...">
          </div>
          <div class="table-responsive">
            <table class="table table-hover">
              <thead class="table-light">
                <tr>
                  <th>FullName</th>
                  <th>Roll.No</th>
                  <th>Branch</th>
                  <th>Account</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="student in filteredStudents" :key="student.id">
                  <td class="fw-bold">{{ student.full_name }}</td>
                  <td>{{ student.roll_number }}</td>
                  <td>{{ student.branch }}</td>
                  <td>
                    <span :class="`badge ${student.is_active ? 'bg-success' : 'bg-danger'}`">
                      {{ student.is_active ? 'Active' : 'Blacklisted' }}
                    </span>
                  </td>
                  <td>
                    <button @click="toggleUserStatus(student.user_id)" class="btn btn-outline-secondary btn-sm">
                      {{ student.is_active ? 'Deactivate' : 'Activate' }}
                    </button>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'
import Sidebar from '../../components/Sidebar.vue'

const router = useRouter()
const activeTab = ref('dashboard')
const username = ref(localStorage.getItem('username'))
const stats = ref({})
const companies = ref([])
const jobs = ref([])
const students = ref([])

// Search
const companySearch = ref('')
const jobSearch = ref('')
const studentSearch = ref('')

const adminMenu = [
  { id: 'dashboard', label: 'Overview', icon: 'bi-grid-1x2' },
  { id: 'companies', label: 'Companies', icon: 'bi-building' },
  { id: 'jobs', label: 'Job Postings', icon: 'bi-briefcase' },
  { id: 'students', label: 'Student Management', icon: 'bi-people' }
]

const statsCards = [
  { label: 'Total Students', key: 'total_students', icon: 'bi-people-fill', color: 'primary' },
  { label: 'Partner Companies', key: 'total_companies', icon: 'bi-building-fill', color: 'success' },
  { label: 'Job Openings', key: 'total_jobs', icon: 'bi-post-card', color: 'info' },
  { label: 'Applications', key: 'total_applications', icon: 'bi-file-person', color: 'warning' },
]

const activeMenuLabel = computed(() => {
  return adminMenu.find(item => item.id === activeTab.value)?.label || 'Dashboard'
})

const currentDate = computed(() => {
  return new Date().toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })
})

// API logic
const getHeaders = () => ({
  headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
})

const fetchData = async () => {
  try {
    if (activeTab.value === 'dashboard') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/stats', getHeaders())
      stats.value = res.data
    } else if (activeTab.value === 'companies') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/companies', getHeaders())
      companies.value = res.data
    } else if (activeTab.value === 'jobs') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/jobs', getHeaders())
      jobs.value = res.data
    } else if (activeTab.value === 'students') {
      const res = await axios.get('http://127.0.0.1:5000/api/admin/students', getHeaders())
      students.value = res.data
    }
  } catch (err) {
    if (err.response?.status === 401) handleLogout()
  }
}

watch(activeTab, fetchData)

// Filters
const filteredCompanies = computed(() => companies.value.filter(c => c.name.toLowerCase().includes(companySearch.value.toLowerCase())))
const filteredJobs = computed(() => jobs.value.filter(j => j.title.toLowerCase().includes(jobSearch.value.toLowerCase())))
const filteredStudents = computed(() => students.value.filter(s => s.full_name.toLowerCase().includes(studentSearch.value.toLowerCase())))

// Actions
const approveCompany = async (id) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/company/approve/${id}`, {}, getHeaders())
  fetchData()
}
const approveJob = async (id) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/job/approve/${id}`, {}, getHeaders())
  fetchData()
}
const toggleUserStatus = async (uid) => {
  await axios.post(`http://127.0.0.1:5000/api/admin/user/toggle-active/${uid}`, {}, getHeaders())
  fetchData()
}
const deleteCompany = async (id) => {
  if (confirm('Permanently remove this company and all its data?')) {
    await axios.delete(`http://127.0.0.1:5000/api/admin/company/${id}`, getHeaders())
    fetchData()
  }
}

const getStatusBadge = (s) => s === 'Approved' ? 'bg-success' : 'bg-warning'

const handleLogout = () => {
  localStorage.clear()
  router.push('/login')
}

onMounted(fetchData)
</script>

<style scoped>
.dashboard-wrapper {
  background-color: #f8f9fa;
  min-height: 100vh;
}

.main-content {
  margin-left: 260px; /* Width of sidebar */
  transition: all 0.3s ease;
}

.icon-box {
  width: 54px;
  height: 54px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 14px;
}

.bg-primary-soft { background-color: rgba(13, 110, 253, 0.1); }
.bg-success-soft { background-color: rgba(25, 135, 84, 0.1); }
.bg-info-soft { background-color: rgba(13, 202, 240, 0.1); }
.bg-warning-soft { background-color: rgba(255, 193, 7, 0.1); }

@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }
}
</style>
