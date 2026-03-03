<template>
  <div class="price-adjustment">
    <BranchPageHeader @open-product-database="openProductDatabaseModal" />

    <!-- Main Content -->
    <main class="main-content">
      <!-- Page Title & Breadcrumb -->
      <div class="page-top">
        <div class="page-info">
          <div class="breadcrumb">
            <a @click="navigateToHome" class="breadcrumb-link">首页</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <a @click="navigateToDocRecognition" class="breadcrumb-link">智能识别</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <a @click="navigateToSmartMatching" class="breadcrumb-link">智能匹配</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <span class="breadcrumb-current">价格调整</span>
          </div>
          <h1 class="page-title">价格调整</h1>
          <p class="page-description">审查AI建议价格，调整最终报价以优化利润空间。</p>
        </div>
        
        <!-- Steps Progress -->
        <div class="steps-progress">
          <div class="step completed">
            <div class="step-number">1</div>
            <span class="step-label" @click="navigateToDocRecognition" style="cursor: pointer;">导入数据</span>
          </div>
          <div class="step-divider"></div>
          <div class="step completed">
            <div class="step-number">
              <span class="material-symbols-outlined">check</span>
            </div>
            <span class="step-label" @click="navigateToSmartMatching" style="cursor: pointer;">智能匹配</span>
          </div>
          <div class="step-divider"></div>
          <div class="step active">
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

      <!-- Stats Cards -->
      <div class="stats-grid">
        <div class="stat-card">
          <span class="stat-label">参考成本平均价</span>
          <div class="stat-content">
            <span class="stat-value">¥{{ avgReferenceCost.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') }}</span>
            <span class="material-symbols-outlined stat-icon">payments</span>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-bar"></div>
          <span class="stat-label">平均利润率</span>
          <div class="stat-content">
            <div class="stat-value-group">
              <span class="stat-value">{{ avgProfitMargin.toFixed(1) }}%</span>
            </div>
            <span class="material-symbols-outlined stat-icon">query_stats</span>
          </div>
        </div>

        <div class="stat-card info">
          <span class="stat-label">总利润</span>
          <div class="stat-content">
            <span class="stat-value">¥{{ totalProfit.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') }}</span>
            <span class="material-symbols-outlined stat-icon">account_balance_wallet</span>
          </div>
        </div>

        <div class="stat-card error">
          <div class="stat-bar"></div>
          <div class="stat-header">
            <span class="stat-label">低利润预警 (<6%)</span>
            <span class="stat-badge">Attention</span>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ lowProfitCount }}</span>
            <span class="material-symbols-outlined stat-icon">warning</span>
          </div>
        </div>
      </div>

      <!-- Data Table -->
      <!-- Loading Overlay -->
      <div v-if="isLoadingData" class="loading-overlay" style="position: fixed; top: 0; left: 0; right: 0; bottom: 0; background: rgba(0, 0, 0, 0.5); display: flex; align-items: center; justify-content: center; z-index: 9999;">
        <div style="background: #1a1a1a; padding: 2rem; border-radius: 8px; text-align: center;">
          <span class="material-symbols-outlined spinning" style="font-size: 3rem; color: #3b82f6; display: block; margin-bottom: 1rem;">sync</span>
          <p style="color: #fff; font-size: 1.1rem; margin: 0;">正在加载数据，请稍候...</p>
        </div>
      </div>

      <div class="table-container">
        <div class="table-header">
          <div class="table-controls-left">
            <div class="filter-select">
              <span class="material-symbols-outlined">filter_list</span>
              <select>
                <option>全部商品</option>
                <option>已手动修改</option>
                <option>低利润商品</option>
                <option>高价值商品 (>1w)</option>
              </select>
            </div>
            <div class="search-input">
              <span class="material-symbols-outlined">search</span>
              <input type="text" placeholder="搜索型号或SKU..." />
            </div>
          </div>
          <div class="table-controls-right">
            <button class="btn-secondary" @click="resetAllPrices">
              <span class="material-symbols-outlined">restart_alt</span>
              重置价格
            </button>
            <div class="divider-vertical"></div>
            <button class="btn-primary" @click="openBatchAdjustDialog('up')">
              <span class="material-symbols-outlined">trending_up</span>
              批量上调
            </button>
            <button class="btn-secondary" @click="openBatchAdjustDialog('down')">
              <span class="material-symbols-outlined">trending_down</span>
              批量下调
            </button>
          </div>
        </div>

        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <input type="checkbox" v-model="allSelected" @change="toggleSelectAll" />
                </th>
                <th class="col-index">序号</th>
                <th class="col-model">产品型号</th>
                <th class="col-original-model">原始品牌型号</th>
                <th class="col-service-level">服务级别</th>
                <th class="col-city">城市</th>
                <th class="col-service-period-unit" @click="togglePeriodUnitDropdown">
  <span class="header-with-dropdown">服务周期单位</span>
  <span class="material-symbols-outlined dropdown-icon">arrow_drop_down</span>
  </th>
                <th class="col-cost">参考成本（未税）</th>
                <th class="col-suggested">建议售价</th>
                <th class="col-final">最终报价 (CNY)</th>
                <th class="col-profit">预估利润</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody v-if="tableData.length > 0">
              <tr
                v-for="(item, index) in tableData"
                :key="index"
                class="table-row"
                :class="{
                  'warning-row': item.profitMargin !== undefined && item.profitMargin < 10
                }"
              >
                <td><input type="checkbox" v-model="item.selected" /></td>
                <td class="col-index">{{ index + 1 }}</td>
                <td class="col-model">
                  <div class="product-info">
                    <div class="product-image"></div>
                    <div class="product-details">
                      <div class="product-name">{{ item.model || '-' }}</div>
                      <div class="product-sku" v-if="item.matchedModel">SKU: {{ formatManufacturer(item.matchedManufacturer || item.manufacturer) }}/{{ item.matchedSeries || '-' }}-{{ item.matchedModel }}</div>
                      <div class="product-sku no-match" v-else>未匹配</div>
                    </div>
                  </div>
                </td>
                <td class="col-original-model">
  {{ item.originalBrandModel || (item.originalManufacturer && item.model ? `${item.originalManufacturer}-${item.model}` : (item.manufacturer && item.model ? `${item.manufacturer}-${item.model}` : '-')) }}
</td>
                <td class="col-service-level">{{ item.serviceLevel || '-' }}</td>
                <td class="col-city">{{ item.city || '-' }}</td>
                <td class="col-service-period-unit">
                  <select
                    class="period-unit-select"
                    v-model="item.servicePeriodUnit"
                    @change="onPeriodUnitChange(index)"
                  >
                    <option value="年">年</option>
                    <option value="月">月</option>
                    <option value="天">天</option>
                  </select>
                </td>
                <td class="text-right">
                  <div class="price-value">{{ item.referenceCost !== undefined ? '¥' + item.referenceCost.toFixed(2) : '-' }}</div>
                </td>
                <td class="text-right">
                  <div class="price-value">{{ item.suggestedPrice ? '¥' + item.suggestedPrice.toFixed(2) : '-' }}</div>
                </td>
                <td class="text-right">
                  <div class="price-input-wrapper">
                    <span class="currency-symbol">¥</span>
                    <input
                      type="text"
                      class="price-input"
                      :value="item.finalPrice ? item.finalPrice.toFixed(2) : ''"
                      @input="updateFinalPrice(index, $event)"
                    />
                  </div>
                  <div
                    class="price-diff"
                    :class="{
                      'up': item.profitMargin > 0,
                      'down': item.profitMargin < 0,
                      'neutral': item.profitMargin === 0
                    }"
                    v-if="item.profitMargin !== undefined"
                  >
                    <span class="material-symbols-outlined" v-if="item.profitMargin > 0">arrow_upward</span>
                    <span class="material-symbols-outlined" v-else-if="item.profitMargin < 0">arrow_downward</span>
                    <span>{{ Math.abs(item.profitMargin).toFixed(1) }}%</span>
                  </div>
                </td>
                <td class="text-center">
                  <span
                    class="profit-badge"
                    :class="{
                      'positive': item.profitMargin !== undefined && item.profitMargin >= 0,
                      'negative': item.profitMargin !== undefined && item.profitMargin < 0
                    }"
                  >
                    {{ item.profitMargin !== undefined ? item.profitMargin.toFixed(1) + '%' : '-' }}
                  </span>
                </td>
                <td class="text-center">
                  <button class="action-btn" title="重置为建议价" @click="resetToSuggested(index)">
                    <span class="material-symbols-outlined">restart_alt</span>
                  </button>
                </td>
              </tr>
            </tbody>
            <tbody v-else>
              <tr>
                <td :colspan="12" class="empty-state">
                  <span class="material-symbols-outlined">inbox</span>
                  <p>暂无数据，请先完成智能匹配</p>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Period Unit Batch Update Dropdown -->
        <Teleport to="body">
          <div
            v-if="periodUnitDropdownVisible"
            class="period-unit-dropdown"
            :style="{ top: periodDropdownPosition.top, left: periodDropdownPosition.left }"
            @click.stop
          >
            <div class="dropdown-title">批量设置服务周期单位</div>
            <div class="dropdown-item" @click="batchUpdateServicePeriodUnit('年')">
              <span class="material-symbols-outlined">event_available</span>
              <span>年</span>
            </div>
            <div class="dropdown-item" @click="batchUpdateServicePeriodUnit('月')">
              <span class="material-symbols-outlined">calendar_month</span>
              <span>月</span>
            </div>
            <div class="dropdown-item" @click="batchUpdateServicePeriodUnit('天')">
              <span class="material-symbols-outlined">today</span>
              <span>天</span>
            </div>
          </div>
        </Teleport>

        <!-- Click outside to close dropdown -->
        <div
          v-if="periodUnitDropdownVisible"
          class="dropdown-overlay"
          @click="closePeriodUnitDropdown"
        ></div>

        <div class="table-footer">
          <span class="footer-text">显示 {{ tableData.length }} 条数据</span>
        </div>
      </div>
    </main>

    <!-- Sticky Bottom Bar -->
    <div class="bottom-bar">
      <div class="bottom-content">
        <div class="bottom-info">
          <div class="info-item">
            <span class="material-symbols-outlined">monetization_on</span>
            <span>预计总利润: <strong>¥{{ totalProfit.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',') }}</strong> ({{ avgProfitMargin.toFixed(1) }}%)</span>
          </div>
          <div class="divider-vertical"></div>
          <div class="info-item">
            <span class="material-symbols-outlined">format_list_numbered</span>
            <span>共 <strong>{{ tableData.length }}</strong> 项数据</span>
          </div>
        </div>
        <div class="bottom-actions">
          <button class="btn-back" @click="navigateBack">上一步</button>
          <div class="action-buttons">
            <button class="btn-draft" @click="saveAsDraft" :disabled="isSavingDraft" :title="'快捷键: Ctrl+S'">
              <span class="material-symbols-outlined" v-if="!isSavingDraft">save</span>
              <span class="material-symbols-outlined spinning" v-else>sync</span>
              {{ isSavingDraft ? '保存中...' : '存为草稿' }}
            </button>
          <button class="btn-next" @click="goToQuotationGeneration">
            生成报价单
            <span class="material-symbols-outlined">assignment_turned_in</span>
          </button>
        </div>
      </div>
    </div>
    </div>

    <!-- 批量调价弹窗 -->
    <Teleport to="body">
      <div v-if="batchAdjustDialogVisible" class="batch-adjust-overlay" @click.self="closeBatchAdjustDialog">
        <div class="batch-adjust-dialog" @click.stop>
          <div class="batch-adjust-header">
            <h3 class="batch-adjust-title">
              <span class="material-symbols-outlined" :class="batchAdjustDirection === 'up' ? 'icon-up' : 'icon-down'">
                {{ batchAdjustDirection === 'up' ? 'trending_up' : 'trending_down' }}
              </span>
              {{ batchAdjustDirection === 'up' ? '批量上调价格' : '批量下调价格' }}
            </h3>
            <button class="batch-adjust-close" @click="closeBatchAdjustDialog">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="batch-adjust-body">
            <p class="batch-adjust-hint">
              已选中 <strong>{{ selectedCount }}</strong> 条数据，将对其"最终报价"按百分比{{ batchAdjustDirection === 'up' ? '上调' : '下调' }}。
            </p>
            <div class="batch-adjust-input-group">
              <label class="batch-adjust-label">调整比例 (%)</label>
              <div class="batch-adjust-input-wrapper">
                <input
                  ref="batchPercentInputRef"
                  type="number"
                  class="batch-adjust-input"
                  v-model.number="batchAdjustPercent"
                  placeholder="例如: 10"
                  min="0"
                  max="999"
                  step="0.1"
                  @keyup.enter="confirmBatchAdjust"
                />
                <span class="batch-adjust-suffix">%</span>
              </div>
              <p class="batch-adjust-example" v-if="batchAdjustPercent > 0">
                示例：¥1000.00 → ¥{{ batchAdjustDirection === 'up'
                  ? (1000 * (1 + batchAdjustPercent / 100)).toFixed(2)
                  : (1000 * (1 - batchAdjustPercent / 100)).toFixed(2) }}
              </p>
            </div>
          </div>
          <div class="batch-adjust-footer">
            <button class="batch-adjust-btn cancel" @click="closeBatchAdjustDialog">取消</button>
            <button
              class="batch-adjust-btn confirm"
              :class="batchAdjustDirection === 'up' ? 'btn-up' : 'btn-down'"
              :disabled="!batchAdjustPercent || batchAdjustPercent <= 0"
              @click="confirmBatchAdjust"
            >
              确认{{ batchAdjustDirection === 'up' ? '上调' : '下调' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 产品数据库弹窗 -->
    <ProductDatabaseModal :is-open="isProductDatabaseModalOpen" @close="closeProductDatabaseModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed, watch, shallowRef, triggerRef, nextTick } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessage } from 'element-plus'
import BranchPageHeader from '../components/BranchPageHeader.vue'
import ProductDatabaseModal from '../components/ProductDatabaseModal.vue'
import {
  PAGE_STATE_KEYS,
  FLOW_DATA_KEYS,
  savePageState,
  restorePageState,
  saveFlowData,
  getFlowData,
  clearPageState,
  clearFlowData,
  getNavigationMode,
  clearNavigationMode,
  setNavigationMode,
  cleanupOldFlowData,
  type PriceAdjustmentState
} from '../stores/quotationStore'
import {
  saveDraft,
  getCurrentDraftId
} from '../utils/draftUtils'

const router = useRouter()

// State
// 使用 shallowRef 优化大数据量性能，只追踪数组引用变化而不追踪内部对象
const tableData = shallowRef<any[]>([])
const allSelected = ref(false)
const isSavingDraft = ref(false)
const isLoadingData = ref(false)
const periodUnitDropdownVisible = ref(false)
const periodDropdownPosition = ref({ top: '0px', left: '0px' })

// 批量调价弹窗
const batchAdjustDialogVisible = ref(false)
const batchAdjustDirection = ref<'up' | 'down'>('up')
const batchAdjustPercent = ref<number>(0)
const batchPercentInputRef = ref<HTMLInputElement | null>(null)

// 已选条目数
const selectedCount = computed(() => {
  return tableData.value.filter(item => item.selected).length
})

// 打开批量调价弹窗
function openBatchAdjustDialog(direction: 'up' | 'down') {
  const count = tableData.value.filter(item => item.selected).length
  if (count === 0) {
    ElMessage.warning('请先勾选需要调整的数据条目')
    return
  }
  batchAdjustDirection.value = direction
  batchAdjustPercent.value = 0
  batchAdjustDialogVisible.value = true
  // 弹窗打开后自动聚焦输入框
  nextTick(() => {
    batchPercentInputRef.value?.focus()
  })
}

// 关闭批量调价弹窗
function closeBatchAdjustDialog() {
  batchAdjustDialogVisible.value = false
  batchAdjustPercent.value = 0
}

// 确认批量调价
function confirmBatchAdjust() {
  const percent = batchAdjustPercent.value
  if (!percent || percent <= 0) {
    ElMessage.warning('请输入有效的调整比例')
    return
  }

  const direction = batchAdjustDirection.value
  let adjustedCount = 0

  tableData.value.forEach(item => {
    if (!item.selected) return
    const currentPrice = item.finalPrice || item.suggestedPrice || 0
    if (currentPrice <= 0) return

    if (direction === 'up') {
      item.finalPrice = Math.round(currentPrice * (1 + percent / 100) * 100) / 100
    } else {
      item.finalPrice = Math.round(currentPrice * (1 - percent / 100) * 100) / 100
      if (item.finalPrice < 0) item.finalPrice = 0
    }

    // 重新计算利润率
    if (item.suggestedPrice && item.suggestedPrice > 0) {
      item.profitMargin = ((item.finalPrice - item.suggestedPrice) / item.suggestedPrice) * 100
    } else {
      item.profitMargin = 0
    }
    adjustedCount++
  })

  triggerRef(tableData)
  closeBatchAdjustDialog()
  ElMessage.success(`已${direction === 'up' ? '上调' : '下调'} ${adjustedCount} 条数据的最终报价 ${percent}%`)
}

// 产品数据库弹窗
const isProductDatabaseModalOpen = ref(false)

const openProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = true
}

const closeProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = false
}

// Computed: Stats
// 参考成本平均价：计算"参考成本（未税）"列的平均值
const avgReferenceCost = computed(() => {
  if (tableData.value.length === 0) return 0
  const total = tableData.value.reduce((sum, item) => {
    return sum + (item.referenceCost || 0)
  }, 0)
  return total / tableData.value.length
})

// 平均利润率：计算"预估利润"列的平均值
const avgProfitMargin = computed(() => {
  const validMargins = tableData.value
    .map(item => item.profitMargin)
    .filter(m => m !== undefined && m !== null)
  if (validMargins.length === 0) return 0
  const sum = validMargins.reduce((a, b) => a + b, 0)
  return sum / validMargins.length
})

// 总利润：计算"最终报价 (CNY)" - "参考成本（未税）"的总和
const totalProfit = computed(() => {
  return tableData.value.reduce((sum, item) => {
    const finalPrice = item.finalPrice || 0
    const referenceCost = item.referenceCost || 0
    return sum + (finalPrice - referenceCost)
  }, 0)
})

// 低利润预警 (<6%)：统计"预估利润"列中小于6%的数据数量
const lowProfitCount = computed(() => {
  return tableData.value.filter(item =>
    item.profitMargin !== undefined && item.profitMargin < 6
  ).length
})

// Get current state for saving
function getCurrentState(): PriceAdjustmentState {
  return {
    tableData: tableData.value,
    hasData: tableData.value.length > 0
  }
}

// Automatically save state when leaving this page (for breadcrumb navigation restore)
onBeforeRouteLeave((to, from, next) => {
  // 离开页面时始终保存状态，以便面包屑导航返回时可以恢复
  if (tableData.value.length > 0) {
    const currentState = getCurrentState()

    // 尝试保存页面状态（用于面包屑返回时恢复）
    try {
      savePageState(PAGE_STATE_KEYS.PRICE_ADJUSTMENT, currentState)
      console.log('PriceAdjustment state saved:', currentState.tableData.length, 'items')
    } catch (error) {
      console.error('Failed to save PriceAdjustment state:', error)
    }

    // 同时保存流程数据（供下一步使用）
    try {
    saveFlowData(FLOW_DATA_KEYS.ADJUSTED_DATA, tableData.value)
      console.log('PriceAdjustment flow data saved:', tableData.value.length, 'items')
    } catch (error) {
      console.error('Failed to save PriceAdjustment flow data:', error)
      // 如果保存失败，可能是 sessionStorage 容量不足
      // 尝试清理旧数据后重试
      try {
        // 清除 CONVERTED_DATA（已经不需要）
        clearFlowData(FLOW_DATA_KEYS.CONVERTED_DATA)
        saveFlowData(FLOW_DATA_KEYS.ADJUSTED_DATA, tableData.value)
        console.log('PriceAdjustment flow data saved after cleanup:', tableData.value.length, 'items')
      } catch (retryError) {
        console.error('Failed to save flow data even after cleanup:', retryError)
      }
    }
  }
  next()
})

// 面包屑导航：跳转到页面（不保存状态，由目标页面恢复自己的状态）
const navigateToHome = () => {
  router.push('/')
}

const navigateToDocRecognition = () => {
  router.push('/document-recognition')
}

const navigateToSmartMatching = () => {
  router.push('/smart-matching')
}

const navigateToPriceAdjustment = () => {
  // 当前页面，无需跳转
}

const navigateBack = () => {
  router.push('/smart-matching')
}

const navigateToQuotationGeneration = () => {
  // 面包屑跳转：直接跳转
  router.push('/quotation-generation')
}

// 流程推进：保存当前状态并进入下一步（由"下一步"按钮调用）
const goToQuotationGeneration = () => {
  // 先清理旧数据以释放 sessionStorage 空间
  cleanupOldFlowData('adjust')

  // 设置导航模式为 'flow'，告诉下一页面这是流程推进
  setNavigationMode('flow')

  // 尝试保存当前页面状态
  try {
  savePageState(PAGE_STATE_KEYS.PRICE_ADJUSTMENT, getCurrentState())
  } catch (error) {
    console.error('Failed to save page state, trying flow data only:', error)
  }

  // 尝试保存流程数据供下一页面使用
  try {
  saveFlowData(FLOW_DATA_KEYS.ADJUSTED_DATA, tableData.value)
    console.log('PriceAdjustment flow data saved successfully')
  } catch (error) {
    console.error('Failed to save flow data:', error)
    alert('数据量较大，部分数据可能无法在页面间传递。建议减少数据量或分批处理。')
  }

  router.push('/quotation-generation')
}

// 存为草稿
async function saveAsDraft() {
  if (tableData.value.length === 0) {
    ElMessage.warning('请先完成价格调整后再保存草稿')
    return
  }

  isSavingDraft.value = true
  try {
    // 保存当前状态
    savePageState(PAGE_STATE_KEYS.PRICE_ADJUSTMENT, getCurrentState())
    saveFlowData(FLOW_DATA_KEYS.ADJUSTED_DATA, tableData.value)

    // 获取当前草稿ID（如果有）
    const existingDraftId = getCurrentDraftId()

    // 保存草稿
    await saveDraft('price_adjustment', existingDraftId ?? undefined)

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

// Toggle select all
function toggleSelectAll() {
  tableData.value.forEach(item => {
    item.selected = allSelected.value
  })
  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
}

// Update final price
function updateFinalPrice(index: number, event: Event) {
  const input = event.target as HTMLInputElement
  const value = parseFloat(input.value.replace(/[^0-9.]/g, ''))

  const item = tableData.value[index]
  if (!isNaN(value)) {
    item.finalPrice = value
    // 重新计算价格调整比率（相较于建议售价的上调/下调比率）
    if (item.suggestedPrice && item.suggestedPrice > 0) {
      item.profitMargin = ((item.finalPrice - item.suggestedPrice) / item.suggestedPrice) * 100
    } else {
      item.profitMargin = 0
    }
  } else {
    item.finalPrice = null
    item.profitMargin = undefined
  }
  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
}

// Reset to suggested price
function resetToSuggested(index: number) {
  const item = tableData.value[index]
  item.finalPrice = item.suggestedPrice
  // 重置为建议售价时，比率为 0%
  item.profitMargin = 0
  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
}

// Reset all prices to suggested prices
function resetAllPrices() {
  tableData.value.forEach(item => {
    item.finalPrice = item.suggestedPrice
    item.profitMargin = 0
  })
  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
}

// Toggle period unit dropdown
function togglePeriodUnitDropdown(event: MouseEvent) {
  const target = event.target as HTMLElement
  const th = target.closest('th') as HTMLElement
  if (th) {
    const rect = th.getBoundingClientRect()
    periodDropdownPosition.value = {
      top: rect.bottom + 4 + 'px',
      left: rect.left + 'px'
    }
  }
  periodUnitDropdownVisible.value = !periodUnitDropdownVisible.value
}

// Close period unit dropdown
function closePeriodUnitDropdown() {
  periodUnitDropdownVisible.value = false
}

// Batch update all service period units
function batchUpdateServicePeriodUnit(unit: string) {
  tableData.value.forEach(item => {
    item.servicePeriodUnit = unit
    const basePrice = item.basePrice || item.price || 0
    let referenceCost = basePrice

    if (unit === '月') {
      referenceCost = basePrice / 12
    } else if (unit === '天') {
      referenceCost = basePrice / 365
    }

    item.referenceCost = referenceCost
    item.suggestedPrice = item.referenceCost
    item.finalPrice = item.suggestedPrice
    item.profitMargin = 0
  })
  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
  closePeriodUnitDropdown()
}

// Handle service period unit change
function onPeriodUnitChange(index: number) {
  // 服务周期单位改变时，重新计算该行的参考成本和建议售价
  const item = tableData.value[index]
  const basePrice = item.basePrice || item.price || 0
  let referenceCost = basePrice

  if (item.servicePeriodUnit === '月') {
    referenceCost = basePrice / 12
  } else if (item.servicePeriodUnit === '天') {
    referenceCost = basePrice / 365
  }

  // 更新参考成本
  item.referenceCost = referenceCost

  // 更新建议售价
  item.suggestedPrice = item.referenceCost

  // 重置最终报价为新的建议售价
  item.finalPrice = item.suggestedPrice

  // 重置比率为 0%
  item.profitMargin = 0
  // 使用 shallowRef 时需要手动触发更新
  triggerRef(tableData)
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

// 格式化厂商字段：去掉 "/NetApp" 这种重复部分
function formatManufacturer(manufacturer: string | undefined): string {
  if (!manufacturer) return ''
  // 如果厂商字段包含 "/"，只取 "/" 前面的部分
  if (manufacturer.includes('/')) {
    return manufacturer.split('/')[0]
  }
  return manufacturer
}

// Calculate all data prices (优化：分批处理大数据量)
function calculatePrices() {
  const items = tableData.value
  const batchSize = 500 // 每批处理 500 条数据
  let currentIndex = 0

  function processBatch() {
    const endIndex = Math.min(currentIndex + batchSize, items.length)
    
    for (let i = currentIndex; i < endIndex; i++) {
      const item = items[i]
    // 参考成本（未税）根据服务周期单位计算：
    // - "年": 不做调整，使用原始价格
    // - "月": 原始价格 / 12
    // - "天": 原始价格 / 365
    const basePrice = item.basePrice || item.price || 0
    let referenceCost = basePrice

    if (item.servicePeriodUnit === '月') {
      referenceCost = basePrice / 12
    } else if (item.servicePeriodUnit === '天') {
      referenceCost = basePrice / 365
    }

    // 参考成本（未税）= 根据服务周期单位计算后的价格
    item.referenceCost = referenceCost

    // 建议售价 = 参考成本（默认相等，不可手动调整）
    item.suggestedPrice = item.referenceCost

    // 最终报价 = 建议售价（默认相等，支持手动调整）
    if (item.finalPrice === null || item.finalPrice === undefined) {
      item.finalPrice = item.suggestedPrice
    }

    // 价格调整比率：显示"最终报价"相较于"建议售价"的上调/下调比率
    if (item.finalPrice !== null && item.finalPrice !== undefined && item.suggestedPrice && item.suggestedPrice > 0) {
      item.profitMargin = ((item.finalPrice - item.suggestedPrice) / item.suggestedPrice) * 100
    } else {
      item.profitMargin = undefined
    }
    }

    currentIndex = endIndex
    // 使用 shallowRef 时需要手动触发更新
    triggerRef(tableData)

    // 如果还有数据未处理，继续处理下一批
    if (currentIndex < items.length) {
      // 使用 requestIdleCallback 或 setTimeout 避免阻塞 UI
      if (typeof requestIdleCallback !== 'undefined') {
        requestIdleCallback(processBatch, { timeout: 100 })
      } else {
        setTimeout(processBatch, 0)
      }
    }
  }

  // 开始处理第一批
  if (items.length > 0) {
    processBatch()
  }
}

// Load data on mount (优化：分批处理大数据量)
onMounted(async () => {
  isLoadingData.value = true
  ElMessage.info('正在加载数据，请稍候...')

  try {
  // 获取导航模式
  const navigationMode = getNavigationMode()
  console.log('PriceAdjustment navigation mode:', navigationMode)

  if (navigationMode === 'flow') {
    // 流程推进模式：重新加载流程数据（来自智能匹配的最新数据）
    const flowData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
    if (flowData && flowData.length > 0) {
      console.log('Loading fresh flow data from SmartMatching:', flowData.length, 'items')
        
        // 使用分批处理来转换数据，避免阻塞 UI
        const batchSize = 1000 // 每批处理 1000 条
        const totalBatches = Math.ceil(flowData.length / batchSize)
        const processedData: any[] = []

        // 分批处理数据转换
        for (let i = 0; i < totalBatches; i++) {
          const start = i * batchSize
          const end = Math.min(start + batchSize, flowData.length)
          const batch = flowData.slice(start, end)
          
          const batchProcessed = batch.map(item => ({
        ...item,
        selected: false,
        basePrice: item.price || 0,  // 保存原始价格，用于根据服务周期单位计算参考成本
        suggestedPrice: null,
        finalPrice: null,  // 初始化为 null，让 calculatePrices() 根据 servicePeriodUnit 计算正确的值
        profitMargin: undefined,
        // 使用模糊匹配处理服务周期单位（如果值为空则默认为"年"）
        servicePeriodUnit: normalizeServicePeriodUnit(item.servicePeriodUnit)
      }))
          
          processedData.push(...batchProcessed)
          
          // 每处理一批后，更新 tableData 并让出控制权，避免阻塞 UI
          tableData.value = [...processedData]
          triggerRef(tableData)
          
          // 使用 setTimeout 让出控制权，允许 UI 更新
          if (i < totalBatches - 1) {
            await new Promise(resolve => setTimeout(resolve, 0))
          }
        }

        // 所有数据转换完成后，计算价格
      calculatePrices()
        
      // 清除旧的页面状态，确保下次加载时使用最新数据
      clearPageState(PAGE_STATE_KEYS.PRICE_ADJUSTMENT)
        
        ElMessage.success(`成功加载 ${flowData.length} 条数据`)
      } else {
        ElMessage.warning('未找到匹配数据，请返回上一步重新匹配')
    }
    // 清除导航模式标志
    clearNavigationMode()
  } else {
    // 面包屑跳转模式：优先恢复页面状态（保持最后一次修改的数据）
    const savedState = restorePageState<PriceAdjustmentState>(PAGE_STATE_KEYS.PRICE_ADJUSTMENT)
    if (savedState && savedState.hasData && savedState.tableData && savedState.tableData.length > 0) {
      console.log('Restoring saved page state:', savedState.tableData.length, 'items')
      tableData.value = savedState.tableData
        ElMessage.success(`已恢复 ${savedState.tableData.length} 条数据`)
    } else {
      // 如果没有保存的状态，尝试从流程数据加载
      const flowData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
      if (flowData && flowData.length > 0) {
        console.log('No saved state, loading flow data:', flowData.length, 'items')
          
          // 分批处理
          const batchSize = 1000
          const totalBatches = Math.ceil(flowData.length / batchSize)
          const processedData: any[] = []

          for (let i = 0; i < totalBatches; i++) {
            const start = i * batchSize
            const end = Math.min(start + batchSize, flowData.length)
            const batch = flowData.slice(start, end)
            
            const batchProcessed = batch.map(item => ({
          ...item,
          selected: false,
              basePrice: item.price || 0,
          suggestedPrice: null,
              finalPrice: null,
          profitMargin: undefined,
          servicePeriodUnit: normalizeServicePeriodUnit(item.servicePeriodUnit)
        }))
            
            processedData.push(...batchProcessed)
            tableData.value = [...processedData]
            triggerRef(tableData)
            
            if (i < totalBatches - 1) {
              await new Promise(resolve => setTimeout(resolve, 0))
            }
          }
          
        calculatePrices()
          ElMessage.success(`成功加载 ${flowData.length} 条数据`)
      }
    }
  }
  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败，请重试')
  } finally {
    isLoadingData.value = false
  }

  // 添加键盘快捷键监听
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // 移除键盘快捷键监听
  window.removeEventListener('keydown', handleKeyDown)
})

// 监听 tableData 变化，实时保存状态（用于面包屑跳转恢复）
watch(tableData, (newData) => {
  if (newData && newData.length > 0) {
    savePageState(PAGE_STATE_KEYS.PRICE_ADJUSTMENT, {
      tableData: newData,
      hasData: true
    })
  }
}, { deep: true })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.price-adjustment {
  font-family: "Noto Sans SC", sans-serif;
  background-color: #101622;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  overflow-x: hidden;
}

h1, h2, h3, h4, h5, h6 {
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
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

.divider-vertical {
  width: 1px;
  height: 1.5rem;
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

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 3rem;
  padding-bottom: 5rem;
  max-width: 1600px;
  margin: 0 auto;
  width: 100%;
}

/* Page Top */
.page-top {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

@media (min-width: 768px) {
  .page-top {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.page-info {
  display: flex;
  flex-direction: column;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
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
  font-size: 1.875rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: white;
}

.page-description {
  color: #94a3b8;
  font-size: 0.875rem;
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

.step.completed .step-number .material-symbols-outlined {
  font-size: 0.875rem;
}

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
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
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
  margin-bottom: 2rem;
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

.stat-card.info {
  /* No bar for info cards */
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
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-content {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.stat-value-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  color: white;
}

.stat-card.success .stat-value {
  color: #22c55e;
}

.stat-card.info .stat-value {
  color: #3b82f6;
}

.stat-card.error .stat-value {
  color: #ef4444;
}

.stat-trend {
  font-size: 0.75rem;
  color: #22c55e;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-trend .material-symbols-outlined {
  font-size: 0.875rem;
}

.stat-icon {
  color: #475569;
  font-size: 1.875rem;
}

.stat-card.success .stat-icon {
  color: rgba(34, 197, 94, 0.2);
}

.stat-card.info .stat-icon {
  color: rgba(59, 130, 246, 0.2);
}

.stat-card.error .stat-icon {
  color: rgba(239, 68, 68, 0.2);
}

/* Table Container */
.table-container {
  display: flex;
  flex-direction: column;
  flex: 1;
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.table-header {
  padding: 1rem;
  border-bottom: 1px solid #232f48;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(21, 28, 43, 0.5);
}

.table-controls-left,
.table-controls-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-select,
.search-input {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select .material-symbols-outlined,
.search-input .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.filter-select select {
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

.filter-select select:focus {
  ring: 2px solid #135bec;
  border-color: transparent;
}

.search-input input {
  width: 16rem;
  padding: 0.5rem 1rem 0.5rem 2.5rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  outline: none;
}

.search-input input::placeholder {
  color: #94a3b8;
}

.search-input input:focus {
  ring: 2px solid #135bec;
  border-color: transparent;
}

.btn-secondary,
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.btn-secondary {
  color: #cbd5e1;
  background: transparent;
  border: 1px solid #232f48;
}

.btn-secondary:hover {
  background-color: rgba(100, 116, 139, 0.1);
}

.btn-primary {
  background-color: #135bec;
  color: white;
  border: 1px solid rgba(19, 91, 236, 0.3);
  font-weight: 500;
}

.btn-primary:hover {
  background-color: #1d6bf5;
}

.btn-secondary .material-symbols-outlined,
.btn-primary .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Table Wrapper */
.table-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.data-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: rgba(28, 38, 56, 1);
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.data-table th {
  padding: 1rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #232f48;
}

.col-checkbox {
  width: 2.5rem;
}

.col-index {
  width: 3rem;
}

.col-model {
  width: 18%;
}

.col-original-model {
  width: 12%;
}

.col-service-level {
  width: 8%;
}

.col-city {
  width: 6%;
}

.col-service-period-unit {
  width: 8%;
  cursor: pointer;
  position: relative;
  user-select: none;
  transition: color 0.2s;
}

.col-service-period-unit:hover {
  color: #135bec;
}

.header-with-dropdown {
  display: inline-block;
}

.dropdown-icon {
  font-size: 1rem;
  margin-left: 0.25rem;
  vertical-align: middle;
  opacity: 0.7;
  transition: transform 0.2s, opacity 0.2s;
}

.col-service-period-unit:hover .dropdown-icon {
  opacity: 1;
}

/* Period Unit Dropdown */
.period-unit-dropdown {
  position: fixed;
  z-index: 1000;
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  min-width: 140px;
  overflow: hidden;
  animation: dropdown-fade-in 0.15s ease-out;
}

@keyframes dropdown-fade-in {
  from {
    opacity: 0;
    transform: translateY(-8px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-title {
  padding: 0.625rem 0.75rem 0.5rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
  border-bottom: 1px solid #232f48;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  cursor: pointer;
  transition: background-color 0.15s;
  color: #cbd5e1;
  font-size: 0.875rem;
}

.dropdown-item:hover {
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
}

.dropdown-item .material-symbols-outlined {
  font-size: 1.125rem;
}

.dropdown-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 999;
  background: transparent;
}

.col-cost,
.col-suggested {
  width: 10%;
  text-align: right;
}

.col-final {
  width: 12%;
  text-align: right;
}

.col-profit {
  width: 8%;
  text-align: center;
}

.col-actions {
  width: 5%;
  text-align: center;
}

.data-table tbody {
  font-size: 0.875rem;
}

.table-row {
  transition: background-color 0.2s;
  border-bottom: 1px solid rgba(35, 47, 72, 0.5);
}

.table-row:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.table-row.warning-row {
  background-color: rgba(239, 68, 68, 0.05);
}

.table-row td {
  padding: 1rem;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.product-image {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.25rem;
  background-color: #475569;
  flex-shrink: 0;
  background-size: cover;
  background-position: center;
  border: 1px solid #232f48;
  background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuC8bNw8VJItp06hBiecpbq1CYdnpg9R4q3wNGExLtJB12zFGseTVIh55z6R5zDKC7prPhUPYhwetnzi9vbx9T3QGmAJh6O2l05nT-lONOoqsrcl3Ol6TYUgydideuguVTSK7eNinFi9dCbWI9LJ_MsnZVjMzivAP5Mdl37gilACF2rzd-ggEsFPYiT9VT6BMuQpCESt1N3Jsx6KdYdbrlXFkA6Xj9luWDiGVie-kZzJ5srr3l8-CY7lvA5EMjVNMflibVLxvglDkUA');
}

.product-image.samsung {
  background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuAIeKKDfx84DBSxhWngyV3MazzWz3EBz17Ihi4MlJu2qiKIZaFYhc77Ki89vuk35axwlKCIjejWSaCkic7noYwbiKp6S_k1g6x1HiqgFwh6AuP90s9mqdTNvtdkTeiE6BYBmcndQgVug-vXm49QAR6gXoGBCvUMNWyJNx7xeND8HUzA_gyhOO7ctmCRXw8kjylwH4tA1MhZrI0Vqv6xzbpMABPQx8H_PprTYEPhDwLkMLa4hUNkRGZIPi-Du8cPuXWhfe15rZmrxkU');
}

.product-image.dell {
  background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuDYW-CRktrjGrEm4rbhQiUFCaKaWiiz-JiyVBzViwQjHIFm7Rlex7mN7hRMqRBKeCo7gY1xc9NEG9my6KDh_VJzXoZSkw9AakZNFzqBU8GUHkKFyRGXPodNdbe-dahsIqy9Rvsm20-mYP36RHYLoGs2XTeAyZg2Dv9XDJRGMDWyQHes0opIm82KTT0Xwj2RHYR78e2rYRoVzfpBS3bgPeDFpkh4HwEoxreMZQ5JdnsNAH1Y01P6oYUqZxNABjQ82_DkJS-RGyTwVC4');
}

.product-image.logitech {
  background-image: url('https://lh3.googleusercontent.com/aida-public/AB6AXuAbwE4AjfnCcCebLJpEL1IheLKZz_4RCqHgjiJyy7fV6dUa4A-ysxJGtmYAKN5aOmVRSxuW8rdE5riMMIoCt_sUMnTQT1gy9fod4oVixLJwiExwHIYzufx__XYb8NidjEn2EP8csFaUtnFxwjEczriT1GDOv-PA_rPBITIcSqCioiq0mUusLXKzNi9yuYr5L0KC65U9mynnX69qYFdjSK0aOuIomVqiUEEqVsMP2BaLRLVNteAfook5Cmgjn5M4EDU5ziE6BrfwwGk');
}

.product-details {
  flex: 1;
  min-width: 0;
}

.product-name {
  font-weight: 500;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.product-sku {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.125rem;
}

.text-right {
  text-align: right;
}

.text-center {
  text-align: center;
}

.price-value {
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  color: #94a3b8;
}

.price-note {
  font-size: 0.625rem;
  color: #64748b;
  margin-top: 0.125rem;
}

.price-input-wrapper {
  position: relative;
  max-width: 8.75rem;
  margin-left: auto;
}

.currency-symbol {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #94a3b8;
  font-size: 0.75rem;
}

.price-input {
  width: 100%;
  padding: 0.375rem 0.75rem 0.375rem 1.5rem;
  text-align: right;
  background-color: #111827;
  border: 1px solid #232f48;
  border-radius: 0.25rem;
  color: white;
  font-size: 0.875rem;
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  font-weight: 500;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  outline: none;
  transition: all 0.2s;
}

.price-input:focus {
  ring: 1px solid #135bec;
  border-color: #135bec;
}

.price-input.warning {
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.price-input.warning:focus {
  ring: 1px solid #ef4444;
  border-color: #ef4444;
}

.price-diff {
  font-size: 0.625rem;
  margin-top: 0.25rem;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.125rem;
  font-weight: 600;
}

.price-diff.up {
  color: #22c55e;
}

.price-diff.down {
  color: #ef4444;
}

.price-diff.neutral {
  color: #94a3b8;
}

.price-diff .material-symbols-outlined {
  font-size: 0.75rem;
}

.profit-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 700;
}

.profit-badge.positive {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.3);
}

.profit-badge.negative {
  background-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.4);
  animation: pulse-red 2s infinite;
}

@keyframes pulse-red {
  0%, 100% {
    box-shadow: 0 0 0 0 rgba(239, 68, 68, 0.4);
  }
  50% {
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.1);
  }
}

.profit-warning {
  font-size: 0.625rem;
  color: #ef444;
  margin-top: 0.125rem;
  font-weight: 500;
}

.action-btn {
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #94a3b8;
}

.action-btn:hover {
  color: #135bec;
}

/* Empty State */
.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #94a3b8;
}

.empty-state .material-symbols-outlined {
  font-size: 3rem;
  color: #64748b;
  margin-bottom: 1rem;
}

.empty-state p {
  font-size: 0.875rem;
}

/* Product SKU Styles */
.product-sku {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.125rem;
}

.product-sku.no-match {
  color: #ef4444;
}

/* Period Unit Select */
.period-unit-select {
  padding: 0.25rem 0.5rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.25rem;
  color: #cbd5e1;
  font-size: 0.75rem;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.period-unit-select:hover {
  border-color: #324467;
}

.period-unit-select:focus {
  border-color: #135bec;
}

.period-unit-select option {
  background-color: #1a2332;
  color: #cbd5e1;
}

/* Table Footer */
.table-footer {
  padding: 1rem;
  border-top: 1px solid #232f48;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #1a2332;
}

.footer-text {
  font-size: 0.875rem;
  color: #94a3b8;
}

.pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn,
.page-number {
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.page-btn:hover:not(:disabled),
.page-number:hover {
  background-color: rgba(100, 116, 139, 0.1);
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-number {
  padding: 0.25rem 0.75rem;
}

.page-number.active {
  background-color: #135bec;
  color: white;
}

/* Bottom Bar */
.bottom-bar {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  z-index: 100;
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
  gap: 1rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.info-item .material-symbols-outlined {
  font-size: 1.25rem;
}

.info-item:first-child .material-symbols-outlined {
  color: #22c55e;
}

.info-item:last-child .material-symbols-outlined {
  color: #3b82f6;
}

.info-item strong {
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
  transform: translateY(0);
}

.btn-next:hover {
  background-color: #1d6bf5;
  transform: translateY(-2px);
}

.btn-next .material-symbols-outlined {
  font-size: 1rem;
}

/* Scrollbar Styles */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(35, 47, 72, 0.5);
}

::-webkit-scrollbar-thumb {
  background: #324467;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4a5d85;
}

/* ===== 批量调价弹窗 ===== */
.batch-adjust-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  animation: ba-fade-in 0.2s ease-out;
}

@keyframes ba-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

.batch-adjust-dialog {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
  width: 90%;
  max-width: 420px;
  animation: ba-slide-up 0.25s ease-out;
  overflow: hidden;
}

@keyframes ba-slide-up {
  from { transform: translateY(16px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

.batch-adjust-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #232f48;
  background-color: #151c2b;
}

.batch-adjust-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.05rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}

.batch-adjust-title .icon-up {
  color: #22c55e;
}

.batch-adjust-title .icon-down {
  color: #ef4444;
}

.batch-adjust-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.batch-adjust-close:hover {
  background-color: rgba(255, 255, 255, 0.08);
  color: #f1f5f9;
}

.batch-adjust-body {
  padding: 1.25rem;
}

.batch-adjust-hint {
  color: #94a3b8;
  font-size: 0.875rem;
  margin: 0 0 1.25rem 0;
  line-height: 1.5;
}

.batch-adjust-hint strong {
  color: #135bec;
}

.batch-adjust-input-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.batch-adjust-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
}

.batch-adjust-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.batch-adjust-input {
  width: 100%;
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  background-color: #101622;
  border: 1px solid #324467;
  border-radius: 0.5rem;
  color: white;
  font-size: 1.125rem;
  font-weight: 600;
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  outline: none;
  transition: all 0.2s;
}

.batch-adjust-input:focus {
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.batch-adjust-input::placeholder {
  color: #475569;
  font-weight: 400;
}

/* 隐藏数字输入框的上下箭头 */
.batch-adjust-input::-webkit-inner-spin-button,
.batch-adjust-input::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}
.batch-adjust-input[type=number] {
  -moz-appearance: textfield;
}

.batch-adjust-suffix {
  position: absolute;
  right: 0.75rem;
  color: #64748b;
  font-size: 1rem;
  font-weight: 600;
  pointer-events: none;
}

.batch-adjust-example {
  color: #64748b;
  font-size: 0.8rem;
  margin: 0.25rem 0 0 0;
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
}

.batch-adjust-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #232f48;
  background-color: #151c2b;
}

.batch-adjust-btn {
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.batch-adjust-btn.cancel {
  background: transparent;
  border: 1px solid #324467;
  color: #cbd5e1;
}

.batch-adjust-btn.cancel:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.batch-adjust-btn.confirm {
  border: none;
  color: white;
  font-weight: 600;
}

.batch-adjust-btn.confirm.btn-up {
  background-color: #22c55e;
}

.batch-adjust-btn.confirm.btn-up:hover:not(:disabled) {
  background-color: #16a34a;
}

.batch-adjust-btn.confirm.btn-down {
  background-color: #ef4444;
}

.batch-adjust-btn.confirm.btn-down:hover:not(:disabled) {
  background-color: #dc2626;
}

.batch-adjust-btn.confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
</style>
