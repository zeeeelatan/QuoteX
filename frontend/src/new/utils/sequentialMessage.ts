import { ElMessage } from 'element-plus'

type MessageType = 'success' | 'warning' | 'info' | 'error'

interface QueuedMessage {
  type: MessageType
  message: string
  duration?: number
}

/** 单通道顺序消息：同一时间只展示一条，关闭后再显示下一条，避免弹窗叠加 */
const queue: QueuedMessage[] = []
let generation = 0
let showing = false

function defaultDuration(type: MessageType, duration?: number): number {
  if (duration !== undefined) return duration
  if (type === 'error') return 4000
  if (type === 'warning') return 3000
  return 2200
}

function showNext() {
  if (showing || queue.length === 0) return
  const item = queue.shift()!
  const duration = defaultDuration(item.type, item.duration)
  const gen = ++generation
  showing = true
  ElMessage({
    type: item.type,
    message: item.message,
    duration,
    showClose: true,
    onClose: () => {
      if (gen !== generation) return
      showing = false
      showNext()
    },
  })
}

export function sequentialMessage(type: MessageType, message: string, duration?: number) {
  queue.push({ type, message, duration })
  showNext()
}

export function clearSequentialMessages() {
  queue.length = 0
  generation += 1
  showing = false
  ElMessage.closeAll()
}

export const seqMsg = {
  success: (message: string, duration?: number) => sequentialMessage('success', message, duration),
  warning: (message: string, duration?: number) => sequentialMessage('warning', message, duration),
  info: (message: string, duration?: number) => sequentialMessage('info', message, duration),
  error: (message: string, duration?: number) => sequentialMessage('error', message, duration),
}
