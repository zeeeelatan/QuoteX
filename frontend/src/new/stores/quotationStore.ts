/**
 * 报价流程全局状态管理
 * 使用内存存储替代 sessionStorage，解决大数据量流转问题
 * 保留与 quotationFlowState.ts 相同的 API 接口
 */

import { reactive, shallowRef } from 'vue'

// ========== Keys 常量（必须先定义） ==========

export const FlowDataKeys = {
  CONVERTED_DATA: 'quotation_convertedData',
  MATCHED_DATA: 'quotation_matchedData',
  ADJUSTED_DATA: 'quotation_adjustedData',
  FINAL_DATA: 'quotation_finalData',
  TRIGGER_MATCHING: 'quotation_triggerMatching',
  NAVIGATION_MODE: 'quotation_navigationMode',
  ORIGINAL_TABLE_DATA: 'quotation_originalTableData',
  CONVERTED_TABLE_DATA: 'quotation_convertedTableData',
  // 新增：用于保留原始Excel文件格式
  ORIGINAL_EXCEL_FILE: 'quotation_originalExcelFile',
  SELECTED_SHEET_NAME: 'quotation_selectedSheetName',
  ORIGINAL_FILE_NAME: 'quotation_originalFileName',
} as const

export const PageStateKeys = {
  DOC_RECOGNITION: 'quotation_state_docRecognition',
  SMART_MATCHING: 'quotation_state_smartMatching',
  PRICE_ADJUSTMENT: 'quotation_state_priceAdjustment',
  QUOTATION_GENERATION: 'quotation_state_quotationGeneration',
} as const

// 保持向后兼容
export const FLOW_DATA_KEYS = FlowDataKeys
export const PAGE_STATE_KEYS = PageStateKeys

// ========== 类型定义 ==========

// 页面状态类型定义
export interface DocumentRecognitionState {
  originalTableData: any[]
  originalHeaders: string[]
  convertedTableData: any[]
  convertedHeaders: string[]
  currentFileName: string
  visibleColumns: string[]
  isUploadSectionCollapsed: boolean
  columnMappings?: Record<string, string>
  selectedQuotationType?: string
  hasData: boolean
}

export interface SmartMatchingState {
  tableData: any[]
  dataSource: 'datacenter' | 'office' | 'hybrid'
  filterStatus: 'all' | 'low' | 'unmatched' | 'matched'
  hasData: boolean
}

export interface PriceAdjustmentState {
  tableData: any[]
  hasData: boolean
}

export interface QuotationGenerationState {
  tableData: any[]
  projectName: string
  customerName: string
  validDays: number
  notes: string
  hasData: boolean
}

// 导出表格数据的接口定义
export interface TableDataWithHeaders {
  headers: string[]
  data: any[]
}

// ========== 全局状态 Store ==========

// 流程数据（使用 shallowRef 优化大数据量性能）
const flowData: Record<string, any> = reactive({
  [FlowDataKeys.CONVERTED_DATA]: shallowRef<any[]>([]),
  [FlowDataKeys.MATCHED_DATA]: shallowRef<any[]>([]),
  [FlowDataKeys.ADJUSTED_DATA]: shallowRef<any[]>([]),
  [FlowDataKeys.FINAL_DATA]: shallowRef<any[]>([]),
  [FlowDataKeys.TRIGGER_MATCHING]: false,
  [FlowDataKeys.NAVIGATION_MODE]: 'jump' as 'flow' | 'jump',
  [FlowDataKeys.ORIGINAL_TABLE_DATA]: shallowRef<TableDataWithHeaders | null>(null),
  [FlowDataKeys.CONVERTED_TABLE_DATA]: shallowRef<TableDataWithHeaders | null>(null),
  // 新增：用于保留原始Excel文件格式
  [FlowDataKeys.ORIGINAL_EXCEL_FILE]: shallowRef<string | null>(null),
  [FlowDataKeys.SELECTED_SHEET_NAME]: shallowRef<string | null>(null),
  [FlowDataKeys.ORIGINAL_FILE_NAME]: shallowRef<string | null>(null),
})

// 页面状态
const pageStates: Record<string, any> = reactive({
  [PageStateKeys.DOC_RECOGNITION]: null as DocumentRecognitionState | null,
  [PageStateKeys.SMART_MATCHING]: null as SmartMatchingState | null,
  [PageStateKeys.PRICE_ADJUSTMENT]: null as PriceAdjustmentState | null,
  [PageStateKeys.QUOTATION_GENERATION]: null as QuotationGenerationState | null,
})

// ========== 流程数据操作 ==========

/**
 * 保存流程数据
 * 使用 shallowRef 存储，大数据量时性能更好
 */
export function saveFlowData<T>(key: string, data: T): void {
  if (key in flowData) {
    const existing = flowData[key]
    // 检查是否是 shallowRef（有 .value 属性）
    if (existing && typeof existing === 'object' && 'value' in existing) {
      existing.value = data
    } else {
      // 如果不是 shallowRef，替换为 shallowRef
      flowData[key] = shallowRef(data)
    }
    console.log(`[QuotationStore] Saved flow data: ${key}, items:`, Array.isArray(data) ? data.length : 'N/A')
  } else {
    // 动态添加新的 key
    flowData[key] = shallowRef(data)
    console.log(`[QuotationStore] Created new flow data key: ${key}`)
  }
}

/**
 * 获取流程数据
 */
export function getFlowData<T>(key: string): T | null {
  if (key in flowData) {
    const existing = flowData[key]
    // 检查是否是 shallowRef（有 .value 属性）
    if (existing && typeof existing === 'object' && 'value' in existing) {
      return existing.value ?? null
    }
    // 如果是普通值，直接返回
    return existing ?? null
  }
  return null
}

/**
 * 清除指定的流程数据
 */
export function clearFlowData(key: string): void {
  if (key in flowData) {
    const existing = flowData[key]
    // 检查是否是 shallowRef
    if (existing && typeof existing === 'object' && 'value' in existing) {
      existing.value = key === FlowDataKeys.TRIGGER_MATCHING ? false : []
    } else {
      // 如果是普通值，直接设置
      flowData[key] = key === FlowDataKeys.TRIGGER_MATCHING ? false : []
    }
    console.log(`[QuotationStore] Cleared flow data: ${key}`)
  }
}

/**
 * 清理旧的流程数据以释放空间
 */
export function cleanupOldFlowData(currentStage: 'doc' | 'match' | 'adjust' | 'generate'): void {
  switch (currentStage) {
    case 'match':
      // 在智能匹配阶段，可以清除原始转换后的数据
      flowData[FlowDataKeys.CONVERTED_DATA].value = []
      console.log('[QuotationStore] Cleaned up CONVERTED_DATA')
      break
    case 'adjust':
      // 在价格调整阶段，清除更早的数据
      flowData[FlowDataKeys.CONVERTED_DATA].value = []
      console.log('[QuotationStore] Cleaned up CONVERTED_DATA')
      break
    case 'generate':
      // 在生成报价阶段，清除之前的数据
      flowData[FlowDataKeys.CONVERTED_DATA].value = []
      flowData[FlowDataKeys.MATCHED_DATA].value = []
      console.log('[QuotationStore] Cleaned up old flow data')
      break
  }
}

/**
 * 清除所有流程数据
 * 安全地处理 shallowRef 和普通值两种情况
 */
export function clearAllFlowData(): void {
  const safeClear = (key: string, defaultVal: any) => {
    const existing = flowData[key]
    if (existing && typeof existing === 'object' && 'value' in existing) {
      existing.value = defaultVal
    } else {
      flowData[key] = shallowRef(defaultVal)
    }
  }

  safeClear(FlowDataKeys.CONVERTED_DATA, [])
  safeClear(FlowDataKeys.MATCHED_DATA, [])
  safeClear(FlowDataKeys.ADJUSTED_DATA, [])
  safeClear(FlowDataKeys.FINAL_DATA, [])
  flowData[FlowDataKeys.TRIGGER_MATCHING] = false
  safeClear(FlowDataKeys.ORIGINAL_TABLE_DATA, null)
  safeClear(FlowDataKeys.CONVERTED_TABLE_DATA, null)
  safeClear(FlowDataKeys.ORIGINAL_EXCEL_FILE, null)
  safeClear(FlowDataKeys.SELECTED_SHEET_NAME, null)
  safeClear(FlowDataKeys.ORIGINAL_FILE_NAME, null)
  console.log('[QuotationStore] Cleared all flow data')
}

// ========== 页面状态操作 ==========

/**
 * 保存页面状态
 */
export function savePageState<T>(key: string, state: T): void {
  pageStates[key] = state
  console.log(`[QuotationStore] Saved page state: ${key}`)
}

/**
 * 恢复页面状态
 */
export function restorePageState<T>(key: string): T | null {
  return pageStates[key] ?? null
}

/**
 * 清除页面状态
 */
export function clearPageState(key: string): void {
  pageStates[key] = null
  console.log(`[QuotationStore] Cleared page state: ${key}`)
}

/**
 * 清除所有页面状态
 */
export function clearAllPageStates(): void {
  Object.keys(PageStateKeys).forEach(key => {
    pageStates[PageStateKeys[key as keyof typeof PageStateKeys]] = null
  })
  console.log('[QuotationStore] Cleared all page states')
}

/**
 * 清除所有报价流程相关的状态
 */
export function clearAllQuotationStates(): void {
  clearAllPageStates()
  clearAllFlowData()
}

// ========== 导航模式操作 ==========

/**
 * 设置导航模式
 */
export function setNavigationMode(mode: 'flow' | 'jump'): void {
  flowData[FlowDataKeys.NAVIGATION_MODE] = mode
  console.log(`[QuotationStore] Set navigation mode: ${mode}`)
}

/**
 * 获取导航模式
 */
export function getNavigationMode(): 'flow' | 'jump' {
  return flowData[FlowDataKeys.NAVIGATION_MODE]
}

/**
 * 清除导航模式
 */
export function clearNavigationMode(): void {
  flowData[FlowDataKeys.NAVIGATION_MODE] = 'jump'
}

// ========== 辅助函数 ==========

/**
 * 获取当前存储的数据统计信息（用于调试）
 */
export function getStoreStats(): Record<string, any> {
  return {
    flowData: {
      convertedData: flowData[FlowDataKeys.CONVERTED_DATA].value.length,
      matchedData: flowData[FlowDataKeys.MATCHED_DATA].value.length,
      adjustedData: flowData[FlowDataKeys.ADJUSTED_DATA].value.length,
      finalData: flowData[FlowDataKeys.FINAL_DATA].value.length,
      triggerMatching: flowData[FlowDataKeys.TRIGGER_MATCHING],
      navigationMode: flowData[FlowDataKeys.NAVIGATION_MODE],
    },
    pageStates: {
      docRecognition: pageStates[PageStateKeys.DOC_RECOGNITION]?.hasData ?? false,
      smartMatching: pageStates[PageStateKeys.SMART_MATCHING]?.hasData ?? false,
      priceAdjustment: pageStates[PageStateKeys.PRICE_ADJUSTMENT]?.hasData ?? false,
      quotationGeneration: pageStates[PageStateKeys.QUOTATION_GENERATION]?.hasData ?? false,
    },
  }
}

/**
 * 导出类型
 */
export type {
  DocumentRecognitionState,
  SmartMatchingState,
  PriceAdjustmentState,
  QuotationGenerationState,
  TableDataWithHeaders,
}

// 导航模式：jump（跳转并恢复状态）或 flow（流程推进）
export type NavigationMode = 'jump' | 'flow'

// ========== 导航辅助函数 ==========

/**
 * 创建带状态保存的导航函数
 * @param navigate 导航函数
 * @param stateKey 状态保存key
 * @param getState 获取当前状态的函数
 * @param dataKey 流程数据key（可选，用于保存传递给下一步的数据）
 * @param getData 获取流程数据的函数（可选）
 */
export function createNavigateWithState<T, D = any>(
  navigate: () => void,
  stateKey: string,
  getState: () => T,
  dataKey?: string,
  getData?: () => D
): () => void {
  return () => {
    // 保存当前页面状态
    const state = getState()
    savePageState(stateKey, state)

    // 如果有流程数据，也保存
    if (dataKey && getData) {
      const data = getData()
      saveFlowData(dataKey, data)
    }

    // 执行导航
    navigate()
  }
}

/**
 * 创建跳转导航函数（不保存状态，直接跳转）
 */
export function createJumpNavigate(navigate: () => void): () => void {
  return () => {
    navigate()
  }
}

// 导出 Store 实例（用于直接访问，调试用）
export const store = {
  flowData,
  pageStates,
}
