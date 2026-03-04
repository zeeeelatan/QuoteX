<template>
  <div class="service-terms-management">
    <!-- Page Heading & Actions -->
    <div class="page-header">
      <div class="header-info">
        <h2 class="page-title">服务条款管理</h2>
        <p class="page-desc">管理所有报价单中使用的法律条款和条件模板</p>
      </div>
      <button class="btn-primary" @click="openCreateDialog">
        <span class="material-symbols-outlined">add</span>
        <span>新增条款</span>
      </button>
    </div>

    <!-- Main Content: List Only -->
    <div class="content-area">
      <!-- Filters -->
      <div class="filters">
        <div class="search-box">
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="searchQuery"
            type="text"
            class="search-input"
            placeholder="搜索条款名称..."
          />
        </div>
        <button class="filter-btn">
          <span class="material-symbols-outlined">filter_list</span>
          <span class="filter-text">筛选</span>
        </button>
      </div>

      <!-- Table Card -->
      <div class="table-card">
        <div class="table-wrapper">
          <table class="terms-table">
            <thead>
              <tr>
                <th class="col-name">条款名称</th>
                <th class="col-products">适用产品</th>
                <th class="col-date">最后修改</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="term in filteredTerms"
                :key="term.id"
                class="term-row"
              >
                <td class="col-name">
                  <div class="name-cell">{{ term.name }}</div>
                </td>
                <td class="col-products">
                  <div class="products-tags">
                    <span
                      v-for="(product, idx) in term.products.slice(0, 2)"
                      :key="idx"
                      class="product-tag"
                    >
                      {{ product }}
                    </span>
                    <span v-if="term.products.length > 2" class="product-more">
                      +{{ term.products.length - 2 }}
                    </span>
                    <span v-if="term.products.length === 0" class="no-products">-</span>
                  </div>
                </td>
                <td class="col-date">{{ term.lastModified }}</td>
                <td class="col-actions">
                  <div class="action-buttons">
                    <button
                      class="action-btn edit-btn"
                      @click="openEditDialog(term)"
                      title="编辑"
                    >
                      <span class="material-symbols-outlined">edit</span>
                    </button>
                    <button
                      class="action-btn delete-btn"
                      @click.stop="confirmDelete(term)"
                      title="删除"
                    >
                      <span class="material-symbols-outlined">delete</span>
                    </button>
                  </div>
                </td>
              </tr>
              <tr v-if="filteredTerms.length === 0">
                <td colspan="4" class="empty-state">
                  <div class="empty-content">
                    <span class="material-symbols-outlined empty-icon">description</span>
                    <p>暂无服务条款数据</p>
                    <button class="btn-text" @click="openCreateDialog">点击创建</button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div v-if="filteredTerms.length > 0" class="pagination">
          <span class="pagination-info">
            显示 {{ paginationInfo }}
          </span>
          <div class="pagination-controls">
            <button
              class="page-btn"
              :disabled="currentPage === 1"
              @click="currentPage--"
            >
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
            <button
              class="page-btn"
              :disabled="currentPage === totalPages"
              @click="currentPage++"
            >
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Editor Dialog (Modal) -->
    <div v-if="showEditorDialog" class="dialog-overlay" @click="closeEditorDialog">
      <div class="editor-dialog" @click.stop>
        <!-- Editor Header -->
        <div class="editor-header">
          <h3 class="editor-title">
            <span class="material-symbols-outlined title-icon">edit_document</span>
            {{ isEditing ? '编辑条款' : '新增条款' }}
          </h3>
          <button class="dialog-close-btn" @click="closeEditorDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>

        <!-- Editor Form -->
        <div class="editor-form">
          <!-- Name Field -->
          <div class="form-field">
            <label class="field-label">
              服务条款名称 <span class="required">*</span>
            </label>
            <input
              v-model="formData.name"
              type="text"
              class="field-input"
              placeholder="请输入条款名称"
            />
          </div>

          <!-- Products Field -->
          <div class="form-field">
            <label class="field-label">适用产品</label>
            <div class="product-selector-container">
              <!-- 已选产品标签 -->
              <div class="selected-products">
                <span
                  v-for="(product, idx) in formData.products"
                  :key="idx"
                  class="product-chip"
                >
                  {{ product }}
                  <button class="chip-remove" @click="removeProduct(idx)">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
              </div>

              <!-- 产品选择器触发按钮 -->
              <button
                class="product-selector-trigger"
                @click="showProductDropdown = !showProductDropdown"
              >
                <span class="material-symbols-outlined">add_circle</span>
                <span>选择产品</span>
                <span class="product-count">{{ unselectedProductCount }} 个可选</span>
              </button>

              <!-- 下拉菜单 -->
              <div v-if="showProductDropdown" class="product-dropdown">
                <!-- 搜索框 -->
                <div class="dropdown-search">
                  <span class="material-symbols-outlined search-icon">search</span>
                  <input
                    v-model="productSearchQuery"
                    type="text"
                    class="search-input"
                    placeholder="搜索产品..."
                    @click.stop
                  />
                </div>

                <!-- 产品列表 -->
                <div class="dropdown-list">
                  <div
                    v-if="filteredProducts.length === 0"
                    class="dropdown-empty"
                  >
                    {{ productSearchQuery ? '没有匹配的产品' : '所有产品已选择' }}
                  </div>
                  <div
                    v-for="product in filteredProducts"
                    :key="product"
                    class="dropdown-item"
                    @click="selectProduct(product)"
                  >
                    <span class="material-symbols-outlined item-icon">add</span>
                    <span class="item-text">{{ product }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Content Field with Rich Text Toolbar -->
          <div class="form-field content-field">
            <div class="content-header">
              <label class="field-label">具体内容</label>
              <button class="preview-btn" @click="togglePreview">
                {{ showPreview ? '编辑' : '预览' }}
              </button>
            </div>

            <!-- Editor Mode -->
            <div v-if="!showPreview" class="rich-text-editor">
              <!-- Toolbar -->
              <div class="editor-toolbar">
                <button
                  class="toolbar-btn"
                  title="加粗"
                  @click="execCommand('bold')"
                >
                  <span class="material-symbols-outlined">format_bold</span>
                </button>
                <button
                  class="toolbar-btn"
                  title="斜体"
                  @click="execCommand('italic')"
                >
                  <span class="material-symbols-outlined">format_italic</span>
                </button>
                <button
                  class="toolbar-btn"
                  title="下划线"
                  @click="execCommand('underline')"
                >
                  <span class="material-symbols-outlined">format_underlined</span>
                </button>
                <div class="toolbar-divider"></div>
                <button
                  class="toolbar-btn"
                  title="无序列表"
                  @click="execCommand('insertUnorderedList')"
                >
                  <span class="material-symbols-outlined">format_list_bulleted</span>
                </button>
                <button
                  class="toolbar-btn"
                  title="有序列表"
                  @click="execCommand('insertOrderedList')"
                >
                  <span class="material-symbols-outlined">format_list_numbered</span>
                </button>
                <div class="toolbar-divider"></div>
                <button
                  class="toolbar-btn"
                  title="插入链接"
                  @click="insertLink"
                >
                  <span class="material-symbols-outlined">link</span>
                </button>
              </div>
              <!-- Content Area -->
              <div
                ref="editorContent"
                class="editor-content"
                contenteditable="true"
                @input="onContentInput"
              ></div>
            </div>

            <!-- Preview Mode -->
            <div v-else class="content-preview">
              <div class="preview-content" v-html="formData.content"></div>
            </div>
          </div>
        </div>

        <!-- Editor Footer -->
        <div class="editor-footer">
          <button class="btn-secondary" @click="closeEditorDialog">
            取消
          </button>
          <button class="btn-primary" @click="saveTerm">
            {{ isEditing ? '保存修改' : '创建条款' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click="showDeleteDialog = false">
      <div class="dialog-card" @click.stop>
        <div class="dialog-header">
          <h3 class="dialog-title">确认删除</h3>
          <button class="dialog-close" @click="showDeleteDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <p>确定要删除服务条款 "{{ termToDelete?.name }}" 吗？此操作不可撤销。</p>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showDeleteDialog = false">
            取消
          </button>
          <button class="btn-danger" @click="deleteTerm">
            确认删除
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import axios from 'axios'
import { getProductCategoryNames } from '@/new/config/productCategories'

// API Base URL
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// 类型定义
interface ServiceTerm {
  id: string
  name: string
  products: string[]
  content: string
  last_modified: string
  created_at: string
}

// 状态
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const terms = ref<ServiceTerm[]>([])
const showPreview = ref(false)
const showDeleteDialog = ref(false)
const showEditorDialog = ref(false)
const termToDelete = ref<ServiceTerm | null>(null)
const selectedTerm = ref<ServiceTerm | null>(null)
const editorContent = ref<HTMLDivElement | null>(null)

// 产品选择器状态
const showProductDropdown = ref(false)
const productSearchQuery = ref('')

// 获取所有可选产品分类
const availableProducts = ref<string[]>([])


// 表单数据
const formData = ref<Partial<ServiceTerm>>({
  name: '',
  products: [],
  content: ''
})

// 是否处于编辑模式
const isEditing = computed(() => !!selectedTerm.value)

// 过滤后的条款列表
const filteredTerms = computed(() => {
  if (!searchQuery.value) return terms.value
  const query = searchQuery.value.toLowerCase()
  return terms.value.filter(term =>
    term.name.toLowerCase().includes(query) ||
    term.products.some(p => p.toLowerCase().includes(query))
  )
})

// 分页信息
const totalPages = computed(() => Math.ceil(filteredTerms.value.length / pageSize.value))
const paginationInfo = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value + 1
  const end = Math.min(currentPage.value * pageSize.value, filteredTerms.value.length)
  return `${start}-${end} 共 ${filteredTerms.value.length} 条`
})

// 可见的页码
const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 3
  let start = Math.max(1, currentPage.value - 1)
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// 过滤后的产品列表（用于下拉选择）
const filteredProducts = computed(() => {
  if (!productSearchQuery.value) {
    return availableProducts.value.filter(
      p => !formData.value.products?.includes(p)
    )
  }
  const query = productSearchQuery.value.toLowerCase()
  return availableProducts.value.filter(
    p => p.toLowerCase().includes(query) && !formData.value.products?.includes(p)
  )
})

// 未选择的产品数量
const unselectedProductCount = computed(() => {
  return availableProducts.value.filter(
    p => !formData.value.products?.includes(p)
  ).length
})

// 从后端加载服务条款数据
async function loadTerms() {
  try {
    const response = await axios.get(`${API_URL}/service-terms/`)
    terms.value = response.data.map((item: any) => ({
      id: String(item.id),
      name: item.name,
      products: item.products || [],
      content: item.content || '',
      lastModified: item.last_modified || '',
      createdAt: item.created_at || ''
    }))
  } catch (error) {
    console.error('Failed to load service terms:', error)
    terms.value = []
  }
}

// 打开新增对话框
function openCreateDialog() {
  selectedTerm.value = null
  formData.value = {
    name: '',
    products: [],
    content: ''
  }
  showPreview.value = false
  showEditorDialog.value = true

  nextTick(() => {
    if (editorContent.value) {
      editorContent.value.innerHTML = ''
    }
  })
}

// 打开编辑对话框
function openEditDialog(term: ServiceTerm) {
  selectedTerm.value = term
  formData.value = {
    name: term.name,
    products: [...term.products],
    content: term.content
  }
  showPreview.value = false
  showEditorDialog.value = true

  nextTick(() => {
    if (editorContent.value) {
      editorContent.value.innerHTML = term.content
    }
  })
}

// 关闭编辑对话框
function closeEditorDialog() {
  showEditorDialog.value = false
  selectedTerm.value = null
  formData.value = {
    name: '',
    products: [],
    content: ''
  }
}

// 保存条款
async function saveTerm() {
  if (!formData.value.name.trim()) {
    alert('请输入条款名称')
    return
  }

  // 确保 content 是最新的
  if (editorContent.value) {
    formData.value.content = editorContent.value.innerHTML
  }

  try {
    const payload = {
      name: formData.value.name,
      products: formData.value.products || [],
      content: formData.value.content || ''
    }

    if (selectedTerm.value) {
      // 更新现有条款
      const response = await axios.put(
        `${API_URL}/service-terms/${selectedTerm.value.id}`,
        payload
      )
      const index = terms.value.findIndex(t => t.id === selectedTerm.value!.id)
      if (index !== -1) {
        terms.value[index] = {
          ...terms.value[index],
          name: response.data.name,
          products: response.data.products || [],
          content: response.data.content || '',
          lastModified: response.data.last_modified || ''
        }
      }
    } else {
      // 创建新条款
      const response = await axios.post(
        `${API_URL}/service-terms/`,
        payload
      )
      const newTerm: ServiceTerm = {
        id: String(response.data.id),
        name: response.data.name,
        products: response.data.products || [],
        content: response.data.content || '',
        lastModified: response.data.last_modified || '',
        createdAt: response.data.created_at || ''
      }
      terms.value.unshift(newTerm)
    }

    // 关闭对话框并重新加载列表
    closeEditorDialog()
    await loadTerms()
  } catch (error) {
    console.error('Failed to save term:', error)
    alert('保存失败，请重试')
  }
}

// 确认删除
function confirmDelete(term: ServiceTerm) {
  termToDelete.value = term
  showDeleteDialog.value = true
}

// 执行删除
async function deleteTerm() {
  if (termToDelete.value) {
    try {
      await axios.delete(`${API_URL}/service-terms/${termToDelete.value.id}`)
      terms.value = terms.value.filter(t => t.id !== termToDelete.value!.id)
      showDeleteDialog.value = false
      termToDelete.value = null
    } catch (error) {
      console.error('Failed to delete term:', error)
      alert('删除失败，请重试')
    }
  }
}

// 移除产品标签
function removeProduct(index: number) {
  formData.value.products?.splice(index, 1)
}

// 富文本编辑器命令
function execCommand(command: string, value?: string) {
  document.execCommand(command, false, value)
  editorContent.value?.focus()
}

// 插入链接
function insertLink() {
  const url = prompt('请输入链接地址：')
  if (url) {
    execCommand('createLink', url)
  }
}

// 内容输入事件
function onContentInput() {
  if (editorContent.value) {
    formData.value.content = editorContent.value.innerHTML
  }
}

// 切换预览
function togglePreview() {
  if (!showPreview.value) {
    // 切换到预览前保存当前内容
    if (editorContent.value) {
      formData.value.content = editorContent.value.innerHTML
    }
  }
  showPreview.value = !showPreview.value
}

// 点击外部关闭下拉菜单
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  if (!target.closest('.product-selector-container')) {
    showProductDropdown.value = false
  }
}

// 选择产品
function selectProduct(productName: string) {
  if (!formData.value.products) {
    formData.value.products = []
  }
  if (!formData.value.products.includes(productName)) {
    formData.value.products.push(productName)
  }
  productSearchQuery.value = ''
}

// 生命周期钩子
onMounted(() => {
  loadTerms()
  // 加载产品分类列表
  availableProducts.value = getProductCategoryNames()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Noto+Sans+SC:wght@400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.service-terms-management {
  font-family: "Inter", "Noto Sans SC", sans-serif;
  color: #e2e8f0;
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

@media (min-width: 640px) {
  .page-header {
    flex-direction: row;
    align-items: center;
    justify-content: space-between;
  }
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  letter-spacing: -0.025em;
}

@media (min-width: 640px) {
  .page-title {
    font-size: 1.875rem;
  }
}

.page-desc {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Buttons */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #135bec;
  color: white;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.2);
}

.btn-primary:hover {
  background-color: #2563eb;
}

.btn-primary:active {
  transform: scale(0.95);
}

.btn-secondary {
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background: transparent;
  color: #f1f5f9;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.btn-danger {
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  border: none;
  background-color: #ef4444;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-text {
  background: transparent;
  border: none;
  color: #135bec;
  font-size: 0.875rem;
  cursor: pointer;
  text-decoration: underline;
}

/* Content Area */
.content-area {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Filters */
.filters {
  display: flex;
  gap: 0.75rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 400px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.search-input {
  width: 100%;
  height: 2.5rem;
  padding-left: 2.5rem;
  padding-right: 1rem;
  border-radius: 0.5rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.search-input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.search-input::placeholder {
  color: #64748b;
}

.filter-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  height: 2.5rem;
  padding: 0 1rem;
  border-radius: 0.5rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #135bec;
  color: #f1f5f9;
}

.filter-text {
  display: none;
}

@media (min-width: 640px) {
  .filter-text {
    display: inline;
    font-size: 0.875rem;
    font-weight: 500;
  }
}

/* Table Card */
.table-card {
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  overflow: hidden;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.table-wrapper {
  overflow-x: auto;
}

.terms-table {
  width: 100%;
  font-size: 0.875rem;
  text-align: left;
  border-collapse: collapse;
}

.terms-table thead {
  background-color: #1c1f27;
  border-bottom: 1px solid #334155;
}

.terms-table th {
  padding: 1rem 1.5rem;
  font-weight: 600;
  color: #f1f5f9;
}

.terms-table th.col-name {
  width: 35%;
}

.terms-table th.col-products {
  width: 35%;
}

.terms-table th.col-actions {
  text-align: right;
  width: 15%;
}

.terms-table tbody {
  border-bottom: 1px solid #334155;
}

.terms-table td {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #1e293b;
}

.term-row {
  transition: background-color 0.2s;
}

.term-row:hover {
  background-color: rgba(255, 255, 255, 0.03);
}

.name-cell {
  font-weight: 500;
  color: #f1f5f9;
}

.products-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.product-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: #282e39;
  color: #f1f5f9;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid transparent;
}

.product-more {
  display: inline-flex;
  align-items: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  background-color: #282e39;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 500;
}

.no-products {
  color: #64748b;
  font-size: 0.75rem;
}

.col-date {
  color: #94a3b8;
  white-space: nowrap;
}

.action-buttons {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.375rem;
  border-radius: 0.375rem;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.edit-btn {
  color: #135bec;
}

.edit-btn:hover {
  background-color: #282e39;
}

.delete-btn {
  color: #ef4444;
}

.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.2);
}

/* Empty State */
.empty-state {
  padding: 3rem;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  color: #94a3b8;
}

.empty-icon {
  font-size: 3rem;
  color: #64748b;
}

.empty-content p {
  font-size: 0.875rem;
  margin: 0;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.5rem;
  border-top: 1px solid #334155;
}

.pagination-info {
  font-size: 0.75rem;
  color: #94a3b8;
}

.pagination-controls {
  display: flex;
  gap: 0.25rem;
}

.page-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 0.25rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.75rem;
  font-weight: 500;
}

.page-btn:hover:not(:disabled) {
  background-color: rgba(255, 255, 255, 0.05);
  color: #f1f5f9;
}

.page-btn.active {
  background-color: #135bec;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Dialog Overlay */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* Editor Dialog */
.editor-dialog {
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.4);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
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

/* Editor Header */
.editor-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
  background-color: #1c1f27;
  border-radius: 0.75rem 0.75rem 0 0;
}

.editor-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 700;
  color: #f1f5f9;
  font-size: 1.125rem;
  margin: 0;
}

.title-icon {
  color: #135bec;
  font-size: 1.25rem;
}

.dialog-close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.dialog-close-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #f1f5f9;
}

/* Editor Form */
.editor-form {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  overflow-y: auto;
  flex: 1;
}

.form-field {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.required {
  color: #ef4444;
}

.field-input {
  width: 100%;
  height: 2.5rem;
  padding: 0 0.75rem;
  border-radius: 0.5rem;
  background-color: #111318;
  border: 1px solid #334155;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.field-input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

/* Products Input */
.products-input {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  min-height: 2.625rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.5rem;
  background-color: #111318;
  border: 1px solid #334155;
  align-items: center;
  transition: all 0.2s;
}

.products-input:focus-within {
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.product-chip {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.2);
  color: #135bec;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.chip-remove {
  display: flex;
  padding: 0.125rem;
  border-radius: 9999px;
  background: transparent;
  border: none;
  cursor: pointer;
  color: #135bec;
}

.chip-remove:hover {
  background-color: rgba(19, 91, 236, 0.2);
}

.chip-remove .material-symbols-outlined {
  font-size: 0.875rem;
}

/* Product Selector */
.product-selector-container {
  position: relative;
}

.selected-products {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.product-selector-trigger {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  background-color: #111318;
  border: 1px solid #334155;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.product-selector-trigger:hover {
  border-color: #475569;
  color: #f1f5f9;
}

.product-selector-trigger .material-symbols-outlined {
  font-size: 1.125rem;
  color: #135bec;
}

.product-count {
  margin-left: auto;
  font-size: 0.75rem;
  color: #64748b;
}

.product-dropdown {
  position: absolute;
  top: calc(100% + 0.25rem);
  left: 0;
  right: 0;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
  z-index: 100;
  max-height: 250px;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  animation: dropdownSlide 0.2s ease-out;
}

@keyframes dropdownSlide {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-search {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #334155;
  background-color: #1c1f27;
}

.dropdown-search .search-icon {
  color: #64748b;
  font-size: 1rem;
  margin-right: 0.5rem;
}

.dropdown-search .search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.dropdown-search .search-input::placeholder {
  color: #64748b;
}

.dropdown-list {
  overflow-y: auto;
  max-height: 200px;
  padding: 0.25rem;
}

.dropdown-empty {
  padding: 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.dropdown-item:hover {
  background-color: rgba(19, 91, 236, 0.1);
}

.dropdown-item .item-icon {
  font-size: 1rem;
  color: #135bec;
}

.dropdown-item .item-text {
  font-size: 0.875rem;
  color: #f1f5f9;
}

/* Content Field */
.content-field {
  flex: 1;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.preview-btn {
  background: transparent;
  border: none;
  color: #135bec;
  font-size: 0.75rem;
  cursor: pointer;
  text-decoration: underline;
}

/* Rich Text Editor */
.rich-text-editor {
  display: flex;
  flex-direction: column;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background-color: #111318;
  overflow: hidden;
  transition: all 0.2s;
}

.rich-text-editor:focus-within {
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-bottom: 1px solid #334155;
  background-color: #1c1f27;
  overflow-x: auto;
}

.toolbar-btn {
  padding: 0.375rem;
  border-radius: 0.25rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-btn:hover {
  background-color: #282e39;
  color: #f1f5f9;
}

.toolbar-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.toolbar-divider {
  width: 1px;
  height: 1rem;
  background-color: #334155;
  margin: 0 0.25rem;
}

.editor-content {
  padding: 0.75rem;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  color: #ffffff !important;
  font-size: 0.875rem;
  line-height: 1.6;
}

.editor-content:empty:before {
  content: attr(data-placeholder);
  color: #64748b;
}

/* 强制覆盖所有内联样式 */
.editor-content *,
.editor-content *:not([class]) {
  color: #ffffff !important;
}

.editor-content p,
.editor-content span,
.editor-content div,
.editor-content li,
.editor-content ul,
.editor-content ol,
.editor-content h1,
.editor-content h2,
.editor-content h3,
.editor-content h4,
.editor-content h5,
.editor-content h6,
.editor-content strong,
.editor-content em,
.editor-content b,
.editor-content i,
.editor-content a,
.editor-content p[style],
.editor-content span[style],
.editor-content div[style] {
  color: #ffffff !important;
}

/* 覆盖带 class 的元素 */
.editor-content .p1,
.editor-content .p2,
.editor-content .p3,
.editor-content .s1,
.editor-content .mb-3,
.editor-content .mb-4,
.editor-content .font-bold,
.editor-content .text-gray-600 {
  color: #ffffff !important;
}

.editor-content .mb-3 {
  margin-bottom: 0.75rem;
}

.editor-content .mb-4 {
  margin-bottom: 1rem;
}

.editor-content .font-bold {
  font-weight: 700;
}

/* Content Preview */
.content-preview {
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background-color: #111318;
  overflow: hidden;
}

.preview-content {
  padding: 0.75rem;
  min-height: 200px;
  max-height: 400px;
  overflow-y: auto;
  color: #ffffff !important;
  font-size: 0.875rem;
  line-height: 1.6;
}

/* 强制覆盖所有内联样式 */
.preview-content *,
.preview-content *:not([class]) {
  color: #ffffff !important;
}

.preview-content p,
.preview-content span,
.preview-content div,
.preview-content li,
.preview-content ul,
.preview-content ol,
.preview-content h1,
.preview-content h2,
.preview-content h3,
.preview-content h4,
.preview-content h5,
.preview-content h6,
.preview-content strong,
.preview-content em,
.preview-content b,
.preview-content i,
.preview-content a,
.preview-content p[style],
.preview-content span[style],
.preview-content div[style] {
  color: #ffffff !important;
}

/* 覆盖带 class 的元素 */
.preview-content .p1,
.preview-content .p2,
.preview-content .p3,
.preview-content .s1,
.preview-content .mb-3,
.preview-content .mb-4,
.preview-content .font-bold,
.preview-content .text-gray-600 {
  color: #ffffff !important;
}

/* Editor Footer */
.editor-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
  background-color: #1c1f27;
  border-radius: 0 0 0.75rem 0.75rem;
}

/* Delete Dialog */
.dialog-card {
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  box-shadow: 0 20px 25px rgba(0, 0, 0, 0.3);
  width: 90%;
  max-width: 400px;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
}

.dialog-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}

.dialog-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
}

.dialog-close:hover {
  color: #f1f5f9;
}

.dialog-body {
  padding: 1.5rem;
}

.dialog-body p {
  margin: 0;
  color: #94a3b8;
  font-size: 0.875rem;
}

.dialog-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}
</style>
