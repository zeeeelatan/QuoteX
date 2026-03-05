<template>
  <div class="homepage-container">
    <aside class="sidebar">
      <button type="button" class="sidebar-header" @click="goToHome" title="返回首页">
        <div class="logo-icon">
          <span class="material-symbols-outlined">smart_toy</span>
        </div>
        <h1 class="logo-text">AI 智能报价系统</h1>
      </button>

      <div class="sidebar-content">
        <div class="menu-section">
          <h3 class="menu-title">快捷操作</h3>
          <button class="menu-item active-item" @click="navigateToDocumentRecognition">
            <span class="material-symbols-outlined">add</span>
            <span class="item-text">发起询价</span>
          </button>
          <button class="menu-item">
            <span class="material-symbols-outlined">upload</span>
            <span class="item-text">导入 BOM 清单</span>
          </button>
          <button class="menu-item" @click="currentView = 'draft-box'" :class="{ 'nav-active': currentView === 'draft-box' }">
            <span class="material-symbols-outlined">description</span>
            <span class="item-text">草稿箱</span>
          </button>
        </div>

        <div class="menu-section">
          <h3 class="menu-title">功能菜单</h3>
          <a href="#" class="menu-item" @click.prevent="goToHome" :class="{ 'nav-active': currentView === 'home' }">
            <span class="material-symbols-outlined">home</span>
            <span class="item-text">首页概览</span>
          </a>
          <a href="#" class="menu-item" @click.prevent="currentView = 'product-database'" :class="{ 'nav-active': currentView === 'product-database' }">
            <span class="material-symbols-outlined">inventory_2</span>
            <span class="item-text">产品数据库</span>
          </a>
          <a href="#" class="menu-item" @click.prevent="currentView = 'quote-history'" :class="{ 'nav-active': currentView === 'quote-history' }">
            <span class="material-symbols-outlined">history</span>
            <span class="item-text">历史记录</span>
          </a>
        </div>

        <div class="menu-section">
          <h3 class="menu-title">报价工具</h3>
          <a href="#" class="menu-item" @click.prevent="currentView = 'onsite-calculator'" :class="{ 'nav-active': currentView === 'onsite-calculator' }">
            <span class="material-symbols-outlined">calculate</span>
            <span class="item-text">驻场服务测算模型</span>
          </a>
          <a href="#" class="menu-item" @click.prevent="currentView = 'relocation-calculator'" :class="{ 'nav-active': currentView === 'relocation-calculator' }">
            <span class="material-symbols-outlined">local_shipping</span>
            <span class="item-text">搬迁服务测算模型</span>
          </a>
        </div>
      </div>

      <div class="sidebar-footer">
        <button class="logout-btn" @click="handleLogout">
          <span class="material-symbols-outlined">logout</span>
          <span class="logout-text">退出登录</span>
        </button>
      </div>
    </aside>

    <main class="main-content">
      <header class="top-header">
        <div class="mobile-header">
          <span class="material-symbols-outlined">menu</span>
          <span class="mobile-title">AI 智能报价</span>
        </div>

        <div class="search-container">
          <div class="search-wrapper">
            <div class="search-icon">
              <span class="material-symbols-outlined">search</span>
            </div>
            <input
              class="search-input"
              placeholder="搜索设备型号、SKU 或历史报价..."
              type="text"
            />
          </div>
        </div>

        <div class="header-actions">
          <button class="icon-button notification-btn">
            <span class="material-symbols-outlined">notifications</span>
            <span class="notification-badge"></span>
          </button>
          <button class="icon-button help-btn">
            <span class="material-symbols-outlined">help</span>
          </button>
          <div class="header-divider"></div>
          <template v-if="isLoggedInRef">
            <div class="header-user-info" ref="userInfoRef" @click="toggleUserMenu">
              <div class="header-user-avatar" :style="userProfile.avatar ? { backgroundImage: `url(${userProfile.avatar})`, backgroundSize: 'cover' } : {}"></div>
              <div class="header-user-details">
                <span class="header-user-name">{{ userProfile.name }}</span>
                <span class="header-user-role">{{ userProfile.position }}</span>
              </div>
              <span class="material-symbols-outlined dropdown-arrow" :class="{ 'expanded': isUserMenuOpen }">expand_more</span>
            </div>
            <Teleport to="body">
              <div v-if="isUserMenuOpen" class="user-dropdown-menu" :style="userDropdownStyle">
                <div class="dropdown-header">
                  <div class="dropdown-avatar" :style="userProfile.avatar ? { backgroundImage: `url(${userProfile.avatar})`, backgroundSize: 'cover' } : {}"></div>
                  <div class="dropdown-info">
                    <span class="dropdown-name">{{ userProfile.name }}</span>
                    <span class="dropdown-role">{{ userProfile.position }}</span>
                  </div>
                </div>
                <div class="dropdown-divider"></div>
                <a href="#" class="dropdown-item" @click.prevent="navigateToSystemSettings">
                  <span class="material-symbols-outlined">settings</span>
                  <span>系统设置</span>
                </a>
                <a href="#" class="dropdown-item" @click.prevent="navigateToPersonalSettings">
                  <span class="material-symbols-outlined">person</span>
                  <span>个人设置</span>
                </a>
                <div class="dropdown-divider"></div>
                <a href="#" class="dropdown-item logout-item" @click.prevent="handleLogout">
                  <span class="material-symbols-outlined">logout</span>
                  <span>退出登录</span>
                </a>
              </div>
            </Teleport>
          </template>
          <template v-else>
            <div class="header-auth-buttons">
              <button type="button" class="header-auth-btn register" @click="openRegisterModal">注册</button>
              <button type="button" class="header-auth-btn login" @click="openLoginModal">登录</button>
            </div>
          </template>
        </div>
      </header>

      <div class="content-area" :class="{ 'embedded-view': currentView === 'product-database' || currentView === 'quote-history' || currentView === 'onsite-calculator' || currentView === 'relocation-calculator', 'draft-view': currentView === 'draft-box', 'chat-active': currentView === 'home' && chatMode }">
        <!-- Product Database View -->
        <ProductDatabase v-if="currentView === 'product-database'" @go-home="currentView = 'home'" />

        <!-- Quote History View -->
        <QuoteHistory v-if="currentView === 'quote-history'" @go-home="currentView = 'home'" />

        <!-- Draft Box View -->
        <div v-if="currentView === 'draft-box'" class="draft-view-container">
          <DraftBox ref="draftBoxRef" />
        </div>

        <!-- Onsite Service Calculator View -->
        <OnsiteServiceCalculator v-if="currentView === 'onsite-calculator'" />

        <!-- Relocation Service Calculator View -->
        <RelocationServiceCalculator v-if="currentView === 'relocation-calculator'" />

        <!-- Home Content -->
        <div v-if="currentView === 'home'" class="home-content">
        <!-- 交互模式：AI 对话界面 -->
        <template v-if="chatMode">
          <section class="chat-mode-section">
            <!-- 顶部返回按钮 -->
            <div class="chat-top-bar">
              <button type="button" class="chat-back-btn" @click="exitChatMode">
                <span class="material-symbols-outlined">arrow_back</span>
                <span>返回主页</span>
              </button>
            </div>
            <!-- 可滚动的消息区域 -->
            <div class="chat-scroll-area" ref="chatMessagesRef">
              <div class="chat-center-col">
                <!-- 欢迎区域（无消息时显示） -->
                <div v-if="chatMessages.length === 0" class="chat-welcome">
                  <div class="chat-welcome-icon">
                    <span class="material-symbols-outlined">smart_toy</span>
                  </div>
                  <h3 class="chat-welcome-title">您好，我是您的智能报价助手</h3>
                  <p class="chat-welcome-desc">您可以上传设备清单、输入报价需求，或者直接询问我关于成本核算的细节。我将为您提供精准的报价建议。</p>
                </div>

                <!-- 消息列表 -->
                <template v-for="(msg, idx) in chatMessages" :key="idx">
                  <!-- AI 消息 -->
                  <div v-if="msg.role === 'assistant'" class="cmsg cmsg-ai">
                    <div class="cmsg-avatar">
                      <span class="material-symbols-outlined">auto_awesome</span>
                      <div class="cmsg-avatar-dot"></div>
                    </div>
                    <div class="cmsg-body">
                      <div class="cmsg-bubble cmsg-bubble-ai" :class="{ 'cmsg-bubble-wide': msg.structured }">
                        <p class="cmsg-source-hint">{{ msg.structured ? '基于系统设备库实时匹配计算' : '已结合维保费率、服务级别、设备库等后台数据生成' }}</p>
                        <div class="cmsg-ai-content" v-html="formatAnalysis(msg.content, msg.isHtml)"></div>
                      </div>
                      <div class="cmsg-actions">
                        <button v-if="msg.structured" type="button" class="cmsg-action-btn cmsg-action-primary" @click="exportQuotation(msg.structured)">
                          <span class="material-symbols-outlined">download</span>
                          导出报价单
                        </button>
                        <button type="button" class="cmsg-action-btn" @click="goToDocumentRecognition">
                          <span class="material-symbols-outlined">receipt_long</span>
                          去发起询价
                        </button>
                        <button type="button" class="cmsg-action-btn">
                          <span class="material-symbols-outlined">refresh</span>
                          重新分析
                        </button>
                      </div>
                    </div>
                  </div>

                  <!-- 用户消息 -->
                  <div v-else class="cmsg cmsg-user">
                    <div class="cmsg-body">
                      <div class="cmsg-bubble cmsg-bubble-user">{{ msg.content }}</div>
                      <div v-if="msg.fileNames?.length" class="cmsg-user-files">
                        <div v-for="(fn, i) in msg.fileNames" :key="i" class="cmsg-file-card">
                          <div class="cmsg-file-icon">
                            <span class="material-symbols-outlined">description</span>
                          </div>
                          <div class="cmsg-file-meta">
                            <p class="cmsg-file-name">{{ fn }}</p>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </template>
              </div>
            </div>

            <!-- 底部浮动输入区 -->
            <div class="chat-float-bar">
              <div class="chat-float-inner">
                <!-- 快捷建议 -->
                <div class="chat-suggest-row">
                  <button type="button" class="chat-suggest-pill" @click="setExample('生成报价摘要')">生成报价摘要</button>
                  <button type="button" class="chat-suggest-pill" @click="setExample('比较历史价格')">比较历史价格</button>
                  <button type="button" class="chat-suggest-pill" @click="setExample('导出为报价单')">导出为报价单</button>
                  <button type="button" class="chat-suggest-pill" @click="setExample('调整参数配置')">调整参数配置</button>
                </div>
                <!-- 输入卡片 -->
                <div class="chat-input-card" :class="{ focused: chatInputFocused }">
                  <div class="chat-input-row">
                    <button type="button" class="chat-attach-btn" @click="triggerChatFileInput" title="附件导入">
                      <span class="material-symbols-outlined">attach_file</span>
                    </button>
                    <input ref="chatFileInputRef" type="file" class="file-input-hidden" accept=".pdf,.doc,.docx,.xls,.xlsx,.txt" multiple @change="onFileSelect" />
                    <input
                      v-model="requirementText"
                      class="chat-text-input"
                      placeholder="输入指令或询问报价细节..."
                      @keydown.enter.prevent="handleGenerate"
                      @focus="chatInputFocused = true"
                      @blur="chatInputFocused = false"
                    />
                    <button
                      type="button"
                      class="chat-send-btn"
                      :disabled="isGenerating || (!requirementText.trim() && attachedFiles.length === 0)"
                      @click="handleGenerate"
                    >
                      <span v-if="isGenerating" class="btn-loading"></span>
                      <span v-else class="material-symbols-outlined">send</span>
                    </button>
                  </div>
                  <div class="chat-attached-row" v-if="attachedFiles.length > 0">
                    <span class="chat-attached-label">已附加:</span>
                    <span v-for="(f, i) in attachedFiles" :key="i" class="chat-attached-tag">
                      {{ f.name }}
                      <button type="button" class="chat-attached-remove" @click="removeAttachedFile(i)">×</button>
                    </span>
                  </div>
                </div>
                <p class="chat-disclaimer">AI 可能会产生误差，请务必核对关键数据。</p>
              </div>
            </div>
          </section>
        </template>

        <!-- 首页：Hero + 问询框 -->
        <template v-else>
        <section class="hero-section">
          <div class="hero-content">
            <div class="hero-text">
              <div class="version-badge">
                <span class="badge-dot"></span>
                AI 驱动 V2.0
              </div>
              <h1 class="hero-title">智能报价助手</h1>
              <p class="hero-description">
                利用先进的生成式 AI,即时创建<b>数据中心</b>、<b>办公设备</b>及<b>安防监控</b>的专业报价方案。只需简单描述您的项目需求。
              </p>
            </div>

            <div class="search-box-container">
              <div class="search-box-wrapper">
                <div class="search-box" :class="{ 'has-files': attachedFiles.length > 0 }">
                  <div class="search-box-icon">
                    <span class="material-symbols-outlined">auto_awesome</span>
                  </div>
                  <div class="search-box-body">
                    <input
                      v-model="requirementText"
                      class="search-box-input"
                      placeholder="询问任何事。输入 @ 以提及和 / 以使用快捷方式。"
                      @keydown.enter.prevent="handleGenerate"
                    />
                    <div class="attach-files-row" v-if="attachedFiles.length > 0">
                      <span class="attach-label">已附加文档:</span>
                      <span v-for="(f, i) in attachedFiles" :key="i" class="file-tag">
                        {{ f.name }}
                        <button type="button" class="file-tag-remove" @click="removeAttachedFile(i)" title="移除">×</button>
                      </span>
                    </div>
                  </div>
                  <div class="search-box-actions-bar">
                    <input
                      ref="fileInputRef"
                      type="file"
                      class="file-input-hidden"
                      accept=".pdf,.doc,.docx,.xls,.xlsx,.txt"
                      multiple
                      @change="onFileSelect"
                    />
                    <button type="button" class="toolbar-icon" title="附件导入" @click="triggerFileInput">
                      <span class="material-symbols-outlined">attach_file</span>
                    </button>
                    <button
                      type="button"
                      class="generate-button generate-button-inline"
                      :disabled="isGenerating || (!requirementText.trim() && attachedFiles.length === 0)"
                      @click="handleGenerate"
                    >
                      <span v-if="isGenerating" class="btn-loading"></span>
                      <span v-else>立即生成</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <div class="quick-examples">
              <span class="examples-label">试一试:</span>
              <button type="button" class="example-link" @click="setExample('50台戴尔 PowerEdge 服务器')">"50台戴尔 PowerEdge 服务器"</button>
              <span class="example-separator">•</span>
              <button type="button" class="example-link" @click="setExample('100人规模办公室全套 IT 设备')">"100人规模办公室全套 IT 设备"</button>
              <span class="example-separator">•</span>
              <button type="button" class="example-link" @click="setExample('智能园区安防监控方案')">"智能园区安防监控方案"</button>
            </div>
          </div>
        </section>
        </template>

        <section v-if="!chatMode" class="stats-section">
          <div class="stat-card">
            <div class="stat-header">
              <p class="stat-label">今日生成报价单</p>
              <span class="material-symbols-outlined stat-icon">receipt_long</span>
            </div>
            <div class="stat-content">
              <h4 class="stat-value">128</h4>
              <span class="stat-trend positive">
                <span class="material-symbols-outlined">trending_up</span>
                +12%
              </span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <p class="stat-label">待审批项目</p>
              <span class="material-symbols-outlined stat-icon orange">pending_actions</span>
            </div>
            <div class="stat-content">
              <h4 class="stat-value">15</h4>
              <span class="stat-subtitle">需要特别关注</span>
            </div>
          </div>

          <div class="stat-card">
            <div class="stat-header">
              <p class="stat-label">系统状态</p>
              <span class="material-symbols-outlined stat-icon green">check_circle</span>
            </div>
            <div class="stat-content">
              <h4 class="stat-value">运行正常</h4>
              <span class="stat-subtitle green">所有服务在线</span>
            </div>
          </div>
        </section>

        <section v-if="!chatMode" class="categories-section">
          <div class="section-header">
            <h2 class="section-title">
              <span class="title-marker"></span>
              浏览分类
            </h2>
            <a href="#" class="view-all-link">
              查看全部
              <span class="material-symbols-outlined">arrow_forward</span>
            </a>
          </div>

          <div class="categories-grid">
            <div class="category-card">
              <div class="category-image datacenter"></div>
              <div class="category-content">
                <div class="category-icon-wrapper">
                  <span class="material-symbols-outlined">dns</span>
                </div>
                <h3 class="category-title">数据中心解决方案</h3>
                <p class="category-description">核心服务器、海量存储阵列、精密空调及智能电源管理系统。</p>
                <div class="category-tags">
                  <span class="tag">机架式服务器</span>
                  <span class="tag">交换机</span>
                </div>
              </div>
            </div>

            <div class="category-card">
              <div class="category-image office"></div>
              <div class="category-content">
                <div class="category-icon-wrapper">
                  <span class="material-symbols-outlined">computer</span>
                </div>
                <h3 class="category-title">智慧办公 IT 设备</h3>
                <p class="category-description">企业级笔记本、高性能工作站、4K 显示器及会议室外设。</p>
                <div class="category-tags">
                  <span class="tag">笔记本电脑</span>
                  <span class="tag">显示器</span>
                </div>
              </div>
            </div>

            <div class="category-card">
              <div class="category-image security"></div>
              <div class="category-content">
                <div class="category-icon-wrapper">
                  <span class="material-symbols-outlined">videocam</span>
                </div>
                <h3 class="category-title">智能安防监控</h3>
                <p class="category-description">高清 IP 摄像机、NVR 网络存储、门禁控制系统及安防传感器。</p>
                <div class="category-tags">
                  <span class="tag">IPC 摄像机</span>
                  <span class="tag">NVR 录像机</span>
                </div>
              </div>
            </div>
          </div>
        </section>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import * as XLSX from 'xlsx'
import { saveAs } from 'file-saver'
import { ElMessage } from 'element-plus'
import { isLoggedInRef, openLoginModal, openRegisterModal, clearAuth } from '../stores/authStore'
import { openSystemSettings, openPersonalSettings, currentSettingsDialog } from '../stores/settingsDialogStore'
import ProductDatabase from './ProductDatabase.vue'
import QuoteHistory from './QuoteHistory.vue'
import DraftBox from '../components/DraftBox.vue'
import OnsiteServiceCalculator from '../components/pricing/OnsiteServiceCalculator.vue'
import RelocationServiceCalculator from '../components/pricing/RelocationServiceCalculator.vue'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'
const API_BASE = API_URL.replace(/\/$/, '')

// 首页智能报价输入
const requirementText = ref('')
const attachedFiles = ref<File[]>([])
const fileInputRef = ref<HTMLInputElement | null>(null)
const chatFileInputRef = ref<HTMLInputElement | null>(null)
const isGenerating = ref(false)
const chatInputFocused = ref(false)
const showResultModal = ref(false)
const aiResultAnalysis = ref('')

// 交互模式与对话记录
const chatMode = ref(false)
interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  fileNames?: string[]
  structured?: any  // 结构化报价数据
  isHtml?: boolean  // 是否为 HTML 富文本
}
const chatMessages = ref<ChatMessage[]>([])
const chatMessagesRef = ref<HTMLElement | null>(null)

// 模型选择（仅用于接口，无 UI）
const availableModels = ref<string[]>(['qwen-plus'])
const selectedModel = ref('qwen-plus')

function triggerFileInput() {
  fileInputRef.value?.click()
}

function triggerChatFileInput() {
  chatFileInputRef.value?.click()
}

async function loadModels() {
  try {
    const res = await axios.get(`${API_BASE}/ai-quote/models`, { timeout: 5000 })
    if (Array.isArray(res.data?.models) && res.data.models.length > 0) {
      availableModels.value = res.data.models
      if (!res.data.models.includes(selectedModel.value)) {
        selectedModel.value = res.data.models[0]
      }
    }
  } catch (_) {
    // 使用默认列表
  }
}

function exitChatMode() {
  chatMode.value = false
  chatMessages.value = []
}

/** 返回首页：任意情况下回到首页（含退出交互对话模式） */
function goToHome() {
  currentView.value = 'home'
  chatMode.value = false
  chatMessages.value = []
}

function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (files?.length) {
    const list = Array.from(files)
    if (attachedFiles.value.length + list.length > 5) {
      ElMessage.warning('最多附加 5 个文档')
      list.splice(5 - attachedFiles.value.length)
    }
    attachedFiles.value.push(...list)
  }
  input.value = ''
}

function removeAttachedFile(index: number) {
  attachedFiles.value.splice(index, 1)
}

function setExample(text: string) {
  requirementText.value = text
}

function formatAnalysis(text: string, isHtml?: boolean): string {
  if (!text) return ''
  // 如果已经是 HTML 格式（包含标签），直接返回
  if (isHtml || text.includes('<table') || text.includes('<div')) {
    return text
  }
  // 纯文本格式化
  return text
    .replace(/\n/g, '<br>')
    .replace(/^(\d+[\.、])/gm, '<strong>$1</strong>')
}

function goToDocumentRecognition() {
  showResultModal.value = false
  router.push('/document-recognition')
}

function exportQuotation(structured: any) {
  if (!structured?.devices?.length) {
    ElMessage.warning('无可导出的报价数据')
    return
  }
  const rows = structured.devices.map((d: any, idx: number) => ({
    '序号': idx + 1,
    '厂商': d.manufacturer || '',
    '匹配型号': d.matched_model || '',
    '匹配率': `${(d.match_rate || 0).toFixed(0)}%`,
    '设备价格(元)': d.device_price || 0,
    '维保费率': `${((d.rate || 0) * 100).toFixed(2)}%`,
    '维保单价(元)': d.price || 0,
    '数量': d.quantity || 1,
    '小计(元)': d.subtotal || 0,
    '一级分类': d.primary_category || '',
    '二级分类': d.secondary_category || '',
    '三级分类': d.tertiary_category || '',
  }))

  // 添加汇总行
  rows.push({
    '序号': '',
    '厂商': '',
    '匹配型号': '',
    '匹配率': '',
    '设备价格(元)': '',
    '维保费率': '',
    '维保单价(元)': '',
    '数量': '合计',
    '小计(元)': structured.total_base || 0,
    '一级分类': '',
    '二级分类': '',
    '三级分类': '',
  })

  if (structured.matched_service_level) {
    rows.push({
      '序号': '',
      '厂商': '',
      '匹配型号': '',
      '匹配率': '',
      '设备价格(元)': '',
      '维保费率': '',
      '维保单价(元)': '',
      '数量': `服务级别 ${structured.matched_service_level.level_code} (×${structured.matched_service_level.coefficient})`,
      '小计(元)': structured.total_adjusted || 0,
      '一级分类': '',
      '二级分类': '',
      '三级分类': '',
    })
  }

  const ws = XLSX.utils.json_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '维保报价')
  const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' })
  const now = new Date().toISOString().slice(0, 10)
  saveAs(new Blob([wbout]), `维保报价_${now}.xlsx`)
  ElMessage.success('报价单已导出')
}

async function handleGenerate() {
  if (!requirementText.value.trim() && attachedFiles.value.length === 0) {
    ElMessage.warning('请描述需求或上传需求文档')
    return
  }
  const userContent = requirementText.value.trim()
  const fileNames = attachedFiles.value.map((f) => f.name)
  isGenerating.value = true
  aiResultAnalysis.value = ''
  try {
    const form = new FormData()
    form.append('requirement', userContent)
    form.append('model', selectedModel.value)
    // 传递历史对话，支持多轮上下文（发送精简版，不含 HTML）
    if (chatMessages.value.length > 0) {
      const history = chatMessages.value.map(m => {
        if (m.role === 'assistant' && m.structured) {
          // 结构化结果只发送摘要，避免发送大量 HTML
          const s = m.structured
          const devSummary = (s.devices || []).map((d: any) =>
            `${d.manufacturer} ${d.matched_model} ×${d.quantity} 维保单价¥${d.price}`
          ).join('; ')
          return { role: m.role, content: `[报价结果] ${devSummary} | 总价¥${s.total_base}` }
        }
        // 普通文本消息，截断过长内容
        return { role: m.role, content: (m.content || '').slice(0, 500) }
      })
      form.append('history', JSON.stringify(history))
    }
    for (const f of attachedFiles.value) {
      form.append('files', f)
    }
    const res = await axios.post(`${API_BASE}/ai-quote/analyze`, form, {
      timeout: 120000
    })
    const analysis = res.data?.analysis || res.data?.suggestion || '未返回分析内容'
    const structured = res.data?.structured || null
    const isHtml = typeof analysis === 'string' && (analysis.includes('<table') || analysis.includes('<div'))
    aiResultAnalysis.value = analysis
    chatMessages.value.push(
      { role: 'user', content: userContent, fileNames: fileNames.length ? fileNames : undefined },
      { role: 'assistant', content: analysis, structured, isHtml }
    )
    chatMode.value = true
    requirementText.value = ''
    attachedFiles.value = []
    await nextTick()
    chatMessagesRef.value?.scrollTo({ top: chatMessagesRef.value.scrollHeight, behavior: 'smooth' })
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    const msg = typeof detail === 'string' ? detail : Array.isArray(detail) ? detail[0] : err?.message ?? '分析失败，请重试'
    ElMessage.error(msg)
    if (err?.response?.status === 503) {
      ElMessage.info('AI 服务暂时不可用，请稍后重试或联系管理员检查配置')
    }
  } finally {
    isGenerating.value = false
  }
}

const router = useRouter()
const route = useRoute()
const currentView = ref<'home' | 'product-database' | 'quote-history' | 'draft-box' | 'onsite-calculator' | 'relocation-calculator'>('home')

// 从路由 query 打开设置弹窗
function applyRouteView() {
  const view = route.query.view as string | undefined
  if (view === 'personal-settings') {
    openPersonalSettings()
  } else if (view === 'system-settings') {
    openSystemSettings()
  }
}

// 用户资料
const userProfile = ref({
  name: '李明',
  position: '高级销售经理',
  avatar: ''
})

// 加载用户资料
async function loadUserProfile() {
  try {
    const res = await axios.get(`${API_URL}/user-profile/`)
    if (res.data) {
      userProfile.value.name = res.data.name || '李明'
      userProfile.value.position = res.data.position || '高级销售经理'
      userProfile.value.avatar = res.data.avatar || ''
    }
  } catch (err) {
    console.error('加载用户资料失败', err)
  }
}

// 监听设置弹窗关闭，刷新用户资料
watch(currentSettingsDialog, (newVal, oldVal) => {
  if (oldVal === 'personal-settings' && newVal === null) {
    loadUserProfile()
  }
})

// 用户下拉菜单
const isUserMenuOpen = ref(false)
const userInfoRef = ref<HTMLElement | null>(null)
const userDropdownPosition = ref<{ top: number; right: number }>({ top: 0, right: 0 })

// 计算用户下拉菜单位置
const updateUserDropdownPosition = () => {
  if (userInfoRef.value) {
    const rect = userInfoRef.value.getBoundingClientRect()
    userDropdownPosition.value = {
      top: rect.bottom + window.scrollY + 8,
      right: window.innerWidth - rect.right
    }
  }
}

// 用户下拉菜单样式
const userDropdownStyle = computed(() => ({
  position: 'fixed',
  top: `${userDropdownPosition.value.top}px`,
  right: `${userDropdownPosition.value.right}px`
}))

const navigateToDocumentRecognition = () => {
  router.push('/document-recognition')
}

const navigateToSystemSettings = () => {
  if (!isLoggedInRef.value) {
    ElMessage.warning('此功能需要登录')
    openLoginModal()
    isUserMenuOpen.value = false
    return
  }
  openSystemSettings()
  isUserMenuOpen.value = false
}

const navigateToPersonalSettings = () => {
  if (!isLoggedInRef.value) {
    ElMessage.warning('此功能需要登录')
    openLoginModal()
    isUserMenuOpen.value = false
    return
  }
  openPersonalSettings()
  isUserMenuOpen.value = false
}

const handleLogout = () => {
  clearAuth()
  isUserMenuOpen.value = false
}

const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
  if (isUserMenuOpen.value) {
    // 使用 nextTick 确保 DOM 更新后再计算位置
    nextTick(() => {
      updateUserDropdownPosition()
    })
  }
}

// 点击外部关闭下拉菜单
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as Node
  const isClickInsideUserInfo = userInfoRef.value && userInfoRef.value.contains(target)
  const isClickInsideDropdown = (target as HTMLElement).closest('.user-dropdown-menu')
  if (!isClickInsideUserInfo && !isClickInsideDropdown) {
    isUserMenuOpen.value = false
  }
}

watch(() => route.query.view, applyRouteView)
watch(isLoggedInRef, (loggedIn) => {
  if (loggedIn) loadUserProfile()
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  loadModels()
  if (isLoggedInRef.value) loadUserProfile()
  applyRouteView()
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@300;400;500;700&family=Space+Grotesk:wght@300;400;500;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.homepage-container {
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
  background-color: #0B1120;
  color: white;
  overflow: hidden;
  height: 100vh;
  display: flex;
}

/* Sidebar Styles */
.sidebar {
  width: 16rem;
  height: 100%;
  display: flex;
  flex-direction: column;
  border-right: 1px solid #232f48;
  background-color: #0B1120;
  flex-shrink: 0;
  z-index: 20;
}

.sidebar-header {
  width: 100%;
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border: none;
  background: transparent;
  color: inherit;
  font: inherit;
  text-align: left;
  cursor: pointer;
  transition: opacity 0.2s;
}

.sidebar-header:hover {
  opacity: 0.9;
}

.logo-icon {
  width: 2rem;
  height: 2rem;
  color: #135bec;
}

.logo-icon .material-symbols-outlined {
  font-size: 1.875rem;
}

.logo-text {
  font-size: 1.125rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  color: white;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.menu-section {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.menu-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0 0.5rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  border-radius: 0.5rem;
  color: #cbd5e1;
  transition: all 0.2s;
  cursor: pointer;
  background: transparent;
  border: none;
  text-decoration: none;
  width: 100%;
}

.menu-item:hover {
  background-color: #151e32;
  color: white;
}

.menu-item.active-item {
  background-color: #135bec;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.2);
}

.menu-item.nav-active {
  background-color: #151e32;
  color: #135bec;
  font-weight: 500;
  border-left: 4px solid #135bec;
}

.menu-item .material-symbols-outlined {
  font-size: 1.25rem;
}

.item-text {
  font-size: 0.875rem;
  font-weight: 500;
}

.sidebar-footer {
  padding: 1rem;
  border-top: 1px solid #232f48;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  width: 100%;
  border-radius: 0.5rem;
  color: #ef4444;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  font-size: 0.875rem;
  font-weight: 500;
}

.logout-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.logout-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

/* Main Content Styles */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background-color: #0B1120;
  position: relative;
}

.top-header {
  height: 4rem;
  border-bottom: 1px solid #232f48;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1.5rem;
  flex-shrink: 0;
  background-color: rgba(11, 17, 32, 0.9);
  backdrop-filter: blur(12px);
  z-index: 10;
}

.mobile-header {
  display: none;
  align-items: center;
  gap: 0.75rem;
  color: white;
}

.mobile-title {
  font-weight: 700;
  font-size: 1.125rem;
}

/* Navigation Buttons */
.nav-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.nav-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.875rem;
  border-radius: 0.5rem;
  color: #94a3b8;
  text-decoration: none;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  white-space: nowrap;
}

.nav-btn:hover {
  color: #ffffff;
  background-color: rgba(255, 255, 255, 0.05);
}

.nav-btn.active {
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.nav-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.search-container {
  display: flex;
  flex: 1;
  max-width: 36rem;
}

.search-wrapper {
  position: relative;
  width: 100%;
}

.search-icon {
  position: absolute;
  top: 0;
  bottom: 0;
  left: 0;
  padding-left: 0.75rem;
  display: flex;
  align-items: center;
  pointer-events: none;
}

.search-icon .material-symbols-outlined {
  color: #94a3b8;
}

.search-input {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 2.5rem;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  background-color: #151e32;
  color: white;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.search-input::placeholder {
  color: #94a3b8;
}

.search-input:focus {
  outline: none;
  border-color: #135bec;
  ring: 1px solid rgba(19, 91, 236, 0.5);
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.header-divider {
  width: 1px;
  height: 1.5rem;
  background-color: #232f48;
}

.header-auth-buttons {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.header-auth-btn {
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}
.header-auth-btn.register {
  color: #94a3b8;
  background: transparent;
}
.header-auth-btn.register:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.05);
}
.header-auth-btn.login {
  color: white;
  background: #135bec;
}
.header-auth-btn.login:hover {
  background: #1d64f2;
}

.header-user-info {
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.header-user-info:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.header-user-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 9999px;
  background-color: #1e293b;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2364748b'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
  background-size: 60%;
  background-position: center;
  background-repeat: no-repeat;
  background-position: center;
}

.header-user-details {
  display: flex;
  flex-direction: column;
}

.header-user-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

.header-user-role {
  font-size: 0.75rem;
  color: #94a3b8;
}

.dropdown-arrow {
  font-size: 1.25rem;
  color: #94a3b8;
  transition: transform 0.2s;
}

.dropdown-arrow.expanded {
  transform: rotate(180deg);
}

/* 用户下拉菜单 - 使用 Teleport 渲染到 body，position 由内联样式控制 */
.user-dropdown-menu {
  min-width: 16rem;
  background-color: #151e32;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.5);
  z-index: 99999;
  overflow: hidden;
  animation: dropdownFadeIn 0.2s ease-out;
}

@keyframes dropdownFadeIn {
  from {
    opacity: 0;
    transform: translateY(-0.5rem);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.dropdown-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem;
  border-bottom: 1px solid #232f48;
}

.dropdown-avatar {
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 9999px;
  background-color: #1e293b;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2364748b'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
  background-size: 60%;
  background-position: center;
  background-repeat: no-repeat;
  background-position: center;
}

.dropdown-info {
  display: flex;
  flex-direction: column;
}

.dropdown-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
}

.dropdown-role {
  font-size: 0.75rem;
  color: #94a3b8;
}

.dropdown-divider {
  height: 1px;
  background-color: #232f48;
  margin: 0;
}

.dropdown-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  text-decoration: none;
  font-size: 0.875rem;
  transition: all 0.2s;
  cursor: pointer;
}

.dropdown-item:hover {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

.dropdown-item .material-symbols-outlined {
  font-size: 1.125rem;
}

.dropdown-item.logout-item {
  color: #ef4444;
}

.dropdown-item.logout-item:hover {
  background-color: rgba(239, 68, 68, 0.1);
  color: #f87171;
}

.icon-button {
  position: relative;
  padding: 0.5rem;
  color: #cbd5e1;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.icon-button:hover {
  color: white;
}

.notification-badge {
  position: absolute;
  top: 0.375rem;
  right: 0.375rem;
  width: 0.5rem;
  height: 0.5rem;
  background-color: #ef4444;
  border-radius: 9999px;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* Content Area */
.content-area {
  flex: 1;
  overflow-y: auto;
  padding: 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

/* Chat active: no padding, fill height */
.content-area.chat-active {
  padding: 0;
  overflow: hidden;
}

.content-area.chat-active .home-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

/* Hero Section */
.hero-section {
  position: relative;
  border-radius: 1rem;
  overflow: hidden;
  min-height: 420px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  background-image: linear-gradient(rgba(11, 17, 32, 0.85), rgba(11, 17, 32, 0.7)),
                    url("https://lh3.googleusercontent.com/aida-public/AB6AXuBxOMNwFgRaFuZYRYn6o1pLKcyfUbKBPDhzXxoxmNkhMVt3t54CLsxmZFPSBNZhNAWV6imkNDZXt2lO9I_qfQQGogyz7VKmrPxuScBo5nu-QMMVTc9515CDFL1wkJ6-sCPqX6HKLRBu-Gyic3gDab1sYO9X-BRTk9p3j9sRQOpmroYDsozJVZeLnpKiTJ-tew6MrIkEQE00D9uoiAULS-Y7iRrCtJhKHqRwPhl1Db5lE4b-xqZgPe5hvKUO9TjgaMD3zyI8ZrBldZs");
  background-size: cover;
  background-position: center;
}

.hero-content {
  position: relative;
  z-index: 10;
  max-width: 64rem;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  align-items: center;
}

.hero-text {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.version-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background-color: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
  backdrop-filter: blur(4px);
  margin-bottom: 0.5rem;
  width: fit-content;
  margin-left: auto;
  margin-right: auto;
  color: #60a5fa;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.badge-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 9999px;
  background-color: #60a5fa;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.hero-title {
  color: white;
  font-size: 3rem;
  font-weight: 700;
  letter-spacing: -0.025em;
  line-height: 1.2;
}

.hero-description {
  color: #cbd5e1;
  font-size: 1.125rem;
  font-weight: 300;
  max-width: 42rem;
  margin: 0 auto;
  line-height: 1.625;
}

.search-box-container {
  width: 100%;
  max-width: 42rem;
  margin-top: 1.5rem;
}

.search-box-wrapper {
  display: flex;
  flex-direction: column;
  width: 100%;
  min-height: 3.5rem;
  position: relative;
}

.search-box {
  display: flex;
  flex-direction: row;
  flex-wrap: nowrap;
  width: 100%;
  align-items: stretch;
  min-height: 3.5rem;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(19, 91, 236, 0.2);
  background-color: rgba(21, 30, 50, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid #232f48;
  transition: all 0.3s;
  overflow: hidden;
}

.search-box.has-files {
  flex-wrap: wrap;
}

.search-box.has-files .search-box-body {
  min-height: 2.5rem;
}

.search-box:focus-within {
  border-color: #135bec;
  box-shadow: 0 0 0 1px rgba(19, 91, 236, 0.5);
}

.search-box-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  width: 3rem;
  padding: 0 0.5rem;
  border-radius: 0.75rem 0 0 0.75rem;
  color: #60a5fa;
}

.search-box-icon .material-symbols-outlined {
  font-size: 1.5rem;
  animation: pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}

.search-box-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  padding: 0.5rem 0;
}

.search-box-input {
  width: 100%;
  min-width: 0;
  background: transparent;
  border: none;
  color: white;
  padding: 0 0.75rem;
  font-size: 1rem;
  font-weight: 500;
  line-height: 1.5;
  box-shadow: none;
  outline: none;
}

.search-box-input::placeholder {
  color: #64748b;
}

.search-box-input:focus {
  outline: none;
}

.attach-files-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem 0 0;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.attach-label {
  margin-right: 0.25rem;
}

.file-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  background: rgba(19, 91, 236, 0.15);
  border: 1px solid rgba(19, 91, 236, 0.3);
  border-radius: 0.375rem;
  color: #93c5fd;
}

.file-tag-remove {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0 0.125rem;
  font-size: 1rem;
  line-height: 1;
}

.file-tag-remove:hover {
  color: #f87171;
}

.search-box-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding-right: 0.5rem;
}

.search-box-actions-bar {
  display: flex;
  align-items: stretch;
  flex-shrink: 0;
  gap: 0.25rem;
  padding: 0.375rem 0.5rem 0.375rem 0;
}

.search-box-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.5rem 0.75rem 0.5rem 0;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 0.5rem;
  background: transparent;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.toolbar-icon:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.06);
}

.toolbar-icon.active {
  background: rgba(19, 91, 236, 0.2);
  color: #60a5fa;
  border-radius: 9999px;
  padding: 0 0.5rem;
  width: auto;
}

.toolbar-model-wrap {
  position: relative;
}

.toolbar-model-wrap .toolbar-icon .model-name {
  max-width: 6rem;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-size: 0.75rem;
}

.model-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  margin-bottom: 0.25rem;
  min-width: 12rem;
  max-height: 14rem;
  overflow-y: auto;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.3);
  z-index: 50;
  padding: 0.25rem;
}

.model-option {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  text-align: left;
  border: none;
  border-radius: 0.375rem;
  background: transparent;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
}

.model-option:hover,
.model-option.active {
  background: rgba(19, 91, 236, 0.2);
  color: #60a5fa;
}

.voice-btn.recording {
  background: rgba(34, 197, 94, 0.25);
  color: #4ade80;
}

.inline-generate {
  padding: 0.5rem 0.75rem;
  min-width: 2.5rem;
}

.inline-generate .material-symbols-outlined {
  font-size: 1.25rem;
}

/* ========== 交互模式（AI 对话页） ========== */
.chat-mode-section {
  position: relative;
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 420px;
}

/* 顶部返回按钮栏 */
.chat-top-bar {
  display: flex;
  align-items: center;
  padding: 12px 24px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  flex-shrink: 0;
}

.chat-back-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
  padding: 6px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.chat-back-btn:hover {
  background: rgba(255, 255, 255, 0.12);
  color: #fff;
  border-color: rgba(255, 255, 255, 0.2);
}

.chat-back-btn .material-symbols-outlined {
  font-size: 18px;
}

/* 滚动消息区域 */
.chat-scroll-area {
  flex: 1;
  overflow-y: auto;
  padding: 2rem 1rem 10rem;
  scroll-behavior: smooth;
}

.chat-center-col {
  max-width: 56rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
}

/* 欢迎区域 */
.chat-welcome {
  text-align: center;
  padding: 3rem 0 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}

.chat-welcome-icon {
  width: 4rem;
  height: 4rem;
  background: rgba(19, 91, 236, 0.2);
  border-radius: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 0 0 1px rgba(19, 91, 236, 0.5), 0 8px 24px rgba(19, 91, 236, 0.2);
}

.chat-welcome-icon .material-symbols-outlined {
  font-size: 2rem;
  color: #135bec;
}

.chat-welcome-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
  margin: 0;
}

.chat-welcome-desc {
  font-size: 0.875rem;
  color: #94a3b8;
  max-width: 28rem;
  line-height: 1.7;
  margin: 0;
}

/* --- 消息行 --- */
.cmsg {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
}

.cmsg-ai {
  justify-content: flex-start;
}

.cmsg-user {
  justify-content: flex-end;
}

/* AI 头像 */
.cmsg-avatar {
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: #135bec;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
}

.cmsg-avatar .material-symbols-outlined {
  font-size: 1.125rem;
  color: white;
}

.cmsg-avatar-dot {
  position: absolute;
  bottom: -3px;
  right: -3px;
  width: 0.75rem;
  height: 0.75rem;
  background: #22c55e;
  border-radius: 9999px;
  border: 2px solid #0B1120;
}

/* 消息体 */
.cmsg-body {
  max-width: 85%;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.cmsg-user .cmsg-body {
  align-items: flex-end;
}

/* 气泡 */
.cmsg-bubble {
  padding: 1.25rem;
  line-height: 1.7;
  font-size: 0.9375rem;
  word-break: break-word;
  white-space: pre-wrap;
}

.cmsg-bubble-ai {
  background: rgba(22, 27, 38, 0.5);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1rem 1rem 1rem 0;
  color: #e2e8f0;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.cmsg-bubble-user {
  background: #135bec;
  color: white;
  border-radius: 1rem 1rem 0 1rem;
  box-shadow: 0 4px 12px rgba(19, 91, 236, 0.15);
}

/* AI 消息内部 */
.cmsg-source-hint {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0 0 0.75rem;
  padding-bottom: 0.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.cmsg-ai-content {
  font-size: 0.9375rem;
  color: #e2e8f0;
  line-height: 1.7;
}

.cmsg-ai-content :deep(strong) {
  color: #93c5fd;
}

.cmsg-ai-content :deep(b) {
  color: #60a5fa;
  font-weight: 600;
}

/* 宽气泡（结构化报价结果） - 让表格有足够空间 */
.cmsg-bubble-wide {
  max-width: none !important;
  width: 100%;
}

.cmsg-ai .cmsg-body:has(.cmsg-bubble-wide) {
  max-width: 95%;
}

/* 快捷操作按钮 */
.cmsg-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cmsg-action-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(255, 255, 255, 0.05);
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.cmsg-action-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.1);
}

.cmsg-action-btn .material-symbols-outlined {
  font-size: 0.875rem;
}

.cmsg-action-btn.cmsg-action-primary {
  background: rgba(19, 91, 236, 0.2);
  border-color: rgba(19, 91, 236, 0.3);
  color: #60a5fa;
}

.cmsg-action-btn.cmsg-action-primary:hover {
  background: rgba(19, 91, 236, 0.3);
  color: white;
}

/* 用户文件卡片 */
.cmsg-user-files {
  display: flex;
  justify-content: flex-end;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.cmsg-file-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(22, 27, 38, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  min-width: 14rem;
}

.cmsg-file-icon {
  width: 2.5rem;
  height: 2.5rem;
  background: rgba(239, 68, 68, 0.2);
  border-radius: 0.375rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.cmsg-file-icon .material-symbols-outlined {
  font-size: 1.25rem;
  color: #ef4444;
}

.cmsg-file-name {
  margin: 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 10rem;
}

/* ========== 底部浮动输入区 ========== */
.chat-float-bar {
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  padding: 1.5rem;
  background: linear-gradient(to top, #0B1120 40%, rgba(11, 17, 32, 0.95) 70%, transparent 100%);
  z-index: 10;
}

.chat-float-inner {
  max-width: 56rem;
  margin: 0 auto;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* 快捷建议 */
.chat-suggest-row {
  display: flex;
  gap: 0.5rem;
  overflow-x: auto;
  padding-bottom: 0.25rem;
}

.chat-suggest-pill {
  flex-shrink: 0;
  padding: 0.5rem 1rem;
  border-radius: 9999px;
  border: 1px solid rgba(255, 255, 255, 0.1);
  background: rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.chat-suggest-pill:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
  color: white;
}

/* 输入卡片 */
.chat-input-card {
  background: rgba(22, 27, 38, 1);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 1rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  padding: 0.5rem;
  transition: all 0.2s;
}

.chat-input-card.focused {
  border-color: rgba(19, 91, 236, 0.4);
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.15), 0 4px 20px rgba(0, 0, 0, 0.4);
}

.chat-input-row {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.chat-attach-btn {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.chat-attach-btn:hover {
  color: white;
  background: rgba(255, 255, 255, 0.05);
}

.chat-text-input {
  flex: 1;
  min-width: 0;
  background: transparent;
  border: none;
  color: white;
  font-size: 0.9375rem;
  padding: 0.5rem 0.25rem;
  outline: none;
}

.chat-text-input::placeholder {
  color: #64748b;
}

.chat-input-btns {
  display: flex;
  gap: 0.25rem;
  padding-right: 0.25rem;
}

.chat-send-btn {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.75rem;
  background: #135bec;
  color: white;
  border: none;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 4px 12px rgba(19, 91, 236, 0.2);
}

.chat-send-btn:hover:not(:disabled) {
  background: #2563eb;
}

.chat-send-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.chat-send-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.chat-send-btn .btn-loading {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

/* 已附加文件 */
.chat-attached-row {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem 0.5rem;
  font-size: 0.75rem;
}

.chat-attached-label {
  color: #94a3b8;
}

.chat-attached-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.2rem 0.5rem;
  background: rgba(19, 91, 236, 0.15);
  border: 1px solid rgba(19, 91, 236, 0.3);
  border-radius: 0.375rem;
  color: #93c5fd;
  font-size: 0.75rem;
}

.chat-attached-remove {
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0;
  font-size: 1rem;
  line-height: 1;
}

.chat-attached-remove:hover {
  color: #f87171;
}

/* 免责声明 */
.chat-disclaimer {
  text-align: center;
  font-size: 0.625rem;
  color: #475569;
  margin: 0;
}

.file-input-hidden {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.attach-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  background: transparent;
  border: 1px solid #334155;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.attach-btn:hover {
  border-color: #135bec;
  color: #60a5fa;
}

.attach-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.search-box-button {
  display: flex;
  align-items: center;
  justify-content: center;
}

.generate-button {
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #135bec;
  color: white;
  font-weight: 700;
  border-radius: 0.5rem;
  padding: 0.625rem 1.5rem;
  transition: all 0.2s;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.3);
}

.generate-button-inline {
  align-self: stretch;
  border-radius: 0 0.75rem 0.75rem 0;
  padding: 0 1.25rem;
  min-height: 2.5rem;
}

.generate-button:hover:not(:disabled) {
  background-color: #1e40af;
  box-shadow: 0 10px 15px -3px rgba(59, 130, 246, 0.3);
}

.generate-button:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.generate-button .btn-loading {
  width: 1rem;
  height: 1rem;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* AI 分析结果弹窗 */
.result-modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 1rem;
}

.result-modal {
  width: 100%;
  max-width: 36rem;
  max-height: 85vh;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
}

.result-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #334155;
}

.result-modal-header h3 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: #f1f5f9;
}

.result-modal-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border-radius: 0.5rem;
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.result-modal-close:hover {
  color: #f1f5f9;
}

.result-modal-body {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem;
}

.result-analysis {
  font-size: 0.9375rem;
  line-height: 1.6;
  color: #e2e8f0;
}

.result-analysis :deep(strong) {
  color: #f1f5f9;
}

.result-modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 1rem 1.25rem;
  border-top: 1px solid #334155;
}

.result-btn {
  padding: 0.5rem 1.25rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.result-btn.secondary {
  background: #334155;
  color: #e2e8f0;
}

.result-btn.secondary:hover {
  background: #475569;
}

.result-btn.primary {
  background: #135bec;
  color: white;
}

.result-btn.primary:hover {
  background: #1e40af;
}

.quick-examples {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
  color: #94a3b8;
  font-size: 0.875rem;
}

.examples-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  font-weight: 600;
  color: #64748b;
  padding-top: 0.125rem;
}

.example-link {
  color: inherit;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.example-link:hover {
  color: #135bec;
  text-decoration: underline;
}

.example-separator {
  color: #475569;
}

/* Stats Section */
.stats-section {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.stat-card {
  background-color: #151e32;
  padding: 1.5rem;
  border-radius: 0.75rem;
  border: 1px solid #232f48;
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: border-color 0.2s;
}

.stat-card:hover {
  border-color: rgba(19, 91, 236, 0.3);
}

.stat-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.stat-label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
}

.stat-icon {
  color: #135bec;
  font-size: 1.25rem;
}

.stat-icon.orange {
  color: #f97316;
}

.stat-icon.green {
  color: #22c55e;
}

.stat-content {
  display: flex;
  align-items: baseline;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: white;
}

.stat-trend {
  font-size: 0.875rem;
  font-weight: 500;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-trend.positive {
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.1);
}

.stat-trend .material-symbols-outlined {
  font-size: 0.75rem;
}

.stat-subtitle {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 400;
}

.stat-subtitle.green {
  color: #22c55e;
  font-weight: 500;
}

/* Categories Section */
.categories-section {
  display: flex;
  flex-direction: column;
}

.section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1.5rem;
}

.section-title {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.title-marker {
  width: 0.25rem;
  height: 1.5rem;
  background-color: #135bec;
  border-radius: 9999px;
}

.view-all-link {
  font-size: 0.875rem;
  color: #135bec;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.25rem;
  transition: all 0.2s;
  text-decoration: none;
}

.view-all-link:hover {
  color: #60a5fa;
  gap: 0.5rem;
}

.view-all-link .material-symbols-outlined {
  font-size: 1rem;
}

.categories-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.category-card {
  position: relative;
  background-color: #151e32;
  border-radius: 0.75rem;
  overflow: hidden;
  border: 1px solid #232f48;
  cursor: pointer;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  transition: all 0.3s;
}

.category-card:hover {
  border-color: rgba(19, 91, 236, 0.5);
  box-shadow: 0 20px 25px -5px rgba(19, 91, 236, 0.05);
}

.category-image {
  height: 12rem;
  background-size: cover;
  background-position: center;
  position: relative;
  transition: transform 0.7s;
}

.category-card:hover .category-image {
  transform: scale(1.05);
}

.category-image::after {
  content: '';
  position: absolute;
  inset: 0;
  background: linear-gradient(to top, #151e32, rgba(21, 30, 50, 0.5), transparent);
  opacity: 0.9;
}

.category-image.datacenter {
  background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuCOHlzEIY4W-0s6iWRScx8m0LmVQdQByh73Vt3_KXDwPPmuzvBY2nd1kncOoiad6vTEaSL5O0f55kiGjVW6SGGibDy8GcDiKUGdULBE0NPY3FE_bOh0U3CN3twcRnDEEuU9DxozpSC3z-UaQ_lxkqxq3ne56TSvRVEKTBw0zbfWaRDqDdv23dTLD027qAQ5Qe-hMk_BSUlbfxMmqOqIDQZZ9w00Jjj3voSqLo8e1fa4iCXAxz-G_Jud8W6G-tsGsr8SIoajVPUNMjM");
}

.category-image.office {
  background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuAsiwbdo-0xcdfPRny-2ypDGqfXmc2tgXsxlXGenwnr6joNJ_d6qRCV19QPivH6SHRFW6RJjSE4CB6b9Zm21B4fHS7FOcIkCceVdEB9igDV1nFcrNzQSQHH8_SD0PXDldCUdNrr2ep56-46PSDT9_FSlN68ntue58QheY7xcHu-iatrsmSbq9SXLCsdREtpydf3ZsBjl_7LR0q6ppLfnJygpMCIN3AP3uxXrSM4CM_87MTTgERb3E0un1CnL7GfEc7dFSqF_MJdakI");
}

.category-image.security {
  background-image: url("https://lh3.googleusercontent.com/aida-public/AB6AXuAj41-Ihy33RX-A4pqAq2Uh64MXHMoNJVS5YlGXGE0jYsVN6Pca1l3akzixJrSe4Q6NX2YT_FCHk8OmiaS7D03z6gxHW39lDNcyTMvs8noG_8Q2AbzwXZC4qqurryxcydNtlHnPQAKHAzbS9gY0gBK2sNNcEtJ0gXplO1CJv4Cc810Rr9n2JOE7feMqTyjkBP1XdrneGBzqMWuxD5-Inhrhr-achGTp_plrnAliepUbQIygEC7TtLtn6gUjDA3nlAKrtUUpIswWnJI");
}

.category-content {
  padding: 1.25rem;
  position: relative;
}

.category-icon-wrapper {
  position: absolute;
  top: -2rem;
  right: 1.25rem;
  width: 3.5rem;
  height: 3.5rem;
  background: linear-gradient(135deg, #135bec, #1e40af);
  border-radius: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.3);
  color: white;
  transition: transform 0.3s;
}

.category-card:hover .category-icon-wrapper {
  transform: translateY(-0.25rem);
}

.category-icon-wrapper .material-symbols-outlined {
  font-size: 1.875rem;
}

.category-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 0.5rem;
  transition: color 0.2s;
}

.category-card:hover .category-title {
  color: #135bec;
}

.category-description {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-bottom: 1.25rem;
  height: 2.5rem;
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.category-tags {
  display: flex;
  align-items: center;
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tag {
  background-color: #1e293b;
  border: 1px solid #334155;
  padding: 0.25rem 0.625rem;
  border-radius: 0.375rem;
  color: #cbd5e1;
}

/* Scrollbar Styles */
::-webkit-scrollbar {
  width: 6px;
  height: 6px;
}

::-webkit-scrollbar-track {
  background: #0B1120;
}

::-webkit-scrollbar-thumb {
  background: #232f48;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #324467;
}

/* Embedded View (Product Database, Quote History, System Settings) */
.content-area.embedded-view {
  padding: 0;
  overflow: auto;
  display: flex;
  flex-direction: column;
}

.content-area.embedded-view > :deep(.product-database),
.content-area.embedded-view > :deep(.quote-history-page),
.content-area.embedded-view > :deep(.onsite-calculator-page),
.content-area.embedded-view > :deep(.relocation-calculator-page) {
  min-height: 100%;
  display: flex;
  flex-direction: column;
}

.content-area.embedded-view > :deep(.product-database) > *,
.content-area.embedded-view > :deep(.quote-history-page) > *,
.content-area.embedded-view > :deep(.onsite-calculator-page) > *,
.content-area.embedded-view > :deep(.relocation-calculator-page) > * {
  border-radius: 0;
}

.content-area.embedded-view > :deep(.product-database) .page-header,
.content-area.embedded-view > :deep(.quote-history-page) .page-header,
.content-area.embedded-view > :deep(.onsite-calculator-page) .page-header,
.content-area.embedded-view > :deep(.relocation-calculator-page) .page-header {
  border-radius: 0;
}

/* Draft View */
.content-area.draft-view {
  display: block;
  padding: 2rem;
  height: calc(100vh - 5rem);
}

.draft-view-container {
  height: 100%;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

/* Responsive Design */
@media (max-width: 768px) {
  .sidebar {
    display: none;
  }

  .mobile-header {
    display: flex;
  }

  .search-container {
    display: none;
  }

  .stats-section {
    grid-template-columns: 1fr;
  }

  .categories-grid {
    grid-template-columns: 1fr;
  }

  .hero-title {
    font-size: 2rem;
  }

  .content-area {
    padding: 1.5rem;
  }
}

@media (max-width: 980px) {
  .categories-grid {
    grid-template-columns: 1fr;
  }
}
</style>
