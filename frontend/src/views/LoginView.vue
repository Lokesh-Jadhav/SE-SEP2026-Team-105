<template>
  <section class="auth-layout narrow">
    <p class="eyebrow">Welcome back</p>
    <h1>Pick up where you left off.</h1>
    <p class="muted">Sign in to your MentorBridge account.</p>

    <form class="card stack" @submit.prevent="submit" :aria-busy="busy">
      <p v-if="route.query.expired" class="notice" role="status">
        Your session expired. Please sign in again.
      </p>
      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <div class="field">
        <label for="login-email">Email address</label>
        <input id="login-email" v-model="email" type="email" autocomplete="username" required />
      </div>

      <div class="field">
        <label for="login-password">Password</label>
        <input id="login-password" v-model="password" type="password" autocomplete="current-password" required />
      </div>

      <button :disabled="busy">{{ busy ? 'Signing in…' : 'Sign in' }}</button>

      <p class="hint">
        New here? <RouterLink to="/register">Create an account</RouterLink>
      </p>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { errorText } from '../utils'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const email = ref('')
const password = ref('')
const error = ref('')
const busy = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    const { data } = await api.post('/auth/login', {
      email: email.value.trim(),
      password: password.value
    })
    auth.setSession(data.token, data.user)
    await router.push(
      data.user.role !== 'admin' && !data.user.profile_completed
        ? '/complete-profile'
        : `/${data.user.role}`
    )
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}
</script>