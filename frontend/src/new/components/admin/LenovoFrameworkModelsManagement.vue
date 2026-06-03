<template>
  <div class="lenovo-models-management">
    <!-- 统计卡片 -->
    <div class="stats-row">
      <div class="stat-card">
        <span class="stat-label">总数</span>
        <span class="stat-value">{{ stats.total?.toLocaleString() ?? '—' }}</span>
      </div>
      <div class="stat-card success">
        <span class="stat-label">已有端型</span>
        <span class="stat-value">{{ stats.with_end_type?.toLocaleString() ?? '—' }}</span>
      </div>
      <div class="stat-card warning">
        <span class="stat-label">待人工指定</span>
        <span class="stat-value">{{ stats.without_end_type?.toLocaleString() ?? '—' }}</span>
      </div>
    </div>

    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增机型
        </button>
        <button class="btn-secondary" @click="reload()" title="刷新">
          <span class="material-symbols-outlined">refresh</span>
        </button>
      </div>
      <div class="toolbar-right">
        <select v-model="filterCategory" @change="resetAndReload" class="filter-select">
          <option value="">全部大类</option>
          <option v-for="c in DEVICE_CATEGORIES" :key="c" :value="c">{{ c }}</option>
        </select>
        <select v-model="filterSource" @change="resetAndReload" class="filter-select">
          <option value="">全部来源</option>
          <option v-for="s in SOURCES" :key="s.value" :value="s.value">{{ s.label }}</option>
        </select>
        <select v-model="filterEndType" @change="resetAndReload" class="filter-select">
          <option value="">端型 任意</option>
          <option value="with">仅 有端型</option>
          <option value="without">仅 待人工</option>
        </select>
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            type="text"
            v-model="searchQuery"
            @input="handleSearch"
            placeholder="搜索 型号 / 品牌 / 系列 / MT..."
          />
        </div>
        <span class="total-count">共 {{ totalCount.toLocaleString() }} 条</span>
      </div>
    </div>

    <!-- 表格 -->
    <div class="table-container" :class="{ loading: loading }">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>

      <table class="data-table">
        <thead>
          <tr>
            <th class="col-id">ID</th>
            <th>设备大类</th>
            <th>品牌</th>
            <th>系列</th>
            <th>型号</th>
            <th>MT</th>
            <th>端型</th>
            <th>子类</th>
            <th>来源</th>
            <th>别名</th>
            <th>备注</th>
            <th class="col-actions">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in items" :key="item.id">
            <td class="id-cell">{{ item.id }}</td>
            <td><span class="badge badge-cat">{{ item.device_category }}</span></td>
            <td class="text-cell">{{ item.brand || '-' }}</td>
            <td class="text-cell">{{ item.series || '-' }}</td>
            <td class="text-cell mono">{{ item.model }}</td>
            <td class="text-cell mono">{{ item.mt_code || '-' }}</td>
            <td>
              <span v-if="item.end_type" class="badge badge-endtype">{{ item.end_type }}</span>
              <span v-else class="badge badge-empty">待人工</span>
            </td>
            <td class="text-cell">{{ item.sub_category || '-' }}</td>
            <td><span class="badge" :class="'badge-src-' + item.source">{{ sourceLabel(item.source) }}</span></td>
            <td class="aliases-cell">
              <span
                v-if="(item.aliases || []).length"
                class="badge badge-alias"
                :title="(item.aliases || []).join('\n')"
              >{{ (item.aliases || []).length }} 条</span>
              <span v-else class="text-muted">-</span>
            </td>
            <td class="text-cell notes-cell" :title="item.notes || ''">{{ item.notes || '-' }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="openDialog(item)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteItem(item)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="!loading && items.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inventory_2</span>
        <p>无匹配数据</p>
      </div>
    </div>

    <!-- 分页 -->
    <div class="pagination">
      <div class="pagination-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </div>
      <div class="pagination-controls">
        <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(1)" title="首页">
          <span class="material-symbols-outlined">first_page</span>
        </button>
        <button class="page-btn" :disabled="currentPage === 1" @click="goToPage(currentPage - 1)" title="上一页">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(currentPage + 1)" title="下一页">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <button class="page-btn" :disabled="currentPage >= totalPages" @click="goToPage(totalPages)" title="末页">
          <span class="material-symbols-outlined">last_page</span>
        </button>
        <select v-model="pageSize" @change="resetAndReload" class="page-size-select">
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
          <option :value="100">100条/页</option>
          <option :value="200">200条/页</option>
        </select>
      </div>
    </div>

    <!-- 新增/编辑弹窗 -->
    <div v-if="dialogVisible" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingItem ? '编辑机型' : '新增机型' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-row">
            <div class="form-group">
              <label>设备大类 *</label>
              <select v-model="formData.device_category">
                <option value="">请选择</option>
                <option v-for="c in DEVICE_CATEGORIES" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>端型</label>
              <select v-model="formData.end_type">
                <option value="">(留空=待人工)</option>
                <option v-for="e in END_TYPES" :key="e" :value="e">{{ e }}</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>品牌</label>
              <input v-model="formData.brand" placeholder="例如 HP / 惠普&慧与/HP&HPE" />
            </div>
            <div class="form-group">
              <label>系列</label>
              <input v-model="formData.series" placeholder="例如 ProLiant DL" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>型号 *</label>
              <input v-model="formData.model" placeholder="例如 DL580 Gen8" />
            </div>
            <div class="form-group">
              <label>MT</label>
              <input v-model="formData.mt_code" placeholder="选填" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>子类</label>
              <select v-model="formData.sub_category">
                <option value="">-</option>
                <option v-for="s in SUB_CATEGORIES" :key="s" :value="s">{{ s }}</option>
              </select>
            </div>
            <div class="form-group">
              <label>来源</label>
              <select v-model="formData.source">
                <option v-for="s in SOURCES" :key="s.value" :value="s.value">{{ s.label }}</option>
              </select>
            </div>
          </div>
          <div class="form-group">
            <label>别名（原始品牌型号映射）</label>
            <div class="alias-editor">
              <div class="alias-tag-list">
                <span v-for="(a, i) in (formData.aliases || [])" :key="i" class="alias-tag">
                  {{ a }}
                  <button class="alias-remove" type="button" @click="removeAlias(i)" title="移除">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
                <span v-if="!(formData.aliases || []).length" class="alias-empty">暂无别名</span>
              </div>
              <div class="alias-input-row">
                <input
                  v-model="newAliasInput"
                  type="text"
                  placeholder="输入原始品牌型号（如 Dell-PowerEdge R630），回车添加"
                  @keydown.enter.prevent="addAlias"
                />
                <button type="button" class="btn-secondary btn-sm" @click="addAlias">添加</button>
              </div>
              <p class="alias-hint">添加时会自动归一化（小写、分隔符统一为空格）；过短或重复将被忽略。</p>
            </div>
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="formData.notes" rows="2" placeholder="选填"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveItem">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface FrameworkModel {
  id: number
  device_category: string
  brand?: string | null
  series?: string | null
  model: string
  mt_code?: string | null
  end_type?: string | null
  sub_category?: string | null
  source?: string | null
  notes?: string | null
  aliases?: string[]
}

// 别名归一化（与后端 normalize_alias 保持一致：保守版）
function normalizeAlias(s: string): string {
  if (!s) return ''
  return s.trim().toLowerCase()
    .replace(/[-_/\\]+/g, ' ')
    .replace(/\s+/g, ' ')
}

const DEVICE_CATEGORIES = ['磁带库', '服务器', '存储', '小型机', '网络设备', '光纤交换机', 'IB交换机']
const END_TYPES = ['低端', '中端', '高端', '超高端', 'L1', 'L2', 'M']
const SUB_CATEGORIES = ['网络交换机', '路由器', '无线AP', '无线控制器']
const SOURCES = [
  { value: 'classification', label: '分类表（人工录入）' },
  { value: 'pattern_expanded', label: '通配展开' },
  { value: 'dc_inventory', label: '数据中心设备库' },
  { value: 'user_confirmed', label: '用户确认' },
  { value: 'manual', label: '手工添加' },
]

function sourceLabel(s: string | null | undefined): string {
  return SOURCES.find(x => x.value === s)?.label || (s || '-')
}

// State
const items = ref<FrameworkModel[]>([])
const stats = ref<any>({})
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)
const loading = ref(false)
const dialogVisible = ref(false)
const editingItem = ref<FrameworkModel | null>(null)

// Filters
const searchQuery = ref('')
const filterCategory = ref('')
const filterSource = ref('')
const filterEndType = ref<'' | 'with' | 'without'>('')

let searchTimeout: ReturnType<typeof setTimeout> | null = null

const formData = ref<Partial<FrameworkModel>>({
  device_category: '',
  brand: '',
  series: '',
  model: '',
  mt_code: '',
  end_type: '',
  sub_category: '',
  source: 'manual',
  notes: '',
  aliases: [],
})

const newAliasInput = ref('')

function addAlias() {
  const raw = newAliasInput.value.trim()
  if (!raw) return
  const norm = normalizeAlias(raw)
  if (norm.length < 3) {
    ElMessage.warning('别名过短（归一化后需 ≥ 3 字符）')
    return
  }
  if (!formData.value.aliases) formData.value.aliases = []
  if (formData.value.aliases.includes(norm)) {
    ElMessage.info('该别名已存在')
    newAliasInput.value = ''
    return
  }
  formData.value.aliases.push(norm)
  newAliasInput.value = ''
}

function removeAlias(idx: number) {
  if (!formData.value.aliases) return
  formData.value.aliases.splice(idx, 1)
}

const totalPages = computed(() => Math.max(1, Math.ceil(totalCount.value / pageSize.value)))

async function loadStats() {
  try {
    const resp = await axios.get(`${API_URL}/lenovo/framework-models/stats`)
    stats.value = resp.data || {}
  } catch (e) {
    console.error('Load stats failed:', e)
  }
}

async function loadList() {
  loading.value = true
  try {
    const params: Record<string, any> = {
      page: currentPage.value,
      page_size: pageSize.value,
    }
    if (searchQuery.value.trim()) params.keyword = searchQuery.value.trim()
    if (filterCategory.value) params.device_category = filterCategory.value
    if (filterSource.value) params.source = filterSource.value
    if (filterEndType.value === 'with') params.has_end_type = true
    else if (filterEndType.value === 'without') params.has_end_type = false
    const resp = await axios.get(`${API_URL}/lenovo/framework-models/`, { params })
    items.value = resp.data?.items || []
    totalCount.value = resp.data?.total || 0
  } catch (e: any) {
    console.error('Load list failed:', e)
    ElMessage.error('加载机型库失败')
  } finally {
    loading.value = false
  }
}

function reload() {
  loadList()
  loadStats()
}

function resetAndReload() {
  currentPage.value = 1
  loadList()
}

function handleSearch() {
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => {
    currentPage.value = 1
    loadList()
  }, 300)
}

function goToPage(p: number) {
  if (p < 1 || p > totalPages.value) return
  currentPage.value = p
  loadList()
}

function openDialog(item?: FrameworkModel) {
  newAliasInput.value = ''
  if (item) {
    editingItem.value = item
    formData.value = {
      ...item,
      aliases: Array.isArray(item.aliases) ? [...item.aliases] : [],
    }
  } else {
    editingItem.value = null
    formData.value = {
      device_category: '',
      brand: '',
      series: '',
      model: '',
      mt_code: '',
      end_type: '',
      sub_category: '',
      source: 'manual',
      notes: '',
      aliases: [],
    }
  }
  dialogVisible.value = true
}

function closeDialog() {
  dialogVisible.value = false
}

function buildPayload() {
  const d = formData.value
  return {
    device_category: (d.device_category || '').trim(),
    brand: (d.brand || '').trim() || null,
    series: (d.series || '').trim() || null,
    model: (d.model || '').trim(),
    mt_code: (d.mt_code || '').trim() || null,
    end_type: (d.end_type || '').trim() || null,
    sub_category: (d.sub_category || '').trim() || null,
    source: (d.source || 'manual').trim(),
    notes: (d.notes || '').trim() || null,
    aliases: Array.isArray(d.aliases) ? d.aliases : [],
  }
}

async function saveItem() {
  const payload = buildPayload()
  if (!payload.device_category) {
    ElMessage.warning('请选择设备大类')
    return
  }
  if (!payload.model) {
    ElMessage.warning('请填写型号')
    return
  }
  try {
    if (editingItem.value) {
      await axios.put(`${API_URL}/lenovo/framework-models/${editingItem.value.id}`, payload)
      ElMessage.success('已更新')
    } else {
      await axios.post(`${API_URL}/lenovo/framework-models/`, payload)
      ElMessage.success('已新增')
    }
    closeDialog()
    reload()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '保存失败')
  }
}

async function deleteItem(item: FrameworkModel) {
  try {
    await ElMessageBox.confirm(
      `确认删除「${item.brand || ''} ${item.model}」吗？`,
      '删除确认',
      { confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning' }
    )
  } catch {
    return
  }
  try {
    await axios.delete(`${API_URL}/lenovo/framework-models/${item.id}`)
    ElMessage.success('已删除')
    reload()
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.detail || '删除失败')
  }
}

onMounted(() => {
  loadStats()
  loadList()
})
</script>

<style scoped>
.lenovo-models-management {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  height: 100%;
  box-sizing: border-box;
}

/* 统计卡片 */
.stats-row {
  display: flex;
  gap: 1rem;
}
.stat-card {
  flex: 1;
  background: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.5rem;
  padding: 0.875rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}
.stat-card.success { border-left: 3px solid #22c55e; }
.stat-card.warning { border-left: 3px solid #eab308; }
.stat-label {
  color: #94a3b8;
  font-size: 0.75rem;
}
.stat-value {
  color: #e2e8f0;
  font-size: 1.25rem;
  font-weight: 600;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.toolbar-left, .toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}
.btn-primary, .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  border: 1px solid transparent;
  border-radius: 0.375rem;
  cursor: pointer;
  font-size: 0.875rem;
  transition: filter 0.15s;
}
.btn-primary {
  background: #3b82f6;
  color: white;
}
.btn-primary:hover { filter: brightness(1.1); }
.btn-secondary {
  background: #1e232f;
  color: #e2e8f0;
  border-color: #2a3447;
}
.btn-secondary:hover { background: #2a3447; }
.filter-select, .page-size-select {
  background: #1e232f;
  color: #e2e8f0;
  border: 1px solid #2a3447;
  border-radius: 0.375rem;
  padding: 0.4rem 0.625rem;
  font-size: 0.8rem;
  cursor: pointer;
}
.search-box {
  display: inline-flex;
  align-items: center;
  background: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.375rem;
  padding: 0.25rem 0.625rem;
  gap: 0.375rem;
  min-width: 220px;
}
.search-box .material-symbols-outlined {
  color: #94a3b8;
  font-size: 1rem;
}
.search-box input {
  background: transparent;
  border: none;
  outline: none;
  color: #e2e8f0;
  flex: 1;
  font-size: 0.8rem;
}
.total-count {
  color: #94a3b8;
  font-size: 0.75rem;
}

/* Table */
.table-container {
  flex: 1;
  background: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.5rem;
  overflow: auto;
  position: relative;
  min-height: 300px;
}
.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #cbd5e1;
  z-index: 10;
}
.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #475569;
  border-top-color: #3b82f6;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8rem;
  color: #cbd5e1;
}
.data-table thead {
  position: sticky;
  top: 0;
  background: #1e232f;
  z-index: 2;
}
.data-table th {
  text-align: left;
  padding: 0.75rem;
  font-size: 0.7rem;
  font-weight: 600;
  color: #94a3b8;
  border-bottom: 1px solid #2a3447;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  white-space: nowrap;
}
.data-table td {
  padding: 0.6rem 0.75rem;
  border-bottom: 1px solid rgba(35, 47, 72, 0.4);
  vertical-align: middle;
}
.data-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.02);
}
.id-cell { color: #64748b; font-family: monospace; }
.text-cell.mono { font-family: monospace; }
.notes-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.col-id { width: 60px; }
.col-actions { width: 92px; }

/* Badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  font-size: 0.7rem;
  border-radius: 9999px;
  white-space: nowrap;
}
.badge-cat { background: rgba(59, 130, 246, 0.15); color: #60a5fa; }
.badge-endtype { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.badge-empty { background: rgba(148, 163, 184, 0.12); color: #94a3b8; border: 1px dashed #475569; }
.badge-src-classification { background: rgba(168, 85, 247, 0.15); color: #c084fc; }
.badge-src-pattern_expanded { background: rgba(245, 158, 11, 0.15); color: #fbbf24; }
.badge-src-dc_inventory { background: rgba(100, 116, 139, 0.18); color: #94a3b8; }
.badge-src-user_confirmed { background: rgba(34, 197, 94, 0.15); color: #22c55e; }
.badge-src-manual { background: rgba(99, 102, 241, 0.15); color: #818cf8; }
.badge-alias { background: rgba(245, 158, 11, 0.15); color: #fbbf24; cursor: help; }
.aliases-cell { text-align: center; }
.text-muted { color: #475569; font-size: 0.75rem; }

/* Alias editor in dialog */
.alias-editor {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  background: #0f1525;
  border: 1px solid #2a3447;
  border-radius: 0.375rem;
  padding: 0.5rem;
}
.alias-tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  min-height: 28px;
}
.alias-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  background: rgba(245, 158, 11, 0.18);
  color: #fbbf24;
  border-radius: 4px;
  padding: 2px 6px 2px 8px;
  font-size: 0.75rem;
  font-family: monospace;
}
.alias-remove {
  background: transparent;
  border: none;
  color: #fbbf24;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  padding: 0;
}
.alias-remove .material-symbols-outlined { font-size: 0.85rem; }
.alias-remove:hover { color: #f87171; }
.alias-empty { color: #64748b; font-size: 0.7rem; padding: 4px 8px; }
.alias-input-row {
  display: flex;
  gap: 6px;
}
.alias-input-row input {
  flex: 1;
  background: #0a0f1c;
  border: 1px solid #2a3447;
  border-radius: 0.375rem;
  padding: 0.4rem 0.625rem;
  color: #e2e8f0;
  font-size: 0.75rem;
  outline: none;
}
.btn-sm { padding: 0.4rem 0.75rem; font-size: 0.75rem; }
.alias-hint { color: #64748b; font-size: 0.7rem; margin: 0; }

/* Actions */
.actions {
  display: flex;
  gap: 4px;
}
.action-btn {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 4px;
  width: 28px;
  height: 28px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: #94a3b8;
  transition: all 0.15s;
}
.action-btn .material-symbols-outlined { font-size: 1rem; }
.action-btn:hover {
  background: rgba(255, 255, 255, 0.06);
  color: #e2e8f0;
}
.action-btn.delete:hover { color: #f87171; }

.empty-state {
  padding: 3rem;
  text-align: center;
  color: #64748b;
}
.empty-state .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pagination-info {
  color: #94a3b8;
  font-size: 0.75rem;
}
.pagination-controls {
  display: flex;
  gap: 0.375rem;
  align-items: center;
}
.page-btn {
  background: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.375rem;
  width: 30px;
  height: 30px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  color: #94a3b8;
  cursor: pointer;
}
.page-btn:hover:not(:disabled) {
  color: #e2e8f0;
  background: #2a3447;
}
.page-btn:disabled { opacity: 0.4; cursor: not-allowed; }
.page-btn .material-symbols-outlined { font-size: 1rem; }

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.dialog {
  background: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.5rem;
  width: 580px;
  max-width: 90vw;
  max-height: 88vh;
  overflow: auto;
}
.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #2a3447;
}
.dialog-header h3 { margin: 0; color: #e2e8f0; font-size: 1rem; }
.close-btn {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
}
.close-btn:hover { color: #f87171; }
.dialog-body { padding: 1.25rem; display: flex; flex-direction: column; gap: 0.75rem; }
.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem;
}
.form-group {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.form-group label {
  font-size: 0.75rem;
  color: #94a3b8;
}
.form-group input,
.form-group select,
.form-group textarea {
  background: #0f1525;
  border: 1px solid #2a3447;
  border-radius: 0.375rem;
  padding: 0.5rem 0.625rem;
  color: #e2e8f0;
  font-size: 0.8rem;
  outline: none;
}
.form-group textarea { resize: vertical; min-height: 56px; }
.dialog-footer {
  padding: 0.875rem 1.25rem;
  border-top: 1px solid #2a3447;
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
