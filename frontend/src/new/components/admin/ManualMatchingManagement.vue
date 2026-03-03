<template>
  <div class="manual-matching-management">
    <!-- Stats Cards -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="stat-icon pending">
          <span class="material-symbols-outlined">pending</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ pendingCount }}</div>
          <div class="stat-label">待确认</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon confirmed">
          <span class="material-symbols-outlined">check_circle</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ confirmedCount }}</div>
          <div class="stat-label">已确认</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon total">
          <span class="material-symbols-outlined">database</span>
        </div>
        <div class="stat-info">
          <div class="stat-value">{{ totalCount }}</div>
          <div class="stat-label">总计</div>
        </div>
      </div>
    </div>

    <!-- Filters -->
    <div class="filters">
      <div class="filter-group">
        <label>筛选状态:</label>
        <select v-model="filterStatus" @change="loadData">
          <option value="all">全部</option>
          <option value="pending">待确认</option>
          <option value="confirmed">已确认</option>
        </select>
      </div>
      <div class="filter-group">
        <label>搜索:</label>
        <input
          v-model="searchQuery"
          @input="handleSearch"
          type="text"
          placeholder="搜索原始型号或匹配型号..."
          class="search-input"
        />
      </div>
      <div class="filter-actions">
        <button class="btn-confirm" @click="confirmSelected" :disabled="!hasSelected">
          <span class="material-symbols-outlined">check</span>
          确认选中 ({{ selectedIds.length }})
        </button>
        <button class="btn-delete" @click="deleteSelected" :disabled="!hasSelected">
          <span class="material-symbols-outlined">delete</span>
          删除选中
        </button>
      </div>
    </div>

    <!-- Table -->
    <div class="table-wrapper">
      <div class="table-container">
        <table class="data-table">
        <thead>
          <tr>
            <th class="col-select">
              <input
                type="checkbox"
                :checked="allSelected"
                :indeterminate="someSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th>原始厂商</th>
            <th>原始型号</th>
            <th>匹配后厂商</th>
            <th>匹配后型号</th>
            <th>分类</th>
            <th>价格</th>
            <th>来源</th>
            <th>状态</th>
            <th>创建时间</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="item in paginatedData"
            :key="item.id"
            :class="{ 'row-selected': selectedIds.includes(item.id) }"
          >
            <td class="col-select">
              <input
                type="checkbox"
                :checked="selectedIds.includes(item.id)"
                @change="toggleSelect(item.id)"
              />
            </td>
            <td>{{ item.original_manufacturer }}</td>
            <td class="cell-model">{{ item.original_model }}</td>
            <td>{{ item.matched_manufacturer }}</td>
            <td class="cell-model-matched">{{ item.matched_model_number }}</td>
            <td>{{ formatCategory(item) }}</td>
            <td>{{ item.device_price ? `¥${item.device_price.toFixed(2)}` : '-' }}</td>
            <td>
              <span class="source-badge" :class="item.data_source">
                {{ getSourceLabel(item.data_source) }}
              </span>
            </td>
            <td>
              <span
                class="status-badge"
                :class="item.is_confirmed ? 'confirmed' : 'pending'"
              >
                {{ item.is_confirmed ? '已确认' : '待确认' }}
              </span>
            </td>
            <td class="cell-time">{{ formatDate(item.created_at) }}</td>
            <td class="col-actions">
              <button
                v-if="!item.is_confirmed"
                class="action-btn confirm"
                @click="confirmItem(item.id)"
                title="确认"
              >
                <span class="material-symbols-outlined">check</span>
              </button>
              <button
                class="action-btn delete"
                @click="deleteItem(item.id)"
                title="删除"
              >
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
          <tr v-if="paginatedData.length === 0">
            <td colspan="12" class="no-data">
              <span class="material-symbols-outlined">inbox</span>
              <span>暂无数据</span>
            </td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <div class="pagination-info">
        共 {{ totalCount }} 条，第 {{ currentPage }} / {{ totalPages || 1 }} 页
      </div>
      <div class="pagination-controls">
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage = 1"
          title="首页"
        >
          <span class="material-symbols-outlined">first_page</span>
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
          title="上一页"
        >
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages || totalPages === 0"
          @click="currentPage++"
          title="下一页"
        >
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <button
          class="page-btn"
          :disabled="currentPage === totalPages || totalPages === 0"
          @click="currentPage = totalPages"
          title="末页"
        >
          <span class="material-symbols-outlined">last_page</span>
        </button>
        <select v-model="pageSize" class="page-size-select" @change="handlePageSizeChange">
          <option :value="10">10条/页</option>
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
          <option :value="100">100条/页</option>
        </select>
      </div>
    </div>

    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      <span class="material-symbols-outlined">{{ toast.type === 'success' ? 'check_circle' : 'error' }}</span>
      <span>{{ toast.message }}</span>
    </div>

    <!-- 确认覆盖对话框 -->
    <div v-if="confirmDialog.show" class="dialog-overlay" @click="closeConfirmDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <span class="material-symbols-outlined dialog-icon">warning</span>
          <h3>数据冲突</h3>
        </div>
        <div class="dialog-body">
          <p>检测到已存在相同"原始厂商"+"原始型号"组合的数据：</p>
          <div class="conflict-info" v-if="confirmDialog.existingRecord">
            <div class="conflict-row">
              <span class="conflict-label">原始厂商:</span>
              <span class="conflict-value">{{ confirmDialog.existingRecord.original_manufacturer || '-' }}</span>
            </div>
            <div class="conflict-row">
              <span class="conflict-label">原始型号:</span>
              <span class="conflict-value">{{ confirmDialog.existingRecord.original_model }}</span>
            </div>
            <div class="conflict-row">
              <span class="conflict-label">匹配后型号:</span>
              <span class="conflict-value">{{ confirmDialog.existingRecord.matched_model_number }}</span>
            </div>
          </div>
          <p class="dialog-question">是否要覆盖已有数据？</p>
        </div>
        <div class="dialog-footer">
          <button class="dialog-btn cancel" @click="closeConfirmDialog">
            取消
          </button>
          <button class="dialog-btn ignore" @click="handleConfirmIgnore">
            忽略（删除当前数据）
          </button>
          <button class="dialog-btn override" @click="handleConfirmOverride">
            覆盖
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
const tableData = ref<any[]>([])
const loading = ref(false)
const filterStatus = ref<'all' | 'pending' | 'confirmed'>('all')
const searchQuery = ref('')
const selectedIds = ref<number[]>([])
const currentPage = ref(1)
const pageSize = ref(20)

// Toast state
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// 确认对话框状态
const confirmDialog = ref({
  show: false,
  itemId: null as number | null,
  conflictType: '' as string,
  existingRecord: null as any
})

// Computed
const totalCount = ref(0)

const pendingCount = computed(() =>
  tableData.value.filter(item => !item.is_confirmed).length
)

const confirmedCount = computed(() =>
  tableData.value.filter(item => item.is_confirmed).length
)

const allSelected = computed(() =>
  paginatedData.value.length > 0 &&
  selectedIds.value.length === paginatedData.value.length
)

const someSelected = computed(() =>
  selectedIds.value.length > 0 &&
  selectedIds.value.length < paginatedData.value.length
)

const hasSelected = computed(() => selectedIds.value.length > 0)

const filteredData = computed(() => {
  let data = tableData.value

  if (filterStatus.value === 'pending') {
    data = data.filter(item => !item.is_confirmed)
  } else if (filterStatus.value === 'confirmed') {
    data = data.filter(item => item.is_confirmed)
  }

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.original_manufacturer?.toLowerCase().includes(query) ||
      item.original_model?.toLowerCase().includes(query) ||
      item.matched_model_number?.toLowerCase().includes(query)
    )
  }

  return data
})

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const totalPages = computed(() =>
  Math.ceil(filteredData.value.length / pageSize.value)
)

// Load data
async function loadData() {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (filterStatus.value === 'pending') {
      params.append('is_confirmed', 'false')
    } else if (filterStatus.value === 'confirmed') {
      params.append('is_confirmed', 'true')
    }
    if (searchQuery.value) {
      params.append('search', searchQuery.value)
    }

    const response = await axios.get(`${API_URL}/manual-matching-override/?${params}`)
    tableData.value = response.data || []
    totalCount.value = tableData.value.length
    currentPage.value = 1
  } catch (error) {
    console.error('Failed to load data:', error)
  } finally {
    loading.value = false
  }
}

let searchTimeout: NodeJS.Timeout | null = null
function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    loadData()
  }, 300)
}

function handlePageSizeChange() {
  currentPage.value = 1
}

// Selection
function toggleSelect(id: number) {
  const index = selectedIds.value.indexOf(id)
  if (index >= 0) {
    selectedIds.value.splice(index, 1)
  } else {
    selectedIds.value.push(id)
  }
}

function toggleSelectAll() {
  if (allSelected.value) {
    selectedIds.value = []
  } else {
    selectedIds.value = paginatedData.value.map(item => item.id)
  }
}

// Actions
async function confirmItem(id: number) {
  // 先检查冲突
  try {
    const checkResponse = await axios.get(`${API_URL}/manual-matching-override/${id}/confirm-check`)
    const checkData = checkResponse.data

    if (checkData.has_conflict) {
      if (checkData.conflict_type === 'empty_model') {
        showToast('原始型号不能为空，无法确认', 'error')
        return
      }
      if (checkData.conflict_type === 'duplicate') {
        // 显示覆盖确认对话框
        confirmDialog.value = {
          show: true,
          itemId: id,
          conflictType: 'duplicate',
          existingRecord: checkData.existing_record
        }
        return
      }
    }

    // 没有冲突，直接确认
    await doConfirmItem(id)
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '确认失败'
    if (typeof errorMsg === 'object' && errorMsg.error === 'conflict') {
      // 服务器返回的冲突错误（双重保险）
      confirmDialog.value = {
        show: true,
        itemId: id,
        conflictType: 'duplicate',
        existingRecord: null
      }
    } else {
      showToast(typeof errorMsg === 'string' ? errorMsg : '确认失败', 'error')
    }
  }
}

async function doConfirmItem(id: number, override: boolean = false) {
  try {
    const params = override ? '?override=true' : ''
    await axios.patch(`${API_URL}/manual-matching-override/${id}/confirm${params}`)
    showToast('确认成功', 'success')
    confirmDialog.value.show = false
    await loadData()
  } catch (error: any) {
    const errorMsg = error.response?.data?.detail || '确认失败'
    showToast(typeof errorMsg === 'string' ? errorMsg : '确认失败', 'error')
  }
}

function handleConfirmOverride() {
  if (confirmDialog.value.itemId !== null) {
    doConfirmItem(confirmDialog.value.itemId, true)
  }
}

function handleConfirmIgnore() {
  // 忽略：删除该条未确认的记录
  if (confirmDialog.value.itemId !== null) {
    deleteItem(confirmDialog.value.itemId, true)
  }
  confirmDialog.value.show = false
}

function closeConfirmDialog() {
  confirmDialog.value.show = false
}

async function confirmSelected() {
  try {
    await axios.patch(`${API_URL}/manual-matching-override/batch-confirm`, selectedIds.value)
    showToast(`已确认 ${selectedIds.value.length} 条记录`, 'success')
    selectedIds.value = []
    await loadData()
  } catch (error) {
    showToast('批量确认失败', 'error')
  }
}

async function deleteItem(id: number, silent: boolean = false) {
  if (!silent && !confirm('确定要删除这条记录吗？')) return
  try {
    await axios.delete(`${API_URL}/manual-matching-override/${id}`)
    if (!silent) showToast('删除成功', 'success')
    await loadData()
  } catch (error) {
    if (!silent) showToast('删除失败', 'error')
  }
}

async function deleteSelected() {
  if (!confirm(`确定要删除选中的 ${selectedIds.value.length} 条记录吗？`)) return
  try {
    await Promise.all(
      selectedIds.value.map(id =>
        axios.delete(`${API_URL}/manual-matching-override/${id}`)
      )
    )
    showToast(`已删除 ${selectedIds.value.length} 条记录`, 'success')
    selectedIds.value = []
    await loadData()
  } catch (error) {
    showToast('批量删除失败', 'error')
  }
}

// Helpers
function formatCategory(item: any): string {
  if (item.tertiary_category) {
    return `${item.primary_category} > ${item.secondary_category} > ${item.tertiary_category}`
  }
  if (item.secondary_category) {
    return `${item.primary_category} > ${item.secondary_category}`
  }
  return item.primary_category || item.device_category || '-'
}

function getSourceLabel(source: string): string {
  const labels: Record<string, string> = {
    datacenter: '数据中心',
    office: '办公设备',
    hybrid: '混合模式'
  }
  return labels[source] || source
}

function formatDate(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Toast notification
function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.value = {
    show: true,
    message,
    type
  }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.manual-matching-management {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  height: 100%;
  position: relative;
  padding-bottom: 60px; /* 为底部分页栏预留空间 */
}

/* Stats Row */
.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
}

.stat-card {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-icon.pending {
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.stat-icon.confirmed {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.stat-icon.total {
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
}

.stat-icon .material-symbols-outlined {
  font-size: 1.5rem;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 1.75rem;
  font-weight: 700;
  color: #f1f5f9;
  font-family: "Inter", sans-serif;
}

.stat-label {
  font-size: 0.875rem;
  color: #64748b;
}

/* Filters */
.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  border: 1px solid #334155;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.filter-group select,
.filter-group input {
  padding: 0.5rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.filter-group input {
  width: 250px;
}

.filter-actions {
  margin-left: auto;
  display: flex;
  gap: 0.75rem;
}

.btn-confirm,
.btn-delete {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-confirm {
  background-color: #22c55e;
  color: white;
}

.btn-confirm:hover:not(:disabled) {
  background-color: #16a34a;
}

.btn-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-delete {
  background-color: #ef4444;
  color: white;
}

.btn-delete:hover:not(:disabled) {
  background-color: #dc2626;
}

.btn-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Table */
.table-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.table-container {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: auto;
  min-height: 300px;
  max-height: calc(100vh - 400px); /* 减去顶部统计卡片、筛选栏和底部分页栏的高度 */
}

.table-container thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table thead {
  background-color: #0f172a;
}

.data-table th {
  padding: 1rem 0.75rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #334155;
}

.data-table td {
  padding: 0.75rem;
  font-size: 0.875rem;
  color: #cbd5e1;
  border-bottom: 1px solid #334155;
}

.data-table tbody tr {
  transition: background-color 0.2s;
}

.data-table tbody tr:hover {
  background-color: #1e293b;
}

.data-table tbody tr.row-selected {
  background-color: rgba(19, 91, 236, 0.1);
}

.col-select {
  width: 40px;
  text-align: center;
}

.cell-model,
.cell-model-matched {
  font-family: "JetBrains Mono", monospace;
  color: #a5b4fc;
  font-weight: 500;
}

.cell-model-matched {
  color: #22c55e;
}

.cell-time {
  font-size: 0.75rem;
  color: #64748b;
}

.col-actions {
  width: 100px;
  text-align: center;
}

.action-btn {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.2s;
}

.action-btn.confirm:hover {
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.1);
}

.action-btn.delete:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}

.no-data {
  text-align: center !important;
  padding: 3rem !important;
  color: #64748b;
}

.no-data .material-symbols-outlined {
  font-size: 2rem;
  display: block;
  margin: 0 auto 0.5rem;
}

.source-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.source-badge.datacenter {
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
}

.source-badge.office {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.source-badge.hybrid {
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.status-badge.pending {
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.status-badge.confirmed {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

/* Pagination - 固定在底部 */
.pagination {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  flex-shrink: 0;
  z-index: 20;
}

.pagination-info {
  color: #94a3b8;
  font-size: 0.875rem;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  padding: 0.375rem 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  background-color: #1e293b;
  color: #f1f5f9;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn .material-symbols-outlined {
  font-size: 1rem;
}

.page-size-select {
  padding: 0.375rem 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.25rem;
  color: #94a3b8;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-size-select:hover {
  border-color: #475569;
}

.page-size-select:focus {
  outline: none;
  border-color: #135bec;
}

/* Toast Notification */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  z-index: 100;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  border-left: 4px solid #22c55e;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast .material-symbols-outlined {
  font-size: 1.25rem;
}

.toast.success .material-symbols-outlined {
  color: #22c55e;
}

.toast.error .material-symbols-outlined {
  color: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* 确认覆盖对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 200;
  animation: fadeIn 0.2s ease-out;
}

.dialog-content {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1.5rem;
  width: 100%;
  max-width: 450px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
  animation: slideUp 0.3s ease-out;
}

.dialog-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.dialog-icon {
  font-size: 1.5rem;
  color: #eab308;
}

.dialog-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
}

.dialog-body {
  margin-bottom: 1.5rem;
}

.dialog-body p {
  margin: 0 0 1rem;
  color: #cbd5e1;
  line-height: 1.5;
}

.dialog-question {
  font-weight: 500;
  color: #f1f5f9;
}

.conflict-info {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 0.75rem 1rem;
  margin: 0.75rem 0;
}

.conflict-row {
  display: flex;
  justify-content: space-between;
  padding: 0.375rem 0;
  border-bottom: 1px solid #1e293b;
}

.conflict-row:last-child {
  border-bottom: none;
}

.conflict-label {
  color: #94a3b8;
  font-size: 0.875rem;
}

.conflict-value {
  color: #f1f5f9;
  font-weight: 500;
  font-size: 0.875rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
}

.dialog-btn {
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.dialog-btn.cancel {
  background-color: #334155;
  color: #cbd5e1;
}

.dialog-btn.cancel:hover {
  background-color: #475569;
}

.dialog-btn.ignore {
  background-color: #64748b;
  color: #f1f5f9;
}

.dialog-btn.ignore:hover {
  background-color: #94a3b8;
}

.dialog-btn.override {
  background-color: #eab308;
  color: #0f172a;
}

.dialog-btn.override:hover {
  background-color: #f59e0b;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
</style>
