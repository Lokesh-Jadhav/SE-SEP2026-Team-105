<template>
  <section class="card stack" aria-labelledby="availability-heading">
    <div>
      <h2 id="availability-heading">{{ title }}</h2>
      <p class="hint">All times are shown in your device's local timezone.</p>
    </div>

    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>

    <form v-if="isMentor" class="stack" @submit.prevent="add">
      <div class="form-grid">
        <div class="field">
          <label for="slot-start">Start time</label>
          <input id="slot-start" v-model="form.start_time" type="datetime-local" required />
        </div>
        <div class="field">
          <label for="slot-end">End time</label>
          <input id="slot-end" v-model="form.end_time" type="datetime-local" required />
        </div>
      </div>
      <button :disabled="busy">Add available time</button>
    </form>

    <p v-if="!futureSlots.length" class="empty">No upcoming availability.</p>

    <article v-for="slot in futureSlots" :key="slot.id" class="item">
      <h3>{{ dateTime(slot.start_time) }}</h3>
      <p class="hint">Until {{ dateTime(slot.end_time) }}</p>
      <div class="actions">
        <span class="badge">{{ slot.is_booked ? 'Booked' : 'Available' }}</span>
        <button
          v-if="isStudent && !slot.is_booked"
          class="secondary small"
          :disabled="busy || requestedIds.includes(slot.id)"
          @click="request(slot.id)"
        >
          {{ requestedIds.includes(slot.id) ? 'Requested' : 'Request this time' }}
        </button>
      </div>
    </article>
  </section>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '../api'
import { dateTime, errorText } from '../utils'

const props = defineProps({
  mentorId: { type: Number, required: true },
  isMentor: Boolean,
  isStudent: Boolean,
  title: { type: String, default: 'Availability' }
})
const emit = defineEmits(['changed'])
const slots = ref([])
const requestedIds = ref([])
const form = ref({ start_time: '', end_time: '' })
const error = ref('')
const notice = ref('')
const busy = ref(false)

const futureSlots = computed(() => slots.value.filter(slot => {
  const raw = slot.end_time
  const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(raw) ? raw : `${raw}Z`
  return new Date(normalized).getTime() > Date.now()
}))

async function load() {
  const { data } = await api.get(`/scheduling/availability/mentor/${props.mentorId}`)
  slots.value = data.availability
}

async function add() {
  error.value = ''
  notice.value = ''
  const start = new Date(form.value.start_time)
  const end = new Date(form.value.end_time)
  if (start <= new Date() || end <= start) {
    error.value = 'Choose a future start time and an end time after it.'
    return
  }
  busy.value = true
  try {
    await api.post('/scheduling/availability', {
      start_time: start.toISOString(),
      end_time: end.toISOString()
    })
    form.value = { start_time: '', end_time: '' }
    notice.value = 'Availability added.'
    await load()
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}

async function request(id) {
  busy.value = true
  error.value = ''
  try {
    await api.post('/scheduling/request', { availability_id: id })
    requestedIds.value.push(id)
    notice.value = 'Request sent. Your mentor will confirm or decline it.'
    emit('changed')
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}

onMounted(async () => {
  try {
    await load()
  } catch (err) {
    error.value = errorText(err)
  }
})
</script>