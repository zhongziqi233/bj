import { createRouter, createWebHistory } from 'vue-router'

import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/login',
    name: 'login',
    component: () => import('@/views/LoginView.vue'),
    meta: { public: true, title: '登录' },
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/views/RegisterView.vue'),
    meta: { public: true, title: '注册' },
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        redirect: '/today',
      },
      {
        path: 'today',
        name: 'today',
        component: () => import('@/views/TodayView.vue'),
        meta: { title: '每日日志' },
      },
      {
        path: 'monthly',
        name: 'monthly',
        component: () => import('@/views/MonthlyView.vue'),
        meta: { title: '月度日志' },
      },
      {
        path: 'future',
        name: 'future',
        component: () => import('@/views/FutureView.vue'),
        meta: { title: '未来日志' },
      },
      {
        path: 'collections',
        name: 'collections',
        component: () => import('@/views/CollectionsView.vue'),
        meta: { title: '自定义集合' },
      },
      {
        path: 'bullet-style',
        name: 'bullet-style',
        component: () => import('@/views/BulletStyleView.vue'),
        meta: { title: '自定义子弹' },
      },
      {
        path: 'collections/:id',
        name: 'collection-detail',
        component: () => import('@/views/CollectionDetailView.vue'),
        meta: { title: '集合详情' },
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { title: '个人设置' },
      },
      {
        path: 'admin/users',
        name: 'admin-users',
        component: () => import('@/views/AdminUsersView.vue'),
        meta: { title: '用户管理', requiresAdmin: true },
      },
    ],
  },
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue'),
    meta: { public: true, title: '页面不存在' },
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  if (!auth.ready) {
    await auth.ensureReady()
  }

  if (to.meta.requiresAuth && !auth.isAuthenticated) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.requiresAdmin && !auth.isAdmin) {
    return { name: 'today' }
  }
  if (to.meta.public && auth.isAuthenticated && ['login', 'register'].includes(to.name)) {
    return { name: 'today' }
  }
  return true
})

router.afterEach((to) => {
  document.title = to.meta.title ? `${to.meta.title} · 子弹笔记` : '子弹笔记'
})

export default router
