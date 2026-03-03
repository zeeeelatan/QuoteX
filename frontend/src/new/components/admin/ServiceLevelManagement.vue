<template>
  <div class="service-level-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增服务级别
        </button>
        <button class="btn-success" @click="downloadTemplateDialog = true">
          <span class="material-symbols-outlined">download</span>
          下载模板
        </button>
        <button class="btn-warning" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入
        </button>
        <button class="btn-danger" @click="clearServiceLevels">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空
        </button>
        <input
          ref="importInput"
          type="file"
          accept=".xlsx,.xls,.csv"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            type="text"
            v-model="searchText"
            placeholder="搜索服务级别/关键字"
            clearable
            @input="filterServiceLevels"
          />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>服务级别</th>
            <th>响应时效</th>
            <th>适用产品</th>
            <th>服务级别系数值</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="level in pagedServiceLevelList" :key="level.id">
            <td><span class="level-badge">{{ level.service_level || level.level_code }}</span></td>
            <td>{{ level.response_time }}</td>
            <td>
              <div class="applicable-products">
                <span v-if="getApplicableProducts(level).length === 0" class="no-products">-</span>
                <span v-for="(product, idx) in getApplicableProducts(level).slice(0, 2)" :key="idx" class="product-tag">
                  {{ product }}
                </span>
                <span v-if="getApplicableProducts(level).length > 2" class="more-products">
                  +{{ getApplicableProducts(level).length - 2 }}
                </span>
              </div>
            </td>
            <td>{{ Number(level.coefficient).toFixed(2) }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="openDialog(level)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteServiceLevel(level.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="pagedServiceLevelList.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">
        共 {{ filteredServiceLevelList.length }} 条
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <span class="pagination-current">{{ currentPage }}</span>
        <button
          class="pagination-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <select v-model="pageSize" class="page-size-select">
          <option :value="10">10条/页</option>
          <option :value="15">15条/页</option>
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
        </select>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="dialogVisible" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>服务级别设置</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>服务级别</label>
            <input v-model="form.service_level" placeholder="例如: 7*24*4" />
          </div>
          <div class="form-group">
            <label>响应时效</label>
            <input v-model="form.response_time" placeholder="例如: 4小时到达现场" />
          </div>
          <div class="form-group">
            <label>适用产品</label>
            <div class="product-selector">
              <div class="selected-products">
                <span v-for="(product, idx) in selectedProducts" :key="idx" class="selected-product-tag">
                  {{ product }}
                  <button class="remove-product" @click="removeProduct(idx)">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
              </div>
              <button class="add-product-btn" @click="showProductDropdown = !showProductDropdown">
                <span class="material-symbols-outlined">add_circle</span>
                选择产品
              </button>
              <div v-if="showProductDropdown" class="product-dropdown">
                <div class="dropdown-search">
                  <input v-model="productSearchQuery" type="text" placeholder="搜索产品..." />
                </div>
                <div class="dropdown-list">
                  <div
                    v-for="product in filteredProducts"
                    :key="product"
                    class="dropdown-item"
                    @click="selectProduct(product)"
                  >
                    {{ product }}
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>服务级别系数值</label>
            <input
              v-model.number="form.coefficient"
              type="number"
              step="0.01"
              placeholder="请输入系数值，如1.5"
            />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveServiceLevel">保存</button>
        </div>
      </div>
    </div>

    <!-- Download Template Dialog -->
    <div v-if="downloadTemplateDialog" class="dialog-overlay" @click="downloadTemplateDialog = false">
      <div class="dialog dialog-sm" @click.stop>
        <div class="dialog-header">
          <h3>下载导入模板</h3>
          <button class="close-btn" @click="downloadTemplateDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="template-options">
            <button class="template-btn" @click="downloadTemplate('xlsx')">
              <span class="material-symbols-outlined">description</span>
              下载 xlsx
            </button>
            <button class="template-btn" @click="downloadTemplate('xls')">
              <span class="material-symbols-outlined">description</span>
              下载 xls
            </button>
            <button class="template-btn" @click="downloadTemplate('csv')">
              <span class="material-symbols-outlined">description</span>
              下载 csv
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { useProductCategories } from '@/new/stores/productCategoryStore'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// 使用共享的产品分类 store（响应式，自动同步）
const { categories } = useProductCategories()

// Product categories - 从 store 动态获取
const allProducts = computed(() => categories.map((c: any) => c.name))
const selectedProducts = ref<string[]>([])
const showProductDropdown = ref(false)
const productSearchQuery = ref('')

// State
const serviceLevelList = ref<any[]>([])
const filteredServiceLevelList = ref<any[]>([])
const searchText = ref('')
const dialogVisible = ref(false)
const downloadTemplateDialog = ref(false)
const importInput = ref<HTMLInputElement | null>(null)

const currentPage = ref(1)
const pageSize = ref(15)

const form = ref({
  id: null as number | null,
  service_level: '',
  response_time: '',
  coefficient: 1.0,
  applicable_products: '' as string | null
})

// Template data
const templateHeaders = ['服务级别', '响应时效', '服务级别系数值']
const templateData = [
  {
    '服务级别': 'SLA A++',
    '响应时效': '7*24*2（2小时工程师和备件到达）',
    '服务级别系数值': '1.5'
  }
]

// Computed
const totalPages = computed(() => Math.ceil(filteredServiceLevelList.value.length / pageSize.value))

const pagedServiceLevelList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredServiceLevelList.value.slice(start, start + pageSize.value)
})

const filteredProducts = computed(() => {
  const products = allProducts.value
  if (!productSearchQuery.value) {
    return products.filter((p: string) => !selectedProducts.value.includes(p))
  }
  const query = productSearchQuery.value.toLowerCase()
  return products.filter((p: string) =>
    p.toLowerCase().includes(query) && !selectedProducts.value.includes(p)
  )
})

// Watch page size changes
watch(pageSize, () => {
  currentPage.value = 1
})

// Fetch service levels
async function fetchServiceLevels() {
  try {
    const response = await axios.get(`${API_URL}/service-level/legacy/`)
    serviceLevelList.value = response.data || []
    filterServiceLevels()
  } catch (error) {
    console.error('Failed to load service levels:', error)
  }
}

// Filter service levels
function filterServiceLevels() {
  const text = searchText.value.trim().toLowerCase()
  if (!text) {
    filteredServiceLevelList.value = serviceLevelList.value
    return
  }
  filteredServiceLevelList.value = serviceLevelList.value.filter(item => {
    return (
      (item.service_level && item.service_level.toLowerCase().includes(text)) ||
      (item.response_time && item.response_time.toLowerCase().includes(text))
    )
  })
  currentPage.value = 1
}

// Get applicable products from level data
function getApplicableProducts(level: any): string[] {
  if (!level.applicable_products) return []
  try {
    return JSON.parse(level.applicable_products)
  } catch {
    return []
  }
}

// Select product
function selectProduct(product: string) {
  selectedProducts.value.push(product)
  productSearchQuery.value = ''
}

// Remove product
function removeProduct(index: number) {
  selectedProducts.value.splice(index, 1)
}

// Open dialog
function openDialog(row?: any) {
  if (row) {
    const products = getApplicableProducts(row)
    selectedProducts.value = [...products]
    form.value = {
      id: row.id,
      service_level: row.service_level || row.level_code || '',
      response_time: row.response_time || '',
      coefficient: Number(row.coefficient) || 1.0,
      applicable_products: row.applicable_products || null
    }
  } else {
    selectedProducts.value = []
    form.value = {
      id: null,
      service_level: '',
      response_time: '',
      coefficient: 1.0,
      applicable_products: null
    }
  }
  showProductDropdown.value = false
  productSearchQuery.value = ''
  dialogVisible.value = true
}

// Close dialog
function closeDialog() {
  dialogVisible.value = false
}

// Save service level
async function saveServiceLevel() {
  if (!form.value.service_level || !form.value.response_time) {
    alert('服务级别和响应时效不能为空')
    return
  }

  if (!form.value.coefficient || form.value.coefficient <= 0) {
    alert('服务级别系数值必须是大于0的数字')
    return
  }

  try {
    const payload = {
      level_code: form.value.service_level,
      response_time: form.value.response_time,
      coefficient: form.value.coefficient,
      applicable_products: selectedProducts.value.length > 0 ? JSON.stringify(selectedProducts.value) : null
    }

    if (form.value.id) {
      await axios.put(`${API_URL}/service-level/${form.value.id}`, payload)
      showToast('修改成功')
    } else {
      await axios.post(`${API_URL}/service-level/`, payload)
      showToast('新增成功')
    }

    dialogVisible.value = false
    fetchServiceLevels()
  } catch (error: any) {
    console.error('Failed to save service level:', error)
    showToast(error.response?.data?.detail || '保存失败', 'error')
  }
}

// Delete service level
async function deleteServiceLevel(id: number) {
  if (!confirm('确定要删除该服务级别吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/service-level/${id}`)
    showToast('删除成功')
    fetchServiceLevels()
  } catch (error: any) {
    console.error('Failed to delete service level:', error)
    showToast(error.response?.data?.detail || '删除失败', 'error')
  }
}

// Clear all service levels
async function clearServiceLevels() {
  if (!confirm('确定要清空所有服务级别吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/service-level/clear`)
    showToast('所有服务级别已清空')
    fetchServiceLevels()
  } catch (error: any) {
    console.error('Failed to clear service levels:', error)
    showToast(error.response?.data?.detail || '清空失败', 'error')
  }
}

// Download template
function downloadTemplate(type: string) {
  if (type === 'csv') {
    // Generate CSV content
    const rows = [templateHeaders.join(',')]
    templateData.forEach(row => {
      rows.push(templateHeaders.map(h => row[h as keyof typeof row]).join(','))
    })
    const csvContent = rows.join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '服务级别导入模板.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    // Generate Excel content
    const ws = XLSX.utils.json_to_sheet(templateData, { header: templateHeaders })
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '模板')
    const ext = type === 'xls' ? 'xls' : 'xlsx'
    XLSX.writeFile(wb, `服务级别导入模板.${ext}`)
  }
  downloadTemplateDialog.value = false
}

// Trigger import
function triggerImport() {
  importInput.value?.click()
}

// Handle import file
async function handleImportFile(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    let data: any[] = []

    if (file.name.endsWith('.csv')) {
      // Read CSV
      const text = await file.text()
      const rows = text.split(/\r?\n/).filter(Boolean)
      const headers = rows[0].split(',')
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i].split(',')
        const obj: any = {}
        headers.forEach((h, idx) => obj[h.trim()] = row[idx]?.trim() || '')
        data.push(obj)
      }
    } else {
      // Read Excel
      const arrayBuffer = await file.arrayBuffer()
      const wb = XLSX.read(arrayBuffer, { type: 'array' })
      const ws = wb.Sheets[wb.SheetNames[0]]
      data = XLSX.utils.sheet_to_json(ws)
    }

    // Transform data format
    data = data.map((row, rowIndex) => {
      let coefficient = row['服务级别系数值'] || row['coefficient'] || ''
      coefficient = Number(coefficient)
      if (!coefficient || isNaN(coefficient) || coefficient <= 0) {
        throw new Error(`第${rowIndex + 2}行服务级别系数值无效，请检查！`)
      }
      return {
        service_level: row['服务级别'] || row['service_level'] || '',
        response_time: row['响应时效'] || row['response_time'] || '',
        coefficient: coefficient
      }
    })

    // Upload to backend
    const response = await axios.post(`${API_URL}/service-level/import-json`, { data })
    showToast(response.data.message || '导入成功')
    fetchServiceLevels()
  } catch (err: any) {
    console.error('Import failed:', err)
    showToast('导入失败: ' + (err.message || err.response?.data?.detail || '未知错误'), 'error')
  }

  target.value = ''
}

// Toast notification
function showToast(message: string, type: 'success' | 'error' = 'success') {
  // Simple toast implementation
  const toast = document.createElement('div')
  toast.className = `toast toast-${type}`
  toast.textContent = message
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background: ${type === 'success' ? '#10b981' : '#ef4444'};
    color: white;
    border-radius: 6px;
    z-index: 9999;
    animation: slideIn 0.3s ease;
  `
  document.body.appendChild(toast)
  setTimeout(() => {
    toast.remove()
  }, 3000)
}

onMounted(() => {
  fetchServiceLevels()
})
</script>

<style scoped>
.service-level-management {
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
  gap: 0.75rem;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-primary,
.btn-secondary,
.btn-success,
.btn-warning,
.btn-danger {
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
  color: white;
}

.btn-primary {
  background-color: #135bec;
}
.btn-primary:hover {
  background-color: #1d64f2;
}

.btn-success {
  background-color: #10b981;
}
.btn-success:hover {
  background-color: #059669;
}

.btn-warning {
  background-color: #f59e0b;
}
.btn-warning:hover {
  background-color: #d97706;
}

.btn-danger {
  background-color: #ef4444;
}
.btn-danger:hover {
  background-color: #dc2626;
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
  width: 220px;
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

.level-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: monospace;
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

/* Pagination */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
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

.pagination-btn {
  background: transparent;
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #e2e8f0;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-current {
  font-size: 0.875rem;
  color: #e2e8f0;
  min-width: 2rem;
  text-align: center;
}

.page-size-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #e2e8f0;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  margin-left: 0.5rem;
}

.page-size-select:focus {
  outline: none;
  border-color: #135bec;
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

.dialog-sm {
  max-width: 350px;
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

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}

/* Template options */
.template-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.template-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.template-btn:hover {
  background-color: #334155;
  border-color: #135bec;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

/* Applicable Products */
.applicable-products {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.no-products {
  color: #64748b;
  font-size: 0.875rem;
}

.product-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background-color: rgba(6, 182, 212, 0.1);
  color: #22d3ee;
  border: 1px solid rgba(6, 182, 212, 0.2);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.more-products {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.375rem;
  background-color: rgba(100, 116, 139, 0.1);
  color: #94a3b8;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

/* Product Selector */
.product-selector {
  position: relative;
}

.selected-products {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 2.5rem;
  padding: 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  margin-bottom: 0.5rem;
}

.selected-product-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border: 1px solid rgba(19, 91, 236, 0.3);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.remove-product {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.remove-product:hover {
  color: #ef4444;
}

.remove-product .material-symbols-outlined {
  font-size: 0.875rem;
}

.add-product-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.add-product-btn:hover {
  border-color: #475569;
  background-color: #1e293b;
}

.add-product-btn .material-symbols-outlined {
  font-size: 1rem;
}

.product-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  z-index: 100;
}

.dropdown-search {
  padding: 0.5rem;
  border-bottom: 1px solid #334155;
}

.dropdown-search input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.dropdown-search input:focus {
  outline: none;
  border-color: #135bec;
}

.dropdown-list {
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  padding: 0.5rem 0.75rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background-color: #334155;
  color: #f1f5f9;
}

.dropdown-item:first-child {
  border-radius: 0.375rem 0.375rem 0 0;
}

.dropdown-item:last-child {
  border-radius: 0 0 0.375rem 0.375rem;
}
</style>
