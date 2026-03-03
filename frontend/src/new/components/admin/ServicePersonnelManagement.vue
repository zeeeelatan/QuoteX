<template>
  <div class="service-personnel-management">
    <!-- Action Toolbar -->
    <div class="action-toolbar">
      <div class="search-filters">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            v-model="searchQuery"
            type="text"
            placeholder="搜索人员类型、技能描述或标签..."
            @input="handleSearch"
          />
        </div>
        <select v-model="filterType" class="filter-select" @change="loadData">
          <option value="">所有人员类型</option>
          <option v-for="type in personnelTypes" :key="type" :value="type">{{ type }}</option>
        </select>
        <select v-model="filterLevel" class="filter-select" @change="loadData">
          <option value="">所有等级</option>
          <option value="专家">专家</option>
          <option value="高级">高级</option>
          <option value="中级">中级</option>
          <option value="初级">初级</option>
        </select>
        <select v-model="filterMode" class="filter-select" @change="loadData">
          <option value="">所有服务模式</option>
          <option value="远程">远程</option>
          <option value="现场">现场</option>
        </select>
      </div>
      <div class="action-buttons">
        <button class="btn btn-secondary" @click="exportData">
          <span class="material-symbols-outlined">download</span>
          导出数据
        </button>
        <button class="btn btn-primary" @click="showAddDialog">
          <span class="material-symbols-outlined">add</span>
          新增人员
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-wrapper">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>人员类型</th>
              <th>技能描述</th>
              <th>能力等级</th>
              <th>服务模式</th>
              <th class="text-right">人天单价 (RMB)</th>
              <th>特长标签</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedData" :key="item.id" class="table-row">
              <td>
                <div class="personnel-type">
                  <span class="type-icon" :class="getLevelClass(item.skill_level)">
                    <span class="material-symbols-outlined">{{ getTypeIcon(item.personnel_type) }}</span>
                  </span>
                  <span class="type-name">{{ item.personnel_type }}</span>
                </div>
              </td>
              <td>
                <p class="skill-desc" :title="item.skill_description">{{ truncateText(item.skill_description, 30) }}</p>
              </td>
              <td>
                <span class="level-badge" :class="getLevelClass(item.skill_level)">
                  <span class="level-dot"></span>
                  {{ item.skill_level }}
                </span>
              </td>
              <td>
                <span class="mode-badge" :class="{ 'mode-remote': item.service_mode === '远程', 'mode-onsite': item.service_mode === '现场' }">
                  {{ item.service_mode }}
                </span>
              </td>
              <td class="text-right">
                <span class="price">¥ {{ formatPrice(item.daily_rate) }}</span>
                <span class="price-unit">/ 天</span>
              </td>
              <td>
                <div class="tags">
                  <span v-for="(tag, idx) in parseTags(item.tags)" :key="idx" class="tag">{{ tag }}</span>
                </div>
              </td>
              <td class="text-center">
                <button class="action-btn" @click="editItem(item)" title="编辑">
                  <span class="material-symbols-outlined">edit</span>
                </button>
                <button class="action-btn delete-btn" @click="confirmDelete(item)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
            <tr v-if="paginatedData.length === 0">
              <td colspan="7" class="no-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Frozen Bottom Bar with Pagination -->
      <div class="bottom-bar">
        <div class="bottom-bar-left">
          <div class="pagination-info">
            显示第 <span>{{ (currentPage - 1) * pageSize + 1 }}</span> 到
            <span>{{ Math.min(currentPage * pageSize, filteredData.length) }}</span> 条，
            共 <span>{{ filteredData.length }}</span> 条数据
          </div>
        </div>
        <div class="bottom-bar-center">
          <div class="page-size-selector">
            <span class="page-size-label">每页显示</span>
            <select v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
              <option :value="10">10</option>
              <option :value="15">15</option>
              <option :value="20">20</option>
              <option :value="30">30</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
            </select>
            <span class="page-size-label">条</span>
          </div>
        </div>
        <div class="bottom-bar-right">
          <div class="pagination-buttons">
            <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
              <span class="material-symbols-outlined">chevron_left</span>
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              class="page-btn"
              :class="{ active: page === currentPage }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
            <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog">
        <div class="dialog-header">
          <h3>{{ dialogTitle }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>服务人员类型 <span class="required">*</span></label>
            <input
              v-model="formData.personnel_type"
              type="text"
              placeholder="例如：系统工程师、项目经理"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>技能描述</label>
            <textarea
              v-model="formData.skill_description"
              placeholder="描述该人员的专业技能和职责"
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>能力级别 <span class="required">*</span></label>
              <select v-model="formData.skill_level" class="form-select">
                <option value="">请选择</option>
                <option value="专家">专家</option>
                <option value="高级">高级</option>
                <option value="中级">中级</option>
                <option value="初级">初级</option>
              </select>
            </div>
            <div class="form-group">
              <label>服务模式 <span class="required">*</span></label>
              <select v-model="formData.service_mode" class="form-select">
                <option value="">请选择</option>
                <option value="远程">远程</option>
                <option value="现场">现场</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>人天单价 (RMB) <span class="required">*</span></label>
              <input
                v-model.number="formData.daily_rate"
                type="number"
                min="0"
                step="0.01"
                placeholder="例如：3500"
                class="form-input"
              />
            </div>
            <div class="form-group">
              <label>特长标签</label>
              <input
                v-model="formData.tags"
                type="text"
                placeholder="多个标签用逗号分隔，如：CCIE证书,PMP"
                class="form-input"
              />
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="closeDialog">取消</button>
          <button class="btn btn-primary" @click="saveItem">保存</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click.self="showDeleteDialog = false">
      <div class="dialog dialog-small">
        <div class="dialog-header">
          <h3>确认删除</h3>
          <button class="close-btn" @click="showDeleteDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <p>确定要删除该服务人员记录吗？此操作不可撤销。</p>
          <p v-if="itemToDelete" class="delete-item-info">
            {{ itemToDelete.personnel_type }} - {{ itemToDelete.skill_level }} - {{ itemToDelete.service_mode }}
          </p>
        </div>
        <div class="dialog-footer">
          <button class="btn btn-secondary" @click="showDeleteDialog = false">取消</button>
          <button class="btn btn-danger" @click="deleteItem">确认删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// Data
const personnelData = ref<any[]>([])
const personnelTypes = ref<string[]>([])
const searchQuery = ref('')
const filterType = ref('')
const filterLevel = ref('')
const filterMode = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = ref(15)

// Dialog
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const editingId = ref<number | null>(null)
const itemToDelete = ref<any>(null)

const formData = ref({
  personnel_type: '',
  skill_description: '',
  skill_level: '',
  service_mode: '',
  daily_rate: 0,
  tags: ''
})

// Computed
const dialogTitle = computed(() => editingId.value ? '编辑服务人员' : '新增服务人员')

const filteredData = computed(() => {
  let data = [...personnelData.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.personnel_type?.toLowerCase().includes(query) ||
      item.skill_description?.toLowerCase().includes(query) ||
      item.tags?.toLowerCase().includes(query)
    )
  }

  if (filterType.value) {
    data = data.filter(item => item.personnel_type === filterType.value)
  }

  if (filterLevel.value) {
    data = data.filter(item => item.skill_level === filterLevel.value)
  }

  if (filterMode.value) {
    data = data.filter(item => item.service_mode === filterMode.value)
  }

  return data
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push(total)
    }
  }

  return pages
})

// Methods
async function loadData() {
  try {
    const params: any = {}
    if (filterType.value) params.personnel_type = filterType.value
    if (filterLevel.value) params.skill_level = filterLevel.value
    if (filterMode.value) params.service_mode = filterMode.value

    const response = await axios.get(`${API_URL}/service_personnel/`, { params })
    personnelData.value = response.data

    // Load unique types for filter
    const typesResponse = await axios.get(`${API_URL}/service_personnel/types/list`)
    personnelTypes.value = typesResponse.data.types || []
  } catch (error: any) {
    console.error('[ServicePersonnelManagement] Failed to load data:', error)
  }
}

function handleSearch() {
  currentPage.value = 1
}

function handlePageSizeChange() {
  currentPage.value = 1
}

function showAddDialog() {
  editingId.value = null
  formData.value = {
    personnel_type: '',
    skill_description: '',
    skill_level: '',
    service_mode: '',
    daily_rate: 0,
    tags: '人天'
  }
  showDialog.value = true
}

function editItem(item: any) {
  editingId.value = item.id
  formData.value = {
    personnel_type: item.personnel_type || '',
    skill_description: item.skill_description || '',
    skill_level: item.skill_level || '',
    service_mode: item.service_mode || '',
    daily_rate: item.daily_rate || 0,
    tags: item.tags || '人天'
  }
  showDialog.value = true
}

async function saveItem() {
  try {
    // Validation
    if (!formData.value.personnel_type?.trim()) {
      alert('请输入服务人员类型')
      return
    }
    if (!formData.value.skill_level) {
      alert('请选择能力级别')
      return
    }
    if (!formData.value.service_mode) {
      alert('请选择服务模式')
      return
    }
    if (!formData.value.daily_rate || formData.value.daily_rate <= 0) {
      alert('请输入有效的人天单价')
      return
    }

    const data = {
      personnel_type: formData.value.personnel_type.trim(),
      skill_description: formData.value.skill_description?.trim() || '',
      skill_level: formData.value.skill_level,
      service_mode: formData.value.service_mode,
      daily_rate: formData.value.daily_rate,
      tags: formData.value.tags || '人天'
    }

    if (editingId.value) {
      await axios.put(`${API_URL}/service_personnel/${editingId.value}`, data)
    } else {
      await axios.post(`${API_URL}/service_personnel/`, data)
    }

    await loadData()
    closeDialog()
  } catch (error: any) {
    console.error('[ServicePersonnelManagement] Failed to save:', error)
    const errorMessage = error.response?.data?.detail || error.message || '保存失败，请重试'
    alert(errorMessage)
  }
}

function closeDialog() {
  showDialog.value = false
  editingId.value = null
}

function confirmDelete(item: any) {
  itemToDelete.value = item
  showDeleteDialog.value = true
}

async function deleteItem() {
  if (!itemToDelete.value) return

  try {
    await axios.delete(`${API_URL}/service_personnel/${itemToDelete.value.id}`)
    await loadData()
    showDeleteDialog.value = false
    itemToDelete.value = null
  } catch (error: any) {
    console.error('[ServicePersonnelManagement] Failed to delete:', error)
    const errorMessage = error.response?.data?.detail || error.message || '删除失败，请重试'
    alert(errorMessage)
  }
}

async function exportData() {
  try {
    const response = await axios.get(`${API_URL}/service_personnel/export`, {
      responseType: 'blob'
    })

    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', `服务人员数据_${new Date().toISOString().slice(0, 10)}.xlsx`)
    document.body.appendChild(link)
    link.click()
    link.remove()
  } catch (error: any) {
    console.error('[ServicePersonnelManagement] Failed to export:', error)
    alert('导出失败，请重试')
  }
}

// Utility functions
function getLevelClass(level: string): string {
  const levelMap: Record<string, string> = {
    '专家': 'expert',
    '高级': 'senior',
    '中级': 'mid',
    '初级': 'junior'
  }
  return levelMap[level] || 'junior'
}

function getTypeIcon(type: string): string {
  const iconMap: Record<string, string> = {
    '工程师': 'engineering',
    '项目经理': 'manage_accounts',
    '开发': 'code',
    '设计师': 'design_services'
  }

  for (const [key, icon] of Object.entries(iconMap)) {
    if (type.includes(key)) return icon
  }
  return 'badge'
}

function formatPrice(price: number): string {
  return price.toLocaleString('zh-CN')
}

function truncateText(text: string | undefined, maxLength: number): string {
  if (!text) return '-'
  return text.length > maxLength ? text.slice(0, maxLength) + '...' : text
}

function parseTags(tags: string | undefined): string[] {
  if (!tags) return []
  return tags.split(',').map(t => t.trim()).filter(t => t)
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<style scoped>
.service-personnel-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

/* Action Toolbar */
.action-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.search-filters {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex: 1;
  flex-wrap: wrap;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #64748b;
  font-size: 1.25rem;
}

.search-box input {
  padding-left: 2.5rem;
  width: 16rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
}

.search-box input:focus {
  outline: none;
  border-color: #135bec;
}

.search-box input::placeholder {
  color: #64748b;
}

.filter-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  min-width: 8rem;
  cursor: pointer;
}

.filter-select:hover {
  border-color: #475569;
}

.action-buttons {
  display: flex;
  gap: 0.75rem;
}

/* Buttons */
.btn {
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
  background-color: #0d4ed3;
}

.btn-secondary {
  background-color: #334155;
  color: #e2e8f0;
}

.btn-secondary:hover {
  background-color: #475569;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Table Wrapper - contains table and frozen bottom bar */
.table-wrapper {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* Table Container */
.table-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
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
  border-bottom: 1px solid #334155;
}

.data-table th.text-right {
  text-align: right;
}

.data-table th.text-center {
  text-align: center;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #1e293b;
  font-size: 0.875rem;
}

.data-table tr.table-row:hover {
  background-color: rgba(30, 41, 59, 0.8);
}

.data-table td.text-right {
  text-align: right;
}

.data-table td.text-center {
  text-align: center;
}

.no-data {
  text-align: center;
  color: #64748b;
  padding: 3rem !important;
}

/* Personnel Type */
.personnel-type {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.type-icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.type-icon.expert {
  background-color: rgba(168, 85, 247, 0.1);
  border: 1px solid rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.type-icon.senior {
  background-color: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.type-icon.mid {
  background-color: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.type-icon.junior {
  background-color: rgba(107, 114, 128, 0.1);
  border: 1px solid rgba(107, 114, 128, 0.2);
  color: #6b7280;
}

.type-name {
  font-weight: 500;
  color: #f1f5f9;
}

/* Skill Description */
.skill-desc {
  color: #cbd5e1;
  margin: 0;
  max-width: 20rem;
}

/* Level Badge */
.level-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.level-badge.expert {
  background-color: rgba(168, 85, 247, 0.1);
  color: #a855f7;
  border: 1px solid rgba(168, 85, 247, 0.2);
}

.level-badge.senior {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.level-badge.mid {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.level-badge.junior {
  background-color: rgba(107, 114, 128, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(107, 114, 128, 0.2);
}

.level-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 9999px;
}

.level-badge.expert .level-dot {
  background-color: #a855f7;
}

.level-badge.senior .level-dot {
  background-color: #3b82f6;
}

.level-badge.mid .level-dot {
  background-color: #22c55e;
}

.level-badge.junior .level-dot {
  background-color: #94a3b8;
}

/* Mode Badge */
.mode-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.mode-badge.mode-remote {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.mode-badge.mode-onsite {
  background-color: rgba(249, 115, 22, 0.1);
  color: #f97316;
}

/* Price */
.price {
  font-family: 'Inter', sans-serif;
  font-weight: 700;
  color: #f1f5f9;
}

.price-unit {
  color: #64748b;
  font-size: 0.75rem;
  margin-left: 0.25rem;
}

/* Tags */
.tags {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  background-color: rgba(6, 182, 212, 0.1);
  color: #22d3ee;
  border: 1px solid rgba(6, 182, 212, 0.2);
}

/* Action Buttons */
.action-btn {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

.action-btn.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.action-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Frozen Bottom Bar */
.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #0f172a;
  border-top: 1px solid #334155;
  flex-shrink: 0;
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.bottom-bar-left {
  flex: 1;
}

.bottom-bar-center {
  flex: 0 0 auto;
}

.bottom-bar-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

/* Page Size Selector */
.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-label {
  font-size: 0.75rem;
  color: #64748b;
}

.page-size-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  cursor: pointer;
  width: 3.5rem;
}

.page-size-select:hover {
  border-color: #475569;
}

.page-size-select:focus {
  outline: none;
  border-color: #135bec;
}

/* Pagination Info */
.pagination-info {
  font-size: 0.75rem;
  color: #64748b;
}

.pagination-info span {
  color: #f1f5f9;
  font-weight: 600;
}

/* Pagination Buttons */
.pagination-buttons {
  display: flex;
  gap: 0.25rem;
}

.page-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  background-color: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #f1f5f9;
}

.page-btn.active {
  background-color: #135bec;
  border-color: #135bec;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Dialog */
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
  z-index: 1000;
}

.dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  width: 100%;
  max-width: 36rem;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-small {
  max-width: 28rem;
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
  margin: 0;
}

.close-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.close-btn:hover {
  background-color: #334155;
  color: #94a3b8;
}

.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
  max-height: 60vh;
}

.dialog-body p {
  color: #cbd5e1;
  margin: 0 0 1rem 0;
}

.delete-item-info {
  padding: 0.75rem;
  background-color: #334155;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #f1f5f9;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}

/* Form */
.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
  margin-bottom: 0.375rem;
}

.required {
  color: #ef4444;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.1);
}

.form-input::placeholder,
.form-textarea::placeholder {
  color: #64748b;
}

.form-textarea {
  resize: vertical;
  min-height: 4rem;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>
