<template>
  <section class="card stack" aria-labelledby="goals-heading">
    <header>
      <p class="eyebrow">Small steps, real progress</p>
      <h2 id="goals-heading">Mentorship goals</h2>
      <p class="hint">Sorted by deadline, earliest first.</p>
    </header>

    <p v-if="error" class="error" role="alert">
      {{ error }}
    </p>

    <p class="sr-only" role="status">
      {{ notice }}
    </p>

    <div class="goal-progress">
      <div class="goal-progress-label">
        <label for="goal-progress">
          {{ progress.completed }} of {{ progress.total }} completed
        </label>

        <span class="hint">{{ progress.percentage }}%</span>
      </div>

      <progress
        id="goal-progress"
        :value="progress.completed"
        :max="progress.total || 1"
      >
        {{ progress.percentage }}%
      </progress>
    </div>

    <!-- Mentor goal creation -->
    <details v-if="isMentor" class="goal-create">
      <summary>Add a goal</summary>

      <form class="stack goal-create-form" @submit.prevent="create">
        <div class="field">
          <label for="goal-title">Goal title</label>
          <input
            id="goal-title"
            v-model="form.title"
            required
            maxlength="255"
          />
        </div>

        <div class="field">
          <label for="goal-description">Description (optional)</label>
          <textarea
            id="goal-description"
            v-model="form.description"
            maxlength="4000"
          />
        </div>

        <div class="field">
          <label for="goal-due">Deadline (optional)</label>
          <input
            id="goal-due"
            v-model="form.due_date"
            type="date"
          />
        </div>

        <div class="actions">
          <button :disabled="busy">
            {{ busy ? 'Saving…' : 'Add goal' }}
          </button>
        </div>
      </form>
    </details>

    <p v-if="initialLoading" role="status" class="empty">
      Loading goals…
    </p>

    <p v-else-if="!goals.length" class="empty">
      No goals yet. Your next steps will appear here.
    </p>

    <!-- Compact goal list -->
    <ul v-else class="goal-list" aria-label="Goals ordered by deadline">
      <li
        v-for="goal in sortedGoals"
        :key="goal.id"
        class="goal-item"
        :class="{
          'goal-item--overdue': isOverdue(goal),
          'goal-item--completed': goal.completed
        }"
      >
        <div class="goal-row">
          <!-- Students can change completion; mentors see read-only status. -->
          <label
            v-if="isStudent"
            class="goal-main"
            :for="`goal-${goal.id}`"
          >
            <input
              :id="`goal-${goal.id}`"
              type="checkbox"
              :checked="goal.completed"
              :disabled="busy"
              @change="toggle(goal.id)"
            />

            <span
              class="goal-title"
              :class="{ 'goal-title--completed': goal.completed }"
            >
              {{ goal.title }}
            </span>
          </label>

          <div v-else class="goal-main">
            <span
              class="goal-status-box"
              :class="{ 'goal-status-box--completed': goal.completed }"
              aria-hidden="true"
            >
              {{ goal.completed ? '✓' : '' }}
            </span>

            <span
              class="goal-title"
              :class="{ 'goal-title--completed': goal.completed }"
            >
              {{ goal.title }}
              <span class="sr-only">
                — {{ goal.completed ? 'Completed' : 'Not completed' }}
              </span>
            </span>
          </div>

          <button
            v-if="isMentor"
            class="secondary small goal-remove"
            :disabled="busy"
            @click="remove(goal)"
          >
            Remove
            <span class="sr-only">{{ goal.title }}</span>
          </button>
        </div>

        <span v-if="isOverdue(goal)" class="goal-overdue-label">
          Overdue
        </span>

        <!-- Native disclosure keeps details hidden until requested. -->
        <details class="goal-details">
          <summary>
            <span class="details-closed">View details</span>
            <span class="details-open">Hide details</span>
            <span class="sr-only">for {{ goal.title }}</span>
          </summary>

          <dl class="goal-detail-content">
            <div>
              <dt>Description</dt>
              <dd class="goal-description">
                {{ goal.description || 'No description provided.' }}
              </dd>
            </div>

            <div>
              <dt>Deadline</dt>
              <dd :class="{ 'goal-deadline--overdue': isOverdue(goal) }">
                {{ dateOnly(goal.due_date) }}
                <span v-if="isOverdue(goal)"> — Overdue</span>
              </dd>
            </div>

            <div>
              <dt>Status</dt>
              <dd>
                {{ goal.completed ? 'Completed' : 'In progress' }}
              </dd>
            </div>

            <div v-if="goal.completed && goal.completed_at">
              <dt>Completed on</dt>
              <dd>{{ dateTime(goal.completed_at) }}</dd>
            </div>
          </dl>
        </details>
      </li>
    </ul>
  </section>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import api from '../api'
import { dateOnly, dateTime, errorText } from '../utils'

defineProps({
  isMentor: {
    type: Boolean,
    default: false
  },
  isStudent: {
    type: Boolean,
    default: false
  }
})

const goals = ref([])
const form = ref({
  title: '',
  description: '',
  due_date: ''
})

const error = ref('')
const notice = ref('')
const busy = ref(false)
const initialLoading = ref(true)

// Refresh the date during polling so overdue styling updates
// if the page stays open overnight.
const today = ref(localDateKey())

let timer = null
let loading = false
let disposed = false

function localDateKey() {
  const date = new Date()
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')

  return `${year}-${month}-${day}`
}

const sortedGoals = computed(() => {
  return [...goals.value].sort((a, b) => {
    // ISO date-only values sort chronologically as strings.
    // No deadline sorts after every dated goal.
    const aDeadline = a.due_date || '9999-12-31'
    const bDeadline = b.due_date || '9999-12-31'

    const deadlineOrder = aDeadline.localeCompare(bDeadline)

    if (deadlineOrder !== 0) return deadlineOrder

    // Keep ordering stable for goals sharing a deadline.
    return a.id - b.id
  })
})

const progress = computed(() => {
  const total = goals.value.length
  const completed = goals.value.filter(goal => goal.completed).length

  return {
    total,
    completed,
    percentage: total ? Math.round((completed / total) * 100) : 0
  }
})

function isOverdue(goal) {
  // A goal due today remains on time until the day has passed.
  // Completed goals are never highlighted as overdue.
  return Boolean(
    !goal.completed &&
    goal.due_date &&
    goal.due_date < today.value
  )
}

async function load() {
  if (disposed || loading || busy.value || document.hidden) return

  loading = true

  try {
    const { data } = await api.get('/goals/')

    if (disposed) return

    goals.value = data.goals
    today.value = localDateKey()
  } catch (err) {
    if (!disposed) {
      error.value = errorText(err)
    }
  } finally {
    loading = false

    if (!disposed) {
      initialLoading.value = false
    }
  }
}

async function mutate(action, message) {
  if (busy.value) return

  busy.value = true
  error.value = ''
  notice.value = ''

  try {
    await action()

    if (!disposed) {
      notice.value = message
    }
  } catch (err) {
    if (!disposed) {
      error.value = errorText(err)
    }
  } finally {
    busy.value = false
    await load()
  }
}

async function create() {
  if (!form.value.title.trim()) return

  await mutate(async () => {
    await api.post('/goals/', {
      title: form.value.title.trim(),
      description: form.value.description.trim(),
      due_date: form.value.due_date
    })

    form.value = {
      title: '',
      description: '',
      due_date: ''
    }
  }, 'Goal added.')
}

async function toggle(id) {
  await mutate(
    () => api.post(`/goals/${id}/toggle`),
    'Goal progress updated.'
  )
}

async function remove(goal) {
  if (!window.confirm(`Remove the goal “${goal.title}”?`)) return

  await mutate(
    () => api.delete(`/goals/${goal.id}`),
    'Goal removed.'
  )
}

function refreshWhenVisible() {
  if (!document.hidden) {
    today.value = localDateKey()
    load()
  }
}

onMounted(() => {
  load()

  timer = setInterval(refreshWhenVisible, 10000)
  document.addEventListener('visibilitychange', refreshWhenVisible)
})

onUnmounted(() => {
  disposed = true
  clearInterval(timer)
  document.removeEventListener('visibilitychange', refreshWhenVisible)
})
</script>

<style scoped>
.goal-progress-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  margin-bottom: 0.4rem;
}

.goal-progress-label .hint {
  margin: 0;
}

.goal-create {
  margin: 0;
  padding-top: 0.75rem;
}

.goal-create-form {
  margin-top: 1rem;
}

.goal-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.goal-item {
  padding: 1rem 0;
  border-bottom: 1px solid var(--line);
}

.goal-item:first-child {
  padding-top: 0.25rem;
}

.goal-item:last-child {
  border-bottom: 0;
  padding-bottom: 0;
}

.goal-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 0.75rem;
}

.goal-main {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  min-width: 0;
  min-height: 44px;
  margin: 0;
  padding: 0.6rem 0;
  flex: 1;
}

label.goal-main {
  cursor: pointer;
}

.goal-main input[type="checkbox"] {
  margin: 0.1rem 0 0;
}

.goal-title {
  font-size: 0.95rem;
  font-weight: 650;
  line-height: 1.5;
  overflow-wrap: anywhere;
}

.goal-title--completed {
  text-decoration: line-through;
  color: var(--muted);
}

.goal-remove {
  flex-shrink: 0;
}

/* Mentor-facing completion indicator: read-only, not a disabled input. */
.goal-status-box {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 22px;
  height: 22px;
  margin-top: 0.1rem;
  border: 1.5px solid var(--control-line);
  border-radius: 5px;
  color: transparent;
  font-size: 0.9rem;
  font-weight: 800;
}

.goal-status-box--completed {
  border-color: var(--primary);
  background: var(--primary);
  color: white;
}

/* Show both text and color so overdue status is not color-only. */
.goal-item--overdue .goal-title {
  color: var(--danger);
}

.goal-overdue-label {
  display: inline-block;
  margin: 0.1rem 0 0.2rem 2.125rem;
  padding: 0.1rem 0.5rem;
  border: 1px solid #d6a19a;
  border-radius: 999px;
  background: var(--danger-soft);
  color: var(--danger);
  font-size: 0.75rem;
  font-weight: 700;
}

/* Override the global details divider for each compact goal. */
.goal-details {
  margin: 0 0 0 2.125rem;
  padding: 0;
  border: 0;
}

.goal-details summary {
  width: fit-content;
  min-height: 44px;
  padding: 0.6rem 0.25rem;
  font-size: 0.85rem;
  font-weight: 600;
  letter-spacing: normal;
}

.details-open {
  display: none;
}

.goal-details[open] .details-closed {
  display: none;
}

.goal-details[open] .details-open {
  display: inline;
}

.goal-detail-content {
  display: grid;
  gap: 0.85rem;
  margin: 0.25rem 0 0.5rem;
  padding: 1rem;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: var(--surface-soft);
}

.goal-detail-content dt {
  margin-bottom: 0.2rem;
  font-size: 0.78rem;
  font-weight: 650;
}

.goal-detail-content dd {
  margin: 0;
  font-size: 0.9rem;
  line-height: 1.65;
}

.goal-description {
  white-space: pre-wrap;
}

.goal-deadline--overdue {
  color: var(--danger);
  font-weight: 650;
}

@media (max-width: 400px) {
  .goal-row {
    gap: 0.5rem;
  }

  .goal-main {
    gap: 0.5rem;
  }

  .goal-title {
    font-size: 0.875rem;
  }

  .goal-remove {
    padding-inline: 0.65rem;
    font-size: 0.8rem;
  }

  .goal-details,
  .goal-overdue-label {
    margin-left: 1.875rem;
  }
}
</style>