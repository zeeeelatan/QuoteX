<template>
  <div class="city-social-insurance">
    <!-- Top Filter Bar -->
    <div class="filter-bar">
      <div class="filter-left">
        <div class="filter-group">
          <label>省份</label>
          <select v-model="filters.province" @change="handleFilterChange">
            <option value="">全部省份</option>
            <option v-for="prov in provinces" :key="prov" :value="prov">{{ prov }}</option>
          </select>
        </div>
        <div class="filter-group">
          <label>城市</label>
          <select v-model="filters.city" @change="applyFilters">
            <option value="">全部城市</option>
            <option v-for="city in filteredCities" :key="city" :value="city">{{ city }}</option>
          </select>
        </div>
        <div class="search-box">
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索城市..."
            @input="handleSearch"
          />
        </div>
      </div>
      <div class="filter-right">
        <button class="btn btn-primary" @click="openAddDialog">
          <span class="material-symbols-outlined">add_circle</span>
          添加数据
        </button>
        <button class="btn btn-success" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入Excel
        </button>
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleImport"
        />
        <button class="btn btn-danger" @click="confirmClear">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空数据
        </button>
      </div>
    </div>

    <!-- Data Table -->
    <div class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>省份</th>
            <th>城市</th>
            <th>社保基数上限</th>
            <th>社保基数下限</th>
            <th>计算基数</th>
            <th>工伤基数</th>
            <th>公司养老</th>
            <th>公司医疗</th>
            <th>公司工伤</th>
            <th>公司失业</th>
            <th>公司残保金</th>
            <th>公司公积金</th>
            <th>个人养老</th>
            <th>个人医疗</th>
            <th>个人失业</th>
            <th>个人公积金</th>
            <th class="text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedData" :key="item.id">
            <td>{{ item.province }}</td>
            <td>
              <span class="city-name">{{ item.city }}</span>
              <span v-if="item.city_alias" class="city-alias">({{ item.city_alias }})</span>
            </td>
            <td>{{ formatNumber(item.upper_limit) }}</td>
            <td>{{ formatNumber(item.lower_limit) }}</td>
            <td>{{ formatNumber(item.calc_base) }}</td>
            <td>{{ formatNumber(item.injury_base) }}</td>
            <td>{{ formatRate(item.corp_pension_rate) }}</td>
            <td>{{ formatRate(item.corp_medical_rate) }}</td>
            <td>{{ formatRate(item.corp_injury_rate) }}</td>
            <td>{{ formatRate(item.corp_unemployment_rate) }}</td>
            <td>{{ formatRate(item.corp_disability_rate) }}</td>
            <td>{{ formatRate(item.corp_fund_rate) }}</td>
            <td>{{ formatRate(item.indiv_pension_rate) }}</td>
            <td>{{ formatRate(item.indiv_medical_rate) }}</td>
            <td>{{ formatRate(item.indiv_unemployment_rate) }}</td>
            <td>{{ formatRate(item.indiv_fund_rate) }}</td>
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
            <td colspan="17" class="empty-state">暂无数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Bottom Bar with Pagination -->
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

    <!-- Add/Edit Dialog -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑数据' : '添加数据'"
      width="800px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="140px">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="20">
          <el-col :span="12">
            <el-form-item label="省份">
              <el-input v-model="formData.province" placeholder="请输入省份" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="城市">
              <el-input v-model="formData.city" placeholder="请输入城市" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="城市别名">
          <el-input v-model="formData.city_alias" placeholder="可选，如：深圳（非深户）" />
        </el-form-item>

        <div class="form-section-title">社保基数</div>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="基数上限">
              <el-input-number v-model="formData.upper_limit" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="基数下限">
              <el-input-number v-model="formData.lower_limit" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="计算基数">
              <el-input-number v-model="formData.calc_base" :min="0" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="工伤基数">
          <el-input-number v-model="formData.injury_base" :min="0" style="width: 100%" />
        </el-form-item>

        <div class="form-section-title">公司部分比例</div>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="养老保险">
              <el-input-number v-model="formData.corp_pension_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="医疗保险">
              <el-input-number v-model="formData.corp_medical_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工伤保险">
              <el-input-number v-model="formData.corp_injury_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="生育保险">
              <el-input-number v-model="formData.corp_maternity_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="失业保险">
              <el-input-number v-model="formData.corp_unemployment_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="残保金">
              <el-input-number v-model="formData.corp_disability_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="公积金">
          <el-input-number v-model="formData.corp_fund_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
        </el-form-item>

        <div class="form-section-title">个人部分比例</div>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="养老保险">
              <el-input-number v-model="formData.indiv_pension_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="医疗保险">
              <el-input-number v-model="formData.indiv_medical_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="工伤保险">
              <el-input-number v-model="formData.indiv_injury_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="20">
          <el-col :span="8">
            <el-form-item label="生育保险">
              <el-input-number v-model="formData.indiv_maternity_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="失业保险">
              <el-input-number v-model="formData.indiv_unemployment_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="公积金">
              <el-input-number v-model="formData.indiv_fund_rate" :min="0" :max="1" :step="0.001" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
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

    <!-- Clear Confirmation Dialog -->
    <el-dialog
      v-model="clearDialogVisible"
      title="确认清空"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>确定要清空所有数据吗？此操作不可恢复！</p>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="clearData">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface CitySocialInsurance {
  id: number
  province: string
  city: string
  city_alias: string | null
  upper_limit: number
  lower_limit: number
  calc_base: number
  injury_base: number | null
  corp_pension_rate: number | null
  corp_medical_rate: number | null
  corp_injury_rate: number | null
  corp_maternity_rate: number | null
  corp_unemployment_rate: number | null
  corp_disability_rate: number | null
  corp_fund_rate: number | null
  indiv_pension_rate: number | null
  indiv_medical_rate: number | null
  indiv_injury_rate: number | null
  indiv_maternity_rate: number | null
  indiv_unemployment_rate: number | null
  indiv_fund_rate: number | null
}

// State
const allData = ref<CitySocialInsurance[]>([])
const provinces = ref<string[]>([])
const allCities = ref<string[]>([])
const filters = ref({
  province: '',
  city: ''
})
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(30)

// Dialog state
const dialogVisible = ref(false)
const isEditMode = ref(false)
const formData = ref<any>({
  province: '',
  city: '',
  city_alias: null,
  upper_limit: 0,
  lower_limit: 0,
  calc_base: 0,
  injury_base: null,
  corp_pension_rate: null,
  corp_medical_rate: null,
  corp_injury_rate: null,
  corp_maternity_rate: null,
  corp_unemployment_rate: null,
  corp_disability_rate: null,
  corp_fund_rate: null,
  indiv_pension_rate: null,
  indiv_medical_rate: null,
  indiv_injury_rate: null,
  indiv_maternity_rate: null,
  indiv_unemployment_rate: null,
  indiv_fund_rate: null
})
const currentEditId = ref<number | null>(null)

// Delete dialog
const deleteDialogVisible = ref(false)
const clearDialogVisible = ref(false)
const itemToDelete = ref<CitySocialInsurance | null>(null)

const fileInput = ref<HTMLInputElement | null>(null)

// Computed
const filteredCities = computed(() => {
  if (!filters.value.province) return allCities.value
  // Filter cities based on selected province
  return allData.value
    .filter(item => item.province === filters.value.province)
    .map(item => item.city)
    .filter((v, i, a) => a.indexOf(v) === i)
})

const filteredData = computed(() => {
  let result = [...allData.value]

  if (filters.value.province) {
    result = result.filter(item => item.province === filters.value.province)
  }
  if (filters.value.city) {
    result = result.filter(item => item.city === filters.value.city)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(item =>
      item.city.toLowerCase().includes(keyword) ||
      item.province.toLowerCase().includes(keyword) ||
      (item.city_alias && item.city_alias.toLowerCase().includes(keyword))
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
    const response = await axios.get(`${API_URL}/city-social-insurance/`)
    allData.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取数据失败')
  }
}

async function fetchProvinces() {
  try {
    const response = await axios.get(`${API_URL}/city-social-insurance/provinces`)
    provinces.value = response.data
  } catch (error: any) {
    console.error('获取省份列表失败:', error)
  }
}

async function fetchCities() {
  try {
    const response = await axios.get(`${API_URL}/city-social-insurance/cities`)
    allCities.value = response.data
  } catch (error: any) {
    console.error('获取城市列表失败:', error)
  }
}

function handleFilterChange() {
  filters.value.city = ''
  currentPage.value = 1
}

function applyFilters() {
  currentPage.value = 1
}

function handleSearch() {
  currentPage.value = 1
}

function formatNumber(num: number | null): string {
  if (num === null || num === undefined) return '-'
  return num.toLocaleString('zh-CN')
}

function formatRate(rate: number | null): string {
  if (rate === null || rate === undefined) return '-'
  return (rate * 100).toFixed(1) + '%'
}

// Dialog methods
function openAddDialog() {
  isEditMode.value = false
  currentEditId.value = null
  formData.value = {
    province: '',
    city: '',
    city_alias: null,
    upper_limit: 0,
    lower_limit: 0,
    calc_base: 0,
    injury_base: null,
    corp_pension_rate: null,
    corp_medical_rate: null,
    corp_injury_rate: null,
    corp_maternity_rate: null,
    corp_unemployment_rate: null,
    corp_disability_rate: null,
    corp_fund_rate: null,
    indiv_pension_rate: null,
    indiv_medical_rate: null,
    indiv_injury_rate: null,
    indiv_maternity_rate: null,
    indiv_unemployment_rate: null,
    indiv_fund_rate: null
  }
  dialogVisible.value = true
}

function openEditDialog(item: CitySocialInsurance) {
  isEditMode.value = true
  currentEditId.value = item.id
  formData.value = { ...item }
  dialogVisible.value = true
}

async function saveData() {
  try {
    if (isEditMode.value && currentEditId.value) {
      await axios.put(`${API_URL}/city-social-insurance/${currentEditId.value}`, formData.value)
      ElMessage.success('更新成功')
    } else {
      await axios.post(`${API_URL}/city-social-insurance/`, formData.value)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await fetchData()
    await fetchProvinces()
    await fetchCities()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

function confirmDelete(item: CitySocialInsurance) {
  itemToDelete.value = item
  deleteDialogVisible.value = true
}

async function deleteData() {
  if (!itemToDelete.value) return
  try {
    await axios.delete(`${API_URL}/city-social-insurance/${itemToDelete.value.id}`)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    await fetchData()
    await fetchProvinces()
    await fetchCities()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

function confirmClear() {
  clearDialogVisible.value = true
}

async function clearData() {
  try {
    await axios.delete(`${API_URL}/city-social-insurance/clear`)
    ElMessage.success('数据已清空')
    clearDialogVisible.value = false
    await fetchData()
    await fetchProvinces()
    await fetchCities()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '清空失败')
  }
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

    await axios.post(`${API_URL}/city-social-insurance/import-excel`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })

    ElMessage.success('导入成功')
    await fetchData()
    await fetchProvinces()
    await fetchCities()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    target.value = ''
  }
}

onMounted(() => {
  fetchData()
  fetchProvinces()
  fetchCities()
})
</script>

<style scoped>
.city-social-insurance {
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

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
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
  padding: 0.75rem 0.5rem;
  text-align: left;
  border-bottom: 1px solid #1e293b;
  font-size: 0.75rem;
}

.data-table th {
  background-color: #1e293b;
  font-weight: 600;
  color: #94a3b8;
  position: sticky;
  top: 0;
  z-index: 10;
  white-space: nowrap;
}

.data-table tbody tr:hover {
  background-color: rgba(19, 91, 236, 0.05);
}

.data-table tbody tr {
  border-bottom: 1px solid #1e293b;
}

.city-name {
  font-weight: 500;
  color: #f1f5f9;
}

.city-alias {
  color: #64748b;
  font-size: 0.7rem;
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

/* Action Buttons */
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

:deep(.el-input-number .el-input__inner) {
  text-align: left;
}

.form-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #135bec;
  margin-bottom: 0.5rem;
  padding-bottom: 0.25rem;
  border-bottom: 1px solid #334155;
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
