<template>
  <div class="stack">
    <header class="page-heading">
      <div>
        <p class="eyebrow">Platform overview</p>
        <h1>Administration.</h1>
        <p>Review people, create thoughtful matches, and understand the experience.</p>
      </div>
      <button class="secondary" :disabled="loading || busy" @click="load">Refresh data</button>
    </header>

    <p v-if="error" class="error" role="alert">{{ error }}</p>
    <p v-if="notice" class="notice" role="status">{{ notice }}</p>
    <p v-if="loading" role="status">Loading platform data…</p>

    <section class="metrics" aria-label="Platform metrics">
      <div v-for="metric in metricCards" :key="metric.key" class="card metric">
        <span>{{ metric.title }}</span>
        <strong>{{ metrics[metric.key] ?? '—' }}</strong>
      </div>
    </section>

    <div class="filters" role="group" aria-label="Administration sections">
      <button
        v-for="item in sections"
        :key="item.id"
        :aria-pressed="section === item.id"
        :aria-controls="`admin-${item.id}`"
        @click="section = item.id"
      >
        {{ item.title }}
      </button>
    </div>

    <section v-if="section === 'students'" id="admin-students" class="card stack" aria-labelledby="students-heading">
      <h2 id="students-heading">Student profiles</h2>
      <div class="field">
        <label for="student-search">Search students</label>
        <input id="student-search" v-model="search" type="search" placeholder="Name or email" />
      </div>

      <p v-if="!filteredStudents.length" class="empty">No student profiles found.</p>

      <div v-else class="table-wrap" role="region" aria-label="Student profiles table" tabindex="0">
        <table>
          <caption class="sr-only">Students and profile review actions</caption>
          <thead>
            <tr><th scope="col">Student</th><th scope="col">Goals and background</th><th scope="col">Status</th><th scope="col">Review</th></tr>
          </thead>
          <tbody>
            <tr v-for="student in filteredStudents" :key="student.id">
              <td>{{ student.full_name }}<br /><small>{{ student.email }}</small></td>
              <td>
                {{ goalLabel(student.goal) }}
                <details>
                  <summary>View profile</summary>
                  <dl>
                    <dt>University</dt><dd>{{ student.university || 'Not provided' }}</dd>
                    <dt>Desired role</dt><dd>{{ student.desired_job_title || 'Not applicable' }}</dd>
                    <dt>Country</dt><dd>{{ student.target_country || 'Not provided' }}</dd>
                    <dt>Degree</dt><dd>{{ student.target_degree || 'Not applicable' }}</dd>
                    <dt>Field</dt><dd>{{ student.field_of_interest || 'Not provided' }}</dd>
                    <dt>Questions</dt><dd>{{ student.questions || 'None provided' }}</dd>
                  </dl>
                </details>
              </td>
              <td><span class="badge" :class="student.status">{{ student.status }}</span></td>
              <td>
                <div v-if="student.status === 'pending'" class="actions">
                  <button class="small" :disabled="busy" @click="review('students', student, 'approved')">Approve</button>
                  <button class="danger small" :disabled="busy" @click="review('students', student, 'rejected')">Reject</button>
                </div>
                <span v-else class="muted">Reviewed</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="section === 'mentors'" id="admin-mentors" class="card stack" aria-labelledby="mentors-heading">
      <h2 id="mentors-heading">Mentor profiles</h2>
      <div class="field">
        <label for="mentor-search">Search mentors</label>
        <input id="mentor-search" v-model="search" type="search" placeholder="Name, email, or expertise" />
      </div>

      <p v-if="!filteredMentors.length" class="empty">No mentor profiles found.</p>

      <div v-else class="table-wrap" role="region" aria-label="Mentor profiles table" tabindex="0">
        <table>
          <caption class="sr-only">Mentors and profile review actions</caption>
          <thead>
            <tr><th scope="col">Mentor</th><th scope="col">Background</th><th scope="col">Status</th><th scope="col">Review</th></tr>
          </thead>
          <tbody>
            <tr v-for="mentor in filteredMentors" :key="mentor.id">
              <td>{{ mentor.full_name }}<br /><small>{{ mentor.email }}</small></td>
              <td>
                {{ mentor.expertise }}
                <details>
                  <summary>View profile</summary>
                  <dl>
                    <dt>Current situation</dt><dd>{{ label(mentor.current_status) }}</dd>
                    <dt>University</dt><dd>{{ mentor.university || 'Not provided' }}</dd>
                    <dt>Country</dt><dd>{{ mentor.country || 'Not provided' }}</dd>
                    <dt>Degree</dt><dd>{{ mentor.degree || 'Not provided' }}</dd>
                    <dt>Role and company</dt><dd>{{ mentor.job_title || 'Not applicable' }} {{ mentor.company ? `at ${mentor.company}` : '' }}</dd>
                    <dt>Introduction</dt><dd>{{ mentor.bio || 'Not provided' }}</dd>
                    <dt>New mentees</dt><dd>{{ mentor.available ? 'Available' : 'Unavailable' }}</dd>
                  </dl>
                </details>
              </td>
              <td><span class="badge" :class="mentor.status">{{ mentor.status }}</span></td>
              <td>
                <div v-if="mentor.status === 'pending'" class="actions">
                  <button class="small" :disabled="busy" @click="review('mentors', mentor, 'approved')">Approve</button>
                  <button class="danger small" :disabled="busy" @click="review('mentors', mentor, 'rejected')">Reject</button>
                </div>
                <span v-else class="muted">Reviewed</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section v-if="section === 'matching'" id="admin-matching" class="stack" aria-labelledby="matching-heading">
      <div class="card">
        <h2 id="matching-heading">Match students</h2>
        <p class="muted">
          Only approved students who have never been matched appear here.
          Recommendations include approved, available mentors without an active mentee.
        </p>
        <div class="field">
          <label for="match-student">Select a student</label>
          <select id="match-student" v-model="selectedStudent">
            <option value="">Choose a student</option>
            <option v-for="student in unmatched" :key="student.user_id" :value="student.user_id">
              {{ student.full_name }} — {{ student.field_of_interest || goalLabel(student.goal) }}
            </option>
          </select>
        </div>
        <p v-if="!unmatched.length && !loading" class="empty">No students awaiting a first match.</p>
      </div>

      <template v-if="selected">
        <section class="card">
          <h3>{{ selected.full_name }}</h3>
          <p>{{ goalLabel(selected.goal) }} · {{ selected.target_country || 'Country not specified' }}</p>
          <p class="muted">{{ selected.questions || 'No mentoring questions provided.' }}</p>
        </section>

        <section aria-labelledby="recommended-heading" class="stack">
          <h2 id="recommended-heading">Top recommendations</h2>
          <p v-if="!selected.recommendations.top_recommendations.length" class="card empty">No eligible mentors available.</p>

          <article
            v-for="rec in selected.recommendations.top_recommendations"
            :key="rec.mentor_user_id"
            class="card"
          >
            <div class="section-top">
              <h3>{{ rec.mentor.full_name }}</h3>
              <span class="badge">Match score {{ rec.score }}</span>
            </div>
            <p>{{ rec.mentor.expertise }}</p>
            <p class="hint">{{ rec.mentor.country }} · {{ rec.mentor.job_title || rec.mentor.degree }}</p>
            <ul v-if="rec.reasons.length">
              <li v-for="reason in rec.reasons" :key="reason">{{ reason }}</li>
            </ul>
            <p v-else class="hint">No specific matching signals found.</p>
            <button :disabled="busy" @click="assign(rec)">Assign mentor</button>
          </article>
        </section>

        <section v-if="selected.recommendations.other_available_mentors.length" class="stack" aria-labelledby="other-heading">
          <h2 id="other-heading">Other available mentors</h2>
          <article v-for="rec in selected.recommendations.other_available_mentors" :key="rec.mentor_user_id" class="card">
            <h3>{{ rec.mentor.full_name }}</h3>
            <p>{{ rec.mentor.expertise }}</p>
            <p class="hint">Match score {{ rec.score }} · {{ rec.mentor.country }}</p>
            <button class="secondary" :disabled="busy" @click="assign(rec)">Assign mentor</button>
          </article>
        </section>
      </template>
    </section>

    <section v-if="section === 'feedback'" id="admin-feedback" class="card stack" aria-labelledby="admin-feedback-heading">
      <h2 id="admin-feedback-heading">Mentorship feedback</h2>
      <p v-if="!feedback.length" class="empty">No feedback submitted yet.</p>
      <article v-for="item in feedback" :key="item.id" class="item">
        <div class="section-top">
          <h3>{{ item.user_email }}</h3>
          <span class="badge">{{ item.rating }} / 5</span>
        </div>
        <p class="hint">{{ label(item.user_role) }} · Mentorship #{{ item.match_id }} · {{ dateTime(item.created_at) }}</p>
        <p>{{ item.comments || 'No comments provided.' }}</p>
      </article>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api'
import { errorText, dateTime, label } from '../utils'

const sections = [
  { id: 'students', title: 'Students' },
  { id: 'mentors', title: 'Mentors' },
  { id: 'matching', title: 'Match students' },
  { id: 'feedback', title: 'Feedback' }
]
const metricCards = [
  { key: 'total_students', title: 'Registered students' },
  { key: 'total_mentors', title: 'Registered mentors' },
  { key: 'pending_students', title: 'Students awaiting review' },
  { key: 'pending_mentors', title: 'Mentors awaiting review' },
  { key: 'active_matches', title: 'Active mentorships' },
  { key: 'ended_matches', title: 'Ended mentorships' },
  { key: 'feedback_count', title: 'Feedback submissions' }
]

const section = ref('students')
const metrics = ref({})
const students = ref([])
const mentors = ref([])
const feedback = ref([])
const unmatched = ref([])
const selectedStudent = ref('')
const search = ref('')
const loading = ref(false)
const busy = ref(false)
const error = ref('')
const notice = ref('')

watch(section, () => { search.value = '' })

const filteredStudents = computed(() => students.value.filter(item =>
  `${item.full_name} ${item.email}`.toLowerCase().includes(search.value.toLowerCase())
))
const filteredMentors = computed(() => mentors.value.filter(item =>
  `${item.full_name} ${item.email} ${item.expertise}`.toLowerCase().includes(search.value.toLowerCase())
))
const selected = computed(() => unmatched.value.find(item => item.user_id === Number(selectedStudent.value)))

function goalLabel(goal) {
  return { job: 'Career guidance', masters: "Master's guidance", both: 'Career and study guidance' }[goal] || goal
}

async function load() {
  if (loading.value) return
  loading.value = true
  error.value = ''
  try {
    const [m, s, t, f] = await Promise.all([
      api.get('/admin/metrics'),
      api.get('/admin/students'),
      api.get('/admin/mentors'),
      api.get('/admin/feedback')
    ])
    metrics.value = m.data
    students.value = s.data.students
    mentors.value = t.data.mentors
    feedback.value = f.data.feedback

    const candidates = await Promise.all(
      students.value.filter(item => item.status === 'approved').map(async student => {
        try {
          const { data } = await api.get(`/matching/recommendations/${student.user_id}`)
          return { ...student, recommendations: data }
        } catch (err) {
          if (err.response?.status === 409) return null
          throw err
        }
      })
    )
    unmatched.value = candidates.filter(Boolean)
    if (!unmatched.value.some(item => item.user_id === Number(selectedStudent.value))) {
      selectedStudent.value = ''
    }
  } catch (err) {
    error.value = errorText(err)
  } finally {
    loading.value = false
  }
}

async function review(type, person, decision) {
  if (!window.confirm(`${decision === 'approved' ? 'Approve' : 'Reject'} ${person.full_name}'s profile?`)) return
  busy.value = true
  error.value = ''
  try {
    await api.post(`/admin/${type}/${person.id}/decision`, { decision })
    notice.value = `${person.full_name}'s profile was ${decision}.`
    await load()
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}

async function assign(rec) {
  if (!selected.value) return
  const student = selected.value
  if (!window.confirm(`Assign ${rec.mentor.full_name} to ${student.full_name}?`)) return

  busy.value = true
  error.value = ''
  try {
    await api.post('/matching/assign', {
      student_id: student.user_id,
      mentor_id: rec.mentor_user_id
    })
    notice.value = `${student.full_name} was matched with ${rec.mentor.full_name}.`
    selectedStudent.value = ''
    await load()
  } catch (err) {
    error.value = errorText(err)
  } finally {
    busy.value = false
  }
}

onMounted(load)
</script>