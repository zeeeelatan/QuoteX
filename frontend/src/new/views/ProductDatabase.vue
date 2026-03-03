<template>
  <div class="product-database">
    <!-- Hero Search Section -->
    <section class="hero-section">
      <div class="hero-bg"></div>
      <div class="hero-overlay"></div>
      <div class="hero-content">
        <div class="hero-text">
          <h1 class="hero-title">设备型号智能搜索</h1>
          <p class="hero-subtitle">输入准确型号以获取AI报价数据，支持模糊匹配与多维度筛选</p>
        </div>

        <!-- Search Box and Filter Button Row -->
        <div class="search-filter-row">
          <!-- Search Box -->
          <div class="search-wrapper">
            <div class="search-box">
              <div class="search-icon">
                <span class="material-symbols-outlined">search</span>
              </div>
              <input
                v-model="searchKeyword"
                @input="onSearchInput"
                class="search-input"
                placeholder="请输入设备型号 (如: iPhone 15 Pro Max)"
              />
              <div class="search-btn-container">
                <button @click="handleSearch" class="search-btn">搜索</button>
              </div>
            </div>
          </div>

          <!-- Filter Toggle Button -->
          <button
            @click="toggleFilters"
            class="filter-toggle-btn"
            :class="{ 'active': hasActiveFilters }"
          >
            <span class="material-symbols-outlined">tune</span>
            <span class="filter-toggle-text">筛选条件</span>
            <span class="material-symbols-outlined dropdown-arrow" :class="{ 'rotated': filtersOpen }">expand_more</span>
          </button>
        </div>

        <!-- Hot Search Chips -->
        <div class="hot-chips-row">
          <span class="hot-label">热门:</span>
          <div class="hot-chips-list">
            <button
              v-for="hot in hotSearches"
              :key="hot"
              @click="searchKeyword = hot; handleSearch()"
              class="hot-chip"
            >
              {{ hot }}
            </button>
          </div>
        </div>

        <!-- Filter Panel (Shown when filtersOpen is true) -->
        <div v-show="filtersOpen" class="filter-panel">
          <div class="filter-panel-header">
            <h3 class="filter-panel-title">筛选条件</h3>
            <button @click="resetFilters" class="reset-link">
              <span class="material-symbols-outlined">refresh</span>
              重置筛选
            </button>
          </div>

          <div class="filter-content">
            <!-- Data Source Filter -->
            <div class="filter-item">
              <label class="filter-label">数据来源</label>
              <div class="radio-group">
                <label class="radio-label">
                  <input v-model="filters.source" value="datacenter" type="radio" name="source" />
                  <span class="radio-dot"></span>
                  <span class="radio-text">数据中心设备</span>
                </label>
                <label class="radio-label">
                  <input v-model="filters.source" value="office" type="radio" name="source" />
                  <span class="radio-dot"></span>
                  <span class="radio-text">办公设备</span>
                </label>
                <label class="radio-label">
                  <input v-model="filters.source" value="hybrid" type="radio" name="source" />
                  <span class="radio-dot"></span>
                  <span class="radio-text">全部</span>
                </label>
              </div>
            </div>

            <!-- Category Filter -->
            <div class="filter-item">
              <label class="filter-label">一级分类</label>
              <div class="checkbox-group">
                <label v-for="cat in primaryCategories" :key="cat" class="checkbox-label">
                  <div class="checkbox-container">
                    <input
                      v-model="filters.categories"
                      :value="cat"
                      type="checkbox"
                      class="checkbox-input"
                    />
                    <span class="checkbox-check">
                      <span class="material-symbols-outlined">check</span>
                    </span>
                  </div>
                  <span class="checkbox-text">{{ cat }}</span>
                  <span class="checkbox-count">{{ getCategoryCount(cat) }}</span>
                </label>
              </div>
            </div>

            <!-- Price Range Filter -->
            <div class="filter-item">
              <label class="filter-label">价格区间 (¥)</label>
              <div class="price-range-box">
                <div class="price-inputs">
                  <input
                    v-model.number="filters.minPrice"
                    class="price-input"
                    type="number"
                    placeholder="最低价"
                  />
                  <span class="price-separator">-</span>
                  <input
                    v-model.number="filters.maxPrice"
                    class="price-input"
                    type="number"
                    placeholder="最高价"
                  />
                </div>
              </div>
            </div>

            <!-- Manufacturer Filter -->
            <div class="filter-item">
              <label class="filter-label">厂商</label>
              <div class="manufacturer-grid">
                <button
                  v-for="mfg in topManufacturers"
                  :key="mfg"
                  @click="toggleManufacturer(mfg)"
                  :class="['manufacturer-chip', { active: filters.manufacturers.includes(mfg) }]"
                >
                  {{ mfg }}
                </button>
              </div>
            </div>
          </div>

          <!-- Apply Button -->
          <div class="filter-footer">
            <button @click="applyFilters" class="apply-filter-btn">
              应用筛选
            </button>
          </div>
        </div>
      </div>
    </section>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Results Area -->
      <div class="results-area">
        <!-- Results Header (Fixed) -->
        <div class="results-header">
          <div class="results-count">
            <p class="count-label">搜索结果</p>
            <span class="count-badge">{{ total }}</span>
          </div>
          <div class="results-controls">
            <!-- Column Filter Toggle -->
            <button @click="toggleColumnFilter" class="column-filter-btn" :class="{ 'active': showColumnFilter }">
              <span class="material-symbols-outlined">view_column</span>
              <span>列筛选</span>
            </button>
            <div class="sort-select">
              <span class="sort-label">排序:</span>
              <select v-model="sortBy" class="sort-input">
                <option value="relevance">综合相关度</option>
                <option value="price_asc">价格 (低到高)</option>
                <option value="price_desc">价格 (高到低)</option>
                <option value="model">型号名称</option>
              </select>
            </div>
          </div>
        </div>

        <!-- Column Filter Panel (Excel-style Field Filter) -->
        <div v-show="showColumnFilter" class="column-filter-panel">
          <div class="column-filter-header">
            <span class="column-filter-title">字段筛选</span>
            <button @click="resetColumnFilters" class="reset-column-btn">
              <span class="material-symbols-outlined">refresh</span>
              清空筛选
            </button>
          </div>
          <div class="field-filter-grid">
            <div
              v-for="field in dataSourceFields"
              :key="field.key"
              class="field-filter-item"
            >
              <button
                @click="toggleFieldFilter(field.key)"
                class="field-filter-trigger"
                :class="{ 'active': activeFilterColumn === field.key, 'has-filter': getFieldSelectedCount(field.key) > 0 }"
              >
                <span class="field-filter-label">{{ field.label }}</span>
                <span class="field-filter-count">{{ getFieldSelectedCount(field.key) }}</span>
                <span class="material-symbols-outlined dropdown-icon" :class="{ 'rotated': activeFilterColumn === field.key }">expand_more</span>
              </button>
              <div
                v-show="activeFilterColumn === field.key"
                class="field-filter-dropdown"
              >
                <div class="field-filter-actions">
                  <button @click="selectAllFieldValues(field.key)" class="filter-action-btn">全选</button>
                  <button @click="clearFieldValues(field.key)" class="filter-action-btn">清空</button>
                </div>
                <div class="field-filter-values">
                  <label
                    v-for="value in getFieldUniqueValues(field.key)"
                    :key="value"
                    class="field-value-checkbox"
                  >
                    <input
                      type="checkbox"
                      :checked="fieldValueFilters[field.key]?.includes(value)"
                      @change="toggleFieldValue(field.key, value)"
                      class="fv-checkbox"
                    />
                    <span class="fv-text">{{ value }}</span>
                  </label>
                  <div v-if="getFieldUniqueValues(field.key).length === 0" class="field-empty">
                    暂无数据
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Loading State -->
        <div v-if="loading" class="loading-state">
          <div class="spinner"></div>
          <p>搜索中...</p>
        </div>

        <!-- Empty State -->
        <div v-else-if="devices.length === 0" class="empty-state">
          <span class="material-symbols-outlined empty-icon">search_off</span>
          <p class="empty-text">暂无搜索结果</p>
          <p class="empty-hint">请尝试调整搜索关键词或筛选条件</p>
        </div>

        <!-- Results List (Scrollable) -->
        <div v-else class="results-list-scroll">
          <div class="results-list">
          <div
            v-for="device in paginatedDevices"
            :key="device.id"
            class="device-card"
            @click="showDeviceDetail(device)"
          >
            <!-- Device Image Placeholder -->
            <div class="device-image">
              <span class="material-symbols-outlined device-icon">devices</span>
              <span v-if="device.device_price" class="price-badge">
                ¥{{ formatPrice(device.device_price) }}
              </span>
            </div>

            <!-- Device Details -->
            <div class="device-details">
              <div class="device-header">
                <div class="device-title-section">
                  <h4 class="device-model">{{ device.model_number }}</h4>
                  <div class="device-tags">
                    <span v-if="device.manufacturer" class="tag tag-manufacturer">{{ device.manufacturer }}</span>
                    <span v-if="device.primary_category" class="tag tag-category">{{ device.primary_category }}</span>
                    <span v-if="device.secondary_category" class="tag tag-sub">{{ device.secondary_category }}</span>
                    <span v-if="device.tertiary_category" class="tag tag-sub">{{ device.tertiary_category }}</span>
                    <span v-if="device.device_series" class="tag tag-series">{{ device.device_series }}</span>
                    <span v-if="device.device_grade" class="tag tag-grade">{{ device.device_grade }}</span>
                  </div>
                </div>
                <div class="device-price-section">
                  <span class="price-label">设备价格</span>
                  <div class="device-price">
                    ¥{{ device.device_price ? formatPrice(device.device_price) : '---' }}
                  </div>
                </div>
              </div>

              <div class="device-divider"></div>

              <div class="device-footer">
                <div class="device-prices-inline">
                  <div class="inline-price-item">
                    <span class="inline-price-label">未税</span>
                    <span class="inline-price-value">¥{{ formatPrice(device.untaxedPrice) }}</span>
                  </div>
                  <div class="inline-price-item">
                    <span class="inline-price-label">6%</span>
                    <span class="inline-price-value price-6">¥{{ formatPrice(device.standardPrice6) }}</span>
                  </div>
                  <div class="inline-price-item">
                    <span class="inline-price-label">13%</span>
                    <span class="inline-price-value price-13">¥{{ formatPrice(device.standardPrice13) }}</span>
                  </div>
                </div>
                <div class="device-actions" @click.stop>
                  <button class="action-btn secondary" @click="showDeviceDetail(device)">详情</button>
                  <button class="action-btn primary" @click="addToQuotation(device)">
                    <span class="material-symbols-outlined">add_shopping_cart</span>
                    加入报价单
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Pagination -->
        <div v-if="totalPages > 1" class="pagination">
          <button
            @click="goToPage(currentPage - 1)"
            :disabled="currentPage === 1"
            class="page-btn"
          >
            <span class="material-symbols-outlined">chevron_left</span>
          </button>
          <button
            v-for="page in displayPages"
            :key="page"
            @click="goToPage(page)"
            :class="['page-num', { active: page === currentPage }]"
          >
            {{ page }}
          </button>
          <button
            @click="goToPage(currentPage + 1)"
            :disabled="currentPage === totalPages"
            class="page-btn"
          >
            <span class="material-symbols-outlined">chevron_right</span>
          </button>
        </div>
        </div>
      </div>
    </main>

    <!-- Device Detail Modal -->
    <Teleport to="body">
      <div v-if="selectedDevice" class="modal-overlay" @click.self="closeModal">
        <div class="modal-dialog" @click.stop>
          <div class="modal-header">
            <h3 class="modal-title">设备详情</h3>
            <button @click="closeModal" class="modal-close">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="modal-content">
            <div class="detail-image">
              <span class="material-symbols-outlined detail-icon">devices</span>
            </div>
            <div class="detail-info">
              <h4 class="detail-model">{{ selectedDevice.model_number }}</h4>
              <div class="detail-tags">
                <span v-if="selectedDevice.manufacturer" class="detail-tag">{{ selectedDevice.manufacturer }}</span>
                <span v-if="selectedDevice.primary_category" class="detail-tag">{{ selectedDevice.primary_category }}</span>
                <span v-if="selectedDevice.device_grade" class="detail-tag">{{ selectedDevice.device_grade }}</span>
              </div>
              <div class="detail-grid">
                <div class="detail-item">
                  <span class="detail-label">设备价格</span>
                  <span class="detail-value">¥{{ selectedDevice.device_price ? formatPrice(selectedDevice.device_price) : '---' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">一级分类</span>
                  <span class="detail-value">{{ selectedDevice.primary_category || '---' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">二级分类</span>
                  <span class="detail-value">{{ selectedDevice.secondary_category || '---' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">三级分类</span>
                  <span class="detail-value">{{ selectedDevice.tertiary_category || '---' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">设备系列</span>
                  <span class="detail-value">{{ selectedDevice.device_series || '---' }}</span>
                </div>
                <div class="detail-item">
                  <span class="detail-label">成色等级</span>
                  <span class="detail-value">{{ selectedDevice.device_grade || '---' }}</span>
                </div>
              </div>

              <!-- Maintenance Prices Section in Modal -->
              <div v-if="selectedDevice.untaxedPrice !== undefined" class="detail-prices-section">
                <h5 class="detail-section-title">维保价格</h5>
                <div class="detail-prices-grid">
                  <div class="detail-price-card">
                    <span class="detail-price-label">未税维保单价</span>
                    <span class="detail-price-value">¥{{ formatPrice(selectedDevice.untaxedPrice) }}</span>
                  </div>
                  <div class="detail-price-card price-6">
                    <span class="detail-price-label">标准维保单价（6%）</span>
                    <span class="detail-price-value">¥{{ formatPrice(selectedDevice.standardPrice6) }}</span>
                  </div>
                  <div class="detail-price-card price-13">
                    <span class="detail-price-label">标准维保单价（13%）</span>
                    <span class="detail-price-value">¥{{ formatPrice(selectedDevice.standardPrice13) }}</span>
                  </div>
                </div>
              </div>
              <div v-if="selectedDevice.remarks" class="detail-remarks">
                <span class="remarks-label">备注:</span>
                <span class="remarks-text">{{ selectedDevice.remarks }}</span>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button @click="closeModal" class="modal-btn cancel">关闭</button>
            <button @click="addToQuotation(selectedDevice); closeModal()" class="modal-btn confirm">
              <span class="material-symbols-outlined">add_shopping_cart</span>
              加入报价单
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

// Router
const router = useRouter()

// API URL - use environment variable or default
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
const searchKeyword = ref('')
const devices = ref<any[]>([])
const loading = ref(false)
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)
const sortBy = ref('relevance')
const selectedDevice = ref<any | null>(null)

// Filter dropdown state
const filtersOpen = ref(false)

// Maintenance rates cache (for price calculation)
const maintenanceRatesCache = ref<any[] | null>(null)

// Filters
const filters = ref({
  source: 'datacenter',
  categories: [] as string[],
  manufacturers: [] as string[],
  minPrice: null as number | null,
  maxPrice: null as number | null
})

// Computed: check if any filters are active
const hasActiveFilters = computed(() => {
  return filters.value.categories.length > 0 ||
         filters.value.manufacturers.length > 0 ||
         filters.value.minPrice !== null ||
         filters.value.maxPrice !== null ||
         filters.value.source !== 'datacenter'
})

// Computed: count active filters
const activeFilterCount = computed(() => {
  let count = 0
  if (filters.value.categories.length > 0) count++
  if (filters.value.manufacturers.length > 0) count++
  if (filters.value.minPrice !== null) count++
  if (filters.value.maxPrice !== null) count++
  if (filters.value.source !== 'datacenter') count++
  return count
})

// Hot searches
const hotSearches = ref([
  'iPhone 15 Pro',
  'MacBook Air M2',
  'RTX 4090',
  'H100',
  'Dell R740'
])

// Primary categories (will be populated from API)
const primaryCategories = ref<string[]>([])

// Top manufacturers (will be populated from API)
const topManufacturers = ref<string[]>([])

// Category counts
const categoryCounts = ref<Record<string, number>>({})

// Column filter state
const showColumnFilter = ref(false)
const activeFilterColumn = ref<string | null>(null)

// Define all available fields based on data source
const dataSourceFields = ref<any[]>([])

// Field value filters (for Excel-style filtering)
const fieldValueFilters = ref<Record<string, string[]>>({})

// Get available fields based on current data source
function getDataSourceFields(): any[] {
  const source = filters.value.source
  if (source === 'office') {
    return [
      { key: 'model_number', label: '型号' },
      { key: 'manufacturer', label: '厂商' },
      { key: 'primary_category', label: '一级分类' },
      { key: 'secondary_category', label: '二级分类' },
      { key: 'tertiary_category', label: '三级分类' },
      { key: 'device_series', label: '设备系列' },
      { key: 'device_grade', label: '成色等级' },
      { key: 'device_price', label: '设备价格' },
      { key: 'sku', label: 'SKU' },
      { key: 'remarks', label: '备注' }
    ]
  } else {
    // datacenter and hybrid use same fields
    return [
      { key: 'model_number', label: '型号' },
      { key: 'manufacturer', label: '厂商' },
      { key: 'primary_category', label: '一级分类' },
      { key: 'secondary_category', label: '二级分类' },
      { key: 'tertiary_category', label: '三级分类' },
      { key: 'device_series', label: '设备系列' },
      { key: 'device_grade', label: '成色等级' },
      { key: 'device_price', label: '设备价格' },
      { key: 'sku', label: 'SKU' },
      { key: 'remarks', label: '备注' }
    ]
  }
}

// Get unique values for a specific field from the current search results
function getFieldUniqueValues(fieldKey: string): string[] {
  const values = new Set<string>()
  devices.value.forEach(device => {
    const value = device[fieldKey]
    if (value !== null && value !== undefined && value !== '') {
      values.add(String(value))
    }
  })
  return Array.from(values).sort()
}

// Get selected count for a field
function getFieldSelectedCount(fieldKey: string): number {
  return fieldValueFilters.value[fieldKey]?.length || 0
}

// Toggle column filter panel
function toggleColumnFilter() {
  showColumnFilter.value = !showColumnFilter.value
  if (showColumnFilter.value) {
    dataSourceFields.value = getDataSourceFields()
  }
}

// Toggle field filter dropdown
function toggleFieldFilter(fieldKey: string) {
  if (activeFilterColumn.value === fieldKey) {
    activeFilterColumn.value = null
  } else {
    activeFilterColumn.value = fieldKey
  }
}

// Toggle field value selection
function toggleFieldValue(fieldKey: string, value: string) {
  if (!fieldValueFilters.value[fieldKey]) {
    fieldValueFilters.value[fieldKey] = []
  }
  const index = fieldValueFilters.value[fieldKey].indexOf(value)
  if (index > -1) {
    fieldValueFilters.value[fieldKey].splice(index, 1)
  } else {
    fieldValueFilters.value[fieldKey].push(value)
  }
}

// Select all values for a field
function selectAllFieldValues(fieldKey: string) {
  fieldValueFilters.value[fieldKey] = getFieldUniqueValues(fieldKey)
}

// Clear all values for a field
function clearFieldValues(fieldKey: string) {
  fieldValueFilters.value[fieldKey] = []
}

// Reset column filters
function resetColumnFilters() {
  fieldValueFilters.value = {}
  activeFilterColumn.value = null
}

// Apply field value filters to filtered devices
const fieldFilteredDevices = computed(() => {
  let result = [...filteredDevices.value]

  // Apply field value filters
  Object.keys(fieldValueFilters.value).forEach(fieldKey => {
    const selectedValues = fieldValueFilters.value[fieldKey]
    if (selectedValues && selectedValues.length > 0) {
      result = result.filter(device => {
        const value = device[fieldKey]
        return selectedValues.includes(String(value))
      })
    }
  })

  return result
})

// Navigate functions
const navigateToHome = () => router.push('/')
const navigateToQuotationGeneration = () => router.push('/quotation-generation')

// Toggle filters dropdown
function toggleFilters() {
  filtersOpen.value = !filtersOpen.value
}

// Apply filters
function applyFilters() {
  filtersOpen.value = false
  currentPage.value = 1
  fetchDevices()
}

// Format price
function formatPrice(price: any): string {
  const num = typeof price === 'string' ? parseFloat(price) : price
  if (isNaN(num)) return '0'
  return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',')
}

// Get category count
function getCategoryCount(category: string): number {
  return categoryCounts.value[category] || 0
}

// Toggle manufacturer
function toggleManufacturer(mfg: string) {
  const index = filters.value.manufacturers.indexOf(mfg)
  if (index > -1) {
    filters.value.manufacturers.splice(index, 1)
  } else {
    filters.value.manufacturers.push(mfg)
  }
}

// Reset filters
function resetFilters() {
  filters.value = {
    source: 'datacenter',
    categories: [],
    manufacturers: [],
    minPrice: null,
    maxPrice: null
  }
  searchKeyword.value = ''
  currentPage.value = 1
  fetchDevices()
}

// Fetch devices from API
async function fetchDevices() {
  loading.value = true
  try {
    // Load maintenance rates if not already loaded
    if (!maintenanceRatesCache.value) {
      try {
        const response = await axios.get(`${API_URL}/maintenance_rates/`)
        maintenanceRatesCache.value = response.data || []
      } catch (error) {
        console.error('Failed to load maintenance rates:', error)
        maintenanceRatesCache.value = []
      }
    }

    const params: any = {
      source: filters.value.source,
      limit: 100, // Get more results for client-side filtering
      offset: 0
    }

    if (searchKeyword.value) {
      params.model_number = searchKeyword.value
    }

    const response = await axios.get(`${API_URL}/devices/search/`, { params })
    const rawData = response.data.data || []
    total.value = response.data.total || 0

    // Calculate maintenance prices for each device
    devices.value = rawData.map((device: any) => {
      const devicePrice = parseFloat(device.device_price) || 0
      const rate = findMaintenanceRate(
        device.primary_category || '',
        device.secondary_category || '',
        device.tertiary_category || ''
      )

      // 未税维保单价
      const untaxedPrice = devicePrice * rate
      // 标准维保单价（6%）
      const standardPrice6 = untaxedPrice * 1.06
      // 标准维保单价（13%）
      const standardPrice13 = untaxedPrice * 1.13

      return {
        ...device,
        untaxedPrice,
        standardPrice6,
        standardPrice13,
        rate
      }
    })

    // Extract categories and manufacturers
    updateFiltersFromData(devices.value)
  } catch (error) {
    console.error('Failed to fetch devices:', error)
    devices.value = []
    total.value = 0
  } finally {
    loading.value = false
  }
}

// Find maintenance rate by categories (same logic as backend)
function findMaintenanceRate(primary: string, secondary: string, tertiary: string): number {
  if (!maintenanceRatesCache.value) return 0.02  // default rate

  const rates = maintenanceRatesCache.value

  // Try tertiary category match first
  if (primary && secondary && tertiary) {
    const match = rates.find((r: any) =>
      r.primary_category === primary &&
      r.secondary_category === secondary &&
      r.tertiary_category === tertiary
    )
    if (match) return match.rate
  }

  // Try secondary category match
  if (primary && secondary) {
    const match = rates.find((r: any) =>
      r.primary_category === primary &&
      r.secondary_category === secondary &&
      !r.tertiary_category
    )
    if (match) return match.rate
  }

  // Try primary category match
  if (primary) {
    const match = rates.find((r: any) =>
      r.primary_category === primary &&
      !r.secondary_category &&
      !r.tertiary_category
    )
    if (match) return match.rate
  }

  return 0.02  // default rate
}

// Update filter options from device data
function updateFiltersFromData(data: any[]) {
  const categories = new Set<string>()
  const manufacturers = new Set<string>()
  const counts: Record<string, number> = {}

  data.forEach(device => {
    if (device.primary_category) {
      categories.add(device.primary_category)
      counts[device.primary_category] = (counts[device.primary_category] || 0) + 1
    }
    if (device.manufacturer) {
      manufacturers.add(device.manufacturer)
    }
  })

  primaryCategories.value = Array.from(categories).sort()
  topManufacturers.value = Array.from(manufacturers).slice(0, 10)
  categoryCounts.value = counts
}

// Handle search
function handleSearch() {
  currentPage.value = 1
  fetchDevices()
}

// Debounce timer for search input
let searchDebounceTimer: ReturnType<typeof setTimeout> | null = null

// Handle search input with debounce
function onSearchInput() {
  if (searchDebounceTimer) {
    clearTimeout(searchDebounceTimer)
  }
  // Debounce for 300ms to avoid too many API calls
  searchDebounceTimer = setTimeout(() => {
    handleSearch()
  }, 300)
}

// Filtered and sorted devices
const filteredDevices = computed(() => {
  let result = [...devices.value]

  // Filter by categories
  if (filters.value.categories.length > 0) {
    result = result.filter(d =>
      filters.value.categories.includes(d.primary_category)
    )
  }

  // Filter by manufacturers
  if (filters.value.manufacturers.length > 0) {
    result = result.filter(d =>
      filters.value.manufacturers.includes(d.manufacturer)
    )
  }

  // Filter by price range
  if (filters.value.minPrice !== null) {
    result = result.filter(d =>
      d.device_price && parseFloat(d.device_price) >= filters.value.minPrice!
    )
  }
  if (filters.value.maxPrice !== null) {
    result = result.filter(d =>
      d.device_price && parseFloat(d.device_price) <= filters.value.maxPrice!
    )
  }

  // Sort
  switch (sortBy.value) {
    case 'price_asc':
      result.sort((a, b) =>
        (parseFloat(a.device_price) || 0) - (parseFloat(b.device_price) || 0)
      )
      break
    case 'price_desc':
      result.sort((a, b) =>
        (parseFloat(b.device_price) || 0) - (parseFloat(a.device_price) || 0)
      )
      break
    case 'model':
      result.sort((a, b) => a.model_number.localeCompare(b.model_number))
      break
    default:
      // relevance - keep original order (server-side sorting)
      break
  }

  return result
})

// Total pages - based on fieldFilteredDevices
const totalPages = computed(() => {
  return Math.ceil(fieldFilteredDevices.value.length / pageSize.value)
})

// Paginated devices - use fieldFilteredDevices instead of filteredDevices
const paginatedDevices = computed(() => {
  const start = (currentPage.value - 1) * pageSize.value
  const end = start + pageSize.value
  return fieldFilteredDevices.value.slice(start, end)
})

// Display page numbers
const displayPages = computed(() => {
  const pages: number[] = []
  const max = 5
  const total = totalPages.value
  const current = currentPage.value

  if (total <= max) {
    for (let i = 1; i <= total; i++) {
      pages.push(i)
    }
  } else {
    if (current <= 3) {
      for (let i = 1; i <= 4; i++) pages.push(i)
      pages.push(-1) // ellipsis
      pages.push(total)
    } else if (current >= total - 2) {
      pages.push(1)
      pages.push(-1)
      for (let i = total - 3; i <= total; i++) pages.push(i)
    } else {
      pages.push(1)
      pages.push(-1)
      for (let i = current - 1; i <= current + 1; i++) pages.push(i)
      pages.push(-1)
      pages.push(total)
    }
  }

  return pages.filter(p => p !== -1 || pages.indexOf(p) === pages.lastIndexOf(p))
})

// Go to page
function goToPage(page: number) {
  if (page >= 1 && page <= totalPages.value) {
    currentPage.value = page
  }
}

// Show device detail
function showDeviceDetail(device: any) {
  selectedDevice.value = device
}

// Close modal
function closeModal() {
  selectedDevice.value = null
}

// Add to quotation (save to flow data)
function addToQuotation(device: any) {
  // Save to flow data for use in quotation generation
  const quotationItem = {
    model: device.model_number,
    manufacturer: device.manufacturer,
    matchedModel: device.model_number,
    originalPrice: parseFloat(device.device_price) || 0,
    suggestedPrice: parseFloat(device.device_price) || 0,
    finalPrice: parseFloat(device.device_price) || 0,
    primaryCategory: device.primary_category,
    secondaryCategory: device.secondary_category,
    tertiaryCategory: device.tertiary_category,
    deviceGrade: device.device_grade,
    deviceSeries: device.device_series
  }

  // Get existing flow data or create new array
  const existingDataStr = sessionStorage.getItem('quotation_flow_cart')
  const existingData = existingDataStr ? JSON.parse(existingDataStr) : []
  existingData.push(quotationItem)
  sessionStorage.setItem('quotation_flow_cart', JSON.stringify(existingData))

  alert(`已将 ${device.model_number} 加入报价单！`)
}

// Watch for filter changes
watch(() => [filters.value.source, filters.value.categories, filters.value.manufacturers, filters.value.minPrice, filters.value.maxPrice], () => {
  currentPage.value = 1
}, { deep: true })

// On mounted
onMounted(() => {
  fetchDevices()
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.product-database {
  font-family: "Noto Sans SC", sans-serif;
  background-color: #101622;
  color: white;
  display: flex;
  flex-direction: column;
  flex: 1;
  padding-top: 72px; /* Space for fixed header - reduced */
}

/* Hero Section */
.hero-section {
  position: relative;
  padding: 1rem 1rem 1.5rem 1rem; /* Reduced from 3rem 1rem 2rem */
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.hero-bg {
  position: absolute;
  inset: 0;
  background-image: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse"><path d="M 10 0 L 0 0 0 10" fill="none" stroke="%23324467" stroke-width="0.5" opacity="0.3"/></pattern></defs><rect width="100" height="100" fill="url(%23grid)"/></svg>');
  opacity: 0.3;
  z-index: 0;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: linear-gradient(to bottom, rgba(17, 23, 34, 0.8), #101622);
  z-index: 0;
}

.hero-content {
  position: relative;
  z-index: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem; /* Reduced from 2rem */
  width: 100%;
  max-width: 1200px;
}

/* Hero Text */
.hero-text {
  text-align: center;
  display: flex;
  flex-direction: column;
  gap: 0.25rem; /* Reduced from 0.5rem */
  margin-bottom: 0; /* Removed margin */
}

.hero-title {
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  font-size: 1.75rem; /* Reduced from 2.5rem */
  font-weight: 700; /* Reduced from 900 */
  letter-spacing: -0.02em;
  color: white;
}

@media (max-width: 768px) {
  .hero-title {
    font-size: 1.25rem; /* Reduced from 2rem */
  }
}

.hero-subtitle {
  font-size: 0.875rem; /* Reduced from 1rem */
  color: #94a3b8;
}

/* Search and Filter Row */
.search-filter-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
}

/* Search Wrapper */
.search-wrapper {
  flex: 1;
}

.search-box {
  display: flex;
  align-items: stretch;
  height: 56px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #324467;
  background-color: #192233;
  transition: border-color 0.2s;
}

.search-box:focus-within {
  border-color: #135bec;
}

.search-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem 0 1rem;
  color: #94a3b8;
}

.search-input {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  outline: none;
  color: white;
  font-size: 1rem;
  font-weight: 500;
  height: 100%;
}

.search-input::placeholder {
  color: rgba(148, 163, 184, 0.5);
}

.search-btn-container {
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
}

.search-btn {
  padding: 0.625rem 1.5rem;
  border-radius: 6px;
  background-color: #135bec;
  color: white;
  font-size: 0.875rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
  white-space: nowrap;
}

.search-btn:hover {
  background-color: #1d6bf5;
}

/* Filter Toggle Button */
.filter-toggle-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1.5rem;
  height: 56px;
  border-radius: 8px;
  background-color: #192233;
  border: 1px solid #324467;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
  flex-shrink: 0;
}

.filter-toggle-btn:hover {
  background-color: #232f48;
  border-color: #475e8a;
}

.filter-toggle-btn.active {
  background-color: rgba(19, 91, 236, 0.1);
  border-color: #135bec;
  color: #135bec;
}

.filter-toggle-btn .material-symbols-outlined {
  font-size: 20px;
}

.dropdown-arrow {
  font-size: 20px;
  transition: transform 0.3s;
}

.dropdown-arrow.rotated {
  transform: rotate(180deg);
}

/* Hot Chips Row */
.hot-chips-row {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  width: 100%;
  flex-wrap: wrap;
}

.hot-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.hot-chips-list {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.hot-chip {
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 1rem;
  border-radius: 999px;
  background-color: #192233;
  border: 1px solid #324467;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.hot-chip:hover {
  border-color: rgba(19, 91, 236, 0.5);
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

/* Filter Panel */
.filter-panel {
  width: 100%;
  border-radius: 12px;
  background-color: rgba(25, 34, 51, 0.8);
  border: 1px solid #324467;
  padding: 1.5rem;
  margin-top: 0;
  animation: slideDown 0.3s ease-out;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.filter-panel-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 1rem;
  border-bottom: 1px solid #324467;
  margin-bottom: 1.5rem;
}

.filter-panel-title {
  font-size: 1rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.reset-link {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #135bec;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.reset-link:hover {
  color: #4dabf7;
}

.reset-link .material-symbols-outlined {
  font-size: 16px;
}

/* Filter Content Grid */
.filter-content {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

@media (max-width: 1024px) {
  .filter-content {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .filter-content {
    grid-template-columns: 1fr;
  }

  .search-filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .filter-toggle-btn {
    width: 100%;
    justify-content: center;
  }
}

/* Filter Item */
.filter-item {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* Radio Group */
.radio-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.radio-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.radio-label input[type="radio"] {
  display: none;
}

.radio-dot {
  width: 16px;
  height: 16px;
  border: 2px solid #324467;
  border-radius: 50%;
  position: relative;
  transition: all 0.2s;
}

.radio-label input[type="radio"]:checked + .radio-dot {
  border-color: #135bec;
  background-color: #135bec;
}

.radio-label input[type="radio"]:checked + .radio-dot::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: white;
}

.radio-text {
  font-size: 0.875rem;
  color: white;
}

/* Checkbox Group */
.checkbox-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 180px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-container {
  position: relative;
}

.checkbox-input {
  display: none;
}

.checkbox-check {
  width: 16px;
  height: 16px;
  border: 1px solid #324467;
  border-radius: 4px;
  background-color: #192233;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.checkbox-label input[type="checkbox"]:checked + .checkbox-check {
  border-color: #135bec;
  background-color: #135bec;
}

.checkbox-check .material-symbols-outlined {
  font-size: 12px;
  color: white;
  opacity: 0;
}

.checkbox-label input[type="checkbox"]:checked + .checkbox-check .material-symbols-outlined {
  opacity: 1;
}

.checkbox-text {
  font-size: 0.875rem;
  color: white;
  flex: 1;
}

.checkbox-count {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-left: auto;
}

/* Price Range */
.price-range-box {
  width: 100%;
}

.price-inputs {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.price-input {
  flex: 1;
  height: 40px;
  padding: 0 0.75rem;
  border-radius: 6px;
  border: 1px solid #324467;
  background-color: #111722;
  color: white;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.price-input:focus {
  outline: none;
  border-color: #135bec;
}

.price-input::placeholder {
  color: rgba(148, 163, 184, 0.5);
}

.price-separator {
  color: #94a3b8;
}

/* Manufacturer Grid */
.manufacturer-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.manufacturer-chip {
  height: 32px;
  padding: 0 1rem;
  border-radius: 999px;
  border: 1px solid #324467;
  background-color: #192233;
  color: #94a3b8;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.manufacturer-chip:hover {
  border-color: #475e8a;
}

.manufacturer-chip.active {
  background-color: rgba(19, 91, 236, 0.2);
  border-color: #135bec;
  color: #135bec;
}

/* Filter Footer */
.filter-footer {
  display: flex;
  justify-content: center;
  padding-top: 1rem;
  border-top: 1px solid #324467;
}

.apply-filter-btn {
  padding: 0.75rem 3rem;
  border-radius: 8px;
  background-color: #135bec;
  color: white;
  font-size: 0.875rem;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: background-color 0.2s;
}

.apply-filter-btn:hover {
  background-color: #1d6bf5;
}

/* Main Content */
.main-content {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem 2rem 2rem 2rem;
  flex: 1;
  max-width: 1200px;
  margin: 0 auto;
  width: 100%;
  overflow: hidden; /* Prevent outer scroll */
}

/* Results Area */
.results-area {
  display: flex;
  flex-direction: column;
  flex: 1;
  overflow: hidden;
  gap: 0;
  background-color: #0d1118;
  border: 1px solid #324467;
  border-radius: 8px;
}

/* Results Header */
.results-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 0.75rem 1rem;
  background-color: #192233;
  border-bottom: 1px solid #324467;
  flex-shrink: 0; /* Prevent shrinking */
}

.results-count {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.count-label {
  font-weight: 500;
  color: white;
}

.count-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  background-color: rgba(19, 91, 236, 0.2);
  color: #135bec;
  font-size: 0.75rem;
  font-weight: 700;
}

.results-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.sort-select {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.sort-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.sort-input {
  background-color: #111722;
  border: 1px solid #324467;
  color: white;
  font-size: 0.875rem;
  border-radius: 4px;
  padding: 0.375rem 0.5rem;
  cursor: pointer;
}

.sort-input:focus {
  outline: none;
  border-color: #135bec;
}

/* Column Filter Button */
.column-filter-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  background-color: #192233;
  border: 1px solid #324467;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.column-filter-btn:hover {
  background-color: #232f48;
  border-color: #475e8a;
}

.column-filter-btn.active {
  background-color: rgba(19, 91, 236, 0.1);
  border-color: #135bec;
  color: #135bec;
}

.column-filter-btn .material-symbols-outlined {
  font-size: 18px;
}

/* Column Filter Panel */
.column-filter-panel {
  padding: 1rem;
  background-color: rgba(25, 34, 51, 0.8);
  border-bottom: 1px solid #324467;
  flex-shrink: 0;
}

.column-filter-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
}

.column-filter-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
}

.reset-column-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #135bec;
  background: none;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.reset-column-btn:hover {
  color: #4dabf7;
}

.reset-column-btn .material-symbols-outlined {
  font-size: 16px;
}

.column-filter-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

/* Field Filter Items */
.field-filter-item {
  position: relative;
  width: calc(50% - 0.25rem);
}

.field-filter-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.625rem 0.75rem;
  background-color: #192233;
  border: 1px solid #324467;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.field-filter-trigger:hover {
  background-color: #232f48;
  border-color: #4a5568;
}

.field-filter-trigger.active {
  background-color: #135bec;
  border-color: #135bec;
}

.field-filter-trigger.has-filter {
  border-color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.field-filter-label {
  font-size: 0.875rem;
  color: #cbd5e1;
}

.field-filter-trigger.active .field-filter-label,
.field-filter-trigger.has-filter .field-filter-label {
  color: white;
}

.field-filter-count {
  font-size: 0.75rem;
  color: #94a3b8;
  background-color: #0d1118;
  padding: 2px 8px;
  border-radius: 10px;
  min-width: 20px;
  text-align: center;
}

.field-filter-trigger.active .field-filter-count,
.field-filter-trigger.has-filter .field-filter-count {
  background-color: rgba(255, 255, 255, 0.2);
  color: white;
}

.field-filter-trigger .dropdown-icon {
  font-size: 1rem;
  color: #94a3b8;
  transition: transform 0.2s;
}

.field-filter-trigger.active .dropdown-icon {
  color: white;
}

.field-filter-trigger .dropdown-icon.rotated {
  transform: rotate(180deg);
}

/* Field Filter Dropdown */
.field-filter-dropdown {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  background-color: #192233;
  border: 1px solid #324467;
  border-radius: 6px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 100;
  max-height: 300px;
  display: flex;
  flex-direction: column;
}

.field-filter-actions {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  border-bottom: 1px solid #324467;
  flex-shrink: 0;
}

.filter-action-btn {
  flex: 1;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  color: #94a3b8;
  background: transparent;
  border: 1px solid #324467;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.filter-action-btn:hover {
  color: white;
  background-color: #232f48;
  border-color: #4a5568;
}

.field-filter-values {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
}

.field-value-checkbox {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.5rem;
  cursor: pointer;
  border-radius: 4px;
  transition: background-color 0.15s;
}

.field-value-checkbox:hover {
  background-color: #232f48;
}

.fv-checkbox {
  width: 14px;
  height: 14px;
  border: 1px solid #324467;
  border-radius: 3px;
  background-color: #0d1118;
  cursor: pointer;
  accent-color: #135bec;
  flex-shrink: 0;
}

.fv-text {
  font-size: 0.813rem;
  color: #cbd5e1;
  word-break: break-word;
}

.field-empty {
  padding: 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.813rem;
}

/* Loading State */
.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 1rem;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #324467;
  border-top-color: #135bec;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Empty State */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  gap: 0.5rem;
}

.empty-icon {
  font-size: 64px;
  color: #324467;
}

.empty-text {
  font-size: 1rem;
  color: white;
}

.empty-hint {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Results List Scroll Container */
.results-list-scroll {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  padding: 1rem;
}

/* Results List */
.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Inline Prices */
.device-prices-inline {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
}

.inline-price-item {
  display: flex;
  align-items: baseline;
  gap: 0.375rem;
}

.inline-price-label {
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
}

.inline-price-value {
  font-size: 0.875rem;
  font-weight: 600;
  font-family: "Space Grotesk", sans-serif;
  color: #135bec;
}

.inline-price-value.price-6 {
  color: #22c55e;
}

.inline-price-value.price-13 {
  color: #f59e0b;
}

.tag-series {
  border-color: #8b5cf7;
  background-color: rgba(139, 92, 247, 0.1);
  color: #8b5cf7;
}

/* Device Card */
.device-card {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  padding: 1rem;
  border-radius: 12px;
  background-color: #192233;
  border: 1px solid #324467;
  cursor: pointer;
  transition: all 0.2s;
}

@media (min-width: 768px) {
  .device-card {
    flex-direction: row;
    align-items: center;
  }
}

.device-card:hover {
  border-color: rgba(19, 91, 236, 0.5);
  box-shadow: 0 10px 25px -5px rgba(19, 91, 236, 0.1);
}

/* Device Image */
.device-image {
  width: 100%;
  height: 128px;
  flex-shrink: 0;
  border-radius: 8px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
}

@media (min-width: 768px) {
  .device-image {
    width: 128px;
  }
}

.device-icon {
  font-size: 64px;
  color: #324467;
}

.price-badge {
  position: absolute;
  top: 8px;
  left: 8px;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  background-color: #ef4444;
  color: white;
  font-size: 0.625rem;
  font-weight: 700;
}

/* Device Details */
.device-details {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.device-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
}

.device-title-section {
  min-width: 0;
}

.device-model {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.device-card:hover .device-model {
  color: #135bec;
}

.device-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.25rem;
}

.tag {
  padding: 0.125rem 0.5rem;
  border-radius: 4px;
  background-color: #111722;
  border: 1px solid #324467;
  font-size: 0.75rem;
  color: #94a3b8;
}

.tag-manufacturer {
  border-color: #324467;
}

.tag-category {
  border-color: #324467;
}

.tag-sub {
  border-color: #324467;
}

.tag-grade {
  background-color: rgba(34, 197, 94, 0.1);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.device-price-section {
  text-align: right;
}

.price-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.device-price {
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.5rem;
  font-weight: 700;
  color: #135bec;
}

.device-divider {
  height: 1px;
  background-color: #324467;
  margin: 0.25rem 0;
}

.device-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
}

/* Device Prices Section */
.device-prices {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 0.75rem;
  border-radius: 8px;
  background-color: rgba(19, 91, 236, 0.05);
  border: 1px solid rgba(19, 91, 236, 0.15);
}

.price-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.device-prices .price-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.device-prices .price-value {
  font-size: 0.875rem;
  font-weight: 600;
  color: #135bec;
}

.device-prices .price-value.price-6 {
  color: #22c55e;
}

.device-prices .price-value.price-13 {
  color: #f59e0b;
}

.device-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.meta-icon {
  font-size: 16px;
  color: #6b7280;
}

.device-actions {
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem 0.75rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.action-btn.secondary {
  border: 1px solid #324467;
  background-color: #111722;
  color: white;
}

.action-btn.secondary:hover {
  background-color: #324467;
}

.action-btn.primary {
  background-color: #135bec;
  border: none;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.2);
}

.action-btn.primary:hover {
  background-color: #1d6bf5;
}

/* Pagination */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #192233;
  border-top: 1px solid #324467;
  flex-shrink: 0;
}

.page-btn,
.page-num {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn {
  border: 1px solid #324467;
  background-color: #192233;
  color: #94a3b8;
}

.page-btn:hover:not(:disabled) {
  color: white;
  border-color: #135bec;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-num {
  border: 1px solid #324467;
  background-color: #192233;
  color: #94a3b8;
}

.page-num:hover {
  color: white;
  border-color: #135bec;
}

.page-num.active {
  background-color: #135bec;
  border-color: #135bec;
  color: white;
  font-weight: 700;
}

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 2rem;
}

.modal-dialog {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 1rem;
  width: 100%;
  max-width: 600px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #232f48;
}

.modal-title {
  font-family: "Space Grotesk", sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.modal-close {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close:hover {
  background-color: #232f48;
  color: white;
}

.modal-content {
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.detail-image {
  width: 100%;
  height: 200px;
  border-radius: 12px;
  background-color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.detail-icon {
  font-size: 96px;
  color: #324467;
}

.detail-model {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.detail-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.detail-tag {
  padding: 0.25rem 0.75rem;
  border-radius: 20px;
  background-color: #232f48;
  color: #94a3b8;
  font-size: 0.875rem;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.detail-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.detail-value {
  font-size: 1rem;
  color: white;
}

.detail-remarks {
  padding: 1rem;
  border-radius: 8px;
  background-color: #111722;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.remarks-label {
  font-size: 0.875rem;
  font-weight: 500;
  color: #94a3b8;
}

.remarks-text {
  font-size: 0.875rem;
  color: white;
  white-space: pre-wrap;
}

/* Detail Prices Section */
.detail-prices-section {
  padding: 1rem;
  border-radius: 8px;
  background-color: rgba(19, 91, 236, 0.05);
  border: 1px solid rgba(19, 91, 236, 0.15);
}

.detail-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.75rem;
}

.detail-prices-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.75rem;
}

@media (max-width: 640px) {
  .detail-prices-grid {
    grid-template-columns: 1fr;
  }
}

.detail-price-card {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
  padding: 0.75rem;
  border-radius: 8px;
  background-color: #192233;
  border: 1px solid #324467;
}

.detail-price-card.price-6 {
  border-color: rgba(34, 197, 94, 0.3);
  background-color: rgba(34, 197, 94, 0.05);
}

.detail-price-card.price-13 {
  border-color: rgba(245, 158, 11, 0.3);
  background-color: rgba(245, 158, 11, 0.05);
}

.detail-price-label {
  font-size: 0.75rem;
  color: #94a3b8;
}

.detail-price-value {
  font-size: 1rem;
  font-weight: 700;
  font-family: "Space Grotesk", sans-serif;
  color: #135bec;
}

.detail-price-card.price-6 .detail-price-value {
  color: #22c55e;
}

.detail-price-card.price-13 .detail-price-value {
  color: #f59e0b;
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #232f48;
}

.modal-btn {
  padding: 0.625rem 1.25rem;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: all 0.2s;
}

.modal-btn.cancel {
  border: 1px solid #324467;
  background: transparent;
  color: white;
}

.modal-btn.cancel:hover {
  background-color: rgba(100, 116, 139, 0.1);
}

.modal-btn.confirm {
  background-color: #22c55e;
  border: none;
  color: white;
}

.modal-btn.confirm:hover {
  background-color: #16a34a;
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(35, 47, 72, 0.5);
}

::-webkit-scrollbar-thumb {
  background: #324467;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #475e8a;
}
</style>
