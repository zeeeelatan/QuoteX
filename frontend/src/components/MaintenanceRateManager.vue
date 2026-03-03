<template>
  <div>
    <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 12px;">
      <el-button type="primary" @click="openDialog()">新增费率</el-button>
      <el-button type="success" @click="downloadTemplateDialog=true">下载模板</el-button>
      <el-button type="warning" @click="triggerImport">导入</el-button>
      <el-button type="danger" @click="clearRates">清空</el-button>
      <el-input v-model="searchText" placeholder="搜索分类/关键字" clearable style="width: 220px; margin-left: 12px;" @input="filterRates" />
      <input ref="importInput" type="file" accept=".xlsx,.xls,.csv" style="display:none" @change="handleImportFile" />
    </div>
    <el-table :data="pagedRateList" style="width: 100%; margin-top: 8px;">
      <el-table-column prop="primary_category" label="一级分类"/>
      <el-table-column prop="secondary_category" label="二级分类"/>
      <el-table-column prop="tertiary_category" label="三级分类"/>
      <el-table-column prop="rate" label="维保费率(%)">
        <template #default="scope">
          {{ Math.round(Number(scope.row.rate) * 100) }}
        </template>
      </el-table-column>
      <el-table-column prop="remark" label="备注"/>
      <el-table-column label="操作">
        <template #default="scope">
          <div style="display: flex; gap: 8px; align-items: center;">
            <el-button size="small" @click="openDialog(scope.row)">编辑</el-button>
            <el-button size="small" type="danger" @click="deleteRate(scope.row.id)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>
    <el-dialog v-model="dialogVisible" title="费率设置">
      <el-form :model="form">
        <el-form-item label="一级分类"><el-input v-model="form.primary_category"/></el-form-item>
        <el-form-item label="二级分类"><el-input v-model="form.secondary_category"/></el-form-item>
        <el-form-item label="三级分类"><el-input v-model="form.tertiary_category"/></el-form-item>
        <el-form-item label="维保费率(%)"><el-input v-model.number="form.rate" placeholder="请输入百分比，如2"/></el-form-item>
        <el-form-item label="备注"><el-input v-model="form.remark"/></el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible=false">取消</el-button>
        <el-button type="primary" @click="saveRate">保存</el-button>
      </template>
    </el-dialog>
    <el-dialog v-model="downloadTemplateDialog" title="下载导入模板" width="300px">
      <div style="text-align:center;">
        <el-button @click="downloadTemplate('xlsx')">下载 xlsx</el-button>
        <el-button @click="downloadTemplate('xls')">下载 xls</el-button>
        <el-button @click="downloadTemplate('csv')">下载 csv</el-button>
      </div>
    </el-dialog>
    <!-- 分页控件放在表格下方，主div内 -->
    <el-pagination
      v-model:current-page="currentPage"
      v-model:page-size="pageSize"
      :page-sizes="[10, 15, 20, 50]"
      :total="filteredRateList.length"
      layout="total, sizes, prev, pager, next, jumper"
      @size-change="handleSizeChange"
      @current-change="handlePageChange"
      style="margin: 16px 0; text-align: right;"
    />
  </div>
</template>
<script setup>
const currentPage = ref(1)
const pageSize = ref(15)
const pagedRateList = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredRateList.value.slice(start, start + pageSize.value)
})
function handleSizeChange(val) {
  pageSize.value = val
  currentPage.value = 1
}
function handlePageChange(val) {
  currentPage.value = val
}

import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as XLSX from 'xlsx'
const rateList = ref([])
const filteredRateList = ref([])
const searchText = ref('')
const dialogVisible = ref(false)
const downloadTemplateDialog = ref(false)
const form = ref({ id: null, primary_category: '', secondary_category: '', tertiary_category: '', rate: 0, remark: '' })
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'
const importInput = ref(null)
const fetchRates = async () => {
  const res = await fetch(`${API_URL}/maintenance_rates/`)
  rateList.value = await res.json()
  filterRates()
}
function filterRates() {
  const text = searchText.value.trim().toLowerCase()
  if (!text) {
    filteredRateList.value = rateList.value
    return
  }
  filteredRateList.value = rateList.value.filter(item => {
    return (
      (item.primary_category && item.primary_category.toLowerCase().includes(text)) ||
      (item.secondary_category && item.secondary_category.toLowerCase().includes(text)) ||
      (item.tertiary_category && item.tertiary_category.toLowerCase().includes(text)) ||
      (item.remark && item.remark.toLowerCase().includes(text))
    )
  })
}
const openDialog = (row) => {
  if (row) {
    form.value = { ...row, rate: Number(row.rate) * 100 }
  } else {
    form.value = { id: null, primary_category: '', secondary_category: '', tertiary_category: '', rate: 0, remark: '' }
  }
  dialogVisible.value = true
}
const saveRate = async () => {
  // 允许输入百分比或小数，自动转换为小数
  let rateVal = form.value.rate
  if (typeof rateVal === 'string') rateVal = rateVal.replace('%','')
  rateVal = Number(rateVal)
  const payload = { ...form.value, rate: rateVal }
  if (form.value.id) {
    await fetch(`${API_URL}/maintenance_rates/${form.value.id}`, { method: 'PUT', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    ElMessage.success('修改成功')
  } else {
    await fetch(`${API_URL}/maintenance_rates/`, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(payload) })
    ElMessage.success('新增成功')
  }
  dialogVisible.value = false
  fetchRates()
}
const deleteRate = async (id) => {
  try {
    await ElMessageBox.confirm(
      '确定要删除该费率吗？此操作不可撤销！',
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await fetch(`${API_URL}/maintenance_rates/${id}`, { method: 'DELETE' })
    ElMessage.success('删除成功')
    fetchRates()
  } catch {
    // 用户取消，无需处理
  }
}
const templateHeaders = [
  '一级分类', '二级分类', '三级分类', '维保费率(%)', '备注'
]
const templateData = [
  {
    '一级分类': '服务器',
    '二级分类': 'X86服务器',
    '三级分类': '通用型',
    '维保费率(%)': '2%',
    '备注': '标准服务器'
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
    link.download = '费率导入模板.csv'
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  } else {
    // 生成Excel内容
    const ws = XLSX.utils.json_to_sheet(templateData, { header: templateHeaders })
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, '模板')
    const ext = type === 'xls' ? 'xls' : 'xlsx'
    XLSX.writeFile(wb, `费率导入模板.${ext}`)
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
    // 兼容费率格式
    data = data.map((row, rowIndex) => {
      let rate = row['维保费率(%)'] || row['rate'] || ''
      if (typeof rate === 'string') rate = rate.replace('%','')
      rate = Number(rate)
      if (!rate || isNaN(rate) || rate <= 0) {
        throw new Error(`第${rowIndex+2}行维保费率无效，请检查！`)
      }
      return {
        primary_category: row['一级分类'] || row['primary_category'] || '',
        secondary_category: row['二级分类'] || row['secondary_category'] || '',
        tertiary_category: row['三级分类'] || row['tertiary_category'] || '',
        rate: rate,
        remark: row['备注'] || row['remark'] || ''
      }
    })
    // 上传到后端
    const res = await fetch(`${API_URL}/maintenance_rates/import`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ data })
    })
    const result = await res.json()
    if (res.ok) {
      ElMessage.success(result.message || '导入成功')
      fetchRates()
    } else {
      ElMessage.error(result.detail || '导入失败')
    }
  } catch (err) {
    ElMessage.error('导入失败: ' + err.message)
  }
  e.target.value = ''
}
const clearRates = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有费率吗？此操作不可撤销！',
      '确认清空',
      {
        confirmButtonText: '清空',
        cancelButtonText: '取消',
        type: 'warning',
      }
    )
    await fetch(`${API_URL}/maintenance_rates/clear`, { method: 'DELETE' })
    ElMessage.success('所有费率已清空')
    fetchRates()
  } catch {
    // 用户取消，无需处理
  }
}
onMounted(fetchRates)
</script> 