<template>
  <div class="auth-page">
    <el-card class="auth-card surface-card" shadow="never">
      <div class="auth-brand">
        <h1>创建账号</h1>
        <p>注册后即可开始记录每日、每月和未来计划。</p>
      </div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" size="large" placeholder="3-50 个字符，不能包含空格" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" size="large" placeholder="用于登录" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" size="large" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input
            v-model="form.confirmPassword"
            size="large"
            type="password"
            show-password
            placeholder="再次输入密码"
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-button type="primary" size="large" class="submit-button" :loading="loading" @click="submit">
          注册并登录
        </el-button>
      </el-form>

      <div class="auth-footer">
        已有账号？
        <router-link to="/login">返回登录</router-link>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'

import { getApiError } from '@/api/http'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const auth = useAuthStore()

const formRef = ref()
const loading = ref(false)
const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
})

const validateConfirm = (_rule, value, callback) => {
  if (value !== form.password) {
    callback(new Error('两次输入的密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度需为 3-50 个字符', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为 8 位', trigger: 'blur' },
  ],
  confirmPassword: [
    { required: true, message: '请再次输入密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  loading.value = true
  try {
    await auth.register({
      username: form.username,
      email: form.email,
      password: form.password,
    })
    ElMessage.success('注册成功')
    router.replace('/today')
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
