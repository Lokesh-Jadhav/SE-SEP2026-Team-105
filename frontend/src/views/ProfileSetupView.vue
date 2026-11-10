<template>
  <section class="auth-layout">
    <p class="eyebrow">Make the right connection</p>
    <h1>Your profile.</h1>
    <p class="muted">Keep your background and goals clear and up to date.</p>

    <p v-if="loading" role="status">Loading your profile…</p>

    <form v-else class="card stack" @submit.prevent="save" :aria-busy="busy">
      <p v-if="route.query.resume" class="notice" role="status">
        Your account was created, but your profile was not saved.
        Complete the details below to continue.
      </p>
      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <ProfileFields v-model="profile" :role="auth.role" prefix="edit" />

      <p class="notice">
        Saving submits your profile for review again.
        Mentor profile saves also turn mentoring availability on,
        following your existing backend behavior.
      </p>

      <div class="actions">
        <button :disabled="busy">{{ busy ? 'Saving…' : 'Save and submit for review' }}</button>
        <RouterLink v-if="auth.user?.profile_completed" :to="auth.dashboard">
          Back to dashboard
        </RouterLink>
      </div>
    </form>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import ProfileFields from '../components/ProfileFields.vue'
import { emptyProfile, profilePayload, errorText } from '../utils'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()
const profile = ref(emptyProfile())
const loading = ref(true)
const busy = ref(false)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/profiles/me')
    profile.value = { ...profile.value, ...(data.profile || {}) }
  } catch (err) {
    error.value = errorText(err)
  } finally {
    loading.value = false
  }
})

async function save() {
  busy.value = true
  error.value = ''
  try {
    await api.post(`/profiles/${auth.role}`, profilePayload(auth.role, profile.value))
    auth.setUser({ ...auth.user, profile_completed: true })
    await router.push(auth.dashboard)
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}
</script>