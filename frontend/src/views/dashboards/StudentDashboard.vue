<template>
  <div class="app-container">
    <Sidebar 
      v-model:activeTab="activeTab" 
      :menuItems="studentMenu"
      :username="profile?.full_name || username"
      role="Student Portfolio"
      @logout="handleLogout"
    />

    <main class="main-workspace no-scrollbar overflow-auto">
      <header class="top-navbar bg-white border-bottom px-4">
        <div class="navbar-content d-flex justify-content-between align-items-center w-100 h-100">
          <div class="brand-info"><h6 class="portal-title-left mb-0">Campus Placement Portal</h6></div>
          <div class="user-profile-meta d-flex align-items-center">
            <div class="avatar-circle me-3">{{ (profile?.full_name || username)?.[0]?.toUpperCase() }}</div>
            <div class="profile-text text-start">
              <div class="fw-bold text-dark small leading-tight">{{ profile?.full_name || username }}</div>
              <div class="text-muted extra-small">Active Session</div>
            </div>
          </div>
        </div>
      </header>

      <div class="workspace-content p-4">
        <!-- Student Dashboard -->
        <div v-if="activeTab === 'dashboard'" class="dashboard-root">
          <div class="row g-4">
            <div class="col-lg-8 d-flex flex-column gap-4">
              <div class="fluid-card border-s-orange mb-0">
                <h3 class="fw-bold mb-0 text-dark">{{ profile.full_name }}</h3>
                <p class="text-muted small text-uppercase tracking-widest mb-0">OVERVIEW | {{ profile.branch || 'MECHANICAL ENGINEERING' }}</p>
              </div>

              <div class="fluid-card mb-0">
                <div class="row text-center py-2">
                  <div v-for="m in metrics" :key="m.label" class="col-3">
                    <div :class="['metric-circle mx-auto mb-2', m.color, stats.placed > 0 ? 'pulse-success' : '']">
                      <span class="fs-4 fw-bold">{{ m.val }}</span>
                    </div>
                    <div class="stat-label-v2">{{ m.label }}</div>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-lg-4">
              <div class="fluid-card h-100">
                <h6 class="fw-bold mb-4">Profile Summary</h6>
                <div class="summary-item mb-4"><div class="extra-small text-muted">CGPA</div><div class="fw-bold fs-5">{{ profile.cgpa }} / 10.0</div></div>
                <div class="skills-expertise"><div class="extra-small text-muted mb-3">Key Expertise</div>
                  <div class="d-flex flex-wrap gap-2 text-uppercase">
                    <span v-for="skill in (profile.skills && profile.skills.length ? profile.skills : ['Python', 'SQL', 'JavaScript', 'Communication', 'Teamwork'])" :key="skill" class="badge bg-light text-dark border extra-small px-3 py-2">{{ skill }}</span>
                  </div>
                </div>
              </div>
            </div>

            <div class="col-12 mt-4">
              <div class="fluid-card min-h-300">
                <div class="d-flex justify-content-between align-items-center mb-4">
                  <h6 class="text-uppercase text-muted extra-small fw-bold tracking-widest mb-0">Upcoming Schedule & Deadlines</h6>
                  <button @click="activeTab = 'jobs'" class="btn btn-sm btn-link text-decoration-none extra-small fw-bold p-0 text-orange">View Job Board <i class="bi bi-arrow-right"></i></button>
                </div>
                
                <div v-if="upcomingAgenda.length > 0" class="agenda-list">
                  <div v-for="event in upcomingAgenda" :key="event.id" class="d-flex align-items-center mb-3 p-3 border border-light-subtle rounded-4 gap-3 bg-light-hover transition-all">
                    <div class="flex-fill">
                      <div class="fw-bold text-dark">{{ event.title }}</div>
                      <div class="extra-small text-muted mt-1 fw-bold">{{ event.date.toLocaleString(undefined, { weekday: 'short', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' }) }}</div>
                    </div>
                    <div>
                      <button v-if="event.type === 'deadline'" @click="applyForJob(event.jobId)" class="btn btn-sm btn-dark extra-small px-3 rounded-3">Quick Apply</button>
                      <span v-else class="badge bg-white text-dark border extra-small px-3 py-2"><i class="bi bi-check-circle-fill text-success me-1"></i> Scheduled</span>
                    </div>
                  </div>
                </div>
                <div v-else class="text-center py-5">
                  <i class="bi bi-calendar2-check text-light opacity-50 mb-3 d-block" style="font-size: 3rem;"></i>
                  <span class="text-muted extra-small fw-bold tracking-widest text-uppercase">Your Agenda is Clear</span>
                  <p class="text-muted small mt-2">No impending interviews or closing deadlines.</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Browse Jobs -->
        <div v-else-if="activeTab === 'jobs'" class="management-root">
          <div class="fluid-card animate-fade-in">
            <div class="d-flex justify-content-between align-items-center mb-4">
              <h5 class="fw-bold mb-0">Browse Opportunities</h5>
              <div v-if="stats.placed > 0" class="badge bg-warning-soft text-warning rounded px-3 border border-warning">
                <i class="bi bi-lock-fill me-2"></i> Placement Locked (Policy Rule #1)
              </div>
            </div>
            
            <!-- Search bar -->
            <div class="search-box position-relative mb-4" style="max-width: 480px;">
              <i class="bi bi-search position-absolute start-0 top-50 translate-middle-y ms-3 text-muted"></i>
              <input type="text" v-model="searchQuery" class="form-control ps-5 rounded-3 border-light-subtle extra-small py-3" placeholder="Search by position, company, or required skills...">
            </div>
            
            <div class="row g-4">
              <div v-for="job in filteredJobs" :key="job.id" class="col-md-6 col-xl-4">
                <div class="job-card-v2 p-4 border rounded-4 h-100 position-relative transition-all d-flex flex-column border-s-orange-thin" :class="!job.cgpa_eligible ? 'cgpa-restricted' : ''">
                  
                  <!-- Restriction Overlay -->
                  <div v-if="!job.cgpa_eligible" class="restricted-overlay d-flex flex-column align-items-center justify-content-center text-center">
                    <i class="bi bi-shield-lock-fill fs-2 mb-2"></i>
                    <div class="fw-bold small">CGPA RESTRICTED</div>
                    <div class="extra-small">Required: {{ job.min_cgpa }}</div>
                  </div>

                  <div class="d-flex justify-content-between align-items-start mb-3">
                    <div><h6 class="fw-bold mb-1">{{ job.title }}</h6><p class="text-muted extra-small mb-0">{{ job.company_name }}</p></div>
                    <div class="badge bg-light text-primary border rounded px-3">{{ job.salary }}</div>
                  </div>
                  
                  <p class="text-muted extra-small mb-4 line-clamp-3">{{ job.description }}</p>
                  
                  <div class="mt-auto pt-3 border-top d-flex justify-content-between align-items-center">
                    <span class="extra-small text-muted"><i class="bi bi-clock me-1"></i> Apply by {{ new Date(job.deadline).toLocaleDateString() }}</span>
                    
                    <button v-if="job.already_applied" class="btn btn-outline-success btn-sm rounded-3 px-4 disabled">Applied</button>
                    <button v-else-if="job.is_placed_locked" class="btn btn-outline-secondary btn-sm rounded-3 px-4 disabled"><i class="bi bi-lock-fill"></i> Locked</button>
                    <button v-else-if="!job.cgpa_eligible" class="btn btn-outline-danger btn-sm rounded-3 px-4 disabled">Ineligible</button>
                    <button v-else @click="applyForJob(job.id)" class="btn btn-outline-dark btn-sm rounded-3 px-4">Apply Now</button>
                  </div>
                </div>
              </div>
              <div v-if="filteredJobs.length === 0" class="col-12 text-center py-5">
                <i class="bi bi-search fs-2 text-light"></i>
                <p class="text-muted small mt-2">No matching job postings found.</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Edit Profile Tab -->
        <div v-else-if="activeTab === 'profile'" class="management-root">
          <div class="fluid-card mx-auto" style="max-width: 800px;">
            <h4 class="fw-bold mb-2">My Academic & Professional Profile</h4>
            <p class="text-muted extra-small mb-4">Provide details to keep employers up to date regarding your background.</p>
            
            <form @submit.prevent="handleUpdateProfile">
              <div class="row g-3">
                <div class="col-md-6">
                  <label class="form-label fw-bold extra-small text-uppercase">Full Name</label>
                  <input v-model="profileForm.full_name" type="text" class="form-control rounded-3 border-light p-3 extra-small" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold extra-small text-uppercase">Branch/Department</label>
                  <select v-model="profileForm.branch" class="form-control rounded-3 border-light p-3 extra-small" required>
                    <option value="" disabled>Select Branch</option>
                    <option value="Computer Science">Computer Science</option>
                    <option value="Electrical Engineering">Electrical Engineering</option>
                    <option value="Mechanical Engineering">Mechanical Engineering</option>
                    <option value="Civil Engineering">Civil Engineering</option>
                    <option value="Chemical Engineering">Chemical Engineering</option>
                  </select>
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold extra-small text-uppercase">CGPA (out of 10.0)</label>
                  <input v-model.number="profileForm.cgpa" type="number" step="0.01" min="0" max="10" class="form-control rounded-3 border-light p-3 extra-small" required />
                </div>
                <div class="col-md-6">
                  <label class="form-label fw-bold extra-small text-uppercase">Graduation Year</label>
                  <input v-model.number="profileForm.grad_year" type="number" class="form-control rounded-3 border-light p-3 extra-small" required />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold extra-small text-uppercase">Key Skills (comma-separated)</label>
                  <input v-model="skillsInput" type="text" class="form-control rounded-3 border-light p-3 extra-small" placeholder="e.g. Python, SQL, Javascript" />
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold extra-small text-uppercase">Education Summary</label>
                  <textarea v-model="profileForm.education_details" class="form-control rounded-3 border-light p-3 extra-small" rows="3" placeholder="List high school, diploma, certifications..."></textarea>
                </div>
                <div class="col-12">
                  <label class="form-label fw-bold extra-small text-uppercase">Experience Details</label>
                  <textarea v-model="profileForm.experience" class="form-control rounded-3 border-light p-3 extra-small" rows="3" placeholder="List internships, club activities, projects..."></textarea>
                </div>
                
                <div class="col-12">
                  <label class="form-label fw-bold extra-small text-uppercase">Resume PDF/Doc</label>
                  <div class="input-group">
                    <input type="file" @change="onFileChange" class="form-control border-light-subtle rounded-start-3 extra-small" accept=".pdf,.doc,.docx" />
                    <button type="button" @click="handleUploadResume" class="btn btn-outline-dark px-4 extra-small rounded-end-3" :disabled="!selectedFile">
                      Upload
                    </button>
                  </div>
                  <div v-if="profile.resume_url" class="mt-2 extra-small text-success">
                    <i class="bi bi-file-earmark-check-fill me-1"></i> Current Resume: 
                    <a :href="'http://127.0.0.1:5000' + profile.resume_url" target="_blank" class="fw-bold text-decoration-none ms-1">View File</a>
                  </div>
                </div>
                
                <div class="col-12 text-center mt-4">
                  <button type="submit" class="btn btn-outline-dark rounded-3 px-5 py-3 fw-bold extra-small text-uppercase">Save Profile</button>
                </div>
              </div>
            </form>
          </div>
        </div>
        <!-- Placement History Tab -->
        <div v-else-if="activeTab === 'history'" class="management-root">
          <div class="fluid-card">
            <div class="d-flex justify-content-between align-items-center mb-1">
              <div>
                <h5 class="fw-bold mb-1">My Application History</h5>
                <p class="text-muted extra-small mb-0">Complete record of all your job applications and their outcomes.</p>
              </div>
              <div class="d-flex align-items-center gap-2">
                <span v-if="exportStatus" class="extra-small text-muted">{{ exportStatus }}</span>
                <button @click="exportCSV" :disabled="exportLoading" class="btn btn-sm btn-outline-dark rounded-3 px-3 extra-small" style="min-width:130px">
                  <i class="bi bi-file-earmark-arrow-down me-1"></i>
                  {{ exportLoading ? 'Exporting...' : 'Export CSV' }}
                </button>
              </div>
            </div>
            <div class="table-responsive mt-3">
              <table class="table align-middle">
                <thead class="extra-small text-uppercase text-muted">
                  <tr>
                    <th>Role & Company</th>
                    <th>Salary</th>
                    <th>Applied On</th>
                    <th>Status</th>
                    <th>Feedback</th>
                    <th class="text-end">Document</th>
                  </tr>
                </thead>
                <tbody class="small">
                  <tr v-for="app in applications" :key="app.id">
                    <td class="py-3">
                      <div class="fw-bold text-dark">{{ app.job_title }}</div>
                      <div class="text-muted extra-small">{{ app.company_name }}</div>
                    </td>
                    <td class="extra-small text-muted">—</td>
                    <td class="extra-small text-muted">{{ new Date(app.applied_at).toLocaleDateString() }}</td>
                    <td>
                      <span :class="['badge rounded extra-small px-3 py-2', statusBadgeClass(app.status)]">{{ app.status }}</span>
                    </td>
                    <td class="extra-small text-muted" style="max-width:200px">{{ app.feedback || '—' }}</td>
                    <td class="text-end">
                      <button v-if="app.status === 'Placed' || app.status === 'Offered'" @click="downloadOfferLetter(app)" class="btn btn-sm btn-outline-dark rounded-3 px-3 extra-small">
                        <i class="bi bi-download me-1"></i> Letter
                      </button>
                      <span v-else class="text-muted extra-small">—</span>
                    </td>
                  </tr>
                  <tr v-if="applications.length === 0">
                    <td colspan="6" class="text-center py-5 text-muted extra-small">No application history yet.</td>
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
const stats = ref({ applied: 0, shortlisted: 0, placed: 0, in_progress: 0 })
const applications = ref([])
const profile = ref({})
const jobsData = ref([])
const searchQuery = ref('')

// Form profile states
const profileForm = ref({
  full_name: '',
  branch: '',
  cgpa: 0.0,
  grad_year: 2026,
  education_details: '',
  experience: '',
  resume_url: ''
})
const skillsInput = ref('')
const selectedFile = ref(null)

const studentMenu = [
  { id: 'dashboard', label: 'My Dashboard', icon: 'bi-grid-fill' },
  { id: 'jobs', label: 'Browse Jobs', icon: 'bi-search' },
  { id: 'history', label: 'Application History', icon: 'bi-clock-history' },
  { id: 'profile', label: 'My Profile', icon: 'bi-person-lines-fill' }
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

const statusBadgeClass = (status) => {
  const m = {
    'Applied': 'bg-light text-dark border',
    'Review Pending': 'bg-warning-soft text-warning border border-warning',
    'Shortlisted': 'bg-info-soft text-info border border-info',
    'Interviewed': 'bg-primary text-white',
    'Offered': 'bg-success text-white',
    'Placed': 'bg-success text-white',
    'Rejected': 'bg-danger-soft text-danger border border-danger',
  }
  return m[status] || 'bg-light text-dark border'
}

const upcomingAgenda = computed(() => {
  const events = []
  const now = new Date()

  // 1. Upcoming Interviews
  applications.value.forEach(app => {
    if (app.interview_date) {
      const d = new Date(app.interview_date)
      if (d >= now) {
        events.push({
          id: 'int_' + app.id,
          type: 'interview',
          title: `Interview: ${app.job_title} @ ${app.company_name}`,
          date: d,
          colorClass: 'bg-primary-soft text-primary border-primary',
          icon: 'bi bi-person-video3'
        })
      }
    }
  })

  // 2. Upcoming Deadlines for eligible, unapplied jobs (only if NOT placed)
  if (!(stats.value.placed > 0)) {
    jobsData.value.forEach(job => {
      if (job.deadline && !job.already_applied && job.cgpa_eligible) {
        const d = new Date(job.deadline)
        if (d >= now) {
          events.push({
            id: 'job_' + job.id,
            jobId: job.id,
            type: 'deadline',
            title: `Deadline: ${job.title} @ ${job.company_name}`,
            date: d,
            colorClass: 'bg-warning-soft text-warning border-warning',
            icon: 'bi bi-hourglass-split'
          })
        }
      }
    })
  }

  // Sort chronologically and take next 5 items
  return events.sort((a, b) => a.date - b.date).slice(0, 5)
})

const fetchData = async () => {
  const token = sessionStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }
  try {
    const res = await axios.get('http://127.0.0.1:5000/api/student/dashboard', { headers })
    stats.value = res.data.stats
    applications.value = res.data.applications
    profile.value = res.data.profile
    
    // Always fetch jobs universally for the agenda feed
    const resJ = await axios.get('http://127.0.0.1:5000/api/student/jobs', { headers })
    jobsData.value = resJ.data
  } catch (err) { console.error(err) }
}

// Watch profile to populate form fields
watch(profile, (newProfile) => {
  if (newProfile) {
    profileForm.value = {
      full_name: newProfile.full_name || '',
      branch: newProfile.branch || '',
      cgpa: newProfile.cgpa || 0,
      grad_year: newProfile.grad_year || 2026,
      education_details: newProfile.education_details || '',
      experience: newProfile.experience || '',
      resume_url: newProfile.resume_url || ''
    }
    skillsInput.value = (newProfile.skills || []).join(', ')
  }
}, { immediate: true })

const applyForJob = async (jobId) => {
  try {
    const res = await axios.post(`http://127.0.0.1:5000/api/student/apply/${jobId}`, {}, {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    fetchData()
  } catch (err) { alert(err.response?.data?.message || 'Error applying') }
}

const handleUpdateProfile = async () => {
  const token = sessionStorage.getItem('token')
  const headers = { Authorization: `Bearer ${token}` }
  const skillsList = skillsInput.value.split(',').map(s => s.trim()).filter(Boolean)
  try {
    await axios.post('http://127.0.0.1:5000/api/student/profile', {
      ...profileForm.value,
      skills: skillsList
    }, { headers })
    alert('Profile updated successfully!')
    fetchData()
    activeTab.value = 'dashboard'
  } catch (err) {
    alert('Error saving profile changes')
  }
}

const onFileChange = (e) => {
  selectedFile.value = e.target.files[0]
}

const handleUploadResume = async () => {
  if (!selectedFile.value) return
  const token = sessionStorage.getItem('token')
  const formData = new FormData()
  formData.append('resume', selectedFile.value)
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/student/upload-resume', formData, {
      headers: {
        Authorization: `Bearer ${token}`,
        'Content-Type': 'multipart/form-data'
      }
    })
    alert('Resume uploaded successfully')
    profile.value.resume_url = res.data.resume_url
    selectedFile.value = null
    fetchData()
  } catch (err) {
    alert(err.response?.data?.message || 'Error uploading file')
  }
}

const downloadOfferLetter = async (app) => {
  const token = sessionStorage.getItem('token')
  try {
    const res = await axios.get(`http://127.0.0.1:5000/api/student/offer-letter/${app.id}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (res.data.success) {
      const newWin = window.open('', '_blank')
      newWin.document.write(res.data.html)
      newWin.document.close()
      setTimeout(() => {
        newWin.print()
      }, 500)
    }
  } catch (err) {
    alert(err.response?.data?.message || 'Error downloading offer letter')
  }
}

const exportLoading = ref(false)
const exportStatus = ref('')

const exportCSV = async () => {
  exportLoading.value = true
  exportStatus.value = 'Starting export...'
  try {
    const res = await axios.post('http://127.0.0.1:5000/api/jobs/export/student', {}, {
      headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
    })
    const taskId = res.data.task_id
    exportStatus.value = 'Processing...'
    pollTask(taskId)
  } catch (err) {
    exportStatus.value = 'Export failed.'
    exportLoading.value = false
  }
}

const pollTask = (taskId) => {
  const interval = setInterval(async () => {
    try {
      const res = await axios.get(`http://127.0.0.1:5000/api/jobs/task/${taskId}`, {
        headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` }
      })
      if (res.data.status === 'SUCCESS') {
        clearInterval(interval)
        exportLoading.value = false
        const file = res.data.result?.file
        exportStatus.value = file ? `Ready: ${file}` : 'Export complete!'
        // Trigger download
        if (file) {
          const dl = await axios.get(`http://127.0.0.1:5000/api/jobs/exports/${file}`, {
            headers: { Authorization: `Bearer ${sessionStorage.getItem('token')}` },
            responseType: 'blob'
          })
          const url = window.URL.createObjectURL(new Blob([dl.data]))
          const a = document.createElement('a'); a.href = url; a.download = file; a.click()
        }
      } else if (res.data.status === 'FAILURE') {
        clearInterval(interval)
        exportLoading.value = false
        exportStatus.value = 'Export failed.'
      }
    } catch { clearInterval(interval); exportLoading.value = false }
  }, 2000)
}

const filteredJobs = computed(() => {
  if (!searchQuery.value) return jobsData.value
  const q = searchQuery.value.toLowerCase()
  return jobsData.value.filter(j =>
    j.title.toLowerCase().includes(q) ||
    j.company_name.toLowerCase().includes(q) ||
    (j.description || '').toLowerCase().includes(q) ||
    (Array.isArray(j.allowed_branches) ? j.allowed_branches.join(' ').toLowerCase().includes(q) : false)
  )
})

watch(activeTab, fetchData)
onMounted(fetchData)
const handleLogout = () => { sessionStorage.clear(); router.push('/login') }
</script>

<style scoped>
.app-container { display: flex; width: 100vw; min-height: 100vh; background-color: #f8fafc; overflow-x: hidden; }
.main-workspace { flex: 1; margin-left: 240px; display: flex; flex-direction: column; width: calc(100vw - 240px); transition: all 0.3s ease; }
.top-navbar { height: 75px; z-index: 10; display: flex; align-items: center; }
.portal-title-left { font-size: 0.8rem; font-weight: 800; text-transform: uppercase; color: #64748b; letter-spacing: 0.1rem; }

.fluid-card { background: white; border-radius: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); padding: 1.5rem; border: 1px solid #f1f5f9; width: 100%; transition: all 0.2s ease; }
.border-s-orange {
  border-left: 6px solid #f97316 !important;
}
.avatar-circle { width: 42px; height: 42px; background-color: #0f172a; color: white; display: flex; align-items: center; justify-content: center; border-radius: 50%; font-weight: 800; }

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

/* Job card orange left accent */
.border-s-orange-thin {
  border-left: 3px solid #f97316 !important;
}

/* Ineligibility Glassmorphism */
.cgpa-restricted { position: relative; }
.restricted-overlay { 
  position: absolute; top: 0; left: 0; right: 0; bottom: 0; 
  background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(8px); 
  z-index: 10; border-radius: inherit; color: #ef4444; 
}

@media (max-width: 991px) { .main-workspace { margin-left: 80px; width: calc(100vw - 80px); } }
</style>
