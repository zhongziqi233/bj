export const BULLET_SHAPES = [
  { key: 'dot', label: '圆点', mode: 'fill', path: 'M12 7.5a4.5 4.5 0 1 0 0 9a4.5 4.5 0 1 0 0-9' },
  { key: 'ring', label: '圆环', mode: 'stroke', path: 'M12 3.5a8.5 8.5 0 1 0 0 17a8.5 8.5 0 1 0 0-17' },
  { key: 'circle', label: '实心圆', mode: 'fill', path: 'M12 3.5a8.5 8.5 0 1 0 0 17a8.5 8.5 0 1 0 0-17' },
  { key: 'square', label: '方形', mode: 'fill', path: 'M5 5h14v14H5z' },
  { key: 'rounded', label: '圆角方形', mode: 'fill', path: 'M7 4h10a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3H7a3 3 0 0 1-3-3V7a3 3 0 0 1 3-3z' },
  { key: 'diamond', label: '菱形', mode: 'fill', path: 'M12 3l9 9-9 9-9-9 9-9z' },
  { key: 'triangle', label: '三角', mode: 'fill', path: 'M12 4l9 16H3l9-16z' },
  { key: 'hexagon', label: '六边形', mode: 'fill', path: 'M12 3l7.8 4.5v9L12 21l-7.8-4.5v-9L12 3z' },
  { key: 'star', label: '星形', mode: 'fill', path: 'M12 3.5l2.6 5.3 5.9.9-4.3 4.1 1 5.8-5.2-2.7-5.2 2.7 1-5.8-4.3-4.1 5.9-.9L12 3.5z' },
  { key: 'sparkle', label: '闪光', mode: 'fill', path: 'M12 2l1.8 6.2L20 10l-6.2 1.8L12 18l-1.8-6.2L4 10l6.2-1.8L12 2z' },
  { key: 'cross', label: '十字', mode: 'fill', path: 'M10 3h4v7h7v4h-7v7h-4v-7H3v-4h7V3z' },
  { key: 'plus', label: '加号', mode: 'stroke', path: 'M12 5v14M5 12h14' },
  { key: 'x', label: '叉号', mode: 'stroke', path: 'M6 6l12 12M18 6L6 18' },
  { key: 'gt', label: '大于号', mode: 'stroke', path: 'M9 5l7 7-7 7' },
  { key: 'lt', label: '小于号', mode: 'stroke', path: 'M15 5l-7 7 7 7' },
  { key: 'slash', label: '斜线', mode: 'stroke', path: 'M5 19L19 5' },
  { key: 'backslash', label: '反斜线', mode: 'stroke', path: 'M5 5l14 14' },
  { key: 'line', label: '横线', mode: 'stroke', path: 'M4 12h16' },
  { key: 'heart', label: '心形', mode: 'fill', path: 'M12 20s-7-4.4-9.3-8.2C.8 8.9 2.4 5 6 5c2 0 3.4 1.1 4 2.1C10.6 6.1 12 5 14 5c3.6 0 5.2 3.9 3.3 6.8C19 15.6 12 20 12 20z' },
  { key: 'flower', label: '花朵', mode: 'fill', path: 'M12 4c1.7 0 3 1.3 3 3 1.7 0 3 1.3 3 3s-1.3 3-3 3c0 1.7-1.3 3-3 3s-3-1.3-3-3c-1.7 0-3-1.3-3-3s1.3-3 3-3c0-1.7 1.3-3 3-3z' },
  { key: 'bolt', label: '闪电', mode: 'fill', path: 'M13 2L4 14h7l-1 8 9-12h-7l1-8z' },
  { key: 'moon', label: '月亮', mode: 'fill', path: 'M20 15.5A8.5 8.5 0 0 1 8.5 4A8.5 8.5 0 1 0 20 15.5z' },
  { key: 'sun', label: '太阳', mode: 'stroke', path: 'M12 4V2M12 22v-2M4 12H2M22 12h-2M5.6 5.6L4.2 4.2M19.8 19.8l-1.4-1.4M18.4 5.6l1.4-1.4M4.2 19.8l1.4-1.4M12 7a5 5 0 1 0 0 10a5 5 0 0 0 0-10z' },
  { key: 'eye', label: '眼睛', mode: 'stroke', path: 'M2 12s3.5-6 10-6 10 6 10 6-3.5 6-10 6S2 12 2 12zM12 9a3 3 0 1 0 0 6a3 3 0 0 0 0-6z' },
  { key: 'check', label: '勾选', mode: 'stroke', path: 'M4 12l5 5L20 6' },
  { key: 'arrow', label: '箭头', mode: 'stroke', path: 'M4 12h14M13 7l5 5-5 5' },
  { key: 'crown', label: '皇冠', mode: 'fill', path: 'M3 8l4 4 5-7 5 7 4-4v10H3V8z' },
  { key: 'gem', label: '宝石', mode: 'fill', path: 'M6 3h12l3 6-9 12L3 9l6-6z' },
  { key: 'leaf', label: '叶子', mode: 'stroke', path: 'M20 4C10 4 4 9 4 16c0 2 1 4 2 4 0-7 5-11 14-12-2 4-6 7-11 8' },
  { key: 'cloud', label: '云朵', mode: 'fill', path: 'M7 18h10a4 4 0 0 0 0-8 6 6 0 0 0-11.3 2A3.5 3.5 0 0 0 7 18z' },
  { key: 'drop', label: '水滴', mode: 'fill', path: 'M12 3s6 6.5 6 11a6 6 0 0 1-12 0c0-4.5 6-11 6-11z' },
]

export const SHAPE_MAP = Object.fromEntries(BULLET_SHAPES.map((shape) => [shape.key, shape]))
export const SHAPE_PATHS = Object.fromEntries(
  BULLET_SHAPES.map((shape) => [shape.key, shape.path]),
)

export function getShape(key) {
  return SHAPE_MAP[key] || SHAPE_MAP.dot
}
