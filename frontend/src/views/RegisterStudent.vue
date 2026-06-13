<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow">
          <div class="card-body">
            <h3 class="card-title text-center mb-4">Student Registration</h3>
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label class="form-label">Full Name</label>
                <input v-model="form.full_name" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Roll Number</label>
                <input v-model="form.roll_number" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Username</label>
                <input v-model="form.username" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Email</label>
                <input v-model="form.email" type="email" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">Password</label>
                <input v-model="form.password" type="password" class="form-control" required />
              </div>
              <div v-if="error" class="alert alert-danger">{{ error }}</div>
              <button type="submit" class="btn btn-info w-100 text-white" :disabled="loading">
                {{ loading ? 'Registering...' : 'Register' }}
              </button>
            </form>
            <div class="text-center mt-3">
              <router-link to="/login">Already have an account? Login</router-link>
            </div>
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
  username: '',
  email: '',
  password: ''
})

const handleRegister = async () => {
  loading.value = true
  error.value = ''
  try {
    await axios.post('http://127.0.0.1:5000/api/auth/register/student', form)
    alert('Registration successful! Please login.')
    router.push('/login')
  } catch (err) {
    error.value = err.response?.data?.message || 'Registration failed'
  } finally {
    loading.value = false
  }
}
</script>
