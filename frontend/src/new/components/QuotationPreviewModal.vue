<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="close">
        <div
          class="modal-window"
          :class="{ maximized: isMaximized }"
          :style="windowStyle"
        >
          <!-- 标题栏 -->
          <div class="modal-header">
            <div class="header-left">
              <div class="breadcrumb">
                <span class="breadcrumb-link">驻场服务报价测算</span>
                <span class="material-symbols-outlined">chevron_right</span>
                <span class="breadcrumb-current">预览报价单</span>
              </div>
              <h1 class="header-title">
                报价单预览
                <span class="preview-badge">A4 打印视图</span>
              </h1>
            </div>
            <div class="header-right">
              <div class="zoom-controls">
                <button class="zoom-btn" @click="zoomOut" title="缩小">
                  <span class="material-symbols-outlined">remove</span>
                </button>
                <span class="zoom-level">{{ zoomLevel }}%</span>
                <button class="zoom-btn" @click="zoomIn" title="放大">
                  <span class="material-symbols-outlined">add</span>
                </button>
              </div>
              <label class="config-toggle" for="sidebar-toggle">
                <span class="material-symbols-outlined">view_sidebar</span>
                配置面板
              </label>
              <button class="fullscreen-btn" @click="toggleMaximize">
                <span class="material-symbols-outlined">{{ isMaximized ? 'fullscreen_exit' : 'fullscreen' }}</span>
              </button>
              <button class="close-btn" @click="close" title="关闭">
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>

          <!-- 内容区域 -->
          <div class="modal-content" v-show="!isMinimized">
            <div class="content-wrapper">
              <!-- Preview Area -->
              <div class="preview-area">
                <div
                  ref="paperRef"
                  class="paper"
                  :style="{ transform: `scale(${zoomLevel / 100})` }"
                >
                  <!-- Watermark -->
                  <div class="watermark" :style="{ opacity: watermarkOpacity / 100 }">
                    {{ watermarkText }}
                  </div>

                  <!-- Paper Content -->
                  <div class="paper-content">
                    <!-- Header Section -->
                    <div class="paper-header">
                      <div class="company-info">
                        <div class="company-logo-upload" @click="triggerLogoUpload" title="点击上传自定义 Logo">
                          <!-- 自定义上传的图片 -->
                          <img v-if="customLogoUrl" :src="customLogoUrl" alt="公司Logo" class="custom-logo-img" />
                          <!-- 默认 Logo -->
                          <div v-else class="company-logo-default">
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
                        <div class="company-full-name">
                          <p class="company-name-text">{{ data.quoteCompanyInfo?.companyName || '北京源晨动力技术服务有限公司' }}</p>
                        </div>
                      </div>
                      <div class="title-section">
                        <h3 class="document-title">驻场服务报价单</h3>
                        <p class="document-number">编号: Q{{ currentYear }}{{ String(currentMonth).padStart(2, '0') }}{{ String(currentDay).padStart(2, '0') }}-XA009</p>
                      </div>
                    </div>

                    <!-- Info Grid -->
                    <div class="info-grid">
                      <div class="info-item">
                        <p class="info-label">报价公司信息</p>
                        <p class="info-value-bold">{{ selectedCompanyInfo.companyName }}</p>
                        <p class="info-value">联系人：{{ selectedCompanyInfo.contactName }}{{ selectedCompanyInfo.department ? ` (${selectedCompanyInfo.department})` : '' }}</p>
                        <p class="info-value">联系电话：{{ selectedCompanyInfo.contactPhone }}</p>
                      </div>
                      <div class="info-item">
                        <p class="info-label">客户信息</p>
                        <p class="info-value-bold">{{ selectedCustomerInfo.customerName }}</p>
                        <p class="info-value">地址：{{ selectedCustomerInfo.customerAddress }}</p>
                      </div>
                      <div class="info-item info-item-right">
                        <input
                          type="text"
                          v-model="editableProjectLabel"
                          class="info-label editable-input"
                          :size="editableProjectLabel.length || 10"
                        />
                        <input
                          type="text"
                          v-model="editableProjectName"
                          class="info-value-bold editable-input"
                          :size="editableProjectName.length || 10"
                        />
                        <p class="info-value">报价日期：{{ quotationDate }}</p>
                        <p class="info-value info-expiry">有效期至：{{ expiryDate }}</p>
                      </div>
                    </div>

                    <!-- Services Table -->
                    <table class="services-table">
                      <thead>
                        <tr>
                          <th class="text-left">服务岗位明细</th>
                          <th class="text-right">人数</th>
                          <th class="text-right">周期(月)</th>
                          <th class="text-right">综合单价 (¥/人/月)</th>
                          <th class="text-right">总价 (¥)</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr v-for="(row, index) in data.positionRows" :key="index">
                          <td class="service-name">
                            <p class="name-bold">{{ row.position || '服务岗位' }}</p>
                            <p class="name-detail">驻场城市: {{ row.city || '-' }}</p>
                          </td>
                          <td class="text-right">{{ row.personnelCount || 1 }}</td>
                          <td class="text-right">{{ getServiceMonths(row) }}</td>
                          <td class="text-right">{{ formatCurrency(getRowUnitPrice(row)) }}</td>
                          <td class="text-right name-bold">{{ formatCurrency(getRowTotalPrice(row)) }}</td>
                        </tr>
                      </tbody>
                    </table>

                    <!-- Summary Section -->
                    <div class="summary-section">
                      <div class="summary-card">
                        <div class="summary-row">
                          <span>项目总价（未税）</span>
                          <span class="summary-value">{{ formatCurrency(getLaborCostBeforeVat()) }}</span>
                        </div>
                        <div class="summary-row">
                          <span>增值税率</span>
                          <span class="summary-value">{{ data.globalParams?.vatRate || 6 }}%</span>
                        </div>
                        <div class="summary-row summary-row-total">
                          <span class="summary-total-label">项目总价</span>
                          <span class="summary-total-value">{{ formatCurrency(getFinalProjectAmount()) }}</span>
                        </div>
                      </div>
                    </div>

                    <!-- Footer Section -->
                    <div class="paper-footer">
                      <div class="footer-grid">
                        <div class="footer-notes">
                          <p class="notes-title">服务条款：</p>
                          <p class="notes-text">
                            1. 本报价单基于当前市场人力成本测算，有效期内签署有效。<br/>
                            2. 最终解释权归{{ data.quoteCompanyInfo?.companyName || '报价公司' }}所有。
                          </p>
                        </div>
                        <div class="footer-signature">
                          <div v-if="includeStamp" class="stamp">★<br/>业务专用章</div>
                          <div class="signature-line">
                            <p class="signature-label">{{ selectedCompanyInfo.companyName }}</p>
                            <p class="signature-name">{{ quotationDate }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Sidebar Config Panel -->
              <input type="checkbox" id="sidebar-toggle" class="sidebar-toggle" v-model="sidebarOpen" />
              <aside class="sidebar-panel" :class="{ open: sidebarOpen }">
                <div class="sidebar-content">
                  <div class="sidebar-header">
                    <h2 class="sidebar-title">
                      <span class="material-symbols-outlined">tune</span>
                      导出配置
                    </h2>
                  </div>
                  <div class="sidebar-body">
                    <!-- Export Format -->
                    <div class="config-section">
                      <label class="config-label">导出格式选择</label>
                      <div class="format-grid">
                        <label class="format-option" :class="{ active: exportFormat === 'pdf' }">
                          <input type="radio" name="export_format" value="pdf" v-model="exportFormat" />
                          <div class="format-card">
                            <span class="material-symbols-outlined format-icon pdf">picture_as_pdf</span>
                            <span class="format-name">PDF 文档</span>
                          </div>
                        </label>
                        <label class="format-option" :class="{ active: exportFormat === 'excel' }">
                          <input type="radio" name="export_format" value="excel" v-model="exportFormat" />
                          <div class="format-card">
                            <span class="material-symbols-outlined format-icon excel">table_view</span>
                            <span class="format-name">Excel 表格</span>
                          </div>
                        </label>
                        <label class="format-option" :class="{ active: exportFormat === 'word' }">
                          <input type="radio" name="export_format" value="word" v-model="exportFormat" />
                          <div class="format-card">
                            <span class="material-symbols-outlined format-icon word">description</span>
                            <span class="format-name">Word 文档</span>
                          </div>
                        </label>
                      </div>
                    </div>

                    <!-- Company & Customer Selection -->
                    <div class="config-section">
                      <label class="config-label">报价信息选择</label>
                      <div class="config-card">
                        <div class="input-group">
                          <label class="input-label">
                            <span class="material-symbols-outlined input-icon">business</span>
                            报价公司
                          </label>
                          <select v-model="selectedCompanyId" class="config-select">
                            <option v-for="company in companiesList" :key="company.id" :value="company.id">
                              {{ company.company_name }}
                            </option>
                          </select>
                        </div>
                        <div class="input-group">
                          <label class="input-label">
                            <span class="material-symbols-outlined input-icon">person</span>
                            客户信息
                          </label>
                          <select v-model="selectedCustomerId" class="config-select">
                            <option v-for="customer in customersList" :key="customer.id" :value="customer.id">
                              {{ customer.customer_name }}
                            </option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <!-- Watermark Settings -->
                    <div class="config-section">
                      <label class="config-label">水印设置</label>
                      <div class="config-card">
                        <div class="input-group">
                          <label class="input-label">水印内容</label>
                          <input type="text" v-model="watermarkText" class="config-input" placeholder="输入水印文字..." />
                        </div>
                        <div class="input-group">
                          <div class="flex justify-between">
                            <label class="input-label">透明度</label>
                            <span class="input-value">{{ watermarkOpacity }}%</span>
                          </div>
                          <input type="range" v-model.number="watermarkOpacity" min="0" max="100" class="slider" />
                        </div>
                      </div>
                    </div>

                    <!-- Content Settings -->
                    <div class="config-section">
                      <label class="config-label">内容与合规</label>
                      <div class="config-list">
                        <div class="config-item">
                          <div class="config-item-left">
                            <span class="material-symbols-outlined config-icon blue">list_alt</span>
                            <span class="config-item-text">包含详细费用明细表</span>
                          </div>
                          <label class="toggle-switch">
                            <input type="checkbox" v-model="includeDetail" />
                            <span class="toggle-slider"></span>
                          </label>
                        </div>
                        <div class="config-item">
                          <div class="config-item-left">
                            <span class="material-symbols-outlined config-icon purple">verified</span>
                            <span class="config-item-text">加盖电子公章/签名</span>
                          </div>
                          <label class="toggle-switch">
                            <input type="checkbox" v-model="includeStamp" />
                            <span class="toggle-slider"></span>
                          </label>
                        </div>
                      </div>
                      <div class="input-group mt-4">
                        <label class="input-label">报价单有效期</label>
                        <select v-model="validityPeriod" class="config-select">
                          <option value="30">30 天 (默认标准)</option>
                          <option value="15">15 天 (加急)</option>
                          <option value="60">60 天</option>
                          <option value="90">90 天 (长期框架)</option>
                        </select>
                      </div>
                    </div>
                  </div>
                  <div class="sidebar-footer">
                    <button class="btn-download" @click="downloadQuotation" :disabled="isDownloading">
                      <span v-if="isDownloading" class="material-symbols-outlined spinning">progress_activity</span>
                      <span v-else class="material-symbols-outlined">download</span>
                      {{ isDownloading ? '生成中...' : '直接下载' }}
                    </button>
                    <button class="btn-email" @click="sendEmail">
                      <span class="material-symbols-outlined">send</span>
                      发送至邮件
                    </button>
                  </div>
                </div>
              </aside>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const props = defineProps<{
  isOpen: boolean
  data: any
}>()

const emit = defineEmits<{
  close: []
}>()

// 公司和客户数据
interface CompanyInfo {
  id: number
  company_name: string
  company_address?: string
}

interface CustomerInfo {
  id: number
  customer_name: string
  customer_address?: string
  contact_person?: string
  contact_phone?: string
}

interface UserProfile {
  name?: string
  phone?: string
  department?: string
}

const companiesList = ref<CompanyInfo[]>([])
const customersList = ref<CustomerInfo[]>([])
const userProfile = ref<UserProfile>({})
const selectedCompanyId = ref<number | null>(null)
const selectedCustomerId = ref<number | null>(null)

// 获取选中的公司信息
const selectedCompanyInfo = computed(() => {
  if (!selectedCompanyId.value) {
    // 返回从 props.data 传入的默认信息
    return {
      companyName: props.data.quoteCompanyInfo?.companyName || '报价公司名称',
      contactName: props.data.quoteCompanyInfo?.contactName || userProfile.value.name || '联系人',
      contactPhone: props.data.quoteCompanyInfo?.contactPhone || userProfile.value.phone || '-',
      department: props.data.quoteCompanyInfo?.department || userProfile.value.department || '',
      companyAddress: props.data.quoteCompanyInfo?.companyAddress || ''
    }
  }
  const company = companiesList.value.find(c => c.id === selectedCompanyId.value)
  if (company) {
    return {
      companyName: company.company_name,
      contactName: userProfile.value.name || '联系人',
      contactPhone: userProfile.value.phone || '-',
      department: userProfile.value.department || '',
      companyAddress: company.company_address || ''
    }
  }
  return {
    companyName: '报价公司名称',
    contactName: '联系人',
    contactPhone: '-',
    department: '',
    companyAddress: ''
  }
})

// 获取选中的客户信息
const selectedCustomerInfo = computed(() => {
  if (!selectedCustomerId.value) {
    // 返回从 props.data 传入的默认信息
    return {
      customerName: props.data.customerName || '客户名称',
      customerAddress: props.data.customerAddress || '客户地址',
      contactPerson: props.data.customerContact || '',
      contactPhone: props.data.customerPhone || ''
    }
  }
  const customer = customersList.value.find(c => c.id === selectedCustomerId.value)
  if (customer) {
    return {
      customerName: customer.customer_name,
      customerAddress: customer.customer_address || '-',
      contactPerson: customer.contact_person || '',
      contactPhone: customer.contact_phone || ''
    }
  }
  return {
    customerName: '客户名称',
    customerAddress: '客户地址',
    contactPerson: '',
    contactPhone: ''
  }
})

// 加载公司和客户数据
async function loadCompaniesAndCustomers() {
  try {
    const [profileRes, companiesRes, customersRes] = await Promise.all([
      axios.get(`${API_URL}/user-profile/`),
      axios.get(`${API_URL}/user-profile/companies`),
      axios.get(`${API_URL}/user-profile/customers`)
    ])

    if (profileRes.data) {
      userProfile.value = {
        name: profileRes.data.name || '',
        phone: profileRes.data.phone || '',
        department: profileRes.data.department || ''
      }
    }

    if (companiesRes.data) {
      companiesList.value = companiesRes.data
      // 默认选中第一个公司
      if (companiesRes.data.length > 0 && !selectedCompanyId.value) {
        selectedCompanyId.value = companiesRes.data[0].id
      }
      // 若用户未手动上传 Logo，则使用个人设置中的公司 Logo 作为默认
      if (!customLogoUrl.value && companiesRes.data.length > 0) {
        const defaultCompany = companiesRes.data.find((c: any) => c.id === selectedCompanyId.value) || companiesRes.data[0]
        if (defaultCompany.company_logo) {
          customLogoUrl.value = defaultCompany.company_logo
        }
      }
    }

    if (customersRes.data) {
      customersList.value = customersRes.data
      // 默认选中第一个客户
      if (customersRes.data.length > 0 && !selectedCustomerId.value) {
        selectedCustomerId.value = customersRes.data[0].id
      }
    }
  } catch (err) {
    console.error('加载公司和客户数据失败', err)
  }
}

// 当 modal 打开时加载数据
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    loadCompaniesAndCustomers()
  }
})

// UI State
const zoomLevel = ref(100)
const sidebarOpen = ref(false)
const isMaximized = ref(false)
const isMinimized = ref(false)

// Config State
const exportFormat = ref('pdf')
const watermarkText = ref('内部报价 · 禁止外传')
const watermarkOpacity = ref(15)
const includeDetail = ref(true)
const includeStamp = ref(false)
const validityPeriod = ref('30')

// 可编辑的项目信息
const editableProjectLabel = ref('项目信息')
const editableProjectName = ref('项目名称')

// Logo 上传相关
const logoInputRef = ref<HTMLInputElement | null>(null)
const customLogoUrl = ref<string>('')

// PDF 导出相关
const paperRef = ref<HTMLElement | null>(null)
const isDownloading = ref(false)

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

  const reader = new FileReader()
  reader.onload = (e) => {
    const result = e.target?.result as string
    customLogoUrl.value = result
    // 保存到 localStorage 以便持久化
    localStorage.setItem('quotation_custom_logo', result)
  }
  reader.readAsDataURL(file)

  // 清空 input 以便重复选择同一文件
  input.value = ''
}

// 初始化时从 localStorage 加载手动上传的 Logo
// 优先级：localStorage 手动上传 > 个人设置公司 Logo > 默认 SVG
function loadCustomLogo() {
  const savedLogo = localStorage.getItem('quotation_custom_logo')
  if (savedLogo) {
    customLogoUrl.value = savedLogo
  }
}

// 组件挂载时加载自定义 Logo
onMounted(() => {
  loadCustomLogo()
})

// 切换公司时，若无手动上传 Logo，则同步切换为所选公司的 Logo
watch(selectedCompanyId, (newId) => {
  if (!newId) return
  const savedLogo = localStorage.getItem('quotation_custom_logo')
  if (savedLogo) return // 用户手动上传过，不覆盖
  const company = companiesList.value.find((c: any) => c.id === newId)
  if (company && company.company_logo) {
    customLogoUrl.value = company.company_logo
  } else {
    customLogoUrl.value = ''
  }
})

// Window size
const windowSize = ref({ width: 1400, height: 800 })

// Date
const currentYear = new Date().getFullYear()
const currentMonth = new Date().getMonth() + 1
const currentDay = new Date().getDate()
const quotationDate = ref(`${currentYear}-${String(currentMonth).padStart(2, '0')}-${String(currentDay).padStart(2, '0')}`)

const expiryDate = computed(() => {
  const date = new Date()
  date.setDate(date.getDate() + parseInt(validityPeriod.value))
  return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`
})

// Helper function to get service months
function getServiceMonths(row: any): number {
  const count = row.serviceCycleCount || 1
  if (row.cycleUnit === 'year') return count * 12
  if (row.cycleUnit === 'day') return Math.round(count / 30 * 10) / 10
  return count
}

// 直接使用前端传递的已计算金额，不再重新计算
// 获取项目总额（最终价格，含所有成本、利润、增值税、账期成本）
function getFinalProjectAmount(): number {
  return props.data.calculatedAmounts?.finalProjectAmount || 0
}

// 获取增值税金额
// 公式：项目总额 × 增值税率 / (1 + 增值税率)
function getVatAmount(): number {
  const finalAmount = getFinalProjectAmount()
  const vatRate = (props.data.calculatedAmounts?.vatRate || 6) / 100
  return finalAmount * vatRate / (1 + vatRate)
}

// 获取人力成本小计（含所有成本项，税前）
// 公式：项目总额 / (1 + 增值税率)
function getLaborCostBeforeVat(): number {
  const finalAmount = getFinalProjectAmount()
  const vatRate = (props.data.calculatedAmounts?.vatRate || 6) / 100
  return finalAmount / (1 + vatRate)
}

// 计算单行岗位的总价
// 根据该岗位在总成本中的占比，按比例分配项目总额
function getRowTotalPrice(row: any): number {
  const finalAmount = getFinalProjectAmount()
  const rowRatio = row.rowRatio || 0
  return finalAmount * rowRatio
}

// 计算单行岗位的综合单价（每人每月）
// 公式：岗位总价 / 人数 / 服务周期（月）
function getRowUnitPrice(row: any): number {
  const totalPrice = getRowTotalPrice(row)
  const personnel = row.personnelCount || 1
  const months = getServiceMonths(row)
  return totalPrice / personnel / months
}

const windowStyle = computed(() => {
  if (isMaximized.value) {
    return {
      left: '0px',
      top: '0px',
      width: '100vw',
      height: 'calc(100vh - 70px)',
      transform: 'none'
    }
  }
  return {
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    width: `${windowSize.value.width}px`,
    height: `${windowSize.value.height}px`
  }
})

// Methods
function formatCurrency(num: number): string {
  return '¥ ' + (num || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function close() {
  emit('close')
}

function zoomIn() {
  if (zoomLevel.value < 150) zoomLevel.value += 10
}

function zoomOut() {
  if (zoomLevel.value > 50) zoomLevel.value -= 10
}

function toggleMaximize() {
  isMaximized.value = !isMaximized.value
  if (isMaximized.value) {
    sidebarOpen.value = false
  }
}

async function downloadQuotation() {
  if (!paperRef.value || isDownloading.value) return

  isDownloading.value = true

  try {
    // 临时重置缩放以获取完整尺寸
    const originalTransform = paperRef.value.style.transform
    paperRef.value.style.transform = 'scale(1)'

    // 临时将 input 元素替换为 p 元素以确保正确渲染
    const inputs = paperRef.value.querySelectorAll('input.editable-input')
    const inputData: { input: HTMLInputElement; p: HTMLParagraphElement; parent: ParentNode }[] = []

    inputs.forEach((input) => {
      const inputEl = input as HTMLInputElement
      const p = document.createElement('p')
      p.textContent = inputEl.value

      // 根据原始 input 的 class 设置对应的样式 class
      if (inputEl.classList.contains('info-label')) {
        p.className = 'info-label'
      } else if (inputEl.classList.contains('info-value-bold')) {
        p.className = 'info-value-bold'
      }

      if (inputEl.parentNode) {
        inputData.push({ input: inputEl, p, parent: inputEl.parentNode })
        inputEl.parentNode.replaceChild(p, inputEl)
      }
    })

    // 使用 html2canvas 捕获报价单内容
    const canvas = await html2canvas(paperRef.value, {
      scale: 2, // 提高清晰度
      useCORS: true,
      allowTaint: true,
      backgroundColor: '#ffffff',
      logging: false
    })

    // 恢复 input 元素
    inputData.forEach(({ input, p, parent }) => {
      parent.replaceChild(input, p)
    })

    // 恢复原始缩放
    paperRef.value.style.transform = originalTransform

    // 创建 PDF (A4 尺寸)
    const pdf = new jsPDF({
      orientation: 'portrait',
      unit: 'mm',
      format: 'a4'
    })

    const imgData = canvas.toDataURL('image/png')
    const pdfWidth = pdf.internal.pageSize.getWidth()
    const pdfHeight = pdf.internal.pageSize.getHeight()

    // 计算图片在 PDF 中的尺寸，保持比例
    const imgWidth = canvas.width
    const imgHeight = canvas.height
    const ratio = Math.min(pdfWidth / imgWidth, pdfHeight / imgHeight)
    const finalWidth = imgWidth * ratio
    const finalHeight = imgHeight * ratio

    // 居中放置
    const x = (pdfWidth - finalWidth) / 2
    const y = 0

    pdf.addImage(imgData, 'PNG', x, y, finalWidth, finalHeight)

    // 生成文件名
    const date = new Date()
    const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
    const fileName = `驻场服务报价单_${selectedCompanyInfo.value.companyName}_${dateStr}.pdf`

    // 下载 PDF
    pdf.save(fileName)

  } catch (error) {
    console.error('PDF 生成失败:', error)
    alert('PDF 生成失败，请重试')
  } finally {
    isDownloading.value = false
  }
}

function sendEmail() {
  // TODO: Implement email logic
  console.log('Sending quotation email')
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 9999;
}

.modal-window {
  position: fixed;
  background-color: #0f131a;
  border: 1px solid #2d3748;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.modal-window.maximized {
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
}

/* Header */
.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #2d3748;
  background-color: #151b26;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #92a4c9;
}

.breadcrumb-link {
  color: #92a4c9;
}

.breadcrumb-current {
  color: #fff;
  font-weight: 500;
}

.header-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.preview-badge {
  font-size: 0.7rem;
  font-weight: 400;
  color: #9ca3af;
  background-color: #1f2937;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #374151;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.5rem;
  background-color: #232f48;
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
}

.zoom-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
}

.zoom-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.zoom-level {
  font-size: 0.7rem;
  color: #d1d5db;
  font-family: monospace;
  min-width: 2.5rem;
  text-align: center;
}

.config-toggle,
.fullscreen-btn,
.close-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background-color: #232f48;
  border: 1px solid #2d3748;
  border-radius: 0.5rem;
  color: #d1d5db;
  font-size: 0.7rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.config-toggle:hover,
.fullscreen-btn:hover {
  background-color: #2d3b55;
  color: #fff;
}

.close-btn:hover {
  background-color: #dc2626;
  color: #fff;
  border-color: #dc2626;
}

/* Content */
.modal-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.content-wrapper {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.preview-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  background-color: #0b0e14;
  display: flex;
  justify-content: center;
}

.preview-area::-webkit-scrollbar {
  width: 8px;
}

.preview-area::-webkit-scrollbar-track {
  background: #0b0e14;
}

.preview-area::-webkit-scrollbar-thumb {
  background: #2d3748;
  border-radius: 4px;
}

.preview-area::-webkit-scrollbar-thumb:hover {
  background: #4a5568;
}

/* Paper */
.paper {
  position: relative;
  background-color: #fff;
  color: #1e293b;
  width: 210mm;
  min-height: 297mm;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
  margin: 0 auto;
  padding: 15mm;
  transform-origin: top center;
}

.watermark {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) rotate(-45deg);
  font-size: 4rem;
  font-weight: 900;
  color: rgba(220, 38, 38, 0.1);
  white-space: nowrap;
  pointer-events: none;
  user-select: none;
}

.paper-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  min-height: 900px;
}

/* Paper Header */
.paper-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #1e293b;
}

.company-info {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
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

.company-logo-default {
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

.company-full-name {
  margin-top: 0.25rem;
}

.company-name-text {
  font-size: 0.875rem;
  color: #334155;
  font-weight: 500;
}

.title-section {
  text-align: right;
}

.document-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: #1e293b;
  margin-bottom: 0.25rem;
}

.document-number {
  font-size: 0.875rem;
  color: #64748b;
  font-family: monospace;
}

/* Info Grid */
.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.info-item-right {
  text-align: right;
  min-width: 180px;
}

.info-label {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
}

.info-value {
  font-size: 0.875rem;
  color: #64748b;
}

.info-value-bold {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
}

.editable-input {
  background: transparent;
  border: none;
  outline: none;
  padding: 0;
  margin: 0;
  width: 100%;
  text-align: inherit;
  font-family: inherit;
  transition: background-color 0.2s;
}

.editable-input:hover {
  background-color: rgba(59, 130, 246, 0.08);
  border-radius: 0.25rem;
}

.editable-input:focus {
  background-color: rgba(59, 130, 246, 0.12);
  border-radius: 0.25rem;
}

input.info-label.editable-input {
  font-size: 0.75rem;
  color: #9ca3af;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.5rem;
  min-width: 120px;
  width: 100%;
  box-sizing: border-box;
}

input.info-value-bold.editable-input {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  min-width: 150px;
  width: 100%;
  box-sizing: border-box;
}

.info-expiry {
  color: #dc2626;
  font-weight: 500;
}

/* Services Table */
.services-table {
  width: 100%;
  font-size: 0.875rem;
  margin-bottom: 2rem;
  border-collapse: collapse;
}

.services-table thead tr {
  background-color: #1e293b;
  color: #fff;
}

.services-table th {
  padding: 0.75rem 1rem;
  font-weight: 500;
  text-align: right;
}

.services-table th.text-left {
  text-align: left;
  border-top-left-radius: 0.25rem;
}

.services-table th:last-child {
  border-top-right-radius: 0.25rem;
}

.services-table tbody tr {
  border-bottom: 1px solid #e2e8f0;
}

.services-table td {
  padding: 1rem;
  color: #64748b;
  text-align: right;
}

.services-table td.text-left,
.services-table td.service-name {
  text-align: left;
}

.name-bold {
  font-weight: 700;
  color: #0f172a;
}

.name-detail {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

/* Summary Section */
.summary-section {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 4rem;
}

.summary-card {
  width: 50%;
  background-color: #f8fafc;
  padding: 1.5rem;
  border-radius: 0.5rem;
  border: 1px solid #e2e8f0;
}

.summary-row {
  display: flex;
  justify-content: space-between;
  color: #64748b;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.summary-row-total {
  border-top: 2px solid #e2e8f0;
  padding-top: 1rem;
  margin-top: 1rem;
}

.summary-value {
  font-family: monospace;
}

.summary-total-label {
  font-weight: 700;
  color: #0f172a;
  font-size: 1rem;
}

.summary-total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #1d4ed8;
  font-family: monospace;
}

/* Footer */
.paper-footer {
  margin-top: auto;
  padding-top: 2rem;
  border-top: 1px solid #e2e8f0;
  position: relative;
}

.footer-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 3rem;
}

.notes-title {
  font-size: 0.875rem;
  color: #64748b;
  margin-bottom: 2rem;
}

.notes-text {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.75;
}

.footer-signature {
  position: relative;
}

.stamp {
  position: absolute;
  top: -3.5rem;
  right: 2.5rem;
  width: 8rem;
  height: 8rem;
  border: 4px solid #dc2626;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0.85;
  transform: rotate(-15deg);
  pointer-events: none;
  color: #dc2626;
  font-weight: 700;
  text-align: center;
  font-size: 0.6rem;
}

.signature-line {
  margin-left: auto;
  position: relative;
  z-index: 2;
  text-align: right;
}

.signature-label {
  font-size: 0.875rem;
  color: #1e293b;
  font-weight: 600;
  white-space: nowrap;
}

.signature-name {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.25rem;
  white-space: nowrap;
}

/* Sidebar */
.sidebar-toggle {
  position: absolute;
  opacity: 0;
  pointer-events: none;
}

.sidebar-panel {
  width: 0;
  overflow: hidden;
  flex-shrink: 0;
  transition: width 0.3s ease;
  position: relative;
}

.sidebar-panel.open {
  width: 380px;
  margin-left: 1rem;
}

.sidebar-content {
  width: 380px;
  min-width: 380px;
  display: flex;
  flex-direction: column;
  background-color: #1a202c;
  border-radius: 0.75rem;
  border: 1px solid #2d3748;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  height: 100%;
  overflow: hidden;
}

.sidebar-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #2d3748;
  background-color: #151b26;
}

.sidebar-title {
  font-size: 0.9rem;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sidebar-title .material-symbols-outlined {
  color: #007aff;
}

.sidebar-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.5rem;
}

.config-section {
  margin-bottom: 1.5rem;
}

.config-label {
  font-size: 0.7rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
  margin-bottom: 0.5rem;
}

.format-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.format-option {
  cursor: pointer;
}

.format-option input {
  display: none;
}

.format-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
  background-color: #232f48;
  height: 4.5rem;
  transition: all 0.2s;
}

.format-option:hover .format-card {
  background-color: #2d3b55;
}

.format-option.active .format-card {
  border-color: #007aff;
  background-color: rgba(0, 122, 255, 0.1);
  box-shadow: 0 0 10px rgba(0, 122, 255, 0.2);
}

.format-icon {
  font-size: 1.5rem;
}

.format-icon.pdf {
  color: #ef4444;
}

.format-icon.excel {
  color: #22c55e;
}

.format-icon.word {
  color: #60a5fa;
}

.format-name {
  font-size: 0.65rem;
  font-weight: 500;
  color: #d1d5db;
}

.format-option.active .format-name {
  color: #fff;
}

.config-card {
  background-color: #232f48;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
}

.input-group {
  margin-bottom: 0.75rem;
}

.input-group:last-child {
  margin-bottom: 0;
}

.input-label {
  font-size: 0.7rem;
  color: #9ca3af;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.25rem;
}

.input-icon {
  font-size: 0.875rem;
  color: #64748b;
}

.input-value {
  font-size: 0.7rem;
  color: #007aff;
}

.config-input {
  width: 100%;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  color: #fff;
  font-size: 0.75rem;
  border-radius: 0.25rem;
  padding: 0.375rem 0.5rem;
}

.config-input:focus {
  outline: none;
  border-color: #007aff;
}

.slider {
  width: 100%;
  height: 0.25rem;
  background-color: #374151;
  border-radius: 9999px;
  appearance: none;
  cursor: pointer;
}

.slider::-webkit-slider-thumb {
  appearance: none;
  width: 0.75rem;
  height: 0.75rem;
  background-color: #007aff;
  border-radius: 50%;
  cursor: pointer;
}

.config-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.config-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  background-color: #232f48;
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
}

.config-item-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.config-icon {
  font-size: 1rem;
}

.config-icon.blue {
  color: #3b82f6;
}

.config-icon.purple {
  color: #a855f7;
}

.config-item-text {
  font-size: 0.75rem;
  color: #e5e7eb;
}

/* Toggle Switch */
.toggle-switch {
  position: relative;
  display: inline-block;
  width: 2rem;
  height: 1rem;
}

.toggle-switch input {
  display: none;
}

.toggle-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #4b5563;
  transition: 0.3s;
  border-radius: 9999px;
}

.toggle-slider:before {
  position: absolute;
  content: "";
  height: 0.75rem;
  width: 0.75rem;
  left: 0.125rem;
  bottom: 0.125rem;
  background-color: #fff;
  transition: 0.3s;
  border-radius: 50%;
}

.toggle-switch input:checked + .toggle-slider {
  background-color: #007aff;
}

.toggle-switch input:checked + .toggle-slider:before {
  transform: translateX(1rem);
}

.config-select {
  width: 100%;
  background-color: #232f48;
  border: 1px solid #2d3748;
  color: #fff;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  padding: 0.5rem;
  appearance: none;
}

.mt-4 {
  margin-top: 1rem;
}

.sidebar-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #2d3748;
  background-color: #151b26;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.btn-download,
.btn-email {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  font-weight: 600;
  padding: 0.625rem 0.875rem;
  border-radius: 0.5rem;
  font-size: 0.8rem;
  transition: all 0.2s;
}

.btn-download {
  background-color: #007aff;
  color: #fff;
  border: none;
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.3);
}

.btn-download:hover:not(:disabled) {
  background-color: #0062cc;
}

.btn-download:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinning {
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

.btn-email {
  background-color: transparent;
  color: #d1d5db;
  border: 1px solid #4b5563;
}

.btn-email:hover {
  border-color: #9ca3af;
  background-color: rgba(255, 255, 255, 0.05);
  color: #fff;
}

/* Transition */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-window,
.modal-leave-to .modal-window {
  opacity: 0;
  transform: translate(-50%, -45%);
}
</style>
