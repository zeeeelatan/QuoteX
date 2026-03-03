<template>
  <div class="outsourced-personnel-management">
    <!-- Top Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="filter-group">
          <label>岗位</label>
          <select v-model="filters.position" @change="applyFilters">
            <option value="">全部</option>
            <option v-for="pos in positions" :key="pos" :value="pos">{{ pos }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>级别</label>
          <select v-model="filters.level" @change="applyFilters">
            <option value="">全部</option>
            <option v-for="lvl in levels" :key="lvl" :value="lvl">{{ lvl }}</option>
          </select>
        </div>
        <div class="search-box">
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索岗位、级别、能力要求..."
            @input="handleSearch"
          />
        </div>
      </div>
      <div class="filter-right">
        <button class="btn btn-primary" @click="openAddDialog">
          <span class="material-symbols-outlined">add_circle</span>
          添加数据
        </button>
        <button class="btn btn-success" @click="downloadTemplate">
          <span class="material-symbols-outlined">download</span>
          下载模板
        </button>
        <button class="btn btn-warning" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入数据
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleImport"
        />
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>岗位</th>
            <th>级别</th>
            <th>子类型</th>
            <th>学历</th>
            <th>语言要求</th>
            <th>工作经验</th>
            <th>通用能力</th>
            <th>专业技能</th>
            <th class="text-right">一线城市薪资</th>
            <th class="text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedData" :key="item.id">
            <td>{{ item.position }}</td>
            <td><span class="level-badge" :class="getLevelClass(item.level)">{{ item.level }}</span></td>
            <td>{{ item.subtype || '-' }}</td>
            <td>{{ item.education }}</td>
            <td class="language-cell">{{ item.language_requirement }}</td>
            <td>{{ item.work_experience || '-' }}</td>
            <td class="icon-cell">
              <button
                v-if="item.general_ability"
                class="content-icon-btn"
                @click="showContent('通用能力', item.general_ability)"
                title="点击查看完整内容"
              >
                <span class="material-symbols-outlined">visibility</span>
              </button>
              <span v-else class="empty-text">-</span>
            </td>
            <td class="icon-cell">
              <button
                v-if="item.technical_skill"
                class="content-icon-btn"
                @click="showContent('专业技能', item.technical_skill)"
                title="点击查看完整内容"
              >
                <span class="material-symbols-outlined">visibility</span>
              </button>
              <span v-else class="empty-text">-</span>
            </td>
            <td class="text-right">
              <span class="salary-text">
                {{ item.tier1_city_salary ? `¥${formatNumber(item.tier1_city_salary)}` : '-' }}
              </span>
            </td>
            <td class="text-center">
              <button class="action-btn edit-btn" @click="openEditDialog(item)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete-btn" @click="confirmDelete(item)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
          <tr v-if="paginatedData.length === 0">
            <td colspan="10" class="empty-state">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Frozen Bottom Bar with Pagination -->
    <div class="bottom-bar">
      <div class="pagination-container">
        <div class="pagination-info">
          显示第 <span>{{ (currentPage - 1) * pageSize + 1 }}</span> 到
          <span>{{ Math.min(currentPage * pageSize, filteredData.length) }}</span> 条，
          共 <span>{{ filteredData.length }}</span> 条数据
        </div>
        <div class="pagination-controls">
          <select v-model="pageSize" @change="currentPage = 1" class="page-size-select">
            <option :value="10">10条/页</option>
            <option :value="15">15条/页</option>
            <option :value="20">20条/页</option>
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

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑数据' : '添加数据'"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="120px">
        <el-form-item label="岗位">
          <el-input v-model="formData.position" placeholder="请输入岗位名称" />
        </el-form-item>
        <el-form-item label="级别">
          <el-select v-model="formData.level" placeholder="请选择级别" style="width: 100%">
            <el-option label="实习生" value="实习生" />
            <el-option label="初级" value="初级" />
            <el-option label="中级" value="中级" />
            <el-option label="高级" value="高级" />
            <el-option label="专家" value="专家" />
            <el-option label="组长" value="组长" />
            <el-option label="经理" value="经理" />
          </el-select>
        </el-form-item>
        <el-form-item label="子类型">
          <el-select v-model="formData.subtype" placeholder="请选择子类型" clearable style="width: 100%">
            <el-option label="A" value="A" />
            <el-option label="B" value="B" />
          </el-select>
        </el-form-item>
        <el-form-item label="学历要求">
          <el-input v-model="formData.education" placeholder="请输入学历要求" />
        </el-form-item>
        <el-form-item label="语言要求">
          <el-input v-model="formData.language_requirement" type="textarea" :rows="2" placeholder="请输入语言要求" />
        </el-form-item>
        <el-form-item label="工作经验">
          <el-input v-model="formData.work_experience" placeholder="请输入工作经验要求" />
        </el-form-item>
        <el-form-item label="通用能力要求">
          <el-input v-model="formData.general_ability" type="textarea" :rows="3" placeholder="请输入通用能力要求" />
        </el-form-item>
        <el-form-item label="专业技术要求">
          <el-input v-model="formData.technical_skill" type="textarea" :rows="3" placeholder="请输入专业技术要求" />
        </el-form-item>
        <el-form-item label="一线城市薪资">
          <el-input-number v-model="formData.tier1_city_salary" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveData">确定</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>确定要删除这条数据吗？</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteData">确定</el-button>
      </template>
    </el-dialog>

    <!-- Content Viewer Dialog -->
    <el-dialog
      v-model="contentDialogVisible"
      :title="contentDialogTitle"
      width="600px"
      :close-on-click-modal="false"
    >
      <div class="content-viewer">
        <pre class="content-text">{{ contentDialogText }}</pre>
      </div>
      <template #footer>
        <el-button type="primary" @click="contentDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface OutsourcedPersonnel {
  id: number
  position: string
  level: string
  subtype: string | null
  education: string
  language_requirement: string
  work_experience: string | null
  general_ability: string | null
  technical_skill: string | null
  tier1_city_salary: number | null
}

// State
const allData = ref<OutsourcedPersonnel[]>([])
const positions = ref<string[]>([])
const levels = ref<string[]>([])
const filters = ref({
  position: '',
  level: ''
})
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(15)

// Dialog state
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formData = ref<Partial<OutsourcedPersonnel>>({
  position: '',
  level: '',
  subtype: null,
  education: '',
  language_requirement: '',
  work_experience: '',
  general_ability: '',
  technical_skill: '',
  tier1_city_salary: null
})
const currentEditId = ref<number | null>(null)

// Delete dialog
const deleteDialogVisible = ref(false)
const itemToDelete = ref<OutsourcedPersonnel | null>(null)

// Content viewer dialog
const contentDialogVisible = ref(false)
const contentDialogTitle = ref('')
const contentDialogText = ref('')

const fileInput = ref<HTMLInputElement | null>(null)

// Show content dialog
function showContent(title: string, content: string) {
  contentDialogTitle.value = title
  contentDialogText.value = content
  contentDialogVisible.value = true
}

// Computed
const filteredData = computed(() => {
  let result = [...allData.value]

  if (filters.value.position) {
    result = result.filter(item => item.position === filters.value.position)
  }
  if (filters.value.level) {
    result = result.filter(item => item.level === filters.value.level)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(item =>
      item.position.toLowerCase().includes(keyword) ||
      item.level.toLowerCase().includes(keyword) ||
      (item.general_ability && item.general_ability.toLowerCase().includes(keyword)) ||
      (item.technical_skill && item.technical_skill.toLowerCase().includes(keyword))
    )
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return filteredData.value.slice(start, end)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 7
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  let endPage = Math.min(totalPages.value, startPage + maxVisible - 1)

  if (endPage - startPage + 1 < maxVisible) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }

  for (let i = startPage; i <= endPage; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
async function fetchData() {
  try {
    const response = await axios.get(`${API_URL}/outsourced-personnel/`)
    allData.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取数据失败')
  }
}

async function fetchFilters() {
  try {
    const [posRes, levelRes] = await Promise.all([
      axios.get(`${API_URL}/outsourced-personnel/positions/list`),
      axios.get(`${API_URL}/outsourced-personnel/levels/list`)
    ])
    positions.value = posRes.data.positions
    levels.value = levelRes.data.levels
  } catch (error: any) {
    ElMessage.error('获取筛选选项失败')
  }
}

function applyFilters() {
  currentPage.value = 1
}

function handleSearch() {
  currentPage.value = 1
}

function getLevelClass(level: string): string {
  const levelMap: Record<string, string> = {
    '实习生': 'level-intern',
    '初级': 'level-junior',
    '中级': 'level-mid',
    '高级': 'level-senior',
    '专家': 'level-expert',
    '组长': 'level-lead',
    '经理': 'level-manager'
  }
  return levelMap[level] || 'level-default'
}

function formatNumber(num: number): string {
  return num.toLocaleString('zh-CN')
}

// Dialog methods
function openAddDialog() {
  isEditMode.value = false
  currentEditId.value = null
  formData.value = {
    position: '',
    level: '',
    subtype: null,
    education: '',
    language_requirement: '',
    work_experience: '',
    general_ability: '',
    technical_skill: '',
    tier1_city_salary: null
  }
  dialogVisible.value = true
}

function openEditDialog(item: OutsourcedPersonnel) {
  isEditMode.value = true
  currentEditId.value = item.id
  formData.value = { ...item }
  dialogVisible.value = true
}

async function saveData() {
  try {
    if (isEditMode.value && currentEditId.value) {
      await axios.put(`${API_URL}/outsourced-personnel/${currentEditId.value}`, formData.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post(`${API_URL}/outsourced-personnel/`, formData.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await fetchData()
    await fetchFilters()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

function confirmDelete(item: OutsourcedPersonnel) {
  itemToDelete.value = item
  deleteDialogVisible.value = true
}

async function deleteData() {
  if (!itemToDelete.value) return
  try {
    await axios.delete(`${API_URL}/outsourced-personnel/${itemToDelete.value.id}`)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    await fetchData()
    await fetchFilters()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// Import/Export
function downloadTemplate() {
  const headers = ['岗位', '级别', '子类型', '学历', '语言要求', '工作经验', '通用能力要求', '专业技术要求', '一线城市参考月工资']
  const csvContent = [
    headers.join(','),
    '服务台人员,实习生,A,大专以上,无,无工作经验,积极主动具有良好个人形象,基本掌握操作系统及软、硬件的安装诊断排错和维修等技能,5000'
  ].join('\n')

  const blob = new Blob(['\ufeff' + csvContent], { type: 'text/csv;charset=utf-8;' })
  const link = document.createElement('a')
  link.href = URL.createObjectURL(blob)
  link.download = '驻场人员岗位及薪资管理模板.csv'
  link.click()
}

function triggerImport() {
  fileInput.value?.click()
}

async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    const formData = new FormData()
    formData.append('file', file)

    ElMessage.info('正在导入...')

    // Read Excel file and convert to JSON
    const XLSX = await import('xlsx')
    const data = await file.arrayBuffer()
    const workbook = XLSX.read(data)
    const worksheet = workbook.Sheets[workbook.SheetNames[0]]
    const jsonData = XLSX.utils.sheet_to_json(worksheet, { header: 1 }) as any[][]

    // Skip header, process data
    const records: any[] = []
    let currentPos = ''
    let currentLevel = ''

    for (let i = 1; i < jsonData.length; i++) {
      const row = jsonData[i]
      if (!row || row.length === 0) continue

      // Forward fill for position and level
      if (row[0]) currentPos = row[0]
      if (row[1]) currentLevel = row[1]

      const record = {
        position: currentPos || '',
        level: currentLevel || '',
        subtype: row[2] || null,
        education: row[3] || '',
        language_requirement: row[4] || '',
        work_experience: row[5] || null,
        general_ability: row[6] || null,
        technical_skill: row[7] || null,
        tier1_city_salary: row[8] || null
      }
      records.push(record)
    }

    // Send to backend
    await axios.post(`${API_URL}/outsourced-personnel/batch-create`, { records })

    ElMessage.success(`成功导入 ${records.length} 条数据`)
    await fetchData()
    await fetchFilters()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    target.value = ''
  }
}

onMounted(() => {
  fetchData()
  fetchFilters()
})
</script>

<style scoped>
.outsourced-personnel-management {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #0f172a;
  color: #e2e8f0;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
  flex-wrap: wrap;
  gap: 1rem;
}

.filter-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-group label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.filter-group select {
  padding: 0.5rem 0.75rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  min-width: 120px;
}

.filter-right {
  display: flex;
  gap: 0.75rem;
}

.search-box {
  position: relative;
}

.search-box input {
  padding-left: 2.5rem;
  width: 16rem;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #cbd5e1;
  font-size: 0.875rem;
}

.search-box input:focus {
  outline: none;
  border-color: #135bec;
}

.search-icon {
  position: absolute;
  left: 0.6rem;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1rem;
  color: #64748b;
}

/* Buttons */
.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
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

.btn-warning {
  background-color: #f59e0b;
  color: white;
}

.btn-warning:hover {
  background-color: #d97706;
}

/* Table */
.table-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 0.75rem 1rem;
  text-align: left;
  border-bottom: 1px solid #1e293b;
}

.data-table th {
  background-color: #1e293b;
  font-weight: 600;
  color: #94a3b8;
  font-size: 0.75rem;
  text-transform: uppercase;
  position: sticky;
  top: 0;
  z-index: 10;
}

.data-table tbody tr:hover {
  background-color: rgba(19, 91, 236, 0.05);
}

.data-table tbody tr {
  border-bottom: 1px solid #1e293b;
}

.text-right {
  text-align: right !important;
}

.text-center {
  text-align: center !important;
}

.empty-state {
  text-align: center;
  padding: 3rem;
  color: #64748b;
}

/* Level Badge */
.level-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.level-intern {
  background-color: rgba(148, 163, 184, 0.2);
  color: #94a3b8;
}

.level-junior {
  background-color: rgba(59, 130, 246, 0.2);
  color: #3b82f6;
}

.level-mid {
  background-color: rgba(34, 197, 94, 0.2);
  color: #22c55e;
}

.level-senior {
  background-color: rgba(249, 115, 22, 0.2);
  color: #f97316;
}

.level-expert {
  background-color: rgba(168, 85, 247, 0.2);
  color: #a855f7;
}

.level-lead {
  background-color: rgba(236, 72, 153, 0.2);
  color: #ec4899;
}

.level-manager {
  background-color: rgba(234, 179, 8, 0.2);
  color: #eab308;
}

.level-default {
  background-color: rgba(100, 116, 139, 0.2);
  color: #64748b;
}

/* Language Cell */
.language-cell {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Icon Cell */
.icon-cell {
  text-align: center !important;
}

.content-icon-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  background-color: rgba(99, 102, 241, 0.1);
  color: #6366f1;
}

.content-icon-btn:hover {
  background-color: rgba(99, 102, 241, 0.2);
  transform: scale(1.05);
}

.content-icon-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.empty-text {
  color: #64748b;
  font-size: 0.875rem;
}

/* Content Viewer */
.content-viewer {
  max-height: 400px;
  overflow-y: auto;
}

.content-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #0f172a;
  padding: 1rem;
  border-radius: 0.5rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
  font-family: inherit;
}

/* Truncate Cell */
.truncate-cell {
  max-width: 250px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Salary Text */
.salary-text {
  font-weight: 600;
  color: #22c55e;
}

/* Action Buttons */
.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  margin: 0 0.25rem;
}

.action-btn .material-symbols-outlined {
  font-size: 1.125rem;
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

/* Bottom Bar */
.bottom-bar {
  position: sticky;
  bottom: 0;
  background-color: #1e293b;
  border-top: 1px solid #334155;
  padding: 0.75rem 1rem;
  z-index: 100;
}

.pagination-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
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
  min-width: 36px;
  height: 36px;
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

/* Dialog Styles */
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

:deep(.el-textarea__inner) {
  background-color: #0f172a;
  border-color: #334155;
  color: #cbd5e1;
}

:deep(.el-select .el-input__wrapper) {
  background-color: #0f172a;
}

/* Scrollbar */
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
