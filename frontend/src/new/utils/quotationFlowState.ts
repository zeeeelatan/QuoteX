/**
 * 报价流程状态管理工具
 * 用于在不同页面之间保存和恢复状态
 */

// 流程数据传递key
export const FLOW_DATA_KEYS = {
  CONVERTED_DATA: 'quotation_convertedData',        // 智能识别后的数据 → 智能匹配
  MATCHED_DATA: 'quotation_matchedData',            // 智能匹配后的数据 → 价格调整
  ADJUSTED_DATA: 'quotation_adjustedData',          // 价格调整后的数据 → 生成报价
  FINAL_DATA: 'quotation_finalData',                // 最终报价数据
  TRIGGER_MATCHING: 'quotation_triggerMatching',    // 标志：是否需要触发新的智能匹配
  NAVIGATION_MODE: 'quotation_navigationMode',      // 导航模式：'flow'（流程推进）或 'jump'（面包屑跳转）
  // 新增：用于导出Excel的原始表格数据
  ORIGINAL_TABLE_DATA: 'quotation_originalTableData',      // 原始表格数据（包含表头和数据行）
  CONVERTED_TABLE_DATA: 'quotation_convertedTableData',    // 转换后表格数据（包含表头和数据行）
  // 新增：用于保留原始Excel文件格式
  ORIGINAL_EXCEL_FILE: 'quotation_originalExcelFile',      // 原始Excel文件的base64数据
  SELECTED_SHEET_NAME: 'quotation_selectedSheetName',      // 识别时选择的工作表名称
  ORIGINAL_FILE_NAME: 'quotation_originalFileName'         // 原始文件名
}

// 各页面状态保存key
export const PAGE_STATE_KEYS = {
  DOC_RECOGNITION: 'quotation_state_docRecognition',
  SMART_MATCHING: 'quotation_state_smartMatching',
  PRICE_ADJUSTMENT: 'quotation_state_priceAdjustment',
  QUOTATION_GENERATION: 'quotation_state_quotationGeneration'
}

// 页面状态类型定义
export interface DocumentRecognitionState {
  originalTableData: any[]
  originalHeaders: string[]
  convertedTableData: any[]
  convertedHeaders: string[]
  currentFileName: string
  visibleColumns: string[]
  isUploadSectionCollapsed: boolean
  columnMappings?: Record<string, string>  // 列映射关系：转换后表头 -> 原始表头
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

/**
 * 保存页面状态
 */
export function savePageState<T>(key: string, state: T): void {
  try {
    const json = JSON.stringify(state)
    // 估算数据大小（JSON 字符串长度 * 2 字节，近似 UTF-16 编码）
    const sizeInBytes = json.length * 2
    const sizeInMB = sizeInBytes / (1024 * 1024)

    if (sizeInMB > 4) {
      console.warn(`Page state size (${sizeInMB.toFixed(2)}MB) is approaching sessionStorage limit`)
    }

    sessionStorage.setItem(key, json)
    console.log(`Saved page state: ${key} (${sizeInMB.toFixed(2)}MB)`)
  } catch (error) {
    console.error('Failed to save page state:', error)
    // 抛出错误以便调用者可以处理
    throw error
  }
}

/**
 * 恢复页面状态
 */
export function restorePageState<T>(key: string): T | null {
  try {
    const saved = sessionStorage.getItem(key)
    if (saved) {
      return JSON.parse(saved) as T
    }
  } catch (error) {
    console.error('Failed to restore page state:', error)
  }
  return null
}

/**
 * 清除页面状态
 */
export function clearPageState(key: string): void {
  sessionStorage.removeItem(key)
}

/**
 * 清除所有报价流程相关的状态
 */
export function clearAllQuotationStates(): void {
  Object.values(PAGE_STATE_KEYS).forEach(key => {
    sessionStorage.removeItem(key)
  })
  Object.values(FLOW_DATA_KEYS).forEach(key => {
    sessionStorage.removeItem(key)
  })
}

// 导出表格数据的接口定义
export interface TableDataWithHeaders {
  headers: string[]
  data: any[]
}

/**
 * 保存流程数据（用于页面间传递）
 */
export function saveFlowData(key: string, data: any): void {
  try {
    const json = JSON.stringify(data)
    // 估算数据大小
    const sizeInBytes = json.length * 2
    const sizeInMB = sizeInBytes / (1024 * 1024)

    if (sizeInMB > 4) {
      console.warn(`Flow data size (${sizeInMB.toFixed(2)}MB) is approaching sessionStorage limit`)
    }

    sessionStorage.setItem(key, json)
    console.log(`Saved flow data: ${key} (${sizeInMB.toFixed(2)}MB)`)
  } catch (error) {
    console.error('Failed to save flow data:', error)
    // 抛出错误以便调用者可以处理
    throw error
  }
}

/**
 * 获取流程数据
 */
export function getFlowData<T>(key: string): T | null {
  try {
    const saved = sessionStorage.getItem(key)
    if (saved) {
      return JSON.parse(saved) as T
    }
  } catch (error) {
    console.error('Failed to get flow data:', error)
  }
  return null
}

/**
 * 清除指定的流程数据
 */
export function clearFlowData(key: string): void {
  try {
    sessionStorage.removeItem(key)
  } catch (error) {
    console.error('Failed to clear flow data:', error)
  }
}

/**
 * 清理旧的流程数据以释放空间
 * 保留当前阶段和下一阶段需要的数据
 */
export function cleanupOldFlowData(currentStage: 'doc' | 'match' | 'adjust' | 'generate'): void {
  try {
    switch (currentStage) {
      case 'match':
        // 在智能匹配阶段，可以清除原始转换后的数据（因为已经匹配）
        sessionStorage.removeItem(FLOW_DATA_KEYS.CONVERTED_DATA)
        console.log('Cleaned up CONVERTED_DATA to free space')
        break
      case 'adjust':
        // 在价格调整阶段，可以清除更早的数据
        sessionStorage.removeItem(FLOW_DATA_KEYS.CONVERTED_DATA)
        console.log('Cleaned up CONVERTED_DATA to free space')
        break
      case 'generate':
        // 在生成报价阶段，可以清除所有之前的数据
        sessionStorage.removeItem(FLOW_DATA_KEYS.CONVERTED_DATA)
        sessionStorage.removeItem(FLOW_DATA_KEYS.MATCHED_DATA)
        console.log('Cleaned up old flow data to free space')
        break
    }
  } catch (error) {
    console.error('Failed to cleanup old flow data:', error)
  }
}

/**
 * 设置导航模式
 * @param mode 'flow' 流程推进（点击下一步）或 'jump' 面包屑跳转
 */
export function setNavigationMode(mode: 'flow' | 'jump'): void {
  try {
    sessionStorage.setItem(FLOW_DATA_KEYS.NAVIGATION_MODE, mode)
  } catch (error) {
    console.error('Failed to set navigation mode:', error)
  }
}

/**
 * 获取导航模式
 * @returns 'flow' 或 'jump'，默认为 'jump'
 */
export function getNavigationMode(): 'flow' | 'jump' {
  try {
    const mode = sessionStorage.getItem(FLOW_DATA_KEYS.NAVIGATION_MODE)
    return (mode === 'flow' ? 'flow' : 'jump') as 'flow' | 'jump'
  } catch (error) {
    console.error('Failed to get navigation mode:', error)
    return 'jump'
  }
}

/**
 * 清除导航模式
 */
export function clearNavigationMode(): void {
  try {
    sessionStorage.removeItem(FLOW_DATA_KEYS.NAVIGATION_MODE)
  } catch (error) {
    console.error('Failed to clear navigation mode:', error)
  }
}

/**
 * 导航模式：jump（跳转并恢复状态）或 flow（流程推进）
 */
export type NavigationMode = 'jump' | 'flow'

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
