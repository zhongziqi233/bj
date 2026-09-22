<template>
  <div class="page-shell">
    <div class="page-heading">
      <div>
        <h1 class="page-title">自定义集合</h1>
        <p class="page-subtitle">用集合整理长期主题，例如读书清单、旅行计划、项目资料或灵感库。</p>
      </div>
      <el-button type="primary" :icon="Plus" @click="openCreate">新建集合</el-button>
    </div>

    <el-skeleton v-if="loading" :rows="5" animated />
    <el-empty v-else-if="!collections.length" description="还没有自定义集合" />
    <div v-else class="collection-grid">
      <article
        v-for="collection in collections"
        :key="collection.id"
        class="surface-card collection-card"
        @click="router.push(`/collections/${collection.id}`)"
      >
        <div class="collection-card-top">
          <el-icon class="collection-icon"><FolderOpened /></el-icon>
          <el-dropdown trigger="click" @click.stop>
            <el-button text circle aria-label="集合操作">
              <el-icon><MoreFilled /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="openEdit(collection)">编辑</el-dropdown-item>
                <el-dropdown-item divided @click="removeCollection(collection)">删除</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
        <h3>{{ collection.name }}</h3>
        <p>{{ collection.description || '暂无描述' }}</p>
        <div class="collection-card-footer">
          <span>{{ collection.entry_count }} 条记录</span>
          <span>打开 →</span>
        </div>
      </article>
    </div>

    <el-dialog v-model="dialogVisible" :title="editingId ? '编辑集合' : '新建集合'" width="460px">
      <el-form ref="formRef" :model="form" :rules="rules" label-position="top">
        <el-form-item label="集合名称" prop="name">
          <el-input v-model="form.name" maxlength="100" show-word-limit placeholder="例如：2026 阅读清单" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="form.description"
            type="textarea"
            :rows="3"
            maxlength="500"
            show-word-limit
            placeholder="这个集合用来记录什么？"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="saveCollection">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { FolderOpened, MoreFilled, Plus } from '@element-plus/icons-vue'

import {
  createCollection,
  deleteCollection,
  listCollections,
  updateCollection,
} from '@/api/collections'
import { getApiError } from '@/api/http'

const router = useRouter()
const collections = ref([])
const loading = ref(false)
const saving = ref(false)
const dialogVisible = ref(false)
const editingId = ref(null)
const formRef = ref()

const form = reactive({
  name: '',
  description: '',
})

const rules = {
  name: [{ required: true, message: '请输入集合名称', trigger: 'blur' }],
}

async function loadCollections() {
  loading.value = true
  try {
    const { data } = await listCollections()
    collections.value = data.items
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    loading.value = false
  }
}

function resetForm() {
  form.name = ''
  form.description = ''
  editingId.value = null
  formRef.value?.clearValidate()
}

function openCreate() {
  resetForm()
  dialogVisible.value = true
}

function openEdit(collection) {
  resetForm()
  editingId.value = collection.id
  form.name = collection.name
  form.description = collection.description
  dialogVisible.value = true
}

async function saveCollection() {
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  saving.value = true
  try {
    if (editingId.value) {
      await updateCollection(editingId.value, form)
    } else {
      await createCollection(form)
    }
    ElMessage.success(editingId.value ? '集合已更新' : '集合已创建')
    dialogVisible.value = false
    loadCollections()
  } catch (error) {
    ElMessage.error(getApiError(error))
  } finally {
    saving.value = false
  }
}

async function removeCollection(collection) {
  try {
    await ElMessageBox.confirm(
      `删除“${collection.name}”会同时删除里面的记录，确定继续吗？`,
      '删除集合',
      {
        type: 'warning',
        confirmButtonText: '删除',
        cancelButtonText: '取消',
      },
    )
    await deleteCollection(collection.id)
    ElMessage.success('集合已删除')
    loadCollections()
  } catch (error) {
    if (error !== 'cancel' && error !== 'close') {
      ElMessage.error(getApiError(error))
    }
  }
}

onMounted(loadCollections)
</script>

<style scoped>
.collection-card-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.collection-icon {
  color: var(--od-blue);
  font-size: 24px;
  filter: drop-shadow(0 0 10px rgba(97, 175, 239, 0.45));
}
</style>
