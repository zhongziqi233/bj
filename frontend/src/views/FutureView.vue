<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <h1 class="page-title">未来日志</h1>
        <p class="page-subtitle">把以后几个月才需要关注的事情放进对应月份，避免现在就被打断。</p>
      </div>
      <el-select v-model="selectedYear" class="year-select">
        <el-option v-for="year in yearOptions" :key="year" :label="`${year} 年`" :value="year" />
      </el-select>
    </div>

    <div class="month-grid">
      <button
        v-for="month in months"
        :key="month.value"
        class="surface-card month-card"
        :class="{ 'month-card-active': selectedMonth === month.value }"
        type="button"
        @click="selectedMonth = month.value"
      >
        <div class="month-card-header">
          <span class="month-card-title">{{ month.label }}</span>
          <el-tag size="small" effect="plain" round>{{ entriesForMonth(month.key).length }}</el-tag>
        </div>
        <div v-if="!entriesForMonth(month.key).length" class="month-empty">暂无安排</div>
        <div v-else class="month-entries">
          <div v-for="entry in entriesForMonth(month.key).slice(0, 3)" :key="entry.id" class="month-entry">
            <BulletMark
              :kind="entry.kind"
              :status="entry.status"
              :size="18"
              class="entry-marker"
            />
            <span class="month-entry-text">{{ entry.content }}</span>
          </div>
          <div v-if="entriesForMonth(month.key).length > 3" class="month-more">
            还有 {{ entriesForMonth(month.key).length - 3 }} 条
          </div>
        </div>
      </button>
    </div>

    <div class="selected-month-section">
      <h2>{{ selectedMonth }} 月详情</h2>
      <EntryComposer
        log-type="future"
        :period-date="selectedPeriodDate"
        :placeholder="`添加到 ${selectedYear} 年 ${selectedMonth} 月`"
        @created="loadEntries"
      />
      <EntryList :entries="selectedEntries" :loading="loading" show-date @refresh="loadEntries" />
    </div>
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

const currentYear = dayjs().year()
const selectedYear = ref(currentYear)
const selectedMonth = ref(dayjs().month() + 1)
const entries = ref([])
const loading = ref(false)

const yearOptions = computed(() => {
  const start = currentYear - 2
  return Array.from({ length: 7 }, (_, index) => start + index)
})

const months = computed(() =>
  Array.from({ length: 12 }, (_, index) => {
    const value = index + 1
    const key = `${selectedYear.value}-${String(value).padStart(2, '0')}`
    return { value, key, label: `${value} 月` }
  }),
)

const selectedPeriodDate = computed(
  () => `${selectedYear.value}-${String(selectedMonth.value).padStart(2, '0')}-01`,
)

const selectedEntries = computed(() => entriesForMonth(selectedPeriodDate.value.slice(0, 7)))

function monthKeyOf(entry) {
  return (entry.period_date || entry.entry_date || '').slice(0, 7)
}

function entriesForMonth(key) {
  return entries.value.filter((entry) => monthKeyOf(entry) === key)
}

async function loadEntries() {
  loading.value = true
  try {
    const { data } = await listEntries({
      log_type: 'future',
      year: selectedYear.value,
    })
    entries.value = data.items
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    loading.value = false
  }
}

watch(selectedYear, () => {
  if (selectedYear.value !== currentYear) {
    selectedMonth.value = 1
  } else {
    selectedMonth.value = dayjs().month() + 1
  }
  loadEntries()
})

onMounted(loadEntries)
</script>

<style scoped>
.year-select {
  width: 130px;
}

.month-card {
  display: block;
  width: 100%;
  border: 1px solid var(--od-border);
  color: inherit;
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease;
}

.month-card:hover,
.month-card-active {
  border-color: rgba(97, 175, 239, 0.55);
  box-shadow:
    0 20px 50px rgba(0, 0, 0, 0.38),
    0 0 28px rgba(97, 175, 239, 0.14);
}

.month-empty,
.month-more {
  color: var(--od-text-dim);
  font-size: 12px;
}

.month-entries {
  display: flex;
  flex-direction: column;
}

.month-entry {
  display: flex;
  gap: 7px;
  padding: 5px 0;
  font-size: 13px;
  line-height: 1.45;
}

.entry-marker {
  flex: none;
}

.month-more {
  margin-top: 8px;
}

.selected-month-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.selected-month-section h2 {
  margin: 8px 0 0;
  font-size: 18px;
}
</style>
