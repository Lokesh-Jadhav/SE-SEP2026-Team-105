<template>
  <a class="skip-link" href="#main-content">Skip to main content</a>

  <header class="site-header">
    <div class="header-inner">
      <RouterLink class="brand" to="/" aria-label="MentorBridge home">
        <span class="brand-mark" aria-hidden="true">m.</span>
        MentorBridge
      </RouterLink>

      <nav aria-label="Main navigation">
        <template v-if="auth.isLoggedIn">
          <RouterLink :to="auth.dashboard">Dashboard</RouterLink>
          <RouterLink v-if="auth.role !== 'admin'" to="/complete-profile">
            Profile
          </RouterLink>
          <button class="button secondary small" @click="logout">Sign out</button>
        </template>

        <template v-else>
          <RouterLink to="/login">Sign in</RouterLink>
          <RouterLink class="button small" to="/register">Get started</RouterLink>
        </template>
      </nav>
    </div>
  </header>

  <main id="main-content" ref="main" tabindex="-1" class="container">
    <RouterView />
  </main>

  <footer class="site-footer">
    <span>MentorBridge</span>
    <span>One connection. A clearer next step.</span>
  </footer>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from './stores/auth'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const main = ref(null)

watch(() => route.path, async () => {
  await nextTick()
  main.value?.focus()
})

function logout() {
  auth.logout()
  router.push('/')
}
</script>