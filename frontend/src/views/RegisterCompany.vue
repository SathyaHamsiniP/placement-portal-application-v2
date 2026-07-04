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
            <input v-model="form.industry" type="text" class="field-input" placeholder="e.g. Technology, Finance" required />
          </div>
          <div class="field-group">
            <label class="field-label">HR CONTACT</label>
            <input v-model="form.hr_contact" type="text" class="field-input" placeholder="Name or Email" required />
          </div>
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
          <button type="submit" class="btn-login" :disabled="loading" style="background:var(--slate-800); color:white;">
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
const form = reactive({ name: '', industry: '', hr_contact: '', username: '', email: '', password: '' })

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
