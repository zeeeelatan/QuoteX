export const QUOTE_TYPE_MAINTENANCE = 'maintenance'
export const QUOTE_TYPE_ONSITE = 'onsite'
export const QUOTE_TYPE_RELOCATION = 'relocation'
export const QUOTE_TYPE_LENOVO = 'lenovo'

export const QUOTE_TYPE_LABELS: Record<string, string> = {
  [QUOTE_TYPE_MAINTENANCE]: '设备维保',
  [QUOTE_TYPE_ONSITE]: '驻场服务',
  [QUOTE_TYPE_RELOCATION]: '搬迁服务',
  [QUOTE_TYPE_LENOVO]: '联想框架'
}

export function getQuoteTypeLabel(quoteType?: string | null): string {
  if (!quoteType) return QUOTE_TYPE_LABELS[QUOTE_TYPE_MAINTENANCE]
  return QUOTE_TYPE_LABELS[quoteType] || quoteType
}
