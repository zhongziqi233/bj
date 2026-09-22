import { computed, ref } from 'vue'
import { defineStore } from 'pinia'

import * as authApi from '@/api/auth'

const TOKEN_KEY = 'bullet-journal-token'
const USER_KEY = 'bullet-journal-user'

function readStoredUser() {
  try {
    return JSON.parse(localStorage.getItem(USER_KEY) || 'null')
  } catch {
    return null
  }
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(TOKEN_KEY) || '')
  const user = ref(readStoredUser())
  const ready = ref(false)

  const isAuthenticated = computed(() => Boolean(token.value))
  const isAdmin = computed(() => Boolean(user.value?.is_admin))

  function persist() {
    if (token.value) {
      localStorage.setItem(TOKEN_KEY, token.value)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
    if (user.value) {
      localStorage.setItem(USER_KEY, JSON.stringify(user.value))
    } else {
      localStorage.removeItem(USER_KEY)
    }
  }

  function setSession(payload) {
    token.value = payload.access_token
    user.value = payload.user
    ready.value = true
    persist()
  }

  async function login(payload) {
    const { data } = await authApi.login(payload)
    setSession(data)
    return data
  }

  async function register(payload) {
    const { data } = await authApi.register(payload)
    setSession(data)
    return data
  }

  async function fetchMe() {
    if (!token.value) {
      ready.value = true
      return null
    }
    const { data } = await authApi.getMe()
    user.value = data.user
    ready.value = true
    persist()
    return data.user
  }

  async function ensureReady() {
    if (ready.value) return
    try {
      await fetchMe()
    } catch {
      logout()
    }
  }

  function logout() {
    token.value = ''
    user.value = null
    ready.value = true
    persist()
  }

  function updateProfile(nextUser) {
    user.value = nextUser
    persist()
  }

  return {
    token,
    user,
    ready,
    isAuthenticated,
    isAdmin,
    login,
    register,
    fetchMe,
    ensureReady,
    logout,
    updateProfile,
  }
})

