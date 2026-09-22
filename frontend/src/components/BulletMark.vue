<template>
  <span
    class="bullet-mark"
    :class="{ 'is-interactive': pointer.active }"
    :style="rootStyle"
    @pointerenter="handlePointerMove"
    @pointermove="handlePointerMove"
    @pointerleave="handlePointerLeave"
  >
    <template v-for="(layer, index) in layers" :key="layer.id || index">
      <img
        v-if="layer.type === 'svg'"
        class="bullet-layer bullet-layer-image"
        :src="layer.data"
        :style="layerStyle(layer, index)"
        alt=""
        draggable="false"
      />
      <svg
        v-else
        class="bullet-layer"
        viewBox="0 0 24 24"
        :style="layerStyle(layer, index)"
        aria-hidden="true"
      >
        <path
          :d="pathFor(layer)"
          :fill="colorOrNone(layer.fill)"
          :stroke="colorOrNone(layer.stroke)"
          :stroke-width="Number(layer.strokeWidth ?? 2)"
          stroke-linecap="round"
          stroke-linejoin="round"
          vector-effect="non-scaling-stroke"
        />
      </svg>
    </template>
  </span>
</template>

<script setup>
import { computed, ref } from 'vue'

import { useBulletStyleStore } from '@/stores/bulletStyle'
import { DEFAULT_BULLET_CONFIG, KIND_ACCENTS } from '@/utils/bulletDefaults'
import { SHAPE_PATHS } from '@/utils/bulletShapes'

const props = defineProps({
  kind: {
    type: String,
    default: 'task',
  },
  status: {
    type: String,
    default: 'open',
  },
  size: {
    type: Number,
    default: 20,
  },
  config: {
    type: Object,
    default: null,
  },
})

const bulletStyle = useBulletStyleStore()
const pointer = ref({ x: 0, y: 0, active: false })

const layers = computed(() => {
  const config =
    props.config ||
    bulletStyle.markFor(props.kind, props.status) ||
    DEFAULT_BULLET_CONFIG[props.kind]
  if (config?.layers?.length) {
    return config.layers
  }
  return DEFAULT_BULLET_CONFIG[props.kind]?.layers || DEFAULT_BULLET_CONFIG.task.layers
})

const accent = computed(() => {
  const firstColoredLayer = layers.value.find(
    (layer) =>
      (layer.fill && layer.fill !== 'none') || (layer.stroke && layer.stroke !== 'none'),
  )
  if (firstColoredLayer?.fill && firstColoredLayer.fill !== 'none') {
    return firstColoredLayer.fill
  }
  if (firstColoredLayer?.stroke && firstColoredLayer.stroke !== 'none') {
    return firstColoredLayer.stroke
  }
  return KIND_ACCENTS[props.kind] || '#61afef'
})

const rootStyle = computed(() => ({
  width: `${props.size}px`,
  height: `${props.size}px`,
  '--bullet-accent': accent.value,
  '--bullet-glow': hexToRgba(accent.value, 0.42),
  transform: pointer.value.active
    ? `perspective(${Math.max(80, props.size * 5)}px) translate3d(${pointer.value.x * 2.6}px, ${pointer.value.y * 2.6}px, 0) rotateX(${-pointer.value.y * 8}deg) rotateY(${pointer.value.x * 8}deg)`
    : 'none',
}))

function pathFor(layer) {
  if (layer.type === 'path') return layer.path
  return SHAPE_PATHS[layer.shape] || SHAPE_PATHS.dot
}

function colorOrNone(value) {
  return value && value !== 'none' ? value : 'none'
}

function layerStyle(layer, index) {
  const scale = Math.min(2, Math.max(0.05, Number(layer.size ?? 100) / 100))
  const offsetX = (Number(layer.x ?? 0) / 100) * props.size
  const offsetY = (Number(layer.y ?? 0) / 100) * props.size
  const rotation = Number(layer.rotation ?? 0)
  const opacity = Math.min(1, Math.max(0, Number(layer.opacity ?? 100) / 100))

  const depth = layers.value.length > 1 ? index / (layers.value.length - 1) : 0.55
  const parallax = pointer.value.active ? props.size * (0.06 + depth * 0.09) : 0

  return {
    width: `${props.size * scale}px`,
    height: `${props.size * scale}px`,
    opacity,
    transform: `translate(-50%, -50%) translate3d(${offsetX + pointer.value.x * parallax}px, ${offsetY + pointer.value.y * parallax}px, ${depth * props.size * 0.08}px) rotate(${rotation}deg)`,
  }
}

function handlePointerMove(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const radiusX = rect.width / 2 || 1
  const radiusY = rect.height / 2 || 1
  pointer.value = {
    x: clamp((event.clientX - (rect.left + radiusX)) / radiusX),
    y: clamp((event.clientY - (rect.top + radiusY)) / radiusY),
    active: true,
  }
}

function handlePointerLeave() {
  pointer.value = { x: 0, y: 0, active: false }
}

function clamp(value) {
  return Math.min(1, Math.max(-1, value))
}

function hexToRgba(color, alpha) {
  const normalized = String(color || '#61afef').replace('#', '')
  const hex = normalized.length === 3
    ? normalized.split('').map((char) => char + char).join('')
    : normalized.padEnd(6, '0').slice(0, 6)
  const value = Number.parseInt(hex, 16)
  const red = (value >> 16) & 255
  const green = (value >> 8) & 255
  const blue = value & 255
  return `rgba(${red}, ${green}, ${blue}, ${alpha})`
}
</script>

<style scoped>
.bullet-mark {
  position: relative;
  display: inline-block;
  flex: none;
  vertical-align: middle;
  filter:
    drop-shadow(0 2px 2px rgba(0, 0, 0, 0.66))
    drop-shadow(0 0 6px var(--bullet-glow, rgba(97, 175, 239, 0.35)));
  transform-style: preserve-3d;
  will-change: transform, filter;
  transition:
    transform 0.12s ease-out,
    filter 0.2s ease;
}

.bullet-mark.is-interactive {
  filter:
    drop-shadow(0 3px 3px rgba(0, 0, 0, 0.7))
    drop-shadow(0 0 9px var(--bullet-glow, rgba(97, 175, 239, 0.5)));
}

.bullet-layer {
  position: absolute;
  z-index: 1;
  top: 50%;
  left: 50%;
  overflow: visible;
  transform-origin: center;
  pointer-events: none;
}

.bullet-layer-image {
  object-fit: contain;
  user-select: none;
}
</style>
