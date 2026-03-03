<template>
  <div class="dispatch-service-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-warning" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入Excel
        </button>
        <button class="btn-danger" @click="clearDispatchServices">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空
        </button>
        <input
          ref="importInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>单位工时</th>
            <th>服务时间窗口</th>
            <th>现场响应时效</th>
            <th>一级城市</th>
            <th>二级城市</th>
            <th>三级城市</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in pagedGroupedList" :key="item.key">
            <td>{{ item.unit_hours }}</td>
            <td>{{ item.time_window }}</td>
            <td>{{ item.response_time }}</td>
            <td class="price-cell">{{ item.price_tier1 || '-' }}</td>
            <td class="price-cell">{{ item.price_tier2 || '-' }}</td>
            <td class="price-cell">{{ item.price_tier3 || '-' }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="pagedGroupedList.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination-container">
      <div class="pagination-info">
        共 {{ groupedDataList.length }} 条
      </div>
      <div class="pagination-controls">
        <button class="pagination-btn" :disabled="currentPage === 1" @click="currentPage--">
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <span class="pagination-current">{{ currentPage }}</span>
        <button class="pagination-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
        <select v-model="pageSize" class="page-size-select">
          <option :value="10">10条/页</option>
          <option :value="12">12条/页</option>
          <option :value="15">15条/页</option>
          <option :value="20">20条/页</option>
        </select>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
const dispatchServiceList = ref<any[]>([])
const importInput = ref<HTMLInputElement | null>(null)

const currentPage = ref(1)
const pageSize = ref(12)

// Computed - 将长格式数据转换为宽格式（与Excel一致）
const groupedDataList = computed(() => {
  // 按单位工时、服务时间窗口、响应时效分组
  const grouped: Record<string, any> = {}

  dispatchServiceList.value.forEach(item => {
    const key = `${item.unit_hours}|${item.time_window}|${item.response_time}`

    if (!grouped[key]) {
      grouped[key] = {
        key,
        unit_hours: item.unit_hours,
        time_window: item.time_window,
        response_time: item.response_time,
        price_tier1: null,
        price_tier2: null,
        price_tier3: null
      }
    }

    // 根据城市等级设置价格
    if (item.city_tier === '一级城市') {
      grouped[key].price_tier1 = Number(item.price)
    } else if (item.city_tier === '二级城市') {
      grouped[key].price_tier2 = Number(item.price)
    } else if (item.city_tier === '三级城市') {
      grouped[key].price_tier3 = Number(item.price)
    }
  })

  // 转为数组并按特定顺序排序
  const orderMap: Record<string, number> = {
    '2小时|5*8|8小时': 1,
    '2小时|5*12|8小时': 2,
    '2小时|7*8|8小时': 3,
    '2小时|7*12|8小时': 4,
    '2小时|5*8|4小时': 5,
    '2小时|5*12|4小时': 6,
    '2小时|7*8|4小时': 7,
    '2小时|7*12|4小时': 8,
    '8小时|5*8|8小时': 9,
    '4小时|5*8|8小时': 10,
  }

  return Object.values(grouped).sort((a, b) => {
    const orderA = orderMap[a.key] || 999
    const orderB = orderMap[b.key] || 999
    return orderA - orderB
  })
})

const totalPages = computed(() => Math.ceil(groupedDataList.value.length / pageSize.value))

const pagedGroupedList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return groupedDataList.value.slice(start, start + pageSize.value)
})

// Watch page size changes
watch(pageSize, () => {
  currentPage.value = 1
})

// Fetch dispatch services
async function fetchDispatchServices() {
  try {
    const response = await axios.get(`${API_URL}/dispatch-service/`)
    dispatchServiceList.value = response.data || []
  } catch (error) {
    console.error('Failed to load dispatch services:', error)
  }
}

// Trigger import
function triggerImport() {
  importInput.value?.click()
}

// Handle import file
async function handleImportFile(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    // Read Excel file
    const arrayBuffer = await file.arrayBuffer()
    const XLSX = await import('xlsx')
    const wb = XLSX.read(arrayBuffer, { type: 'array' })
    const ws = wb.Sheets[wb.SheetNames[0]]
    const data: any[] = XLSX.utils.sheet_to_json(ws)

    // Transform data: convert wide format to long format
    const records: any[] = []

    data.forEach((row: any) => {
      const timeWindow = row['服务时间窗口']
      const responseTime = row['现场响应时效']
      const unitHoursRaw = row['单位工时']

      // Determine service type based on unit hours and response time
      let serviceType = ''
      let unitHours = ''
      if (unitHoursRaw === '2小时') {
        serviceType = responseTime === '8小时' ? '标准报价' : '加急报价'
        unitHours = '2小时'
      } else if (unitHoursRaw === '1人天') {
        serviceType = '人天报价'
        unitHours = '8小时'
      } else if (unitHoursRaw === '半人天') {
        serviceType = '半天报价'
        unitHours = '4小时'
      } else {
        unitHours = unitHoursRaw
      }

      // Create records for each city tier
      const cityTiers = [
        { name: '一级城市', price: row['一级城市'] },
        { name: '二级城市', price: row['二级城市'] },
        { name: '三级城市', price: row['三级城市'] }
      ]

      cityTiers.forEach(tier => {
        if (tier.price !== undefined && tier.price !== null) {
          records.push({
            service_type: serviceType,
            unit_hours: unitHours,
            time_window: timeWindow,
            response_time: responseTime,
            city_tier: tier.name,
            price: Number(tier.price),
            description: `派单服务 - ${serviceType}`
          })
        }
      })
    })

    // Clear existing data and import new data
    await axios.delete(`${API_URL}/dispatch-service/`)
    await axios.post(`${API_URL}/dispatch-service/batch-create`, { records })

    showToast(`导入成功，共 ${records.length} 条数据`)
    fetchDispatchServices()
  } catch (err: any) {
    console.error('Import failed:', err)
    showToast('导入失败: ' + (err.message || err.response?.data?.detail || '未知错误'), 'error')
  }

  target.value = ''
}

// Clear all dispatch services
async function clearDispatchServices() {
  if (!confirm('确定要清空所有派单服务数据吗？此操作不可撤销！')) return

  try {
    // 批量删除所有记录
    const response = await axios.get(`${API_URL}/dispatch-service/`)
    const ids = response.data.map((item: any) => item.id)

    await Promise.all(ids.map((id: number) => axios.delete(`${API_URL}/dispatch-service/${id}`)))

    showToast('所有派单服务数据已清空')
    fetchDispatchServices()
  } catch (error: any) {
    console.error('Failed to clear dispatch services:', error)
    showToast('清空失败', 'error')
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
  fetchDispatchServices()
})
</script>

<style scoped>
.dispatch-service-management {
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

.btn-secondary {
  background-color: #334155;
}

.btn-secondary:hover {
  background-color: #475569;
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
}

.data-table tbody tr:hover {
  background-color: #334155;
}

.price-cell {
  font-weight: 600;
  color: #f1f5f9;
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

.material-symbols-outlined {
  font-family: 'Material Symbols Outlined';
  font-size: 1.25rem;
  vertical-align: middle;
}
</style>
