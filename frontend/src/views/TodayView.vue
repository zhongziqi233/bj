<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <h1 class="page-title">每日日志</h1>
        <p class="page-subtitle">把今天要做的事、发生的事和想法快速记下来。</p>
      </div>
      <div class="date-tools">
        <el-button :icon="ArrowLeft" circle @click="shiftDay(-1)" />
        <el-date-picker
          v-model="selectedDate"
          type="date"
          value-format="YYYY-MM-DD"
          :clearable="false"
          class="date-picker"
        />
        <el-button :icon="ArrowRight" circle @click="shiftDay(1)" />
        <el-button @click="selectedDate = today()">回到今天</el-button>
      </div>
    </div>

    <EntryComposer
      log-type="daily"
      :entry-date="selectedDate"
      placeholder="今天要做什么？"
      @created="loadEntries"
    />

    <div class="summary-strip">
      <el-statistic title="全部记录" :value="entries.length" />
      <el-statistic title="待办任务" :value="pendingCount" />
      <el-statistic title="已完成" :value="completedCount" />
    </div>

    <EntryList :entries="entries" :loading="loading" @refresh="loadEntries" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'
import { ArrowLeft, ArrowRight } from '@element-plus/icons-vue'
import { useRoute } from 'vue-router'

import EntryComposer from '@/components/EntryComposer.vue'
import EntryList from '@/components/EntryList.vue'
import { listEntries } from '@/api/entries'
import { getApiError } from '@/api/http'
import { today } from '@/utils/date'

const selectedDate = ref(today())
const entries = ref([])
const loading = ref(false)
const route = useRoute()

const pendingCount = computed(
  () => entries.value.filter((entry) => entry.kind === 'task' && entry.status === 'open').length,
)
const completedCount = computed(
  () => entries.value.filter((entry) => entry.kind === 'task' && entry.status === 'completed').length,
)

async function loadEntries() {
  loading.value = true
  try {
    const { data } = await listEntries({
      log_type: 'daily',
      date: selectedDate.value,
    })
    entries.value = data.items
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    loading.value = false
  }
}

function shiftDay(days) {
  selectedDate.value = dayjs(selectedDate.value).add(days, 'day').format('YYYY-MM-DD')
}

watch(selectedDate, loadEntries)
onMounted(() => {
  if (route.query.date) {
    selectedDate.value = String(route.query.date)
  }
  loadEntries()
})
</script>

<style scoped>
.date-tools {
  display: flex;
  align-items: center;
  gap: 8px;
}

.date-picker {
  width: 160px;
}

.summary-strip {
  position: relative;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 12px;
  overflow: hidden;
  padding: 18px 20px;
  border: 1px solid var(--od-border);
  border-radius: 18px;
  background: linear-gradient(135deg, rgba(40, 44, 52, 0.92), rgba(33, 37, 43, 0.82));
  box-shadow: 0 16px 42px rgba(0, 0, 0, 0.24);
  backdrop-filter: blur(14px);
  animation: cardIn 0.55s cubic-bezier(0.2, 0.8, 0.2, 1) both;
}

.summary-strip::after {
  position: absolute;
  right: 0;
  bottom: 0;
  left: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--od-blue), var(--od-purple), var(--od-cyan));
  opacity: 0.85;
  content: "";
}

.summary-strip :deep(.el-statistic__number) {
  color: var(--od-text-strong);
  font-weight: 750;
}

.summary-strip :deep(.el-statistic:nth-child(1) .el-statistic__number) {
  color: var(--od-blue);
  text-shadow: 0 0 18px rgba(97, 175, 239, 0.28);
}

.summary-strip :deep(.el-statistic:nth-child(2) .el-statistic__number) {
  color: var(--od-yellow);
  text-shadow: 0 0 18px rgba(229, 192, 123, 0.22);
}

.summary-strip :deep(.el-statistic:nth-child(3) .el-statistic__number) {
  color: var(--od-green);
  text-shadow: 0 0 18px rgba(152, 195, 121, 0.22);
}

@media (max-width: 680px) {
  .date-tools {
    width: 100%;
    flex-wrap: wrap;
  }

  .date-picker {
    flex: 1;
    min-width: 150px;
  }

  .summary-strip {
    grid-template-columns: 1fr;
  }
}
</style>
