<template>
  <div class="flex min-h-screen bg-perplexity-bg" style="font-family: Inter, 'Noto Sans', '微软雅黑', sans-serif;">
    <!-- 极简左侧导航栏 -->
    <nav class="side-nav">
      <!-- 品牌标识区域 -->
      <div class="brand-section">
        <div class="brand-icon">🏢</div>
        <div class="brand-text">智能报价</div>
        <div class="brand-subtitle">系统</div>
      </div>
      
      <div class="nav-btn-group">
        <button class="side-nav-btn" :class="{active: activeFunction === 'convert'}" @click="activeFunction = 'convert'">
          <span class="nav-icon">📄</span>
          <span class="nav-label">智能识别</span>
        </button>
        <button class="side-nav-btn" :class="{active: activeFunction === 'match'}" @click="activeFunction = 'match'">
          <span class="nav-icon">🔍</span>
          <span class="nav-label">智能匹配</span>
        </button>
        <button class="side-nav-btn" :class="{active: activeFunction === 'quote'}" @click="activeFunction = 'quote'">
          <span class="nav-icon">💰</span>
          <span class="nav-label">生成报价单</span>
        </button>
        <button class="side-nav-btn" :class="{active: activeFunction === 'search'}" @click="activeFunction = 'search'">
          <span class="nav-icon">🔎</span>
          <span class="nav-label">手动搜索</span>
        </button>
        <button ref="adminBtnRef" class="side-nav-btn" :class="{active: activeFunction === 'admin'}" @click="toggleAdminMenu">
          <span class="nav-icon">⚙️</span>
          <span class="nav-label">后台管理</span>
        </button>
      </div>
      
      <!-- 底部版本信息 -->
      <div class="version-info">
        <div class="version-text">v1.0.0</div>
      </div>
    </nav>
    <!-- 后台管理二级菜单弹窗，绝对定位到后台管理按钮右下 -->
    <!-- 数据源选择（右上角，Element Plus 风格） -->
    <div class="data-source-switcher">
      <span class="switcher-label">数据源</span>
      <el-select v-model="dataSource" size="small" class="data-source-select" placeholder="选择数据源" style="width: 120px;">
        <el-option label="数据中心" value="datacenter" />
        <el-option label="办公设备" value="office" />
        <el-option label="混合" value="hybrid" />
      </el-select>
    </div>
    <div v-if="showAdminMenu" class="admin-menu-popup" :style="adminMenuStyle" @mouseleave="showAdminMenu = false">
      <div class="admin-menu-list">
        <div class="admin-menu-item" :class="{active: adminSubPage === 'rate'}" @click="openAdminSubPage('rate')">费率管理</div>
        <div class="admin-menu-item" :class="{active: adminSubPage === 'service_level'}" @click="openAdminSubPage('service_level')">服务级别管理</div>
        <div class="admin-menu-item" :class="{active: adminSubPage === 'gpu_price'}" @click="openAdminSubPage('gpu_price')">GPU价格管理</div>
          <div class="admin-menu-item" :class="{active: adminSubPage === 'spare_part'}" @click="openAdminSubPage('spare_part')">备件管理</div>
      </div>
    </div>
    <!-- 右侧主内容区 -->
    <main class="main-content">
      <div v-if="activeFunction === 'convert'">
        <h1 class="text-3xl font-bold mb-6">智能识别</h1>
        <div class="upload-area mb-6">
          <input type="file" @change="handleConvertFileChange" accept=".xlsx,.xls" id="convert-file-input" />
          <button @click="triggerFileInput('convert')" class="action-button">选择Excel文件</button>
        </div>
        <div v-if="originalTableData.length > 0" class="split-view">
          <!-- 左侧原始表格 -->
          <div class="original-table">
            <h3 style="display: flex; justify-content: space-between; align-items: center;">
              <span>原始表格</span>
              <span v-if="originalTableData.length > 0" class="device-model-count">共导入设备型号：{{ getDeviceModelCount() }} 条</span>
            </h3>
            <!-- 删除列数/行数统计 -->
            <div class="table-container original-table-container">
              <table border="1" class="original-data-table">
                <thead>
                  <tr>
                    <th v-for="(header, index) in originalHeaders" :key="index" class="original-th">
                      {{ header }}
                      <div class="resizer" @mousedown="startResize($event, 'original', index)"></div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in originalTableData" :key="rowIndex">
                    <td v-for="(header, colIndex) in originalHeaders" :key="colIndex" class="original-td">
                      {{ row[header] || '' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- 右侧转换表格 -->
          <div class="converted-table">
            <h3>转换后表格</h3>
            <div class="table-container">
              <table border="1" class="editable-table">
                <thead>
                  <tr>
                    <th v-for="(header, index) in visibleColumns" :key="header">
                      <span class="header-text" @click="openMappingDialog(header, index)" :title="'点击更改该列的数据映射'">{{ header }}</span>
                      <button class="edit-mapping-btn" @click.stop="openMappingDialog(header, index)" title="更改映射">✎</button>
                      <button class="clear-col-btn" @click="clearColumn(header)" title="清空该列">×</button>
                      <div class="resizer" @mousedown.stop="startResize($event, 'converted', index)"></div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in convertedTableData" :key="rowIndex">
                    <td v-for="header in visibleColumns" :key="header">
                      <input type="text" :value="row[header]" @input="updateCell(rowIndex, header, $event)" />
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="actions convert-actions button-flex-wrap">
              <button @click="addRow">添加行</button>
              <button @click="exportConvertedData">导出结果</button>
              <button @click="resetConvertData">清空数据</button>
              <button @click="sendToMatch" class="match-btn">智能匹配</button>
            </div>
          </div>
        </div>
      </div>
      <div v-if="activeFunction === 'match'">
        <h1 class="text-3xl font-bold mb-6">智能匹配</h1>
        <!-- 匹配进度条 -->
        <div v-if="matchingInProgress" class="progress-wrapper">
          <div class="progress-bar">
            <div class="progress-inner" :style="{ width: matchingProgress + '%' }"></div>
          </div>
          <div class="progress-text">{{ matchingCompleted }}/{{ matchingTotal }} ({{ matchingProgress }}%)</div>
        </div>
        <div class="upload-area mb-6">
          <input type="file" @change="handleFileChange" accept=".xlsx,.xls" id="match-file-input" />
          <button @click="triggerFileInput('match')" class="action-button">选择Excel文件</button>
        </div>
        <div v-if="tableData.length > 0" class="table-area">
          <div class="table-container">
            <table border="1">
              <thead>
                <tr>
                  <th>厂商<div class="resizer" @mousedown="startResize($event, 'match', 0)"></div></th>
                  <th>设备/软件型号<div class="resizer" @mousedown="startResize($event, 'match', 1)"></div></th>
                  <th>设备/软件分类<div class="resizer" @mousedown="startResize($event, 'match', 2)"></div></th>
                  <th>服务级别<div class="resizer" @mousedown="startResize($event, 'match', 3)"></div></th>
                  <th>匹配型号<div class="resizer" @mousedown="startResize($event, 'match', 4)"></div></th>
                  <th>匹配度<div class="resizer" @mousedown="startResize($event, 'match', 5)"></div></th>
                  <th>原始单价<div class="resizer" @mousedown="startResize($event, 'match', 6)"></div></th>
                  <th>服务级别系数<div class="resizer" @mousedown="startResize($event, 'match', 7)"></div></th>
                  <th>调整后单价<div class="resizer" @mousedown="startResize($event, 'match', 8)"></div></th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, index) in tableData" :key="index">
                  <td>{{ item.manufacturer }}</td>
                  <td>{{ item.model }}</td>
                  <td>{{ item.deviceCategory }}</td>
                  <td>{{ item.serviceLevel || '-' }}</td>
                  <td>
                    <div class="model-cell">
                      <span
                        class="matched-model-span"
                        @click="openSearch(index)"
                        :title="'点击修改匹配型号'"
                        style="cursor:pointer;display:inline-block;min-width:60px;"
                      >
                        <span :class="{
                          'matched': item.matchRate >= 70,
                          'moderate-match': item.matchRate >= 50 && item.matchRate < 70,
                          'low-match': item.matchRate > 0 && item.matchRate < 50,
                          'unmatched': !item.matchedModel
                        }">
                          {{ item.matchedModel || '未匹配' }}
                          <span v-if="item.matchRate < 50 && item.matchRate > 0" class="low-match-hint">(低匹配度)</span>
                        </span>
                        <span class="edit-hint">(点击修改)</span>
                      </span>
                      <div v-if="activeModelIndex === index" class="model-selector">
                        <select v-model="item.matchedModel" @change="updateModelSelection(index)">
                          <option value="">未匹配</option>
                          <option v-for="option in modelOptions" :key="option.id" :value="option.model">
                            {{ option.model }} ({{ option.manufacturer }})
                          </option>
                        </select>
                      </div>
                    </div>
                  </td>
                  <td>
                    <span :class="['match-rate-text',
                      item.matchRate >= 70 ? 'match-high' :
                      item.matchRate >= 50 ? 'match-mid' :
                      item.matchRate > 0 ? 'match-low' : 'match-none']">
                      {{ Math.round(item.matchRate) }}%
                    </span>
                  </td>
                  <td>{{ item.originalPrice ? '¥' + item.originalPrice.toFixed(2) : '-' }}</td>
                  <td>
                    <span v-if="item.serviceLevelCoefficient !== 1" class="service-level-coefficient">
                      {{ item.serviceLevelCoefficient.toFixed(2) }}
                      <span v-if="item.matchedServiceLevel" class="service-level-info" :title="`匹配服务级别: ${item.matchedServiceLevel.level_code} (${item.matchedServiceLevel.response_time})`">
                        ({{ item.matchedServiceLevel.level_code }})
                      </span>
                    </span>
                    <span v-else>-</span>
                  </td>
                  <td>{{ item.price ? '¥' + item.price.toFixed(2) : '-' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <div class="actions">
            <button @click="exportData">导出结果</button>
            <button @click="resetMatchData">清空数据</button>
            <button @click="generateQuotes" class="generate-quote-btn">生成报价单</button>
          </div>
        </div>
      </div>
      <div v-if="activeFunction === 'quote'">
        <h1 class="text-3xl font-bold mb-6">生成报价单</h1>
        <div class="quote-info">
          <p>报价单模块可显示根据原始表格和转换后表格生成的设备报价信息。单价数据来源于智能匹配模块的匹配结果。</p>
        </div>
        <div class="quote-actions">
          <button @click="generateQuotes">更新报价单</button>
          <button @click="exportQuotes">导出报价单</button>
          <button @click="resetQuotes">清空报价单</button>
        </div>
        <div v-if="originalQuoteData.length > 0 || convertedQuoteData.length > 0" class="split-view">
          <!-- 左侧原始表报价单 -->
          <div class="original-quote">
            <h3>原始表报价单</h3>
            <div class="table-container">
              <table border="1">
                <thead>
                  <tr>
                    <th v-for="(header, index) in originalQuoteHeaders" :key="index">
                      {{ header }}
                      <div class="resizer" @mousedown="startResize($event, 'original-quote', index)"></div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in originalQuoteData" :key="rowIndex">
                    <td v-for="(header, colIndex) in originalQuoteHeaders" :key="colIndex">
                      {{ row[header] || '' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
          <!-- 右侧转换后报价单 -->
          <div class="converted-quote">
            <h3>转换后报价单</h3>
            <div class="table-container">
              <table border="1">
                <thead>
                  <tr>
                    <th v-for="header in visibleQuoteColumns" :key="header">
                      {{ header }}
                      <div class="resizer" @mousedown="startResize($event, 'converted-quote', visibleQuoteColumns.indexOf(header))"></div>
                    </th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, rowIndex) in convertedQuoteData" :key="rowIndex">
                    <td v-for="header in visibleQuoteColumns" :key="header">
                      {{ row[header] || '' }}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
        <div v-else class="no-data-message">
          请先使用智能识别和智能匹配功能处理数据，然后点击"生成报价单"按钮生成报价单
        </div>
      </div>
      <div v-if="activeFunction === 'search'">
        <h1 class="text-3xl font-bold mb-8">手动搜索</h1>
        <div class="flex flex-col items-center w-full">
          <div class="relative w-full max-w-xl">
            <input
              id="model_number"
              v-model="searchForm.model_number"
              @input="handleSearchInput"
              placeholder="请输入设备型号进行搜索"
              class="w-full px-5 py-3 text-lg border border-gray-300 rounded-full shadow focus:outline-none focus:border-blue-500 transition"
              autocomplete="off"
            />
            <!-- 搜索按钮已移除 -->
          </div>
          <div v-if="searchResults.length" class="w-full max-w-xl bg-white rounded-xl shadow mt-2 divide-y divide-gray-100">
            <div
              v-for="result in searchResults"
              :key="result.id || result.model_number || result.model"
              class="px-5 py-4 hover:bg-slate-50 cursor-pointer group border-b last:border-b-0"
            >
              <div class="flex items-center mb-2">
                <div class="font-semibold text-base text-gray-900" style="min-width:0;">{{ result.model_number || result.model }}</div>
                <span class="ml-3 text-blue-500 copy-model-btn" @click.stop="copyModelInfo(result, $event)">点击复制型号</span>
              </div>
              <div class="grid grid-cols-2 gap-x-6 gap-y-1 text-sm text-gray-700">
                <div class="col-span-1">
                  <!-- 三种维保单价显示 -->
                  <div v-if="getMaintenancePriceInfo(result)" class="font-semibold text-green-700 standard-rate-rightcol">
                    <div class="price-item">
                      未税维保单价：¥{{ getMaintenancePriceInfo(result).untaxedPrice.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
                    </div>
                    <div class="price-item">
                      标准维保单价（6%）：¥{{ getMaintenancePriceInfo(result).price6Percent.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
                    </div>
                    <div class="price-item">
                      标准维保单价（13%）：¥{{ getMaintenancePriceInfo(result).price13Percent.toLocaleString(undefined, {minimumFractionDigits: 2, maximumFractionDigits: 2}) }}
                    </div>
                  </div>
                  <template v-for="(value, key) in result">
                    <div v-if="key !== 'id'">
                      <span class="font-medium">{{ fieldLabelMap[key] || key }}：</span>
                      <span v-if="key==='device_price' && value !== undefined && value !== null">¥{{ Number(value).toFixed(2) }}</span>
                      <span v-else>{{ value }}</span>
                    </div>
                  </template>
                </div>
                <div class="col-span-1">
                  <!-- 右侧字段渲染逻辑保持不变 -->
                </div>
              </div>
            </div>
          </div>
          <div v-else-if="searchForm.model_number" class="w-full max-w-xl text-center text-gray-400 mt-4">暂无搜索结果</div>
        </div>
      </div>
      <div v-if="activeFunction === 'admin' && adminSubPage === 'rate'">
        <MaintenanceRateManager />
      </div>
      <div v-if="activeFunction === 'admin' && adminSubPage === 'service_level'">
        <ServiceLevelManager />
      </div>
      <div v-if="activeFunction === 'admin' && adminSubPage === 'spare_part'">
        <SparePartManager />
      </div>
      <div v-if="activeFunction === 'admin' && adminSubPage === 'gpu_price'">
        <GPUPriceManager />
      </div>
      <div v-if="activeFunction === 'admin' && !adminSubPage">
        <div class="admin-welcome">
          <h1 class="text-3xl font-bold mb-6">后台管理</h1>
          <div class="admin-content">
            <p class="text-gray-600 mb-4">请从左侧菜单选择要管理的功能模块：</p>
            <div class="admin-modules">
              <div class="admin-module-card">
                <h3>费率管理</h3>
                <p>管理设备维护费率配置</p>
                <button @click="openAdminSubPage('rate')" class="module-btn">进入管理</button>
              </div>
              <div class="admin-module-card">
                <h3>服务级别管理</h3>
                <p>管理服务级别配置</p>
                <button @click="openAdminSubPage('service_level')" class="module-btn">进入管理</button>
              </div>
              <div class="admin-module-card">
                <h3>GPU价格管理</h3>
                <p>导入并管理GPU价格、费率与费用</p>
                <button @click="openAdminSubPage('gpu_price')" class="module-btn">进入管理</button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

  <!-- 列映射编辑弹窗 -->
  <div v-if="showMappingDialog" class="mapping-dialog-overlay" @click.self="closeMappingDialog">
    <div class="mapping-dialog-content">
      <div class="mapping-header">
        <h3>更改列映射 - {{ editingColumn }}</h3>
        <button class="close-button" @click="closeMappingDialog">×</button>
      </div>
      <div class="mapping-body">
        <p class="mapping-hint">请选择"{{ editingColumn }}"列应该从原始表格的哪一列获取数据：</p>
        <div class="mapping-options">
          <label class="mapping-option">
            <input type="radio" value="" v-model="selectedSourceColumn" />
            <span>清空当前列数据</span>
          </label>
          <label class="mapping-option" v-for="header in originalHeaders" :key="header">
            <input type="radio" :value="header" v-model="selectedSourceColumn" />
            <span>{{ header }}</span>
          </label>
        </div>
      </div>
      <div class="mapping-footer">
        <button class="cancel-btn" @click="closeMappingDialog">取消</button>
        <button class="confirm-btn" @click="applyMapping">确认映射</button>
      </div>
    </div>
  </div>

  <!-- 智能匹配表格手动搜索弹窗 -->
    <div v-if="showSearchDialog" class="search-dialog" style="z-index: 2000;">
      <div class="search-dialog-content">
        <div class="search-header">
          <h3>手动搜索设备型号</h3>
          <button class="close-button" @click="showSearchDialog = false">×</button>
        </div>
        <div class="search-form">
          <div class="search-input">
            <input type="text" v-model="searchQuery.model" @input="handleSearch(1, pageSize)" placeholder="请输入设备型号关键词" />
          </div>
        </div>
        <div class="search-results">
          <div v-if="searchResults.length">
            <div v-for="result in searchResults" :key="result.id || result.model_number || result.model" class="search-result-item" @click="selectSearchResult(result, $event)">
              <div class="result-info">
                <span class="result-model">{{ result.model_number || result.model }}</span>
                <span class="result-manufacturer">{{ result.manufacturer }}</span>
                <span class="result-category">{{ result.device_category || result.category }}</span>
                <span class="result-price" v-if="result.device_price || result.price">¥{{ (result.device_price || result.price).toFixed(2) }}</span>
              </div>
            </div>
          </div>
          <div v-else class="no-results">暂无搜索结果</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, shallowRef, nextTick, watch, onMounted, computed } from 'vue'
import * as XLSX from 'xlsx'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import MaintenanceRateManager from './components/MaintenanceRateManager.vue'
import ServiceLevelManager from './components/ServiceLevelManager.vue'
import GPUPriceManager from './views/GPUPriceManager.vue'
import SparePartManager from './views/SparePartManager.vue'
import { fetchRates, findRate, calcStandardRatePrice, calcMaintenancePrices } from './rateUtils.js'
import { fetchServiceLevels, calculateServiceLevelPrice } from './serviceLevelUtils.js'

// 开发模式检测
const isDev = computed(() => import.meta.env.DEV)

// 设备字段列表
const deviceFields = [
  { key: 'manufacturer', label: '厂商' },
  { key: 'device_series', label: '设备系列' },
  { key: 'model_number', label: '设备型号' },
  { key: 'business_scenario', label: '业务场景' },
  { key: 'primary_category', label: '设备一级分类' },
  { key: 'secondary_category', label: '设备二级分类' },
  { key: 'tertiary_category', label: '设备三级分类' },
  { key: 'remarks', label: '备注' },
  { key: 'device_price', label: '整机价格' },
  { key: 'device_grade', label: '设备档次' }
]

// 查询条件
const searchForm = ref({
  manufacturer: '',
  device_series: '',
  model_number: '',
  business_scenario: '',
  primary_category: '',
  secondary_category: '',
  tertiary_category: '',
  remarks: '',
  device_price: '',
  device_grade: ''
})

// 查询结果
const searchResults = ref([])
const totalResults = ref(0)
const currentPage = ref(1)
const pageSize = ref(10)

function handlePageChange(page) {
  if (!page || isNaN(page) || page < 1) page = 1;
  currentPage.value = page;
  handleSearch(page, pageSize.value);
}

const searchInputTimeout = ref(null)

function handleSearchInput() {
  if (searchInputTimeout.value) clearTimeout(searchInputTimeout.value)
  searchInputTimeout.value = setTimeout(() => {
    searchDevices()
  }, 300)
}

async function searchDevices() {
  const model = searchForm.value.model_number?.trim()
  if (!model) {
    searchResults.value = []
    return
  }
  try {
    const params = new URLSearchParams()
    params.append('model_number', model)
    params.append('source', dataSource.value)
    const resp = await fetch(`${API_URL}/devices/search/?${params.toString()}`)
    const data = await resp.json()
    // 兼容后端返回格式
    searchResults.value = Array.isArray(data) ? data : (data.data || [])
  } catch (e) {
    searchResults.value = []
  }
}

// 智能匹配相关变量
const tableData = ref([])

// 服务级别相关变量
const serviceLevels = ref([])
const serviceLevelLoading = ref(false)
const activeModelIndex = ref(null)
const modelOptions = ref([])

// 获取API URL，支持跨域访问
const API_URL = import.meta.env.VITE_API_BASE_URL || (
  window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1' 
    ? 'http://localhost:5002'
    : `http://${window.location.hostname}:5002`
)

console.log('App.vue使用的API地址:', API_URL)

// 功能切换变量
const activeFunction = ref('convert') // 默认显示识别功能

// 智能识别相关变量
const originalTableData = ref([])
const originalHeaders = ref([])
// 使用 shallowRef 优化大数据量的响应式性能，只追踪数组引用变化而不追踪内部对象
const convertedTableData = shallowRef([])
const targetHeaders = ref([
  "序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息", 
  "设备数量", "城市", "机房地址", "服务级别", "服务周期", 
  "服务周期单位", "服务范围", "单价", "备注", "设备原值单价", 
  "特殊需求", "易损件类型", "耗材包数量"
])
// 列显示控制 - 默认显示最重要的几列
const visibleColumns = ref(["序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息", "设备数量", "城市", "机房地址",
  "服务级别", "服务周期", "服务周期单位", "服务范围"]);
const showColumnSelector = ref(false)

// 列映射编辑功能
const showMappingDialog = ref(false)
const editingColumn = ref('')
const editingColumnIndex = ref(-1)
const selectedSourceColumn = ref('')

// 原始表格列控制
const visibleOriginalColumns = ref([])
const showOriginalColumnSelector = ref(false)

// 报价单相关变量
const originalQuoteData = ref([])
const originalQuoteHeaders = ref([])
const convertedQuoteData = ref([])
const visibleQuoteColumns = ref([
  "序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息", "设备数量", "单价"
])
const showQuoteColumnSelector = ref(false)

// 数据源：datacenter | office | hybrid
const dataSource = ref('datacenter')
// 当数据源切换时，若在“智能匹配”页且已有数据，则自动按照新数据源重新匹配
watch(dataSource, async () => {
  if (activeFunction.value === 'match' && tableData.value.length > 0) {
    await sendToMatch()
  }
})

// 匹配进度
const matchingInProgress = ref(false)
const matchingTotal = ref(0)
const matchingCompleted = ref(0)
const matchingProgress = computed(() => {
  if (!matchingTotal.value) return 0
  return Math.floor((matchingCompleted.value / matchingTotal.value) * 100)
})

// 列宽调整相关变量
const resizing = ref(false)
const currentResizer = ref(null)
const currentTable = ref(null)
const startX = ref(0)
const startWidth = ref(0)
const currentColumnIndex = ref(0)

// 手动搜索相关变量
const showSearchDialog = ref(false)
const searchQuery = ref({
  model: '',
  manufacturer: '',
  category: ''
})
const searchTimeout = ref(null)

// 处理开始调整列宽
function startResize(event, tableType, columnIndex) {
  event.preventDefault()
  resizing.value = true
  currentResizer.value = event.target
  currentTable.value = tableType
  currentColumnIndex.value = columnIndex
  
  // 记录起始宽度和位置
  startX.value = event.pageX
  const table = event.target.closest('table')
  const headerCell = table.rows[0].cells[columnIndex]
  startWidth.value = headerCell.offsetWidth
  
  // 添加调整中的样式
  currentResizer.value.classList.add('resizing')
  
  // 添加鼠标移动和松开事件监听
  document.addEventListener('mousemove', resize)
  document.addEventListener('mouseup', stopResize)
}

// 处理调整列宽过程
function resize(event) {
  if (!resizing.value) return
  
  const dx = event.pageX - startX.value
  
  // 获取正在调整的表格
  let tableSelector
  if (currentTable.value === 'original') {
    tableSelector = '.original-table table'
  } else if (currentTable.value === 'converted') {
    tableSelector = '.converted-table table'
  } else if (currentTable.value === 'match') {
    tableSelector = '.table-area .table-container table'
  } else if (currentTable.value === 'original-quote') {
    tableSelector = '.original-quote table'
  } else if (currentTable.value === 'converted-quote') {
    tableSelector = '.converted-quote table'
  }
  
  const table = document.querySelector(tableSelector)
  if (!table) return
  
  // 计算新宽度（不能小于最小宽度）
  const newWidth = Math.max(startWidth.value + dx, 80)
  
  // 应用新宽度到所有行的相应单元格
  for (let i = 0; i < table.rows.length; i++) {
    if (table.rows[i].cells[currentColumnIndex.value]) {
      table.rows[i].cells[currentColumnIndex.value].style.width = `${newWidth}px`
      table.rows[i].cells[currentColumnIndex.value].style.minWidth = `${newWidth}px`
    }
  }
}

// 处理结束调整列宽
function stopResize() {
  if (!resizing.value) return
  
  resizing.value = false
  
  // 移除调整中的样式
  if (currentResizer.value) {
    currentResizer.value.classList.remove('resizing')
  }
  
  // 移除事件监听
  document.removeEventListener('mousemove', resize)
  document.removeEventListener('mouseup', stopResize)
}

// 监听功能模式变化
watch(activeFunction, (newValue) => {
  // 可以在这里添加一些切换功能时需要执行的逻辑
  console.log('切换到功能:', newValue)
})

// 通用文件输入触发
function triggerFileInput(type) {
  if (type === 'match') {
    document.getElementById('match-file-input').click()
  } else if (type === 'convert') {
    document.getElementById('convert-file-input').click()
  }
}

// 处理智能识别功能的文件上传
function handleConvertFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  
  // 检查文件类型
  if (!file.name.match(/\.(xlsx|xls)$/)) {
    alert('请选择正确的Excel文件格式 (.xlsx 或 .xls)')
    return
  }
  
  // 清空之前的数据
  originalTableData.value = []
  originalHeaders.value = []
  convertedTableData.value = []
  
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      console.log('开始读取Excel文件:', file.name)
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      
      if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
        throw new Error('Excel文件中没有找到工作表')
      }
      
      const firstSheet = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheet]
      
      if (!worksheet) {
        throw new Error('无法读取工作表数据')
      }
      
      // 检查工作表是否有数据
      if (!worksheet['!ref']) {
        throw new Error('工作表中没有数据或格式不正确')
      }
      
      // 获取工作表的范围
      const range = XLSX.utils.decode_range(worksheet['!ref']);
      console.log('Excel表格范围:', range);
      
      // 检查范围是否有效
      if (range.s.c > range.e.c || range.s.r > range.e.r) {
        throw new Error('Excel文件数据范围无效')
      }
      
      // 获取所有列的表头（包括空列）
      const headers = [];
      for (let c = range.s.c; c <= range.e.c; c++) {
        const cellAddress = XLSX.utils.encode_cell({ r: range.s.r, c });
        const cell = worksheet[cellAddress];
        // 如果单元格存在，使用其值，否则使用占位名称
        let headerName = `列${c+1}`;
        if (cell && cell.v !== undefined && cell.v !== null) {
          headerName = String(cell.v);
        }
        headers.push(headerName);
      }
      
      console.log('识别到的表头:', headers);
      
      // 使用自定义表头解析数据，保留原始格式
      const jsonData = [];
      for (let r = range.s.r + 1; r <= range.e.r; r++) {
        const row = {};
        let hasData = false; // 检查行是否有数据
        
        for (let c = range.s.c; c <= range.e.c; c++) {
          const cellAddress = XLSX.utils.encode_cell({ r, c });
          const cell = worksheet[cellAddress];
          const headerName = headers[c - range.s.c];
          let cellValue = '';
          
          if (cell && cell.v !== undefined && cell.v !== null) {
            cellValue = String(cell.v);
            hasData = true;
          }
          
          row[headerName] = cellValue;
        }
        
        // 只添加有数据的行
        if (hasData) {
          jsonData.push(row);
        }
      }
      
      console.log('读取的数据行数:', jsonData.length);
      
      // 设置原始表头和数据
      originalHeaders.value = headers;
      originalTableData.value = jsonData;
      
      console.log('识别到的表头:', headers);
      console.log('读取的数据行数:', jsonData.length);
      
      // 在设置数据之后，初始化所有原始列为可见
      visibleOriginalColumns.value = [...originalHeaders.value];
      
      // 创建映射关系，从原始表格到目标表格
      const foundMappings = {}
      
      // 定义字段映射关系
      const fieldMappings = {
        // 厂商相关字段映射
        '厂商': ['厂商', '厂商品牌', '品牌', '制造商', '生产商', 'manufacturer', 'vendor', 'brand'],
        '设备/软件型号': ['设备型号', '软件型号', '设备/软件型号', '型号', '产品型号', '产品名称', '设备名称', '设备名', '设备号', '设备编号', 'model', 'product model'],
        '设备/软件分类': ['设备分类', '软件分类', '设备/软件分类', '分类', '设备类型', '类别', 'category', 'type'],
        '配置信息': ['配置信息', '配置', '设备配置', '规格', '参数', '技术参数', '详细配置', 'configuration', 'spec', 'specification'],
        '设备数量': ['设备数量', '数量', '台数', '套数', '装机量', 'quantity', 'count', 'number'],
        '城市': ['城市', '地区', '所在城市', '使用地区', '地点', 'city', 'location', 'area'],
        '机房地址': ['机房地址', '地址', '安装地点', '使用地点', '详细地址', '位置', 'address', 'location address'],
        '服务级别': ['服务级别', '服务等级', '支持级别', '维保级别', '服务类型', 'service level', 'support level'],
        '服务周期': ['服务周期', '周期', '合同期', '维保时间', '年限', 'service period', 'contract period'],
        '服务周期单位': ['周期单位', '单位', '时间单位', 'period unit'],
        '服务范围': ['服务范围', '服务内容', '维保范围', '服务说明', 'service scope', 'coverage'],
        '单价': ['单价', '价格', '报价', '维保单价', '年单价', 'price', 'unit price'],
        '备注': ['备注', '说明', '附注', '其他', '额外说明', 'note', 'remark', 'comment'],
        '设备原值单价': ['设备原值', '原始价格', '整机价格', '设备原值单价', 'original price', 'full price'],
        '特殊需求': ['特殊需求', '特殊要求', '额外需求', '客户需求', 'special requirement', 'special need'],
        '易损件类型': ['易损件', '易损件类型', '易损件种类', 'consumable type'],
        '耗材包数量': ['耗材数量', '耗材包数量', '耗材包', 'consumable count']
      }
      
      // 尝试映射原始表格的列到目标表格的列
      for (const [targetField, possibleFields] of Object.entries(fieldMappings)) {
        for (const originalHeader of originalHeaders.value) {
          // 检查原始表头是否匹配任何可能的字段
          const normalizedHeader = String(originalHeader).trim().toLowerCase()
          
          for (const possibleField of possibleFields) {
            if (normalizedHeader.includes(possibleField.toLowerCase())) {
              foundMappings[targetField] = originalHeader
              break
            }
          }
          
          // 如果找到了映射，就跳出循环
          if (foundMappings[targetField]) {
            break
          }
        }
      }
      
      console.log('找到的映射关系:', foundMappings);
      
      // 确保基本字段都有映射
      if (!foundMappings['序号']) {
        foundMappings['序号'] = 'auto_generated';
      }
      
      // 生成转换表格
      convertedTableData.value = originalTableData.value.map((row, index) => {
        const convertedRow = {}
        
        // 为目标表格的每一列都初始化一个空值
        targetHeaders.value.forEach(header => {
          convertedRow[header] = ''
        })
        
        // 设置序号
        convertedRow['序号'] = (index + 1).toString()
        
        // 设置默认值
        convertedRow['设备数量'] = '1'
        convertedRow['服务周期'] = '1'
        convertedRow['服务周期单位'] = '年'
        convertedRow['服务范围'] = '维保服务'
        convertedRow['服务级别'] = '7*24*NCR'
        
        // 根据找到的映射关系填充数据
        for (const [targetHeader, sourceHeader] of Object.entries(foundMappings)) {
          if (sourceHeader === 'auto_generated') continue; // 跳过自动生成的字段
          
          if (row[sourceHeader] !== undefined) {
            convertedRow[targetHeader] = row[sourceHeader].toString()
          }
        }
        
        // 特殊处理某些字段
        
        // 尝试从各种配置信息字段中提取信息
        const configFields = ['设备数据', '配置', '规格', '参数', '详细信息']
        for (const field of configFields) {
          if (row[field] && !convertedRow['配置信息']) {
            convertedRow['配置信息'] = row[field].toString()
          }
        }
        
        // 尝试合并SN信息到配置信息中
        for (const header of originalHeaders.value) {
          const headerStr = String(header);
          if ((headerStr.includes('SN') || headerStr.includes('序列号')) && row[header]) {
            if (convertedRow['配置信息']) {
              convertedRow['配置信息'] += `; ${header}: ${row[header]}`
            } else {
              convertedRow['配置信息'] = `${header}: ${row[header]}`
            }
          }
        }
        
        // 尝试提取地址信息
        const addressFields = ['地址', '位置', '安装地点', '使用地点', 'address', 'location']
        for (const header of originalHeaders.value) {
          for (const addressField of addressFields) {
            if (String(header).toLowerCase().includes(addressField.toLowerCase()) && row[header] && !convertedRow['机房地址']) {
              convertedRow['机房地址'] = row[header].toString()
              break
            }
          }
        }
        
        // 尝试提取城市信息
        const cityFields = ['城市', '地区', '所在城市', '使用地区', 'city', 'area']
        for (const header of originalHeaders.value) {
          for (const cityField of cityFields) {
            if (String(header).toLowerCase().includes(cityField.toLowerCase()) && row[header] && !convertedRow['城市']) {
              convertedRow['城市'] = row[header].toString()
              break
            }
          }
        }
        
        // 如果地址包含城市信息但城市字段为空，尝试从地址中提取城市
        if (convertedRow['机房地址'] && !convertedRow['城市']) {
          const address = convertedRow['机房地址']
          // 简单提取规则：取地址的前两个字符作为城市
          // 这里可以根据需要改进提取逻辑
          if (address.length >= 2) {
            convertedRow['城市'] = address.substring(0, 2)
          }
        }
        
        return convertedRow
      })
      
      // 默认显示所有原始列，确保可以看到完整的原始数据
      visibleOriginalColumns.value = [...originalHeaders.value];
      
      // 配置转换后表格显示的列 - 使用固定表头
      visibleColumns.value = targetHeaders.value;
      
    } catch (error) {
      console.error('处理Excel文件时出错:', error)
      alert('Excel文件解析失败：' + (error.message || '未知错误') + '\n请确保文件格式正确且包含有效数据')
    }
  }
  reader.readAsArrayBuffer(file)
}

// 初始化可见列
function initializeVisibleColumns(mappings) {
  // 使用固定的表头列表
  visibleColumns.value = [...targetHeaders.value];
}

// 向转换表格添加一行
function addRow() {
  const newRow = {}
  targetHeaders.value.forEach(header => {
    newRow[header] = ''
  })
  convertedTableData.value.push(newRow)
}

// 更新单元格数据（由于使用 shallowRef，需要手动更新）
function updateCell(rowIndex, header, event) {
  const value = event.target.value
  // 直接修改对象属性
  convertedTableData.value[rowIndex][header] = value
}

// 导出转换后的表格
function exportConvertedData() {
  const ws = XLSX.utils.json_to_sheet(convertedTableData.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  XLSX.writeFile(wb, '转换后的表格.xlsx')
}

// 重置转换数据
function resetConvertData() {
  originalTableData.value = []
  originalHeaders.value = []
  convertedTableData.value = []
  visibleOriginalColumns.value = []

  // 显示提示信息给用户
  alert('数据已清空。请重新上传Excel文件进行转换。')
}

// 清空指定列的数据
function clearColumn(columnName) {
  convertedTableData.value.forEach(row => {
    row[columnName] = ''
  })
}

// 打开列映射编辑对话框
function openMappingDialog(columnName, columnIndex) {
  // 序号列不允许修改映射
  if (columnName === '序号') {
    return
  }
  editingColumn.value = columnName
  editingColumnIndex.value = columnIndex
  selectedSourceColumn.value = ''
  showMappingDialog.value = true
}

// 关闭列映射编辑对话框
function closeMappingDialog() {
  showMappingDialog.value = false
  editingColumn.value = ''
  editingColumnIndex.value = -1
  selectedSourceColumn.value = ''
}

// 应用列映射
// 应用列映射 - 优化版本，使用批量替换避免频繁响应式更新
async function applyMapping() {
  if (!editingColumn.value) return

  const targetColumn = editingColumn.value
  const sourceColumn = selectedSourceColumn.value
  const originalData = originalTableData.value
  const convertedData = convertedTableData.value

  // 立即关闭对话框
  showMappingDialog.value = false

  // 使用 requestAnimationFrame 确保 UI 先更新（关闭对话框动画）
  await new Promise(resolve => requestAnimationFrame(() => resolve()))

  // 使用批量替换而非逐行修改，大幅减少响应式更新次数
  const newData = convertedData.map((row, index) => {
    const newRow = { ...row }
    if (sourceColumn === '') {
      newRow[targetColumn] = ''
    } else if (index < originalData.length) {
      const sourceValue = originalData[index][sourceColumn]
      newRow[targetColumn] = sourceValue !== undefined ? String(sourceValue) : ''
    }
    return newRow
  })

  // 一次性替换整个数组，只触发一次响应式更新
  convertedTableData.value = newData

  // 清理状态
  editingColumn.value = ''
  selectedSourceColumn.value = ''
  editingColumnIndex.value = -1
}

// 将转换后的数据发送到智能匹配界面
async function sendToMatch() {
  // 允许两种来源：1) 转换后表格 2) 当前表格已有数据
  let matchItems = []
  if (convertedTableData.value.length > 0) {
    matchItems = convertedTableData.value.map(row => ({
      category: row['设备/软件分类'] || '',
      manufacturer: row['厂商'] || '',
      model: row['设备/软件型号'] || '',
      serviceLevel: row['服务级别'] || '',
      matchedModel: '',
      matchRate: 0,
      price: undefined,
      originalPrice: undefined,
      serviceLevelPrice: undefined,
      serviceLevelCoefficient: 1,
      matchedServiceLevel: null,
      possibleMatches: [],
      deviceCategory: ''
    }))
  } else if (tableData.value.length > 0) {
    // 从当前列表重跑匹配（用于数据源切换时）
    matchItems = tableData.value.map(item => ({
      category: item.deviceCategory || item.category || '',
      manufacturer: item.manufacturer || '',
      model: item.model || '',
      serviceLevel: item.serviceLevel || '',
      matchedModel: '',
      matchRate: 0,
      price: undefined,
      originalPrice: undefined,
      serviceLevelPrice: undefined,
      serviceLevelCoefficient: 1,
      matchedServiceLevel: null,
      possibleMatches: [],
      deviceCategory: ''
    }))
  } else {
    alert('没有可匹配的数据')
    return
  }
  
  // 更新匹配数据
  tableData.value = matchItems
  
  // 切换到匹配界面
  activeFunction.value = 'match'
  
  // 自动调用匹配API（带进度条）
  matchingInProgress.value = true
  matchingTotal.value = matchItems.length
  matchingCompleted.value = 0

  // 并发限制，避免一次性请求过多
  const concurrency = 8
  let current = 0
  async function worker() {
    while (current < matchItems.length) {
      const index = current++
      const item = matchItems[index]
    try {
      // 准备请求数据
      const matchRequest = {
        manufacturer: item.manufacturer,
        model: item.model,
          category: item.category,
          source: dataSource.value
      }
      
      // 调用匹配API
      const response = await axios.post(`${API_URL}/match/`, matchRequest)
      
      // 更新匹配结果
      if (response.data) {
        const result = response.data
        tableData.value[index].matchedModel = result.matched_model || ''
        tableData.value[index].matchRate = result.match_rate || 0
        tableData.value[index].originalPrice = result.price
        tableData.value[index].deviceCategory = result.device_category || result.category || '' // 设置设备三级分类
        
        // 计算服务级别调整后的价格
        if (result.price && item.serviceLevel) {
          const priceCalculation = calculateServiceLevelPrice(
            result.price,
            item.serviceLevel,
            serviceLevels.value
          )

          tableData.value[index].price = priceCalculation.adjustedPrice
          tableData.value[index].serviceLevelPrice = priceCalculation.adjustedPrice
          tableData.value[index].serviceLevelCoefficient = priceCalculation.coefficient
          tableData.value[index].matchedServiceLevel = priceCalculation.matchedLevel
        } else {
          tableData.value[index].price = result.price
          tableData.value[index].serviceLevelPrice = result.price
          tableData.value[index].serviceLevelCoefficient = 1
          tableData.value[index].matchedServiceLevel = null
        }
        // 直接使用后端返回的厂商信息（匹配设备对应的厂商）
        if (result.manufacturer) {
          tableData.value[index].manufacturer = result.manufacturer
        }
      }
      } catch (error) {
      console.error('匹配API调用失败:', error)
      } finally {
        matchingCompleted.value++
      }
    }
  }
  await Promise.all(new Array(Math.min(concurrency, matchItems.length)).fill(0).map(() => worker()))
  matchingInProgress.value = false
}

// 重置匹配数据
function resetMatchData() {
  tableData.value = []
  activeModelIndex.value = null
  modelOptions.value = []
}

// 生成报价单
function generateQuotes() {
  // 检查是否有必要的数据
  if (originalTableData.value.length === 0 && convertedTableData.value.length === 0) {
    alert('请先使用智能识别功能上传表格数据')
    return
  }
  
  if (tableData.value.length === 0) {
    alert('请先使用智能匹配功能进行匹配')
    return
  }
  
  // 生成原始表报价单
  if (originalTableData.value.length > 0) {
    // 创建包含原始表头 + 单价列的表头
    originalQuoteHeaders.value = [...originalHeaders.value, '单价']
    
    // 为每一行添加单价信息
    originalQuoteData.value = originalTableData.value.map((row, index) => {
      // 尝试查找型号列和厂商列
      const modelHeader = originalHeaders.value.find(h => 
        h.toLowerCase().includes('型号') || 
        h.toLowerCase().includes('model') || 
        h.toLowerCase().includes('设备') || 
        h.toLowerCase().includes('产品')
      ) || ''
      
      const manufacturerHeader = originalHeaders.value.find(h => 
        h.toLowerCase().includes('厂商') || 
        h.toLowerCase().includes('品牌') || 
        h.toLowerCase().includes('制造商') || 
        h.toLowerCase().includes('生产商') || 
        h.toLowerCase().includes('manufacturer') || 
        h.toLowerCase().includes('vendor')
      ) || ''
      
      // 获取型号和厂商值
      const modelValue = row[modelHeader] || ''
      const manufacturerValue = row[manufacturerHeader] || ''
      
      // 获取服务级别值（如果存在）
      const serviceLevelHeader = originalHeaders.value.find(h => 
        h.toLowerCase().includes('服务级别') || 
        h.toLowerCase().includes('service') || 
        h.toLowerCase().includes('sla')
      ) || ''
      const serviceLevelValue = row[serviceLevelHeader] || ''
      
      // 查找匹配的设备，优先使用索引匹配（如果索引有效）
      let matchedItem = null
      if (index < tableData.value.length) {
        matchedItem = tableData.value[index]
      }
      
      // 如果索引匹配失败，尝试精确匹配
      if (!matchedItem || matchedItem.model !== modelValue) {
        matchedItem = tableData.value.find(item => 
          item.model === modelValue && 
          item.manufacturer === manufacturerValue &&
          item.serviceLevel === serviceLevelValue
        )
      }
      
      // 如果没有精确匹配，尝试只匹配型号和服务级别
      if (!matchedItem) {
        matchedItem = tableData.value.find(item => 
          item.model === modelValue &&
          item.serviceLevel === serviceLevelValue
        )
      }
      
      // 如果仍然没有匹配，尝试只匹配型号
      if (!matchedItem) {
        matchedItem = tableData.value.find(item => 
          item.model === modelValue
        )
      }
      
      // 创建包含原始数据的新对象
      const newRow = { ...row }
      
      // 添加单价列（数字类型）- 使用服务级别调整后的价格
      if (matchedItem?.serviceLevelPrice !== undefined) {
        newRow['单价'] = matchedItem.serviceLevelPrice
      } else if (matchedItem?.price) {
        newRow['单价'] = matchedItem.price
      } else {
        newRow['单价'] = null
      }
      
      return newRow
    })
  }
  
  // 生成转换后报价单
  if (convertedTableData.value.length > 0) {
    // 转换后报价单表头与转换后表格相同
    
    // 为每一行添加匹配的单价信息
    convertedQuoteData.value = convertedTableData.value.map((row, index) => {
      // 查找匹配的设备
      const modelValue = row['设备/软件型号'] || ''
      const manufacturerValue = row['厂商'] || ''
      const serviceLevelValue = row['服务级别'] || ''
      
      // 优先使用索引匹配（如果索引有效）
      let matchedItem = null
      if (index < tableData.value.length) {
        matchedItem = tableData.value[index]
      }
      
      // 如果索引匹配失败，尝试精确匹配
      if (!matchedItem || matchedItem.model !== modelValue) {
        matchedItem = tableData.value.find(item => 
          item.model === modelValue && 
          item.manufacturer === manufacturerValue &&
          item.serviceLevel === serviceLevelValue
        )
      }
      
      // 如果没有精确匹配，尝试只匹配型号和服务级别
      if (!matchedItem) {
        matchedItem = tableData.value.find(item => 
          item.model === modelValue &&
          item.serviceLevel === serviceLevelValue
        )
      }
      
      // 如果仍然没有匹配，尝试只匹配型号
      if (!matchedItem) {
        matchedItem = tableData.value.find(item => 
          item.model === modelValue
        )
      }
      
      // 创建包含转换后数据的新对象
      const newRow = { ...row }
      
      // 设置单价字段（数字类型）- 使用服务级别调整后的价格
      if (matchedItem?.serviceLevelPrice !== undefined) {
        newRow['单价'] = matchedItem.serviceLevelPrice
      } else if (matchedItem?.price) {
        newRow['单价'] = matchedItem.price
      }
      
      return newRow
    })
  }
  
  // 切换到报价单功能
  activeFunction.value = 'quote'
  
  // 确保重要列在报价单中可见
  if (!visibleQuoteColumns.value.includes("单价")) {
    visibleQuoteColumns.value.push("单价");
  }
  
  if (!visibleQuoteColumns.value.includes("设备/软件型号")) {
    visibleQuoteColumns.value.push("设备/软件型号");
  }
}

// 导出报价单
function exportQuotes() {
  if (originalQuoteData.value.length === 0 && convertedQuoteData.value.length === 0) {
    alert('没有可导出的报价单数据')
    return
  }
  
  // 创建一个新的工作簿
  const wb = XLSX.utils.book_new()
  
  // 导出原始表报价单（如果有）
  if (originalQuoteData.value.length > 0) {
    const ws1 = XLSX.utils.json_to_sheet(originalQuoteData.value)
    XLSX.utils.book_append_sheet(wb, ws1, '原始表报价单')
  }
  
  // 导出转换后报价单（如果有）
  if (convertedQuoteData.value.length > 0) {
    const ws2 = XLSX.utils.json_to_sheet(convertedQuoteData.value)
    XLSX.utils.book_append_sheet(wb, ws2, '转换后报价单')
  }
  
  // 导出Excel文件
  XLSX.writeFile(wb, '设备报价单.xlsx')
}

// 重置报价单数据
function resetQuotes() {
  originalQuoteData.value = []
  originalQuoteHeaders.value = []
  convertedQuoteData.value = []
}

// 以下是原有的函数
async function handleFileChange(event) {
  const file = event.target.files[0]
  if (!file) return
  
  // 清空之前的数据，确保新导入覆盖旧数据
  tableData.value = []
  
  const reader = new FileReader()
  reader.onload = async (e) => {
    try {
      const data = new Uint8Array(e.target.result)
      const workbook = XLSX.read(data, { type: 'array' })
      const firstSheet = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[firstSheet]
      const json = XLSX.utils.sheet_to_json(worksheet)
      
      // 处理数据并调用后端API进行匹配
      const items = json.map(row => {
        // 标准化分类
        let category = row['设备/软件分类'] || ''
        // 分类标准化映射
        const categoryMap = {
          '存储': '硬件',
          '服务器': '硬件',
          '计算机': '硬件',
          '网络': '硬件',
          '安全': '硬件',
          // 可以添加更多映射
        }
        // 如果有映射，使用映射后的分类
        if (category in categoryMap) {
          category = categoryMap[category]
        }
        
        const serviceLevel = row['服务级别'] || ''
        return {
          category: category,
          manufacturer: row['厂商'] || '',
          model: row['设备/软件型号'] || '',
          serviceLevel: serviceLevel,
          matchedModel: '',
          matchRate: 0,
          price: undefined,
          originalPrice: undefined,
          serviceLevelPrice: undefined,
          serviceLevelCoefficient: 1,
          matchedServiceLevel: null,
          deviceCategory: '',
          possibleMatches: []
        }
      })
      
      // 调用批量匹配API - 使用分批并发处理解决大数据量超时问题
      try {
        const batchSize = 200 // 每批处理200条数据
        const totalBatches = Math.ceil(items.length / batchSize)
        let completedBatches = 0
        const allResults = []

        // 显示大文件处理提示
        if (items.length > 500) {
          ElMessage.info(`正在处理 ${items.length} 条数据，请稍候...`)
        }

        // 分批并发处理
        for (let batchNum = 0; batchNum < totalBatches; batchNum++) {
          const startIdx = batchNum * batchSize
          const endIdx = Math.min(startIdx + batchSize, items.length)
          const batchItems = items.slice(startIdx, endIdx)

          const matchRequests = batchItems.map(item => ({
            manufacturer: item.manufacturer,
            model: item.model,
            category: item.category,
            source: dataSource.value || 'datacenter'
          }))

          try {
            const response = await axios.post(`${API_URL}/bulk-match/`, { items: matchRequests }, { timeout: 60000 })
            allResults.push(...response.data)

            completedBatches++
            if (items.length > 500) {
              ElMessage.success(`处理进度: ${completedBatches}/${totalBatches} 批 (${Math.round(completedBatches / totalBatches * 100)}%)`)
            }
          } catch (error) {
            console.error(`批次 ${batchNum + 1} 匹配失败:`, error)
            // 为失败的批次创建空结果
            allResults.push(...batchItems.map(() => ({
              matched_model: '',
              match_rate: 0,
              price: null,
              device_category: ''
            })))
          }
        }

        // 更新匹配结果 - 批量更新优化性能
        for (let i = 0; i < items.length; i++) {
          const result = allResults[i]
          if (!result) continue

          items[i].matchedModel = result.matched_model || ''
          items[i].matchRate = result.match_rate || 0
          items[i].originalPrice = result.price
          items[i].deviceCategory = result.device_category || ''
          if (result.manufacturer) {
            items[i].manufacturer = result.manufacturer
          }

          // 计算服务级别调整后的价格
          if (result.price && items[i].serviceLevel) {
            const priceCalculation = calculateServiceLevelPrice(
              result.price,
              items[i].serviceLevel,
              serviceLevels.value
            )
            items[i].price = priceCalculation.adjustedPrice
            items[i].serviceLevelPrice = priceCalculation.adjustedPrice
            items[i].serviceLevelCoefficient = priceCalculation.coefficient
            items[i].matchedServiceLevel = priceCalculation.matchedLevel
          } else {
            items[i].price = result.price
            items[i].serviceLevelPrice = result.price
            items[i].serviceLevelCoefficient = 1
            items[i].matchedServiceLevel = null
          }

          // 初始化可能的匹配结果为空数组
          items[i].possibleMatches = []
        }

        // 对于小数据量（<500条），获取可能匹配选项；大数据量跳过此步骤
        if (items.length <= 500) {
          const searchConcurrency = 10
          let searchIndex = 0

          async function searchWorker() {
            while (searchIndex < items.length) {
              const i = searchIndex++
              const item = items[i]

              try {
                let searchModel = item.matchedModel || item.model
                const searchResponse = await axios.get(`${API_URL}/devices/search/?model=${encodeURIComponent(searchModel)}&source=${encodeURIComponent(dataSource.value)}`, { timeout: 10000 })
                items[i].possibleMatches = searchResponse.data
              } catch (error) {
                items[i].possibleMatches = []
              }
            }
          }

          await Promise.all(new Array(Math.min(searchConcurrency, items.length)).fill(0).map(() => searchWorker()))
        }

        if (items.length > 500) {
          ElMessage.success(`数据处理完成！共 ${items.length} 条`)
        }
      } catch (error) {
        console.error('匹配API调用失败:', error)
        alert('匹配API调用失败，请检查网络连接或稍后重试')
        
        // 如果API调用失败，使用模拟数据
        for (const item of items) {
          const matchRate = Math.random() * 100

          // 根据匹配度决定是否默认填充匹配型号
          if (matchRate >= 50) {
            item.matchedModel = `Matched-${item.model}`
            item.deviceCategory = '硬件' // 默认分类
            const basePrice = Math.random() * 10000
            item.originalPrice = basePrice

            // 计算服务级别调整后的价格
            if (basePrice && item.serviceLevel) {
              const priceCalculation = calculateServiceLevelPrice(
                basePrice,
                item.serviceLevel,
                serviceLevels.value
              )
              item.price = priceCalculation.adjustedPrice
              item.serviceLevelPrice = priceCalculation.adjustedPrice
              item.serviceLevelCoefficient = priceCalculation.coefficient
              item.matchedServiceLevel = priceCalculation.matchedLevel
            } else {
              item.price = basePrice
              item.serviceLevelPrice = basePrice
              item.serviceLevelCoefficient = 1
              item.matchedServiceLevel = null
            }
          } else {
            item.matchedModel = ''
            item.deviceCategory = ''
            item.originalPrice = undefined
            item.price = undefined
            item.serviceLevelPrice = undefined
            item.serviceLevelCoefficient = 1
            item.matchedServiceLevel = null
          }

          item.matchRate = matchRate
        }
      }
      
      tableData.value = items
      alert('文件解析成功')
    } catch (error) {
      console.error(error)
      alert('文件解析失败')
    }
    
    // 重置文件输入控件，使其可以重复选择同一个文件
    event.target.value = ''
  }
  reader.readAsArrayBuffer(file)
}

async function showModelOptions(index, model) {
  activeModelIndex.value = index
  const currentItem = tableData.value[index]
  
  try {
    // 如果已经有缓存的可能匹配结果，直接使用
    if (currentItem.possibleMatches && currentItem.possibleMatches.length > 0) {
      modelOptions.value = currentItem.possibleMatches
    } else {
      // 否则从后端获取可能匹配的型号列表
      const searchModel = currentItem.matchedModel || model
      const response = await axios.get(`${API_URL}/devices/search/?model=${encodeURIComponent(searchModel)}&source=${encodeURIComponent(dataSource.value)}`)
      modelOptions.value = response.data
      // 缓存可能的匹配结果
      currentItem.possibleMatches = response.data
      
      // 如果搜索的是匹配型号，且未包含原始型号的搜索结果，则再次搜索原始型号
      if (currentItem.matchedModel && searchModel !== model) {
        const origResponse = await axios.get(`${API_URL}/devices/search/?model=${encodeURIComponent(model)}&source=${encodeURIComponent(dataSource.value)}`)
        // 合并结果
        for (const item of origResponse.data) {
          if (!modelOptions.value.some(m => m.model === item.model)) {
            modelOptions.value.push(item)
            currentItem.possibleMatches.push(item)
          }
        }
      }
    }
    
    // 如果没有获取到可能的匹配，但当前已有匹配型号，确保下拉框中包含当前匹配型号
    if ((modelOptions.value.length === 0 || !modelOptions.value.some(m => m.model === currentItem.matchedModel)) && currentItem.matchedModel) {
      // 查询当前匹配型号的详细信息
      try {
        const matchResponse = await axios.get(`${API_URL}/devices/search/?model=${encodeURIComponent(currentItem.matchedModel)}&source=${encodeURIComponent(dataSource.value)}`)
        if (matchResponse.data.length > 0) {
          // 如果找到匹配型号的详细信息，添加到选项列表
          const matchInfo = matchResponse.data.find(m => m.model === currentItem.matchedModel) || matchResponse.data[0]
          if (!modelOptions.value.some(m => m.model === matchInfo.model)) {
            modelOptions.value.push(matchInfo)
          }
        } else {
          // 如果找不到匹配型号的详细信息，使用默认信息
          modelOptions.value.push({
            id: 'current-match',
            model: currentItem.matchedModel,
            manufacturer: '当前匹配',
            full_price: currentItem.price / (0.02 * 1.06) // 根据维保价格反推整机价格
          })
        }
      } catch (error) {
        console.error('获取当前匹配型号详情失败:', error)
        // 创建一个包含当前匹配型号的选项
        modelOptions.value.push({
          id: 'current-match',
          model: currentItem.matchedModel,
          manufacturer: '当前匹配',
          full_price: currentItem.price / (0.02 * 1.06) // 根据维保价格反推整机价格
        })
      }
    }
  } catch (error) {
    console.error('获取匹配型号失败:', error)
    modelOptions.value = []
    
    // 同样，如果API调用失败但有当前匹配型号，也要确保显示
    if (currentItem.matchedModel) {
      modelOptions.value = [{
        id: 'current-match',
        model: currentItem.matchedModel,
        manufacturer: '当前匹配',
        full_price: currentItem.price / (0.02 * 1.06)
      }]
    }
  }
}

async function updateModelSelection(index) {
  const selectedItem = tableData.value[index]
  const originalDeviceModel = selectedItem.model // 获取原始设备型号
  
  if (selectedItem.matchedModel) {
    // 查找匹配的设备信息
    const selectedModel = selectedItem.possibleMatches?.find(m => m.model === selectedItem.matchedModel) ||
                        modelOptions.value?.find(m => m.model === selectedItem.matchedModel)
    if (selectedModel) {
      // 自动同步分类、价格和厂商
      const primary_category = selectedModel.primary_category || ''
      const secondary_category = selectedModel.secondary_category || ''
      const tertiary_category = selectedModel.tertiary_category || ''
      const device_price = selectedModel.device_price || 0
      
      // 查找费率
      const rate = findRate(rateList.value, { primary_category, secondary_category, tertiary_category })
      
      // 如果找不到费率，使用默认费率2%
      const finalRate = rate || 0.02
      
      // 批量更新所有具有相同设备型号的行
      const updatedIndexes = []
      tableData.value.forEach((item, idx) => {
        if (item.model === originalDeviceModel) {
          // 计算价格，确保有设备价格
          let price = null
          if (device_price > 0) {
            price = calcStandardRatePrice(device_price, finalRate)
          }
          
          // 记录原始价格用于显示
          const originalPrice = price
          
          // 计算服务级别调整后的价格
          if (price && item.serviceLevel) {
            const priceCalculation = calculateServiceLevelPrice(
              price, 
              item.serviceLevel, 
              serviceLevels.value
            )
            
            price = priceCalculation.adjustedPrice
          }
          
          tableData.value[idx] = {
            ...item,
            matchedModel: selectedModel.model,
            manufacturer: selectedModel.manufacturer, // 同步厂商
            deviceCategory: selectedModel.tertiary_category || selectedModel.device_category || selectedModel.category || '', // 优先用三级分类
            primary_category,
            secondary_category,
            tertiary_category,
            device_price,
            matchRate: 100,
            price,
            originalPrice,
            serviceLevelPrice: price,
            serviceLevelCoefficient: item.serviceLevel ? (price / originalPrice) : 1
          }
          updatedIndexes.push(idx)
        }
      })
      
      // 提示用户批量更新了多少行
      if (updatedIndexes.length > 1) {
        ElMessage.success(`已批量更新 ${updatedIndexes.length} 行相同设备型号的匹配结果`)
      }
    }
  } else {
    // 批量重置所有具有相同设备型号的行
    const updatedIndexes = []
    tableData.value.forEach((item, idx) => {
      if (item.model === originalDeviceModel) {
        tableData.value[idx] = {
          ...item,
          matchRate: 0,
          price: undefined,
          originalPrice: undefined,
          serviceLevelPrice: undefined,
          serviceLevelCoefficient: 1,
          deviceCategory: '',
          primary_category: '',
          secondary_category: '',
          tertiary_category: '',
          device_price: 0,
          manufacturer: '', // 清空厂商
          matchedModel: '' // 清空匹配型号
        }
        updatedIndexes.push(idx)
      }
    })
    
    // 提示用户批量重置了多少行
    if (updatedIndexes.length > 1) {
      ElMessage.info(`已批量重置 ${updatedIndexes.length} 行相同设备型号的匹配结果`)
    }
  }
  // 关闭选择器
  activeModelIndex.value = null
}

// 获取设备型号计数
function getDeviceModelCount() {
  if (!originalTableData.value || originalTableData.value.length === 0) {
    return 0;
  }
  
  // 查找可能的设备型号列名
  const possibleModelColumns = [
    '型号', '设备型号', '设备/软件型号', '软件型号', '产品型号', 
    '产品名称', '设备名称', '设备名', '设备号', '设备编号', 
    'model', 'product model', 'device model'
  ];
  
  // 找到实际存在的设备型号列
  const modelColumn = originalHeaders.value.find(header => 
    possibleModelColumns.some(col => 
      String(header).toLowerCase().includes(col.toLowerCase()) || 
      col.toLowerCase().includes(String(header).toLowerCase())
    )
  );
  
  if (!modelColumn) {
    // 如果没有找到设备型号列，返回总行数
    return originalTableData.value.length;
  }
  
  // 统计有设备型号数据的行数
  return originalTableData.value.filter(row => {
    const modelValue = row[modelColumn];
    return modelValue && 
           modelValue !== '' && 
           modelValue !== null && 
           modelValue !== undefined &&
           String(modelValue).trim() !== '';
  }).length;
}

// 计算两个字符串的相似度百分比 (0-100)
function calculateSimilarity(str1, str2) {
  if (!str1 || !str2) return 0;
  
  str1 = String(str1).toLowerCase();
  str2 = String(str2).toLowerCase();
  
  const maxLength = Math.max(str1.length, str2.length);
  if (maxLength === 0) return 100; // 两个空串被认为是完全匹配的
  
  // 计算编辑距离
  const matrix = [];
  for (let i = 0; i <= str1.length; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= str2.length; j++) {
    matrix[0][j] = j;
  }
  
  for (let i = 1; i <= str1.length; i++) {
    for (let j = 1; j <= str2.length; j++) {
      const cost = str1[i-1] === str2[j-1] ? 0 : 1;
      matrix[i][j] = Math.min(
        matrix[i-1][j] + 1,     // 删除
        matrix[i][j-1] + 1,     // 插入
        matrix[i-1][j-1] + cost // 替换
      );
    }
  }
  
  const editDistance = matrix[str1.length][str2.length];
  const similarity = ((1 - editDistance / maxLength) * 100);
  return similarity;
}

function exportData() {
  const exportData = tableData.value.map(item => ({
    '厂商': item.manufacturer,
    '设备/软件型号': item.model,
    '设备/软件分类': item.deviceCategory,
    '匹配型号': item.matchedModel || '未匹配',
    '匹配度': item.matchRate ? `${item.matchRate.toFixed(2)}%` : '0%',
    '原始单价': item.originalPrice ? `¥${item.originalPrice.toFixed(2)}` : '-',
    '调整后单价': item.price ? `¥${item.price.toFixed(2)}` : '-',
    '服务级别系数': item.serviceLevelCoefficient !== 1 ? item.serviceLevelCoefficient.toFixed(2) : '-'
  }))
  
  const ws = XLSX.utils.json_to_sheet(exportData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, 'Sheet1')
  XLSX.writeFile(wb, '报价结果.xlsx')
}

const handleSearch = async (page = 1, pageSize = 20) => {
  if (searchTimeout.value) {
    clearTimeout(searchTimeout.value);
  }
  searchTimeout.value = setTimeout(async () => {
    // 放宽输入长度限制为1
    if (!searchQuery.value.model || searchQuery.value.model.length < 1) {
      searchResults.value = [];
      totalResults.value = 0;
      return;
    }
    try {
    const params = new URLSearchParams();
      params.append('model_number', searchQuery.value.model);
      params.append('limit', pageSize);
      const offset = Number((page - 1) * pageSize);
      params.append('offset', isNaN(offset) ? 0 : offset);
    params.append('source', dataSource.value);
    const response = await fetch(`${API_URL}/devices/search/?${params}`);
      if (!response.ok) {
        throw new Error('搜索请求失败');
      }
      const data = await response.json();
      searchResults.value = data.data;
      totalResults.value = data.total;
    } catch (error) {
      console.error('搜索设备失败:', error);
      searchResults.value = [];
      totalResults.value = 0;
    }
  }, 300); // 300ms 防抖延迟
}

const selectSearchResult = (result, event) => {
  // 兼容后端返回model_number或model
  const selectedModel = result.model_number || result.model;
  searchQuery.value.model = selectedModel;
  const index = activeModelIndex.value;
  if (index !== null && index >= 0 && index < tableData.value.length) {
    const originalDeviceModel = tableData.value[index].model; // 获取原始设备型号
    
    // 同步分类字段
    const primary_category = result.primary_category || '';
    const secondary_category = result.secondary_category || '';
    const tertiary_category = result.tertiary_category || '';
    const device_price = result.device_price || 0;
    
    // 查找费率
    const rate = findRate(rateList.value, { primary_category, secondary_category, tertiary_category });
    
    // 如果找不到费率，使用默认费率2%
    const finalRate = rate || 0.02;
    
    // 批量更新所有具有相同设备型号的行
    const updatedIndexes = [];
    tableData.value.forEach((item, idx) => {
      if (item.model === originalDeviceModel) {
        // 计算价格，确保有设备价格
        let price = null;
        if (device_price > 0) {
          price = calcStandardRatePrice(device_price, finalRate);
        }
        
        // 记录原始价格用于显示
        const originalPrice = price;
        
        // 计算服务级别调整后的价格
        if (price && item.serviceLevel) {
          const priceCalculation = calculateServiceLevelPrice(
            price, 
            item.serviceLevel, 
            serviceLevels.value
          );
          
          price = priceCalculation.adjustedPrice;
        }
        
        tableData.value[idx] = {
          ...item,
          matchedModel: selectedModel,
          manufacturer: result.manufacturer, // 同步厂商
          deviceCategory: result.tertiary_category || result.device_category || result.category || '', // 优先用三级分类
          primary_category,
          secondary_category,
          tertiary_category,
          device_price,
          matchRate: calculateSimilarity(item.model, selectedModel),
          price,
          originalPrice,
          serviceLevelPrice: price,
          serviceLevelCoefficient: item.serviceLevel ? (price / originalPrice) : 1,
          possibleMatches: [result]
        };
        updatedIndexes.push(idx);
      }
    });
    
    // 提示用户批量更新了多少行
    if (updatedIndexes.length > 1) {
      ElMessage.success(`已批量更新 ${updatedIndexes.length} 行相同设备型号的匹配结果`);
    }
    
    showSearchDialog.value = false;
    activeModelIndex.value = null;
    const button = event?.target;
    if (button) {
      const originalText = button.textContent;
      button.textContent = '已选择';
      button.style.backgroundColor = '#67C23A';
      setTimeout(() => {
        button.textContent = originalText;
        button.style.backgroundColor = '#4CAF50';
      }, 800);
    }
  } else {
    setTimeout(() => {
      showSearchDialog.value = false;
    }, 500);
  }
}

// 在 setup 函数中添加 openSearch 方法
function openSearch(index) {
  activeModelIndex.value = index;
  showSearchDialog.value = true;
  currentPage.value = 1;
  // 自动填充当前行型号并立即搜索
  if (tableData.value[index] && tableData.value[index].model) {
    searchQuery.value.model = tableData.value[index].model;
    handleSearch(1, pageSize.value);
  } else {
    searchQuery.value.model = '';
    handleSearch(1, pageSize.value);
  }
  // 在对话框打开后自动聚焦到搜索输入框
  nextTick(() => {
    const searchInput = document.querySelector('.search-input input');
    if (searchInput) {
      searchInput.focus();
    }
  });
}

// 计算设备的主维保价格信息
const getMaintenancePriceInfo = (result) => {
  if (!result.device_price || !rateList.value.length) {
    return null;
  }
  
  const rate = findRate(rateList.value, {
    primary_category: result.primary_category,
    secondary_category: result.secondary_category,
    tertiary_category: result.tertiary_category
  });
  
  if (!rate) {
    return null;
  }
  
  return calcMaintenancePrices(result.device_price, rate);
};

// 在script部分添加复制功能
const copyModelInfo = (result, event) => {
  const modelToCopy = result.model_number || result.model;
  if (!modelToCopy) {
    ElMessage.error('没有可复制的型号信息');
    return;
  }
  try {
    const textarea = document.createElement('textarea');
    textarea.value = modelToCopy;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    if (event && event.target) {
      const button = event.target.closest('span') || event.target;
      if (button) {
        const originalText = button.innerText || button.textContent;
        const originalBg = button.style.backgroundColor;
        button.innerText = '已复制';
        button.style.backgroundColor = '#67C23A';
        setTimeout(() => {
          button.innerText = originalText;
          button.style.backgroundColor = originalBg;
        }, 1000);
      }
    }
    ElMessage.success('已复制型号信息');
  } catch (error) {
    console.error('复制失败:', error);
    ElMessage.error('复制失败');
  }
};

// 列选择功能
function selectAllColumns() {
  visibleColumns.value = [...targetHeaders.value];
}

function resetColumns() {
  visibleColumns.value = ["序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息", "设备数量", "城市", "机房地址", 
    "服务级别", "服务周期", "服务周期单位", "服务范围"];
}

// 初始化时确保所有列都可见
onMounted(() => {
  if (visibleColumns.value.length === 0) {
    selectAllColumns();
  }
});

// 列选择功能 - 报价单
function selectAllQuoteColumns() {
  visibleQuoteColumns.value = [...targetHeaders.value];
}

function resetQuoteColumns() {
  visibleQuoteColumns.value = ["序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息", "设备数量", "单价"];
}

// 列选择功能 - 原始表格
function selectAllOriginalColumns() {
  visibleOriginalColumns.value = [...originalHeaders.value];
}

function resetOriginalColumns() {
  // 默认显示所有原始列
  selectAllOriginalColumns();
}

// 当原始表头发生变化时，更新可见列
watch(originalHeaders, (newHeaders) => {
  if (newHeaders.length > 0) {
    // 默认显示所有列
    visibleOriginalColumns.value = [...newHeaders];
  }
});

// 字段中文映射
const fieldLabelMap = {
  manufacturer: '厂商',
  device_series: '设备系列',
  model_number: '设备型号',
  business_scenario: '业务场景',
  primary_category: '设备一级分类',
  secondary_category: '设备二级分类',
  tertiary_category: '设备三级分类',
  remarks: '备注',
  device_price: '整机价格',
  device_grade: '设备档次',
};

const hoveredModelRow = ref(null);

// 费率相关
const rateList = ref([])
onMounted(async () => {
  // ... existing code ...
  try {
    rateList.value = await fetchRates()
  } catch {}
  
  // 加载服务级别数据
  await loadServiceLevels()
})

// 加载服务级别数据
async function loadServiceLevels() {
  serviceLevelLoading.value = true
  try {
    serviceLevels.value = await fetchServiceLevels()
    console.log('服务级别数据加载成功:', serviceLevels.value)
  } catch (error) {
    console.error('加载服务级别数据失败:', error)
    ElMessage.error('加载服务级别数据失败')
  } finally {
    serviceLevelLoading.value = false
  }
}

const showAdminMenu = ref(false)
const adminSubPage = ref('')
const adminBtnRef = ref(null)
const adminMenuStyle = ref({})
function toggleAdminMenu() {
  showAdminMenu.value = !showAdminMenu.value
  activeFunction.value = 'admin'
  nextTick(() => {
    if (showAdminMenu.value && adminBtnRef.value) {
      const rect = adminBtnRef.value.getBoundingClientRect()
      adminMenuStyle.value = {
        position: 'fixed',
        left: rect.right + 4 + 'px',
        top: rect.top + 'px',
        zIndex: 1000
      }
    }
  })
}
function openAdminSubPage(page) {
  adminSubPage.value = page
  showAdminMenu.value = false
  activeFunction.value = 'admin'
}
</script>

.device-search-form {
  margin: 30px 0 20px 0;
  padding: 20px;
  border: 1px solid #eee;
  border-radius: 8px;
  background: #f9f9f9;
  max-width: 700px;
}
.form-row {
  display: flex;
  align-items: center;
  margin-bottom: 10px;
}
.form-row label {
  width: 120px;
  font-weight: bold;
}
.form-row input {
  flex: 1;
  padding: 6px 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
.device-search-results {
  margin-top: 20px;
}

<style>
/* 导航标签 */
.nav-tabs {
  display: flex;
  border-bottom: 1px solid #ddd;
  margin-bottom: 20px;
}

.tab {
  padding: 10px 20px;
  cursor: pointer;
  border: 1px solid transparent;
  border-bottom: none;
  margin-right: 5px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
}

.tab:hover {
  background-color: #f9f9f9;
}

.tab.active {
  background-color: #4CAF50;
  color: white;
  border-color: #4CAF50;
}

.upload-area {
  margin: 20px 0;
  padding: 20px;
  border: 2px dashed #ccc;
  text-align: center;
  border-radius: 8px;
}

input[type="file"] {
  display: none;
}

button {
  padding: 8px 16px;
  background-color: #4CAF50;
  color: white;
  border: none;
  cursor: pointer;
  margin: 5px;
  border-radius: 4px;
}

button:hover {
  background-color: #45a049;
}

/* 分屏视图样式 */
.split-view {
  display: flex;
  gap: 20px;
  margin-top: 20px;
  width: 100%;
  overflow: hidden;
}

.original-table, .converted-table {
  flex: 1;  /* 平均分配空间，各占一半 */
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  background-color: #f9f9f9;
  overflow: hidden;
  width: 50%;  /* 确保各占一半宽度 */
}

.table-container {
  max-height: 500px;
  overflow-y: auto;
  overflow-x: auto;  /* 启用横向滚动条 */
  margin-top: 10px;
  width: 100%;
}

h3 {
  margin-top: 0;
  color: #333;
  border-bottom: 1px solid #ddd;
  padding-bottom: 8px;
}

/* 可编辑表格样式 */
.editable-table td input {
  width: 100%;
  padding: 6px;
  border: 1px solid transparent;
  background-color: transparent;
  border-radius: 3px;
  transition: all 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal; /* 允许输入框内文本折行 */
  word-break: break-word; /* 确保长单词可以换行 */
  min-height: 30px; /* 设置最小高度 */
}

.editable-table td {
  padding: 4px !important;
  overflow: visible; /* 输入框需要在聚焦时可以溢出显示 */
  height: auto; /* 根据内容自动调整高度 */
}

.editable-table td input:focus {
  border-color: #4CAF50;
  background-color: #f0fff0;
  box-shadow: 0 0 3px rgba(76, 175, 80, 0.5);
  position: relative;
  z-index: 5;
}

/* 提升表格美观度 */
tr:nth-child(even) {
  background-color: #f9f9f9;
}

tr:hover {
  background-color: #f0f7ff;
}

/* 智能识别表格样式优化 */
.original-table .table-container, 
.converted-table .table-container {
  max-height: 450px;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

/* 调整响应式布局 */
@media (max-width: 1200px) {
  .split-view {
    flex-direction: column;
  }
  
  .original-table, .converted-table {
    width: 100%;
    max-width: 100%;
  }
}

/* 表格基础样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  table-layout: auto; /* 让表格根据内容自适应列宽 */
}
th, td {
  padding: 6px 8px;
  text-align: left;
  border: 1px solid #ddd;
  position: relative;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 60px;
  font-size: 13px;
}
/* 允许内容较多的列自动变宽 */
th, td {
  max-width: none;
}
/* 适当缩小表格字体和间距 */
@media (max-width: 900px) {
  th, td {
    font-size: 12px;
    padding: 4px 6px;
  }
}

th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
  z-index: 2;
}

/* 列宽调整样式 */
.resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 5px;
  height: 100%;
  background-color: transparent;
  cursor: col-resize;
  user-select: none;
  touch-action: none;
  z-index: 3;
}

.resizer:hover,
.resizing {
  background-color: #4CAF50;
}

/* 表头文字样式 */
.header-text {
  display: inline-block;
  max-width: calc(100% - 30px);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* 列清空按钮样式 */
.clear-col-btn {
  position: absolute;
  top: 4px;
  right: 10px;
  width: 18px;
  height: 18px;
  border: none;
  background-color: #f44336;
  color: white;
  border-radius: 50%;
  cursor: pointer;
  font-size: 14px;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s, background-color 0.2s;
  z-index: 4;
}

.clear-col-btn:hover {
  background-color: #d32f2f;
}

th:hover .clear-col-btn {
  opacity: 1;
}

/* 表格容器样式 */
.table-area, .table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  width: 100%;
  border: 1px solid #eee;
  border-radius: 4px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

/* 特殊列的初始宽度设置 */
/* 序号列 */
th:nth-child(1), td:nth-child(1) {
  width: 60px;
  min-width: 60px;
  max-width: 60px;
}

/* 厂商列和分类列 */
th:nth-child(2), td:nth-child(2),
th:nth-child(4), td:nth-child(4) {
  width: 120px;
  min-width: 120px;
}

/* 型号列和匹配型号列 - 给更多空间 */
th:nth-child(3), td:nth-child(3) {
  width: 200px;
  min-width: 150px;
}

/* 配置信息列 - 需要更宽 */
th:nth-child(5), td:nth-child(5) {
  width: 180px;
  min-width: 150px;
}

/* 数量列和单价列 - 较窄 */
th:nth-child(6), td:nth-child(6),
th:nth-child(13), td:nth-child(13) {
  width: 80px;
  min-width: 80px;
}

/* 服务相关列 - 中等宽度 */
th:nth-child(9), td:nth-child(9),
th:nth-child(10), td:nth-child(10),
th:nth-child(11), td:nth-child(11),
th:nth-child(12), td:nth-child(12) {
  width: 100px;
  min-width: 100px;
}

/* 允许可编辑表格内容换行 */
.editable-table td input {
  white-space: normal;
}

/* 匹配功能相关样式 */
.model-selector {
  width: 100%;
}

.model-selector select {
  width: 100%;
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 3px;
}

.matched {
  color: #67C23A;
  font-weight: bold;
}

.moderate-match {
  color: #E6A23C;
  font-weight: bold;
}

.low-match {
  color: #F56C6C;
  font-style: italic;
}

.low-match-hint {
  font-size: 0.8em;
  color: #F56C6C;
}

.unmatched {
  color: #F56C6C;
}

.edit-hint {
  font-size: 0.8em;
  color: #999;
  margin-left: 5px;
}

.progress-bar {
  width: 100%;
  height: 20px;
  background-color: #eee;
  border-radius: 10px;
  position: relative;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  position: absolute;
  left: 0;
  top: 0;
}

.progress-bar span {
  position: relative;
  z-index: 1;
  padding: 0 5px;
}

.actions {
  margin-top: 20px;
  text-align: right;
}

h1 {
  text-align: center;
  color: #333;
  margin: 20px 0;
}

.convert-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 15px;
}

.match-btn {
  background-color: #2196F3;
  margin-left: 10px;
}

.match-btn:hover {
  background-color: #0b7dda;
}

.quote-actions {
  display: flex;
  justify-content: center;
  margin: 15px 0 25px;
  gap: 15px;
}

.quote-actions button {
  min-width: 120px;
  padding: 10px 16px;
  font-size: 15px;
}

.no-data-message {
  text-align: center;
  color: #999;
  margin-top: 40px;
  padding: 20px;
  background-color: #f9f9f9;
  border-radius: 8px;
  border: 1px dashed #ddd;
}

.original-quote, .converted-quote {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
  overflow: hidden;
}

.original-quote h3, .converted-quote h3 {
  color: #333;
  border-bottom: 1px solid #eee;
  padding-bottom: 10px;
  margin-bottom: 15px;
}

/* 报价单表格样式 */
.original-quote table, .converted-quote table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 10px;
}

.original-quote th, .converted-quote th {
  background-color: #f2f8ff;
  font-weight: 600;
  padding: 10px 8px;
  position: sticky;
  top: 0;
  z-index: 2;
}

.original-quote td, .converted-quote td {
  padding: 8px;
  text-align: left;
  border: 1px solid #ddd;
  white-space: normal;
  word-break: break-word;
}

/* 单价列样式 */
.original-quote td:last-child, 
.converted-quote td:nth-child(13) {
  font-weight: 600;
  color: #2c3e50;
  text-align: right;
  background-color: #f0fff0;
}

/* 报价单中的列宽调整 */
@media (min-width: 1200px) {
  .split-view {
    max-width: 95%;
    margin: 0 auto;
  }
  
  .original-quote, .converted-quote {
    min-width: 45%;
  }
}

.generate-quote-btn {
  background-color: #673AB7;
  color: white;
  font-weight: bold;
  margin-left: 15px;
}

.generate-quote-btn:hover {
  background-color: #5E35B1;
}

.quote-info {
  background-color: #e8f4ff;
  padding: 12px 20px;
  border-radius: 4px;
  margin: 10px 0 20px;
  border-left: 4px solid #2196F3;
  font-size: 14px;
}

.quote-info p {
  margin: 0;
  line-height: 1.6;
  color: #0d47a1;
}

.search-button {
  margin: 5px;
  padding: 5px 10px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 5px;
}

.search-button:hover {
  background-color: #45a049;
}

/* 列映射编辑弹窗样式 */
.mapping-dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1500;
}

.mapping-dialog-content {
  background-color: white;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
  max-height: 70vh;
  overflow-y: auto;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  animation: slideIn 0.2s ease-out;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.mapping-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e0e0e0;
}

.mapping-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.mapping-header .close-button {
  background: none;
  border: none;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  padding: 0;
  width: 30px;
  height: 30px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.mapping-header .close-button:hover {
  background-color: #f0f0f0;
  color: #333;
}

.mapping-body {
  padding: 20px;
}

.mapping-hint {
  margin: 0 0 16px 0;
  font-size: 14px;
  color: #666;
  line-height: 1.5;
}

.mapping-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-height: 300px;
  overflow-y: auto;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
  padding: 8px;
}

.mapping-option {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.mapping-option:hover {
  background-color: #f5f5f5;
}

.mapping-option input[type="radio"] {
  cursor: pointer;
}

.mapping-option span {
  font-size: 14px;
  color: #333;
}

.mapping-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid #e0e0e0;
}

.mapping-footer button {
  padding: 8px 20px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn {
  background-color: #f0f0f0;
  border: 1px solid #d0d0d0;
  color: #666;
}

.cancel-btn:hover {
  background-color: #e0e0e0;
}

.confirm-btn {
  background-color: #4CAF50;
  border: 1px solid #45a049;
  color: white;
}

.confirm-btn:hover {
  background-color: #45a049;
}

/* 编辑映射按钮样式 */
.edit-mapping-btn {
  position: absolute;
  top: 4px;
  right: 32px;
  width: 18px;
  height: 18px;
  border: none;
  background-color: #2196F3;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.2s, background-color 0.2s;
  z-index: 5;
}

.edit-mapping-btn:hover {
  background-color: #1976D2;
}

th:hover .edit-mapping-btn {
  opacity: 1;
}

/* 表头文字添加点击提示样式 */
.header-text {
  cursor: pointer;
}

.header-text:hover {
  color: #2196F3;
}

.search-dialog {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.search-dialog-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  width: 80%;
  max-width: 800px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
}

.search-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 10px;
  border-bottom: 1px solid #eee;
}

.search-header h3 {
  margin: 0;
  color: #333;
}

.close-button {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
  padding: 0;
  margin: 0;
}

.close-button:hover {
  color: #333;
}

.search-form {
  margin-bottom: 20px;
}

.search-input input {
  width: 100%;
  padding: 12px;
  border: 2px solid #ddd;
  border-radius: 6px;
  font-size: 16px;
  transition: border-color 0.3s;
}

.search-input input:focus {
  outline: none;
  border-color: #4CAF50;
}

.search-results {
  max-height: calc(80vh - 180px);
  overflow-y: auto;
  padding-right: 10px;
}

.search-result-item {
  padding: 15px;
  border: 1px solid #eee;
  border-radius: 6px;
  margin-bottom: 10px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.search-result-item:hover {
  background-color: #f5f9ff;
  border-color: #4CAF50;
  transform: translateY(-1px);
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.result-info {
  display: grid;
  grid-template-columns: 2fr 2fr 1fr 1fr;
  gap: 15px;
  align-items: center;
}

.result-model {
  font-weight: bold;
  color: #2c3e50;
  font-size: 16px;
}

.result-manufacturer {
  color: #666;
}

.result-category {
  color: #888;
  font-size: 14px;
}

.result-price {
  color: #4CAF50;
  font-weight: bold;
  text-align: right;
}

.no-results {
  text-align: center;
  color: #666;
  padding: 30px;
  background-color: #f9f9f9;
  border-radius: 6px;
  font-size: 14px;
}

.model-cell {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.search-button-inline {
  align-self: flex-start;
  padding: 2px 8px;
  font-size: 12px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 3px;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  gap: 4px;
  margin-bottom: 4px;
}

.search-button-inline:hover {
  background-color: #45a049;
}

.model-selector {
  width: 100%;
}

.model-selector select {
  width: 100%;
  padding: 4px;
  border: 1px solid #ddd;
  border-radius: 3px;
}

.search-result-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
  margin-top: 10px;
}

.copy-button, .select-button {
  padding: 6px 12px;
  font-size: 13px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.copy-button {
  background-color: #2196F3;
  color: white;
}

.copy-button:hover {
  background-color: #0b7dda;
}

.select-button {
  background-color: #4CAF50;
  color: white;
}

.select-button:hover {
  background-color: #45a049;
}

/* 列选择器样式 */
.column-control {
  margin-bottom: 10px;
  position: relative;
}

.toggle-columns-btn {
  padding: 5px 10px;
  background-color: #f0f0f0;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
}

.column-selector {
  position: absolute;
  top: 100%;
  left: 0;
  background-color: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 10px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  z-index: 100;
  width: 250px;
  max-height: 400px;
  overflow-y: auto;
}

.column-option {
  margin: 5px 0;
  display: flex;
  align-items: center;
}

.column-option label {
  margin-left: 5px;
  cursor: pointer;
}

.column-actions {
  margin-top: 10px;
  display: flex;
  justify-content: space-between;
}

.column-actions button {
  padding: 3px 8px;
  background-color: #f8f8f8;
  border: 1px solid #ddd;
  border-radius: 3px;
  cursor: pointer;
}

.column-actions button:hover {
  background-color: #e8e8e8;
}

/* 表格信息样式 */
.table-info {
  font-size: 12px;
  color: #666;
  margin-bottom: 8px;
  display: flex;
  gap: 15px;
}

.table-info span {
  background-color: #f0f0f0;
  padding: 3px 8px;
  border-radius: 3px;
}

/* 调试信息 */
.debug-info {
  font-size: 12px;
  color: #666;
  margin-bottom: 5px;
  padding: 5px;
  background-color: #f8f8f8;
  border-radius: 3px;
  display: flex;
  gap: 10px;
}

.debug-info div {
  background-color: #e8e8e8;
  padding: 2px 6px;
  border-radius: 3px;
}

.original-table-container {
  max-height: 450px;
  overflow-y: auto;
  overflow-x: auto;
  margin-top: 10px;
  width: 100%;
}

.original-th, .original-td {
  padding: 8px;
  text-align: left;
  border: 1px solid #ddd;
  position: relative;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; /* 防止内容折行 */
}

.original-th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
  z-index: 2;
}

/* 原始表格特定样式 */
.original-data-table {
  width: 100%;
  border-collapse: collapse;
  table-layout: auto; /* 使用自动布局，让表格根据内容确定列宽 */
}

.original-table-container {
  max-height: 450px;
  overflow-y: auto;
  overflow-x: auto;
  margin-top: 10px;
  width: 100%;
  border: 1px solid #e0e0e0;
  border-radius: 4px;
}

.original-th, .original-td {
  min-width: 100px; /* 设置最小宽度 */
  padding: 8px;
  text-align: left;
  border: 1px solid #ddd;
  position: relative;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap; /* 防止内容折行 */
}

.original-th {
  background-color: #f2f2f2;
  position: sticky;
  top: 0;
  z-index: 2;
}

/* 取消原有的特殊列的初始宽度设置 */
.original-data-table th:nth-child(n), 
.original-data-table td:nth-child(n) {
  width: auto; /* 覆盖之前固定宽度的设置 */
  min-width: auto;
  max-width: none;
}

/* 优化"整机价格"列宽和显示 */
th, td {
  /* ... existing code ... */
  white-space: nowrap; /* 防止内容折行 */
  text-overflow: ellipsis;
  overflow: hidden;
}

/* 针对"整机价格"列（假设为第1列）设置更大宽度并允许拖拽 */
.search-results table th:first-child,
.search-results table td:first-child {
  min-width: 120px;
  width: 160px;
  max-width: 300px;
  white-space: nowrap;
  overflow-x: auto;
  text-overflow: initial;
}

/* 允许用户拖拽调整所有列宽 */
.search-results table th {
  position: relative;
}
.search-results table .resizer {
  position: absolute;
  top: 0;
  right: 0;
  width: 5px;
  height: 100%;
  background-color: transparent;
  cursor: col-resize;
  user-select: none;
  z-index: 3;
}
.search-results table .resizer:hover,
.search-results table .resizing {
  background-color: #4CAF50;
}

.main-content {
  flex: 1; /* 占据剩余空间 */
  max-width: 1400px;
  margin: 0 auto;
  min-height: 90vh;
  display: flex;
  flex-direction: column;
  justify-content: flex-start;
  padding: 20px 20px 20px 0; /* 右侧和上下边距，左边不需要因为有侧边栏 */
}
.button-flex-wrap {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 12px;
  margin-top: 20px;
  margin-bottom: 10px;
}
button, .el-button {
  font-size: 14px !important;
  padding: 7px 18px !important;
  min-width: 100px;
  margin: 6px 8px 6px 0;
  border-radius: 6px;
}
@media (max-width: 900px) {
  /* 小屏幕时改为垂直布局 */
  .flex.min-h-screen {
    flex-direction: column;
  }
  
  .side-nav {
    width: 100%;
    height: auto;
    margin: 10px;
    flex-direction: row;
    justify-content: space-around;
    padding: 15px;
    border-radius: 8px;
  }
  
  .brand-section {
    display: none; /* 隐藏品牌信息 */
  }
  
  .nav-btn-group {
    flex-direction: row;
    width: 100%;
    justify-content: space-around;
  }
  
  .side-nav-btn {
    width: 60px;
    height: 60px;
    margin: 0 5px;
  }
  
  .nav-label {
    display: none; /* 只显示图标 */
  }
  
  .version-info {
    display: none; /* 隐藏版本信息 */
  }
  
  .main-content {
    max-width: 99vw;
    padding: 10px;
    margin: 0;
  }
  
  .split-view {
    flex-direction: column;
    gap: 10px;
  }
  
  .original-table, .converted-table, .original-quote, .converted-quote {
    width: 100%;
    min-width: 0;
    max-width: 100vw;
    padding: 8px;
  }
  
  .button-flex-wrap {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
}
.table-container, .original-table-container {
  max-height: 350px;
  min-height: 80px;
  overflow-y: auto;
  overflow-x: auto;
  font-size: 13px;
}
table, th, td {
  font-size: 13px;
}
.bg-perplexity-bg {
  background: #fcfcf7;
}
.data-source-switcher {
  position: fixed;
  top: 20px;
  right: 20px;
  display: flex;
  gap: 12px;
  align-items: center;
  z-index: 3000;
  background: rgba(255, 255, 255, 0.95);
  padding: 8px 12px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  backdrop-filter: blur(10px);
}
.data-source-switcher .switcher-label { color: #666; font-size: 13px; }
.data-source-select :deep(.el-input__wrapper) {
  border-radius: 6px;
}
.progress-wrapper { margin-bottom: 12px; }
.progress-bar { width: 320px; height: 8px; background: #eee; border-radius: 4px; overflow: hidden; }
.progress-inner { height: 100%; background: #67C23A; transition: width .2s ease; }
.progress-text { font-size: 12px; color: #666; margin-top: 4px; }
.side-nav {
  width: 180px;
  min-width: 180px;
  flex-shrink: 0; /* 防止收缩 */
  background: linear-gradient(180deg, #ffffff 0%, #fafafa 100%);
  box-shadow: 0 8px 32px 0 rgba(0,0,0,0.08), 0 2px 8px 0 rgba(0,0,0,0.04);
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 32px 16px 24px 16px;
  border-radius: 16px;
  margin: 20px 0 20px 20px;
  height: calc(100vh - 40px);
  z-index: 10;
  border: 1px solid rgba(0,0,0,0.06);
}

.brand-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.08);
  width: 100%;
}

.brand-icon {
  font-size: 32px;
  margin-bottom: 8px;
  opacity: 0.9;
}

.brand-text {
  font-size: 16px;
  font-weight: 700;
  color: #333;
  letter-spacing: 0.5px;
  margin-bottom: 2px;
}

.brand-subtitle {
  font-size: 12px;
  color: #888;
  font-weight: 500;
  letter-spacing: 1px;
}

.nav-btn-group {
  display: flex;
  flex-direction: column;
  gap: 12px;
  width: 100%;
  align-items: center;
}

.version-info {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid rgba(0, 0, 0, 0.06);
  width: 100%;
  display: flex;
  justify-content: center;
}

.version-text {
  font-size: 11px;
  color: #aaa;
  font-weight: 500;
  letter-spacing: 0.5px;
}

.side-nav-btn {
  width: 140px;
  height: 80px;
  background: rgba(255, 255, 255, 0.7);
  border: 1px solid rgba(0, 0, 0, 0.08);
  outline: none;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #666;
  position: relative;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
}
.nav-icon {
  font-size: 24px;
  margin-bottom: 6px;
  transition: transform 0.3s ease;
}

.nav-label {
  display: block !important;
  font-size: 13px;
  color: #666;
  font-weight: 600;
  letter-spacing: 0.2px;
  background: none !important;
  box-shadow: none !important;
  border-radius: 0;
  padding: 0;
  position: static;
  white-space: nowrap;
  pointer-events: none;
  opacity: 1 !important;
  visibility: visible !important;
  text-align: center;
  line-height: 1.2;
}
.side-nav-btn:hover {
  background: rgba(255, 255, 255, 0.9);
  border-color: rgba(33, 150, 243, 0.3);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12), 0 4px 8px rgba(0, 0, 0, 0.08);
  transform: translateY(-2px);
}

.side-nav-btn:hover .nav-icon {
  transform: scale(1.1);
}

.side-nav-btn:hover .nav-label {
  color: #2196F3;
}

.side-nav-btn.active {
  background: linear-gradient(135deg, #2196F3 0%, #1976D2 100%);
  border-color: #1976D2;
  box-shadow: 0 8px 24px rgba(33, 150, 243, 0.3), 0 4px 8px rgba(33, 150, 243, 0.2);
  color: white;
  transform: translateY(-1px);
}

.side-nav-btn.active .nav-icon {
  color: white;
  transform: scale(1.05);
}

.side-nav-btn.active .nav-label {
  color: white;
  font-weight: 700;
}

.standard-rate-left-align {
  margin-left: 0 !important;
  text-align: left !important;
  display: inline-block;
  font-size: 1.25em;
  font-weight: bold;
  color: #27ae60;
  vertical-align: middle;
}

.standard-rate-rightcol {
  margin-bottom: 6px;
  text-align: left;
  font-size: 1.25em;
  font-weight: bold;
  color: #27ae60;
}

.price-item {
  margin-bottom: 4px;
  font-size: 0.9em;
}

.copy-model-btn {
  cursor: pointer;
  user-select: none;
  font-size: 15px;
  margin-left: 8px;
  transition: color 0.2s;
}
.copy-model-btn:hover {
  color: #2563eb;
  text-decoration: underline;
}

.admin-menu-popup {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 12px;
  box-shadow: 0 12px 32px rgba(0, 0, 0, 0.15), 0 4px 8px rgba(0, 0, 0, 0.1);
  min-width: 180px;
  padding: 12px 0;
  border: 1px solid rgba(0, 0, 0, 0.1);
  font-size: 14px;
  backdrop-filter: blur(20px);
}
.admin-menu-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}
.admin-menu-item {
  padding: 12px 20px;
  font-size: 14px;
  color: #333;
  cursor: pointer;
  border-radius: 8px;
  transition: all 0.3s ease;
  font-weight: 500;
}
.admin-menu-item.active {
  background: #e6f4ff;
  color: #2196F3;
  font-weight: bold;
}
.admin-menu-item.disabled {
  color: #bbb;
  cursor: not-allowed;
}
.admin-menu-item:hover:not(.active):not(.disabled) {
  background: #f5faff;
  color: #2196F3;
}

.device-model-count {
  font-size: 15px;
  color: #666;
  font-weight: 400;
  margin-left: 16px;
}

.converted-table .editable-table th,
.converted-table .editable-table td {
  font-size: 13px;
  max-width: none;
  min-width: 60px;
  padding: 6px 8px;
  text-align: left;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.converted-table .editable-table {
  table-layout: auto;
  width: 100%;
}

/* 统一原始表格和转换后表格样式 */
.converted-table .editable-table,
.original-table .original-data-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 20px;
  table-layout: auto;
}
.converted-table .editable-table th,
.converted-table .editable-table td,
.original-table .original-data-table th,
.original-table .original-data-table td {
  padding: 6px 8px;
  text-align: left;
  border: 1px solid #ddd;
  position: relative;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  min-width: 60px;
  font-size: 13px;
  max-width: none;
}
.converted-table .editable-table td input {
  width: 100%;
  padding: 6px;
  border: 1px solid transparent;
  background-color: transparent;
  border-radius: 3px;
  transition: all 0.2s;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: normal;
  word-break: break-word;
  min-height: 30px;
  font-size: 13px;
}

.match-rate-text {
  font-size: inherit;
  font-weight: bold;
  padding: 0;
  border-radius: 0;
  display: inline-block;
  background: linear-gradient(90deg, #4285F4 0%, #8e24aa 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-fill-color: transparent;
}
.match-high {
  color: #fff;
  background: #43a047;
}
.match-mid {
  color: #fff;
  background: #fbc02d;
}
.match-low {
  color: #fff;
  background: #e57373;
}
.match-none {
  color: #888;
  background: #eee;
}

/* 服务级别相关样式 */
.service-level-coefficient {
  color: #e67e22;
  font-weight: bold;
  background: #fef9e7;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
}

.service-level-info {
  color: #7f8c8d;
  font-size: 11px;
  margin-left: 4px;
  cursor: help;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

/* 后台管理欢迎页面样式 */
.admin-welcome {
  padding: 20px;
}

.admin-content {
  max-width: 800px;
  margin: 0 auto;
}

.admin-modules {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
  margin-top: 30px;
}

.admin-module-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: all 0.3s ease;
}

.admin-module-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
  transform: translateY(-2px);
}

.admin-module-card h3 {
  color: #333;
  margin: 0 0 12px 0;
  font-size: 18px;
  font-weight: 600;
}

.admin-module-card p {
  color: #666;
  margin: 0 0 20px 0;
  line-height: 1.5;
}

.module-btn {
  background: #2196F3;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: background 0.3s ease;
}

.module-btn:hover {
  background: #1976D2;
}
.action-button {
  background-color: #4CAF50; /* Green */
  border: none;
  color: white;
  padding: 15px 32px;
  text-align: center;
  text-decoration: none;
  display: inline-block;
  font-size: 16px;
  margin: 4px 2px;
  cursor: pointer;
  border-radius: 8px;
  transition: background-color 0.3s;
}
.action-button:hover {
  background-color: #45a049;
}

.mb-6 {
  margin-bottom: 1.5rem;
}
</style>
