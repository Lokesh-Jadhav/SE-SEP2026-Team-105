export function errorText(error) {
  return error.response?.data?.error ||
    error.response?.data?.message ||
    'Something went wrong. Please try again.'
}

export function dateTime(value) {
  if (!value) return 'Not specified'

  // SQLite-backed API timestamps may omit the UTC suffix.
  const normalized = /(?:Z|[+-]\d{2}:\d{2})$/i.test(value)
    ? value
    : `${value}Z`

  const date = new Date(normalized)

  return Number.isNaN(date.getTime())
    ? 'Invalid date'
    : date.toLocaleString([], {
        dateStyle: 'medium',
        timeStyle: 'short'
      })
}

export function dateOnly(value) {
  if (!value) return 'No due date'
  return new Date(`${value}T12:00:00`).toLocaleDateString([], {
    dateStyle: 'medium'
  })
}

export function label(value) {
  return String(value || '').replaceAll('_', ' ')
}

export function emptyProfile() {
  return {
    full_name: '',
    university: '',
    goal: 'job',
    desired_job_title: '',
    target_country: '',
    target_degree: '',
    field_of_interest: '',
    questions: '',
    current_status: 'working',
    country: '',
    degree: '',
    job_title: '',
    company: '',
    expertise: '',
    bio: ''
  }
}

export function profilePayload(role, form) {
  if (role === 'student') {
    const job = ['job', 'both'].includes(form.goal)
    const study = ['masters', 'both'].includes(form.goal)

    return {
      full_name: form.full_name.trim(),
      university: form.university.trim(),
      goal: form.goal,
      desired_job_title: job ? form.desired_job_title.trim() : '',
      target_country: form.target_country.trim(),
      target_degree: study ? form.target_degree.trim() : '',
      field_of_interest: form.field_of_interest.trim(),
      questions: form.questions.trim()
    }
  }

  const working = form.current_status === 'working'

  return {
    full_name: form.full_name.trim(),
    current_status: form.current_status,
    university: form.university.trim(),
    country: form.country.trim(),
    degree: form.degree.trim(),
    job_title: working ? form.job_title.trim() : '',
    company: working ? form.company.trim() : '',
    expertise: form.expertise.trim(),
    bio: form.bio.trim()
  }
}