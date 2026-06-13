<template>
  <div class="container mt-4">
    <div class="row">
      <div class="col-12">
        <div class="d-flex justify-content-between align-items-center mb-4">
          <h2>Admin Dashboard</h2>
          <button @click="logout" class="btn btn-danger">Logout</button>
        </div>
        <div class="card bg-light">
          <div class="card-body">
            <h4>Welcome, Admin</h4>
            <p>You can manage company approvals and placements from here.</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()
const logout = () => {
  localStorage.clear()
  router.push('/login')
}
</script>
