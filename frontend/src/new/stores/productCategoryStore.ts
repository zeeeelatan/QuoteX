/**
 * 产品分类状态管理
 * 使用 localStorage 持久化，按用户隔离
 */

import { reactive, watch } from 'vue'
import { getStorageKeyPrefix } from './authStore'

// 默认产品分类
const DEFAULT_CATEGORIES: ProductCategory[] = [
  {
    id: 'maintenance',
    name: '维保服务报价',
    icon: 'shield_with_heart',
    description: '定义维保服务核心参数与AI报价模型逻辑，支持灵活定价策略'
  },
  {
    id: 'onsite',
    name: '驻场服务报价',
    icon: 'person_pin_circle',
    description: '配置驻场服务人员、工时及服务级别定价'
  },
  {
    id: 'itsupport',
    name: 'IT服务支持报价（单价框架 / 据实结算）',
    icon: 'headset_mic',
    description: '单价框架 / 据实结算模式配置'
  },
  {
    id: 'inspection',
    name: '巡检服务报价',
    icon: 'visibility',
    description: '定期巡检服务路线、频率及定价策略'
  },
  {
    id: 'hybrid',
    name: '混合服务报价',
    icon: 'layers',
    description: '组合多种服务类型的综合报价方案'
  },
  {
    id: 'procurement',
    name: '设备/备件采购报价',
    icon: 'shopping_cart',
    description: '硬件设备及备件采购定价与折扣规则'
  },
  {
    id: 'integration',
    name: '系统集成报价',
    icon: 'memory',
    description: '系统集成项目工程量评估与定价'
  },
  {
    id: 'single',
    name: '单次服务报价（一价全包）',
    icon: 'confirmation_number',
    description: '一口价模式单次服务定价配置'
  },
  {
    id: 'relocation',
    name: '搬迁服务报价',
    icon: 'local_shipping',
    description: '设备搬迁工程量评估与计费标准'
  },
  {
    id: 'leasing',
    name: '设备/备件租赁报价',
    icon: 'autorenew',
    description: '租赁期限、费率及残值处理规则'
  },
  {
    id: 'weakcurrent',
    name: '弱电实施报价',
    icon: 'electrical_services',
    description: '弱电工程布线、安装及调试定价'
  },
  {
    id: 'cloud',
    name: '云服务报价',
    icon: 'cloud',
    description: '云资源订阅、迁移及运维服务定价'
  },
  {
    id: 'chain',
    name: '连锁门店服务报价',
    icon: 'storefront',
    description: '连锁门店统一服务定价与管理'
  }
]

// localStorage key（与 getStorageKeyPrefix 组合实现按用户隔离）
const STORAGE_KEY = 'product_categories'

function getStorageKey(): string {
  return getStorageKeyPrefix() + STORAGE_KEY
}

// 产品分类接口
export interface ProductCategory {
  id: string
  name: string
  icon: string
  description: string
}

// 从 localStorage 加载分类（按用户隔离）
function loadFromStorage(): ProductCategory[] {
  try {
    const stored = localStorage.getItem(getStorageKey())
    if (stored) {
      const parsed = JSON.parse(stored)
      if (Array.isArray(parsed) && parsed.length > 0) {
        return parsed
      }
    }
  } catch (e) {
    console.warn('[ProductCategoryStore] Failed to load from localStorage:', e)
  }
  return DEFAULT_CATEGORIES
}

// 保存到 localStorage（按用户隔离）
function saveToStorage(categories: ProductCategory[]): void {
  try {
    localStorage.setItem(getStorageKey(), JSON.stringify(categories))
  } catch (e) {
    console.warn('[ProductCategoryStore] Failed to save to localStorage:', e)
  }
}

// 响应式状态
const categories = reactive<ProductCategory[]>(loadFromStorage())

// 监听变化并自动保存
watch(
  () => [...categories],
  (newCategories) => {
    saveToStorage(newCategories)
  },
  { deep: true }
)

// ========== 公开 API ==========

/**
 * 获取所有产品分类（响应式）
 */
export function useProductCategories() {
  return {
    categories,
    /**
     * 添加新分类
     */
    addCategory(category: Omit<ProductCategory, 'id'> & { id?: string }): ProductCategory | null {
      const id = category.id || `custom_${Date.now()}`

      // 检查 ID 是否已存在
      if (categories.some(c => c.id === id)) {
        console.warn('[ProductCategoryStore] Category ID already exists:', id)
        return null
      }

      // 检查名称是否已存在
      if (categories.some(c => c.name === category.name)) {
        console.warn('[ProductCategoryStore] Category name already exists:', category.name)
        return null
      }

      const newCategory: ProductCategory = {
        id,
        name: category.name,
        icon: category.icon,
        description: category.description || ''
      }

      categories.push(newCategory)
      console.log('[ProductCategoryStore] Added category:', newCategory)
      return newCategory
    },

    /**
     * 更新分类
     */
    updateCategory(id: string, updates: Partial<Omit<ProductCategory, 'id'>>): boolean {
      const index = categories.findIndex(c => c.id === id)
      if (index === -1) {
        console.warn('[ProductCategoryStore] Category not found:', id)
        return false
      }

      // 如果更新名称，检查是否与其他分类冲突
      if (updates.name && updates.name !== categories[index].name) {
        const exists = categories.some((c, i) => i !== index && c.name === updates.name)
        if (exists) {
          console.warn('[ProductCategoryStore] Category name already exists:', updates.name)
          return false
        }
      }

      Object.assign(categories[index], updates)
      console.log('[ProductCategoryStore] Updated category:', id)
      return true
    },

    /**
     * 删除分类
     */
    deleteCategory(id: string): boolean {
      const index = categories.findIndex(c => c.id === id)
      if (index === -1) {
        console.warn('[ProductCategoryStore] Category not found:', id)
        return false
      }

      // 不允许删除默认分类
      if (DEFAULT_CATEGORIES.some(c => c.id === id)) {
        console.warn('[ProductCategoryStore] Cannot delete default category:', id)
        return false
      }

      categories.splice(index, 1)
      console.log('[ProductCategoryStore] Deleted category:', id)
      return true
    },

    /**
     * 根据 ID 获取分类
     */
    getCategoryById(id: string): ProductCategory | undefined {
      return categories.find(c => c.id === id)
    },

    /**
     * 根据名称获取分类
     */
    getCategoryByName(name: string): ProductCategory | undefined {
      return categories.find(c => c.name === name)
    },

    /**
     * 获取所有分类名称列表
     */
    getCategoryNames(): string[] {
      return categories.map(c => c.name)
    },

    /**
     * 重置为默认分类
     */
    resetToDefault(): void {
      categories.splice(0, categories.length, ...DEFAULT_CATEGORIES)
      console.log('[ProductCategoryStore] Reset to default categories')
    },

    /**
     * 检查是否为默认分类
     */
    isDefaultCategory(id: string): boolean {
      return DEFAULT_CATEGORIES.some(c => c.id === id)
    }
  }
}

// 导出类型
export type { ProductCategory }

// 导出默认分类常量（用于参考）
export { DEFAULT_CATEGORIES }
