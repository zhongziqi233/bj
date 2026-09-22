import { ref } from 'vue'
import { defineStore } from 'pinia'

import * as bulletStyleApi from '@/api/bulletStyle'
import { cloneBulletConfig, DEFAULT_BULLET_CONFIG } from '@/utils/bulletDefaults'

export const useBulletStyleStore = defineStore('bulletStyle', () => {
  const config = ref(cloneBulletConfig(DEFAULT_BULLET_CONFIG))
  const isCustom = ref(false)
  const loaded = ref(false)
  const loading = ref(false)

  function markFor(kind, status = 'open') {
    const kindConfig = config.value[kind] || DEFAULT_BULLET_CONFIG[kind]
    if (status && status !== 'open' && kindConfig?.statuses?.[status]?.layers?.length) {
      return kindConfig.statuses[status]
    }
    return kindConfig
  }

  async function load(force = false) {
    if (loaded.value && !force) {
      return config.value
    }
    loading.value = true
    try {
      const { data } = await bulletStyleApi.getBulletStyle()
      config.value = data.config
      isCustom.value = data.is_custom
      loaded.value = true
      return config.value
    } finally {
      loading.value = false
    }
  }

  async function save(nextConfig) {
    const { data } = await bulletStyleApi.updateBulletStyle(nextConfig)
    config.value = data.config
    isCustom.value = data.is_custom
    loaded.value = true
    return data.config
  }

  async function reset() {
    const { data } = await bulletStyleApi.resetBulletStyle()
    config.value = data.config
    isCustom.value = data.is_custom
    loaded.value = true
    return data.config
  }

  return {
    config,
    isCustom,
    loaded,
    loading,
    markFor,
    load,
    save,
    reset,
  }
})
