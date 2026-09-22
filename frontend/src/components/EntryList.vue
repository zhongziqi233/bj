<template>
  <el-card class="surface-card entry-list-card" shadow="never">
    <template #header>
      <div class="entry-list-header">
        <div>
          <span class="entry-list-title">记录</span>
          <span class="entry-list-count">{{ entries.length }} 条</span>
        </div>
        <el-tag v-if="entries.length" type="info" effect="plain" round>
          {{ completedCount }} / {{ taskCount }} 个任务已完成
        </el-tag>
      </div>
    </template>

    <el-skeleton v-if="loading" :rows="5" animated />
    <div v-else-if="!entries.length" class="empty-hint">
      <el-empty description="这里还没有记录" />
    </div>
    <div v-else class="entry-list">
      <div
        v-for="entry in entries"
        :key="entry.id"
        class="entry-row"
        :class="{ 'entry-completed': entry.status === 'completed' }"
      >
        <div class="entry-main">
          <button
            v-if="entry.kind === 'task'"
            type="button"
            class="entry-bullet-button"
            :class="{ 'is-done': entry.status === 'completed' }"
            :disabled="!['open', 'completed'].includes(entry.status)"
            :aria-label="entry.status === 'completed' ? '标记为未完成' : '标记为已完成'"
            @click="toggleTask(entry, entry.status !== 'completed')"
          >
            <BulletMark kind="task" :status="entry.status" :size="24" />
            <span v-if="entry.status === 'completed'" class="entry-bullet-check">✓</span>
          </button>
          <span v-else class="entry-kind">
            <BulletMark :kind="entry.kind" :status="entry.status" :size="24" />
          </span>

          <span v-if="entry.important" class="entry-important" title="重点">
            <el-icon><StarFilled /></el-icon>
          </span>

          <div class="entry-body">
            <div class="entry-content">{{ entry.content }}</div>
            <div class="entry-meta">
              <span>{{ kindLabels[entry.kind] }}</span>
              <span v-if="showDate && entry.entry_date">{{ entry.entry_date }}</span>
              <span v-if="entry.status === 'postponed' && entry.migrated_to_date">
                已推迟至 {{ entry.migrated_to_date }}
              </span>
              <span v-if="entry.status === 'migrated' && entry.migrated_to_date">
                已迁移至 {{ entry.migrated_to_date }}
              </span>
              <span v-if="entry.status === 'scheduled' && entry.scheduled_date">
                已安排至 {{ entry.scheduled_date.slice(0, 7) }}
              </span>
              <el-tag
                v-if="entry.status !== 'open'"
                :type="statusTypes[entry.status] || 'info'"
                size="small"
                effect="light"
              >
                {{ statusLabels[entry.status] }}
              </el-tag>
            </div>
          </div>
        </div>

        <el-popover
          :visible="actionDialog.visible && actionDialog.entry?.id === entry.id"
          trigger="manual"
          placement="bottom-end"
          :width="320"
          :offset="10"
          popper-class="entry-action-popper"
          @update:visible="(value) => !value && closeActionDialog()"
        >
          <div class="entry-action-popover">
            <div class="popover-title">{{ actionDialog.title }}</div>
            <p class="dialog-tip">{{ actionDialog.tip }}</p>
            <el-date-picker
              v-model="actionDialog.targetDate"
              :type="actionDialog.mode === 'migrate' ? 'date' : 'month'"
              :value-format="actionDialog.mode === 'migrate' ? 'YYYY-MM-DD' : 'YYYY-MM'"
              :placeholder="actionDialog.mode === 'migrate' ? '选择日期' : '选择月份'"
              style="width: 100%"
            />
            <div class="popover-actions">
              <el-button size="small" @click="closeActionDialog">取消</el-button>
              <el-button
                size="small"
                type="primary"
                :loading="actionLoading"
                @click="confirmAction"
              >
                确认
              </el-button>
            </div>
          </div>
          <template #reference>
            <span class="entry-action-trigger">
              <el-dropdown trigger="click" @command="(command) => handleCommand(command, entry)">
                <el-button text circle aria-label="更多操作">
                  <el-icon><MoreFilled /></el-icon>
                </el-button>
                <template #dropdown>
                  <el-dropdown-menu>
                    <el-dropdown-item command="edit">编辑内容</el-dropdown-item>
                    <el-dropdown-item
                      v-if="entry.kind === 'task' && entry.status === 'open'"
                      command="postpone"
                    >
                      推迟到明天（&gt;）
                    </el-dropdown-item>
                    <el-dropdown-item
                      v-if="entry.kind === 'task' && entry.status === 'open'"
                      command="migrate"
                    >
                      迁移到指定日期（&lt;）
                    </el-dropdown-item>
                    <el-dropdown-item v-if="entry.status === 'open'" command="schedule">
                      安排到未来日志
                    </el-dropdown-item>
                    <el-dropdown-item command="delete" divided>删除</el-dropdown-item>
                  </el-dropdown-menu>
                </template>
              </el-dropdown>
            </span>
          </template>
        </el-popover>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { computed, reactive, ref } from 'vue'
import dayjs from 'dayjs'
import { ElMessage, ElMessageBox } from 'element-plus'
import { MoreFilled, StarFilled } from '@element-plus/icons-vue'

import BulletMark from '@/components/BulletMark.vue'
import {
  deleteEntry,
  migrateEntry,
  postponeEntry,
  scheduleEntry,
  updateEntry,
} from '@/api/entries'
import { getApiError } from '@/api/http'

const props = defineProps({
  entries: {
    type: Array,
    default: () => [],
  },
  loading: {
    type: Boolean,
    default: false,
  },
  showDate: {
    type: Boolean,
    default: false,
  },
})

const emit = defineEmits(['refresh'])

const kindLabels = {
  task: '任务',
  event: '事件',
  note: '笔记',
}

const statusLabels = {
  open: '进行中',
  completed: '已完成',
  postponed: '已推迟',
  migrated: '已迁移',
  scheduled: '已安排',
  cancelled: '已取消',
}

const statusTypes = {
  completed: 'success',
  postponed: 'warning',
  migrated: 'warning',
  scheduled: 'primary',
  cancelled: 'info',
}

const taskCount = computed(() => props.entries.filter((entry) => entry.kind === 'task').length)
const completedCount = computed(
  () => props.entries.filter((entry) => entry.kind === 'task' && entry.status === 'completed').length,
)

const actionLoading = ref(false)
const actionDialog = reactive({
  visible: false,
  mode: 'migrate',
  entry: null,
  targetDate: '',
  title: '',
  tip: '',
})

function openActionDialog(mode, entry) {
  actionDialog.mode = mode
  actionDialog.entry = entry
  actionDialog.visible = true
  if (mode === 'migrate') {
    actionDialog.title = '迁移任务'
    actionDialog.tip = '迁移会创建一个副本到目标日期，并把当前任务标记为已迁移。'
    actionDialog.targetDate = dayjs().add(1, 'day').format('YYYY-MM-DD')
  } else {
    actionDialog.title = '安排到未来日志'
    actionDialog.tip = '安排会创建一个副本到未来日志的目标月份，并把当前记录标记为已安排。'
    actionDialog.targetDate = dayjs().format('YYYY-MM')
  }
}

function closeActionDialog() {
  actionDialog.visible = false
}

async function handleCommand(command, entry) {
  if (command === 'edit') {
    await editContent(entry)
  } else if (command === 'postpone') {
    await postponeTask(entry)
  } else if (command === 'migrate' || command === 'schedule') {
    openActionDialog(command, entry)
  } else if (command === 'delete') {
    await removeEntry(entry)
  }
}

async function editContent(entry) {
  try {
    const { value } = await ElMessageBox.prompt('修改记录内容', '编辑记录', {
      inputValue: entry.content,
      inputType: 'textarea',
      inputValidator: (value) => Boolean(value && value.trim()),
      inputErrorMessage: '内容不能为空',
      confirmButtonText: '保存',
      cancelButtonText: '取消',
    })
    await updateEntry(entry.id, { content: value.trim() })
    ElMessage.success('已保存')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getApiError(error))
    }
  }
}

async function toggleTask(entry, value) {
  if (!['open', 'completed'].includes(entry.status)) return
  try {
    await updateEntry(entry.id, { status: value ? 'completed' : 'open' })
    emit('refresh')
  } catch (error) {
    ElMessage.error(getApiError(error))
  }
}

async function confirmAction() {
  if (!actionDialog.targetDate) {
    ElMessage.warning('请选择目标日期或月份')
    return
  }

  actionLoading.value = true
  try {
    if (actionDialog.mode === 'migrate') {
      await migrateEntry(actionDialog.entry.id, actionDialog.targetDate)
    } else {
      await scheduleEntry(actionDialog.entry.id, `${actionDialog.targetDate}-01`)
    }
    ElMessage.success('操作成功')
    closeActionDialog()
    emit('refresh')
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    actionLoading.value = false
  }
}

async function postponeTask(entry) {
  try {
    await postponeEntry(entry.id)
    ElMessage.success('任务已推迟到明天')
    emit('refresh')
  } catch (error) {
    ElMessage.error(getApiError(error))
  }
}

async function removeEntry(entry) {
  try {
    await ElMessageBox.confirm('删除后无法恢复，确定删除这条记录吗？', '删除记录', {
      type: 'warning',
      confirmButtonText: '删除',
      cancelButtonText: '取消',
    })
    await deleteEntry(entry.id)
    ElMessage.success('已删除')
    emit('refresh')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getApiError(error))
    }
  }
}
</script>

<style scoped>
.entry-list-card {
  padding: 4px;
}

.entry-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
}

.entry-list-title {
  font-weight: 700;
}

.entry-list-count {
  margin-left: 8px;
  color: var(--od-text-dim);
  font-size: 13px;
}

.entry-list {
  display: flex;
  flex-direction: column;
}

.entry-row {
  position: relative;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  overflow: hidden;
  padding: 13px 4px;
  border-bottom: 1px solid var(--od-border);
  border-radius: 10px;
  transition:
    background-color 0.2s ease,
    box-shadow 0.2s ease;
}

.entry-row::after {
  position: absolute;
  inset: 0;
  z-index: 0;
  background: linear-gradient(
    110deg,
    transparent 25%,
    rgba(97, 175, 239, 0.09) 48%,
    rgba(198, 120, 221, 0.07) 56%,
    transparent 75%
  );
  transform: translateX(-125%);
  transition: transform 0.55s ease;
  pointer-events: none;
  content: "";
}

.entry-row > * {
  position: relative;
  z-index: 1;
}

.entry-row:hover {
  background: linear-gradient(90deg, rgba(97, 175, 239, 0.1), transparent 62%);
  box-shadow:
    inset 3px 0 0 0 rgba(97, 175, 239, 0.72),
    0 0 20px rgba(97, 175, 239, 0.08);
}

.entry-row:hover::after {
  transform: translateX(125%);
}

.entry-row:last-child {
  border-bottom: 0;
}

.entry-main {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  min-width: 0;
}

.entry-bullet-button {
  position: relative;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  margin-top: 0;
  padding: 0;
  border: 0;
  background: transparent;
  cursor: pointer;
  transition: filter 0.2s ease;
}

.entry-bullet-button:hover {
  filter: drop-shadow(0 0 10px rgba(97, 175, 239, 0.36));
}

.entry-bullet-button:disabled {
  cursor: default;
}

.entry-bullet-button:disabled:hover {
  filter: none;
}

.entry-bullet-button.is-done {
  opacity: 0.62;
}

.entry-bullet-check {
  position: absolute;
  right: -3px;
  bottom: -3px;
  display: grid;
  width: 13px;
  height: 13px;
  place-items: center;
  border-radius: 50%;
  background: var(--od-green);
  color: #1b1f24;
  font-size: 9px;
  font-weight: 900;
  box-shadow: 0 0 10px rgba(152, 195, 121, 0.5);
}

.entry-kind {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 26px;
  height: 26px;
  flex: none;
}

.entry-important {
  display: inline-flex;
  padding-top: 2px;
  flex: none;
}

.entry-body {
  min-width: 0;
}

.entry-content {
  font-size: 15px;
}

.entry-meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 5px;
  color: var(--od-text-dim);
  font-size: 12px;
}

.entry-meta .el-tag {
  height: 20px;
  padding: 0 7px;
  font-size: 11px;
}

.dialog-tip {
  margin: 0 0 14px;
  color: var(--od-text-muted);
  line-height: 1.6;
}

.entry-action-trigger {
  display: inline-flex;
  align-items: center;
}

.entry-action-popover {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.popover-title {
  color: var(--od-text-strong);
  font-weight: 700;
}

.popover-actions {
  display: flex;
  justify-content: flex-end;
  gap: 8px;
}
</style>
