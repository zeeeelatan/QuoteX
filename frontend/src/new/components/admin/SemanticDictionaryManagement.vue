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
        <el-button type="warning" :loading="mining" @click="runMine">
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
      <el-select v-model="typeFilter" placeholder="全部类型" clearable style="width:140px;margin-left:8px;" @change="loadTerms">
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
    <el-dialog v-model="dialogVisible" title="手动新增噪声词" width="420px">
      <el-form label-width="80px">
        <el-form-item label="词">
          <el-input v-model="form.term" placeholder="如：监控接入交换机 / ProLiant" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.term_type" style="width:100%;">
            <el-option label="设备类型" value="device_type" />
            <el-option label="系列名" value="series" />
            <el-option label="修饰词" value="modifier" />
          </el-select>
        </el-form-item>
        <el-form-item label="语言">
          <el-select v-model="form.lang" style="width:100%;">
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
    await ElMessageBox.confirm(`确定删除「${row.term}」？`, '提示', { type: 'warning' })
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
.semantic-dict {
  padding: 4px;
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
  color: #1f2937;
}
.intro-desc {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.6;
  max-width: 760px;
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
  border: 1px solid #e5e7eb;
  transition: all 0.15s;
}
.stat-card:hover { transform: translateY(-1px); box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
.stat-card .num { font-size: 24px; font-weight: 700; }
.stat-card .label { font-size: 12px; color: #6b7280; margin-top: 2px; }
.stat-card.pending .num { color: #d97706; }
.stat-card.approved .num { color: #059669; }
.stat-card.rejected .num { color: #dc2626; }
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
.sel-count { font-size: 13px; color: #6b7280; }
.term-text { font-weight: 500; }
</style>
