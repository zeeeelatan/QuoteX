<template>
  <div class="admin-dashboard">
    <!-- Sidebar -->
    <aside class="sidebar" :class="{ collapsed: sidebarCollapsed }">
      <div class="sidebar-header">
        <div class="logo">
          <span class="material-symbols-outlined">smart_toy</span>
          <span v-show="!sidebarCollapsed" class="logo-text">AI Quote Admin</span>
        </div>
        <button class="collapse-btn" @click="toggleSidebar">
          <span class="material-symbols-outlined">{{ sidebarCollapsed ? 'chevron_right' : 'chevron_left' }}</span>
        </button>
      </div>

      <nav class="sidebar-nav">
        <div class="nav-section">
          <div v-show="!sidebarCollapsed" class="nav-section-title">数据管理</div>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'itinfra' }"
            @click.prevent="switchModule('itinfra')"
          >
            <span class="material-symbols-outlined">storage</span>
            <span v-show="!sidebarCollapsed" class="nav-text">IT基础架构库</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'office' }"
            @click.prevent="switchModule('office')"
          >
            <span class="material-symbols-outlined">devices</span>
            <span v-show="!sidebarCollapsed" class="nav-text">终端设备库</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'gpu' }"
            @click.prevent="switchModule('gpu')"
          >
            <span class="material-symbols-outlined">memory</span>
            <span v-show="!sidebarCollapsed" class="nav-text">GPU 价格</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'spare' }"
            @click.prevent="switchModule('spare')"
          >
            <span class="material-symbols-outlined">inventory_2</span>
            <span v-show="!sidebarCollapsed" class="nav-text">备件管理</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'manual' }"
            @click.prevent="switchModule('manual')"
          >
            <span class="material-symbols-outlined">handyman</span>
            <span v-show="!sidebarCollapsed" class="nav-text">手动匹配</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'personnel' }"
            @click.prevent="switchModule('personnel')"
          >
            <span class="material-symbols-outlined">badge</span>
            <span v-show="!sidebarCollapsed" class="nav-text">服务人员数据</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'single-service' }"
            @click.prevent="switchModule('single-service')"
          >
            <span class="material-symbols-outlined">confirmation_number</span>
            <span v-show="!sidebarCollapsed" class="nav-text">单次服务数据</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'outsourced' }"
            @click.prevent="switchModule('outsourced')"
          >
            <span class="material-symbols-outlined">work</span>
            <span v-show="!sidebarCollapsed" class="nav-text">驻场人员岗位薪资</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'dispatch-service' }"
            @click.prevent="switchModule('dispatch-service')"
          >
            <span class="material-symbols-outlined">local_shipping</span>
            <span v-show="!sidebarCollapsed" class="nav-text">派单服务数据</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'superimposed-price' }"
            @click.prevent="switchModule('superimposed-price')"
          >
            <span class="material-symbols-outlined">layers</span>
            <span v-show="!sidebarCollapsed" class="nav-text">叠加单价数据</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'city-social-insurance' }"
            @click.prevent="switchModule('city-social-insurance')"
          >
            <span class="material-symbols-outlined">location_city</span>
            <span v-show="!sidebarCollapsed" class="nav-text">城市社保基准</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'relocation-vehicle' }"
            @click.prevent="switchModule('relocation-vehicle')"
          >
            <span class="material-symbols-outlined">local_shipping</span>
            <span v-show="!sidebarCollapsed" class="nav-text">机房搬迁车型数据</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'china-city-tier' }"
            @click.prevent="switchModule('china-city-tier')"
          >
            <span class="material-symbols-outlined">map</span>
            <span v-show="!sidebarCollapsed" class="nav-text">中国城市分级表</span>
          </a>
        </div>

        <div class="nav-section">
          <div v-show="!sidebarCollapsed" class="nav-section-title">产品管理</div>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'product-mgmt' }"
            @click.prevent="switchModule('product-mgmt')"
          >
            <span class="material-symbols-outlined">category</span>
            <span v-show="!sidebarCollapsed" class="nav-text">产品分类管理</span>
          </a>
        </div>

        <div class="nav-section">
          <div v-show="!sidebarCollapsed" class="nav-section-title">价格因子</div>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'rate' }"
            @click.prevent="switchModule('rate')"
          >
            <span class="material-symbols-outlined">tune</span>
            <span v-show="!sidebarCollapsed" class="nav-text">维保费率</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'service' }"
            @click.prevent="switchModule('service')"
          >
            <span class="material-symbols-outlined">verified</span>
            <span v-show="!sidebarCollapsed" class="nav-text">服务级别</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'parameter' }"
            @click.prevent="switchModule('parameter')"
          >
            <span class="material-symbols-outlined">settings_applications</span>
            <span v-show="!sidebarCollapsed" class="nav-text">调价参数</span>
          </a>
        </div>

        <div class="nav-section">
          <div v-show="!sidebarCollapsed" class="nav-section-title">系统</div>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'settings' }"
            @click.prevent="switchModule('settings')"
          >
            <span class="material-symbols-outlined">settings</span>
            <span v-show="!sidebarCollapsed" class="nav-text">系统设置</span>
          </a>
          <a
            href="#"
            class="nav-item"
            :class="{ active: activeModule === 'terms' }"
            @click.prevent="switchModule('terms')"
          >
            <span class="material-symbols-outlined">gavel</span>
            <span v-show="!sidebarCollapsed" class="nav-text">服务条款</span>
          </a>
        </div>
      </nav>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="handleLogout">
          <span class="material-symbols-outlined">logout</span>
          <span v-show="!sidebarCollapsed" class="nav-text">退出登录</span>
        </button>
      </div>
    </aside>

    <!-- Main Content -->
    <main class="main-content">
      <!-- Header -->
      <header class="header">
        <div class="header-left">
          <h1 class="page-title">{{ moduleTitles[activeModule] }}</h1>
          <p class="page-subtitle">{{ moduleDescriptions[activeModule] }}</p>
        </div>
        <div class="header-right">
          <div class="user-info">
            <span class="material-symbols-outlined user-icon">account_circle</span>
            <span class="user-name">{{ displayUsername }}</span>
          </div>
          <a href="/" class="back-to-app">
            <span class="material-symbols-outlined">home</span>
            返回应用
          </a>
        </div>
      </header>

      <!-- Content Area -->
      <div class="content-area">
        <!-- 数据管理模块 -->
        <!-- IT基础架构库 -->
        <div v-show="activeModule === 'itinfra'" class="module-content full-height">
          <ITInfrastructureLibrary />
        </div>

        <!-- 终端设备库 -->
        <div v-show="activeModule === 'office'" class="module-content full-height">
          <OfficeDeviceLibrary />
        </div>

        <!-- GPU 价格管理 -->
        <div v-show="activeModule === 'gpu'" class="module-content">
          <GPUPriceManagement @api-call="makeApiCall" />
        </div>

        <!-- 备件管理 -->
        <div v-show="activeModule === 'spare'" class="module-content">
          <SparePartsManagement @api-call="makeApiCall" />
        </div>

        <!-- 手动匹配管理 -->
        <div v-show="activeModule === 'manual'" class="module-content">
          <ManualMatchingManagement />
        </div>

        <!-- 服务人员数据管理 -->
        <div v-show="activeModule === 'personnel'" class="module-content full-height">
          <ServicePersonnelManagement />
        </div>

        <!-- 单次服务数据管理 -->
        <div v-show="activeModule === 'single-service'" class="module-content full-height">
          <SingleServiceManagement />
        </div>

        <!-- 驻场人员岗位及薪资管理 -->
        <div v-show="activeModule === 'outsourced'" class="module-content full-height">
          <OutsourcedPersonnelManagement />
        </div>

        <!-- 派单服务数据管理 -->
        <div v-show="activeModule === 'dispatch-service'" class="module-content full-height">
          <DispatchServiceManagement />
        </div>

        <!-- 叠加单价数据管理 -->
        <div v-show="activeModule === 'superimposed-price'" class="module-content full-height">
          <SuperimposedPriceManagement />
        </div>

        <!-- 城市社保基准管理 -->
        <div v-show="activeModule === 'city-social-insurance'" class="module-content full-height">
          <CitySocialInsurance />
        </div>

        <!-- 机房搬迁车型数据 -->
        <div v-show="activeModule === 'relocation-vehicle'" class="module-content full-height">
          <RelocationVehicleManagement />
        </div>

        <!-- 中国城市分级表 -->
        <div v-show="activeModule === 'china-city-tier'" class="module-content full-height">
          <ChinaCityTierManagement />
        </div>

        <!-- 产品管理模块 -->
        <div v-show="activeModule === 'product-mgmt'" class="module-content full-height">
          <ProductManagement />
        </div>

        <!-- 价格因子模块 -->
        <!-- 维保费率管理 -->
        <div v-show="activeModule === 'rate'" class="module-content">
          <RateManagement @api-call="makeApiCall" />
        </div>

        <!-- 服务级别管理 -->
        <div v-show="activeModule === 'service'" class="module-content">
          <ServiceLevelManagement @api-call="makeApiCall" />
        </div>

        <!-- 调价参数管理 -->
        <div v-show="activeModule === 'parameter'" class="module-content">
          <ProductParameterManagement />
        </div>

        <!-- 系统模块 -->
        <!-- 系统设置 -->
        <div v-show="activeModule === 'settings'" class="module-content">
          <SystemSettings />
        </div>

        <!-- 服务条款管理 -->
        <div v-show="activeModule === 'terms'" class="module-content">
          <ServiceTermsManagement />
        </div>
      </div>
    </main>

    <!-- Toast Notification -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      <span class="material-symbols-outlined">{{ toast.icon }}</span>
      <span>{{ toast.message }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import RateManagement from '../components/admin/RateManagement.vue'
import ServiceLevelManagement from '../components/admin/ServiceLevelManagement.vue'
import ProductParameterManagement from '../components/admin/ProductParameterManagement.vue'
import GPUPriceManagement from '../components/admin/GPUPriceManagement.vue'
import SparePartsManagement from '../components/admin/SparePartsManagement.vue'
import ManualMatchingManagement from '../components/admin/ManualMatchingManagement.vue'
import SystemSettings from '../components/admin/SystemSettings.vue'
import ServiceTermsManagement from '../components/admin/ServiceTermsManagement.vue'
import ITInfrastructureLibrary from '../components/admin/ITInfrastructureLibrary.vue'
import OfficeDeviceLibrary from '../components/admin/OfficeDeviceLibrary.vue'
import ProductManagement from '../components/admin/ProductManagement.vue'
import ServicePersonnelManagement from '../components/admin/ServicePersonnelManagement.vue'
import SingleServiceManagement from '../components/admin/SingleServiceManagement.vue'
import OutsourcedPersonnelManagement from '../components/admin/OutsourcedPersonnelManagement.vue'
import DispatchServiceManagement from '../components/admin/DispatchServiceManagement.vue'
import SuperimposedPriceManagement from '../components/admin/SuperimposedPriceManagement.vue'
import CitySocialInsurance from '../components/admin/CitySocialInsurance.vue'
import RelocationVehicleManagement from '../components/admin/RelocationVehicleManagement.vue'
import ChinaCityTierManagement from '../components/admin/ChinaCityTierManagement.vue'

const router = useRouter()

// API Base URL
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
const sidebarCollapsed = ref(false)
const activeModule = ref('rate')
const displayUsername = ref('')

const moduleTitles: Record<string, string> = {
  itinfra: 'IT基础架构库',
  office: '终端设备库',
  'product-mgmt': '产品分类管理',
  rate: '维保费率管理',
  service: '服务级别管理',
  parameter: '调价参数管理',
  gpu: 'GPU 价格管理',
  spare: '备件管理',
  manual: '手动匹配管理',
  personnel: '服务人员数据管理',
  'single-service': '单次服务数据管理',
  outsourced: '驻场人员岗位及薪资管理',
  'dispatch-service': '派单服务数据管理',
  'superimposed-price': '叠加单价数据管理',
  'city-social-insurance': '城市社保基准管理',
  'relocation-vehicle': '机房搬迁车型数据',
  'china-city-tier': '中国城市分级表',
  settings: '系统设置',
  terms: '服务条款管理'
}

const moduleDescriptions: Record<string, string> = {
  itinfra: '管理数据中心设备库，支持增删改查和批量导入导出',
  office: '管理办公设备库，支持增删改查和批量导入导出',
  'product-mgmt': '配置各类服务产品的定价参数、AI报价逻辑及报价单模板',
  rate: '管理设备维护费率配置',
  service: '配置服务级别和响应时间',
  parameter: '配置报价引擎的核心费率、时效因子及成本基数',
  gpu: '管理 GPU 设备价格信息',
  spare: '管理备件库存和价格',
  manual: '管理手动匹配覆盖记录',
  personnel: '管理可用于项目报价的技术服务人员及其费率标准',
  'single-service': '管理单次服务报价数据，包含操作实施、安装调试、备件更换等服务项及定价标准',
  outsourced: '管理驻场人员岗位级别、能力要求及薪资标准',
  'dispatch-service': '管理派单服务定价数据，包含不同工时、时间窗口、响应时效和城市等级的价格标准',
  'superimposed-price': '管理叠加单价数据，包含单价说明、收费标准及适用产品配置',
  'city-social-insurance': '管理各城市社保缴纳基数和比例，支持批量导入Excel',
  'relocation-vehicle': '管理机房搬迁车型数据，支持从 Excel（机房搬迁车型数据大全.xlsx）导入',
  'china-city-tier': '管理中国城市分级数据（城市等级、行政级别、物流枢纽等级等），支持 Excel 导入',
  settings: '系统配置和偏好设置',
  terms: '管理所有报价单中使用的法律条款和条件模板'
}

// Toast notification
const toast = ref({
  show: false,
  message: '',
  type: 'success',
  icon: 'check_circle'
})

// Check login status on mount
onMounted(() => {
  const isLoggedIn = localStorage.getItem('admin_logged_in')
  if (!isLoggedIn) {
    router.push('/admin')
  }
  const username = localStorage.getItem('admin_username_display')
  displayUsername.value = username || 'Admin'
})

// Toggle sidebar
function toggleSidebar() {
  sidebarCollapsed.value = !sidebarCollapsed.value
}

// Switch module
function switchModule(module: string) {
  activeModule.value = module
}

// Handle logout
function handleLogout() {
  localStorage.removeItem('admin_logged_in')
  localStorage.removeItem('admin_username_display')
  router.push('/admin')
}

// Show toast notification
function showToast(message: string, type: 'success' | 'error' = 'success') {
  toast.value = {
    show: true,
    message,
    type,
    icon: type === 'success' ? 'check_circle' : 'error'
  }
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

// API call handler for child components
async function makeApiCall(config: any) {
  try {
    const response = await axios({
      ...config,
      baseURL: API_URL
    })
    showToast('操作成功', 'success')
    return response.data
  } catch (error: any) {
    const message = error.response?.data?.detail || error.message || '操作失败'
    showToast(message, 'error')
    throw error
  }
}

// Expose API URL and function for child components
defineExpose({
  API_URL,
  showToast
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Noto+Sans+SC:wght@300;400;500;700;900&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.admin-dashboard {
  font-family: "Inter", "Noto Sans SC", sans-serif;
  background-color: #0f172a;
  color: #e2e8f0;
  display: flex;
  height: 100vh;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: 260px;
  background-color: #1e293b;
  border-right: 1px solid #334155;
  display: flex;
  flex-direction: column;
  transition: width 0.3s;
}

.sidebar.collapsed {
  width: 70px;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid #334155;
}

.logo {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.logo .material-symbols-outlined {
  font-size: 1.5rem;
  color: #135bec;
}

.logo-text {
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
}

.collapse-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.collapse-btn:hover {
  background-color: #334155;
  color: #94a3b8;
}

.sidebar-nav {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.nav-section {
  margin-bottom: 1.5rem;
}

.nav-section-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0 1rem;
  margin-bottom: 0.5rem;
}

.nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #94a3b8;
  text-decoration: none;
  transition: all 0.2s;
  margin: 0.125rem 0.5rem;
  border-radius: 0.375rem;
}

.nav-item:hover {
  background-color: #334155;
  color: #f1f5f9;
}

.nav-item.active {
  background-color: rgba(19, 91, 236, 0.15);
  color: #135bec;
}

.nav-item .material-symbols-outlined {
  font-size: 1.25rem;
}

.nav-text {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #334155;
}

.logout-btn {
  width: 100%;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: transparent;
  border: none;
  border-radius: 0.375rem;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.2s;
}

.logout-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Main Content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 2rem;
  background-color: #1e293b;
  border-bottom: 1px solid #334155;
}

.header-left {
  display: flex;
  flex-direction: column;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.125rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.user-icon {
  font-size: 1.75rem;
  color: #64748b;
}

.user-name {
  font-size: 0.875rem;
  color: #cbd5e1;
}

.back-to-app {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  background-color: #334155;
  color: #94a3b8;
  text-decoration: none;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.back-to-app:hover {
  background-color: #475569;
  color: #f1f5f9;
}

.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
}

.module-content {
  height: 100%;
}

.module-content.full-height {
  overflow: hidden;
}

/* Toast Notification */
.toast {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  background-color: #1e293b;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.3);
  z-index: 100;
  animation: slideIn 0.3s ease-out;
}

.toast.success {
  border-left: 4px solid #22c55e;
}

.toast.error {
  border-left: 4px solid #ef4444;
}

.toast .material-symbols-outlined {
  font-size: 1.25rem;
}

.toast.success .material-symbols-outlined {
  color: #22c55e;
}

.toast.error .material-symbols-outlined {
  color: #ef4444;
}

@keyframes slideIn {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e293b;
}

::-webkit-scrollbar-thumb {
  background: #475569;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #64748b;
}
</style>
