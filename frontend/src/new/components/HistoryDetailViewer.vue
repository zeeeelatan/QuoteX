<template>
  <div class="history-detail-viewer">
    <!-- 全屏弹窗 -->
    <div class="fullscreen-modal">
      <!-- 顶部头 -->
      <header class="viewer-header">
        <div class="header-left">
          <div class="record-badge">
            <span class="material-symbols-outlined">history</span>
            历史记录 #{{ historyData?.id }}
          </div>
          <h1 class="viewer-title">报价流程回溯</h1>
          <p class="viewer-subtitle">
            {{ historyData?.file_name }} · {{ formatDateTime(historyData?.created_at) }}
          </p>
        </div>
        <div class="header-right">
          <div class="readonly-badge">
            <span class="material-symbols-outlined">visibility</span>
            只读模式
          </div>
          <button @click="$emit('close')" class="close-btn">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
      </header>

      <!-- 步骤进度条 -->
      <div class="steps-progress">
        <div 
          v-for="(step, index) in steps" 
          :key="step.key"
          class="step-item"
          :class="{ active: currentStep === step.key, completed: getStepIndex(currentStep) > index }"
          @click="currentStep = step.key"
        >
          <div class="step-number">{{ index + 1 }}</div>
          <div class="step-info">
            <span class="step-label">{{ step.label }}</span>
            <span class="step-count" v-if="getStepDataCount(step.key)">
              {{ getStepDataCount(step.key) }} 条数据
            </span>
          </div>
          <div v-if="index < steps.length - 1" class="step-connector"></div>
        </div>
      </div>

      <!-- 内容区域 -->
      <main class="viewer-content">
        <!-- 步骤1: 导入数据 -->
        <div v-if="currentStep === 'import'" class="step-content">
          <div class="content-header">
            <div class="content-title-area">
              <span class="material-symbols-outlined content-icon">upload_file</span>
              <div>
                <h2 class="content-title">导入数据</h2>
                <p class="content-desc">Excel 数据导入与格式转换</p>
              </div>
            </div>
            <div class="content-stats">
              <div class="stat-item">
                <span class="stat-label">原始数据</span>
                <span class="stat-value">{{ importData?.data?.length || 0 }} 项</span>
              </div>
              <div class="stat-item">
                <span class="stat-label">转换后数据</span>
                <span class="stat-value">{{ importConvertedData?.length || 0 }} 项</span>
              </div>
            </div>
          </div>

          <!-- 双表格并排展示 -->
          <div class="import-tables-row">
            <!-- 原始表格 -->
            <div class="import-table-col">
              <div class="import-table-title">
                <span class="title-text original">原始表格</span>
                <span class="title-badge" v-if="importData?.data?.length">已识别 {{ importData.data.length }} 项</span>
              </div>
              <div class="table-section">
                <div class="table-wrapper import-table-scroll">
                  <table class="data-table readonly" v-if="importData?.headers?.length">
                    <thead>
                      <tr>
                        <th v-for="header in importData.headers" :key="header">{{ header }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in importData?.data?.slice(0, 50)" :key="idx">
                        <td v-for="header in importData.headers" :key="header">
                          {{ row[header] ?? '-' }}
                        </td>
                      </tr>
                      <tr v-if="!importData?.data?.length">
                        <td :colspan="importData?.headers?.length || 1" class="no-data-cell">
                          暂无数据
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-else class="no-data-placeholder">暂无原始数据</div>
                </div>
                <div v-if="importData?.data?.length > 50" class="more-hint">
                  仅显示前 50 条，共 {{ importData.data.length }} 条
                </div>
              </div>
            </div>

            <!-- 转换后表格 -->
            <div class="import-table-col">
              <div class="import-table-title">
                <span class="title-text converted">转换后表格</span>
                <span class="title-badge" v-if="importConvertedData?.length">已识别 {{ importConvertedData.length }} 项</span>
              </div>
              <div class="table-section">
                <div class="table-wrapper import-table-scroll">
                  <table class="data-table readonly" v-if="importConvertedHeaders?.length">
                    <thead>
                      <tr>
                        <th v-for="header in importConvertedHeaders" :key="header">{{ header }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in importConvertedData?.slice(0, 50)" :key="idx">
                        <td v-for="header in importConvertedHeaders" :key="header">
                          {{ row[header] ?? '-' }}
                        </td>
                      </tr>
                      <tr v-if="!importConvertedData?.length">
                        <td :colspan="importConvertedHeaders?.length || 1" class="no-data-cell">
                          暂无数据
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <div v-else class="no-data-placeholder">暂无转换后数据</div>
                </div>
                <div v-if="importConvertedData?.length > 50" class="more-hint">
                  仅显示前 50 条，共 {{ importConvertedData.length }} 条
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 步骤2: 智能匹配 -->
        <div v-if="currentStep === 'match'" class="step-content">
          <div class="content-header">
            <div class="content-title-area">
              <span class="material-symbols-outlined content-icon">link</span>
              <div>
                <h2 class="content-title">智能匹配</h2>
                <p class="content-desc">设备型号匹配结果</p>
              </div>
            </div>
            <div class="content-stats">
              <div class="stat-item">
                <span class="stat-label">总设备</span>
                <span class="stat-value">{{ matchData?.length || 0 }}</span>
              </div>
              <div class="stat-item highlight">
                <span class="stat-label">高匹配度</span>
                <span class="stat-value">{{ highMatchCount }}</span>
              </div>
              <div class="stat-item warning">
                <span class="stat-label">低匹配度</span>
                <span class="stat-value">{{ lowMatchCount }}</span>
              </div>
            </div>
          </div>

          <div class="table-section">
            <div class="table-wrapper">
              <table class="data-table readonly match-table">
                <thead>
                  <tr>
                    <th class="row-num">序号</th>
                    <th>厂商</th>
                    <th>原始品牌型号</th>
                    <th>分类</th>
                    <th>服务级别</th>
                    <th>匹配型号</th>
                    <th>置信度</th>
                    <th>原始单价</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in matchData" :key="idx" :class="getMatchRowClass(item)">
                    <td class="row-num">{{ idx + 1 }}</td>
                    <td>{{ item.manufacturer || '-' }}</td>
                    <td class="model-cell">{{ item.originalBrandModel || item.model || '-' }}</td>
                    <td>{{ item.category || '-' }}</td>
                    <td>{{ item.serviceLevel || '-' }}</td>
                    <td class="matched-model">{{ item.matchedModel || '-' }}</td>
                    <td>
                      <span class="match-rate" :class="getMatchRateClass(item.matchRate)">
                        {{ item.matchRate ? Math.round(item.matchRate) + '%' : '-' }}
                      </span>
                    </td>
                    <td class="price-cell">{{ formatPrice(item.originalPrice) }}</td>
                  </tr>
                  <tr v-if="!matchData?.length">
                    <td colspan="8" class="no-data-cell">暂无数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 步骤3: 价格调整 -->
        <div v-if="currentStep === 'adjust'" class="step-content">
          <div class="content-header">
            <div class="content-title-area">
              <span class="material-symbols-outlined content-icon">tune</span>
              <div>
                <h2 class="content-title">价格调整</h2>
                <p class="content-desc">服务级别系数与最终价格</p>
              </div>
            </div>
            <div class="content-stats">
              <div class="stat-item">
                <span class="stat-label">设备数</span>
                <span class="stat-value">{{ adjustData?.length || 0 }}</span>
              </div>
            </div>
          </div>

          <div class="table-section">
            <div class="table-wrapper">
              <table class="data-table readonly adjust-table">
                <thead>
                  <tr>
                    <th class="row-num">序号</th>
                    <th>产品型号</th>
                    <th>原始品牌型号</th>
                    <th>服务级别</th>
                    <th>城市</th>
                    <th>参考成本</th>
                    <th>建议售价</th>
                    <th>最终报价 (CNY)</th>
                    <th>预估利润</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in adjustData" :key="idx">
                    <td class="row-num">{{ idx + 1 }}</td>
                    <td class="model-cell">{{ item.matchedModel || item.model || '-' }}</td>
                    <td>{{ item.originalBrandModel || '-' }}</td>
                    <td>{{ item.serviceLevel || '-' }}</td>
                    <td>{{ item.city || '-' }}</td>
                    <td class="price-cell">{{ formatPrice(item.referenceCost || item.originalPrice) }}</td>
                    <td class="price-cell">{{ formatPrice(item.suggestedPrice) }}</td>
                    <td class="price-cell final-price">{{ formatPrice(item.finalPrice || item.suggestedPrice) }}</td>
                    <td>
                      <span class="profit-rate" :class="getProfitClass(item.profitMargin)">
                        {{ item.profitMargin ? item.profitMargin.toFixed(1) + '%' : '0.0%' }}
                      </span>
                    </td>
                  </tr>
                  <tr v-if="!adjustData?.length">
                    <td colspan="9" class="no-data-cell">暂无数据</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>

        <!-- 步骤4: 生成报价 -->
        <div v-if="currentStep === 'quote'" class="step-content">
          <div class="content-header">
            <div class="content-title-area">
              <span class="material-symbols-outlined content-icon">receipt</span>
              <div>
                <h2 class="content-title">生成报价</h2>
                <p class="content-desc">最终报价单预览与导出</p>
              </div>
            </div>
            <div class="content-stats">
              <div class="stat-item">
                <span class="stat-label">设备数量</span>
                <span class="stat-value">{{ historyTotalDeviceCount }} 台</span>
              </div>
              <div class="stat-item highlight">
                <span class="stat-label">报价总额</span>
                <span class="stat-value amount">{{ formatPrice(historyData?.total_amount) }}</span>
              </div>
            </div>
          </div>

          <!-- 导出按钮 -->
          <div class="export-actions">
            <button class="export-action-btn pdf" @click="downloadQuotePDF" :disabled="isExporting">
              <span class="material-symbols-outlined">{{ isExporting ? 'hourglass_empty' : 'picture_as_pdf' }}</span>
              {{ isExporting ? '导出中...' : '下载 PDF' }}
            </button>
            <button class="export-action-btn excel" @click="exportQuoteExcel" :disabled="isExporting">
              <span class="material-symbols-outlined">{{ isExporting ? 'hourglass_empty' : 'table_view' }}</span>
              {{ isExporting ? '导出中...' : '导出 Excel' }}
            </button>
          </div>

          <!-- 报价单预览 -->
          <div class="quotation-preview" ref="quotationDocRef">
            <div class="doc-decoration"></div>

            <!-- Document Header -->
            <div class="doc-header">
              <div class="company-info">
                <!-- Logo：优先使用保存的自定义 Logo -->
                <img v-if="quoteMetadata?.company_logo" :src="quoteMetadata.company_logo" alt="公司Logo" class="custom-logo-img" />
                <div v-else class="company-logo">
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
                <h2 class="company-name">{{ quoteMetadata?.company_name || '公司名称' }}</h2>
                <p class="company-address" style="white-space: pre-line;">{{ quoteMetadata?.company_address || '' }}</p>
                <p class="company-contact" v-if="quoteMetadata?.contact_name">联系人：{{ quoteMetadata.contact_name }}</p>
                <p class="company-contact" v-if="quoteMetadata?.contact_phone">电话：{{ quoteMetadata.contact_phone }}</p>
              </div>
              <div class="quote-info">
                <h1 class="doc-title">报价单</h1>
                <p class="quote-number">单号：{{ quoteMetadata?.quote_number || '-' }}</p>
                <p class="quote-date">{{ quoteMetadata?.quote_date || '-' }}</p>
              </div>
            </div>

            <!-- Customer Info -->
            <div class="info-grid">
              <div class="info-block">
                <p class="info-label">客户信息</p>
                <p class="customer-name">{{ quoteMetadata?.customer_company || quoteMetadata?.customer_name || '-' }}</p>
                <p class="company-contact" v-if="quoteMetadata?.customer_address" style="white-space: pre-line;">{{ quoteMetadata.customer_address }}</p>
                <p class="company-contact" v-if="quoteMetadata?.customer_contact_person">联系人：{{ quoteMetadata.customer_contact_person }}</p>
                <p class="company-contact" v-if="quoteMetadata?.customer_contact_phone">电话：{{ quoteMetadata.customer_contact_phone }}</p>
              </div>
              <div class="info-block text-right">
                <p class="info-label">有效期</p>
                <p class="validity-date">{{ quoteMetadata?.validity_date || '-' }}之前有效</p>
              </div>
            </div>

            <!-- Items Table -->
            <div class="items-table">
              <table class="quote-table">
                <thead>
                  <tr>
                    <th class="col-no">序号</th>
                    <th class="col-desc">项目描述</th>
                    <th class="col-qty">数量</th>
                    <th class="col-price">单价</th>
                    <th class="col-total">总价</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-if="!quoteMetadata?.table_data?.length">
                    <td colspan="5" class="no-data-cell">暂无数据</td>
                  </tr>
                  <tr v-for="(item, index) in quoteMetadata?.table_data" :key="index" class="item-row">
                    <td class="text-center col-no">{{ index + 1 }}</td>
                    <td class="item-desc">
                      <p class="item-name">{{ item.model || '未命名产品' }}</p>
                      <p class="item-detail">
                        厂商: {{ formatManufacturer(item.matchedManufacturer) || '-' }}
                        <span v-if="item.matchedSeries"> | 系列: {{ item.matchedSeries }}</span>
                        <span v-if="item.serviceLevel"> | 服务级别: {{ item.serviceLevel }}</span>
                        <span v-if="item.servicePeriodUnit"> | 周期: {{ item.servicePeriodUnit }}</span>
                      </p>
                    </td>
                    <td class="text-center">{{ item.quantity || 1 }}</td>
                    <td class="text-right">¥{{ (item.finalPrice || 0).toFixed(2) }}</td>
                    <td class="text-right item-total">¥{{ ((item.finalPrice || 0) * (item.quantity || 1)).toFixed(2) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>

            <!-- Summary -->
            <div class="summary-section">
              <div class="summary-content">
                <div class="summary-row">
                  <span class="summary-label">设备数量</span>
                  <span class="summary-value">{{ historyTotalDeviceCount }} 台</span>
                </div>
                <div class="summary-row">
                  <span class="summary-label">小计</span>
                  <span class="summary-value">¥{{ quoteSubtotal.toFixed(2) }}</span>
                </div>
                <div class="summary-total">
                  <span class="total-label">总计 (CNY)</span>
                  <span class="total-value">¥{{ (historyData?.total_amount || 0).toFixed(2) }}</span>
                </div>
              </div>
            </div>

            <!-- Terms -->
            <div class="terms-section">
              <h4 class="terms-title">条款与条件</h4>
              <p v-for="(para, idx) in quoteTermsParagraphs" :key="idx" class="terms-paragraph">{{ para }}</p>
              <div class="doc-footer">
                <p class="footer-text">第 1 页 / 共 1 页</p>
              </div>
            </div>
          </div>
        </div>
      </main>

      <!-- 底部导航 -->
      <footer class="viewer-footer">
        <div class="footer-info">
          <span class="info-item">
            <span class="material-symbols-outlined">person</span>
            {{ historyData?.user_name }}
          </span>
          <span class="info-item">
            <span class="material-symbols-outlined">devices</span>
            {{ historyData?.device_count || 0 }} 台设备
          </span>
          <span class="info-item amount-badge">
            <span class="material-symbols-outlined">payments</span>
            总额: {{ formatPrice(historyData?.total_amount) }}
          </span>
        </div>
        <div class="footer-nav">
          <button 
            @click="prevStep" 
            :disabled="currentStep === 'import'"
            class="nav-btn prev"
          >
            <span class="material-symbols-outlined">arrow_back</span>
            上一步
          </button>
          <button 
            @click="nextStep" 
            :disabled="currentStep === 'quote'"
            class="nav-btn next"
          >
            下一步
            <span class="material-symbols-outlined">arrow_forward</span>
          </button>
        </div>
      </footer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'

interface Props {
  historyData: any
}

const props = defineProps<Props>()
defineEmits<{
  close: []
}>()

// 步骤定义
const steps = [
  { key: 'import', label: '导入数据' },
  { key: 'match', label: '智能匹配' },
  { key: 'adjust', label: '价格调整' },
  { key: 'quote', label: '生成报价' }
]

const currentStep = ref('import')
const quoteView = ref('original')
const quotationDocRef = ref<HTMLElement | null>(null)  // 报价单预览区域引用
const isExporting = ref(false)  // 导出状态

// 数据计算 - 导入数据优先从 import_data 获取，回退到 page_states.doc_recognition
const importData = computed(() => {
  const raw = props.historyData?.import_data
  if (raw && (raw.data?.length > 0 || raw.converted?.data?.length > 0)) {
    return raw
  }
  // 回退：从 page_states.doc_recognition 构造（与草稿模式一致）
  const docState = props.historyData?.page_states?.doc_recognition
  if (docState) {
    return {
      headers: docState.originalHeaders || [],
      data: docState.originalTableData || [],
      converted: {
        headers: docState.convertedHeaders || docState.visibleColumns || [],
        data: docState.convertedTableData || []
      }
    }
  }
  return raw
})
// 识别结果：优先取 converted，回退到 import_data 本身
const importConvertedHeaders = computed(() => {
  const ch = importData.value?.converted?.headers
  if (ch && ch.length > 0) return ch
  // headers 为空时，尝试从数据行的 key 中提取
  const cd = importData.value?.converted?.data
  if (cd && cd.length > 0) {
    const keys = Object.keys(cd[0])
    if (keys.length > 0) return keys
  }
  return importData.value?.headers || []
})
const importConvertedData = computed(() => {
  return importData.value?.converted?.data || importData.value?.data || []
})
const matchData = computed(() => props.historyData?.match_data)
const adjustData = computed(() => props.historyData?.price_adjust_data)
const quoteData = computed(() => props.historyData?.quote_data)
const quoteMetadata = computed(() => props.historyData?.quote_metadata)

// 设备总数量（对数量列求和）
const historyTotalDeviceCount = computed(() => {
  if (!quoteMetadata.value?.table_data) return 0
  return quoteMetadata.value.table_data.reduce((sum: number, item: any) => {
    return sum + (parseInt(item.quantity) || 1)
  }, 0)
})

// 报价单小计
const quoteSubtotal = computed(() => {
  if (!quoteMetadata.value?.table_data) return 0
  return quoteMetadata.value.table_data.reduce((sum: number, item: any) => {
    const price = parseFloat(item.finalPrice) || 0
    const quantity = parseInt(item.quantity) || 1
    return sum + (price * quantity)
  }, 0)
})

// 服务条款内容（转换为纯文本）
// 将 HTML 转为纯文本（使用 DOMParser，与 QuotationGeneration 一致）
function convertHtmlToPlainText(html: string): string {
  if (!html) return ''
  const parser = new DOMParser()
  const doc = parser.parseFromString(html, 'text/html')

  const blockTags = new Set([
    'p', 'div', 'section', 'article', 'header', 'footer',
    'table', 'thead', 'tbody', 'tr', 'td', 'th',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6'
  ])

  const walk = (node: Node, listType?: 'ol' | 'ul', listIndex = 1): string => {
    if (node.nodeType === Node.TEXT_NODE) {
      return node.nodeValue || ''
    }
    if (node.nodeType !== Node.ELEMENT_NODE) return ''

    const el = node as HTMLElement
    const tag = el.tagName.toLowerCase()

    if (tag === 'br') return '\n'

    if (tag === 'ol' || tag === 'ul') {
      const listItems = Array.from(el.children).filter(
        child => child.tagName.toLowerCase() === 'li'
      ) as HTMLElement[]
      let idx = 1
      let text = ''
      for (const li of listItems) {
        const line = walk(li, tag as 'ol' | 'ul', idx)
        if (line.trim().length > 0) { text += line; idx += 1 }
      }
      return text + (text ? '\n' : '')
    }

    if (tag === 'li') {
      const prefix = listType === 'ol' ? `${listIndex}. ` : ''
      const content = Array.from(el.childNodes).map(child => walk(child)).join('')
      if (content.replace(/[\s\u00A0]/g, '').length === 0) return ''
      return `${prefix}${content}\n`
    }

    const content = Array.from(el.childNodes).map(child => walk(child)).join('')
    if (blockTags.has(tag)) {
      const hasVisible = content.replace(/[\s\u00A0]/g, '').length > 0
      return (hasVisible ? content : '') + '\n'
    }
    return content
  }

  let text = ''
  doc.body.childNodes.forEach(child => { text += walk(child) })

  return text
    .replace(/\r\n/g, '\n').replace(/\r/g, '\n')
    .replace(/\n{3,}/g, '\n\n')
    .replace(/[ \t]+\n/g, '\n').replace(/[ \t]+$/g, '')
    .replace(/^\n+/, '').replace(/\n+$/, '')
}

// 条款内容按行拆分（与 QuotationGeneration 的 termsContentParagraphs 一致）
const quoteTermsParagraphs = computed(() => {
  const raw = quoteMetadata.value?.service_terms_content
  const text = raw
    ? convertHtmlToPlainText(raw)
    : '费用需在发票日期后 30 天内支付。逾期付款将收取每月 1.5% 的服务费。'
  if (!text) return ['']
  const lines = text.split(/\n/).map(s => {
    const withTabs = s.replace(/\t/g, '  ')
    const withIndent = withTabs.replace(/^( +)/, (m: string) => '\u00A0'.repeat(m.length))
    return withIndent.trimEnd() || '\u00A0'
  })
  // 过滤仅包含编号的孤立行
  return lines.filter((line, idx) => {
    if (/^\d+\.\s*$/.test(line) && idx + 1 < lines.length && lines[idx + 1].startsWith(line.trim())) {
      return false
    }
    return true
  })
})

// 统计数据
const highMatchCount = computed(() => 
  matchData.value?.filter((item: any) => item.matchRate >= 70)?.length || 0
)

const lowMatchCount = computed(() => 
  matchData.value?.filter((item: any) => item.matchRate < 70)?.length || 0
)

// 方法
function getStepIndex(key: string): number {
  return steps.findIndex(s => s.key === key)
}

function getStepDataCount(key: string): number {
  switch (key) {
    case 'import': return importConvertedData.value?.length || 0
    case 'match': return matchData.value?.length || 0
    case 'adjust': return adjustData.value?.length || 0
    case 'quote': return (quoteData.value?.original?.length || 0) + (quoteData.value?.converted?.length || 0)
    default: return 0
  }
}

function prevStep() {
  const idx = getStepIndex(currentStep.value)
  if (idx > 0) {
    currentStep.value = steps[idx - 1].key
  }
}

function nextStep() {
  const idx = getStepIndex(currentStep.value)
  if (idx < steps.length - 1) {
    currentStep.value = steps[idx + 1].key
  }
}

function getMatchRowClass(item: any): string {
  if (!item.matchRate) return ''
  if (item.matchRate >= 70) return 'match-high-row'
  if (item.matchRate >= 50) return 'match-mid-row'
  return 'match-low-row'
}

function getMatchRateClass(rate: number): string {
  if (!rate) return ''
  if (rate >= 70) return 'rate-high'
  if (rate >= 50) return 'rate-mid'
  return 'rate-low'
}

function getProfitClass(profit: number): string {
  if (!profit) return ''
  if (profit >= 10) return 'profit-high'
  if (profit >= 0) return 'profit-mid'
  return 'profit-low'
}

function formatPrice(price: any): string {
  if (price === null || price === undefined) return '-'
  const num = Number(price)
  if (isNaN(num)) return '-'
  return '¥' + num.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDateTime(dateStr: string): string {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function formatCellValue(value: any): string {
  if (value === null || value === undefined) return '-'
  if (typeof value === 'number') {
    // 检查是否是价格类型
    if (value > 100) {
      return '¥' + value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
    }
    return value.toString()
  }
  return String(value)
}

function getQuoteOriginalHeaders(): string[] {
  if (!quoteData.value?.original?.length) return []
  return Object.keys(quoteData.value.original[0])
}

function getQuoteConvertedHeaders(): string[] {
  if (!quoteData.value?.converted?.length) return []
  return Object.keys(quoteData.value.converted[0])
}

// 格式化厂商名称
function formatManufacturer(manufacturer: any): string {
  if (!manufacturer) return ''
  const str = String(manufacturer)
  // 如果已经是简短名称，直接返回
  if (str.length <= 20) return str
  // 否则提取主要部分
  if (str.includes('HP&HPE') || str.includes('惠普&慧与')) return 'HP/HPE'
  if (str.includes('戴尔') || str.includes('Dell')) return 'Dell'
  if (str.includes('华为') || str.includes('Huawei')) return 'Huawei'
  if (str.includes('联想') || str.includes('Lenovo')) return 'Lenovo'
  if (str.includes('浪潮') || str.includes('Inspur')) return 'Inspur'
  if (str.includes('中科曙光')) return 'Sugon'
  return str.substring(0, 20)
}

// 使用 Canvas 渲染页码图片（避免 jsPDF 中文字体问题）
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

// 下载报价单 PDF - 使用 onclone 将克隆元素移至 body 根节点，彻底脱离页面布局链
async function downloadQuotePDF() {
  if (!quotationDocRef.value || !quoteMetadata.value?.table_data?.length) {
    alert('没有可导出的数据')
    return
  }

  isExporting.value = true
  const savedScrollX = window.scrollX
  const savedScrollY = window.scrollY

  try {
    const html2canvas = (await import('html2canvas')).default
    const { default: jsPDF } = await import('jspdf')

    const element = quotationDocRef.value

    // ── A4 参数 ──
    const a4Width = 210   // mm
    const a4Height = 297  // mm
    const pageMargin = 10 // mm
    const imgWidthMm = a4Width - 2 * pageMargin

    // 渲染宽度：A4 at 96dpi ≈ 794px
    const renderWidth = 794

    window.scrollTo(0, 0)

    // ── html2canvas：通过 onclone 在克隆文档中重构布局 ──
    const fullCanvas = await html2canvas(element, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff',
      windowWidth: renderWidth,
      windowHeight: 50000,
      allowTaint: true,
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
          padding: 40px 50px;
          background: white;
          color: #0f172a;
          box-shadow: none;
          border-radius: 0;
          position: static;
        `

        const terms = clonedEl.querySelector('.terms-section') as HTMLElement
        if (terms) terms.style.marginTop = '2rem'

        clonedEl.querySelectorAll('.doc-footer, .doc-decoration').forEach(
          el => (el as HTMLElement).style.display = 'none'
        )

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

    const SEARCH_RANGE = 200
    const PADDING_X = 120
    const SAMPLE_STEP = 6
    const WHITE_THRESHOLD = 245

    const safePageRanges: Array<{start: number, end: number}> = []
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
        const scanTop = Math.max(Math.round(currentY + 100), idealEnd - SEARCH_RANGE)
        const scanHeight = idealEnd - scanTop
        const scanLeft = Math.min(PADDING_X, Math.round(fullCanvas.width * 0.1))
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

      safePageRanges.push({ start: currentY, end: safeEnd })
      currentY = safeEnd
    }

    const totalPages = safePageRanges.length
    console.log(`[PDF] 智能分页后总页数: ${totalPages}`)

    if (totalPages > 50) {
      alert(`内容过长，预计需要 ${totalPages} 页，建议使用 Excel 导出`)
      isExporting.value = false
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
      const imgHeightMm = (pageCanvas.height / pageCanvas.width) * imgWidthMm
      doc.addImage(
        pageCanvas.toDataURL('image/png', 1.0),
        'PNG',
        pageMargin,
        pageMargin,
        imgWidthMm,
        imgHeightMm
      )

      // 页码用 Canvas 渲染图片，避免 jsPDF 中文字体问题
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

    const fileName = `报价单_${quoteMetadata.value.quote_number || 'history'}_${new Date().toISOString().slice(0, 10)}.pdf`
    doc.save(fileName)
    console.log('PDF 导出成功:', fileName, `共 ${totalPages} 页`)
  } catch (error) {
    console.error('PDF 生成失败:', error)
    alert('PDF 生成失败: ' + (error as Error).message)
  } finally {
    isExporting.value = false
    window.scrollTo(savedScrollX, savedScrollY)
  }
}

// 导出报价单 Excel
async function exportQuoteExcel() {
  if (!quoteMetadata.value?.table_data?.length) {
    alert('没有可导出的数据')
    return
  }

  isExporting.value = true

  try {
    const tableData = quoteMetadata.value.table_data

    // 准备表格数据
    const exportData = tableData.map((item: any, index: number) => ({
      '序号': index + 1,
      '产品型号': item.model || '未命名产品',
      '厂商': formatManufacturer(item.matchedManufacturer) || '-',
      '系列': item.matchedSeries || '-',
      '服务级别': item.serviceLevel || '-',
      '服务周期': item.servicePeriodUnit || '-',
      '数量': item.quantity || 1,
      '单价': (item.finalPrice || 0).toFixed(2),
      '总价': ((item.finalPrice || 0) * (item.quantity || 1)).toFixed(2)
    }))

    // 创建工作簿
    const wb = XLSX.utils.book_new()
    const ws = XLSX.utils.json_to_sheet(exportData)

    // 设置列宽
    ws['!cols'] = [
      { wch: 6 },  // 序号
      { wch: 30 }, // 产品型号
      { wch: 15 }, // 厂商
      { wch: 15 }, // 系列
      { wch: 12 }, // 服务级别
      { wch: 10 }, // 服务周期
      { wch: 8 },  // 数量
      { wch: 12 }, // 单价
      { wch: 12 }  // 总价
    ]

    XLSX.utils.book_append_sheet(wb, ws, '报价单')

    // 生成文件名
    const fileName = `报价单_${quoteMetadata.value.quote_number || 'history'}_${new Date().toISOString().slice(0, 10)}.xlsx`

    // 导出
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
    saveAs(new Blob([wbout], { type: 'application/octet-stream' }), fileName)

    console.log('Excel 导出成功:', fileName)
  } catch (error) {
    console.error('Excel 导出失败:', error)
    alert('Excel 导出失败，请重试')
  } finally {
    isExporting.value = false
  }
}
</script>

<style scoped>
.history-detail-viewer {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background-color: rgba(0, 0, 0, 0.85);
  display: flex;
  align-items: center;
  justify-content: center;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.fullscreen-modal {
  width: 100%;
  height: 100%;
  background-color: #0f172a;
  display: flex;
  flex-direction: column;
  animation: slideUp 0.3s ease-out;
}

@keyframes slideUp {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}

/* Header */
.viewer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.record-badge {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  background-color: rgba(19, 91, 236, 0.15);
  color: #60a5fa;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 600;
  width: fit-content;
}

.record-badge .material-symbols-outlined {
  font-size: 0.875rem;
}

.viewer-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.viewer-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.readonly-badge {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
}

.close-btn {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  background-color: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background-color: #ef4444;
  border-color: #ef4444;
  color: #fff;
}

/* Steps Progress */
.steps-progress {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 1.5rem 2rem;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  gap: 0;
}

.step-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  transition: all 0.2s;
  position: relative;
}

.step-item:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.step-item.active {
  background-color: rgba(19, 91, 236, 0.15);
}

.step-number {
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background-color: #334155;
  color: #94a3b8;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.step-item.active .step-number {
  background-color: #135bec;
  color: #fff;
}

.step-item.completed .step-number {
  background-color: #22c55e;
  color: #fff;
}

.step-info {
  display: flex;
  flex-direction: column;
}

.step-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  transition: all 0.2s;
}

.step-item.active .step-label {
  color: #f1f5f9;
}

.step-count {
  font-size: 0.75rem;
  color: #64748b;
}

.step-connector {
  width: 3rem;
  height: 2px;
  background-color: #334155;
  margin-left: 1rem;
}

.step-item.completed + .step-item .step-connector,
.step-item.completed .step-connector {
  background-color: #22c55e;
}

/* Content */
.viewer-content {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem 2rem;
}

.step-content {
  animation: fadeIn 0.3s ease-out;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid #334155;
}

.content-title-area {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.content-icon {
  font-size: 2rem;
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.15);
  padding: 0.75rem;
  border-radius: 0.75rem;
}

.content-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.content-desc {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0 0;
}

.content-stats {
  display: flex;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  padding: 0.5rem 1rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  border: 1px solid #334155;
}

.stat-item.highlight {
  border-color: #22c55e;
  background-color: rgba(34, 197, 94, 0.1);
}

.stat-item.warning {
  border-color: #eab308;
  background-color: rgba(234, 179, 8, 0.1);
}

.stat-label {
  font-size: 0.75rem;
  color: #64748b;
}

.stat-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
}

.stat-value.amount {
  color: #22c55e;
}

/* Import Tables - Side by Side */
.import-tables-row {
  display: flex;
  gap: 1rem;
  align-items: flex-start;
}

.import-table-col {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
}

.import-table-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.import-table-title .title-text {
  font-size: 0.9375rem;
  font-weight: 600;
}

.import-table-title .title-text.original {
  color: #3b82f6;
}

.import-table-title .title-text.converted {
  color: #3b82f6;
}

.import-table-title .title-badge {
  font-size: 0.75rem;
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 999px;
  padding: 0.125rem 0.625rem;
  white-space: nowrap;
}

.import-table-scroll {
  max-height: calc(100vh - 360px);
}

.no-data-placeholder {
  padding: 3rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

/* Headers Hint */
.headers-hint {
  padding: 0.75rem 1rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
  border: 1px solid #334155;
}

.hint-label {
  font-size: 0.75rem;
  color: #64748b;
}

.hint-value {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-left: 0.5rem;
}

/* Table Section */
.table-section {
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
  max-height: calc(100vh - 400px);
  overflow-y: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.data-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th {
  padding: 0.875rem 1rem;
  text-align: left;
  background-color: #0f172a;
  color: #64748b;
  font-weight: 600;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.data-table td {
  padding: 0.75rem 1rem;
  color: #e2e8f0;
  border-bottom: 1px solid #334155;
  max-width: 300px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.data-table.readonly td {
  cursor: default;
}

.row-num {
  width: 50px;
  text-align: center !important;
  color: #64748b;
  font-weight: 500;
}

.model-cell {
  font-family: "JetBrains Mono", monospace;
  color: #a5b4fc;
}

.matched-model {
  font-family: "JetBrains Mono", monospace;
  color: #22c55e;
  font-weight: 500;
}

.price-cell {
  text-align: right;
  font-weight: 500;
}

.final-price {
  color: #22c55e !important;
  font-weight: 700;
}

.no-data-cell {
  text-align: center !important;
  padding: 3rem !important;
  color: #64748b;
}

/* Match Rate */
.match-rate {
  display: inline-flex;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  font-size: 0.75rem;
}

.rate-high {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.rate-mid {
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.rate-low {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Match Row Classes */
.match-high-row {
  border-left: 3px solid #22c55e;
}

.match-mid-row {
  border-left: 3px solid #eab308;
}

.match-low-row {
  border-left: 3px solid #ef4444;
}

/* Profit Rate */
.profit-rate {
  display: inline-flex;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 600;
  font-size: 0.75rem;
}

.profit-high {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.profit-mid {
  background-color: rgba(59, 130, 246, 0.15);
  color: #3b82f6;
}

.profit-low {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

/* Table Toggle Buttons */
.table-toggle {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn:hover {
  background-color: #334155;
  color: #f1f5f9;
}

.toggle-btn.active {
  background-color: #135bec;
  border-color: #135bec;
  color: #fff;
}

.toggle-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Section Subtitle */
.section-subtitle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  border: 1px solid #334155;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.section-subtitle .material-symbols-outlined {
  font-size: 1.125rem;
  color: #135bec;
}

/* No Data Wrapper */
.no-data-wrapper {
  background-color: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  padding: 3rem;
}

/* More Hint */
.more-hint {
  margin-top: 0.75rem;
  padding: 0.5rem 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.75rem;
  background-color: rgba(100, 116, 139, 0.1);
  border-radius: 0.375rem;
}

/* Quote Tabs */
.quote-tabs {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.quote-tab {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.quote-tab:hover {
  background-color: #334155;
  color: #f1f5f9;
}

.quote-tab.active {
  background-color: #135bec;
  border-color: #135bec;
  color: #fff;
}

/* Footer */
.viewer-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #1e293b;
  border-top: 1px solid #334155;
}

.footer-info {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.info-item .material-symbols-outlined {
  font-size: 1.125rem;
}

.amount-badge {
  padding: 0.5rem 1rem;
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
  border-radius: 0.5rem;
  font-weight: 600;
}

.footer-nav {
  display: flex;
  gap: 0.75rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.nav-btn.prev {
  background-color: #334155;
  color: #f1f5f9;
}

.nav-btn.prev:hover:not(:disabled) {
  background-color: #475569;
}

.nav-btn.next {
  background-color: #135bec;
  color: #fff;
}

.nav-btn.next:hover:not(:disabled) {
  background-color: #1d64f2;
}

.nav-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Scrollbar */
.table-wrapper::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.table-wrapper::-webkit-scrollbar-track {
  background: #1e293b;
}

.table-wrapper::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}

/* Export Actions */
.export-actions {
  display: flex;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.export-action-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.export-action-btn.pdf {
  background-color: #ef4444;
  color: #fff;
}

.export-action-btn.pdf:hover:not(:disabled) {
  background-color: #dc2626;
}

.export-action-btn.excel {
  background-color: #22c55e;
  color: #fff;
}

.export-action-btn.excel:hover:not(:disabled) {
  background-color: #16a34a;
}

.export-action-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Quotation Preview */
.quotation-preview {
  background-color: white;
  color: #0f172a;
  min-height: 900px;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
  padding: 3rem;
  display: flex;
  flex-direction: column;
  position: relative;
  border-radius: 0.125rem;
  max-width: 210mm;
  margin: 0 auto;
}

.doc-decoration {
  position: absolute;
  top: 0;
  right: 0;
  width: 150px;
  height: 150px;
  background: linear-gradient(135deg, rgba(19, 91, 236, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

.doc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2rem;
  padding-bottom: 1.5rem;
  border-bottom: 2px solid #e2e8f0;
}

.company-info {
  flex: 1;
}

.custom-logo-img {
  max-width: 180px;
  max-height: 60px;
  object-fit: contain;
  margin-bottom: 0.75rem;
}

.company-contact {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
  line-height: 1.5;
}

.company-logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 0.75rem;
}

.company-logo .logo-icon {
  width: 40px;
  height: 40px;
}

.logo-text-group {
  display: flex;
  flex-direction: column;
}

.logo-cn {
  font-size: 0.875rem;
  font-weight: 700;
  color: #005bac;
  line-height: 1.2;
}

.logo-en {
  font-size: 0.5rem;
  color: #8dc21f;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.company-name {
  font-size: 1.125rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.company-address {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
  line-height: 1.4;
}

.quote-info {
  text-align: right;
}

.doc-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: #005bac;
  margin: 0 0 0.5rem 0;
  letter-spacing: 0.1em;
}

.quote-number,
.quote-date {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.25rem 0;
}

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

.info-block.text-right {
  text-align: right;
}

.info-label {
  font-size: 0.75rem;
  font-weight: 700;
  color: #64748b;
  margin: 0 0 0.5rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.customer-name {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.customer-detail {
  font-size: 0.875rem;
  color: #64748b;
  margin: 0.125rem 0;
}

.validity-date {
  font-size: 1rem;
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.validity-note {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

/* Items Table */
.items-table {
  margin-bottom: 2rem;
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

.quote-table tbody tr {
  border-bottom: 1px solid #f8fafc;
}

.quote-table tbody tr:hover {
  background-color: #f8fafc;
}

.quote-table td {
  padding: 1rem 0;
  color: #475569;
}

.quote-table .col-no {
  width: 50px;
  text-align: center;
}

.quote-table .col-desc {
  width: auto;
}

.quote-table .col-qty {
  width: 80px;
  text-align: center;
}

.quote-table .col-price,
.quote-table .col-total {
  width: 100px;
  text-align: right;
}

.item-desc {
  padding-right: 1rem;
}

.item-name {
  font-weight: 600;
  color: #1e293b;
  margin: 0 0 0.25rem 0;
}

.item-detail {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.text-center {
  text-align: center;
}

.text-right {
  text-align: right;
}

.item-total {
  font-weight: 600;
  color: #135bec;
}

/* Summary */
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
  font-size: 0.875rem;
  font-weight: 500;
  color: #1e293b;
}

.summary-total {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
}

.total-label {
  font-size: 1rem;
  font-weight: 700;
  color: #135bec;
}

.total-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #22c55e;
}

/* Terms */
.terms-section {
  padding-top: 1.5rem;
  border-top: 1px solid #e2e8f0;
}

.terms-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #475569;
  margin: 0 0 0.75rem 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.terms-content {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0 0 1rem 0;
  white-space: pre-line;
}

.terms-paragraph {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.6;
  margin: 0;
  white-space: pre-wrap;
}

.doc-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 1rem;
  margin-top: 1rem;
  border-top: 1px solid #e2e8f0;
}

.footer-text {
  font-size: 0.625rem;
  color: #94a3b8;
  margin: 0;
}
</style>





