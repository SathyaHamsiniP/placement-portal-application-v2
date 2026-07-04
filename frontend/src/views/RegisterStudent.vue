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
          <div class="field-group">
            <label class="field-label">ROLL NUMBER</label>
            <input v-model="form.roll_number" type="text" class="field-input" placeholder="e.g. 21F300123" required />
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
const form = reactive({ full_name: '', roll_number: '', username: '', email: '', password: '' })

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
