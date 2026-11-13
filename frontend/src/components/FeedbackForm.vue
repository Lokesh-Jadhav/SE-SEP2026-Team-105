<template>
  <section class="card stack" aria-labelledby="feedback-heading">
    <div>
      <p class="eyebrow">Close the loop</p>
      <h2 id="feedback-heading">How was your mentorship?</h2>
      <p class="muted">Your feedback helps administrators understand the experience.</p>
    </div>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <div v-if="submitted" class="notice" role="status">
      <p>Thank you. Your feedback has been submitted.</p>
      <RouterLink :to="auth.dashboard">Return to dashboard</RouterLink>
    </div>

    <form v-else class="stack" @submit.prevent="submit" :aria-busy="busy">
      <div class="field">
        <label :for="`rating-${matchId}`">Overall rating</label>
        <select :id="`rating-${matchId}`" v-model.number="rating" required>
          <option disabled value="">Choose a rating</option>
          <option :value="1">1 — Poor</option>
          <option :value="2">2 — Fair</option>
          <option :value="3">3 — Good</option>
          <option :value="4">4 — Very good</option>
          <option :value="5">5 — Excellent</option>
        </select>
      </div>
      <div class="field">
        <label :for="`comments-${matchId}`">Comments (optional)</label>
        <textarea :id="`comments-${matchId}`" v-model="comments" maxlength="4000" />
      </div>
      <button :disabled="busy">{{ busy ? 'Submitting…' : 'Submit feedback' }}</button>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { errorText } from '../utils'

const props = defineProps({ matchId: { type: Number, required: true } })
const emit = defineEmits(['submitted'])
const auth = useAuthStore()
const rating = ref('')
const comments = ref('')
const error = ref('')
const busy = ref(false)
const submitted = ref(false)

async function submit() {
  busy.value = true
  error.value = ''
  try {
    await api.post('/mentorship/feedback', {
      match_id: props.matchId,
      rating: rating.value,
      comments: comments.value.trim()
    })
    submitted.value = true
    emit('submitted')
  } catch (err) {
    if (err.response?.status === 409) {
      submitted.value = true
      emit('submitted')
    } else {
      error.value = errorText(err)
    }
  } finally {
    busy.value = false
  }
}
</script>