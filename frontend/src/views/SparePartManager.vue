<template>
  <div class="sp-page">
    <h2>备件管理</h2>
    <div class="actions">
      <input type="file" ref="fileRef" accept=".xls,.xlsx" @change="handleFileUpload" style="display:none" />
      <el-button type="primary" @click="fetchData">刷新</el-button>
      <el-button type="success" @click="downloadTemplate">下载模板</el-button>
      <el-button type="warning" @click="() => fileRef && fileRef.click()">导入</el-button>
      <el-button type="danger" @click="clearAll">清空</el-button>
    </div>
    <el-table :data="rows" style="width: 100%">
      <el-table-column prop="manufacturer" label="厂商" />
      <el-table-column prop="part_pn" label="备件PN" />
      <el-table-column prop="part_desc" label="备件描述" />
      <el-table-column prop="part_category" label="备件分类" />
      <el-table-column prop="part_condition" label="备件成色" />
      <el-table-column prop="repair_method" label="报修方式" />
      <el-table-column prop="repair_period" label="报修期限" />
      <el-table-column prop="unit_price" label="单价">
        <template #default="scope">{{ currency(scope.row.unit_price) }}</template>
      </el-table-column>
    </el-table>
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

async function fetchData(){
  const resp = await fetch(`${API_URL}/spare_parts/`)
  rows.value = await resp.json()
}
function downloadTemplate(){
  window.open(`${API_URL}/spare_parts/template?fmt=xlsx`, '_blank')
}
async function handleFileUpload(e){
  const file = e.target.files[0]
  if (!file) return
  const form = new FormData()
  form.append('file', file)
  const resp = await fetch(`${API_URL}/spare_parts/import`, { method:'POST', body: form })
  if (resp.ok){ await fetchData() } else { alert('导入失败') }
  e.target.value = ''
}
async function clearAll(){
  await fetch(`${API_URL}/spare_parts/clear`, { method:'DELETE' })
  await fetchData()
}
onMounted(fetchData)
</script>

<style scoped>
.actions { margin: 8px 0 12px; display:flex; gap:12px; align-items:center; }
</style>


