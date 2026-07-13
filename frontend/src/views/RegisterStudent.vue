<template>
  <div class="login-page">
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-logo"><i class="bi bi-person-fill text-white opacity-75"></i></div>
        <h1 class="brand-title">Student Registration</h1>
        <p class="brand-tagline">Start your placement journey.</p>
      </div>
    </div>
    <div class="form-panel">
      <div class="form-inner">
        <p class="form-eyebrow">STUDENT PORTAL</p>
        <h2 class="form-heading">Create student account</h2>
        
        <form @submit.prevent="handleRegister" class="login-form">
          <div class="field-group">
            <label class="field-label">FULL NAME</label>
            <input v-model="form.full_name" type="text" class="field-input" placeholder="e.g. John Doe" required />
          </div>
          <div class="row">
            <div class="col-md-6">
              <div class="field-group">
                <label class="field-label">ROLL NUMBER</label>
                <input v-model="form.roll_number" type="text" class="field-input" placeholder="e.g. 21F300123" required />
              </div>
            </div>
            <div class="col-md-6">
              <div class="field-group">
                <label class="field-label">BRANCH</label>
                <select v-model="form.branch" class="field-input" required>
                  <option value="" disabled selected>Select Branch</option>
                  <option value="Computer Science">Computer Science</option>
                  <option value="Electrical Engineering">Electrical Engineering</option>
                  <option value="Mechanical Engineering">Mechanical Engineering</option>
                  <option value="Civil Engineering">Civil Engineering</option>
                  <option value="Chemical Engineering">Chemical Engineering</option>
                </select>
              </div>
            </div>
          </div>
          <div class="row">
            <div class="col-md-6">
              <div class="field-group">
                <label class="field-label">CGPA</label>
                <input v-model="form.cgpa" type="number" step="0.01" min="0" max="10" class="field-input" placeholder="e.g. 8.5" required />
              </div>
            </div>
            <div class="col-md-6">
              <div class="field-group">
                <label class="field-label">GRADUATION YEAR</label>
                <input v-model="form.grad_year" type="number" class="field-input" placeholder="e.g. 2026" required />
              </div>
            </div>
          </div>
          <div class="field-group">
            <label class="field-label">SKILLS (COMMA SEPARATED)</label>
            <input v-model="form.skills" type="text" class="field-input" placeholder="e.g. Python, SQL, HTML" required />
          </div>
          <div class="field-group">
            <label class="field-label">EDUCATION DETAILS</label>
            <textarea v-model="form.education_details" class="field-input" placeholder="High school, prior college degrees details..." rows="2" style="resize: none;" required></textarea>
          </div>
          <div class="field-group">
            <label class="field-label">EXPERIENCE</label>
            <textarea v-model="form.experience" class="field-input" placeholder="Internships, projects, or works..." rows="2" style="resize: none;" required></textarea>
          </div>
          <hr style="border-top: 1px solid var(--slate-200); margin: 1.5rem 0;" />
          <div class="field-group">
            <label class="field-label">USERNAME</label>
            <input v-model="form.username" type="text" class="field-input" required />
          </div>
          <div class="field-group">
            <label class="field-label">EMAIL</label>
            <input v-model="form.email" type="email" class="field-input" required />
          </div>
          <div class="field-group">
            <label class="field-label">PASSWORD</label>
            <input v-model="form.password" type="password" class="field-input" required />
          </div>

          <div v-if="error" class="error-alert">
            <i class="bi bi-exclamation-circle-fill me-2"></i>{{ error }}
          </div>
          <button type="submit" class="btn-login" :disabled="loading" style="background:#f97316; color:white;">
            <span v-if="loading">Registering...</span>
            <span v-else>Register Student</span>
          </button>
        </form>

        <div class="register-links">
          <p class="register-prompt">Already have an account?</p>
          <div class="register-btns">
            <router-link to="/login" class="btn-register btn-register-outline w-100 justify-content-center">
              <i class="bi bi-box-arrow-in-right me-2"></i>Back to Sign In
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const error = ref('')
const loading = ref(false)
const form = reactive({
  full_name: '',
  roll_number: '',
  branch: '',
  cgpa: '',
  grad_year: '',
  skills: '',
  education_details: '',
  experience: '',
  username: '',
  email: '',
  password: ''
})

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await axios.post('http://127.0.0.1:5000/api/auth/register/student', form)
    alert('Registration successful! You can now login.')
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
