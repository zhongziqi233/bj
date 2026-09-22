<template>
  <el-card class="surface-card composer-card" shadow="never">
    <div class="composer-row">
      <el-select v-model="form.kind" class="kind-select" aria-label="记录类型">
        <el-option label="任务" value="task">
          <span class="composer-option"><BulletMark kind="task" :size="16" />任务</span>
        </el-option>
        <el-option label="事件" value="event">
          <span class="composer-option"><BulletMark kind="event" :size="16" />事件</span>
        </el-option>
        <el-option label="笔记" value="note">
          <span class="composer-option"><BulletMark kind="note" :size="16" />笔记</span>
        </el-option>
      </el-select>

      <el-input
        v-model="form.content"
        class="content-input"
        :placeholder="placeholder"
        maxlength="500"
        show-word-limit
        @keyup.enter="submit"
      />

      <el-date-picker
        v-if="allowDate"
        v-model="form.date"
        class="date-select"
        type="date"
        value-format="YYYY-MM-DD"
        placeholder="可选日期"
        clearable
      />

      <el-checkbox v-model="form.important" class="important-check">
        <el-icon><Star /></el-icon>
        重点
      </el-checkbox>

      <el-button type="primary" :loading="submitting" @click="submit">
        添加
      </el-button>
    </div>
    <div class="composer-hint">
      <span><BulletMark kind="task" :size="14" /> 任务</span>
      <span><BulletMark kind="event" :size="14" /> 事件</span>
      <span><BulletMark kind="note" :size="14" /> 笔记</span>
      <span v-if="allowDate">不填写日期时，归入本月任务列表</span>
    </div>
  </el-card>
</template>

<script setup>
import { reactive, ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Star } from '@element-plus/icons-vue'

import BulletMark from '@/components/BulletMark.vue'
import { createEntry } from '@/api/entries'
import { getApiError } from '@/api/http'
import { today } from '@/utils/date'

const props = defineProps({
  logType: {
    type: String,
    required: true,
  },
  entryDate: {
    type: String,
    default: '',
  },
  periodDate: {
    type: String,
    default: '',
  },
  collectionId: {
    type: Number,
    default: null,
  },
  allowDate: {
    type: Boolean,
    default: false,
  },
  placeholder: {
    type: String,
    default: '写下一件事，按 Enter 快速添加',
  },
})

const emit = defineEmits(['created'])

const form = reactive({
  kind: 'task',
  content: '',
  important: false,
  date: '',
})
const submitting = ref(false)

watch(
  () => props.entryDate,
  (value) => {
    if (value) form.date = value
  },
  { immediate: true },
)

async function submit() {
  const content = form.content.trim()
  if (!content) {
    ElMessage.warning('先写下记录内容')
    return
  }

  const payload = {
    kind: form.kind,
    content,
    important: form.important,
    log_type: props.logType,
  }

  if (props.logType === 'daily') {
    payload.entry_date = props.entryDate || today()
  } else if (props.logType === 'monthly') {
    if (props.allowDate && form.date) {
      payload.entry_date = form.date
    } else {
      payload.period_date = props.periodDate || `${today().slice(0, 7)}-01`
    }
  } else if (props.logType === 'future') {
    payload.period_date = props.periodDate
  } else if (props.logType === 'collection') {
    payload.collection_id = props.collectionId
  }

  submitting.value = true
  try {
    await createEntry(payload)
    form.content = ''
    form.important = false
    ElMessage.success('已添加')
    emit('created')
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    submitting.value = false
  }
}
</script>

<style scoped>
.composer-card {
  padding: 4px;
}

.composer-row {
  display: flex;
  align-items: center;
  gap: 10px;
}

.kind-select {
  width: 108px;
  flex: none;
}

.content-input {
  flex: 1;
  min-width: 160px;
}

.date-select {
  width: 150px;
  flex: none;
}

.important-check {
  flex: none;
}

.composer-hint {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 10px;
  color: var(--od-text-dim);
  font-size: 12px;
}

.composer-option {
  display: inline-flex;
  align-items: center;
  gap: 7px;
}

.composer-option :deep(.bullet-mark),
.composer-hint :deep(.bullet-mark) {
  margin-right: 5px;
}

@media (max-width: 760px) {
  .composer-row {
    align-items: stretch;
    flex-wrap: wrap;
  }

  .kind-select,
  .date-select {
    width: calc(50% - 5px);
  }

  .content-input {
    width: 100%;
    flex-basis: 100%;
    order: -1;
  }

  .important-check {
    flex: 1;
  }
}
</style>
