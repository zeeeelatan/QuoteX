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
      <el-table-column prop="level_code" label="服务级别"/>
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
        <el-form-item label="服务级别"><el-input v-model="form.level_code"/></el-form-item>
        <el-form-item label="响应时效"><el-input v-model="form.response_time"/></el-form-item>
        <el-form-item label="服务级别系数值"><el-input v-model.number="form.coefficient" placeholder="请输入系数值，如1.2"/></el-form-item>
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
    <!-- 分页控件放在表格下方，主div内 -->
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
const currentPage = ref(1)
const pageSize = ref(15)
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

import { ref, onMounted, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import * as XLSX from 'xlsx'
const serviceLevelList = ref([])
const filteredServiceLevelList = ref([])
const searchText = ref('')
const dialogVisible = ref(false)
const downloadTemplateDialog = ref(false)
const form = ref({ id: null, level_code: '', response_time: '', coefficient: 1.0 })
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'
const importInput = ref(null)

const fetchServiceLevels = async () => {
  try {
    const res = await fetch(`${API_URL}/service-level/`)
    if (res.ok) {
      serviceLevelList.value = await res.json()
      filterServiceLevels()
    } else {
      ElMessage.error('获取服务级别列表失败')
    }
  } catch (error) {
    ElMessage.error('获取服务级别列表失败: ' + error.message)
  }
}

function filterServiceLevels() {
  const text = searchText.value.trim().toLowerCase()
  if (!text) {
    filteredServiceLevelList.value = serviceLevelList.value
    return
  }
  filteredServiceLevelList.value = serviceLevelList.value.filter(item => {
    return item.level_code.toLowerCase().includes(text) ||
           item.response_time.toLowerCase().includes(text) ||
           String(item.coefficient).includes(text)
  })
}

function openDialog(item = null) {
  if (item) {
    form.value = { ...item }
  } else {
    form.value = { id: null, level_code: '', response_time: '', coefficient: 1.0 }
  }
  dialogVisible.value = true
}

async function saveServiceLevel() {
  try {
    const url = form.value.id 
      ? `${API_URL}/service-level/${form.value.id}`
      : `${API_URL}/service-level/`
    
    const method = form.value.id ? 'PUT' : 'POST'
    
    const response = await fetch(url, {
      method,
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        level_code: form.value.level_code,
        response_time: form.value.response_time,
        coefficient: form.value.coefficient
      })
    })
    
    if (response.ok) {
      ElMessage.success(form.value.id ? '更新成功' : '创建成功')
      dialogVisible.value = false
      await fetchServiceLevels()
    } else {
      const error = await response.json()
      ElMessage.error(error.detail || '操作失败')
    }
  } catch (error) {
    ElMessage.error('操作失败: ' + error.message)
  }
}

async function deleteServiceLevel(id) {
  try {
    const result = await ElMessageBox.confirm('确定要删除这个服务级别吗？', '确认删除', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (result) {
      const response = await fetch(`${API_URL}/service-level/${id}`, {
        method: 'DELETE'
      })
      
      if (response.ok) {
        ElMessage.success('删除成功')
        await fetchServiceLevels()
      } else {
        ElMessage.error('删除失败')
      }
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('删除失败: ' + error.message)
    }
  }
}

async function clearServiceLevels() {
  try {
    const result = await ElMessageBox.confirm('确定要清空所有服务级别吗？此操作不可恢复！', '确认清空', {
      confirmButtonText: '确定',
      cancelButtonText: '取消',
      type: 'warning'
    })
    
    if (result) {
      // 获取所有服务级别并逐个删除
      const serviceLevels = await fetch(`${API_URL}/service-level/`).then(res => res.json())
      
      for (const item of serviceLevels) {
        await fetch(`${API_URL}/service-level/${item.id}`, { method: 'DELETE' })
      }
      
      ElMessage.success('清空成功')
      await fetchServiceLevels()
    }
  } catch (error) {
    if (error !== 'cancel') {
      ElMessage.error('清空失败: ' + error.message)
    }
  }
}

function triggerImport() {
  importInput.value.click()
}

async function handleImportFile(event) {
  const file = event.target.files[0]
  if (!file) return
  
  const formData = new FormData()
  formData.append('file', file)
  
  try {
    const response = await fetch(`${API_URL}/service-level/import`, {
      method: 'POST',
      body: formData
    })
    
    const result = await response.json()
    
    if (response.ok) {
      ElMessage.success(result.message)
      await fetchServiceLevels()
    } else {
      ElMessage.error(result.detail || '导入失败')
    }
  } catch (error) {
    ElMessage.error('导入失败: ' + error.message)
  }
  
  // 清空文件输入
  event.target.value = ''
}

async function downloadTemplate(format) {
  try {
    const response = await fetch(`${API_URL}/service-level/template`)
    if (response.ok) {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `服务级别导入模板.${format}`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
      downloadTemplateDialog.value = false
    } else {
      ElMessage.error('下载模板失败')
    }
  } catch (error) {
    ElMessage.error('下载模板失败: ' + error.message)
  }
}

onMounted(() => {
  fetchServiceLevels()
})
</script> 