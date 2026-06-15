<template>
  <div class="sidebar d-flex flex-column text-white shadow-lg">
    <div class="sidebar-header p-4 pb-2">
      <span class="small fw-bold tracking-tight text-orange text-uppercase">Controls</span>
    </div>
    
    <div class="sidebar-nav flex-grow-1 overflow-auto px-2 mt-3 no-scrollbar">
      <ul class="nav nav-pills flex-column gap-1">
        <li v-for="item in menuItems" :key="item.id" class="nav-item">
          <a 
            href="#" 
            class="nav-link d-flex align-items-center px-3 py-2" 
            :class="{ active: activeTab === item.id }"
            @click.prevent="$emit('update:activeTab', item.id)"
          >
            <i :class="`bi ${item.icon} me-3 fs-6`"></i>
            <span class="menu-text">{{ item.label }}</span>
          </a>
        </li>
      </ul>
    </div>

    <div class="sidebar-footer p-3 mt-auto">
      <button @click="$emit('logout')" class="btn btn-link nav-link text-white-50 p-2 w-100 text-start d-flex align-items-center hover-white border-0">
        <i class="bi bi-box-arrow-left me-3 fs-5"></i>
        <span class="menu-text">Logout</span>
      </button>
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
  width: 240px;
  background-color: #0f172a;
  height: 100vh;
  position: fixed;
  left: 0;
  top: 0;
  z-index: 1000;
  font-family: 'Inter', sans-serif;
  overflow: hidden;
}

.text-orange { color: #f97316 !important; }

.nav-link {
  color: #94a3b8;
  border-radius: 10px;
  transition: color 0.1s ease, background-color 0.1s ease;
  font-size: 0.85rem;
}

.nav-link:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.05);
}

.sidebar .nav-link.active {
  background: linear-gradient(135deg, #f97316 0%, #ea580c 100%) !important;
  color: #fff !important;
  box-shadow: 0 4px 12px rgba(249, 115, 22, 0.2);
  transition: none !important; /* Immediate switch to avoid blue glimpse */
}

.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { 
  -ms-overflow-style: none; /* IE and Edge */
  scrollbar-width: none; /* Firefox */
}

.menu-text {
  font-weight: 500;
  letter-spacing: 0.01em;
}

.hover-white:hover {
  color: #fff !important;
}

@media (max-width: 991px) {
  .sidebar { width: 80px; }
  .sidebar span { display: none; }
  .nav-link { justify-content: center; padding: 12px !important; }
  .nav-link i { margin-right: 0 !important; }
}
</style>
