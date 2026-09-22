<template>
  <el-container class="app-layout">
    <el-aside class="app-aside" width="236px">
      <div class="brand">
        <div class="brand-mark">•</div>
        <div>
          <div class="brand-name">子弹笔记</div>
          <div class="brand-caption">Bullet Journal</div>
        </div>
      </div>

      <el-menu :default-active="route.path" router class="app-menu">
        <el-menu-item index="/today">
          <el-icon><Sunny /></el-icon>
          <span>每日日志</span>
        </el-menu-item>
        <el-menu-item index="/monthly">
          <el-icon><Calendar /></el-icon>
          <span>月度日志</span>
        </el-menu-item>
        <el-menu-item index="/future">
          <el-icon><Collection /></el-icon>
          <span>未来日志</span>
        </el-menu-item>
        <el-menu-item index="/collections">
          <el-icon><FolderOpened /></el-icon>
          <span>自定义集合</span>
        </el-menu-item>
        <el-menu-item index="/bullet-style">
          <el-icon><Brush /></el-icon>
          <span>自定义子弹</span>
        </el-menu-item>
        <el-menu-item v-if="auth.isAdmin" index="/admin/users">
          <el-icon><UserFilled /></el-icon>
          <span>用户管理</span>
        </el-menu-item>
      </el-menu>

      <div class="aside-note">
        <div class="aside-note-title">快速记录法</div>
        <p><BulletMark kind="task" :size="14" /> 任务</p>
        <p><BulletMark kind="event" :size="14" /> 事件</p>
        <p><BulletMark kind="note" :size="14" /> 笔记</p>
        <div class="aside-note-subtitle">任务状态</div>
        <p><BulletMark kind="task" status="postponed" :size="14" /> 推迟到明天 </p>
        <p><BulletMark kind="task" status="migrated" :size="14" /> 迁移到指定日期 </p>
        <p><BulletMark kind="task" status="completed" :size="14" /> 任务完成 </p>
      </div>
    </el-aside>

    <el-container class="app-content">
      <el-header class="app-header">
        <div>
          <div class="header-title">{{ route.meta.title || '子弹笔记' }}</div>
          <div class="header-date">{{ formattedToday }}</div>
        </div>
        <el-dropdown @command="handleCommand">
          <button class="user-trigger">
            <span class="user-avatar">{{ auth.user?.username?.slice(0, 1).toUpperCase() }}</span>
            <span class="user-name">{{ auth.user?.username }}</span>
            <el-icon><ArrowDown /></el-icon>
          </button>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">个人设置</el-dropdown-item>
              <el-dropdown-item v-if="auth.isAdmin" command="admin">用户管理</el-dropdown-item>
              <el-dropdown-item divided command="logout">退出登录</el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </el-header>

      <el-main class="app-main">
        <router-view v-slot="{ Component, route }">
          <transition name="page-fade" mode="out-in">
            <component :is="Component" :key="route.fullPath" />
          </transition>
        </router-view>
      </el-main>
    </el-container>
  </el-container>
</template>

<script setup>
import { computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import dayjs from 'dayjs'
import {
  ArrowDown,
  Brush,
  Calendar,
  Collection,
  FolderOpened,
  Sunny,
  UserFilled,
} from '@element-plus/icons-vue'

import BulletMark from '@/components/BulletMark.vue'
import { useAuthStore } from '@/stores/auth'
import { useBulletStyleStore } from '@/stores/bulletStyle'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()
const bulletStyle = useBulletStyleStore()

const formattedToday = computed(() => dayjs().format('YYYY年MM月DD日 dddd'))

onMounted(() => {
  bulletStyle.load().catch(() => {})
})

function handleCommand(command) {
  if (command === 'profile') {
    router.push('/profile')
  } else if (command === 'admin') {
    router.push('/admin/users')
  } else if (command === 'logout') {
    auth.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.app-layout {
  min-height: 100vh;
  background: transparent;
}

.app-aside {
  position: relative;
  isolation: isolate;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  padding: 22px 14px;
  border-right: 1px solid var(--od-border);
  background:
    linear-gradient(180deg, rgba(33, 37, 43, 0.98), rgba(27, 31, 36, 0.98)),
    var(--od-bg-deep);
  color: var(--od-text-strong);
  box-shadow: 14px 0 40px rgba(0, 0, 0, 0.22);
}

.app-aside::before {
  position: absolute;
  top: -90px;
  left: -90px;
  width: 240px;
  height: 240px;
  border-radius: 50%;
  background: radial-gradient(circle, rgba(97, 175, 239, 0.22), transparent 70%);
  filter: blur(14px);
  pointer-events: none;
  content: "";
  z-index: -1;
  animation: floatOrb 10s ease-in-out infinite;
}

.brand {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 10px 26px;
}

.brand-mark {
  display: grid;
  width: 38px;
  height: 38px;
  place-items: center;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--od-blue), var(--od-purple));
  color: #1b1f24;
  font-size: 24px;
  font-weight: 900;
  line-height: 1;
  box-shadow:
    0 0 0 1px rgba(97, 175, 239, 0.25),
    0 0 24px rgba(97, 175, 239, 0.24);
  animation: markPulse 4s ease-in-out infinite;
}

.brand-name {
  color: var(--od-text-strong);
  font-size: 17px;
  font-weight: 750;
  letter-spacing: 0.04em;
}

.brand-caption {
  margin-top: 2px;
  color: var(--od-text-dim);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.app-menu {
  border-right: 0;
  background: transparent;
}

.app-menu :deep(.el-menu-item) {
  height: 46px;
  margin: 4px 0;
  border-radius: 12px;
  color: var(--od-text);
  transition:
    color 0.2s ease,
    background-color 0.2s ease,
    transform 0.2s ease,
    box-shadow 0.2s ease;
}

.app-menu :deep(.el-menu-item:hover) {
  background: rgba(97, 175, 239, 0.1);
  color: var(--od-blue);
  transform: translateX(4px);
}

.app-menu :deep(.el-menu-item.is-active) {
  background: linear-gradient(90deg, rgba(97, 175, 239, 0.2), rgba(198, 120, 221, 0.08));
  color: var(--od-blue);
  font-weight: 700;
  box-shadow:
    inset 3px 0 0 0 var(--od-blue),
    0 0 24px rgba(97, 175, 239, 0.12);
}

.aside-note {
  margin-top: auto;
  padding: 18px 12px;
  border-top: 1px solid var(--od-border);
  color: var(--od-text-dim);
  font-size: 12px;
}

.aside-note-title {
  margin-bottom: 10px;
  color: var(--od-text-strong);
  font-weight: 700;
}

.aside-note-subtitle {
  margin-top: 14px;
  margin-bottom: 8px;
  color: var(--od-text-strong);
  font-weight: 700;
}

.aside-note p {
  margin: 7px 0;
}

.aside-note :deep(.bullet-mark) {
  margin-right: 6px;
}

.app-content {
  min-width: 0;
}

.app-header {
  position: relative;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 82px;
  padding: 0 34px;
  border-bottom: 1px solid var(--od-border);
  background: rgba(33, 37, 43, 0.78);
  box-shadow: 0 12px 34px rgba(0, 0, 0, 0.18);
  backdrop-filter: blur(18px);
}

.app-header::after {
  position: absolute;
  right: 0;
  bottom: -1px;
  left: 0;
  height: 1px;
  background: linear-gradient(
    90deg,
    transparent,
    rgba(97, 175, 239, 0.75),
    rgba(198, 120, 221, 0.7),
    transparent
  );
  background-size: 200% 100%;
  pointer-events: none;
  content: "";
  animation: headerGlow 6s linear infinite;
}

.header-title {
  color: var(--od-text-strong);
  font-size: 20px;
  font-weight: 750;
}

.header-date {
  margin-top: 4px;
  color: var(--od-text-dim);
  font-size: 12px;
}

.user-trigger {
  display: flex;
  align-items: center;
  gap: 9px;
  padding: 6px 10px 6px 6px;
  border: 1px solid var(--od-border);
  border-radius: 99px;
  background: rgba(40, 44, 52, 0.86);
  color: var(--od-text-strong);
  cursor: pointer;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.2s ease;
}

.user-trigger:hover {
  transform: translateY(-1px);
  border-color: rgba(97, 175, 239, 0.55);
  box-shadow: 0 0 24px rgba(97, 175, 239, 0.16);
}

.user-avatar {
  display: grid;
  width: 30px;
  height: 30px;
  place-items: center;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--od-blue), var(--od-purple));
  color: #1b1f24;
  font-size: 13px;
  font-weight: 800;
  box-shadow: 0 0 18px rgba(97, 175, 239, 0.24);
}

.user-name {
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 13px;
  font-weight: 650;
}

.app-main {
  padding: 30px 34px 46px;
  background: transparent;
}

@media (max-width: 820px) {
  .app-aside {
    width: 72px !important;
    padding: 18px 8px;
  }

  .brand {
    justify-content: center;
    padding: 0 0 20px;
  }

  .brand > div:last-child,
  .app-menu span,
  .aside-note {
    display: none;
  }

  .app-menu :deep(.el-menu-item) {
    justify-content: center;
    padding: 0 !important;
  }

  .app-header,
  .app-main {
    padding-right: 18px;
    padding-left: 18px;
  }
}
</style>
