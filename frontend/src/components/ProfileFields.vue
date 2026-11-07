<template>
  <fieldset>
    <legend>{{ role === 'student' ? 'Your goals and background' : 'Your mentoring background' }}</legend>

    <div class="form-grid">
      <div class="field">
        <label :for="`${prefix}-name`">Full name</label>
        <input :id="`${prefix}-name`" v-model="model.full_name" required maxlength="150" autocomplete="name" />
      </div>

      <div class="field">
        <label :for="`${prefix}-university`">
          {{ role === 'student' ? 'Current or previous university' : 'University' }}
          <span v-if="role === 'student'" class="muted">(optional)</span>
        </label>
        <input :id="`${prefix}-university`" v-model="model.university" maxlength="200" />
      </div>

      <template v-if="role === 'student'">
        <div class="field full">
          <label :for="`${prefix}-goal`">What would you like help with?</label>
          <select :id="`${prefix}-goal`" v-model="model.goal">
            <option value="job">Finding a job</option>
            <option value="masters">Studying abroad for a master's</option>
            <option value="both">Both career and master's guidance</option>
          </select>
          <p class="hint" aria-live="polite">
            {{ model.goal === 'job'
              ? 'Tell us about the role you want.'
              : model.goal === 'masters'
                ? 'Tell us where and what you want to study.'
                : 'Tell us about both your career and study plans.' }}
          </p>
        </div>

        <div v-if="jobGoal" class="field">
          <label :for="`${prefix}-job`">Desired job title</label>
          <input :id="`${prefix}-job`" v-model="model.desired_job_title" required maxlength="200" placeholder="e.g. Software Engineer" />
        </div>

        <div class="field">
          <label :for="`${prefix}-country`">
            {{ studyGoal ? 'Target study country' : 'Preferred work country' }}
          </label>
          <input :id="`${prefix}-country`" v-model="model.target_country" required maxlength="100" placeholder="e.g. Canada" />
          <p v-if="model.goal === 'both'" class="hint">
            Used as your primary target country for matching.
          </p>
        </div>

        <div v-if="studyGoal" class="field">
          <label :for="`${prefix}-degree`">Desired master's program</label>
          <input :id="`${prefix}-degree`" v-model="model.target_degree" required maxlength="200" placeholder="e.g. MSc Computer Science" />
        </div>

        <div class="field">
          <label :for="`${prefix}-field`">Field of interest</label>
          <input :id="`${prefix}-field`" v-model="model.field_of_interest" required maxlength="200" placeholder="e.g. Machine Learning" />
        </div>

        <div class="field full">
          <label :for="`${prefix}-questions`">What would you like to ask your mentor? (optional)</label>
          <textarea :id="`${prefix}-questions`" v-model="model.questions" maxlength="4000" />
        </div>
      </template>

      <template v-else>
        <div class="field full">
          <label :for="`${prefix}-status`">Your current situation</label>
          <select :id="`${prefix}-status`" v-model="model.current_status">
            <option value="working">Working professionally</option>
            <option value="studying_abroad">Studying abroad</option>
          </select>
        </div>

        <div class="field">
          <label :for="`${prefix}-country`">Current country</label>
          <input :id="`${prefix}-country`" v-model="model.country" required maxlength="100" />
        </div>

        <div class="field">
          <label :for="`${prefix}-degree`">
            {{ model.current_status === 'working' ? 'Highest qualification' : 'Current degree or program' }}
          </label>
          <input :id="`${prefix}-degree`" v-model="model.degree" required maxlength="200" />
        </div>

        <template v-if="model.current_status === 'working'">
          <div class="field">
            <label :for="`${prefix}-job`">Current job title</label>
            <input :id="`${prefix}-job`" v-model="model.job_title" required maxlength="200" />
          </div>
          <div class="field">
            <label :for="`${prefix}-company`">Company or organization</label>
            <input :id="`${prefix}-company`" v-model="model.company" required maxlength="200" />
          </div>
        </template>

        <div class="field full">
          <label :for="`${prefix}-expertise`">Areas of expertise</label>
          <input :id="`${prefix}-expertise`" v-model="model.expertise" required maxlength="500" :aria-describedby="`${prefix}-expertise-help`" />
          <p :id="`${prefix}-expertise-help`" class="hint">
            Separate areas with commas, such as Software Engineering, Interviews, Graduate Applications.
          </p>
        </div>

        <div class="field full">
          <label :for="`${prefix}-bio`">Short introduction (optional)</label>
          <textarea :id="`${prefix}-bio`" v-model="model.bio" maxlength="4000" />
        </div>
      </template>
    </div>
  </fieldset>
</template>

<script setup>
import { computed } from 'vue'

const model = defineModel({ required: true })
defineProps({
  role: { type: String, required: true },
  prefix: { type: String, default: 'profile' }
})

const jobGoal = computed(() => ['job', 'both'].includes(model.value.goal))
const studyGoal = computed(() => ['masters', 'both'].includes(model.value.goal))
</script>