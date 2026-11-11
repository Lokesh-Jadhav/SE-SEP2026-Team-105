<template>
  <div class="stack">
    <header class="page-heading">
      <div>
        <p class="eyebrow">{{ mentor ? 'Mentor workspace' : 'Your next steps' }}</p>
        <h1>Hello, {{ firstName }}.</h1>
        <p>{{ mentor ? 'Make space for meaningful guidance.' : 'Keep moving toward what matters to you.' }}</p>
      </div>
      <button class="secondary small" :disabled="loading" @click="refresh">
        Refresh dashboard
      </button>
    </header>

    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="loading && !profile" role="status">Loading your dashboard…</p>

    <section v-if="mentor && profile" class="card">
      <div class="section-top">
        <div>
          <h2>Open to a new mentee</h2>
          <p class="hint">Turning this off prevents new assignments. It does not end an existing mentorship.</p>
        </div>
        <label class="check-row">
          <input
            type="checkbox"
            :checked="profile.available"
            :disabled="busy"
            @change="toggleAvailability($event.target.checked)"
          />
          {{ profile.available ? 'Available' : 'Unavailable' }}
        </label>
      </div>
    </section>

    <section v-if="profile && !activeMatch" class="card">
      <p class="eyebrow">Profile status</p>
      <h2>{{ statusTitle }}</h2>
      <p class="muted">{{ statusDescription }}</p>
      <span class="badge" :class="profile.status">{{ profile.status }}</span>
      <div v-if="profile.status === 'rejected'" class="actions">
        <RouterLink to="/complete-profile">Review and resubmit profile</RouterLink>
      </div>
    </section>

    <section v-for="ended in pendingFeedback" :key="ended.id" class="notice">
      <h2>Mentorship ended</h2>
      <p>
        {{ ended.ended_by === auth.role
          ? 'You ended this mentorship.'
          : ended.ended_by
            ? `Your ${mentor ? 'student' : 'mentor'} ended this mentorship.`
            : 'This mentorship has ended.' }}
        Please share your feedback.
      </p>
      <RouterLink class="button small" :to="`/feedback/${ended.id}`">Give feedback</RouterLink>
    </section>

    <template v-if="activeMatch">
      <section class="card">
        <div class="section-top">
          <div>
            <p class="eyebrow">{{ mentor ? 'Your mentee' : 'Your mentor' }}</p>
            <h2>{{ activeMatch.other_user.full_name }}</h2>
            <p class="muted">{{ activeMatch.other_user.email }}</p>
          </div>
          <button class="danger" :disabled="busy" @click="endMentorship">End mentorship</button>
        </div>
        <p class="hint">Ending is immediate. Both participants will be asked for feedback.</p>
      </section>

      <div class="columns">
        <div class="stack">
          <ChatPanel
            :key="`chat-${activeMatch.id}`"
            :match-id="activeMatch.id"
            :other-name="activeMatch.other_user.full_name"
          />
          <section class="card stack">
            <h2>{{ mentor ? 'Meeting requests' : 'Your meetings' }}</h2>
            <p v-if="!currentMeetings.length" class="empty">No meetings yet.</p>

            <article v-for="meeting in currentMeetings" :key="meeting.id" class="item">
              <h3>{{ dateTime(meeting.start_time) }}</h3>
              <p class="hint">Until {{ dateTime(meeting.end_time) }}</p>
              <div class="actions">
                <span class="badge" :class="meeting.status">{{ meeting.status }}</span>
                <template v-if="mentor && meeting.status === 'pending'">
                  <button class="small" :disabled="busy" @click="decide(meeting.id, 'accepted')">Accept</button>
                  <button class="secondary small" :disabled="busy" @click="decide(meeting.id, 'rejected')">Decline</button>
                </template>
                <a
                  v-if="meeting.status === 'accepted' && meeting.meet_link"
                  class="button secondary small"
                  :href="meeting.meet_link"
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  Join meeting<span class="sr-only"> (opens in a new tab)</span>
                </a>
              </div>
            </article>
          </section>
        </div>

        <div class="stack">
          <GoalsPanel :key="`goals-${activeMatch.id}`" :is-mentor="mentor" :is-student="!mentor" />
          <AvailabilityCalendar
            :key="`slots-${activeMatch.id}`"
            :mentor-id="mentor ? auth.user.id : activeMatch.other_user.id"
            :is-mentor="mentor"
            :is-student="!mentor"
            :title="mentor ? 'Your availability' : 'Mentor availability'"
            @changed="refresh"
          />
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import api from '../api'
import { dateTime, errorText } from '../utils'
import ChatPanel from './ChatPanel.vue'
import GoalsPanel from './GoalsPanel.vue'
import AvailabilityCalendar from './AvailabilityCalendar.vue'

const props = defineProps({ mentor: Boolean })
const auth = useAuthStore()
const router = useRouter()
const profile = ref(null)
const match = ref(null)
const endedMatches = ref([])
const meetings = ref([])
const error = ref('')
const loading = ref(false)
const busy = ref(false)
let timer
let disposed = false

const firstName = computed(() => profile.value?.full_name?.split(' ')[0] || 'there')
const activeMatch = computed(() => match.value && match.value.status !== 'ended' ? match.value : null)
const pendingFeedback = computed(() => endedMatches.value.filter(item => !item.feedback_submitted))
const currentMeetings = computed(() => meetings.value.filter(item => item.match_id === activeMatch.value?.id))

const statusTitle = computed(() => {
  if (profile.value?.status === 'pending') return 'Your profile is being reviewed.'
  if (profile.value?.status === 'rejected') return 'Your profile needs another look.'
  if (!props.mentor && endedMatches.value.length) return 'Your mentorship is complete.'
  if (props.mentor && !profile.value?.available) return 'You are not accepting new mentees.'
  return props.mentor ? 'Waiting for your next connection.' : 'We are finding your mentor.'
})

const statusDescription = computed(() => {
  if (profile.value?.status === 'pending') return 'An administrator will review your completed profile before matching.'
  if (profile.value?.status === 'rejected') return 'Review your details and resubmit your profile for administrator review.'
  if (!props.mentor && endedMatches.value.length) return 'Your completed mentorship is not placed back in the unmatched student queue.'
  return 'Approved profiles are matched by an administrator based on goals, background, and availability.'
})

async function refresh() {
  if (loading.value || busy.value) return
  loading.value = true
  try {
    const results = await Promise.all([
      api.get('/profiles/me'),
      api.get('/matching/my-match'),
      api.get('/mentorship/ended'),
      api.get('/scheduling/meetings')
    ])
    if (disposed) return
    profile.value = results[0].data.profile
    match.value = results[1].data.match
    endedMatches.value = results[2].data.matches
    meetings.value = results[3].data.meetings
    error.value = ''
  } catch (err) {
    if (!disposed) error.value = errorText(err)
  } finally {
    loading.value = false
  }
}

async function toggleAvailability(available) {
  busy.value = true
  try {
    await api.post('/mentorship/toggle-availability', { available })
    profile.value.available = available
    error.value = ''
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
    await refresh()
  }
}

async function endMentorship() {
  if (!window.confirm('End this mentorship now? This cannot be undone. Both participants will be asked for feedback.')) return
  busy.value = true
  try {
    const { data } = await api.post('/mentorship/end-request')
    await router.push(`/feedback/${data.match_id}`)
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}

async function decide(id, decision) {
  busy.value = true
  try {
    await api.post(`/scheduling/meetings/${id}/decision`, { decision })
    error.value = ''
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
    await refresh()
  }
}

onMounted(() => {
  refresh()
  timer = setInterval(() => {
    if (!document.hidden) refresh()
  }, 10000)
})
onUnmounted(() => {
  disposed = true
  clearInterval(timer)
})
</script>