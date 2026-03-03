<template>
  <div>
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
      <el-button type="primary" @click="openDialog()">新增服务级别</el-button>
      <el-button type="success" @click="downloadTemplateDialog=true">下载模板</el-button>
      <el-button type="warning" @click="triggerImport">导入</el-button>
      <el-button type="danger" @click="clearServiceLevels">清空</el-button>
      <el-input v-model="searchText" placeholder="搜索服务级别/关键字" clearable style="width: 220px; margin-left: 12px;" @input="filterServiceLevels" />
      <input ref="importInput" type="file" accept=".xlsx,.xls,.csv" style="display:none" @change="handleImportFile" />
    </div>
    <el-table :data="pagedServiceLevelList" style="width: 100%; margin-top: 8px;">
      <el-table-column prop="service_level" label="服务级别"/>
      <el-table-column prop="response_time" label="响应时效"/>
      <el-table-column prop="coefficient" label="服务级别系数值">
        <template #default="scope">
          {{ Number(scope.row.coefficient).toFixed(2) }}
        </template>
      </el-table-column>
      <el-table-column label="操作">
        <template #default="scope">
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-button size="small" @click="openDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteServiceLevel(scope.row.id)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialogVisible" title="服务级别设置">
      <el-form :model="form">
        <el-form-item label="服务级别"><el-input v-model="form.service_level"/></el-form-item>
        <el-form-item label="响应时效"><el-input v-model="form.response_time"/></el-form-item>
        <el-form-item label="服务级别系数值"><el-input v-model.number="form.coefficient" placeholder="请输入系数值，如1.5"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="saveServiceLevel">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="downloadTemplateDialog" title="下载导入模板" width="300px">
      <div style="text-align:center;">
        <el-button @click="downloadTemplate('xlsx')">下载 xlsx</el-button>
        <el-button @click="downloadTemplate('xls')">下载 xls</el-button>
        <el-button @click="downloadTemplate('csv')">下载 csv</el-button>
      </div>
    </el-dialog>
    <!-- 分页控件 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 15, 20, 50]"
      :total="filteredServiceLevelList.length"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      style="margin: 16px 0; text-align: right;"
    />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as XLSX from 'xlsx'

const currentPage = ref(1)
const pageSize = ref(15)
const serviceLevelList = ref([])
const filteredServiceLevelList = ref([])
const searchText = ref('')
const dialogVisible = ref(false)
const downloadTemplateDialog = ref(false)
const form = ref({ id: null, service_level: '', response_time: '', coefficient: 1.0 })
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'
const importInput = ref(null)

const pagedServiceLevelList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredServiceLevelList.value.slice(start, start + pageSize.value)
})

function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
}

function handlePageChange(val) {
  currentPage.value = val
}

const fetchServiceLevels = async () => {
  const res = await fetch(`${API_URL}/service_levels/`)
  serviceLevelList.value = await res.json()
  filterServiceLevels()
}

function filterServiceLevels() {
  const text = searchText.value.trim().toLowerCase()
  if (!text) {
    filteredServiceLevelList.value = serviceLevelList.value
    return
  }
  filteredServiceLevelList.value = serviceLevelList.value.filter(item => {
    return (
      (item.service_level && item.service_level.toLowerCase().includes(text)) ||
      (item.response_time && item.response_time.toLowerCase().includes(text))
    )
  })
}

const openDialog = (row) => {
  if (row) {
    form.value = { ...row }
  } else {
    form.value = { id: null, service_level: '', response_time: '', coefficient: 1.0 }
  }
  dialogVisible.value = true
}

const saveServiceLevel = async () => {
  const payload = { ...form.value }
  if (form.value.id) {
    await fetch(`${API_URL}/service_levels/${form.value.id}`, { 
      method: 'PUT', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify(payload) 
    })
    ElMessage.success('修改成功')
  } else {
    await fetch(`${API_URL}/service_levels/`, { 
      method: 'POST', 
      headers: { 'Content-Type': 'application/json' }, 
      body: JSON.stringify(payload) 
    })
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchServiceLevels()
}

const deleteServiceLevel = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该服务级别吗？此操作不可撤销！',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await fetch(`${API_URL}/service_levels/${id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    fetchServiceLevels()
  } catch {
    // 用户取消，无需处理
  }
}

const templateHeaders = [
  '服务级别', '响应时效', '服务级别系数值'
]

const templateData = [
  {
    '服务级别': 'SLA A++',
    '响应时效': '7*24*2（2小时工程师和备件到达）',
    '服务级别系数值': '1.5'
  }
]

function downloadTemplate(type) {
  if (type === 'csv') {
    // 生成CSV内容
    const rows = [templateHeaders.join(',')]
    templateData.forEach(row => {
      rows.push(templateHeaders.map(h => row[h]).join(','))
    })
    const csvContent = rows.join('\r\n')
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' })
    const link = document.createElement('a')
    link.href = URL.createObjectURL(blob)
    link.download = '服务级别导入模板.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    // 生成Excel内容
    const ws = XLSX.utils.json_to_sheet(templateData, { header: templateHeaders })
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '模板')
    const ext = type === 'xls' ? 'xls' : 'xlsx'
    XLSX.writeFile(wb, `服务级别导入模板.${ext}`)
  }
  downloadTemplateDialog.value = false
}

function triggerImport() {
  importInput.value && importInput.value.click()
}

async function handleImportFile(e) {
  const file = e.target.files[0]
  if (!file) return
  try {
    let data = []
    if (file.name.endsWith('.csv')) {
      // 读取CSV
      const text = await file.text()
      const rows = text.split(/\r?\n/).filter(Boolean)
      const headers = rows[0].split(',')
      for (let i = 1; i < rows.length; i++) {
        const row = rows[i].split(',')
        const obj = {}
        headers.forEach((h, idx) => obj[h.trim()] = row[idx]?.trim() || '')
        data.push(obj)
      }
    } else {
      // 读取Excel
      const wb = await XLSX.read(await file.arrayBuffer(), { type: 'array' })
      const ws = wb.Sheets[wb.SheetNames[0]]
      data = XLSX.utils.sheet_to_json(ws)
    }
    // 转换数据格式
    data = data.map((row, rowIndex) => {
      let coefficient = row['服务级别系数值'] || row['coefficient'] || ''
      coefficient = Number(coefficient)
      if (!coefficient || isNaN(coefficient) || coefficient <= 0) {
        throw new Error(`第${rowIndex+2}行服务级别系数值无效，请检查！`)
      }
      return {
        service_level: row['服务级别'] || row['service_level'] || '',
        response_time: row['响应时效'] || row['response_time'] || '',
        coefficient: coefficient
      }
    })
    // 上传到后端
    const res = await fetch(`${API_URL}/service_levels/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    })
    const result = await res.json()
    if (res.ok) {
      ElMessage.success(result.message || '导入成功')
      fetchServiceLevels()
    } else {
      ElMessage.error(result.detail || '导入失败')
    }
  } catch (err) {
    ElMessage.error('导入失败: ' + err.message)
  }
  e.target.value = ''
}

const clearServiceLevels = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有服务级别吗？此操作不可撤销！',
      '确认清空',
      {
        confirmButtonText: '清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await fetch(`${API_URL}/service_levels/clear`, { method: 'DELETE' })
    ElMessage.success('所有服务级别已清空')
    fetchServiceLevels()
  } catch {
    // 用户取消，无需处理
  }
}

onMounted(fetchServiceLevels)
</script> 