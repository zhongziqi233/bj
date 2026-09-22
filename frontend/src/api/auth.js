import http from './http'

export function register(payload) {
  return http.post('/auth/register', payload)
}

export function login(payload) {
  return http.post('/auth/login', payload)
}

export function getMe() {
  return http.get('/auth/me')
}

export function changePassword(payload) {
  return http.put('/auth/password', payload)
}

