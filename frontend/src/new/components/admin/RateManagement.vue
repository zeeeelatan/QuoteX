<template>
  <div class="rate-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="showAddDialog = true">
          <span class="material-symbols-outlined">add</span>
          添加费率
        </button>
        <button class="btn-secondary" @click="exportData">
          <span class="material-symbols-outlined">download</span>
          导出
        </button>
        <button class="btn-secondary" @click="$refs.fileInput?.click()">
          <span class="material-symbols-outlined">upload</span>
          导入
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleImport"
        />
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input type="text" v-model="searchQuery" placeholder="搜索费率..." />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>一级分类</th>
            <th>二级分类</th>
            <th>三级分类</th>
            <th>费率</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="rate in filteredRates" :key="rate.id">
            <td>{{ rate.primary_category || '-' }}</td>
            <td>{{ rate.secondary_category || '-' }}</td>
            <td>{{ rate.tertiary_category || '-' }}</td>
            <td>{{ (rate.rate * 100).toFixed(2) }}%</td>
            <td class="actions">
              <button class="action-btn edit" @click="editRate(rate)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteRate(rate.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredRates.length === 0" class="empty-state">
        <span class="material-symbols-outlined">inbox</span>
        <p>暂无数据</p>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showAddDialog || editingRate" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingRate ? '编辑费率' : '添加费率' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>一级分类</label>
            <input v-model="formData.primary_category" placeholder="例如: 服务器" />
          </div>
          <div class="form-group">
            <label>二级分类</label>
            <input v-model="formData.secondary_category" placeholder="例如: 机架式服务器" />
          </div>
          <div class="form-group">
            <label>三级分类</label>
            <input v-model="formData.tertiary_category" placeholder="例如: 通用型" />
          </div>
          <div class="form-group">
            <label>费率 (%)</label>
            <input v-model.number="formData.rate_value" type="number" step="0.01" placeholder="例如: 8" />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveRate">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const emit = defineEmits(['api-call'])

// State
const rates = ref<any[]>([])
const searchQuery = ref('')
const showAddDialog = ref(false)
const editingRate = ref<any>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const formData = ref({
  primary_category: '',
  secondary_category: '',
  tertiary_category: '',
  rate_value: 0
})

// Computed
const filteredRates = computed(() => {
  if (!searchQuery.value) return rates.value
  const query = searchQuery.value.toLowerCase()
  return rates.value.filter(rate =>
    (rate.primary_category || '').toLowerCase().includes(query) ||
    (rate.secondary_category || '').toLowerCase().includes(query) ||
    (rate.tertiary_category || '').toLowerCase().includes(query)
  )
})

// Load rates
async function loadRates() {
  try {
    const response = await axios.get(`${API_URL}/maintenance_rates/`)
    rates.value = response.data || []
  } catch (error) {
    console.error('Failed to load rates:', error)
  }
}

// Edit rate
function editRate(rate: any) {
  editingRate.value = rate
  formData.value = {
    primary_category: rate.primary_category || '',
    secondary_category: rate.secondary_category || '',
    tertiary_category: rate.tertiary_category || '',
    rate_value: (rate.rate || 0) * 100
  }
}

// Delete rate
async function deleteRate(id: number) {
  if (!confirm('确定要删除这条费率吗？')) return
  try {
    await axios.delete(`${API_URL}/maintenance_rates/${id}`)
    rates.value = rates.value.filter(r => r.id !== id)
  } catch (error) {
    console.error('Failed to delete rate:', error)
  }
}

// Save rate
async function saveRate() {
  const data = {
    primary_category: formData.value.primary_category || null,
    secondary_category: formData.value.secondary_category || null,
    tertiary_category: formData.value.tertiary_category || null,
    rate: formData.value.rate_value / 100
  }

  try {
    if (editingRate.value) {
      await axios.put(`${API_URL}/maintenance_rates/${editingRate.value.id}`, data)
      const index = rates.value.findIndex(r => r.id === editingRate.value.id)
      if (index !== -1) {
        rates.value[index] = { ...editingRate.value, ...data }
      }
    } else {
      const response = await axios.post(`${API_URL}/maintenance_rates/`, data)
      rates.value.push(response.data)
    }
    closeDialog()
  } catch (error) {
    console.error('Failed to save rate:', error)
  }
}

// Close dialog
function closeDialog() {
  showAddDialog.value = false
  editingRate.value = null
  formData.value = {
    primary_category: '',
    secondary_category: '',
    tertiary_category: '',
    rate_value: 0
  }
}

// Export data
function exportData() {
  const exportData = rates.value.map(rate => ({
    '一级分类': rate.primary_category || '',
    '二级分类': rate.secondary_category || '',
    '三级分类': rate.tertiary_category || '',
    '费率': ((rate.rate || 0) * 100).toFixed(2) + '%'
  }))
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '维保费率')
  XLSX.writeFile(wb, '维保费率.xlsx')
}

// Import data
async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      const sheet = workbook.Sheets[workbook.SheetNames[0]]
      const jsonData = XLSX.utils.sheet_to_json(sheet)

      for (const row of jsonData) {
        const rate = parseFloat(row['费率']?.replace('%', '')) / 100
        await axios.post(`${API_URL}/maintenance_rates/`, {
          primary_category: row['一级分类'] || null,
          secondary_category: row['二级分类'] || null,
          tertiary_category: row['三级分类'] || null,
          rate: isNaN(rate) ? 0.02 : rate
        })
      }

      await loadRates()
      target.value = ''
    } catch (error) {
      console.error('Import failed:', error)
    }
  }
  reader.readAsArrayBuffer(file)
}

onMounted(() => {
  loadRates()
})
</script>

<style scoped>
.rate-management {
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
  gap: 1rem;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-primary,
.btn-secondary {
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
}

.btn-primary {
  background-color: #135bec;
  color: white;
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

.search-box {
  display: flex;
  align-items: center;
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
}

.search-box .material-symbols-outlined {
  font-size: 1.125rem;
  color: #64748b;
  margin-right: 0.5rem;
}

.search-box input {
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-size: 0.875rem;
  width: 200px;
}

.search-box input:focus {
  outline: none;
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
  border-radius: 0.5rem;
  width: 90%;
  max-width: 500px;
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

.form-group input {
  padding: 0.625rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.875rem;
}

.form-group input:focus {
  outline: none;
  border-color: #135bec;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
}
</style>
