<template>
  <div class="gpu-price-page">
    <h2>GPU价格管理</h2>
    <div class="actions">
      <input type="file" ref="fileRef" accept=".xls,.xlsx" @change="handleFileUpload" style="display:none" />
      <el-button type="primary" @click="fetchData">刷新</el-button>
      <el-button type="success" @click="downloadTemplate">下载模板</el-button>
      <el-button type="warning" @click="openImport">导入</el-button>
      <el-button type="danger" @click="clearAll">清空</el-button>
    </div>
    <table border="1" class="data-table">
      <thead>
        <tr>
          <th>厂商</th>
          <th>系列</th>
          <th>型号</th>
          <th>GPU卡显存</th>
          <th>GPU卡接口类型</th>
          <th>销售情况</th>
          <th>GPU卡价格</th>
          <th>GPU卡费率</th>
          <th>备件维修费</th>
          <th>人工维修费</th>
          <th>维保服务费</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="row in rows" :key="row.id">
          <td>{{ row.manufacturer || '-' }}</td>
          <td>{{ row.series || '-' }}</td>
          <td>{{ row.model || '-' }}</td>
          <td>{{ row.gpu_memory || '-' }}</td>
          <td>{{ row.gpu_interface_type || '-' }}</td>
          <td>{{ row.sales_status || '-' }}</td>
          <td>{{ currency(row.gpu_price) }}</td>
          <td>{{ percent(row.gpu_rate) }}</td>
          <td>{{ currency(row.spare_repair_cost) }}</td>
          <td>{{ currency(row.labor_repair_cost) }}</td>
          <td>{{ currency(row.service_fee) }}</td>
        </tr>
      </tbody>
    </table>
  </div>
  
</template>

<script setup>
import { ref, onMounted } from 'vue'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const rows = ref([])
const fileRef = ref()

function currency(v){
  if (v === null || v === undefined) return '-'
  const n = Number(v)
  if (Number.isNaN(n)) return '-'
  return `¥${n.toFixed(2)}`
}
function percent(v){
  if (v === null || v === undefined) return '-'
  const n = Number(v)
  if (Number.isNaN(n)) return '-'
  return `${(n*100).toFixed(2)}%`
}

function downloadTemplate(){
  // 优先 xlsx，失败时用户可手动替换为 csv
  window.open(`${API_URL}/gpu_prices/template?fmt=xlsx`, '_blank')
}
function openImport(){
  fileRef.value && fileRef.value.click()
}
async function fetchData(){
  const resp = await fetch(`${API_URL}/gpu_prices/`)
  rows.value = await resp.json()
}

async function handleFileUpload(e){
  const file = e.target.files[0]
  if (!file) return
  const form = new FormData()
  form.append('file', file)
  const resp = await fetch(`${API_URL}/gpu_prices/import`, { method:'POST', body: form })
  const result = await resp.json().catch(() => ({}))
  if (resp.ok) {
    const msg = `导入成功：插入 ${result.inserted_count || 0} 条，修正 ${result.corrected_count || 0} 条，跳过 ${result.skipped_count || 0} 条。`
    alert(msg)
    await fetchData()
  } else {
    alert(`导入失败：${result.detail || '请检查模板与数据格式'}`)
  }
  e.target.value = ''
}

async function clearAll(){
  await fetch(`${API_URL}/gpu_prices/clear`, { method: 'DELETE' })
  await fetchData()
}

onMounted(fetchData)
</script>

<style scoped>
.gpu-price-page { padding: 16px; }
.actions { margin: 8px 0 12px; display:flex; gap:12px; align-items:center; }
.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 6px 8px; text-align: right; }
.data-table th:first-child, .data-table td:first-child { text-align: left; }
</style>



