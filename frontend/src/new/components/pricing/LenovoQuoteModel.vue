<template>
  <div class="lenovo-model-page">
    <!-- Header -->
    <div class="page-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">首页</span>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-item">报价工具</span>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-item active">联想框架报价模型</span>
      </div>
      <div class="header-actions-row">
        <div>
          <h1 class="page-title">联想框架报价模型</h1>
          <p class="page-subtitle">面向联想框架报价体系的快速查价 / 端型识别 / 价格表浏览工具</p>
        </div>
      </div>
    </div>

    <!-- Tabs -->
    <div class="tabs-bar">
      <button
        v-for="tab in TABS"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="activeTab = tab.key"
      >
        <span class="material-symbols-outlined">{{ tab.icon }}</span>
        {{ tab.label }}
      </button>
    </div>

    <!-- ====== Tab 1: 报价计算 ====== -->
    <div v-if="activeTab === 'quote'" class="card">
      <div class="card-header">
        <span class="material-symbols-outlined card-icon">request_quote</span>
        <h3 class="card-title">报价计算</h3>
        <span class="card-hint">输入设备信息 + SLA + 配置项 → 直查联想框架价格表</span>
      </div>

      <div class="form-grid">
        <div class="form-item">
          <label>设备大类 <span class="req">*</span></label>
          <select v-model="quoteForm.device_category">
            <option v-for="opt in DEVICE_CATEGORIES" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="form-item">
          <label>品牌</label>
          <input v-model="quoteForm.brand" placeholder="如 HP / IBM / Lenovo" />
        </div>
        <div class="form-item">
          <label>型号 <span class="req">*</span></label>
          <input v-model="quoteForm.model" placeholder="如 DL360 / TS4500 / MSL3040" />
        </div>
        <div class="form-item">
          <label>SLA <span class="req">*</span></label>
          <input v-model="quoteForm.sla" placeholder="如 7*24*NBD / 7*24*4 / 5*9*NBD" />
        </div>
        <div class="form-item">
          <label>数量</label>
          <input v-model.number="quoteForm.quantity" type="number" min="1" />
        </div>

        <!-- 磁带库专属 -->
        <div class="form-item" v-if="quoteForm.device_category === '磁带库'">
          <label>驱动器配置</label>
          <select v-model="quoteForm.drive_config">
            <option v-for="o in ['LTO5','LTO6','LTO7','LTO8']" :key="o" :value="o">{{ o }}</option>
          </select>
        </div>

        <!-- 网络设备专属 -->
        <div class="form-item" v-if="quoteForm.device_category === '网络设备'">
          <label>子类</label>
          <select v-model="quoteForm.sub_category">
            <option v-for="o in ['网络交换机','路由器','无线控制器','无线AP']" :key="o" :value="o">{{ o }}</option>
          </select>
        </div>

        <!-- 服务器专属 -->
        <template v-if="quoteForm.device_category === '服务器'">
          <div class="form-item">
            <label>含 SSD</label>
            <select v-model="quoteForm.includes_ssd">
              <option :value="false">不含</option>
              <option :value="true">含</option>
            </select>
          </div>
          <div class="form-item">
            <label>报价类型</label>
            <select v-model="quoteForm.package_type">
              <option v-for="o in ['备件维保','整包']" :key="o" :value="o">{{ o }}</option>
            </select>
          </div>
        </template>

        <!-- 服务器/小型机：含硬盘 -->
        <div class="form-item" v-if="quoteForm.device_category === '服务器' || quoteForm.device_category === '小型机'">
          <label>含硬盘不返还</label>
          <select v-model="quoteForm.includes_disk">
            <option :value="false">不含</option>
            <option :value="true">含</option>
          </select>
        </div>

        <!-- 存储：含硬盘不回收 -->
        <div class="form-item" v-if="quoteForm.device_category === '存储'">
          <label>含硬盘不回收</label>
          <select v-model="quoteForm.includes_disk_no_return">
            <option :value="false">不含</option>
            <option :value="true">含</option>
          </select>
        </div>
      </div>

      <div class="form-actions">
        <button class="btn-primary" :disabled="quoteLoading" @click="runQuote">
          <span class="material-symbols-outlined">search</span>
          {{ quoteLoading ? '查询中…' : '查询报价' }}
        </button>
        <button class="btn-secondary" @click="resetQuoteForm">
          <span class="material-symbols-outlined">restart_alt</span>
          重置
        </button>
      </div>

      <!-- 结果 -->
      <div v-if="quoteResult" class="result-panel">
        <div class="result-row">
          <span class="result-label">状态</span>
          <span class="result-value">
            <span class="status-badge" :class="`status-${quoteResult.status}`">
              {{ STATUS_LABEL[quoteResult.status] || quoteResult.status }}
            </span>
          </span>
        </div>
        <div class="result-row" v-if="quoteResult.message">
          <span class="result-label">说明</span>
          <span class="result-value">{{ quoteResult.message }}</span>
        </div>
        <div class="result-row">
          <span class="result-label">端型</span>
          <span class="result-value">
            <span v-if="quoteResult.end_type" class="end-type-badge">{{ quoteResult.end_type }}</span>
            <span v-else class="muted">-</span>
          </span>
        </div>
        <div class="result-row" v-if="quoteResult.sub_category">
          <span class="result-label">子类</span>
          <span class="result-value">{{ quoteResult.sub_category }}</span>
        </div>
        <div class="result-row">
          <span class="result-label">命中方式</span>
          <span class="result-value">
            <span class="method-badge" :class="`method-${quoteResult.match_method}`">
              {{ METHOD_LABEL[quoteResult.match_method] || quoteResult.match_method || '-' }}
            </span>
            <span class="muted" v-if="quoteResult.matched_classification_id">
              · 分类 id={{ quoteResult.matched_classification_id }}
            </span>
            <span class="muted" v-if="quoteResult.matched_pattern_id">
              · 通配规则 id={{ quoteResult.matched_pattern_id }}
            </span>
          </span>
        </div>
        <div class="result-row" v-if="quoteResult.unit_price">
          <span class="result-label">单价</span>
          <span class="result-value price">¥{{ Number(quoteResult.unit_price).toFixed(2) }}</span>
        </div>
        <div class="result-row" v-if="quoteResult.total_price">
          <span class="result-label">总价（×{{ quoteResult.quantity }}）</span>
          <span class="result-value price strong">¥{{ Number(quoteResult.total_price).toFixed(2) }}</span>
        </div>
        <div class="result-row" v-if="quoteResult.price_notes">
          <span class="result-label">价格备注</span>
          <span class="result-value muted">{{ quoteResult.price_notes }}</span>
        </div>
      </div>
    </div>

    <!-- ====== Tab 2: 端型查询 ====== -->
    <div v-if="activeTab === 'classify'" class="card">
      <div class="card-header">
        <span class="material-symbols-outlined card-icon">category</span>
        <h3 class="card-title">端型识别</h3>
        <span class="card-hint">用品牌 + 型号在分类表查端型，命中不到走 Word 通配规则兜底</span>
      </div>

      <div class="form-grid">
        <div class="form-item">
          <label>设备大类 <span class="req">*</span></label>
          <select v-model="classifyForm.device_category">
            <option v-for="opt in DEVICE_CATEGORIES" :key="opt" :value="opt">{{ opt }}</option>
          </select>
        </div>
        <div class="form-item">
          <label>品牌</label>
          <input v-model="classifyForm.brand" placeholder="如 HP" />
        </div>
        <div class="form-item">
          <label>型号 <span class="req">*</span></label>
          <input v-model="classifyForm.model" placeholder="如 DL360" />
        </div>
      </div>
      <div class="form-actions">
        <button class="btn-primary" :disabled="classifyLoading" @click="runClassify">
          <span class="material-symbols-outlined">search</span>
          {{ classifyLoading ? '查询中…' : '查端型' }}
        </button>
        <button class="btn-secondary" @click="resetClassifyForm">
          <span class="material-symbols-outlined">restart_alt</span>
          重置
        </button>
      </div>

      <div v-if="classifyResult" class="result-panel compact">
        <div class="result-row">
          <span class="result-label">端型</span>
          <span class="result-value">
            <span v-if="classifyResult.end_type" class="end-type-badge">{{ classifyResult.end_type }}</span>
            <span v-else class="muted">未识别</span>
          </span>
        </div>
        <div class="result-row" v-if="classifyResult.sub_category">
          <span class="result-label">子类</span>
          <span class="result-value">{{ classifyResult.sub_category }}</span>
        </div>
        <div class="result-row">
          <span class="result-label">命中方式</span>
          <span class="result-value">
            <span class="method-badge" :class="`method-${classifyResult.match_method}`">
              {{ METHOD_LABEL[classifyResult.match_method] || classifyResult.match_method || '-' }}
            </span>
            <span class="muted" v-if="classifyResult.matched_classification_id">
              · 分类 id={{ classifyResult.matched_classification_id }}
            </span>
            <span class="muted" v-if="classifyResult.matched_pattern_id">
              · 通配规则 id={{ classifyResult.matched_pattern_id }}
            </span>
          </span>
        </div>
      </div>
    </div>

    <!-- ====== Tab 3: 价格表浏览 ====== -->
    <div v-if="activeTab === 'browse'" class="card">
      <div class="card-header">
        <span class="material-symbols-outlined card-icon">table_view</span>
        <h3 class="card-title">价格表浏览</h3>
        <span class="card-hint">挑一张价格表，全字段模糊检索</span>
      </div>

      <div class="browse-toolbar">
        <div class="form-item inline">
          <label>价格表</label>
          <select v-model="browseKind" @change="loadBrowseRows">
            <option v-for="t in PRICE_TABLES" :key="t.kind" :value="t.kind">{{ t.label }}</option>
          </select>
        </div>
        <div class="form-item inline grow">
          <label>关键字</label>
          <input v-model="browseSearch" placeholder="任意字段模糊匹配（端型/SLA/驱动器/含SSD/备注...）" />
        </div>
        <span class="muted small">共 {{ filteredBrowseRows.length }} / {{ browseRows.length }} 行</span>
      </div>

      <div class="table-wrap">
        <table class="data-table">
          <thead>
            <tr>
              <th v-for="col in browseCols" :key="col.key">{{ col.label }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(row, i) in pagedBrowseRows" :key="row.id || i">
              <td v-for="col in browseCols" :key="col.key">{{ formatCell(row[col.key], col) }}</td>
            </tr>
            <tr v-if="filteredBrowseRows.length === 0">
              <td :colspan="browseCols.length" class="empty">
                <span class="material-symbols-outlined">inbox</span>
                <span>{{ browseLoading ? '加载中…' : '暂无数据' }}</span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination">
        <button class="page-btn" :disabled="browsePage === 1" @click="browsePage--">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <span class="page-cur">{{ browsePage }} / {{ browseTotalPages }}</span>
        <button class="page-btn" :disabled="browsePage >= browseTotalPages" @click="browsePage++">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <select v-model="browsePageSize" class="page-size">
          <option :value="20">20 条/页</option>
          <option :value="50">50 条/页</option>
          <option :value="100">100 条/页</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const DEVICE_CATEGORIES = ['磁带库', '光纤交换机', '网络设备', '服务器', 'IB交换机', '小型机', '存储']

const STATUS_LABEL: Record<string, string> = {
  ok: '已命中',
  unmatched: '未匹配端型',
  no_price: '端型OK但缺价格',
}
const METHOD_LABEL: Record<string, string> = {
  exact: '精确', fuzzy: '模糊', pattern: '兜底', none: '未命中',
}

const TABS = [
  { key: 'quote', label: '报价计算', icon: 'request_quote' },
  { key: 'classify', label: '端型识别', icon: 'category' },
  { key: 'browse', label: '价格表浏览', icon: 'table_view' },
]
const activeTab = ref<'quote' | 'classify' | 'browse'>('quote')

// ============ Tab 1: 报价计算 ============
interface QuoteForm {
  device_category: string
  brand: string
  model: string
  sla: string
  quantity: number
  drive_config: string
  sub_category: string
  includes_ssd: boolean
  package_type: string
  includes_disk: boolean
  includes_disk_no_return: boolean
}
const DEFAULT_QUOTE: QuoteForm = {
  device_category: '服务器',
  brand: '', model: '', sla: '7*24*NBD', quantity: 1,
  drive_config: 'LTO7',
  sub_category: '网络交换机',
  includes_ssd: false, package_type: '备件维保',
  includes_disk: false, includes_disk_no_return: false,
}
const quoteForm = ref<QuoteForm>({ ...DEFAULT_QUOTE })
const quoteResult = ref<any | null>(null)
const quoteLoading = ref(false)

function resetQuoteForm() {
  quoteForm.value = { ...DEFAULT_QUOTE }
  quoteResult.value = null
}

function buildQuotePayload(): any {
  const p = quoteForm.value
  const payload: any = {
    device_category: p.device_category,
    brand: p.brand || undefined,
    model: p.model,
    sla: p.sla,
    quantity: Number(p.quantity) || 1,
  }
  if (p.device_category === '磁带库') payload.drive_config = p.drive_config
  if (p.device_category === '网络设备') payload.sub_category = p.sub_category
  if (p.device_category === '服务器') {
    payload.includes_ssd = p.includes_ssd
    payload.package_type = p.package_type
    payload.includes_disk = p.includes_disk
  }
  if (p.device_category === '小型机') payload.includes_disk = p.includes_disk
  if (p.device_category === '存储') payload.includes_disk_no_return = p.includes_disk_no_return
  return payload
}

async function runQuote() {
  if (!quoteForm.value.model.trim()) {
    ElMessage.warning('请输入设备型号')
    return
  }
  if (!quoteForm.value.sla.trim()) {
    ElMessage.warning('请输入 SLA')
    return
  }
  quoteLoading.value = true
  try {
    const resp = await axios.post(`${API_URL}/lenovo/quote`, buildQuotePayload())
    quoteResult.value = resp.data
  } catch (e: any) {
    ElMessage.error(`查询失败：${e?.response?.data?.detail || e?.message}`)
    quoteResult.value = null
  } finally {
    quoteLoading.value = false
  }
}

// ============ Tab 2: 端型识别 ============
const DEFAULT_CLASSIFY = { device_category: '服务器', brand: '', model: '' }
const classifyForm = ref({ ...DEFAULT_CLASSIFY })
const classifyResult = ref<any | null>(null)
const classifyLoading = ref(false)

function resetClassifyForm() {
  classifyForm.value = { ...DEFAULT_CLASSIFY }
  classifyResult.value = null
}

async function runClassify() {
  if (!classifyForm.value.model.trim()) {
    ElMessage.warning('请输入型号')
    return
  }
  classifyLoading.value = true
  try {
    // 复用 /lenovo/quote，传一组"故意缺价格维度"的最小参数
    // 端型仍会在返回的 result 里给出来；价格部分可能是 no_price，我们只看端型
    const resp = await axios.post(`${API_URL}/lenovo/quote`, {
      device_category: classifyForm.value.device_category,
      brand: classifyForm.value.brand || undefined,
      model: classifyForm.value.model,
      sla: '_dummy',
      quantity: 1,
    })
    classifyResult.value = resp.data
  } catch (e: any) {
    ElMessage.error(`查询失败：${e?.response?.data?.detail || e?.message}`)
    classifyResult.value = null
  } finally {
    classifyLoading.value = false
  }
}

// ============ Tab 3: 价格表浏览 ============
interface ColDef { key: string; label: string; type?: 'bool' | 'price' }
interface PriceTableDef { kind: string; label: string; cols: ColDef[] }
const PRICE_TABLES: PriceTableDef[] = [
  {
    kind: 'tape', label: '磁带库价格',
    cols: [
      { key: 'end_type', label: '端型' },
      { key: 'drive_config', label: '驱动器配置' },
      { key: 'sla', label: 'SLA' },
      { key: 'price', label: '单价', type: 'price' },
      { key: 'notes', label: '备注' },
    ],
  },
  {
    kind: 'network', label: '网络价格',
    cols: [
      { key: 'device_category', label: '设备大类' },
      { key: 'end_type', label: '端型' },
      { key: 'sla', label: 'SLA' },
      { key: 'price', label: '单价', type: 'price' },
      { key: 'notes', label: '备注' },
    ],
  },
  {
    kind: 'server', label: '服务器价格',
    cols: [
      { key: 'end_type', label: '端型' },
      { key: 'includes_ssd', label: '含SSD', type: 'bool' },
      { key: 'package_type', label: '报价类型' },
      { key: 'sla', label: 'SLA' },
      { key: 'includes_disk', label: '含硬盘不返还', type: 'bool' },
      { key: 'price', label: '单价', type: 'price' },
      { key: 'notes', label: '备注' },
    ],
  },
  {
    kind: 'storage', label: '存储价格',
    cols: [
      { key: 'end_type', label: '端型' },
      { key: 'sla', label: 'SLA' },
      { key: 'includes_disk_no_return', label: '含硬盘不回收', type: 'bool' },
      { key: 'price', label: '单价', type: 'price' },
      { key: 'notes', label: '备注' },
    ],
  },
  {
    kind: 'minicomputer', label: '小型机价格',
    cols: [
      { key: 'end_type', label: '端型' },
      { key: 'sla', label: 'SLA' },
      { key: 'includes_disk', label: '含硬盘不返还', type: 'bool' },
      { key: 'price', label: '单价', type: 'price' },
      { key: 'notes', label: '备注' },
    ],
  },
  {
    kind: 'inspection', label: '巡检价格',
    cols: [
      { key: 'unit', label: '单位' },
      { key: 'price', label: '单价', type: 'price' },
      { key: 'tax_rate', label: '税率' },
      { key: 'notes', label: '备注' },
    ],
  },
]
const browseKind = ref('tape')
const browseRows = ref<any[]>([])
const browseSearch = ref('')
const browseLoading = ref(false)
const browsePage = ref(1)
const browsePageSize = ref(20)

const browseCols = computed(() => {
  const t = PRICE_TABLES.find(t => t.kind === browseKind.value)
  return t ? t.cols : []
})

const filteredBrowseRows = computed(() => {
  const q = browseSearch.value.trim().toLowerCase()
  if (!q) return browseRows.value
  return browseRows.value.filter(r =>
    browseCols.value.some(c => {
      const v = formatCell(r[c.key], c).toLowerCase()
      return v.includes(q)
    })
  )
})

const browseTotalPages = computed(() =>
  Math.max(1, Math.ceil(filteredBrowseRows.value.length / browsePageSize.value))
)
const pagedBrowseRows = computed(() => {
  const start = (browsePage.value - 1) * browsePageSize.value
  return filteredBrowseRows.value.slice(start, start + browsePageSize.value)
})

watch([browseKind, browseSearch, browsePageSize], () => { browsePage.value = 1 })

function formatCell(v: any, col: ColDef): string {
  if (v === null || v === undefined || v === '') return '-'
  if (col.type === 'bool') return v ? '是' : '否'
  if (col.type === 'price') return '¥' + Number(v).toFixed(2)
  return String(v)
}

async function loadBrowseRows() {
  browseLoading.value = true
  try {
    const resp = await axios.get(`${API_URL}/lenovo/prices/${browseKind.value}/`)
    browseRows.value = resp.data || []
  } catch (e: any) {
    ElMessage.error(`加载失败：${e?.response?.data?.detail || e?.message}`)
    browseRows.value = []
  } finally {
    browseLoading.value = false
  }
}

onMounted(() => {
  loadBrowseRows()
})
</script>

<style scoped>
.lenovo-model-page {
  padding: 1.5rem 2rem;
  color: #e5e7eb;
  background: #0a0e1a;
  min-height: 100%;
}

.page-header {
  margin-bottom: 1.25rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  font-size: 0.8rem;
  color: #6b7d96;
  margin-bottom: 0.75rem;
}
.breadcrumb-item.active { color: #c7d3e6; font-weight: 500; }
.breadcrumb-separator { font-size: 1rem; }

.page-title {
  font-size: 1.4rem;
  font-weight: 700;
  margin: 0;
  color: #f1f5f9;
}
.page-subtitle {
  margin: 0.35rem 0 0 0;
  color: #8aa0c0;
  font-size: 0.9rem;
}

.tabs-bar {
  display: flex;
  gap: 0.35rem;
  margin-bottom: 1rem;
  border-bottom: 1px solid rgba(75, 97, 137, 0.25);
}
.tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.6rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #8aa0c0;
  cursor: pointer;
  font-size: 0.9rem;
  transition: color 0.15s, border-color 0.15s;
}
.tab-btn:hover { color: #c7d3e6; }
.tab-btn.active {
  color: #74a8ff;
  border-bottom-color: #2563eb;
  font-weight: 600;
}

.card {
  background: rgba(20, 30, 48, 0.6);
  border: 1px solid rgba(75, 97, 137, 0.25);
  border-radius: 0.6rem;
  padding: 1.25rem;
  margin-bottom: 1rem;
}
.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.card-icon { color: #74a8ff; font-size: 1.25rem; }
.card-title { margin: 0; font-size: 1rem; color: #e3eaf5; }
.card-hint { color: #6b7d96; font-size: 0.78rem; margin-left: 0.5rem; }

.form-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 0.85rem 1.2rem;
}
.form-item { display: flex; flex-direction: column; gap: 0.35rem; }
.form-item.inline { flex-direction: row; align-items: center; gap: 0.5rem; }
.form-item.inline.grow { flex: 1; }
.form-item.inline label { white-space: nowrap; }
.form-item label { font-size: 0.8rem; color: #8aa0c0; }
.req { color: #f87171; }
.form-item input, .form-item select {
  padding: 0.5rem 0.7rem;
  background: rgba(20, 30, 48, 0.8);
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.4rem;
  color: #e3eaf5;
  font-size: 0.88rem;
}
.form-item.inline input, .form-item.inline select { flex: 1; }

.form-actions {
  display: flex;
  gap: 0.5rem;
  margin-top: 1.2rem;
}

.btn-primary, .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.55rem 1rem;
  border-radius: 0.4rem;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
}
.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover:not(:disabled) { background: #1d4ed8; }
.btn-primary:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-secondary {
  background: rgba(75, 97, 137, 0.25); color: #e3eaf5;
}

.result-panel {
  margin-top: 1.2rem;
  padding: 1rem 1.2rem;
  background: rgba(20, 30, 48, 0.4);
  border: 1px solid rgba(75, 97, 137, 0.25);
  border-radius: 0.5rem;
}
.result-panel.compact { padding: 0.75rem 1rem; }
.result-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.35rem 0;
}
.result-label {
  min-width: 7rem;
  color: #8aa0c0;
  font-size: 0.85rem;
}
.result-value {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  color: #e3eaf5;
  font-size: 0.88rem;
}
.result-value.price { color: #fbbf24; font-weight: 600; }
.result-value.strong { font-size: 1.05rem; }
.result-value .muted { color: #6b7d96; font-size: 0.78rem; }

.status-badge, .method-badge, .end-type-badge {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 0.3rem;
  font-size: 0.78rem;
  font-weight: 600;
}
.status-ok { background: rgba(34, 197, 94, 0.18); color: #4ade80; }
.status-no_price { background: rgba(234, 179, 8, 0.18); color: #facc15; }
.status-unmatched { background: rgba(239, 68, 68, 0.18); color: #f87171; }

.method-exact { background: rgba(34, 197, 94, 0.18); color: #4ade80; }
.method-fuzzy { background: rgba(234, 179, 8, 0.18); color: #facc15; }
.method-pattern { background: rgba(168, 85, 247, 0.18); color: #c084fc; }
.method-none { background: rgba(239, 68, 68, 0.18); color: #f87171; }

.end-type-badge { background: rgba(37, 99, 235, 0.18); color: #74a8ff; }

/* 浏览表 */
.browse-toolbar {
  display: flex;
  align-items: end;
  gap: 1rem;
  margin-bottom: 0.85rem;
  flex-wrap: wrap;
}
.muted { color: #6b7d96; }
.small { font-size: 0.8rem; }

.table-wrap {
  overflow: auto;
  background: rgba(20, 30, 48, 0.4);
  border: 1px solid rgba(75, 97, 137, 0.25);
  border-radius: 0.5rem;
  max-height: 24rem;
}
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}
.data-table th {
  text-align: left;
  padding: 0.5rem 0.85rem;
  background: rgba(20, 30, 48, 0.85);
  border-bottom: 1px solid rgba(75, 97, 137, 0.25);
  color: #8aa0c0;
  font-weight: 500;
  white-space: nowrap;
  position: sticky;
  top: 0;
}
.data-table td {
  padding: 0.45rem 0.85rem;
  border-bottom: 1px solid rgba(75, 97, 137, 0.12);
  color: #d6dfee;
}
.data-table .empty {
  text-align: center;
  padding: 1.5rem;
  color: #6b7d96;
}
.data-table .empty .material-symbols-outlined {
  display: block;
  margin: 0 auto 0.4rem auto;
  font-size: 1.5rem;
}

.pagination {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 0.75rem;
}
.page-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: rgba(20, 30, 48, 0.6);
  border: 1px solid rgba(75, 97, 137, 0.3);
  border-radius: 0.35rem;
  color: #c7d3e6;
  cursor: pointer;
}
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-cur { color: #c7d3e6; font-size: 0.85rem; padding: 0 0.5rem; }
.page-size {
  padding: 0.35rem 0.5rem;
  background: rgba(20, 30, 48, 0.6);
  border: 1px solid rgba(75, 97, 137, 0.3);
  border-radius: 0.35rem;
  color: #c7d3e6;
  font-size: 0.85rem;
}
</style>
