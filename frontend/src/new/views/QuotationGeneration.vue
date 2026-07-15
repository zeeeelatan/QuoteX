<template>
  <div class="quotation-generation">
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
            <a @click="navigateToPriceAdjustment" class="breadcrumb-link">价格调整</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <span class="breadcrumb-current">生成报价单</span>
          </div>
          <h1 class="page-title">生成报价单</h1>
          <p class="page-description">预览详情，自定义最终布局，并导出文档。</p>
        </div>
        
        <!-- Steps Progress -->
        <div class="steps-progress">
          <div class="step completed">
            <div class="step-number">
              <span class="material-symbols-outlined">check</span>
            </div>
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
          <div class="step completed">
            <div class="step-number">
              <span class="material-symbols-outlined">check</span>
            </div>
            <span class="step-label" @click="navigateToPriceAdjustment" style="cursor: pointer;">价格调整</span>
          </div>
          <div class="step-divider"></div>
          <div class="step active">
            <div class="step-number">4</div>
            <span class="step-label" @click="navigateToQuotationGeneration" style="cursor: pointer;">生成报价</span>
          </div>
        </div>
      </div>

      <!-- Content Grid -->
      <div class="content-grid">
        <!-- Preview Section -->
        <div class="preview-section">
          <div class="preview-wrapper">
            <div class="quotation-document" ref="quotationDocRef">
              <div class="doc-decoration"></div>
              
              <!-- Document Header -->
              <div class="doc-header">
                <div class="company-info">
                  <div class="company-logo-upload" @click="triggerLogoUpload" title="点击上传自定义 Logo">
                    <!-- 自定义上传的图片 -->
                    <img v-if="customLogoUrl" :src="customLogoUrl" alt="公司Logo" class="custom-logo-img" />
                    <!-- 默认 Logo -->
                    <div v-else class="company-logo-text">
                      <svg class="logo-icon" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
                        <circle cx="50" cy="50" r="45" fill="none" stroke="#005bac" stroke-width="6"/>
                        <path d="M30 50 Q50 20 70 50 Q50 80 30 50" fill="#8dc21f" stroke="none"/>
                        <path d="M25 35 Q50 10 75 35" fill="none" stroke="#005bac" stroke-width="5" stroke-linecap="round"/>
                      </svg>
                      <div class="logo-text-group">
                        <span class="logo-cn">源晨动力</span>
                        <span class="logo-en">YUANCHENDONGLI</span>
                      </div>
                    </div>
                    <div class="logo-upload-hint">
                      <span class="material-symbols-outlined">upload</span>
                    </div>
                    <input 
                      type="file" 
                      ref="logoInputRef" 
                      accept="image/*" 
                      @change="handleLogoUpload" 
                      style="display: none;"
                    />
                  </div>
                  <h2 class="company-name">{{ quoteCompanyName }}</h2>
                  <p class="company-address" style="white-space: pre-line;">{{ quoteCompanyAddress }}</p>
                  <p class="company-contact" v-if="quoteContactName">联系人：{{ quoteContactName }}</p>
                  <p class="company-contact" v-if="quoteContactPhone">电话：{{ quoteContactPhone }}</p>
                </div>
                <div class="quote-info">
                  <h1 class="doc-title">报价单</h1>
                  <p class="quote-number">单号：{{ quoteNumber }}</p>
                  <p class="quote-date">{{ quoteDate }}</p>
                </div>
              </div>

              <!-- Customer Info -->
              <div class="info-grid">
                <div class="info-block">
                  <p class="info-label">客户信息</p>
                  <p class="customer-name">{{ selectedCustomerInfo.customerName }}</p>
                  <p class="company-contact" v-if="selectedCustomerInfo.customerAddress" style="white-space: pre-line;">{{ selectedCustomerInfo.customerAddress }}</p>
                  <p class="company-contact" v-if="selectedCustomerInfo.contactPerson">联系人：{{ selectedCustomerInfo.contactPerson }}</p>
                  <p class="company-contact" v-if="selectedCustomerInfo.contactPhone">电话：{{ selectedCustomerInfo.contactPhone }}</p>
                </div>
                <div class="info-block text-right">
                  <p class="info-label">有效期</p>
                  <p class="validity-date">{{ validityDate }}之前有效</p>
                </div>
              </div>

              <!-- Items Table -->
              <div class="items-table" :class="{ 'is-scrolling': !isGeneratingPDF }">
                <div class="items-table-scroll" ref="itemsWrapperRef">
                  <table class="quote-table">
                    <thead>
                      <tr>
                        <th class="col-no">序号</th>
                        <th class="col-desc">项目描述</th>
                        <th class="col-qty">数量</th>
                        <th class="col-period">服务周期</th>
                        <th class="col-price">单价</th>
                        <th class="col-total">总价</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-if="tableData.length === 0">
                        <td colspan="6" style="text-align: center; padding: 3rem; color: #94a3b8;">
                          暂无数据，请先完成价格调整
                        </td>
                      </tr>
                      <tr v-if="qTopPadding > 0" :style="{ height: qTopPadding + 'px' }" class="virtual-spacer"><td></td></tr>
                      <tr v-for="(item, i) in qVisibleItems" :key="qStartIndex + i" class="item-row" :style="{ height: QUOTE_ROW_HEIGHT + 'px' }">
                        <td class="text-center col-no">{{ qStartIndex + i + 1 }}</td>
                        <td class="item-desc">
                          <p class="item-name">{{ item.model || item.matchedModel || '未命名产品' }}</p>
                          <p class="item-detail">
                            厂商: {{ formatManufacturer(item.matchedManufacturer || item.manufacturer) || '-' }}
                            <span v-if="item.matchedSeries"> | 系列: {{ item.matchedSeries }}</span>
                            <span v-if="item.serviceLevel"> | 服务级别: {{ item.serviceLevel }}</span>
                          </p>
                        </td>
                        <td class="text-center">{{ item.quantity || 1 }}</td>
                        <td class="text-center">{{ formatServicePeriodDisplay(item) }}</td>
                        <td class="text-right">¥{{ getItemUnitPrice(item).toFixed(2) }}</td>
                        <td class="text-right item-total">¥{{ getItemTotalPrice(item).toFixed(2) }}</td>
                      </tr>
                      <tr v-if="qBottomPadding > 0" :style="{ height: qBottomPadding + 'px' }" class="virtual-spacer"><td></td></tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Summary -->
              <div class="summary-section">
                <div class="summary-content">
                  <div class="summary-row">
                    <span class="summary-label">设备数量</span>
                    <span class="summary-value">{{ totalDeviceCount }} 台</span>
                  </div>
                  <div class="summary-row">
                    <span class="summary-label">小计</span>
                    <span class="summary-value">¥{{ subtotal.toFixed(2) }}</span>
                  </div>
                  <div v-if="showTaxColumn" class="summary-row">
                    <span class="summary-label">税率</span>
                    <span class="summary-value">{{ (selectedTaxRate * 100).toFixed(0) }}%</span>
                  </div>
                  <div class="summary-total">
                    <span class="total-label">总计 (CNY)</span>
                    <span class="total-value">¥{{ total.toFixed(2) }}</span>
                  </div>
                  <div v-if="showSignature" class="signature-section">
                    <div class="signature-row">
                      <span class="signature-label">客户签字</span>
                      <div class="signature-line"></div>
                    </div>
                    <div class="signature-row">
                      <span class="signature-label">日期</span>
                      <div class="signature-line"></div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Terms -->
              <div class="terms-section">
                <h4 class="terms-title">条款与条件</h4>
                <p v-for="(para, idx) in termsContentParagraphs" :key="idx" class="terms-paragraph">{{ para }}</p>
                <div class="doc-footer">
                  <p class="footer-text">第 1 页 / 共 1 页</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Control Panel -->
        <div class="control-panel">
          <!-- Export Section -->
          <div class="panel-card">
            <h3 class="panel-title">
              <span class="material-symbols-outlined">ios_share</span>
              导出操作
            </h3>
            <div class="export-grid">
              <button class="export-btn pdf" @click="downloadPDF" :disabled="tableData.length === 0 || isGeneratingPDF">
                <span class="material-symbols-outlined">{{ isGeneratingPDF ? 'hourglass_empty' : 'picture_as_pdf' }}</span>
                <span class="btn-text">{{ isGeneratingPDF ? '生成中...' : '下载 PDF' }}</span>
              </button>
              <button class="export-btn excel" @click="openPreviewDialog" :disabled="tableData.length === 0">
                <span class="material-symbols-outlined">{{ isExporting ? 'hourglass_empty' : 'table_view' }}</span>
                <span class="btn-text">{{ isExporting ? '导出中...' : '导出 Excel' }}</span>
              </button>
            </div>
            <button class="send-email-btn">
              <span class="material-symbols-outlined">send</span>
              通过邮件发送
            </button>
          </div>

          <!-- Configuration Section -->
          <div class="panel-card">
            <h3 class="panel-title">
              <span class="material-symbols-outlined">tune</span>
              配置选项
            </h3>
            
            <div class="config-group">
              <label class="config-label">客户选择</label>
              <div class="select-wrapper">
                <select v-model="selectedCustomer" class="config-select">
                  <option :value="''">请选择客户</option>
                  <option v-for="c in customersList" :key="c.id" :value="c.id">{{ c.customer_name }}</option>
                </select>
                <span class="material-symbols-outlined select-icon">expand_more</span>
              </div>
            </div>

            <div class="config-group">
              <label class="config-label">布局选择</label>
              <div class="select-wrapper">
                <select v-model="priceLayout" class="config-select">
                  <option value="layout1">数量+单价(未税)+总价(未税)</option>
                  <option value="layout2">数量+单价(未税)+税率+总价(含税)</option>
                  <option value="layout3">数量+单价(含税6%)+总价(含税6%)</option>
                  <option value="layout4">数量+单价(含税13%)+总价(含税13%)</option>
                </select>
                <span class="material-symbols-outlined select-icon">expand_more</span>
              </div>
            </div>

            <div class="config-group">
              <label class="config-label">模板选择</label>
              <div class="select-wrapper">
                <select v-model="templateStyle" class="config-select">
                  <option value="system_modern">系统内置 - 现代商务</option>
                  <option value="system_minimal">系统内置 - 极简暗黑</option>
                  <option value="custom_1">自定义 - 企业标准版</option>
                </select>
                <span class="material-symbols-outlined select-icon">expand_more</span>
              </div>
            </div>

            <div class="config-group">
              <label class="config-label">服务条款</label>
              <div class="select-wrapper">
                <select v-model="serviceTerms" class="config-select">
                  <option v-for="term in serviceTermsList" :key="term.id" :value="String(term.id)">
                    {{ term.name }}
                  </option>
                </select>
                <span class="material-symbols-outlined select-icon">expand_more</span>
              </div>
            </div>

            <hr class="divider-line" />

            <div class="toggle-group">
              <div class="toggle-item">
                <span class="toggle-label">显示税费列</span>
                <div v-if="showTaxColumn" class="tax-rate-inline">
                  <label class="tax-rate-option" :class="{ active: selectedTaxRate === 0.06 }">
                    <input type="radio" v-model="selectedTaxRate" :value="0.06" />
                    <span>6%</span>
                  </label>
                  <label class="tax-rate-option" :class="{ active: selectedTaxRate === 0.13 }">
                    <input type="radio" v-model="selectedTaxRate" :value="0.13" />
                    <span>13%</span>
                  </label>
                </div>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="showTaxColumn" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div class="toggle-item">
                <span class="toggle-label">包含折扣信息</span>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="showDiscount" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
              <div class="toggle-item">
                <span class="toggle-label">显示签字栏</span>
                <label class="toggle-switch">
                  <input type="checkbox" v-model="showSignature" />
                  <span class="toggle-slider"></span>
                </label>
              </div>
            </div>
          </div>

          <!-- Status Card -->
          <div class="status-card">
            <div class="status-icon">
              <span class="material-symbols-outlined">{{ tableData.length > 0 ? 'check_circle' : 'info' }}</span>
            </div>
            <div class="status-text">
              <p class="status-title">{{ tableData.length > 0 ? '准备就绪' : '等待数据' }}</p>
              <p class="status-desc">{{ tableData.length > 0 ? `共 ${tableData.length} 项报价数据` : '请先完成价格调整步骤' }}</p>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- Sticky Bottom Bar -->
    <div class="bottom-bar">
      <div class="bottom-content">
        <div class="bottom-info">
          <div class="info-item">
            <span class="material-symbols-outlined">payments</span>
            <span>报价总额: <strong>¥{{ formatNumber(total) }}</strong></span>
          </div>
          <div class="divider-vertical"></div>
          <div class="info-item">
            <span class="material-symbols-outlined">format_list_numbered</span>
            <span>共 <strong>{{ tableData.length }}</strong> 项数据</span>
          </div>
        </div>
        <div class="bottom-actions">
          <button class="btn-back" @click="navigateBack">上一步</button>
          <button class="btn-complete" @click="completeQuotation">
            完成报价
            <span class="material-symbols-outlined">check_circle</span>
          </button>
        </div>
      </div>
    </div>

    <!-- Excel 预览弹窗 -->
    <Teleport to="body">
      <div v-if="showPreviewDialog" class="preview-overlay" @click.self="closePreviewDialog">
        <div class="preview-dialog" @click.stop>
          <div class="preview-header">
            <h3 class="preview-title">
              <span class="material-symbols-outlined">table_view</span>
              Excel 导出预览
            </h3>
            <button class="close-btn" @click="closePreviewDialog">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>

          <div class="preview-content">
            <!-- 原始表格预览 -->
            <div class="preview-table-section">
              <div class="preview-table-header">
                <h4 class="preview-table-title">原始表格 + 维保单价</h4>
                <span class="preview-table-count">{{ previewOriginalData.data?.length || 0 }} 行</span>
              </div>
              <div class="preview-table-wrapper">
                <table class="preview-table">
                  <thead>
                    <tr>
                      <th v-for="header in previewOriginalData.headers" :key="header">{{ header }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in previewOriginalData.data?.slice(0, 5)" :key="index">
                      <td v-for="header in previewOriginalData.headers" :key="header">
                        {{ formatCellValue(row[header]) }}
                      </td>
                    </tr>
                    <tr v-if="!previewOriginalData.data || previewOriginalData.data.length === 0">
                      <td :colspan="previewOriginalData.headers?.length || 1" class="empty-preview">
                        暂无数据
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="previewOriginalData.data && previewOriginalData.data.length > 5" class="preview-more-hint">
                  仅显示前 5 行，导出后包含全部数据
                </div>
              </div>
            </div>

            <!-- 转换后表格预览 -->
            <div class="preview-table-section">
              <div class="preview-table-header">
                <h4 class="preview-table-title">转换后表格 + 更新单价</h4>
                <span class="preview-table-count">{{ previewConvertedData.data?.length || 0 }} 行</span>
              </div>
              <div class="preview-table-wrapper">
                <table class="preview-table">
                  <thead>
                    <tr>
                      <th v-for="header in previewConvertedData.headers" :key="header">{{ header }}</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, index) in previewConvertedData.data?.slice(0, 5)" :key="index">
                      <td v-for="header in previewConvertedData.headers" :key="header">
                        {{ formatCellValue(row[header]) }}
                      </td>
                    </tr>
                    <tr v-if="!previewConvertedData.data || previewConvertedData.data.length === 0">
                      <td :colspan="previewConvertedData.headers?.length || 1" class="empty-preview">
                        暂无数据
                      </td>
                    </tr>
                  </tbody>
                </table>
                <div v-if="previewConvertedData.data && previewConvertedData.data.length > 5" class="preview-more-hint">
                  仅显示前 5 行，导出后包含全部数据
                </div>
              </div>
            </div>
          </div>

          <div class="preview-footer">
            <button class="preview-btn cancel" @click="closePreviewDialog">
              取消
            </button>
            <button class="preview-btn confirm" @click="exportQuotationExcel" :disabled="isExporting">
              <span class="material-symbols-outlined">{{ isExporting ? 'hourglass_empty' : 'download' }}</span>
              {{ isExporting ? '导出中...' : '确认导出' }}
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
import { ref, onMounted, computed, watch, nextTick } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import api from '../../api/index'
import BranchPageHeader from '../components/BranchPageHeader.vue'
import ProductDatabaseModal from '../components/ProductDatabaseModal.vue'
import { getStorageKeyPrefix } from '../stores/authStore'
import { useVirtualList } from '../composables/useVirtualList'
import {
  PAGE_STATE_KEYS,
  FLOW_DATA_KEYS,
  savePageState,
  restorePageState,
  clearPageState,
  saveFlowData,
  getFlowData,
  getNavigationMode,
  clearNavigationMode,
  setNavigationMode,
  clearAllQuotationStates,
  getExternalRef,
  type QuotationGenerationState,
  type TableDataWithHeaders,
  type SheetTableDataWithHeaders,
  type DocumentRecognitionState
} from '../stores/quotationStore'

const router = useRouter()

// State
const tableData = ref<any[]>([])
const projectName = ref('设备报价单')
const customerName = ref('')
const validDays = ref(30)
const notes = ref('')
const isExporting = ref(false)
const sourceFileName = ref('')  // 源文件名（来自智能识别模块导入的文件）
const isGeneratingPDF = ref(false)  // PDF生成状态
const quotationDocRef = ref<HTMLElement | null>(null)  // 报价单预览区域引用

// ============ 虚拟滚动（仅在预览态生效，PDF 导出时关闭以让 html2canvas 抓全量 DOM）============
const itemsWrapperRef = ref<HTMLElement | null>(null)
const QUOTE_ROW_HEIGHT = 56
const quoteVirtualItems = computed(() => {
  // PDF 生成时返回完整列表，使虚拟化退化为全量渲染
  return isGeneratingPDF.value ? [] : tableData.value
})
const { visibleItems: qVisibleItemsRaw, topPadding: qTopPaddingRaw, bottomPadding: qBottomPaddingRaw, startIndex: qStartIndexRaw } =
  useVirtualList(quoteVirtualItems, QUOTE_ROW_HEIGHT, itemsWrapperRef)
const qVisibleItems = computed(() => isGeneratingPDF.value ? tableData.value : qVisibleItemsRaw.value)
const qTopPadding = computed(() => isGeneratingPDF.value ? 0 : qTopPaddingRaw.value)
const qBottomPadding = computed(() => isGeneratingPDF.value ? 0 : qBottomPaddingRaw.value)
const qStartIndex = computed(() => isGeneratingPDF.value ? 0 : qStartIndexRaw.value)

// Logo 上传相关
const logoInputRef = ref<HTMLInputElement | null>(null)
const customLogoUrl = ref<string>('')

// 公司信息（从个人设置动态加载）
const quoteCompanyName = ref('')
const quoteCompanyAddress = ref('')
const quoteContactName = ref('')   // 登录用户姓名
const quoteContactPhone = ref('')  // 登录用户联系方式

// 客户列表（从个人设置动态加载）与当前选中的客户 id
const customersList = ref<{ id: number; customer_name: string; contact_person?: string; contact_phone?: string; customer_address?: string }[]>([])
const selectedCustomer = ref<number | ''>('')  // 客户选择，对应客户 id

// 配置选项状态
const priceLayout = ref('layout2')  // 布局选择（默认：数量+单价(未税)+税率+总价(含税)）
const templateStyle = ref('system_modern')  // 模板选择
const serviceTerms = ref('')  // 服务条款（当前选中的ID）
const serviceTermsList = ref<any[]>([])  // 服务条款列表
const showTaxColumn = ref(true)  // 显示税费列
const selectedTaxRate = ref(0.13)  // 税率选择，默认13%
const showDiscount = ref(true)  // 包含折扣信息
const showSignature = ref(false)  // 显示签字栏

// 预览弹窗状态
const showPreviewDialog = ref(false)

// 产品数据库弹窗
const isProductDatabaseModalOpen = ref(false)

const openProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = true
}

const closeProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = false
}

function normalizeLogoSource(logoUrl: string): string {
  if (!logoUrl) return ''
  const normalized = logoUrl.trim()
  if (!normalized) return ''

  // blob URL 不能跨会话持久化，且在 HTTPS 页面中 blob:http:// 会触发不安全警告
  if (normalized.startsWith('blob:')) return ''

  if (typeof window !== 'undefined' && window.location.protocol === 'https:' && normalized.startsWith('http://')) {
    return `https://${normalized.slice('http://'.length)}`
  }

  return normalized
}

// 根据「客户选择」展示的客户信息（来自个人设置客户列表）
const selectedCustomerInfo = computed(() => {
  const id = selectedCustomer.value === '' ? null : Number(selectedCustomer.value)
  if (id == null) {
    return {
      customerName: '-',
      contactPerson: '',
      contactPhone: '',
      customerAddress: ''
    }
  }
  const customer = customersList.value.find(c => c.id === id)
  if (!customer) {
    return {
      customerName: '-',
      contactPerson: '',
      contactPhone: '',
      customerAddress: ''
    }
  }
  return {
    customerName: customer.customer_name || '客户名称',
    contactPerson: customer.contact_person || '',
    contactPhone: customer.contact_phone || '',
    customerAddress: customer.customer_address || ''
  }
})

// 从个人设置加载公司信息、客户列表、用户资料
async function loadCompanyAndCustomers() {
  try {
    const [companiesData, customersData, profileData] = await Promise.all([
      api.get('/user-profile/companies'),
      api.get('/user-profile/customers'),
      api.get('/user-profile/')
    ])
    if (companiesData && companiesData.length > 0) {
      const company = companiesData[0]
      quoteCompanyName.value = company.company_name || '公司名称'
      quoteCompanyAddress.value = company.company_address || ''
      // 若用户未手动在报价页上传过 Logo，则使用个人设置中的公司 Logo 作为默认
      const companyLogo = normalizeLogoSource(company.company_logo || '')
      if (!customLogoUrl.value && companyLogo) {
        customLogoUrl.value = companyLogo
      }
    } else {
      quoteCompanyName.value = '公司名称'
      quoteCompanyAddress.value = ''
    }
    if (customersData && Array.isArray(customersData)) {
      customersList.value = customersData
    } else {
      customersList.value = []
    }
    // 加载当前用户姓名和联系方式
    if (profileData) {
      quoteContactName.value = profileData.name || ''
      quoteContactPhone.value = profileData.phone || ''
    }
  } catch (err) {
    console.error('加载公司/客户信息失败', err)
    quoteCompanyName.value = '公司名称'
    quoteCompanyAddress.value = ''
    customersList.value = []
  }
}

// 原始表格和转换后表格数据（用于预览和导出）
const originalTableData = ref<TableDataWithHeaders | null>(null)
const convertedTableData = ref<TableDataWithHeaders | null>(null)
const originalSheetTables = ref<SheetTableDataWithHeaders[]>([])
const convertedSheetTables = ref<SheetTableDataWithHeaders[]>([])

function buildOriginalPreviewForSheet(headers: string[], data: any[], sheetName?: string) {
  // 构建型号→价格映射（扫描所有可能的型号标识）
  const priceByModel = new Map<string, number>()
  const scopedTableData = sheetName
    ? tableData.value.filter(item => !item.sheetName || item.sheetName === sheetName)
    : tableData.value

  scopedTableData.forEach(item => {
    const keys = [item.model, item.matchedModel, item.originalModel].filter(Boolean)
    const price = item.finalPrice || item.suggestedPrice || 0
    keys.forEach(k => {
      const normalized = k.toString().trim().toUpperCase()
      if (normalized) priceByModel.set(normalized, price)
    })
  })

  // 判断原始表和匹配表行数是否一致（一致则可安全使用行索引映射）
  const rowCountMatch = data.length === scopedTableData.length

  // 根据布局选择确定价格乘数和表头名称
  let priceMultiplier = 1
  let priceHeaderName = '维保单价'
  if (priceLayout.value === 'layout3') {
    priceMultiplier = 1.06
    priceHeaderName = '维保单价(含税6%)'
  } else if (priceLayout.value === 'layout4') {
    priceMultiplier = 1.13
    priceHeaderName = '维保单价(含税13%)'
  }

  return {
    headers: [...headers, priceHeaderName],
    data: data.map((row, rowIndex) => {
      const newRow = { ...row }
      let basePrice = 0

      // 优先按型号名称匹配：扫描该行所有列值，尝试匹配已知型号（避免索引错位）
      const allValues = Object.values(row)
      for (const val of allValues) {
        if (val !== null && val !== undefined && val !== '') {
          const normalized = String(val).trim().toUpperCase()
          const matched = priceByModel.get(normalized)
          if (matched && matched > 0) {
            basePrice = matched
            break
          }
        }
      }

      // 兜底：行数一致时按行索引获取价格
      if (basePrice === 0 && rowCountMatch && rowIndex < scopedTableData.length) {
        const item = scopedTableData[rowIndex]
        basePrice = item.finalPrice || item.suggestedPrice || 0
      }

      const adjustedPrice = Math.round(basePrice * priceMultiplier * 100) / 100
      newRow[priceHeaderName] = adjustedPrice
      return newRow
    })
  }
}

// 预览数据：原始表格 + 维保单价列
const previewOriginalData = computed(() => {
  if (!originalTableData.value || !tableData.value.length) return []

  const { headers, data } = originalTableData.value
  return buildOriginalPreviewForSheet(headers, data)
})

// 预览数据：转换后表格 + 更新单价为建议售价
const previewConvertedData = computed(() => {
  if (!convertedTableData.value || !tableData.value.length) return []

  const { headers, data } = convertedTableData.value

  // 备用映射：按型号名称匹配
  const priceByModel = new Map<string, number>()
  tableData.value.forEach(item => {
    const keys = [item.model, item.matchedModel, item.originalModel].filter(Boolean)
    const price = item.finalPrice || item.suggestedPrice || 0
    keys.forEach(k => {
      const normalized = k.toString().trim().toUpperCase()
      if (normalized) priceByModel.set(normalized, price)
    })
  })

  // 判断转换表和匹配表行数是否一致
  const rowCountMatch = data.length === tableData.value.length

  // 根据布局选择确定价格乘数和表头名称
  let priceMultiplier = 1
  let priceHeaderName = '单价'
  let originalPriceHeader = '单价'  // 原始表头名称，用于查找原有数据
  if (priceLayout.value === 'layout3') {
    priceMultiplier = 1.06
    priceHeaderName = '单价(含税6%)'
  } else if (priceLayout.value === 'layout4') {
    priceMultiplier = 1.13
    priceHeaderName = '单价(含税13%)'
  }

  // 更新表头：将"单价"替换为新的表头名称
  const newHeaders = headers.map(h => h === originalPriceHeader ? priceHeaderName : h)

  return {
    headers: newHeaders,
    data: data.map((row, rowIndex) => {
      const newRow: Record<string, any> = {}
      // 复制所有列数据，并处理价格列
      headers.forEach(h => {
        if (h === originalPriceHeader) {
          let basePrice = 0
          // 优先按型号名称匹配（避免索引错位）
          const modelValue = (row['设备/软件型号'] || '').toString().trim().toUpperCase()
          if (modelValue) {
            basePrice = priceByModel.get(modelValue) || 0
          }
          // 扫描所有列值匹配
          if (basePrice === 0) {
            for (const val of Object.values(row)) {
              if (val !== null && val !== undefined && val !== '') {
                const normalized = String(val).trim().toUpperCase()
                const matched = priceByModel.get(normalized)
                if (matched && matched > 0) {
                  basePrice = matched
                  break
                }
              }
            }
          }
          // 兜底：行数一致时按行索引取价
          if (basePrice === 0 && rowCountMatch && rowIndex < tableData.value.length) {
            const item = tableData.value[rowIndex]
            basePrice = item.finalPrice || item.suggestedPrice || 0
          }
          // 如果仍为 0，保留原单价值
          if (basePrice === 0) {
            basePrice = Number(row[h]) || 0
          }
          const adjustedPrice = Math.round(Number(basePrice) * priceMultiplier * 100) / 100
          newRow[priceHeaderName] = adjustedPrice
        } else {
          newRow[h] = row[h]
        }
      })
      return newRow
    })
  }
})

// Get current state for saving
function getCurrentState(): QuotationGenerationState {
  return {
    tableData: tableData.value,
    projectName: projectName.value,
    customerName: customerName.value,
    validDays: validDays.value,
    notes: notes.value,
    hasData: tableData.value.length > 0
  }
}

// Automatically save state when leaving this page (for breadcrumb navigation restore)
onBeforeRouteLeave((to, from, next) => {
  // Always save state when leaving, so breadcrumb navigation can restore it
  if (tableData.value.length > 0) {
    savePageState(PAGE_STATE_KEYS.QUOTATION_GENERATION, getCurrentState())
    // Also save to flow data
    saveFlowData(FLOW_DATA_KEYS.FINAL_DATA, tableData.value)
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
  router.push('/price-adjustment')
}

const navigateToQuotationGeneration = () => {
  // 当前页面，无需跳转
}

const navigateBack = () => {
  // 返回价格调整页面
  router.push('/price-adjustment')
}

// 当前用户名（可以从 localStorage 或其他地方获取）
const currentUserName = ref('系统用户')

// 加载服务条款列表
async function loadServiceTerms() {
  try {
    console.log('[QuotationGeneration] Loading service terms...')
    const termsData = await api.get('/service-terms/')
    console.log('[QuotationGeneration] Service terms response:', termsData)

    // 在列表前面添加"无"选项
    serviceTermsList.value = [
      { id: 'none', name: '无', products: [], content: '', last_modified: '', created_at: '' },
      ...termsData
    ]

    // 如果有数据且当前没有选中，默认选中"标准维保条款"
    if (termsData.length > 0 && !serviceTerms.value) {
      // 查找"标准维保条款"
      const standardTerm = termsData.find((t: any) => t.name === '标准维保条款')
      if (standardTerm) {
        serviceTerms.value = String(standardTerm.id)
        console.log('[QuotationGeneration] Default selected term: 标准维保条款, id:', serviceTerms.value)
      } else {
        // 如果找不到"标准维保条款"，使用第一个实际条款（跳过"无"）
        serviceTerms.value = String(termsData[0].id)
        console.log('[QuotationGeneration] Default selected term:', serviceTerms.value)
      }
    }
  } catch (error) {
    console.error('Failed to load service terms:', error)
    // 降级方案：只有"无"选项
    serviceTermsList.value = [
      { id: 'none', name: '无', products: [], content: '', last_modified: '', created_at: '' }
    ]
    serviceTerms.value = 'none'
  }
}

const completeQuotation = async () => {
  try {
    // 先确认用户是否要完成报价
    await ElMessageBox.confirm(
      '确认完成报价？完成后将清除当前报价数据。',
      '完成报价',
      {
        confirmButtonText: '确认完成',
        cancelButtonText: '返回修改',
        type: 'warning',
      }
    )

    // 保存历史记录到后端
    try {
      // 获取各节点数据 - 从内存 store 读取原始导入数据
      let rawImportData = getFlowData<TableDataWithHeaders>(FLOW_DATA_KEYS.ORIGINAL_TABLE_DATA)
      let convertedImportData = getFlowData<TableDataWithHeaders>(FLOW_DATA_KEYS.CONVERTED_TABLE_DATA)

      // 如果 store 中没有，尝试从组件本地 ref 获取（onMounted 时已加载）
      if (!rawImportData && originalTableData.value) {
        rawImportData = originalTableData.value
      }
      if (!convertedImportData && convertedTableData.value) {
        convertedImportData = convertedTableData.value
      }

      // 再尝试从 DocumentRecognition 页面状态恢复
      if (!rawImportData || !convertedImportData) {
        const docState = restorePageState<DocumentRecognitionState>(PAGE_STATE_KEYS.DOC_RECOGNITION)
        if (docState) {
          if (!rawImportData && docState.originalTableData?.length > 0) {
            rawImportData = {
              headers: docState.originalHeaders || [],
              data: docState.originalTableData
            }
          }
          if (!convertedImportData && docState.convertedTableData?.length > 0) {
            convertedImportData = {
              headers: docState.convertedHeaders || docState.visibleColumns || [],
              data: docState.convertedTableData
            }
          }
        }
      }

      // import_data 需要包含原始表格和转换后表格，用于历史记录的"导入数据"节点展示
      const importData = rawImportData ? {
        headers: rawImportData.headers,
        data: rawImportData.data,
        // 同时保存转换后的数据（用于历史记录查看）
        converted: convertedImportData ? {
          headers: convertedImportData.headers,
          data: convertedImportData.data
        } : null
      } : null

      // 获取匹配数据（从 sessionStorage）
      const matchedData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
      // 获取价格调整数据
      const adjustedData = getFlowData<any[]>(FLOW_DATA_KEYS.ADJUSTED_DATA)

      // 构建报价单数据
      const quoteData = {
        original: originalTableData.value ? {
          headers: [...originalTableData.value.headers, '维保单价'],
          data: previewOriginalData.value?.data || []
        } : null,
        converted: convertedTableData.value ? {
          headers: [...convertedTableData.value.headers, '维保单价'],
          data: previewConvertedData.value?.data || []
        } : null
      }

      // 计算总价
      const totalAmount = tableData.value.reduce((sum, item) => {
        return sum + getItemTotalPrice(item)
      }, 0)

      // 收集页面状态（与草稿保存模式一致）
      const docState = restorePageState<DocumentRecognitionState>(PAGE_STATE_KEYS.DOC_RECOGNITION)
      const savedPageStates: Record<string, any> = {}
      if (docState) savedPageStates.doc_recognition = docState

      // 构建历史记录数据
      const historyData = {
        file_name: sourceFileName.value || `${projectName.value}_${quoteNumber.value}.xlsx`,
        user_name: currentUserName.value,
        status: 'completed',
        total_amount: totalAmount,
        import_data: importData,
        match_data: matchedData || null,
        price_adjust_data: adjustedData || null,
        quote_data: quoteData,
        page_states: Object.keys(savedPageStates).length > 0 ? savedPageStates : null,
        data_source: 'datacenter',
        device_count: tableData.value.length,
        quote_metadata: {
          // 外部系统集成：若本次询价由第三方系统（如 TopSales）发起，
          // 携带其引用令牌，供对方按 GET /quote-history/by-ref/{ref} 查询本次报价结果
          external_ref: getExternalRef() || undefined,
          quote_number: quoteNumber.value,
          quote_date: quoteDate.value,
          project_name: projectName.value,
          customer_name: customerName.value,
          valid_days: validDays.value,
          validity_date: validityDate.value,
          service_terms: serviceTerms.value,
          service_terms_content: serviceTerms.value && serviceTerms.value !== 'none'
            ? serviceTermsList.value.find((t: any) => String(t.id) === String(serviceTerms.value))?.content || ''
            : '',
          // 公司信息快照
          company_name: quoteCompanyName.value,
          company_address: quoteCompanyAddress.value,
          company_logo: customLogoUrl.value || '',
          contact_name: quoteContactName.value,
          contact_phone: quoteContactPhone.value,
          // 客户信息快照
          customer_company: selectedCustomerInfo.value.customerName,
          customer_address: selectedCustomerInfo.value.customerAddress,
          customer_contact_person: selectedCustomerInfo.value.contactPerson,
          customer_contact_phone: selectedCustomerInfo.value.contactPhone,
          table_data: tableData.value.map(item => ({
            model: item.model || item.matchedModel || '未命名产品',
            matchedManufacturer: item.matchedManufacturer || item.manufacturer,
            matchedSeries: item.matchedSeries,
            serviceLevel: item.serviceLevel,
            servicePeriod: getItemServicePeriod(item),
            servicePeriodUnit: item.servicePeriodUnit,
            quantity: getItemQuantity(item),
            finalPrice: getItemUnitPrice(item),
            suggestedPrice: item.suggestedPrice,
            totalPrice: getItemTotalPrice(item)
          }))
        }
      }

      // 保存到后端
      await api.post('/quote-history/', historyData)
      console.log('History saved successfully')
    } catch (error) {
      console.error('Failed to save history:', error)
      // 保存失败时不能继续清空数据 / 提示"已完成"，否则会让用户误以为保存成功，
      // 实际报价数据却已丢失（例如未登录导致的 401，会在 axios 拦截器里弹出具体错误提示）
      return
    }

    // 完成报价：清除所有流程状态和本地数据
    clearAllQuotationStates()

    // 清空本地数据
    tableData.value = []
    projectName.value = '设备报价单'
    customerName.value = ''
    validDays.value = 30
    notes.value = ''
    quoteNumber.value = generateQuoteNumber()
    originalTableData.value = null
    convertedTableData.value = null

    ElMessage.success('报价已完成！所有数据已清除。')
    router.push('/')
  } catch (error: any) {
    if (error === 'cancel' || error?.toString?.().includes('cancel')) return
    console.error('completeQuotation error:', error)
    ElMessage.error('完成报价时发生错误，请重试。')
  }
}

// 格式化数字（添加千分位）
function formatNumber(value: number): string {
  if (value == null || isNaN(value)) return '0.00'
  return value.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// 生成报价单号
function generateQuoteNumber() {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const random = Math.floor(Math.random() * 9000) + 1000
  return `Q-${year}${month}${day}-${random}`
}

const quoteNumber = ref(generateQuoteNumber())

// Load data on mount
onMounted(() => {
  // 加载公司信息与客户列表（个人设置）
  loadCompanyAndCustomers()
  // 加载服务条款列表
  loadServiceTerms()

  // 加载自定义 Logo
  loadCustomLogo()
  
  // 获取导航模式
  const navigationMode = getNavigationMode()
  console.log('QuotationGeneration navigation mode:', navigationMode)

  // 加载原始表格和转换后表格数据（用于导出预览）
  originalTableData.value = getFlowData<TableDataWithHeaders>(FLOW_DATA_KEYS.ORIGINAL_TABLE_DATA)
  convertedTableData.value = getFlowData<TableDataWithHeaders>(FLOW_DATA_KEYS.CONVERTED_TABLE_DATA)
  originalSheetTables.value = getFlowData<SheetTableDataWithHeaders[]>(FLOW_DATA_KEYS.ORIGINAL_SHEET_TABLES) || []
  convertedSheetTables.value = getFlowData<SheetTableDataWithHeaders[]>(FLOW_DATA_KEYS.CONVERTED_SHEET_TABLES) || []

  // 获取源文件名（来自智能识别模块导入的文件）
  const docRecognitionState = restorePageState<DocumentRecognitionState>(PAGE_STATE_KEYS.DOC_RECOGNITION)
  if (docRecognitionState && docRecognitionState.currentFileName) {
    sourceFileName.value = docRecognitionState.currentFileName
    console.log('Source file name:', sourceFileName.value)
  }

  if (navigationMode === 'flow') {
    // 流程推进模式：从价格调整页面传递的最新数据
    const flowData = getFlowData<any[]>(FLOW_DATA_KEYS.ADJUSTED_DATA)
    if (flowData && flowData.length > 0) {
      console.log('Loading fresh flow data from PriceAdjustment:', flowData.length, 'items')
      tableData.value = flowData
      // 更新报价单号
      quoteNumber.value = generateQuoteNumber()
      // 清除旧的页面状态
      clearPageState(PAGE_STATE_KEYS.QUOTATION_GENERATION)
    } else {
      console.log('No flow data available')
    }
    // 清除导航模式标志
    clearNavigationMode()
  } else {
    // 面包屑跳转模式：优先恢复页面状态（保持最后一次修改的数据）
    const savedState = restorePageState<QuotationGenerationState>(PAGE_STATE_KEYS.QUOTATION_GENERATION)
    if (savedState && savedState.hasData && savedState.tableData && savedState.tableData.length > 0) {
      console.log('Restoring saved page state:', savedState.tableData.length, 'items')
      tableData.value = savedState.tableData
      projectName.value = savedState.projectName || projectName.value
      customerName.value = savedState.customerName || ''
      validDays.value = savedState.validDays || 30
      notes.value = savedState.notes || ''
    } else {
      // 如果没有保存的状态，尝试从流程数据加载
      const flowData = getFlowData<any[]>(FLOW_DATA_KEYS.ADJUSTED_DATA)
      if (flowData && flowData.length > 0) {
        console.log('No saved state, loading flow data:', flowData.length, 'items')
        tableData.value = flowData
        quoteNumber.value = generateQuoteNumber()
      }
    }
  }
})

// Computed: Quote date
const quoteDate = computed(() => {
  const now = new Date()
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
})

// Computed: Validity date
const validityDate = computed(() => {
  const now = new Date()
  now.setDate(now.getDate() + validDays.value)
  return `${now.getFullYear()}年${now.getMonth() + 1}月${now.getDate()}日`
})

// Computed: Subtotal
const subtotal = computed(() => {
  return tableData.value.reduce((sum, item) => {
    return sum + getItemTotalPrice(item)
  }, 0)
})

// Computed: Total (含税)
const total = computed(() => {
  if (showTaxColumn.value) {
    return subtotal.value * (1 + selectedTaxRate.value)
  }
  return subtotal.value
})

// Computed: 设备总数量（对数量列求和）
const totalDeviceCount = computed(() => {
  return tableData.value.reduce((sum, item) => sum + (parseInt(item.quantity) || 1), 0)
})

// 将服务条款 HTML 转为纯文本（保留段前空格与列表结构）
function convertHtmlToPlainText(html: string): string {
  if (!html) return ''
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')

  const blockTags = new Set([
    'p', 'div', 'section', 'article', 'header', 'footer',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
  ])

  const manualNumberRe = /^[\s\u00A0]*\d+[.、]/

  const walk = (node: Node, autoNumber: boolean, listType?: 'ol' | 'ul', listIndex = 1): string => {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.nodeValue || ''
    }
    if (node.nodeType !== Node.ELEMENT_NODE) {
      return ''
    }

    const el = node as HTMLElement
    const tag = el.tagName.toLowerCase()

    if (tag === 'br') {
      return '\n'
    }

    if (tag === 'ol' || tag === 'ul') {
      const listItems = Array.from(el.children).filter(
        child => child.tagName.toLowerCase() === 'li'
      ) as HTMLElement[]
      const effectiveType = autoNumber ? (tag as 'ol' | 'ul') : 'ul'
      let idx = 1
      let text = ''
      for (const li of listItems) {
        const line = walk(li, autoNumber, effectiveType, idx)
        if (line.trim().length > 0) {
          text += line
          idx += 1
        }
      }
      // 不额外补换行，避免列表边界产生空行
      return text
    }

    if (tag === 'li') {
      const content = Array.from(el.childNodes).map(child => walk(child, autoNumber)).join('')
      if (content.replace(/[\s\u00A0]/g, '').length === 0) {
        return ''
      }
      // 内容本身已以编号开头时不再追加自动序号
      const prefix = listType === 'ol' && !manualNumberRe.test(content) ? `${listIndex}. ` : ''
      const line = `${prefix}${content}`
      // 内容以块级元素结尾时已带换行，不再重复补，避免条目后产生空行
      return line.endsWith('\n') ? line : `${line}\n`
    }

    const content = Array.from(el.childNodes).map(child => walk(child, autoNumber)).join('')
    if (blockTags.has(tag)) {
      const hasVisible = content.replace(/[\s\u00A0]/g, '').length > 0
      return (hasVisible ? content : '') + '\n'
    }
    return content
  }

  const render = (autoNumber: boolean): string => {
    let text = ''
    doc.body.childNodes.forEach(child => {
      text += walk(child, autoNumber)
    })

    return text
      .replace(/\r\n/g, '\n')
      .replace(/\r/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/[ \t]+\n/g, '\n')
      .replace(/[ \t]+$/g, '')
      .replace(/^\n+/, '')
      .replace(/\n+$/, '')
  }

  // 两遍转换：先不加自动编号，若文本中已存在手动编号行（如 "12. 标题"），
  // 说明条款采用手动编号，直接采用该结果，避免 "2. 12." 双重编号；
  // 完全没有手动编号时，才对 <ol> 启用自动编号
  const plainWithoutAutoNumber = render(false)
  if (/^[ \t\u00A0]*\d+[.、]/m.test(plainWithoutAutoNumber)) {
    return plainWithoutAutoNumber
  }
  return render(true)
}

// Computed: 当前选中的服务条款内容（转换为纯文本）
const currentServiceTermsContent = computed(() => {
  // 如果选择了"无"或未选择，显示默认文本
  if (!serviceTerms.value || serviceTerms.value === 'none') {
    return '费用需在发票日期后 30 天内支付。逾期付款将收取每月 1.5% 的服务费。'
  }

  // 查找选中的服务条款
  const selectedTerm = serviceTermsList.value.find(t => String(t.id) === String(serviceTerms.value))
  if (!selectedTerm || !selectedTerm.content) {
    return '费用需在发票日期后 30 天内支付。逾期付款将收取每月 1.5% 的服务费。'
  }

  // 将 HTML 内容转换为纯文本，保留段前空格
  const plainText = convertHtmlToPlainText(selectedTerm.content)

  return plainText || '费用需在发票日期后 30 天内支付。逾期付款将收取每月 1.5% 的服务费。'
})

// 将条款内容拆分为行级列表，用于 PDF 分页时每行可独立分页，避免文字被截断
const termsContentParagraphs = computed(() => {
  const text = currentServiceTermsContent.value
  if (!text) return ['']
  // 按单个换行拆分为行，每行是独立的 DOM 元素，给分页算法提供逐行断点
  // 保留空行作为段落间距，不过滤掉空字符串，用 \u00A0 (non-breaking space) 代替纯空行以保留间距
  const lines = text.split(/\n/).map(s => {
    const withTabs = s.replace(/\t/g, '  ')
    const withIndent = withTabs.replace(/^( +)/, (m) => '\u00A0'.repeat(m.length))
    return withIndent.trimEnd() || '\u00A0'
  })
  // 过滤掉仅包含编号的孤立行（如 "1."），这些是编辑器产生的伪影
  // 条件：行内容匹配 "数字." 且后续行以同一编号开头（真正的条款标题）
  return lines.filter((line, idx) => {
    if (/^\d+\.\s*$/.test(line) && idx + 1 < lines.length && lines[idx + 1].startsWith(line.trim())) {
      return false
    }
    return true
  })
})

// 格式化厂商字段：去掉 "/NetApp" 这种重复部分
function formatManufacturer(manufacturer: string | undefined): string {
  if (!manufacturer) return ''
  if (manufacturer.includes('/')) {
    return manufacturer.split('/')[0]
  }
  return manufacturer
}

function getItemUnitPrice(item: any): number {
  return Number(item?.finalPrice ?? item?.suggestedPrice ?? 0) || 0
}

function getItemQuantity(item: any): number {
  const quantity = Number(item?.quantity)
  return Number.isFinite(quantity) && quantity > 0 ? quantity : 1
}

function getItemServicePeriod(item: any): number {
  const raw = item?.servicePeriod
  if (raw === null || raw === undefined || raw === '') return 1

  if (typeof raw === 'number') {
    return Number.isFinite(raw) && raw > 0 ? raw : 1
  }

  const normalized = String(raw).trim()
  if (!normalized) return 1

  const matched = normalized.match(/(\d+(?:\.\d+)?)/)
  if (!matched) return 1

  const period = Number(matched[1])
  return Number.isFinite(period) && period > 0 ? period : 1
}

function formatServicePeriodDisplay(item: any): string {
  const rawPeriod = item?.servicePeriod
  const normalizedPeriod = rawPeriod === null || rawPeriod === undefined ? '' : String(rawPeriod).trim()
  const unit = item?.servicePeriodUnit ? String(item.servicePeriodUnit).trim() : ''

  if (normalizedPeriod) {
    if (unit && normalizedPeriod.includes(unit)) return normalizedPeriod
    return `${normalizedPeriod}${unit}`
  }

  return `1${unit || ''}`
}

function getItemTotalPrice(item: any): number {
  return getItemUnitPrice(item) * getItemQuantity(item) * getItemServicePeriod(item)
}

// ========== Logo 上传功能 ==========

// 触发 Logo 上传
function triggerLogoUpload() {
  logoInputRef.value?.click()
}

// 处理 Logo 上传
function handleLogoUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    alert('请选择图片文件')
    return
  }
  
  // 验证文件大小（最大 2MB）
  if (file.size > 2 * 1024 * 1024) {
    alert('图片大小不能超过 2MB')
    return
  }
  
  // 读取图片并转为 Base64
  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    customLogoUrl.value = result
    // 保存到 localStorage 以便持久化（按用户隔离）
    localStorage.setItem(getStorageKeyPrefix() + 'quotation_custom_logo', result)
  }
  reader.readAsDataURL(file)
  
  // 清空 input 以便重复选择同一文件
  input.value = ''
}

// 初始化时从 localStorage 加载手动上传的 Logo（按用户隔离）
// 注意：个人设置中的公司 Logo 在 loadCompanyAndCustomers 中作为默认加载，
// 若用户在报价页手动上传过，localStorage 中的值优先
function loadCustomLogo() {
  const savedLogo = localStorage.getItem(getStorageKeyPrefix() + 'quotation_custom_logo')
  if (!savedLogo) return

  const normalizedSavedLogo = normalizeLogoSource(savedLogo)
  if (!normalizedSavedLogo) {
    localStorage.removeItem(getStorageKeyPrefix() + 'quotation_custom_logo')
    return
  }
  customLogoUrl.value = normalizedSavedLogo
}

// 使用 Canvas 绘制中文页脚（仅页码），避免 jsPDF 默认字体不支持中文导致乱码
function createFooterImageDataUrl(pageNum: number, totalPages: number): string {
  const canvas = document.createElement('canvas')
  const dpr = 2
  canvas.width = 800 * dpr
  canvas.height = 36 * dpr
  const ctx = canvas.getContext('2d')
  if (!ctx) return ''
  ctx.scale(dpr, dpr)
  ctx.fillStyle = '#ffffff'
  ctx.fillRect(0, 0, 800, 36)
  ctx.fillStyle = '#94a3b8'
  ctx.font = '12px "PingFang SC", "Microsoft YaHei", "Noto Sans SC", "Hiragino Sans GB", sans-serif'
  ctx.textAlign = 'center'
  ctx.fillText(`第 ${pageNum} 页 / 共 ${totalPages} 页`, 400, 22)
  return canvas.toDataURL('image/png', 1.0)
}

// 下载PDF - 使用 onclone 将克隆元素移至 body 根节点，彻底脱离页面布局链
async function downloadPDF() {
  if (!quotationDocRef.value || tableData.value.length === 0) {
    alert('没有可导出的数据')
    return
  }

  isGeneratingPDF.value = true
  const savedScrollX = window.scrollX
  const savedScrollY = window.scrollY

  // 等待虚拟化退化为全量渲染（isGeneratingPDF 让 qVisibleItems 返回 tableData.value）
  await nextTick()

  try {
    const html2canvas = (await import('html2canvas')).default
    const { default: jsPDF } = await import('jspdf')

    const element = quotationDocRef.value

    // ── A4 参数 ──
    const a4Width = 210   // mm
    const a4Height = 297  // mm
    const pageMargin = 10 // mm
    const imgWidthMm = a4Width - 2 * pageMargin

    // 渲染宽度：A4 at 96dpi ≈ 794px，给出最佳 A4 页面比例
    const renderWidth = 794

    // 重置滚动位置
    window.scrollTo(0, 0)

    // ── html2canvas 渲染：通过 onclone 在克隆文档中重构布局 ──
    // onclone 在渲染前执行，将报价单元素移至 body 根节点并重设样式，
    // 完全消除原页面 flex/overflow/vh 等布局约束的影响。
    // 不传 width/height —— 让 html2canvas 从 onclone 修改后的元素自动计算。
    const fullCanvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
      windowWidth: renderWidth,
      windowHeight: 50000,  // 足够大的虚拟视口，避免任何 vh 单位截断
      allowTaint: true,
      scrollX: 0,
      scrollY: 0,
      onclone: (clonedDoc: Document, clonedEl: HTMLElement) => {
        // 1. 从原始父节点链中脱离
        clonedEl.remove()

        // 2. 清空 body，消除所有页面布局上下文
        clonedDoc.body.innerHTML = ''
        clonedDoc.body.style.cssText = 'margin:0;padding:0;overflow:visible;background:white;'
        clonedDoc.documentElement.style.overflow = 'visible'

        // 3. 将报价单元素直接挂载到 body
        clonedDoc.body.appendChild(clonedEl)

        // 4. 重设元素样式：固定宽度、自动高度、无溢出限制
        clonedEl.style.cssText = `
          width: ${renderWidth}px;
          max-width: none;
          min-height: 0;
          height: auto;
          overflow: visible;
          display: block;
          padding: 40px 50px;
          background: white;
          color: #0f172a;
          box-shadow: none;
          border-radius: 0;
          position: static;
        `

        // 5. 修复 terms-section：去掉 margin-top: auto，用固定间距
        const terms = clonedEl.querySelector('.terms-section') as HTMLElement
        if (terms) {
          terms.style.marginTop = '2rem'
        }

        // 6. 隐藏不需要出现在 PDF 中的元素
        clonedEl.querySelectorAll('.logo-upload-hint, .doc-footer, .doc-decoration').forEach(
          el => (el as HTMLElement).style.display = 'none'
        )

        // 7. 禁用所有动画/过渡
        const resetStyle = clonedDoc.createElement('style')
        resetStyle.textContent = '*, *::before, *::after { animation: none !important; transition: none !important; }'
        clonedDoc.head.appendChild(resetStyle)
      }
    })

    console.log(`[PDF] 画布尺寸: ${fullCanvas.width} x ${fullCanvas.height}px`)

    // ── 智能分页：扫描空白行避免文字被截断 ──
    const pxToMm = imgWidthMm / fullCanvas.width
    const pageContentHeightMm = a4Height - 2 * pageMargin
    const pageHeightPx = pageContentHeightMm / pxToMm

    // 在每个分页点向上搜索空白像素行（文字行间隙），避免在文字中间切断
    const SEARCH_RANGE = 200   // 向上搜索范围（画布像素），约覆盖数行文字
    const PADDING_X = 120      // 跳过左右边距区域（画布像素）
    const SAMPLE_STEP = 6      // 水平采样间距，兼顾速度和精度
    const WHITE_THRESHOLD = 245 // 接近白色的阈值（0-255）

    const safePageRanges: Array<{start: number, end: number}> = []
    let currentY = 0
    const fullCtx = fullCanvas.getContext('2d')

    while (currentY < fullCanvas.height) {
      const idealEnd = Math.round(currentY + pageHeightPx)

      // 最后一页：直接到底
      if (idealEnd >= fullCanvas.height) {
        safePageRanges.push({ start: currentY, end: fullCanvas.height })
        break
      }

      let safeEnd = idealEnd

      if (fullCtx) {
        // 在 idealEnd 上方 SEARCH_RANGE 范围内搜索空白行
        const scanTop = Math.max(Math.round(currentY + 100), idealEnd - SEARCH_RANGE)
        const scanHeight = idealEnd - scanTop
        const scanLeft = Math.min(PADDING_X, Math.round(fullCanvas.width * 0.1))
        const scanWidth = Math.max(1, fullCanvas.width - 2 * scanLeft)

        if (scanHeight > 0) {
          const imageData = fullCtx.getImageData(scanLeft, scanTop, scanWidth, scanHeight)
          const data = imageData.data

          // 从底部向上扫描，找第一条全白行（文字行间的空隙）
          for (let row = scanHeight - 1; row >= 0; row--) {
            let isBlankRow = true
            const rowOffset = row * scanWidth * 4

            for (let x = 0; x < scanWidth * 4; x += SAMPLE_STEP * 4) {
              const idx = rowOffset + x
              if (data[idx] < WHITE_THRESHOLD || data[idx + 1] < WHITE_THRESHOLD || data[idx + 2] < WHITE_THRESHOLD) {
                isBlankRow = false
                break
              }
            }

            if (isBlankRow) {
              safeEnd = scanTop + row
              break
            }
          }
        }
      }

      safePageRanges.push({ start: currentY, end: safeEnd })
      currentY = safeEnd
    }

    const totalPages = safePageRanges.length
    console.log(`[PDF] 每页理想高度: ${Math.round(pageHeightPx)}px, 智能分页后总页数: ${totalPages}`)

    if (totalPages > 50) {
      alert(`内容过长，预计需要 ${totalPages} 页，建议使用 Excel 导出`)
      isGeneratingPDF.value = false
      return
    }

    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })

    for (let pageIdx = 0; pageIdx < totalPages; pageIdx++) {
      const { start: startY, end: endY } = safePageRanges[pageIdx]
      const sliceHeight = endY - startY

      if (sliceHeight <= 0) continue

      const pageCanvas = document.createElement('canvas')
      pageCanvas.width = fullCanvas.width
      pageCanvas.height = Math.round(sliceHeight)
      const ctx = pageCanvas.getContext('2d')
      if (ctx) {
        ctx.fillStyle = '#ffffff'
        ctx.fillRect(0, 0, pageCanvas.width, pageCanvas.height)
        ctx.drawImage(
          fullCanvas,
          0, Math.round(startY),
          fullCanvas.width, Math.round(sliceHeight),
          0, 0,
          fullCanvas.width, Math.round(sliceHeight)
        )
      }

      if (pageIdx > 0) doc.addPage()
      // 内容在页面顶部对齐，底部可能留白（因为安全分页点比理想高度短）
      const imgHeightMm = (pageCanvas.height / pageCanvas.width) * imgWidthMm
      doc.addImage(
        pageCanvas.toDataURL('image/png', 1.0),
        'PNG',
        pageMargin,
        pageMargin,
        imgWidthMm,
        imgHeightMm
      )

      // 添加页脚（页码）
      const footerImg = createFooterImageDataUrl(pageIdx + 1, totalPages)
      if (footerImg) {
        const footerWidthMm = 80
        const footerHeightMm = 4
        doc.addImage(
          footerImg,
          'PNG',
          (a4Width - footerWidthMm) / 2,
          a4Height - pageMargin + 1,
          footerWidthMm,
          footerHeightMm
        )
      }
    }

    const fileName = `报价单_${quoteNumber.value}_${new Date().toISOString().slice(0, 10)}.pdf`
    doc.save(fileName)
  } catch (error) {
    console.error('PDF 生成失败:', error)
    alert('PDF 生成失败: ' + (error as Error).message)
  } finally {
    isGeneratingPDF.value = false
    window.scrollTo(savedScrollX, savedScrollY)
  }
}

// 打开预览弹窗
function openPreviewDialog() {
  if (tableData.value.length === 0) {
    alert('没有可导出的数据')
    return
  }
  showPreviewDialog.value = true
}

// 关闭预览弹窗
function closePreviewDialog() {
  showPreviewDialog.value = false
}

// 导出 Excel（生成两个文件：原始格式报价表 + 标准格式表格）
async function exportQuotationExcel() {
  if (tableData.value.length === 0) {
    alert('没有可导出的数据')
    return
  }

  isExporting.value = true

  try {
    // 动态导入 ExcelJS
    const ExcelJS = (await import('exceljs')).default

    // 尝试获取原始Excel文件数据
    const originalExcelBase64 = getFlowData<string>(FLOW_DATA_KEYS.ORIGINAL_EXCEL_FILE)
    const selectedSheetName = getFlowData<string>(FLOW_DATA_KEYS.SELECTED_SHEET_NAME)
    const selectedSheetNames = getFlowData<string[]>(FLOW_DATA_KEYS.SELECTED_SHEET_NAMES) || (selectedSheetName ? [selectedSheetName] : [])
    const originalFileName = getFlowData<string>(FLOW_DATA_KEYS.ORIGINAL_FILE_NAME) || ''
    console.log('[Export] originalExcelBase64:', originalExcelBase64 ? `存在(${originalExcelBase64.length}字符)` : '不存在')
    console.log('[Export] selectedSheetName:', selectedSheetName)
    console.log('[Export] selectedSheetNames:', selectedSheetNames)
    console.log('[Export] originalFileName:', originalFileName)
    console.log('[Export] tableData行数:', tableData.value.length)
    console.log('[Export] originalTableData:', originalTableData.value ? `headers=${originalTableData.value.headers?.length}, data=${originalTableData.value.data?.length}` : '不存在')

    // 辅助函数：判断是否为价格列
    const isPriceColumn = (header: string) => {
      return header.includes('维保单价') || header.includes('单价') ||
             header.includes('价格') || header.includes('总价')
    }

    // 辅助函数：将HTML转换为纯文本
    // 使用统一的 HTML -> 纯文本转换，保留段前空格
    const htmlToPlainText = (html: string) => {
      return convertHtmlToPlainText(html)
    }

    // 辅助函数：获取后台配置的服务条款内容
    const getServiceTermsContent = (): string | null => {
      if (!serviceTerms.value || serviceTerms.value === 'none') {
        return null
      }
      const selectedTerm = serviceTermsList.value.find(t => String(t.id) === String(serviceTerms.value))
      if (!selectedTerm || !selectedTerm.content) {
        return null
      }
      return htmlToPlainText(selectedTerm.content)
    }

    // 辅助函数：添加服务条款到工作表
    const addServiceTermsToWorksheet = (worksheet: any, startRow: number, colCount: number) => {
      const termsContent = getServiceTermsContent()
      if (!termsContent) return startRow

      const mergeCols = Math.max(colCount, 6)

      // 空一行后添加"条款与条件"标题行（加粗，与 PDF 格式一致）
      const titleRow = startRow + 2
      worksheet.mergeCells(titleRow, 1, titleRow, mergeCols)
      const titleCell = worksheet.getCell(titleRow, 1)
      titleCell.value = '条款与条件'
      titleCell.font = { size: 11, bold: true }
      titleCell.alignment = { vertical: 'middle', horizontal: 'left' }
      worksheet.getRow(titleRow).height = 22

      // 过滤掉编辑器产生的孤立编号行（如首行的 "1."）
      const lines = termsContent.split('\n')
      const filteredLines = lines.filter((line, idx) => {
        if (/^\d+\.\s*$/.test(line) && idx + 1 < lines.length && lines[idx + 1].startsWith(line.trim())) {
          return false
        }
        return true
      })
      const cleanedContent = filteredLines.join('\n')

      // 条款内容行（合并2行 × mergeCols列，确保所有条款内容可见）
      const termsRow = titleRow + 1
      const termsRowEnd = termsRow + 1
      worksheet.mergeCells(termsRow, 1, termsRowEnd, mergeCols)

      const cell = worksheet.getCell(termsRow, 1)
      cell.value = cleanedContent
      cell.alignment = { vertical: 'top', horizontal: 'left', wrapText: true }
      cell.font = { size: 10 }

      // 每行固定 230 磅行高（ExcelJS 行高单位即为磅）
      worksheet.getRow(termsRow).height = 230
      worksheet.getRow(termsRowEnd).height = 230

      return termsRowEnd
    }

    // 辅助函数：下载文件
    const downloadFile = (buffer: ArrayBuffer, fileName: string) => {
      const blob = new Blob([buffer], {
        type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
      })
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = fileName
      link.click()
      window.URL.revokeObjectURL(url)
    }

    // 获取价格数据映射（按行索引）—— 直接从 tableData 取价，避免间接匹配导致 0 值
    // 根据布局选择确定价格乘数
    let exportPriceMultiplier = 1
    if (priceLayout.value === 'layout3') {
      exportPriceMultiplier = 1.06
    } else if (priceLayout.value === 'layout4') {
      exportPriceMultiplier = 1.13
    }

    const buildPriceDataMap = (items: any[]) => {
      const map = new Map<number, number>()
      items.forEach((item, index) => {
        const basePrice = item.finalPrice || item.suggestedPrice || 0
        if (basePrice > 0) {
          const adjustedPrice = Math.round(basePrice * exportPriceMultiplier * 100) / 100
          map.set(index, adjustedPrice)
        }
      })
      return map
    }

    const priceDataMap = buildPriceDataMap(tableData.value)
    const primarySheetItems = selectedSheetName
      ? tableData.value.filter((item: any) => item.sheetName === selectedSheetName)
      : tableData.value
    const primaryPriceDataMap = buildPriceDataMap(primarySheetItems.length > 0 ? primarySheetItems : tableData.value)
    console.log('[Export] priceDataMap 共', priceDataMap.size, '条, tableData 共', tableData.value.length, '条')

    // ===== 联想框架价格 =====
    // 只要 tableData 里任意一行存在 lenovo_unit_price>0，就在最末加"联想框架单价"列；
    // 没跑过联想报价时，行里没有这个字段，导出和现有完全一致，不追加。
    const LENOVO_HEADER = '联想框架单价(含税13%)'
    const buildLenovoPriceMap = (items: any[]) => {
      const map = new Map<number, number>()
      items.forEach((item, index) => {
        const p = Number(item?.lenovo_unit_price)
        if (Number.isFinite(p) && p > 0) {
          // 联想价格表里本就含税 13%，不再应用 exportPriceMultiplier
          map.set(index, Math.round(p * 100) / 100)
        }
      })
      return map
    }
    const lenovoPriceDataMap = buildLenovoPriceMap(tableData.value)
    const primaryLenovoPriceDataMap = buildLenovoPriceMap(
      primarySheetItems.length > 0 ? primarySheetItems : tableData.value
    )
    const hasLenovoData = lenovoPriceDataMap.size > 0
    console.log('[Export] hasLenovoData=', hasLenovoData, ' 联想价数=', lenovoPriceDataMap.size)

    /** 给定输出表的一行 / 行号 / sheetName，找它在 tableData 中对应的联想单价 */
    const matchLenovoPrice = (row: any, rowIndex: number, sheetName?: string): number | null => {
      const matched = tableData.value.find((item: any, itemIndex: number) => {
        if (sheetName && item.sheetName && item.sheetName !== sheetName) return false
        if (Number.isFinite(Number(item.sourceRowIndex)) && Number(item.sourceRowIndex) === rowIndex) return true
        if (!item.sheetName && itemIndex === rowIndex) return true
        return false
      })
      let p = Number(matched?.lenovo_unit_price)
      if (!Number.isFinite(p) || p <= 0) {
        const modelValue = String(row?.['设备/软件型号'] || row?.['设备型号'] || '').trim().toUpperCase()
        if (modelValue) {
          const byModel = tableData.value.find((item: any) => {
            if (sheetName && item.sheetName && item.sheetName !== sheetName) return false
            return [item.model, item.matchedModel, item.originalModel]
              .filter(Boolean)
              .some((key: string) => String(key).trim().toUpperCase() === modelValue)
          })
          p = Number(byModel?.lenovo_unit_price)
        }
      }
      return Number.isFinite(p) && p > 0 ? Math.round(p * 100) / 100 : null
    }

    // ===== 文件1：保留原始格式的报价表（仅在空白列添加价格） =====
    // 使用 JSZip 直接操作 xlsx 内部 XML，避免 ExcelJS load→save 丢失主题色/样式
    let hasOriginalFile = false
    if (originalExcelBase64 && selectedSheetName) {
      try {
        console.log('[Export] 生成文件1：原始格式报价表（JSZip 方式保留样式）')

        const binaryString = atob(originalExcelBase64)
        const bytes = new Uint8Array(binaryString.length)
        for (let i = 0; i < binaryString.length; i++) {
          bytes[i] = binaryString.charCodeAt(i)
        }

        const JSZip = (await import('jszip')).default
        const zip = await JSZip.loadAsync(bytes.buffer)

        // 读取 workbook.xml 找到目标 sheet 的 rId
        const workbookXml = await zip.file('xl/workbook.xml')?.async('string')
        if (!workbookXml) throw new Error('无法读取 workbook.xml')

        // 解析所有 sheet 名称和 rId
        const sheetMatches = [...workbookXml.matchAll(/<sheet\s+[^>]*name="([^"]*)"[^>]*r:id="([^"]*)"[^>]*\/?>/g)]
        let targetRId = ''
        // 按名称匹配 → 模糊匹配 → 第一个
        for (const m of sheetMatches) {
          if (m[1] === selectedSheetName) { targetRId = m[2]; break }
        }
        if (!targetRId) {
          for (const m of sheetMatches) {
            if (m[1].includes(selectedSheetName) || selectedSheetName.includes(m[1]) ||
                m[1].replace(/\s/g, '') === selectedSheetName.replace(/\s/g, '')) {
              targetRId = m[2]; break
            }
          }
        }
        if (!targetRId && sheetMatches.length > 0) targetRId = sheetMatches[0][2]

        // 通过 rId 在 workbook.xml.rels 中找到 sheet 文件路径
        const relsXml = await zip.file('xl/_rels/workbook.xml.rels')?.async('string') || ''
        const relMatch = relsXml.match(new RegExp(`<Relationship[^>]*Id="${targetRId}"[^>]*Target="([^"]*)"[^>]*/>`))
        let sheetPath = relMatch ? `xl/${relMatch[1]}` : 'xl/worksheets/sheet1.xml'
        // 修正相对路径
        sheetPath = sheetPath.replace('xl/xl/', 'xl/')

        const sheetXml = await zip.file(sheetPath)?.async('string')
        if (!sheetXml) throw new Error(`无法读取工作表: ${sheetPath}`)

        console.log('[Export] 目标工作表路径:', sheetPath)

        // ---- 解析 sheet XML ----
        const parser = new DOMParser()
        const doc = parser.parseFromString(sheetXml, 'application/xml')
        const nsResolver = doc.documentElement.namespaceURI || 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'

        const sheetDataEl = doc.getElementsByTagNameNS(nsResolver, 'sheetData')[0]
        if (!sheetDataEl) throw new Error('未找到 sheetData')

        const rows = sheetDataEl.getElementsByTagNameNS(nsResolver, 'row')

        // 辅助函数：列号转字母（1→A, 2→B, 27→AA）
        const colToLetter = (col: number): string => {
          let s = ''
          while (col > 0) {
            col--
            s = String.fromCharCode(65 + (col % 26)) + s
            col = Math.floor(col / 26)
          }
          return s
        }

        // 辅助函数：从单元格引用提取行号和列号
        const parseRef = (ref: string) => {
          const match = ref.match(/^([A-Z]+)(\d+)$/)
          if (!match) return { col: 0, row: 0 }
          let col = 0
          for (const ch of match[1]) col = col * 26 + (ch.charCodeAt(0) - 64)
          return { col, row: parseInt(match[2]) }
        }

        // 找最大列号
        let maxCol = 0
        for (let i = 0; i < rows.length; i++) {
          const cells = rows[i].getElementsByTagNameNS(nsResolver, 'c')
          for (let j = 0; j < cells.length; j++) {
            const ref = cells[j].getAttribute('r') || ''
            const { col } = parseRef(ref)
            if (col > maxCol) maxCol = col
          }
        }
        const priceColIndex = maxCol + 1
        const priceColLetter = colToLetter(priceColIndex)
        // 联想框架单价列（仅在 hasLenovoData 时使用）
        const lenovoColIndex = hasLenovoData ? priceColIndex + 1 : priceColIndex
        const lenovoColLetter = hasLenovoData ? colToLetter(lenovoColIndex) : priceColLetter
        // 终列：表头条款、dimension、cols 都按这个最右列计算
        const lastColIndex = hasLenovoData ? lenovoColIndex : priceColIndex
        const lastColLetter = hasLenovoData ? lenovoColLetter : priceColLetter

        const getSheetWorksheetSelection = (sheetName: string) => {
          return originalSheetTables.value.find((sheet) => sheet.sheetName === sheetName)?.worksheetSelection || null
        }

        // ---- 智能检测表头行位置 ----
        const knownHeaders = originalTableData.value?.headers || []
        const significantHeaders = knownHeaders
          .filter((h: string) => h && !h.startsWith('列') && h !== '序号')
          .slice(0, 5)
          .map((h: string) => h.replace(/[\s*]/g, ''))
        const commonDeviceKeywords = ['产品大类', '设备类型', '设备品牌', '设备型号', '序列号', '设备地点', 'SLA', '服务时长', '序号']

        // 读取 sharedStrings 用于获取单元格文本值
        let sharedStrings: string[] = []
        const ssXml = await zip.file('xl/sharedStrings.xml')?.async('string')
        if (ssXml) {
          const ssDoc = parser.parseFromString(ssXml, 'application/xml')
          const ssNs = ssDoc.documentElement.namespaceURI || nsResolver
          const siEls = ssDoc.getElementsByTagNameNS(ssNs, 'si')
          for (let i = 0; i < siEls.length; i++) {
            // 获取 si 下所有 t 元素的文本并拼接
            const tEls = siEls[i].getElementsByTagNameNS(ssNs, 't')
            let text = ''
            for (let j = 0; j < tEls.length; j++) text += tEls[j].textContent || ''
            sharedStrings.push(text)
          }
        }

        // 获取行中所有单元格的文本值
        const getRowTexts = (rowEl: Element): string[] => {
          const texts: string[] = []
          const cells = rowEl.getElementsByTagNameNS(nsResolver, 'c')
          for (let j = 0; j < cells.length; j++) {
            const vEl = cells[j].getElementsByTagNameNS(nsResolver, 'v')[0]
            const cellType = cells[j].getAttribute('t')
            if (vEl && vEl.textContent) {
              if (cellType === 's') {
                const idx = parseInt(vEl.textContent)
                texts.push((sharedStrings[idx] || '').replace(/[\s*\n]/g, ''))
              } else {
                texts.push(vEl.textContent.replace(/[\s*\n]/g, ''))
              }
            }
          }
          return texts
        }

        const primarySheetSelection = selectedSheetName ? getSheetWorksheetSelection(selectedSheetName) : null
        let headerRowNum = primarySheetSelection?.headerRowNumber || 1
        if (primarySheetSelection) {
          console.log('[Export] 使用手动选区表头行:', headerRowNum, 'sheet:', selectedSheetName)
        } else {
          for (let i = 0; i < Math.min(rows.length, 30); i++) {
            const rowNum = parseInt(rows[i].getAttribute('r') || String(i + 1))
            const texts = getRowTexts(rows[i])
            if (texts.length < 3) continue

            if (significantHeaders.length >= 3) {
              let matchCount = 0
              for (const sh of significantHeaders) {
                if (texts.some(v => v.includes(sh) || sh.includes(v))) matchCount++
              }
              if (matchCount >= Math.min(3, significantHeaders.length)) {
                headerRowNum = rowNum
                console.log('[Export] 策略1: 检测到表头行位于第', rowNum, '行')
                break
              }
            }

            let kwCount = 0
            for (const kw of commonDeviceKeywords) {
              if (texts.some(v => v.includes(kw))) kwCount++
            }
            if (kwCount >= 3) {
              headerRowNum = rowNum
              console.log('[Export] 策略2: 检测到表头行位于第', rowNum, '行')
              break
            }
          }
        }
        console.log('[Export] 使用表头行:', headerRowNum)

        // ---- 添加 sharedStrings 条目（"维保单价" + 可选"联想框架单价"） ----
        let ssDoc2: Document | null = null
        let priceHeaderSsIndex = -1
        let lenovoHeaderSsIndex = -1
        if (ssXml) {
          ssDoc2 = parser.parseFromString(ssXml, 'application/xml')
          const ssNs2 = ssDoc2.documentElement.namespaceURI || nsResolver
          const siEls2 = ssDoc2.getElementsByTagNameNS(ssNs2, 'si')
          priceHeaderSsIndex = siEls2.length

          const appendSharedString = (text: string) => {
            const newSi = ssDoc2!.createElementNS(ssNs2, 'si')
            const newT = ssDoc2!.createElementNS(ssNs2, 't')
            newT.textContent = text
            newSi.appendChild(newT)
            ssDoc2!.documentElement.appendChild(newSi)
          }
          appendSharedString('维保单价')
          let addedCount = 1
          if (hasLenovoData) {
            lenovoHeaderSsIndex = priceHeaderSsIndex + 1
            appendSharedString(LENOVO_HEADER)
            addedCount = 2
          }

          // 更新 count 和 uniqueCount 属性
          const sstEl = ssDoc2.documentElement
          const oldCount = parseInt(sstEl.getAttribute('count') || '0')
          const oldUnique = parseInt(sstEl.getAttribute('uniqueCount') || '0')
          sstEl.setAttribute('count', String(oldCount + addedCount))
          sstEl.setAttribute('uniqueCount', String(oldUnique + addedCount))
        }

        // ---- 构建型号→价格查找表 ----
        // 注意：key 的归一化必须与 getRowTexts 一致（去除所有空白和星号）
        const normalizeForMatch = (s: string) => String(s).replace(/[\s*\n]/g, '').toUpperCase()
        const modelPriceMap = new Map<string, number>()
        const lenovoModelPriceMap = new Map<string, number>()
        tableData.value.forEach((item: any) => {
          const basePrice = item.finalPrice || item.suggestedPrice || 0
          if (basePrice > 0) {
            const adjustedPrice = Math.round(basePrice * exportPriceMultiplier * 100) / 100
            const keys = [item.model, item.matchedModel, item.originalModel].filter(Boolean)
            keys.forEach((k: string) => {
              const normalized = normalizeForMatch(k)
              if (normalized && !modelPriceMap.has(normalized)) {
                modelPriceMap.set(normalized, adjustedPrice)
              }
            })
          }
          // 联想价（不应用 exportPriceMultiplier，价格表里本就含税 13%）
          const lp = Number(item.lenovo_unit_price)
          if (Number.isFinite(lp) && lp > 0) {
            const rounded = Math.round(lp * 100) / 100
            const keys = [item.model, item.matchedModel, item.originalModel].filter(Boolean)
            keys.forEach((k: string) => {
              const normalized = normalizeForMatch(k)
              if (normalized && !lenovoModelPriceMap.has(normalized)) {
                lenovoModelPriceMap.set(normalized, rounded)
              }
            })
          }
        })

        // ---- 在 sheet XML 中插入价格列单元格 ----
        const dataStartRowNum = headerRowNum + 1
        // 统计实际有数据内容的行数（排除表头后的空行、条款行等）
        let actualDataRowCount = 0
        const dataRowIndices: number[] = []  // 存储数据行在 rows 数组中的索引
        const worksheetRowToSeqIndex = new Map<number, number>()

        if (primarySheetSelection?.dataRowNumbers?.length) {
          primarySheetSelection.dataRowNumbers.forEach((rowNumber, seqIdx) => {
            worksheetRowToSeqIndex.set(rowNumber, seqIdx)
          })
          for (let i = 0; i < rows.length; i++) {
            const rn = parseInt(rows[i].getAttribute('r') || '0')
            if (worksheetRowToSeqIndex.has(rn)) {
              actualDataRowCount++
              dataRowIndices.push(i)
            }
          }
        } else {
          for (let i = 0; i < rows.length; i++) {
            const rn = parseInt(rows[i].getAttribute('r') || '0')
            if (rn >= dataStartRowNum) {
              const texts = getRowTexts(rows[i])
              // 至少有2个非空单元格内容才算数据行
              if (texts.filter(t => t.length > 0).length >= 2) {
                actualDataRowCount++
                dataRowIndices.push(i)
              }
            }
          }
        }
        const expectedPrimaryCount = selectedSheetName
          ? tableData.value.filter((item: any) => item.sheetName === selectedSheetName).length || tableData.value.length
          : tableData.value.length
        const rowCountMatch = actualDataRowCount === expectedPrimaryCount
        console.log('[Export] 实际数据行:', actualDataRowCount, ', tableData 行:', tableData.value.length, ', 行数一致:', rowCountMatch)

        // 查找表头行样式 ID 用于价格表头单元格
        let headerStyleId = ''
        for (let i = 0; i < rows.length; i++) {
          const rn = parseInt(rows[i].getAttribute('r') || '0')
          if (rn === headerRowNum) {
            const cells = rows[i].getElementsByTagNameNS(nsResolver, 'c')
            if (cells.length > 0) {
              headerStyleId = cells[0].getAttribute('s') || ''
            }
            break
          }
        }

        // 构建数据行的顺序索引映射（rows 数组 index → tableData 顺序 index）
        const rowIndexToSeqIndex = new Map<number, number>()
        dataRowIndices.forEach((rowsIdx, seqIdx) => {
          rowIndexToSeqIndex.set(rowsIdx, seqIdx)
        })

        for (let i = 0; i < rows.length; i++) {
          const rowNum = parseInt(rows[i].getAttribute('r') || '0')

          // ---- 维保单价单元格 ----
          const newCell = doc.createElementNS(nsResolver, 'c')
          newCell.setAttribute('r', `${priceColLetter}${rowNum}`)

          if (rowNum === headerRowNum) {
            // 表头单元格 — 引用 sharedStrings 中的"维保单价"
            if (priceHeaderSsIndex >= 0) {
              newCell.setAttribute('t', 's')
              if (headerStyleId) newCell.setAttribute('s', headerStyleId)
              const vEl = doc.createElementNS(nsResolver, 'v')
              vEl.textContent = String(priceHeaderSsIndex)
              newCell.appendChild(vEl)
            }
          } else if (rowNum >= dataStartRowNum) {
            let price: number | undefined

            // 优先使用顺序索引映射（按数据行顺序对应 tableData 顺序）
            const seqIndex = primarySheetSelection?.dataRowNumbers?.length
              ? worksheetRowToSeqIndex.get(rowNum)
              : rowIndexToSeqIndex.get(i)
            if (rowCountMatch && seqIndex !== undefined) {
              price = primaryPriceDataMap.get(seqIndex)
            }
            // 回退：通过型号名称匹配
            if (price === undefined) {
              const texts = getRowTexts(rows[i])
              for (const t of texts) {
                const normalized = normalizeForMatch(t)
                if (normalized && modelPriceMap.has(normalized)) {
                  price = modelPriceMap.get(normalized)
                  break
                }
              }
            }

            if (price !== undefined && price > 0) {
              const vEl = doc.createElementNS(nsResolver, 'v')
              vEl.textContent = String(price)
              newCell.appendChild(vEl)
              // 复用同行其他单元格的样式
              const cells = rows[i].getElementsByTagNameNS(nsResolver, 'c')
              if (cells.length > 0) {
                const sAttr = cells[0].getAttribute('s')
                if (sAttr) newCell.setAttribute('s', sAttr)
              }
            }
          }

          rows[i].appendChild(newCell)

          // ---- 联想框架单价单元格（仅在 hasLenovoData 时追加）----
          if (hasLenovoData) {
            const lenovoCell = doc.createElementNS(nsResolver, 'c')
            lenovoCell.setAttribute('r', `${lenovoColLetter}${rowNum}`)
            if (rowNum === headerRowNum) {
              if (lenovoHeaderSsIndex >= 0) {
                lenovoCell.setAttribute('t', 's')
                if (headerStyleId) lenovoCell.setAttribute('s', headerStyleId)
                const vEl = doc.createElementNS(nsResolver, 'v')
                vEl.textContent = String(lenovoHeaderSsIndex)
                lenovoCell.appendChild(vEl)
              }
            } else if (rowNum >= dataStartRowNum) {
              let lp: number | undefined
              const seqIndex = primarySheetSelection?.dataRowNumbers?.length
                ? worksheetRowToSeqIndex.get(rowNum)
                : rowIndexToSeqIndex.get(i)
              if (rowCountMatch && seqIndex !== undefined) {
                lp = primaryLenovoPriceDataMap.get(seqIndex)
              }
              if (lp === undefined) {
                const texts = getRowTexts(rows[i])
                for (const t of texts) {
                  const normalized = normalizeForMatch(t)
                  if (normalized && lenovoModelPriceMap.has(normalized)) {
                    lp = lenovoModelPriceMap.get(normalized)
                    break
                  }
                }
              }
              if (lp !== undefined && lp > 0) {
                const vEl = doc.createElementNS(nsResolver, 'v')
                vEl.textContent = String(lp)
                lenovoCell.appendChild(vEl)
                const cells = rows[i].getElementsByTagNameNS(nsResolver, 'c')
                if (cells.length > 0) {
                  const sAttr = cells[0].getAttribute('s')
                  if (sAttr) lenovoCell.setAttribute('s', sAttr)
                }
              }
            }
            rows[i].appendChild(lenovoCell)
          }
        }

        // 更新 dimension（如果存在）：终列改为最右新列
        const dimEl = doc.getElementsByTagNameNS(nsResolver, 'dimension')[0]
        if (dimEl) {
          const oldRef = dimEl.getAttribute('ref') || ''
          const updatedRef = oldRef.replace(/([A-Z]+)(\d+)$/, `${lastColLetter}$2`)
          dimEl.setAttribute('ref', updatedRef)
        }

        // 更新列宽信息：维保单价 + 可选 联想框架单价
        let colsEl = doc.getElementsByTagNameNS(nsResolver, 'cols')[0]
        if (colsEl) {
          const appendColWidth = (colIdx: number, width: string) => {
            const colEl = doc.createElementNS(nsResolver, 'col')
            colEl.setAttribute('min', String(colIdx))
            colEl.setAttribute('max', String(colIdx))
            colEl.setAttribute('width', width)
            colEl.setAttribute('customWidth', '1')
            colsEl.appendChild(colEl)
          }
          appendColWidth(priceColIndex, '15')
          if (hasLenovoData) appendColWidth(lenovoColIndex, '20')
        }

        // ---- 在 styles.xml 中添加 wrapText + bold 样式，供条款单元格使用 ----
        let wrapTextStyleIndex = ''
        let boldStyleIndex = ''
        const stylesXml = await zip.file('xl/styles.xml')?.async('string')
        let stylesDoc: Document | null = null
        if (stylesXml) {
          stylesDoc = parser.parseFromString(stylesXml, 'application/xml')
          const stylesNs = stylesDoc.documentElement.namespaceURI || nsResolver

          const cellXfsEl = stylesDoc.getElementsByTagNameNS(stylesNs, 'cellXfs')[0]
          if (cellXfsEl) {
            const xfEls = cellXfsEl.getElementsByTagNameNS(stylesNs, 'xf')

            // 添加加粗+左对齐样式（用于标题行）
            // 先找到一个有字体的 xf 作为基础，或使用 fontId=0
            const boldXf = stylesDoc.createElementNS(stylesNs, 'xf')
            boldXf.setAttribute('numFmtId', '0')
            boldXf.setAttribute('fontId', '0')
            boldXf.setAttribute('fillId', '0')
            boldXf.setAttribute('borderId', '0')
            boldXf.setAttribute('xfId', '0')
            boldXf.setAttribute('applyAlignment', '1')
            const boldAlign = stylesDoc.createElementNS(stylesNs, 'alignment')
            boldAlign.setAttribute('vertical', 'center')
            boldAlign.setAttribute('horizontal', 'left')
            boldXf.appendChild(boldAlign)
            cellXfsEl.appendChild(boldXf)
            boldStyleIndex = String(xfEls.length - 1)

            // 添加 wrapText+顶部对齐样式（用于条款内容）
            const wrapXf = stylesDoc.createElementNS(stylesNs, 'xf')
            wrapXf.setAttribute('numFmtId', '0')
            wrapXf.setAttribute('fontId', '0')
            wrapXf.setAttribute('fillId', '0')
            wrapXf.setAttribute('borderId', '0')
            wrapXf.setAttribute('xfId', '0')
            wrapXf.setAttribute('applyAlignment', '1')
            const wrapAlign = stylesDoc.createElementNS(stylesNs, 'alignment')
            wrapAlign.setAttribute('wrapText', '1')
            wrapAlign.setAttribute('vertical', 'top')
            wrapAlign.setAttribute('horizontal', 'left')
            wrapXf.appendChild(wrapAlign)
            cellXfsEl.appendChild(wrapXf)
            wrapTextStyleIndex = String(xfEls.length - 1)

            // 更新 cellXfs count
            const oldXfCount = parseInt(cellXfsEl.getAttribute('count') || '0')
            cellXfsEl.setAttribute('count', String(oldXfCount + 2))
          }
        }

        // ---- 添加服务条款（在数据行之后） ----
        const termsContent = getServiceTermsContent()
        if (termsContent) {
          const lastDataRowNum = dataStartRowNum + tableData.value.length - 1
          const titleRowNum = lastDataRowNum + 3  // 空一行
          const termsRowNum = titleRowNum + 1
          const termsRowEndNum = termsRowNum + 1
          const mergeCols = Math.max(lastColIndex, 6)

          // 添加"条款与条件"和条款内容到 sharedStrings
          let titleSsIndex = -1
          let contentSsIndex = -1

          // 过滤掉编辑器产生的孤立编号行
          const lines = termsContent.split('\n')
          const filteredLines = lines.filter((line: string, idx: number) => {
            if (/^\d+\.\s*$/.test(line) && idx + 1 < lines.length && lines[idx + 1].startsWith(line.trim())) {
              return false
            }
            return true
          })
          const cleanedContent = filteredLines.join('\n')

          if (ssDoc2) {
            const ssNs2 = ssDoc2.documentElement.namespaceURI || nsResolver
            const siEls = ssDoc2.getElementsByTagNameNS(ssNs2, 'si')

            // "条款与条件" 标题
            titleSsIndex = siEls.length
            const titleSi = ssDoc2.createElementNS(ssNs2, 'si')
            const titleT = ssDoc2.createElementNS(ssNs2, 't')
            titleT.textContent = '条款与条件'
            titleSi.appendChild(titleT)
            ssDoc2.documentElement.appendChild(titleSi)

            // 条款内容（siEls 是 live NodeList，appendChild 后 length 已自动 +1）
            contentSsIndex = siEls.length
            const contentSi = ssDoc2.createElementNS(ssNs2, 'si')
            const contentT = ssDoc2.createElementNS(ssNs2, 't')
            contentT.textContent = cleanedContent
            contentSi.appendChild(contentT)
            ssDoc2.documentElement.appendChild(contentSi)

            // 更新 count/uniqueCount
            const sstEl = ssDoc2.documentElement
            const oldCount = parseInt(sstEl.getAttribute('count') || '0')
            const oldUnique = parseInt(sstEl.getAttribute('uniqueCount') || '0')
            sstEl.setAttribute('count', String(oldCount + 2))
            sstEl.setAttribute('uniqueCount', String(oldUnique + 2))
          }

          // 创建标题行
          const titleRow = doc.createElementNS(nsResolver, 'row')
          titleRow.setAttribute('r', String(titleRowNum))
          titleRow.setAttribute('ht', '22')
          titleRow.setAttribute('customHeight', '1')
          const titleCell = doc.createElementNS(nsResolver, 'c')
          titleCell.setAttribute('r', `A${titleRowNum}`)
          titleCell.setAttribute('t', 's')
          if (boldStyleIndex) titleCell.setAttribute('s', boldStyleIndex)
          const titleV = doc.createElementNS(nsResolver, 'v')
          titleV.textContent = String(titleSsIndex)
          titleCell.appendChild(titleV)
          titleRow.appendChild(titleCell)
          sheetDataEl.appendChild(titleRow)

          // 创建条款内容行
          const termsRow = doc.createElementNS(nsResolver, 'row')
          termsRow.setAttribute('r', String(termsRowNum))
          termsRow.setAttribute('ht', '230')
          termsRow.setAttribute('customHeight', '1')
          const termsCell = doc.createElementNS(nsResolver, 'c')
          termsCell.setAttribute('r', `A${termsRowNum}`)
          termsCell.setAttribute('t', 's')
          if (wrapTextStyleIndex) termsCell.setAttribute('s', wrapTextStyleIndex)
          const termsV = doc.createElementNS(nsResolver, 'v')
          termsV.textContent = String(contentSsIndex)
          termsCell.appendChild(termsV)
          termsRow.appendChild(termsCell)
          sheetDataEl.appendChild(termsRow)

          // 第二行（合并区域的下半部分）
          const termsRow2 = doc.createElementNS(nsResolver, 'row')
          termsRow2.setAttribute('r', String(termsRowEndNum))
          termsRow2.setAttribute('ht', '230')
          termsRow2.setAttribute('customHeight', '1')
          sheetDataEl.appendChild(termsRow2)

          // 添加合并单元格定义
          let mergeCellsEl = doc.getElementsByTagNameNS(nsResolver, 'mergeCells')[0]
          if (!mergeCellsEl) {
            mergeCellsEl = doc.createElementNS(nsResolver, 'mergeCells')
            mergeCellsEl.setAttribute('count', '0')
            // mergeCells 需要在 sheetData 之后插入
            const sheetDataParent = sheetDataEl.parentNode!
            const nextSibling = sheetDataEl.nextSibling
            if (nextSibling) {
              sheetDataParent.insertBefore(mergeCellsEl, nextSibling)
            } else {
              sheetDataParent.appendChild(mergeCellsEl)
            }
          }

          const endColLetter = colToLetter(mergeCols)

          // 标题行合并
          const titleMerge = doc.createElementNS(nsResolver, 'mergeCell')
          titleMerge.setAttribute('ref', `A${titleRowNum}:${endColLetter}${titleRowNum}`)
          mergeCellsEl.appendChild(titleMerge)

          // 条款内容行合并
          const termsMerge = doc.createElementNS(nsResolver, 'mergeCell')
          termsMerge.setAttribute('ref', `A${termsRowNum}:${endColLetter}${termsRowEndNum}`)
          mergeCellsEl.appendChild(termsMerge)

          // 更新 mergeCells count
          const existingCount = parseInt(mergeCellsEl.getAttribute('count') || '0')
          mergeCellsEl.setAttribute('count', String(existingCount + 2))

          console.log('[Export] 已添加服务条款（JSZip XML 方式）')
        }

        // 序列化修改后的 XML 写回 ZIP
        const serializer = new XMLSerializer()
        const updatedSheetXml = serializer.serializeToString(doc)
        zip.file(sheetPath, updatedSheetXml)

        if (ssDoc2) {
          const updatedSsXml = serializer.serializeToString(ssDoc2)
          zip.file('xl/sharedStrings.xml', updatedSsXml)
        }

        if (stylesDoc) {
          const updatedStylesXml = serializer.serializeToString(stylesDoc)
          zip.file('xl/styles.xml', updatedStylesXml)
        }

        const extraSheetNames = selectedSheetNames.filter(name => name && name !== selectedSheetName)
        for (const extraSheetName of extraSheetNames) {
          const extraItems = tableData.value.filter((item: any) => item.sheetName === extraSheetName)
          if (extraItems.length === 0) continue

          let extraRId = ''
          for (const m of sheetMatches) {
            if (m[1] === extraSheetName) { extraRId = m[2]; break }
          }
          if (!extraRId) continue

          const extraRelMatch = relsXml.match(new RegExp(`<Relationship[^>]*Id="${extraRId}"[^>]*Target="([^"]*)"[^>]*/>`))
          let extraSheetPath = extraRelMatch ? `xl/${extraRelMatch[1]}` : ''
          extraSheetPath = extraSheetPath.replace('xl/xl/', 'xl/')
          if (!extraSheetPath) continue

          const extraSheetXml = await zip.file(extraSheetPath)?.async('string')
          if (!extraSheetXml) continue

          const extraDoc = parser.parseFromString(extraSheetXml, 'application/xml')
          const extraNs = extraDoc.documentElement.namespaceURI || nsResolver
          const extraSheetDataEl = extraDoc.getElementsByTagNameNS(extraNs, 'sheetData')[0]
          if (!extraSheetDataEl) continue
          const extraRows = extraSheetDataEl.getElementsByTagNameNS(extraNs, 'row')

          let extraMaxCol = 0
          for (let i = 0; i < extraRows.length; i++) {
            const cells = extraRows[i].getElementsByTagNameNS(extraNs, 'c')
            for (let j = 0; j < cells.length; j++) {
              const ref = cells[j].getAttribute('r') || ''
              const { col } = parseRef(ref)
              if (col > extraMaxCol) extraMaxCol = col
            }
          }
          const extraPriceColIndex = extraMaxCol + 1
          const extraPriceColLetter = colToLetter(extraPriceColIndex)
          const extraLenovoColIndex = hasLenovoData ? extraPriceColIndex + 1 : extraPriceColIndex
          const extraLenovoColLetter = hasLenovoData ? colToLetter(extraLenovoColIndex) : extraPriceColLetter
          const extraLastColLetter = hasLenovoData ? extraLenovoColLetter : extraPriceColLetter

          const getExtraRowTexts = (rowEl: Element): string[] => {
            const texts: string[] = []
            const cells = rowEl.getElementsByTagNameNS(extraNs, 'c')
            for (let j = 0; j < cells.length; j++) {
              const vEl = cells[j].getElementsByTagNameNS(extraNs, 'v')[0]
              const cellType = cells[j].getAttribute('t')
              if (vEl && vEl.textContent) {
                if (cellType === 's') {
                  const idx = parseInt(vEl.textContent)
                  texts.push((sharedStrings[idx] || '').replace(/[\s*\n]/g, ''))
                } else {
                  texts.push(vEl.textContent.replace(/[\s*\n]/g, ''))
                }
              }
            }
            return texts
          }

          const extraSheetSelection = getSheetWorksheetSelection(extraSheetName)
          let extraHeaderRowNum = extraSheetSelection?.headerRowNumber || 1
          if (!extraSheetSelection) {
            for (let i = 0; i < Math.min(extraRows.length, 30); i++) {
              const rowNum = parseInt(extraRows[i].getAttribute('r') || String(i + 1))
              const texts = getExtraRowTexts(extraRows[i])
              if (texts.length < 3) continue
              let kwCount = 0
              for (const kw of commonDeviceKeywords) {
                if (texts.some(v => v.includes(kw))) kwCount++
              }
              if (kwCount >= 3) {
                extraHeaderRowNum = rowNum
                break
              }
            }
          }

          const extraDataRowIndices: number[] = []
          const extraWorksheetRowToSeqIndex = new Map<number, number>()
          if (extraSheetSelection?.dataRowNumbers?.length) {
            extraSheetSelection.dataRowNumbers.forEach((rowNumber, seqIdx) => {
              extraWorksheetRowToSeqIndex.set(rowNumber, seqIdx)
            })
            for (let i = 0; i < extraRows.length; i++) {
              const rn = parseInt(extraRows[i].getAttribute('r') || '0')
              if (extraWorksheetRowToSeqIndex.has(rn)) {
                extraDataRowIndices.push(i)
              }
            }
          } else {
            for (let i = 0; i < extraRows.length; i++) {
              const rn = parseInt(extraRows[i].getAttribute('r') || '0')
              if (rn > extraHeaderRowNum && getExtraRowTexts(extraRows[i]).filter(t => t.length > 0).length >= 2) {
                extraDataRowIndices.push(i)
              }
            }
          }

          let extraHeaderStyleId = ''
          for (let i = 0; i < extraRows.length; i++) {
            const rn = parseInt(extraRows[i].getAttribute('r') || '0')
            if (rn === extraHeaderRowNum) {
              const cells = extraRows[i].getElementsByTagNameNS(extraNs, 'c')
              extraHeaderStyleId = cells[0]?.getAttribute('s') || ''
              break
            }
          }

          for (let i = 0; i < extraRows.length; i++) {
            const rowNum = parseInt(extraRows[i].getAttribute('r') || '0')

            // ---- 维保单价单元格 ----
            const newCell = extraDoc.createElementNS(extraNs, 'c')
            newCell.setAttribute('r', `${extraPriceColLetter}${rowNum}`)

            const seqIndex = extraSheetSelection?.dataRowNumbers?.length
              ? extraWorksheetRowToSeqIndex.get(rowNum) ?? -1
              : extraDataRowIndices.indexOf(i)
            const item = seqIndex >= 0 ? extraItems[seqIndex] : null

            if (rowNum === extraHeaderRowNum && priceHeaderSsIndex >= 0) {
              newCell.setAttribute('t', 's')
              if (extraHeaderStyleId) newCell.setAttribute('s', extraHeaderStyleId)
              const vEl = extraDoc.createElementNS(extraNs, 'v')
              vEl.textContent = String(priceHeaderSsIndex)
              newCell.appendChild(vEl)
            } else {
              const basePrice = item?.finalPrice || item?.suggestedPrice || 0
              if (basePrice > 0) {
                const vEl = extraDoc.createElementNS(extraNs, 'v')
                vEl.textContent = String(Math.round(basePrice * exportPriceMultiplier * 100) / 100)
                newCell.appendChild(vEl)
                const cells = extraRows[i].getElementsByTagNameNS(extraNs, 'c')
                const sAttr = cells[0]?.getAttribute('s')
                if (sAttr) newCell.setAttribute('s', sAttr)
              }
            }
            extraRows[i].appendChild(newCell)

            // ---- 联想框架单价单元格（仅在 hasLenovoData 时追加） ----
            if (hasLenovoData) {
              const lenovoCell = extraDoc.createElementNS(extraNs, 'c')
              lenovoCell.setAttribute('r', `${extraLenovoColLetter}${rowNum}`)
              if (rowNum === extraHeaderRowNum && lenovoHeaderSsIndex >= 0) {
                lenovoCell.setAttribute('t', 's')
                if (extraHeaderStyleId) lenovoCell.setAttribute('s', extraHeaderStyleId)
                const vEl = extraDoc.createElementNS(extraNs, 'v')
                vEl.textContent = String(lenovoHeaderSsIndex)
                lenovoCell.appendChild(vEl)
              } else {
                const lp = Number(item?.lenovo_unit_price)
                if (Number.isFinite(lp) && lp > 0) {
                  const vEl = extraDoc.createElementNS(extraNs, 'v')
                  vEl.textContent = String(Math.round(lp * 100) / 100)
                  lenovoCell.appendChild(vEl)
                  const cells = extraRows[i].getElementsByTagNameNS(extraNs, 'c')
                  const sAttr = cells[0]?.getAttribute('s')
                  if (sAttr) lenovoCell.setAttribute('s', sAttr)
                }
              }
              extraRows[i].appendChild(lenovoCell)
            }
          }

          const extraDimEl = extraDoc.getElementsByTagNameNS(extraNs, 'dimension')[0]
          if (extraDimEl) {
            const oldRef = extraDimEl.getAttribute('ref') || ''
            extraDimEl.setAttribute('ref', oldRef.replace(/([A-Z]+)(\d+)$/, `${extraLastColLetter}$2`))
          }

          const extraUpdatedSheetXml = serializer.serializeToString(extraDoc)
          zip.file(extraSheetPath, extraUpdatedSheetXml)
          console.log('[Export] 已为原格式工作表追加价格列:', extraSheetName)
        }

        hasOriginalFile = true
        const baseName = originalFileName.replace(/\.xlsx?$/i, '')
        const fileName1 = `报价单-${baseName}.xlsx`
        const buffer1 = await zip.generateAsync({ type: 'arraybuffer' })
        downloadFile(buffer1, fileName1)
        console.log('[Export] 文件1导出成功（JSZip 方式，样式完整保留）:', fileName1)

      } catch (loadError) {
        console.error('[Export] 加载原始Excel文件失败:', loadError)
        hasOriginalFile = false
      }
    }

    // 如果没有原始文件，使用原始表格数据创建文件1
    if (!hasOriginalFile && previewOriginalData.value && previewOriginalData.value.headers) {
      console.log('[Export] 无原始文件，使用原始表格数据生成文件1')

      const workbook1 = new ExcelJS.Workbook()
      workbook1.creator = 'AI报价系统'
      workbook1.created = new Date()

      const safeSheetName = (name: string, index: number) => {
        const cleaned = (name || `工作表${index + 1}`).replace(/[\\/?*[\]:]/g, ' ').trim()
        return (cleaned || `工作表${index + 1}`).slice(0, 31)
      }
      const sourceSheets = originalSheetTables.value.length > 0
        ? originalSheetTables.value.map((sheet) => {
            const sheetPreview = buildOriginalPreviewForSheet(sheet.headers, sheet.data, sheet.sheetName)
            return {
              sheetName: sheet.sheetName,
              headers: sheetPreview.headers,
              data: sheetPreview.data
            }
          })
        : [{ sheetName: '报价表', headers: previewOriginalData.value.headers, data: previewOriginalData.value.data }]

      sourceSheets.forEach((sheetSource, sheetIndex) => {
        const baseHeaders = sheetSource.headers
        const originalHeaders = hasLenovoData ? [...baseHeaders, LENOVO_HEADER] : baseHeaders
        const originalData = sheetSource.data
        const worksheet = workbook1.addWorksheet(safeSheetName(sheetSource.sheetName, sheetIndex))

        const headerRow = worksheet.addRow(originalHeaders)
        headerRow.font = { bold: true }
        headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE0E0E0' } }
        worksheet.columns = originalHeaders.map(() => ({ width: 18 }))

        originalData.forEach((row, rowIndex) => {
          const values = baseHeaders.map(header => {
            const val = row[header]
            if (isPriceColumn(header) && val !== '' && val !== null && val !== undefined) {
              return Number(val)
            }
            return val ?? ''
          })
          if (hasLenovoData) {
            const lp = matchLenovoPrice(row, rowIndex, sheetSource.sheetName)
            values.push(lp !== null ? lp : '')
          }
          const dataRow = worksheet.addRow(values)
          originalHeaders.forEach((header, colIndex) => {
            if (isPriceColumn(header) || header === LENOVO_HEADER) {
              dataRow.getCell(colIndex + 1).numFmt = '¥#,##0.00'
            }
          })
        })

        addServiceTermsToWorksheet(worksheet, originalData.length + 1, originalHeaders.length)
      })

      const fallbackBaseName = originalFileName ? originalFileName.replace(/\.xlsx?$/i, '') : (projectName.value || '设备报价单')
      const fileName1 = `报价单-${fallbackBaseName}.xlsx`
      const buffer1 = await workbook1.xlsx.writeBuffer()
      downloadFile(buffer1, fileName1)
      console.log('[Export] 文件1导出成功:', fileName1)
    }

    // ===== 文件2：标准格式表格（基于转换后表格） =====
    if (previewConvertedData.value && previewConvertedData.value.headers) {
      console.log('[Export] 生成文件2：标准格式表格')

      const workbook2 = new ExcelJS.Workbook()
      workbook2.creator = 'AI报价系统'
      workbook2.created = new Date()

      const safeSheetName = (name: string, index: number) => {
        const cleaned = (name || `工作表${index + 1}`).replace(/[\\/?*[\]:]/g, ' ').trim()
        return (cleaned || `工作表${index + 1}`).slice(0, 31)
      }

      const previewHeaders = previewConvertedData.value.headers
      const sheetSources = convertedSheetTables.value.length > 0
        ? convertedSheetTables.value
        : [{ sheetName: '标准报价表', headers: previewHeaders, data: previewConvertedData.value.data }]

      const getSheetPrice = (row: any, rowIndex: number, sheetName: string) => {
        const matchedBySheet = tableData.value.find((item, itemIndex) => {
          if (item.sheetName && item.sheetName !== sheetName) return false
          if (Number.isFinite(Number(item.sourceRowIndex)) && Number(item.sourceRowIndex) === rowIndex) return true
          if (!item.sheetName && itemIndex === rowIndex) return true
          return false
        })
        let basePrice = matchedBySheet?.finalPrice || matchedBySheet?.suggestedPrice || 0

        if (!basePrice) {
          const modelValue = String(row['设备/软件型号'] || '').trim().toUpperCase()
          const matchedByModel = tableData.value.find(item => {
            if (item.sheetName && item.sheetName !== sheetName) return false
            return [item.model, item.matchedModel, item.originalModel]
              .filter(Boolean)
              .some((key: string) => String(key).trim().toUpperCase() === modelValue)
          })
          basePrice = matchedByModel?.finalPrice || matchedByModel?.suggestedPrice || 0
        }

        return Math.round(Number(basePrice || row['单价'] || 0) * exportPriceMultiplier * 100) / 100
      }

      sheetSources.forEach((sheetSource, sheetIndex) => {
        const baseConvertedHeaders = (sheetSource.headers || previewHeaders).map(h => h === '单价'
          ? (priceLayout.value === 'layout3' ? '单价(含税6%)' : priceLayout.value === 'layout4' ? '单价(含税13%)' : h)
          : h
        )
        const convertedHeaders = hasLenovoData
          ? [...baseConvertedHeaders, LENOVO_HEADER]
          : baseConvertedHeaders
        const rawHeaders = sheetSource.headers || previewHeaders
        const worksheet = workbook2.addWorksheet(safeSheetName(sheetSource.sheetName, sheetIndex))

        const headerRow = worksheet.addRow(convertedHeaders)
        headerRow.font = { bold: true }
        headerRow.fill = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFE0E0E0' } }
        worksheet.columns = convertedHeaders.map((header) => ({
          width: header === LENOVO_HEADER ? 22 : (isPriceColumn(header) ? 15 : 18)
        }))

        sheetSource.data.forEach((row, rowIndex) => {
          const values = rawHeaders.map((rawHeader, headerIndex) => {
            const exportHeader = baseConvertedHeaders[headerIndex]
            if (rawHeader === '单价') {
              return getSheetPrice(row, rowIndex, sheetSource.sheetName)
            }
            const val = row[rawHeader]
            if (isPriceColumn(exportHeader) && val !== '' && val !== null && val !== undefined) {
              return Number(val)
            }
            return val ?? ''
          })
          if (hasLenovoData) {
            const lp = matchLenovoPrice(row, rowIndex, sheetSource.sheetName)
            values.push(lp !== null ? lp : '')
          }
          const dataRow = worksheet.addRow(values)

          convertedHeaders.forEach((header, colIndex) => {
            const cell = dataRow.getCell(colIndex + 1)
            if (isPriceColumn(header) || header === LENOVO_HEADER) {
              cell.numFmt = '¥#,##0.00'
            }
            cell.border = {
              top: { style: 'thin' },
              left: { style: 'thin' },
              bottom: { style: 'thin' },
              right: { style: 'thin' }
            }
          })
        })

        convertedHeaders.forEach((_, colIndex) => {
          headerRow.getCell(colIndex + 1).border = {
            top: { style: 'thin' },
            left: { style: 'thin' },
            bottom: { style: 'thin' },
            right: { style: 'thin' }
          }
        })

        addServiceTermsToWorksheet(worksheet, sheetSource.data.length + 1, convertedHeaders.length)
      })

      // 生成文件名并下载
      const stdBaseName = originalFileName ? originalFileName.replace(/\.xlsx?$/i, '') : (projectName.value || '设备报价单')
      const fileName2 = `标准格式报价单-${stdBaseName}.xlsx`
      const buffer2 = await workbook2.xlsx.writeBuffer()

      // 稍微延迟下载第二个文件，避免浏览器拦截
      setTimeout(() => {
        downloadFile(buffer2, fileName2)
        console.log('[Export] 文件2导出成功:', fileName2)
      }, 500)
    }

    console.log('[Export] 两个报价单文件导出完成')

    // 导出成功后关闭弹窗
    closePreviewDialog()
  } catch (error) {
    console.error('导出报价单失败:', error)
    alert('导出报价单失败，请重试')
  } finally {
    isExporting.value = false
  }
}

// 格式化表格单元格数据
function formatCellValue(value: any): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'number') return String(value)
  return String(value)
}

// 监听 tableData 变化，实时保存状态（用于面包屑跳转恢复）
watch(tableData, (newData) => {
  if (newData && newData.length > 0) {
    savePageState(PAGE_STATE_KEYS.QUOTATION_GENERATION, {
      tableData: newData,
      projectName: projectName.value,
      customerName: customerName.value,
      validDays: validDays.value,
      notes: notes.value,
      hasData: true
    })
  }
}, { deep: true })
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.quotation-generation {
  font-family: "Noto Sans SC", sans-serif;
  background-color: #101622;
  color: white;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
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

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  background-image: url("/images/homepage/page-bg.jpg");
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
  max-width: 1800px;
  margin: 0 auto;
  width: 100%;
  overflow-y: auto;
  min-height: 0;
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
  flex-wrap: wrap;
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

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 1.5rem;
  flex: 1;
}

@media (min-width: 1280px) {
  .content-grid {
    grid-template-columns: 1fr 360px;
  }
}

/* Preview Section */
.preview-section {
  flex: 1;
  display: flex;
  justify-content: center;
  background-color: #0d121c;
  border-radius: 0.75rem;
  border: 1px solid #232f48;
  padding: 2rem;
  overflow-y: auto;
  box-shadow: inset 0 2px 4px 0 rgba(0, 0, 0, 0.1);
}

.preview-wrapper {
  width: 100%;
  max-width: 800px;
}

.quotation-document {
  background-color: white;
  color: #0f172a;
  min-height: 900px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
  padding: 3rem;
  display: flex;
  flex-direction: column;
  position: relative;
  border-radius: 0.125rem;
}

.doc-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 16rem;
  height: 16rem;
  background: linear-gradient(to bottom left, #eff6ff, transparent);
  border-bottom-left-radius: 9999px;
  opacity: 0.5;
  pointer-events: none;
}

/* Document Header */
.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 3rem;
  gap: 2rem;
}

.company-info {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.company-logo-upload {
  position: relative;
  cursor: pointer;
  margin-bottom: 0.5rem;
  padding: 0.25rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  border: 2px dashed transparent;
}

.company-logo-upload:hover {
  border-color: #e2e8f0;
  background: #f8fafc;
}

.company-logo-upload:hover .logo-upload-hint {
  opacity: 1;
}

.custom-logo-img {
  height: 3rem;
  max-width: 12rem;
  object-fit: contain;
}

.logo-upload-hint {
  position: absolute;
  top: 50%;
  right: -2rem;
  transform: translateY(-50%);
  opacity: 0;
  transition: opacity 0.2s;
  color: #94a3b8;
}

.logo-upload-hint .material-symbols-outlined {
  font-size: 1.25rem;
}

.company-logo-text {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.logo-icon {
  width: 2.5rem;
  height: 2.5rem;
}

.logo-text-group {
  display: flex;
  flex-direction: column;
}

.logo-cn {
  font-size: 1.25rem;
  font-weight: 700;
  color: #005bac;
  letter-spacing: 0.1em;
}

.logo-en {
  font-size: 0.625rem;
  font-weight: 600;
  color: #005bac;
  letter-spacing: 0.05em;
}

.company-name {
  font-size: 1.25rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
}

.company-address {
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
}

.company-contact {
  color: #64748b;
  font-size: 0.875rem;
  line-height: 1.5;
}

.quote-info {
  text-align: right;
}

.doc-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #005bac;
  margin-bottom: 0.5rem;
  letter-spacing: 0.1em;
}

.quote-number {
  color: #64748b;
  font-weight: 500;
}

.quote-date {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 2rem;
  margin-bottom: 3rem;
}

.info-block {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.customer-name {
  font-weight: 700;
  color: #0f172a;
  font-size: 1.125rem;
}

.customer-detail {
  color: #475569;
}

.validity-date {
  font-weight: 700;
  color: #0f172a;
}

.validity-note {
  color: #475569;
  font-size: 0.875rem;
  margin-top: 0.25rem;
}

/* Items Table */
.items-table {
  margin-bottom: 2rem;
}

/* 预览态：表格区固定高度内滚动；PDF 态由 is-scrolling 类移除恢复 auto */
.items-table.is-scrolling .items-table-scroll {
  max-height: 60vh;
  overflow-y: auto;
  position: relative;
}
.items-table:not(.is-scrolling) .items-table-scroll {
  max-height: none;
  overflow: visible;
}

.items-table-scroll .quote-table thead {
  position: sticky;
  top: 0;
  background: white;
  z-index: 2;
}

.quote-table tbody tr.virtual-spacer {
  background: transparent !important;
  border: none !important;
  transition: none;
}
.quote-table tbody tr.virtual-spacer td {
  padding: 0;
  border: none;
}

.quote-table {
  width: 100%;
  text-align: left;
  border-collapse: collapse;
}

.quote-table thead tr {
  border-bottom: 2px solid #f1f5f9;
}

.quote-table th {
  padding: 0.75rem 0;
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.col-no {
  width: 8%;
  text-align: center;
}

.col-desc {
  width: 42%;
}

.col-qty {
  width: 10%;
  text-align: center;
}

.col-period {
  width: 12%;
  text-align: center;
}

.col-price,
.col-total {
  text-align: right;
}

.quote-table tbody tr {
  border-bottom: 1px solid #f8fafc;
  transition: background-color 0.2s;
}

.quote-table tbody tr:hover {
  background-color: #f8fafc;
}

.quote-table td {
  padding: 1rem 0;
  color: #475569;
}

.item-desc {
  padding-right: 1rem;
}

.item-name {
  font-weight: 700;
  color: #0f172a;
}

.item-detail {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
}

.item-total {
  font-weight: 500;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

/* Summary Section */
.summary-section {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 3rem;
}

.summary-content {
  width: 50%;
  min-width: 250px;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #f1f5f9;
}

.summary-label {
  color: #475569;
}

.summary-value {
  font-weight: 500;
  color: #0f172a;
}

.summary-value.discount {
  color: #ef4444;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.total-label {
  font-weight: 700;
  color: #0f172a;
  font-size: 1.125rem;
}

.total-value {
  font-weight: 700;
  font-size: 1.875rem;
  color: #135bec;
  font-family: "Space Grotesk", sans-serif;
}

/* Signature Section */
.signature-section {
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.signature-row {
  display: flex;
  align-items: flex-end;
  gap: 1rem;
  margin-bottom: 1.25rem;
}

.signature-row:last-child {
  margin-bottom: 0;
}

.signature-label {
  color: #64748b;
  font-size: 0.875rem;
  white-space: nowrap;
  min-width: 4rem;
}

.signature-line {
  flex: 1;
  border-bottom: 1px solid #0f172a;
  min-height: 1.5rem;
}

/* Terms Section */
.terms-section {
  margin-top: auto;
}

.terms-title {
  font-weight: 700;
  color: #0f172a;
  font-size: 0.875rem;
  text-transform: uppercase;
  margin-bottom: 0.5rem;
}

.terms-content {
  color: #64748b;
  font-size: 0.75rem;
  line-height: 1.6;
  text-align: justify;
  white-space: pre-line;
}

.terms-paragraph {
  color: #64748b;
  font-size: 0.75rem;
  line-height: 1.6;
  text-align: justify;
  white-space: pre-wrap;
  margin-bottom: 0.1em;
}

.doc-footer {
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #f1f5f9;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.footer-text {
  color: #cbd5e1;
  font-size: 0.75rem;
}

/* Control Panel */
.control-panel {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.panel-card {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.panel-title {
  color: white;
  font-weight: 700;
  font-size: 1.125rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.panel-title .material-symbols-outlined {
  color: #135bec;
  font-size: 1.25rem;
}

/* Export Grid */
.export-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}

.export-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border-radius: 0.5rem;
  background-color: #232f48;
  border: 1px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}

.export-btn:hover {
  border-color: rgba(19, 91, 236, 0.5);
  background-color: rgba(19, 91, 236, 0.1);
}

.export-btn.pdf:hover {
  background-color: rgba(239, 68, 68, 0.1);
  border-color: rgba(239, 68, 68, 0.5);
}

.export-btn.excel:hover {
  background-color: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.5);
}

.export-btn .material-symbols-outlined {
  color: white;
  font-size: 1.875rem;
  margin-bottom: 0.5rem;
  transition: transform 0.2s;
}

.export-btn:hover .material-symbols-outlined {
  transform: scale(1.1);
}

.btn-text {
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.send-email-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background-color: #135bec;
  color: white;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  margin-top: 0.5rem;
}

.send-email-btn:hover {
  background-color: #1d6bf5;
}

.send-email-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.export-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.export-btn:disabled:hover {
  border-color: transparent;
  background-color: #232f48;
}

.export-btn:disabled:hover .material-symbols-outlined {
  transform: none;
}

/* Configuration */
.config-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-label {
  color: #92a4c9;
  font-size: 0.875rem;
  font-weight: 500;
}

.select-wrapper {
  position: relative;
}

.config-select {
  width: 100%;
  appearance: none;
  border-radius: 0.5rem;
  background-color: #232f48;
  border: 1px solid #232f48;
  color: white;
  padding: 0.75rem 2.5rem 0.75rem 0.75rem;
  font-size: 0.875rem;
  outline: none;
  cursor: pointer;
  transition: all 0.2s;
}

.config-select:focus {
  border-color: #135bec;
  ring: 1px solid rgba(19, 91, 236, 0.5);
}

.select-icon {
  position: absolute;
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  color: #92a4c9;
  pointer-events: none;
  font-size: 1.25rem;
}

.divider-line {
  border: none;
  border-top: 1px solid #232f48;
  margin: 0.5rem 0;
}

/* Toggle Group */
.toggle-group {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.toggle-label {
  color: white;
  font-size: 0.875rem;
}

.toggle-switch {
  position: relative;
  display: inline-block;
  width: 2.75rem;
  height: 1.5rem;
  cursor: pointer;
}

.toggle-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #232f48;
  transition: 0.3s;
  border-radius: 9999px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 1.25rem;
  width: 1.25rem;
  left: 0.125rem;
  bottom: 0.125rem;
  background-color: white;
  transition: 0.3s;
  border-radius: 9999px;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #135bec;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(1.25rem);
}

/* Tax Rate Inline Selector */
.tax-rate-inline {
  display: flex;
  gap: 0.375rem;
  margin-left: auto;
  margin-right: 0.75rem;
}

.tax-rate-option {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  background-color: #232f48;
  border: 1px solid transparent;
  border-radius: 0.25rem;
  color: #64748b;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.tax-rate-option input {
  display: none;
}

.tax-rate-option:hover {
  color: #94a3b8;
}

.tax-rate-option.active {
  background-color: rgba(19, 91, 236, 0.15);
  border-color: rgba(19, 91, 236, 0.3);
  color: #135bec;
}

/* Status Card */
.status-card {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.status-icon {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background-color: rgba(34, 197, 94, 0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.status-icon .material-symbols-outlined {
  color: #22c55e;
  font-size: 1.5rem;
}

.status-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.status-title {
  color: white;
  font-weight: 500;
  font-size: 0.875rem;
}

.status-desc {
  color: #92a4c9;
  font-size: 0.75rem;
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

/* 预览弹窗样式 */
.preview-overlay {
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
  padding: 2rem;
}

.preview-dialog {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 1rem;
  width: 100%;
  max-width: 1400px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #232f48;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: white;
}

.preview-title .material-symbols-outlined {
  color: #135bec;
  font-size: 1.5rem;
}

.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.close-btn .material-symbols-outlined {
  font-size: 1.5rem;
}

.preview-content {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

@media (max-width: 1024px) {
  .preview-content {
    grid-template-columns: 1fr;
  }
}

.preview-table-section {
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.preview-table-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #232f48;
  background-color: rgba(19, 91, 236, 0.1);
}

.preview-table-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 600;
  color: #135bec;
}

.preview-table-count {
  font-size: 0.75rem;
  color: #94a3b8;
  background-color: #232f48;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
}

.preview-table-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
}

.preview-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.75rem;
}

.preview-table thead {
  position: sticky;
  top: 0;
  background-color: #1a2332;
  z-index: 10;
}

.preview-table th {
  padding: 0.75rem 0.5rem;
  text-align: left;
  font-weight: 600;
  color: #94a3b8;
  white-space: nowrap;
  border-bottom: 1px solid #232f48;
}

.preview-table td {
  padding: 0.5rem;
  color: #cbd5e1;
  border-bottom: 1px solid #232f48;
  white-space: nowrap;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-table tbody tr:hover {
  background-color: rgba(19, 91, 236, 0.05);
}

.preview-table tbody tr:last-child td {
  border-bottom: none;
}

.empty-preview {
  text-align: center !important;
  padding: 2rem !important;
  color: #64748b !important;
}

.preview-more-hint {
  text-align: center;
  padding: 0.5rem;
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
  background-color: rgba(100, 116, 139, 0.1);
}

.preview-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #232f48;
  background-color: #1a2332;
  border-radius: 0 0 1rem 1rem;
}

.preview-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
}

.preview-btn.cancel {
  background: transparent;
  border: 1px solid #232f48;
  color: #cbd5e1;
}

.preview-btn.cancel:hover {
  background-color: rgba(100, 116, 139, 0.1);
}

.preview-btn.confirm {
  background-color: #135bec;
  border: none;
  color: white;
}

.preview-btn.confirm:hover:not(:disabled) {
  background-color: #1d6bf5;
  transform: translateY(-1px);
}

.preview-btn.confirm:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.preview-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Bottom Bar Styles */
.bottom-bar {
  flex-shrink: 0;
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

.divider-vertical {
  width: 1px;
  height: 24px;
  background-color: #232f48;
}

.bottom-actions {
  display: flex;
  gap: 1rem;
}

.btn-back,
.btn-complete {
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

.btn-complete {
  background-color: #22c55e;
  color: white;
  border: none;
  font-weight: 700;
  box-shadow: 0 10px 15px -3px rgba(34, 197, 94, 0.25);
  transform: translateY(0);
}

.btn-complete:hover {
  background-color: #16a34a;
  transform: translateY(-2px);
}

.btn-complete .material-symbols-outlined {
  font-size: 1rem;
}

/* 打印和PDF导出时防止内容被分页截断 */
@media print {
  .doc-header,
  .info-grid,
  .items-table thead,
  .item-row,
  .summary-section,
  .summary-row,
  .summary-total,
  .terms-title,
  .terms-content,
  .terms-paragraph,
  .doc-footer {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }

  .summary-section,
  .terms-section {
    page-break-before: auto;
    break-before: auto;
  }
}

/* 用于PDF渲染时的防分页样式 */
.quotation-document .doc-header,
.quotation-document .info-grid,
.quotation-document .items-table thead,
.quotation-document .item-row,
.quotation-document .summary-section,
.quotation-document .summary-row,
.quotation-document .summary-total,
.quotation-document .terms-title,
.quotation-document .terms-paragraph,
.quotation-document .doc-footer {
  break-inside: avoid;
  page-break-inside: avoid;
}
</style>
