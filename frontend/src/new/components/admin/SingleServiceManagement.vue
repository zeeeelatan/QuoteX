<template>
  <div class="single-service-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="openDialog()">
          <span class="material-symbols-outlined">add</span>
          新增单次服务
        </button>
        <button class="btn-success" @click="downloadTemplateDialog = true">
          <span class="material-symbols-outlined">download</span>
          下载模板
        </button>
        <button class="btn-warning" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入
        </button>
        <button class="btn-danger" @click="clearServices">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空
        </button>
        <input
          ref="importInput"
          type="file"
          accept=".xlsx,.xls,.csv"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
      <div class="toolbar-right">
        <div class="filter-group">
          <select v-model="filterBusinessType" class="filter-select" @change="loadData">
            <option value="">所有业务类型</option>
            <option v-for="type in businessTypes" :key="type" :value="type">{{ type }}</option>
          </select>
          <select v-model="filterServiceName" class="filter-select" @change="loadData">
            <option value="">所有服务名称</option>
            <option v-for="name in serviceNames" :key="name" :value="name">{{ name }}</option>
          </select>
        </div>
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input
            type="text"
            v-model="searchQuery"
            placeholder="搜索业务类型/服务名称..."
            @input="handleSearch"
          />
        </div>
      </div>
    </div>

    <div class="table-wrapper">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>业务类型</th>
              <th>服务名称</th>
              <th>服务细项</th>
              <th>设备类型</th>
              <th>设备级别</th>
              <th>工程师</th>
              <th>单位</th>
              <th class="text-right">标准报价</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in paginatedData" :key="item.id" class="table-row">
              <td><span class="business-type-badge">{{ item.business_type }}</span></td>
              <td>{{ item.service_name }}</td>
              <td class="service-detail">{{ item.service_detail }}</td>
              <td>{{ item.device_type }}</td>
              <td><span class="level-badge" :class="getLevelClass(item.device_level)">{{ item.device_level }}</span></td>
              <td><span class="engineer-badge" :class="getEngineerClass(item.engineer_capability)">{{ item.engineer_capability }}</span></td>
              <td>{{ item.unit }}</td>
              <td class="text-right">
                <span class="price">¥ {{ formatPrice(item.standard_quote) }}</span>
              </td>
              <td class="text-center">
                <button class="action-btn" @click="editItem(item)" title="编辑">
                  <span class="material-symbols-outlined">edit</span>
                </button>
                <button class="action-btn delete-btn" @click="confirmDelete(item)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
            <tr v-if="paginatedData.length === 0">
              <td colspan="9" class="no-data">暂无数据</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Frozen Bottom Bar with Pagination -->
      <div class="bottom-bar">
        <div class="bottom-bar-left">
          <div class="pagination-info">
            显示第 <span>{{ (currentPage - 1) * pageSize + 1 }}</span> 到
            <span>{{ Math.min(currentPage * pageSize, filteredData.length) }}</span> 条，
            共 <span>{{ filteredData.length }}</span> 条数据
          </div>
        </div>
        <div class="bottom-bar-center">
          <div class="page-size-selector">
            <span class="page-size-label">每页显示</span>
            <select v-model="pageSize" @change="handlePageSizeChange" class="page-size-select">
              <option :value="10">10</option>
              <option :value="15">15</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
            </select>
            <span class="page-size-label">条</span>
          </div>
        </div>
        <div class="bottom-bar-right">
          <div class="pagination-buttons">
            <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
              <span class="material-symbols-outlined">chevron_left</span>
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              class="page-btn"
              :class="{ active: page === currentPage }"
              @click="currentPage = page"
            >
              {{ page }}
            </button>
            <button class="page-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showDialog" class="dialog-overlay" @click.self="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ dialogTitle }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-row">
            <div class="form-group">
              <label>业务类型</label>
              <input v-model="formData.business_type" placeholder="例如: TAAS" />
            </div>
            <div class="form-group">
              <label>服务名称</label>
              <input v-model="formData.service_name" placeholder="例如: 操作实施服务" />
            </div>
          </div>
          <div class="form-group">
            <label>服务细项</label>
            <input v-model="formData.service_detail" placeholder="例如: 设备硬件安装上架/下架/加电/下电" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>设备类型</label>
              <input v-model="formData.device_type" placeholder="例如: 网络/安全" />
            </div>
            <div class="form-group">
              <label>设备/服务级别</label>
              <input v-model="formData.device_level" placeholder="例如: 低端" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>工程师能力标签</label>
              <select v-model="formData.engineer_capability" class="form-select">
                <option value="L1">L1</option>
                <option value="L2">L2</option>
                <option value="L3">L3</option>
                <option value="L4">L4</option>
                <option value="L5">L5</option>
              </select>
            </div>
            <div class="form-group">
              <label>单位</label>
              <select v-model="formData.unit" class="form-select">
                <option value="台">台</option>
                <option value="次">次</option>
                <option value="套">套</option>
                <option value="柜">柜</option>
                <option value="块">块</option>
              </select>
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>数量</label>
              <input v-model.number="formData.quantity" type="number" step="0.1" />
            </div>
            <div class="form-group">
              <label>上门费用</label>
              <input v-model.number="formData.on_site_fee" type="number" step="0.01" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>基准工时数</label>
              <input v-model.number="formData.base_hours" type="number" step="0.1" />
            </div>
            <div class="form-group">
              <label>基准工时费</label>
              <input v-model.number="formData.base_hourly_rate" type="number" step="0.01" />
            </div>
          </div>
          <div class="form-group">
            <label>标准报价</label>
            <input v-model.number="formData.standard_quote" type="number" step="0.01" />
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>紧急响应系数</label>
              <input v-model.number="formData.emergency_response" type="number" step="0.1" />
            </div>
            <div class="form-group">
              <label>特殊时间段系数</label>
              <input v-model.number="formData.special_time_period" type="number" step="0.1" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>一线城市系数</label>
              <input v-model.number="formData.tier1_city" type="number" step="0.1" />
            </div>
            <div class="form-group">
              <label>其他城市系数</label>
              <input v-model.number="formData.other_city" type="number" step="0.1" />
            </div>
          </div>
          <div class="form-group">
            <label>批量需求系数</label>
            <input v-model.number="formData.batch_demand" type="number" step="0.1" />
          </div>
          <div class="form-group">
            <label>备注</label>
            <textarea v-model="formData.remarks" class="form-textarea" rows="2"></textarea>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveItem">保存</button>
        </div>
      </div>
    </div>

    <!-- Delete Confirmation Dialog -->
    <div v-if="showDeleteDialog" class="dialog-overlay" @click.self="showDeleteDialog = false">
      <div class="dialog dialog-small" @click.stop>
        <div class="dialog-header">
          <h3>确认删除</h3>
          <button class="close-btn" @click="showDeleteDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <p>确定要删除该服务项吗？此操作不可撤销。</p>
          <p v-if="itemToDelete" class="delete-item-info">
            {{ itemToDelete.service_name }} - {{ itemToDelete.service_detail }}
          </p>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showDeleteDialog = false">取消</button>
          <button class="btn-danger" @click="deleteItem">确认删除</button>
        </div>
      </div>
    </div>

    <!-- Download Template Dialog -->
    <div v-if="downloadTemplateDialog" class="dialog-overlay" @click="downloadTemplateDialog = false">
      <div class="dialog dialog-sm" @click.stop>
        <div class="dialog-header">
          <h3>下载导入模板</h3>
          <button class="close-btn" @click="downloadTemplateDialog = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="template-options">
            <button class="template-btn" @click="downloadTemplate('xlsx')">
              <span class="material-symbols-outlined">description</span>
              下载 xlsx
            </button>
            <button class="template-btn" @click="downloadTemplate('xls')">
              <span class="material-symbols-outlined">description</span>
              下载 xls
            </button>
            <button class="template-btn" @click="downloadTemplate('csv')">
              <span class="material-symbols-outlined">description</span>
              下载 csv
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// Data
const dataList = ref<any[]>([])
const businessTypes = ref<string[]>([])
const serviceNames = ref<string[]>([])
const searchQuery = ref('')
const filterBusinessType = ref('')
const filterServiceName = ref('')

// Pagination
const currentPage = ref(1)
const pageSize = ref(15)

// Dialog
const showDialog = ref(false)
const showDeleteDialog = ref(false)
const downloadTemplateDialog = ref(false)
const editingId = ref<number | null>(null)
const itemToDelete = ref<any>(null)

const formData = ref({
  business_type: 'TAAS',
  service_name: '',
  service_detail: '',
  device_type: '',
  device_level: '',
  engineer_capability: 'L2',
  quantity: 1,
  on_site_fee: 0,
  base_hours: 1,
  base_hourly_rate: 0,
  unit: '台',
  standard_quote: 0,
  emergency_response: 0.3,
  special_time_period: 0.5,
  tier1_city: 0,
  other_city: 0.25,
  batch_demand: 0.3,
  remarks: ''
})

// Computed
const dialogTitle = computed(() => editingId.value ? '编辑单次服务' : '新增单次服务')

const filteredData = computed(() => {
  let data = [...dataList.value]

  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    data = data.filter(item =>
      item.business_type?.toLowerCase().includes(query) ||
      item.service_name?.toLowerCase().includes(query) ||
      item.service_detail?.toLowerCase().includes(query) ||
      item.device_type?.toLowerCase().includes(query)
    )
  }

  return data
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const total = totalPages.value
  const current = currentPage.value

  if (total <= 7) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 4) {
      for (let i = 1; i <= 5; i++) pages.push(i)
      pages.push(total)
    } else if (current >= total - 3) {
      pages.push(1)
      for (let i = total - 4; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push(total)
    }
  }

  return pages
})

// Watch
watch(pageSize, () => {
  currentPage.value = 1
})

// Methods
async function loadData() {
  try {
    const params: any = {}
    if (filterBusinessType.value) params.business_type = filterBusinessType.value
    if (filterServiceName.value) params.service_name = filterServiceName.value

    const response = await axios.get(`${API_URL}/single-service/`, { params })
    dataList.value = response.data || []

    // Load types
    const typesResponse = await axios.get(`${API_URL}/single-service/business-types/list`)
    businessTypes.value = typesResponse.data.business_types || []

    const namesResponse = await axios.get(`${API_URL}/single-service/service-names/list`)
    serviceNames.value = namesResponse.data.service_names || []
  } catch (error: any) {
    console.error('[SingleServiceManagement] Failed to load data:', error)
  }
}

function handleSearch() {
  currentPage.value = 1
}

function handlePageSizeChange() {
  currentPage.value = 1
}

function formatPrice(price: number): string {
  return price.toLocaleString('zh-CN', { minimumFractionDigits: 0, maximumFractionDigits: 2 })
}

function getLevelClass(level: string): string {
  if (!level) return ''
  const l = level.toLowerCase()
  if (l.includes('低')) return 'level-low'
  if (l.includes('中')) return 'level-mid'
  if (l.includes('高')) return 'level-high'
  return ''
}

function getEngineerClass(engineer: string): string {
  if (!engineer) return 'eng-l2'
  const e = engineer.toLowerCase()
  if (e.includes('l1')) return 'eng-l1'
  if (e.includes('l2')) return 'eng-l2'
  if (e.includes('l3')) return 'eng-l3'
  if (e.includes('l4')) return 'eng-l4'
  if (e.includes('l5')) return 'eng-l5'
  return 'eng-l2'
}

function openDialog(item?: any) {
  if (item) {
    editingId.value = item.id
    formData.value = {
      business_type: item.business_type || '',
      service_name: item.service_name || '',
      service_detail: item.service_detail || '',
      device_type: item.device_type || '',
      device_level: item.device_level || '',
      engineer_capability: item.engineer_capability || 'L2',
      quantity: item.quantity || 1,
      on_site_fee: item.on_site_fee || 0,
      base_hours: item.base_hours || 1,
      base_hourly_rate: item.base_hourly_rate || 0,
      unit: item.unit || '台',
      standard_quote: item.standard_quote || 0,
      emergency_response: item.emergency_response || 0.3,
      special_time_period: item.special_time_period || 0.5,
      tier1_city: item.tier1_city || 0,
      other_city: item.other_city || 0.25,
      batch_demand: item.batch_demand || 0.3,
      remarks: item.remarks || ''
    }
  } else {
    editingId.value = null
    formData.value = {
      business_type: 'TAAS',
      service_name: '',
      service_detail: '',
      device_type: '',
      device_level: '',
      engineer_capability: 'L2',
      quantity: 1,
      on_site_fee: 0,
      base_hours: 1,
      base_hourly_rate: 0,
      unit: '台',
      standard_quote: 0,
      emergency_response: 0.3,
      special_time_period: 0.5,
      tier1_city: 0,
      other_city: 0.25,
      batch_demand: 0.3,
      remarks: ''
    }
  }
  showDialog.value = true
}

function closeDialog() {
  showDialog.value = false
}

async function saveItem() {
  try {
    const data = { ...formData.value }

    if (editingId.value) {
      await axios.put(`${API_URL}/single-service/${editingId.value}`, data)
    } else {
      await axios.post(`${API_URL}/single-service/`, data)
    }

    await loadData()
    closeDialog()
  } catch (error: any) {
    console.error('[SingleServiceManagement] Failed to save:', error)
    const errorMessage = error.response?.data?.detail || error.message || '保存失败，请重试'
    alert(errorMessage)
  }
}

function confirmDelete(item: any) {
  itemToDelete.value = item
  showDeleteDialog.value = true
}

async function deleteItem() {
  if (!itemToDelete.value) return

  try {
    await axios.delete(`${API_URL}/single-service/${itemToDelete.value.id}`)
    await loadData()
    showDeleteDialog.value = false
    itemToDelete.value = null
  } catch (error: any) {
    console.error('[SingleServiceManagement] Failed to delete:', error)
    const errorMessage = error.response?.data?.detail || error.message || '删除失败，请重试'
    alert(errorMessage)
  }
}

async function clearServices() {
  if (!confirm('确定要清空所有服务数据吗？此操作不可撤销！')) return

  try {
    await axios.delete(`${API_URL}/single-service/clear`)
    await loadData()
  } catch (error: any) {
    console.error('[SingleServiceManagement] Failed to clear:', error)
    alert(error.response?.data?.detail || '清空失败，请重试')
  }
}

function downloadTemplate(type: string) {
  const headers = [
    '业务类型', '服务名称', '服务细项', '设备类型（硬件/软件）',
    '设备/服务级别', '工程师能力标签', '数量', '上门费用',
    '基准工时数', '基准工时费', '单位', '标准报价',
    '紧急响应', '特殊时间段（夜晚及节假日）',
    '一线/新一线/省会城市', '其他城市', '备注', '适用城市',
    '批量需求 (每增加一次)'
  ]
  const sampleData = [{
    '业务类型': 'TAAS',
    '服务名称': '操作实施服务',
    '服务细项': '设备硬件安装上架/下架/加电/下电',
    '设备类型（硬件/软件）': '机房机柜内设备',
    '设备/服务级别': '1U-2U',
    '工程师能力标签': 'L1',
    '数量': 1,
    '上门费用': 150,
    '基准工时数': 1,
    '基准工时费': 30,
    '单位': '台',
    '标准报价': 180,
    '紧急响应': 0.3,
    '特殊时间段（夜晚及节假日）': 0.5,
    '一线/新一线/省会城市': 0,
    '其他城市': 0.25,
    '备注': '转包',
    '适用城市': '',
    '批量需求 (每增加一次)': 0.3
  }]

  if (type === 'csv') {
    const rows = [headers.join(',')]
    sampleData.forEach(row => {
      rows.push(headers.map(h => row[h as keyof typeof row] || '').join(','))
    })
    const csvContent = rows.join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '单次服务数据管理模板.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    const XLSX = (window as any).XLSX
    const ws = XLSX.utils.json_to_sheet(sampleData, { header: headers })
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '模板')
    const ext = type === 'xls' ? 'xls' : 'xlsx'
    XLSX.writeFile(wb, `单次服务数据管理模板.${ext}`)
  }
  downloadTemplateDialog.value = false
}

function triggerImport() {
  const input = document.createElement('input')
  input.type = 'file'
  input.accept = '.xlsx,.xls,.csv'
  input.onchange = async (e: Event) => {
    const target = e.target as HTMLInputElement
    const file = target.files?.[0]
    if (!file) return

    try {
      const XLSX = (window as any).XLSX
      const arrayBuffer = await file.arrayBuffer()
      const wb = XLSX.read(arrayBuffer, { type: 'array' })
      const ws = wb.Sheets[wb.SheetNames[0]]
      const jsonData = XLSX.utils.sheet_to_json(ws)

      const data = jsonData.map((row: any, idx: number) => ({
        business_type: row['业务类型'] || '',
        service_name: row['服务名称'] || '',
        service_detail: row['服务细项'] || '',
        device_type: row['*设备类型（硬件/软件）'] || row['设备类型（硬件/软件）'] || '',
        device_level: row['*设备/服务级别'] || row['设备/服务级别'] || '',
        engineer_capability: row['工程师能力标签'] || '',
        quantity: row['数量'] || 1,
        on_site_fee: row['上门费用'] || 0,
        base_hours: row['*基准工时数'] || 0,
        base_hourly_rate: row['*基准工时费'] || 0,
        unit: row['*单位'] || '台',
        standard_quote: row['标准报价'] || 0,
        emergency_response: row['紧急响应'] || 0,
        special_time_period: row['特殊时间段（夜晚及节假日）'] || 0,
        tier1_city: row['一线/新一线/省会城市'] || 0,
        other_city: row['其他城市'] || 0,
        remarks: row['备注'] || '',
        applicable_cities: row['适用城市'] || '',
        batch_demand: row['批量需求 (每增加一次)'] || 0
      }))

      const response = await axios.post(`${API_URL}/single-service/import-batch`, { data })
      alert(response.data?.message || '导入成功')
      await loadData()
    } catch (err: any) {
      console.error('Import failed:', err)
      alert('导入失败: ' + (err.message || '未知错误'))
    }

    target.value = ''
  }
  input.click()
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.single-service-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

/* Toolbar */
.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  gap: 0.5rem;
}

.filter-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  min-width: 8rem;
  cursor: pointer;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
}

.search-box .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #64748b;
  font-size: 1.25rem;
}

.search-box input {
  padding-left: 2.5rem;
  width: 16rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
  border-radius: 0.375rem;
  font-size: 0.875rem;
}

.search-box input:focus {
  outline: none;
  border-color: #135bec;
}

/* Buttons */
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
  font-weight:  500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.btn-primary {
  background-color: #135bec;
  color: white;
}
.btn-primary:hover { background-color: #0d4ed3; }

.btn-success {
  background-color: #10b981;
}
.btn-success:hover { background-color: #059669; }

.btn-warning {
  background-color: #f59e0b;
}
.btn-warning:hover { background-color: #d97706; }

.btn-danger {
  background-color: #ef4444;
}
.btn-danger:hover { background-color: #dc2626; }

.btn-secondary {
  background-color: #334155;
  color: #e2e8f0;
}
.btn-secondary:hover { background-color: #475569; }

/* Table Wrapper */
.table-wrapper {
  flex: 1;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.table-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
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
  z-index: 5;
}

.data-table td {
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #1e293b;
  font-size: 0.875rem;
}

.data-table tbody tr:hover {
  background-color: #334155;
}

.data-table tr.table-row:hover {
  background-color: rgba(30, 41, 59, 0.8);
}

.data-table th.text-right,
.data-table td.text-right {
  text-align: right;
}

.data-table th.text-center,
.data-table td.text-center {
  text-align: center;
}

.no-data {
  text-align: center;
  color: # #64748b;
  padding: 3rem !important;
}

/* Badges */
.business-type-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
  border: 1px solid rgba(19, 91, 236, 0.2);
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
}

.level-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.level-badge.level-low {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.level-badge.level-mid {
  background-color: rgba(59, 130, 246, 0.1);
  color: #3b82f6;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.level-badge.level-high {
  background-color: rgba(249, 115, 22, 0.1);
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.2);
}

.engineer-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 0.25rem;
  font-size: 0.7rem;
  font-weight: 600;
}

.engine-badge.eng-l1 {
  background-color: #22c55e;
  color: white;
}

.engine-badge.eng-l2 {
  background-color: #3b82f6;
  color: white;
}

.engine-badge.eng-l3 {
  background-color: #f59e0b;
  color: white;
}

.engine-badge.eng-l4 {
  background-color: #f97316;
  color: white;
}

.engine-badge.eng-l5 {
  background-color: #ef4444;
  color: white;
}

.service-detail {
  max-width: 15rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.price {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  color: #f1f5f9;
}

/* Action Buttons */
.action-btn {
  padding: 0.375rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

.action-btn.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

/* Frozen Bottom Bar */
.bottom-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #0f172a;
  border-top: 1px solid #334155;
  flex-shrink: 0;
  position: sticky;
  bottom: 0;
  z-index: 10;
}

.bottom-bar-left {
  flex: 1;
}

.bottom-bar-center {
  flex: 0 0 auto;
}

.bottom-bar-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.pagination-info {
  font-size: 0.75rem;
  color: #94a3b8;
}

.pagination-info span {
  color: #f1f5f9;
  font-weight: 600;
}

.page-size-selector {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-label {
  font-size: 0.75rem;
  color: #64748b;
}

.page-size-select {
  background-color: #0f172a;
  border: 1px solid #334155;
  color: #cbd5e1;
  padding: 0.375rem 0.5rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  cursor: pointer;
  width: 3.5rem;
}

.pagination-buttons {
  display: flex;
  gap: 0.25rem;
}

.page-btn {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  background-color: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #f1f5f9;
}

.page-btn.active {
  background-color: #135bec;
  border-color: #135bec;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Dialog */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.dialog {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  width: 90%;
  max-width: 600px;
  max-height: 90vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.dialog-small {
  max-width: 400px;
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
  overflow-y: auto;
  max-height: 60vh;
}

.dialog-body p {
  color: #cbd5e1;
  margin: 0 0 1rem 0;
}

.delete-item-info {
  padding: 0.75rem;
  background-color: #334155;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  color: #f1f5f9;
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.form-group {
  margin-bottom: 1rem;
}

.form-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 500;
  color: #94a3b8;
  margin-bottom: 0.375rem;
}

.form-group input,
.form-group select,
.form-group textarea {
  width: 100%;
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f1f5f9;
  font-size: 0.875rem;
}

.form-group input:focus,
.form-group select:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #135bec;
}

.form-textarea {
  resize: vertical;
  min-height: 2rem;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}

/* Template options */
.template-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.template-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.template-btn:hover {
  background-color: #334155;
  border-color: #135bec;
}

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-size: 1.125rem;
}
</style>
