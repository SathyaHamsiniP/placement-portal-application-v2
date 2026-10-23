<template>
  <div id="app" class="app-container">
    <router-view />
  </div>
</template>

<style>
.app-container {
  min-height: 100vh;
  background-color: #f8f9fa;
  color: yellow !important;
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

body, #app, * {
  color: yellow !important; /* or hex code #eab308 */
}
</style>
