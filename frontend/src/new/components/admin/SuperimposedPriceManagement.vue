<template>
  <div class="superimposed-price-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增数据
        </button>
        <button class="btn-danger" @click="clearAllPrices">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索单价说明、收费标准..."
            @input="handleSearch"
          />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>单价说明</th>
            <th>收费标准</th>
            <th>适用产品</th>
            <th>备注</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in pagedPriceList" :key="item.id">
            <td class="name-cell">{{ item.price_description }}</td>
            <td class="standard-cell">{{ item.charging_standard }}</td>
            <td>
              <div class="products-tags">
                <span v-if="getApplicableProducts(item).length === 0" class="no-products">全部产品</span>
                <span v-for="(product, idx) in getApplicableProducts(item).slice(0, 3)" :key="idx" class="product-tag">
                  {{ product }}
                </span>
                <span v-if="getApplicableProducts(item).length > 3" class="more-products">
                  +{{ getApplicableProducts(item).length - 3 }}
                </span>
              </div>
            </td>
            <td class="remarks-cell">{{ item.remarks || '-' }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="openDialog(item)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deletePrice(item.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="pagedPriceList.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">
        共 {{ filteredPriceList.length }} 条
      </div>
      <div class="pagination-controls">
        <button class="pagination-btn" :disabled="currentPage === 1" @click="currentPage--">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <span class="pagination-current">{{ currentPage }}</span>
        <button class="pagination-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <select v-model="pageSize" class="page-size-select">
          <option :value="10">10条/页</option>
          <option :value="15">15条/页</option>
          <option :value="20">20条/页</option>
        </select>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="dialogVisible" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ isEdit ? '编辑' : '新增' }}叠加单价</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>单价说明 <span class="required">*</span></label>
            <input
              v-model="form.price_description"
              type="text"
              placeholder="例如：差旅补贴、远程技术支持"
            />
          </div>

          <div class="form-group">
            <label>收费标准 <span class="required">*</span></label>
            <textarea
              v-model="form.charging_standard"
              placeholder="请输入收费标准"
              class="form-textarea"
              rows="3"
            ></textarea>
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
            <span class="form-hint">未选择则默认适用于所有产品</span>
          </div>

          <div class="form-group">
            <label>备注</label>
            <textarea
              v-model="form.remarks"
              placeholder="可选：添加备注信息"
              class="form-textarea"
              rows="2"
            ></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="savePrice">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { useProductCategories } from '@/new/stores/productCategoryStore'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// 使用共享的产品分类 store
const { categories } = useProductCategories()

// State
const priceList = ref<any[]>([])
const filteredPriceList = ref<any[]>([])
const dialogVisible = ref(false)
const isEdit = ref(false)
const searchKeyword = ref('')

const currentPage = ref(1)
const pageSize = ref(15)

// 产品选择相关
const selectedProducts = ref<string[]>([])
const showProductDropdown = ref(false)
const productSearchQuery = ref('')

const form = ref({
  id: null as number | null,
  price_description: '',
  charging_standard: '',
  remarks: ''
})

// Computed
const totalPages = computed(() => Math.ceil(filteredPriceList.value.length / pageSize.value))

const pagedPriceList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredPriceList.value.slice(start, start + pageSize.value)
})

const allProducts = computed(() => categories.map((c: any) => c.name))

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

// Fetch prices
async function fetchPrices() {
  try {
    const response = await axios.get(`${API_URL}/superimposed-price/`)
    priceList.value = response.data || []
    applyFilters()
  } catch (error) {
    console.error('Failed to load prices:', error)
  }
}

// Apply filters
function applyFilters() {
  let result = priceList.value

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(item =>
      (item.price_description && item.price_description.toLowerCase().includes(keyword)) ||
      (item.charging_standard && item.charging_standard.toLowerCase().includes(keyword))
    )
  }

  filteredPriceList.value = result
  currentPage.value = 1
}

// Handle search
function handleSearch() {
  applyFilters()
}

// Get applicable products from JSON string
function getApplicableProducts(item: any): string[] {
  if (!item.applicable_products) return []
  try {
    return JSON.parse(item.applicable_products)
  } catch {
    return []
  }
}

// Open dialog
function openDialog(row?: any) {
  if (row) {
    isEdit.value = true
    form.value = {
      id: row.id,
      price_description: row.price_description || '',
      charging_standard: row.charging_standard || '',
      remarks: row.remarks || ''
    }
    selectedProducts.value = getApplicableProducts(row)
  } else {
    isEdit.value = false
    form.value = {
      id: null,
      price_description: '',
      charging_standard: '',
      remarks: ''
    }
    selectedProducts.value = []
  }
  dialogVisible.value = true
}

// Close dialog
function closeDialog() {
  dialogVisible.value = false
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

// Save price
async function savePrice() {
  if (!form.value.price_description) {
    alert('请输入单价说明')
    return
  }
  if (!form.value.charging_standard) {
    alert('请输入收费标准')
    return
  }

  try {
    const payload = {
      price_description: form.value.price_description,
      charging_standard: form.value.charging_standard,
      applicable_products: selectedProducts.value.length > 0 ? selectedProducts.value : null,
      remarks: form.value.remarks || null
    }

    if (isEdit.value) {
      await axios.put(`${API_URL}/superimposed-price/${form.value.id}`, payload)
      showToast('修改成功')
    } else {
      await axios.post(`${API_URL}/superimposed-price/`, payload)
      showToast('新增成功')
    }

    dialogVisible.value = false
    fetchPrices()
  } catch (error: any) {
    console.error('Failed to save price:', error)
    showToast(error.response?.data?.detail || '保存失败', 'error')
  }
}

// Delete price
async function deletePrice(id: number) {
  if (!confirm('确定要删除该数据吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/superimposed-price/${id}`)
    showToast('删除成功')
    fetchPrices()
  } catch (error: any) {
    console.error('Failed to delete price:', error)
    showToast(error.response?.data?.detail || '删除失败', 'error')
  }
}

// Clear all
async function clearAllPrices() {
  if (!confirm('确定要清空所有数据吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/superimposed-price/clear`)
    showToast('所有数据已清空')
    fetchPrices()
  } catch (error: any) {
    console.error('Failed to clear prices:', error)
    showToast(error.response?.data?.detail || '清空失败', 'error')
  }
}

// Toast notification
function showToast(message: string, type: 'success' | 'error' = 'success') {
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
  fetchPrices()
})
</script>

<style scoped>
.superimposed-price-management {
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
}

.btn-secondary:hover {
  background-color: #475569;
}

.search-box {
  display: flex;
  align-items: center;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
}

.search-box .material-symbols-outlined {
  color: #64748b;
  margin-right: 0.5rem;
}

.search-box input {
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-size: 0.875rem;
  outline: none;
  width: 200px;
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

.name-cell {
  font-weight: 600;
  color: #f1f5f9;
}

.standard-cell {
  color: #cbd5e1;
  max-width: 300px;
}

.products-tags {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  flex-wrap: wrap;
}

.product-tag {
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.no-products {
  color: #64748b;
  font-style: italic;
  font-size: 0.75rem;
}

.more-products {
  color: #64748b;
  font-size: 0.75rem;
}

.remarks-cell {
  color: #94a3b8;
  max-width: 200px;
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
  max-width: 550px;
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

.form-group .required {
  color: #ef4444;
}

.form-group input,
.form-group textarea {
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #135bec;
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
}

.form-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.product-selector {
  position: relative;
}

.selected-products {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.selected-product-tag {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.remove-product {
  background: transparent;
  border: none;
  color: #135bec;
  cursor: pointer;
  padding: 0;
  display: flex;
}

.remove-product:hover {
  color: #ef4444;
}

.add-product-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.add-product-btn:hover {
  border-color: #135bec;
  color: #135bec;
}

.product-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  z-index: 10;
}

.dropdown-search {
  padding: 0.5rem;
  border-bottom: 1px solid #334155;
}

.dropdown-search input {
  width: 100%;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.25rem;
  padding: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  outline: none;
}

.dropdown-list {
  max-height: 200px;
  overflow-y: auto;
}

.dropdown-item {
  padding: 0.5rem 0.75rem;
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.875rem;
}

.dropdown-item:hover {
  background-color: #334155;
  color: #e2e8f0;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
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
</style>
