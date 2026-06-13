import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import RegisterStudent from '../views/RegisterStudent.vue'
import RegisterCompany from '../views/RegisterCompany.vue'
import AdminDashboard from '../views/dashboards/AdminDashboard.vue'
import CompanyDashboard from '../views/dashboards/CompanyDashboard.vue'
import StudentDashboard from '../views/dashboards/StudentDashboard.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', name: 'Login', component: Login },
  { path: '/register/student', name: 'RegisterStudent', component: RegisterStudent },
  { path: '/register/company', name: 'RegisterCompany', component: RegisterCompany },
  { 
    path: '/admin', 
    name: 'AdminDashboard', 
    component: AdminDashboard, 
    meta: { requiresAuth: true, role: 'Admin' } 
  },
  { 
    path: '/company', 
    name: 'CompanyDashboard', 
    component: CompanyDashboard, 
    meta: { requiresAuth: true, role: 'Company' } 
  },
  { 
    path: '/student', 
    name: 'StudentDashboard', 
    component: StudentDashboard, 
    meta: { requiresAuth: true, role: 'Student' } 
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  const role = localStorage.getItem('role')

  if (to.meta.requiresAuth) {
    if (!token) {
      next('/login')
    } else if (to.meta.role && to.meta.role !== role) {
      next('/') // Or a forbidden page
    } else {
      next()
    }
  } else {
    next()
  }
})

export default router
