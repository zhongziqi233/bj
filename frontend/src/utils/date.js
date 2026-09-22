import dayjs from 'dayjs'

export function today() {
  return dayjs().format('YYYY-MM-DD')
}

export function currentMonth() {
  return dayjs().format('YYYY-MM')
}

export function formatDate(value) {
  return value ? dayjs(value).format('YYYY-MM-DD') : ''
}

export function formatMonth(value) {
  return value ? dayjs(value).format('YYYY-MM') : ''
}

export function formatDateTime(value) {
  return value ? dayjs(value).format('YYYY-MM-DD HH:mm') : ''
}

