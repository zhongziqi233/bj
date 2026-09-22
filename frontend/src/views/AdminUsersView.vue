<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <h1 class="page-title">用户管理</h1>
        <p class="page-subtitle">管理员可以查看用户、启用或禁用账号、调整角色和重置密码。</p>
      </div>
    </div>

    <el-card class="surface-card admin-table-card" shadow="never">
      <div class="table-toolbar">
        <el-input
          v-model="search"
          class="search-input"
          clearable
          placeholder="搜索用户名或邮箱"
          :prefix-icon="Search"
          @keyup.enter="handleSearch"
          @clear="handleSearch"
        />
        <el-button type="primary" @click="handleSearch">搜索</el-button>
      </div>

      <el-table v-loading="loading" :data="users" row-key="id" style="width: 100%">
        <el-table-column prop="username" label="用户名" min-width="130" />
        <el-table-column prop="email" label="邮箱" min-width="210" />
        <el-table-column label="注册时间" min-width="160">
          <template #default="{ row }">{{ formatDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column label="角色" width="110" align="center">
          <template #default="{ row }">
            <div class="switch-cell">
              <el-switch
                :model-value="row.is_admin"
                :disabled="row.id === auth.user?.id"
                @change="(value) => toggleUser(row, 'is_admin', value)"
              />
              <span>{{ row.is_admin ? '管理员' : '用户' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="状态" width="110" align="center">
          <template #default="{ row }">
            <div class="switch-cell">
              <el-switch
                :model-value="row.is_active"
                :disabled="row.id === auth.user?.id"
                active-color="var(--od-green)"
                inactive-color="var(--od-text-dim)"
                @change="(value) => toggleUser(row, 'is_active', value)"
              />
              <span>{{ row.is_active ? '启用' : '禁用' }}</span>
            </div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="180" fixed="right" align="right">
          <template #default="{ row }">
            <el-button text type="primary" @click="openResetPassword(row)">重置密码</el-button>
            <el-button
              text
              type="danger"
              :disabled="row.id === auth.user?.id"
              @click="removeUser(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>

      <div class="pagination-row">
        <el-pagination
          v-model:current-page="page"
          v-model:page-size="pageSize"
          :total="total"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          @current-change="loadUsers"
          @size-change="handleSizeChange"
        />
      </div>
    </el-card>

    <el-dialog v-model="resetDialogVisible" title="重置用户密码" width="420px">
      <p class="dialog-tip">
        即将重置用户 <strong>{{ resetTarget?.username }}</strong> 的密码。
      </p>
      <el-form ref="resetFormRef" :model="resetForm" :rules="resetRules" label-position="top">
        <el-form-item label="新密码" prop="new_password">
          <el-input v-model="resetForm.new_password" type="password" show-password placeholder="至少 8 位" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="resetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="resetting" @click="submitResetPassword">确认重置</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search } from '@element-plus/icons-vue'

import { deleteUser, listUsers, resetUserPassword, updateUser } from '@/api/users'
import { getApiError } from '@/api/http'
import { useAuthStore } from '@/stores/auth'
import { formatDateTime } from '@/utils/date'

const auth = useAuthStore()
const users = ref([])
const loading = ref(false)
const search = ref('')
const page = ref(1)
const pageSize = ref(10)
const total = ref(0)

const resetDialogVisible = ref(false)
const resetting = ref(false)
const resetTarget = ref(null)
const resetFormRef = ref()
const resetForm = reactive({ new_password: '' })
const resetRules = {
  new_password: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 8, message: '密码长度至少为 8 位', trigger: 'blur' },
  ],
}

async function loadUsers() {
  loading.value = true
  try {
    const { data } = await listUsers({
      page: page.value,
      page_size: pageSize.value,
      search: search.value.trim(),
    })
    users.value = data.items
    total.value = data.total
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    loading.value = false
  }
}

function handleSearch() {
  page.value = 1
  loadUsers()
}

function handleSizeChange() {
  page.value = 1
  loadUsers()
}

async function toggleUser(user, field, value) {
  try {
    const payload = { [field]: value }
    await updateUser(user.id, payload)
    ElMessage.success('用户信息已更新')
    loadUsers()
  } catch (error) {
    ElMessage.error(getApiError(error))
    loadUsers()
  }
}

function openResetPassword(user) {
  resetTarget.value = user
  resetForm.new_password = ''
  resetDialogVisible.value = true
  resetFormRef.value?.clearValidate()
}

async function submitResetPassword() {
  const valid = await resetFormRef.value.validate().catch(() => false)
  if (!valid) return

  resetting.value = true
  try {
    await resetUserPassword(resetTarget.value.id, resetForm.new_password)
    ElMessage.success('密码已重置')
    resetDialogVisible.value = false
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    resetting.value = false
  }
}

async function removeUser(user) {
  try {
    await ElMessageBox.confirm(
      `删除用户“${user.username}”会同时删除该用户的日志和集合，确定继续吗？`,
      '删除用户',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
      },
    )
    await deleteUser(user.id)
    ElMessage.success('用户已删除')
    if (users.value.length === 1 && page.value > 1) {
      page.value -= 1
    }
    loadUsers()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getApiError(error))
    }
  }
}

onMounted(loadUsers)
</script>

<style scoped>
.table-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}

.search-input {
  max-width: 340px;
}

.pagination-row {
  display: flex;
  justify-content: flex-end;
  margin-top: 18px;
}

.dialog-tip {
  margin: 0 0 16px;
  color: var(--od-text-muted);
  line-height: 1.6;
}

.switch-cell {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  font-size: 12px;
}
</style>
