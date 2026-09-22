import http from './http'

export function listCollections() {
  return http.get('/collections')
}

export function getCollection(id) {
  return http.get(`/collections/${id}`)
}

export function createCollection(payload) {
  return http.post('/collections', payload)
}

export function updateCollection(id, payload) {
  return http.patch(`/collections/${id}`, payload)
}

export function deleteCollection(id) {
  return http.delete(`/collections/${id}`)
}

