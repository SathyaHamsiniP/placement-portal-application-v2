<template>
  <div class="app-container">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="studentMenu"
      :username="username"
      role="Student Portfolio"
      @logout="handleLogout"
    />

    <main class="main-workspace no-scrollbar overflow-auto">
      <header class="top-navbar bg-white border-bottom px-4">
        <div class="navbar-content d-flex justify-content-between align-items-center w-100 h-100">
          <div class="brand-info"><h6 class="portal-title-left mb-0">Campus Placement Portal</h6></div>
          <div class="user-profile-meta d-flex align-items-center">
            <div class="avatar-circle me-3">{{ username?.[0]?.toUpperCase() }}</div>
            <div class="profile-text text-start">
              <div class="fw-bold text-dark small leading-tight">{{ username }}</div>
              <div class="text-muted extra-small">Active Session</div>
            </div>
          </div>
        </div>
      </header>

      <div class="workspace-content p-4">
        <!-- Student Dashboard -->
        <div v-if="activeTab === 'dashboard'" class="dashboard-root">
          <div class="row g-4">
            <div class="col-lg-8">
              <div class="fluid-card mb-4 border-s-orange">
                <h3 class="fw-bold mb-0 text-dark">{{ profile.full_name }}</h3>
                <p class="text-muted small text-uppercase tracking-widest mb-0">OVERVIEW | {{ profile.branch || 'MECHANICAL ENGINEERING' }}</p>
              </div>

              <div class="fluid-card mb-4">
                <div class="row text-center py-2">
                  <div v-for="m in metrics" :key="m.label" class="col-3">
                    <div :class="['metric-circle mx-auto mb-2', m.color, stats.placed > 0 ? 'pulse-success' : '']">
                      <span class="fs-4 fw-bold">{{ m.val }}</span>
                    </div>
                    <div class="stat-label-v2">{{ m.label }}</div>
                  </div>
                </div>
              </div>

              <div class="fluid-card">
                <h6 class="text-uppercase text-muted extra-small fw-bold tracking-widest mb-4">Active Applications</h6>
                <div class="table-responsive">
                  <table class="table align-middle">
                    <thead class="extra-small text-uppercase text-muted border-0">
                      <tr><th>Role & Company</th><th>Applied</th><th>Recruitment Timeline</th><th class="text-end">Documents</th></tr>
                    </thead>
                    <tbody class="small fw-medium">
                      <tr v-for="app in applications" :key="app.id" class="border-light">
                        <td class="py-4">
                          <div class="fw-bold text-dark mb-1">{{ app.job_title }}</div>
                          <div class="text-muted extra-small mb-2">{{ app.company_name }}</div>
                          <div v-if="app.feedback" class="feedback-bubble mt-2 p-2 rounded-2 bg-light border-start border-primary border-3 extra-small">
                            <strong>Feedback:</strong> {{ app.feedback }}
                          </div>
                        </td>
                        <td class="extra-small text-muted">{{ new Date(app.applied_at).toLocaleDateString() }}</td>
                        <td class="timeline-cell">
                          <div v-if="app.status === 'Rejected'" class="rejection-notice py-2 px-3 rounded-pill bg-danger-soft text-danger extra-small fw-bold">
                            <i class="bi bi-x-circle-fill me-2"></i> APPLICATION REJECTED
                          </div>
                          <div v-else class="timeline-path">
                            <div v-for="(step, idx) in timelineSteps" :key="idx" class="timeline-point-wrapper">
                              <div :class="['timeline-dot', isStepActive(app.status, step) ? 'active' : '']"></div>
                              <span class="dot-label">{{ step }}</span>
                            </div>
                            <div class="timeline-line"></div>
                          </div>
                        </td>
                        <td class="text-end">
                          <button v-if="app.status === 'Placed' || app.status === 'Offered'" class="btn btn-sm btn-outline-success rounded-pill px-3 extra-small">
                            <i class="bi bi-download"></i> Letter
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div class="col-lg-4">
              <div class="fluid-card mb-4 min-h-300">
                <h6 class="fw-bold mb-4">Profile Summary</h6>
                <div class="summary-item mb-4"><div class="extra-small text-muted">CGPA</div><div class="fw-bold fs-5">{{ profile.cgpa }} / 10.0</div></div>
                <div class="skills-expertise"><div class="extra-small text-muted mb-3">Key Expertise</div>
                  <div class="d-flex flex-wrap gap-2 text-uppercase"><span v-for="skill in ['Python', 'SQL', 'JavaScript', 'Communication', 'Teamwork']" :key="skill" class="badge bg-light text-dark border extra-small px-3 py-2">{{ skill }}</span></div>
                </div>
              </div>
              <div class="fluid-card mb-4">
                <h6 class="text-uppercase text-muted extra-small fw-bold tracking-widest mb-4">Quick Actions</h6>
                <div class="list-group list-group-flush gap-2">
                  <button @click="activeTab = 'jobs'" class="list-group-item list-group-item-action border-0 rounded-3 small d-flex justify-content-between align-items-center py-3">
                    <span><i class="bi bi-search me-3 text-primary"></i> Explore New Jobs</span>
                    <i class="bi bi-chevron-right opacity-25"></i>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Browse Jobs -->
        <div v-else-if="activeTab === 'jobs'" class="management-root">
          <div class="fluid-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">Browse Opportunities</h5>
              <div v-if="stats.placed > 0" class="badge bg-warning-soft text-warning rounded-pill px-3 border border-warning">
                <i class="bi bi-lock-fill me-2"></i> Placement Locked (Policy Rule #1)
              </div>
            </div>
            
            <div class="row g-4 overflow-auto" style="max-height: 75vh;">
              <div v-for="job in filteredJobs" :key="job.id" class="col-md-6 col-xl-4">
                <div :class="['job-card-v2 p-4 border rounded-4 h-100 position-relative transition-all d-flex flex-column', !job.cgpa_eligible ? 'cgpa-restricted' : '']">
                  
                  <!-- Restriction Overlay -->
                  <div v-if="!job.cgpa_eligible" class="restricted-overlay d-flex flex-column align-items-center justify-content-center text-center">
                    <i class="bi bi-shield-lock-fill fs-2 mb-2"></i>
                    <div class="fw-bold small">CGPA RESTRICTED</div>
                    <div class="extra-small">Required: {{ job.min_cgpa }}</div>
                  </div>

                  <div class="d-flex justify-content-between align-items-start mb-3">
                    <div><h6 class="fw-bold mb-1">{{ job.title }}</h6><p class="text-muted extra-small mb-0">{{ job.company_name }}</p></div>
                    <div class="badge bg-light text-primary border rounded-pill px-3">{{ job.salary }}</div>
                  </div>
                  
                  <p class="text-muted extra-small mb-4 line-clamp-3">{{ job.description }}</p>
                  
                  <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                    <span class="extra-small text-muted"><i class="bi bi-clock me-1"></i> Apply by {{ new Date(job.deadline).toLocaleDateString() }}</span>
                    
                    <button v-if="job.already_applied" class="btn btn-outline-success btn-sm rounded-pill px-4 disabled">Applied</button>
                    <button v-else-if="job.is_placed_locked" class="btn btn-outline-secondary btn-sm rounded-pill px-4 disabled"><i class="bi bi-lock-fill"></i> Locked</button>
                    <button v-else-if="!job.cgpa_eligible" class="btn btn-outline-danger btn-sm rounded-pill px-4 disabled">Ineligible</button>
                    <button v-else @click="applyForJob(job.id)" class="btn btn-primary-orange btn-sm rounded-pill px-4">Apply Now</button>
                  </div>
                </div>
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

const router = useRouter()
const activeTab = ref('dashboard')
const username = ref(localStorage.getItem('username'))
const stats = ref({ applied: 0, shortlisted: 0, placed: 0, in_progress: 0 })
const applications = ref([])
const profile = ref({})
const jobsData = ref([])
const searchQuery = ref('')

const studentMenu = [
  { id: 'dashboard', label: 'My Dashboard', icon: 'bi-grid-fill' },
  { id: 'jobs', label: 'Browse Jobs', icon: 'bi-search' }
]

const timelineSteps = ['APPLIED', 'REVIEW', 'SHORTLISTED', 'INTERVIEW', 'OFFER', 'PLACED']

const metrics = computed(() => [
  { label: 'APPLIED', val: stats.value.applied, color: 'blue' },
  { label: 'SHORTLISTED', val: stats.value.shortlisted, color: 'cyan' },
  { label: 'PLACED', val: stats.value.placed, color: 'green' },
  { label: 'IN PROGRESS', val: stats.value.in_progress, color: 'orange' }
])

const isStepActive = (currentStatus, step) => {
  const statusMap = { 'Applied': 1, 'Review Pending': 2, 'Shortlisted': 3, 'Interviewed': 4, 'Offered': 5, 'Placed': 6 }
  const currentLevel = statusMap[currentStatus] || 1
  const stepLevel = timelineSteps.indexOf(step) + 1
  return currentLevel >= stepLevel
}

const fetchData = async () => {
  const token = localStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/student/dashboard', { headers })
    stats.value = res.data.stats
    applications.value = res.data.applications
    profile.value = res.data.profile
    if (activeTab.value === 'jobs') {
      const resJ = await axios.get('http://127.0.0.1:5000/api/student/jobs', { headers })
      jobsData.value = resJ.data
    }
  } catch (err) { console.error(err) }
}

const applyForJob = async (jobId) => {
  try {
    const res = await axios.post(`http://127.0.0.1:5000/api/student/apply/${jobId}`, {}, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    })
    fetchData()
  } catch (err) { alert(err.response?.data?.message || 'Error applying') }
}

const filteredJobs = computed(() => {
  if (!searchQuery.value) return jobsData.value
  const q = searchQuery.value.toLowerCase()
  return jobsData.value.filter(j => j.title.toLowerCase().includes(q) || j.company_name.toLowerCase().includes(q))
})

watch(activeTab, fetchData)
onMounted(fetchData)
const handleLogout = () => { localStorage.clear(); router.push('/login') }
</script>

<style scoped>
.app-container { display: flex; width: 100vw; min-height: 100vh; background-color: #f8fafc; overflow-x: hidden; }
.main-workspace { flex: 1; margin-left: 240px; display: flex; flex-direction: column; width: calc(100vw - 240px); }
.top-navbar { height: 75px; z-index: 10; display: flex; align-items: center; }
.portal-title-left { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #64748b; letter-spacing: 0.1rem; }

.fluid-card { background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 1.5rem; border: 1px solid #f1f5f9; width: 100%; transition: all 0.2s ease; }
.border-s-orange { border-left: 6px solid #f97316; }

.metric-circle { width: 70px; height: 70px; border-radius: 50%; display: flex; align-items: center; justify-content: center; border-width: 3px; border-style: solid; }
.metric-circle.blue { border-color: #0d6efd; color: #0d6efd; }
.metric-circle.cyan { border-color: #0dcaf0; color: #0dcaf0; }
.metric-circle.green { border-color: #198754; color: #198754; }
.metric-circle.orange { border-color: #f97316; color: #f97316; }

.pulse-success { animation: pulse 2s infinite; }
@keyframes pulse { 0% { box-shadow: 0 0 0 0 rgba(25, 135, 84, 0.4); } 70% { box-shadow: 0 0 0 15px rgba(25, 135, 84, 0); } 100% { box-shadow: 0 0 0 0 rgba(25, 135, 84, 0); } }

.stat-label-v2 { font-size: 9px; font-weight: 800; color: #94a3b8; letter-spacing: 0.05em; margin-top: 0.4rem; }

.timeline-path { position: relative; display: flex; justify-content: space-between; align-items: center; width: 300px; padding: 10px 0; }
.timeline-line { position: absolute; top: 50%; left: 0; right: 0; height: 2px; background: #e2e8f0; z-index: 1; transform: translateY(-50%); }
.timeline-point-wrapper { position: relative; z-index: 2; display: flex; flex-direction: column; align-items: center; }
.timeline-dot { width: 12px; height: 12px; border-radius: 50%; background: #e2e8f0; border: 2px solid #fff; transition: all 0.3s ease; }
.timeline-dot.active { background: #f97316; box-shadow: 0 0 0 4px rgba(249, 115, 22, 0.2); }
.dot-label { font-size: 8px; font-weight: 700; color: #94a3b8; margin-top: 6px; }

.bg-danger-soft { background: #fee2e2; }
.bg-warning-soft { background: #fffbeb; }
.btn-primary-orange { background: #f97316; color: white; border: none; }
.btn-primary-orange:hover { background: #ea580c; color: white; }

/* Ineligibility Glassmorphism */
.cgpa-restricted { position: relative; }
.restricted-overlay { 
  position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
  background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(8px); 
  z-index: 10; border-radius: inherit; color: #ef4444; 
}

@media (max-width: 1200px) { .main-workspace { margin-left: 0; width: 100vw; } }
</style>
