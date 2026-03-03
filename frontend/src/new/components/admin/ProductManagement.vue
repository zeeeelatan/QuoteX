<template>
  <div class="product-management">
    <!-- Left Sidebar - Product Categories -->
    <aside class="product-sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <h1 class="sidebar-title" v-show="!sidebarCollapsed">
          <span class="material-symbols-outlined">category</span>
          产品分类管理
        </h1>
        <button class="collapse-toggle" @click="toggleSidebar" :title="sidebarCollapsed ? '展开' : '收缩'">
          <span class="material-symbols-outlined">{{ sidebarCollapsed ? 'chevron_right' : 'chevron_left' }}</span>
        </button>
      </div>

      <div class="category-list">
        <div
          v-for="category in categories"
          :key="category.id"
          class="category-item"
          :class="{ active: selectedCategory === category.id }"
          @click="selectCategory(category.id)"
          :title="sidebarCollapsed ? category.name : ''"
        >
          <span class="category-icon">
            <span class="material-symbols-outlined">{{ category.icon }}</span>
          </span>
          <div class="category-name-wrapper" v-show="!sidebarCollapsed">
            <p class="category-name">{{ category.name }}</p>
            <button
              class="category-delete-btn"
              @click.stop="deleteCategoryItem(category)"
              :title="'删除: ' + category.name"
            >
              <span class="material-symbols-outlined">delete</span>
            </button>
          </div>
        </div>
      </div>

      <div class="sidebar-footer" v-show="!sidebarCollapsed">
        <button class="add-category-btn" @click="showAddCategoryDialog = true">
          <span class="material-symbols-outlined">add</span>
          新增分类
        </button>
      </div>
    </aside>

    <!-- 新增分类对话框 -->
    <div v-if="showAddCategoryDialog" class="dialog-overlay" @click.self="showAddCategoryDialog = false">
      <div class="dialog-container">
        <div class="dialog-header">
          <h3 class="dialog-title">新增产品分类</h3>
          <button class="dialog-close" @click="showAddCategoryDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>分类代码 <span class="required">*</span></label>
            <input
              v-model="newCategory.id"
              type="text"
              placeholder="例如: new-service"
              class="form-input"
            />
            <span class="form-hint">英文字母、数字和连字符，用于系统内部标识</span>
          </div>
          <div class="form-group">
            <label>分类名称 <span class="required">*</span></label>
            <input
              v-model="newCategory.name"
              type="text"
              placeholder="例如: 新服务报价"
              class="form-input"
            />
          </div>
          <div class="form-group">
            <label>分类图标</label>
            <div class="icon-selector">
              <div
                v-for="icon in availableIcons"
                :key="icon"
                class="icon-option"
                :class="{ selected: newCategory.icon === icon }"
                @click="newCategory.icon = icon"
              >
                <span class="material-symbols-outlined">{{ icon }}</span>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>分类描述</label>
            <textarea
              v-model="newCategory.description"
              placeholder="描述该分类的用途和特点..."
              class="form-textarea"
              rows="3"
            ></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="dialog-btn cancel-btn" @click="showAddCategoryDialog = false">
            取消
          </button>
          <button class="dialog-btn confirm-btn" @click="addNewCategory">
            确认添加
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content Area -->
    <main class="product-main">
      <!-- Breadcrumbs -->
      <div class="breadcrumbs">
        <a class="breadcrumb-link" href="#">后台管理</a>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <a class="breadcrumb-link" href="#">产品管理</a>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-current">{{ currentCategoryName }}配置</span>
      </div>

      <!-- Page Heading -->
      <div class="page-header">
        <div class="header-info">
          <h2 class="page-title">{{ currentCategoryName }}配置</h2>
          <p class="page-description">{{ currentCategoryDescription }}</p>
        </div>
        <div class="header-actions">
          <button class="action-btn secondary">
            <span class="material-symbols-outlined">preview</span>
            预览效果
          </button>
          <button class="action-btn primary">
            <span class="material-symbols-outlined">save</span>
            保存更改
          </button>
        </div>
      </div>

      <!-- Tabs Navigation -->
      <div class="tabs-nav">
        <a class="tab-item active" href="#">
          <p class="tab-text">产品定义</p>
        </a>
        <a class="tab-item" href="#">
          <p class="tab-text">报价单表头定制</p>
        </a>
        <a class="tab-item" href="#">
          <p class="tab-text">AI 建议逻辑</p>
        </a>
      </div>

      <!-- Content Panel -->
      <div class="content-panel">
        <!-- Left Section: Basic Parameters -->
        <div class="left-section">
          <section class="card">
            <h3 class="card-title">
              <span class="material-symbols-outlined">edit_note</span>
              基础参数定义
            </h3>
            <div class="form-grid">
              <div class="form-group">
                <label>产品代码</label>
                <input type="text" :value="formData.productCode" />
              </div>
              <div class="form-group">
                <label>计费模式</label>
                <select v-model="formData.billingMode">
                  <option>年费 (Annual)</option>
                  <option>月结 (Monthly)</option>
                  <option>按次计费 (Per Incident)</option>
                </select>
              </div>
              <div class="form-group">
                <label>基准单价 (CNY)</label>
                <div class="input-with-prefix">
                  <span class="prefix">¥</span>
                  <input type="number" v-model.number="formData.basePrice" step="0.01" />
                </div>
              </div>
              <div class="form-group">
                <label>利润率上限 (%)</label>
                <input type="number" v-model.number="formData.profitMargin" />
              </div>
            </div>
          </section>

          <!-- Service Level Options -->
          <section class="card">
            <div class="card-header">
              <h3 class="card-title">
                <span class="material-symbols-outlined">hotel_class</span>
                服务级别定义 (SLA)
              </h3>
              <button class="add-btn">+ 添加级别</button>
            </div>
            <div class="table-container">
              <table class="sla-table">
                <thead>
                  <tr>
                    <th>级别名称</th>
                    <th>响应时间</th>
                    <th>报价系数</th>
                    <th class="text-right">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="level in slaLevels" :key="level.id">
                    <td class="font-medium">{{ level.name }}</td>
                    <td class="text-muted">{{ level.response }}</td>
                    <td>
                      <span class="coefficient-badge">{{ level.coefficient }}</span>
                    </td>
                    <td class="text-right">
                      <button class="icon-btn">
                        <span class="material-symbols-outlined">edit</span>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </div>

        <!-- Right Section: AI Settings & Status -->
        <div class="right-section">
          <section class="card">
            <h3 class="card-title">
              <span class="material-symbols-outlined">psychology</span>
              AI 报价引擎配置
            </h3>
            <div class="ai-config">
              <div class="toggle-item">
                <div class="toggle-info">
                  <p class="toggle-title">启用 AI 智能推荐</p>
                  <p class="toggle-desc">基于历史成交数据自动推荐系数</p>
                </div>
                <div class="toggle-switch" :class="{ active: aiSettings.enabled }" @click="aiSettings.enabled = !aiSettings.enabled">
                  <div class="toggle-dot"></div>
                </div>
              </div>

              <div class="sliders">
                <div class="slider-item">
                  <div class="slider-header">
                    <span class="slider-label">风险加成权重</span>
                    <span class="slider-value">{{ aiSettings.riskWeight }}%</span>
                  </div>
                  <div class="slider-track">
                    <div class="slider-fill" :style="{ width: aiSettings.riskWeight + '%' }"></div>
                  </div>
                </div>
                <div class="slider-item">
                  <div class="slider-header">
                    <span class="slider-label">客户历史粘性</span>
                    <span class="slider-value">{{ aiSettings.loyaltyWeight }}%</span>
                  </div>
                  <div class="slider-track">
                    <div class="slider-fill" :style="{ width: aiSettings.loyaltyWeight + '%' }"></div>
                  </div>
                </div>
              </div>

              <div class="info-box">
                <div class="info-content">
                  <span class="material-symbols-outlined info-icon">info</span>
                  <p class="info-text">
                    <span class="info-label">系统提示:</span>
                    当前 AI 正在使用 "Market Dynamics V2" 模型。过去30天内已优化 1,280 笔报价单，平均成交率提升了 12.4%。
                  </p>
                </div>
              </div>
            </div>
          </section>

          <section class="card">
            <h3 class="card-title">
              <span class="material-symbols-outlined">history</span>
              更新日志
            </h3>
            <div class="timeline">
              <div v-for="(log, index) in updateLogs" :key="index" class="timeline-item" :class="{ 'has-line': index < updateLogs.length - 1 }">
                <div class="timeline-dot" :class="{ active: log.active }"></div>
                <div class="timeline-content">
                  <p class="timeline-title" :class="{ 'text-white': log.active, 'text-muted': !log.active }">{{ log.action }}</p>
                  <p class="timeline-time" :class="{ 'text-muted': log.active, 'text-dimmer': !log.active }">{{ log.time }} · {{ log.user }}</p>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useProductCategories, DEFAULT_CATEGORIES, type ProductCategory } from '@/new/stores/productCategoryStore'

interface SLALevel {
  id: number
  name: string
  response: string
  coefficient: string
}

interface UpdateLog {
  action: string
  time: string
  user: string
  active: boolean
}

// 可选图标列表
const availableIcons = [
  'category',
  'shield_with_heart',
  'person_pin_circle',
  'headset_mic',
  'visibility',
  'layers',
  'shopping_cart',
  'memory',
  'confirmation_number',
  'local_shipping',
  'autorenew',
  'electrical_services',
  'cloud',
  'storefront',
  'settings',
  'support_agent',
  'construction',
  'business_center',
  'devices',
  'inventory_2',
  'warehouse',
  'precision_manufacturing',
  'cable',
  'router',
  'dns',
  'shield',
  'security'
]

// 使用共享的产品分类 store
const { categories, addCategory, deleteCategory, updateCategory } = useProductCategories()

// 新增分类对话框状态
const showAddCategoryDialog = ref(false)

// 新分类表单数据
const newCategory = ref({
  id: '',
  name: '',
  icon: 'category',
  description: ''
})

const selectedCategory = ref('maintenance')
const sidebarCollapsed = ref(false)

const currentCategoryName = computed(() => {
  const cat = categories.find((c: ProductCategory) => c.id === selectedCategory.value)
  return cat?.name.replace('报价', '') || ''
})

const currentCategoryDescription = computed(() => {
  const cat = categories.find((c: ProductCategory) => c.id === selectedCategory.value)
  return cat?.description || ''
})

// 添加新分类
function addNewCategory() {
  // 验证必填字段
  if (!newCategory.value.id.trim()) {
    alert('请输入分类代码')
    return
  }
  if (!newCategory.value.name.trim()) {
    alert('请输入分类名称')
    return
  }

  // 检查名称是否已存在（store 已检查 ID）
  const nameExists = categories.some((c: ProductCategory) => c.name === newCategory.value.name)
  if (nameExists) {
    alert('分类名称已存在，请使用其他名称')
    return
  }

  // 使用 store 添加分类
  const result = addCategory({
    id: newCategory.value.id,
    name: newCategory.value.name,
    icon: newCategory.value.icon,
    description: newCategory.value.description || ''
  })

  if (!result) {
    alert('分类代码已存在，请使用其他代码')
    return
  }

  // 添加到更新日志
  updateLogs.value.unshift({
    action: `创建分类: ${newCategory.value.name}`,
    time: '刚刚',
    user: '管理员',
    active: true
  })
  // 将之前的日志标记为非活跃
  updateLogs.value.forEach((log, index) => {
    if (index > 0) log.active = false
  })

  // 选中新创建的分类
  selectedCategory.value = newCategory.value.id

  // 重置表单并关闭对话框
  newCategory.value = {
    id: '',
    name: '',
    icon: 'category',
    description: ''
  }
  showAddCategoryDialog.value = false
}

// Form data
const formData = ref({
  productCode: 'SERVICE-MAINT-001',
  billingMode: '年费 (Annual)',
  basePrice: 12000.00,
  profitMargin: 45
})

// SLA Levels
const slaLevels = ref<SLALevel[]>([
  { id: 1, name: 'Standard (7x24x4)', response: '4小时内到达现场', coefficient: '1.0x' },
  { id: 2, name: 'Priority (7x24x2)', response: '2小时内到达现场', coefficient: '1.35x' },
  { id: 3, name: 'Economy (5x9xNBD)', response: '次个工作日响应', coefficient: '0.8x' }
])

// AI Settings
const aiSettings = ref({
  enabled: true,
  riskWeight: 65,
  loyaltyWeight: 40
})

// Update Logs
const updateLogs = ref<UpdateLog[]>([
  { action: '修改基准单价', time: '今天 14:30', user: '管理员', active: true },
  { action: '同步 AI 模型权重', time: '昨天 09:12', user: '系统任务', active: false },
  { action: '创建分类: 维保服务', time: '2023-10-24', user: '管理员', active: false }
])

// Methods
function selectCategory(id: string) {
  selectedCategory.value = id
}

// 删除分类
function deleteCategoryItem(category: ProductCategory) {
  // 检查是否为默认分类
  const isDefault = DEFAULT_CATEGORIES.some((c: ProductCategory) => c.id === category.id)
  if (isDefault) {
    alert('系统默认分类不能删除')
    return
  }

  // 确认删除
  const confirmed = confirm(`确定要删除分类"${category.name}"吗？此操作不可恢复。`)
  if (!confirmed) {
    return
  }

  // 执行删除
  const success = deleteCategory(category.id)
  if (success) {
    // 如果删除的是当前选中的分类，切换到默认分类
    if (selectedCategory.value === category.id) {
      selectedCategory.value = 'maintenance'
    }

    // 添加到更新日志
    updateLogs.value.unshift({
      action: `删除分类: ${category.name}`,
      time: '刚刚',
      user: '管理员',
      active: true
    })
    // 将之前的日志标记为非活跃
    updateLogs.value.forEach((log, index) => {
      if (index > 0) log.active = false
    })
  } else {
    alert('删除失败，请稍后重试')
  }
}

function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}
</script>

<style scoped>
.product-management {
  display: flex;
  height: 100%;
  overflow: hidden;
  background: #0f1923;
}

/* Left Sidebar */
.product-sidebar {
  width: 280px;
  border-right: 1px solid #2e4b6b;
  background: #0f1923;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  transition: width 0.3s;
}

.product-sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  padding: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  height: 3.5rem;
}

.product-sidebar:not(.collapsed) .sidebar-header {
  padding: 1.5rem 1rem 1.5rem;
  justify-content: flex-start;
}

.collapse-toggle {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  width: 2rem;
  height: 2rem;
  border: none;
  background: transparent;
  color: #8dacce;
  cursor: pointer;
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.collapse-toggle:hover {
  color: #fff;
  background: rgba(255, 255, 255, 0.1);
}

.collapse-toggle .material-symbols-outlined {
  font-size: 1.25rem;
}

.sidebar-title {
  color: #fff;
  font-size: 1rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-title .material-symbols-outlined {
  color: #007bff;
  font-size: 1.25rem;
}

.sidebar-subtitle {
  color: #8dacce;
  font-size: 0.75rem;
  margin-top: 0.25rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.category-list {
  flex: 1;
  padding: 0 0.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.5rem;
  border-radius: 0.5rem;
  color: #8dacce;
  cursor: pointer;
  transition: all 0.2s;
}

.product-sidebar:not(.collapsed) .category-item {
  padding: 0.625rem 0.75rem;
}

.category-item:hover {
  color: #fff;
  background: #16222e;
}

.category-item.active {
  background: #007bff;
  color: #fff;
  box-shadow: 0 4px 15px rgba(0, 123, 255, 0.2);
}

.category-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 1.5rem;
}

.category-icon .material-symbols-outlined {
  font-size: 1.25rem;
}

.category-name {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 分类名称包装器 - 用于放置名称和删除按钮 */
.category-name-wrapper {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.category-name-wrapper .category-name {
  flex: 1;
  min-width: 0;
}

/* 分类删除按钮 */
.category-delete-btn {
  display: none;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  background: transparent;
  border: none;
  color: #5a7a9a;
  cursor: pointer;
  border-radius: 0.25rem;
  transition: all 0.2s;
  flex-shrink: 0;
}

.category-delete-btn .material-symbols-outlined {
  font-size: 1rem;
}

.category-item:hover .category-delete-btn {
  display: flex;
}

.category-delete-btn:hover {
  background: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.sidebar-footer {
  padding: 1rem 0.75rem;
  border-top: 1px solid #2e4b6b;
  background: #0a1118;
}

.product-sidebar:not(.collapsed) .sidebar-footer {
  padding: 1rem 1.5rem;
}

.add-category-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background: #16222e;
  color: #fff;
  border: none;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.add-category-btn:hover {
  background: #2e4b6b;
}

/* Main Content */
.product-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow-y: auto;
}

/* Breadcrumbs */
.breadcrumbs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  font-size: 0.75rem;
}

.breadcrumb-link {
  color: #8dacce;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #fff;
}

.breadcrumb-separator {
  font-size: 0.75rem;
  color: #2e4b6b;
}

.breadcrumb-current {
  color: #fff;
  font-weight: 600;
}

/* Page Header */
.page-header {
  display: flex;
  flex-wrap: wrap;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  padding: 1rem 1.5rem 1.5rem;
}

.header-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.page-title {
  color: #fff;
  font-size: 1.875rem;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.page-description {
  color: #8dacce;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.action-btn.secondary {
  background: transparent;
  border: 1px solid #2e4b6b;
  color: #fff;
}

.action-btn.secondary:hover {
  background: #16222e;
}

.action-btn.primary {
  background: #007bff;
  color: #fff;
  box-shadow: 0 0 15px rgba(0, 123, 255, 0.4);
}

.action-btn.primary:hover {
  box-shadow: 0 0 25px rgba(0, 123, 255, 0.6);
  transform: translateY(-1px);
}

/* Tabs */
.tabs-nav {
  display: flex;
  border-bottom: 1px solid #2e4b6b;
  gap: 2rem;
  padding: 0 1.5rem;
}

.tab-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border-bottom: 2px solid transparent;
  padding: 0.75rem 0;
  color: #8dacce;
  text-decoration: none;
  transition: all 0.2s;
}

.tab-item:hover {
  color: #fff;
}

.tab-item.active {
  border-bottom-color: #007bff;
  color: #fff;
}

.tab-text {
  font-size: 0.875rem;
}

.tab-item.active .tab-text {
  font-weight: 600;
}

/* Content Panel */
.content-panel {
  padding: 1.5rem;
  display: grid;
  grid-template-columns: 1fr 340px;
  gap: 1.5rem;
}

@media (max-width: 1280px) {
  .content-panel {
    grid-template-columns: 1fr;
  }
}

.left-section,
.right-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* Cards */
.card {
  background: #16222e;
  border: 1px solid #2e4b6b;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.card-title {
  color: #fff;
  font-size: 1.125rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.card-title .material-symbols-outlined {
  color: #007bff;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
}

.add-btn {
  color: #007bff;
  font-size: 0.875rem;
  font-weight: 500;
  background: none;
  border: none;
  cursor: pointer;
}

.add-btn:hover {
  text-decoration: underline;
}

/* Form */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group label {
  color: #8dacce;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.form-group input,
.form-group select {
  width: 100%;
  background: #0f1923;
  border: 1px solid #2e4b6b;
  border-radius: 0.5rem;
  color: #fff;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.input-with-prefix {
  position: relative;
}

.input-with-prefix .prefix {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #8dacce;
}

.input-with-prefix input {
  padding-left: 2.25rem;
}

/* Table */
.table-container {
  overflow-x: auto;
}

.sla-table {
  width: 100%;
  text-align: left;
  font-size: 0.875rem;
}

.sla-table thead {
  color: #8dacce;
  border-bottom: 1px solid #2e4b6b;
}

.sla-table th {
  padding: 0.75rem 1rem;
  font-weight: 600;
  text-transform: uppercase;
}

.sla-table tbody {
  border-top: none;
}

.sla-table td {
  padding: 1rem;
  border-top: 1px solid rgba(46, 75, 107, 0.5);
}

.sla-table tr:hover td {
  background: rgba(255, 255, 255, 0.05);
}

.sla-table .font-medium {
  color: #fff;
  font-weight: 500;
}

.sla-table .text-muted {
  color: #8dacce;
}

.sla-table .text-right {
  text-align: right;
}

.coefficient-badge {
  background: rgba(0, 123, 255, 0.2);
  color: #007bff;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(0, 123, 255, 0.3);
  font-size: 0.75rem;
}

.icon-btn {
  background: none;
  border: none;
  color: #8dacce;
  cursor: pointer;
  padding: 0;
}

.icon-btn:hover {
  color: #fff;
}

/* AI Config */
.ai-config {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  background: #0f1923;
  border: 1px solid #2e4b6b;
  border-radius: 0.5rem;
}

.toggle-info {
  flex: 1;
}

.toggle-title {
  color: #fff;
  font-size: 0.875rem;
  font-weight: 600;
}

.toggle-desc {
  color: #8dacce;
  font-size: 0.625rem;
  margin-top: 0.125rem;
}

.toggle-switch {
  width: 3rem;
  height: 1.5rem;
  background: #2e4b6b;
  border-radius: 9999px;
  position: relative;
  cursor: pointer;
  transition: background 0.2s;
}

.toggle-switch.active {
  background: #007bff;
}

.toggle-dot {
  width: 1rem;
  height: 1rem;
  background: #fff;
  border-radius: 50%;
  position: absolute;
  top: 0.125rem;
  left: 0.125rem;
  transition: left 0.2s;
}

.toggle-switch.active .toggle-dot {
  left: 1.375rem;
}

.sliders {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.slider-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.slider-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
}

.slider-label {
  color: #8dacce;
}

.slider-value {
  color: #007bff;
  font-weight: 600;
}

.slider-track {
  width: 100%;
  height: 0.375rem;
  background: #0f1923;
  border-radius: 9999px;
  overflow: hidden;
}

.slider-fill {
  height: 100%;
  background: #007bff;
  border-radius: 9999px;
  transition: width 0.2s;
}

.info-box {
  padding: 1rem;
  background: rgba(0, 123, 255, 0.1);
  border: 1px solid rgba(0, 123, 255, 0.2);
  border-radius: 0.5rem;
}

.info-content {
  display: flex;
  gap: 0.75rem;
}

.info-icon {
  color: #007bff;
  font-size: 1.25rem;
}

.info-text {
  font-size: 0.6875rem;
  color: #8dacce;
  line-height: 1.5;
}

.info-label {
  color: #fff;
  font-weight: 600;
  display: block;
  margin-bottom: 0.25rem;
}

/* Timeline */
.timeline {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.timeline-item {
  display: flex;
  gap: 0.75rem;
  position: relative;
}

.timeline-item.has-line {
  padding-bottom: 1rem;
}

.timeline-item.has-line::after {
  content: '';
  position: absolute;
  left: 0.4375rem;
  top: 1.5rem;
  bottom: 0;
  width: 1px;
  background: #2e4b6b;
}

.timeline-dot {
  width: 1rem;
  height: 1rem;
  border-radius: 50%;
  background: #007bff;
  flex-shrink: 0;
  margin-top: 0.25rem;
  border: 4px solid #0f1923;
}

.timeline-dot:not(.active) {
  background: #2e4b6b;
}

.timeline-content {
  display: flex;
  flex-direction: column;
}

.timeline-title {
  font-size: 0.75rem;
  font-weight: 500;
  margin: 0;
}

.timeline-time {
  font-size: 0.625rem;
  margin: 0;
}

.text-dimmer {
  color: #2e4b6b;
}

/* Scrollbar */
.product-sidebar::-webkit-scrollbar,
.product-main::-webkit-scrollbar {
  width: 6px;
}

.product-sidebar::-webkit-scrollbar-track,
.product-main::-webkit-scrollbar-track {
  background: #0f1923;
}

.product-sidebar::-webkit-scrollbar-thumb,
.product-main::-webkit-scrollbar-thumb {
  background: #2e4b6b;
  border-radius: 10px;
}

.product-sidebar::-webkit-scrollbar-thumb:hover,
.product-main::-webkit-scrollbar-thumb:hover {
  background: #007bff;
}

/* 新增分类对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 9999;
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

.dialog-container {
  background: #16222e;
  border: 1px solid #2e4b6b;
  border-radius: 0.75rem;
  width: 90%;
  max-width: 500px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #2e4b6b;
}

.dialog-title {
  color: #fff;
  font-size: 1.125rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.dialog-title::before {
  content: '';
  display: inline-block;
  width: 4px;
  height: 1.25rem;
  background: #007bff;
  border-radius: 2px;
}

.dialog-close {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #8dacce;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.dialog-close:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.dialog-close .material-symbols-outlined {
  font-size: 1.25rem;
}

.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.dialog-body .form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dialog-body .form-group label {
  color: #8dacce;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dialog-body .form-group .required {
  color: #ef4444;
}

.dialog-body .form-input {
  width: 100%;
  background: #0f1923;
  border: 1px solid #2e4b6b;
  border-radius: 0.5rem;
  color: #fff;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.dialog-body .form-input:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.dialog-body .form-textarea {
  width: 100%;
  background: #0f1923;
  border: 1px solid #2e4b6b;
  border-radius: 0.5rem;
  color: #fff;
  padding: 0.625rem 1rem;
  font-size: 0.875rem;
  resize: vertical;
  min-height: 80px;
  font-family: inherit;
  transition: all 0.2s;
}

.dialog-body .form-textarea:focus {
  outline: none;
  border-color: #007bff;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.1);
}

.dialog-body .form-hint {
  font-size: 0.6875rem;
  color: #5a7a9a;
}

/* 图标选择器 */
.icon-selector {
  display: grid;
  grid-template-columns: repeat(8, 1fr);
  gap: 0.5rem;
}

.icon-option {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  background: #0f1923;
  border: 1px solid #2e4b6b;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-option:hover {
  border-color: #007bff;
  background: rgba(0, 123, 255, 0.1);
}

.icon-option.selected {
  background: #007bff;
  border-color: #007bff;
}

.icon-option.selected .material-symbols-outlined {
  color: #fff;
}

.icon-option .material-symbols-outlined {
  font-size: 1.25rem;
  color: #8dacce;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #2e4b6b;
  background: #0f1923;
}

.dialog-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.cancel-btn {
  background: transparent;
  border: 1px solid #2e4b6b;
  color: #fff;
}

.cancel-btn:hover {
  background: #16222e;
  border-color: #4a6a8a;
}

.confirm-btn {
  background: #007bff;
  color: #fff;
}

.confirm-btn:hover {
  background: #0056b3;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 123, 255, 0.3);
}
</style>
