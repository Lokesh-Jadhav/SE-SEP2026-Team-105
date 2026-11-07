import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

import LandingView from '../views/LandingView.vue'
import LoginView from '../views/LoginView.vue'
import RegisterView from '../views/RegisterView.vue'
import ProfileSetupView from '../views/ProfileSetupView.vue'
import StudentDashboard from '../views/StudentDashboard.vue'
import MentorDashboard from '../views/MentorDashboard.vue'
import AdminDashboard from '../views/AdminDashboard.vue'
import FeedbackView from '../views/FeedbackView.vue'

const router = createRouter({
  history: createWebHistory(),
  scrollBehavior: () => ({ top: 0 }),
  routes: [
    { path: '/', component: LandingView, meta: { title: 'Welcome' } },
    { path: '/login', component: LoginView, meta: { title: 'Sign in' } },
    { path: '/register', component: RegisterView, meta: { title: 'Join MentorBridge' } },
    {
      path: '/complete-profile',
      component: ProfileSetupView,
      meta: { auth: true, title: 'Your profile' }
    },
    {
      path: '/student',
      component: StudentDashboard,
      meta: { auth: true, role: 'student', title: 'Student dashboard' }
    },
    {
      path: '/mentor',
      component: MentorDashboard,
      meta: { auth: true, role: 'mentor', title: 'Mentor dashboard' }
    },
    {
      path: '/admin',
      component: AdminDashboard,
      meta: { auth: true, role: 'admin', title: 'Administration' }
    },
    {
      path: '/feedback/:matchId(\\d+)',
      component: FeedbackView,
      meta: { auth: true, title: 'Mentorship feedback' }
    },
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

router.beforeEach(to => {
  const auth = useAuthStore()

  if (to.meta.auth && !auth.isLoggedIn) return '/login'

  if (to.meta.role && auth.role !== to.meta.role) {
    return auth.isLoggedIn ? auth.dashboard : '/login'
  }

  if (to.path === '/complete-profile' && auth.role === 'admin') return '/admin'

  if (
    to.meta.auth &&
    auth.role !== 'admin' &&
    !auth.user?.profile_completed &&
    to.path !== '/complete-profile'
  ) {
    return '/complete-profile'
  }
})

router.afterEach(to => {
  document.title = `${to.meta.title || 'MentorBridge'} · MentorBridge`
})

export default router