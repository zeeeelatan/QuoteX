<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="isOpen" class="modal-overlay" @click.self="handleOverlayClick">
        <div
          class="modal-window"
          :class="{
            'maximized': isMaximized,
            'minimized': isMinimized
          }"
          :style="windowStyle"
          @mousedown="handleMouseDown"
        >
          <!-- 标题栏 -->
          <div class="modal-header" @mousedown="handleHeaderMouseDown">
            <div class="header-left">
              <span class="material-symbols-outlined header-icon">inventory_2</span>
              <span class="header-title">产品数据库</span>
            </div>
            <div class="header-right">
              <button class="window-btn" @click="toggleMinimize" title="最小化">
                <span class="material-symbols-outlined">remove</span>
              </button>
              <button class="window-btn" @click="toggleMaximize" title="最大化">
                <span class="material-symbols-outlined">{{ isMaximized ? 'crop_square' : 'check_box_outline_blank' }}</span>
              </button>
              <button class="window-btn close-btn" @click="close" title="关闭">
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>

          <!-- 内容区域 -->
          <div class="modal-content" v-show="!isMinimized">
            <ProductDatabase @go-home="close" />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import ProductDatabase from '../views/ProductDatabase.vue'

const props = defineProps<{
  isOpen: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

// 窗口状态
const isMaximized = ref(false)
const isMinimized = ref(false)
const windowPosition = ref({ x: 0, y: 0 })
const windowSize = ref({ width: 1200, height: 700 })

// 拖拽状态
const isDragging = ref(false)
const dragOffset = ref({ x: 0, y: 0 })

// 计算窗口样式
const windowStyle = computed(() => {
  if (isMaximized.value) {
    return {
      left: '0px',
      top: '0px',
      width: '100vw',
      height: 'calc(100vh - 70px)',
      transform: 'none'
    }
  }

  if (isMinimized.value) {
    return {
      left: `${windowPosition.value.x}px`,
      top: 'calc(100vh - 50px)',
      width: '200px',
      height: '40px',
      transform: 'none'
    }
  }

  return {
    left: `${windowPosition.value.x}px`,
    top: `${windowPosition.value.y}px`,
    width: `${windowSize.value.width}px`,
    height: `${windowSize.value.height}px`,
    transform: 'none'
  }
})

// 初始化窗口位置
const initializePosition = () => {
  const x = (window.innerWidth - windowSize.value.width) / 2
  const y = (window.innerHeight - windowSize.value.height) / 2 + 35
  windowPosition.value = { x, y }
}

// 监听弹窗打开状态
watch(() => props.isOpen, (newValue) => {
  if (newValue) {
    initializePosition()
    isMaximized.value = false
    isMinimized.value = false
  }
})

// 关闭弹窗
const close = () => {
  emit('close')
}

// 点击遮罩层关闭（如果未最大化）
const handleOverlayClick = () => {
  if (!isMaximized.value && !isMinimized.value) {
    close()
  }
}

// 切换最大化
const toggleMaximize = () => {
  isMaximized.value = !isMaximized.value
  if (isMaximized.value) {
    isMinimized.value = false
  }
}

// 切换最小化
const toggleMinimize = () => {
  isMinimized.value = !isMinimized.value
  if (isMinimized.value) {
    isMaximized.value = false
  }
}

// 拖拽功能
const handleMouseDown = (e: MouseEvent) => {
  if (isMaximized.value || isMinimized.value) return
  // 只在标题栏区域可以拖拽
  if ((e.target as HTMLElement).closest('.modal-header')) {
    isDragging.value = true
    dragOffset.value = {
      x: e.clientX - windowPosition.value.x,
      y: e.clientY - windowPosition.value.y
    }
  }
}

const handleHeaderMouseDown = (e: MouseEvent) => {
  if (isMaximized.value || isMinimized.value) return
  isDragging.value = true
  dragOffset.value = {
    x: e.clientX - windowPosition.value.x,
    y: e.clientY - windowPosition.value.y
  }

  const handleMouseMove = (e: MouseEvent) => {
    if (!isDragging.value) return
    windowPosition.value = {
      x: e.clientX - dragOffset.value.x,
      y: e.clientY - dragOffset.value.y
    }
  }

  const handleMouseUp = () => {
    isDragging.value = false
    document.removeEventListener('mousemove', handleMouseMove)
    document.removeEventListener('mouseup', handleMouseUp)
  }

  document.addEventListener('mousemove', handleMouseMove)
  document.addEventListener('mouseup', handleMouseUp)
}
</script>

<style scoped>
.modal-overlay {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.3);
  z-index: 9998;
}

.modal-window {
  position: fixed;
  background-color: #0B1120;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.2s ease;
}

.modal-window.maximized {
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
}

.modal-window.minimized {
  position: fixed;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  border-radius: 0.5rem 0.5rem 0 0;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #151e32;
  border-bottom: 1px solid #232f48;
  cursor: move;
  user-select: none;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.header-icon {
  color: #135bec;
  font-size: 1.25rem;
}

.header-title {
  color: #ffffff;
  font-size: 0.875rem;
  font-weight: 500;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.window-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.15s;
}

.window-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.window-btn.close-btn:hover {
  background-color: #ef4444;
  color: #ffffff;
}

.window-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.modal-content {
  flex: 1;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

/* 确保 ProductDatabase 组件在弹窗中正确显示 */
.modal-content :deep(.product-database) {
  height: 100%;
  padding-top: 0;
  overflow: hidden;
}

/* 确保主内容区域有正确的高度 */
.modal-content :deep(.main-content) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* 确保结果区域有正确的高度 */
.modal-content :deep(.results-area) {
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* 确保滚动区域有正确的高度 */
.modal-content :deep(.results-list-scroll) {
  min-height: 100px;
  max-height: 100%;
}

/* 添加滚动条样式 */
.modal-content :deep(.results-list-scroll)::-webkit-scrollbar {
  width: 8px;
}

.modal-content :deep(.results-list-scroll)::-webkit-scrollbar-track {
  background: #1a2332;
  border-radius: 4px;
}

.modal-content :deep(.results-list-scroll)::-webkit-scrollbar-thumb {
  background: #3a4a5f;
  border-radius: 4px;
}

.modal-content :deep(.results-list-scroll)::-webkit-scrollbar-thumb:hover {
  background: #4a5a6f;
}

/* 弹窗动画 */
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}

.modal-enter-active .modal-window,
.modal-leave-active .modal-window {
  transition: transform 0.2s ease, opacity 0.2s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-from .modal-window,
.modal-leave-to .modal-window {
  transform: scale(0.95);
  opacity: 0;
}
</style>
