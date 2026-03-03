<template>
  <div class="smart-matching">
    <BranchPageHeader @open-product-database="openProductDatabaseModal" />

    <main class="main-container">
      <div class="page-header">
        <div class="header-content">
          <div class="breadcrumb">
            <a @click="navigateToHome" class="breadcrumb-link">首页</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <span class="breadcrumb-current">智能匹配</span>
          </div>
          <h1 class="page-title">智能匹配</h1>
          <p class="page-description">系统自动匹配设备型号并计算价格，低置信度条目建议人工复核。</p>
        </div>
        <div class="header-right">
          <div class="steps-progress">
            <div class="step completed">
              <div class="step-number">1</div>
              <span class="step-label" @click="navigateToDocumentRecognition" style="cursor: pointer;">导入数据</span>
            </div>
            <div class="step-divider"></div>
            <div class="step active">
              <div class="step-number">2</div>
              <span class="step-label" @click="navigateToSmartMatching" style="cursor: pointer;">智能匹配</span>
            </div>
            <div class="step-divider"></div>
            <div class="step">
              <div class="step-number">3</div>
              <span class="step-label" @click="navigateToPriceAdjustment" style="cursor: pointer;">价格调整</span>
            </div>
            <div class="step-divider"></div>
            <div class="step">
              <div class="step-number">4</div>
              <span class="step-label" @click="navigateToQuotationGeneration" style="cursor: pointer;">生成报价</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-state" v-if="tableData.length === 0 && !loading">
        <div class="empty-content">
          <span class="material-symbols-outlined empty-icon">device_search</span>
          <p class="empty-title">暂无数据</p>
          <p class="empty-subtitle">请先在"导入数据"页面上传Excel文件</p>
          <button class="btn-primary" @click="navigateToDocumentRecognition">
            <span class="material-symbols-outlined">upload_file</span>
            前往导入数据
          </button>
        </div>
      </div>

      <!-- Matching Progress -->
      <div class="matching-progress" v-if="matchingInProgress">
        <div class="progress-content">
          <span class="material-symbols-outlined progress-icon">sync</span>
          <div class="progress-info">
            <p class="progress-title">正在智能匹配中...</p>
            <p class="progress-status">已处理 {{ matchingCompleted }} / {{ matchingTotal }} 条数据</p>
          </div>
          <div class="progress-bar-wrapper">
            <div class="progress-bar" :style="{ width: matchingProgress + '%' }"></div>
          </div>
          <span class="progress-percent">{{ matchingProgress }}%</span>
          <button class="stop-matching-btn" @click="stopMatching" title="停止匹配">
            <span class="material-symbols-outlined">stop</span>
            停止
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid" v-if="tableData.length > 0">
        <div class="stat-card">
          <span class="stat-label">导入总行数</span>
          <div class="stat-content">
            <span class="stat-value">{{ tableData.length }}</span>
            <span class="material-symbols-outlined stat-icon">list_alt</span>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-bar"></div>
          <span class="stat-label">成功匹配 (高置信度)</span>
          <div class="stat-content">
            <span class="stat-value">{{ highConfidenceCount }}</span>
            <span class="material-symbols-outlined stat-icon">check_circle</span>
          </div>
        </div>

        <div class="stat-card warning">
          <div class="stat-bar"></div>
          <div class="stat-header">
            <span class="stat-label">需人工复核 (低置信度)</span>
            <span class="stat-badge" v-if="lowConfidenceCount > 0">待复核</span>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ lowConfidenceCount }}</span>
            <span class="material-symbols-outlined stat-icon">warning</span>
          </div>
        </div>

        <div class="stat-card error">
          <div class="stat-bar"></div>
          <div class="stat-header">
            <span class="stat-label">未匹配</span>
            <span class="stat-badge" v-if="unmatchedCount > 0">需处理</span>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ unmatchedCount }}</span>
            <span class="material-symbols-outlined stat-icon">error</span>
          </div>
        </div>
      </div>

      <!-- Data Table -->
      <div class="table-container" v-if="tableData.length > 0">
        <div class="table-header">
          <div class="table-controls-left">
            <div class="filter-select">
              <span class="material-symbols-outlined">filter_list</span>
              <select v-model="filterStatus">
                <option value="all">显示全部状态</option>
                <option value="low">仅显示低置信度</option>
                <option value="unmatched">仅显示未匹配</option>
                <option value="matched">仅显示已匹配</option>
              </select>
            </div>
            <div class="data-source-select">
              <span class="material-symbols-outlined">storage</span>
              <select v-model="dataSource">
                <option value="datacenter">数据中心设备</option>
                <option value="office">办公设备</option>
                <option value="hybrid">混合模式</option>
              </select>
            </div>
            <div class="pricing-params-dropdown" v-click-outside="closePricingParamsDropdown">
              <button class="pricing-params-btn" @click="togglePricingParamsDropdown" :class="{ active: showPricingParamsDropdown }">
                <span class="material-symbols-outlined">tune</span>
                <span>调价参数</span>
                <span class="material-symbols-outlined dropdown-arrow">expand_more</span>
              </button>
              <div class="pricing-params-panel" v-if="showPricingParamsDropdown">
                <div class="params-panel-header">
                  <span class="params-panel-title">调价参数设置</span>
                  <span class="params-panel-desc">启用后将在报价计算时应用</span>
                </div>
                <div class="params-list">
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">workspace_premium</span>
                      <div class="param-text">
                        <span class="param-name">服务模式</span>
                        <span class="param-desc">金牌/银牌/铜牌服务费率</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.serviceMode" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">schedule</span>
                      <div class="param-text">
                        <span class="param-name">时效因子</span>
                        <span class="param-desc">SLA服务级别系数</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.slaFactor" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">memory</span>
                      <div class="param-text">
                        <span class="param-name">硬件折旧系数</span>
                        <span class="param-desc">设备年折旧率调整</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.hardwareDepreciation" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">public</span>
                      <div class="param-text">
                        <span class="param-name">区域调节系数</span>
                        <span class="param-desc">地区价格系数</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.regionalAdjustment" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                </div>
                <div class="params-panel-footer">
                  <button class="params-reset-btn" @click="resetPricingParams">重置为默认</button>
                  <button class="params-apply-btn" @click="applyPricingParams">应用设置</button>
                </div>
              </div>
            </div>
          </div>
          <div class="table-controls-right">
            <button class="btn-danger" @click="deleteSelectedRows" :disabled="selectedRows.size === 0">
              <span class="material-symbols-outlined">delete</span>
              删除
              <span v-if="selectedRows.size > 0" class="delete-count">({{ selectedRows.size }})</span>
            </button>
            <button class="btn-secondary" @click="startMatching" :disabled="matchingInProgress">
              <span class="material-symbols-outlined">refresh</span>
              重新匹配
            </button>
            <button class="btn-primary" @click="exportData">
              <span class="material-symbols-outlined">download</span>
              导出数据
            </button>
          </div>
        </div>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <label class="custom-checkbox" @click="toggleSelectAll">
                    <span class="checkbox-circle" :class="{ 'checked': isAllSelected, 'indeterminate': isPartialSelected }">
                      <span class="material-symbols-outlined" v-if="isAllSelected">check</span>
                      <span class="material-symbols-outlined" v-else-if="isPartialSelected">remove</span>
                    </span>
                  </label>
                </th>
                <th class="col-index">序号</th>
                <th class="col-manufacturer">厂商</th>
                <th class="col-model">原始品牌型号</th>
                <th class="col-category">分类</th>
                <th class="col-service-level">服务级别</th>
                <th class="col-match">匹配型号</th>
                <th class="col-confidence">置信度</th>
                <th class="col-price">原始单价</th>
                <th class="col-coefficient">服务系数</th>
                <th class="col-adjusted-price">调整后单价</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="(item, index) in filteredTableData"
                :key="index"
                :class="{
                  'warning-row': item.matchRate > 0 && item.matchRate < 70,
                  'error-row': !item.matchedModel || item.matchRate === 0
                }"
              >
                <td class="col-checkbox">
                  <label class="custom-checkbox" @click="toggleRowSelection(getOriginalIndex(item))">
                    <span class="checkbox-circle" :class="{ 'checked': selectedRows.has(getOriginalIndex(item)) }">
                      <span class="material-symbols-outlined" v-if="selectedRows.has(getOriginalIndex(item))">check</span>
                    </span>
                  </label>
                </td>
                <td class="col-index">{{ index + 1 }}</td>
                <td class="col-manufacturer">{{ item.manufacturer || '-' }}</td>
                <td class="col-model">
                  <span class="original-model">{{ item.originalBrandModel || '-' }}</span>
                </td>
                <td class="col-category">{{ item.deviceCategory || '-' }}</td>
                <td class="col-service-level">{{ item.serviceLevel || '-' }}</td>
                <td class="col-match">
                  <div class="match-cell-wrapper">
                  <span
                    class="matched-model"
                    :class="{
                      'high-match': item.matchRate >= 70,
                      'mid-match': item.matchRate >= 50 && item.matchRate < 70,
                      'low-match': item.matchRate > 0 && item.matchRate < 50,
                      'no-match': !item.matchedModel || item.matchRate === 0
                    }"
                    @click="openSearch(index)"
                    :title="'点击修改匹配型号'"
                  >
                    {{ item.matchedModel || '未匹配' }}
                  </span>
                    <button
                      v-if="item.matchedModel"
                      class="clear-match-btn"
                      @click.stop="clearMatchResult(index)"
                      title="清空匹配结果"
                    >
                      <span class="material-symbols-outlined">close</span>
                    </button>
                  </div>
                </td>
                <td class="col-confidence">
                  <span
                    class="confidence-badge"
                    :class="{
                      'high': item.matchRate >= 70,
                      'mid': item.matchRate >= 50 && item.matchRate < 70,
                      'low': item.matchRate > 0 && item.matchRate < 50,
                      'none': !item.matchedModel || item.matchRate === 0
                    }"
                  >
                    {{ item.matchRate ? Math.round(item.matchRate) + '%' : '-' }}
                  </span>
                </td>
                <td class="col-price">{{ item.originalPrice ? '¥' + item.originalPrice.toFixed(2) : '-' }}</td>
                <td class="col-coefficient">
                  <span v-if="item.serviceLevelCoefficient !== 1" class="coefficient-value">
                    {{ item.serviceLevelCoefficient.toFixed(2) }}
                  </span>
                  <span v-else>-</span>
                </td>
                <td class="col-adjusted-price">{{ item.price ? '¥' + item.price.toFixed(2) : '-' }}</td>
                <td class="col-actions">
                  <button class="action-btn edit" @click="openSearch(index)" title="修改匹配">
                    <span class="material-symbols-outlined">edit</span>
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div class="table-footer">
          <span class="footer-text">显示 {{ filteredTableData.length }} 条数据，共 {{ tableData.length }} 条</span>
        </div>
      </div>
    </main>

    <!-- Search Dialog -->
    <div class="dialog-overlay" v-if="showSearchDialog" @click="closeSearchDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3 class="dialog-title">手动搜索设备</h3>
          <button class="dialog-close" @click="closeSearchDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <!-- 数据源选择 -->
          <div class="search-source-selector">
            <label class="source-label">数据来源：</label>
            <div class="source-options">
              <label class="source-option">
                <input
                  type="radio"
                  name="searchDataSource"
                  value="datacenter"
                  v-model="searchDataSource"
                  @change="onSearchDataSourceChange"
                />
                <span class="source-radio"></span>
                <span class="source-name">数据中心设备</span>
              </label>
              <label class="source-option">
                <input
                  type="radio"
                  name="searchDataSource"
                  value="office"
                  v-model="searchDataSource"
                  @change="onSearchDataSourceChange"
                />
                <span class="source-radio"></span>
                <span class="source-name">办公设备</span>
              </label>
              <label class="source-option">
                <input
                  type="radio"
                  name="searchDataSource"
                  value="hybrid"
                  v-model="searchDataSource"
                  @change="onSearchDataSourceChange"
                />
                <span class="source-radio"></span>
                <span class="source-name">混合模式</span>
              </label>
            </div>
          </div>

          <div class="search-input-group">
            <span class="material-symbols-outlined">search</span>
            <input
              ref="searchInputRef"
              type="text"
              v-model="searchQuery"
              @input="handleSearchInput"
              placeholder="输入设备型号搜索..."
              class="search-input-field"
            />
          </div>
          <div class="search-results" v-if="searchLoading">
            <div class="search-loading">
              <span class="material-symbols-outlined loading-icon">sync</span>
              <span>搜索中...</span>
            </div>
          </div>
          <div class="search-results" v-else-if="searchResults.length > 0">
            <div class="results-header">找到 {{ totalResults }} 条结果</div>
            <div class="results-list">
              <div
                v-for="result in searchResults"
                :key="result.id"
                class="result-item"
                @click="selectSearchResult(result)"
              >
                <div class="result-info">
                  <div class="result-model">{{ result.model_number || result.model }}</div>
                  <div class="result-details">
                    {{ result.manufacturer }} • {{ result.primary_category }} >
                    {{ result.secondary_category }} > {{ result.tertiary_category }}
                  </div>
                </div>
                <div class="result-price" v-if="result.device_price">
                  ¥{{ result.device_price.toFixed(2) }}
                </div>
              </div>
            </div>
            <div class="results-pagination" v-if="totalResults > pageSize">
              <button
                class="page-btn"
                :disabled="searchPage === 1"
                @click="changeSearchPage(searchPage - 1)"
              >
                <span class="material-symbols-outlined">chevron_left</span>
              </button>
              <span class="page-info">第 {{ searchPage }} 页</span>
              <button
                class="page-btn"
                :disabled="searchPage * pageSize >= totalResults"
                @click="changeSearchPage(searchPage + 1)"
              >
                <span class="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
          <div class="search-results" v-else-if="searchQuery && searchQuery.length >= 2">
            <div class="no-results">
              <span class="material-symbols-outlined">search_off</span>
              <span>未找到匹配的设备</span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeSearchDialog">取消</button>
        </div>
      </div>
    </div>

    <!-- Sticky Bottom Bar -->
    <div class="bottom-bar" v-if="tableData.length > 0">
      <div class="bottom-content">
        <div class="bottom-info" v-if="lowConfidenceCount > 0 || unmatchedCount > 0">
          <span class="material-symbols-outlined">info</span>
          <span>还有 <strong>{{ lowConfidenceCount + unmatchedCount }}</strong> 个条目需要处理</span>
        </div>
        <div class="bottom-info" v-else>
          <span class="material-symbols-outlined" style="color: #22c55e;">check_circle</span>
          <span>所有条目已完成匹配</span>
        </div>
        <div class="bottom-actions">
          <button class="btn-back" @click="navigateToDocumentRecognition">
            <span class="material-symbols-outlined">arrow_back</span>
            上一步
          </button>
          <div class="action-buttons">
            <button class="btn-draft" @click="saveAsDraft" :disabled="isSavingDraft" :title="'快捷键: Ctrl+S'">
              <span class="material-symbols-outlined" v-if="!isSavingDraft">save</span>
              <span class="material-symbols-outlined spinning" v-else>sync</span>
              {{ isSavingDraft ? '保存中...' : '存为草稿' }}
            </button>
            <button class="btn-next" @click="goToPriceAdjustment" :disabled="isNavigating">
              <span class="material-symbols-outlined spinning" v-if="isNavigating">sync</span>
              <span v-else>下一步: 价格调整</span>
              <span class="material-symbols-outlined" v-if="!isNavigating">arrow_forward</span>
          </button>
          </div>
        </div>
      </div>
    </div>

    <div class="background-effects">
      <div class="effect-blob effect-top"></div>
      <div class="effect-blob effect-bottom"></div>
    </div>

    <!-- 产品数据库弹窗 -->
    <ProductDatabaseModal :is-open="isProductDatabaseModalOpen" @close="closeProductDatabaseModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, shallowRef, triggerRef, watch } from 'vue'
import { useRouter, onBeforeRouteUpdate, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import BranchPageHeader from '../components/BranchPageHeader.vue'
import ProductDatabaseModal from '../components/ProductDatabaseModal.vue'
import {
  PAGE_STATE_KEYS,
  FLOW_DATA_KEYS,
  savePageState,
  restorePageState,
  clearPageState,
  saveFlowData,
  clearFlowData,
  getFlowData,
  setNavigationMode,
  cleanupOldFlowData,
  type SmartMatchingState
} from '../stores/quotationStore'
import {
  saveDraft,
  getCurrentDraftId
} from '../utils/draftUtils'

const router = useRouter()

// v-click-outside directive
const vClickOutside = {
  mounted(el: any, binding: any) {
    el._clickOutside = (event: MouseEvent) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el._clickOutside)
  }
}

// API Base URL
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
// 使用 shallowRef 优化大数据量性能，只追踪数组引用变化而不追踪内部对象
const tableData = shallowRef<any[]>([])
const loading = ref(false)
const isSavingDraft = ref(false)
const isNavigating = ref(false)
const matchingInProgress = ref(false)
const matchingTotal = ref(0)
const matchingCompleted = ref(0)
const matchingProgress = computed(() => {
  if (!matchingTotal.value) return 0
  return Math.floor((matchingCompleted.value / matchingTotal.value) * 100)
})

// Filter
const filterStatus = ref<'all' | 'low' | 'unmatched' | 'matched'>('all')

// Row selection for deletion
const selectedRows = ref<Set<number>>(new Set())

// Data source
const dataSource = ref<'datacenter' | 'office' | 'hybrid'>('datacenter')

// Pricing params dropdown
const showPricingParamsDropdown = ref(false)
const pricingParams = ref({
  serviceMode: true,
  slaFactor: true,
  hardwareDepreciation: false,
  regionalAdjustment: false
})

// Search dialog
const showSearchDialog = ref(false)
const activeModelIndex = ref<number | null>(null)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const searchLoading = ref(false)
const totalResults = ref(0)
const searchPage = ref(1)

// 产品数据库弹窗
const isProductDatabaseModalOpen = ref(false)

const openProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = true
}

const closeProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = false
}
const pageSize = 20
const searchInputRef = ref<HTMLInputElement | null>(null)
// 搜索对话框中的数据源选择（只对该次搜索有效）
const searchDataSource = ref<'datacenter' | 'office' | 'hybrid'>('datacenter')
let searchTimeout: NodeJS.Timeout | null = null

// Service levels cache (to avoid repeated API calls)
const serviceLevelsCache = ref<any[] | null>(null)

// AbortController for cancelling matching requests
const abortController = ref<AbortController | null>(null)
const shouldStop = ref(false)

// Maintenance rates cache (for manual price calculation)
const maintenanceRatesCache = ref<any[] | null>(null)

// Track manual adjustments (记录手动调整的匹配结果)
const manualAdjustments = ref<any[]>([])

// Stats
const highConfidenceCount = computed(() =>
  tableData.value.filter(item => item.matchRate >= 70).length
)
const lowConfidenceCount = computed(() =>
  tableData.value.filter(item => item.matchRate > 0 && item.matchRate < 70).length
)
const unmatchedCount = computed(() =>
  tableData.value.filter(item => !item.matchedModel || item.matchRate === 0).length
)

// Filtered table data
const filteredTableData = computed(() => {
  if (filterStatus.value === 'all') return tableData.value
  if (filterStatus.value === 'low') return tableData.value.filter(item => item.matchRate > 0 && item.matchRate < 70)
  if (filterStatus.value === 'unmatched') return tableData.value.filter(item => !item.matchedModel || item.matchRate === 0)
  if (filterStatus.value === 'matched') return tableData.value.filter(item => item.matchRate >= 70)
  return tableData.value
})

// Selection computed properties
const isAllSelected = computed(() => {
  if (filteredTableData.value.length === 0) return false
  return filteredTableData.value.every(item => selectedRows.value.has(tableData.value.indexOf(item)))
})

const isPartialSelected = computed(() => {
  if (filteredTableData.value.length === 0) return false
  const selectedCount = filteredTableData.value.filter(item => selectedRows.value.has(tableData.value.indexOf(item))).length
  return selectedCount > 0 && selectedCount < filteredTableData.value.length
})

// Get original index in tableData for a filtered item
function getOriginalIndex(item: any): number {
  return tableData.value.indexOf(item)
}

// Toggle single row selection
function toggleRowSelection(index: number) {
  const newSet = new Set(selectedRows.value)
  if (newSet.has(index)) {
    newSet.delete(index)
  } else {
    newSet.add(index)
  }
  selectedRows.value = newSet
}

// Toggle all rows selection
function toggleSelectAll() {
  if (isAllSelected.value) {
    // Deselect all filtered items
    const newSet = new Set(selectedRows.value)
    filteredTableData.value.forEach(item => {
      newSet.delete(tableData.value.indexOf(item))
    })
    selectedRows.value = newSet
  } else {
    // Select all filtered items
    const newSet = new Set(selectedRows.value)
    filteredTableData.value.forEach(item => {
      newSet.add(tableData.value.indexOf(item))
    })
    selectedRows.value = newSet
  }
}

// Delete selected rows
function deleteSelectedRows() {
  if (selectedRows.value.size === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.size} 条数据吗？删除后的数据将不进行下一步的流转。`,
    '确认删除',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    // Convert Set to sorted array (descending) to avoid index shift issues
    const indicesToDelete = Array.from(selectedRows.value).sort((a, b) => b - a)

    // Create new array without deleted items
    const newData = tableData.value.filter((_, index) => !selectedRows.value.has(index))
    tableData.value = newData

    // Clear selection
    selectedRows.value = new Set()

    // Update page state
    savePageState(PAGE_STATE_KEYS.SMART_MATCHING, getCurrentState())

    ElMessage.success(`已删除 ${indicesToDelete.length} 条数据`)
  }).catch(() => {
    // User cancelled
  })
}

// Clear selection when filter changes
watch(filterStatus, () => {
  selectedRows.value = new Set()
})

// Navigation
const navigateToHome = () => router.push('/')
const navigateToDocumentRecognition = () => router.push('/document-recognition')
const navigateToSmartMatching = () => {
  // 当前页面，无需跳转
}
const navigateToPriceAdjustment = () => {
  // 面包屑跳转：直接跳转，由目标页面恢复自己的状态
  router.push('/price-adjustment')
}
const navigateToQuotationGeneration = () => router.push('/quotation-generation')

// 流程推进：保存当前状态并进入下一步
const goToPriceAdjustment = async () => {
  // 防止重复点击
  if (isNavigating.value) {
    return
  }

  isNavigating.value = true
  ElMessage.info(`正在处理 ${tableData.value.length} 条数据，请稍候...`)

  try {
  // 发送手动调整数据到后端
  console.log('准备发送手动调整数据:', manualAdjustments.value)
  if (manualAdjustments.value.length > 0) {
    try {
      const response = await axios.post(`${API_URL}/manual-matching-override/batch`, manualAdjustments.value)
      console.log(`已成功发送 ${manualAdjustments.value.length} 条手动调整记录到后端`, response.data)
      // 清空已发送的记录
      manualAdjustments.value = []
    } catch (error) {
      console.error('发送手动调整数据失败:', error)
        ElMessage.warning('部分手动调整数据保存失败，但将继续跳转')
    }
  } else {
    console.log('没有手动调整数据需要发送')
  }

    // 先清理旧数据以释放空间
    cleanupOldFlowData('match')

    // 使用 nextTick 确保 DOM 更新后再保存数据，避免阻塞 UI
    await nextTick()

    // 尝试保存当前页面状态（使用 try-catch 包裹，失败不影响流程）
    try {
  savePageState(PAGE_STATE_KEYS.SMART_MATCHING, getCurrentState())
    } catch (error) {
      console.warn('Failed to save page state, continuing with flow data only:', error)
    }

    // 保存流程数据供下一页面使用（这是关键数据，必须成功）
    // 使用异步方式保存，避免阻塞
    await new Promise<void>((resolve) => {
      // 使用 setTimeout 将数据保存操作放到下一个事件循环，避免阻塞 UI
      setTimeout(() => {
        try {
  saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, tableData.value)
          console.log(`Flow data saved successfully: ${tableData.value.length} items`)
          resolve()
        } catch (error) {
          console.error('Failed to save flow data:', error)
          ElMessage.error('数据保存失败，请重试或减少数据量')
          isNavigating.value = false
          throw error
        }
      }, 0)
    })

  // 设置导航模式为 'flow'（流程推进），触发下一页面的重新加载逻辑
  setNavigationMode('flow')
    
    // 使用 nextTick 确保数据保存完成后再跳转
    await nextTick()
    
    // 跳转到价格调整页面
  router.push('/price-adjustment')
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('跳转失败，请重试')
    isNavigating.value = false
  }
}

// 存为草稿
async function saveAsDraft() {
  if (tableData.value.length === 0) {
    ElMessage.warning('请先完成数据匹配后再保存草稿')
    return
  }

  isSavingDraft.value = true
  try {
    // 保存当前状态
    savePageState(PAGE_STATE_KEYS.SMART_MATCHING, getCurrentState())
    saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, tableData.value)

    // 获取当前草稿ID（如果有）
    const existingDraftId = getCurrentDraftId()

    // 保存草稿
    await saveDraft('smart_matching', existingDraftId ?? undefined)

    ElMessage.success('草稿保存成功')
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败，请重试')
  } finally {
    isSavingDraft.value = false
  }
}

// 键盘快捷键处理
function handleKeyDown(event: KeyboardEvent) {
  // Ctrl+S 或 Cmd+S 保存草稿
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    saveAsDraft()
  }
}

// Get current state for saving
function getCurrentState(): SmartMatchingState {
  return {
    tableData: tableData.value,
    dataSource: dataSource.value,
    filterStatus: filterStatus.value,
    hasData: tableData.value.length > 0
  }
}

// Load data from sessionStorage
onMounted(async () => {
  // Check if we should trigger new matching (from "下一步" button)
  const triggerMatching = getFlowData<boolean>(FLOW_DATA_KEYS.TRIGGER_MATCHING)

  if (triggerMatching === true) {
    // Clear the trigger flag
    clearFlowData(FLOW_DATA_KEYS.TRIGGER_MATCHING)
    // Clear any existing page state to force fresh matching
    clearPageState(PAGE_STATE_KEYS.SMART_MATCHING)
    // Load data and trigger matching
    await loadData(true)
    return
  }

  // First try to restore page state (breadcrumb navigation or page refresh)
  const savedState = restorePageState<SmartMatchingState>(PAGE_STATE_KEYS.SMART_MATCHING)
  if (savedState && savedState.hasData) {
    // Restore page state - do NOT trigger matching
    tableData.value = savedState.tableData || []
    dataSource.value = savedState.dataSource || 'datacenter'
    filterStatus.value = savedState.filterStatus || 'all'
    console.log('Restored saved state:', tableData.value.length, 'items')
    return  // 已有数据，不继续检查
  }

  // Second: check for matched data from flow (from "next step" navigation)
    const matchedData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
    if (matchedData && matchedData.length > 0) {
      // Restore matched data without triggering matching
      tableData.value = matchedData
    console.log('Restored matched data:', tableData.value.length, 'items')
    return  // 已有数据，不继续检查
  }

  // Third: only trigger matching if explicitly requested (from "下一步" button)
  // Do NOT auto-trigger matching on breadcrumb navigation or page refresh
  console.log('No saved data found, not triggering automatic matching')

  // 添加键盘快捷键监听
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // 移除键盘快捷键监听
  window.removeEventListener('keydown', handleKeyDown)
})

// Handle navigation when component is already mounted (breadcrumb navigation)
onBeforeRouteUpdate((to, from, next) => {
  // 当从其他页面（如"价格调整"）返回"智能匹配"时
  // 需要先保存源页面的状态，然后恢复本页面的状态
  if (to.path === '/smart-matching' && from.path !== '/smart-matching') {
    // 从其他页面返回：恢复智能匹配的保存状态
    const savedState = restorePageState<SmartMatchingState>(PAGE_STATE_KEYS.SMART_MATCHING)
    if (savedState && savedState.hasData && savedState.tableData && savedState.tableData.length > 0) {
      // 恢复页面状态 - 不触发匹配
      tableData.value = savedState.tableData
      dataSource.value = savedState.dataSource || 'datacenter'
      filterStatus.value = savedState.filterStatus || 'all'
      console.log('Breadcrumb navigation: restored SmartMatching state with', tableData.value.length, 'items')
      next()
      return
    }

    // 如果没有保存的页面状态，尝试从流程数据加载
      const matchedData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
      if (matchedData && matchedData.length > 0) {
        tableData.value = matchedData
      console.log('Breadcrumb navigation: restored flow data with', tableData.value.length, 'items')
      next()
      return
      }

    console.log('Breadcrumb navigation: no saved data found')
  }
  next()
})

// Automatically save state when leaving this page (for breadcrumb navigation restore)
onBeforeRouteLeave((to, from, next) => {
  // 离开页面时始终保存状态，以便面包屑导航可以恢复
  if (tableData.value.length > 0) {
    const currentState = getCurrentState()

    // 尝试保存页面状态（用于面包屑返回时恢复）
    try {
      savePageState(PAGE_STATE_KEYS.SMART_MATCHING, currentState)
      console.log('SmartMatching state saved:', currentState.tableData.length, 'items')
    } catch (error) {
      console.error('Failed to save SmartMatching state:', error)
    }

    // 同时保存流程数据（供下一步使用）
    try {
    saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, tableData.value)
      console.log('SmartMatching flow data saved:', tableData.value.length, 'items')
    } catch (error) {
      console.error('Failed to save SmartMatching flow data:', error)
      // 如果保存失败，可能是 sessionStorage 容量不足
      // 清理一些旧数据后重试
      try {
        // 清除 CONVERTED_DATA（已经匹配完成，不再需要原始数据）
        clearFlowData(FLOW_DATA_KEYS.CONVERTED_DATA)
        saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, tableData.value)
        console.log('SmartMatching flow data saved after cleanup:', tableData.value.length, 'items')
      } catch (retryError) {
        console.error('Failed to save flow data even after cleanup:', retryError)
      }
    }
  }
  next()
})

async function loadData(triggerMatching: boolean = false) {
  try {
    const stored = getFlowData<any[]>(FLOW_DATA_KEYS.CONVERTED_DATA)
    if (stored && stored.length > 0) {
      // Initialize table data from converted data
      tableData.value = stored.map(row => ({
        manufacturer: row['厂商'] || '',
        model: row['设备/软件型号'] || '',
        originalBrandModel: `${row['厂商'] || ''}-${row['设备/软件型号'] || ''}`,  // 原始品牌型号 = 厂商-型号
        originalManufacturer: row['厂商'] || '',  // 保存原始厂商（来自Excel，永不修改）
        category: row['设备/软件分类'] || '',
        deviceCategory: '',
        serviceLevel: row['服务级别'] || '7*24*NCR',
        // 保留来自智能识别模块的字段，供价格调整使用
        city: row['城市'] || '',
        servicePeriod: row['服务周期'] || '1',
        servicePeriodUnit: normalizeServicePeriodUnit(row['服务周期单位']),
        // 匹配相关字段
        matchedModel: '',
        matchRate: 0,
        matchedManufacturer: '',  // 匹配到的厂商
        matchedSeries: '',        // 匹配到的设备系列
        originalPrice: null as number | null,
        price: null as number | null,
        serviceLevelCoefficient: 1,
        matchedServiceLevel: null,
        confirmed: false,
        primary_category: '',
        secondary_category: '',
        tertiary_category: '',
        device_price: null as number | null,
        rate: 0
      }))

      // Only auto start matching if explicitly requested (e.g., from "下一步" button)
      if (triggerMatching) {
        nextTick(() => {
          startMatching()
        })
      }
    }
  } catch (error) {
    console.error('Failed to load converted data:', error)
  }
}

// Start matching
async function startMatching() {
  if (matchingInProgress.value || tableData.value.length === 0) return

  matchingInProgress.value = true
  matchingTotal.value = tableData.value.length
  matchingCompleted.value = 0
  shouldStop.value = false
  abortController.value = new AbortController()

  // Load service levels once at the start (cache for all rows)
  // Use legacy API to get data with service_level field
  if (!serviceLevelsCache.value) {
    try {
      const response = await axios.get(`${API_URL}/service-level/legacy/`)
      serviceLevelsCache.value = response.data || []
    } catch (error) {
      console.error('Failed to load service levels:', error)
      serviceLevelsCache.value = []
    }
  }

  // Load maintenance rates for manual price calculation
  if (!maintenanceRatesCache.value) {
    try {
      const response = await axios.get(`${API_URL}/maintenance_rates/`)
      maintenanceRatesCache.value = response.data || []
    } catch (error) {
      console.error('Failed to load maintenance rates:', error)
      maintenanceRatesCache.value = []
    }
  }

  // 使用分批并发匹配，实时更新进度
  await individualMatching()

  matchingInProgress.value = false
  abortController.value = null
}

// Individual matching - 分批并发匹配，实时更新进度
async function individualMatching() {
  const concurrency = 10  // 增加并发数到10
  let current = 0
  const total = tableData.value.length

  async function worker() {
    while (current < total && !shouldStop.value) {
      const index = current++
      const item = tableData.value[index]

      try {
        const response = await axios.post(`${API_URL}/match/`, {
          manufacturer: item.manufacturer,
          model: item.model,
          category: item.category,
          source: dataSource.value
        }, {
          signal: abortController.value?.signal
        })

        if (response.data) {
          tableData.value[index].matchedModel = response.data.matched_model || ''
          tableData.value[index].matchRate = response.data.match_rate || 0
          // 原始单价 = 设备价格 × 费率（未含税）
          tableData.value[index].originalPrice = (response.data.device_price || 0) * (response.data.rate || 0)
          tableData.value[index].deviceCategory = response.data.device_category || response.data.category || ''
          tableData.value[index].device_price = response.data.device_price || null
          tableData.value[index].primary_category = response.data.primary_category || ''
          tableData.value[index].secondary_category = response.data.secondary_category || ''
          tableData.value[index].tertiary_category = response.data.tertiary_category || ''
          tableData.value[index].rate = response.data.rate || 0
          // 保存匹配到的厂商和系列信息，供价格调整模块使用
          tableData.value[index].matchedManufacturer = response.data.manufacturer || ''
          tableData.value[index].matchedSeries = response.data.device_series || ''
          // 更新显示的厂商为匹配到的厂商（与手动匹配逻辑一致）
          // 如果后端返回了厂商，则用后端返回的；否则保留原始值
          if (response.data.manufacturer) {
            tableData.value[index].manufacturer = response.data.manufacturer
          }

          if (tableData.value[index].originalPrice && item.serviceLevel) {
            const priceInfo = await calculateServiceLevelPrice(
              tableData.value[index].originalPrice!,
              item.serviceLevel
            )
            tableData.value[index].price = priceInfo.adjustedPrice
            tableData.value[index].serviceLevelCoefficient = priceInfo.coefficient
            tableData.value[index].matchedServiceLevel = priceInfo.matchedLevel
          }
        }
      } catch (error: any) {
        // 如果是主动取消的错误，不记录日志
        if (error.name === 'CanceledError' || error.code === 'ERR_CANCELED' || error.message?.includes('cancel')) {
          console.log('Matching was stopped by user')
          return
        }
        console.error('Match failed for item:', item.model, error)
        // 失败时也要设置默认值
        tableData.value[index].matchedModel = ''
        tableData.value[index].matchRate = 0
      } finally {
        // 每完成一条立即更新进度
        matchingCompleted.value++
        // 使用 shallowRef 时需要手动触发更新
        triggerRef(tableData)
      }
    }
  }

  const workers = Array(Math.min(concurrency, total)).fill(0).map(() => worker())
  await Promise.all(workers)
}

// Stop matching
function stopMatching() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  shouldStop.value = true
  matchingInProgress.value = false
  console.log('Matching stopped by user')
}

// Pricing params dropdown functions
function togglePricingParamsDropdown() {
  showPricingParamsDropdown.value = !showPricingParamsDropdown.value
}

function closePricingParamsDropdown() {
  showPricingParamsDropdown.value = false
}

function resetPricingParams() {
  pricingParams.value = {
    serviceMode: true,
    slaFactor: true,
    hardwareDepreciation: false,
    regionalAdjustment: false
  }
  console.log('Pricing params reset to default')
}

function applyPricingParams() {
  console.log('Applying pricing params:', pricingParams.value)
  // TODO: 实现应用逻辑
  closePricingParamsDropdown()
}

// Find maintenance rate by categories (same logic as backend)
function findMaintenanceRate(primary: string, secondary: string, tertiary: string): number {
  if (!maintenanceRatesCache.value) return 0.02  // default rate

  const rates = maintenanceRatesCache.value

  // Try tertiary category match first
  if (primary && secondary && tertiary) {
    const match = rates.find((r: any) =>
      r.primary_category === primary &&
      r.secondary_category === secondary &&
      r.tertiary_category === tertiary
    )
    if (match) return match.rate
  }

  // Try secondary category match
  if (primary && secondary) {
    const match = rates.find((r: any) =>
      r.primary_category === primary &&
      r.secondary_category === secondary &&
      !r.tertiary_category
    )
    if (match) return match.rate
  }

  // Try primary category match
  if (primary) {
    const match = rates.find((r: any) =>
      r.primary_category === primary &&
      !r.secondary_category &&
      !r.tertiary_category
    )
    if (match) return match.rate
  }

  return 0.02  // default rate
}

// Calculate service level price (uses cached service levels)
// 匹配规则：使用 serviceLevel 值（如 "7*24*2"）与后台"服务级别"管理中的 "响应时效" 字段进行模糊匹配
// 例如 "7*24*2" 应匹配到 "响应时效" 为 "7*24*2（2小时工程师和备件到达）" 的记录
// 如果匹配不到，使用 "7*24*NCR" 作为默认值
async function calculateServiceLevelPrice(basePrice: number, serviceLevel: string) {
  try {
    const levels = serviceLevelsCache.value || []
    const inputLevel = (serviceLevel || '7*24*NCR').trim()

    // 通过 response_time 字段进行模糊匹配
    // 查找 response_time 包含 inputLevel 的记录
    let matchedLevel = levels.find((l: any) => {
      const responseTime = (l.response_time || '').trim()
      return responseTime.includes(inputLevel)
    })

    // 如果没有匹配到，尝试使用默认值 "7*24*NCR"
    if (!matchedLevel && inputLevel !== '7*24*NCR') {
      matchedLevel = levels.find((l: any) => {
        const responseTime = (l.response_time || '').trim()
        return responseTime.includes('7*24*NCR')
      })
    }

    // 如果还是匹配不到，使用默认系数 1.0
    const coefficient = matchedLevel ? (Number(matchedLevel.coefficient) || 1) : 1.0
    const adjustedPrice = basePrice * coefficient

    return {
      adjustedPrice,
      coefficient,
      matchedLevel: matchedLevel || null
    }
  } catch (error) {
    console.error('Failed to calculate service level price:', error)
    return {
      adjustedPrice: basePrice,
      coefficient: 1.0,
      matchedLevel: null
    }
  }
}

// Parse service level (e.g., "7*24*3" -> { hours: 24, type: 'NCR' })
function parseServiceLevel(level: string) {
  const parts = level.split('*')
  if (parts.length >= 3) {
    return {
      hours: parseInt(parts[1]) || 24,
      type: parts[2]
    }
  }
  return { hours: 24, type: 'NCR' }
}

// 模糊匹配服务周期单位
function normalizeServicePeriodUnit(value: string): string {
  if (!value) return '年'
  const normalized = value.toString().trim()
  if (normalized.includes('年')) return '年'
  if (normalized.includes('月')) return '月'
  if (normalized.includes('天')) return '天'
  // 默认为年
  return '年'
}

// Open search dialog
function openSearch(index: number) {
  activeModelIndex.value = index
  showSearchDialog.value = true
  searchPage.value = 1
  // 重置搜索数据源为当前行的数据源
  searchDataSource.value = tableData.value[index].dataSource || 'datacenter'
  // Use original model for search (not the matched one)
  searchQuery.value = tableData.value[index].model || ''
  handleSearchInput()

  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

// Close search dialog
function closeSearchDialog() {
  showSearchDialog.value = false
  activeModelIndex.value = null
  searchQuery.value = ''
  searchResults.value = []
}

// Clear match result - 清空匹配结果，恢复到"未匹配"状态
function clearMatchResult(index: number) {
  const item = tableData.value[index]
  if (item) {
    // 重置匹配相关字段
    item.matchedModel = ''
    item.matchRate = 0
    item.matchedManufacturer = ''
    item.matchedSeries = ''
    item.originalPrice = 0
    item.price = 0
    item.serviceLevelCoefficient = 1
    item.deviceCategory = ''
    // 保留原始数据（厂商、型号等）
    console.log(`已清空第 ${index + 1} 行的匹配结果`)
    // 使用 shallowRef 时需要手动触发更新
    triggerRef(tableData)
  }
}

// Handle search input
function handleSearchInput() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(() => {
    performSearch()
  }, 300)
}

// Perform search
async function performSearch() {
  if (!searchQuery.value || searchQuery.value.length < 1) {
    searchResults.value = []
    totalResults.value = 0
    return
  }

  // Load maintenance rates if not already loaded (needed for price calculation)
  if (!maintenanceRatesCache.value) {
    try {
      const response = await axios.get(`${API_URL}/maintenance_rates/`)
      maintenanceRatesCache.value = response.data || []
    } catch (error) {
      console.error('Failed to load maintenance rates:', error)
      maintenanceRatesCache.value = []
    }
  }

  searchLoading.value = true

  try {
    const params = new URLSearchParams()
    params.append('model', searchQuery.value)
    // 使用搜索对话框中的数据源，而不是全局数据源
    params.append('source', searchDataSource.value)
    params.append('limit', pageSize.toString())
    params.append('offset', ((searchPage.value - 1) * pageSize).toString())

    const response = await axios.get(`${API_URL}/devices/search/?${params}`)
    searchResults.value = response.data.data || response.data || []
    totalResults.value = response.data.total || searchResults.value.length
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
    totalResults.value = 0
  } finally {
    searchLoading.value = false
  }
}

// Change search page
function changeSearchPage(page: number) {
  searchPage.value = page
  performSearch()
}

// 数据源改变时重新搜索
function onSearchDataSourceChange() {
  // 重置页码并重新搜索
  searchPage.value = 1
  if (searchQuery.value && searchQuery.value.length >= 1) {
    performSearch()
  }
}

// Select search result
async function selectSearchResult(result: any) {
  const index = activeModelIndex.value
  if (index === null || index < 0 || index >= tableData.value.length) return

  const selectedModel = result.model_number || result.model
  const devicePrice = result.device_price || 0

  // Find maintenance rate by categories (for manual price calculation)
  const rate = findMaintenanceRate(
    result.primary_category || '',
    result.secondary_category || '',
    result.tertiary_category || ''
  )

  // 原始单价 = 设备价格 × 费率（未含税）
  const originalPrice = devicePrice * rate
  const originalModel = tableData.value[index].model  // 原始型号（来自Excel"设备/软件型号"列）
  const originalManufacturer = tableData.value[index].originalManufacturer || ''  // 原始厂商（来自Excel"厂商"列，永不修改）

  console.log('手动匹配 - 原始值:', { originalManufacturer, originalModel })
  console.log('手动匹配 - 匹配值:', { manufacturer: result.manufacturer, model: result.model_number || result.model })

  // Find all rows with the same original model
  const matchedIndexes: number[] = []
  tableData.value.forEach((item, idx) => {
    if (item.model === originalModel) {
      matchedIndexes.push(idx)
    }
  })

  // Update all matched rows
  for (const idx of matchedIndexes) {
    // Calculate similarity for each row
    const similarity = calculateSimilarity(tableData.value[idx].model, selectedModel)

    tableData.value[idx].matchedModel = selectedModel
    tableData.value[idx].matchRate = similarity
    tableData.value[idx].originalPrice = originalPrice
    tableData.value[idx].deviceCategory = result.tertiary_category || result.device_category || ''
    tableData.value[idx].manufacturer = result.manufacturer || tableData.value[idx].manufacturer
    tableData.value[idx].device_price = devicePrice
    tableData.value[idx].primary_category = result.primary_category || ''
    tableData.value[idx].secondary_category = result.secondary_category || ''
    tableData.value[idx].tertiary_category = result.tertiary_category || ''
    tableData.value[idx].rate = rate
    tableData.value[idx].matchedManufacturer = result.manufacturer || ''
    tableData.value[idx].matchedSeries = result.device_series || ''
    tableData.value[idx].manuallyAdjusted = true  // 标记为手动调整

    // Recalculate service level price for each row
    if (originalPrice && tableData.value[idx].serviceLevel) {
      const priceInfo = await calculateServiceLevelPrice(originalPrice, tableData.value[idx].serviceLevel)
      tableData.value[idx].price = priceInfo.adjustedPrice
      tableData.value[idx].serviceLevelCoefficient = priceInfo.coefficient
      tableData.value[idx].matchedServiceLevel = priceInfo.matchedLevel
    }

    // 记录手动调整数据（传入原始厂商和型号，来自Excel）
    // 使用循环外捕获的原始值，确保所有行使用相同的原始厂商和型号
    saveManualAdjustment(
      originalManufacturer,  // 原始厂商（来自Excel"厂商"列）
      originalModel,  // 原始型号（来自Excel"设备/软件型号"列）
      result
    )
  }

  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
  closeSearchDialog()
}

// Save manual adjustment record
function saveManualAdjustment(
  originalManufacturer: string,  // 原始厂商（来自Excel"厂商"列）
  originalModel: string,  // 原始型号（来自Excel"设备/软件型号"列）
  searchResult: any  // 手动选择的匹配结果
) {
  // 检查是否已存在相同的原始厂商+型号组合
  const existingIndex = manualAdjustments.value.findIndex(
    item =>
      item.original_manufacturer === originalManufacturer &&
      item.original_model === originalModel
  )

  const adjustment = {
    original_manufacturer: originalManufacturer,  // 来自Excel"厂商"列
    original_model: originalModel,  // 来自Excel"设备/软件型号"列
    matched_manufacturer: searchResult.manufacturer || originalManufacturer,
    matched_model_number: searchResult.model_number || searchResult.model,
    device_price: searchResult.device_price || null,
    primary_category: searchResult.primary_category || '',
    secondary_category: searchResult.secondary_category || '',
    tertiary_category: searchResult.tertiary_category || '',
    device_category: searchResult.tertiary_category || searchResult.device_category || '',
    data_source: dataSource.value
  }

  if (existingIndex >= 0) {
    // 更新现有记录
    manualAdjustments.value[existingIndex] = adjustment
    console.log('更新手动调整记录:', adjustment)
  } else {
    // 添加新记录
    manualAdjustments.value.push(adjustment)
    console.log('添加手动调整记录:', adjustment)
    console.log('当前手动调整记录总数:', manualAdjustments.value.length)
  }
}

// Calculate similarity between two strings
function calculateSimilarity(str1: string, str2: string): number {
  if (!str1 || !str2) return 0
  const s1 = str1.toLowerCase().replace(/[^a-z0-9]/g, '')
  const s2 = str2.toLowerCase().replace(/[^a-z0-9]/g, '')
  if (s1 === s2) return 100

  const longer = s1.length > s2.length ? s1 : s2
  const shorter = s1.length > s2.length ? s2 : s1

  if (longer.length === 0) return 100

  const costs = []
  for (let i = 0; i <= longer.length; i++) {
    let lastValue = i
    for (let j = 0; j <= shorter.length; j++) {
      if (i === 0) {
        costs[j] = j
      } else if (j > 0) {
        let newValue = costs[j - 1]
        if (longer.charAt(i - 1) !== shorter.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1
        }
        costs[j - 1] = lastValue
        lastValue = newValue
      }
    }
    if (i > 0) costs[shorter.length] = lastValue
  }

  const editDistance = costs[shorter.length]
  return Math.max(0, Math.round((1 - editDistance / longer.length) * 100))
}

// Export data
async function exportData() {
  const exportDataItems = tableData.value.map(item => ({
    '厂商': item.manufacturer,
    '设备/软件型号': item.model,
    '设备/软件分类': item.deviceCategory,
    '服务级别': item.serviceLevel,
    '匹配型号': item.matchedModel || '未匹配',
    '置信度': item.matchRate ? `${Math.round(item.matchRate)}%` : '0%',
    '原始单价': item.originalPrice ? `¥${item.originalPrice.toFixed(2)}` : '-',
    '服务系数': item.serviceLevelCoefficient !== 1 ? item.serviceLevelCoefficient.toFixed(2) : '-',
    '调整后单价': item.price ? `¥${item.price.toFixed(2)}` : '-'
  }))

  // Use XLSX to export - 处理不同的模块导出格式
  const xlsxModule = await import('xlsx')
  const XLSX = xlsxModule.default || xlsxModule
  const ws = XLSX.utils.json_to_sheet(exportDataItems)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '匹配结果')
  XLSX.writeFile(wb, '智能匹配结果.xlsx')
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.smart-matching {
  font-family: "Noto Sans SC", sans-serif;
  background-color: #101622;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Header Styles */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #232f48;
  background-color: #101622;
  padding: 1rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  transition: opacity 0.2s;
}

.logo-link:hover {
  opacity: 0.8;
}

.logo-wrapper {
  width: 2rem;
  height: 2rem;
  color: #135bec;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(19, 91, 236, 0.1);
  border-radius: 0.5rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.015em;
}

.nav-links {
  display: none;
  flex: 1;
  justify-content: center;
  gap: 2.5rem;
}

@media (min-width: 768px) {
.nav-links {
  display: flex;
  }
}

.nav-link {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover, .nav-link.active {
  color: #135bec;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.icon-btn {
  position: relative;
  color: #94a3b8;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.icon-btn:hover {
  color: #135bec;
}

.notification-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 0.5rem;
  height: 0.5rem;
  background-color: #ef4444;
  border-radius: 9999px;
}

.divider {
  height: 2rem;
  width: 1px;
  background-color: #232f48;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuAZzVh9Czf4lzFyasoKua12Eo_RHM1ujGM5v8mh-HBKcsHP_5jyMC8gYZnu-fmr5pGhTTYYpRiCyUFw_FHBk319iL8wwenXkG9wr10t58CMhxMvy02eYEyj1RTmdLWGLoatidW47JrFehs1ny_2EWjNatPB9Rw9Jz4T2Ao8uZ1rGhJbe2QzgIrJquoWcwdHNdezINC3ZZMlE10NcF7DNlYd6pJXE-cdDrntOREOm4QAbqJSaw13F-IZfQm2vzzUvc-COJeeiC5_Xew");
  background-size: cover;
  background-position: center;
  ring: 2px solid #232f48;
}

.user-details {
  display: none;
  flex-direction: column;
}

@media (min-width: 1024px) {
  .user-details {
    display: flex;
  }
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1;
}

.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

/* Main Container */
.main-container {
  flex: 1;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (min-width: 768px) {
  .page-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.header-content {
  display: flex;
  flex-direction: column;
}

.header-right {
  display: flex;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #92a4c9;
}

.breadcrumb-link {
  color: inherit;
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.breadcrumb-link:hover {
  color: #135bec;
  text-decoration: underline;
}

.breadcrumb-current {
  color: white;
  font-weight: 500;
}

.breadcrumb .material-symbols-outlined {
  font-size: 1rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.025em;
  margin-top: 0.25rem;
}

.page-description {
  color: #92a4c9;
  font-size: 1rem;
  margin-top: 0.25rem;
}

/* Steps Progress */
.steps-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #1a2332;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid #232f48;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.step:hover {
  opacity: 0.8;
}

.step.active {
  color: #135bec;
  opacity: 1;
}

.step.completed {
  opacity: 0.5;
}

.step-number {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  background-color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
  color: white;
}

.step.active .step-number {
  background-color: #135bec;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.25);
}

.step.completed .step-number {
  background-color: #22c55e;
  color: white;
}

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
}

.step.active .step-label {
  font-weight: 700;
}

.step-label:hover {
  text-decoration: underline;
}

.step-divider {
  height: 1px;
  width: 1rem;
  background-color: #475569;
  flex-shrink: 0;
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem;
  background-color: #1a2332;
  border-radius: 0.75rem;
  border: 1px solid #232f48;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.empty-icon {
  font-size: 5rem;
  color: #475569;
  margin-bottom: 1.5rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 1rem;
  color: #92a4c9;
  margin-bottom: 2rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #135bec;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #1e40af;
}

/* Matching Progress */
.matching-progress {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.progress-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.progress-icon {
  font-size: 2rem;
  color: #135bec;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-info {
  flex: 1;
}

.progress-title {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.progress-status {
  font-size: 0.875rem;
  color: #92a4c9;
}

.progress-bar-wrapper {
  flex: 1;
  height: 0.5rem;
  background-color: #232f48;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #135bec, #3b82f6);
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.progress-percent {
  font-size: 1.125rem;
  font-weight: 700;
  color: #135bec;
  min-width: 3.5rem;
  text-align: right;
}

.stop-matching-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.stop-matching-btn:hover {
  background-color: #dc2626;
  transform: scale(1.02);
}

.stop-matching-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
}

.stat-card:hover {
  border-color: #324467;
}

.stat-bar {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 4px;
}

.stat-card.success .stat-bar {
  background-color: #22c55e;
}

.stat-card.warning .stat-bar {
  background-color: #eab308;
}

.stat-card.error .stat-bar {
  background-color: #ef4444;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-badge {
  background-color: rgba(234, 179, 8, 0.1);
  color: #eab308;
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-card.error .stat-badge {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-content {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
}

.stat-card.success .stat-value {
  color: #22c55e;
}

.stat-card.warning .stat-value {
  color: #eab308;
}

.stat-card.error .stat-value {
  color: #ef4444;
}

.stat-icon {
  color: #475569;
  font-size: 1.5rem;
}

.stat-card.success .stat-icon {
  color: rgba(34, 197, 94, 0.2);
}

.stat-card.warning .stat-icon {
  color: rgba(234, 179, 8, 0.2);
}

.stat-card.error .stat-icon {
  color: rgba(239, 68, 68, 0.2);
}

/* Table Container */
.table-container {
  display: flex;
  flex-direction: column;
  background-color: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

.table-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #2a3447;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(21, 26, 35, 0.5);
}

.table-controls-left,
.table-controls-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-select,
.data-source-select {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select .material-symbols-outlined,
.data-source-select .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.filter-select select,
.data-source-select select {
  padding: 0.5rem 2rem 0.5rem 2.5rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
  appearance: none;
}

.filter-select select:focus,
.data-source-select select:focus {
  border-color: #135bec;
}

/* Pricing Params Dropdown */
.pricing-params-dropdown {
  position: relative;
}

.pricing-params-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.pricing-params-btn:hover {
  border-color: #3b4d6a;
  background-color: #161d2d;
}

.pricing-params-btn.active {
  border-color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.pricing-params-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.pricing-params-btn .dropdown-arrow {
  font-size: 1rem;
  transition: transform 0.2s;
}

.pricing-params-btn.active .dropdown-arrow {
  transform: rotate(180deg);
}

.pricing-params-panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 320px;
  background-color: #1a2332;
  border: 1px solid #3b4d6a;
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 100;
  overflow: hidden;
}

.params-panel-header {
  padding: 1rem;
  border-bottom: 1px solid #2a3447;
  background-color: rgba(19, 91, 236, 0.05);
}

.params-panel-title {
  display: block;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #f1f5f9;
}

.params-panel-desc {
  display: block;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.params-list {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.param-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.param-item:hover {
  border-color: #3b4d6a;
  background-color: #161d2d;
}

.param-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.param-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(19, 91, 236, 0.15);
  border-radius: 0.375rem;
  color: #60a5fa;
  font-size: 1.125rem;
}

.param-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.param-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.param-desc {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Switch Toggle */
.param-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.param-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #374151;
  border-radius: 22px;
  transition: all 0.3s;
}

.switch-slider:before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: all 0.3s;
}

.param-switch input:checked + .switch-slider {
  background-color: #135bec;
}

.param-switch input:checked + .switch-slider:before {
  transform: translateX(18px);
}

.params-panel-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #2a3447;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  background-color: rgba(21, 26, 35, 0.5);
}

.params-reset-btn,
.params-apply-btn {
  padding: 0.5rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.params-reset-btn {
  background-color: transparent;
  color: #94a3b8;
  border: 1px solid #374151;
}

.params-reset-btn:hover {
  background-color: #374151;
  color: #e2e8f0;
}

.params-apply-btn {
  background-color: #135bec;
  color: white;
}

.params-apply-btn:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
  background: transparent;
  border: 1px solid #232f48;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: rgba(100, 116, 139, 0.1);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fca5a5;
  background: transparent;
  border: 1px solid #ef4444;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: #9ca3af;
  border-color: #4b5563;
}

.delete-count {
  font-size: 0.75rem;
  color: inherit;
}

/* Custom Circular Checkbox */
.custom-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.checkbox-circle {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  border: 2px solid #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: transparent;
}

.checkbox-circle:hover {
  border-color: #94a3b8;
}

.checkbox-circle.checked {
  border-color: #3b82f6;
  background: #3b82f6;
}

.checkbox-circle.indeterminate {
  border-color: #3b82f6;
  background: transparent;
}

.checkbox-circle .material-symbols-outlined {
  font-size: 0.875rem;
  color: #fff;
}

.checkbox-circle.indeterminate .material-symbols-outlined {
  color: #3b82f6;
}

/* Table Wrapper */
.table-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
  min-height: 400px;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.75rem;
}

.data-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #1e232f;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.data-table th {
  padding: 1rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #2a3447;
  white-space: nowrap;
}

.col-checkbox { width: 3rem; text-align: center; }
.col-index { width: 3.5rem; text-align: center; }
.col-manufacturer { width: 10rem; }
.col-model { width: 14rem; }
.col-category { width: 10rem; }
.col-service-level { width: 8rem; }
.col-match { width: 14rem; }
.col-confidence { width: 5rem; text-align: center; }
.col-price { width: 7rem; text-align: right; }
.col-coefficient { width: 7rem; text-align: center; }
.col-adjusted-price { width: 7rem; text-align: right; }
.col-actions { width: 6rem; text-align: center; }

.data-table tbody tr {
  transition: background-color 0.2s;
  border-bottom: 1px solid rgba(35, 47, 72, 0.5);
}

.data-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.data-table tbody tr.warning-row {
  background-color: rgba(234, 179, 8, 0.05);
  border-left: 3px solid #eab308;
}

.data-table tbody tr.error-row {
  background-color: rgba(239, 68, 68, 0.05);
  border-left: 3px solid #ef4444;
}

.data-table td {
  padding: 0.75rem 0.5rem;
}

.original-model {
  color: #cbd5e1;
}

.matched-model {
  cursor: pointer;
  font-weight: 500;
  transition: color 0.2s;
}

.matched-model.high-match {
  color: #22c55e;
}

.matched-model.mid-match {
  color: #eab308;
}

.matched-model.low-match {
  color: #f97316;
}

.matched-model.no-match {
  color: #94a3b8;
  font-style: italic;
}

.matched-model:hover {
  text-decoration: underline;
}

/* 匹配单元格包装器 */
.match-cell-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.clear-match-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  background-color: transparent;
  border: 1px solid #475569;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  opacity: 0.6;
}

.clear-match-btn:hover {
  background-color: rgba(239, 68, 68, 0.15);
  border-color: #ef4444;
  color: #ef4444;
  opacity: 1;
}

.clear-match-btn .material-symbols-outlined {
  font-size: 0.875rem;
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 3rem;
}

.confidence-badge.high {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.confidence-badge.mid {
  background-color: rgba(234, 179, 8, 0.1);
  color: #eab308;
  border: 1px solid rgba(234, 179, 8, 0.2);
}

.confidence-badge.low {
  background-color: rgba(249, 115, 22, 0.1);
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.2);
}

.confidence-badge.none {
  background-color: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.coefficient-value {
  color: #135bec;
  font-weight: 500;
}

.service-level-info {
  color: #92a4c9;
  font-size: 0.7rem;
}

.action-btn {
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #9ca3af;
  margin: 0 0.125rem;
}

.action-btn.edit:hover {
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.action-btn.confirm:hover {
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.1);
}

/* Table Footer */
.table-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #2a3447;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #1e232f;
}

.footer-text {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Bottom Bar */
.bottom-bar {
  position: sticky;
  bottom: 0;
  z-index: 50;
  background-color: #1a2332;
  border-top: 1px solid #232f48;
  padding: 1rem;
  box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
}

.bottom-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bottom-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.bottom-info .material-symbols-outlined {
  color: #eab308;
}

.bottom-info strong {
  color: white;
}

.bottom-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-draft {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  background-color: transparent;
  color: #92a4c9;
  font-weight: 600;
  font-size: 0.875rem;
  border: 1px solid #3e4c6b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-draft:hover:not(:disabled) {
  background-color: #2d3b59;
  color: white;
  border-color: #4e5c7b;
}

.btn-draft:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-draft .material-symbols-outlined {
  font-size: 1.125rem;
}

.btn-draft .material-symbols-outlined.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.btn-back,
.btn-next {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-back {
  border: 1px solid #232f48;
  background: transparent;
  color: white;
}

.btn-back:hover {
  background-color: rgba(100, 116, 139, 0.1);
}

.btn-next {
  background-color: #135bec;
  color: white;
  border: none;
  font-weight: 700;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.25);
}

.btn-next:hover {
  background-color: #1d6bf5;
}

/* Search Dialog */
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
  z-index: 100;
}

.dialog-content {
  background-color: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.75rem;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #2a3447;
}

.dialog-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
}

.dialog-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.dialog-close:hover {
  background-color: rgba(100, 116, 139, 0.1);
  color: white;
}

.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

/* 搜索对话框中的数据源选择器 */
.search-source-selector {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
}

.search-source-selector .source-label {
  display: block;
  color: #94a3b8;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.search-source-selector .source-options {
  display: flex;
  gap: 1.5rem;
}

.source-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  position: relative;
}

.source-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.source-radio {
  width: 16px;
  height: 16px;
  border: 2px solid #475569;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.source-option:hover .source-radio {
  border-color: #22c55e;
}

.source-option input[type="radio"]:checked ~ .source-radio {
  background-color: #22c55e;
  border-color: #22c55e;
}

.source-option input[type="radio"]:checked ~ .source-radio::after {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: white;
}

.source-option input[type="radio"]:focus ~ .source-name {
  color: #22c55e;
}

.source-name {
  color: #cbd5e1;
  font-size: 0.875rem;
  user-select: none;
}

.search-input-group {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.search-input-group .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.search-input-field {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  outline: none;
}

.search-input-field:focus {
  border-color: #135bec;
}

.search-results {
  margin-top: 1rem;
}

.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #94a3b8;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.results-header {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.result-item:hover {
  background-color: #232f48;
  border-color: #135bec;
}

.result-info {
  flex: 1;
}

.result-model {
  font-weight: 500;
  color: #135bec;
  margin-bottom: 0.25rem;
}

.result-details {
  font-size: 0.75rem;
  color: #94a3b8;
}

.result-price {
  font-size: 0.875rem;
  font-weight: 600;
  color: #22c55e;
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #94a3b8;
}

.no-results .material-symbols-outlined {
  font-size: 2rem;
}

.results-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.page-btn {
  background: transparent;
  border: 1px solid #232f48;
  color: #94a3b8;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #232f48;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.875rem;
  color: #94a3b8;
}

.dialog-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #2a3447;
  display: flex;
  justify-content: flex-end;
}

/* Background Effects */
.background-effects {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
  overflow: hidden;
}

.effect-blob {
  position: absolute;
  border-radius: 9999px;
  filter: blur(100px);
}

.effect-top {
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background-color: rgba(19, 91, 236, 0.05);
}

.effect-bottom {
  bottom: -10%;
  left: -5%;
  width: 600px;
  height: 600px;
  background-color: rgba(37, 99, 235, 0.05);
  filter: blur(120px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e232f;
}

::-webkit-scrollbar-thumb {
  background: #324467;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4b6189;
}

/* Responsive */
@media (max-width: 1024px) {
  .nav-links {
    display: none;
  }

  .table-container {
    overflow-x: auto;
  }
}
</style>
