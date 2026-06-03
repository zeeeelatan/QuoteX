/**
 * 通用虚拟列表 composable（固定行高）
 *
 * 用法：
 *   const tableWrapper = ref<HTMLElement | null>(null)
 *   const { visibleItems, topPadding, bottomPadding, startIndex } =
 *     useVirtualList(filteredTableData, 60, tableWrapper)
 *
 * 模板：
 *   <div class="table-wrapper" ref="tableWrapper">
 *     <table>
 *       <thead>...</thead>
 *       <tbody>
 *         <tr v-if="topPadding > 0" :style="{ height: topPadding + 'px' }"><td></td></tr>
 *         <tr v-for="(item, i) in visibleItems" :key="item._uid ?? (startIndex + i)">
 *           ...
 *         </tr>
 *         <tr v-if="bottomPadding > 0" :style="{ height: bottomPadding + 'px' }"><td></td></tr>
 *       </tbody>
 *     </table>
 *   </div>
 */
import { ref, computed, onMounted, onBeforeUnmount, watch, type Ref, type ComputedRef } from 'vue'

interface VirtualListResult<T> {
  visibleItems: ComputedRef<T[]>
  topPadding: ComputedRef<number>
  bottomPadding: ComputedRef<number>
  startIndex: ComputedRef<number>
  endIndex: ComputedRef<number>
  scrollToIndex: (index: number) => void
}

export function useVirtualList<T>(
  items: Ref<T[]> | ComputedRef<T[]>,
  rowHeight: number,
  scrollerRef: Ref<HTMLElement | null>,
  overscan = 8,
): VirtualListResult<T> {
  const scrollTop = ref(0)
  const viewportHeight = ref(0)

  const totalCount = computed(() => items.value.length)
  const totalHeight = computed(() => totalCount.value * rowHeight)

  const startIndex = computed(() => {
    if (totalCount.value === 0) return 0
    const raw = Math.floor(scrollTop.value / rowHeight) - overscan
    return Math.max(0, raw)
  })

  const endIndex = computed(() => {
    if (totalCount.value === 0) return 0
    const visibleCount = Math.ceil(viewportHeight.value / rowHeight) + overscan * 2
    return Math.min(totalCount.value, startIndex.value + visibleCount)
  })

  const visibleItems = computed(() => items.value.slice(startIndex.value, endIndex.value))
  const topPadding = computed(() => startIndex.value * rowHeight)
  const bottomPadding = computed(() => Math.max(0, totalHeight.value - endIndex.value * rowHeight))

  let rafScheduled = false
  const onScroll = () => {
    if (!scrollerRef.value || rafScheduled) return
    rafScheduled = true
    requestAnimationFrame(() => {
      if (scrollerRef.value) scrollTop.value = scrollerRef.value.scrollTop
      rafScheduled = false
    })
  }

  let resizeObserver: ResizeObserver | null = null
  const measureViewport = () => {
    if (scrollerRef.value) viewportHeight.value = scrollerRef.value.clientHeight
  }

  onMounted(() => {
    measureViewport()
    if (scrollerRef.value) {
      scrollerRef.value.addEventListener('scroll', onScroll, { passive: true })
      if (typeof ResizeObserver !== 'undefined') {
        resizeObserver = new ResizeObserver(() => measureViewport())
        resizeObserver.observe(scrollerRef.value)
      } else {
        window.addEventListener('resize', measureViewport)
      }
    }
  })

  onBeforeUnmount(() => {
    if (scrollerRef.value) scrollerRef.value.removeEventListener('scroll', onScroll)
    if (resizeObserver) resizeObserver.disconnect()
    else window.removeEventListener('resize', measureViewport)
  })

  // 当外部 ref 异步赋值时（v-if 渲染容器）也要绑定
  watch(scrollerRef, (el, oldEl) => {
    if (oldEl) oldEl.removeEventListener('scroll', onScroll)
    if (el) {
      el.addEventListener('scroll', onScroll, { passive: true })
      measureViewport()
      if (resizeObserver) {
        if (oldEl) resizeObserver.unobserve(oldEl)
        resizeObserver.observe(el)
      }
    }
  })

  // 列表长度或筛选变化后，确保 scrollTop 不超过新的总高度
  watch(totalCount, () => {
    if (!scrollerRef.value) return
    const maxScroll = Math.max(0, totalHeight.value - viewportHeight.value)
    if (scrollerRef.value.scrollTop > maxScroll) {
      scrollerRef.value.scrollTop = maxScroll
      scrollTop.value = maxScroll
    }
  })

  const scrollToIndex = (index: number) => {
    if (!scrollerRef.value) return
    scrollerRef.value.scrollTop = Math.max(0, index * rowHeight)
  }

  return { visibleItems, topPadding, bottomPadding, startIndex, endIndex, scrollToIndex }
}
