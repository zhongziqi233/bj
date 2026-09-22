<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <el-button text :icon="ArrowLeft" class="back-button" @click="router.push('/collections')">
          返回集合
        </el-button>
        <h1 class="page-title">{{ collection?.name || '集合详情' }}</h1>
        <p class="page-subtitle">{{ collection?.description || '暂无描述' }}</p>
      </div>
      <div v-if="collection" class="collection-summary">
        <el-tag effect="plain" round>{{ collection.entry_count }} 条记录</el-tag>
      </div>
    </div>

    <template v-if="collection">
      <EntryComposer
        log-type="collection"
        :collection-id="collection.id"
        :placeholder="`添加到“${collection.name}”`"
        @created="loadCollection"
      />
      <EntryList :entries="collection.entries || []" :loading="loading" @refresh="loadCollection" />
    </template>
    <el-skeleton v-else :rows="6" animated />
  </div>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { ArrowLeft } from '@element-plus/icons-vue'

import EntryComposer from '@/components/EntryComposer.vue'
import EntryList from '@/components/EntryList.vue'
import { getCollection } from '@/api/collections'
import { getApiError } from '@/api/http'

const route = useRoute()
const router = useRouter()
const collection = ref(null)
const loading = ref(false)

async function loadCollection() {
  loading.value = true
  try {
    const { data } = await getCollection(route.params.id)
    collection.value = data.collection
  } catch (error) {
    ElMessage.error(getApiError(error))
    router.replace('/collections')
  } finally {
    loading.value = false
  }
}

onMounted(loadCollection)
</script>

<style scoped>
.back-button {
  margin-bottom: 10px;
  padding-left: 0;
  color: var(--od-blue);
}

.back-button:hover {
  color: var(--od-cyan);
  text-shadow: 0 0 16px rgba(86, 182, 194, 0.38);
}

.collection-summary {
  padding-top: 4px;
}
</style>
