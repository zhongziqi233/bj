<template>
  <div class="auth-page">
    <el-card class="auth-card surface-card" shadow="never">
      <div class="auth-brand">
        <h1>欢迎回来</h1>
        <p>用子弹笔记理清今天、这个月和更长远的计划。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名或邮箱" prop="identifier">
          <el-input v-model="form.identifier" size="large" placeholder="请输入用户名或邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            placeholder="请输入密码"
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="submit-button" :loading="loading" @click="submit">
          登录
        </el-button>
      </el-form>

      <div class="auth-footer">
        还没有账号？
        <router-link to="/register">立即注册</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { getApiError } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  identifier: '',
  password: '',
})

const rules = {
  identifier: [{ required: true, message: '请输入用户名或邮箱', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await auth.login(form)
    ElMessage.success('登录成功')
    router.replace(route.query.redirect || '/today')
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.submit-button {
  width: 100%;
  margin-top: 6px;
}

a {
  margin-left: 5px;
  color: var(--od-blue);
  font-weight: 700;
  text-decoration: none;
  transition:
    color 0.2s ease,
    text-shadow 0.2s ease;
}

a:hover {
  color: var(--od-cyan);
  text-shadow: 0 0 16px rgba(86, 182, 194, 0.42);
}
</style>
