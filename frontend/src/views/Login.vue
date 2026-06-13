<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-4">
        <div class="card shadow">
          <div class="card-body">
            <h3 class="card-title text-center mb-4">Placement Portal Login</h3>
            <form @submit.prevent="handleLogin">
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="username" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="password" type="password" class="form-control" required />
              </div>
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <button type="submit" class="btn btn-primary w-100" :disabled="loading">
                {{ loading ? 'Logging in...' : 'Login' }}
              </button>
            </form>
            <hr />
            <div class="text-center">
              <p class="mb-1">Don't have an account?</p>
              <div class="d-grid gap-2">
                <router-link to="/register/student" class="btn btn-outline-info btn-sm">Register as Student</router-link>
                <router-link to="/register/company" class="btn btn-outline-secondary btn-sm">Register as Company</router-link>
              </div>
            </div>
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
    
    localStorage.setItem('token', response.data.token)
    localStorage.setItem('role', response.data.role)
    localStorage.setItem('username', response.data.username)
    
    // Redirect based on role
    if (response.data.role === 'Admin') router.push('/admin')
    else if (response.data.role === 'Company') router.push('/company')
    else if (response.data.role === 'Student') router.push('/student')
    
  } catch (err) {
    error.value = err.response?.data?.message || 'Login failed'
  } finally {
    loading.value = false
  }
}
</script>
