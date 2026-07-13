<template>
  <div class="login-page">
    <!-- Left branding panel -->
    <div class="brand-panel">
      <div class="brand-inner">
        <div class="brand-logo">
          <i class="bi bi-mortarboard-fill"></i>
        </div>
        <h1 class="brand-title">Campus<br>Placement<br>Portal</h1>
        <p class="brand-tagline">Connecting talent with opportunity — one placement at a time.</p>
        <div class="brand-stats">
          <div class="bstat"><div class="bstat-val">500+</div><div class="bstat-label">Students</div></div>
          <div class="bstat"><div class="bstat-val">80+</div><div class="bstat-label">Companies</div></div>
          <div class="bstat"><div class="bstat-val">95%</div><div class="bstat-label">Placed</div></div>
        </div>
      </div>
    </div>

    <!-- Right login form panel -->
    <div class="form-panel">
      <div class="form-inner">
        <p class="form-eyebrow">WELCOME BACK</p>
        <h2 class="form-heading">Sign in to your account</h2>

        <form @submit.prevent="handleLogin" class="login-form">
          <div class="field-group">
            <label class="field-label">USERNAME</label>
            <input v-model="username" type="text" class="field-input" placeholder="Enter your username" required />
          </div>
          <div class="field-group">
            <label class="field-label">PASSWORD</label>
            <input v-model="password" type="password" class="field-input" placeholder="Enter your password" required />
          </div>

          <div v-if="error" class="error-alert">
            <i class="bi bi-exclamation-circle-fill me-2"></i>{{ error }}
          </div>

          <button type="submit" class="btn-login" :disabled="loading">
            <span v-if="loading"><i class="bi bi-hourglass-split me-2"></i>Signing in...</span>
            <span v-else>Sign In</span>
          </button>
        </form>

        <div class="register-links">
          <p class="register-prompt">Don't have an account?</p>
          <div class="register-btns">
            <router-link to="/register/student" class="btn-register">
              <i class="bi bi-person-plus me-2"></i>Register as Student
            </router-link>
            <router-link to="/register/company" class="btn-register btn-register-outline">
              <i class="bi bi-building me-2"></i>Register as Company
            </router-link>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)
const router = useRouter()

const handleLogin = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.post('http://127.0.0.1:5000/api/auth/login', {
      username: username.value,
      password: password.value
    })
    sessionStorage.setItem('token', response.data.token)
    sessionStorage.setItem('role', response.data.role)
    sessionStorage.setItem('username', response.data.username)

    if (response.data.role === 'Admin') router.push('/admin')
    else if (response.data.role === 'Company') router.push('/company')
    else if (response.data.role === 'Student') router.push('/student')
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed. Please check your credentials.'
  } finally {
    loading.value = false
  }
}
</script>

<style>
* { font-family: 'Inter', system-ui, sans-serif; box-sizing: border-box; }

.login-page {
  display: flex;
  min-height: 100vh;
  background: #f8fafc;
}

/* ── Left branding panel ── */
.brand-panel {
  width: 42%;
  background: linear-gradient(145deg, #f97316 0%, #ea580c 60%, #c2410c 100%);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 48px;
  position: relative;
  overflow: hidden;
}
.brand-panel::before {
  content: '';
  position: absolute;
  top: -80px; right: -80px;
  width: 320px; height: 320px;
  background: rgba(255,255,255,0.07);
  border-radius: 50%;
}
.brand-panel::after {
  content: '';
  position: absolute;
  bottom: -60px; left: -60px;
  width: 240px; height: 240px;
  background: rgba(255,255,255,0.05);
  border-radius: 50%;
}
.brand-inner { position: relative; z-index: 1; color: white; }
.brand-logo {
  font-size: 52px;
  margin-bottom: 24px;
  opacity: 0.95;
}
.brand-title {
  font-size: 42px;
  font-weight: 800;
  line-height: 1.1;
  letter-spacing: -1px;
  margin: 0 0 20px;
}
.brand-tagline {
  font-size: 15px;
  line-height: 1.6;
  opacity: 0.85;
  margin: 0 0 48px;
  max-width: 340px;
}
.brand-stats {
  display: flex;
  gap: 40px;
}
.bstat-val {
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.5px;
}
.bstat-label {
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  opacity: 0.75;
  margin-top: 2px;
}

/* ── Right form panel ── */
.form-panel {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 48px;
}
.form-inner {
  width: 100%;
  max-width: 420px;
}
.form-eyebrow {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  color: #f97316;
  text-transform: uppercase;
  margin: 0 0 10px;
}
.form-heading {
  font-size: 28px;
  font-weight: 800;
  color: #0f172a;
  letter-spacing: -0.5px;
  margin: 0 0 36px;
}

/* ── Fields ── */
.login-form { display: flex; flex-direction: column; gap: 20px; }
.field-group { display: flex; flex-direction: column; gap: 8px; }
.field-label {
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  color: #64748b;
  text-transform: uppercase;
}
.field-input {
  width: 100%;
  padding: 14px 16px;
  border: 1.5px solid #e2e8f0;
  border-radius: 10px;
  font-size: 14px;
  font-family: 'Inter', sans-serif;
  color: #0f172a;
  background: #fff;
  transition: border-color 0.2s, box-shadow 0.2s;
  outline: none;
}
.field-input::placeholder { color: #94a3b8; }
.field-input:focus {
  border-color: #f97316;
  box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.12);
}

/* ── Login button ── */
.btn-login {
  width: 100%;
  padding: 15px;
  background: #f97316;
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 700;
  font-family: 'Inter', sans-serif;
  cursor: pointer;
  transition: background 0.2s, transform 0.1s, box-shadow 0.2s;
  margin-top: 4px;
  letter-spacing: 0.02em;
}
.btn-login:hover:not(:disabled) {
  background: #ea580c;
  box-shadow: 0 4px 16px rgba(249,115,22,0.35);
}
.btn-login:active:not(:disabled) { transform: scale(0.99); }
.btn-login:disabled { opacity: 0.65; cursor: not-allowed; }

/* ── Register links ── */
.register-links {
  margin-top: 32px;
  padding-top: 28px;
  border-top: 1px solid #f1f5f9;
}
.register-prompt {
  font-size: 13px;
  color: #64748b;
  margin: 0 0 14px;
  text-align: center;
}
.register-btns { display: flex; flex-direction: column; gap: 10px; }
.btn-register {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 13px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  font-family: 'Inter', sans-serif;
  text-decoration: none;
  background: #f97316;
  color: white;
  border: 1.5px solid #f97316;
  transition: background 0.2s, box-shadow 0.2s;
}
.btn-register:hover {
  background: #ea580c;
  border-color: #ea580c;
  box-shadow: 0 4px 14px rgba(249,115,22,0.28);
}
.btn-register-outline {
  background: transparent;
  color: #f97316;
}
.btn-register-outline:hover {
  background: rgba(249,115,22,0.07);
  border-color: #f97316;
  box-shadow: none;
}

/* ── Error ── */
.error-alert {
  background: #fef2f2;
  color: #dc2626;
  border: 1px solid #fecaca;
  border-radius: 10px;
  padding: 12px 16px;
  font-size: 13px;
  font-weight: 500;
  display: flex;
  align-items: center;
}

@media (max-width: 768px) {
  .login-page { flex-direction: column; }
  .brand-panel { width: 100%; padding: 40px 32px; }
  .brand-title { font-size: 30px; }
  .form-panel { padding: 40px 24px; }
}
</style>
