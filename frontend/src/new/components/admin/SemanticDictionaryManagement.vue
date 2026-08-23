<template>
  <div class="semantic-dict">
    <!-- 顶部说明 + 操作 -->
    <div class="header-bar">
      <div class="intro">
        <p class="intro-title">语义词典 —— 智能匹配的“设备类型/噪声词”库</p>
        <p class="intro-desc">
          系统会从「已确认的手动匹配」记录中自动挖掘候选噪声词（如“监控接入交换机”“ProLiant”），
          经此处<strong>采纳</strong>后即进入智能匹配的语义抽取词典生效，帮助算法剥离无用信息、只保留型号核心串。
        </p>
      </div>
      <div class="actions">
        <el-button type="primary" :loading="mining" @click="runMine">
          <span class="material-symbols-outlined" style="font-size:18px;margin-right:4px;">manage_search</span>
          从已确认记录挖掘
        </el-button>
        <el-button type="primary" plain @click="openCreate">手动新增词</el-button>
      </div>
    </div>

    <!-- 统计卡片 -->
    <div class="stat-cards">
      <div class="stat-card pending" @click="switchTab('pending')">
        <div class="num">{{ stats.pending }}</div>
        <div class="label">待审核</div>
      </div>
      <div class="stat-card approved" @click="switchTab('approved')">
        <div class="num">{{ stats.approved }}</div>
        <div class="label">已采纳（生效中）</div>
      </div>
      <div class="stat-card rejected" @click="switchTab('rejected')">
        <div class="num">{{ stats.rejected }}</div>
        <div class="label">已拒绝</div>
      </div>
    </div>

    <!-- 标签页 + 工具栏 -->
    <div class="toolbar">
      <el-radio-group v-model="activeStatus" @change="loadTerms">
        <el-radio-button label="pending">待审核</el-radio-button>
        <el-radio-button label="approved">已采纳</el-radio-button>
        <el-radio-button label="rejected">已拒绝</el-radio-button>
      </el-radio-group>
      <el-input
        v-model="search"
        placeholder="搜索词"
        clearable
        style="width:200px;margin-left:12px;"
        @input="onSearch"
      />
      <el-select
        v-model="typeFilter"
        placeholder="全部类型"
        clearable
        popper-class="semantic-dict-popper"
        style="width:140px;margin-left:8px;"
        @change="loadTerms"
      >
        <el-option label="设备类型" value="device_type" />
        <el-option label="系列名" value="series" />
        <el-option label="修饰词" value="modifier" />
      </el-select>
      <div class="toolbar-right">
        <template v-if="selected.length">
          <span class="sel-count">已选 {{ selected.length }} 项</span>
          <el-button v-if="activeStatus !== 'approved'" type="success" size="small" @click="batchReview('approved')">采纳</el-button>
          <el-button v-if="activeStatus !== 'rejected'" type="danger" size="small" @click="batchReview('rejected')">拒绝</el-button>
        </template>
      </div>
    </div>

    <!-- 表格 -->
    <el-table
      :data="terms"
      v-loading="loading"
      border
      stripe
      height="calc(100vh - 420px)"
      @selection-change="(rows) => (selected = rows)"
    >
      <el-table-column type="selection" width="46" />
      <el-table-column prop="term" label="词" min-width="200">
        <template #default="{ row }">
          <span class="term-text">{{ row.term }}</span>
        </template>
      </el-table-column>
      <el-table-column prop="term_type" label="类型" width="110">
        <template #default="{ row }">
          <el-tag size="small" :type="typeTagColor(row.term_type)">{{ typeLabel(row.term_type) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column prop="lang" label="语言" width="80">
        <template #default="{ row }">{{ row.lang === 'cn' ? '中文' : '英文' }}</template>
      </el-table-column>
      <el-table-column prop="frequency" label="出现频次" width="100" sortable />
      <el-table-column prop="source" label="来源" width="90">
        <template #default="{ row }">{{ row.source === 'miner' ? '自动挖掘' : '手动' }}</template>
      </el-table-column>
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag size="small" :type="statusTagColor(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button v-if="row.status !== 'approved'" link type="success" @click="reviewOne(row, 'approved')">采纳</el-button>
          <el-button v-if="row.status !== 'rejected'" link type="warning" @click="reviewOne(row, 'rejected')">拒绝</el-button>
          <el-button link type="danger" @click="removeTerm(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <!-- 手动新增弹窗 -->
    <el-dialog v-model="dialogVisible" class="semantic-dict-dialog" title="手动新增噪声词" width="420px">
      <el-form label-width="80px">
        <el-form-item label="词">
          <el-input v-model="form.term" placeholder="如：监控接入交换机 / ProLiant" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.term_type" popper-class="semantic-dict-popper" style="width:100%;">
            <el-option label="设备类型" value="device_type" />
            <el-option label="系列名" value="series" />
            <el-option label="修饰词" value="modifier" />
          </el-select>
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="form.lang" popper-class="semantic-dict-popper" style="width:100%;">
            <el-option label="中文" value="cn" />
            <el-option label="英文" value="en" />
          </el-select>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="submitCreate">新增并采纳</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface Term {
  id: number
  term: string
  term_type: string
  lang: string
  frequency: number
  status: string
  source: string
}

const terms = ref<Term[]>([])
const selected = ref<Term[]>([])
const loading = ref(false)
const mining = ref(false)
const activeStatus = ref('pending')
const search = ref('')
const typeFilter = ref('')
const stats = reactive({ pending: 0, approved: 0, rejected: 0, total: 0 })

const dialogVisible = ref(false)
const form = reactive({ term: '', term_type: 'device_type', lang: 'cn' })

let searchTimer: any = null
function onSearch() {
  clearTimeout(searchTimer)
  searchTimer = setTimeout(loadTerms, 300)
}

function switchTab(s: string) {
  activeStatus.value = s
  loadTerms()
}

async function loadStats() {
  try {
    const { data } = await axios.get(`${API_URL}/semantic-terms/stats`)
    Object.assign(stats, data)
  } catch (e) { /* 表可能尚未迁移 */ }
}

async function loadTerms() {
  loading.value = true
  try {
    const params: any = { status: activeStatus.value, limit: 1000 }
    if (search.value) params.search = search.value
    if (typeFilter.value) params.term_type = typeFilter.value
    const { data } = await axios.get(`${API_URL}/semantic-terms/`, { params })
    terms.value = data
  } catch (e) {
    ElMessage.error('加载词典失败（请确认后端已更新并迁移）')
  } finally {
    loading.value = false
  }
}

async function runMine() {
  mining.value = true
  try {
    const { data } = await axios.post(`${API_URL}/semantic-terms/mine`)
    ElMessage.success(`挖掘完成：扫描 ${data.scanned_records} 条记录，新增候选 ${data.new_candidates} 个，待审核共 ${data.total_pending} 个`)
    activeStatus.value = 'pending'
    await Promise.all([loadStats(), loadTerms()])
  } catch (e) {
    ElMessage.error('挖掘失败')
  } finally {
    mining.value = false
  }
}

async function reviewOne(row: Term, status: string) {
  await doReview([row.id], status)
}

async function batchReview(status: string) {
  await doReview(selected.value.map((r) => r.id), status)
}

async function doReview(ids: number[], status: string) {
  if (!ids.length) return
  try {
    await axios.post(`${API_URL}/semantic-terms/review`, { ids, status })
    ElMessage.success(status === 'approved' ? '已采纳' : '已拒绝')
    await Promise.all([loadStats(), loadTerms()])
  } catch (e) {
    ElMessage.error('操作失败')
  }
}

async function removeTerm(row: Term) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.term}」？`, '提示', {
      type: 'warning',
      customClass: 'semantic-dict-messagebox',
    })
    await axios.delete(`${API_URL}/semantic-terms/${row.id}`)
    ElMessage.success('已删除')
    await Promise.all([loadStats(), loadTerms()])
  } catch (e) { /* 取消 */ }
}

function openCreate() {
  form.term = ''
  form.term_type = 'device_type'
  form.lang = 'cn'
  dialogVisible.value = true
}

async function submitCreate() {
  if (!form.term.trim()) {
    ElMessage.warning('请输入词')
    return
  }
  try {
    await axios.post(`${API_URL}/semantic-terms/`, { ...form, status: 'approved', source: 'manual' })
    ElMessage.success('已新增并采纳')
    dialogVisible.value = false
    await Promise.all([loadStats(), loadTerms()])
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '新增失败')
  }
}

function typeLabel(t: string) {
  return { device_type: '设备类型', series: '系列名', modifier: '修饰词' }[t] || t
}
function typeTagColor(t: string) {
  return { device_type: 'primary', series: 'warning', modifier: 'info' }[t] || 'info'
}
function statusLabel(s: string) {
  return { pending: '待审核', approved: '已采纳', rejected: '已拒绝' }[s] || s
}
function statusTagColor(s: string) {
  return { pending: 'warning', approved: 'success', rejected: 'danger' }[s] || 'info'
}

onMounted(() => {
  loadStats()
  loadTerms()
})
</script>

<style scoped>
/* 配色令牌与 AdminDashboard 保持一致（Slate 深色 + 品牌蓝 #135bec），
   本组件是 admin 目录下唯一使用 el-table 的模块，其余均为原生表格，
   故此处把 el-table 的 CSS 变量对齐到同一套令牌，使观感与兄弟模块统一。 */
.semantic-dict {
  --sd-bg-page: #0f172a;
  --sd-bg-panel: #1e293b;
  --sd-border: #334155;
  --sd-border-strong: #475569;
  --sd-text: #e2e8f0;
  --sd-text-strong: #f1f5f9;
  --sd-text-muted: #94a3b8;
  --sd-text-dim: #64748b;
  --sd-accent: #135bec;
  --sd-accent-hover: #1d64f2;

  --el-color-primary: #135bec;

  padding: 4px;
  color: var(--sd-text);
}
.header-bar {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 16px;
  margin-bottom: 16px;
}
.intro-title {
  font-size: 15px;
  font-weight: 600;
  margin: 0 0 4px;
  color: var(--sd-text-strong);
}
.intro-desc {
  font-size: 13px;
  color: var(--sd-text-muted);
  margin: 0;
  line-height: 1.6;
  max-width: 760px;
}
.intro-desc strong {
  color: var(--sd-text-strong);
  font-weight: 600;
}
.actions {
  display: flex;
  gap: 12px;
  flex-shrink: 0;
}
.stat-cards {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}
.stat-card {
  flex: 0 0 150px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  background-color: var(--sd-bg-panel);
  border: 1px solid var(--sd-border);
  transition: all 0.15s;
}
.stat-card:hover {
  transform: translateY(-1px);
  border-color: var(--sd-border-strong);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.35);
}
.stat-card .num { font-size: 24px; font-weight: 700; }
.stat-card .label { font-size: 12px; color: var(--sd-text-muted); margin-top: 2px; }
.stat-card.pending .num { color: #f59e0b; }
.stat-card.approved .num { color: #10b981; }
.stat-card.rejected .num { color: #ef4444; }
.toolbar {
  display: flex;
  align-items: center;
  margin-bottom: 12px;
}
.toolbar-right {
  margin-left: auto;
  display: flex;
  align-items: center;
  gap: 8px;
}
.sel-count { font-size: 13px; color: var(--sd-text-muted); }
.term-text { font-weight: 500; color: var(--sd-text-strong); }

/* ---------------- 表格 ---------------- */
.semantic-dict :deep(.el-table) {
  --el-table-bg-color: var(--sd-bg-panel);
  --el-table-tr-bg-color: var(--sd-bg-panel);
  --el-table-header-bg-color: var(--sd-bg-page);
  --el-table-border-color: var(--sd-border);
  --el-table-text-color: var(--sd-text);
  --el-table-header-text-color: var(--sd-text-muted);
  --el-table-row-hover-bg-color: var(--sd-border);
  --el-table-current-row-bg-color: rgba(19, 91, 236, 0.15);
  /* 斑马纹行由该变量渲染 */
  --el-fill-color-lighter: #223049;
  /* v-loading 遮罩 */
  --el-mask-color: rgba(15, 23, 42, 0.72);
  --el-text-color-secondary: var(--sd-text-dim);

  background-color: var(--sd-bg-panel);
  border-radius: 0.5rem;
}
/* 表头：对齐原生表格模块的小号大写灰字 */
.semantic-dict :deep(.el-table th.el-table__cell) {
  background-color: var(--sd-bg-page);
  color: var(--sd-text-muted);
  font-size: 0.75rem;
  font-weight: 600;
  letter-spacing: 0.05em;
}
.semantic-dict :deep(.el-table td.el-table__cell) {
  font-size: 0.875rem;
}
/* 固定列与表头单元格跟随所在行底色，避免横向滚动时出现亮色残留 */
.semantic-dict :deep(.el-table .el-table-fixed-column--right),
.semantic-dict :deep(.el-table .el-table-fixed-column--left) {
  background-color: inherit;
}
.semantic-dict :deep(.el-table th.el-table-fixed-column--right),
.semantic-dict :deep(.el-table th.el-table-fixed-column--left) {
  background-color: var(--sd-bg-page);
}
/* 表格底部那条分隔线 */
.semantic-dict :deep(.el-table .el-table__inner-wrapper::before) {
  background-color: var(--sd-border);
}
.semantic-dict :deep(.el-table__empty-text) {
  color: var(--sd-text-dim);
}
/* 排序箭头 */
.semantic-dict :deep(.el-table .sort-caret.ascending) {
  border-bottom-color: var(--sd-text-dim);
}
.semantic-dict :deep(.el-table .sort-caret.descending) {
  border-top-color: var(--sd-text-dim);
}
.semantic-dict :deep(.el-table .ascending .sort-caret.ascending) {
  border-bottom-color: var(--sd-accent);
}
.semantic-dict :deep(.el-table .descending .sort-caret.descending) {
  border-top-color: var(--sd-accent);
}
/* 表格内滚动条与全局保持一致 */
.semantic-dict :deep(.el-scrollbar__thumb) {
  background-color: var(--sd-border-strong);
}

/* ---------------- 状态标签 ----------------
   EP 默认的 light-9 底色（如 #ecf5ff）在深色表格上是一排亮色药丸，
   改为项目侧边栏同款的半透明色底 + 亮色文字。 */
.semantic-dict :deep(.el-tag) {
  border-width: 1px;
  background-color: rgba(100, 116, 139, 0.2);
  border-color: rgba(100, 116, 139, 0.45);
  color: var(--sd-text-muted);
}
.semantic-dict :deep(.el-tag.el-tag--primary) {
  background-color: rgba(19, 91, 236, 0.15);
  border-color: rgba(19, 91, 236, 0.4);
  color: #60a5fa;
}
.semantic-dict :deep(.el-tag.el-tag--warning) {
  background-color: rgba(245, 158, 11, 0.15);
  border-color: rgba(245, 158, 11, 0.4);
  color: #fbbf24;
}
.semantic-dict :deep(.el-tag.el-tag--success) {
  background-color: rgba(16, 185, 129, 0.15);
  border-color: rgba(16, 185, 129, 0.4);
  color: #34d399;
}
.semantic-dict :deep(.el-tag.el-tag--danger) {
  background-color: rgba(239, 68, 68, 0.15);
  border-color: rgba(239, 68, 68, 0.4);
  color: #f87171;
}

/* 操作列的文字按钮：与标签同色系，保证深底可读 */
.semantic-dict :deep(.el-button.is-link.el-button--success) { color: #34d399; }
.semantic-dict :deep(.el-button.is-link.el-button--warning) { color: #fbbf24; }
.semantic-dict :deep(.el-button.is-link.el-button--danger) { color: #f87171; }
.semantic-dict :deep(.el-button.is-link:hover) { opacity: 0.75; }

/* ---------------- 复选框 ---------------- */
.semantic-dict :deep(.el-checkbox__inner) {
  background-color: var(--sd-bg-page);
  border-color: var(--sd-border-strong);
}
.semantic-dict :deep(.el-checkbox:hover .el-checkbox__inner) {
  border-color: var(--sd-accent);
}
.semantic-dict :deep(.el-checkbox__input.is-checked .el-checkbox__inner),
.semantic-dict :deep(.el-checkbox__input.is-indeterminate .el-checkbox__inner) {
  background-color: var(--sd-accent);
  border-color: var(--sd-accent);
}

/* ---------------- 输入框 / 下拉 ---------------- */
.semantic-dict :deep(.el-input__wrapper),
.semantic-dict :deep(.el-select__wrapper) {
  background-color: var(--sd-bg-page);
  box-shadow: 0 0 0 1px var(--sd-border) inset;
}
.semantic-dict :deep(.el-input__wrapper:hover),
.semantic-dict :deep(.el-select__wrapper:hover) {
  box-shadow: 0 0 0 1px var(--sd-border-strong) inset;
}
.semantic-dict :deep(.el-input__wrapper.is-focus),
.semantic-dict :deep(.el-select__wrapper.is-focused) {
  box-shadow: 0 0 0 1px var(--sd-accent) inset;
}
.semantic-dict :deep(.el-input__inner),
.semantic-dict :deep(.el-select__placeholder) {
  color: var(--sd-text);
}
.semantic-dict :deep(.el-input__inner::placeholder),
.semantic-dict :deep(.el-select__placeholder.is-transparent) {
  color: var(--sd-text-dim);
}
.semantic-dict :deep(.el-input__icon),
.semantic-dict :deep(.el-select__caret) {
  color: var(--sd-text-dim);
}

/* ---------------- 标签页按钮组 ---------------- */
.semantic-dict :deep(.el-radio-button__inner) {
  background-color: var(--sd-bg-panel);
  border-color: var(--sd-border);
  color: var(--sd-text-muted);
  box-shadow: none;
}
.semantic-dict :deep(.el-radio-button__inner:hover) {
  color: var(--sd-text-strong);
}
.semantic-dict :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background-color: var(--sd-accent);
  border-color: var(--sd-accent);
  color: #fff;
  box-shadow: -1px 0 0 0 var(--sd-accent);
}

/* ---------------- 按钮 ---------------- */
/* plain 主色按钮对齐项目的 slate 次级按钮 */
.semantic-dict :deep(.el-button--primary.is-plain) {
  background-color: var(--sd-border);
  border-color: var(--sd-border-strong);
  color: var(--sd-text);
}
.semantic-dict :deep(.el-button--primary.is-plain:hover) {
  background-color: var(--sd-border-strong);
  border-color: var(--sd-text-dim);
  color: var(--sd-text-strong);
}
.semantic-dict :deep(.el-button--primary:not(.is-plain):not(.is-link)) {
  background-color: var(--sd-accent);
  border-color: var(--sd-accent);
}
.semantic-dict :deep(.el-button--primary:not(.is-plain):not(.is-link):hover) {
  background-color: var(--sd-accent-hover);
  border-color: var(--sd-accent-hover);
}
</style>

<!-- el-dialog / el-select 下拉 / MessageBox 会被 teleport 到 body，
     scoped 选择器无法命中，故以专属类名做非作用域样式，避免影响其他页面 -->
<style>
.semantic-dict-dialog,
.semantic-dict-messagebox {
  background-color: #1e293b;
  border: 1px solid #334155;
}
.semantic-dict-dialog .el-dialog__title,
.semantic-dict-messagebox .el-message-box__title {
  color: #f1f5f9;
}
.semantic-dict-dialog .el-dialog__headerbtn .el-dialog__close,
.semantic-dict-messagebox .el-message-box__headerbtn .el-message-box__close {
  color: #64748b;
}
.semantic-dict-dialog .el-dialog__headerbtn:hover .el-dialog__close,
.semantic-dict-messagebox .el-message-box__headerbtn:hover .el-message-box__close {
  color: #f1f5f9;
}
.semantic-dict-messagebox .el-message-box__content {
  color: #e2e8f0;
}
.semantic-dict-dialog .el-form-item__label {
  color: #94a3b8;
}
.semantic-dict-dialog .el-input__wrapper,
.semantic-dict-dialog .el-select__wrapper {
  background-color: #0f172a;
  box-shadow: 0 0 0 1px #334155 inset;
}
.semantic-dict-dialog .el-input__wrapper:hover,
.semantic-dict-dialog .el-select__wrapper:hover {
  box-shadow: 0 0 0 1px #475569 inset;
}
.semantic-dict-dialog .el-input__wrapper.is-focus,
.semantic-dict-dialog .el-select__wrapper.is-focused {
  box-shadow: 0 0 0 1px #135bec inset;
}
.semantic-dict-dialog .el-input__inner,
.semantic-dict-dialog .el-select__selected-item {
  color: #e2e8f0;
}
.semantic-dict-dialog .el-input__inner::placeholder {
  color: #64748b;
}
.semantic-dict-dialog .el-select__caret {
  color: #64748b;
}
.semantic-dict-dialog .el-button:not(.el-button--primary) {
  background-color: #334155;
  border-color: #475569;
  color: #e2e8f0;
}
.semantic-dict-dialog .el-button:not(.el-button--primary):hover {
  background-color: #475569;
  border-color: #64748b;
  color: #f1f5f9;
}
.semantic-dict-dialog .el-button--primary,
.semantic-dict-messagebox .el-button--primary {
  background-color: #135bec;
  border-color: #135bec;
}
.semantic-dict-dialog .el-button--primary:hover,
.semantic-dict-messagebox .el-button--primary:hover {
  background-color: #1d64f2;
  border-color: #1d64f2;
}

/* 下拉面板 */
.semantic-dict-popper.el-popper {
  background-color: #1e293b;
  border: 1px solid #334155;
}
.semantic-dict-popper.el-popper .el-popper__arrow::before {
  background-color: #1e293b;
  border-color: #334155;
}
.semantic-dict-popper .el-select-dropdown__item {
  color: #e2e8f0;
}
.semantic-dict-popper .el-select-dropdown__item.is-hovering {
  background-color: #334155;
}
.semantic-dict-popper .el-select-dropdown__item.is-selected {
  color: #135bec;
  font-weight: 600;
}
</style>
