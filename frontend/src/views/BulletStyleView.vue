<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <h1 class="page-title">自定义子弹</h1>
        <p class="page-subtitle">
          为任务、事件和笔记设计专属符号。可以叠加预设矢量，也可以上传 SVG 或粘贴任意路径。
        </p>
      </div>
      <div class="heading-actions">
        <el-button :icon="Refresh" @click="resetAll">恢复默认</el-button>
        <el-button type="primary" :icon="Check" :loading="saving" @click="save">保存样式</el-button>
      </div>
    </div>

    <div class="bullet-editor-layout">
      <el-card class="surface-card preview-card" shadow="never">
        <template #header>
          <div class="card-header">实时预览</div>
        </template>
        <el-radio-group v-model="activeKind" class="kind-switch">
          <el-radio-button
            v-for="item in kindOptions"
            :key="item.value"
            :value="item.value"
          >
            {{ item.label }}
          </el-radio-button>
        </el-radio-group>
        <el-radio-group
          v-if="activeKind === 'task'"
          v-model="activeStatus"
          class="status-switch"
        >
          <el-radio-button
            v-for="item in statusOptions"
            :key="item.value"
            :value="item.value"
          >
            {{ item.label }}
          </el-radio-button>
        </el-radio-group>

        <div class="preview-stage">
          <div class="preview-hero">
            <BulletMark :kind="activeKind" :config="activeBullet" :size="96" />
            <span>
              {{ activeKindLabel }}<template v-if="activeStatusLabel"> · {{ activeStatusLabel }}</template>
            </span>
          </div>
          <div class="preview-row">
            <BulletMark :kind="activeKind" :config="activeBullet" :size="26" />
            <div>
              <div class="preview-row-title">今天要做的事情</div>
              <div class="preview-row-meta">在真实日志列表中的效果</div>
            </div>
          </div>
          <div class="preview-sizes">
            <span v-for="size in [16, 20, 26, 32]" :key="size">
              <BulletMark :kind="activeKind" :config="activeBullet" :size="size" />
            </span>
          </div>
        </div>
      </el-card>

      <el-card class="surface-card library-card" shadow="never">
        <template #header>
          <div class="card-header">添加矢量图层</div>
        </template>

        <div class="section-label">预设矢量</div>
        <div class="shape-library">
          <button
            v-for="shape in shapePreviews"
            :key="shape.key"
            type="button"
            class="shape-button"
            :title="shape.label"
            @click="addPreset(shape)"
          >
            <BulletMark :config="{ layers: [shape.layer] }" :size="30" />
            <span>{{ shape.label }}</span>
          </button>
        </div>

        <el-divider />

        <div class="section-label">任意矢量</div>
        <div class="import-actions">
          <input
            ref="fileInputRef"
            class="file-input"
            type="file"
            accept=".svg,image/svg+xml"
            @change="onSvgUpload"
          />
          <el-button :icon="UploadFilled" @click="openFilePicker">上传 SVG 文件</el-button>
          <span class="import-hint">建议不超过 200 KB</span>
        </div>
        <div class="path-import">
          <el-input
            v-model="pathInput"
            type="textarea"
            :rows="2"
            placeholder="粘贴 SVG path 的 d 数据，例如 M12 2L2 22h20L12 2z"
          />
          <el-button type="primary" plain :disabled="!pathInput.trim()" @click="addPathLayer">
            添加路径
          </el-button>
        </div>
      </el-card>
    </div>

    <el-card class="surface-card layers-card" shadow="never">
      <template #header>
        <div class="card-header-row">
          <div class="card-header">图层（从下到上叠加）</div>
          <el-tag effect="plain" round>{{ activeBullet.layers.length }} 层</el-tag>
        </div>
      </template>

      <div class="layers-layout">
        <div class="layer-list">
          <button
            v-for="(layer, index) in activeBullet.layers"
            :key="layer.id"
            type="button"
            class="layer-item"
            :class="{ active: selectedLayerId === layer.id }"
            @click="selectedLayerId = layer.id"
          >
            <span class="layer-index">{{ index + 1 }}</span>
            <BulletMark :config="{ layers: [layer] }" :size="26" />
            <span class="layer-name">{{ layerName(layer) }}</span>
            <span class="layer-actions" @click.stop>
              <el-button
                text
                circle
                size="small"
                :disabled="index === 0"
                @click="moveLayer(index, -1)"
              >
                <el-icon><ArrowUp /></el-icon>
              </el-button>
              <el-button
                text
                circle
                size="small"
                :disabled="index === activeBullet.layers.length - 1"
                @click="moveLayer(index, 1)"
              >
                <el-icon><ArrowDown /></el-icon>
              </el-button>
              <el-button text circle size="small" @click="duplicateLayer(layer)">
                <el-icon><CopyDocument /></el-icon>
              </el-button>
              <el-button
                text
                circle
                size="small"
                type="danger"
                :disabled="activeBullet.layers.length <= 1"
                @click="removeLayer(layer)"
              >
                <el-icon><Delete /></el-icon>
              </el-button>
            </span>
          </button>
        </div>

        <div v-if="selectedLayer" class="layer-controls">
          <div class="control-header">
            <span>{{ layerName(selectedLayer) }}</span>
            <el-button text type="primary" @click="resetCurrent">当前类型恢复默认</el-button>
          </div>

          <el-form label-position="top" size="small">
            <el-form-item label="大小">
              <el-slider v-model="selectedLayer.size" :min="5" :max="200" show-input />
            </el-form-item>
            <el-form-item label="水平偏移">
              <el-slider v-model="selectedLayer.x" :min="-100" :max="100" show-input />
            </el-form-item>
            <el-form-item label="垂直偏移">
              <el-slider v-model="selectedLayer.y" :min="-100" :max="100" show-input />
            </el-form-item>
            <el-form-item label="旋转角度">
              <el-slider v-model="selectedLayer.rotation" :min="-180" :max="180" show-input />
            </el-form-item>
            <el-form-item label="透明度">
              <el-slider v-model="selectedLayer.opacity" :min="0" :max="100" show-input />
            </el-form-item>

            <template v-if="selectedLayer.type !== 'svg'">
              <el-form-item label="填充">
                <div class="color-control">
                  <el-switch
                    :model-value="hasFill(selectedLayer)"
                    @change="(value) => toggleFill(selectedLayer, value)"
                  />
                  <el-color-picker
                    :model-value="fillColor(selectedLayer)"
                    :disabled="!hasFill(selectedLayer)"
                    @change="(value) => setFill(selectedLayer, value)"
                  />
                </div>
              </el-form-item>
              <el-form-item label="描边">
                <div class="color-control">
                  <el-switch
                    :model-value="hasStroke(selectedLayer)"
                    @change="(value) => toggleStroke(selectedLayer, value)"
                  />
                  <el-color-picker
                    :model-value="strokeColor(selectedLayer)"
                    :disabled="!hasStroke(selectedLayer)"
                    @change="(value) => setStroke(selectedLayer, value)"
                  />
                </div>
              </el-form-item>
              <el-form-item label="描边宽度">
                <el-slider
                  v-model="selectedLayer.strokeWidth"
                  :min="0"
                  :max="8"
                  :step="0.1"
                  show-input
                />
              </el-form-item>
            </template>
            <el-alert
              v-else
              title="导入的 SVG 会保留原始颜色"
              description="仍可调整大小、位置、旋转和透明度。"
              type="info"
              :closable="false"
              show-icon
            />
          </el-form>
        </div>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  ArrowDown,
  ArrowUp,
  Check,
  CopyDocument,
  Delete,
  Refresh,
  UploadFilled,
} from '@element-plus/icons-vue'

import BulletMark from '@/components/BulletMark.vue'
import { getApiError } from '@/api/http'
import { useBulletStyleStore } from '@/stores/bulletStyle'
import {
  cloneBulletConfig,
  createLayerId,
  createPresetLayer,
  DEFAULT_BULLET_CONFIG,
  KIND_ACCENTS,
  KIND_LABELS,
  TASK_STATUS_OPTIONS,
} from '@/utils/bulletDefaults'
import { BULLET_SHAPES, SHAPE_MAP } from '@/utils/bulletShapes'

const bulletStyle = useBulletStyleStore()

const kindOptions = [
  { label: KIND_LABELS.task, value: 'task' },
  { label: KIND_LABELS.event, value: 'event' },
  { label: KIND_LABELS.note, value: 'note' },
]
const statusOptions = TASK_STATUS_OPTIONS

const activeKind = ref('task')
const activeStatus = ref('open')
const localConfig = ref(cloneBulletConfig(DEFAULT_BULLET_CONFIG))
const selectedLayerId = ref(null)
const pathInput = ref('')
const fileInputRef = ref()
const saving = ref(false)

const activeKindConfig = computed(
  () => localConfig.value[activeKind.value] || DEFAULT_BULLET_CONFIG[activeKind.value],
)
const activeBullet = computed(() => {
  const kindConfig = activeKindConfig.value
  if (activeKind.value === 'task' && activeStatus.value !== 'open') {
    return (
      kindConfig.statuses?.[activeStatus.value] ||
      DEFAULT_BULLET_CONFIG.task.statuses[activeStatus.value]
    )
  }
  return kindConfig
})
const activeKindLabel = computed(
  () => kindOptions.find((item) => item.value === activeKind.value)?.label || '任务',
)
const activeStatusLabel = computed(() =>
  activeKind.value === 'task'
    ? TASK_STATUS_OPTIONS.find((item) => item.value === activeStatus.value)?.label || '待办'
    : '',
)
const selectedLayer = computed(
  () =>
    activeBullet.value.layers.find((layer) => layer.id === selectedLayerId.value) ||
    activeBullet.value.layers[0] ||
    null,
)
const shapePreviews = computed(() =>
  BULLET_SHAPES.map((shape) => ({
    ...shape,
    layer: createPresetLayer(shape.key, KIND_ACCENTS[activeKind.value]),
  })),
)

watch(activeKind, () => {
  if (activeKind.value !== 'task') {
    activeStatus.value = 'open'
  }
  selectedLayerId.value = activeBullet.value.layers[0]?.id || null
})
watch(activeStatus, () => {
  selectedLayerId.value = activeBullet.value.layers[0]?.id || null
})

onMounted(async () => {
  try {
    await bulletStyle.load()
    localConfig.value = cloneBulletConfig(bulletStyle.config)
  } catch {
    localConfig.value = cloneBulletConfig(DEFAULT_BULLET_CONFIG)
  }
  selectedLayerId.value = activeBullet.value.layers[0]?.id || null
})

function addLayer(layer) {
  if (!layer.id) {
    layer.id = createLayerId(activeKind.value)
  }
  activeBullet.value.layers.push(layer)
  selectedLayerId.value = layer.id
}

function addPreset(shape) {
  addLayer(createPresetLayer(shape.key, KIND_ACCENTS[activeKind.value]))
}

function addPathLayer() {
  const path = pathInput.value.trim()
  if (!path || path.length > 2000 || !/^[0-9A-Za-z.,\s+\-eE]+$/.test(path)) {
    ElMessage.warning('路径只能包含 SVG path 标准字符，且不能超过 2000 个字符')
    return
  }
  addLayer({
    id: createLayerId('path'),
    type: 'path',
    path,
    size: 90,
    x: 0,
    y: 0,
    rotation: 0,
    opacity: 100,
    fill: 'none',
    stroke: KIND_ACCENTS[activeKind.value],
    strokeWidth: 2,
  })
  pathInput.value = ''
}

function openFilePicker() {
  fileInputRef.value?.click()
}

function onSvgUpload(event) {
  const file = event.target.files?.[0]
  if (!file) return
  if (!file.name.toLowerCase().endsWith('.svg') && !file.type.includes('svg')) {
    ElMessage.warning('请选择 SVG 文件')
    event.target.value = ''
    return
  }
  if (file.size > 200 * 1024) {
    ElMessage.warning('SVG 文件不能超过 200 KB')
    event.target.value = ''
    return
  }

  const reader = new FileReader()
  reader.onload = () => {
    addLayer({
      id: createLayerId('svg'),
      type: 'svg',
      data: String(reader.result),
      size: 100,
      x: 0,
      y: 0,
      rotation: 0,
      opacity: 100,
      fill: 'none',
      stroke: 'none',
      strokeWidth: 0,
    })
    ElMessage.success('SVG 已添加')
  }
  reader.onerror = () => ElMessage.error('读取 SVG 失败')
  reader.readAsDataURL(file)
  event.target.value = ''
}

function duplicateLayer(layer) {
  const index = activeBullet.value.layers.findIndex((item) => item.id === layer.id)
  const clone = JSON.parse(JSON.stringify(layer))
  clone.id = createLayerId(activeKind.value)
  activeBullet.value.layers.splice(index + 1, 0, clone)
  selectedLayerId.value = clone.id
}

function removeLayer(layer) {
  if (activeBullet.value.layers.length <= 1) {
    ElMessage.warning('至少保留一个图层')
    return
  }
  const index = activeBullet.value.layers.findIndex((item) => item.id === layer.id)
  activeBullet.value.layers.splice(index, 1)
  selectedLayerId.value =
    activeBullet.value.layers[Math.max(0, index - 1)]?.id ||
    activeBullet.value.layers[0]?.id ||
    null
}

function moveLayer(index, delta) {
  const target = index + delta
  if (target < 0 || target >= activeBullet.value.layers.length) return
  const [layer] = activeBullet.value.layers.splice(index, 1)
  activeBullet.value.layers.splice(target, 0, layer)
}

function layerName(layer) {
  if (layer.type === 'svg') return '导入的 SVG'
  if (layer.type === 'path') return '自定义路径'
  return SHAPE_MAP[layer.shape]?.label || '预设图形'
}

function hasFill(layer) {
  return Boolean(layer.fill && layer.fill !== 'none')
}

function fillColor(layer) {
  return hasFill(layer) ? layer.fill : KIND_ACCENTS[activeKind.value]
}

function toggleFill(layer, value) {
  layer.fill = value ? fillColor(layer) : 'none'
}

function setFill(layer, value) {
  if (value) layer.fill = value
}

function hasStroke(layer) {
  return Boolean(layer.stroke && layer.stroke !== 'none')
}

function strokeColor(layer) {
  return hasStroke(layer) ? layer.stroke : KIND_ACCENTS[activeKind.value]
}

function toggleStroke(layer, value) {
  layer.stroke = value ? strokeColor(layer) : 'none'
}

function setStroke(layer, value) {
  if (value) layer.stroke = value
}

async function save() {
  saving.value = true
  try {
    await bulletStyle.save(localConfig.value)
    ElMessage.success('子弹样式已保存')
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    saving.value = false
  }
}

function resetCurrent() {
  const defaults = cloneBulletConfig(DEFAULT_BULLET_CONFIG)
  if (activeKind.value === 'task' && activeStatus.value !== 'open') {
    if (!activeKindConfig.value.statuses) {
      activeKindConfig.value.statuses = {}
    }
    activeKindConfig.value.statuses[activeStatus.value] =
      defaults.task.statuses[activeStatus.value]
  } else {
    localConfig.value[activeKind.value] = defaults[activeKind.value]
  }
  selectedLayerId.value = activeBullet.value.layers[0]?.id || null
  ElMessage.info('当前子弹已恢复默认，保存后生效')
}

async function resetAll() {
  try {
    await ElMessageBox.confirm(
      '恢复默认会清除当前所有自定义图层，确定继续吗？',
      '恢复默认',
      {
        type: 'warning',
        confirmButtonText: '恢复',
        cancelButtonText: '取消',
      },
    )
    await bulletStyle.reset()
    localConfig.value = cloneBulletConfig(bulletStyle.config)
    selectedLayerId.value = activeBullet.value.layers[0]?.id || null
    ElMessage.success('已恢复默认子弹样式')
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getApiError(error))
    }
  }
}
</script>

<style scoped>
.heading-actions {
  display: flex;
  gap: 10px;
}

.bullet-editor-layout {
  display: grid;
  grid-template-columns: minmax(320px, 0.9fr) minmax(380px, 1.1fr);
  gap: 16px;
}

.preview-card,
.library-card,
.layers-card {
  padding: 4px;
}

.card-header,
.card-header-row {
  font-weight: 700;
}

.card-header-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.kind-switch {
  margin-bottom: 16px;
}

.status-switch {
  margin-bottom: 16px;
}

.preview-stage {
  display: flex;
  min-height: 330px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  border: 1px solid var(--od-border);
  border-radius: 16px;
  background:
    linear-gradient(rgba(97, 175, 239, 0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(97, 175, 239, 0.05) 1px, transparent 1px),
    rgba(27, 31, 36, 0.7);
  background-size: 28px 28px;
}

.preview-hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  color: var(--od-text-muted);
  font-size: 12px;
}

.preview-hero :deep(.bullet-mark) {
  filter: drop-shadow(0 0 22px rgba(97, 175, 239, 0.22));
}

.preview-row {
  display: flex;
  align-items: center;
  gap: 12px;
  width: min(320px, 90%);
  padding: 14px 16px;
  border: 1px solid var(--od-border);
  border-radius: 14px;
  background: rgba(40, 44, 52, 0.78);
  box-shadow: 0 14px 34px rgba(0, 0, 0, 0.24);
}

.preview-row-title {
  color: var(--od-text-strong);
  font-size: 14px;
}

.preview-row-meta {
  margin-top: 4px;
  color: var(--od-text-dim);
  font-size: 11px;
}

.preview-sizes {
  display: flex;
  align-items: center;
  gap: 18px;
  color: var(--od-text-dim);
}

.section-label {
  margin-bottom: 10px;
  color: var(--od-text-muted);
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
}

.shape-library {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(70px, 1fr));
  gap: 8px;
  max-height: 280px;
  overflow-y: auto;
  padding-right: 4px;
}

.shape-button {
  display: flex;
  min-height: 68px;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 4px;
  border: 1px solid var(--od-border);
  border-radius: 12px;
  background: rgba(40, 44, 52, 0.72);
  color: var(--od-text-muted);
  font-size: 11px;
  cursor: pointer;
  transition:
    transform 0.2s ease,
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    color 0.2s ease;
}

.shape-button:hover {
  transform: translateY(-2px);
  border-color: rgba(97, 175, 239, 0.55);
  color: var(--od-text-strong);
  box-shadow: 0 10px 26px rgba(97, 175, 239, 0.16);
}

.import-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.file-input {
  display: none;
}

.import-hint {
  color: var(--od-text-dim);
  font-size: 12px;
}

.path-import {
  display: flex;
  align-items: flex-end;
  gap: 10px;
  margin-top: 12px;
}

.path-import .el-input {
  flex: 1;
}

.layers-layout {
  display: grid;
  grid-template-columns: minmax(240px, 0.7fr) minmax(360px, 1.3fr);
  gap: 18px;
}

.layer-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.layer-item {
  display: flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  padding: 9px 10px;
  border: 1px solid var(--od-border);
  border-radius: 12px;
  background: rgba(40, 44, 52, 0.62);
  color: var(--od-text);
  text-align: left;
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    background-color 0.2s ease,
    transform 0.2s ease;
}

.layer-item:hover,
.layer-item.active {
  transform: translateX(3px);
  border-color: rgba(97, 175, 239, 0.55);
  background: rgba(97, 175, 239, 0.1);
}

.layer-index {
  display: grid;
  width: 20px;
  height: 20px;
  place-items: center;
  border-radius: 6px;
  background: rgba(97, 175, 239, 0.18);
  color: var(--od-blue);
  font-size: 11px;
  font-weight: 800;
}

.layer-name {
  flex: 1;
  min-width: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
}

.layer-actions {
  display: flex;
  align-items: center;
  flex: none;
}

.layer-controls {
  padding: 4px 8px;
  border-left: 1px solid var(--od-border);
}

.control-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
  color: var(--od-text-strong);
  font-weight: 700;
}

.color-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

@media (max-width: 980px) {
  .bullet-editor-layout,
  .layers-layout {
    grid-template-columns: 1fr;
  }

  .layer-controls {
    border-top: 1px solid var(--od-border);
    border-left: 0;
    padding-top: 16px;
  }
}

@media (max-width: 560px) {
  .heading-actions,
  .import-actions,
  .path-import {
    width: 100%;
    align-items: stretch;
    flex-wrap: wrap;
  }

  .heading-actions .el-button {
    flex: 1;
  }
}
</style>
