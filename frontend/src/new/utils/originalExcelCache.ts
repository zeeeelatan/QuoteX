/**
 * 原始需求 Excel 持久化缓存
 *
 * 报价流程的内存 store 在刷新页面后会丢失；
 * 这里用 IndexedDB 保存原始附件 base64，并在导出时从
 * 内存 → IndexedDB → 最近上传 localStorage 三级回源，
 * 确保“保留原格式”导出路径尽可能可用。
 */

import { getStorageKeyPrefix } from '../stores/authStore'

export interface OriginalExcelCachePayload {
  fileName: string
  base64: string
  selectedSheetName: string
  selectedSheetNames: string[]
  savedAt: number
}

const DB_NAME = 'ai_quote_original_excel'
const DB_VERSION = 1
const STORE_NAME = 'files'
const RECORD_ID = 'current'

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION)
    request.onerror = () => reject(request.error || new Error('打开 IndexedDB 失败'))
    request.onsuccess = () => resolve(request.result)
    request.onupgradeneeded = () => {
      const db = request.result
      if (!db.objectStoreNames.contains(STORE_NAME)) {
        db.createObjectStore(STORE_NAME, { keyPath: 'id' })
      }
    }
  })
}

export async function persistOriginalExcelCache(
  payload: Omit<OriginalExcelCachePayload, 'savedAt'>
): Promise<void> {
  if (!payload.base64 || !payload.fileName) return
  try {
    const db = await openDb()
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite')
      tx.oncomplete = () => resolve()
      tx.onerror = () => reject(tx.error || new Error('写入 IndexedDB 失败'))
      tx.objectStore(STORE_NAME).put({
        id: RECORD_ID,
        ...payload,
        savedAt: Date.now()
      })
    })
    db.close()
  } catch (error) {
    console.warn('[OriginalExcelCache] 持久化失败:', error)
  }
}

export async function loadOriginalExcelCache(): Promise<OriginalExcelCachePayload | null> {
  try {
    const db = await openDb()
    const record = await new Promise<any>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readonly')
      const req = tx.objectStore(STORE_NAME).get(RECORD_ID)
      req.onsuccess = () => resolve(req.result || null)
      req.onerror = () => reject(req.error || new Error('读取 IndexedDB 失败'))
    })
    db.close()
    if (!record?.base64) return null
    return {
      fileName: record.fileName || '',
      base64: record.base64,
      selectedSheetName: record.selectedSheetName || '',
      selectedSheetNames: Array.isArray(record.selectedSheetNames) ? record.selectedSheetNames : [],
      savedAt: record.savedAt || 0
    }
  } catch (error) {
    console.warn('[OriginalExcelCache] 读取失败:', error)
    return null
  }
}

export async function clearOriginalExcelCache(): Promise<void> {
  try {
    const db = await openDb()
    await new Promise<void>((resolve, reject) => {
      const tx = db.transaction(STORE_NAME, 'readwrite')
      tx.oncomplete = () => resolve()
      tx.onerror = () => reject(tx.error || new Error('清理 IndexedDB 失败'))
      tx.objectStore(STORE_NAME).delete(RECORD_ID)
    })
    db.close()
  } catch (error) {
    console.warn('[OriginalExcelCache] 清理失败:', error)
  }
}

interface RecentUploadRecord {
  id: string
  fileName: string
  fileData: string
  rowCount: number
  timestamp: number
}

/** 从智能识别页的“最近上传”localStorage 中按文件名找回原始附件 */
export function loadOriginalExcelFromRecentUploads(fileName: string): string | null {
  if (!fileName) return null
  try {
    const key = `${getStorageKeyPrefix()}recentUploads`
    const stored = localStorage.getItem(key)
    if (!stored) return null
    const records = JSON.parse(stored) as RecentUploadRecord[]
    if (!Array.isArray(records)) return null

    const normalize = (name: string) => name.trim().toLowerCase()
    const target = normalize(fileName)
    const exact = records.find(r => normalize(r.fileName || '') === target && r.fileData)
    if (exact?.fileData) return exact.fileData

    // 允许去掉扩展名后的模糊匹配
    const stem = target.replace(/\.xlsx?$/i, '')
    const fuzzy = records.find(r => {
      const name = normalize(r.fileName || '')
      return r.fileData && (name.includes(stem) || stem.includes(name.replace(/\.xlsx?$/i, '')))
    })
    return fuzzy?.fileData || null
  } catch (error) {
    console.warn('[OriginalExcelCache] 从最近上传恢复失败:', error)
    return null
  }
}

export type OriginalExcelResolveSource = 'memory' | 'indexeddb' | 'recentUploads' | 'none'

export interface ResolvedOriginalExcel {
  base64: string | null
  fileName: string
  selectedSheetName: string | null
  selectedSheetNames: string[]
  source: OriginalExcelResolveSource
}

/**
 * 导出前解析原始 Excel：内存 store → IndexedDB → 最近上传
 * 找到后会回写到内存 store（由调用方传入 writeBack 回调）
 */
function sameExcelFileName(a: string, b: string): boolean {
  const normalize = (name: string) => name.trim().toLowerCase().replace(/\.xlsx?$/i, '')
  return !!a && !!b && normalize(a) === normalize(b)
}

export async function resolveOriginalExcel(options: {
  memoryBase64: string | null | undefined
  memoryFileName: string | null | undefined
  memorySheetName: string | null | undefined
  memorySheetNames: string[] | null | undefined
}): Promise<ResolvedOriginalExcel> {
  let fileName = options.memoryFileName || ''
  let selectedSheetName = options.memorySheetName || null
  let selectedSheetNames = options.memorySheetNames || []
  let base64 = options.memoryBase64 || null
  let source: OriginalExcelResolveSource = base64 ? 'memory' : 'none'

  const cached = (!base64 || !fileName || !selectedSheetName)
    ? await loadOriginalExcelCache()
    : null

  if (!base64 && cached?.base64) {
    // 若内存里有文件名，优先要求与缓存一致，避免串文件；无文件名则直接用缓存
    const nameOk = !fileName || !cached.fileName || sameExcelFileName(fileName, cached.fileName)
    if (nameOk) {
      base64 = cached.base64
      source = 'indexeddb'
      if (!fileName && cached.fileName) fileName = cached.fileName
      if (!selectedSheetName && cached.selectedSheetName) {
        selectedSheetName = cached.selectedSheetName
      }
      if ((!selectedSheetNames || selectedSheetNames.length === 0) && cached.selectedSheetNames?.length) {
        selectedSheetNames = cached.selectedSheetNames
      }
    }
  } else if (cached) {
    if (!fileName && cached.fileName) fileName = cached.fileName
    if (!selectedSheetName && cached.selectedSheetName) {
      selectedSheetName = cached.selectedSheetName
    }
    if ((!selectedSheetNames || selectedSheetNames.length === 0) && cached.selectedSheetNames?.length) {
      selectedSheetNames = cached.selectedSheetNames
    }
  }

  if (!base64 && fileName) {
    const fromRecent = loadOriginalExcelFromRecentUploads(fileName)
    if (fromRecent) {
      base64 = fromRecent
      source = 'recentUploads'
    }
  }

  return {
    base64,
    fileName,
    selectedSheetName,
    selectedSheetNames: selectedSheetNames || [],
    source
  }
}
