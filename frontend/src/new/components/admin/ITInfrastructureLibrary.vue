<template>
  <div class="it-infrastructure-library">
    <!-- 数据表格容器 -->
    <div class="table-section">
      <!-- 筛选搜索区域 -->
      <div class="filter-search-bar">
        <div class="filter-grid">
          <div class="filter-item">
            <label>厂商</label>
            <select v-model="filters.manufacturer" @change="applyFilters">
              <option value="">全部厂商</option>
              <option v-for="m in filterOptions.manufacturers" :key="m" :value="m">{{ m }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>设备系列</label>
            <select v-model="filters.device_series" @change="applyFilters">
              <option value="">全部系列</option>
              <option v-for="s in filterOptions.series" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>业务场景</label>
            <select v-model="filters.business_scenario" @change="applyFilters">
              <option value="">全部场景</option>
              <option v-for="s in filterOptions.scenarios" :key="s" :value="s">{{ s }}</option>
            </select>
          </div>
          <div class="filter-item">
            <label>设备档次</label>
            <select v-model="filters.device_grade" @change="applyFilters">
              <option value="">全部档次</option>
              <option v-for="g in filterOptions.grades" :key="g" :value="g">{{ g }}</option>
            </select>
          </div>
          <div class="filter-item filter-search">
            <label>关键词查询</label>
            <div class="search-input-wrapper">
              <span class="material-symbols-outlined">manage_search</span>
              <input
                type="text"
                :value="searchInput"
                @input="onSearchInput"
                @keyup.enter="applyFilters"
                placeholder="型号、备注..."
              />
            </div>
          </div>
          <div class="filter-actions">
            <button class="filter-btn" @click="applyFilters" title="筛选">
              <span class="material-symbols-outlined">filter_list</span>
            </button>
            <button class="refresh-btn" @click="resetFilters" title="重置">
              <span class="material-symbols-outlined">refresh</span>
            </button>
          </div>
        </div>
      </div>

      <div class="table-wrapper">
        <!-- 批量操作栏 -->
        <div class="batch-actions-bar" v-if="selectedDevices.length > 0" :class="{ 'show': selectedDevices.length > 0 }">
          <div class="batch-info">
            <span class="material-symbols-outlined">check_circle</span>
            <span>已选择 <strong>{{ selectedDevices.length }}</strong> 项</span>
          </div>
          <div class="batch-buttons">
            <button class="batch-btn danger" @click="batchDelete" title="批量删除">
              <span class="material-symbols-outlined">delete</span>
              批量删除
            </button>
            <button class="batch-btn primary" @click="showBatchEditDialog = true" title="批量修改">
              <span class="material-symbols-outlined">edit</span>
              批量修改
            </button>
            <button class="batch-btn" @click="clearSelection" title="取消选择">
              <span class="material-symbols-outlined">close</span>
              取消
            </button>
          </div>
        </div>

        <table class="data-table">
          <thead>
            <tr>
              <th class="checkbox-col">
                <input
                  type="checkbox"
                  :checked="isAllSelected"
                  :indeterminate="isSomeSelected"
                  @change="toggleSelectAll"
                />
              </th>
              <th>厂商</th>
              <th>设备系列</th>
              <th>设备型号</th>
              <th>业务场景</th>
              <th>一级分类</th>
              <th>二级分类</th>
              <th>三级分类</th>
              <th>备注</th>
              <th>整机价格 (¥)</th>
              <th>档次</th>
              <th>机架高度(U)</th>
              <th class="actions-col">管理操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="device in devices" :key="device.id" class="table-row" :class="{ 'selected': selectedDevices.includes(device.id) }">
              <td class="checkbox-col">
                <input
                  type="checkbox"
                  :checked="selectedDevices.includes(device.id)"
                  @change="toggleSelect(device.id)"
                />
              </td>
              <td class="font-bold">{{ device.manufacturer || '-' }}</td>
              <td>{{ device.device_series || '-' }}</td>
              <td class="model-number">{{ device.model_number || '-' }}</td>
              <td>
                <span v-if="device.business_scenario" class="scenario-badge">{{ device.business_scenario }}</span>
                <span v-else>-</span>
              </td>
              <td>{{ device.primary_category || '-' }}</td>
              <td>{{ device.secondary_category || '-' }}</td>
              <td>{{ device.tertiary_category || '-' }}</td>
              <td class="remarks">
                <span :title="device.remarks">{{ truncateText(device.remarks, 20) || '-' }}</span>
              </td>
              <td class="price">{{ formatPrice(device.device_price) }}</td>
              <td>
                <div class="grade-indicator">
                  <span class="grade-dot" :class="getGradeClass(device.device_grade)"></span>
                  <span>{{ device.device_grade || '-' }}</span>
                </div>
              </td>
              <td class="rack-height">{{ device.rack_height_u || '-' }}</td>
              <td class="actions">
                <button class="action-btn edit" @click="editDevice(device)" title="编辑">
                  <span class="material-symbols-outlined">edit</span>
                </button>
                <button class="action-btn delete" @click="deleteDevice(device.id)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="devices.length === 0 && !loading" class="empty-state">
          <span class="material-symbols-outlined">inbox</span>
          <p>暂无数据</p>
        </div>
        <div v-if="loading" class="loading-state">
          <span class="material-symbols-outlined loading-icon">hourglass_empty</span>
          <p>加载中...</p>
        </div>
      </div>

      <!-- 分页 -->
      <div class="pagination">
        <div class="pagination-left">
          <p class="pagination-info">显示 {{ paginationInfo }}</p>
          <div class="page-size-selector">
            <span>每页</span>
            <select v-model="pagination.pageSize" @change="onPageSizeChange">
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="200">200</option>
            </select>
            <span>条</span>
          </div>
        </div>
        <div class="pagination-controls">
          <button
            class="page-btn"
            :disabled="pagination.page <= 1"
            @click="changePage(pagination.page - 1)"
          >
            <span class="material-symbols-outlined">chevron_left</span>
          </button>
          <button
            v-for="p in visiblePages"
            :key="p"
            class="page-btn"
            :class="{ active: p === pagination.page }"
            @click="changePage(p)"
          >
            {{ p }}
          </button>
          <button
            class="page-btn"
            :disabled="pagination.page >= totalPages"
            @click="changePage(pagination.page + 1)"
          >
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

    <!-- 添加/编辑对话框 -->
    <div v-if="showAddDialog || editingDevice" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingDevice ? '编辑设备' : '新增设备' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-grid">
            <div class="form-group">
              <label>厂商 <span class="required">*</span></label>
              <input v-model="formData.manufacturer" placeholder="例如: 华为" />
            </div>
            <div class="form-group">
              <label>设备系列</label>
              <input v-model="formData.device_series" placeholder="例如: FusionServer" />
            </div>
            <div class="form-group">
              <label>设备型号 <span class="required">*</span></label>
              <input v-model="formData.model_number" placeholder="例如: 2288H V5" />
            </div>
            <div class="form-group">
              <label>业务场景</label>
              <select v-model="formData.business_scenario">
                <option value="">请选择</option>
                <option>通用计算</option>
                <option>核心交换</option>
                <option>虚拟化</option>
                <option>存储</option>
                <option>其他</option>
              </select>
            </div>
            <div class="form-group">
              <label>一级分类</label>
              <input v-model="formData.primary_category" placeholder="例如: 计算" />
            </div>
            <div class="form-group">
              <label>二级分类</label>
              <input v-model="formData.secondary_category" placeholder="例如: 机架式" />
            </div>
            <div class="form-group">
              <label>三级分类</label>
              <input v-model="formData.tertiary_category" placeholder="例如: 2U双路" />
            </div>
            <div class="form-group">
              <label>设备档次</label>
              <select v-model="formData.device_grade">
                <option value="">请选择</option>
                <option>入门级</option>
                <option>中端级</option>
                <option>高端级</option>
              </select>
            </div>
            <div class="form-group">
              <label>机架高度(U)</label>
              <input v-model.number="formData.rack_height_u" type="number" step="1" min="0" placeholder="例如: 2" />
            </div>
            <div class="form-group">
              <label>整机价格 (¥)</label>
              <input v-model.number="formData.device_price" type="number" step="0.01" placeholder="例如: 45800.00" />
            </div>
            <div class="form-group full-width">
              <label>备注</label>
              <textarea v-model="formData.remarks" rows="2" placeholder="设备备注信息..."></textarea>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveDevice" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 批量修改对话框 -->
    <div v-if="showBatchEditDialog" class="dialog-overlay" @click="showBatchEditDialog = false">
      <div class="dialog batch-edit-dialog" @click.stop>
        <div class="dialog-header">
          <h3>批量修改设备 (已选择 {{ selectedDevices.length }} 项)</h3>
          <button class="close-btn" @click="showBatchEditDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="batch-edit-fields">
            <div class="form-group">
              <label>要修改的字段</label>
              <select v-model="batchEditField">
                <option value="">请选择要修改的字段</option>
                <option value="manufacturer">厂商</option>
                <option value="device_series">设备系列</option>
                <option value="business_scenario">业务场景</option>
                <option value="primary_category">一级分类</option>
                <option value="secondary_category">二级分类</option>
                <option value="tertiary_category">三级分类</option>
                <option value="device_grade">设备档次</option>
                <option value="rack_height_u">机架高度(U)</option>
                <option value="remarks">备注</option>
              </select>
            </div>
            <div class="form-group" v-if="batchEditField">
              <label>{{ getFieldLabel(batchEditField) }}</label>
              <input
                v-if="batchEditField !== 'device_grade'"
                v-model="batchEditValue"
                :placeholder="`输入新的${getFieldLabel(batchEditField)}值`"
              />
              <select v-else v-model="batchEditValue">
                <option value="">请选择档次</option>
                <option>入门级</option>
                <option>中端级</option>
                <option>高端级</option>
              </select>
            </div>
          </div>
          <div class="batch-preview" v-if="batchEditField && batchEditValue">
            <p class="preview-text">将会把 <strong>{{ selectedDevices.length }}</strong> 个设备的 <strong>{{ getFieldLabel(batchEditField) }}</strong> 修改为:</p>
            <p class="preview-value">"{{ batchEditValue }}"</p>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showBatchEditDialog = false">取消</button>
          <button class="btn-primary" @click="applyBatchEdit" :disabled="!batchEditField || !batchEditValue || batchSaving">
            {{ batchSaving ? '处理中...' : '确认修改' }}
          </button>
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

// 设备数据接口
interface Device {
  id: number
  manufacturer?: string
  model_number?: string
  device_series?: string
  primary_category?: string
  secondary_category?: string
  tertiary_category?: string
  business_scenario?: string
  remarks?: string
  device_grade?: string
  device_price?: number
  rack_height_u?: number  // 机架高度(U)
  created_at?: string
  updated_at?: string
}

// State
const devices = ref<Device[]>([])
const loading = ref(false)
const saving = ref(false)
const batchSaving = ref(false)
const showAddDialog = ref(false)
const showBatchEditDialog = ref(false)
const editingDevice = ref<Device | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

// 多选相关状态
const selectedDevices = ref<number[]>([])
const batchEditField = ref('')
const batchEditValue = ref('')

// 本地搜索输入状态（避免每次输入都触发响应式更新）
const searchInput = ref('')

const filters = ref({
  search: '',
  manufacturer: '',
  device_series: '',
  business_scenario: '',
  device_grade: ''
})

const filterOptions = ref({
  manufacturers: [] as string[],
  series: [] as string[],
  scenarios: [] as string[],
  grades: [] as string[]
})

const pagination = ref({
  page: 1,
  pageSize: 20,
  total: 0
})

const formData = ref({
  manufacturer: '',
  model_number: '',
  device_series: '',
  business_scenario: '',
  primary_category: '',
  secondary_category: '',
  tertiary_category: '',
  device_grade: '',
  device_price: null as number | null,
  rack_height_u: null as number | null,
  remarks: ''
})

// Computed
const paginationInfo = computed(() => {
  const start = (pagination.value.page - 1) * pagination.value.pageSize + 1
  const end = Math.min(start + devices.value.length - 1, pagination.value.total)
  return `${start} 到 ${end} 条，共 ${pagination.value.total}`
})

const totalPages = computed(() => {
  return Math.ceil(pagination.value.total / pagination.value.pageSize)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = pagination.value.page

  for (let i = Math.max(1, current - 2); i <= Math.min(total, current + 2); i++) {
    pages.push(i)
  }
  return pages
})

// 多选相关计算属性
const isAllSelected = computed(() => {
  return devices.value.length > 0 && selectedDevices.value.length === devices.value.length
})

const isSomeSelected = computed(() => {
  return selectedDevices.value.length > 0 && selectedDevices.value.length < devices.value.length
})

// 多选操作函数
function toggleSelect(deviceId: number) {
  const index = selectedDevices.value.indexOf(deviceId)
  if (index > -1) {
    selectedDevices.value.splice(index, 1)
  } else {
    selectedDevices.value.push(deviceId)
  }
}

function toggleSelectAll(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.checked) {
    selectedDevices.value = devices.value.map(d => d.id)
  } else {
    selectedDevices.value = []
  }
}

function clearSelection() {
  selectedDevices.value = []
}

async function batchDelete() {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedDevices.value.length} 个设备吗？`, '批量删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    batchSaving.value = true
    const promises = selectedDevices.value.map(id => axios.delete(`${API_URL}/devices/${id}`))
    await Promise.all(promises)

    ElMessage.success(`成功删除 ${selectedDevices.value.length} 个设备`)
    selectedDevices.value = []
    loadDevices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to batch delete:', error)
      ElMessage.error('批量删除失败')
    }
  } finally {
    batchSaving.value = false
  }
}

function getFieldLabel(field: string): string {
  const labels: Record<string, string> = {
    manufacturer: '厂商',
    device_series: '设备系列',
    business_scenario: '业务场景',
    primary_category: '一级分类',
    secondary_category: '二级分类',
    tertiary_category: '三级分类',
    device_grade: '设备档次',
    rack_height_u: '机架高度(U)',
    remarks: '备注'
  }
  return labels[field] || field
}

async function applyBatchEdit() {
  if (!batchEditField.value || !batchEditValue.value) return

  try {
    await ElMessageBox.confirm(
      `确定要将 ${selectedDevices.value.length} 个设备的 "${getFieldLabel(batchEditField.value)}" 修改为 "${batchEditValue.value}" 吗？`,
      '批量修改',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    batchSaving.value = true
    const promises = selectedDevices.value.map(id =>
      axios.put(`${API_URL}/devices/${id}`, {
        [batchEditField.value]: batchEditValue.value
      })
    )

    await Promise.all(promises)

    ElMessage.success(`成功修改 ${selectedDevices.value.length} 个设备`)
    showBatchEditDialog.value = false
    batchEditField.value = ''
    batchEditValue.value = ''
    selectedDevices.value = []
    loadDevices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to batch edit:', error)
      ElMessage.error('批量修改失败')
    }
  } finally {
    batchSaving.value = false
  }
}

// Methods
async function loadDevices() {
  loading.value = true
  try {
    const skip = (pagination.value.page - 1) * pagination.value.pageSize
    const url = `${API_URL}/devices/`
    const params = new URLSearchParams({
      skip: String(skip),
      limit: String(pagination.value.pageSize)
    })

    if (filters.value.search) params.append('search', filters.value.search)
    if (filters.value.manufacturer) params.append('manufacturer', filters.value.manufacturer)
    if (filters.value.device_series) params.append('device_series', filters.value.device_series)
    if (filters.value.business_scenario) params.append('business_scenario', filters.value.business_scenario)
    if (filters.value.device_grade) params.append('device_grade', filters.value.device_grade)

    console.log('[ITInfrastructure] Loading devices from:', url + '?' + params.toString())
    const response = await axios.get(url + '?' + params.toString())
    console.log('[ITInfrastructure] Response:', response.data)
    devices.value = response.data?.data || []
    pagination.value.total = response.data?.total || 0
  } catch (error: any) {
    console.error('[ITInfrastructure] Failed to load devices:', error)
    ElMessage.error('加载设备数据失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

async function loadFilterOptions() {
  try {
    const [manufRes, seriesRes, scenariosRes, gradesRes] = await Promise.all([
      axios.get(`${API_URL}/devices/manufacturers`),
      axios.get(`${API_URL}/devices/device-series`),
      axios.get(`${API_URL}/devices/business-scenarios`),
      axios.get(`${API_URL}/devices/device-grades`)
    ])
    filterOptions.value.manufacturers = manufRes.data || []
    filterOptions.value.series = seriesRes.data || []
    filterOptions.value.scenarios = scenariosRes.data || []
    filterOptions.value.grades = gradesRes.data || []
  } catch (error) {
    console.error('Failed to load filter options:', error)
  }
}

function resetFilters() {
  filters.value = {
    search: '',
    manufacturer: '',
    device_series: '',
    business_scenario: '',
    device_grade: ''
  }
  searchInput.value = ''
  pagination.value.page = 1
  loadDevices()
}

function onSearchInput(event: Event) {
  const target = event.target as HTMLInputElement
  searchInput.value = target.value
}

function applyFilters() {
  // 同步搜索输入到筛选条件
  filters.value.search = searchInput.value
  pagination.value.page = 1
  loadDevices()
}

function changePage(page: number) {
  pagination.value.page = page
  loadDevices()
}

function onPageSizeChange() {
  pagination.value.page = 1
  loadDevices()
}

function editDevice(device: Device) {
  editingDevice.value = device
  formData.value = {
    manufacturer: device.manufacturer || '',
    model_number: device.model_number || '',
    device_series: device.device_series || '',
    business_scenario: device.business_scenario || '',
    primary_category: device.primary_category || '',
    secondary_category: device.secondary_category || '',
    tertiary_category: device.tertiary_category || '',
    device_grade: device.device_grade || '',
    device_price: device.device_price || null,
    rack_height_u: device.rack_height_u || null,
    remarks: device.remarks || ''
  }
}

function closeDialog() {
  showAddDialog.value = false
  editingDevice.value = null
  formData.value = {
    manufacturer: '',
    model_number: '',
    device_series: '',
    business_scenario: '',
    primary_category: '',
    secondary_category: '',
    tertiary_category: '',
    device_grade: '',
    device_price: null,
    rack_height_u: null,
    remarks: ''
  }
}

async function saveDevice() {
  if (!formData.value.manufacturer || !formData.value.model_number) {
    ElMessage.warning('请填写必填项（厂商、设备型号）')
    return
  }

  saving.value = true
  try {
    const data = {
      ...formData.value,
      device_price: formData.value.device_price || null
    }

    if (editingDevice.value) {
      await axios.put(`${API_URL}/devices/${editingDevice.value.id}`, data)
      ElMessage.success('设备更新成功')
    } else {
      await axios.post(`${API_URL}/devices/`, data)
      ElMessage.success('设备添加成功')
    }

    closeDialog()
    loadDevices()
    loadFilterOptions()
  } catch (error) {
    console.error('Failed to save device:', error)
    ElMessage.error('保存设备失败')
  } finally {
    saving.value = false
  }
}

async function deleteDevice(id: number) {
  try {
    await ElMessageBox.confirm('确定要删除此设备吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await axios.delete(`${API_URL}/devices/${id}`)
    ElMessage.success('设备删除成功')
    loadDevices()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('Failed to delete device:', error)
      ElMessage.error('删除设备失败')
    }
  }
}

async function exportData() {
  try {
    const params: any = {}
    if (filters.value.search) params.search = filters.value.search
    if (filters.value.manufacturer) params.manufacturer = filters.value.manufacturer

    window.open(`${API_URL}/devices/export/data?${new URLSearchParams(params)}`, '_blank')
    ElMessage.success('导出任务已开始')
  } catch (error) {
    console.error('Failed to export:', error)
    ElMessage.error('导出失败')
  }
}

async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${API_URL}/devices/import`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success(`导入成功，共 ${response.data.count} 条记录`)
    loadDevices()
    loadFilterOptions()
  } catch (error) {
    console.error('Failed to import:', error)
    ElMessage.error('导入失败')
  } finally {
    target.value = ''
  }
}

function formatPrice(price: number | undefined): string {
  if (price === null || price === undefined) return '-'
  return price.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function truncateText(text: string | undefined, maxLength: number): string {
  if (!text) return ''
  return text.length > maxLength ? text.substring(0, maxLength) + '...' : text
}

function getGradeClass(grade: string | undefined): string {
  if (!grade) return ''
  if (grade.includes('高端')) return 'high'
  if (grade.includes('中端')) return 'mid'
  if (grade.includes('入门')) return 'low'
  return ''
}

// Lifecycle
onMounted(() => {
  loadDevices()
  loadFilterOptions()
})
</script>

<style scoped>
.it-infrastructure-library {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  gap: 0;
}

/* 表格区域 - 可滚动 */
.table-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
  min-height: 0;
}

/* 筛选搜索栏 */
.filter-search-bar {
  padding: 1.25rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
  background: rgba(15, 23, 42, 0.6);
}

.filter-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  align-items: end;
}

.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.filter-item label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.filter-item select,
.filter-item input {
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(51, 65, 85, 0.7);
  background: #0f172a;
  color: #94a3b8;
  font-size: 0.75rem;
}

.filter-item select:focus,
.filter-item input:focus {
  outline: none;
  border-color: #007AFF;
  color: #f1f5f9;
}

.filter-search {
  grid-column: span 2;
  min-width: 240px;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

.search-input-wrapper .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  font-size: 1rem;
  color: #64748b;
  pointer-events: none;
}

.search-input-wrapper input {
  width: 100%;
  padding-left: 2.5rem;
}

.filter-actions {
  display: flex;
  gap: 0.5rem;
  align-self: end;
}

.filter-btn,
.refresh-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(51, 65, 85, 0.7);
  background: rgba(15, 23, 42, 0.8);
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.filter-btn:hover {
  border-color: #007AFF;
  color: #007AFF;
  background: rgba(0, 122, 255, 0.1);
}

.refresh-btn:hover {
  border-color: #64748b;
  color: #94a3b8;
  background: rgba(30, 41, 59, 0.8);
}

.filter-btn .material-symbols-outlined,
.refresh-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

/* 批量操作栏 */
.batch-actions-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  background: rgba(0, 122, 255, 0.15);
  border: 1px solid rgba(0, 122, 255, 0.3);
  border-radius: 0.5rem;
  margin: 0 1.25rem 1rem 1.25rem;
  animation: slideDown 0.2s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.batch-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.8125rem;
  color: #007AFF;
}

.batch-info .material-symbols-outlined {
  font-size: 1.125rem;
}

.batch-info strong {
  font-weight: 600;
}

.batch-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.batch-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid;
  transition: all 0.2s;
}

.batch-btn {
  background: rgba(15, 23, 42, 0.8);
  border-color: rgba(51, 65, 85, 0.7);
  color: #94a3b8;
}

.batch-btn:hover {
  background: rgba(30, 41, 59, 0.8);
  border-color: #64748b;
  color: #f1f5f9;
}

.batch-btn.primary {
  background: #007AFF;
  border-color: #007AFF;
  color: white;
}

.batch-btn.primary:hover {
  background: #1a85ff;
  border-color: #1a85ff;
}

.batch-btn.danger {
  background: transparent;
  border-color: rgba(239, 68, 68, 0.5);
  color: #ef4444;
}

.batch-btn.danger:hover {
  background: rgba(239, 68, 68, 0.1);
  border-color: #ef4444;
}

.batch-btn .material-symbols-outlined {
  font-size: 1rem;
}

/* 表格包装器 */
.table-wrapper {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
  min-height: 0;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  min-width: 1300px;
}

.rack-height {
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  color: #a78bfa;
  font-weight: 500;
  text-align: center;
}

.data-table thead {
  background: rgba(15, 23, 42, 0.8);
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table th {
  padding: 1.25rem 1.5rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
  border-bottom: 1px solid rgba(51, 65, 85, 0.8);
}

.data-table td {
  padding: 1rem 1.5rem;
  color: #cbd5e1;
  font-size: 0.8125rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
  vertical-align: middle;
  height: 3.5rem;
  line-height: 1.5rem;
}

.data-table td > * {
  line-height: normal;
  display: inline-block;
  vertical-align: middle;
}

.data-table tbody tr {
  transition: background-color 0.2s;
}

.data-table tbody tr:hover {
  background: rgba(0, 122, 255, 0.05);
}

.data-table .font-bold {
  font-weight: 600;
  color: #e2e8f0;
}

.data-table .model-number {
  color: #007AFF;
  font-weight: 500;
}

.scenario-badge {
  display: inline-block;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid rgba(59, 130, 246, 0.3);
  background: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  font-size: 0.625rem;
  font-weight: 600;
}

.remarks {
  max-width: 200px;
}

.remarks span {
  display: block;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  font-family: 'SF Mono', 'Roboto Mono', monospace;
  color: #00D1FF;
  font-weight: 600;
}

.grade-indicator {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.grade-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: #64748b;
}

.grade-dot.high {
  background: #fb923c;
  box-shadow: 0 0 8px rgba(251, 146, 60, 0.8);
}

.grade-dot.mid {
  background: #007AFF;
  box-shadow: 0 0 8px rgba(0, 122, 255, 0.8);
}

.grade-dot.low {
  background: #22c55e;
}

.actions-col {
  text-align: right;
}

/* 复选框列 */
.checkbox-col {
  width: 3rem;
  text-align: center;
  padding: 0 0.75rem !important;
}

.checkbox-col input[type="checkbox"] {
  width: 1rem;
  height: 1rem;
  cursor: pointer;
  accent-color: #007AFF;
}

.data-table tbody tr.selected {
  background: rgba(0, 122, 255, 0.1);
}

.data-table tbody tr.selected td {
  border-top: 1px solid rgba(0, 122, 255, 0.3);
  border-bottom: 1px solid rgba(0, 122, 255, 0.3);
}

.data-table tbody tr.selected td:first-child {
  border-left: 2px solid #007AFF;
}

.data-table tbody tr.selected td:last-child {
  border-right: 2px solid #007AFF;
}

.actions {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 0.5rem;
}

.action-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.action-btn.edit:hover {
  color: white;
  background: #007AFF;
  box-shadow: 0 0 15px -3px rgba(0, 122, 255, 0.5);
}

.action-btn.delete:hover {
  color: white;
  background: #ef4444;
  box-shadow: 0 0 15px rgba(239, 68, 68, 0.4);
}

.action-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

/* 空状态和加载状态 */
.empty-state, .loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state .material-symbols-outlined,
.loading-state .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem 1.5rem;
  border-top: 1px solid rgba(51, 65, 85, 0.8);
  background: rgba(2, 6, 23, 0.6);
  flex-shrink: 0;
}

.pagination-left {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.pagination-info {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
}

.page-size-selector select {
  padding: 0.25rem 0.5rem;
  border-radius: 0.375rem;
  border: 1px solid rgba(51, 65, 85, 0.7);
  background: #0f172a;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
}

.page-size-selector select:focus {
  outline: none;
  border-color: #007AFF;
}

.pagination-controls {
  display: flex;
  gap: 0.5rem;
}

.page-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(51, 65, 85, 0.8);
  background: transparent;
  color: #64748b;
  font-size: 0.75rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background: rgba(30, 41, 59, 0.8);
  border-color: #475569;
  color: #94a3b8;
}

.page-btn.active {
  background: #007AFF;
  border-color: #007AFF;
  color: white;
}

.page-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}

/* 对话框 */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background: #1e293b;
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 0.75rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow-y: auto;
}

.dialog-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1.25rem;
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.dialog-header h3 {
  font-size: 1.125rem;
  font-weight: 600;
  color: #f1f5f9;
  margin: 0;
}

.close-btn {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  border: none;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.close-btn:hover {
  background: rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.dialog-body {
  padding: 1.5rem;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.form-group.full-width {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.required {
  color: #ef4444;
}

.form-group input,
.form-group select,
.form-group textarea {
  padding: 0.625rem 0.875rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(51, 65, 85, 0.7);
  background: #0f172a;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #007AFF;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1.25rem;
  border-top: 1px solid rgba(51, 65, 85, 0.5);
}

.btn-primary, .btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: #007AFF;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #1a85ff;
}

.btn-primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-secondary {
  background: rgba(30, 41, 59, 0.4);
  border: 1px solid rgba(51, 65, 85, 0.5);
  color: #94a3b8;
}

.btn-secondary:hover {
  border-color: rgba(0, 122, 255, 0.5);
  color: white;
  background: rgba(30, 41, 59, 0.6);
}

/* 批量编辑对话框特有样式 */
.batch-edit-dialog {
  max-width: 500px;
}

.batch-edit-fields {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.batch-preview {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(0, 122, 255, 0.1);
  border: 1px solid rgba(0, 122, 255, 0.3);
  border-radius: 0.5rem;
}

.preview-text {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0 0 0.375rem 0;
}

.preview-text strong {
  color: #007AFF;
}

.preview-value {
  font-size: 0.875rem;
  color: #f1f5f9;
  margin: 0;
  font-weight: 600;
}

/* 滚动条 */
.table-wrapper::-webkit-scrollbar,
.dialog::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

.table-wrapper::-webkit-scrollbar-track,
.dialog::-webkit-scrollbar-track {
  background: transparent;
}

.table-wrapper::-webkit-scrollbar-thumb,
.dialog::-webkit-scrollbar-thumb {
  background: #334155;
  border-radius: 10px;
}

.table-wrapper::-webkit-scrollbar-thumb:hover,
.dialog::-webkit-scrollbar-thumb:hover {
  background: #475569;
}
</style>
