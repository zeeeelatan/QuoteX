/**
 * 报价草稿管理工具
 * 用于保存、加载和继续编辑报价草稿
 */

import api from '../../api/index'
import {
  savePageState,
  restorePageState,
  saveFlowData,
  getFlowData,
  clearAllQuotationStates,
  PAGE_STATE_KEYS,
  FLOW_DATA_KEYS,
  type DocumentRecognitionState,
  type SmartMatchingState,
  type PriceAdjustmentState,
  type QuotationGenerationState,
  type TableDataWithHeaders
} from '../stores/quotationStore'
import { getUserName } from '../stores/authStore'

// 草稿阶段类型
export type DraftStage = 'doc_recognition' | 'smart_matching' | 'price_adjustment' | 'quotation_generation'

// 草稿数据接口
export interface DraftData {
  id?: number  // 已有草稿的ID
  file_name: string
  user_name: string
  status: 'draft'
  draft_stage: DraftStage
  device_count: number
  data_source: 'datacenter' | 'office' | 'hybrid'
  // 流程数据
  import_data?: {
    headers: string[]
    data: any[]
    converted?: {
      headers: string[]
      data: any[]
    }
  }
  match_data?: any[]
  price_adjust_data?: any[]
  quote_data?: any
  quote_metadata?: any
  // 页面状态
  page_states?: {
    doc_recognition?: DocumentRecognitionState
    smart_matching?: SmartMatchingState
    price_adjustment?: PriceAdjustmentState
    quotation_generation?: QuotationGenerationState
  }
}

// 草稿列表项接口
export interface DraftListItem {
  id: number
  file_name: string
  user_name: string
  status: string
  device_count: number
  created_at: string
  updated_at: string
  draft_stage: string
}

/**
 * 获取当前用户名（优先从登录态读取）
 */
function getCurrentUserName(): string {
  return getUserName()
}

/**
 * 收集当前页面和流程的所有数据
 */
function collectCurrentDraftData(stage: DraftStage): DraftData {
  const userName = getCurrentUserName()
  let fileName = '未命名草稿'
  let deviceCount = 0
  let dataSource: 'datacenter' | 'office' | 'hybrid' = 'datacenter'

  // 收集流程数据
  const importData = getFlowData<TableDataWithHeaders>(FLOW_DATA_KEYS.CONVERTED_DATA)
  const matchedData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
  const adjustedData = getFlowData<any[]>(FLOW_DATA_KEYS.ADJUSTED_DATA)

  // 收集页面状态
  const docState = restorePageState<DocumentRecognitionState>(PAGE_STATE_KEYS.DOC_RECOGNITION)
  const matchState = restorePageState<SmartMatchingState>(PAGE_STATE_KEYS.SMART_MATCHING)
  const adjustState = restorePageState<PriceAdjustmentState>(PAGE_STATE_KEYS.PRICE_ADJUSTMENT)
  const quoteState = restorePageState<QuotationGenerationState>(PAGE_STATE_KEYS.QUOTATION_GENERATION)

  // 根据不同阶段获取数据
  if (stage === 'doc_recognition' && docState) {
    fileName = docState.currentFileName || '未命名草稿'
    deviceCount = docState.originalTableData?.length || 0
  } else if (stage === 'smart_matching' && matchState) {
    fileName = docState?.currentFileName || '未命名草稿'
    deviceCount = matchState.tableData?.length || 0
    dataSource = matchState.dataSource
  } else if (stage === 'price_adjustment' && adjustState) {
    fileName = docState?.currentFileName || '未命名草稿'
    deviceCount = adjustState.tableData?.length || 0
    dataSource = matchState?.dataSource || 'datacenter'
  } else if (stage === 'quotation_generation' && quoteState) {
    fileName = docState?.currentFileName || '未命名草稿'
    deviceCount = quoteState.tableData?.length || 0
    dataSource = matchState?.dataSource || 'datacenter'
  }

  // 构建草稿数据
  const draftData: DraftData = {
    file_name: fileName,
    user_name: userName,
    status: 'draft',
    draft_stage: stage,
    device_count: deviceCount,
    data_source: dataSource,
    import_data: importData ? {
      headers: importData.headers,
      data: importData.data,
      converted: null
    } : undefined,
    match_data: matchedData || undefined,
    price_adjust_data: adjustedData || undefined,
    page_states: {}
  }

  // 保存各页面状态
  if (docState) draftData.page_states!.doc_recognition = docState
  if (matchState) draftData.page_states!.smart_matching = matchState
  if (adjustState) draftData.page_states!.price_adjustment = adjustState
  if (quoteState) draftData.page_states!.quotation_generation = quoteState

  return draftData
}

/**
 * 保存草稿（新建或更新）
 */
export async function saveDraft(stage: DraftStage, existingDraftId?: number): Promise<number> {
  try {
    const draftData = collectCurrentDraftData(stage)
    const payload = { ...draftData, status: 'draft', draft_stage: stage }

    if (existingDraftId) {
      try {
        // 尝试更新现有草稿（silentError: PUT 404 由此处处理，不弹全局提示）
        await api.put(`/quote-history/${existingDraftId}`, payload, { silentError: true } as any)
        return existingDraftId
      } catch (putError: any) {
        // 如果草稿不存在（404）或无权限（401），回退为创建新草稿
        if (putError?.response?.status === 404 || putError?.response?.status === 401) {
          console.warn(`草稿 ${existingDraftId} 不存在或无权限，创建新草稿`)
          const response = await api.post('/quote-history/', payload)
          return response.id
        }
        throw putError
      }
    } else {
      // 创建新草稿
      const response = await api.post('/quote-history/', payload)
      return response.id
    }
  } catch (error) {
    console.error('保存草稿失败:', error)
    throw error
  }
}

/**
 * 获取草稿列表
 */
export async function getDraftList(): Promise<DraftListItem[]> {
  try {
    const response = await api.get('/quote-history/drafts')
    return response
  } catch (error) {
    console.error('获取草稿列表失败:', error)
    throw error
  }
}

/**
 * 获取草稿详情
 */
export async function getDraftDetail(draftId: number): Promise<DraftData> {
  try {
    const response = await api.get(`/quote-history/${draftId}`)
    return response
  } catch (error) {
    console.error('获取草稿详情失败:', error)
    throw error
  }
}

/**
 * 加载草稿并恢复状态
 */
export async function loadDraft(draftId: number): Promise<void> {
  try {
    const draft = await getDraftDetail(draftId)

    // 清除当前状态
    clearAllQuotationStates()

    // 恢复流程数据
    if (draft.import_data) {
      saveFlowData(FLOW_DATA_KEYS.CONVERTED_DATA, {
        headers: draft.import_data.headers,
        data: draft.import_data.data
      })
    }
    if (draft.match_data) {
      saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, draft.match_data)
    }
    if (draft.price_adjust_data) {
      saveFlowData(FLOW_DATA_KEYS.ADJUSTED_DATA, draft.price_adjust_data)
    }

    // 恢复页面状态
    if (draft.page_states) {
      if (draft.page_states.doc_recognition) {
        savePageState(PAGE_STATE_KEYS.DOC_RECOGNITION, draft.page_states.doc_recognition)
      }
      if (draft.page_states.smart_matching) {
        savePageState(PAGE_STATE_KEYS.SMART_MATCHING, draft.page_states.smart_matching)
      }
      if (draft.page_states.price_adjustment) {
        savePageState(PAGE_STATE_KEYS.PRICE_ADJUSTMENT, draft.page_states.price_adjustment)
      }
      if (draft.page_states.quotation_generation) {
        savePageState(PAGE_STATE_KEYS.QUOTATION_GENERATION, draft.page_states.quotation_generation)
      }
    }

    // 保存当前草稿ID到 localStorage，用于后续更新
    localStorage.setItem('current_draft_id', String(draftId))

    console.log('[DraftUtils] 草稿加载成功:', draft)
  } catch (error) {
    console.error('加载草稿失败:', error)
    throw error
  }
}

/**
 * 删除草稿
 */
export async function deleteDraft(draftId: number): Promise<void> {
  try {
    await api.delete(`/quote-history/${draftId}`)
  } catch (error) {
    console.error('删除草稿失败:', error)
    throw error
  }
}

/**
 * 获取当前正在编辑的草稿ID
 */
export function getCurrentDraftId(): number | null {
  const id = localStorage.getItem('current_draft_id')
  return id ? parseInt(id, 10) : null
}

/**
 * 清除当前草稿ID
 */
export function clearCurrentDraftId(): void {
  localStorage.removeItem('current_draft_id')
}

/**
 * 完成报价（将草稿转为完成状态）
 */
export async function completeQuoteFromDraft(draftId: number, finalData: any): Promise<void> {
  try {
    await api.put(`/quote-history/${draftId}`, {
      status: 'completed',
      ...finalData
    })
    clearCurrentDraftId()
  } catch (error) {
    console.error('完成报价失败:', error)
    throw error
  }
}

/**
 * 格式化草稿阶段显示名称
 */
export function formatDraftStage(stage: string): string {
  const stageMap: Record<string, string> = {
    'doc_recognition': '文档识别',
    'smart_matching': '智能匹配',
    'price_adjustment': '价格调整',
    'quotation_generation': '生成报价'
  }
  return stageMap[stage] || stage
}

/**
 * 格式化时间显示
 */
export function formatDraftTime(dateString: string): string {
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  return date.toLocaleDateString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

/**
 * 根据草稿阶段获取路由路径
 */
export function getRouteByDraftStage(stage: string): string {
  const routeMap: Record<string, string> = {
    'doc_recognition': '/document-recognition',
    'smart_matching': '/smart-matching',
    'price_adjustment': '/price-adjustment',
    'quotation_generation': '/quotation-generation'
  }
  return routeMap[stage] || '/document-recognition'
}
