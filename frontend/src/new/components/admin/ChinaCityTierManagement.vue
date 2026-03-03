<template>
  <div class="china-city-tier-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button type="button" class="btn btn-primary" @click="fetchData">
          <span class="material-symbols-outlined">refresh</span>
          刷新
        </button>
        <button type="button" class="btn btn-primary" @click="openAddDialog">
          <span class="material-symbols-outlined">add_circle</span>
          添加数据
        </button>
        <button type="button" class="btn btn-success" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入Excel
        </button>
        <button type="button" class="btn btn-danger" @click="confirmClear">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空数据
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
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索城市、省份、等级..."
            @input="currentPage = 1"
          />
        </div>
        <span class="total-count">共 {{ filteredData.length }} 条</span>
      </div>
    </div>

    <div class="table-container" :class="{ loading: loading }">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>城市等级</th>
              <th>城市等级代码</th>
              <th>城市名称</th>
              <th>所属省份</th>
              <th>行政级别</th>
              <th>是否省会</th>
              <th>GDP万亿城市</th>
              <th>物流枢纽等级</th>
              <th>备注</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in paginatedData" :key="row.id">
              <td>{{ row.seq_no ?? '-' }}</td>
              <td>{{ row.city_tier ?? '-' }}</td>
              <td>{{ row.tier_code ?? '-' }}</td>
              <td>{{ row.city_name ?? '-' }}</td>
              <td>{{ row.province ?? '-' }}</td>
              <td>{{ row.admin_level ?? '-' }}</td>
              <td>{{ row.is_provincial_capital ?? '-' }}</td>
              <td>{{ row.is_gdp_trillion ?? '-' }}</td>
              <td>{{ row.logistics_hub_level ?? '-' }}</td>
              <td class="desc-cell">{{ row.remarks ?? '-' }}</td>
              <td class="text-center">
                <button class="action-btn edit-btn" @click="openEditDialog(row)" title="编辑">
                  <span class="material-symbols-outlined">edit</span>
                </button>
                <button class="action-btn delete-btn" @click="confirmDelete(row)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && filteredData.length === 0" class="empty-state">
        <span class="material-symbols-outlined">location_city</span>
        <p>暂无中国城市分级数据，请导入 Excel 或添加数据</p>
      </div>
    </div>

    <div class="bottom-bar">
      <div class="pagination-container">
        <div class="pagination-info">
          显示第 <span>{{ (currentPage - 1) * pageSize + 1 }}</span> 到
          <span>{{ Math.min(currentPage * pageSize, filteredData.length) }}</span> 条，
          共 <span>{{ filteredData.length }}</span> 条数据
        </div>
        <div class="pagination-controls">
          <select v-model="pageSize" @change="currentPage = 1" class="page-size-select">
            <option :value="15">15条/页</option>
            <option :value="30">30条/页</option>
            <option :value="50">50条/页</option>
            <option :value="100">100条/页</option>
          </select>
          <button class="pagination-btn" :disabled="currentPage === 1" @click="currentPage--">
            <span class="material-symbols-outlined">chevron_left</span>
          </button>
          <button
            v-for="page in visiblePages"
            :key="page"
            class="pagination-btn page-number"
            :class="{ active: page === currentPage }"
            @click="currentPage = page"
          >
            {{ page }}
          </button>
          <button class="pagination-btn" :disabled="currentPage >= totalPages" @click="currentPage++">
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
      </div>
    </div>

    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑数据' : '添加数据'"
      width="640px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="120px">
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="序号">
              <el-input-number v-model="formData.seq_no" :min="0" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="城市等级">
              <el-input v-model="formData.city_tier" placeholder="如：一线城市" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="城市等级代码">
              <el-input v-model="formData.tier_code" placeholder="如：T1" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="城市名称">
              <el-input v-model="formData.city_name" placeholder="城市名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="所属省份">
              <el-input v-model="formData.province" placeholder="省份" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="行政级别">
              <el-input v-model="formData.admin_level" placeholder="如：副省级市" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="是否省会">
              <el-input v-model="formData.is_provincial_capital" placeholder="是/否" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="GDP万亿城市">
              <el-input v-model="formData.is_gdp_trillion" placeholder="是/否" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="物流枢纽等级">
          <el-input v-model="formData.logistics_hub_level" placeholder="如：国家级" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="formData.remarks" type="textarea" :rows="2" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <div class="dialog-footer-actions">
          <button type="button" class="btn btn-secondary" @click="dialogVisible = false">取消</button>
          <button type="button" class="btn btn-primary" @click="saveData">确定</button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="deleteDialogVisible" title="确认删除" width="400px" :close-on-click-modal="false">
      <p>确定要删除这条数据吗？</p>
      <template #footer>
        <div class="dialog-footer-actions">
          <button type="button" class="btn btn-secondary" @click="deleteDialogVisible = false">取消</button>
          <button type="button" class="btn btn-danger" @click="deleteData">确定</button>
        </div>
      </template>
    </el-dialog>

    <el-dialog v-model="clearDialogVisible" title="确认清空" width="400px" :close-on-click-modal="false">
      <p>确定要清空所有数据吗？此操作不可恢复！</p>
      <template #footer>
        <div class="dialog-footer-actions">
          <button type="button" class="btn btn-secondary" @click="clearDialogVisible = false">取消</button>
          <button type="button" class="btn btn-danger" @click="clearData">确定</button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface ChinaCityTierRow {
  id: number
  seq_no: number | null
  city_tier: string | null
  tier_code: string | null
  city_name: string
  province: string | null
  admin_level: string | null
  is_provincial_capital: string | null
  is_gdp_trillion: string | null
  logistics_hub_level: string | null
  remarks: string | null
}

const list = ref<ChinaCityTierRow[]>([])
const loading = ref(false)
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(30)
const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentEditId = ref<number | null>(null)
const deleteDialogVisible = ref(false)
const clearDialogVisible = ref(false)
const itemToDelete = ref<ChinaCityTierRow | null>(null)
const fileInput = ref<HTMLInputElement | null>(null)

const defaultForm = (): Partial<ChinaCityTierRow> => ({
  seq_no: null,
  city_tier: null,
  tier_code: null,
  city_name: '',
  province: null,
  admin_level: null,
  is_provincial_capital: null,
  is_gdp_trillion: null,
  logistics_hub_level: null,
  remarks: null
})
const formData = ref<Partial<ChinaCityTierRow>>(defaultForm())

const filteredData = computed(() => {
  if (!searchKeyword.value.trim()) return list.value
  const k = searchKeyword.value.toLowerCase()
  return list.value.filter(
    (row) =>
      (row.city_name && row.city_name.toLowerCase().includes(k)) ||
      (row.province && row.province.toLowerCase().includes(k)) ||
      (row.city_tier && row.city_tier.toLowerCase().includes(k)) ||
      (row.tier_code && row.tier_code.toLowerCase().includes(k))
  )
})

const totalPages = computed(() => Math.max(1, Math.ceil(filteredData.value.length / pageSize.value)))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const visiblePages = computed(() => {
  const total = totalPages.value
  const maxVisible = 7
  let start = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let end = Math.min(total, start + maxVisible - 1)
  if (end - start + 1 < maxVisible) start = Math.max(1, end - maxVisible + 1)
  const pages: number[] = []
  for (let i = start; i <= end; i++) pages.push(i)
  return pages
})

async function fetchData() {
  loading.value = true
  try {
    const res = await axios.get(`${API_URL}/china-city-tier/`)
    list.value = res.data
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '获取数据失败')
  } finally {
    loading.value = false
  }
}

function openAddDialog() {
  isEditMode.value = false
  currentEditId.value = null
  formData.value = defaultForm()
  dialogVisible.value = true
}

function openEditDialog(row: ChinaCityTierRow) {
  isEditMode.value = true
  currentEditId.value = row.id
  formData.value = { ...row }
  dialogVisible.value = true
}

async function saveData() {
  try {
    if (isEditMode.value && currentEditId.value != null) {
      await axios.put(`${API_URL}/china-city-tier/${currentEditId.value}`, formData.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post(`${API_URL}/china-city-tier/`, formData.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '保存失败')
  }
}

function confirmDelete(row: ChinaCityTierRow) {
  itemToDelete.value = row
  deleteDialogVisible.value = true
}

async function deleteData() {
  if (!itemToDelete.value) return
  try {
    await axios.delete(`${API_URL}/china-city-tier/${itemToDelete.value.id}`)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '删除失败')
  }
}

function confirmClear() {
  clearDialogVisible.value = true
}

async function clearData() {
  try {
    await axios.delete(`${API_URL}/china-city-tier/clear`)
    ElMessage.success('数据已清空')
    clearDialogVisible.value = false
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '清空失败')
  }
}

function triggerImport() {
  fileInput.value?.click()
}

async function handleImport(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  try {
    const fd = new FormData()
    fd.append('file', file)
    ElMessage.info('正在导入...')
    await axios.post(`${API_URL}/china-city-tier/import-excel`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success('导入成功')
    input.value = ''
    await fetchData()
  } catch (e: any) {
    ElMessage.error(e.response?.data?.detail || '导入失败')
  }
}

onMounted(() => {
  fetchData()
})
</script>

<style scoped>
.china-city-tier-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: #0f172a;
  color: #e2e8f0;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 1rem 0;
  flex-shrink: 0;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

/* 按钮：与城市社保基准、机房搬迁车型数据一致 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #135bec;
  color: white;
}

.btn-primary:hover {
  background-color: #0d4fd6;
}

.btn-success {
  background-color: #22c55e;
  color: white;
}

.btn-success:hover {
  background-color: #16a34a;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.btn-secondary {
  background-color: #334155;
  color: #cbd5e1;
}

.btn-secondary:hover {
  background-color: #475569;
}

.search-box {
  position: relative;
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  min-width: 12rem;
}

.search-box input {
  border: none;
  outline: none;
  background: transparent;
  color: #cbd5e1;
  font-size: 0.875rem;
  width: 100%;
}

.search-box input::placeholder {
  color: #64748b;
}

.search-box .search-icon {
  position: absolute;
  left: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: #64748b;
  pointer-events: none;
}

.total-count {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* 表格容器：深色背景与边框 */
.table-container {
  flex: 1;
  min-height: 0;
  position: relative;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  overflow: hidden;
}

.table-container.loading {
  pointer-events: none;
}

.table-scroll {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 100%;
}

/* 表头与数据行：字体、线条颜色与其他模块一致 */
.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.data-table th,
.data-table td {
  padding: 0.5rem 0.625rem;
  text-align: left;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.data-table th {
  background: #1e293b;
  color: #94a3b8;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table td {
  color: #e2e8f0;
}

.data-table tbody tr:hover {
  background: rgba(56, 189, 248, 0.06);
}

.data-table td.desc-cell {
  max-width: 12rem;
  white-space: normal;
  word-break: break-word;
}

.text-center {
  text-align: center !important;
}

/* 行内操作按钮 */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  margin: 0 0.125rem;
}

.action-btn .material-symbols-outlined {
  font-size: 1rem;
}

.edit-btn {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

.edit-btn:hover {
  background-color: rgba(19, 91, 236, 0.2);
}

.delete-btn {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.2);
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
  z-index: 10;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #334155;
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}

/* 底部分页栏 */
.bottom-bar {
  flex-shrink: 0;
  background-color: #1e293b;
  border-top: 1px solid #334155;
  padding: 0.75rem 1rem;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: #94a3b8;
}

.pagination-info span {
  color: #cbd5e1;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-size-select {
  padding: 0.375rem 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  margin-right: 0.5rem;
}

.pagination-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  padding: 0 0.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.pagination-btn:hover:not(:disabled) {
  background-color: #334155;
  color: #f1f5f9;
}

.pagination-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.pagination-btn.page-number {
  font-size: 0.875rem;
}

.pagination-btn.page-number.active {
  background-color: #135bec;
  border-color: #135bec;
  color: white;
}

.pagination-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.dialog-footer-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

/* 弹窗深色主题（与其他模块一致） */
:deep(.el-dialog) {
  background-color: #1e293b;
  border: 1px solid #334155;
}

:deep(.el-dialog__title) {
  color: #f1f5f9;
}

:deep(.el-dialog__body) {
  color: #cbd5e1;
}

:deep(.el-form-item__label) {
  color: #94a3b8;
}

:deep(.el-input__wrapper) {
  background-color: #0f172a;
  border-color: #334155;
}

:deep(.el-input__inner) {
  color: #cbd5e1;
}

/* 滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>
