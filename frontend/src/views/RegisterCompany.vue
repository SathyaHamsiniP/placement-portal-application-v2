<template>
  <div class="login-page">
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-logo"><i class="bi bi-mortarboard-fill"></i></div>
        <h1 class="brand-title">Campus<br>Placement<br>Portal</h1>
        <p class="brand-tagline">Join our network of top corporate partners.</p>
      </div>
    </div>
    <div class="form-panel">
      <div class="form-inner">
        <p class="form-eyebrow">COMPANY REGISTRATION</p>
        <h2 class="form-heading">Create corporate account</h2>
        
        <div class="error-alert mb-4" style="background:#fff3cd; color:#856404; border:1px solid #ffeeba;">
            <i class="bi bi-info-circle-fill me-2"></i>Account will require manual Admin approval.
        </div>

        <form @submit.prevent="handleRegister" class="login-form">
          <div class="field-group">
            <label class="field-label">COMPANY NAME</label>
            <input v-model="form.name" type="text" class="field-input" placeholder="e.g. Software Corp" required />
          </div>
          <div class="field-group">
            <label class="field-label">INDUSTRY</label>
            <select v-model="form.industry" class="field-input" required>
              <option value="" disabled selected>Select Industry</option>
              <option value="Software">Software</option>
              <option value="Hardware">Hardware</option>
              <option value="Finance">Finance</option>
              <option value="Consulting">Consulting</option>
              <option value="Cloud">Cloud</option>
              <option value="AI/ML">AI / ML</option>
              <option value="E-Commerce">E-Commerce</option>
              <option value="HealthTech">HealthTech</option>
              <option value="EdTech">EdTech</option>
              <option value="Logistics">Logistics</option>
            </select>
          </div>
          <div class="row">
            <div class="col-md-6">
              <div class="field-group">
                <label class="field-label">LOCATION</label>
                <input v-model="form.location" type="text" class="field-input" placeholder="e.g. Bangalore, India" required />
              </div>
            </div>
            <div class="col-md-6">
              <div class="field-group">
                <label class="field-label">WEBSITE</label>
                <input v-model="form.website" type="url" class="field-input" placeholder="e.g. https://company.com" required />
              </div>
            </div>
          </div>
          <div class="field-group">
            <label class="field-label">HR CONTACT</label>
            <input v-model="form.hr_contact" type="text" class="field-input" placeholder="Name or Email" required />
          </div>
          <div class="field-group">
            <label class="field-label">DESCRIPTION</label>
            <textarea v-model="form.description" class="field-input" placeholder="Brief about company size, operations, etc..." rows="3" style="resize: none;" required></textarea>
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
          <button type="submit" class="btn-login" :disabled="loading" style="background:#0f172a; color:white;">
            <span v-if="loading">Registering...</span>
            <span v-else>Register Company</span>
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
  name: '',
  industry: '',
  hr_contact: '',
  location: '',
  website: '',
  description: '',
  username: '',
  email: '',
  password: ''
})

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await axios.post('http://127.0.0.1:5000/api/auth/register/company', form)
    alert('Registration successful! Please wait for Admin approval.')
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
