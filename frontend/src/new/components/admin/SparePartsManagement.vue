<template>
  <div class="spare-parts-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="showAddDialog = true">
          <span class="material-symbols-outlined">add</span>
          添加备件
        </button>
        <button class="btn-secondary" @click="exportData">
          <span class="material-symbols-outlined">download</span>
          导出
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input 
            type="text" 
            v-model="searchQuery" 
            @input="handleSearch"
            placeholder="搜索备件..." 
          />
        </div>
        <span class="total-count">共 {{ totalCount.toLocaleString() }} 条</span>
      </div>
    </div>

    <div class="table-container" :class="{ loading: loading }">
      <!-- 加载遮罩 -->
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      
      <table class="data-table">
        <thead>
          <tr>
            <th>厂商</th>
            <th>备件 PN</th>
            <th>备件描述</th>
            <th>备件分类</th>
            <th>备件成色</th>
            <th>报修方式</th>
            <th>报修期限</th>
            <th>单价</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="part in parts" :key="part.id">
            <td>{{ part.manufacturer }}</td>
            <td><span class="pn-code">{{ part.part_pn }}</span></td>
            <td class="desc-cell">{{ part.part_desc }}</td>
            <td>{{ part.part_category || '-' }}</td>
            <td>{{ part.part_condition || '-' }}</td>
            <td>{{ part.repair_method || '-' }}</td>
            <td>{{ part.repair_period || '-' }}</td>
            <td class="price-cell">¥{{ part.unit_price?.toLocaleString() || '-' }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="editPart(part)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deletePart(part.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && parts.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inventory_2</span>
        <p>暂无备件数据</p>
      </div>
    </div>
    
    <!-- 分页 -->
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
        <button class="page-btn" :disabled="currentPage === totalPages" @click="nextPage" title="下一页">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <button class="page-btn" :disabled="currentPage === totalPages" @click="goToPage(totalPages)" title="末页">
          <span class="material-symbols-outlined">last_page</span>
        </button>
        <select v-model="pageSize" @change="currentPage = 1; loadParts()" class="page-size-select">
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
          <option :value="100">100条/页</option>
        </select>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showAddDialog || editingPart" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingPart ? '编辑备件' : '添加备件' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-row">
            <div class="form-group">
              <label>厂商</label>
              <input v-model="formData.manufacturer" placeholder="例如: Dell" />
            </div>
            <div class="form-group">
              <label>备件 PN</label>
              <input v-model="formData.part_pn" placeholder="例如: XXX-XXXX" />
            </div>
          </div>
          <div class="form-group">
            <label>备件描述</label>
            <input v-model="formData.part_desc" placeholder="备件描述" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>备件分类</label>
              <input v-model="formData.part_category" placeholder="例如: 硬盘" />
            </div>
            <div class="form-group">
              <label>备件成色</label>
              <input v-model="formData.part_condition" placeholder="例如: 全新/翻新" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>报修方式</label>
              <input v-model="formData.repair_method" placeholder="例如: 更换" />
            </div>
            <div class="form-group">
              <label>报修期限</label>
              <input v-model="formData.repair_period" placeholder="例如: 3个工作日" />
            </div>
          </div>
          <div class="form-group">
            <label>单价 (元)</label>
            <input v-model.number="formData.unit_price" type="number" placeholder="单价" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="savePart">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
const parts = ref<any[]>([])
const searchQuery = ref('')
const showAddDialog = ref(false)
const editingPart = ref<any>(null)
const loading = ref(false)

// 分页
const currentPage = ref(1)
const pageSize = ref(50)
const totalCount = ref(0)
let searchTimeout: NodeJS.Timeout | null = null

const formData = ref({
  manufacturer: '',
  part_pn: '',
  part_desc: '',
  part_category: '',
  part_condition: '',
  repair_method: '',
  repair_period: '',
  unit_price: 0
})

// Computed
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value) || 1)

// Load parts with pagination
async function loadParts() {
  loading.value = true
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }
    if (searchQuery.value) {
      params.search = searchQuery.value
    }
    
    // 并行请求数据和总数
    const [dataResponse, countResponse] = await Promise.all([
      axios.get(`${API_URL}/spare_parts/`, { params }),
      axios.get(`${API_URL}/spare_parts/count`, { params: searchQuery.value ? { search: searchQuery.value } : {} })
    ])
    
    parts.value = dataResponse.data || []
    totalCount.value = countResponse.data.total || 0
  } catch (error) {
    console.error('Failed to load spare parts:', error)
  } finally {
    loading.value = false
  }
}

// 搜索处理（防抖）
function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadParts()
  }, 300)
}

// 分页处理
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
    loadParts()
  }
}

function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    loadParts()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    loadParts()
  }
}

// Edit part
function editPart(part: any) {
  editingPart.value = part
  formData.value = {
    manufacturer: part.manufacturer || '',
    part_pn: part.part_pn || '',
    part_desc: part.part_desc || '',
    part_category: part.part_category || '',
    part_condition: part.part_condition || '',
    repair_method: part.repair_method || '',
    repair_period: part.repair_period || '',
    unit_price: part.unit_price || 0
  }
}

// Delete part
async function deletePart(id: number) {
  if (!confirm('确定要删除这个备件吗？')) return
  try {
    await axios.delete(`${API_URL}/spare_parts/${id}`)
    // 重新加载当前页数据
    loadParts()
  } catch (error) {
    console.error('Failed to delete part:', error)
  }
}

// Save part
async function savePart() {
  const data = {
    manufacturer: formData.value.manufacturer,
    part_pn: formData.value.part_pn,
    part_desc: formData.value.part_desc,
    part_category: formData.value.part_category || '',
    part_condition: formData.value.part_condition || '',
    repair_method: formData.value.repair_method || '',
    repair_period: formData.value.repair_period || '',
    unit_price: formData.value.unit_price
  }

  try {
    if (editingPart.value) {
      await axios.put(`${API_URL}/spare_parts/${editingPart.value.id}`, data)
    } else {
      await axios.post(`${API_URL}/spare_parts/`, data)
    }
    closeDialog()
    // 重新加载数据
    loadParts()
  } catch (error) {
    console.error('Failed to save part:', error)
  }
}

// Close dialog
function closeDialog() {
  showAddDialog.value = false
  editingPart.value = null
  formData.value = {
    manufacturer: '',
    part_pn: '',
    part_desc: '',
    part_category: '',
    part_condition: '',
    repair_method: '',
    repair_period: '',
    unit_price: 0
  }
}

// Export data
function exportData() {
  const exportData = parts.value.map((part, index) => ({
    '序号': index + 1,
    '厂商': part.manufacturer,
    '备件PN': part.part_pn,
    '备件描述': part.part_desc,
    '备件分类': part.part_category || '',
    '备件成色': part.part_condition || '',
    '报修方式': part.repair_method || '',
    '报修期限': part.repair_period || '',
    '单价': part.unit_price || 0
  }))
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '备件清单')
  XLSX.writeFile(wb, '备件价格管理.xlsx')
}

onMounted(() => {
  loadParts()
})
</script>

<style scoped>
.spare-parts-management {
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

.table-container {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: auto;
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
}

.data-table tbody tr:hover {
  background-color: #334155;
}

.pn-code {
  font-family: monospace;
  color: #135bec;
}

.price-cell {
  font-weight: 600;
  color: #22c55e;
}

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

/* Total Count */
.total-count {
  font-size: 0.875rem;
  color: #64748b;
  padding: 0.5rem 0.75rem;
  background-color: #1e293b;
  border-radius: 0.375rem;
}

/* Loading */
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

/* Description Cell */
.desc-cell {
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
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

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}
</style>

