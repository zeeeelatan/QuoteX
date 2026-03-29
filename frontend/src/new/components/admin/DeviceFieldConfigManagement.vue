<template>
  <div class="field-config-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增字段配置
        </button>
      </div>
      <div class="toolbar-right">
        <div class="filter-group">
          <label>设备分类</label>
          <select v-model="filterDeviceType" @change="fetchConfigs">
            <option value="">全部（含全局）</option>
            <option v-for="dt in deviceTypes" :key="dt" :value="dt">{{ dt }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>作用域</label>
          <select v-model="filterScope" @change="fetchConfigs">
            <option value="">全部</option>
            <option value="type">类型级</option>
            <option value="instance">实例级</option>
          </select>
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>字段标识</th>
            <th>显示名</th>
            <th>字段类型</th>
            <th>必填</th>
            <th>枚举选项</th>
            <th>默认值</th>
            <th>排序</th>
            <th>作用域</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <template v-for="group in groupedConfigs" :key="group.device_type">
            <tr class="group-header-row">
              <td colspan="9">
                <span class="group-label">
                  <span class="material-symbols-outlined">folder</span>
                  {{ group.device_type || '全局配置' }}
                </span>
              </td>
            </tr>
            <tr v-for="item in group.items" :key="item.id">
              <td><code class="field-key-badge">{{ item.field_key }}</code></td>
              <td>{{ item.field_label }}</td>
              <td><span class="type-badge" :class="'type-' + item.field_type">{{ item.field_type }}</span></td>
              <td>
                <span v-if="item.required" class="required-yes">
                  <span class="material-symbols-outlined">check_circle</span>
                </span>
                <span v-else class="required-no">-</span>
              </td>
              <td>
                <div v-if="item.field_type === 'enum' && item.enum_options && item.enum_options.length > 0" class="enum-tags">
                  <span v-for="(opt, idx) in item.enum_options.slice(0, 3)" :key="idx" class="enum-tag">{{ opt }}</span>
                  <span v-if="item.enum_options.length > 3" class="more-tags">+{{ item.enum_options.length - 3 }}</span>
                </div>
                <span v-else class="text-muted">-</span>
              </td>
              <td>{{ item.default_value || '-' }}</td>
              <td>{{ item.display_order ?? 0 }}</td>
              <td><span class="scope-badge" :class="'scope-' + item.scope">{{ item.scope === 'type' ? '类型级' : '实例级' }}</span></td>
              <td class="actions">
                <button class="action-btn edit" @click="openDialog(item)" title="编辑">
                  <span class="material-symbols-outlined">edit</span>
                </button>
                <button class="action-btn delete" @click="deleteConfig(item.id)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <div v-if="configList.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">
        共 {{ configList.length }} 条
      </div>
      <div class="pagination-controls">
        <button
          class="pagination-btn"
          :disabled="currentPage === 1"
          @click="currentPage--"
        >
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <span class="pagination-current">{{ currentPage }}</span>
        <button
          class="pagination-btn"
          :disabled="currentPage >= totalPages"
          @click="currentPage++"
        >
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <select v-model="pageSize" class="page-size-select">
          <option :value="15">15条/页</option>
          <option :value="20">20条/页</option>
          <option :value="50">50条/页</option>
          <option :value="100">100条/页</option>
        </select>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="dialogVisible" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ form.id ? '编辑字段配置' : '新增字段配置' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>设备分类 <span class="hint">（支持一/二/三级分类名称，留空表示全局配置）</span></label>
            <input v-model="form.device_type" placeholder="例如: X86服务器、网络设备、计算" />
          </div>
          <div class="form-group">
            <label>字段标识 <span class="required-mark">*</span></label>
            <input v-model="form.field_key" placeholder="例如: port_speed" />
          </div>
          <div class="form-group">
            <label>显示名称 <span class="required-mark">*</span></label>
            <input v-model="form.field_label" placeholder="例如: 端口速率" />
          </div>
          <div class="form-group">
            <label>字段类型 <span class="required-mark">*</span></label>
            <select v-model="form.field_type">
              <option value="string">string</option>
              <option value="number">number</option>
              <option value="enum">enum</option>
              <option value="boolean">boolean</option>
            </select>
          </div>
          <div class="form-group">
            <label class="checkbox-label">
              <input type="checkbox" v-model="form.required" />
              <span>必填</span>
            </label>
          </div>
          <div v-if="form.field_type === 'enum'" class="form-group">
            <label>枚举选项</label>
            <div class="enum-input-area">
              <div class="enum-tags-edit">
                <span v-for="(opt, idx) in form.enum_options" :key="idx" class="enum-tag-edit">
                  {{ opt }}
                  <button class="remove-tag" @click="removeEnumOption(idx)">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </span>
              </div>
              <div class="enum-add-row">
                <input
                  v-model="newEnumOption"
                  placeholder="输入选项后按回车添加"
                  @keydown.enter.prevent="addEnumOption"
                />
                <button class="btn-add-tag" @click="addEnumOption">
                  <span class="material-symbols-outlined">add</span>
                </button>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>默认值</label>
            <input v-model="form.default_value" placeholder="默认值" />
          </div>
          <div class="form-group">
            <label>排序</label>
            <input v-model.number="form.display_order" type="number" placeholder="0" />
          </div>
          <div class="form-group">
            <label>作用域 <span class="required-mark">*</span></label>
            <select v-model="form.scope">
              <option value="type">类型级</option>
              <option value="instance">实例级</option>
            </select>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveConfig">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface FieldConfig {
  id: number
  device_type: string | null
  field_key: string
  field_label: string
  field_type: string
  required: boolean
  enum_options: string[] | null
  default_value: string | null
  display_order: number
  scope: string
}

// State
const configList = ref<FieldConfig[]>([])
const deviceTypes = ref<string[]>([])
const filterDeviceType = ref('')
const filterScope = ref('')
const dialogVisible = ref(false)
const newEnumOption = ref('')
const currentPage = ref(1)
const pageSize = ref(15)

const form = ref({
  id: null as number | null,
  device_type: '' as string,
  field_key: '',
  field_label: '',
  field_type: 'string',
  required: false,
  enum_options: [] as string[],
  default_value: '',
  display_order: 0,
  scope: 'type'
})

// Computed
const totalPages = computed(() => Math.ceil(configList.value.length / pageSize.value))

const pagedConfigList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return configList.value.slice(start, start + pageSize.value)
})

const groupedConfigs = computed(() => {
  const groups: Record<string, FieldConfig[]> = {}
  for (const item of pagedConfigList.value) {
    const key = item.device_type || ''
    if (!groups[key]) groups[key] = []
    groups[key].push(item)
  }
  // Sort: global (empty key) first, then alphabetical
  const sorted = Object.entries(groups).sort(([a], [b]) => {
    if (a === '') return -1
    if (b === '') return 1
    return a.localeCompare(b)
  })
  return sorted.map(([device_type, items]) => ({ device_type, items }))
})

// Watch page size changes
watch(pageSize, () => {
  currentPage.value = 1
})

// Fetch device types
async function fetchDeviceTypes() {
  try {
    const response = await axios.get(`${API_URL}/device-field-configs/device-types`)
    deviceTypes.value = response.data || []
  } catch (error) {
    console.error('Failed to load device types:', error)
  }
}

// Fetch configs
async function fetchConfigs() {
  try {
    const params: Record<string, string> = {}
    if (filterDeviceType.value) params.device_type = filterDeviceType.value
    if (filterScope.value) params.scope = filterScope.value
    const response = await axios.get(`${API_URL}/device-field-configs/`, { params })
    configList.value = response.data?.data || response.data || []
    currentPage.value = 1
  } catch (error) {
    console.error('Failed to load configs:', error)
  }
}

// Enum options management
function addEnumOption() {
  const val = newEnumOption.value.trim()
  if (!val) return
  if (form.value.enum_options.includes(val)) {
    showToast('该选项已存在', 'error')
    return
  }
  form.value.enum_options.push(val)
  newEnumOption.value = ''
}

function removeEnumOption(idx: number) {
  form.value.enum_options.splice(idx, 1)
}

// Open dialog
function openDialog(row?: FieldConfig) {
  if (row) {
    form.value = {
      id: row.id,
      device_type: row.device_type || '',
      field_key: row.field_key,
      field_label: row.field_label,
      field_type: row.field_type,
      required: row.required,
      enum_options: row.enum_options ? [...row.enum_options] : [],
      default_value: row.default_value || '',
      display_order: row.display_order ?? 0,
      scope: row.scope || 'type'
    }
  } else {
    form.value = {
      id: null,
      device_type: filterDeviceType.value || '',
      field_key: '',
      field_label: '',
      field_type: 'string',
      required: false,
      enum_options: [],
      default_value: '',
      display_order: 0,
      scope: 'type'
    }
  }
  newEnumOption.value = ''
  dialogVisible.value = true
}

// Close dialog
function closeDialog() {
  dialogVisible.value = false
}

// Save config
async function saveConfig() {
  if (!form.value.field_key.trim()) {
    showToast('字段标识不能为空', 'error')
    return
  }
  if (!form.value.field_label.trim()) {
    showToast('显示名称不能为空', 'error')
    return
  }
  if (!form.value.field_type) {
    showToast('请选择字段类型', 'error')
    return
  }
  if (!form.value.scope) {
    showToast('请选择作用域', 'error')
    return
  }

  try {
    const payload = {
      device_type: form.value.device_type.trim() || null,
      field_key: form.value.field_key.trim(),
      field_label: form.value.field_label.trim(),
      field_type: form.value.field_type,
      required: form.value.required,
      enum_options: form.value.field_type === 'enum' ? form.value.enum_options : null,
      default_value: form.value.default_value.trim() || null,
      display_order: form.value.display_order ?? 0,
      scope: form.value.scope
    }

    if (form.value.id) {
      await axios.put(`${API_URL}/device-field-configs/${form.value.id}`, payload)
      showToast('修改成功')
    } else {
      await axios.post(`${API_URL}/device-field-configs/`, payload)
      showToast('新增成功')
    }

    dialogVisible.value = false
    fetchConfigs()
    fetchDeviceTypes()
  } catch (error: any) {
    console.error('Failed to save config:', error)
    showToast(error.response?.data?.detail || '保存失败', 'error')
  }
}

// Delete config
async function deleteConfig(id: number) {
  if (!confirm('确定要删除该字段配置吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/device-field-configs/${id}`)
    showToast('删除成功')
    fetchConfigs()
    fetchDeviceTypes()
  } catch (error: any) {
    console.error('Failed to delete config:', error)
    showToast(error.response?.data?.detail || '删除失败', 'error')
  }
}

// Toast notification
function showToast(message: string, type: 'success' | 'error' = 'success') {
  const toast = document.createElement('div')
  toast.className = `toast toast-${type}`
  toast.textContent = message
  toast.style.cssText = `
    position: fixed;
    top: 20px;
    right: 20px;
    padding: 12px 20px;
    background: ${type === 'success' ? '#10b981' : '#ef4444'};
    color: white;
    border-radius: 6px;
    z-index: 9999;
    animation: slideIn 0.3s ease;
  `
  document.body.appendChild(toast)
  setTimeout(() => {
    toast.remove()
  }, 3000)
}

onMounted(() => {
  fetchDeviceTypes()
  fetchConfigs()
})
</script>

<style scoped>
.field-config-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

.toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  color: #94a3b8;
  white-space: nowrap;
}

.filter-group select {
  padding: 0.5rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  min-width: 140px;
}

.filter-group select:focus {
  outline: none;
  border-color: #135bec;
}

.btn-primary,
.btn-secondary,
.btn-success,
.btn-warning,
.btn-danger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  color: white;
}

.btn-primary {
  background-color: #135bec;
}
.btn-primary:hover {
  background-color: #1d64f2;
}

.btn-secondary {
  background-color: #334155;
  color: #e2e8f0;
}
.btn-secondary:hover {
  background-color: #475569;
}

.btn-success {
  background-color: #10b981;
}
.btn-success:hover {
  background-color: #059669;
}

.btn-warning {
  background-color: #f59e0b;
}
.btn-warning:hover {
  background-color: #d97706;
}

.btn-danger {
  background-color: #ef4444;
}
.btn-danger:hover {
  background-color: #dc2626;
}

.table-container {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  background-color: #0f172a;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  position: sticky;
  top: 0;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #334155;
  font-size: 0.875rem;
  color: #e2e8f0;
}

.data-table tbody tr:hover:not(.group-header-row) {
  background-color: #334155;
}

/* Group header row */
.group-header-row td {
  background-color: rgba(30, 41, 59, 0.4);
  padding: 0.5rem 1rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.group-label {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #94a3b8;
}

.group-label .material-symbols-outlined {
  font-size: 1rem;
  color: #64748b;
}

/* Field key badge */
.field-key-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: monospace;
}

/* Type badges */
.type-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: monospace;
}

.type-string {
  background-color: rgba(16, 185, 129, 0.15);
  color: #10b981;
}

.type-number {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.type-enum {
  background-color: rgba(139, 92, 246, 0.15);
  color: #8b5cf6;
}

.type-boolean {
  background-color: rgba(6, 182, 212, 0.15);
  color: #06b6d4;
}

/* Scope badges */
.scope-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.scope-type {
  background-color: rgba(19, 91, 236, 0.12);
  color: #60a5fa;
}

.scope-instance {
  background-color: rgba(245, 158, 11, 0.12);
  color: #fbbf24;
}

/* Required indicators */
.required-yes .material-symbols-outlined {
  font-size: 1rem;
  color: #10b981;
}

.required-no {
  color: #64748b;
}

/* Enum tags in table */
.enum-tags {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  flex-wrap: wrap;
}

.enum-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.0625rem 0.375rem;
  background-color: rgba(139, 92, 246, 0.1);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.2);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.more-tags {
  display: inline-flex;
  align-items: center;
  padding: 0.0625rem 0.375rem;
  background-color: rgba(100, 116, 139, 0.1);
  color: #94a3b8;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.text-muted {
  color: #64748b;
}

.actions {
  display: flex;
  gap: 0.25rem;
}

.action-btn {
  background: transparent;
  border: none;
  padding: 0.25rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #64748b;
}

.action-btn.edit:hover {
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.action-btn.delete:hover {
  color: #ef4444;
  background-color: rgba(239, 68, 68, 0.1);
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #64748b;
}

.empty-state .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 1rem;
}

/* Pagination */
.pagination-container {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: #94a3b8;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.pagination-btn {
  background: transparent;
  border: 1px solid #334155;
  color: #94a3b8;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #e2e8f0;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-current {
  font-size: 0.875rem;
  color: #e2e8f0;
  min-width: 2rem;
  text-align: center;
}

.page-size-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #e2e8f0;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  margin-left: 0.5rem;
}

.page-size-select:focus {
  outline: none;
  border-color: #135bec;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  width: 90%;
  max-width: 560px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
}

.dialog-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
}

.close-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
}

.dialog-body {
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-group label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.form-group .hint {
  font-size: 0.75rem;
  color: #64748b;
}

.required-mark {
  color: #ef4444;
}

.form-group input[type="text"],
.form-group input[type="number"],
.form-group input:not([type]) {
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.form-group input[type="text"]:focus,
.form-group input[type="number"]:focus,
.form-group input:not([type]):focus {
  outline: none;
  border-color: #135bec;
}

.form-group select {
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.form-group select:focus {
  outline: none;
  border-color: #135bec;
}

/* Checkbox label */
.checkbox-label {
  display: flex;
  flex-direction: row !important;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  accent-color: #135bec;
}

.checkbox-label span {
  font-size: 0.875rem;
  color: #e2e8f0;
}

/* Enum input area */
.enum-input-area {
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 0.5rem;
}

.enum-tags-edit {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
  min-height: 1.5rem;
  margin-bottom: 0.5rem;
}

.enum-tag-edit {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.5rem;
  background-color: rgba(139, 92, 246, 0.15);
  color: #a78bfa;
  border: 1px solid rgba(139, 92, 246, 0.3);
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.remove-tag {
  background: transparent;
  border: none;
  color: inherit;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
}

.remove-tag:hover {
  color: #ef4444;
}

.remove-tag .material-symbols-outlined {
  font-size: 0.875rem;
}

.enum-add-row {
  display: flex;
  gap: 0.375rem;
}

.enum-add-row input {
  flex: 1;
  padding: 0.375rem 0.5rem;
  background-color: transparent;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.8125rem;
}

.enum-add-row input:focus {
  outline: none;
  border-color: #135bec;
}

.btn-add-tag {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.375rem;
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
  border: 1px solid rgba(19, 91, 236, 0.3);
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-tag:hover {
  background-color: rgba(19, 91, 236, 0.25);
}

.btn-add-tag .material-symbols-outlined {
  font-size: 1rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>
