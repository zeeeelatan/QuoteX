<template>
  <div class="quote-management-page">
    <div class="page-header">
      <div class="header-left">
        <button class="back-btn" @click="$router.push('/new')">
          <span class="material-symbols-outlined">arrow_back</span>
        </button>
        <div class="title-section">
          <h1 class="page-title">报价管理</h1>
          <p class="page-subtitle">管理和查看所有报价单</p>
        </div>
      </div>
      <div class="header-actions">
        <button class="btn-primary" @click="createNewQuote">
          <span class="material-symbols-outlined">add</span>
          新建报价单
        </button>
      </div>
    </div>

    <!-- Filter Bar -->
    <div class="filter-bar">
      <div class="filter-group">
        <span class="material-symbols-outlined filter-icon">filter_list</span>
        <select class="filter-select" v-model="statusFilter">
          <option value="">全部状态</option>
          <option value="draft">草稿</option>
          <option value="pending">待审批</option>
          <option value="approved">已审批</option>
          <option value="rejected">已拒绝</option>
        </select>
        <select class="filter-select" v-model="dateFilter">
          <option value="">全部时间</option>
          <option value="today">今天</option>
          <option value="week">本周</option>
          <option value="month">本月</option>
          <option value="year">今年</option>
        </select>
        <input class="search-input-filter" type="text" v-model="searchKeyword" placeholder="搜索报价单号、客户名称..." />
      </div>
    </div>

    <!-- Quotes Table -->
    <div class="quotes-table-wrapper">
      <table class="quotes-table">
        <thead>
          <tr>
            <th>报价单号</th>
            <th>客户名称</th>
            <th>项目名称</th>
            <th>报价金额</th>
            <th>创建时间</th>
            <th>状态</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="quote in filteredQuotes" :key="quote.id">
            <td class="quote-no">{{ quote.no }}</td>
            <td class="customer-name">{{ quote.customer }}</td>
            <td class="project-name">{{ quote.project }}</td>
            <td class="amount">¥{{ quote.amount.toLocaleString() }}</td>
            <td class="create-time">{{ quote.createTime }}</td>
            <td class="status">
              <span class="status-badge" :class="quote.status">{{ statusText[quote.status] }}</span>
            </td>
            <td class="actions">
              <button class="action-btn" @click="viewQuote(quote)" title="查看">
                <span class="material-symbols-outlined">visibility</span>
              </button>
              <button class="action-btn" @click="editQuote(quote)" title="编辑">
                <span class="material-symbols-outlined">edit</span>
              </button>
              <button class="action-btn danger" @click="deleteQuote(quote)" title="删除">
                <span class="material-symbols-outlined">delete</span>
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <!-- Empty State -->
      <div v-if="filteredQuotes.length === 0" class="empty-state">
        <span class="material-symbols-outlined empty-icon">description</span>
        <p class="empty-text">暂无报价单数据</p>
        <button class="btn-primary" @click="createNewQuote">
          <span class="material-symbols-outlined">add</span>
          创建第一个报价单
        </button>
      </div>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="filteredQuotes.length > 0">
      <button class="page-btn" :disabled="currentPage === 1" @click="currentPage--">
        <span class="material-symbols-outlined">chevron_left</span>
      </button>
      <span class="page-info">第 {{ currentPage }} / {{ totalPages }} 页</span>
      <button class="page-btn" :disabled="currentPage === totalPages" @click="currentPage++">
        <span class="material-symbols-outlined">chevron_right</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

// State
const statusFilter = ref('')
const dateFilter = ref('')
const searchKeyword = ref('')
const currentPage = ref(1)
const pageSize = 10

// Mock data
const quotes = ref([
  { id: 1, no: 'QT202401080001', customer: '阿里巴巴集团', project: '数据中心服务器采购', amount: 1250000, createTime: '2024-01-08 10:30', status: 'approved' },
  { id: 2, no: 'QT202401070002', customer: '腾讯科技', project: '办公设备批量采购', amount: 680000, createTime: '2024-01-07 14:20', status: 'pending' },
  { id: 3, no: 'QT202401060003', customer: '华为技术', project: '安防监控系统', amount: 450000, createTime: '2024-01-06 09:15', status: 'draft' },
  { id: 4, no: 'QT202401050004', customer: '百度在线', project: 'GPU服务器集群', amount: 2800000, createTime: '2024-01-05 16:45', status: 'approved' },
  { id: 5, no: 'QT202401040005', customer: '字节跳动', project: '机房网络设备', amount: 920000, createTime: '2024-01-04 11:20', status: 'rejected' },
  { id: 6, no: 'QT202401030006', customer: '京东集团', project: '智能仓储设备', amount: 1500000, createTime: '2024-01-03 13:00', status: 'approved' },
  { id: 7, no: 'QT202401020007', customer: '网易公司', project: '办公电脑采购', amount: 320000, createTime: '2024-01-02 10:00', status: 'pending' },
])

const statusText: Record<string, string> = {
  draft: '草稿',
  pending: '待审批',
  approved: '已审批',
  rejected: '已拒绝'
}

// Computed
const filteredQuotes = computed(() => {
  let result = quotes.value

  if (statusFilter.value) {
    result = result.filter(q => q.status === statusFilter.value)
  }

  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    result = result.filter(q =>
      q.no.toLowerCase().includes(keyword) ||
      q.customer.toLowerCase().includes(keyword) ||
      q.project.toLowerCase().includes(keyword)
    )
  }

  return result
})

const totalPages = computed(() => Math.ceil(filteredQuotes.value.length / pageSize))

// Methods
function createNewQuote() {
  router.push('/new/document-recognition')
}

function viewQuote(quote: any) {
  console.log('View quote:', quote)
}

function editQuote(quote: any) {
  console.log('Edit quote:', quote)
}

function deleteQuote(quote: any) {
  if (confirm(`确定要删除报价单 ${quote.no} 吗？`)) {
    quotes.value = quotes.value.filter(q => q.id !== quote.id)
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Space+Grotesk:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.quote-management-page {
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  background-color: #0B1120;
  color: white;
  height: 100%;
  display: flex;
  flex-direction: column;
  padding: 1.5rem 2rem;
  overflow-y: auto;
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.back-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: #151e32;
  border: 1px solid #232f48;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.back-btn:hover {
  background-color: #232f48;
  color: white;
}

.back-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.title-section {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-top: 0.125rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

/* Buttons */
.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1.25rem;
  background-color: #135bec;
  border: none;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #1e40af;
}

.btn-primary .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Filter Bar */
.filter-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background-color: #151e32;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  margin-bottom: 1rem;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.filter-icon {
  color: #94a3b8;
  font-size: 1.25rem;
}

.filter-select, .search-input-filter {
  background-color: #0B1120;
  border: 1px solid #3e4c6b;
  border-radius: 0.375rem;
  padding: 0.5rem 0.75rem;
  color: white;
  font-size: 0.875rem;
}

.filter-select {
  cursor: pointer;
}

.search-input-filter {
  width: 200px;
}

.search-input-filter::placeholder {
  color: #5e6e8c;
}

/* Table */
.quotes-table-wrapper {
  background-color: #151e32;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  overflow: hidden;
}

.quotes-table {
  width: 100%;
  border-collapse: collapse;
}

.quotes-table thead {
  background-color: #1e293b;
}

.quotes-table th {
  padding: 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.quotes-table tbody tr {
  border-bottom: 1px solid #232f48;
  transition: background-color 0.2s;
}

.quotes-table tbody tr:hover {
  background-color: #1a2332;
}

.quotes-table tbody tr:last-child {
  border-bottom: none;
}

.quotes-table td {
  padding: 1rem;
  font-size: 0.875rem;
}

.quote-no {
  color: #135bec;
  font-weight: 500;
}

.customer-name, .project-name {
  color: #e2e8f0;
}

.amount {
  color: #22c55e;
  font-weight: 600;
}

.create-time {
  color: #94a3b8;
}

.status-badge {
  display: inline-block;
  padding: 0.25rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.draft {
  background-color: rgba(148, 163, 184, 0.15);
  color: #94a3b8;
}

.status-badge.pending {
  background-color: rgba(245, 158, 11, 0.15);
  color: #f59e0b;
}

.status-badge.approved {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

.status-badge.rejected {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.25rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.action-btn:hover {
  background-color: #232f48;
  color: white;
}

.action-btn.danger:hover {
  background-color: rgba(239, 68, 68, 0.15);
  color: #ef4444;
}

.action-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
}

.empty-icon {
  font-size: 4rem;
  color: #3e4c6b;
  margin-bottom: 1rem;
}

.empty-text {
  color: #94a3b8;
  font-size: 1rem;
  margin-bottom: 1.5rem;
}

/* Pagination */
.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  margin-top: 1.5rem;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: #151e32;
  border: 1px solid #232f48;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #232f48;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.page-info {
  color: #94a3b8;
  font-size: 0.875rem;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #0B1120;
}

::-webkit-scrollbar-thumb {
  background: #232f48;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #3e4c6b;
}
</style>
