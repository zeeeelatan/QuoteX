<template>
  <div class="job-position-management">
    <div class="country-module-tabs" role="tablist" aria-label="国家薪资模块">
      <button
        type="button"
        class="country-module-tab"
        :class="{ active: activeCountryModule === 'china' }"
        @click="activeCountryModule = 'china'"
      >
        中国大陆
      </button>
      <button
        type="button"
        class="country-module-tab"
        :class="{ active: activeCountryModule === 'korea' }"
        @click="activeCountryModule = 'korea'"
      >
        韩国
      </button>
    </div>

    <!-- Top Filter Bar -->
    <div v-if="activeCountryModule === 'china'" class="filter-bar">
      <div class="filter-left">
        <div class="filter-group">
          <label>序列</label>
          <select v-model="filters.sequenceType" @change="applyFilters">
            <option value="">全部</option>
            <option value="技术序列">技术序列</option>
            <option value="管理序列">管理序列</option>
          </select>
        </div>
        <div class="filter-group">
          <label>类别</label>
          <select v-model="filters.category" @change="applyFilters">
            <option value="">全部</option>
            <option v-for="cat in categories" :key="cat" :value="cat">{{ cat }}</option>
          </select>
        </div>
        <div class="search-box">
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索岗位名称、级别、类别..."
            @input="handleSearch"
          />
        </div>
      </div>
      <div class="filter-right actions">
        <el-button type="primary" @click="refreshData">
          <span class="material-symbols-outlined btn-icon">refresh</span>
          刷新
        </el-button>
        <el-button type="success" @click="downloadTemplate">
          <span class="material-symbols-outlined btn-icon">download</span>
          下载模板
        </el-button>
        <el-button type="warning" @click="triggerImport">
          <span class="material-symbols-outlined btn-icon">upload</span>
          导入数据
        </el-button>
        <el-button type="danger" @click="clearDialogVisible = true">
          <span class="material-symbols-outlined btn-icon">delete_sweep</span>
          清空
        </el-button>
        <input
          ref="fileInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleImport"
        />
      </div>
    </div>

    <div v-else class="filter-bar">
      <div class="filter-left">
        <div class="search-box">
          <span class="material-symbols-outlined search-icon">search</span>
          <input
            v-model="koreaSearchKeyword"
            type="text"
            placeholder="搜索城市、岗位..."
          />
        </div>
      </div>
      <div class="filter-right actions">
        <el-button type="primary" @click="fetchKoreaData">
          <span class="material-symbols-outlined btn-icon">refresh</span>
          刷新
        </el-button>
        <el-button type="success" @click="openKoreaEditDialog()">
          <span class="material-symbols-outlined btn-icon">add</span>
          新增岗位
        </el-button>
      </div>
    </div>

    <!-- Data Table -->
    <div v-if="activeCountryModule === 'china'" class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>序列</th>
            <th>类别</th>
            <th>岗位名称</th>
            <th>级别</th>
            <th class="text-right">系统最低薪资</th>
            <th class="text-right">系统最高薪资</th>
            <th class="text-center">薪资城市数</th>
            <th class="text-center">职级详情</th>
            <th class="text-center">城市薪资</th>
            <th class="text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in paginatedData" :key="item.id">
            <td>
              <span class="seq-badge" :class="item.sequence_type === '管理序列' ? 'seq-mgmt' : 'seq-tech'">
                {{ item.sequence_type }}
              </span>
            </td>
            <td>{{ item.category }}</td>
            <td class="position-cell" :title="item.position_name">{{ item.position_name }}</td>
            <td>
              <span class="level-badge" :class="getLevelClass(item)">{{ item.level_name }}</span>
            </td>
            <td class="text-right salary-text">{{ formatSalaryBound(item.system_salary_min) }}</td>
            <td class="text-right salary-text">{{ formatSalaryBound(item.system_salary_max) }}</td>
            <td class="text-center">
              <span class="salary-count" :class="{ 'salary-count-empty': !item.salary_city_count }">
                {{ item.salary_city_count }}
              </span>
            </td>
            <td class="text-center">
              <button class="content-icon-btn" @click="showDetail(item)" title="查看职级详情">
                <span class="material-symbols-outlined">visibility</span>
              </button>
            </td>
            <td class="text-center">
              <button class="content-icon-btn" @click="openSalaryDialog(item)" title="查看/编辑城市薪资">
                <span class="material-symbols-outlined">payments</span>
              </button>
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
            <td colspan="10" class="empty-state">暂无数据，请点击「导入数据」上传《IT岗位技术与管理序列分级表》</td>
          </tr>
        </tbody>
      </table>
    </div>

    <div v-else class="table-container">
      <table class="data-table">
        <thead>
          <tr>
            <th>国家/地区</th>
            <th>城市</th>
            <th>岗位名称</th>
            <th class="text-right">税前月薪（KRW）</th>
            <th>备注</th>
            <th class="text-center">状态</th>
            <th class="text-center">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="item in filteredKoreaData" :key="item.id">
            <td><span class="seq-badge seq-korea">韩国</span></td>
            <td>{{ item.city }}</td>
            <td class="position-cell" :title="item.position_name">{{ item.position_name }}</td>
            <td class="text-right salary-text">₩{{ formatNumber(item.monthly_salary_krw) }}</td>
            <td :title="item.notes || ''">{{ item.notes || '-' }}</td>
            <td class="text-center">
              <span class="status-badge" :class="item.is_active ? 'status-active' : 'status-inactive'">
                {{ item.is_active ? '启用' : '停用' }}
              </span>
            </td>
            <td class="text-center">
              <button class="action-btn edit-btn" @click="openKoreaEditDialog(item)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn delete-btn" @click="deleteKoreaSalary(item)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
          <tr v-if="filteredKoreaData.length === 0">
            <td colspan="7" class="empty-state">暂无韩国岗位薪资数据</td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Frozen Bottom Bar with Pagination -->
    <div v-if="activeCountryModule === 'china'" class="bottom-bar">
      <div class="pagination-container">
        <div class="pagination-info">
          显示第 <span>{{ filteredData.length === 0 ? 0 : (currentPage - 1) * pageSize + 1 }}</span> 到
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

    <!-- Detail Dialog -->
    <el-dialog
      v-model="detailDialogVisible"
      :title="detailTitle"
      width="720px"
      :close-on-click-modal="false"
    >
      <div class="content-viewer" v-if="detailData">
        <div v-for="section in detailSections" :key="section.label" class="detail-section">
          <h4 class="detail-section-title">{{ section.label }}</h4>
          <pre class="content-text">{{ section.value || '暂无' }}</pre>
        </div>
      </div>
      <template #footer>
        <el-button type="primary" @click="detailDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="koreaEditDialogVisible"
      :title="koreaEditId == null ? '新增韩国岗位薪资' : '编辑韩国岗位薪资'"
      width="560px"
      :close-on-click-modal="false"
    >
      <el-form :model="koreaFormData" label-width="130px">
        <el-form-item label="城市">
          <el-input v-model="koreaFormData.city" placeholder="如：首尔" />
        </el-form-item>
        <el-form-item label="岗位名称">
          <el-input v-model="koreaFormData.position_name" placeholder="如：桌面运维（3年+）" />
        </el-form-item>
        <el-form-item label="税前月薪（KRW）">
          <el-input-number
            v-model="koreaFormData.monthly_salary_krw"
            :min="1"
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="状态">
          <el-switch v-model="koreaFormData.is_active" active-text="启用" inactive-text="停用" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="koreaFormData.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="koreaEditDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveKoreaSalary">确定</el-button>
      </template>
    </el-dialog>

    <!-- Edit Dialog -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑岗位职级"
      width="720px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="140px">
        <el-form-item label="序列类型">
          <el-select v-model="formData.sequence_type" style="width: 100%">
            <el-option label="技术序列" value="技术序列" />
            <el-option label="管理序列" value="管理序列" />
          </el-select>
        </el-form-item>
        <el-form-item label="岗位类别/方向">
          <el-input v-model="formData.category" placeholder="如：研发类 / 研发管理" />
        </el-form-item>
        <el-form-item label="岗位名称">
          <el-input v-model="formData.position_name" placeholder="如：前端开发工程师" />
        </el-form-item>
        <el-form-item label="级别名称">
          <el-input v-model="formData.level_name" placeholder="如：初级 (Junior/P1-P2)" />
        </el-form-item>
        <el-form-item label="级别排序">
          <el-input-number v-model="formData.level_rank" :min="1" :max="10" style="width: 100%" />
        </el-form-item>
        <el-form-item label="系统最低薪资">
          <el-input-number
            v-model="formData.system_salary_min"
            :min="0"
            :max="formData.system_salary_max ?? undefined"
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="系统最高薪资">
          <el-input-number
            v-model="formData.system_salary_max"
            :min="formData.system_salary_min ?? 0"
            :precision="0"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="级别核心要求">
          <el-input v-model="formData.core_requirements" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="适用认证参考">
          <el-input v-model="formData.certifications" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="工作内容">
          <el-input v-model="formData.work_content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="工作产出/交付物">
          <el-input v-model="formData.deliverables" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="KPI考核点">
          <el-input v-model="formData.kpi_standards" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveData">确定</el-button>
      </template>
    </el-dialog>

    <!-- Salary Dialog -->
    <el-dialog
      v-model="salaryDialogVisible"
      :title="salaryDialogTitle"
      width="640px"
      :close-on-click-modal="false"
    >
      <div class="salary-toolbar">
        <div class="search-box salary-search">
          <span class="material-symbols-outlined search-icon">search</span>
          <input v-model="salarySearchKeyword" type="text" placeholder="搜索城市..." />
        </div>
        <div class="salary-add">
          <el-input v-model="newSalaryCity" placeholder="城市（如：西安市）" style="width: 160px" />
          <el-input-number v-model="newSalaryValue" :min="0" :precision="0" placeholder="月薪" style="width: 140px" />
          <el-button type="primary" @click="addSalary">新增</el-button>
        </div>
      </div>
      <div class="salary-table-container">
        <table class="data-table salary-table">
          <thead>
            <tr>
              <th>省份</th>
              <th>城市</th>
              <th class="text-right">税前月薪（元）</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in filteredSalaries" :key="item.id">
              <td>{{ item.province || '-' }}</td>
              <td>{{ item.city }}</td>
              <td class="text-right">
                <template v-if="editingSalaryId === item.id">
                  <el-input-number
                    v-model="editingSalaryValue"
                    :min="0"
                    :precision="0"
                    size="small"
                    style="width: 130px"
                  />
                </template>
                <span v-else class="salary-text">¥{{ formatNumber(item.salary) }}</span>
              </td>
              <td class="text-center">
                <template v-if="editingSalaryId === item.id">
                  <button class="action-btn edit-btn" @click="saveSalaryEdit(item)" title="保存">
                    <span class="material-symbols-outlined">check</span>
                  </button>
                  <button class="action-btn delete-btn" @click="editingSalaryId = null" title="取消">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </template>
                <template v-else>
                  <button class="action-btn edit-btn" @click="startSalaryEdit(item)" title="编辑">
                    <span class="material-symbols-outlined">edit</span>
                  </button>
                  <button class="action-btn delete-btn" @click="deleteSalary(item)" title="删除">
                    <span class="material-symbols-outlined">delete</span>
                  </button>
                </template>
              </td>
            </tr>
            <tr v-if="filteredSalaries.length === 0">
              <td colspan="4" class="empty-state">暂无城市薪资数据</td>
            </tr>
          </tbody>
        </table>
      </div>
      <template #footer>
        <el-button type="primary" @click="salaryDialogVisible = false">关闭</el-button>
      </template>
    </el-dialog>

    <!-- Delete Confirmation Dialog -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="420px"
      :close-on-click-modal="false"
    >
      <p>确定要删除「{{ itemToDelete?.position_name }} - {{ itemToDelete?.level_name }}」吗？该岗位的所有城市薪资数据将一并删除。</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="deleteData">确定</el-button>
      </template>
    </el-dialog>

    <!-- Clear Confirmation Dialog -->
    <el-dialog
      v-model="clearDialogVisible"
      title="确认清空"
      width="420px"
      :close-on-click-modal="false"
    >
      <p>确定要清空全部岗位职级及城市薪资数据吗？此操作不可恢复。</p>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="clearAll">确定清空</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

interface JobPositionItem {
  id: number
  sequence_type: string
  category: string
  position_name: string
  level_name: string
  level_rank: number
  system_salary_max: number | null
  system_salary_min: number | null
  salary_city_count: number
}

interface JobPositionDetail extends JobPositionItem {
  core_requirements: string | null
  certifications: string | null
  work_content: string | null
  deliverables: string | null
  kpi_standards: string | null
}

interface SalaryItem {
  id: number
  province: string | null
  city: string
  salary: number
}

interface KoreaJobSalaryItem {
  id: number
  city: string
  position_name: string
  monthly_salary_krw: number
  notes: string | null
  is_active: boolean
}

// State
const activeCountryModule = ref<'china' | 'korea'>('china')
const allData = ref<JobPositionItem[]>([])
const categories = ref<string[]>([])
const filters = ref({ sequenceType: '', category: '' })
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = ref(15)

const fileInput = ref<HTMLInputElement | null>(null)

const koreaData = ref<KoreaJobSalaryItem[]>([])
const koreaSearchKeyword = ref('')
const koreaEditDialogVisible = ref(false)
const koreaEditId = ref<number | null>(null)
const koreaFormData = ref({
  city: '首尔',
  position_name: '',
  monthly_salary_krw: 5640000,
  notes: '',
  is_active: true
})

const filteredKoreaData = computed(() => {
  const keyword = koreaSearchKeyword.value.trim().toLowerCase()
  if (!keyword) return koreaData.value
  return koreaData.value.filter(item =>
    item.city.toLowerCase().includes(keyword) ||
    item.position_name.toLowerCase().includes(keyword)
  )
})

// Detail dialog
const detailDialogVisible = ref(false)
const detailData = ref<JobPositionDetail | null>(null)
const detailTitle = computed(() =>
  detailData.value ? `${detailData.value.position_name} - ${detailData.value.level_name}` : '职级详情'
)
const detailSections = computed(() => {
  if (!detailData.value) return []
  return [
    { label: '级别核心要求（含建议认证）', value: detailData.value.core_requirements },
    { label: '适用认证参考', value: detailData.value.certifications },
    { label: '工作内容', value: detailData.value.work_content },
    { label: '工作产出/交付物', value: detailData.value.deliverables },
    { label: 'KPI考核点及标准参考值', value: detailData.value.kpi_standards }
  ]
})

// Edit dialog
const editDialogVisible = ref(false)
const formData = ref<Partial<JobPositionDetail>>({})
const currentEditId = ref<number | null>(null)

// Salary dialog
const salaryDialogVisible = ref(false)
const salaryPosition = ref<JobPositionItem | null>(null)
const salaries = ref<SalaryItem[]>([])
const salarySearchKeyword = ref('')
const editingSalaryId = ref<number | null>(null)
const editingSalaryValue = ref(0)
const newSalaryCity = ref('')
const newSalaryValue = ref<number | undefined>(undefined)
const salaryDialogTitle = computed(() =>
  salaryPosition.value
    ? `城市薪资 - ${salaryPosition.value.position_name} - ${salaryPosition.value.level_name}`
    : '城市薪资'
)
const filteredSalaries = computed(() => {
  if (!salarySearchKeyword.value) return salaries.value
  const kw = salarySearchKeyword.value.trim()
  return salaries.value.filter(
    s => s.city.includes(kw) || (s.province && s.province.includes(kw))
  )
})

// Delete / clear dialogs
const deleteDialogVisible = ref(false)
const itemToDelete = ref<JobPositionItem | null>(null)
const clearDialogVisible = ref(false)

// Computed list
const filteredData = computed(() => {
  let result = [...allData.value]
  if (filters.value.sequenceType) {
    result = result.filter(item => item.sequence_type === filters.value.sequenceType)
  }
  if (filters.value.category) {
    result = result.filter(item => item.category === filters.value.category)
  }
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(item =>
      item.position_name.toLowerCase().includes(keyword) ||
      item.level_name.toLowerCase().includes(keyword) ||
      item.category.toLowerCase().includes(keyword)
    )
  }
  return result
})

const totalPages = computed(() => Math.ceil(filteredData.value.length / pageSize.value))

const paginatedData = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  return filteredData.value.slice(start, start + pageSize.value)
})

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 7
  let startPage = Math.max(1, currentPage.value - Math.floor(maxVisible / 2))
  const endPage = Math.min(totalPages.value, startPage + maxVisible - 1)
  if (endPage - startPage + 1 < maxVisible) {
    startPage = Math.max(1, endPage - maxVisible + 1)
  }
  for (let i = startPage; i <= endPage; i++) pages.push(i)
  return pages
})

// Methods
async function fetchData() {
  try {
    const response = await axios.get(`${API_URL}/job-positions/`)
    allData.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取数据失败')
  }
}

async function fetchCategories() {
  try {
    const response = await axios.get(`${API_URL}/job-positions/categories/list`)
    categories.value = response.data.categories || []
  } catch {
    // 类别筛选失败不阻塞主流程
  }
}

async function fetchKoreaData() {
  try {
    const response = await axios.get(`${API_URL}/korea-job-salaries/`)
    koreaData.value = response.data.map((item: any) => ({
      ...item,
      monthly_salary_krw: Number(item.monthly_salary_krw)
    }))
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取韩国岗位薪资失败')
  }
}

function openKoreaEditDialog(item?: KoreaJobSalaryItem) {
  koreaEditId.value = item?.id ?? null
  koreaFormData.value = item
    ? {
        city: item.city,
        position_name: item.position_name,
        monthly_salary_krw: Number(item.monthly_salary_krw),
        notes: item.notes || '',
        is_active: item.is_active
      }
    : {
        city: '首尔',
        position_name: '',
        monthly_salary_krw: 5640000,
        notes: '',
        is_active: true
      }
  koreaEditDialogVisible.value = true
}

async function saveKoreaSalary() {
  const payload = {
    ...koreaFormData.value,
    city: koreaFormData.value.city.trim(),
    position_name: koreaFormData.value.position_name.trim()
  }
  if (!payload.city || !payload.position_name || payload.monthly_salary_krw <= 0) {
    ElMessage.warning('请完整填写城市、岗位名称和税前月薪')
    return
  }

  try {
    if (koreaEditId.value == null) {
      await axios.post(`${API_URL}/korea-job-salaries/`, payload)
      ElMessage.success('韩国岗位薪资已新增')
    } else {
      await axios.put(`${API_URL}/korea-job-salaries/${koreaEditId.value}`, payload)
      ElMessage.success('韩国岗位薪资已更新')
    }
    koreaEditDialogVisible.value = false
    await fetchKoreaData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  }
}

async function deleteKoreaSalary(item: KoreaJobSalaryItem) {
  try {
    await axios.delete(`${API_URL}/korea-job-salaries/${item.id}`)
    ElMessage.success('韩国岗位薪资已删除')
    await fetchKoreaData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

async function refreshData() {
  await Promise.all([fetchData(), fetchCategories()])
  ElMessage.success('数据已刷新')
}

function applyFilters() {
  currentPage.value = 1
}

function handleSearch() {
  currentPage.value = 1
}

function getLevelClass(item: JobPositionItem): string {
  if (item.sequence_type === '管理序列') {
    const map: Record<number, string> = { 1: 'level-lead', 2: 'level-manager', 3: 'level-director' }
    return map[item.level_rank] || 'level-default'
  }
  const map: Record<number, string> = {
    1: 'level-junior', 2: 'level-mid', 3: 'level-senior', 4: 'level-expert'
  }
  return map[item.level_rank] || 'level-default'
}

function formatNumber(num: number): string {
  return Number(num).toLocaleString('zh-CN')
}

function formatSalaryBound(value: number | null): string {
  return value == null ? '-' : `¥${formatNumber(value)}`
}

// Detail
async function showDetail(item: JobPositionItem) {
  try {
    const response = await axios.get(`${API_URL}/job-positions/${item.id}`)
    detailData.value = response.data
    detailDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取详情失败')
  }
}

// Edit
async function openEditDialog(item: JobPositionItem) {
  try {
    const response = await axios.get(`${API_URL}/job-positions/${item.id}`)
    formData.value = { ...response.data }
    currentEditId.value = item.id
    editDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取数据失败')
  }
}

async function saveData() {
  if (!currentEditId.value) return
  const minSalary = formData.value.system_salary_min
  const maxSalary = formData.value.system_salary_max
  if (minSalary != null && maxSalary != null && minSalary > maxSalary) {
    ElMessage.warning('系统最低薪资不能大于系统最高薪资')
    return
  }
  try {
    await axios.put(`${API_URL}/job-positions/${currentEditId.value}`, formData.value)
    ElMessage.success('更新成功')
    editDialogVisible.value = false
    await fetchData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '操作失败')
  }
}

// Delete
function confirmDelete(item: JobPositionItem) {
  itemToDelete.value = item
  deleteDialogVisible.value = true
}

async function deleteData() {
  if (!itemToDelete.value) return
  try {
    await axios.delete(`${API_URL}/job-positions/${itemToDelete.value.id}`)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    await Promise.all([fetchData(), fetchCategories()])
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

async function clearAll() {
  try {
    await axios.delete(`${API_URL}/job-positions/clear`)
    ElMessage.success('已清空全部数据')
    clearDialogVisible.value = false
    await Promise.all([fetchData(), fetchCategories()])
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '清空失败')
  }
}

// Salary dialog
async function openSalaryDialog(item: JobPositionItem) {
  salaryPosition.value = item
  salarySearchKeyword.value = ''
  editingSalaryId.value = null
  newSalaryCity.value = ''
  newSalaryValue.value = undefined
  try {
    const response = await axios.get(`${API_URL}/job-positions/${item.id}/salaries`)
    salaries.value = response.data
    salaryDialogVisible.value = true
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '获取城市薪资失败')
  }
}

function startSalaryEdit(item: SalaryItem) {
  editingSalaryId.value = item.id
  editingSalaryValue.value = Number(item.salary)
}

async function saveSalaryEdit(item: SalaryItem) {
  if (!salaryPosition.value) return
  try {
    await axios.put(`${API_URL}/job-positions/${salaryPosition.value.id}/salary`, {
      city: item.city,
      salary: editingSalaryValue.value,
      province: item.province
    })
    ElMessage.success('薪资已更新')
    editingSalaryId.value = null
    const response = await axios.get(`${API_URL}/job-positions/${salaryPosition.value.id}/salaries`)
    salaries.value = response.data
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '更新失败')
  }
}

async function addSalary() {
  if (!salaryPosition.value) return
  const city = newSalaryCity.value.trim()
  if (!city || newSalaryValue.value == null) {
    ElMessage.warning('请填写城市和月薪')
    return
  }
  try {
    await axios.put(`${API_URL}/job-positions/${salaryPosition.value.id}/salary`, {
      city,
      salary: newSalaryValue.value
    })
    ElMessage.success('已保存')
    newSalaryCity.value = ''
    newSalaryValue.value = undefined
    const response = await axios.get(`${API_URL}/job-positions/${salaryPosition.value.id}/salaries`)
    salaries.value = response.data
    await fetchData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '保存失败')
  }
}

async function deleteSalary(item: SalaryItem) {
  if (!salaryPosition.value) return
  try {
    await axios.delete(`${API_URL}/job-positions/${salaryPosition.value.id}/salary`, {
      params: { city: item.city }
    })
    ElMessage.success('已删除')
    salaries.value = salaries.value.filter(s => s.id !== item.id)
    await fetchData()
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '删除失败')
  }
}

// Import / template
function triggerImport() {
  fileInput.value?.click()
}

async function handleImport(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  try {
    ElMessage.info('正在导入，将清空原有数据...')
    const uploadForm = new FormData()
    uploadForm.append('file', file)
    const response = await axios.post(`${API_URL}/job-positions/import-excel`, uploadForm, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    ElMessage.success(response.data.message || '导入成功')
    await Promise.all([fetchData(), fetchCategories()])
  } catch (error: any) {
    ElMessage.error(error.response?.data?.detail || '导入失败')
  } finally {
    target.value = ''
  }
}

async function downloadTemplate() {
  const XLSX = await import('xlsx')
  const wb = XLSX.utils.book_new()

  const baseHeaders = [
    '序号', '岗位类别', '岗位名称', '技术级别',
    '级别核心要求(含建议认证)', '适用认证参考', '工作内容',
    '工作产出/交付物', 'KPI考核点及标准参考值'
  ]
  const cityProvinces = ['北京', '上海', '广东', '四川']
  const cityNames = ['北京市', '上海市', '广州市', '成都市']
  const boundHeaders = ['系统取值最大值', '系统取值最小值']

  const techSheet = XLSX.utils.aoa_to_sheet([
    ['技术序列 —— 各岗位分级详情(要求/认证/内容/产出/KPI)；城市薪资列可按需增删，城市名需与城市社保表一致'],
    [...Array(9).fill(null), ...cityProvinces, null, null],
    [...baseHeaders, ...cityNames, ...boundHeaders],
    [1, '研发类', '前端开发工程师', '初级 (Junior/P1-P2)', '本科及以上，1-2年经验', '无强制认证', '页面开发与Bug修复', '可上线的页面/组件源代码', '需求交付准时率≥90%', 16000, 16000, 12000, 9500, 19200, 5200]
  ])
  XLSX.utils.book_append_sheet(wb, techSheet, '技术序列分级详情')

  const mgmtHeaders = [...baseHeaders]
  mgmtHeaders[1] = '管理方向'
  mgmtHeaders[3] = '管理级别'
  const mgmtSheet = XLSX.utils.aoa_to_sheet([
    ['管理序列 —— 各管理方向分级详情'],
    [...Array(9).fill(null), ...cityProvinces, null, null],
    [...mgmtHeaders, ...cityNames, ...boundHeaders],
    [1, '研发管理', '研发经理/技术总监', '初级管理 (团队负责人/Team Lead)', '5年以上研发经验', '建议PMP', '团队任务分配与进度把控', '团队周报/月报', '团队任务按期交付率≥90%', 35000, 35000, 28000, 21000, 42000, 11600]
  ])
  XLSX.utils.book_append_sheet(wb, mgmtSheet, '管理序列分级详情')

  XLSX.writeFile(wb, 'IT岗位技术与管理序列分级表模板.xlsx')
}

onMounted(() => {
  fetchData()
  fetchCategories()
  fetchKoreaData()
})
</script>

<style scoped>
.job-position-management {
  height: 100%;
  display: flex;
  flex-direction: column;
  background-color: #0f172a;
  color: #e2e8f0;
}

.country-module-tabs {
  display: flex;
  gap: 4px;
  padding: 12px 16px 0;
  background: #1e293b;
  border-bottom: 1px solid #334155;
}

.country-module-tab {
  min-width: 112px;
  padding: 10px 16px;
  border: 0;
  border-bottom: 3px solid transparent;
  background: transparent;
  color: #94a3b8;
  font-size: 0.9rem;
  font-weight: 600;
  cursor: pointer;
}

.country-module-tab:hover {
  color: #e2e8f0;
}

.country-module-tab.active {
  border-bottom-color: #3b82f6;
  color: #ffffff;
}

.seq-korea {
  background: rgba(16, 185, 129, 0.15);
  color: #6ee7b7;
}

.status-badge {
  display: inline-flex;
  min-width: 48px;
  justify-content: center;
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 0.75rem;
}

.status-active {
  background: rgba(34, 197, 94, 0.15);
  color: #86efac;
}

.status-inactive {
  background: rgba(148, 163, 184, 0.15);
  color: #cbd5e1;
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

.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.actions :deep(.el-button) {
  margin-left: 0;
}

.btn-icon {
  font-size: 1.125rem;
  margin-right: 0.25rem;
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

.position-cell {
  max-width: 260px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Badges */
.seq-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.seq-tech {
  background-color: rgba(19, 91, 236, 0.15);
  color: #60a5fa;
}

.seq-mgmt {
  background-color: rgba(234, 179, 8, 0.15);
  color: #eab308;
}

.level-badge {
  display: inline-block;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  max-width: 220px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  vertical-align: middle;
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

.level-director {
  background-color: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.level-default {
  background-color: rgba(100, 116, 139, 0.2);
  color: #64748b;
}

.salary-count {
  font-weight: 600;
  color: #22c55e;
}

.salary-count-empty {
  color: #64748b;
}

/* Icon buttons */
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

/* Salary dialog */
.salary-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.salary-search input {
  width: 12rem;
}

.salary-add {
  display: flex;
  gap: 8px;
  align-items: center;
}

.salary-table-container {
  max-height: 420px;
  overflow-y: auto;
}

.salary-text {
  font-weight: 600;
  color: #22c55e;
}

/* Detail dialog */
.content-viewer {
  max-height: 480px;
  overflow-y: auto;
}

.detail-section {
  margin-bottom: 1rem;
}

.detail-section-title {
  margin: 0 0 0.375rem;
  font-size: 0.8125rem;
  color: #94a3b8;
  font-weight: 600;
}

.content-text {
  white-space: pre-wrap;
  word-wrap: break-word;
  background-color: #0f172a;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: #cbd5e1;
  font-size: 0.875rem;
  line-height: 1.6;
  margin: 0;
  font-family: inherit;
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
