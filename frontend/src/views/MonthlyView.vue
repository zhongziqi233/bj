<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <h1 class="page-title">月度日志</h1>
        <p class="page-subtitle">左边日历安排具体日期，右边任务列表收纳这个月要做的事。</p>
      </div>
      <el-date-picker
        v-model="selectedMonth"
        type="month"
        value-format="YYYY-MM"
        :clearable="false"
        class="month-picker"
      />
    </div>

    <div class="monthly-layout">
      <el-card class="surface-card calendar-card" shadow="never">
        <el-calendar v-model="calendarDate">
          <template #date-cell="{ data }">
            <div class="calendar-cell" @click="openDaily(data.day)">
              <span>{{ Number(data.day.slice(-2)) }}</span>
              <span v-if="countForDay(data.day)" class="calendar-count">
                {{ countForDay(data.day) }}
              </span>
            </div>
          </template>
        </el-calendar>
      </el-card>

      <el-card class="surface-card monthly-tasks-card" shadow="never">
        <template #header>
          <div class="card-header">
            <span>本月任务</span>
            <el-tag type="info" effect="plain" round>{{ monthlyTasks.length }} 条</el-tag>
          </div>
        </template>
        <div v-if="!monthlyTasks.length" class="empty-hint compact">
          暂无未指定日期的月度任务
        </div>
        <div v-else class="monthly-task-list">
          <div v-for="entry in monthlyTasks" :key="entry.id" class="monthly-task-item">
            <BulletMark
              :kind="entry.kind"
              :status="entry.status"
              :size="18"
              class="entry-marker"
            />
            <span class="monthly-task-content">{{ entry.content }}</span>
          </div>
        </div>
      </el-card>
    </div>

    <EntryComposer
      log-type="monthly"
      :period-date="monthStart"
      allow-date
      placeholder="添加月度任务，也可以指定一个日期"
      @created="loadEntries"
    />

    <EntryList :entries="entries" :loading="loading" show-date @refresh="loadEntries" />
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { ElMessage } from 'element-plus'

import BulletMark from '@/components/BulletMark.vue'
import EntryComposer from '@/components/EntryComposer.vue'
import EntryList from '@/components/EntryList.vue'
import { listEntries } from '@/api/entries'
import { getApiError } from '@/api/http'
import { currentMonth } from '@/utils/date'
import { useRouter } from 'vue-router'

const router = useRouter()
const selectedMonth = ref(currentMonth())
const calendarDate = ref(dayjs().toDate())
const entries = ref([])
const loading = ref(false)

const monthStart = computed(() => `${selectedMonth.value}-01`)
const monthlyTasks = computed(() => entries.value.filter((entry) => !entry.entry_date))

function countForDay(day) {
  return entries.value.filter((entry) => entry.entry_date === day).length
}

function openDaily(day) {
  router.push({ name: 'today', query: { date: day } })
}

async function loadEntries() {
  loading.value = true
  try {
    const { data } = await listEntries({
      log_type: 'monthly',
      month: selectedMonth.value,
    })
    entries.value = data.items
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    loading.value = false
  }
}

watch(selectedMonth, (value) => {
  calendarDate.value = dayjs(`${value}-01`).toDate()
  loadEntries()
})

onMounted(() => {
  calendarDate.value = dayjs(`${selectedMonth.value}-01`).toDate()
  loadEntries()
})
</script>

<style scoped>
.month-picker {
  width: 160px;
}

.monthly-layout {
  display: grid;
  grid-template-columns: minmax(0, 1.4fr) minmax(280px, 0.6fr);
  gap: 16px;
}

.calendar-card,
.monthly-tasks-card {
  padding: 4px;
}

.calendar-card :deep(.el-calendar) {
  --el-calendar-border: transparent;
}

.calendar-cell {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  width: 100%;
  height: 100%;
  padding: 3px;
  border-radius: 8px;
}

.calendar-cell:hover {
  background: rgba(97, 175, 239, 0.14);
  box-shadow: 0 0 18px rgba(97, 175, 239, 0.12);
}

.calendar-count {
  display: grid;
  min-width: 18px;
  height: 18px;
  padding: 0 4px;
  place-items: center;
  border-radius: 99px;
  background: linear-gradient(135deg, var(--od-blue), var(--od-purple));
  color: #1b1f24;
  box-shadow: 0 0 18px rgba(97, 175, 239, 0.26);
  font-size: 11px;
  font-weight: 800;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-weight: 700;
}

.compact {
  padding: 16px 8px;
}

.monthly-task-list {
  display: flex;
  flex-direction: column;
}

.monthly-task-item {
  display: flex;
  gap: 9px;
  padding: 10px 4px;
  border-bottom: 1px solid var(--od-border);
  transition:
    background-color 0.2s ease,
    box-shadow 0.2s ease;
}

.monthly-task-item:hover {
  background: rgba(97, 175, 239, 0.06);
  box-shadow: inset 3px 0 0 0 rgba(97, 175, 239, 0.62);
}

.monthly-task-item:last-child {
  border-bottom: 0;
}

.entry-marker {
  flex: none;
}

.monthly-task-content {
  min-width: 0;
  line-height: 1.55;
  word-break: break-word;
}

@media (max-width: 980px) {
  .monthly-layout {
    grid-template-columns: 1fr;
  }
}
</style>
