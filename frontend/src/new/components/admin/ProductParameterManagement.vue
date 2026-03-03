<template>
  <div class="pricing-parameter-management">
    <!-- Batch Actions Bar (shown when items are selected) -->
    <div v-if="selectedIds.size > 0" class="batch-actions-bar">
      <div class="batch-actions-left">
        <span class="selected-count">已选择 <strong>{{ selectedIds.size }}</strong> 项</span>
        <button class="btn btn-secondary" @click="clearSelection">
          <span class="material-symbols-outlined">close</span>
          取消选择
        </button>
      </div>
      <div class="batch-actions-right">
        <button class="btn btn-primary" @click="openBatchEditDialog">
          <span class="material-symbols-outlined">edit</span>
          批量编辑
        </button>
        <button class="btn btn-danger" @click="batchDelete">
          <span class="material-symbols-outlined">delete</span>
          批量删除
        </button>
      </div>
    </div>

    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增调价参数
        </button>
        <button class="btn-success" @click="downloadTemplateDialog = true">
          <span class="material-symbols-outlined">download</span>
          下载模板
        </button>
        <button class="btn-warning" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入
        </button>
        <button class="btn-danger" @click="clearPricingParameters">
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
            placeholder="搜索参数项/参数值"
            clearable
            @input="filterPricingParameters"
          />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th class="checkbox-column">
              <label class="checkbox-wrapper">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  :indeterminate="isSomeSelected"
                  @change="toggleSelectAll"
                />
                <span class="checkbox-custom"></span>
              </label>
            </th>
            <th>调价参数项</th>
            <th>调价参数值</th>
            <th>适用产品</th>
            <th>系数</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="param in pagedParameterList"
            :key="param.id"
            :class="{ selected: selectedIds.has(param.id) }"
          >
            <td class="checkbox-column">
              <label class="checkbox-wrapper">
                <input
                  type="checkbox"
                  :checked="selectedIds.has(param.id)"
                  @change="toggleSelect(param.id)"
                />
                <span class="checkbox-custom"></span>
              </label>
            </td>
            <td><span class="category-badge">{{ param.parameter_category }}</span></td>
            <td>{{ param.parameter_value }}</td>
            <td>
              <div class="applicable-products">
                <span v-if="getApplicableProducts(param).length === 0" class="no-products">-</span>
                <span v-for="(product, idx) in getApplicableProducts(param).slice(0, 2)" :key="idx" class="product-tag">
                  {{ product }}
                </span>
                <span v-if="getApplicableProducts(param).length > 2" class="more-products">
                  +{{ getApplicableProducts(param).length - 2 }}
                </span>
              </div>
            </td>
            <td>{{ Number(param.coefficient).toFixed(2) }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="openDialog(param)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deletePricingParameter(param.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="pagedParameterList.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">
        显示第 <span>{{ (currentPage - 1) * pageSize + 1 }}</span> 到
        <span>{{ Math.min(currentPage * pageSize, filteredParameterList.length) }}</span> 条，
        共 <span>{{ filteredParameterList.length }}</span> 条数据
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button
          v-for="page in visiblePages"
          :key="page"
          class="pagination-btn page-number"
          :class="{ active: page === currentPage }"
          @click="currentPage = page"
        >
          {{ page }}
        </button>
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
          <h3>调价参数设置</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>调价参数项</label>
            <input v-model="form.parameter_category" placeholder="例如: 学历名称、工作年限、服务模式等" />
          </div>
          <div class="form-group">
            <label>调价参数值</label>
            <input v-model="form.parameter_value" placeholder="例如: 博士、10年" />
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
            <label>系数</label>
            <input
              v-model.number="form.coefficient"
              type="number"
              step="0.1"
              placeholder="请输入系数值，如1.5"
            />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="savePricingParameter">保存</button>
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

    <!-- Batch Edit Dialog -->
    <div v-if="batchEditDialogVisible" class="dialog-overlay" @click="closeBatchEditDialog">
      <div class="dialog batch-edit-dialog" @click.stop>
        <div class="dialog-header">
          <h3>批量编辑调价参数 ({{ selectedIds.size }} 项)</h3>
          <button class="close-btn" @click="closeBatchEditDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="batch-edit-info">
            <span class="material-symbols-outlined">info</span>
            <span>仅修改选中的字段，未选中的字段将保持原值</span>
          </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="batchEditForm.updateCategory" />
              调价参数项
            </label>
            <input
              v-model="batchEditForm.parameter_category"
              placeholder="保持原值"
              :disabled="!batchEditForm.updateCategory"
            />
          </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="batchEditForm.updateValue" />
              调价参数值
            </label>
            <input
              v-model="batchEditForm.parameter_value"
              placeholder="保持原值"
              :disabled="!batchEditForm.updateValue"
            />
          </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="batchEditForm.updateCoefficient" />
              系数
            </label>
            <input
              v-model.number="batchEditForm.coefficient"
              type="number"
              step="0.1"
              placeholder="保持原值"
              :disabled="!batchEditForm.updateCoefficient"
            />
          </div>

          <div class="form-group">
            <label>
              <input type="checkbox" v-model="batchEditForm.updateProducts" />
              适用产品
            </label>
            <div class="product-selector" :class="{ disabled: !batchEditForm.updateProducts }">
              <div class="selected-products">
                <span v-for="(product, idx) in batchSelectedProducts" :key="idx" class="selected-product-tag">
                  {{ product }}
                  <button class="remove-product" @click="removeBatchProduct(idx)" :disabled="!batchEditForm.updateProducts">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
              </div>
              <button class="add-product-btn" @click="showBatchProductDropdown = !showBatchProductDropdown" :disabled="!batchEditForm.updateProducts">
                <span class="material-symbols-outlined">add_circle</span>
                选择产品
              </button>
              <div v-if="showBatchProductDropdown && batchEditForm.updateProducts" class="product-dropdown">
                <div class="dropdown-search">
                  <input v-model="batchProductSearchQuery" type="text" placeholder="搜索产品..." />
                </div>
                <div class="dropdown-list">
                  <div
                    v-for="product in batchFilteredProducts"
                    :key="product"
                    class="dropdown-item"
                    @click="selectBatchProduct(product)"
                  >
                    {{ product }}
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeBatchEditDialog">取消</button>
          <button class="btn-primary" @click="saveBatchEdit">保存修改</button>
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
const pricingParameterList = ref<any[]>([])
const filteredParameterList = ref<any[]>([])
const searchText = ref('')
const dialogVisible = ref(false)
const downloadTemplateDialog = ref(false)
const importInput = ref<HTMLInputElement | null>(null)

const currentPage = ref(1)
const pageSize = ref(15)

const form = ref({
  id: null as number | null,
  parameter_category: '',
  parameter_value: '',
  coefficient: 1.0,
  applicable_products: null as string | null
})

// Batch selection state
const selectedIds = ref<Set<number>>(new Set())

// Batch edit state
const batchEditDialogVisible = ref(false)
const batchEditForm = ref({
  updateCategory: false,
  parameter_category: '',
  updateValue: false,
  parameter_value: '',
  updateCoefficient: false,
  coefficient: null as number | null,
  updateProducts: false
})
const batchSelectedProducts = ref<string[]>([])
const showBatchProductDropdown = ref(false)
const batchProductSearchQuery = ref('')

// Template data
const templateHeaders = ['调价参数项', '调价参数值', '适用产品', '系数']
const templateData = [
  {
    '调价参数项': '学历名称',
    '调价参数值': '博士',
    '适用产品': '',
    '系数': '2.0'
  }
]

// Computed
const totalPages = computed(() => Math.ceil(filteredParameterList.value.length / pageSize.value))

const pagedParameterList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredParameterList.value.slice(start, start + pageSize.value)
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

// Batch selection computed
const isAllSelected = computed(() => {
  return pagedParameterList.value.length > 0 &&
    pagedParameterList.value.every(param => selectedIds.value.has(param.id))
})

const isSomeSelected = computed(() => {
  return pagedParameterList.value.some(param => selectedIds.value.has(param.id)) &&
    !pagedParameterList.value.every(param => selectedIds.value.has(param.id))
})

const batchFilteredProducts = computed(() => {
  const products = allProducts.value
  if (!batchProductSearchQuery.value) {
    return products.filter((p: string) => !batchSelectedProducts.value.includes(p))
  }
  const query = batchProductSearchQuery.value.toLowerCase()
  return products.filter((p: string) =>
    p.toLowerCase().includes(query) && !batchSelectedProducts.value.includes(p)
  )
})

// Watch page size changes
watch(pageSize, () => {
  currentPage.value = 1
})

// Fetch pricing parameters
async function fetchPricingParameters() {
  try {
    const response = await axios.get(`${API_URL}/pricing-parameter/legacy/`)
    pricingParameterList.value = response.data || []
    filterPricingParameters()
  } catch (error) {
    console.error('Failed to load pricing parameters:', error)
  }
}

// Filter pricing parameters
function filterPricingParameters() {
  const text = searchText.value.trim().toLowerCase()
  if (!text) {
    filteredParameterList.value = pricingParameterList.value
    return
  }
  filteredParameterList.value = pricingParameterList.value.filter(item => {
    return (
      (item.parameter_category && item.parameter_category.toLowerCase().includes(text)) ||
      (item.parameter_value && item.parameter_value.toLowerCase().includes(text))
    )
  })
  currentPage.value = 1
}

// Get applicable products from parameter data
function getApplicableProducts(param: any): string[] {
  if (!param.applicable_products) return []
  try {
    return JSON.parse(param.applicable_products)
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
      parameter_category: row.parameter_category || '',
      parameter_value: row.parameter_value || '',
      coefficient: Number(row.coefficient) || 1.0,
      applicable_products: row.applicable_products || null
    }
  } else {
    selectedProducts.value = []
    form.value = {
      id: null,
      parameter_category: '',
      parameter_value: '',
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

// Save pricing parameter
async function savePricingParameter() {
  if (!form.value.parameter_category || !form.value.parameter_value) {
    alert('调价参数项和调价参数值不能为空')
    return
  }

  if (!form.value.coefficient || form.value.coefficient <= 0) {
    alert('系数必须是大于0的数字')
    return
  }

  try {
    const payload = {
      parameter_category: form.value.parameter_category,
      parameter_value: form.value.parameter_value,
      coefficient: form.value.coefficient,
      applicable_products: selectedProducts.value.length > 0 ? JSON.stringify(selectedProducts.value) : null
    }

    if (form.value.id) {
      await axios.put(`${API_URL}/pricing-parameter/${form.value.id}`, payload)
      showToast('修改成功')
    } else {
      await axios.post(`${API_URL}/pricing-parameter/`, payload)
      showToast('新增成功')
    }

    dialogVisible.value = false
    fetchPricingParameters()
  } catch (error: any) {
    console.error('Failed to save pricing parameter:', error)
    showToast(error.response?.data?.detail || '保存失败', 'error')
  }
}

// Delete pricing parameter
async function deletePricingParameter(id: number) {
  if (!confirm('确定要删除该调价参数吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/pricing-parameter/${id}`)
    showToast('删除成功')
    selectedIds.value.delete(id)
    fetchPricingParameters()
  } catch (error: any) {
    console.error('Failed to delete pricing parameter:', error)
    showToast(error.response?.data?.detail || '删除失败', 'error')
  }
}

// Batch selection functions
function toggleSelect(id: number) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
  // Trigger reactivity
  selectedIds.value = new Set(selectedIds.value)
}

function toggleSelectAll() {
  if (isAllSelected.value) {
    // Deselect all on current page
    pagedParameterList.value.forEach(param => selectedIds.value.delete(param.id))
  } else {
    // Select all on current page
    pagedParameterList.value.forEach(param => selectedIds.value.add(param.id))
  }
  // Trigger reactivity
  selectedIds.value = new Set(selectedIds.value)
}

function clearSelection() {
  selectedIds.value = new Set()
}

// Batch delete
async function batchDelete() {
  if (selectedIds.value.size === 0) return

  const count = selectedIds.value.size
  if (!confirm(`确定要删除选中的 ${count} 条调价参数吗？此操作不可撤销！`)) return

  try {
    // Delete all selected items
    const promises = Array.from(selectedIds.value).map(id =>
      axios.delete(`${API_URL}/pricing-parameter/${id}`)
    )
    await Promise.all(promises)

    showToast(`成功删除 ${count} 条调价参数`)
    selectedIds.value = new Set()
    fetchPricingParameters()
  } catch (error: any) {
    console.error('Failed to batch delete:', error)
    showToast(error.response?.data?.detail || '批量删除失败', 'error')
  }
}

// Batch edit functions
function openBatchEditDialog() {
  if (selectedIds.value.size === 0) return

  // Reset form
  batchEditForm.value = {
    updateCategory: false,
    parameter_category: '',
    updateValue: false,
    parameter_value: '',
    updateCoefficient: false,
    coefficient: null,
    updateProducts: false
  }
  batchSelectedProducts.value = []
  showBatchProductDropdown.value = false
  batchProductSearchQuery.value = ''

  batchEditDialogVisible.value = true
}

function closeBatchEditDialog() {
  batchEditDialogVisible.value = false
}

function selectBatchProduct(product: string) {
  batchSelectedProducts.value.push(product)
  batchProductSearchQuery.value = ''
}

function removeBatchProduct(index: number) {
  batchSelectedProducts.value.splice(index, 1)
}

async function saveBatchEdit() {
  if (selectedIds.value.size === 0) return

  // Check if at least one field is selected for update
  const hasUpdate = batchEditForm.value.updateCategory ||
    batchEditForm.value.updateValue ||
    batchEditForm.value.updateCoefficient ||
    batchEditForm.value.updateProducts

  if (!hasUpdate) {
    alert('请至少选择一个要修改的字段')
    return
  }

  // Validate coefficient if selected
  if (batchEditForm.value.updateCoefficient) {
    if (!batchEditForm.value.coefficient || batchEditForm.value.coefficient <= 0) {
      alert('系数必须是大于0的数字')
      return
    }
  }

  try {
    const promises = Array.from(selectedIds.value).map(id => {
      // Get original data
      const original = pricingParameterList.value.find(p => p.id === id)
      if (!original) return Promise.resolve()

      // Build payload with only updated fields
      const payload: any = {}

      if (batchEditForm.value.updateCategory && batchEditForm.value.parameter_category) {
        payload.parameter_category = batchEditForm.value.parameter_category
      }
      if (batchEditForm.value.updateValue && batchEditForm.value.parameter_value) {
        payload.parameter_value = batchEditForm.value.parameter_value
      }
      if (batchEditForm.value.updateCoefficient && batchEditForm.value.coefficient) {
        payload.coefficient = batchEditForm.value.coefficient
      }
      if (batchEditForm.value.updateProducts) {
        payload.applicable_products = batchSelectedProducts.value.length > 0
          ? JSON.stringify(batchSelectedProducts.value)
          : null
      }

      return axios.put(`${API_URL}/pricing-parameter/${id}`, payload)
    })

    await Promise.all(promises)

    showToast(`成功修改 ${selectedIds.value.size} 条调价参数`)
    batchEditDialogVisible.value = false
    selectedIds.value = new Set()
    fetchPricingParameters()
  } catch (error: any) {
    console.error('Failed to batch update:', error)
    showToast(error.response?.data?.detail || '批量修改失败', 'error')
  }
}

// Clear all pricing parameters
async function clearPricingParameters() {
  if (!confirm('确定要清空所有调价参数吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/pricing-parameter/clear`)
    showToast('所有调价参数已清空')
    fetchPricingParameters()
  } catch (error: any) {
    console.error('Failed to clear pricing parameters:', error)
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
    link.download = '调价参数导入模板.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    // Generate Excel content
    const ws = XLSX.utils.json_to_sheet(templateData, { header: templateHeaders })
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '模板')
    const ext = type === 'xls' ? 'xls' : 'xlsx'
    XLSX.writeFile(wb, `调价参数导入模板.${ext}`)
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
      let coefficient = row['系数'] || row['coefficient'] || ''
      coefficient = Number(coefficient)
      if (!coefficient || isNaN(coefficient) || coefficient <= 0) {
        throw new Error(`第${rowIndex + 2}行系数无效，请检查！`)
      }
      return {
        parameter_category: row['调价参数项'] || row['parameter_category'] || '',
        parameter_value: row['调价参数值'] || row['parameter_value'] || '',
        applicable_products: row['适用产品'] || row['applicable_products'] || null,
        coefficient: coefficient
      }
    })

    // Upload to backend
    const response = await axios.post(`${API_URL}/pricing-parameter/import-json`, { data })
    showToast(response.data.message || '导入成功')
    fetchPricingParameters()
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
  fetchPricingParameters()
})
</script>

<style scoped>
.pricing-parameter-management {
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

.category-badge {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
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

.pagination-info span {
  color: #f1f5f9;
  font-weight: 600;
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
  min-width: 2rem;
  justify-content: center;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #e2e8f0;
}

.pagination-btn.active {
  background-color: #135bec;
  border-color: #135bec;
  color: white;
}

.pagination-btn.page-number {
  font-size: 0.875rem;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
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

.form-group input,
.form-group select {
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #135bec;
}

.form-select {
  cursor: pointer;
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

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-size: 1.25rem;
  vertical-align: middle;
}

/* Batch Operations Styles */
.batch-actions-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: linear-gradient(135deg, #135bec 0%, #0d4db3 100%);
  border-radius: 0.5rem;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.batch-actions-left,
.batch-actions-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.selected-count {
  color: white;
  font-size: 0.875rem;
}

.selected-count strong {
  font-weight: 700;
  font-size: 1rem;
}

.batch-actions-bar .btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.batch-actions-bar .btn-primary {
  background: white;
  color: #135bec;
}

.batch-actions-bar .btn-primary:hover {
  background: #f1f5f9;
}

.batch-actions-bar .btn-secondary {
  background: rgba(255, 255, 255, 0.15);
  color: white;
}

.batch-actions-bar .btn-secondary:hover {
  background: rgba(255, 255, 255, 0.25);
}

.batch-actions-bar .btn-danger {
  background: #ef4444;
  color: white;
}

.batch-actions-bar .btn-danger:hover {
  background: #dc2626;
}

.batch-actions-bar .material-symbols-outlined {
  font-size: 1rem;
}

/* Checkbox Column */
.checkbox-column {
  width: 48px;
  text-align: center;
}

.checkbox-wrapper {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  position: relative;
}

.checkbox-wrapper input[type="checkbox"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.checkbox-custom {
  width: 18px;
  height: 18px;
  border: 2px solid #475569;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
  background: transparent;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkbox-custom {
  background: #135bec;
  border-color: #135bec;
}

.checkbox-wrapper input[type="checkbox"]:checked + .checkbox-custom::after {
  content: '';
  width: 5px;
  height: 10px;
  border: solid white;
  border-width: 0 2px 2px 0;
  transform: rotate(45deg);
  margin-top: -2px;
}

.checkbox-wrapper input[type="checkbox"]:indeterminate + .checkbox-custom {
  background: #135bec;
  border-color: #135bec;
}

.checkbox-wrapper input[type="checkbox"]:indeterminate + .checkbox-custom::after {
  content: '';
  width: 10px;
  height: 2px;
  background: white;
  border-radius: 1px;
}

.checkbox-wrapper:hover .checkbox-custom {
  border-color: #135bec;
}

/* Selected row style */
.data-table tbody tr.selected {
  background-color: rgba(19, 91, 236, 0.1) !important;
}

.data-table tbody tr.selected td {
  border-top-color: rgba(19, 91, 236, 0.3);
  border-bottom-color: rgba(19, 91, 236, 0.3);
}

/* Batch Edit Dialog */
.batch-edit-dialog {
  max-width: 550px;
}

.batch-edit-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: rgba(19, 91, 236, 0.1);
  border: 1px solid rgba(19, 91, 236, 0.2);
  border-radius: 0.375rem;
  margin-bottom: 1rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

.batch-edit-info .material-symbols-outlined {
  color: #135bec;
  font-size: 1.125rem;
}

.batch-edit .form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.batch-edit .form-group > label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
  cursor: pointer;
}

.batch-edit .form-group > label input[type="checkbox"] {
  width: 18px;
  height: 18px;
  accent-color: #135bec;
  cursor: pointer;
}

.batch-edit .form-group input:disabled,
.batch-edit .form-group select:disabled,
.batch-edit .form-group .product-selector.disabled {
  opacity: 0.5;
  pointer-events: none;
}

.product-selector.disabled .add-product-btn {
  cursor: not-allowed;
}

.batch-edit .form-group input::placeholder,
.batch-edit .form-group select option:first-child {
  color: #64748b;
}
</style>
