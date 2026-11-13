<template>
  <section class="auth-layout">
    <p class="eyebrow">Reflect and move forward</p>
    <h1>Mentorship feedback.</h1>

    <p v-if="loading" role="status">Loading mentorship details…</p>
    <p v-else-if="error" class="error" role="alert">{{ error }}</p>

    <div v-else-if="endedMatch?.feedback_submitted" class="card stack">
      <h2>Thank you for sharing your experience.</h2>
      <p>Your feedback has already been submitted.</p>
      <RouterLink :to="auth.dashboard">Return to dashboard</RouterLink>
    </div>

    <FeedbackForm v-else-if="endedMatch" :match-id="matchId" />
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { errorText } from '../utils'
import FeedbackForm from '../components/FeedbackForm.vue'

const route = useRoute()
const auth = useAuthStore()
const matchId = computed(() => Number(route.params.matchId))
const endedMatch = ref(null)
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  try {
    const { data } = await api.get('/mentorship/ended')
    endedMatch.value = data.matches.find(item => item.id === matchId.value)
    if (!endedMatch.value) error.value = 'This ended mentorship is not available for your account.'
  } catch (err) {
    error.value = errorText(err)
  } finally {
    loading.value = false
  }
})
</script>