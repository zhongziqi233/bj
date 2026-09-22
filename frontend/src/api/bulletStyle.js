import http from './http'

export function getBulletStyle() {
  return http.get('/bullet-style')
}

export function updateBulletStyle(config) {
  return http.put('/bullet-style', { config })
}

export function resetBulletStyle() {
  return http.delete('/bullet-style')
}

