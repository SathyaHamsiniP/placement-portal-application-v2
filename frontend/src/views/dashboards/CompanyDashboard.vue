<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2>Company Dashboard</h2>
          <button @click="logout" class="btn btn-danger">Logout</button>
        </div>
        <div class="card bg-light">
          <div class="card-body">
            <h4>Welcome, {{ username }}</h4>
            <p>Post drives and manage applicants once your profile is approved.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const username = localStorage.getItem('username')
const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>
