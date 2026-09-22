import http from './http'

export function listUsers(params) {
  return http.get('/users', { params })
}

export function updateUser(id, payload) {
  return http.patch(`/users/${id}`, payload)
}

export function resetUserPassword(id, newPassword) {
  return http.post(`/users/${id}/reset-password`, { new_password: newPassword })
}

export function deleteUser(id) {
  return http.delete(`/users/${id}`)
}

