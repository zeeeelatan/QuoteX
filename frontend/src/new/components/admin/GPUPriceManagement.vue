<template>
  <div class="gpu-price-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-primary" @click="showAddDialog = true">
          <span class="material-symbols-outlined">add</span>
          添加 GPU 价格
        </button>
        <button class="btn-secondary" @click="exportData">
          <span class="material-symbols-outlined">download</span>
          导出
        </button>
      </div>
      <div class="toolbar-right">
        <div class="search-box">
          <span class="material-symbols-outlined">search</span>
          <input type="text" v-model="searchQuery" placeholder="搜索 GPU..." />
        </div>
      </div>
    </div>

    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>厂商</th>
            <th>系列</th>
            <th>型号</th>
            <th>显存</th>
            <th>GPU 价格</th>
            <th>维保费率</th>
            <th>备件维修费</th>
            <th>人工维修费</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="gpu in filteredGPUs" :key="gpu.id">
            <td>{{ gpu.manufacturer }}</td>
            <td>{{ gpu.series }}</td>
            <td>{{ gpu.model }}</td>
            <td>{{ gpu.gpu_memory }}GB</td>
            <td>¥{{ gpu.gpu_price?.toLocaleString() || '-' }}</td>
            <td>{{ (gpu.gpu_rate * 100).toFixed(2) }}%</td>
            <td>¥{{ gpu.spare_repair_cost?.toLocaleString() || '-' }}</td>
            <td>¥{{ gpu.labor_repair_cost?.toLocaleString() || '-' }}</td>
            <td class="actions">
              <button class="action-btn edit" @click="editGPU(gpu)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete" @click="deleteGPU(gpu.id)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>
      <div v-if="filteredGPUs.length === 0" class="empty-state">
        <span class="material-symbols-outlined">memory</span>
        <p>暂无 GPU 数据</p>
      </div>
    </div>

    <!-- Add/Edit Dialog -->
    <div v-if="showAddDialog || editingGPU" class="dialog-overlay" @click="closeDialog">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingGPU ? '编辑 GPU 价格' : '添加 GPU 价格' }}</h3>
          <button class="close-btn" @click="closeDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="form-row">
            <div class="form-group">
              <label>厂商</label>
              <input v-model="formData.manufacturer" placeholder="NVIDIA" />
            </div>
            <div class="form-group">
              <label>系列</label>
              <input v-model="formData.series" placeholder="例如: A100" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>型号</label>
              <input v-model="formData.model" placeholder="例如: A100-SXM4-80GB" />
            </div>
            <div class="form-group">
              <label>显存 (GB)</label>
              <input v-model.number="formData.gpu_memory" type="number" placeholder="80" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>GPU 价格</label>
              <input v-model.number="formData.gpu_price" type="number" placeholder="价格" />
            </div>
            <div class="form-group">
              <label>维保费率 (%)</label>
              <input v-model.number="formData.gpu_rate_value" type="number" step="0.01" placeholder="5" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label>备件维修费</label>
              <input v-model.number="formData.spare_repair_cost" type="number" placeholder="费用" />
            </div>
            <div class="form-group">
              <label>人工维修费</label>
              <input v-model.number="formData.labor_repair_cost" type="number" placeholder="费用" />
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeDialog">取消</button>
          <button class="btn-primary" @click="saveGPU">保存</button>
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

// State
const gpus = ref<any[]>([])
const searchQuery = ref('')
const showAddDialog = ref(false)
const editingGPU = ref<any>(null)

const formData = ref({
  manufacturer: '',
  series: '',
  model: '',
  gpu_memory: 0,
  gpu_price: 0,
  gpu_rate_value: 5,
  spare_repair_cost: 0,
  labor_repair_cost: 0
})

// Computed
const filteredGPUs = computed(() => {
  if (!searchQuery.value) return gpus.value
  const query = searchQuery.value.toLowerCase()
  return gpus.value.filter(gpu =>
    (gpu.manufacturer || '').toLowerCase().includes(query) ||
    (gpu.series || '').toLowerCase().includes(query) ||
    (gpu.model || '').toLowerCase().includes(query)
  )
})

// Load GPUs
async function loadGPUs() {
  try {
    const response = await axios.get(`${API_URL}/gpu_prices/`)
    gpus.value = response.data || []
  } catch (error) {
    console.error('Failed to load GPU prices:', error)
  }
}

// Edit GPU
function editGPU(gpu: any) {
  editingGPU.value = gpu
  formData.value = {
    manufacturer: gpu.manufacturer || '',
    series: gpu.series || '',
    model: gpu.model || '',
    gpu_memory: gpu.gpu_memory || 0,
    gpu_price: gpu.gpu_price || 0,
    gpu_rate_value: (gpu.gpu_rate || 0) * 100,
    spare_repair_cost: gpu.spare_repair_cost || 0,
    labor_repair_cost: gpu.labor_repair_cost || 0
  }
}

// Delete GPU
async function deleteGPU(id: number) {
  if (!confirm('确定要删除这个 GPU 价格吗？')) return
  try {
    await axios.delete(`${API_URL}/gpu_prices/${id}`)
    gpus.value = gpus.value.filter(g => g.id !== id)
  } catch (error) {
    console.error('Failed to delete GPU:', error)
  }
}

// Save GPU
async function saveGPU() {
  const data = {
    manufacturer: formData.value.manufacturer,
    series: formData.value.series,
    model: formData.value.model,
    gpu_memory: formData.value.gpu_memory,
    gpu_price: formData.value.gpu_price,
    gpu_rate: formData.value.gpu_rate_value / 100,
    spare_repair_cost: formData.value.spare_repair_cost,
    labor_repair_cost: formData.value.labor_repair_cost
  }

  try {
    if (editingGPU.value) {
      await axios.put(`${API_URL}/gpu_prices/${editingGPU.value.id}`, data)
      const index = gpus.value.findIndex(g => g.id === editingGPU.value.id)
      if (index !== -1) {
        gpus.value[index] = { ...editingGPU.value, ...data }
      }
    } else {
      const response = await axios.post(`${API_URL}/gpu_prices/`, data)
      gpus.value.push(response.data)
    }
    closeDialog()
  } catch (error) {
    console.error('Failed to save GPU:', error)
  }
}

// Close dialog
function closeDialog() {
  showAddDialog.value = false
  editingGPU.value = null
  formData.value = {
    manufacturer: '',
    series: '',
    model: '',
    gpu_memory: 0,
    gpu_price: 0,
    gpu_rate_value: 5,
    spare_repair_cost: 0,
    labor_repair_cost: 0
  }
}

// Export data
function exportData() {
  const exportData = gpus.value.map(gpu => ({
    '厂商': gpu.manufacturer,
    '系列': gpu.series,
    '型号': gpu.model,
    '显存(GB)': gpu.gpu_memory,
    'GPU价格': gpu.gpu_price || 0,
    '维保费率(%)': (gpu.gpu_rate * 100).toFixed(2),
    '备件维修费': gpu.spare_repair_cost || 0,
    '人工维修费': gpu.labor_repair_cost || 0
  }))
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'GPU价格')
  XLSX.writeFile(wb, 'GPU价格.xlsx')
}

onMounted(() => {
  loadGPUs()
})
</script>

<style scoped>
.gpu-price-management {
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
  max-width: 600px;
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
}

.form-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
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
