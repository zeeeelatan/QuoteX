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
                        <h3 class="document-title">{{ documentTitle }}</h3>
                        <p class="document-number">编号: Q{{ currentYear }}{{ String(currentMonth).padStart(2, '0') }}{{ String(currentDay).padStart(2, '0') }}-XA009</p>
                      </div>
                    </div>

                    <!-- Info Grid -->
                    <div class="info-grid">
                      <div class="info-item">
                        <p class="info-label">报价公司信息</p>
                        <textarea
                          v-model="editableCompanyInfo.companyName"
                          class="quote-inline-input quote-wrap-field info-value-bold"
                          rows="1"
                          aria-label="报价公司名称"
                          placeholder="请输入报价公司名称"
                          @input="autoGrowTextarea"
                        ></textarea>
                        <div class="editable-info-row info-value">
                          <span>联系人：</span>
                          <input v-model="editableCompanyInfo.contactName" class="quote-inline-input compact" aria-label="报价公司联系人" placeholder="联系人" />
                        </div>
                        <label class="editable-info-row info-value">
                          <span>联系电话：</span>
                          <input v-model="editableCompanyInfo.contactPhone" class="quote-inline-input" aria-label="报价公司联系电话" placeholder="联系电话" />
                        </label>
                      </div>
                      <div class="info-item">
                        <p class="info-label">客户信息</p>
                        <textarea
                          v-model="editableCustomerInfo.customerName"
                          class="quote-inline-input quote-wrap-field info-value-bold"
                          rows="1"
                          aria-label="客户名称"
                          placeholder="请输入客户名称"
                          @input="autoGrowTextarea"
                        ></textarea>
                        <label class="editable-info-row info-value">
                          <span>地址：</span>
                          <textarea
                            v-model="editableCustomerInfo.customerAddress"
                            class="quote-inline-input quote-wrap-field"
                            rows="1"
                            aria-label="客户地址"
                            placeholder="客户地址"
                            @input="autoGrowTextarea"
                          ></textarea>
                        </label>
                      </div>
                      <div class="info-item info-item-right">
                        <p
                          class="info-label editable-field"
                          contenteditable="true"
                          spellcheck="false"
                          @blur="onProjectLabelBlur"
                          @keydown.enter.prevent="blurEditableField"
                        >{{ editableProjectLabel }}</p>
                        <p
                          ref="projectNameElement"
                          class="info-value-bold editable-field"
                          :class="{ 'project-name-placeholder': !editableProjectName }"
                          contenteditable="true"
                          spellcheck="false"
                          data-placeholder="请输入项目名称"
                          @input="onProjectNameInput"
                          @compositionstart="onProjectNameCompositionStart"
                          @compositionend="onProjectNameCompositionEnd"
                          @blur="onProjectNameBlur"
                          @keydown.enter.prevent="blurEditableField"
                        ></p>
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
                          <th class="text-right">综合单价 (CNY/人/月)</th>
                          <th class="text-right">总价 (CNY)</th>
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
                        <div v-if="isOverseasQuote" class="summary-row">
                          <span>完全成本（{{ costCurrency }}）</span>
                          <span class="summary-value">{{ costCurrencySymbol }} {{ formatLocalCost(data.calculatedAmounts?.costTotalLocal ?? data.calculatedAmounts?.costTotalKrw) }}</span>
                        </div>
                        <div v-if="isOverseasQuote" class="summary-row">
                          <span>{{ costCurrency }}/CNY 汇率</span>
                          <span class="summary-value">
                            {{ data.calculatedAmounts?.exchangeRate }}
                            <template v-if="data.calculatedAmounts?.exchangeRateDate">（{{ data.calculatedAmounts.exchangeRateDate }}）</template>
                            <template v-if="data.calculatedAmounts?.exchangeRateSource"> · {{ data.calculatedAmounts.exchangeRateSource }}</template>
                          </span>
                        </div>
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

                    <!-- Footer：服务条款独占分割线下方全宽，落款置于条款之后 -->
                    <div class="paper-footer">
                      <div class="footer-notes">
                        <p class="notes-title">服务条款：</p>
                        <div v-if="currentServiceTermsLines.length" class="notes-text terms-lines">
                          <p
                            v-for="(line, index) in currentServiceTermsLines"
                            :key="`${selectedServiceTermId}-${index}`"
                            class="terms-line"
                          >{{ line || '\u00a0' }}</p>
                        </div>
                        <p v-else class="notes-text terms-empty">未选择服务条款</p>
                      </div>
                      <div class="footer-signature">
                        <div class="signature-block">
                          <p class="signature-company">{{ selectedCompanyInfo.companyName }}</p>
                          <p class="signature-date">日期：{{ quotationDate }}</p>
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
                          <select
                            v-model="selectedCompanyId"
                            class="config-select"
                            @change="onCompanySelectChange"
                          >
                            <option v-for="company in companiesList" :key="company.id" :value="company.id">
                              {{ company.company_name }}
                            </option>
                            <option :value="ADD_COMPANY_OPTION">＋ 新增报价公司</option>
                          </select>
                        </div>
                        <div class="input-group">
                          <label class="input-label">
                            <span class="material-symbols-outlined input-icon">person</span>
                            客户信息
                          </label>
                          <select
                            v-model="selectedCustomerId"
                            class="config-select"
                            @change="onCustomerSelectChange"
                          >
                            <option v-for="customer in customersList" :key="customer.id" :value="customer.id">
                              {{ customer.customer_name }}
                            </option>
                            <option :value="ADD_CUSTOMER_OPTION">＋ 新增客户信息</option>
                          </select>
                        </div>
                      </div>
                    </div>

                    <!-- Service Terms -->
                    <div class="config-section">
                      <label class="config-label">服务条款</label>
                      <div class="config-card">
                        <div class="input-group">
                          <label class="input-label">
                            <span class="material-symbols-outlined input-icon">policy</span>
                            条款模板
                          </label>
                          <select
                            v-model="selectedServiceTermId"
                            class="config-select"
                            :disabled="serviceTermsLoading"
                          >
                            <option value="none">不显示服务条款</option>
                            <option
                              v-for="term in serviceTermsList"
                              :key="term.id"
                              :value="String(term.id)"
                            >
                              {{ term.name }}
                            </option>
                          </select>
                        </div>
                        <p v-if="serviceTermsLoading" class="config-status">正在加载后台服务条款...</p>
                        <p v-else-if="serviceTermsError" class="config-status error">{{ serviceTermsError }}</p>
                        <p v-else-if="selectedServiceTerm" class="config-status">
                          已选择：{{ selectedServiceTerm.name }}
                        </p>
                      </div>
                    </div>

                    <!-- Validity -->
                    <div class="config-section">
                      <label class="config-label">报价单有效期</label>
                      <div class="config-card">
                        <div class="input-group">
                          <select v-model="validityPeriod" class="config-select">
                            <option value="15">15 天</option>
                            <option value="30">30 天</option>
                            <option value="60">60 天</option>
                            <option value="90">90 天</option>
                          </select>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div class="sidebar-footer">
                    <button class="btn-download" @click="downloadQuotation" :disabled="isDownloading">
                      <span v-if="isDownloading" class="material-symbols-outlined spinning">progress_activity</span>
                      <span v-else class="material-symbols-outlined">download</span>
                      {{ isDownloading ? '生成中...' : exportFormat === 'excel' ? '下载 Excel' : '下载 PDF' }}
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

    <!-- 快捷新增报价公司 -->
    <el-dialog
      v-model="showAddCompanyDialog"
      title="新增报价公司"
      width="480px"
      append-to-body
      :z-index="11000"
      destroy-on-close
      class="quick-add-dialog"
      @closed="resetAddCompanyForm"
    >
      <div class="quick-add-form">
        <div class="quick-add-field">
          <label class="quick-add-label">公司名称 <span class="required">*</span></label>
          <el-input v-model="newCompanyForm.company_name" placeholder="例如：北京源晨动力技术服务有限公司" maxlength="100" />
        </div>
        <div class="quick-add-field">
          <label class="quick-add-label">公司地址</label>
          <el-input
            v-model="newCompanyForm.company_address"
            type="textarea"
            :rows="2"
            placeholder="办公地址"
            maxlength="200"
          />
        </div>
        <div class="quick-add-field">
          <label class="quick-add-label">公司网站</label>
          <el-input v-model="newCompanyForm.company_website" placeholder="https://..." maxlength="200" />
        </div>
      </div>
      <template #footer>
        <div class="actions">
          <el-button @click="showAddCompanyDialog = false">取消</el-button>
          <el-button type="primary" :loading="isCreatingCompany" @click="createAndSelectCompany">
            创建并选用
          </el-button>
        </div>
      </template>
    </el-dialog>

    <!-- 快捷新增客户 -->
    <el-dialog
      v-model="showAddCustomerDialog"
      title="新增客户信息"
      width="480px"
      append-to-body
      :z-index="11000"
      destroy-on-close
      class="quick-add-dialog"
      @closed="resetAddCustomerForm"
    >
      <div class="quick-add-form">
        <div class="quick-add-field">
          <label class="quick-add-label">客户名称 <span class="required">*</span></label>
          <el-input v-model="newCustomerForm.customer_name" placeholder="例如：未来科技集团" maxlength="100" />
        </div>
        <div class="quick-add-field">
          <label class="quick-add-label">联系人</label>
          <el-input v-model="newCustomerForm.contact_person" placeholder="联系人姓名" maxlength="50" />
        </div>
        <div class="quick-add-field">
          <label class="quick-add-label">联系电话</label>
          <el-input v-model="newCustomerForm.contact_phone" placeholder="联系电话" maxlength="30" />
        </div>
        <div class="quick-add-field">
          <label class="quick-add-label">客户地址</label>
          <el-input
            v-model="newCustomerForm.customer_address"
            type="textarea"
            :rows="2"
            placeholder="办公地址"
            maxlength="200"
          />
        </div>
      </div>
      <template #footer>
        <div class="actions">
          <el-button @click="showAddCustomerDialog = false">取消</el-button>
          <el-button type="primary" :loading="isCreatingCustomer" @click="createAndSelectCustomer">
            创建并选用
          </el-button>
        </div>
      </template>
    </el-dialog>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import ExcelJS from 'exceljs'
import { saveAs } from 'file-saver'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const props = defineProps<{
  isOpen: boolean
  mode?: 'preview' | 'export'
  data: any
}>()

const emit = defineEmits<{
  close: []
}>()

const isOverseasQuote = computed(() => Boolean(props.data?.country && props.data.country !== 'china'))
const quoteCountryName = computed(() => props.data?.countryName || (props.data?.country === 'korea' ? '韩国' : '中国大陆'))
const costCurrency = computed(() => props.data?.costCurrency || (props.data?.country === 'korea' ? 'KRW' : 'CNY'))
const costCurrencySymbol = computed(() => props.data?.costCurrencySymbol || (props.data?.country === 'korea' ? '₩' : '¥'))
const costCurrencyPrecision = computed(() => Number(props.data?.costCurrencyPrecision ?? (props.data?.country === 'korea' ? 0 : 2)))
const documentTitle = computed(() => isOverseasQuote.value ? `${quoteCountryName.value}驻场服务报价单` : '驻场服务报价单')

// 公司和客户数据
interface CompanyInfo {
  id: number
  company_name: string
  company_address?: string
  company_logo?: string
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

interface ServiceTerm {
  id: number | string
  name: string
  products: string[]
  content: string
}

const ADD_COMPANY_OPTION = '__add_company__'
const ADD_CUSTOMER_OPTION = '__add_customer__'

const companiesList = ref<CompanyInfo[]>([])
const customersList = ref<CustomerInfo[]>([])
const userProfile = ref<UserProfile>({})
const selectedCompanyId = ref<number | string | null>(null)
const selectedCustomerId = ref<number | string | null>(null)
const previousCompanyId = ref<number | null>(null)
const previousCustomerId = ref<number | null>(null)
const serviceTermsList = ref<ServiceTerm[]>([])
const selectedServiceTermId = ref('')
const serviceTermsLoading = ref(false)
const serviceTermsError = ref('')

// 快捷新增报价公司 / 客户（下拉底部入口）
const showAddCompanyDialog = ref(false)
const showAddCustomerDialog = ref(false)
const isCreatingCompany = ref(false)
const isCreatingCustomer = ref(false)
const newCompanyForm = ref({
  company_name: '',
  company_address: '',
  company_website: ''
})
const newCustomerForm = ref({
  customer_name: '',
  contact_person: '',
  contact_phone: '',
  customer_address: ''
})

function resetAddCompanyForm() {
  newCompanyForm.value = {
    company_name: '',
    company_address: '',
    company_website: ''
  }
}

function resetAddCustomerForm() {
  newCustomerForm.value = {
    customer_name: '',
    contact_person: '',
    contact_phone: '',
    customer_address: ''
  }
}

function onCompanySelectChange() {
  if (selectedCompanyId.value === ADD_COMPANY_OPTION) {
    selectedCompanyId.value = previousCompanyId.value
    resetAddCompanyForm()
    showAddCompanyDialog.value = true
    return
  }
  previousCompanyId.value = typeof selectedCompanyId.value === 'number'
    ? selectedCompanyId.value
    : Number(selectedCompanyId.value) || null
}

function onCustomerSelectChange() {
  if (selectedCustomerId.value === ADD_CUSTOMER_OPTION) {
    selectedCustomerId.value = previousCustomerId.value
    resetAddCustomerForm()
    showAddCustomerDialog.value = true
    return
  }
  previousCustomerId.value = typeof selectedCustomerId.value === 'number'
    ? selectedCustomerId.value
    : Number(selectedCustomerId.value) || null
}

async function createAndSelectCompany() {
  const name = newCompanyForm.value.company_name.trim()
  if (!name) {
    ElMessage.warning('请输入公司名称')
    return
  }
  isCreatingCompany.value = true
  try {
    const res = await axios.post(`${API_URL}/user-profile/companies`, {
      company_name: name,
      company_address: newCompanyForm.value.company_address.trim() || null,
      company_website: newCompanyForm.value.company_website.trim() || null
    })
    const created = res.data
    await loadCompaniesAndCustomers()
    if (created?.id) {
      selectedCompanyId.value = created.id
      previousCompanyId.value = created.id
      if (created.company_logo) customLogoUrl.value = created.company_logo
    }
    showAddCompanyDialog.value = false
    ElMessage.success('公司创建成功，已自动选用')
  } catch (error) {
    console.error('创建公司失败', error)
    ElMessage.error('创建公司失败，请重试')
  } finally {
    isCreatingCompany.value = false
  }
}

async function createAndSelectCustomer() {
  const name = newCustomerForm.value.customer_name.trim()
  if (!name) {
    ElMessage.warning('请输入客户名称')
    return
  }
  isCreatingCustomer.value = true
  try {
    const res = await axios.post(`${API_URL}/user-profile/customers`, {
      customer_name: name,
      contact_person: newCustomerForm.value.contact_person.trim() || null,
      contact_phone: newCustomerForm.value.contact_phone.trim() || null,
      customer_address: newCustomerForm.value.customer_address.trim() || null
    })
    const created = res.data
    await loadCompaniesAndCustomers()
    if (created?.id) {
      selectedCustomerId.value = created.id
      previousCustomerId.value = created.id
    }
    showAddCustomerDialog.value = false
    ElMessage.success('客户创建成功，已自动选用')
  } catch (error) {
    console.error('创建客户失败', error)
    ElMessage.error('创建客户失败，请重试')
  } finally {
    isCreatingCustomer.value = false
  }
}

function resolveSelectedId(raw: number | string | null): number | null {
  if (raw === null || raw === '' || raw === ADD_COMPANY_OPTION || raw === ADD_CUSTOMER_OPTION) return null
  const id = Number(raw)
  return Number.isFinite(id) ? id : null
}

// 从用户配置解析当前选中的公司和客户。预览时会复制为临时可编辑数据，
// 不直接修改这里的系统配置来源。
const configuredCompanyInfo = computed(() => {
  const companyId = resolveSelectedId(selectedCompanyId.value)
  if (!companyId) {
    return {
      companyName: props.data.quoteCompanyInfo?.companyName || '报价公司名称',
      contactName: props.data.quoteCompanyInfo?.contactName || userProfile.value.name || '联系人',
      contactPhone: props.data.quoteCompanyInfo?.contactPhone || userProfile.value.phone || '-',
      department: props.data.quoteCompanyInfo?.department || userProfile.value.department || '',
      companyAddress: props.data.quoteCompanyInfo?.companyAddress || ''
    }
  }
  const company = companiesList.value.find(c => c.id === companyId)
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
const configuredCustomerInfo = computed(() => {
  const customerId = resolveSelectedId(selectedCustomerId.value)
  if (!customerId) {
    return {
      customerName: props.data.customerName || '客户名称',
      customerAddress: props.data.customerAddress || '客户地址',
      contactPerson: props.data.customerContact || '',
      contactPhone: props.data.customerPhone || ''
    }
  }
  const customer = customersList.value.find(c => c.id === customerId)
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

const editableCompanyInfo = ref({
  companyName: '',
  contactName: '',
  contactPhone: '',
  department: '',
  companyAddress: ''
})
const editableCustomerInfo = ref({
  customerName: '',
  customerAddress: '',
  contactPerson: '',
  contactPhone: ''
})

// 保留原有导出代码的数据接口，但返回本次预览的临时编辑副本。
const selectedCompanyInfo = computed(() => editableCompanyInfo.value)
const selectedCustomerInfo = computed(() => editableCustomerInfo.value)

function resetEditablePartyInfo() {
  editableCompanyInfo.value = { ...configuredCompanyInfo.value }
  editableCustomerInfo.value = { ...configuredCustomerInfo.value }
  nextTick(resizePartyTextareas)
}

function autoGrowTextarea(event: Event) {
  const element = event.target as HTMLTextAreaElement
  element.style.height = '0px'
  element.style.height = `${element.scrollHeight}px`
}

function resizePartyTextareas() {
  paperRef.value?.querySelectorAll<HTMLTextAreaElement>('.quote-wrap-field').forEach(element => {
    element.style.height = '0px'
    element.style.height = `${element.scrollHeight}px`
  })
}

watch(configuredCompanyInfo, value => {
  if (props.isOpen) {
    editableCompanyInfo.value = { ...value }
    nextTick(resizePartyTextareas)
  }
}, { deep: true })

watch(configuredCustomerInfo, value => {
  if (props.isOpen) {
    editableCustomerInfo.value = { ...value }
    nextTick(resizePartyTextareas)
  }
}, { deep: true })

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
      if (companiesRes.data.length > 0 && !resolveSelectedId(selectedCompanyId.value)) {
        selectedCompanyId.value = companiesRes.data[0].id
        previousCompanyId.value = companiesRes.data[0].id
      } else {
        previousCompanyId.value = resolveSelectedId(selectedCompanyId.value)
      }
      // 若用户未手动上传 Logo，则使用个人设置中的公司 Logo 作为默认
      if (!customLogoUrl.value && companiesRes.data.length > 0) {
        const currentId = resolveSelectedId(selectedCompanyId.value)
        const defaultCompany = companiesRes.data.find((c: any) => c.id === currentId) || companiesRes.data[0]
        if (defaultCompany.company_logo) {
          customLogoUrl.value = defaultCompany.company_logo
        }
      }
    }

    if (customersRes.data) {
      customersList.value = customersRes.data
      // 默认选中第一个客户
      if (customersRes.data.length > 0 && !resolveSelectedId(selectedCustomerId.value)) {
        selectedCustomerId.value = customersRes.data[0].id
        previousCustomerId.value = customersRes.data[0].id
      } else {
        previousCustomerId.value = resolveSelectedId(selectedCustomerId.value)
      }
    }
  } catch (err) {
    console.error('加载公司和客户数据失败', err)
  }
}

async function loadServiceTerms() {
  serviceTermsLoading.value = true
  serviceTermsError.value = ''

  try {
    const response = await axios.get<ServiceTerm[]>(`${API_URL}/service-terms/`)
    serviceTermsList.value = Array.isArray(response.data) ? response.data : []

    const selectionExists = serviceTermsList.value.some(
      term => String(term.id) === selectedServiceTermId.value
    )
    if (!selectionExists) {
      const defaultTerm = serviceTermsList.value.find(term => term.name === '驻场服务条款')
        || serviceTermsList.value.find(term => term.name.includes('驻场'))
        || serviceTermsList.value[0]
      selectedServiceTermId.value = defaultTerm ? String(defaultTerm.id) : 'none'
    }
  } catch (error) {
    console.error('加载服务条款失败', error)
    serviceTermsList.value = []
    selectedServiceTermId.value = 'none'
    serviceTermsError.value = '服务条款加载失败，请检查后端服务'
  } finally {
    serviceTermsLoading.value = false
  }
}

// 当 modal 打开时加载数据
watch(() => props.isOpen, (newVal) => {
  if (newVal) {
    resetEditablePartyInfo()
    editableProjectLabel.value = '项目信息'
    editableProjectName.value = props.data?.projectName?.trim() || ''
    nextTick(() => {
      if (projectNameElement.value) {
        projectNameElement.value.innerText = editableProjectName.value
      }
    })
    loadCompaniesAndCustomers()
    loadServiceTerms()
  } else {
    // 本次手工修改仅用于当前预览；关闭后立即丢弃。
    resetEditablePartyInfo()
  }
})

// UI State
const zoomLevel = ref(100)
const sidebarOpen = ref(true)
const isMaximized = ref(false)
const isMinimized = ref(false)

// Config State
const exportFormat = ref('pdf')
const validityPeriod = ref('15')

function convertServiceTermHtmlToPlainText(html: string): string {
  if (!html) return ''

  const doc = new DOMParser().parseFromString(html, 'text/html')
  const blockTags = new Set([
    'p', 'div', 'section', 'article', 'header', 'footer',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
  ])
  const manualNumberPattern = /^[\s\u00a0]*\d+[.、]/

  const walk = (
    node: Node,
    autoNumber: boolean,
    listType?: 'ol' | 'ul',
    listIndex = 1
  ): string => {
    if (node.nodeType === Node.TEXT_NODE) return node.nodeValue || ''
    if (node.nodeType !== Node.ELEMENT_NODE) return ''

    const element = node as HTMLElement
    const tag = element.tagName.toLowerCase()
    if (tag === 'br') return '\n'

    if (tag === 'ol' || tag === 'ul') {
      const listItems = Array.from(element.children).filter(
        child => child.tagName.toLowerCase() === 'li'
      ) as HTMLElement[]
      let index = 1
      let text = ''
      for (const listItem of listItems) {
        const line = walk(listItem, autoNumber, tag, index)
        if (line.trim()) {
          text += line
          index += 1
        }
      }
      return text
    }

    if (tag === 'li') {
      const content = Array.from(element.childNodes)
        .map(child => walk(child, autoNumber))
        .join('')
      if (!content.replace(/[\s\u00a0]/g, '')) return ''

      const prefix = listType === 'ol' && autoNumber && !manualNumberPattern.test(content)
        ? `${listIndex}. `
        : ''
      const line = `${prefix}${content}`
      return line.endsWith('\n') ? line : `${line}\n`
    }

    const content = Array.from(element.childNodes)
      .map(child => walk(child, autoNumber))
      .join('')
    if (blockTags.has(tag)) {
      return content.replace(/[\s\u00a0]/g, '') ? `${content}\n` : ''
    }
    return content
  }

  const render = (autoNumber: boolean) => {
    let text = ''
    doc.body.childNodes.forEach(child => {
      text += walk(child, autoNumber)
    })
    return text
      .replace(/\r\n?/g, '\n')
      .replace(/\n{3,}/g, '\n\n')
      .replace(/[ \t]+\n/g, '\n')
      .replace(/^\n+|\n+$/g, '')
  }

  const plainText = render(false)
  return /^[ \t\u00a0]*\d+[.、]/m.test(plainText) ? plainText : render(true)
}

const selectedServiceTerm = computed(() => serviceTermsList.value.find(
  term => String(term.id) === selectedServiceTermId.value
) || null)

const currentServiceTermsContent = computed(() => {
  if (!selectedServiceTerm.value || selectedServiceTermId.value === 'none') return ''
  return convertServiceTermHtmlToPlainText(selectedServiceTerm.value.content)
})

const currentServiceTermsLines = computed(() => {
  if (!currentServiceTermsContent.value) return []
  return currentServiceTermsContent.value.split('\n').map(line => line.trimEnd())
})

// 可编辑的项目信息（使用与客户信息相同的 p 标签样式，保证字体一致）
const editableProjectLabel = ref('项目信息')
const editableProjectName = ref('')
const projectNameElement = ref<HTMLElement | null>(null)
const isProjectNameComposing = ref(false)

function blurEditableField(event: Event) {
  ;(event.target as HTMLElement)?.blur()
}

function onProjectLabelBlur(event: FocusEvent) {
  const text = (event.target as HTMLElement).innerText.replace(/\n/g, '').trim()
  editableProjectLabel.value = text || '项目信息'
  ;(event.target as HTMLElement).innerText = editableProjectLabel.value
}

function onProjectNameBlur(event: FocusEvent) {
  const text = (event.target as HTMLElement).innerText.replace(/\n/g, '').trim()
  editableProjectName.value = text
  ;(event.target as HTMLElement).innerText = text
}

function onProjectNameInput(event: Event) {
  if (isProjectNameComposing.value) return
  editableProjectName.value = (event.target as HTMLElement).innerText.replace(/\n/g, '')
}

function onProjectNameCompositionStart() {
  isProjectNameComposing.value = true
}

function onProjectNameCompositionEnd(event: CompositionEvent) {
  isProjectNameComposing.value = false
  editableProjectName.value = (event.target as HTMLElement).innerText.replace(/\n/g, '')
}

// Logo 上传相关
const logoInputRef = ref<HTMLInputElement | null>(null)
const customLogoUrl = ref<string>('')

const DEFAULT_COMPANY_LOGO_SVG = `
<svg width="300" height="88" viewBox="0 0 300 88" xmlns="http://www.w3.org/2000/svg">
  <circle cx="44" cy="44" r="34" fill="none" stroke="#005bac" stroke-width="5"/>
  <path d="M28 44 Q44 21 60 44 Q44 67 28 44" fill="#8dc21f"/>
  <path d="M24 32 Q44 12 64 32" fill="none" stroke="#005bac" stroke-width="4" stroke-linecap="round"/>
  <text x="92" y="39" font-family="Microsoft YaHei, Arial, sans-serif" font-size="24" font-weight="700" fill="#1A3A5C">源晨动力</text>
  <text x="94" y="62" font-family="Arial, sans-serif" font-size="13" font-weight="700" letter-spacing="1.5" fill="#005bac">YUANCHENDONGLI</text>
</svg>`

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

function encodeSvgDataUrl(svg: string): string {
  return `data:image/svg+xml;base64,${btoa(unescape(encodeURIComponent(svg)))}`
}

function getExcelLogoSource(): string {
  return customLogoUrl.value || encodeSvgDataUrl(DEFAULT_COMPANY_LOGO_SVG)
}

function imageSourceToPngDataUrl(source: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image()
    img.onload = () => {
      const naturalWidth = img.naturalWidth || 300
      const naturalHeight = img.naturalHeight || 88
      const canvas = document.createElement('canvas')
      canvas.width = naturalWidth
      canvas.height = naturalHeight
      const ctx = canvas.getContext('2d')
      if (!ctx) {
        reject(new Error('无法创建 Logo 画布'))
        return
      }
      ctx.clearRect(0, 0, naturalWidth, naturalHeight)
      ctx.drawImage(img, 0, 0, naturalWidth, naturalHeight)
      resolve(canvas.toDataURL('image/png'))
    }
    img.onerror = () => reject(new Error('Logo 图片加载失败'))
    if (!source.startsWith('data:')) {
      img.crossOrigin = 'anonymous'
    }
    img.src = source
  })
}

async function addLogoToWorksheet(workbook: ExcelJS.Workbook, worksheet: ExcelJS.Worksheet) {
  try {
    const logoDataUrl = await imageSourceToPngDataUrl(getExcelLogoSource())
    const logoImageId = workbook.addImage({
      base64: logoDataUrl,
      extension: 'png'
    })
    worksheet.addImage(logoImageId, {
      tl: { col: 0.15, row: 0.18 },
      ext: { width: 150, height: 44 }
    })
  } catch (error) {
    console.warn('Logo 写入 Excel 失败，已继续导出报价单:', error)
  }
}

// 组件挂载时加载自定义 Logo
onMounted(() => {
  loadCustomLogo()
})

watch(
  () => [props.isOpen, props.mode] as const,
  ([isOpen]) => {
    if (!isOpen) {
      sidebarOpen.value = false
      return
    }
    sidebarOpen.value = true
  },
  { immediate: true }
)

// 切换公司时，若无手动上传 Logo，则同步切换为所选公司的 Logo
watch(selectedCompanyId, (newId) => {
  const companyId = resolveSelectedId(newId)
  if (!companyId) return
  const savedLogo = localStorage.getItem('quotation_custom_logo')
  if (savedLogo) return // 用户手动上传过，不覆盖
  const company = companiesList.value.find((c: any) => c.id === companyId)
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

function formatLocalCost(num: number): string {
  return Number(num || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: costCurrencyPrecision.value,
    maximumFractionDigits: costCurrencyPrecision.value
  })
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
}

async function downloadQuotation() {
  if (isDownloading.value) return

  // Remove the editing focus outline before capturing the quotation.
  if (document.activeElement instanceof HTMLElement) document.activeElement.blur()
  await nextTick()
  resizePartyTextareas()

  if (exportFormat.value === 'excel') {
    await downloadExcel()
  } else {
    await downloadPDF()
  }
}

// 生成文件名前缀
function getFileNameBase(): string {
  const date = new Date()
  const dateStr = `${date.getFullYear()}${String(date.getMonth() + 1).padStart(2, '0')}${String(date.getDate()).padStart(2, '0')}`
  const prefix = isOverseasQuote.value ? `${quoteCountryName.value}驻场服务报价单` : '驻场服务报价单'
  return `${prefix}_${selectedCompanyInfo.value.companyName}_${dateStr}`
}

// 格式化数字为货币字符串（不带 ¥ 符号，用于 Excel）
function formatNumber(num: number): number {
  return Math.round((num || 0) * 100) / 100
}

/** 页脚页码图（中文），对齐「生成报价单」导出逻辑 */
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

/**
 * PDF 导出：对齐「发起询价 → 生成报价单」流程
 * - onclone 脱离页面布局链，完整渲染条款与落款
 * - 扫描空白行智能分页，避免条款文字被腰斩
 */
async function downloadPDF() {
  if (!paperRef.value) return

  isDownloading.value = true
  const savedScrollX = window.scrollX
  const savedScrollY = window.scrollY
  const paperEl = paperRef.value
  const originalTransform = paperEl.style.transform

  try {
    paperEl.style.transform = 'none'
    await nextTick()
    await new Promise<void>((resolve) => requestAnimationFrame(() => requestAnimationFrame(() => resolve())))

    const html2canvas = (await import('html2canvas')).default
    const { default: jsPDF } = await import('jspdf')

    const a4Width = 210
    const a4Height = 297
    const pageMargin = 10
    const imgWidthMm = a4Width - 2 * pageMargin
    const renderWidth = 794 // ≈ 210mm @ 96dpi

    window.scrollTo(0, 0)

    const fullCanvas = await html2canvas(paperEl, {
      scale: 2,
      useCORS: true,
      allowTaint: true,
      logging: false,
      backgroundColor: '#ffffff',
      windowWidth: renderWidth,
      windowHeight: 50000,
      scrollX: 0,
      scrollY: 0,
      onclone: (clonedDoc: Document, clonedEl: HTMLElement) => {
        clonedEl.remove()
        clonedDoc.body.innerHTML = ''
        clonedDoc.body.style.cssText = 'margin:0;padding:0;overflow:visible;background:white;'
        clonedDoc.documentElement.style.overflow = 'visible'
        clonedDoc.body.appendChild(clonedEl)

        clonedEl.style.cssText = `
          width: ${renderWidth}px;
          max-width: none;
          min-height: 0;
          height: auto;
          overflow: visible;
          display: block;
          padding: 40px 48px 56px;
          background: white;
          color: #0f172a;
          box-shadow: none;
          border-radius: 0;
          position: static;
          transform: none !important;
          box-sizing: border-box;
        `

        // 可编辑字段导出时去掉 contenteditable，保留原有 info-* 样式类
        clonedEl.querySelectorAll('.editable-field').forEach((el) => {
          const node = el as HTMLElement
          node.removeAttribute('contenteditable')
          node.classList.remove('editable-field')
        })
        clonedEl.querySelectorAll('.project-name-placeholder').forEach((el) => {
          const node = el as HTMLElement
          node.textContent = '-'
          node.classList.remove('project-name-placeholder')
          node.removeAttribute('data-placeholder')
        })

        clonedEl.querySelectorAll('.logo-upload-hint').forEach(
          (el) => ((el as HTMLElement).style.display = 'none')
        )

        const pdfStyle = clonedDoc.createElement('style')
        pdfStyle.textContent = `
          *, *::before, *::after { animation: none !important; transition: none !important; }
          .paper-content {
            display: block !important;
            min-height: 0 !important;
            height: auto !important;
            overflow: visible !important;
          }
          .paper-footer {
            margin-top: 28px !important;
            padding-top: 20px !important;
            display: flex !important;
            flex-direction: column !important;
            gap: 28px !important;
            width: 100% !important;
            overflow: visible !important;
            page-break-inside: auto !important;
          }
          .footer-notes {
            width: 100% !important;
          }
          .notes-title {
            margin: 0 0 10px !important;
            color: #334155 !important;
            font-weight: 700 !important;
          }
          .terms-lines {
            display: flex !important;
            flex-direction: column !important;
            gap: 8px !important;
          }
          .terms-line {
            margin: 0 !important;
            color: #475569 !important;
            font-size: 13px !important;
            line-height: 1.7 !important;
            white-space: pre-wrap !important;
            overflow-wrap: anywhere !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
          }
          .footer-signature {
            width: 100% !important;
            display: flex !important;
            justify-content: flex-end !important;
            padding: 12px 0 8px !important;
            margin-top: 8px !important;
            position: relative !important;
            page-break-inside: avoid !important;
            break-inside: avoid !important;
          }
          .signature-block {
            text-align: right !important;
            min-width: 220px !important;
          }
          .signature-company {
            margin: 0 0 8px !important;
            color: #0f172a !important;
            font-size: 14px !important;
            font-weight: 700 !important;
            white-space: nowrap !important;
          }
          .signature-date {
            margin: 0 !important;
            color: #334155 !important;
            font-size: 13px !important;
            font-weight: 500 !important;
            white-space: nowrap !important;
          }
          .data-table, .summary-section, .paper-header, .info-grid {
            page-break-inside: avoid !important;
            break-inside: avoid !important;
          }
        `
        clonedDoc.head.appendChild(pdfStyle)
      }
    })

    // 智能分页：在空白像素行处分页，避免条款被腰斩
    const pxToMm = imgWidthMm / fullCanvas.width
    const pageContentHeightMm = a4Height - 2 * pageMargin
    const pageHeightPx = pageContentHeightMm / pxToMm
    const SEARCH_RANGE = 220
    const PADDING_X = 80
    const SAMPLE_STEP = 6
    const WHITE_THRESHOLD = 245

    const safePageRanges: Array<{ start: number; end: number }> = []
    let currentY = 0
    const fullCtx = fullCanvas.getContext('2d')

    while (currentY < fullCanvas.height) {
      const idealEnd = Math.round(currentY + pageHeightPx)
      if (idealEnd >= fullCanvas.height) {
        safePageRanges.push({ start: currentY, end: fullCanvas.height })
        break
      }

      let safeEnd = idealEnd
      if (fullCtx) {
        const scanTop = Math.max(Math.round(currentY + 80), idealEnd - SEARCH_RANGE)
        const scanHeight = idealEnd - scanTop
        const scanLeft = Math.min(PADDING_X, Math.round(fullCanvas.width * 0.08))
        const scanWidth = Math.max(1, fullCanvas.width - 2 * scanLeft)
        if (scanHeight > 0) {
          const imageData = fullCtx.getImageData(scanLeft, scanTop, scanWidth, scanHeight)
          const data = imageData.data
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

      // 避免分页点几乎不动导致死循环
      if (safeEnd <= currentY + 40) safeEnd = idealEnd
      safePageRanges.push({ start: currentY, end: safeEnd })
      currentY = safeEnd
      if (safePageRanges.length > 40) break
    }

    const doc = new jsPDF({ orientation: 'portrait', unit: 'mm', format: 'a4' })
    const totalPages = safePageRanges.length

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
      const imgHeightMm = (pageCanvas.height / pageCanvas.width) * imgWidthMm
      doc.addImage(
        pageCanvas.toDataURL('image/jpeg', 0.92),
        'JPEG',
        pageMargin,
        pageMargin,
        imgWidthMm,
        imgHeightMm
      )

      const footerImg = createFooterImageDataUrl(pageIdx + 1, totalPages)
      if (footerImg) {
        doc.addImage(
          footerImg,
          'PNG',
          (a4Width - 80) / 2,
          a4Height - pageMargin + 1,
          80,
          4
        )
      }
    }

    doc.save(`${getFileNameBase()}.pdf`)
  } catch (error) {
    console.error('PDF 生成失败:', error)
    alert('PDF 生成失败，请重试')
  } finally {
    paperEl.style.transform = originalTransform
    window.scrollTo(savedScrollX, savedScrollY)
    isDownloading.value = false
  }
}

async function downloadExcel() {
  isDownloading.value = true

  try {
    const wb = new ExcelJS.Workbook()
    wb.creator = selectedCompanyInfo.value.companyName
    wb.created = new Date()

    const ws = wb.addWorksheet('驻场服务报价单', {
      pageSetup: { paperSize: 9, orientation: 'portrait', fitToPage: true }
    })

    // 列宽设置
    ws.columns = [
      { width: 6 },   // A - 序号
      { width: 22 },  // B - 服务岗位
      { width: 14 },  // C - 驻场城市
      { width: 10 },  // D - 人数
      { width: 12 },  // E - 周期(月)
      { width: 18 },  // F - 综合单价
      { width: 18 },  // G - 总价
    ]

    await addLogoToWorksheet(wb, ws)

    // 样式定义
    const titleFont: Partial<ExcelJS.Font> = { name: '微软雅黑', size: 16, bold: true, color: { argb: 'FF1A3A5C' } }
    const headerFont: Partial<ExcelJS.Font> = { name: '微软雅黑', size: 10, bold: true, color: { argb: 'FFFFFFFF' } }
    const labelFont: Partial<ExcelJS.Font> = { name: '微软雅黑', size: 9, color: { argb: 'FF666666' } }
    const valueFont: Partial<ExcelJS.Font> = { name: '微软雅黑', size: 10, bold: true }
    const normalFont: Partial<ExcelJS.Font> = { name: '微软雅黑', size: 10 }
    const headerFill: ExcelJS.FillPattern = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FF1A3A5C' } }
    const altRowFill: ExcelJS.FillPattern = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFF7F9FC' } }
    const totalBgFill: ExcelJS.FillPattern = { type: 'pattern', pattern: 'solid', fgColor: { argb: 'FFEEF3FA' } }
    const thinBorder: Partial<ExcelJS.Borders> = {
      top: { style: 'thin', color: { argb: 'FFD0D5DD' } },
      bottom: { style: 'thin', color: { argb: 'FFD0D5DD' } },
      left: { style: 'thin', color: { argb: 'FFD0D5DD' } },
      right: { style: 'thin', color: { argb: 'FFD0D5DD' } }
    }

    let rowNum = 1

    // ===== 标题 =====
    ws.mergeCells(`A${rowNum}:G${rowNum}`)
    const titleRow = ws.getRow(rowNum)
    titleRow.height = 36
    const titleCell = ws.getCell(`A${rowNum}`)
    titleCell.value = documentTitle.value
    titleCell.font = titleFont
    titleCell.alignment = { horizontal: 'center', vertical: 'middle' }
    rowNum++

    // 编号行
    ws.mergeCells(`A${rowNum}:G${rowNum}`)
    const numCell = ws.getCell(`A${rowNum}`)
    numCell.value = `编号: Q${currentYear}${String(currentMonth).padStart(2, '0')}${String(currentDay).padStart(2, '0')}-XA009`
    numCell.font = { ...labelFont, size: 9 }
    numCell.alignment = { horizontal: 'center', vertical: 'middle' }
    ws.getRow(rowNum).height = 20
    rowNum++

    // 空行
    rowNum++

    // ===== 报价信息 =====
    // 报价公司
    ws.mergeCells(`A${rowNum}:C${rowNum}`)
    ws.getCell(`A${rowNum}`).value = '报价公司信息'
    ws.getCell(`A${rowNum}`).font = labelFont
    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = '客户信息'
    ws.getCell(`E${rowNum}`).font = labelFont
    rowNum++

    ws.mergeCells(`A${rowNum}:C${rowNum}`)
    ws.getCell(`A${rowNum}`).value = selectedCompanyInfo.value.companyName
    ws.getCell(`A${rowNum}`).font = valueFont
    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = selectedCustomerInfo.value.customerName
    ws.getCell(`E${rowNum}`).font = valueFont
    rowNum++

    ws.mergeCells(`A${rowNum}:C${rowNum}`)
    ws.getCell(`A${rowNum}`).value = `联系人：${selectedCompanyInfo.value.contactName}`
    ws.getCell(`A${rowNum}`).font = normalFont
    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = `地址：${selectedCustomerInfo.value.customerAddress}`
    ws.getCell(`E${rowNum}`).font = normalFont
    rowNum++

    ws.mergeCells(`A${rowNum}:C${rowNum}`)
    ws.getCell(`A${rowNum}`).value = `联系电话：${selectedCompanyInfo.value.contactPhone}`
    ws.getCell(`A${rowNum}`).font = normalFont
    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = `报价日期：${quotationDate.value}`
    ws.getCell(`E${rowNum}`).font = normalFont
    rowNum++

    // 项目信息 & 有效期
    ws.mergeCells(`A${rowNum}:C${rowNum}`)
    ws.getCell(`A${rowNum}`).value = `${editableProjectLabel.value}：${editableProjectName.value.trim() || '-'}`
    ws.getCell(`A${rowNum}`).font = normalFont
    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = `有效期至：${expiryDate.value}`
    ws.getCell(`E${rowNum}`).font = normalFont
    rowNum++

    // 空行
    rowNum++

    // ===== 服务明细表头 =====
    const headers = ['序号', '服务岗位', '驻场城市', '人数', '周期(月)', '综合单价(CNY/人/月)', '总价(CNY)']
    const headerRow = ws.getRow(rowNum)
    headerRow.height = 28
    headers.forEach((h, i) => {
      const cell = ws.getCell(rowNum, i + 1)
      cell.value = h
      cell.font = headerFont
      cell.fill = headerFill
      cell.alignment = { horizontal: i >= 3 ? 'right' : 'left', vertical: 'middle' }
      cell.border = thinBorder
    })
    rowNum++

    // ===== 服务明细数据 =====
    const rows = props.data.positionRows || []
    rows.forEach((row: any, index: number) => {
      const months = getServiceMonths(row)
      const unitPrice = getRowUnitPrice(row)
      const totalPrice = getRowTotalPrice(row)
      const dataRow = ws.getRow(rowNum)
      dataRow.height = 24

      const values = [
        index + 1,
        row.position || '服务岗位',
        row.city || '-',
        row.personnelCount || 1,
        months,
        formatNumber(unitPrice),
        formatNumber(totalPrice)
      ]

      values.forEach((v, i) => {
        const cell = ws.getCell(rowNum, i + 1)
        cell.value = v
        cell.font = normalFont
        cell.alignment = { horizontal: i >= 3 ? 'right' : 'left', vertical: 'middle' }
        cell.border = thinBorder
        // 交替行背景
        if (index % 2 === 1) {
          cell.fill = altRowFill
        }
        // 金额列数字格式
        if (i >= 5) {
          cell.numFmt = '#,##0.00'
        }
      })
      rowNum++
    })

    // 空行
    rowNum++

    // ===== 汇总区域 =====
    const laborBeforeVat = getLaborCostBeforeVat()
    const vatRate = props.data.globalParams?.vatRate || 6
    const finalAmount = getFinalProjectAmount()

    const summaryItems = [
      ...(isOverseasQuote.value ? [
        {
          label: `完全成本（${costCurrency.value}）`,
          value: `${costCurrencySymbol.value}${formatLocalCost(props.data.calculatedAmounts?.costTotalLocal ?? props.data.calculatedAmounts?.costTotalKrw)}`
        },
        {
          label: `${costCurrency.value}/CNY 汇率`,
          value: `${props.data.calculatedAmounts?.exchangeRate || 0}${props.data.calculatedAmounts?.exchangeRateDate ? `（${props.data.calculatedAmounts.exchangeRateDate}）` : ''}${props.data.calculatedAmounts?.exchangeRateSource ? ` · ${props.data.calculatedAmounts.exchangeRateSource}` : ''}`
        },
        { label: '我方管理费率', value: `${props.data.calculatedAmounts?.managementRate || 0}%` }
      ] : []),
      { label: '项目总价（未税）', value: formatNumber(laborBeforeVat) },
      { label: '增值税率', value: `${vatRate}%` },
      { label: '项目总价', value: formatNumber(finalAmount) }
    ]

    summaryItems.forEach((item, index) => {
      ws.mergeCells(`A${rowNum}:E${rowNum}`)
      const labelCell = ws.getCell(`A${rowNum}`)
      labelCell.value = item.label
      labelCell.alignment = { horizontal: 'right', vertical: 'middle' }

      ws.mergeCells(`F${rowNum}:G${rowNum}`)
      const valCell = ws.getCell(`F${rowNum}`)
      valCell.alignment = { horizontal: 'right', vertical: 'middle' }

      if (index === summaryItems.length - 1) {
        // 合计行加粗加背景
        labelCell.font = { ...valueFont, size: 12, color: { argb: 'FF1A3A5C' } }
        valCell.value = item.value as number
        valCell.font = { ...valueFont, size: 12, color: { argb: 'FF1A3A5C' } }
        valCell.numFmt = '#,##0.00'
        // 背景
        for (let c = 1; c <= 7; c++) {
          ws.getCell(rowNum, c).fill = totalBgFill
          ws.getCell(rowNum, c).border = thinBorder
        }
        ws.getRow(rowNum).height = 30
      } else {
        labelCell.font = normalFont
        valCell.value = typeof item.value === 'number' ? item.value : item.value
        valCell.font = normalFont
        if (typeof item.value === 'number') {
          valCell.numFmt = '#,##0.00'
        }
        ws.getRow(rowNum).height = 24
      }
      rowNum++
    })

    // 空行
    rowNum++
    rowNum++

    // ===== 服务条款 =====
    const serviceTermLines = currentServiceTermsLines.value
    if (serviceTermLines.length > 0) {
      ws.mergeCells(`A${rowNum}:G${rowNum}`)
      ws.getCell(`A${rowNum}`).value = '服务条款：'
      ws.getCell(`A${rowNum}`).font = { ...valueFont, size: 9 }
      ws.getRow(rowNum).height = 24
      rowNum++

      serviceTermLines.forEach((line) => {
        ws.mergeCells(`A${rowNum}:G${rowNum}`)
        const termCell = ws.getCell(`A${rowNum}`)
        termCell.value = line || ' '
        termCell.font = { ...normalFont, size: 9, color: { argb: 'FF666666' } }
        termCell.alignment = { vertical: 'top', wrapText: true }
        ws.getRow(rowNum).height = line
          ? Math.min(90, Math.max(20, Math.ceil(line.length / 72) * 18))
          : 10
        rowNum++
      })
    }

    // 空行
    rowNum++

    // 签章行
    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = selectedCompanyInfo.value.companyName
    ws.getCell(`E${rowNum}`).font = valueFont
    ws.getCell(`E${rowNum}`).alignment = { horizontal: 'right' }
    rowNum++

    ws.mergeCells(`E${rowNum}:G${rowNum}`)
    ws.getCell(`E${rowNum}`).value = `日期：${quotationDate.value}`
    ws.getCell(`E${rowNum}`).font = normalFont
    ws.getCell(`E${rowNum}`).alignment = { horizontal: 'right' }

    // 导出
    const buffer = await wb.xlsx.writeBuffer()
    saveAs(new Blob([buffer], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }), `${getFileNameBase()}.xlsx`)

  } catch (error) {
    console.error('Excel 生成失败:', error)
    alert('Excel 生成失败，请重试')
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
  /* 禁止把纸张拉伸成视口高度，否则条款会溢出白底且 PDF 截断 */
  align-items: flex-start;
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

/* Paper：高度随内容增长，条款过长时自动拉长白底页面 */
.paper {
  position: relative;
  background-color: #fff;
  color: #1e293b;
  width: 210mm;
  min-height: 297mm;
  height: fit-content;
  box-shadow: 0 0 50px rgba(0, 0, 0, 0.5);
  margin: 0 auto 2rem;
  padding: 15mm;
  transform-origin: top center;
  overflow: visible;
  flex-shrink: 0;
  align-self: flex-start;
  box-sizing: border-box;
}

.paper-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  min-height: calc(297mm - 30mm);
  height: auto;
  overflow: visible;
  box-sizing: border-box;
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
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 1.5rem;
  margin-bottom: 2.5rem;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  min-width: 0;
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
  margin: 0 0 0.5rem;
  line-height: 1.4;
}

.info-value {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.info-value-bold {
  font-size: 0.875rem;
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  line-height: 1.4;
}

.quote-inline-input {
  width: 100%;
  min-width: 0;
  margin: 0;
  padding: 0;
  border: none;
  border-radius: 3px;
  outline: none;
  background: transparent;
  color: inherit;
  font-family: inherit;
  box-sizing: border-box;
  transition: border-color 0.2s, background-color 0.2s, box-shadow 0.2s;
}

.quote-wrap-field {
  display: block;
  min-height: 1.4em;
  overflow: hidden;
  resize: none;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.quote-inline-input:hover {
  background: rgba(59, 130, 246, 0.06);
}

.quote-inline-input:focus {
  background: #eff6ff;
  box-shadow: inset 0 -1px 0 #60a5fa;
}

.editable-info-row {
  display: flex;
  align-items: baseline;
  flex-wrap: wrap;
  min-width: 0;
  margin: 0;
  white-space: normal;
}

.editable-info-row > span {
  flex: 0 0 auto;
}

.editable-info-row .quote-inline-input {
  flex: 1 1 0;
  min-width: 2.5rem;
  font-size: inherit;
  font-weight: inherit;
  line-height: inherit;
}

.editable-info-row .quote-inline-input.compact {
  flex: 0 1 auto;
  width: 7rem;
  field-sizing: content;
}

/* 仅交互反馈，不改字体/颜色，与客户信息保持一致 */
.editable-field {
  outline: none;
  cursor: text;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
  min-height: 1.25em;
}

.editable-field:hover {
  background-color: rgba(59, 130, 246, 0.08);
}

.editable-field:focus {
  background-color: rgba(59, 130, 246, 0.12);
}

.project-name-placeholder::before {
  content: attr(data-placeholder);
  color: #c0c7d1;
  font-weight: 400;
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

/* Footer：分割线以下条款全宽独占，公司落款在条款下方靠右 */
.paper-footer {
  margin-top: auto;
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1.75rem;
  width: 100%;
  overflow: visible;
}

.footer-notes {
  width: 100%;
  min-width: 0;
}

.notes-title {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0 0 0.75rem;
  font-weight: 600;
}

.notes-text {
  font-size: 0.875rem;
  color: #64748b;
  line-height: 1.75;
}

.terms-lines {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
  width: 100%;
}

.terms-line {
  margin: 0;
  white-space: pre-wrap;
  overflow-wrap: anywhere;
  word-break: break-word;
}

.terms-empty {
  color: #94a3b8;
}

.footer-signature {
  position: relative;
  width: 100%;
  display: flex;
  justify-content: flex-end;
  padding-top: 0.75rem;
  margin-top: 0.5rem;
  min-height: 3.5rem;
}

.signature-block {
  position: relative;
  z-index: 2;
  text-align: right;
  min-width: 14rem;
}

.signature-company {
  margin: 0 0 0.4rem;
  font-size: 0.9rem;
  color: #0f172a;
  font-weight: 700;
  white-space: nowrap;
}

.signature-date {
  margin: 0;
  font-size: 0.875rem;
  color: #334155;
  font-weight: 500;
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
  grid-template-columns: repeat(2, 1fr);
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

.quick-add-form {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.quick-add-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.quick-add-label {
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 600;
}

.quick-add-label .required {
  color: #f56c6c;
}

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
  justify-content: flex-end;
}

/* 快捷新增弹窗被 Teleport 到 body，需要使用全局选择器统一 Element Plus 样式 */
:global(.quick-add-dialog.el-dialog) {
  --el-dialog-bg-color: #151d2b;
  --el-text-color-primary: #f8fafc;
  --el-text-color-regular: #cbd5e1;
  --el-border-color: #324467;
  --el-color-primary: #135bec;
  margin-top: 12vh;
  overflow: hidden;
  border: 1px solid #324467;
  border-radius: 12px;
  background: #151d2b;
  box-shadow: 0 28px 70px rgba(0, 0, 0, 0.62);
  font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
}

:global(.quick-add-dialog .el-dialog__header) {
  display: flex;
  align-items: center;
  min-height: 58px;
  margin: 0;
  padding: 0 22px;
  border-bottom: 1px solid #2a3955;
  background: #192233;
}

:global(.quick-add-dialog .el-dialog__title) {
  color: #f8fafc;
  font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
  font-size: 1rem;
  font-weight: 700;
}

:global(.quick-add-dialog .el-dialog__headerbtn) {
  top: 9px;
  right: 12px;
  width: 40px;
  height: 40px;
  border-radius: 8px;
}

:global(.quick-add-dialog .el-dialog__headerbtn:hover) {
  background: rgba(255, 255, 255, 0.06);
}

:global(.quick-add-dialog .el-dialog__headerbtn .el-dialog__close) {
  color: #94a3b8;
  font-size: 18px;
}

:global(.quick-add-dialog .el-dialog__headerbtn:hover .el-dialog__close) {
  color: #fff;
}

:global(.quick-add-dialog .el-dialog__body) {
  padding: 22px;
  color: #cbd5e1;
  background: #151d2b;
}

:global(.quick-add-dialog .el-dialog__footer) {
  padding: 14px 22px 18px;
  border-top: 1px solid #2a3955;
  background: #151d2b;
}

:global(.quick-add-dialog .el-input__wrapper),
:global(.quick-add-dialog .el-textarea__inner) {
  color: #f8fafc;
  background: #0f1623;
  border: 1px solid #324467;
  border-radius: 8px;
  box-shadow: none;
  font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
}

:global(.quick-add-dialog .el-input__wrapper) {
  min-height: 40px;
  padding: 0 12px;
}

:global(.quick-add-dialog .el-input__wrapper:hover),
:global(.quick-add-dialog .el-textarea__inner:hover) {
  border-color: #4d6592;
}

:global(.quick-add-dialog .el-input__wrapper.is-focus),
:global(.quick-add-dialog .el-textarea__inner:focus) {
  border-color: #2f70f3;
  box-shadow: 0 0 0 3px rgba(19, 91, 236, 0.14);
}

:global(.quick-add-dialog .el-input__inner),
:global(.quick-add-dialog .el-textarea__inner) {
  color: #f8fafc;
  font-size: 0.875rem;
}

:global(.quick-add-dialog .el-input__inner::placeholder),
:global(.quick-add-dialog .el-textarea__inner::placeholder) {
  color: #64748b;
}

:global(.quick-add-dialog .el-button) {
  min-width: 82px;
  height: 38px;
  border-color: #3b4d70;
  border-radius: 8px;
  color: #cbd5e1;
  background: #202b40;
  font-family: "Noto Sans SC", "Microsoft YaHei", sans-serif;
  font-weight: 600;
}

:global(.quick-add-dialog .el-button:hover) {
  color: #fff;
  border-color: #5874a8;
  background: #293750;
}

:global(.quick-add-dialog .el-button--primary) {
  color: #fff;
  border-color: #135bec;
  background: #135bec;
}

:global(.quick-add-dialog .el-button--primary:hover) {
  border-color: #2f70f3;
  background: #2f70f3;
}

:global(.el-overlay:has(.quick-add-dialog)) {
  background-color: rgba(4, 8, 15, 0.7);
  backdrop-filter: blur(2px);
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

.config-select:disabled {
  cursor: wait;
  opacity: 0.65;
}

.config-status {
  margin: 0.5rem 0 0;
  color: #92a4c9;
  font-size: 0.7rem;
  line-height: 1.5;
}

.config-status.error {
  color: #fca5a5;
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
