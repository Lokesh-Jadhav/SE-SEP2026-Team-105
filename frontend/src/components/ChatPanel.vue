<template>
  <section class="card stack" aria-labelledby="chat-heading">
    <div class="section-top">
      <h2 id="chat-heading">Conversation</h2>
      <span class="hint">With {{ otherName }}</span>
    </div>

    <p v-if="error" class="error" role="alert">{{ error }}</p>

    <div
      ref="box"
      class="chat-history"
      role="region"
      aria-label="Message history"
      tabindex="0"
    >
      <p v-if="!messages.length" class="empty">Start with a hello or a question.</p>

      <article
        v-for="message in messages"
        :key="message.id"
        class="bubble"
        :class="{ mine: message.sender_id === auth.user.id }"
        :aria-label="message.sender_id === auth.user.id ? 'Your message' : `Message from ${otherName}`"
      >
        <p>{{ message.body }}</p>
        <div class="message-meta">
          <time>{{ dateTime(message.created_at) }}</time>
          <span
            v-if="message.sender_id === auth.user.id"
            class="receipt"
            :class="{ read: status(message) === 'read' }"
            :aria-label="`Message ${status(message)}`"
            :title="status(message)"
          >
            <span aria-hidden="true">{{ status(message) === 'sent' ? '✓' : '✓✓' }}</span>
            <span class="sr-only">{{ status(message) }}</span>
          </span>
        </div>
      </article>
    </div>

    <p class="sr-only" role="status">{{ announcement }}</p>

    <form class="stack" @submit.prevent="send">
      <div class="field">
        <label for="message-draft">Your message</label>
        <textarea id="message-draft" v-model="draft" required maxlength="5000" rows="2" />
      </div>
      <div class="actions">
        <button :disabled="sending || !draft.trim()">{{ sending ? 'Sending…' : 'Send message' }}</button>
        <span class="hint">Messages refresh automatically.</span>
      </div>
    </form>
  </section>
</template>

<script setup>
import { ref, onMounted, onUnmounted, nextTick } from 'vue'
import api from '../api'
import { useAuthStore } from '../stores/auth'
import { dateTime, errorText } from '../utils'

const props = defineProps({
  matchId: { type: Number, required: true },
  otherName: { type: String, required: true }
})
const auth = useAuthStore()
const box = ref(null)
const messages = ref([])
const draft = ref('')
const error = ref('')
const announcement = ref('')
const sending = ref(false)
let timer
let loading = false
let disposed = false

function status(message) {
  return message.status || (
    message.read_at || message.read_by_recipient
      ? 'read'
      : message.delivered_at ? 'delivered' : 'sent'
  )
}

async function load() {
  if (loading || sending.value || document.hidden) return
  loading = true
  try {
    const nearBottom = !box.value ||
      box.value.scrollHeight - box.value.scrollTop - box.value.clientHeight < 90
    const previous = new Set(messages.value.map(message => message.id))
    const first = messages.value.length === 0
    const { data } = await api.get(`/chat/${props.matchId}`)
    if (disposed) return

    const incoming = data.messages.filter(
      message => !previous.has(message.id) && message.sender_id !== auth.user.id
    )
    messages.value = data.messages
    error.value = ''
    if (!first && incoming.length) announcement.value = `${incoming.length} new message${incoming.length > 1 ? 's' : ''}.`

    await nextTick()
    if (nearBottom && box.value) box.value.scrollTop = box.value.scrollHeight
  } catch (err) {
    if (!disposed) error.value = errorText(err)
  } finally {
    loading = false
  }
}

async function send() {
  if (!draft.value.trim() || sending.value) return
  sending.value = true
  error.value = ''
  try {
    await api.post(`/chat/${props.matchId}`, { body: draft.value.trim() })
    draft.value = ''
    announcement.value = 'Message sent.'
  } catch (err) {
    error.value = errorText(err)
  } finally {
    sending.value = false
  }
  await load()
  await nextTick()
  if (box.value) box.value.scrollTop = box.value.scrollHeight
}

onMounted(() => {
  load()
  timer = setInterval(load, 3000)
})
onUnmounted(() => {
  disposed = true
  clearInterval(timer)
})
</script>

<style scoped>
.chat-history {
  height: 360px;
  overflow-y: auto;
  padding: .75rem;
  background: #fafbf9;
  border: 1px solid var(--line);
  border-radius: 12px;
}
.bubble {
  width: fit-content;
  max-width: 88%;
  padding: .8rem 1rem;
  border: 1px solid var(--line);
  background: white;
  border-radius: 14px 14px 14px 3px;
  margin-bottom: .75rem;
  overflow-wrap: anywhere;
}
.bubble.mine {
  margin-left: auto;
  background: #eaf2eb;
  border-radius: 14px 14px 3px 14px;
}
.bubble p { white-space: pre-wrap; margin-bottom: .4rem; }
.message-meta { display: flex; justify-content: flex-end; gap: .6rem; font-size: .7rem; color: var(--muted); }
.receipt { color: #596961; font-weight: 800; }
.receipt.read { color: #175dcc; }
</style>