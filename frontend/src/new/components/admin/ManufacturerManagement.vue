<template>
  <div class="manufacturer-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增品牌
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            type="text"
            v-model="searchQuery"
            @input="handleSearch"
            placeholder="搜索品牌名称..."
          />
        </div>
        <span class="total-count">共 {{ totalCount.toLocaleString() }} 条</span>
      </div>
    </div>

    <div class="table-container" :class="{ loading: loading }">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>标准名称</th>
            <th>别名</th>
            <th>创建时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in manufacturers" :key="item.id">
            <td class="id-cell">{{ item.id }}</td>
            <td><span class="name-text">{{ item.name }}</span></td>
            <td>
              <div class="alias-tags">
                <span
                  v-for="alias in (item.aliases || [])"
                  :key="alias"
                  class="alias-tag"
                >
                  {{ alias }}
                  <button class="alias-remove" @click="removeAlias(item.id, alias)" title="移除别名">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
                <span v-if="!item.aliases || item.aliases.length === 0" class="no-alias">-</span>
              </div>
            </td>
            <td class="time-cell">{{ formatTime(item.created_at) }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="openDialog(item)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteManufacturer(item.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && manufacturers.length === 0" class="empty-state">
        <span class="material-symbols-outlined">domain</span>
        <p>暂无品牌数据</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination">
      <div class="pagination-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </div>
      <div class="pagination-controls">
        <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(1)" title="首页">
          <span class="material-symbols-outlined">first_page</span>
        </button>
        <button class="page-btn" :disabled="currentPage === 1" @click="prevPage" title="上一页">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="nextPage" title="下一页">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(totalPages)" title="末页">
          <span class="material-symbols-outlined">last_page</span>
        </button>
        <select v-model="pageSize" @change="currentPage = 1; loadManufacturers()" class="page-size-select">
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
          <option :value="100">100条/页</option>
        </select>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="dialogVisible" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingItem ? '编辑品牌' : '新增品牌' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>标准品牌名称</label>
            <input v-model="formData.name" placeholder="例如: 惠普&慧与/HP&HPE" />
          </div>
          <div class="form-group">
            <label>别名管理</label>
            <div class="alias-editor">
              <div class="alias-tag-list">
                <span
                  v-for="(alias, idx) in formData.aliases"
                  :key="idx"
                  class="alias-tag editable"
                >
                  {{ alias }}
                  <button class="alias-remove" @click="removeFormAlias(idx)">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
              </div>
              <div class="alias-input-row">
                <input
                  v-model="newAliasInput"
                  placeholder="输入别名后按回车添加"
                  @keydown.enter.prevent="addFormAlias"
                />
                <button class="btn-add-alias" @click="addFormAlias" :disabled="!newAliasInput.trim()">
                  <span class="material-symbols-outlined">add</span>
                </button>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveManufacturer">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface Manufacturer {
  id: number
  name: string
  aliases: string[]
  created_at: string
}

// State
const manufacturers = ref<Manufacturer[]>([])
const searchQuery = ref('')
const dialogVisible = ref(false)
const editingItem = ref<Manufacturer | null>(null)
const loading = ref(false)
const newAliasInput = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = ref(20)
const totalCount = ref(0)
let searchTimeout: ReturnType<typeof setTimeout> | null = null

const formData = ref<{ name: string; aliases: string[] }>({
  name: '',
  aliases: []
})

const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)

// Format time
function formatTime(dateStr: string): string {
  if (!dateStr) return '-'
  const d = new Date(dateStr)
  const pad = (n: number) => String(n).padStart(2, '0')
  return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())} ${pad(d.getHours())}:${pad(d.getMinutes())}`
}

// Load manufacturers
async function loadManufacturers() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    const response = await axios.get(`${API_URL}/manufacturers/`, { params })
    const data = response.data
    if (Array.isArray(data)) {
      manufacturers.value = data
      // If backend doesn't return total, estimate from response
      totalCount.value = data.length < pageSize.value && currentPage.value === 1
        ? data.length
        : (currentPage.value - 1) * pageSize.value + data.length + (data.length === pageSize.value ? 1 : 0)
    } else if (data && typeof data === 'object') {
      manufacturers.value = data.items || data.data || []
      totalCount.value = data.total ?? data.count ?? manufacturers.value.length
    }
  } catch (error: any) {
    console.error('Failed to load manufacturers:', error)
    ElMessage.error('加载品牌列表失败')
  } finally {
    loading.value = false
  }
}

// Search with debounce
function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadManufacturers()
  }, 300)
}

// Pagination
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadManufacturers()
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    loadManufacturers()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadManufacturers()
  }
}

// Open dialog
function openDialog(item?: Manufacturer) {
  if (item) {
    editingItem.value = item
    formData.value = {
      name: item.name,
      aliases: [...(item.aliases || [])]
    }
  } else {
    editingItem.value = null
    formData.value = { name: '', aliases: [] }
  }
  newAliasInput.value = ''
  dialogVisible.value = true
}

// Close dialog
function closeDialog() {
  dialogVisible.value = false
  editingItem.value = null
  newAliasInput.value = ''
  formData.value = { name: '', aliases: [] }
}

// Alias management in form
function addFormAlias() {
  const alias = newAliasInput.value.trim()
  if (!alias) return
  if (formData.value.aliases.includes(alias)) {
    ElMessage.warning('该别名已存在')
    return
  }
  formData.value.aliases.push(alias)
  newAliasInput.value = ''
}

function removeFormAlias(idx: number) {
  formData.value.aliases.splice(idx, 1)
}

// Save manufacturer
async function saveManufacturer() {
  if (!formData.value.name.trim()) {
    ElMessage.warning('请输入品牌名称')
    return
  }

  try {
    if (editingItem.value) {
      // Update
      await axios.put(`${API_URL}/manufacturers/${editingItem.value.id}`, {
        name: formData.value.name,
        aliases: formData.value.aliases
      })
      ElMessage.success('品牌更新成功')
    } else {
      // Create
      await axios.post(`${API_URL}/manufacturers/`, {
        name: formData.value.name,
        aliases: formData.value.aliases
      })
      ElMessage.success('品牌创建成功')
    }
    closeDialog()
    loadManufacturers()
  } catch (error: any) {
    console.error('Failed to save manufacturer:', error)
    const msg = error.response?.data?.detail || '保存失败'
    ElMessage.error(msg)
  }
}

// Delete manufacturer
async function deleteManufacturer(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除该品牌吗？删除后不可恢复。', '确认删除', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return // cancelled
  }

  try {
    await axios.delete(`${API_URL}/manufacturers/${id}`)
    ElMessage.success('品牌已删除')
    loadManufacturers()
  } catch (error: any) {
    console.error('Failed to delete manufacturer:', error)
    const msg = error.response?.data?.detail || '删除失败'
    ElMessage.error(msg)
  }
}

// Remove alias directly from table row (via API)
async function removeAlias(manufacturerId: number, alias: string) {
  try {
    await ElMessageBox.confirm(`确定要移除别名「${alias}」吗？`, '确认移除', {
      confirmButtonText: '移除',
      cancelButtonText: '取消',
      type: 'warning'
    })
  } catch {
    return
  }

  try {
    await axios.delete(`${API_URL}/manufacturers/${manufacturerId}/aliases`, {
      params: { alias }
    })
    ElMessage.success('别名已移除')
    loadManufacturers()
  } catch (error: any) {
    console.error('Failed to remove alias:', error)
    const msg = error.response?.data?.detail || '移除别名失败'
    ElMessage.error(msg)
  }
}

onMounted(() => {
  loadManufacturers()
})
</script>

<style scoped>
.manufacturer-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-primary,
.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background-color: #135bec;
  color: white;
}

.btn-primary:hover {
  background-color: #1d64f2;
}

.btn-secondary {
  background-color: #334155;
  color: #e2e8f0;
}

.btn-secondary:hover {
  background-color: #475569;
}

.search-box {
  display: flex;
  align-items: center;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
}

.search-box .material-symbols-outlined {
  font-size: 1.125rem;
  color: #64748b;
  margin-right: 0.5rem;
}

.search-box input {
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-size: 0.875rem;
  width: 200px;
}

.search-box input:focus {
  outline: none;
}

.total-count {
  font-size: 0.875rem;
  color: #64748b;
  padding: 0.5rem 0.75rem;
  background-color: #1e293b;
  border-radius: 0.375rem;
}

/* Table */
.table-container {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: auto;
}

.table-container.loading {
  position: relative;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background-color: rgba(15, 23, 42, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  z-index: 10;
  color: #94a3b8;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid #334155;
  border-top-color: #135bec;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background-color: #0f172a;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #334155;
  font-size: 0.875rem;
  color: #e2e8f0;
}

.data-table tbody tr:hover {
  background-color: #334155;
}

.id-cell {
  color: #64748b;
  font-family: monospace;
}

.name-text {
  font-weight: 500;
  color: #f1f5f9;
}

.time-cell {
  color: #94a3b8;
  font-size: 0.8125rem;
}

/* Alias Tags */
.alias-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  align-items: center;
}

.alias-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.15);
  border: 1px solid rgba(19, 91, 236, 0.3);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  color: #93b4f5;
}

.alias-tag.editable {
  background-color: rgba(19, 91, 236, 0.15);
  border-color: rgba(19, 91, 236, 0.3);
}

.alias-remove {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  transition: color 0.2s;
}

.alias-remove .material-symbols-outlined {
  font-size: 0.875rem;
}

.alias-remove:hover {
  color: #ef4444;
}

.no-alias {
  color: #475569;
  font-size: 0.875rem;
}

/* Actions */
.actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  background: transparent;
  border: none;
  padding: 0.25rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
}

.action-btn.edit:hover {
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.action-btn.delete:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.empty-state .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  margin-top: 1rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: #94a3b8;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #f1f5f9;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.page-size-select {
  padding: 0.375rem 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.25rem;
  color: #94a3b8;
  font-size: 0.875rem;
  cursor: pointer;
}

.page-size-select:hover {
  border-color: #475569;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
}

.dialog-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
}

.close-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
}

.dialog-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.form-group input {
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.form-group input:focus {
  outline: none;
  border-color: #135bec;
}

/* Alias Editor */
.alias-editor {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.alias-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  min-height: 1.5rem;
}

.alias-input-row {
  display: flex;
  gap: 0.5rem;
}

.alias-input-row input {
  flex: 1;
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.alias-input-row input:focus {
  outline: none;
  border-color: #135bec;
}

.btn-add-alias {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  background-color: #135bec;
  border: none;
  border-radius: 0.375rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-alias:hover:not(:disabled) {
  background-color: #1d64f2;
}

.btn-add-alias:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}
</style>
