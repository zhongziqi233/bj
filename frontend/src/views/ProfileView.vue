<template>
  <div class="page-shell profile-page">
    <div class="page-heading">
      <div>
        <h1 class="page-title">个人设置</h1>
        <p class="page-subtitle">查看账号信息并修改登录密码。</p>
      </div>
    </div>

    <div class="profile-grid">
      <el-card class="surface-card profile-card" shadow="never">
        <template #header>
          <div class="card-header">账号信息</div>
        </template>
        <el-descriptions :column="1" border>
          <el-descriptions-item label="用户名">{{ auth.user?.username }}</el-descriptions-item>
          <el-descriptions-item label="邮箱">{{ auth.user?.email }}</el-descriptions-item>
          <el-descriptions-item label="角色">
            <el-tag :type="auth.isAdmin ? 'warning' : 'info'" effect="plain">
              {{ auth.isAdmin ? '管理员' : '普通用户' }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="注册时间">
            {{ formatDateTime(auth.user?.created_at) }}
          </el-descriptions-item>
        </el-descriptions>
      </el-card>

      <el-card class="surface-card profile-card" shadow="never">
        <template #header>
          <div class="card-header">修改密码</div>
        </template>
        <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
          <el-form-item label="原密码" prop="old_password">
            <el-input v-model="form.old_password" type="password" show-password />
          </el-form-item>
          <el-form-item label="新密码" prop="new_password">
            <el-input v-model="form.new_password" type="password" show-password placeholder="至少 8 位" />
          </el-form-item>
          <el-form-item label="确认新密码" prop="confirm_password">
            <el-input v-model="form.confirm_password" type="password" show-password />
          </el-form-item>
          <el-button type="primary" :loading="saving" @click="submit">保存新密码</el-button>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'

import { changePassword } from '@/api/auth'
import { getApiError } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatDateTime } from '@/utils/date'

const auth = useAuthStore()
const formRef = ref()
const saving = ref(false)

const form = reactive({
  old_password: '',
  new_password: '',
  confirm_password: '',
})

const validateConfirm = (_rule, value, callback) => {
  if (value !== form.new_password) {
    callback(new Error('两次输入的新密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  old_password: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为 8 位', trigger: 'blur' },
  ],
  confirm_password: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    { validator: validateConfirm, trigger: 'blur' },
  ],
}

async function submit() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    await changePassword({
      old_password: form.old_password,
      new_password: form.new_password,
    })
    ElMessage.success('密码修改成功')
    formRef.value.resetFields()
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  auth.fetchMe().catch(() => {})
})
</script>

<style scoped>
.profile-grid {
  display: grid;
  grid-template-columns: minmax(300px, 0.8fr) minmax(320px, 1.2fr);
  gap: 18px;
}

.profile-card {
  padding: 4px;
}

.card-header {
  font-weight: 700;
}

@media (max-width: 880px) {
  .profile-grid {
    grid-template-columns: 1fr;
  }
}
</style>

