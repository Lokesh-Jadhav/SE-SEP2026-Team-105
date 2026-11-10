import axios from 'axios'
import { useAuthStore } from './stores/auth'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000/api',
  timeout: 20000
})

api.interceptors.request.use(config => {
  const auth = useAuthStore()

  if (auth.token) {
    config.headers.Authorization = `Bearer ${auth.token}`
  }

  return config
})

api.interceptors.response.use(
  response => response,
  error => {
    // Invalid login credentials must remain on the login page.
    const url = error.config?.url || ''
    const authenticationRequest = ['/auth/login', '/auth/register'].includes(url)

    if (error.response?.status === 401 && !authenticationRequest) {
      useAuthStore().logout()
      if (window.location.pathname !== '/login') {
        window.location.assign('/login?expired=1')
      }
    }

    return Promise.reject(error)
  }
)

export default api