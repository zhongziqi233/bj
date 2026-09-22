import http from './http'

export function listEntries(params) {
  return http.get('/entries', { params })
}

export function createEntry(payload) {
  return http.post('/entries', payload)
}

export function updateEntry(id, payload) {
  return http.patch(`/entries/${id}`, payload)
}

export function deleteEntry(id) {
  return http.delete(`/entries/${id}`)
}

export function migrateEntry(id, targetDate) {
  return http.post(`/entries/${id}/migrate`, { target_date: targetDate })
}

export function postponeEntry(id) {
  return http.post(`/entries/${id}/postpone`)
}

export function scheduleEntry(id, targetDate) {
  return http.post(`/entries/${id}/schedule`, { target_date: targetDate })
}
