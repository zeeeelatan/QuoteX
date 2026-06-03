<template>
  <div class="lenovo-framework-management">
    <!-- Tabs -->
    <div class="tabs-bar">
      <button
        v-for="tab in TABS"
        :key="tab.key"
        class="tab-btn"
        :class="{ active: activeTab === tab.key }"
        @click="switchTab(tab.key)"
      >
        {{ tab.label }}
        <span class="tab-count">{{ tabCounts[tab.key] ?? '—' }}</span>
      </button>
    </div>

    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增
        </button>
        <button class="btn-danger" @click="clearAll">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空当前表
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            type="text"
            v-model="searchText"
            placeholder="搜索（支持模糊匹配任意字段）"
          />
        </div>
      </div>
    </div>

    <!-- Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th v-for="f in currentTab.fields" :key="f.key" :style="f.width ? { width: f.width } : {}">
              {{ f.label }}
            </th>
            <th class="actions-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="row in pagedRows" :key="row.id">
            <td v-for="f in currentTab.fields" :key="f.key">
              {{ formatCell(row[f.key], f) }}
            </td>
            <td class="actions">
              <button class="action-btn edit" @click="openDialog(row)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteRow(row.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="pagedRows.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>{{ loading ? '加载中…' : '暂无数据' }}</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">共 {{ filteredRows.length }} 条</div>
      <div class="pagination-controls">
        <button class="pagination-btn" :disabled="currentPage === 1" @click="currentPage--">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <span class="pagination-current">{{ currentPage }} / {{ totalPages }}</span>
        <button class="pagination-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <select v-model="pageSize" class="page-size-select">
          <option :value="15">15 条/页</option>
          <option :value="30">30 条/页</option>
          <option :value="50">50 条/页</option>
          <option :value="100">100 条/页</option>
        </select>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="dialogVisible" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingRow ? '编辑' : '新增' }} - {{ currentTab.label }}</h3>
          <button class="dialog-close" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-grid">
            <div class="form-item" v-for="f in currentTab.fields" :key="f.key">
              <label>
                {{ f.label }}
                <span v-if="f.required" class="required-mark">*</span>
              </label>
              <select v-if="f.type === 'select'" v-model="formData[f.key]">
                <option v-for="o in f.options" :key="o" :value="o">{{ o }}</option>
              </select>
              <select v-else-if="f.type === 'boolean'" v-model="formData[f.key]">
                <option :value="false">否</option>
                <option :value="true">是</option>
              </select>
              <input
                v-else-if="f.type === 'number'"
                type="number"
                step="0.01"
                v-model.number="formData[f.key]"
              />
              <input v-else type="text" v-model="formData[f.key]" />
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveRow">保存</button>
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

type FieldType = 'text' | 'number' | 'select' | 'boolean'

interface FieldDef {
  key: string
  label: string
  type: FieldType
  required?: boolean
  options?: string[]
  width?: string
}

interface TabDef {
  key: string
  label: string
  apiPath: string
  fields: FieldDef[]
}

const SLA_TAPE = ['5*9*NBD维保', '7*24*ND维保', '7*24*4上门维保']
const SLA_SERVER = ['5*9*NBD', '7*24', '7*24*4']
const END_GLB = ['低端', '中端', '高端', '超高端', 'L1', 'L2', 'M']

const TABS: TabDef[] = [
  {
    key: 'classification',
    label: '机型分类',
    apiPath: '/lenovo/classification/',
    fields: [
      { key: 'device_category', label: '设备大类', type: 'select', required: true,
        options: ['磁带库', '光纤交换机', '网络设备', '服务器', 'IB交换机', '小型机', '存储'] },
      { key: 'brand', label: '品牌', type: 'text' },
      { key: 'series', label: '系列', type: 'text' },
      { key: 'model', label: '型号', type: 'text', required: true },
      { key: 'mt_code', label: 'MT', type: 'text' },
      { key: 'end_type', label: '端型', type: 'select', required: true, options: END_GLB },
      { key: 'sub_category', label: '子类', type: 'select',
        options: ['', '网络交换机', '路由器', '无线控制器', '无线AP'] },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'pattern-rule',
    label: '通配规则',
    apiPath: '/lenovo/pattern-rule/',
    fields: [
      { key: 'device_category', label: '设备大类', type: 'select', required: true,
        options: ['服务器', '存储'] },
      { key: 'brand', label: '品牌', type: 'text', required: true },
      { key: 'pattern_raw', label: '原始 pattern', type: 'text', required: true },
      { key: 'pattern_regex', label: '正则', type: 'text', required: true },
      { key: 'end_type', label: '端型', type: 'select', required: true, options: END_GLB },
      { key: 'priority', label: '优先级', type: 'number' },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'tape',
    label: '磁带库价格',
    apiPath: '/lenovo/prices/tape/',
    fields: [
      { key: 'end_type', label: '端型', type: 'select', required: true, options: ['低端', '中端', '高端'] },
      { key: 'drive_config', label: '驱动器配置', type: 'select', required: true,
        options: ['LTO5', 'LTO6', 'LTO7', 'LTO8'] },
      { key: 'sla', label: 'SLA', type: 'select', required: true, options: SLA_TAPE },
      { key: 'price', label: '单价', type: 'number', required: true },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'network',
    label: '网络价格',
    apiPath: '/lenovo/prices/network/',
    fields: [
      { key: 'device_category', label: '设备大类', type: 'select', required: true,
        options: ['FC光纤交换机', '网络交换机', '路由器', '无线控制器', 'IB光纤交换机', '无线AP'] },
      { key: 'end_type', label: '端型', type: 'select', required: true, options: ['低端', '中端'] },
      { key: 'sla', label: 'SLA', type: 'select', required: true, options: SLA_TAPE },
      { key: 'price', label: '单价', type: 'number', required: true },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'server',
    label: '服务器价格',
    apiPath: '/lenovo/prices/server/',
    fields: [
      { key: 'end_type', label: '端型', type: 'select', required: true, options: ['低端', '中端', '高端'] },
      { key: 'includes_ssd', label: '含 SSD', type: 'boolean', required: true },
      { key: 'package_type', label: '报价类型', type: 'select', required: true,
        options: ['备件维保', '整包'] },
      { key: 'sla', label: 'SLA', type: 'select', required: true, options: SLA_SERVER },
      { key: 'includes_disk', label: '含硬盘不返还', type: 'boolean', required: true },
      { key: 'price', label: '单价', type: 'number', required: true },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'storage',
    label: '存储价格',
    apiPath: '/lenovo/prices/storage/',
    fields: [
      { key: 'end_type', label: '端型', type: 'select', required: true, options: ['L1', 'L2', 'M'] },
      { key: 'sla', label: 'SLA', type: 'select', required: true, options: SLA_SERVER },
      { key: 'includes_disk_no_return', label: '含硬盘不回收', type: 'boolean', required: true },
      { key: 'price', label: '单价', type: 'number', required: true },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'minicomputer',
    label: '小型机价格',
    apiPath: '/lenovo/prices/minicomputer/',
    fields: [
      { key: 'end_type', label: '端型', type: 'select', required: true,
        options: ['低端', '中端', '高端', '超高端'] },
      { key: 'sla', label: 'SLA', type: 'select', required: true, options: SLA_TAPE },
      { key: 'includes_disk', label: '含硬盘不返还', type: 'boolean', required: true },
      { key: 'price', label: '单价', type: 'number', required: true },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
  {
    key: 'inspection',
    label: '巡检价格',
    apiPath: '/lenovo/prices/inspection/',
    fields: [
      { key: 'unit', label: '单位', type: 'select', required: true, options: ['人天', '半人天'] },
      { key: 'price', label: '单价', type: 'number', required: true },
      { key: 'tax_rate', label: '税率', type: 'number' },
      { key: 'notes', label: '备注', type: 'text' },
    ],
  },
]

const activeTab = ref<string>('classification')
const rows = ref<any[]>([])
const tabCounts = ref<Record<string, number>>({})
const loading = ref(false)
const searchText = ref('')
const currentPage = ref(1)
const pageSize = ref(30)

const dialogVisible = ref(false)
const editingRow = ref<any | null>(null)
const formData = ref<Record<string, any>>({})

const currentTab = computed(() => TABS.find(t => t.key === activeTab.value)!)

const filteredRows = computed(() => {
  if (!searchText.value.trim()) return rows.value
  const q = searchText.value.trim().toLowerCase()
  return rows.value.filter(r =>
    currentTab.value.fields.some(f => String(r[f.key] ?? '').toLowerCase().includes(q))
  )
})

const totalPages = computed(() =>
  Math.max(1, Math.ceil(filteredRows.value.length / pageSize.value))
)

const pagedRows = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRows.value.slice(start, start + pageSize.value)
})

function formatCell(value: any, field: FieldDef): string {
  if (value === null || value === undefined || value === '') return '-'
  if (field.type === 'boolean') return value ? '是' : '否'
  if (field.type === 'number') return String(value)
  return String(value)
}

async function loadRows() {
  loading.value = true
  try {
    const resp = await axios.get(`${API_URL}${currentTab.value.apiPath}`)
    rows.value = resp.data || []
    tabCounts.value[activeTab.value] = rows.value.length
  } catch (e: any) {
    ElMessage.error(`加载失败：${e?.response?.data?.detail || e?.message}`)
  } finally {
    loading.value = false
  }
}

async function loadAllCounts() {
  // 加载各 tab 总数（仅展示用，不阻塞）
  await Promise.all(TABS.map(async tab => {
    if (tab.key === activeTab.value) return  // 当前 tab loadRows 时会更新
    try {
      const resp = await axios.get(`${API_URL}${tab.apiPath}`)
      tabCounts.value[tab.key] = (resp.data || []).length
    } catch {
      tabCounts.value[tab.key] = 0
    }
  }))
}

function switchTab(key: string) {
  if (activeTab.value === key) return
  activeTab.value = key
  currentPage.value = 1
  searchText.value = ''
  loadRows()
}

function openDialog(row?: any) {
  editingRow.value = row || null
  const init: Record<string, any> = {}
  currentTab.value.fields.forEach(f => {
    if (row) {
      init[f.key] = row[f.key]
    } else {
      // 默认值
      if (f.type === 'boolean') init[f.key] = false
      else if (f.type === 'number') init[f.key] = 0
      else init[f.key] = ''
    }
  })
  // pattern_rule 默认 priority
  if (currentTab.value.key === 'pattern-rule' && !row) init.priority = 100
  if (currentTab.value.key === 'inspection' && !row) init.tax_rate = 0.06
  formData.value = init
  dialogVisible.value = true
}

function closeDialog() {
  dialogVisible.value = false
  editingRow.value = null
  formData.value = {}
}

async function saveRow() {
  // 必填校验
  for (const f of currentTab.value.fields) {
    if (f.required) {
      const v = formData.value[f.key]
      if (v === '' || v === null || v === undefined) {
        ElMessage.warning(`${f.label} 为必填`)
        return
      }
    }
  }
  try {
    if (editingRow.value) {
      await axios.put(
        `${API_URL}${currentTab.value.apiPath}${editingRow.value.id}`,
        formData.value,
      )
      ElMessage.success('已更新')
    } else {
      await axios.post(`${API_URL}${currentTab.value.apiPath}`, formData.value)
      ElMessage.success('已新增')
    }
    closeDialog()
    await loadRows()
  } catch (e: any) {
    ElMessage.error(`保存失败：${e?.response?.data?.detail || e?.message}`)
  }
}

async function deleteRow(id: number) {
  try {
    await ElMessageBox.confirm('确认删除该记录？', '提示', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning',
    })
  } catch {
    return
  }
  try {
    await axios.delete(`${API_URL}${currentTab.value.apiPath}${id}`)
    ElMessage.success('已删除')
    await loadRows()
  } catch (e: any) {
    ElMessage.error(`删除失败：${e?.response?.data?.detail || e?.message}`)
  }
}

async function clearAll() {
  try {
    await ElMessageBox.confirm(
      `确认清空"${currentTab.value.label}"全部数据？该操作不可恢复。`,
      '危险操作',
      { confirmButtonText: '清空', cancelButtonText: '取消', type: 'error' },
    )
  } catch {
    return
  }
  try {
    await axios.delete(`${API_URL}${currentTab.value.apiPath}`)
    ElMessage.success('已清空')
    await loadRows()
  } catch (e: any) {
    ElMessage.error(`清空失败：${e?.response?.data?.detail || e?.message}`)
  }
}

onMounted(async () => {
  await loadRows()
  loadAllCounts()
})
</script>

<style scoped>
.lenovo-framework-management {
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.tabs-bar {
  display: flex;
  gap: 0.4rem;
  border-bottom: 1px solid rgba(75, 97, 137, 0.25);
  overflow-x: auto;
  flex-wrap: wrap;
}

.tab-btn {
  padding: 0.55rem 1rem;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #8aa0c0;
  cursor: pointer;
  font-size: 0.9rem;
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  transition: color 0.15s, border-color 0.15s;
}

.tab-btn:hover {
  color: #c7d3e6;
}

.tab-btn.active {
  color: #74a8ff;
  border-bottom-color: #2563eb;
  font-weight: 600;
}

.tab-count {
  font-size: 0.75rem;
  padding: 0.05rem 0.45rem;
  border-radius: 0.5rem;
  background: rgba(75, 97, 137, 0.25);
  color: #c7d3e6;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  flex-wrap: wrap;
}

.toolbar-left {
  display: flex;
  gap: 0.5rem;
}

.btn-primary, .btn-danger, .btn-secondary {
  display: inline-flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.45rem 0.9rem;
  border-radius: 0.4rem;
  border: none;
  cursor: pointer;
  font-size: 0.85rem;
}

.btn-primary { background: #2563eb; color: #fff; }
.btn-primary:hover { background: #1d4ed8; }
.btn-danger { background: #dc2626; color: #fff; }
.btn-danger:hover { background: #b91c1c; }
.btn-secondary { background: rgba(75, 97, 137, 0.25); color: #e3eaf5; }

.search-box {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  background: rgba(20, 30, 48, 0.5);
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.4rem;
  color: #c7d3e6;
}

.search-box input {
  background: transparent;
  border: none;
  outline: none;
  color: #e3eaf5;
  font-size: 0.85rem;
  width: 18rem;
}

.table-container {
  overflow: auto;
  background: rgba(20, 30, 48, 0.4);
  border: 1px solid rgba(75, 97, 137, 0.25);
  border-radius: 0.5rem;
  min-height: 18rem;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
}

.data-table th {
  text-align: left;
  padding: 0.6rem 0.85rem;
  background: rgba(20, 30, 48, 0.7);
  border-bottom: 1px solid rgba(75, 97, 137, 0.25);
  color: #8aa0c0;
  font-weight: 500;
  white-space: nowrap;
  position: sticky;
  top: 0;
}

.data-table td {
  padding: 0.5rem 0.85rem;
  border-bottom: 1px solid rgba(75, 97, 137, 0.12);
  color: #d6dfee;
}

.actions {
  white-space: nowrap;
  display: flex;
  gap: 0.3rem;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.85rem;
  height: 1.85rem;
  background: transparent;
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.35rem;
  color: #c7d3e6;
  cursor: pointer;
}

.action-btn.edit:hover { color: #74a8ff; border-color: #2563eb; }
.action-btn.delete:hover { color: #f87171; border-color: #dc2626; }

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 2rem;
  color: #6b7d96;
}

.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

.pagination-info { color: #8aa0c0; font-size: 0.85rem; }

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
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

.pagination-btn:disabled { opacity: 0.4; cursor: not-allowed; }

.pagination-current { color: #c7d3e6; font-size: 0.85rem; padding: 0 0.5rem; }

.page-size-select {
  padding: 0.35rem 0.5rem;
  background: rgba(20, 30, 48, 0.6);
  border: 1px solid rgba(75, 97, 137, 0.3);
  border-radius: 0.35rem;
  color: #c7d3e6;
  font-size: 0.85rem;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  width: min(640px, 92vw);
  background: #0f1825;
  border: 1px solid rgba(75, 97, 137, 0.35);
  border-radius: 0.6rem;
  display: flex;
  flex-direction: column;
  max-height: 86vh;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid rgba(75, 97, 137, 0.25);
}

.dialog-header h3 { margin: 0; color: #e3eaf5; font-size: 1rem; }

.dialog-close {
  background: transparent;
  border: none;
  color: #8aa0c0;
  cursor: pointer;
}

.dialog-body {
  padding: 1rem 1.1rem;
  overflow-y: auto;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem 1rem;
}

.form-item { display: flex; flex-direction: column; gap: 0.3rem; }

.form-item label { color: #8aa0c0; font-size: 0.8rem; }

.required-mark { color: #f87171; margin-left: 0.15rem; }

.form-item input, .form-item select {
  padding: 0.5rem 0.7rem;
  background: rgba(20, 30, 48, 0.8);
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.4rem;
  color: #e3eaf5;
  font-size: 0.88rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  padding: 0.85rem 1.1rem;
  border-top: 1px solid rgba(75, 97, 137, 0.25);
}
</style>
