<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<style>
.app-container {
  min-height: 100vh;
  background-color: #f8f9fa;
}

.card {
  border: none;
  border-radius: 12px;
}

.btn {
  border-radius: 8px;
  padding: 10px 20px;
  font-weight: 500;
}
</style>
