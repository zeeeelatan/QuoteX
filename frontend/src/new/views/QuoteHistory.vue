<template>
  <div class="quote-history-page">
    <!-- Header -->
    <header class="page-header">
      <div class="header-content">
        <div class="header-left">
          <div class="breadcrumb">
            <a @click="navigateToHome" class="breadcrumb-link">首页</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <span class="breadcrumb-current">历史记录</span>
          </div>
          <h2 class="page-title">报价单生成记录</h2>
          <p class="page-description">查询过往所有的自动报价记录详情与数据节点</p>
        </div>
        <div class="header-actions">
          <button @click="refreshList" class="action-btn secondary-btn">
            <span class="material-symbols-outlined">refresh</span>
            刷新列表
          </button>
          <button @click="exportRecords" class="action-btn primary-btn">
            <span class="material-symbols-outlined">download</span>
            导出记录 (.csv)
          </button>
        </div>
      </div>

      <!-- Filters -->
      <div class="filters-row">
        <div class="filter-group search-group">
          <div class="search-input-wrapper">
            <span class="material-symbols-outlined search-icon">search</span>
            <input
              v-model="searchKeyword"
              @keyup.enter="handleSearch"
              type="text"
              class="search-input"
              placeholder="输入文件名称、ID或用户姓名..."
            />
          </div>
        </div>
        <div class="filter-group">
          <select v-model="dateRange" class="filter-select">
            <option value="7">最近 7 天</option>
            <option value="30">最近 30 天</option>
            <option value="90">最近 3 个月</option>
            <option value="all">全部时间</option>
          </select>
        </div>
        <div class="filter-group">
          <select v-model="statusFilter" class="filter-select">
            <option value="all">全部状态</option>
            <option value="completed">已生成</option>
            <option value="processing">处理中</option>
            <option value="failed">生成失败</option>
          </select>
        </div>
        <button @click="handleSearch" class="query-btn">查询</button>
      </div>
    </header>

    <!-- Table -->
    <main class="main-content">
      <div class="table-container">
        <div class="table-wrapper">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-id">ID</th>
                <th>导入文件名称</th>
                <th>用户</th>
                <th class="col-sortable" @click="toggleSort">
                  生成时间
                  <span class="material-symbols-outlined sort-icon">swap_vert</span>
                </th>
                <th class="col-amount">报价总额 (CNY)</th>
                <th class="col-status">状态</th>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr
                v-for="item in historyList"
                :key="item.id"
                class="table-row"
                :class="{ 'row-processing': item.status === 'processing' }"
              >
                <td class="col-id">{{ '#' + item.id }}</td>
                <td class="col-file">
                  <div class="file-info">
                    <div class="file-icon" :class="getFileIconClass(item.file_name)">
                      <span class="material-symbols-outlined">{{ getFileIcon(item.file_name) }}</span>
                    </div>
                    <span class="file-name" :title="item.file_name">{{ truncateFileName(item.file_name) }}</span>
                  </div>
                </td>
                <td class="col-user">
                  <div class="user-display">
                    <div class="user-avatar-small">{{ getUserInitials(item.user_name) }}</div>
                    <span>{{ item.user_name }}</span>
                  </div>
                </td>
                <td class="col-time">{{ formatDateTime(item.created_at) }}</td>
                <td class="col-amount">
                  <span v-if="item.total_amount" class="amount-value">¥ {{ formatAmount(item.total_amount) }}</span>
                  <span v-else class="amount-empty">-</span>
                </td>
                <td class="col-status">
                  <span class="status-badge" :class="'status-' + item.status">
                    <span v-if="item.status === 'completed'" class="status-dot"></span>
                    <span v-if="item.status === 'processing'" class="status-dot animate-pulse"></span>
                    <span v-if="item.status === 'failed'" class="material-symbols-outlined status-error">error</span>
                    {{ getStatusText(item.status) }}
                  </span>
                </td>
                <td class="col-actions">
                  <button
                    v-if="item.status === 'completed'"
                    @click="viewDetail(item)"
                    class="detail-btn"
                  >
                    查看详情
                  </button>
                  <button
                    v-else-if="item.status === 'processing'"
                    class="detail-btn disabled"
                    disabled
                  >
                    稍后查看
                  </button>
                  <button
                    v-else
                    @click="retryQuote(item)"
                    class="retry-btn"
                  >
                    重试
                  </button>
                </td>
              </tr>
              <tr v-if="historyList.length === 0" class="empty-row">
                <td colspan="7" class="empty-cell">
                  <div class="empty-state">
                    <span class="material-symbols-outlined empty-icon">folder_open</span>
                    <p>暂无历史记录</p>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div class="pagination">
          <div class="pagination-info">
            显示 <span class="page-current">{{ startIndex + 1 }}</span> 到
            <span class="page-current">{{ endIndex }}</span> 条，
            共 <span class="page-total">{{ totalCount }}</span> 条记录
          </div>
          <div class="pagination-controls">
            <button
              @click="prevPage"
              :disabled="currentPage === 1"
              class="page-btn"
            >
              <span class="material-symbols-outlined">chevron_left</span>
            </button>
            <button
              v-for="page in visiblePages"
              :key="page"
              @click="goToPage(page)"
              class="page-num"
              :class="{ active: page === currentPage }"
            >
              {{ page }}
            </button>
            <button
              @click="nextPage"
              :disabled="currentPage === totalPages"
              class="page-btn"
            >
              <span class="material-symbols-outlined">chevron_right</span>
            </button>
          </div>
        </div>
      </div>
    </main>

    <!-- 全屏历史详情查看器 -->
    <HistoryDetailViewer
      v-if="showDetailModal && currentDetail"
      :history-data="currentDetail"
      @close="closeDetailModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import api from '../../api/index'
import HistoryDetailViewer from '../components/HistoryDetailViewer.vue'

// 定义 emit
const emit = defineEmits<{
  'go-home': []
}>()


// State
const historyList = ref<any[]>([])
const totalCount = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const searchKeyword = ref('')
const dateRange = ref('all')
const statusFilter = ref('all')
const sortDesc = ref(true)

// Modal
const showDetailModal = ref(false)
const currentDetail = ref<any>(null)
const activeTab = ref('import')

// Data tabs
const dataTabs = [
  { key: 'import', label: '导入数据', icon: 'upload_file' },
  { key: 'match', label: '数据匹配', icon: 'link' },
  { key: 'adjust', label: '价格调整', icon: 'tune' },
  { key: 'quote', label: '生成报价', icon: 'receipt' }
]

// Computed
const totalPages = computed(() => Math.ceil(totalCount.value / pageSize.value))
const startIndex = computed(() => (currentPage.value - 1) * pageSize.value)
const endIndex = computed(() => Math.min(currentPage.value * pageSize.value, totalCount.value))

const visiblePages = computed(() => {
  const pages: number[] = []
  const maxVisible = 5
  let start = Math.max(1, currentPage.value - 2)
  let end = Math.min(totalPages.value, start + maxVisible - 1)

  if (end - start < maxVisible - 1) {
    start = Math.max(1, end - maxVisible + 1)
  }

  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  return pages
})

// Methods
const navigateToHome = () => {
  emit('go-home')
}

const refreshList = async () => {
  await fetchHistory()
}

const fetchHistory = async () => {
  try {
    const params: any = {
      skip: (currentPage.value - 1) * pageSize.value,
      limit: pageSize.value
    }

    if (statusFilter.value !== 'all') {
      params.status = statusFilter.value
    }

    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }

    const response = await api.get('/quote-history/', { params })
    historyList.value = response

    // Fetch total count
    const countParams: any = {}
    if (statusFilter.value !== 'all') countParams.status = statusFilter.value
    if (searchKeyword.value) countParams.search = searchKeyword.value

    const countResponse = await api.get('/quote-history/count', { params: countParams })
    totalCount.value = countResponse.total
  } catch (error) {
    console.error('Failed to fetch history:', error)
  }
}

const handleSearch = () => {
  currentPage.value = 1
  fetchHistory()
}

const toggleSort = () => {
  sortDesc.value = !sortDesc.value
  fetchHistory()
}

const prevPage = () => {
  if (currentPage.value > 1) {
    currentPage.value--
    fetchHistory()
  }
}

const nextPage = () => {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    fetchHistory()
  }
}

const goToPage = (page: number) => {
  currentPage.value = page
  fetchHistory()
}

const viewDetail = async (item: any) => {
  try {
    const response = await api.get(`/quote-history/${item.id}`)
    currentDetail.value = response
    activeTab.value = 'import'
    showDetailModal.value = true
  } catch (error) {
    console.error('Failed to fetch detail:', error)
  }
}

const closeDetailModal = () => {
  showDetailModal.value = false
  currentDetail.value = null
}

const retryQuote = (item: any) => {
  // TODO: Implement retry logic
  console.log('Retry quote:', item.id)
}

const exportRecords = () => {
  // TODO: Implement export
  console.log('Export records')
}

// Helper functions
const getNodeData = (key: string) => {
  if (!currentDetail.value) return null

  switch (key) {
    case 'import':
      return currentDetail.value.import_data
    case 'match':
      return currentDetail.value.match_data
    case 'adjust':
      return currentDetail.value.price_adjust_data
    case 'quote':
      return currentDetail.value.quote_data
    default:
      return null
  }
}

const getQuoteHeaders = () => {
  const converted = getNodeData('quote')?.converted
  if (converted && converted.length > 0) {
    return Object.keys(converted[0]).slice(0, 8)
  }
  return []
}

const getFileIcon = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  switch (ext) {
    case 'xlsx':
    case 'xls':
      return 'table_chart'
    case 'csv':
      return 'description'
    case 'zip':
      return 'folder_zip'
    default:
      return 'description'
  }
}

const getFileIconClass = (fileName: string) => {
  const ext = fileName.split('.').pop()?.toLowerCase()
  switch (ext) {
    case 'xlsx':
    case 'xls':
      return 'icon-excel'
    case 'csv':
      return 'icon-csv'
    case 'zip':
      return 'icon-zip'
    default:
      return 'icon-default'
  }
}

const getUserInitials = (userName: string) => {
  const name = userName || ''
  if (name.length <= 2) return name.toUpperCase()
  // For Chinese names, take last character; for English, take first letters
  if (/[\u4e00-\u9fa5]/.test(name)) {
    return name.slice(-2).toUpperCase()
  }
  return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2)
}

const truncateFileName = (fileName: string) => {
  if (fileName.length <= 30) return fileName
  return fileName.slice(0, 27) + '...'
}

const formatDateTime = (dateStr: string) => {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

const formatAmount = (amount: number) => {
  return amount.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

const getStatusText = (status: string) => {
  switch (status) {
    case 'completed': return '已生成'
    case 'processing': return '处理中'
    case 'failed': return '生成失败'
    default: return status
  }
}

const getMatchRateClass = (rate: number) => {
  if (rate >= 70) return 'match-high'
  if (rate >= 50) return 'match-mid'
  return 'match-low'
}

// Lifecycle
onMounted(() => {
  fetchHistory()
})
</script>

<style scoped>
.quote-history-page {
  min-height: 100vh;
  background-color: #101622;
  display: flex;
  flex-direction: column;
}

/* Header */
.page-header {
  padding: 32px;
  border-bottom: 1px solid #232f48;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 24px;
}

.header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 8px;
}

.breadcrumb-link {
  color: #92a4c9;
  font-size: 12px;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.breadcrumb-link:hover {
  color: #fff;
}

.breadcrumb-current {
  color: #135bec;
  font-size: 12px;
  font-weight: 500;
}

.material-symbols-outlined {
  font-size: 12px;
}

.page-title {
  font-size: 28px;
  font-weight: 700;
  color: #fff;
  line-height: 1.2;
}

.page-description {
  color: #92a4c9;
  font-size: 16px;
}

.header-actions {
  display: flex;
  gap: 12px;
}

.action-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.secondary-btn {
  background-color: #111722;
  border: 1px solid #232f48;
  color: #fff;
}

.secondary-btn:hover {
  background-color: #1e2736;
  border-color: #135bec;
}

.primary-btn {
  background-color: #135bec;
  color: #fff;
}

.primary-btn:hover {
  background-color: #1d64f2;
}

/* Filters */
.filters-row {
  display: flex;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.search-group {
  flex: 1;
  min-width: 280px;
  max-width: 400px;
}

.search-input-wrapper {
  display: flex;
  align-items: center;
  height: 40px;
  background-color: #111722;
  border: 1px solid #232f48;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.2s;
}

.search-input-wrapper:focus-within {
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.search-icon {
  color: #92a4c9;
  padding: 0 12px;
  font-size: 18px;
}

.search-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 14px;
  outline: none;
}

.search-input::placeholder {
  color: rgba(146, 164, 201, 0.5);
}

.filter-select {
  appearance: none;
  width: 180px;
  height: 40px;
  padding: 0 36px 0 12px;
  background-color: #111722;
  border: 1px solid #232f48;
  border-radius: 8px;
  color: #fff;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2392a4c9'%3E%3Cpath d='M7 10l5 5 5-5z'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 12px center;
  background-size: 20px;
}

.filter-select:hover {
  background-color: #1e2736;
}

.query-btn {
  height: 40px;
  padding: 0 24px;
  background-color: #111722;
  border: 1px solid #232f48;
  border-radius: 8px;
  color: #92a4c9;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.query-btn:hover {
  border-color: #135bec;
  color: #135bec;
}

/* Main Content */
.main-content {
  flex: 1;
  padding: 0 32px 32px;
  overflow-y: auto;
}

.table-container {
  background-color: #111722;
  border: 1px solid #232f48;
  border-radius: 12px;
  overflow: hidden;
}

.table-wrapper {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th {
  padding: 16px 24px;
  text-align: left;
  font-size: 12px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: #92a4c9;
  background-color: #1a212e;
  border-bottom: 1px solid #232f48;
}

.data-table th.col-id {
  width: 80px;
}

.data-table th.col-sortable {
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 4px;
}

.data-table th.col-sortable:hover {
  color: #fff;
}

.sort-icon {
  font-size: 16px;
}

.data-table th.col-amount,
.data-table td.col-amount {
  text-align: right;
}

.data-table th.col-status,
.data-table td.col-status {
  text-align: center;
}

.data-table th.col-actions,
.data-table td.col-actions {
  text-align: right;
}

.data-table td {
  padding: 16px 24px;
  border-bottom: 1px solid #232f48;
  color: #fff;
  font-size: 14px;
}

.table-row {
  transition: background-color 0.2s;
}

.table-row:hover {
  background-color: #1e2736;
}

.row-processing {
  background-color: rgba(19, 91, 236, 0.05);
}

/* File Info */
.file-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.file-icon {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  background-color: #232f48;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon.icon-excel {
  color: #22c55e;
}

.file-icon.icon-csv {
  color: #3b82f6;
}

.file-icon.icon-zip {
  color: #eab308;
}

.file-icon span {
  font-size: 20px;
}

.file-name {
  max-width: 240px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* User Display */
.user-display {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-avatar-small {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: rgba(19, 91, 236, 0.2);
  color: #60a5fa;
  font-size: 10px;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
}

/* Status Badge */
.status-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  border-radius: 9999px;
  font-size: 12px;
  font-weight: 500;
}

.status-completed {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.status-processing {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
  border: 1px solid rgba(19, 91, 236, 0.2);
}

.status-failed {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: currentColor;
}

.status-error {
  font-size: 14px;
}

.animate-pulse {
  animation: pulse 1.5s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

/* Buttons */
.detail-btn {
  padding: 6px 12px;
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.detail-btn:hover {
  background-color: #135bec;
  color: #fff;
}

.detail-btn.disabled {
  background-color: #111722;
  color: #92a4c9;
  cursor: not-allowed;
  opacity: 0.6;
}

.retry-btn {
  padding: 6px 12px;
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
  margin-left: auto;
}

.retry-btn:hover {
  background-color: #ef4444;
  color: #fff;
}

/* Amount */
.amount-value {
  font-weight: 700;
  color: #fff;
}

.amount-empty {
  color: #92a4c9;
  font-style: italic;
}

/* Empty State */
.empty-row:hover {
  background-color: transparent !important;
}

.empty-cell {
  padding: 60px 24px !important;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  color: #92a4c9;
}

.empty-icon {
  font-size: 64px;
  opacity: 0.5;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  background-color: #111722;
  border-top: 1px solid #232f48;
}

.pagination-info {
  font-size: 14px;
  color: #92a4c9;
}

.page-current,
.page-total {
  color: #fff;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  gap: 8px;
}

.page-btn {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #232f48;
  background-color: transparent;
  color: #92a4c9;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled) {
  background-color: #232f48;
  color: #fff;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num {
  width: 36px;
  height: 36px;
  border-radius: 8px;
  border: 1px solid #232f48;
  background-color: transparent;
  color: #92a4c9;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  font-weight: 500;
}

.page-num:hover {
  background-color: #232f48;
  color: #fff;
}

.page-num.active {
  background-color: #135bec;
  border-color: #135bec;
  color: #fff;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 24px;
}

.modal-content {
  width: 100%;
  max-width: 900px;
  max-height: 90vh;
  background-color: #111722;
  border: 1px solid #232f48;
  border-radius: 12px;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 24px;
  border-bottom: 1px solid #232f48;
}

.modal-title {
  font-size: 18px;
  font-weight: 600;
  color: #fff;
}

.modal-close {
  width: 32px;
  height: 32px;
  border-radius: 6px;
  border: none;
  background-color: transparent;
  color: #92a4c9;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-close:hover {
  background-color: #232f48;
  color: #fff;
}

.modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Detail Sections */
.detail-section {
  margin-bottom: 24px;
}

.section-title {
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  margin-bottom: 16px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.info-label {
  font-size: 12px;
  color: #92a4c9;
}

.info-value {
  font-size: 14px;
  color: #fff;
}

.amount-highlight {
  color: #22c55e;
  font-weight: 600;
}

/* Tabs */
.tabs {
  display: flex;
  gap: 8px;
  margin-bottom: 16px;
  border-bottom: 1px solid #232f48;
}

.tab-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 16px;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  color: #92a4c9;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.tab-btn:hover {
  color: #fff;
}

.tab-btn.active {
  color: #135bec;
  border-bottom-color: #135bec;
}

.tab-icon {
  font-size: 18px;
}

/* Tab Content */
.tab-content {
  background-color: #0d111c;
  border-radius: 8px;
  padding: 16px;
  min-height: 300px;
}

.data-node-content {
  height: 100%;
}

.node-info {
  margin-bottom: 16px;
  padding: 12px;
  background-color: #111722;
  border-radius: 6px;
}

.node-label {
  font-size: 12px;
  color: #92a4c9;
}

.node-value {
  font-size: 14px;
  color: #fff;
  margin-left: 8px;
}

.data-table-wrapper {
  overflow-x: auto;
}

.snapshot-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}

.snapshot-table th {
  padding: 10px 12px;
  text-align: left;
  background-color: #1a212e;
  color: #92a4c9;
  font-weight: 600;
  border-bottom: 1px solid #232f48;
  white-space: nowrap;
}

.snapshot-table td {
  padding: 10px 12px;
  color: #e2e8f0;
  border-bottom: 1px solid #232f48;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.snapshot-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.more-hint {
  margin-top: 12px;
  font-size: 12px;
  color: #92a4c9;
  text-align: center;
}

.no-data {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 200px;
  gap: 12px;
  color: #92a4c9;
}

.no-data span {
  font-size: 48px;
  opacity: 0.5;
}

/* Quote Summary */
.quote-summary {
  display: flex;
  gap: 24px;
  margin-bottom: 16px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.summary-label {
  font-size: 12px;
  color: #92a4c9;
}

.summary-value {
  font-size: 16px;
  color: #22c55e;
  font-weight: 600;
}

/* Match Rate Classes */
.match-high {
  color: #22c55e;
}

.match-mid {
  color: #eab308;
}

.match-low {
  color: #ef4444;
}
</style>
