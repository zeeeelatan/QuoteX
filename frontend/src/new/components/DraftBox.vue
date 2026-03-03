<template>
  <div class="draft-box" v-if="showDraftBox">
    <!-- Header Section -->
    <div class="draft-header">
      <div class="header-title-row">
        <div class="header-icon">
          <span class="material-symbols-outlined">folder_open</span>
        </div>
        <div class="header-text">
          <h2 class="header-title">草稿箱管理</h2>
          <p class="header-subtitle">管理暂存的询价流程，点击条目可快速恢复报价现场</p>
        </div>
      </div>
    </div>

    <!-- Toolbar Section -->
    <div class="draft-toolbar">
      <div class="search-box">
        <div class="search-icon">
          <span class="material-symbols-outlined">search</span>
        </div>
        <input
          type="text"
          v-model="searchQuery"
          class="search-input"
          placeholder="输入文件名称或单号搜索..."
          @input="filterDrafts"
        />
      </div>
      <div class="toolbar-actions">
        <button class="toolbar-btn filter-btn">
          <span class="material-symbols-outlined">filter_list</span>
          <span>筛选</span>
        </button>
        <button
          class="toolbar-btn delete-btn"
          :disabled="selectedDrafts.size === 0"
          @click="deleteSelectedDrafts"
        >
          <span class="material-symbols-outlined">delete</span>
          <span>批量删除</span>
        </button>
      </div>
    </div>

    <!-- Table Section -->
    <div class="draft-table-container" v-if="!loading && filteredDrafts.length > 0">
      <table class="draft-table">
        <thead>
          <tr>
            <th class="checkbox-col">
              <input
                type="checkbox"
                class="checkbox"
                :checked="isAllSelected"
                @change="toggleSelectAll"
              />
            </th>
            <th>导入文件名称</th>
            <th>当前节点</th>
            <th>数据条目</th>
            <th>用户</th>
            <th>暂存时间</th>
            <th class="actions-col">操作</th>
          </tr>
        </thead>
        <tbody>
          <tr
            v-for="draft in filteredDrafts"
            :key="draft.id"
            class="draft-row"
            :class="{ 'selected': selectedDrafts.has(draft.id) }"
          >
            <td class="checkbox-col">
              <input
                type="checkbox"
                class="checkbox"
                :checked="selectedDrafts.has(draft.id)"
                @change="toggleSelectDraft(draft.id)"
              />
            </td>
            <td>
              <div class="file-info">
                <span class="file-icon">
                  <span class="material-symbols-outlined">description</span>
                </span>
                <div class="file-details">
                  <span class="file-name">{{ draft.file_name }}</span>
                  <span class="file-meta">{{ draft.device_count }} 项数据</span>
                </div>
              </div>
            </td>
            <td>
              <span class="stage-badge" :class="getStageClass(draft.draft_stage)">
                <span class="stage-dot"></span>
                {{ formatDraftStage(draft.draft_stage) }}
              </span>
            </td>
            <td>
              <span class="item-count">{{ draft.device_count.toLocaleString() }}</span>
            </td>
            <td>
              <div class="user-info">
                <div class="user-avatar" :class="getUserColorClass(draft.user_name)">
                  {{ getInitial(draft.user_name) }}
                </div>
                <span class="user-name">{{ draft.user_name }}</span>
              </div>
            </td>
            <td>
              <span class="save-time">{{ formatSaveTime(draft.updated_at) }}</span>
            </td>
            <td class="actions-col">
              <div class="row-actions">
                <button class="continue-btn" @click="continueDraft(draft)">
                  <span>继续报价</span>
                  <span class="material-symbols-outlined">arrow_forward</span>
                </button>
                <button class="icon-btn delete-icon-btn" @click="deleteDraft(draft.id)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Empty State -->
    <div class="empty-state" v-else-if="!loading && filteredDrafts.length === 0">
      <div class="empty-icon-wrapper">
        <span class="material-symbols-outlined empty-icon">content_paste_off</span>
      </div>
      <h3 class="empty-title">暂无草稿</h3>
      <p class="empty-text">{{ searchQuery ? '未找到匹配的草稿记录' : '当前没有保存的草稿记录' }}</p>
      <p class="empty-hint" v-if="!searchQuery">在报价过程中使用 Ctrl+S 快捷键保存草稿</p>
    </div>

    <!-- Loading State -->
    <div class="loading-state" v-if="loading">
      <div class="spinner"></div>
      <p>加载中...</p>
    </div>

    <!-- Pagination -->
    <div class="pagination" v-if="!loading && filteredDrafts.length > 0">
      <div class="pagination-info">
        显示 <span class="info-number">1</span> 到 <span class="info-number">{{ filteredDrafts.length }}</span> 条，共 <span class="info-number">{{ drafts.length }}</span> 条记录
      </div>
      <div class="pagination-controls">
        <button class="page-btn" disabled>
          <span class="material-symbols-outlined">chevron_left</span>
        </button>
        <button class="page-num active">1</button>
        <button class="page-btn" disabled>
          <span class="material-symbols-outlined">chevron_right</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessageBox, ElMessage } from 'element-plus'
import {
  getDraftList,
  deleteDraft as deleteDraftApi,
  loadDraft,
  formatDraftStage,
  getRouteByDraftStage
} from '../utils/draftUtils'

const router = useRouter()

const showDraftBox = ref(true)
const drafts = ref<any[]>([])
const loading = ref(false)
const searchQuery = ref('')
const selectedDrafts = ref<Set<number>>(new Set())

// 过滤后的草稿列表
const filteredDrafts = computed(() => {
  if (!searchQuery.value) {
    return drafts.value
  }
  const query = searchQuery.value.toLowerCase()
  return drafts.value.filter(draft =>
    draft.file_name.toLowerCase().includes(query) ||
    draft.user_name.toLowerCase().includes(query)
  )
})

// 是否全选
const isAllSelected = computed(() => {
  return filteredDrafts.value.length > 0 &&
         filteredDrafts.value.every(d => selectedDrafts.value.has(d.id))
})

// 加载草稿列表
async function loadDrafts() {
  loading.value = true
  try {
    const list = await getDraftList()
    drafts.value = list.map((d: any) => ({ ...d, id: Number(d.id) }))
  } catch (error) {
    console.error('加载草稿列表失败:', error)
    ElMessage.error('加载草稿列表失败')
  } finally {
    loading.value = false
  }
}

// 过滤草稿
function filterDrafts() {
  // Computed property handles this
}

// 继续编辑草稿
async function continueDraft(draft: any) {
  const id = Number(draft.id)
  if (Number.isNaN(id)) return
  try {
    await loadDraft(id)
    const route = getRouteByDraftStage(draft.draft_stage)
    router.push(route)
  } catch (error: any) {
    console.error('加载草稿失败:', error)
    const msg = error?.response?.data?.detail ?? '加载草稿失败，请重试'
    ElMessage.error(typeof msg === 'string' ? msg : '加载草稿失败，请重试')
  }
}

// 删除单个草稿
async function deleteDraft(draftId: number | string) {
  const id = Number(draftId)
  if (Number.isNaN(id)) return
  try {
    await ElMessageBox.confirm('确定要删除这个草稿吗？', '删除草稿', {
      confirmButtonText: '删除',
      cancelButtonText: '取消',
      type: 'warning'
    })

    await deleteDraftApi(id)
    ElMessage.success('草稿已删除')
    await loadDrafts()
  } catch (error: any) {
    if (error !== 'cancel') {
      console.error('删除草稿失败:', error)
      const msg = error?.response?.data?.detail ?? '删除草稿失败，请重试'
      ElMessage.error(typeof msg === 'string' ? msg : '删除草稿失败，请重试')
    }
  }
}

// 批量删除选中草稿
async function deleteSelectedDrafts() {
  if (selectedDrafts.value.size === 0) return

  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedDrafts.value.size} 个草稿吗？`,
      '批量删除草稿',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    for (const draftId of selectedDrafts.value) {
      await deleteDraftApi(draftId)
    }

    ElMessage.success(`已删除 ${selectedDrafts.value.size} 个草稿`)
    selectedDrafts.value.clear()
    await loadDrafts()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('批量删除草稿失败:', error)
      ElMessage.error('删除草稿失败，请重试')
    }
  }
}

// 切换选中单个草稿
function toggleSelectDraft(draftId: number) {
  if (selectedDrafts.value.has(draftId)) {
    selectedDrafts.value.delete(draftId)
  } else {
    selectedDrafts.value.add(draftId)
  }
}

// 切换全选
function toggleSelectAll() {
  if (isAllSelected.value) {
    selectedDrafts.value.clear()
  } else {
    filteredDrafts.value.forEach(d => selectedDrafts.value.add(d.id))
  }
}

// 获取阶段对应的样式类
function getStageClass(stage: string): string {
  const stageMap: Record<string, string> = {
    'doc_recognition': 'stage-blue',
    'smart_matching': 'stage-purple',
    'price_adjustment': 'stage-amber',
    'quotation_generation': 'stage-green'
  }
  return stageMap[stage] || 'stage-gray'
}

// 获取用户名首字母
function getInitial(userName: string): string {
  return userName ? userName.charAt(0).toUpperCase() : '?'
}

// 获取用户头像颜色类
function getUserColorClass(userName: string): string {
  const colors = ['bg-indigo', 'bg-pink', 'bg-emerald', 'bg-cyan', 'bg-orange']
  let hash = 0
  for (let i = 0; i < userName.length; i++) {
    hash = userName.charCodeAt(i) + ((hash << 5) - hash)
  }
  return colors[Math.abs(hash) % colors.length]
}

// 格式化保存时间
function formatSaveTime(dateString: string): string {
  const date = new Date(dateString)
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')
  return `${year}-${month}-${day} ${hours}:${minutes}`
}

// 切换显示/隐藏
function toggleDraftBox() {
  showDraftBox.value = !showDraftBox.value
}

onMounted(() => {
  loadDrafts()
})

// 暴露方法供父组件调用
defineExpose({
  loadDrafts,
  toggleDraftBox
})
</script>

<style scoped>
.draft-box {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1.5rem;
}

/* Header Section */
.draft-header {
  display: flex;
  align-items: center;
}

.header-title-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.header-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.75rem;
  height: 2.75rem;
  background-color: #1c1f27;
  border: 1px solid #282e39;
  border-radius: 0.5rem;
}

.header-icon .material-symbols-outlined {
  color: #135bec;
  font-size: 1.75rem;
}

.header-text {
  display: flex;
  flex-direction: column;
}

.header-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  margin: 0;
  line-height: 1.2;
}

.header-subtitle {
  font-size: 0.875rem;
  color: #9da6b9;
  margin: 0.25rem 0 0 0;
}

/* Toolbar Section */
.draft-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 1rem;
  background-color: #161b26;
  border: 1px solid #282e39;
  border-radius: 0.75rem;
}

.search-box {
  position: relative;
  flex: 1;
  max-width: 480px;
  min-width: 280px;
}

.search-icon {
  position: absolute;
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  pointer-events: none;
}

.search-icon .material-symbols-outlined {
  color: #9da6b9;
  font-size: 1.25rem;
}

.search-input {
  width: 100%;
  padding: 0.625rem 0.75rem 0.625rem 2.5rem;
  background-color: #0b0e14;
  border: 1px solid #282e39;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  outline: none;
  transition: all 0.2s;
}

.search-input::placeholder {
  color: #9da6b9;
}

.search-input:focus {
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.1);
}

.toolbar-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.filter-btn {
  background-color: #0b0e14;
  color: #9da6b9;
}

.filter-btn:hover {
  color: white;
  background-color: #1c1f27;
}

.delete-btn {
  background-color: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.delete-btn:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.2);
}

.delete-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

/* Table Section */
.draft-table-container {
  flex: 1;
  background-color: #161b26;
  border: 1px solid #282e39;
  border-radius: 0.75rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.draft-table {
  width: 100%;
  border-collapse: collapse;
}

.draft-table thead {
  background-color: #1c1f27;
  border-bottom: 1px solid #282e39;
  position: sticky;
  top: 0;
  z-index: 10;
}

.draft-table th {
  padding: 1rem 1.5rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #9da6b9;
}

.draft-table td {
  padding: 1rem 1.5rem;
}

.draft-table th,
.draft-table td {
  vertical-align: middle;
}

.draft-table tbody {
  overflow-y: auto;
}

.draft-row {
  border-bottom: 1px solid #282e39;
  transition: background-color 0.2s;
}

.draft-row:last-child {
  border-bottom: none;
}

.draft-row:hover {
  background-color: rgba(28, 31, 39, 0.5);
}

.draft-row.selected {
  background-color: rgba(19, 91, 236, 0.1);
}

.checkbox-col {
  width: 60px;
}

.checkbox {
  width: 1rem;
  height: 1rem;
  border-radius: 0.25rem;
  background-color: #0b0e14;
  border: 1px solid #282e39;
  cursor: pointer;
  accent-color: #135bec;
}

/* File Info */
.file-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.file-icon {
  display: flex;
  align-items: center;
  justify-content: center;
}

.file-icon .material-symbols-outlined {
  font-size: 1.5rem;
  color: #217346;
}

.file-details {
  display: flex;
  flex-direction: column;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

.file-name:hover {
  color: #135bec;
}

.file-meta {
  font-size: 0.75rem;
  color: #9da6b9;
}

/* Stage Badge */
.stage-badge {
  display: inline-flex;
  align-items: center;
  padding: 0.375rem 0.625rem;
  border-radius: 9999px;
  font-size: 0.75rem;
  font-weight: 500;
  border: 1px solid;
}

.stage-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  margin-right: 0.375rem;
}

.stage-blue {
  background-color: rgba(59, 130, 246, 0.1);
  color: #60a5fa;
  border-color: rgba(59, 130, 246, 0.2);
}

.stage-blue .stage-dot {
  background-color: #60a5fa;
}

.stage-purple {
  background-color: rgba(168, 85, 247, 0.1);
  color: #a78bfa;
  border-color: rgba(168, 85, 247, 0.2);
}

.stage-purple .stage-dot {
  background-color: #a78bfa;
}

.stage-amber {
  background-color: rgba(245, 158, 11, 0.1);
  color: #fbbf24;
  border-color: rgba(245, 158, 11, 0.2);
}

.stage-amber .stage-dot {
  background-color: #fbbf24;
}

.stage-green {
  background-color: rgba(34, 197, 94, 0.1);
  color: #4ade80;
  border-color: rgba(34, 197, 94, 0.2);
}

.stage-green .stage-dot {
  background-color: #4ade80;
}

.stage-gray {
  background-color: rgba(107, 114, 128, 0.1);
  color: #9ca3af;
  border-color: rgba(107, 114, 128, 0.2);
}

.stage-gray .stage-dot {
  background-color: #9ca3af;
}

/* Item Count */
.item-count {
  font-size: 0.875rem;
  color: white;
  font-variant-numeric: tabular-nums;
}

/* User Info */
.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-avatar {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.625rem;
  font-weight: 700;
  text-transform: uppercase;
}

.user-avatar.bg-indigo {
  background-color: rgba(99, 102, 241, 0.2);
  border: 1px solid rgba(99, 102, 241, 0.3);
  color: #a5b4fc;
}

.user-avatar.bg-pink {
  background-color: rgba(236, 72, 153, 0.2);
  border: 1px solid rgba(236, 72, 153, 0.3);
  color: #f9a8d4;
}

.user-avatar.bg-emerald {
  background-color: rgba(16, 185, 129, 0.2);
  border: 1px solid rgba(16, 185, 129, 0.3);
  color: #6ee7b7;
}

.user-avatar.bg-cyan {
  background-color: rgba(6, 182, 212, 0.2);
  border: 1px solid rgba(6, 182, 212, 0.3);
  color: #67e8f9;
}

.user-avatar.bg-orange {
  background-color: rgba(249, 115, 22, 0.2);
  border: 1px solid rgba(249, 115, 22, 0.3);
  color: #fdba74;
}

.user-name {
  font-size: 0.875rem;
  color: #9da6b9;
}

/* Save Time */
.save-time {
  font-size: 0.875rem;
  color: #9da6b9;
  font-variant-numeric: tabular-nums;
}

/* Actions */
.actions-col {
  text-align: right;
}

.row-actions {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}

.continue-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background-color: #135bec;
  color: white;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 6px -1px rgba(19, 91, 236, 0.2);
}

.continue-btn:hover {
  background-color: #1e40af;
}

.continue-btn .material-symbols-outlined {
  font-size: 1rem;
}

.icon-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  background-color: transparent;
  border: none;
  color: #9da6b9;
  cursor: pointer;
  transition: all 0.2s;
}

.icon-btn:hover {
  color: #f87171;
  background-color: rgba(239, 68, 68, 0.1);
}

.icon-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Empty State */
.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  background-color: #161b26;
  border: 1px solid #282e39;
  border-radius: 0.75rem;
}

.empty-icon-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 5rem;
  height: 5rem;
  background-color: #1c1f27;
  border-radius: 50%;
  margin-bottom: 1rem;
}

.empty-icon {
  font-size: 2.5rem;
  color: #9da6b9;
}

.empty-title {
  font-size: 1rem;
  font-weight: 500;
  color: white;
  margin: 0 0 0.5rem 0;
}

.empty-text {
  font-size: 0.875rem;
  color: #9da6b9;
  margin: 0 0 0.25rem 0;
}

.empty-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin: 0;
}

/* Loading State */
.loading-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem 1rem;
  background-color: #161b26;
  border: 1px solid #282e39;
  border-radius: 0.75rem;
}

.spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #282e39;
  border-top-color: #135bec;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-state p {
  margin-top: 1rem;
  color: #9da6b9;
  font-size: 0.875rem;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background-color: #161b26;
  border: 1px solid #282e39;
  border-top: none;
  border-radius: 0 0 0.75rem 0.75rem;
}

.pagination-info {
  font-size: 0.875rem;
  color: #9da6b9;
}

.info-number {
  color: white;
  font-weight: 500;
}

.pagination-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.page-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  background-color: transparent;
  border: none;
  color: #9da6b9;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #1c1f27;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.page-num {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.375rem;
  background-color: #135bec;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

/* Scrollbar */
.draft-table-container::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

.draft-table-container::-webkit-scrollbar-track {
  background: #111318;
}

.draft-table-container::-webkit-scrollbar-thumb {
  background: #282e39;
  border-radius: 4px;
}

.draft-table-container::-webkit-scrollbar-thumb:hover {
  background: #3b4354;
}
</style>
