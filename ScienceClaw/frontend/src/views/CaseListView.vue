<template>
  <div class="case-list-view">
    <div class="case-list-view__header">
      <h1>{{ t('cases.title') }}</h1>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        {{ t('cases.create') }}
      </el-button>
    </div>

    <!-- Filters -->
    <div class="case-list-view__filters">
      <el-select v-model="filterStatus" :placeholder="t('cases.filterStatus')" clearable>
        <el-option :label="t('cases.status.pending')" value="pending" />
        <el-option :label="t('cases.status.running')" value="running" />
        <el-option :label="t('cases.status.completed')" value="completed" />
        <el-option :label="t('cases.status.failed')" value="failed" />
      </el-select>
      <el-input
        v-model="searchQuery"
        :placeholder="t('cases.search')"
        clearable
        style="width: 300px"
      >
        <template #prefix>
          <el-icon><Search /></el-icon>
        </template>
      </el-input>
    </div>

    <!-- Table -->
    <el-table
      v-loading="loading"
      :data="filteredCases"
      stripe
      style="width: 100%"
      @row-click="handleRowClick"
    >
      <el-table-column :label="t('cases.columns.id')" width="200">
        <template #default="{ row }">
          <code>{{ row.id.slice(0, 8) }}...</code>
        </template>
      </el-table-column>
      <el-table-column :label="t('cases.columns.targetRepo')" prop="target_repo" />
      <el-table-column :label="t('cases.columns.status')" width="120">
        <template #default="{ row }">
          <el-tag :type="statusType(row.status)">
            {{ row.status }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column :label="t('cases.columns.createdAt')" width="180">
        <template #default="{ row }">
          {{ formatDate(row.created_at) }}
        </template>
      </el-table-column>
      <el-table-column :label="t('cases.columns.actions')" width="120" fixed="right">
        <template #default="{ row }">
          <el-button
            type="danger"
            size="small"
            circle
            @click.stop="handleDelete(row)"
          >
            <el-icon><Delete /></el-icon>
          </el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- Pagination -->
    <div class="case-list-view__pagination">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="totalCount"
        :page-sizes="[10, 20, 50]"
        layout="total, sizes, prev, pager, next"
      />
    </div>

    <!-- Create Dialog -->
    <el-dialog
      v-model="showCreateDialog"
      :title="t('cases.createTitle')"
      width="500px"
    >
      <el-form :model="createForm" label-width="120px">
        <el-form-item :label="t('cases.form.targetRepo')" required>
          <el-input v-model="createForm.target_repo" placeholder="linux-riscv" />
        </el-form-item>
        <el-form-item :label="t('cases.form.inputContext')">
          <el-input
            v-model="createForm.input_context"
            type="textarea"
            :rows="4"
            :placeholder="t('cases.form.inputContextPlaceholder')"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showCreateDialog = false">{{ t('common.cancel') }}</el-button>
        <el-button type="primary" :loading="creating" @click="handleCreate">
          {{ t('common.create') }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { Plus, Search, Delete } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { listCases, createCase, deleteCase } from '@/api/cases'
import type { Case, CreateCaseRequest } from '@/types/case'

const { t } = useI18n()
const router = useRouter()

// State
const cases = ref<Case[]>([])
const loading = ref(false)
const page = ref(1)
const pageSize = ref(10)
const totalCount = ref(0)
const filterStatus = ref('')
const searchQuery = ref('')
const showCreateDialog = ref(false)
const creating = ref(false)
let refreshTimer: ReturnType<typeof setInterval> | null = null

const createForm = ref<CreateCaseRequest>({
  target_repo: '',
  input_context: {},
})

// Computed
const filteredCases = computed(() => {
  let result = cases.value
  if (filterStatus.value) {
    result = result.filter(c => c.status === filterStatus.value)
  }
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    result = result.filter(c =>
      c.target_repo.toLowerCase().includes(query) ||
      c.id.toLowerCase().includes(query)
    )
  }
  return result
})

// Methods
const statusType = (status: string) => {
  switch (status) {
    case 'completed': return 'success'
    case 'running': return 'primary'
    case 'failed': return 'danger'
    case 'pending': return 'info'
    default: return 'info'
  }
}

const formatDate = (timestamp: number) => {
  return new Date(timestamp * 1000).toLocaleString()
}

const fetchCases = async () => {
  loading.value = true
  try {
    const response = await listCases({
      page: page.value,
      limit: pageSize.value,
      status: filterStatus.value || undefined,
    })
    cases.value = response.cases
    totalCount.value = response.total
  } catch (error) {
    ElMessage.error(t('cases.fetchError'))
  } finally {
    loading.value = false
  }
}

const handleCreate = async () => {
  if (!createForm.value.target_repo) {
    ElMessage.warning(t('cases.form.targetRepoRequired'))
    return
  }
  creating.value = true
  try {
    await createCase(createForm.value)
    ElMessage.success(t('cases.createSuccess'))
    showCreateDialog.value = false
    createForm.value = { target_repo: '', input_context: {} }
    await fetchCases()
  } catch (error) {
    ElMessage.error(t('cases.createError'))
  } finally {
    creating.value = false
  }
}

const handleDelete = async (row: Case) => {
  try {
    await ElMessageBox.confirm(
      t('cases.deleteConfirm', { id: row.id.slice(0, 8) }),
      t('common.confirm'),
      { type: 'warning' }
    )
    await deleteCase(row.id)
    ElMessage.success(t('cases.deleteSuccess'))
    await fetchCases()
  } catch {
    // Cancelled
  }
}

const handleRowClick = (row: Case) => {
  router.push(`/cases/${row.id}`)
}

// Lifecycle
onMounted(() => {
  fetchCases()
  refreshTimer = setInterval(fetchCases, 30000)
})

onUnmounted(() => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
  }
})
</script>

<style scoped>
.case-list-view {
  padding: 24px;
}

.case-list-view__header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.case-list-view__header h1 {
  margin: 0;
}

.case-list-view__filters {
  display: flex;
  gap: 16px;
  margin-bottom: 24px;
}

.case-list-view__pagination {
  margin-top: 24px;
  display: flex;
  justify-content: flex-end;
}
</style>
