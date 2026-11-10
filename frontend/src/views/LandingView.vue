<template>
  <section class="hero">
    <p class="eyebrow">Guidance for what comes next</p>
    <h1>A clearer path starts with a conversation.</h1>
    <p>
      Connect with a mentor who understands your goals.
      Get practical guidance for your career, postgraduate studies,
      and the decisions in between.
    </p>
    <div class="actions">
      <RouterLink class="button" :to="auth.isLoggedIn ? auth.dashboard : '/register'">
        {{ auth.isLoggedIn ? 'Open dashboard' : 'Find your next step' }}
      </RouterLink>
      <RouterLink v-if="!auth.isLoggedIn" to="/register?role=mentor">
        Become a mentor
      </RouterLink>
    </div>
  </section>

  <section aria-labelledby="how-title">
    <div class="page-heading">
      <div>
        <p class="eyebrow">Simple by design</p>
        <h2 id="how-title">More guidance. Less guesswork.</h2>
      </div>
    </div>

    <div class="grid">
      <article v-for="step in steps" :key="step.title" class="card">
        <p class="step-number">{{ step.number }}</p>
        <h3>{{ step.title }}</h3>
        <p class="muted">{{ step.text }}</p>
      </article>
    </div>
  </section>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'
const auth = useAuthStore()

const steps = [
  { number: '01', title: 'Tell us your goals', text: 'Create a profile focused on the support you need.' },
  { number: '02', title: 'Meet your mentor', text: 'An administrator reviews profiles and connects you with a suitable mentor.' },
  { number: '03', title: 'Make steady progress', text: 'Chat, arrange meetings, and work through goals together.' }
]
</script>