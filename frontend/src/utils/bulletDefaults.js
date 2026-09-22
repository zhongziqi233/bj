import { getShape } from './bulletShapes'

export const KIND_LABELS = {
  task: '任务',
  event: '事件',
  note: '笔记',
}

export const KIND_ACCENTS = {
  task: '#e5c07b',
  event: '#61afef',
  note: '#c678dd',
}

export const DEFAULT_BULLET_CONFIG = {
  task: {
    layers: [
      {
        id: 'task-dot',
        type: 'preset',
        shape: 'dot',
        size: 38,
        x: 0,
        y: 0,
        rotation: 0,
        opacity: 100,
        fill: '#e5c07b',
        stroke: 'none',
        strokeWidth: 1.8,
      },
    ],
    statuses: {
      completed: {
        layers: [
          {
            id: 'task-completed',
            type: 'preset',
            shape: 'x',
            size: 82,
            x: 0,
            y: 0,
            rotation: 0,
            opacity: 100,
            fill: 'none',
            stroke: '#98c379',
            strokeWidth: 2.1,
          },
        ],
      },
      postponed: {
        layers: [
          {
            id: 'task-postponed',
            type: 'preset',
            shape: 'gt',
            size: 86,
            x: 0,
            y: 0,
            rotation: 0,
            opacity: 100,
            fill: 'none',
            stroke: '#e5c07b',
            strokeWidth: 2.1,
          },
        ],
      },
      migrated: {
        layers: [
          {
            id: 'task-migrated',
            type: 'preset',
            shape: 'lt',
            size: 86,
            x: 0,
            y: 0,
            rotation: 0,
            opacity: 100,
            fill: 'none',
            stroke: '#d19a66',
            strokeWidth: 2.1,
          },
        ],
      },
      scheduled: {
        layers: [
          {
            id: 'task-scheduled',
            type: 'preset',
            shape: 'arrow',
            size: 86,
            x: 0,
            y: 0,
            rotation: 0,
            opacity: 100,
            fill: 'none',
            stroke: '#61afef',
            strokeWidth: 2.1,
          },
        ],
      },
    },
  },
  event: {
    layers: [
      {
        id: 'event-ring',
        type: 'preset',
        shape: 'ring',
        size: 86,
        x: 0,
        y: 0,
        rotation: 0,
        opacity: 100,
        fill: 'none',
        stroke: '#61afef',
        strokeWidth: 1.9,
      },
    ],
  },
  note: {
    layers: [
      {
        id: 'note-line',
        type: 'preset',
        shape: 'line',
        size: 86,
        x: 0,
        y: 0,
        rotation: 0,
        opacity: 100,
        fill: 'none',
        stroke: '#c678dd',
        strokeWidth: 2.1,
      },
    ],
  },
}

let layerCounter = 0

export function createLayerId(prefix = 'layer') {
  layerCounter += 1
  return `${prefix}-${Date.now().toString(36)}-${layerCounter.toString(36)}`
}

export function cloneBulletConfig(config = DEFAULT_BULLET_CONFIG) {
  const cloned = JSON.parse(JSON.stringify(config))
  Object.keys(cloned).forEach((kind) => {
    cloned[kind].layers.forEach((layer) => {
      layer.id = createLayerId(kind)
    })
    Object.keys(cloned[kind].statuses || {}).forEach((status) => {
      cloned[kind].statuses[status].layers.forEach((layer) => {
        layer.id = createLayerId(`${kind}-${status}`)
      })
    })
  })
  return cloned
}

export const TASK_STATUS_OPTIONS = [
  { label: '待办', value: 'open' },
  { label: '完成', value: 'completed' },
  { label: '推迟', value: 'postponed' },
  { label: '迁移', value: 'migrated' },
  { label: '已安排', value: 'scheduled' },
]

export function createPresetLayer(shapeKey, color) {
  const shape = getShape(shapeKey)
  return {
    id: createLayerId('preset'),
    type: 'preset',
    shape: shape.key,
    size: 90,
    x: 0,
    y: 0,
    rotation: 0,
    opacity: 100,
    fill: shape.mode === 'fill' ? color : 'none',
    stroke: shape.mode === 'stroke' ? color : 'none',
    strokeWidth: 2,
  }
}
