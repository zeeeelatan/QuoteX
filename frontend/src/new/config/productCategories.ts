/**
 * 产品分类配置
 * 用于产品分类管理和服务条款管理之间的关联
 */

export interface ProductCategory {
  id: string
  name: string
  icon: string
  description: string
}

export const PRODUCT_CATEGORIES: ProductCategory[] = [
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

// 获取所有产品分类名称列表
export function getProductCategoryNames(): string[] {
  return PRODUCT_CATEGORIES.map(cat => cat.name)
}

// 根据 ID 获取产品分类
export function getCategoryById(id: string): ProductCategory | undefined {
  return PRODUCT_CATEGORIES.find(cat => cat.id === id)
}

// 根据名称获取产品分类 ID
export function getCategoryIdByName(name: string): string | undefined {
  const category = PRODUCT_CATEGORIES.find(cat => cat.name === name)
  return category?.id
}
