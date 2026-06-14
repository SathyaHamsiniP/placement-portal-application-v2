<template>
  <div class="sidebar d-flex flex-column flex-shrink-0 p-3 bg-white shadow-sm h-100">
    <div class="d-flex align-items-center mb-4 mb-md-0 me-md-auto text-decoration-none">
      <div class="logo-box bg-primary text-white me-2">
        <i class="bi bi-mortarboard-fill"></i>
      </div>
      <span class="fs-5 fw-bold text-dark">Portal.v2</span>
    </div>
    <hr>
    <ul class="nav nav-pills flex-column mb-auto gap-2">
      <li v-for="item in menuItems" :key="item.id" class="nav-item">
        <a 
          href="#" 
          class="nav-link py-3 d-flex align-items-center" 
          :class="{ active: activeTab === item.id }"
          @click.prevent="$emit('update:activeTab', item.id)"
        >
          <i :class="`bi ${item.icon} me-3 fs-5`"></i>
          <span>{{ item.label }}</span>
        </a>
      </li>
    </ul>
    <hr>
    <div class="dropdown">
      <div class="d-flex align-items-center text-dark text-decoration-none p-2 status-user">
        <div class="avatar bg-secondary-soft text-secondary me-2">
          {{ username?.[0]?.toUpperCase() || 'U' }}
        </div>
        <div class="user-info">
          <div class="fw-bold text-truncate" style="max-width: 100px;">{{ username }}</div>
          <small class="text-muted">{{ role }}</small>
        </div>
        <button @click="$emit('logout')" class="btn btn-link text-danger ms-auto p-0 border-0">
          <i class="bi bi-box-arrow-right fs-5"></i>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  menuItems: { type: Array, required: true },
  activeTab: { type: String, required: true },
  username: { type: String, default: 'User' },
  role: { type: String, default: 'Member' }
})

defineEmits(['update:activeTab', 'logout'])
</script>

<style scoped>
.sidebar {
  width: 260px;
  position: fixed;
  left: 0;
  top: 0;
  bottom: 0;
  z-index: 1000;
}

.logo-box {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 1.2rem;
}

.nav-link {
  color: #6c757d;
  font-weight: 500;
  border-radius: 12px;
  transition: all 0.2s ease;
}

.nav-link:hover {
  background-color: #f8f9fa;
  color: #0d6efd;
}

.nav-link.active {
  background-color: #0d6efd;
  color: white !important;
  box-shadow: 0 4px 12px rgba(13, 110, 253, 0.25);
}

.avatar {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
}

.bg-secondary-soft { background-color: #e9ecef; }

.status-user {
  background-color: #fcfcfc;
  border-radius: 12px;
}

.user-info {
  line-height: 1.2;
}

@media (max-width: 768px) {
  .sidebar {
    width: 100%;
    position: relative;
    height: auto !important;
  }
}
</style>
