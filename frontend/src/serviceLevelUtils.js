/**
 * 服务级别匹配工具函数
 */

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

/**
 * 解析服务级别要求，提取关键信息
 * @param {string} serviceLevel - 服务级别要求，如 "7*24*3"
 * @returns {object} 解析结果
 */
function parseServiceLevel(serviceLevel) {
  if (!serviceLevel) return null
  
  // 移除空格并转换为小写
  const cleanLevel = serviceLevel.replace(/\s+/g, '').toLowerCase()
  
  // 匹配 7*24*N 格式
  const pattern1 = /7\*24\*(\d+)/i
  const match1 = cleanLevel.match(pattern1)
  if (match1) {
    return {
      type: '7*24',
      hours: parseInt(match1[1]),
      original: serviceLevel
    }
  }
  
  // 匹配 7*12*N 格式
  const pattern2 = /7\*12\*(\d+)/i
  const match2 = cleanLevel.match(pattern2)
  if (match2) {
    return {
      type: '7*12',
      hours: parseInt(match2[1]),
      original: serviceLevel
    }
  }
  
  // 匹配 5*9*N 格式
  const pattern3 = /5\*9\*(\d+)/i
  const match3 = cleanLevel.match(pattern3)
  if (match3) {
    return {
      type: '5*9',
      hours: parseInt(match3[1]),
      original: serviceLevel
    }
  }
  
  // 匹配 5*9*NCD 格式
  if (cleanLevel.includes('5*9*ncd')) {
    return {
      type: '5*9*NCD',
      hours: 24,
      original: serviceLevel
    }
  }
  
  // 匹配 5*9*NBD 格式
  if (cleanLevel.includes('5*9*nbd')) {
    return {
      type: '5*9*NBD',
      hours: 24,
      original: serviceLevel
    }
  }
  
  // 匹配 5*9*NCD 格式
  if (cleanLevel.includes('5*9*ncd')) {
    return {
      type: '5*9*NCD',
      hours: 24,
      original: serviceLevel
    }
  }
  
  // 匹配 5*9*NBR 格式
  if (cleanLevel.includes('5*9*nbr')) {
    return {
      type: '5*9*NBR',
      hours: 24,
      original: serviceLevel
    }
  }
  
  // 匹配 5*9*NBR 格式
  if (cleanLevel.includes('5*9*nbr')) {
    return {
      type: '5*9*NBR',
      hours: 24,
      original: serviceLevel
    }
  }
  
  // 匹配 7*24*NCD 格式
  if (cleanLevel.includes('7*24*ncd')) {
    return {
      type: '7*24*NCD',
      hours: 4,  // 工程师4小时
      original: serviceLevel
    }
  }
  
  // 匹配 N小时 格式
  const pattern4 = /(\d+)小时/i
  const match4 = cleanLevel.match(pattern4)
  if (match4) {
    return {
      type: 'hours',
      hours: parseInt(match4[1]),
      original: serviceLevel
    }
  }
  
  // 匹配 N天 格式
  const pattern5 = /(\d+)天/i
  const match5 = cleanLevel.match(pattern5)
  if (match5) {
    return {
      type: 'days',
      hours: parseInt(match5[1]) * 24,
      original: serviceLevel
    }
  }
  
  // 匹配 N分钟 格式
  const pattern6 = /(\d+)分钟/i
  const match6 = cleanLevel.match(pattern6)
  if (match6) {
    return {
      type: 'minutes',
      hours: parseInt(match6[1]) / 60,
      original: serviceLevel
    }
  }
  
  return null
}

/**
 * 解析响应时效，提取小时数
 * @param {string} responseTime - 响应时效，如 "2小时工程师和备件到达"
 * @returns {number} 小时数
 */
function parseResponseTime(responseTime) {
  if (!responseTime) return null
  
  // 移除空格并转换为小写
  const cleanTime = responseTime.replace(/\s+/g, '').toLowerCase()
  
  // 匹配 7*24*N 格式
  const pattern1 = /7\*24\*(\d+)/i
  const match1 = cleanTime.match(pattern1)
  if (match1) {
    return parseInt(match1[1])
  }
  
  // 匹配 7*12*N 格式
  const pattern2 = /7\*12\*(\d+)/i
  const match2 = cleanTime.match(pattern2)
  if (match2) {
    return parseInt(match2[1])
  }
  
  // 匹配 5*9*N 格式
  const pattern3 = /5\*9\*(\d+)/i
  const match3 = cleanTime.match(pattern3)
  if (match3) {
    return parseInt(match3[1])
  }
  
  // 匹配 7*24*NCD 格式
  if (cleanTime.includes('7*24*ncd')) {
    return 4  // 工程师4小时
  }
  
  // 匹配 5*9*NCD 格式
  if (cleanTime.includes('5*9*ncd')) {
    return 4  // 工程师4小时
  }
  
  // 匹配 5*9*NBD 格式
  if (cleanTime.includes('5*9*nbd')) {
    return 4  // 工程师4小时
  }
  
  // 匹配 N小时 格式
  const pattern4 = /(\d+)小时/i
  const match4 = cleanTime.match(pattern4)
  if (match4) {
    return parseInt(match4[1])
  }
  
  // 匹配 N天 格式
  const pattern5 = /(\d+)天/i
  const match5 = cleanTime.match(pattern5)
  if (match5) {
    return parseInt(match5[1]) * 24
  }
  
  // 匹配 N分钟 格式
  const pattern6 = /(\d+)分钟/i
  const match6 = cleanTime.match(pattern6)
  if (match6) {
    return parseInt(match6[1]) / 60
  }
  
  // 匹配 NCD (下一自然日)
  if (cleanTime.includes('ncd')) {
    return 24
  }
  
  // 匹配 NBD (下一工作日)
  if (cleanTime.includes('nbd')) {
    return 24
  }
  
  // 匹配 NBR (下一工作日)
  if (cleanTime.includes('nbr')) {
    return 24
  }
  
  return null
}

/**
 * 就高匹配服务级别
 * @param {string} requiredLevel - 要求的服务级别
 * @param {Array} availableLevels - 可用的服务级别列表
 * @returns {object|null} 匹配的服务级别信息
 */
function matchServiceLevel(requiredLevel, availableLevels) {
  if (!requiredLevel || !availableLevels || availableLevels.length === 0) {
    return null
  }
  
  const required = parseServiceLevel(requiredLevel)
  if (!required) {
    return null
  }
  
  // 解析所有可用服务级别的响应时效
  const parsedLevels = availableLevels.map(level => ({
    ...level,
    parsedHours: parseResponseTime(level.response_time)
  })).filter(level => level.parsedHours !== null)
  
  if (parsedLevels.length === 0) {
    return null
  }
  
  // 按响应时效排序（从快到慢）
  parsedLevels.sort((a, b) => a.parsedHours - b.parsedHours)
  
  // 找到最接近但不超过要求的服务级别，优先匹配完全相同的服务级别
  let bestMatch = null
  let minDifference = Infinity
  
  for (const level of parsedLevels) {
    if (level.parsedHours <= required.hours) {
      const difference = required.hours - level.parsedHours
      
      // 检查是否是相同的服务级别类型
      const isSameType = level.response_time.toLowerCase().includes(required.type.toLowerCase()) ||
                         required.original.toLowerCase().includes(level.response_time.toLowerCase().split('（')[0])
      
      // 优先选择：1) 差异更小的 2) 相同类型的 3) 系数更高的
      if (difference < minDifference || 
          (difference === minDifference && isSameType && !bestMatch?.isSameType) ||
          (difference === minDifference && isSameType === bestMatch?.isSameType && 
           parseFloat(level.coefficient) > parseFloat(bestMatch?.coefficient || 0))) {
        minDifference = difference
        bestMatch = { ...level, isSameType }
      }
    }
  }
  
  // 如果没有找到完全匹配的，选择最快的服务级别
  if (!bestMatch && parsedLevels.length > 0) {
    bestMatch = parsedLevels[0]
  }
  
  return bestMatch
}

/**
 * 获取所有服务级别
 * @returns {Promise<Array>} 服务级别列表
 */
async function fetchServiceLevels() {
  try {
    const response = await fetch(`${API_URL}/service-level/`)
    if (response.ok) {
      return await response.json()
    } else {
      console.error('获取服务级别失败:', response.status)
      return []
    }
  } catch (error) {
    console.error('获取服务级别失败:', error)
    return []
  }
}

/**
 * 计算服务级别调整后的价格
 * @param {number} originalPrice - 原始价格
 * @param {string} serviceLevel - 服务级别要求
 * @param {Array} availableLevels - 可用的服务级别列表
 * @returns {object} 计算结果
 */
function calculateServiceLevelPrice(originalPrice, serviceLevel, availableLevels) {
  if (!originalPrice || !serviceLevel) {
    return {
      originalPrice,
      adjustedPrice: originalPrice,
      coefficient: 1,
      matchedLevel: null,
      isAdjusted: false
    }
  }
  
  const matchedLevel = matchServiceLevel(serviceLevel, availableLevels)
  
  if (!matchedLevel) {
    return {
      originalPrice,
      adjustedPrice: originalPrice,
      coefficient: 1,
      matchedLevel: null,
      isAdjusted: false
    }
  }
  
  const coefficient = parseFloat(matchedLevel.coefficient)
  const adjustedPrice = originalPrice * coefficient
  
  return {
    originalPrice,
    adjustedPrice,
    coefficient,
    matchedLevel,
    isAdjusted: true
  }
}

export {
  parseServiceLevel,
  parseResponseTime,
  matchServiceLevel,
  fetchServiceLevels,
  calculateServiceLevelPrice
} 