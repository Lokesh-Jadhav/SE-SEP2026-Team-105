<template>
  <section class="auth-layout">
    <p class="eyebrow">Your next chapter</p>
    <h1>Join MentorBridge.</h1>
    <p class="muted">A few details help us make a more meaningful connection.</p>

    <form class="card stack" @submit.prevent="submit" :aria-busy="busy">
      <p v-if="error" class="error" role="alert">{{ error }}</p>

      <fieldset>
        <legend>Your account</legend>
        <div class="form-grid">
          <div class="field full">
            <label for="register-role">I am joining as</label>
            <select id="register-role" v-model="role">
              <option value="student">A student looking for guidance</option>
              <option value="mentor">A mentor or alumnus offering guidance</option>
            </select>
          </div>
          <div class="field">
            <label for="register-email">Email address</label>
            <input id="register-email" v-model="email" type="email" autocomplete="email" required />
          </div>
          <div class="field">
            <label for="register-password">Password</label>
            <input id="register-password" v-model="password" type="password" autocomplete="new-password" required minlength="8" aria-describedby="password-help" />
            <p id="password-help" class="hint">Use at least 8 characters.</p>
          </div>
        </div>
      </fieldset>

      <ProfileFields v-model="profile" :role="role" prefix="register" />

      <p class="hint">Your completed profile will be submitted for administrator review.</p>
      <button :disabled="busy">{{ busy ? 'Creating your account…' : 'Create account and submit profile' }}</button>
      <p class="hint">Already registered? <RouterLink to="/login">Sign in</RouterLink></p>
    </form>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import ProfileFields from '../components/ProfileFields.vue'
import { emptyProfile, profilePayload, errorText } from '../utils'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const role = ref(route.query.role === 'mentor' ? 'mentor' : 'student')
const email = ref('')
const password = ref('')
const profile = ref(emptyProfile())
const error = ref('')
const busy = ref(false)

async function submit() {
  error.value = ''
  busy.value = true
  let accountCreated = false

  try {
    const { data } = await api.post('/auth/register', {
      role: role.value,
      email: email.value.trim(),
      password: password.value
    })
    auth.setSession(data.token, data.user)
    accountCreated = true

    await api.post(`/profiles/${role.value}`, profilePayload(role.value, profile.value))
    auth.setUser({ ...data.user, profile_completed: true })
    await router.push(`/${role.value}`)
  } catch (err) {
    if (accountCreated) {
      await router.push({
        path: '/complete-profile',
        query: { resume: '1' }
      })
    } else {
      error.value = errorText(err)
    }
  } finally {
    busy.value = false
  }
}
</script>