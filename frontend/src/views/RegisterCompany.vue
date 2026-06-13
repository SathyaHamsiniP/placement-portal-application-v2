<template>
  <div class="container mt-5">
    <div class="row justify-content-center">
      <div class="col-md-5">
        <div class="card shadow">
          <div class="card-body">
            <h3 class="card-title text-center mb-4">Company Registration</h3>
            <div class="alert alert-warning py-2 mb-4" style="font-size: 0.9rem;">
              Note: Your account will require manual approval from the Institute Admin.
            </div>
            <form @submit.prevent="handleRegister">
              <div class="mb-3">
                <label class="form-label">Company Name</label>
                <input v-model="form.name" type="text" class="form-control" required />
              </div>
              <div class="mb-3">
                <label class="form-label">HR Contact (Name/Email)</label>
                <input v-model="form.hr_contact" type="text" class="form-control" required />
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
              <button type="submit" class="btn btn-secondary w-100" :disabled="loading">
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
  name: '',
  hr_contact: '',
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
