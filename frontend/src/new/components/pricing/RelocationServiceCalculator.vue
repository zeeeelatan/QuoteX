<template>
  <div class="relocation-calculator-page" :class="{ 'embedded-mode': embedded }">
    <!-- 生成正式报价单弹窗（非嵌入模式） -->
    <Teleport v-if="!embedded" to="body">
      <Transition name="relocation-modal">
        <div v-if="showQuotationView" class="relocation-quotation-overlay" @click.self="closeQuotationView">
          <div
            class="relocation-quotation-window"
            :class="{ maximized: quotationMaximized }"
            :style="quotationWindowStyle"
          >
            <!-- 标题栏 -->
            <div class="relocation-quotation-header">
              <div class="relocation-quotation-header-left">
                <div class="relocation-quotation-breadcrumb">
                  <span class="relocation-quotation-breadcrumb-link">搬迁服务报价测算</span>
                  <span class="material-symbols-outlined">chevron_right</span>
                  <span class="relocation-quotation-breadcrumb-current">生成正式报价单</span>
                </div>
                <h1 class="relocation-quotation-title">
                  报价单预览
                  <span class="relocation-quotation-badge">A4 打印视图</span>
                </h1>
              </div>
              <div class="relocation-quotation-header-right">
                <div class="relocation-quotation-zoom">
                  <button type="button" class="relocation-quotation-zoom-btn" @click="quotationZoomOut" title="缩小">
                    <span class="material-symbols-outlined">remove</span>
                  </button>
                  <span class="relocation-quotation-zoom-level">{{ quotationZoomLevel }}%</span>
                  <button type="button" class="relocation-quotation-zoom-btn" @click="quotationZoomIn" title="放大">
                    <span class="material-symbols-outlined">add</span>
                  </button>
                </div>
                <button type="button" class="relocation-quotation-fullscreen-btn" @click="toggleQuotationMaximize">
                  <span class="material-symbols-outlined">{{ quotationMaximized ? 'fullscreen_exit' : 'fullscreen' }}</span>
                </button>
                <button type="button" class="relocation-quotation-close-btn" @click="closeQuotationView" title="关闭">
                  <span class="material-symbols-outlined">close</span>
                </button>
              </div>
            </div>

            <!-- 内容区域：预览 + 侧边栏 -->
            <div class="relocation-quotation-main">
              <!-- 文档预览区域 -->
              <div class="relocation-quotation-preview-section">
                <div class="relocation-quotation-preview-scroll">
                  <div
                    ref="quotationContentRef"
                    class="relocation-quotation-paper"
                    :style="{ transform: `scale(${quotationZoomLevel / 100})` }"
                  >
                    <div class="relocation-quotation-paper-inner">
                      <!-- 文档头部 -->
                      <div class="rq-doc-header">
                        <div class="rq-doc-header-left">
                          <div class="rq-doc-logo" @click="triggerRelocationLogoUpload" title="点击上传自定义 Logo" style="cursor: pointer;">
                            <img v-if="relocationCustomLogoUrl" :src="relocationCustomLogoUrl" alt="公司Logo" style="max-height: 48px; max-width: 200px; object-fit: contain;" />
                            <template v-else>
                              <span class="material-symbols-outlined">rocket_launch</span>
                              <span class="rq-doc-logo-text">{{ QUOTATION_COMPANY.name }}</span>
                            </template>
                            <input
                              type="file"
                              ref="relocationLogoInputRef"
                              accept="image/*"
                              style="display: none;"
                              @change="handleRelocationLogoUpload"
                            />
                          </div>
                          <h2 class="rq-doc-title">数据中心搬迁服务报价单</h2>
                          <p class="rq-doc-subtitle">系统编号：{{ quotationData.meta.orderNo }}</p>
                        </div>
                        <div class="rq-doc-header-right">
                          <div class="rq-doc-status">PREVIEW</div>
                          <p class="rq-doc-date">打印日期：{{ quotationData.meta.date }}</p>
                        </div>
                      </div>

                      <!-- 信息网格 -->
                      <div class="rq-info-grid">
                        <div class="rq-info-block">
                          <h3 class="rq-info-label">报价方信息</h3>
                          <p class="rq-info-title">{{ quotationData.companyName }}</p>
                          <p class="rq-info-text">联系人：李经理</p>
                          <p class="rq-info-text">电话：400-888-9999</p>
                        </div>
                        <div class="rq-info-block">
                          <h3 class="rq-info-label">客户信息</h3>
                          <p class="rq-info-title">{{ quotationData.customer.name }}</p>
                          <p class="rq-info-text" v-for="(line, i) in quotationData.customer.locationLines" :key="i">{{ line }}</p>
                        </div>
                        <div class="rq-info-block">
                          <h3 class="rq-info-label">项目摘要</h3>
                          <p class="rq-info-text"><span class="rq-info-highlight">报价日期：</span>{{ quotationData.meta.date }}</p>
                          <p class="rq-info-text"><span class="rq-info-highlight">有效期至：</span>{{ quotationData.meta.validUntil || '30天内有效' }}</p>
                          <p class="rq-info-text"><span class="rq-info-highlight">币种：</span>人民币 (CNY)</p>
                        </div>
                      </div>

                      <!-- 报价表格 -->
                      <div class="rq-table-section">
                        <table class="rq-table">
                          <thead>
                            <tr>
                              <th class="rq-th">项目名称</th>
                              <th class="rq-th">服务描述</th>
                              <th class="rq-th">单位</th>
                              <th class="rq-th rq-th-right">数量</th>
                              <th class="rq-th rq-th-right">单价</th>
                              <th class="rq-th rq-th-right">小计</th>
                            </tr>
                          </thead>
                          <tbody>
                            <template v-for="(group, gIdx) in groupedQuotationItems" :key="gIdx">
                              <tr class="rq-group-row">
                                <td colspan="6" class="rq-group-cell">【{{ group.name }}】</td>
                              </tr>
                              <tr v-for="(item, idx) in group.items" :key="item.id" class="rq-item-row">
                                <td class="rq-td rq-td-name">{{ item.title }}</td>
                                <td class="rq-td rq-td-desc">{{ item.desc || '-' }}</td>
                                <td class="rq-td">{{ item.unit || '项' }}</td>
                                <td class="rq-td rq-td-right">{{ item.qty }}</td>
                                <td class="rq-td rq-td-right">¥{{ formatMoney(item.price) }}</td>
                                <td class="rq-td rq-td-right rq-td-total">¥{{ formatMoney(item.qty * item.price) }}</td>
                              </tr>
                            </template>
                          </tbody>
                        </table>
                      </div>

                      <!-- 汇总区域 -->
                      <div class="rq-summary">
                        <div class="rq-summary-box">
                          <div class="rq-summary-row">
                            <span class="rq-summary-label">项目小计:</span>
                            <span class="rq-summary-value">¥{{ formatMoney(quotationData.subTotal) }}</span>
                          </div>
                          <div class="rq-summary-row">
                            <span class="rq-summary-label">增值税 ({{ quotationData.taxRatePercent }}%):</span>
                            <span class="rq-summary-value">¥{{ formatMoney(quotationData.subTotal * quotationData.taxRatePercent / 100) }}</span>
                          </div>
                          <div class="rq-summary-divider"></div>
                          <div class="rq-summary-row rq-summary-total-row">
                            <span class="rq-summary-total-label">总计金额:</span>
                            <span class="rq-summary-total-value">¥{{ formatMoney(quotationData.finalTotal) }}</span>
                          </div>
                        </div>
                      </div>

                      <!-- 条款说明 -->
                      <div class="rq-terms">
                        <div class="rq-terms-col">
                          <p class="rq-terms-title">支付说明：</p>
                          <ul class="rq-terms-list">
                            <li>预付款项：合同签订后支付 30%</li>
                            <li>验收款项：项目完成并验收通过后支付 60%</li>
                            <li>质保金：验收通过半年后支付 10%</li>
                          </ul>
                        </div>
                        <div class="rq-terms-col">
                          <p class="rq-terms-title">备注说明：</p>
                          <p class="rq-terms-text">报价包含气垫车运输服务及夜间施工费用。若设备搬迁规模变动超过 10% 则需重新调整报价单。</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 配置侧边栏 -->
              <aside class="relocation-quotation-sidebar">
                <div class="rq-sidebar-header">
                  <h3 class="rq-sidebar-title">配置选项</h3>
                  <span class="material-symbols-outlined rq-sidebar-icon">sync_alt</span>
                </div>

                <!-- 客户选择 -->
                <div class="rq-sidebar-section">
                  <label class="rq-sidebar-label">选择客户</label>
                  <div class="rq-sidebar-select-wrap">
                    <select v-model="quotationCustomerSelect" class="rq-sidebar-select">
                      <option value="default">{{ quotationData.customer.name }}</option>
                    </select>
                    <span class="material-symbols-outlined rq-sidebar-select-icon">expand_more</span>
                  </div>
                </div>

                <!-- 价格布局 -->
                <div class="rq-sidebar-section">
                  <label class="rq-sidebar-label">价格布局</label>
                  <div class="rq-sidebar-toggle-group">
                    <button
                      type="button"
                      class="rq-sidebar-toggle-btn"
                      :class="{ active: quotationPriceLayout === 'with-tax' }"
                      @click="quotationPriceLayout = 'with-tax'"
                    >含税报价</button>
                    <button
                      type="button"
                      class="rq-sidebar-toggle-btn"
                      :class="{ active: quotationPriceLayout === 'without-tax' }"
                      @click="quotationPriceLayout = 'without-tax'"
                    >未税报价</button>
                  </div>
                </div>

                <!-- 报价模板 -->
                <div class="rq-sidebar-section">
                  <label class="rq-sidebar-label">报价模板</label>
                  <div class="rq-sidebar-templates">
                    <div
                      class="rq-sidebar-template"
                      :class="{ active: quotationTemplate === 'classic' }"
                      @click="quotationTemplate = 'classic'"
                    >
                      <div class="rq-template-preview rq-template-classic">
                        <div class="rq-tpl-bar"></div>
                        <div class="rq-tpl-line"></div>
                        <div class="rq-tpl-body"></div>
                      </div>
                      <p class="rq-template-name">经典商务</p>
                    </div>
                    <div
                      class="rq-sidebar-template"
                      :class="{ active: quotationTemplate === 'dark' }"
                      @click="quotationTemplate = 'dark'"
                    >
                      <div class="rq-template-preview rq-template-dark">
                        <div class="rq-tpl-bar"></div>
                        <div class="rq-tpl-line"></div>
                        <div class="rq-tpl-body"></div>
                      </div>
                      <p class="rq-template-name">暗黑科技</p>
                    </div>
                  </div>
                </div>

                <!-- 底部操作区 -->
                <div class="rq-sidebar-footer">
                  <!-- AI 建议 -->
                  <div class="rq-ai-suggestion">
                    <div class="rq-ai-header">
                      <span class="material-symbols-outlined">auto_awesome</span>
                      <span class="rq-ai-title">AI 建议</span>
                    </div>
                    <p class="rq-ai-text">根据历史数据，该类项目的「项目管理」费率通常在 12%-15% 之间，当前设定略低，建议上调以覆盖风险。</p>
                  </div>

                  <!-- 操作按钮 -->
                  <div class="rq-sidebar-actions">
                    <button type="button" class="rq-action-btn rq-action-secondary" @click="closeQuotationView">
                      <span class="material-symbols-outlined">edit</span>
                      编辑数据
                    </button>
                    <button type="button" class="rq-action-btn rq-action-secondary" @click="handleQuotationPrint">
                      <span class="material-symbols-outlined">visibility</span>
                      预览
                    </button>
                  </div>
                  <button type="button" class="rq-action-btn rq-action-primary" @click="handleExportQuotationPdf">
                    <span class="material-symbols-outlined">picture_as_pdf</span>
                    导出 PDF 报价单
                  </button>
                </div>
              </aside>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>

    <template v-if="embedded || !showQuotationView">
    <div v-if="!embedded" class="page-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">首页</span>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-item">报价工具</span>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-item active">搬迁服务报价测算</span>
      </div>
      <div class="header-actions-row">
        <div>
          <h1 class="page-title">
            搬迁服务报价测算
            <span class="ai-badge">V2.0 智能测算模型</span>
          </h1>
          <p class="page-subtitle">按 U 数梯度包装、车辆物流与保险费率的一体化成本测算</p>
        </div>
        <div class="header-buttons actions">
          <button type="button" class="header-btn" @click="resetForm">
            <span class="material-symbols-outlined">restart_alt</span>
            重置
          </button>
        </div>
      </div>
    </div>

    <div class="calculator-content">
      <div class="left-section">
        <div class="tabs-row">
          <div class="tabs">
            <button type="button" class="tab" :class="{ active: activeTab === 1 }" @click="activeTab = 1">1. 项目概况</button>
            <button type="button" class="tab" :class="{ active: activeTab === 2 }" @click="activeTab = 2">2. 设备清单管理</button>
            <button type="button" class="tab" :class="{ active: activeTab === 3 }" @click="activeTab = 3">3. 费用测算配置</button>
          </div>
        </div>

        <!-- 1. 项目概况 -->
        <template v-if="activeTab === 1">
          <section class="overview-section card panel">
            <div class="card-title-row">
              <span class="material-symbols-outlined card-icon primary">psychology</span>
              <h3 class="card-title">项目需求输入</h3>
            </div>
            <div class="overview-input-grid">
              <div class="upload-col">
                <label class="field-label">上传需求文档 (支持 PDF/Word/Excel)</label>
                <div
                  class="upload-zone"
                  :class="{ 'upload-zone-dragover': isDragging }"
                  @click="triggerFileInput"
                  @dragover.prevent="isDragging = true"
                  @dragleave.prevent="isDragging = false"
                  @drop.prevent="onDrop"
                >
                  <span class="material-symbols-outlined upload-icon">cloud_upload</span>
                  <p class="upload-text">点击或拖拽文件到此处</p>
                  <p class="upload-hint">最大支持 50MB</p>
                  <input
                    ref="fileInputRef"
                    type="file"
                    class="upload-input-hidden"
                    accept=".pdf,.doc,.docx,.xls,.xlsx"
                    multiple
                    @change="onFileSelect"
                  />
                </div>
                <p v-if="uploadedFiles.length" class="upload-files-hint">{{ uploadedFiles.length }} 个文件已选择</p>
              </div>
              <div class="desc-col">
                <label class="field-label">项目需求详细描述</label>
                <textarea
                  v-model="requirementDescription"
                  class="overview-textarea"
                  placeholder="请在此输入或粘贴项目的详细需求描述，例如：包含两地三中心搬迁、业务不停机要求、具体搬迁时间窗口等..."
                  rows="6"
                />
              </div>
            </div>
            <div class="overview-actions">
              <el-button type="primary" class="ai-glow-btn" @click="onAiAnalyze">
                <span class="material-symbols-outlined btn-icon">auto_awesome</span>
                AI 智能分析需求
              </el-button>
            </div>
          </section>
          <section class="overview-section card panel">
            <div class="breakdown-header">
              <div class="card-title-row">
                <span class="material-symbols-outlined card-icon primary">analytics</span>
                <h3 class="card-title">需求拆解明细表</h3>
              </div>
              <span class="breakdown-subtitle">基于 AI 模型分析生成，支持手动微调</span>
            </div>
            <div class="breakdown-table-wrap">
              <table class="tech-table">
                <thead>
                  <tr>
                    <th>服务类型</th>
                    <th>服务描述</th>
                    <th>服务明细</th>
                    <th>输出物</th>
                    <th>单位</th>
                    <th>数量</th>
                    <th>单价</th>
                    <th>总价</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in requirementBreakdown" :key="idx" class="tech-table-row">
                    <td class="service-type">{{ row.serviceType }}</td>
                    <td>{{ row.serviceDesc }}</td>
                    <td>{{ row.serviceDetail }}</td>
                    <td>{{ row.deliverable }}</td>
                    <td>{{ row.unit }}</td>
                    <td>{{ row.quantity }}</td>
                    <td>{{ row.unitPrice }}</td>
                    <td class="total-price">{{ row.totalPrice }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>
        </template>

        <template v-else-if="activeTab === 3">
          <!-- 搬迁路径配置 -->
          <section class="route-config-section card panel">
            <div class="route-config-header">
              <div>
                <h3 class="route-config-title">
                  <span class="material-symbols-outlined route-config-icon">route</span>
                  搬迁路径配置
                </h3>
                <p class="route-config-desc">按顺序设置路径中的地点，系统将自动识别地域属性</p>
              </div>
              <button type="button" class="add-row-btn" @click="addRouteLocation">
                <span class="material-symbols-outlined">add</span>
                添加地点
              </button>
            </div>
            <div class="route-path-list">
              <div class="route-path-line" aria-hidden="true"></div>
              <div
                v-for="(loc, index) in routeLocations"
                :key="loc.id"
                class="route-location-row"
                :class="{ confirmed: loc.confirmed, 'has-dropdown': loc.searching || loc.searchResults.length > 0 }"
              >
                <div
                  class="route-type-badge"
                  :class="index === 0 ? 'origin' : 'destination'"
                >
                  <span>{{ locationLabel(index) }}</span>
                </div>
                <div class="route-location-content">
                  <div class="route-location-header">
                    <span class="route-location-label">
                      {{ locationLabel(index) }}
                    </span>
                    <span v-if="loc.tier" class="route-tier-badge" :class="tierClass(loc.tier)">
                      {{ loc.tier }}
                    </span>
                  </div>
                  <div class="route-address-row">
                    <div class="route-address-input-wrap">
                      <input
                        v-model="loc.address"
                        type="text"
                        class="route-address-input"
                        placeholder="请输入详细地址，自动检索匹配地点..."
                        @input="onRouteAddressInput(loc.id)"
                        @blur="() => setTimeout(() => clearInlineSearchResults(loc.id), 200)"
                      />
                      <button
                        type="button"
                        class="route-map-btn"
                        title="打开地图选择"
                        @click="openRouteMapPicker(loc.id)"
                      >
                        <span class="material-symbols-outlined">map</span>
                      </button>
                      <!-- 内联搜索下拉框 -->
                      <div v-if="loc.searchResults.length > 0 || loc.searching" class="route-inline-dropdown">
                        <div v-if="loc.searching && loc.searchResults.length === 0" class="route-inline-loading">
                          <span class="material-symbols-outlined spinning">progress_activity</span>
                          搜索中...
                        </div>
                        <div
                          v-for="(res, ri) in loc.searchResults"
                          :key="ri"
                          class="route-inline-item"
                          @mousedown.prevent="selectInlineSearchResult(loc.id, res)"
                        >
                          <span class="material-symbols-outlined route-inline-icon">location_on</span>
                          <div class="route-inline-text">
                            <div class="route-inline-addr">{{ res.addr }}</div>
                            <div class="route-inline-meta">{{ res.city || '全国' }}</div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <div v-if="loc.confirmed" class="route-confirmed-info">
                    <span v-if="loc.selectedAddress" class="route-info-item route-selected-addr">
                      <span class="material-symbols-outlined route-info-icon place-icon">place</span>
                      <span class="route-selected-text">{{ loc.selectedAddress }}</span>
                    </span>
                    <span class="route-info-item">
                      <span class="material-symbols-outlined route-info-icon success">check_circle</span>
                      坐标: <span class="route-mono">{{ loc.coords }}</span>
                    </span>
                    <span class="route-info-item">
                      <span class="material-symbols-outlined route-info-icon">location_on</span>
                      所属城市: <span class="route-text">{{ loc.city }}</span>
                    </span>
                  </div>
                </div>
                <button
                  v-if="routeLocations.length > 1"
                  type="button"
                  class="route-delete-btn"
                  title="删除"
                  @click="removeRouteLocation(loc.id)"
                >
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
            </div>

            <!-- 地图位置确认弹窗 -->
            <div v-if="isRouteMapOpen" class="route-map-overlay" @click.self="closeRouteMap">
              <div class="route-map-modal" @click.stop>
                <div class="route-map-modal-header">
                  <h3 class="route-map-modal-title">
                    <span class="material-symbols-outlined">map</span>
                    地图位置确认
                  </h3>
                  <button type="button" class="route-map-close" aria-label="关闭" @click.stop="closeRouteMap">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
                <div class="route-map-modal-body">
                  <div class="route-map-search-wrap">
                    <span class="material-symbols-outlined route-map-search-icon">search</span>
                    <input
                      v-model="routeSearchQuery"
                      type="text"
                      class="route-map-search-input"
                      placeholder="输入关键词搜索地址..."
                      @keydown.enter.prevent="confirmRouteMapFromSearch"
                    />
                  </div>
                  <div class="route-map-preview">
                    <template v-if="hasAmapKey && !routeMapLoadFailed">
                      <div id="route-map-container" class="route-map-inner"></div>
                      <div v-if="routeMapLoading" class="route-map-loading">
                        <span class="material-symbols-outlined route-map-pin">location_on</span>
                        <p>地图加载中...</p>
                      </div>
                      <!-- 地图瓦片未加载时的提示遮罩 -->
                      <div v-if="!routeMapLoading && !routeMapTilesLoaded" class="route-map-tiles-hint">
                        <div class="route-map-tiles-hint-content">
                          <span class="material-symbols-outlined">info</span>
                          <span>地图详情可能受 API 限制无法显示，请直接从下方搜索结果选择位置</span>
                        </div>
                      </div>
                      <div v-if="routeMapPending && !routeMapLoading" class="route-map-confirm-row">
                        <span class="route-map-pending-text">
                          <span class="material-symbols-outlined route-info-icon success">check_circle</span>
                          {{ routeMapPending.address }} · {{ routeMapPending.city || '未知城市' }} · {{ routeMapPending.coords }}
                        </span>
                        <button type="button" class="route-map-confirm-btn" @click="confirmRouteMapSelection">
                          <span class="material-symbols-outlined">check</span>
                          确认该位置
                        </button>
                      </div>
                    </template>
                    <template v-else>
                      <div class="route-map-placeholder">
                        <span class="material-symbols-outlined route-map-pin">location_on</span>
                        <p v-if="routeMapLoadFailed">地图服务暂不可用（Key 可能被禁用），请从下方结果选择或联系管理员检查高德地图 Key</p>
                        <p v-else>请配置高德地图 Key (VITE_AMAP_KEY) 以使用地图选点</p>
                        <p class="route-map-placeholder-hint">或从下方结果选择/输入地址确认位置</p>
                      </div>
                    </template>
                  </div>
                  <div class="route-map-results">
                    <template v-if="routeMapSearching">
                      <p class="route-map-results-hint">搜索中...</p>
                    </template>
                    <template v-else-if="routeMapSearchResults.length">
                      <p class="route-map-results-title">
                        <span class="material-symbols-outlined">check_circle</span>
                        点击下方结果确认位置：
                      </p>
                      <button
                        v-for="(res, i) in routeMapSearchResults"
                        :key="i"
                        type="button"
                        class="route-map-result-item"
                        @click="confirmRouteMapPoint(res.city, res.addr, res.coords)"
                      >
                        <span class="material-symbols-outlined route-result-icon">check</span>
                        <div>
                          <div class="route-result-addr">{{ res.addr }}</div>
                          <div class="route-result-meta">{{ res.city || '全国' }} · {{ res.coords }}</div>
                        </div>
                      </button>
                    </template>
                    <template v-else>
                      <p class="route-map-results-hint">输入关键词后按回车搜索</p>
                    </template>
                  </div>
                </div>
              </div>
            </div>

            <!-- 路线规划弹窗 -->
            <div v-if="isRoutePlanningOpen" class="route-map-overlay" @click.self="closeRoutePlanning">
              <div class="route-planning-modal" @click.stop>
                <div class="route-map-modal-header">
                  <h3 class="route-map-modal-title">
                    <span class="material-symbols-outlined">directions_car</span>
                    驾车路线规划
                  </h3>
                  <button type="button" class="route-map-close" aria-label="关闭" @click.stop="closeRoutePlanning">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
                <div class="route-planning-body">
                  <!-- 路线信息 -->
                  <div class="route-planning-info">
                    <div class="route-planning-endpoints">
                      <div class="route-endpoint">
                        <span class="endpoint-marker origin">A</span>
                        <span class="endpoint-text">{{ routePlanningOrigin?.address || '始发地' }}</span>
                      </div>
                      <span class="endpoint-arrow">→</span>
                      <div class="route-endpoint">
                        <span class="endpoint-marker dest">B</span>
                        <span class="endpoint-text">{{ routePlanningDest?.address || '目的地' }}</span>
                      </div>
                    </div>
                    <!-- 路线策略选择 -->
                    <div class="route-policy-tabs">
                      <button
                        v-for="policy in routePolicyOptions"
                        :key="policy.value"
                        type="button"
                        class="route-policy-tab"
                        :class="{ active: routePlanningPolicy === policy.value }"
                        @click="changeRoutePolicy(policy.value)"
                      >
                        {{ policy.label }}
                      </button>
                    </div>
                  </div>
                  <!-- 地图容器 -->
                  <div class="route-planning-map-wrap">
                    <div id="route-planning-map-container" class="route-planning-map"></div>
                    <div v-if="routePlanningLoading" class="route-planning-loading">
                      <span class="material-symbols-outlined spinning">sync</span>
                      路线计算中...
                    </div>
                  </div>
                  <!-- 路线结果 -->
                  <div class="route-planning-results">
                    <div v-if="routePlanningResults.length === 0 && !routePlanningLoading" class="route-planning-empty">
                      暂无路线结果
                    </div>
                    <div
                      v-for="(route, idx) in routePlanningResults"
                      :key="idx"
                      class="route-result-card"
                      :class="{ selected: routePlanningSelectedIndex === idx }"
                      @click="selectRoutePlan(idx)"
                    >
                      <div class="route-result-header">
                        <span v-if="idx === 0" class="route-result-tag recommend">推荐</span>
                        <span v-else class="route-result-tag">方案 {{ idx + 1 }}</span>
                      </div>
                      <div class="route-result-info">
                        <span class="route-result-duration">{{ route.duration }}</span>
                        <span class="route-result-divider">|</span>
                        <span class="route-result-distance">{{ route.distance }}</span>
                      </div>
                      <div class="route-result-via">
                        途经：{{ route.via || '—' }}
                      </div>
                    </div>
                  </div>
                  <!-- 确认按钮 -->
                  <div class="route-planning-actions">
                    <button type="button" class="route-planning-cancel" @click="closeRoutePlanning">取消</button>
                    <button
                      type="button"
                      class="route-planning-confirm"
                      :disabled="routePlanningSelectedIndex === null"
                      @click="confirmRoutePlan"
                    >
                      <span class="material-symbols-outlined">check</span>
                      确认选择
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <!-- 地域属性说明 -->
            <div class="route-tip-box">
              <span class="material-symbols-outlined route-tip-icon">info</span>
              <div class="route-tip-content">
                <strong class="route-tip-title">地域属性说明：</strong><br />
                不同城市的地域属性将直接影响结算费率。例如：<strong class="route-tip-highlight">一线城市</strong>可能存在拥堵费或停车费溢价；<strong class="route-tip-highlight">偏远城市</strong>将产生长途返空补贴。请务必通过地图确认获取准确城市属性。
              </div>
            </div>
          </section>

          <section class="config-section">
            <div class="card panel labor-cost-panel">
              <div class="labor-cost-header">
                <div class="card-title-row">
                  <span class="material-symbols-outlined card-icon primary">engineering</span>
                  <h3 class="card-title">人工服务费</h3>
                </div>
                <div class="actions">
                  <el-button type="default" plain @click="restoreLaborDefaults">
                    恢复默认
                  </el-button>
                  <button type="button" class="add-row-btn" @click="addLaborItem">
                    <span class="material-symbols-outlined">add</span>
                    新增服务项
                  </button>
                </div>
              </div>
              <div class="labor-cost-table-wrap">
                <table class="labor-cost-table">
                  <thead>
                    <tr>
                      <th class="col-type">服务类型</th>
                      <th class="col-desc">服务描述</th>
                      <th class="col-unit">单位</th>
                      <th class="col-qty">数量</th>
                      <th class="col-price">单价 (¥)</th>
                      <th class="col-total">总价 (¥)</th>
                      <th class="col-action"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in laborCostItems" :key="row.id" class="labor-cost-row">
                      <td>
                        <template v-if="row.serviceType === '其它服务'">
                          <input
                            v-model.trim="row.customServiceType"
                            class="labor-input"
                            type="text"
                            placeholder="自定义服务类型"
                          />
                        </template>
                        <select
                          v-else
                          v-model="row.serviceType"
                          class="labor-input labor-select"
                          @change="onLaborServiceTypeChange(row)"
                        >
                          <option v-for="opt in laborServiceTypeOptions" :key="opt" :value="opt">{{ opt }}</option>
                        </select>
                      </td>
                      <td>
                        <input v-model.trim="row.serviceDesc" class="labor-input" type="text" placeholder="服务描述" />
                      </td>
                      <td class="unit-cell">人天</td>
                      <td>
                        <input v-model.number="row.quantity" class="labor-input labor-input-num" type="number" min="0" />
                      </td>
                      <td>
                        <input v-model.number="row.unitPrice" class="labor-input labor-input-num" type="number" min="0" placeholder="单价" />
                      </td>
                      <td class="total-cell">{{ formatMoney(laborRowTotal(row)) }}</td>
                      <td class="action-cell">
                        <button type="button" class="row-delete-btn" title="删除" @click="removeLaborItem(idx)">
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="packaging-section">
              <div class="card panel packaging-detail-panel">
                <div class="labor-cost-header">
                  <div class="card-title-row">
                    <span class="material-symbols-outlined card-icon primary">inventory_2</span>
                    <h3 class="card-title">包装耗材费</h3>
                  </div>
                  <div class="actions">
                    <button type="button" class="sync-equipment-btn" @click="syncPackagingFromEquipment">
                      <span class="material-symbols-outlined">sync</span>
                      从设备清单同步
                    </button>
                    <button type="button" class="add-row-btn" @click="addPackagingItem">
                      <span class="material-symbols-outlined">add</span>
                      新增条目
                    </button>
                  </div>
                </div>
                <div v-if="packagingValidationWarning" class="packaging-validation-alert">
                  <span class="material-symbols-outlined alert-icon">info</span>
                  {{ packagingValidationWarning }}
                </div>
                <div class="labor-cost-table-wrap">
                  <table class="labor-cost-table packaging-detail-table">
                    <thead>
                      <tr>
                        <th class="col-type">机架高度(U)</th>
                        <th class="col-desc">包装形式</th>
                        <th class="col-unit">单位</th>
                        <th class="col-qty">数量</th>
                        <th class="col-price">单价 (¥)</th>
                        <th class="col-total">总价 (¥)</th>
                        <th class="col-action"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="row in packagingItemsVisible" :key="row.id" class="labor-cost-row" :class="{ 'unknown-tier-row': row.tierIndex === -1 }">
                        <td>
                          <select
                            v-model.number="row.tierIndex"
                            class="labor-input labor-select packaging-tier-select"
                            :class="{ 'unknown-tier-select': row.tierIndex === -1 }"
                          >
                            <option v-if="row.tierIndex === -1" :value="-1" disabled>未知</option>
                            <option
                              v-for="(tier, ti) in packagingTiers"
                              :key="ti"
                              :value="ti"
                            >
                              {{ tier.range }}
                            </option>
                          </select>
                        </td>
                        <td>
                          <span class="labor-input labor-input-readonly">{{ row.tierIndex === -1 ? '请选择档位' : (packagingTiers[row.tierIndex]?.label ?? '—') }}</span>
                        </td>
                        <td class="unit-cell">台</td>
                        <td class="qty-cell">
                          <input
                            v-model.number="row.quantity"
                            class="labor-input labor-input-num"
                            type="number"
                            min="0"
                            @change="clampPackagingItemQuantity(getPackagingIndexById(row.id))"
                          />
                        </td>
                        <td class="price-cell">
                          <span class="labor-input labor-input-readonly labor-input-num">{{ packagingTiers[row.tierIndex]?.price ?? 0 }}</span>
                        </td>
                        <td class="total-cell">{{ formatMoney(packagingItemTotal(row)) }}</td>
                        <td class="action-cell">
                          <button type="button" class="row-delete-btn" title="删除" @click="removePackagingItem(getPackagingIndexById(row.id))">
                            <span class="material-symbols-outlined">delete</span>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                    <tfoot class="packaging-summary-row">
                      <tr>
                        <td colspan="3" class="summary-label">汇总</td>
                        <td class="qty-cell summary-qty">{{ packagingQuantityTotal }}</td>
                        <td class="price-cell">—</td>
                        <td class="total-cell summary-total">{{ formatMoney(packagingCost) }}</td>
                        <td class="action-cell"></td>
                      </tr>
                    </tfoot>
                  </table>
                </div>
                <div class="section-title-row packaging-tiers-title">
                  <span class="section-hint">根据设备高度自动匹配费率</span>
                </div>
                <div class="packaging-tiers">
                  <div
                    v-for="(tier, idx) in packagingTiers"
                    :key="idx"
                    class="tier-card"
                    @click.stop
                  >
                    <p class="tier-range">{{ tier.range }}</p>
                    <div class="tier-price-wrap">
                      <span class="tier-price-prefix">¥</span>
                      <input
                        v-model.number="tier.price"
                        type="number"
                        min="0"
                        step="1"
                        class="tier-price-input"
                        title="单价可编辑"
                        @click.stop
                        @change="clampTierPrice(idx)"
                      />
                    </div>
                    <p class="tier-label">{{ tier.label }}</p>
                  </div>
                </div>
              </div>
            </div>

            <div class="card panel logistics-panel">
              <div class="logistics-card-header">
                <div class="header-left">
                  <span class="material-symbols-outlined card-icon primary">local_shipping</span>
                  <h3 class="card-title">物流运输费</h3>
                </div>
              </div>
              <!-- 标签栏 -->
              <div class="logistics-tabs-container">
                <div class="logistics-tabs">
                  <button
                    type="button"
                    class="logistics-tab-btn"
                    :class="{ active: logisticsSubTab === 0 }"
                    @click="logisticsSubTab = 0"
                  >
                    车辆配送费
                  </button>
                  <button
                    type="button"
                    class="logistics-tab-btn"
                    :class="{ active: logisticsSubTab === 1 }"
                    @click="logisticsSubTab = 1"
                  >
                    人工搬运费
                  </button>
                  <button
                    type="button"
                    class="logistics-tab-btn"
                    :class="{ active: logisticsSubTab === 2 }"
                    @click="logisticsSubTab = 2"
                  >
                    同园区搬迁
                  </button>
                </div>
                <div v-if="logisticsSubTab === 0" class="logistics-header-actions">
                  <label class="split-batch-switch-label">
                    <span class="switch-label-text">拆分批次</span>
                    <el-switch v-model="logisticsSplitBatch" />
                  </label>
                  <button
                    v-if="logisticsSplitBatch"
                    type="button"
                    class="add-batch-btn"
                    @click="addLogisticsBatch"
                  >
                    <span class="material-symbols-outlined">add</span>
                    新增批次
                  </button>
                  <button
                    v-else
                    type="button"
                    class="add-row-btn"
                    @click="addLogisticsItem"
                  >
                    <span class="material-symbols-outlined">add</span>
                    新增条目
                  </button>
                </div>
                <button
                  v-else
                  type="button"
                  class="add-row-btn"
                  @click="logisticsSubTab === 1 ? addPackagingItem() : addSameParkItem()"
                >
                  <span class="material-symbols-outlined">add</span>
                  新增条目
                </button>
              </div>
              <div class="logistics-tab-content">
                <!-- 车辆配送费 -->
                <template v-if="logisticsSubTab === 0">
                  <!-- 拆分批次：卡片式布局，每个批次一张卡片 -->
                  <div v-if="logisticsSplitBatch" class="batch-cards-layout">
                    <div
                      v-for="(batch, batchIdx) in logisticsBatches"
                      :key="batch.id"
                      class="batch-card"
                      :class="{ active: activeBatchId === batch.id }"
                      @click="activeBatchId = batch.id"
                    >
                      <!-- 批次属性区域 -->
                      <div class="batch-card-top">
                        <div class="batch-card-fields">
                          <div class="batch-field">
                            <label class="batch-field-label">批次名称</label>
                            <input
                              type="text"
                              class="batch-field-input"
                              :value="batch.name"
                              @input="(e) => updateBatchField(batch.id, 'name', (e.target as HTMLInputElement).value)"
                              @click.stop
                            />
                          </div>
                          <div class="batch-field">
                            <label class="batch-field-label">预计日期</label>
                            <input
                              type="date"
                              class="batch-field-input"
                              :value="batch.date"
                              @input="(e) => updateBatchField(batch.id, 'date', (e.target as HTMLInputElement).value)"
                              @click.stop
                            />
                          </div>
                          <div class="batch-field batch-field-wide">
                            <label class="batch-field-label">批次备注</label>
                            <input
                              type="text"
                              class="batch-field-input"
                              placeholder="选填备注..."
                              :value="batch.desc"
                              @input="(e) => updateBatchField(batch.id, 'desc', (e.target as HTMLInputElement).value)"
                              @click.stop
                            />
                          </div>
                        </div>
                        <button
                          type="button"
                          class="batch-card-delete"
                          :disabled="logisticsBatches.length <= 1"
                          title="删除批次"
                          @click.stop="removeLogisticsBatch(batch.id)"
                        >
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </div>

                      <!-- 车型条目区域 -->
                      <div class="batch-card-items">
                        <div class="batch-card-items-header">
                          <span class="batch-card-items-title">
                            <span class="material-symbols-outlined">local_shipping</span>
                            运力配置
                          </span>
                          <button type="button" class="add-vehicle-btn" @click.stop="activeBatchId = batch.id; addLogisticsItem()">
                            <span class="material-symbols-outlined">add</span>
                            新增车型
                          </button>
                        </div>

                        <div class="labor-cost-table-wrap" @click.stop>
                          <table class="labor-cost-table batch-vehicle-table">
                            <thead>
                              <tr>
                                <th class="col-type">车型</th>
                                <th class="col-desc">运输路径</th>
                                <th class="col-qty">数量</th>
                                <th class="col-price">公里数</th>
                                <th class="col-price">公里价 (¥)</th>
                                <th class="col-total">小计 (¥)</th>
                                <th class="col-action"></th>
                              </tr>
                            </thead>
                            <tbody>
                              <tr v-if="batch.items.length === 0">
                                <td colspan="7" class="batch-card-empty-cell">暂无车型配置，请点击"新增车型"添加</td>
                              </tr>
                              <tr v-for="(row, idx) in batch.items" :key="row.id" class="labor-cost-row">
                                <td>
                                  <select
                                    v-model="row.vehicleId"
                                    class="labor-input"
                                    @change="onLogisticsVehicleChange(row)"
                                  >
                                    <option :value="null">请选择车型</option>
                                    <option
                                      v-for="v in vehicleOptions"
                                      :key="v.id"
                                      :value="v.id"
                                    >
                                      {{ v.vehicle_name || v.vehicle_category || `车型 #${v.id}` }}
                                    </option>
                                  </select>
                                </td>
                                <td>
                                  <div class="route-path-inline">
                                    <select
                                      v-model.number="row.routeOriginIndex"
                                      class="labor-input route-inline-select"
                                      :class="{ empty: row.routeOriginIndex == null }"
                                      :title="getRouteLocationAddress(row.routeOriginIndex) || '选择始发地'"
                                      @change="onLogisticsRoutePathChange(row)"
                                    >
                                      <option :value="null">始发地</option>
                                      <option
                                        v-for="(loc, i) in routeLocations"
                                        :key="'o-' + loc.id"
                                        :value="i"
                                      >
                                        {{ locationLabel(i) }}
                                      </option>
                                    </select>
                                    <span class="route-arrow">→</span>
                                    <select
                                      v-model.number="row.routeDestIndex"
                                      class="labor-input route-inline-select"
                                      :class="{ empty: row.routeDestIndex == null }"
                                      :title="getRouteLocationAddress(row.routeDestIndex) || '选择目的地'"
                                      @change="onLogisticsRoutePathChange(row)"
                                    >
                                      <option :value="null">目的地</option>
                                      <option
                                        v-for="(loc, i) in routeLocations"
                                        :key="'d-' + loc.id"
                                        :value="i"
                                      >
                                        {{ locationLabel(i) }}
                                      </option>
                                    </select>
                                    <button
                                      v-if="row.routeOriginIndex != null && row.routeDestIndex != null && row.routeOriginIndex !== row.routeDestIndex"
                                      type="button"
                                      class="route-map-btn-small"
                                      title="查看路线地图"
                                      @click.stop="openRoutePlanningMap(row)"
                                    >
                                      <span class="material-symbols-outlined">map</span>
                                    </button>
                                  </div>
                                </td>
                                <td>
                                  <input
                                    v-model.number="row.quantity"
                                    class="labor-input labor-input-num"
                                    type="number"
                                    min="0"
                                    @change="clampLogisticsItemQuantity(idx)"
                                  />
                                </td>
                                <td>
                                  <input
                                    v-model.number="row.km"
                                    class="labor-input labor-input-num"
                                    type="number"
                                    min="0"
                                    @change="clampLogisticsItemKm(idx)"
                                  />
                                </td>
                                <td>
                                  <input
                                    v-model.number="row.kmPrice"
                                    class="labor-input labor-input-num"
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    @change="clampLogisticsItemKmPrice(idx)"
                                  />
                                </td>
                                <td class="total-cell">{{ formatMoney(logisticsItemTotal(row)) }}</td>
                                <td class="action-cell">
                                  <button
                                    type="button"
                                    class="row-delete-btn"
                                    title="删除"
                                    @click.stop="activeBatchId = batch.id; removeLogisticsItem(idx)"
                                  >
                                    <span class="material-symbols-outlined">delete</span>
                                  </button>
                                </td>
                              </tr>
                            </tbody>
                          </table>
                        </div>
                      </div>

                      <!-- 批次小计 -->
                      <div class="batch-card-footer">
                        <span class="batch-card-footer-label">本批次费用</span>
                        <span class="batch-card-footer-total">¥ {{ formatMoney(calculateBatchTotal(batch)) }}</span>
                      </div>
                    </div>

                    <!-- 运力不足提醒 -->
                    <div v-if="vehicleCapacityCheck.hasVehicle && !vehicleCapacityCheck.sufficient" class="capacity-warning">
                      <span class="material-symbols-outlined capacity-warning-icon">warning</span>
                      <div class="capacity-warning-body">
                        <p class="capacity-warning-title">运力不足</p>
                        <p class="capacity-warning-desc">
                          设备清单总占用空间 <strong>{{ vehicleCapacityCheck.requiredU }}U</strong>，
                          当前车辆总可装载 <strong>{{ vehicleCapacityCheck.totalCapacityU }}U</strong>，
                          缺口 <strong>{{ vehicleCapacityCheck.shortage }}U</strong>。
                        </p>
                        <ul class="capacity-warning-list">
                          <li v-for="v in vehicleMinQuantities" :key="v.vehicleId">
                            <strong>{{ v.name }}</strong>（单车可装 {{ v.maxPerTrip }}U）：当前 {{ v.currentQty }} 辆，
                            <template v-if="v.currentQty < v.minQty">
                              <span class="capacity-short">建议至少 {{ v.minQty }} 辆</span>
                            </template>
                            <template v-else>已满足</template>
                          </li>
                        </ul>
                      </div>
                    </div>

                    <!-- 底部汇总 -->
                    <div class="batch-summary-bar">
                      <div class="batch-summary-stats">
                        <div class="summary-stat">
                          <span class="stat-label">批次数量</span>
                          <span class="stat-value">{{ logisticsBatches.length }} 个批次</span>
                        </div>
                        <div class="summary-stat">
                          <span class="stat-label">车辆总数</span>
                          <span class="stat-value">{{ logisticsBatchesVehicleCount }} 台</span>
                        </div>
                      </div>
                      <div class="batch-summary-total">
                        <span class="total-label">车辆配送费预估总计</span>
                        <span class="total-value">
                          <span class="total-currency">¥</span>
                          {{ formatMoney(logisticsBatchesTotal) }}
                        </span>
                      </div>
                    </div>
                  </div>

                <!-- 不拆分批次：仅显示运力配置表与汇总，不显示批次选择框 -->
                <div v-else class="logistics-flat-layout">
                  <div class="batch-vehicles-section">
                    <div class="batch-vehicles-header">
                      <h4 class="batch-vehicles-title">
                        <span class="material-symbols-outlined">local_shipping</span>
                        运力配置
                      </h4>
                      <button type="button" class="add-vehicle-btn" @click="addLogisticsItem">
                        <span class="material-symbols-outlined">add</span>
                        新增车型条目
                      </button>
                    </div>
                    <div class="batch-table-header">
                      <div class="col-vehicle">车型</div>
                      <div class="col-route">运输路径</div>
                      <div class="col-qty">数量</div>
                      <div class="col-km">公里数</div>
                      <div class="col-price">公里价</div>
                      <div class="col-total">小计(¥)</div>
                      <div class="col-action"></div>
                    </div>
                    <div v-if="logisticsItems.length > 0" class="batch-items-list">
                      <div v-for="(row, idx) in logisticsItems" :key="row.id" class="batch-vehicle-row">
                        <div class="batch-vehicle-card">
                          <div class="col-vehicle">
                            <div class="vehicle-cell">
                              <div class="vehicle-icon">
                                <span class="material-symbols-outlined">local_shipping</span>
                              </div>
                              <select
                                v-model="row.vehicleId"
                                class="vehicle-select"
                                @change="onLogisticsVehicleChange(row)"
                              >
                                <option :value="null">请选择车型</option>
                                <option
                                  v-for="v in vehicleOptions"
                                  :key="v.id"
                                  :value="v.id"
                                >
                                  {{ v.vehicle_name || v.vehicle_category || `车型 #${v.id}` }}
                                </option>
                              </select>
                            </div>
                          </div>
                          <div class="col-route">
                            <div class="route-path-inline">
                              <select
                                v-model.number="row.routeOriginIndex"
                                class="route-select"
                                :class="{ empty: row.routeOriginIndex == null }"
                                :title="getRouteLocationAddress(row.routeOriginIndex) || '选择始发地'"
                                @change="onLogisticsRoutePathChange(row)"
                              >
                                <option :value="null">始发地</option>
                                <option
                                  v-for="(loc, i) in routeLocations"
                                  :key="'o-' + loc.id"
                                  :value="i"
                                >
                                  {{ locationLabel(i) }}
                                </option>
                              </select>
                              <span class="route-arrow">→</span>
                              <select
                                v-model.number="row.routeDestIndex"
                                class="route-select"
                                :class="{ empty: row.routeDestIndex == null }"
                                :title="getRouteLocationAddress(row.routeDestIndex) || '选择目的地'"
                                @change="onLogisticsRoutePathChange(row)"
                              >
                                <option :value="null">目的地</option>
                                <option
                                  v-for="(loc, i) in routeLocations"
                                  :key="'d-' + loc.id"
                                  :value="i"
                                >
                                  {{ locationLabel(i) }}
                                </option>
                              </select>
                              <button
                                v-if="row.routeOriginIndex != null && row.routeDestIndex != null && row.routeOriginIndex !== row.routeDestIndex"
                                type="button"
                                class="route-map-btn-small"
                                title="查看路线地图"
                                @click="openRoutePlanningMap(row)"
                              >
                                <span class="material-symbols-outlined">map</span>
                              </button>
                            </div>
                            <span v-if="row.routeDistanceLoading" class="route-loading">测算中...</span>
                          </div>
                          <div class="col-qty">
                            <input
                              v-model.number="row.quantity"
                              class="num-input"
                              type="number"
                              min="0"
                              @change="clampLogisticsItemQuantity(idx)"
                            />
                          </div>
                          <div class="col-km">
                            <input
                              v-model.number="row.km"
                              class="num-input"
                              type="number"
                              min="0"
                              @change="clampLogisticsItemKm(idx)"
                            />
                          </div>
                          <div class="col-price">
                            <input
                              v-model.number="row.kmPrice"
                              class="num-input"
                              type="number"
                              min="0"
                              step="0.01"
                              @change="clampLogisticsItemKmPrice(idx)"
                            />
                          </div>
                          <div class="col-total">
                            <span class="total-value">{{ formatMoney(logisticsItemTotal(row)) }}</span>
                          </div>
                          <div class="col-action">
                            <button
                              type="button"
                              class="delete-btn"
                              title="删除"
                              @click="removeLogisticsItem(idx)"
                            >
                              <span class="material-symbols-outlined">delete</span>
                            </button>
                          </div>
                        </div>
                        <div class="batch-vehicle-formula">
                          <span>起步价: ¥{{ getStartPriceForVehicle(row.vehicleId) }}</span>
                          <span class="formula-dot">•</span>
                          <span>计算逻辑: {{ row.quantity }} × ({{ getStartPriceForVehicle(row.vehicleId) }} + {{ row.km }} × {{ row.kmPrice }})</span>
                        </div>
                      </div>
                    </div>
                    <div v-else class="batch-empty">
                      <span class="material-symbols-outlined">inventory_2</span>
                      <p>尚未添加车型配置</p>
                    </div>
                    <div v-if="distinctVehiclesInUse.length" class="vehicle-info-cards">
                      <div class="vehicle-info-cards-header">
                        <span class="section-hint">下方展示所选车型，起步价与公里价可在此调整</span>
                      </div>
                      <div class="vehicle-info-grid">
                        <div v-for="entry in distinctVehiclesInUse" :key="entry.vehicleId" class="vehicle-info-card">
                          <div class="vehicle-card-header">
                            <div class="vehicle-card-icon">
                              <span class="material-symbols-outlined">local_shipping</span>
                            </div>
                            <div class="vehicle-card-name">{{ entry.vehicle.vehicle_name || entry.vehicle.vehicle_category || '未命名车型' }}</div>
                          </div>
                          <div class="vehicle-card-specs">
                            <span class="vehicle-spec-label">可装1U(台):</span>
                            <span class="vehicle-spec-value">{{ entry.vehicle.server_1u ?? '—' }}</span>
                          </div>
                          <div class="vehicle-card-prices">
                            <div class="vehicle-price-item">
                              <span class="vehicle-price-label">起步价</span>
                              <div class="vehicle-price-input-wrap">
                                <span class="price-prefix">¥</span>
                                <input
                                  :value="getDisplayStartPrice(entry.vehicleId)"
                                  type="number"
                                  min="0"
                                  step="1"
                                  class="vehicle-price-input"
                                  @input="onVehicleStartPriceInput(entry.vehicleId, $event)"
                                />
                              </div>
                            </div>
                            <div class="vehicle-price-item">
                              <span class="vehicle-price-label">公里价</span>
                              <div class="vehicle-price-input-wrap">
                                <span class="price-prefix">¥</span>
                                <input
                                  :value="getDisplayKmPrice(entry.vehicleId)"
                                  type="number"
                                  min="0"
                                  step="0.01"
                                  class="vehicle-price-input"
                                  @input="onVehicleKmPriceInput(entry.vehicleId, $event)"
                                />
                              </div>
                            </div>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                  <!-- 运力不足提醒 -->
                  <div v-if="vehicleCapacityCheck.hasVehicle && !vehicleCapacityCheck.sufficient" class="capacity-warning">
                    <span class="material-symbols-outlined capacity-warning-icon">warning</span>
                    <div class="capacity-warning-body">
                      <p class="capacity-warning-title">运力不足</p>
                      <p class="capacity-warning-desc">
                        设备清单总占用空间 <strong>{{ vehicleCapacityCheck.requiredU }}U</strong>，
                        当前车辆总可装载 <strong>{{ vehicleCapacityCheck.totalCapacityU }}U</strong>，
                        缺口 <strong>{{ vehicleCapacityCheck.shortage }}U</strong>。
                      </p>
                      <ul class="capacity-warning-list">
                        <li v-for="v in vehicleMinQuantities" :key="v.vehicleId">
                          <strong>{{ v.name }}</strong>（单车可装 {{ v.maxPerTrip }}U）：当前 {{ v.currentQty }} 辆，
                          <template v-if="v.currentQty < v.minQty">
                            <span class="capacity-short">建议至少 {{ v.minQty }} 辆</span>
                          </template>
                          <template v-else>已满足</template>
                        </li>
                      </ul>
                    </div>
                  </div>

                  <div class="batch-summary-bar">
                    <div class="batch-summary-stats">
                      <div class="summary-stat">
                        <span class="stat-label">车辆总数</span>
                        <span class="stat-value">{{ logisticsBatchesVehicleCount }} 台</span>
                      </div>
                    </div>
                    <div class="batch-summary-total">
                      <span class="total-label">车辆配送费预估总计</span>
                      <span class="total-value">
                        <span class="total-currency">¥</span>
                        {{ formatMoney(logisticsBatchesTotal) }}
                      </span>
                    </div>
                  </div>
                </div>
              </template>
              <!-- 人工搬运费：与按U数梯度包装计费结构一致 -->
              <template v-else-if="logisticsSubTab === 1">
                <div class="labor-cost-table-wrap">
                  <table class="labor-cost-table packaging-detail-table">
                    <thead>
                      <tr>
                        <th class="col-type">机架高度(U)</th>
                        <th class="col-desc">包装形式</th>
                        <th class="col-unit">单位</th>
                        <th class="col-qty">数量</th>
                        <th class="col-price">单价 (¥)</th>
                        <th class="col-total">总价 (¥)</th>
                        <th class="col-action"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in manualHandlingItems" :key="row.id" class="labor-cost-row" :class="{ 'unknown-tier-row': row.tierIndex === -1 }">
                        <td>
                          <select
                            v-model.number="row.tierIndex"
                            class="labor-input labor-select packaging-tier-select"
                            :class="{ 'unknown-tier-select': row.tierIndex === -1 }"
                          >
                            <option v-if="row.tierIndex === -1" :value="-1" disabled>未知</option>
                            <option
                              v-for="(tier, ti) in manualHandlingTiers"
                              :key="ti"
                              :value="ti"
                            >
                              {{ tier.range }}
                            </option>
                          </select>
                        </td>
                        <td>
                          <span class="labor-input labor-input-readonly">{{ row.tierIndex === -1 ? '请选择档位' : (manualHandlingTiers[row.tierIndex]?.label ?? '—') }}</span>
                        </td>
                        <td class="unit-cell">台</td>
                        <td class="qty-cell">
                          <input
                            v-model.number="row.quantity"
                            class="labor-input labor-input-num"
                            type="number"
                            min="0"
                            @change="clampManualHandlingItemQuantity(idx)"
                          />
                        </td>
                        <td class="price-cell">
                          <span class="labor-input labor-input-readonly labor-input-num">{{ manualHandlingTiers[row.tierIndex]?.price ?? 0 }}</span>
                        </td>
                        <td class="total-cell">{{ formatMoney(manualHandlingItemTotal(row)) }}</td>
                        <td class="action-cell">
                          <button type="button" class="row-delete-btn" title="删除" @click="removeManualHandlingItem(idx)">
                            <span class="material-symbols-outlined">delete</span>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="section-title-row packaging-tiers-title">
                  <span class="section-hint">根据设备高度自动匹配费率</span>
                </div>
                <div class="packaging-tiers">
                  <div
                    v-for="(tier, idx) in manualHandlingTiers"
                    :key="'mh-' + idx"
                    class="tier-card"
                    @click.stop
                  >
                    <p class="tier-range">{{ tier.range }}</p>
                    <div class="tier-price-wrap">
                      <span class="tier-price-prefix">¥</span>
                      <input
                        v-model.number="tier.price"
                        type="number"
                        min="0"
                        step="1"
                        class="tier-price-input"
                        title="单价可编辑"
                        @click.stop
                        @change="clampManualHandlingTierPrice(idx)"
                      />
                    </div>
                    <p class="tier-label">{{ tier.label }}</p>
                  </div>
                </div>
              </template>
              <!-- 同园区搬迁：与按U数梯度包装计费结构一致 -->
              <template v-else-if="logisticsSubTab === 2">
                <div class="labor-cost-table-wrap">
                  <table class="labor-cost-table packaging-detail-table">
                    <thead>
                      <tr>
                        <th class="col-type">机架高度(U)</th>
                        <th class="col-desc">包装形式</th>
                        <th class="col-unit">单位</th>
                        <th class="col-qty">数量</th>
                        <th class="col-price">单价 (¥)</th>
                        <th class="col-total">总价 (¥)</th>
                        <th class="col-action"></th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, idx) in sameParkItems" :key="row.id" class="labor-cost-row">
                        <td>
                          <select
                            v-model.number="row.tierIndex"
                            class="labor-input labor-select packaging-tier-select"
                          >
                            <option
                              v-for="(tier, ti) in sameParkTiers"
                              :key="ti"
                              :value="ti"
                            >
                              {{ tier.range }}
                            </option>
                          </select>
                        </td>
                        <td>
                          <span class="labor-input labor-input-readonly">{{ sameParkTiers[row.tierIndex]?.label ?? '—' }}</span>
                        </td>
                        <td class="unit-cell">台</td>
                        <td class="qty-cell">
                          <input
                            v-model.number="row.quantity"
                            class="labor-input labor-input-num"
                            type="number"
                            min="0"
                            @change="clampSameParkItemQuantity(idx)"
                          />
                        </td>
                        <td class="price-cell">
                          <span class="labor-input labor-input-readonly labor-input-num">{{ sameParkTiers[row.tierIndex]?.price ?? 0 }}</span>
                        </td>
                        <td class="total-cell">{{ formatMoney(sameParkItemTotal(row)) }}</td>
                        <td class="action-cell">
                          <button type="button" class="row-delete-btn" title="删除" @click="removeSameParkItem(idx)">
                            <span class="material-symbols-outlined">delete</span>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div class="section-title-row packaging-tiers-title">
                  <span class="section-hint">根据设备高度自动匹配费率</span>
                </div>
                <div class="packaging-tiers">
                  <div
                    v-for="(tier, idx) in sameParkTiers"
                    :key="'sp-' + idx"
                    class="tier-card"
                    @click.stop
                  >
                    <p class="tier-range">{{ tier.range }}</p>
                    <div class="tier-price-wrap">
                      <span class="tier-price-prefix">¥</span>
                      <input
                        v-model.number="tier.price"
                        type="number"
                        min="0"
                        step="1"
                        class="tier-price-input"
                        title="单价可编辑"
                        @click.stop
                        @change="clampSameParkTierPrice(idx)"
                      />
                    </div>
                    <p class="tier-label">{{ tier.label }}</p>
                  </div>
                </div>
              </template>
              </div>
            </div>

            <div class="card panel value-added-panel">
              <div class="labor-cost-header">
                <div class="card-title-row">
                  <span class="material-symbols-outlined card-icon primary">add_task</span>
                  <h3 class="card-title">增值服务费</h3>
                </div>
                <button type="button" class="add-row-btn" @click="addValueAddedItem">
                  <span class="material-symbols-outlined">add</span>
                  新增服务项
                </button>
              </div>
              <div class="labor-cost-table-wrap">
                <table class="labor-cost-table value-added-table">
                  <thead>
                    <tr>
                      <th class="col-type">服务项名称</th>
                      <th class="col-desc">服务描述</th>
                      <th class="col-unit">单位</th>
                      <th class="col-qty">数量</th>
                      <th class="col-price">单价 (¥)</th>
                      <th class="col-total">总价 (¥)</th>
                      <th class="col-action"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in valueAddedItems" :key="row.id" class="labor-cost-row">
                      <td>
                        <input v-model.trim="row.itemName" class="labor-input" type="text" placeholder="服务项名称" />
                      </td>
                      <td>
                        <input v-model.trim="row.serviceDesc" class="labor-input" type="text" placeholder="服务描述" />
                      </td>
                      <td class="unit-cell">{{ row.unit ?? '台' }}</td>
                      <td>
                        <input v-model.number="row.quantity" class="labor-input labor-input-num" type="number" min="0" />
                      </td>
                      <td>
                        <input v-model.number="row.unitPrice" class="labor-input labor-input-num" type="number" min="0" />
                      </td>
                      <td class="total-cell">{{ formatMoney(valueAddedRowTotal(row)) }}</td>
                      <td class="action-cell">
                        <button type="button" class="row-delete-btn" title="删除" @click="removeValueAddedItem(idx)">
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <!-- 其他费用：专用设备租用、外部人工调用、专用设备采购 -->
            <div class="card panel other-cost-panel">
              <div class="other-cost-header">
                <div class="card-title-row">
                  <span class="material-symbols-outlined card-icon primary">payments</span>
                  <h3 class="card-title">其他费用</h3>
                </div>
                <div class="other-cost-tabs-row">
                  <div class="other-cost-tabs">
                    <button
                      type="button"
                      class="other-cost-tab"
                      :class="{ active: otherCostSubTab === 0 }"
                      @click="otherCostSubTab = 0"
                    >
                      专用设备租用
                    </button>
                    <button
                      type="button"
                      class="other-cost-tab"
                      :class="{ active: otherCostSubTab === 1 }"
                      @click="otherCostSubTab = 1"
                    >
                      外部人工调用
                    </button>
                    <button
                      type="button"
                      class="other-cost-tab"
                      :class="{ active: otherCostSubTab === 2 }"
                      @click="otherCostSubTab = 2"
                    >
                      专用设备采购
                    </button>
                  </div>
                  <button
                    type="button"
                    class="add-row-btn"
                    @click="otherCostSubTab === 0 ? addEquipmentRentalItem() : otherCostSubTab === 1 ? addExternalLaborItem() : addEquipmentPurchaseItem()"
                  >
                    <span class="material-symbols-outlined">add</span>
                    新增条目
                  </button>
                </div>
              </div>
              <div class="other-cost-table-wrap">
                <!-- 专用设备租用 -->
                <table v-if="otherCostSubTab === 0" class="labor-cost-table other-cost-table">
                  <thead>
                    <tr>
                      <th class="col-type">设备名称</th>
                      <th class="col-type">品牌</th>
                      <th class="col-desc">型号</th>
                      <th class="col-qty">数量</th>
                      <th class="col-unit">单位</th>
                      <th class="col-price">租用价格 (¥)</th>
                      <th class="col-total">总价 (¥)</th>
                      <th class="col-action"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in equipmentRentalItems" :key="row.id" class="labor-cost-row">
                      <td class="equipment-name-cell">
                        <div class="equipment-name-combobox">
                          <input
                            v-model.trim="row.equipmentName"
                            class="labor-input equipment-name-input"
                            type="text"
                            placeholder="设备名称"
                          />
                          <span
                            class="equipment-name-caret"
                            title="选择预设"
                            @click.stop="toggleEquipmentNameDropdown(row.id, row, $event)"
                          >
                            <span class="material-symbols-outlined">keyboard_arrow_down</span>
                          </span>
                        </div>
                      </td>
                      <td><input v-model.trim="row.brand" class="labor-input" type="text" placeholder="品牌" /></td>
                      <td><input v-model.trim="row.model" class="labor-input" type="text" placeholder="型号" /></td>
                      <td><input v-model.number="row.quantity" class="labor-input labor-input-num" type="number" min="0" /></td>
                      <td><input v-model.trim="row.unit" class="labor-input" type="text" placeholder="单位" /></td>
                      <td><input v-model.number="row.rentalPrice" class="labor-input labor-input-num" type="number" min="0" /></td>
                      <td class="total-cell">{{ formatMoney(equipmentRentalRowTotal(row)) }}</td>
                      <td class="action-cell">
                        <button type="button" class="row-delete-btn" title="删除" @click="removeEquipmentRentalItem(idx)">
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <!-- 外部人工调用 -->
                <table v-else-if="otherCostSubTab === 1" class="labor-cost-table other-cost-table">
                  <thead>
                    <tr>
                      <th class="col-type">人员类型</th>
                      <th class="col-desc">服务内容</th>
                      <th class="col-qty">数量</th>
                      <th class="col-unit">单位</th>
                      <th class="col-price">单价 (¥)</th>
                      <th class="col-total">总价 (¥)</th>
                      <th class="col-action"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in externalLaborItems" :key="row.id" class="labor-cost-row">
                      <td><input v-model.trim="row.personnelType" class="labor-input" type="text" placeholder="人员类型" /></td>
                      <td><input v-model.trim="row.serviceContent" class="labor-input" type="text" placeholder="服务内容" /></td>
                      <td><input v-model.number="row.quantity" class="labor-input labor-input-num" type="number" min="0" /></td>
                      <td><input v-model.trim="row.unit" class="labor-input" type="text" placeholder="单位" /></td>
                      <td><input v-model.number="row.unitPrice" class="labor-input labor-input-num" type="number" min="0" /></td>
                      <td class="total-cell">{{ formatMoney(externalLaborRowTotal(row)) }}</td>
                      <td class="action-cell">
                        <button type="button" class="row-delete-btn" title="删除" @click="removeExternalLaborItem(idx)">
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
                <!-- 专用设备采购 -->
                <table v-else class="labor-cost-table other-cost-table">
                  <thead>
                    <tr>
                      <th class="col-type">设备名称</th>
                      <th class="col-type">品牌</th>
                      <th class="col-desc">型号</th>
                      <th class="col-qty">数量</th>
                      <th class="col-unit">单位</th>
                      <th class="col-price">采购价格 (¥)</th>
                      <th class="col-total">总价 (¥)</th>
                      <th class="col-action"></th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr v-for="(row, idx) in equipmentPurchaseItems" :key="row.id" class="labor-cost-row">
                      <td class="equipment-name-cell">
                        <div class="equipment-name-combobox">
                          <input
                            v-model.trim="row.equipmentName"
                            class="labor-input equipment-name-input"
                            type="text"
                            placeholder="设备名称"
                          />
                          <span
                            class="equipment-name-caret"
                            title="选择预设"
                            @click.stop="toggleEquipmentNameDropdown(row.id, row, $event)"
                          >
                            <span class="material-symbols-outlined">keyboard_arrow_down</span>
                          </span>
                        </div>
                      </td>
                      <td><input v-model.trim="row.brand" class="labor-input" type="text" placeholder="品牌" /></td>
                      <td><input v-model.trim="row.model" class="labor-input" type="text" placeholder="型号" /></td>
                      <td><input v-model.number="row.quantity" class="labor-input labor-input-num" type="number" min="0" /></td>
                      <td><input v-model.trim="row.unit" class="labor-input" type="text" placeholder="单位" /></td>
                      <td><input v-model.number="row.purchasePrice" class="labor-input labor-input-num" type="number" min="0" /></td>
                      <td class="total-cell">{{ formatMoney(equipmentPurchaseRowTotal(row)) }}</td>
                      <td class="action-cell">
                        <button type="button" class="row-delete-btn" title="删除" @click="removeEquipmentPurchaseItem(idx)">
                          <span class="material-symbols-outlined">delete</span>
                        </button>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            <div class="card panel insurance-panel">
              <div class="card-title-row">
                <span class="material-symbols-outlined card-icon primary">security</span>
                <h3 class="card-title">设备保险费</h3>
              </div>
              <div class="insurance-row">
                <div class="insurance-total">
                  <label class="field-label">设备申报总价值 (可手动调整)</label>
                  <div class="input-with-prefix">
                    <span class="input-prefix">¥</span>
                    <input
                      :value="declaredValueInput !== null ? declaredValueInput : formattedDeclaredValue"
                      type="text"
                      inputmode="decimal"
                      class="field-input declared-value-input"
                      @input="onDeclaredValueInput"
                      @focus="onDeclaredValueFocus"
                      @blur="onDeclaredValueBlur"
                    />
                  </div>
                </div>
                <div class="insurance-rate-field">
                  <label class="field-label">费率配置 (‰)</label>
                  <div class="input-with-suffix">
                    <input v-model.number="insuranceRatePermille" type="number" min="0" step="0.1" class="field-input" />
                    <span class="input-suffix">‰</span>
                  </div>
                </div>
                <div class="insurance-premium">
                  <p class="field-label">保险费</p>
                  <p class="total-value">¥ {{ formatMoney(insuranceCost) }}</p>
                </div>
              </div>
            </div>
          </section>
        </template>
        <!-- 2. 设备清单管理 -->
        <template v-else-if="activeTab === 2">
          <!-- 导入区 -->
          <section class="overview-section card panel equipment-import-section">
            <div class="equipment-import-header">
              <div class="card-title-row">
                <span class="material-symbols-outlined card-icon primary">upload_file</span>
                <h3 class="card-title">设备清单导入</h3>
              </div>
              <div class="equipment-import-actions">
                <el-button type="success" class="download-template-btn" @click="onDownloadTemplate">
                  <span class="material-symbols-outlined btn-icon">download</span>
                  下载标准模板
                </el-button>
                <el-button v-if="equipmentList.length > 0 && equipmentList.some(r => r.model)" type="primary" :loading="isMatchingEquipment" @click="batchMatchEquipment">
                  <span class="material-symbols-outlined btn-icon">sync</span>
                  重新匹配
                </el-button>
              </div>
            </div>
            <div
              class="upload-zone equipment-upload-zone"
              :class="{ 'upload-zone-dragover': isEquipmentDragging }"
              @click="triggerEquipmentFileInput"
              @dragover.prevent="isEquipmentDragging = true"
              @dragleave.prevent="isEquipmentDragging = false"
              @drop.prevent="onEquipmentDrop"
            >
              <span class="material-symbols-outlined upload-icon equipment-upload-icon">upload_file</span>
              <div class="equipment-upload-text">
                <p class="upload-text">点击或拖拽 Excel/CSV 文件到此处上传</p>
                <p class="upload-hint">支持批量导入资产信息，系统将自动识别表头并匹配设备库</p>
              </div>
              <input
                ref="equipmentFileInputRef"
                type="file"
                class="upload-input-hidden"
                accept=".xls,.xlsx,.csv"
                @change="onEquipmentFileSelect"
              />
            </div>
          </section>

          <!-- 原始导入数据表格 -->
          <section v-if="importedOriginalData.length > 0" class="card panel eq-original-table-section">
            <div class="eq-original-table-header">
              <div class="card-title-row">
                <span class="material-symbols-outlined card-icon">table_view</span>
                <h3 class="card-title">原始导入数据</h3>
                <span class="eq-original-file-tag">{{ importedFileName }}</span>
                <span class="eq-original-count-tag">{{ importedOriginalData.length }} 行 × {{ importedOriginalHeaders.length }} 列</span>
              </div>
            </div>
            <div class="eq-original-table-wrap">
              <table class="tech-table eq-original-table">
                <thead>
                  <tr>
                    <th v-for="h in importedOriginalHeaders" :key="h">{{ h }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, ri) in importedOriginalData" :key="ri">
                    <td v-for="h in importedOriginalHeaders" :key="h">{{ row[h] || '' }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </section>

          <!-- 设备明细清单（转换后表格） -->
          <section class="equipment-list-section card panel">
            <div class="equipment-list-header">
              <div class="equipment-list-title-row">
                <h3 class="card-title equipment-list-title">设备明细清单</h3>
                <span class="inline-edit-tag">
                  <span class="inline-edit-dot"></span>
                  支持行内编辑
                </span>
                <span v-if="isMatchingEquipment" class="eq-matching-tag">
                  <span class="eq-matching-spinner"></span>
                  匹配中...
                </span>
              </div>
              <div class="equipment-header-actions">
                <select v-model="eqMatchDataSource" class="eq-source-select" title="匹配数据源">
                  <option value="datacenter">数据中心</option>
                  <option value="office">办公设备</option>
                  <option value="hybrid">全部</option>
                </select>
                <el-button type="primary" :loading="isMatchingEquipment" @click="batchMatchEquipment">
                  <span class="material-symbols-outlined btn-icon">sync</span>
                  手动匹配
                </el-button>
                <el-button type="danger" plain class="clear-list-btn" @click="clearEquipmentList">
                  <span class="material-symbols-outlined btn-icon">delete_sweep</span>
                  清空列表
                </el-button>
              </div>
            </div>
            <div class="equipment-table-wrap">
              <table class="tech-table equipment-table">
                <thead>
                  <tr>
                    <th class="col-brand eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('品牌', $event)">
                      <div class="eq-header-cell">
                        <span>品牌</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['品牌'] }">{{ getEqMappedOriginal('品牌') }}</span>
                      <!-- 映射下拉菜单 -->
                      <div v-if="eqActiveDropdown === '品牌'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['品牌']" @click.stop="clearEqMapping('品牌')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['品牌'] === oh }" @click.stop="selectEqOriginalHeader('品牌', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['品牌'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="col-model eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('型号', $event)">
                      <div class="eq-header-cell">
                        <span>型号</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['型号'] }">{{ getEqMappedOriginal('型号') }}</span>
                      <div v-if="eqActiveDropdown === '型号'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['型号']" @click.stop="clearEqMapping('型号')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['型号'] === oh }" @click.stop="selectEqOriginalHeader('型号', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['型号'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="col-match-model">匹配型号</th>
                    <th class="col-type eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('设备类型', $event)">
                      <div class="eq-header-cell">
                        <span>设备类型</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['设备类型'] }">{{ getEqMappedOriginal('设备类型') }}</span>
                      <div v-if="eqActiveDropdown === '设备类型'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['设备类型']" @click.stop="clearEqMapping('设备类型')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['设备类型'] === oh }" @click.stop="selectEqOriginalHeader('设备类型', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['设备类型'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="col-match-type">匹配设备类型</th>
                    <th class="col-u eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('机架高度(U)', $event)">
                      <div class="eq-header-cell">
                        <span>机架高度(U)</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['机架高度(U)'] }">{{ getEqMappedOriginal('机架高度(U)') }}</span>
                      <div v-if="eqActiveDropdown === '机架高度(U)'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['机架高度(U)']" @click.stop="clearEqMapping('机架高度(U)')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['机架高度(U)'] === oh }" @click.stop="selectEqOriginalHeader('机架高度(U)', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['机架高度(U)'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="col-qty eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('数量', $event)">
                      <div class="eq-header-cell">
                        <span>数量</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['数量'] }">{{ getEqMappedOriginal('数量') }}</span>
                      <div v-if="eqActiveDropdown === '数量'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['数量']" @click.stop="clearEqMapping('数量')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['数量'] === oh }" @click.stop="selectEqOriginalHeader('数量', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['数量'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="col-asset eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('资产编号(可选)', $event)">
                      <div class="eq-header-cell">
                        <span>资产编号</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['资产编号(可选)'] }">{{ getEqMappedOriginal('资产编号(可选)') }}</span>
                      <div v-if="eqActiveDropdown === '资产编号(可选)'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['资产编号(可选)']" @click.stop="clearEqMapping('资产编号(可选)')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['资产编号(可选)'] === oh }" @click.stop="selectEqOriginalHeader('资产编号(可选)', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['资产编号(可选)'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="eq-header-dropdown-wrap" @click="toggleEqHeaderDropdown('备注', $event)">
                      <div class="eq-header-cell">
                        <span>备注</span>
                        <span v-if="importedOriginalHeaders.length" class="material-symbols-outlined eq-dropdown-icon">expand_more</span>
                      </div>
                      <span v-if="importedOriginalHeaders.length" class="eq-mapped-source" :class="{ mapped: eqColumnMappings['备注'] }">{{ getEqMappedOriginal('备注') }}</span>
                      <div v-if="eqActiveDropdown === '备注'" class="eq-mapping-dropdown" @click.stop>
                        <div class="eq-dd-header"><span>选择对应列</span><button v-if="eqColumnMappings['备注']" @click.stop="clearEqMapping('备注')"><span class="material-symbols-outlined">close</span></button></div>
                        <div class="eq-dd-options">
                          <div v-for="oh in importedOriginalHeaders" :key="oh" class="eq-dd-option" :class="{ selected: eqColumnMappings['备注'] === oh }" @click.stop="selectEqOriginalHeader('备注', oh)">
                            <span class="material-symbols-outlined">{{ eqColumnMappings['备注'] === oh ? 'check_circle' : 'radio_button_unchecked' }}</span>
                            <span>{{ oh }}</span>
                          </div>
                        </div>
                      </div>
                    </th>
                    <th class="col-action">操作</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(row, idx) in equipmentList" :key="row.id" class="equipment-row" :class="{ 'eq-row-warning': row.matchRate > 0 && row.matchRate < 70, 'eq-row-error': row.model && !row.matchedModel && !isMatchingEquipment }">
                    <td>
                      <input v-model.trim="row.brand" class="inline-input" type="text" placeholder="品牌" />
                    </td>
                    <td>
                      <input v-model.trim="row.model" class="inline-input" type="text" placeholder="型号" />
                    </td>
                    <!-- 匹配型号 -->
                    <td class="col-match-model">
                      <div class="eq-match-cell">
                        <span
                          class="eq-matched-model"
                          :class="{
                            'high-match': row.matchRate >= 70,
                            'mid-match': row.matchRate >= 50 && row.matchRate < 70,
                            'low-match': row.matchRate > 0 && row.matchRate < 50,
                            'no-match': !row.matchedModel || row.matchRate === 0
                          }"
                          @click="openEqSearch(idx)"
                          title="点击修改匹配型号"
                        >
                          {{ row.matchedModel || '未匹配' }}
                        </span>
                        <span v-if="row.matchRate > 0" class="eq-match-badge" :class="{ high: row.matchRate >= 70, mid: row.matchRate >= 50 && row.matchRate < 70, low: row.matchRate < 50 }">
                          {{ row.matchRate }}%
                        </span>
                        <button v-if="row.matchedModel" class="eq-clear-match-btn" @click.stop="clearEqMatchResult(idx)" title="清空匹配">
                          <span class="material-symbols-outlined">close</span>
                        </button>
                      </div>
                    </td>
                    <td>
                      <input
                        v-model.trim="row.deviceType"
                        class="inline-input eq-device-type-input"
                        list="eq-device-type-list"
                        type="text"
                        placeholder="选择或输入"
                      />
                      <datalist id="eq-device-type-list">
                        <option v-for="opt in deviceTypeOptions" :key="opt" :value="opt" />
                      </datalist>
                    </td>
                    <!-- 匹配设备类型（仅显示三级分类） -->
                    <td class="col-match-type">
                      <span class="eq-match-type-text" :class="{ empty: !row.matchedDeviceType }">
                        {{ displayTertiaryDeviceType(row.matchedDeviceType) }}
                      </span>
                    </td>
                    <td>
                      <input v-model.number="row.rackU" class="inline-input text-center" type="number" min="0" @change="syncRackUByModel(row)" />
                    </td>
                    <td>
                      <input v-model.number="row.quantity" class="inline-input text-center" type="number" min="0" />
                    </td>
                    <td>
                      <input v-model.trim="row.assetNumber" class="inline-input" type="text" placeholder="可选" />
                    </td>
                    <td>
                      <input v-model.trim="row.remarks" class="inline-input" type="text" placeholder="输入备注..." />
                    </td>
                    <td class="col-action">
                      <button type="button" class="row-delete-btn" title="删除" @click="removeEquipmentRow(idx)">
                        <span class="material-symbols-outlined">delete</span>
                      </button>
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
            <div class="equipment-list-footer">
              <div class="equipment-stats">
                <div class="stat-item">
                  <span class="stat-label">设备总台数</span>
                  <span class="stat-value">{{ totalEquipmentCount }} <small class="stat-unit">台</small></span>
                </div>
                <div class="stat-item">
                  <span class="stat-label">总占用空间 (U)</span>
                  <span class="stat-value primary">{{ totalRackU }} <small class="stat-unit">U</small></span>
                </div>
              </div>
              <el-button class="add-row-btn" @click="addEquipmentRow">
                <span class="material-symbols-outlined btn-icon">add</span>
                手动新增一行
              </el-button>
            </div>
          </section>

          <!-- 设备匹配搜索弹窗 -->
          <Teleport to="body">
            <div v-if="eqSearchDialogVisible" class="eq-search-overlay" @click.self="closeEqSearch">
              <div class="eq-search-dialog">
                <div class="eq-search-dialog-header">
                  <h3>搜索设备型号</h3>
                  <button class="eq-search-close-btn" @click="closeEqSearch">
                    <span class="material-symbols-outlined">close</span>
                  </button>
                </div>
                <div class="eq-search-bar">
                  <input
                    ref="eqSearchInputRef"
                    v-model="eqSearchQuery"
                    class="eq-search-input"
                    type="text"
                    placeholder="输入设备型号搜索..."
                    @input="onEqSearchInput"
                    @keydown.enter="performEqSearch"
                  />
                  <div class="eq-search-source-selector">
                    <label><input type="radio" v-model="eqSearchSource" value="datacenter" @change="performEqSearch" /> 数据中心</label>
                    <label><input type="radio" v-model="eqSearchSource" value="office" @change="performEqSearch" /> 办公设备</label>
                    <label><input type="radio" v-model="eqSearchSource" value="hybrid" @change="performEqSearch" /> 全部</label>
                  </div>
                </div>
                <div class="eq-search-results">
                  <div v-if="eqSearchLoading" class="eq-search-loading">
                    <span class="eq-matching-spinner"></span> 搜索中...
                  </div>
                  <div v-else-if="eqSearchResults.length === 0 && eqSearchQuery" class="eq-search-empty">
                    未找到匹配的设备
                  </div>
                  <div
                    v-for="result in eqSearchResults"
                    :key="result.id || result.model_number"
                    class="eq-search-result-item"
                    @click="selectEqSearchResult(result)"
                  >
                    <div class="eq-result-main">
                      <span class="eq-result-manufacturer">{{ result.manufacturer || '-' }}</span>
                      <span class="eq-result-model">{{ result.model_number }}</span>
                    </div>
                    <div class="eq-result-meta">
                      <span v-if="result.primary_category" class="eq-result-category">{{ [result.primary_category, result.secondary_category, result.tertiary_category].filter(Boolean).join(' / ') }}</span>
                      <span v-if="result.device_price" class="eq-result-price">¥{{ Number(result.device_price).toLocaleString() }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Teleport>
        </template>

        <!-- 4. 生成报价（嵌入模式内联显示） -->
        <template v-else-if="activeTab === 4 && embedded">
          <div class="inline-quotation-view">
            <div class="inline-quotation-main">
              <!-- 文档预览区域 -->
              <div class="inline-quotation-preview">
                <div class="inline-quotation-toolbar">
                  <h3 class="inline-quotation-title">
                    <span class="material-symbols-outlined">description</span>
                    报价单预览
                    <span class="relocation-quotation-badge">A4 打印视图</span>
                  </h3>
                  <div class="inline-quotation-actions">
                    <div class="relocation-quotation-zoom">
                      <button type="button" class="relocation-quotation-zoom-btn" @click="quotationZoomOut" title="缩小">
                        <span class="material-symbols-outlined">remove</span>
                      </button>
                      <span class="relocation-quotation-zoom-level">{{ quotationZoomLevel }}%</span>
                      <button type="button" class="relocation-quotation-zoom-btn" @click="quotationZoomIn" title="放大">
                        <span class="material-symbols-outlined">add</span>
                      </button>
                    </div>
                    <button type="button" class="rq-action-btn rq-action-secondary" @click="handleQuotationPrint">
                      <span class="material-symbols-outlined">visibility</span>
                      预览
                    </button>
                    <button type="button" class="rq-action-btn rq-action-primary" @click="handleExportQuotationPdf">
                      <span class="material-symbols-outlined">picture_as_pdf</span>
                      导出 PDF
                    </button>
                  </div>
                </div>
                <div class="inline-quotation-scroll">
                  <div
                    ref="quotationContentRef"
                    class="relocation-quotation-paper"
                    :style="{ transform: `scale(${quotationZoomLevel / 100})` }"
                  >
                    <div class="relocation-quotation-paper-inner">
                      <!-- 文档头部 -->
                      <div class="rq-doc-header">
                        <div class="rq-doc-header-left">
                          <div class="rq-doc-logo" @click="triggerRelocationLogoUpload" title="点击上传自定义 Logo" style="cursor: pointer;">
                            <img v-if="relocationCustomLogoUrl" :src="relocationCustomLogoUrl" alt="公司Logo" style="max-height: 48px; max-width: 200px; object-fit: contain;" />
                            <template v-else>
                              <span class="material-symbols-outlined">rocket_launch</span>
                              <span class="rq-doc-logo-text">{{ QUOTATION_COMPANY.name }}</span>
                            </template>
                            <input
                              type="file"
                              ref="relocationLogoInputRef"
                              accept="image/*"
                              style="display: none;"
                              @change="handleRelocationLogoUpload"
                            />
                          </div>
                          <h2 class="rq-doc-title">数据中心搬迁服务报价单</h2>
                          <p class="rq-doc-subtitle">系统编号：{{ quotationData.meta.orderNo }}</p>
                        </div>
                        <div class="rq-doc-header-right">
                          <div class="rq-doc-status">PREVIEW</div>
                          <p class="rq-doc-date">打印日期：{{ quotationData.meta.date }}</p>
                        </div>
                      </div>

                      <!-- 信息网格 -->
                      <div class="rq-info-grid">
                        <div class="rq-info-block">
                          <h3 class="rq-info-label">报价方信息</h3>
                          <p class="rq-info-title">{{ quotationData.companyName }}</p>
                          <p class="rq-info-text">联系人：李经理</p>
                          <p class="rq-info-text">电话：400-888-9999</p>
                        </div>
                        <div class="rq-info-block">
                          <h3 class="rq-info-label">客户信息</h3>
                          <p class="rq-info-title">{{ quotationData.customer.name }}</p>
                          <p class="rq-info-text" v-for="(line, i) in quotationData.customer.locationLines" :key="i">{{ line }}</p>
                        </div>
                        <div class="rq-info-block">
                          <h3 class="rq-info-label">项目摘要</h3>
                          <p class="rq-info-text"><span class="rq-info-highlight">报价日期：</span>{{ quotationData.meta.date }}</p>
                          <p class="rq-info-text"><span class="rq-info-highlight">有效期至：</span>{{ quotationData.meta.validUntil || '30天内有效' }}</p>
                          <p class="rq-info-text"><span class="rq-info-highlight">币种：</span>人民币 (CNY)</p>
                        </div>
                      </div>

                      <!-- 报价表格 -->
                      <div class="rq-table-section">
                        <table class="rq-table">
                          <thead>
                            <tr>
                              <th class="rq-th">项目名称</th>
                              <th class="rq-th">服务描述</th>
                              <th class="rq-th">单位</th>
                              <th class="rq-th rq-th-right">数量</th>
                              <th class="rq-th rq-th-right">单价</th>
                              <th class="rq-th rq-th-right">小计</th>
                            </tr>
                          </thead>
                          <tbody>
                            <template v-for="(group, gIdx) in groupedQuotationItems" :key="gIdx">
                              <tr class="rq-group-row">
                                <td colspan="6" class="rq-group-cell">【{{ group.name }}】</td>
                              </tr>
                              <tr v-for="(item, idx) in group.items" :key="item.id" class="rq-item-row">
                                <td class="rq-td rq-td-name">{{ item.title }}</td>
                                <td class="rq-td rq-td-desc">{{ item.desc || '-' }}</td>
                                <td class="rq-td">{{ item.unit || '项' }}</td>
                                <td class="rq-td rq-td-right">{{ item.qty }}</td>
                                <td class="rq-td rq-td-right">¥{{ formatMoney(item.price) }}</td>
                                <td class="rq-td rq-td-right rq-td-total">¥{{ formatMoney(item.qty * item.price) }}</td>
                              </tr>
                            </template>
                          </tbody>
                        </table>
                      </div>

                      <!-- 汇总区域 -->
                      <div class="rq-summary">
                        <div class="rq-summary-box">
                          <div class="rq-summary-row">
                            <span class="rq-summary-label">项目小计:</span>
                            <span class="rq-summary-value">¥{{ formatMoney(quotationData.subTotal) }}</span>
                          </div>
                          <div class="rq-summary-row">
                            <span class="rq-summary-label">增值税 ({{ quotationData.taxRatePercent }}%):</span>
                            <span class="rq-summary-value">¥{{ formatMoney(quotationData.subTotal * quotationData.taxRatePercent / 100) }}</span>
                          </div>
                          <div class="rq-summary-divider"></div>
                          <div class="rq-summary-row rq-summary-total-row">
                            <span class="rq-summary-total-label">总计金额:</span>
                            <span class="rq-summary-total-value">¥{{ formatMoney(quotationData.finalTotal) }}</span>
                          </div>
                        </div>
                      </div>

                      <!-- 条款说明 -->
                      <div class="rq-terms">
                        <div class="rq-terms-col">
                          <p class="rq-terms-title">支付说明：</p>
                          <ul class="rq-terms-list">
                            <li>预付款项：合同签订后支付 30%</li>
                            <li>验收款项：项目完成并验收通过后支付 60%</li>
                            <li>质保金：验收通过半年后支付 10%</li>
                          </ul>
                        </div>
                        <div class="rq-terms-col">
                          <p class="rq-terms-title">备注说明：</p>
                          <p class="rq-terms-text">报价包含气垫车运输服务及夜间施工费用。若设备搬迁规模变动超过 10% 则需重新调整报价单。</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              <!-- 配置侧边栏 -->
              <aside class="inline-quotation-sidebar">
                <!-- 客户选择 -->
                <div class="rq-sidebar-section">
                  <label class="rq-sidebar-label">选择客户</label>
                  <div class="rq-sidebar-select-wrap">
                    <select v-model="quotationCustomerSelect" class="rq-sidebar-select">
                      <option value="default">{{ quotationData.customer.name }}</option>
                    </select>
                    <span class="material-symbols-outlined rq-sidebar-select-icon">expand_more</span>
                  </div>
                </div>

                <!-- 价格布局 -->
                <div class="rq-sidebar-section">
                  <label class="rq-sidebar-label">价格布局</label>
                  <div class="rq-sidebar-toggle-group">
                    <button type="button" class="rq-sidebar-toggle-btn" :class="{ active: quotationPriceLayout === 'with-tax' }" @click="quotationPriceLayout = 'with-tax'">含税报价</button>
                    <button type="button" class="rq-sidebar-toggle-btn" :class="{ active: quotationPriceLayout === 'without-tax' }" @click="quotationPriceLayout = 'without-tax'">未税报价</button>
                  </div>
                </div>

                <!-- 报价模板 -->
                <div class="rq-sidebar-section">
                  <label class="rq-sidebar-label">报价模板</label>
                  <div class="rq-sidebar-templates">
                    <div class="rq-sidebar-template" :class="{ active: quotationTemplate === 'classic' }" @click="quotationTemplate = 'classic'">
                      <div class="rq-template-preview rq-template-classic">
                        <div class="rq-tpl-bar"></div><div class="rq-tpl-line"></div><div class="rq-tpl-body"></div>
                      </div>
                      <p class="rq-template-name">经典商务</p>
                    </div>
                    <div class="rq-sidebar-template" :class="{ active: quotationTemplate === 'dark' }" @click="quotationTemplate = 'dark'">
                      <div class="rq-template-preview rq-template-dark">
                        <div class="rq-tpl-bar"></div><div class="rq-tpl-line"></div><div class="rq-tpl-body"></div>
                      </div>
                      <p class="rq-template-name">暗黑科技</p>
                    </div>
                  </div>
                </div>

                <!-- AI 建议 -->
                <div class="rq-ai-suggestion">
                  <div class="rq-ai-header">
                    <span class="material-symbols-outlined">auto_awesome</span>
                    <span class="rq-ai-title">AI 建议</span>
                  </div>
                  <p class="rq-ai-text">根据历史数据，该类项目的「项目管理」费率通常在 12%-15% 之间，当前设定略低，建议上调以覆盖风险。</p>
                </div>
              </aside>
            </div>
          </div>
        </template>

        <template v-else>
          <div class="placeholder-tab">
            <p>未知标签页</p>
          </div>
        </template>
      </div>

      <aside v-show="activeTab !== 4" class="right-dashboard">
        <div class="summary-card">
          <div class="glow-effect"></div>
          <h3 class="summary-title">
            <span class="material-symbols-outlined">calculate</span>
            实时报价总览
          </h3>

          <!-- 全局参数 -->
          <div class="global-params-section">
            <h4 class="section-title">全局参数</h4>
            <div class="global-params-grid">
              <div class="global-param-item">
                <label class="param-label">增值税率</label>
                <div class="input-with-suffix">
                  <input v-model.number="globalParams.vatRate" class="param-input" type="number" />
                  <span class="input-suffix">%</span>
                </div>
              </div>
              <div class="global-param-item">
                <label class="param-label">账期</label>
                <div class="input-with-suffix">
                  <input v-model.number="globalParams.paymentCycle" class="param-input" type="number" />
                  <span class="input-suffix">天</span>
                </div>
              </div>
              <div class="global-param-item">
                <label class="param-label">利润率</label>
                <div class="input-with-suffix">
                  <input v-model.number="globalParams.profitRate" class="param-input" type="number" min="0" />
                  <span class="input-suffix">%</span>
                </div>
              </div>
              <div class="global-param-item">
                <label class="param-label">年化资金成本率</label>
                <div class="input-with-suffix">
                  <input v-model.number="globalParams.fundingCostRate" class="param-input" type="number" min="0" />
                  <span class="input-suffix">%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 项目总额 + 成本小计 / 预估总毛利 -->
          <div class="summary-numbers">
            <div class="main-price highlight">
              <p class="price-label">项目总额</p>
              <div class="price-value">¥ {{ formatMoney(finalProjectAmount) }}</div>
              <div class="price-trend">
                <span class="material-symbols-outlined trend-icon">receipt_long</span>
                含利润率及增值税
              </div>
            </div>
            <div class="sub-prices">
              <div class="sub-price-item">
                <p class="sub-price-label">成本小计</p>
                <div class="sub-price-value">¥ {{ formatMoney(costSubtotal) }}</div>
                <div class="sub-price-note">包装+物流+人工+增值+保险</div>
              </div>
              <div class="sub-price-item">
                <p class="sub-price-label">预估总毛利</p>
                <div class="sub-price-value">¥ {{ formatMoney(totalGrossProfit) }}</div>
                <div class="sub-price-note">利润率: {{ totalMargin }}%</div>
              </div>
            </div>
          </div>

          <!-- 成本构成 -->
          <div class="breakdown-section">
            <h4 class="breakdown-title">成本构成</h4>
            <div class="breakdown-list">
              <div v-for="group in costBreakdown" :key="group.name" class="breakdown-group">
                <!-- 大类 -->
                <div class="breakdown-item breakdown-item-group">
                  <div class="breakdown-header">
                    <span class="breakdown-name">{{ group.name }}</span>
                    <span class="breakdown-amount">¥ {{ formatMoney(group.amount) }}</span>
                    <span class="breakdown-percent">{{ group.percent }}%</span>
                  </div>
                  <div class="breakdown-bar">
                    <div class="breakdown-fill" :style="{ width: group.percent + '%', backgroundColor: group.color }"></div>
                  </div>
                </div>
                <!-- 子项 -->
                <div v-if="group.children.length > 0" class="breakdown-children">
                  <div v-for="sub in group.children" :key="sub.name" class="breakdown-sub-item">
                    <span class="breakdown-sub-name">{{ sub.name }}</span>
                    <span class="breakdown-sub-amount">¥ {{ formatMoney(sub.amount) }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="summary-actions">
            <button type="button" class="btn-primary" @click="onGenerateQuote">
              生成正式报价单
              <span class="material-symbols-outlined">arrow_forward</span>
            </button>
            <button type="button" class="btn-secondary" @click="onExportExcel">
              导出 Excel 明细
              <span class="material-symbols-outlined">download</span>
            </button>
          </div>
        </div>
        <div class="warning-card">
          <span class="material-symbols-outlined warning-icon">warning</span>
          <div>
            <p class="warning-title">成本预警</p>
            <p class="warning-desc">当前保险费率 ({{ insuranceRatePermille }}‰) 略高于同行业 0.6‰ 的均值，建议核实资产残值评估。</p>
          </div>
        </div>
      </aside>
    </div>

    <!-- 设备名称预设下拉：Teleport 到 body，避免被表格 overflow 裁剪，置于最顶层 -->
    </template>
    <Teleport to="body">
      <div
        v-show="equipmentNameDropdownId !== null && equipmentNameDropdownRect"
        class="equipment-name-dropdown equipment-name-dropdown-fixed"
        :style="equipmentNameDropdownRect ? { left: equipmentNameDropdownRect.left + 'px', top: equipmentNameDropdownRect.top + 'px', width: equipmentNameDropdownRect.width + 'px' } : {}"
        @click.stop
      >
        <button
          v-for="opt in EQUIPMENT_NAME_PRESET_OPTIONS"
          :key="opt"
          type="button"
          class="equipment-name-option"
          @click="equipmentNameDropdownRowRef && selectEquipmentNamePreset(equipmentNameDropdownRowRef, opt)"
        >
          {{ opt }}
        </button>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import html2canvas from 'html2canvas'
import { jsPDF } from 'jspdf'
import * as XLSX from 'xlsx'

const props = withDefaults(defineProps<{
  embedded?: boolean
}>(), {
  embedded: false
})

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'
const AMAP_KEY = import.meta.env.VITE_AMAP_KEY as string || ''
const AMAP_SECURITY_KEY = import.meta.env.VITE_AMAP_SECURITY_KEY as string || ''
const hasAmapKey = computed(() => !!AMAP_KEY)

// 使用高德地图 JS API 2.0
function loadAMap(): Promise<typeof window.AMap> {
  return new Promise((resolve, reject) => {
    if (typeof (window as any).AMap !== 'undefined') {
      resolve((window as any).AMap)
      return
    }
    // 安全密钥必须在加载 SDK 前设置
    if (AMAP_SECURITY_KEY) {
      ;(window as any)._AMapSecurityConfig = { securityJsCode: AMAP_SECURITY_KEY }
    }
    const callbackName = 'onAMapReady_' + Date.now()
    ;(window as any)[callbackName] = () => {
      delete (window as any)[callbackName]
      resolve((window as any).AMap)
    }
    const script = document.createElement('script')
    script.type = 'text/javascript'
    script.src = `https://webapi.amap.com/maps?v=2.0&key=${encodeURIComponent(AMAP_KEY)}&callback=${callbackName}&plugin=AMap.Geocoder,AMap.PlaceSearch,AMap.Driving,AMap.ToolBar,AMap.Scale`
    script.onerror = () => {
      delete (window as any)[callbackName]
      reject(new Error('高德地图脚本加载失败'))
    }
    document.head.appendChild(script)
  })
}

const fileInputRef = ref<HTMLInputElement | null>(null)
const requirementDescription = ref('')
const uploadedFiles = ref<File[]>([])
const isDragging = ref(false)

const requirementBreakdown = ref([
  { serviceType: '现场勘察', serviceDesc: '两地机房环境调研', serviceDetail: '路由、电力、承重确认', deliverable: '勘察报告', unit: '人天', quantity: 4, unitPrice: '¥3,000', totalPrice: '¥12,000' },
  { serviceType: '设备搬迁', serviceDesc: '核心存储及服务器', serviceDetail: '上下架、标签粘贴、包装', deliverable: '设备清单', unit: '台', quantity: 120, unitPrice: '¥280', totalPrice: '¥33,600' },
  { serviceType: '物流运输', serviceDesc: '同城恒温气垫运输', serviceDetail: '专业搬运工、精细防护', deliverable: '签收单', unit: '车/次', quantity: 3, unitPrice: '¥3,500', totalPrice: '¥10,500' },
  { serviceType: '系统集成', serviceDesc: '线缆连接及标签管理', serviceDetail: '电源线、网线、光纤敷设', deliverable: '拓扑图', unit: 'U', quantity: 320, unitPrice: '¥50', totalPrice: '¥16,000' },
  { serviceType: '项目管理', serviceDesc: '全流程PM管理', serviceDetail: '协调、计划、进度控制', deliverable: '项目周报', unit: '项', quantity: 1, unitPrice: '¥14,350', totalPrice: '¥14,350' }
])

function triggerFileInput() {
  fileInputRef.value?.click()
}

function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (files?.length) {
    uploadedFiles.value = Array.from(files)
    ElMessage.success(`已选择 ${files.length} 个文件`)
  }
  input.value = ''
}

function onDrop(e: DragEvent) {
  isDragging.value = false
  const files = e.dataTransfer?.files
  if (files?.length) {
    uploadedFiles.value = Array.from(files)
    ElMessage.success(`已选择 ${files.length} 个文件`)
  }
}

function onAiAnalyze() {
  ElMessage.info('AI 智能分析需求功能待对接')
}

// 2. 设备清单管理
const deviceTypeOptions = ['服务器', '存储设备', '网络交换机', '安全设备']
let equipmentIdCounter = 0
function nextEquipmentId() {
  return `eq-${++equipmentIdCounter}`
}

interface EquipmentRow {
  id: string
  brand: string
  model: string
  matchedModel: string
  matchedManufacturer: string
  matchRate: number
  matchedPrice: number
  deviceType: string
  matchedDeviceType: string       // 匹配到的三级分类
  matchedPrimaryCategory: string
  matchedSecondaryCategory: string
  matchedTertiaryCategory: string
  rackU: number
  quantity: number
  assetNumber: string
  remarks: string
}

/** 从任意值解析为数字（支持 "2"、"2U"、2 等），用于机架高度(U)和数量，保证求和正确 */
function parseEquipmentNumber(v: unknown): number {
  if (v === null || v === undefined) return 0
  const n = Number(v)
  if (!Number.isNaN(n) && Number.isFinite(n)) return Math.max(0, n)
  const s = String(v).trim().replace(/[^\d.-]/g, '')
  const parsed = parseFloat(s)
  return Number.isNaN(parsed) ? 0 : Math.max(0, parsed)
}

function createEmptyRow(): EquipmentRow {
  return reactive({
    id: nextEquipmentId(),
    brand: '',
    model: '',
    matchedModel: '',
    matchedManufacturer: '',
    matchRate: 0,
    matchedPrice: 0,
    deviceType: '',
    matchedDeviceType: '',
    matchedPrimaryCategory: '',
    matchedSecondaryCategory: '',
    matchedTertiaryCategory: '',
    rackU: 0,
    quantity: 1,
    assetNumber: '',
    remarks: ''
  }) as EquipmentRow
}

const equipmentList = ref<EquipmentRow[]>([])

const equipmentFileInputRef = ref<HTMLInputElement | null>(null)
const isEquipmentDragging = ref(false)

// ---- 原始表格数据（导入时保留展示） ----
const importedOriginalHeaders = ref<string[]>([])
const importedOriginalData = ref<Record<string, any>[]>([])
const importedFileName = ref('')

// ---- 列映射（转换后表头 → 原始表头） ----
const equipmentStandardFields = ['品牌', '型号', '设备类型', '机架高度(U)', '数量', '资产编号(可选)', '备注']
const equipmentFieldMappings: Record<string, string[]> = {
  '品牌': ['品牌', '厂商', '厂商品牌', '制造商', '生产商', 'brand', 'manufacturer', 'vendor'],
  '型号': ['型号', '设备型号', '产品型号', '设备名称', 'model', 'product model'],
  '设备类型': ['设备类型', '设备分类', '类型', '分类', 'type', 'category'],
  '机架高度(U)': ['机架高度', 'U', 'U数', '高度(U)', 'rack u', 'rackU'],
  '数量': ['数量', '台数', '套数', 'quantity', 'count', 'qty'],
  '资产编号(可选)': ['资产编号', '编号', '序列号', '资产号', 'SN', 'asset', 'serial'],
  '备注': ['备注', '说明', '备注信息', 'remark', 'note']
}
const eqColumnMappings = ref<Record<string, string>>({})
const eqActiveDropdown = ref<string | null>(null)

function getEqMappedOriginal(targetHeader: string): string {
  return eqColumnMappings.value[targetHeader] || '未映射'
}

/** 匹配设备类型只显示三级分类（兼容 "一级/二级/三级" 格式，取最后一段） */
function displayTertiaryDeviceType(val: string | undefined): string {
  if (!val || !val.trim()) return '-'
  const parts = val.split(/\s*\/\s*/)
  return parts[parts.length - 1]?.trim() || val.trim()
}

function toggleEqHeaderDropdown(headerName: string, event: Event) {
  event.stopPropagation()
  if (eqActiveDropdown.value === headerName) {
    eqActiveDropdown.value = null
  } else {
    eqActiveDropdown.value = headerName
  }
}

function selectEqOriginalHeader(targetHeader: string, originalHeader: string) {
  eqColumnMappings.value[targetHeader] = originalHeader
  eqActiveDropdown.value = null
  remapEquipmentData(targetHeader)
}

function clearEqMapping(targetHeader: string) {
  delete eqColumnMappings.value[targetHeader]
  eqActiveDropdown.value = null
  remapEquipmentData(targetHeader)
}

function autoMapEquipmentHeaders() {
  const mappings: Record<string, string> = {}
  const lowerOrigHeaders = importedOriginalHeaders.value.map(h => h.toLowerCase().trim())

  for (const [standard, aliases] of Object.entries(equipmentFieldMappings)) {
    for (const alias of aliases) {
      const idx = lowerOrigHeaders.findIndex(h =>
        h === alias.toLowerCase() || h.includes(alias.toLowerCase()) || alias.toLowerCase().includes(h)
      )
      if (idx >= 0 && !Object.values(mappings).includes(importedOriginalHeaders.value[idx])) {
        mappings[standard] = importedOriginalHeaders.value[idx]
        break
      }
    }
  }
  eqColumnMappings.value = mappings
}

function remapEquipmentData(changedColumn?: string) {
  if (importedOriginalData.value.length === 0) return

  // 按行映射原始数据 → equipmentList
  for (let i = 0; i < equipmentList.value.length; i++) {
    const origRow = importedOriginalData.value[i]
    if (!origRow) continue
    const row = equipmentList.value[i]

    const fieldToKey: Record<string, keyof EquipmentRow> = {
      '品牌': 'brand', '型号': 'model', '设备类型': 'deviceType',
      '机架高度(U)': 'rackU', '数量': 'quantity', '资产编号(可选)': 'assetNumber', '备注': 'remarks'
    }

    const fields = changedColumn ? [changedColumn] : equipmentStandardFields
    for (const field of fields) {
      const origHeader = eqColumnMappings.value[field]
      const key = fieldToKey[field]
      if (!key) continue
      if (origHeader && origRow[origHeader] !== undefined) {
        const val = String(origRow[origHeader]).trim()
        if (key === 'rackU' || key === 'quantity') {
          ;(row as any)[key] = parseEquipmentNumber(origRow[origHeader])
        } else if (key === 'deviceType') {
          // 优先使用映射列的值（可匹配预设选项或保留原文），空值不硬置
          const matched = deviceTypeOptions.find(opt =>
            val.includes(opt) || opt.includes(val)
          )
          row.deviceType = matched || val || ''
        } else {
          ;(row as any)[key] = val
        }
      } else if (!origHeader) {
        // 映射被清除时清空对应字段（设备类型与其它文本列一致，不硬置为「服务器」）
        if (key === 'rackU' || key === 'quantity') {
          ;(row as any)[key] = 0
        } else if (key === 'deviceType') {
          row.deviceType = ''
        } else {
          ;(row as any)[key] = ''
        }
      }
    }
  }
}

// 设备总台数：对「数量」列求和（使用统一数字解析，避免字符串导致不求和）
const totalEquipmentCount = computed(() => {
  return equipmentList.value.reduce((sum, row) => sum + parseEquipmentNumber(row.quantity), 0)
})
// 总占用空间(U)：对每行的「机架高度(U)×数量」求和（同上，保证 rackU 按数字参与计算）
const totalRackU = computed(() => {
  return equipmentList.value.reduce((sum, row) => sum + parseEquipmentNumber(row.rackU) * parseEquipmentNumber(row.quantity), 0)
})

function onDownloadTemplate() {
  // 生成标准模板
  const ws = XLSX.utils.aoa_to_sheet([equipmentStandardFields])
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '设备清单')
  XLSX.writeFile(wb, '搬迁设备清单模板.xlsx')
  ElMessage.success('模板下载成功')
}

function triggerEquipmentFileInput() {
  equipmentFileInputRef.value?.click()
}

function parseEquipmentExcel(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })
      if (!workbook.SheetNames?.length) {
        ElMessage.error('Excel 文件中没有找到工作表')
        return
      }
      const sheetName = workbook.SheetNames[0]
      const worksheet = workbook.Sheets[sheetName]
      if (!worksheet || !worksheet['!ref']) {
        ElMessage.error('工作表为空')
        return
      }
      const range = XLSX.utils.decode_range(worksheet['!ref'])

      // 提取表头
      const headers: string[] = []
      for (let c = range.s.c; c <= range.e.c; c++) {
        const cellAddr = XLSX.utils.encode_cell({ r: range.s.r, c })
        const cell = worksheet[cellAddr]
        headers.push(cell?.v !== undefined && cell?.v !== null ? String(cell.v).trim() : `列${c + 1}`)
      }

      // 提取数据
      const rows: Record<string, any>[] = []
      for (let r = range.s.r + 1; r <= range.e.r; r++) {
        const row: Record<string, any> = {}
        let hasData = false
        for (let c = range.s.c; c <= range.e.c; c++) {
          const cellAddr = XLSX.utils.encode_cell({ r, c })
          const cell = worksheet[cellAddr]
          const header = headers[c - range.s.c]
          const val = cell?.v !== undefined && cell?.v !== null ? String(cell.v).trim() : ''
          row[header] = val
          if (val) hasData = true
        }
        if (hasData) rows.push(row)
      }

      if (rows.length === 0) {
        ElMessage.warning('Excel 文件中无有效数据行')
        return
      }

      // 保存原始数据
      importedOriginalHeaders.value = headers
      importedOriginalData.value = rows
      importedFileName.value = file.name

      // 自动映射表头
      autoMapEquipmentHeaders()

      // 生成设备行
      equipmentList.value = rows.map(origRow => {
        const row = createEmptyRow()
        // 按映射填充
        for (const [standard, key] of Object.entries({
          '品牌': 'brand', '型号': 'model', '设备类型': 'deviceType',
          '机架高度(U)': 'rackU', '数量': 'quantity', '资产编号(可选)': 'assetNumber', '备注': 'remarks'
        } as Record<string, string>)) {
          const origHeader = eqColumnMappings.value[standard]
            if (origHeader && origRow[origHeader] !== undefined) {
            const val = String(origRow[origHeader]).trim()
            if (key === 'rackU' || key === 'quantity') {
              ;(row as any)[key] = parseEquipmentNumber(origRow[origHeader])
            } else if (key === 'deviceType') {
              const matched = deviceTypeOptions.find(opt => val.includes(opt) || opt.includes(val))
              ;(row as any)[key] = matched || val || ''
            } else {
              ;(row as any)[key] = val
            }
          }
        }
        return row
      })

      ElMessage.success(`成功导入 ${rows.length} 条设备记录`)

      // 自动执行批量匹配
      batchMatchEquipment()
    } catch (err: any) {
      console.error('Excel 解析失败:', err)
      ElMessage.error('Excel 解析失败: ' + (err.message || '未知错误'))
    }
  }
  reader.readAsArrayBuffer(file)
}

function onEquipmentFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) parseEquipmentExcel(file)
  input.value = ''
}

function onEquipmentDrop(e: DragEvent) {
  isEquipmentDragging.value = false
  const file = e.dataTransfer?.files?.[0]
  if (file) parseEquipmentExcel(file)
}

function clearEquipmentList() {
  equipmentList.value = []
  importedOriginalHeaders.value = []
  importedOriginalData.value = []
  importedFileName.value = ''
  eqColumnMappings.value = {}
  ElMessage.success('已清空列表')
}

function addEquipmentRow() {
  equipmentList.value.push(createEmptyRow())
}

function removeEquipmentRow(index: number) {
  equipmentList.value.splice(index, 1)
  if (importedOriginalData.value.length > index) {
    importedOriginalData.value.splice(index, 1)
  }
}

// ---- 设备匹配逻辑 ----
const eqMatchDataSource = ref<'datacenter' | 'office' | 'hybrid'>('datacenter')
const isMatchingEquipment = ref(false)

async function batchMatchEquipment() {
  const list = equipmentList.value.filter(r => r.model.trim())
  if (list.length === 0) return
  isMatchingEquipment.value = true

  try {
    const items = list.map(r => ({
      manufacturer: r.brand || '',
      model: r.model,
      category: r.deviceType || '',
      source: eqMatchDataSource.value
    }))

    const resp = await axios.post(`${API_URL}/bulk-match/`, { items })
    const results = resp.data as any[]

    for (let i = 0; i < results.length && i < list.length; i++) {
      const result = results[i]
      const row = list[i]
      if (result.matched_model) {
        row.matchedModel = result.matched_model
        row.matchedManufacturer = result.manufacturer || ''
        row.matchRate = Math.round(result.match_rate || 0)
        row.matchedPrice = result.device_price || 0
        row.matchedPrimaryCategory = result.primary_category || ''
        row.matchedSecondaryCategory = result.secondary_category || ''
        row.matchedTertiaryCategory = result.tertiary_category || ''
        row.matchedDeviceType = result.tertiary_category || ''
        // 从匹配结果填充机架高度(U)
        if (result.rack_height_u != null) {
          row.rackU = parseEquipmentNumber(result.rack_height_u)
        }
      } else {
        // 明确标记未匹配
        row.matchedModel = ''
        row.matchRate = 0
        row.matchedDeviceType = ''
      }
    }

    const matchedCount = list.filter(r => r.matchedModel).length
    ElMessage.success(`匹配完成：${matchedCount}/${list.length} 条设备匹配成功`)
  } catch (err: any) {
    console.error('批量匹配失败:', err)
    ElMessage.error('批量匹配失败: ' + (err.response?.data?.detail || err.message || ''))
  } finally {
    isMatchingEquipment.value = false
  }
}

// ---- 搜索弹窗（修改匹配型号） ----
const eqSearchDialogVisible = ref(false)
const eqSearchQuery = ref('')
const eqSearchResults = ref<any[]>([])
const eqSearchLoading = ref(false)
const eqSearchActiveIndex = ref(-1)
const eqSearchSource = ref<'datacenter' | 'office' | 'hybrid'>('datacenter')
const eqSearchInputRef = ref<HTMLInputElement | null>(null)
let eqSearchDebounce: ReturnType<typeof setTimeout> | null = null

function openEqSearch(index: number) {
  eqSearchActiveIndex.value = index
  const row = equipmentList.value[index]
  eqSearchQuery.value = row.model || ''
  eqSearchResults.value = []
  eqSearchSource.value = eqMatchDataSource.value  // 同步主选择器的数据源
  eqSearchDialogVisible.value = true
  nextTick(() => {
    eqSearchInputRef.value?.focus()
    if (eqSearchQuery.value) performEqSearch()
  })
}

function closeEqSearch() {
  eqSearchDialogVisible.value = false
  eqSearchActiveIndex.value = -1
  eqSearchQuery.value = ''
  eqSearchResults.value = []
}

function onEqSearchInput() {
  if (eqSearchDebounce) clearTimeout(eqSearchDebounce)
  eqSearchDebounce = setTimeout(() => {
    performEqSearch()
  }, 300)
}

async function performEqSearch() {
  if (!eqSearchQuery.value.trim()) {
    eqSearchResults.value = []
    return
  }
  eqSearchLoading.value = true
  try {
    const resp = await axios.get(`${API_URL}/devices/search/`, {
      params: { model: eqSearchQuery.value.trim(), source: eqSearchSource.value, limit: 20, offset: 0 }
    })
    eqSearchResults.value = resp.data?.data || resp.data || []
  } catch (err) {
    console.error('搜索失败:', err)
  } finally {
    eqSearchLoading.value = false
  }
}

function selectEqSearchResult(result: any) {
  const idx = eqSearchActiveIndex.value
  if (idx < 0 || idx >= equipmentList.value.length) return

  const clickedRow = equipmentList.value[idx]
  const originalModel = clickedRow.model  // 当前行的原始型号

  // 找到所有具有相同原始型号的行，统一应用手动匹配结果
  const sameModelIndexes: number[] = []
  equipmentList.value.forEach((item, i) => {
    if (item.model && item.model === originalModel) {
      sameModelIndexes.push(i)
    }
  })

  // 如果没有找到同型号行（不应该发生），至少更新当前行
  if (sameModelIndexes.length === 0) {
    sameModelIndexes.push(idx)
  }

  const matchedModelStr = (result.model_number || '').toUpperCase().replace(/[\s\-_]/g, '')

  // 更新所有同型号行（匹配设备类型只显示三级分类）
  for (const i of sameModelIndexes) {
    const row = equipmentList.value[i]
    row.matchedModel = result.model_number || ''
    row.matchedManufacturer = result.manufacturer || ''
    row.matchedPrice = result.device_price || 0
    row.matchedPrimaryCategory = result.primary_category || ''
    row.matchedSecondaryCategory = result.secondary_category || ''
    row.matchedTertiaryCategory = result.tertiary_category || ''
    row.matchedDeviceType = result.tertiary_category || ''

    // 从搜索结果填充机架高度(U)
    if (result.rack_height_u != null) {
      row.rackU = parseEquipmentNumber(result.rack_height_u)
    }

    // 计算匹配度
    const origNorm = (row.model || '').toUpperCase().replace(/[\s\-_]/g, '')
    if (origNorm === matchedModelStr) {
      row.matchRate = 100
    } else if (matchedModelStr.includes(origNorm) || origNorm.includes(matchedModelStr)) {
      row.matchRate = 90
    } else {
      row.matchRate = 80
    }
  }

  // 将手动调整保存到后端（写入 manual_matching_override 表），
  // 这样后续的批量匹配也会使用此覆盖结果
  saveEqManualAdjustment(clickedRow.brand, originalModel, result)

  const count = sameModelIndexes.length
  if (count > 1) {
    ElMessage.success(`已将匹配结果应用到所有 ${count} 条「${originalModel}」记录`)
  }

  closeEqSearch()
}

/** 保存手动匹配覆盖到后端 */
async function saveEqManualAdjustment(originalManufacturer: string, originalModel: string, searchResult: any) {
  const adjustment = {
    original_manufacturer: originalManufacturer || '',
    original_model: originalModel,
    matched_manufacturer: searchResult.manufacturer || originalManufacturer || '',
    matched_model_number: searchResult.model_number || '',
    device_price: searchResult.device_price || null,
    primary_category: searchResult.primary_category || '',
    secondary_category: searchResult.secondary_category || '',
    tertiary_category: searchResult.tertiary_category || '',
    device_category: searchResult.tertiary_category || '',
    data_source: eqMatchDataSource.value
  }

  try {
    await axios.post(`${API_URL}/manual-matching-override/batch`, [adjustment])
    console.log('手动匹配覆盖已保存:', adjustment)
  } catch (err) {
    console.warn('手动匹配覆盖保存失败（不影响当前操作）:', err)
  }
}

function clearEqMatchResult(index: number) {
  const row = equipmentList.value[index]
  row.matchedModel = ''
  row.matchedManufacturer = ''
  row.matchRate = 0
  row.matchedPrice = 0
  row.matchedDeviceType = ''
  row.matchedPrimaryCategory = ''
  row.matchedSecondaryCategory = ''
  row.matchedTertiaryCategory = ''
}

/** 手动修改某行的机架高度(U)后，同步所有匹配型号相同的行 */
function syncRackUByModel(row: EquipmentRow) {
  const model = row.matchedModel
  if (!model) return
  for (const r of equipmentList.value) {
    if (r !== row && r.matchedModel === model) {
      r.rackU = row.rackU
    }
  }
}

// 关闭下拉菜单（点击页面其他位置）
function onDocClickEquipment(e: MouseEvent) {
  if (eqActiveDropdown.value) {
    const target = e.target as HTMLElement
    if (!target.closest('.eq-header-dropdown-wrap')) {
      eqActiveDropdown.value = null
    }
  }
}
onMounted(() => document.addEventListener('click', onDocClickEquipment))
onUnmounted(() => document.removeEventListener('click', onDocClickEquipment))

const activeTab = ref(3)
const insuranceRatePermille = ref(6)
const declaredValue = ref(0)
/** 设备申报总价值输入框编辑态：非 null 时显示该字符串，失焦后解析为 declaredValue 并置为 null */
const declaredValueInput = ref<string | null>(null)

/** 从设备明细清单自动计算设备申报总价值：匹配价格 × 数量 的总和 */
const equipmentTotalDeclaredValue = computed(() => {
  return equipmentList.value.reduce((sum, row) => {
    const price = Number(row.matchedPrice) || 0
    const qty = parseEquipmentNumber(row.quantity)
    return sum + price * qty
  }, 0)
})

// 设备清单变更时自动同步申报总价值
watch(equipmentTotalDeclaredValue, (newVal) => {
  declaredValue.value = Math.round(newVal * 100) / 100
})

// 车辆与物流：从机房搬迁车型数据动态拉取
const vehicleOptions = ref<Array<{ id: number; vehicle_name?: string; vehicle_category?: string; server_1u?: string; start_price?: string; km_price?: string }>>([])

/** 解析后台起步价/公里价：若为区间如 "4-5" 取最大值 5，单值则取该值 */
function parseRangeToMax(str: string | null | undefined): number {
  if (str == null || String(str).trim() === '') return 0
  const s = String(str).trim()
  const parts = s.split(/[-－~]\s*/).map((p) => p.replace(/[^\d.]/g, '').trim()).filter(Boolean)
  if (parts.length === 0) {
    const single = Number(s.replace(/[^\d.]/g, ''))
    return isNaN(single) ? 0 : Math.max(0, single)
  }
  const nums = parts.map((p) => Number(p)).filter((n) => !isNaN(n))
  if (nums.length === 0) return 0
  return Math.max(...nums)
}

interface LogisticsItem {
  id: string
  vehicleId: number | null
  routeOriginIndex: number | null
  routeDestIndex: number | null
  quantity: number
  km: number
  kmPrice: number
  routeDistanceLoading?: boolean
}

// 批次接口
interface LogisticsBatch {
  id: string
  name: string
  date: string
  desc: string
  items: LogisticsItem[]
}

let logisticsIdCounter = 0
function nextLogisticsId() {
  return `log-${++logisticsIdCounter}`
}

let batchIdCounter = 0
function nextBatchId() {
  return `batch-${++batchIdCounter}`
}

function createDefaultLogisticsItem(): LogisticsItem {
  const first = vehicleOptions.value[0]
  const vehicleId = first?.id ?? null
  const kmPrice = first ? parseRangeToMax(first.km_price) : 0
  return { id: nextLogisticsId(), vehicleId, routeOriginIndex: null, routeDestIndex: null, quantity: 1, km: 0, kmPrice }
}

function createDefaultBatch(): LogisticsBatch {
  return {
    id: nextBatchId(),
    name: `批次 ${logisticsBatches.value.length + 1}`,
    date: new Date().toISOString().split('T')[0],
    desc: '',
    items: [createDefaultLogisticsItem()]
  }
}
/** 运输路径展示文案：始发地->目的地 */
function logisticsRoutePathLabel(row: LogisticsItem): string {
  const o = row.routeOriginIndex
  const d = row.routeDestIndex
  if (o == null || d == null) return '请选择'
  return `${locationLabel(o)}→${locationLabel(d)}`
}
/** 根据搬迁路径下标返回该地点的详细地址（用于悬停提示） */
function getRouteLocationAddress(index: number | null): string {
  if (index == null) return ''
  const loc = routeLocations.value[index]
  if (!loc) return ''
  const parts = [loc.address, loc.city].filter(Boolean)
  if (loc.coords) parts.push(`坐标: ${loc.coords}`)
  return parts.length ? parts.join(' · ') : locationLabel(index)
}
// 批次列表（默认1个批次）
const logisticsBatches = ref<LogisticsBatch[]>([
  {
    id: nextBatchId(),
    name: '第一批次',
    date: new Date().toISOString().split('T')[0],
    desc: '',
    items: [{ id: nextLogisticsId(), vehicleId: null, routeOriginIndex: null, routeDestIndex: null, quantity: 1, km: 0, kmPrice: 0 }]
  }
])
const activeBatchId = ref<string>(logisticsBatches.value[0]?.id ?? '')

/** 拆分批次开关：开时显示批次侧栏与批次选择，关时不拆分批次、不显示批次选择框 */
const logisticsSplitBatch = ref(false)

watch(logisticsSplitBatch, (on) => {
  if (!on && logisticsBatches.value.length) {
    // 合并所有批次条目到第一个批次，仅保留一个批次
    const first = logisticsBatches.value[0]
    const restItems = logisticsBatches.value.slice(1).flatMap((b) => b.items)
    first.items = [...first.items, ...restItems]
    logisticsBatches.value = [{ ...first, items: first.items }]
    activeBatchId.value = first.id
  }
})

// 当前激活的批次
const currentBatch = computed(() => {
  return logisticsBatches.value.find(b => b.id === activeBatchId.value) || logisticsBatches.value[0]
})

// 当前批次的物流条目（兼容旧代码）
const logisticsItems = computed({
  get: () => currentBatch.value?.items ?? [],
  set: (val) => {
    const batch = logisticsBatches.value.find(b => b.id === activeBatchId.value)
    if (batch) batch.items = val
  }
})

// 添加新批次
function addLogisticsBatch() {
  const newBatch: LogisticsBatch = {
    id: nextBatchId(),
    name: `批次 ${logisticsBatches.value.length + 1}`,
    date: new Date().toISOString().split('T')[0],
    desc: '',
    items: [createDefaultLogisticsItem()]
  }
  logisticsBatches.value.push(newBatch)
  activeBatchId.value = newBatch.id
}

// 删除批次
function removeLogisticsBatch(batchId: string) {
  if (logisticsBatches.value.length <= 1) {
    ElMessage.warning('至少保留一个批次')
    return
  }
  const idx = logisticsBatches.value.findIndex(b => b.id === batchId)
  if (idx === -1) return
  logisticsBatches.value.splice(idx, 1)
  // 如果删除的是当前激活的批次，切换到第一个
  if (activeBatchId.value === batchId) {
    activeBatchId.value = logisticsBatches.value[0]?.id ?? ''
  }
}

// 更新批次基本信息
function updateBatchField(batchId: string, field: keyof LogisticsBatch, value: string) {
  const batch = logisticsBatches.value.find(b => b.id === batchId)
  if (batch && field !== 'items' && field !== 'id') {
    (batch as any)[field] = value
  }
}

// 计算单个批次总价
function calculateBatchTotal(batch: LogisticsBatch): number {
  return batch.items.reduce((sum, item) => sum + logisticsItemTotal(item), 0)
}

// 所有批次总价
const logisticsBatchesTotal = computed(() => {
  return logisticsBatches.value.reduce((sum, b) => sum + calculateBatchTotal(b), 0)
})

// 所有批次车辆总数
const logisticsBatchesVehicleCount = computed(() => {
  return logisticsBatches.value.reduce((sum, b) =>
    sum + b.items.reduce((s, item) => s + (Number(item.quantity) || 0), 0), 0
  )
})
/** 车型级起步价/公里价覆盖，在下方车型卡中修改后生效 */
const vehicleOverrides = ref<Record<number, { startPrice?: number; kmPrice?: number }>>({})
/** 表格中出现的不同车型（用于下方展示多张车型卡） */
const distinctVehiclesInUse = computed(() => {
  const ids = [...new Set(logisticsItems.value.map((r) => r.vehicleId).filter((id): id is number => id != null))]
  return ids.map((vehicleId) => {
    const vehicle = vehicleOptions.value.find((v) => v.id === vehicleId)
    return { vehicleId, vehicle: vehicle ?? { id: vehicleId, vehicle_name: `车型 #${vehicleId}` } }
  })
})

/** 运力判断：计算所有批次全部车辆的总可装U数，并与设备清单的总占用U数比较 */
const vehicleCapacityCheck = computed(() => {
  const requiredU = totalRackU.value
  let totalCapacityU = 0
  let hasVehicle = false
  // 遍历所有批次的所有条目
  for (const batch of logisticsBatches.value) {
    for (const item of batch.items) {
      if (item.vehicleId == null) continue
      const vehicle = vehicleOptions.value.find(v => v.id === item.vehicleId)
      if (!vehicle) continue
      hasVehicle = true
      const maxPerTrip = parseRangeToMax(vehicle.server_1u)
      if (maxPerTrip <= 0) continue
      totalCapacityU += maxPerTrip * (Number(item.quantity) || 0)
    }
  }
  const sufficient = !hasVehicle || requiredU <= 0 || totalCapacityU >= requiredU
  const shortage = requiredU - totalCapacityU
  return { requiredU, totalCapacityU, sufficient, shortage, hasVehicle }
})

/** 按车型汇总的建议最少车辆数 */
const vehicleMinQuantities = computed(() => {
  const requiredU = totalRackU.value
  if (requiredU <= 0) return []
  // 收集当前使用的不同车型
  const vehicleIds = new Set<number>()
  for (const batch of logisticsBatches.value) {
    for (const item of batch.items) {
      if (item.vehicleId != null) vehicleIds.add(item.vehicleId)
    }
  }
  const result: Array<{ vehicleId: number; name: string; maxPerTrip: number; currentQty: number; minQty: number }> = []
  for (const vid of vehicleIds) {
    const vehicle = vehicleOptions.value.find(v => v.id === vid)
    if (!vehicle) continue
    const maxPerTrip = parseRangeToMax(vehicle.server_1u)
    if (maxPerTrip <= 0) continue
    // 当前该车型的总数量
    let currentQty = 0
    for (const batch of logisticsBatches.value) {
      for (const item of batch.items) {
        if (item.vehicleId === vid) currentQty += Number(item.quantity) || 0
      }
    }
    const minQty = Math.ceil(requiredU / maxPerTrip)
    result.push({
      vehicleId: vid,
      name: vehicle.vehicle_name || vehicle.vehicle_category || `车型 #${vid}`,
      maxPerTrip,
      currentQty,
      minQty,
    })
  }
  return result
})

function getStartPriceForVehicle(vehicleId: number | null): number {
  if (vehicleId == null) return 0
  const override = vehicleOverrides.value[vehicleId]?.startPrice
  if (override != null) return override
  const v = vehicleOptions.value.find((x) => x.id === vehicleId)
  return v ? parseRangeToMax(v.start_price) : 0
}
/** 车型卡中展示的起步价（可被覆盖） */
function getDisplayStartPrice(vehicleId: number): number {
  return getStartPriceForVehicle(vehicleId)
}
/** 车型卡中展示的公里价（可被覆盖；无覆盖时取该车型首条条目的 row.kmPrice 或后台默认） */
function getDisplayKmPrice(vehicleId: number): number {
  const override = vehicleOverrides.value[vehicleId]?.kmPrice
  if (override != null) return override
  const firstRow = logisticsItems.value.find((r) => r.vehicleId === vehicleId)
  if (firstRow != null) return Math.max(0, Number(firstRow.kmPrice) || 0)
  const v = vehicleOptions.value.find((x) => x.id === vehicleId)
  return v ? parseRangeToMax(v.km_price) : 0
}
function onVehicleStartPriceInput(vehicleId: number, e: Event) {
  const val = (e.target as HTMLInputElement).value
  const n = Number(val)
  if (!vehicleOverrides.value[vehicleId]) vehicleOverrides.value[vehicleId] = {}
  vehicleOverrides.value[vehicleId].startPrice = isNaN(n) || n < 0 ? 0 : n
  vehicleOverrides.value = { ...vehicleOverrides.value }
}
function onVehicleKmPriceInput(vehicleId: number, e: Event) {
  const val = (e.target as HTMLInputElement).value
  const n = Number(val)
  const num = isNaN(n) || n < 0 ? 0 : n
  if (!vehicleOverrides.value[vehicleId]) vehicleOverrides.value[vehicleId] = {}
  vehicleOverrides.value[vehicleId].kmPrice = num
  vehicleOverrides.value = { ...vehicleOverrides.value }
  logisticsItems.value.forEach((row) => {
    if (row.vehicleId === vehicleId) row.kmPrice = num
  })
}
function onVehicleDetail(_vehicleId: number) {
  ElMessage.info('车型详情功能待对接')
}
function logisticsItemTotal(row: LogisticsItem): number {
  const q = Math.max(0, Number(row.quantity) || 0)
  const km = Math.max(0, Number(row.km) || 0)
  const kmP = Math.max(0, Number(row.kmPrice) || 0)
  return q * (getStartPriceForVehicle(row.vehicleId) + km * kmP)
}
function addLogisticsItem() {
  logisticsItems.value.push(createDefaultLogisticsItem())
}
function removeLogisticsItem(index: number) {
  if (logisticsItems.value.length <= 1) return
  logisticsItems.value.splice(index, 1)
}
function onLogisticsVehicleChange(row: LogisticsItem) {
  if (row.vehicleId == null) return
  row.kmPrice = getDisplayKmPrice(row.vehicleId)
}

/** 运输路径（始发地/目的地）变更：若两地均已选且不同，则调用百度驾车路线测算公里数 */
function onLogisticsRoutePathChange(row: LogisticsItem) {
  const o = row.routeOriginIndex
  const d = row.routeDestIndex
  if (o == null || d == null || o === d) {
    if (o === d && o != null) row.km = 0
    return
  }
  fetchDrivingDistance(row)
}

/** 调用高德地图驾车路线规划，将最短驾车距离写入 row.km（公里） */
async function fetchDrivingDistance(row: LogisticsItem) {
  const o = row.routeOriginIndex
  const d = row.routeDestIndex
  if (o == null || d == null || o === d) return
  const startLoc = routeLocations.value[o]
  const destLoc = routeLocations.value[d]
  if (!startLoc?.coords?.trim() || !destLoc?.coords?.trim()) {
    ElMessage.warning('请先在「搬迁路径配置」中为始发地、目的地确认地图坐标后再选运输路径')
    return
  }
  const parseCoords = (s: string): [number, number] | null => {
    const parts = s.split(/[,，\s]+/).map((p) => Number(p.trim())).filter((n) => !isNaN(n))
    return parts.length >= 2 ? [parts[0], parts[1]] : null
  }
  const startArr = parseCoords(startLoc.coords)
  const destArr = parseCoords(destLoc.coords)
  if (!startArr || !destArr) {
    ElMessage.warning('始发地或目的地坐标格式有误，请重新在地图中选点确认')
    return
  }
  row.routeDistanceLoading = true
  try {
    let AMap = (window as any).AMap
    if (typeof AMap === 'undefined') {
      AMap = await loadAMap()
    }
    if (typeof AMap === 'undefined') {
      ElMessage.warning('高德地图未加载，无法测算驾车距离')
      return
    }
    await new Promise<void>((resolve) => {
      let resolved = false
      const timeout = setTimeout(() => {
        if (!resolved) {
          resolved = true
          console.warn('驾车路线测算超时')
          resolve()
        }
      }, 10000)

      const driving = new AMap.Driving({
        policy: AMap.DrivingPolicy.LEAST_DISTANCE
      })
      driving.search(
        new AMap.LngLat(startArr[0], startArr[1]),
        new AMap.LngLat(destArr[0], destArr[1]),
        (status: string, result: any) => {
          if (resolved) return
          resolved = true
          clearTimeout(timeout)
          try {
            if (status === 'complete' && result.routes && result.routes.length > 0) {
              const route = result.routes[0]
              const kmVal = (route.distance || 0) / 1000
              row.km = Math.round(kmVal * 100) / 100
              console.log(`驾车距离测算完成: ${row.km} 公里`)
            }
          } catch (e) {
            console.error('解析驾车距离失败', e)
          }
          resolve()
        }
      )
    })
  } catch (e) {
    console.error('驾车路线测算失败', e)
    ElMessage.warning('驾车距离测算失败，请检查网络或稍后重试')
  } finally {
    row.routeDistanceLoading = false
  }
}
function clampLogisticsItemQuantity(idx: number) {
  const row = logisticsItems.value[idx]
  if (row) row.quantity = clampNonNegative(Number(row.quantity) || 0)
}
function clampLogisticsItemKm(idx: number) {
  const row = logisticsItems.value[idx]
  if (row) row.km = clampNonNegative(Number(row.km) || 0)
}
function clampLogisticsItemKmPrice(idx: number) {
  const row = logisticsItems.value[idx]
  if (row) row.kmPrice = clampNonNegative(Number(row.kmPrice) || 0)
}

// ========== 路线规划弹窗相关 ==========
const isRoutePlanningOpen = ref(false)
const routePlanningLoading = ref(false)
const routePlanningRow = ref<LogisticsItem | null>(null)
const routePlanningOrigin = ref<RouteLocation | null>(null)
const routePlanningDest = ref<RouteLocation | null>(null)
const routePlanningPolicy = ref(0) // 0: 推荐, 1: 最短, 2: 不走高速
const routePlanningResults = ref<Array<{ duration: string; distance: string; distanceKm: number; via: string }>>([])
const routePlanningSelectedIndex = ref<number | null>(null)
/** 从 Direction API v2 拉取的多条路线原始数据，用于地图绘制与切换展示 */
const routePlanningApiRoutes = ref<Array<{ distance: number; duration: number; steps: Array<{ polyline?: string; road?: string }> }>>([])
let routePlanningMapInstance: any = null
let routePlanningDriving: any = null
/** 当前地图上绘制的路线 overlay，用于清除后重绘 */
let routePlanningPolylines: any[] = []

const routePolicyOptions = [
  { value: 0, label: '推荐路线' },
  { value: 1, label: '最短路程' },
  { value: 2, label: '不走高速' }
]

function openRoutePlanningMap(row: LogisticsItem) {
  const o = row.routeOriginIndex
  const d = row.routeDestIndex
  if (o == null || d == null || o === d) return

  routePlanningRow.value = row
  routePlanningOrigin.value = routeLocations.value[o] || null
  routePlanningDest.value = routeLocations.value[d] || null
  routePlanningPolicy.value = 1 // 默认最短路程
  routePlanningResults.value = []
  routePlanningSelectedIndex.value = null
  routePlanningApiRoutes.value = []
  isRoutePlanningOpen.value = true

  nextTick(() => initRoutePlanningMap())
}

function closeRoutePlanning() {
  isRoutePlanningOpen.value = false
  routePlanningRow.value = null
  routePlanningOrigin.value = null
  routePlanningDest.value = null
  routePlanningResults.value = []
  routePlanningSelectedIndex.value = null
  destroyRoutePlanningMap()
}

async function initRoutePlanningMap() {
  const container = document.getElementById('route-planning-map-container')
  if (!container) return

  routePlanningLoading.value = true

  try {
    let AMap = (window as any).AMap
    if (typeof AMap === 'undefined') {
      AMap = await loadAMap()
    }
    if (typeof AMap === 'undefined') {
      ElMessage.warning('高德地图未加载')
      return
    }

    // 创建地图实例（GCJ-02 坐标：北京）
    routePlanningMapInstance = new AMap.Map('route-planning-map-container', {
      zoom: 6,
      center: [116.397, 39.909],
      scrollWheel: true
    })

    // 添加控件
    try {
      routePlanningMapInstance.addControl(new AMap.ToolBar())
      routePlanningMapInstance.addControl(new AMap.Scale())
    } catch (_) {}

    // 搜索路线
    searchRoutePlan()
  } catch (e) {
    console.error('路线规划地图初始化失败', e)
    routePlanningLoading.value = false
  }
}

function destroyRoutePlanningMap() {
  try {
    clearRoutePlanningPolylines()
    if (routePlanningDriving) {
      routePlanningDriving.clear()
      routePlanningDriving = null
    }
    if (routePlanningMapInstance) {
      routePlanningMapInstance.destroy()
      routePlanningMapInstance = null
    }
  } catch (_) {
    routePlanningMapInstance = null
    routePlanningDriving = null
  }
}

/** 清除地图上由 API 路线绘制的折线 */
function clearRoutePlanningPolylines() {
  if (!routePlanningMapInstance) return
  routePlanningPolylines.forEach((overlay) => {
    try {
      overlay.setMap(null)
    } catch (_) {}
  })
  routePlanningPolylines = []
}

/**
 * 高德 Direction REST API 驾车路线规划
 * origin/destination 格式：lng,lat（高德要求经度在前）
 */
async function fetchAmapDirection(
  originLng: number,
  originLat: number,
  destLng: number,
  destLat: number,
  strategy: number,
  alternatives: 0 | 1
): Promise<{ routes: Array<{ distance: number; duration: number; steps: Array<{ polyline?: string; road?: string }> }> } | null> {
  if (!AMAP_KEY) return null
  const origin = `${originLng},${originLat}`
  const destination = `${destLng},${destLat}`
  const url = `https://restapi.amap.com/v3/direction/driving?origin=${encodeURIComponent(origin)}&destination=${encodeURIComponent(destination)}&key=${encodeURIComponent(AMAP_KEY)}&strategy=${strategy}&extensions=all`
  try {
    const res = await fetch(url)
    const data = await res.json()
    if (data.status !== '1' || !data.route?.paths?.length) return null
    return {
      routes: data.route.paths.map((p: any) => ({
        distance: Number(p.distance) || 0,
        duration: Number(p.duration) || 0,
        steps: (p.steps || []).map((s: any) => ({ polyline: s.polyline, road: s.road }))
      }))
    }
  } catch (_) {
    return null
  }
}

/** 将高德 API 返回的 polyline 字符串解析为 LngLat 数组（格式 "lng,lat;lng,lat;..."） */
function parsePathToLngLats(AMap: any, path: string): any[] {
  if (!path || typeof path !== 'string') return []
  const points: any[] = []
  const pairs = path.split(';').map((s) => s.trim()).filter(Boolean)
  for (const pair of pairs) {
    const [lng, lat] = pair.split(',').map((s) => Number(s.trim()))
    if (!isNaN(lng) && !isNaN(lat)) {
      points.push(new AMap.LngLat(lng, lat))
    }
  }
  return points
}

/** 在地图上绘制指定路线的折线（用于 API 多方案） */
function drawRoutePlanningPolyline(routeIndex: number, isHighlight: boolean) {
  const AMap = (window as any).AMap
  if (!AMap || !routePlanningMapInstance || !routePlanningApiRoutes.value[routeIndex]) return
  clearRoutePlanningPolylines()
  const route = routePlanningApiRoutes.value[routeIndex]
  const allPoints: any[] = []
  for (const step of route.steps || []) {
    if (step.polyline) {
      const pts = parsePathToLngLats(AMap, step.polyline)
      allPoints.push(...pts)
    }
  }
  if (allPoints.length < 2) return
  const polyline = new AMap.Polyline({
    path: allPoints,
    strokeColor: isHighlight ? '#135bec' : '#64748b',
    strokeWeight: isHighlight ? 5 : 3,
    strokeOpacity: 0.9
  })
  polyline.setMap(routePlanningMapInstance)
  routePlanningPolylines.push(polyline)
  routePlanningMapInstance.setFitView()
}

function changeRoutePolicy(policy: number) {
  routePlanningPolicy.value = policy
  routePlanningSelectedIndex.value = null
  searchRoutePlan()
}

async function searchRoutePlan() {
  if (!routePlanningOrigin.value?.coords || !routePlanningDest.value?.coords) return
  if (!routePlanningMapInstance) return

  const AMap = (window as any).AMap
  if (!AMap) return

  routePlanningLoading.value = true
  routePlanningResults.value = []
  routePlanningApiRoutes.value = []
  clearRoutePlanningPolylines()

  const parseCoords = (s: string): [number, number] | null => {
    const parts = s.split(/[,，\s]+/).map((p) => Number(p.trim())).filter((n) => !isNaN(n))
    return parts.length >= 2 ? [parts[0], parts[1]] : null
  }

  const startArr = parseCoords(routePlanningOrigin.value.coords)
  const destArr = parseCoords(routePlanningDest.value.coords)
  if (!startArr || !destArr) {
    routePlanningLoading.value = false
    return
  }

  const [startLng, startLat] = startArr
  const [destLng, destLat] = destArr

  // 高德 REST API strategy: 0 速度优先, 2 距离优先, 4 不走高速
  const strategyMap: Record<number, number> = { 0: 0, 1: 2, 2: 4 }
  const strategy = strategyMap[routePlanningPolicy.value] ?? 0
  const alternatives: 0 | 1 = routePlanningPolicy.value === 0 ? 1 : 0

  // 先尝试 REST API
  const apiResult = await fetchAmapDirection(startLng, startLat, destLng, destLat, strategy, alternatives)
  if (apiResult && apiResult.routes.length > 0) {
    routePlanningLoading.value = false
    const plans: Array<{ duration: string; distance: string; distanceKm: number; via: string }> = []
    for (const r of apiResult.routes) {
      const distanceKm = (r.distance || 0) / 1000
      const totalSeconds = Math.round(r.duration || 0)
      const days = Math.floor(totalSeconds / 86400)
      const hours = Math.floor((totalSeconds % 86400) / 3600)
      const minutes = Math.floor((totalSeconds % 3600) / 60)
      const durationDisplay = days > 0 ? `${days}天${hours}小时` : hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`
      const distanceDisplay = `${distanceKm.toFixed(1)}公里`
      const roadNames = new Set<string>()
      for (const step of r.steps || []) {
        const name = (step as any).road
        if (name && name !== '无名路') roadNames.add(name)
      }
      const via = roadNames.size > 0 ? Array.from(roadNames).slice(0, 4).join('、') : '详见地图路线'
      plans.push({
        duration: durationDisplay,
        distance: distanceDisplay,
        distanceKm: Math.round(distanceKm * 100) / 100,
        via
      })
    }
    routePlanningResults.value = plans
    routePlanningApiRoutes.value = apiResult.routes.map((r) => ({
      distance: r.distance || 0,
      duration: r.duration || 0,
      steps: (r as any).steps || []
    }))
    routePlanningSelectedIndex.value = 0
    drawRoutePlanningPolyline(0, true)
    if (plans.length > 0 && routePlanningRow.value) {
      routePlanningRow.value.km = plans[0].distanceKm
    }
    return
  }

  // REST API 失败时回退到 JS SDK AMap.Driving
  if (routePlanningDriving) {
    routePlanningDriving.clear()
  }

  // 高德 JS API DrivingPolicy: LEAST_TIME=0, LEAST_FEE=1, LEAST_DISTANCE=2, REAL_TRAFFIC=4
  const jsPolicyMap: Record<number, number> = { 0: 0, 1: 2, 2: 4 }
  const jsPolicy = jsPolicyMap[routePlanningPolicy.value] ?? 0

  routePlanningDriving = new AMap.Driving({
    map: routePlanningMapInstance,
    policy: jsPolicy
  })

  routePlanningDriving.search(
    new AMap.LngLat(startLng, startLat),
    new AMap.LngLat(destLng, destLat),
    (status: string, result: any) => {
      routePlanningLoading.value = false
      if (status !== 'complete' || !result.routes) return

      const plans: Array<{ duration: string; distance: string; distanceKm: number; via: string }> = []

      for (let i = 0; i < Math.min(result.routes.length, 3); i++) {
        try {
          const route = result.routes[i]
          if (!route) continue

          const distanceKm = (route.distance || 0) / 1000
          const totalSeconds = Math.round(route.time || 0)
          const days = Math.floor(totalSeconds / 86400)
          const hours = Math.floor((totalSeconds % 86400) / 3600)
          const minutes = Math.floor((totalSeconds % 3600) / 60)
          const durationDisplay = days > 0 ? `${days}天${hours}小时` : hours > 0 ? `${hours}小时${minutes}分钟` : `${minutes}分钟`
          const distanceDisplay = `${distanceKm.toFixed(1)}公里`

          const roadNames = new Set<string>()
          for (const step of route.steps || []) {
            if (step.road && step.road !== '无名路') roadNames.add(step.road)
          }
          const via = roadNames.size > 0 ? Array.from(roadNames).slice(0, 4).join('、') : '详见地图路线'

          plans.push({
            duration: durationDisplay,
            distance: distanceDisplay,
            distanceKm: Math.round(distanceKm * 100) / 100,
            via
          })
        } catch (_) {}
      }

      routePlanningResults.value = plans
      if (plans.length > 0) {
        routePlanningSelectedIndex.value = 0
        if (routePlanningRow.value) {
          routePlanningRow.value.km = plans[0].distanceKm
        }
      }
    }
  )
}

function selectRoutePlan(index: number) {
  routePlanningSelectedIndex.value = index
  if (routePlanningApiRoutes.value.length > 0) {
    drawRoutePlanningPolyline(index, true)
  }
  // 切换路线方案时实时更新公里数
  const selected = routePlanningResults.value[index]
  if (selected && routePlanningRow.value) {
    routePlanningRow.value.km = selected.distanceKm
  }
}

function confirmRoutePlan() {
  if (routePlanningSelectedIndex.value === null) return
  const selected = routePlanningResults.value[routePlanningSelectedIndex.value]
  if (!selected || !routePlanningRow.value) return

  // 更新公里数
  routePlanningRow.value.km = selected.distanceKm
  ElMessage.success(`已选择路线：${selected.distance}`)

  closeRoutePlanning()
}

async function loadVehicles() {
  try {
    const res = await axios.get(`${API_URL}/relocation-vehicle/`)
    const list = Array.isArray(res.data) ? res.data : []
    vehicleOptions.value = list
    if (list.length && logisticsItems.value.length === 1 && logisticsItems.value[0].vehicleId == null) {
      logisticsItems.value[0].vehicleId = list[0].id
      logisticsItems.value[0].kmPrice = parseRangeToMax(list[0].km_price)
    }
  } catch (_) {
    vehicleOptions.value = []
  }
}

const DEFAULT_PACKAGING_TIERS = [
  { range: '< 2U', price: 15, label: '基础包装' },
  { range: '3U-5U', price: 28, label: '中型包装' },
  { range: '6U - 10U', price: 45, label: '大型包装' },
  { range: '11U - 20U', price: 80, label: '加强抗震' },
  { range: '> 20U', price: 120, label: '定制木箱' }
]

const packagingTiers = ref(
  DEFAULT_PACKAGING_TIERS.map((t) => ({ ...t }))
)

/** 根据机架高度 U 值映射到包装梯档索引：<2U→0, 3-5U→1, 6-10U→2, 11-20U→3, >20U→4, 未知→-1 */
function getTierIndexForRackU(u: unknown): number {
  if (u === null || u === undefined || u === '') return -1
  const n = Number(u)
  if (isNaN(n) || n <= 0) return -1
  if (n <= 2) return 0
  if (n <= 5) return 1
  if (n <= 10) return 2
  if (n <= 20) return 3
  return 4
}

/** 按包装梯档汇总设备明细清单的数量，返回 { byTier: number[5], unknown: number } */
const equipmentQuantityByTier = computed(() => {
  const tiers = DEFAULT_PACKAGING_TIERS.length
  const byTier = new Array<number>(tiers).fill(0)
  let unknown = 0
  for (const row of equipmentList.value) {
    const q = Number(row.quantity) || 0
    if (q <= 0) continue
    const ti = getTierIndexForRackU(row.rackU)
    if (ti === -1) {
      unknown += q
    } else {
      byTier[ti] += q
    }
  }
  return { byTier, unknown }
})

/** 根据设备明细清单的机架高度(U)与数量，自动生成「按U数梯度包装计费」条目（每梯档一行，数量为对应设备数量之和） */
function syncPackagingFromEquipment() {
  const { byTier, unknown } = equipmentQuantityByTier.value
  const items: PackagingItem[] = byTier.map((quantity, tierIndex) => ({
    id: nextPackagingId(),
    tierIndex,
    quantity
  }))
  // 机架高度为空的设备归为"未知"条目（tierIndex = -1），由用户手动调整
  if (unknown > 0) {
    items.push({
      id: nextPackagingId(),
      tierIndex: -1,
      quantity: unknown
    })
  }
  packagingItems.value = items
}

/** 人工搬运费：与按U数梯度包装计费结构一致，单价逻辑后续单独配置 */
const DEFAULT_MANUAL_HANDLING_TIERS = [
  { range: '< 2U', price: 15, label: '基础包装' },
  { range: '3U-5U', price: 25, label: '中型包装' },
  { range: '6U - 10U', price: 50, label: '大型包装' },
  { range: '11U - 20U', price: 100, label: '加强抗震' },
  { range: '> 20U', price: 150, label: '定制木箱' }
]
const manualHandlingTiers = ref(
  DEFAULT_MANUAL_HANDLING_TIERS.map((t) => ({ ...t }))
)

/** 同园区搬迁：与按U数梯度包装计费结构一致 */
const DEFAULT_SAME_PARK_TIERS = [
  { range: '< 2U', price: 26, label: '基础包装' },
  { range: '3U-5U', price: 35, label: '中型包装' },
  { range: '6U - 10U', price: 50, label: '大型包装' },
  { range: '11U - 20U', price: 180, label: '加强抗震' },
  { range: '> 20U', price: 240, label: '定制木箱' }
]
const sameParkTiers = ref(DEFAULT_SAME_PARK_TIERS.map((t) => ({ ...t })))

interface SameParkItem {
  id: string
  tierIndex: number
  quantity: number
}
let sameParkIdCounter = 0
function nextSameParkId() {
  return `sp-${++sameParkIdCounter}`
}
function createDefaultSameParkItem(): SameParkItem {
  return { id: nextSameParkId(), tierIndex: 0, quantity: 0 }
}
const sameParkItems = ref<SameParkItem[]>([createDefaultSameParkItem()])

function sameParkItemTotal(row: SameParkItem): number {
  const tier = sameParkTiers.value[row.tierIndex]
  const q = Number(row.quantity) || 0
  return tier ? tier.price * q : 0
}
function addSameParkItem() {
  sameParkItems.value.push(createDefaultSameParkItem())
}
function removeSameParkItem(index: number) {
  if (sameParkItems.value.length <= 1) return
  sameParkItems.value.splice(index, 1)
}
function clampSameParkItemQuantity(idx: number) {
  const row = sameParkItems.value[idx]
  if (row) row.quantity = clampNonNegative(Number(row.quantity) || 0)
}
function clampSameParkTierPrice(idx: number) {
  const tiers = sameParkTiers.value
  if (tiers[idx]) {
    tiers[idx].price = clampNonNegative(Number(tiers[idx].price) || 0)
  }
}

const logisticsSubTab = ref(0)

interface PackagingItem {
  id: string
  tierIndex: number
  quantity: number
}
let packagingIdCounter = 0
function nextPackagingId() {
  return `pkg-${++packagingIdCounter}`
}
function createDefaultPackagingItem(): PackagingItem {
  return { id: nextPackagingId(), tierIndex: 0, quantity: 65 }
}
const packagingItems = ref<PackagingItem[]>([createDefaultPackagingItem()])

function packagingItemTotal(row: PackagingItem): number {
  const tier = packagingTiers.value[row.tierIndex]
  const q = Number(row.quantity) || 0
  return tier ? tier.price * q : 0
}
function addPackagingItem() {
  packagingItems.value.push(createDefaultPackagingItem())
}
function removePackagingItem(index: number) {
  if (packagingItems.value.length <= 1) return
  packagingItems.value.splice(index, 1)
}
function clampPackagingItemQuantity(idx: number) {
  const row = packagingItems.value[idx]
  if (row) row.quantity = clampNonNegative(Number(row.quantity) || 0)
}

/** 仅展示数量 > 0 或未知梯档的包装条目 */
const packagingItemsVisible = computed(() =>
  packagingItems.value.filter((row) => (Number(row.quantity) || 0) > 0 || row.tierIndex === -1)
)
/** 包装计费数量汇总（用于表格底部校验展示） */
const packagingQuantityTotal = computed(() =>
  packagingItems.value.reduce((sum, row) => sum + (Number(row.quantity) || 0), 0)
)
function getPackagingIndexById(id: string): number {
  return packagingItems.value.findIndex((r) => r.id === id)
}

function clampTierPrice(idx: number) {
  const tiers = packagingTiers.value
  if (tiers[idx]) {
    tiers[idx].price = clampNonNegative(Number(tiers[idx].price) || 0)
  }
}

interface ManualHandlingItem {
  id: string
  tierIndex: number
  quantity: number
}
let manualHandlingIdCounter = 0
function nextManualHandlingId() {
  return `mh-${++manualHandlingIdCounter}`
}
function createDefaultManualHandlingItem(): ManualHandlingItem {
  return { id: nextManualHandlingId(), tierIndex: 0, quantity: 0 }
}
const manualHandlingItems = ref<ManualHandlingItem[]>([createDefaultManualHandlingItem()])
function manualHandlingItemTotal(row: ManualHandlingItem): number {
  const tier = manualHandlingTiers.value[row.tierIndex]
  const q = Number(row.quantity) || 0
  return tier ? tier.price * q : 0
}
function addManualHandlingItem() {
  manualHandlingItems.value.push(createDefaultManualHandlingItem())
}
function removeManualHandlingItem(index: number) {
  if (manualHandlingItems.value.length <= 1) return
  manualHandlingItems.value.splice(index, 1)
}
function clampManualHandlingItemQuantity(idx: number) {
  const row = manualHandlingItems.value[idx]
  if (row) row.quantity = clampNonNegative(Number(row.quantity) || 0)
}
function clampManualHandlingTierPrice(idx: number) {
  const tiers = manualHandlingTiers.value
  if (tiers[idx]) {
    tiers[idx].price = clampNonNegative(Number(tiers[idx].price) || 0)
  }
}

// 以「按U数梯度包装计费」为源，同步「人工搬运费」条目：条数、机架高度(U)、包装形式、单位、数量一致；单价仍用人工搬运费自定义梯档
function syncManualHandlingFromPackaging() {
  const pkg = packagingItems.value
  const current = manualHandlingItems.value
  manualHandlingItems.value = pkg.map((row, i) => ({
    id: current[i]?.id ?? nextManualHandlingId(),
    tierIndex: row.tierIndex,
    quantity: row.quantity
  }))
}
watch(packagingItems, syncManualHandlingFromPackaging, { deep: true, immediate: true })

// 设备明细清单变更时，自动按梯档汇总并更新「按U数梯度包装计费」条目与数量
watch(equipmentList, () => syncPackagingFromEquipment(), { deep: true, immediate: true })

/** 包装数量与设备清单一致性校验 */
const packagingValidationWarning = computed(() => {
  const totalFromPackaging = packagingItems.value.reduce((sum, row) => sum + (Number(row.quantity) || 0), 0)
  const totalFromEquipment = totalEquipmentCount.value
  // 存在未知梯档条目时优先提示
  const unknownItems = packagingItems.value.filter(row => row.tierIndex === -1 && (Number(row.quantity) || 0) > 0)
  if (unknownItems.length > 0) {
    const unknownQty = unknownItems.reduce((s, r) => s + (Number(r.quantity) || 0), 0)
    return `有 ${unknownQty} 台设备机架高度未知，请在下方选择对应的机架高度(U)档位，或在设备明细清单中补充机架高度信息后重新同步。`
  }
  if (totalFromPackaging !== totalFromEquipment) {
    return `包装数量合计（${totalFromPackaging} 台）与设备明细清单总台数（${totalFromEquipment} 台）不一致，请点击「从设备清单同步」或核对数量。`
  }
  const { byTier } = equipmentQuantityByTier.value
  const sumByTier = new Array(5).fill(0)
  for (const row of packagingItems.value) {
    const ti = row.tierIndex
    if (ti >= 0 && ti < 5) sumByTier[ti] += Number(row.quantity) || 0
  }
  for (let k = 0; k < 5; k++) {
    if (sumByTier[k] !== byTier[k]) {
      const range = DEFAULT_PACKAGING_TIERS[k]?.range ?? ''
      return `梯档「${range}」包装数量与设备清单该档位数量不一致，请点击「从设备清单同步」或核对。`
    }
  }
  return null
})

// 搬迁路径配置 - 城市级别映射
const cityTierMap: Record<string, string> = {
  // 一线城市
  '北京': '一线城市', '上海': '一线城市', '广州': '一线城市', '深圳': '一线城市',
  // 新一线城市
  '成都': '新一线', '杭州': '新一线', '重庆': '新一线', '西安': '新一线',
  '苏州': '新一线', '武汉': '新一线', '南京': '新一线', '天津': '新一线',
  '郑州': '新一线', '长沙': '新一线', '东莞': '新一线', '佛山': '新一线',
  '宁波': '新一线', '青岛': '新一线', '沈阳': '新一线',
  // 二线城市
  '合肥': '二线城市', '昆明': '二线城市', '济南': '二线城市', '大连': '二线城市',
  '厦门': '二线城市', '哈尔滨': '二线城市', '福州': '二线城市', '无锡': '二线城市',
  '长春': '二线城市', '南昌': '二线城市', '贵阳': '二线城市', '石家庄': '二线城市',
  '南宁': '二线城市', '太原': '二线城市', '珠海': '二线城市', '温州': '二线城市',
  '常州': '二线城市', '泉州': '二线城市', '烟台': '二线城市', '惠州': '二线城市',
  '嘉兴': '二线城市', '徐州': '二线城市', '金华': '二线城市', '台州': '二线城市',
  '中山': '二线城市', '绍兴': '二线城市', '潍坊': '二线城市', '保定': '二线城市',
  '兰州': '二线城市', '海口': '二线城市', '呼和浩特': '二线城市', '乌鲁木齐': '二线城市',
  '银川': '二线城市', '西宁': '二线城市',
  // 偏远城市
  '拉萨': '偏远城市', '喀什': '偏远城市', '呼伦贝尔': '偏远城市', '阿里': '偏远城市',
  '日喀则': '偏远城市', '那曲': '偏远城市', '林芝': '偏远城市', '昌都': '偏远城市',
  '山南': '偏远城市', '阿勒泰': '偏远城市', '塔城': '偏远城市', '克拉玛依': '偏远城市',
  '和田': '偏远城市', '阿克苏': '偏远城市', '伊犁': '偏远城市', '博尔塔拉': '偏远城市',
  '克孜勒苏': '偏远城市', '巴音郭楞': '偏远城市', '吐鲁番': '偏远城市', '哈密': '偏远城市',
  '海西': '偏远城市', '海北': '偏远城市', '海南州': '偏远城市', '黄南': '偏远城市',
  '果洛': '偏远城市', '玉树': '偏远城市', '甘南': '偏远城市', '临夏': '偏远城市',
  '阿拉善': '偏远城市', '锡林郭勒': '偏远城市', '兴安': '偏远城市', '延边': '偏远城市'
}
interface RouteLocation {
  id: string
  address: string           // 用户输入的文本
  selectedAddress: string   // 地图选中的完整地址
  city: string
  tier: string
  coords: string
  confirmed: boolean
  searchResults: Array<{ city: string; addr: string; coords: string }>  // 内联搜索结果
  searching: boolean        // 搜索中状态
}
function locationLabel(index: number): string {
  return String.fromCharCode(65 + index)
}
let routeLocationIdCounter = 0
function nextRouteLocationId() {
  return `route-${++routeLocationIdCounter}`
}
const routeLocations = ref<RouteLocation[]>([
  { id: nextRouteLocationId(), address: '', selectedAddress: '', city: '', tier: '', coords: '', confirmed: false, searchResults: [], searching: false },
  { id: nextRouteLocationId(), address: '', selectedAddress: '', city: '', tier: '', coords: '', confirmed: false, searchResults: [], searching: false }
])
const isRouteMapOpen = ref(false)
const activeRouteLocationId = ref<string | null>(null)
const routeSearchQuery = ref('')
// 下方结果列表：优先展示高德搜索/地理编码的实时结果，无结果时显示提示
const routeMapSearchResults = ref<{ city: string; addr: string; coords: string }[]>([])
const routeMapSearching = ref(false)
// 高德地图实例（配置了 Key 时使用）
let routeMapInstance: any = null
let routeMapMarker: any = null
let routeMapGeocoder: any = null
const routeMapPending = ref<{ address: string; city: string; coords: string } | null>(null)
const routeMapLoading = ref(false)
const routeMapLoadFailed = ref(false)
const routeMapTilesLoaded = ref(false) // 瓦片是否加载成功
function tierClass(tier: string): string {
  if (tier === '一线城市') return 'tier-1'
  if (tier === '偏远城市') return 'tier-remote'
  return 'tier-other'
}

function initRouteMap() {
  const container = document.getElementById('route-map-container')
  if (!container || !AMAP_KEY) return
  routeMapLoading.value = true
  routeMapLoadFailed.value = false
  loadAMap()
    .then((AMap) => {
      try {
        const mapContainer = document.getElementById('route-map-container')
        if (!mapContainer) return

        // 确保容器有明确的尺寸
        if (!mapContainer.style.width) mapContainer.style.width = '100%'
        if (!mapContainer.style.height) mapContainer.style.height = '350px'

        routeMapInstance = new AMap.Map('route-map-container', {
          zoom: 12,
          center: [121.4692, 31.2325], // 上海 GCJ-02
          scrollWheel: true
        })

        // 添加地图控件
        try {
          routeMapInstance.addControl(new AMap.ToolBar())
          routeMapInstance.addControl(new AMap.Scale())
        } catch (_) {}

        routeMapGeocoder = new AMap.Geocoder()
        const initLngLat = new AMap.LngLat(121.4692, 31.2325)
        routeMapMarker = new AMap.Marker({ position: initLngLat, visible: false })
        routeMapMarker.setMap(routeMapInstance)

        // 等待地图加载完成后再触发搜索
        let mapReady = false
        const triggerInitialSearch = () => {
          if (mapReady) return
          mapReady = true
          routeMapLoading.value = false
          if (routeSearchQuery.value.trim()) {
            setTimeout(() => doRouteSearch(routeSearchQuery.value.trim()), 300)
          }
        }

        // 强制刷新地图尺寸
        const forceRefreshMap = () => {
          if (!routeMapInstance) return
          try {
            if (typeof routeMapInstance.resize === 'function') {
              routeMapInstance.resize()
            }
            const center = routeMapInstance.getCenter()
            if (center) {
              routeMapInstance.panTo(center)
            }
          } catch (_) {}
        }

        // 监听地图加载完成事件（高德用 'complete'）
        routeMapInstance.on('complete', () => {
          routeMapTilesLoaded.value = true
          triggerInitialSearch()
        })

        // 多次尝试刷新地图以确保瓦片加载
        setTimeout(forceRefreshMap, 100)
        setTimeout(forceRefreshMap, 300)
        setTimeout(forceRefreshMap, 600)
        setTimeout(() => {
          forceRefreshMap()
          triggerInitialSearch()
          setTimeout(() => {
            if (!routeMapTilesLoaded.value) {
              console.warn('高德地图瓦片未能加载，可能是 API Key 限制')
            }
          }, 2000)
        }, 1000)

        routeMapInstance.on('click', (e: any) => {
          const lnglat = e.lnglat
          if (!lnglat) return
          const lng = lnglat.getLng()
          const lat = lnglat.getLat()
          routeMapMarker.setPosition(lnglat)
          routeMapMarker.show()
          routeMapGeocoder.getAddress(lnglat, (status: string, result: any) => {
            if (status === 'complete' && result.regeocode) {
              const comp = result.regeocode.addressComponent || {}
              const city = comp.city || comp.province || ''
              const addr = result.regeocode.formattedAddress || [comp.province, comp.city, comp.district, comp.street, comp.streetNumber].filter(Boolean).join('')
              routeMapPending.value = { address: addr, city, coords: `${Number(lng).toFixed(4)}, ${Number(lat).toFixed(4)}` }
            } else {
              routeMapPending.value = { address: `${lng.toFixed(4)}, ${lat.toFixed(4)}`, city: '', coords: `${Number(lng).toFixed(4)}, ${Number(lat).toFixed(4)}` }
            }
          })
        })
      } catch (e) {
        console.error('高德地图初始化失败', e)
        routeMapLoadFailed.value = true
        routeMapLoading.value = false
      }
    })
    .catch((e) => {
      console.error('高德地图加载失败', e)
      routeMapLoading.value = false
      routeMapLoadFailed.value = true
      ElMessage.warning('地图加载失败，请检查 Key 或从下方结果选择。')
    })
}

function destroyRouteMap() {
  routeMapPending.value = null
  try {
    if (routeMapMarker) {
      routeMapMarker.setMap(null)
      routeMapMarker = null
    }
    if (routeMapInstance) {
      routeMapInstance.destroy()
      routeMapInstance = null
    }
  } catch (_) {
    routeMapInstance = null
    routeMapMarker = null
  }
  routeMapGeocoder = null
}

/** 根据关键词搜索地点并更新下方结果列表（优先 PlaceSearch 获取多个 POI 结果） */
function doRouteSearch(keyword: string) {
  if (!keyword.trim()) {
    routeMapSearchResults.value = []
    return
  }
  const AMap = (window as any).AMap
  if (!AMap || !routeMapInstance || routeMapLoadFailed.value) {
    provideManualFallback(keyword)
    return
  }
  routeMapSearching.value = true
  routeMapSearchResults.value = []

  tryLocalSearch(keyword)
}

/** 使用 PlaceSearch 搜索 POI（返回多个结果，不需要 map 实例） */
function tryLocalSearch(keyword: string) {
  const AMap = (window as any).AMap
  if (!AMap) {
    routeMapSearching.value = false
    tryGeocoderFallback(keyword)
    return
  }

  let callbackFired = false
  try {
    const placeSearch = new AMap.PlaceSearch({
      pageSize: 10
    })
    const timeoutId = setTimeout(() => {
      if (!callbackFired) {
        callbackFired = true
        tryGeocoderFallback(keyword)
      }
    }, 5000)

    placeSearch.search(keyword, (status: string, result: any) => {
      if (callbackFired) return
      callbackFired = true
      clearTimeout(timeoutId)

      if (status !== 'complete' || !result.poiList?.pois?.length) {
        tryGeocoderFallback(keyword)
        return
      }
      const list: { city: string; addr: string; coords: string }[] = []
      for (const poi of result.poiList.pois) {
        if (!poi.location) continue
        const lng = poi.location.getLng()
        const lat = poi.location.getLat()
        const title = poi.name || ''
        const address = poi.address || ''
        const addr = title ? (address ? `${title}（${address}）` : title) : address
        const city = poi.cityname || ''
        list.push({ city, addr, coords: `${Number(lng).toFixed(4)}, ${Number(lat).toFixed(4)}` })
      }
      if (list.length === 0) {
        tryGeocoderFallback(keyword)
      } else {
        routeMapSearching.value = false
        routeMapSearchResults.value = list
        if (list.length > 0 && routeMapInstance) {
          const firstCoords = list[0].coords.split(', ')
          if (firstCoords.length === 2) {
            routeMapInstance.setZoomAndCenter(14, [parseFloat(firstCoords[0]), parseFloat(firstCoords[1])])
          }
        }
      }
    })
  } catch (_) {
    callbackFired = true
    tryGeocoderFallback(keyword)
  }
}

/** 使用 Geocoder 进行地址解析（作为 PlaceSearch 的兜底） */
function tryGeocoderFallback(keyword: string) {
  if (!routeMapGeocoder) {
    routeMapSearching.value = false
    provideManualFallback(keyword)
    return
  }

  let geocoderFired = false
  const geocoderTimeout = setTimeout(() => {
    if (!geocoderFired) {
      geocoderFired = true
      routeMapSearching.value = false
      provideManualFallback(keyword)
    }
  }, 4000)

  routeMapGeocoder.getLocation(keyword, (status: string, result: any) => {
    if (geocoderFired) return
    geocoderFired = true
    clearTimeout(geocoderTimeout)

    if (status === 'complete' && result.geocodes && result.geocodes.length > 0) {
      const geocode = result.geocodes[0]
      const location = geocode.location
      const lng = location.getLng()
      const lat = location.getLat()
      const coordsStr = `${Number(lng).toFixed(4)}, ${Number(lat).toFixed(4)}`
      const comp = geocode.addressComponent || {}
      const city = comp.city || comp.province || ''
      const addr = geocode.formattedAddress || keyword.trim()

      routeMapSearching.value = false
      routeMapSearchResults.value = [{ city, addr, coords: coordsStr }]
      if (routeMapInstance) {
        routeMapInstance.setZoomAndCenter(15, [lng, lat])
      }
      if (routeMapMarker) {
        routeMapMarker.setPosition(location)
        routeMapMarker.show()
      }
    } else {
      routeMapSearching.value = false
      provideManualFallback(keyword)
    }
  })
}

/** 根据关键词智能识别城市并提供手动确认选项 */
function provideManualFallback(keyword: string) {
  // 常见城市名映射
  const cityPatterns: { pattern: RegExp; city: string }[] = [
    { pattern: /上海|浦东|陆家嘴|徐汇|黄浦|静安|长宁|普陀|虹口|杨浦|闵行|宝山|嘉定|金山|松江|青浦|奉贤|崇明/, city: '上海' },
    { pattern: /北京|朝阳|海淀|西城|东城|丰台|通州|大兴|顺义|昌平|房山/, city: '北京' },
    { pattern: /广州|天河|越秀|荔湾|白云|番禺|黄埔|花都|南沙|从化|增城/, city: '广州' },
    { pattern: /深圳|福田|罗湖|南山|宝安|龙岗|盐田|龙华|坪山|光明/, city: '深圳' },
    { pattern: /杭州|西湖|上城|下城|江干|拱墅|余杭|萧山|滨江|富阳|临安/, city: '杭州' },
    { pattern: /南京|玄武|秦淮|建邺|鼓楼|浦口|栖霞|雨花台|江宁|六合|溧水/, city: '南京' },
    { pattern: /成都|锦江|青羊|金牛|武侯|成华|龙泉驿|青白江|新都|温江|双流/, city: '成都' },
    { pattern: /武汉|江岸|江汉|硚口|汉阳|武昌|青山|洪山|东西湖|蔡甸|江夏/, city: '武汉' },
    { pattern: /重庆|渝中|大渡口|江北|沙坪坝|九龙坡|南岸|北碚|渝北|巴南/, city: '重庆' },
    { pattern: /天津|和平|河东|河西|南开|河北|红桥|东丽|西青|津南|北辰|武清/, city: '天津' },
    { pattern: /苏州|姑苏|虎丘|吴中|相城|吴江|昆山|太仓|常熟|张家港/, city: '苏州' },
    { pattern: /无锡|梁溪|锡山|惠山|滨湖|新吴|江阴|宜兴/, city: '无锡' },
    { pattern: /宁波|海曙|江北|北仑|镇海|鄞州|奉化|余姚|慈溪|象山|宁海/, city: '宁波' },
    { pattern: /青岛|市南|市北|黄岛|崂山|李沧|城阳|即墨|胶州|平度|莱西/, city: '青岛' },
    { pattern: /西安|新城|碑林|莲湖|灞桥|未央|雁塔|阎良|临潼|长安|高陵/, city: '西安' },
    { pattern: /郑州|中原|二七|管城|金水|上街|惠济|中牟|巩义|荥阳|新密|新郑|登封/, city: '郑州' },
    { pattern: /长沙|芙蓉|天心|岳麓|开福|雨花|望城|长沙县|浏阳|宁乡/, city: '长沙' },
    { pattern: /东莞|莞城|南城|东城|万江|石碣|石龙|茶山|石排|企石|横沥|桥头/, city: '东莞' },
    { pattern: /佛山|禅城|南海|顺德|三水|高明/, city: '佛山' },
    { pattern: /合肥|瑶海|庐阳|蜀山|包河|长丰|肥东|肥西|庐江|巢湖/, city: '合肥' },
  ]

  let detectedCity = ''
  for (const { pattern, city } of cityPatterns) {
    if (pattern.test(keyword)) {
      detectedCity = city
      break
    }
  }

  // 生成模拟坐标（基于城市中心点的近似值）
  // GCJ-02 坐标（高德地图坐标系）
  const cityCenterCoords: Record<string, string> = {
    '上海': '121.4692, 31.2325',
    '北京': '116.3975, 39.9085',
    '广州': '113.2644, 23.1291',
    '深圳': '114.0579, 22.5431',
    '杭州': '120.1536, 30.2655',
    '南京': '118.7969, 32.0603',
    '成都': '104.0657, 30.6595',
    '武汉': '114.3046, 30.5928',
    '重庆': '106.5516, 29.5630',
    '天津': '117.1901, 39.1256',
    '苏州': '120.6195, 31.2990',
    '无锡': '120.3119, 31.4912',
    '宁波': '121.5440, 29.8683',
    '青岛': '120.3826, 36.0671',
    '西安': '108.9402, 34.3416',
    '郑州': '113.6254, 34.7466',
    '长沙': '112.9388, 28.2282',
    '东莞': '113.7518, 23.0208',
    '佛山': '113.1219, 23.0218',
    '合肥': '117.2272, 31.8206',
  }

  const coords = cityCenterCoords[detectedCity] || '116.3975, 39.9085'

  // 显示手动确认选项
  routeMapSearchResults.value = [{
    city: detectedCity || '未知',
    addr: keyword.trim(),
    coords: coords
  }]

  if (!detectedCity) {
    ElMessage.info('无法精确解析地址，请确认或在地图上点击选点')
  }
}

watch(isRouteMapOpen, (open) => {
  if (open && hasAmapKey.value && !routeMapLoadFailed.value) {
    routeMapTilesLoaded.value = false
    nextTick(() => initRouteMap())
  } else if (!open) {
    destroyRouteMap()
    routeMapLoadFailed.value = false
    routeMapSearchResults.value = []
    routeMapSearching.value = false
    routeMapTilesLoaded.value = false
  }
})

function confirmRouteMapSelection() {
  const pending = routeMapPending.value
  if (!pending || !activeRouteLocationId.value) return
  confirmRouteMapPoint(pending.city, pending.address, pending.coords)
}

function addRouteLocation() {
  routeLocations.value.push({
    id: nextRouteLocationId(),
    address: '',
    selectedAddress: '',
    city: '',
    tier: '',
    coords: '',
    confirmed: false,
    searchResults: [],
    searching: false
  })
}
function removeRouteLocation(id: string) {
  if (routeLocations.value.length <= 1) return
  routeLocations.value = routeLocations.value.filter((l) => l.id !== id)
}
function openRouteMapPicker(id: string) {
  activeRouteLocationId.value = id
  const loc = routeLocations.value.find((l) => l.id === id)
  // 清除内联搜索结果
  if (loc) {
    loc.searchResults = []
    loc.searching = false
  }
  routeSearchQuery.value = loc?.address ?? ''
  isRouteMapOpen.value = true
}
function closeRouteMap() {
  try {
    destroyRouteMap()
  } catch (_) {}
  isRouteMapOpen.value = false
  activeRouteLocationId.value = null
  routeMapLoadFailed.value = false
}
// 内联搜索防抖定时器
const inlineSearchTimers = new Map<string, ReturnType<typeof setTimeout>>()

function onRouteAddressInput(id: string) {
  const loc = routeLocations.value.find((l) => l.id === id)
  if (!loc) return

  // 重置确认状态
  loc.confirmed = false
  loc.searchResults = []

  const keyword = loc.address.trim()
  if (!keyword) {
    loc.searching = false
    return
  }

  // 防抖：延迟300ms后触发搜索
  if (inlineSearchTimers.has(id)) {
    clearTimeout(inlineSearchTimers.get(id)!)
  }

  loc.searching = true
  inlineSearchTimers.set(id, setTimeout(() => {
    doInlineRouteSearch(id, keyword)
  }, 300))
}

// 内联地图搜索
async function doInlineRouteSearch(locId: string, keyword: string) {
  const loc = routeLocations.value.find((l) => l.id === locId)
  if (!loc) return

  const AMap = (window as any).AMap
  if (!AMap) {
    loc.searching = false
    return
  }

  let callbackFired = false

  try {
    // PlaceSearch 不需要 map 实例
    const placeSearch = new AMap.PlaceSearch({
      pageSize: 8
    })

    const timeoutId = setTimeout(() => {
      if (!callbackFired) {
        callbackFired = true
        loc.searching = false
        tryInlineGeocoderFallback(locId, keyword)
      }
    }, 5000)

    placeSearch.search(keyword, (status: string, result: any) => {
      if (callbackFired) return
      callbackFired = true
      clearTimeout(timeoutId)
      loc.searching = false

      if (status !== 'complete' || !result.poiList?.pois?.length) {
        tryInlineGeocoderFallback(locId, keyword)
        return
      }

      const items: Array<{ city: string; addr: string; coords: string }> = []
      for (let i = 0; i < Math.min(result.poiList.pois.length, 6); i++) {
        try {
          const poi = result.poiList.pois[i]
          if (!poi?.location) continue
          const lng = poi.location.getLng()
          const lat = poi.location.getLat()
          const title = poi.name || ''
          const address = poi.address || ''
          const addr = title ? (address ? `${title}（${address}）` : title) : address
          const city = poi.cityname || ''
          if (addr) {
            items.push({
              city: city,
              addr: addr,
              coords: `${Number(lng).toFixed(4)}, ${Number(lat).toFixed(4)}`
            })
          }
        } catch (_) {}
      }

      if (items.length > 0) {
        loc.searchResults = items
      } else {
        tryInlineGeocoderFallback(locId, keyword)
      }
    })
  } catch (_) {
    loc.searching = false
    loc.searchResults = []
  }
}

/** 内联地址搜索的 Geocoder 兜底：全国范围解析，与「地图位置确认」弹窗行为一致 */
function tryInlineGeocoderFallback(locId: string, keyword: string) {
  const loc = routeLocations.value.find((l) => l.id === locId)
  if (!loc) return

  const AMap = (window as any).AMap
  if (!AMap) {
    loc.searching = false
    return
  }

  const geocoder = new AMap.Geocoder()
  let fired = false
  const timeoutId = setTimeout(() => {
    if (!fired) {
      fired = true
      loc.searching = false
    }
  }, 4000)

  geocoder.getLocation(keyword, (status: string, result: any) => {
    if (fired) return
    fired = true
    clearTimeout(timeoutId)

    if (status !== 'complete' || !result.geocodes || result.geocodes.length === 0) {
      loc.searching = false
      return
    }

    const geocode = result.geocodes[0]
    const location = geocode.location
    const lng = location.getLng()
    const lat = location.getLat()
    const coordsStr = `${Number(lng).toFixed(4)}, ${Number(lat).toFixed(4)}`
    const comp = geocode.addressComponent || {}
    const city = comp.city || comp.province || ''
    const addr = geocode.formattedAddress || keyword.trim()

    loc.searching = false
    loc.searchResults = [{ city, addr, coords: coordsStr }]
  })
}

// 选择内联搜索结果
function selectInlineSearchResult(locId: string, result: { city: string; addr: string; coords: string }) {
  const loc = routeLocations.value.find((l) => l.id === locId)
  if (!loc) return

  const normalizedCity = normalizeCityName(result.city)
  const tier = cityTierMap[normalizedCity] ?? '三线及以下'

  loc.selectedAddress = result.addr
  loc.city = normalizedCity || result.city
  loc.tier = tier
  loc.coords = result.coords
  loc.confirmed = true
  loc.searchResults = []
  loc.searching = false
}

// 清除内联搜索结果（点击外部时）
function clearInlineSearchResults(locId: string) {
  const loc = routeLocations.value.find((l) => l.id === locId)
  if (loc) {
    loc.searchResults = []
    loc.searching = false
  }
}
/** 标准化城市名称，去除"市"后缀以匹配 cityTierMap */
function normalizeCityName(city: string): string {
  if (!city) return ''
  // 去除末尾的"市"字
  let normalized = city.replace(/市$/, '')
  // 处理直辖市特殊情况
  if (normalized === '北京' || normalized === '上海' || normalized === '天津' || normalized === '重庆') {
    return normalized
  }
  // 处理省份名称（如果传入的是省份，尝试提取城市）
  normalized = normalized.replace(/省$/, '')
  return normalized
}

function confirmRouteMapPoint(mockCity: string, mockAddr: string, coordsOverride?: string) {
  const id = activeRouteLocationId.value
  if (!id) return
  // 标准化城市名称以匹配 cityTierMap
  const normalizedCity = normalizeCityName(mockCity)
  const tier = cityTierMap[normalizedCity] ?? '三线及以下'
  const coords = coordsOverride ?? `${(Math.random() * 20 + 100).toFixed(2)}, ${(Math.random() * 10 + 20).toFixed(2)}`
  routeLocations.value = routeLocations.value.map((loc) =>
    loc.id === id
      ? { ...loc, selectedAddress: mockAddr, city: normalizedCity || mockCity, tier, coords, confirmed: true, searchResults: [], searching: false }
      : loc
  )
  closeRouteMap()
}
function confirmRouteMapFromSearch() {
  const keyword = routeSearchQuery.value.trim()
  if (!keyword) return
  // 直接调用 doRouteSearch，它会处理所有情况（Geocoder、LocalSearch、手动兜底）
  doRouteSearch(keyword)
}

// 人工服务费
const laborServiceTypeOptions = ['现场勘察', '项目管理', '其它服务']
let laborIdCounter = 0
function nextLaborId() {
  return `labor-${++laborIdCounter}`
}
interface LaborCostRow {
  id: string
  serviceType: string
  /** 当 serviceType 为「其它服务」时，可编辑的自定义类型名称 */
  customServiceType?: string
  serviceDesc: string
  quantity: number
  unitPrice: number | null
}
/** 按服务类型返回默认单价：现场勘察 990，项目管理 1450，其它服务 为空 */
function getDefaultLaborUnitPrice(serviceType: string): number | null {
  if (serviceType === '现场勘察') return 990
  if (serviceType === '项目管理') return 1450
  if (serviceType === '其它服务') return null
  return 990
}
function createEmptyLaborRow(): LaborCostRow {
  return {
    id: nextLaborId(),
    serviceType: '现场勘察',
    serviceDesc: '',
    quantity: 0,
    unitPrice: 990
  }
}
const laborCostItems = ref<LaborCostRow[]>([
  { id: nextLaborId(), serviceType: '现场勘察', serviceDesc: '搬迁前设备状态记录与风险评估', quantity: 1, unitPrice: 990 },
  { id: nextLaborId(), serviceType: '项目管理', serviceDesc: '全程项目协调、进度把控与资源调度', quantity: 1, unitPrice: 1450 }
])

function laborRowTotal(row: LaborCostRow): number {
  const q = Number(row.quantity) || 0
  const p = row.unitPrice != null ? Number(row.unitPrice) : 0
  return q * p
}

/** 服务类型变更时，按类型填入默认单价（其它服务为空） */
function onLaborServiceTypeChange(row: LaborCostRow) {
  row.unitPrice = getDefaultLaborUnitPrice(row.serviceType)
}

function addLaborItem() {
  laborCostItems.value.push(createEmptyLaborRow())
}

function removeLaborItem(index: number) {
  laborCostItems.value.splice(index, 1)
}

/** 恢复「现场勘察」「项目管理」的单价为默认值：990、1450 */
function restoreLaborDefaults() {
  laborCostItems.value.forEach((row) => {
    const def = getDefaultLaborUnitPrice(row.serviceType)
    if (def != null) row.unitPrice = def
  })
}

// 增值服务明细
let valueAddedIdCounter = 0
function nextValueAddedId() {
  return `va-${++valueAddedIdCounter}`
}
interface ValueAddedRow {
  id: string
  itemName: string
  serviceDesc: string
  /** 单位，如 台、根，默认 台 */
  unit?: string
  quantity: number
  unitPrice: number
}
function createEmptyValueAddedRow(): ValueAddedRow {
  return {
    id: nextValueAddedId(),
    itemName: '',
    serviceDesc: '',
    unit: '台',
    quantity: 0,
    unitPrice: 0
  }
}
const valueAddedItems = ref<ValueAddedRow[]>([
  { id: nextValueAddedId(), itemName: '停机测试服务', serviceDesc: '搬迁前后系统连通性与压力测试', unit: '台', quantity: 10, unitPrice: 20 },
  { id: nextValueAddedId(), itemName: '设备上下架', serviceDesc: '服务器、存储等设备的标准上下架实施', unit: '台', quantity: 40, unitPrice: 15 },
  { id: nextValueAddedId(), itemName: '拆布垂直线缆', serviceDesc: '机柜内垂直线缆的拆除与敷设', unit: '根', quantity: 1, unitPrice: 6.5 },
  { id: nextValueAddedId(), itemName: '拆布水平线缆', serviceDesc: '机房水平线缆的拆除与敷设', unit: '根', quantity: 1, unitPrice: 18 }
])

function valueAddedRowTotal(row: ValueAddedRow): number {
  const q = Number(row.quantity) || 0
  const p = Number(row.unitPrice) || 0
  return q * p
}

function addValueAddedItem() {
  valueAddedItems.value.push(createEmptyValueAddedRow())
}

function removeValueAddedItem(index: number) {
  valueAddedItems.value.splice(index, 1)
}

// 其他费用：专用设备租用、外部人工调用、专用设备采购
let otherCostIdCounter = 0
function nextOtherCostId() {
  return `other-${++otherCostIdCounter}`
}
interface EquipmentRentalRow {
  id: string
  equipmentName: string
  brand: string
  model: string
  quantity: number
  unit: string
  rentalPrice: number
}
interface EquipmentPurchaseRow {
  id: string
  equipmentName: string
  brand: string
  model: string
  quantity: number
  unit: string
  purchasePrice: number
}
interface ExternalLaborRow {
  id: string
  personnelType: string
  serviceContent: string
  quantity: number
  unit: string
  unitPrice: number
}
function createEmptyEquipmentRentalRow(): EquipmentRentalRow {
  return { id: nextOtherCostId(), equipmentName: '', brand: '', model: '', quantity: 0, unit: '台', rentalPrice: 0 }
}
function createEmptyEquipmentPurchaseRow(): EquipmentPurchaseRow {
  return { id: nextOtherCostId(), equipmentName: '', brand: '', model: '', quantity: 0, unit: '台', purchasePrice: 0 }
}
function createEmptyExternalLaborRow(): ExternalLaborRow {
  return { id: nextOtherCostId(), personnelType: '', serviceContent: '', quantity: 0, unit: '人天', unitPrice: 0 }
}
const equipmentRentalItems = ref<EquipmentRentalRow[]>([createEmptyEquipmentRentalRow()])
const equipmentPurchaseItems = ref<EquipmentPurchaseRow[]>([createEmptyEquipmentPurchaseRow()])
const externalLaborItems = ref<ExternalLaborRow[]>([createEmptyExternalLaborRow()])
const otherCostSubTab = ref(0) // 0 专用设备租用 1 外部人工调用 2 专用设备采购

/** 设备名称预设选项（专用设备租用 / 专用设备采购） */
const EQUIPMENT_NAME_PRESET_OPTIONS = ['海关锁', '车内GPS+CCTV']
/** 当前展开设备名称预设下拉的行 id（同一时间只展开一行） */
const equipmentNameDropdownId = ref<string | null>(null)
/** 当前展开下拉对应的行（用于 Teleport 内选项回填） */
const equipmentNameDropdownRowRef = ref<{ equipmentName: string } | null>(null)
/** 下拉框定位（Teleport 到 body 时使用 fixed 定位，避免被表格 overflow 裁剪） */
const equipmentNameDropdownRect = ref<{ left: number; top: number; width: number } | null>(null)

function toggleEquipmentNameDropdown(rowId: string, row: { equipmentName: string }, e: MouseEvent) {
  if (equipmentNameDropdownId.value === rowId) {
    closeEquipmentNameDropdown()
    return
  }
  const el = (e.currentTarget as HTMLElement).closest('.equipment-name-combobox') as HTMLElement
  equipmentNameDropdownRowRef.value = row
  equipmentNameDropdownId.value = rowId
  nextTick(() => {
    if (el) {
      const rect = el.getBoundingClientRect()
      equipmentNameDropdownRect.value = {
        left: rect.left,
        top: rect.bottom + 2,
        width: rect.width
      }
    }
  })
}
function selectEquipmentNamePreset(row: { equipmentName: string }, value: string) {
  row.equipmentName = value
  closeEquipmentNameDropdown()
}

function equipmentRentalRowTotal(row: EquipmentRentalRow): number {
  return (Number(row.quantity) || 0) * (Number(row.rentalPrice) || 0)
}
function equipmentPurchaseRowTotal(row: EquipmentPurchaseRow): number {
  return (Number(row.quantity) || 0) * (Number(row.purchasePrice) || 0)
}
function externalLaborRowTotal(row: ExternalLaborRow): number {
  return (Number(row.quantity) || 0) * (Number(row.unitPrice) || 0)
}

function addEquipmentRentalItem() {
  equipmentRentalItems.value.push(createEmptyEquipmentRentalRow())
}
function removeEquipmentRentalItem(index: number) {
  equipmentRentalItems.value.splice(index, 1)
}
function addEquipmentPurchaseItem() {
  equipmentPurchaseItems.value.push(createEmptyEquipmentPurchaseRow())
}
function removeEquipmentPurchaseItem(index: number) {
  equipmentPurchaseItems.value.splice(index, 1)
}
function addExternalLaborItem() {
  externalLaborItems.value.push(createEmptyExternalLaborRow())
}
function removeExternalLaborItem(index: number) {
  externalLaborItems.value.splice(index, 1)
}

const equipmentRentalCost = computed(() =>
  equipmentRentalItems.value.reduce((sum, row) => sum + equipmentRentalRowTotal(row), 0)
)
const equipmentPurchaseCost = computed(() =>
  equipmentPurchaseItems.value.reduce((sum, row) => sum + equipmentPurchaseRowTotal(row), 0)
)
const externalLaborCost = computed(() =>
  externalLaborItems.value.reduce((sum, row) => sum + externalLaborRowTotal(row), 0)
)
const otherCostTotal = computed(() =>
  equipmentRentalCost.value + equipmentPurchaseCost.value + externalLaborCost.value
)

function clampNonNegative(v: number): number {
  const n = Number(v)
  return isNaN(n) || n < 0 ? 0 : n
}

const packagingCost = computed(() =>
  packagingItems.value.reduce((sum, row) => sum + packagingItemTotal(row), 0)
)

const logisticsCost = computed(() =>
  logisticsBatches.value.reduce((sum, batch) =>
    sum + batch.items.reduce((s, row) => s + logisticsItemTotal(row), 0), 0
  )
)

const manualHandlingCost = computed(() =>
  manualHandlingItems.value.reduce((sum, row) => sum + manualHandlingItemTotal(row), 0)
)

const sameParkCost = computed(() =>
  sameParkItems.value.reduce((sum, row) => sum + sameParkItemTotal(row), 0)
)

const laborCost = computed(() => {
  return laborCostItems.value.reduce((sum, row) => sum + laborRowTotal(row), 0)
})

const valueAddedCost = computed(() => {
  return valueAddedItems.value.reduce((sum, row) => sum + valueAddedRowTotal(row), 0)
})

const insuranceCost = computed(() => {
  const val = Number(declaredValue.value)
  const rate = Number(insuranceRatePermille.value) || 0
  return Math.round((isNaN(val) || val < 0 ? 0 : val) * (rate / 1000))
})

/** 成本小计（包装+物流+人工搬运+同园区搬迁+人工+增值+其他费用+保险） */
const costSubtotal = computed(() => {
  return packagingCost.value + logisticsCost.value + manualHandlingCost.value + sameParkCost.value + laborCost.value + valueAddedCost.value + otherCostTotal.value + insuranceCost.value
})

/** 全局参数：增值税率、账期、利润率、年化资金成本率 */
const globalParams = ref({
  vatRate: 6,
  paymentCycle: 0,
  profitRate: 0,
  fundingCostRate: 3
})

/** 基础项目金额 = 成本小计 × (1+利润率) × (1+增值税率) */
const baseProjectAmount = computed(() => {
  const profit = 1 + (globalParams.value.profitRate || 0) / 100
  const vat = 1 + (globalParams.value.vatRate ?? 6) / 100
  return costSubtotal.value * profit * vat
})

/** 账期成本率 = 年化资金成本率 × (账期天数/365) */
const fundingCostRateForCycle = computed(() => {
  const rate = (globalParams.value.fundingCostRate || 0) / 100
  const days = globalParams.value.paymentCycle || 0
  return rate * (days / 365)
})

/** 项目总额（含账期成本）P = B / (1 - r) */
const finalProjectAmount = computed(() => {
  const r = fundingCostRateForCycle.value
  if (r >= 1) return baseProjectAmount.value
  return Math.round(baseProjectAmount.value / (1 - r))
})

/** 预估总毛利 = 成本小计 × 利润率 × (1+增值税率) */
const totalGrossProfit = computed(() => {
  const profitRate = (globalParams.value.profitRate || 0) / 100
  const vat = 1 + (globalParams.value.vatRate ?? 6) / 100
  return Math.round(costSubtotal.value * profitRate * vat)
})

/** 利润率显示 */
const totalMargin = computed(() => (globalParams.value.profitRate ?? 0).toFixed(1))

/** 成本构成（按大类分组，含子项明细，用于右侧栏展示） */
interface CostSubItem { name: string; amount: number; percent: number }
interface CostGroup { name: string; amount: number; percent: number; color: string; children: CostSubItem[] }
const costBreakdown = computed((): CostGroup[] => {
  const total = finalProjectAmount.value
  const vat = 1 + (globalParams.value.vatRate ?? 6) / 100
  const pct = (v: number) => total > 0 ? Math.round((v / total) * 100) : 0

  const p1 = Math.round(packagingCost.value * vat)
  const p2 = Math.round(logisticsCost.value * vat)
  const pMh = Math.round(manualHandlingCost.value * vat)
  const pSamePark = Math.round(sameParkCost.value * vat)
  const p3 = Math.round(laborCost.value * vat)
  const p4 = Math.round(valueAddedCost.value * vat)
  const pRental = Math.round(equipmentRentalCost.value * vat)
  const pLabor = Math.round(externalLaborCost.value * vat)
  const pPurchase = Math.round(equipmentPurchaseCost.value * vat)
  const p5 = Math.round(insuranceCost.value * vat)
  const fundingCost = Math.round(total * fundingCostRateForCycle.value)

  // 人工服务费 = 专业人工费（现场勘察、项目管理等）
  const laborTotal = p3
  const laborChildren: CostSubItem[] = laborCostItems.value.map(item => {
    const amt = Math.round(item.quantity * item.unitPrice * vat)
    return { name: item.serviceType, amount: amt, percent: pct(amt) }
  })

  // 包装耗材费
  const packChildren: CostSubItem[] = []
  for (const item of packagingItems.value) {
    const tier = packagingTiers.value[item.tierIndex]
    if (!tier) continue
    const amt = Math.round(item.quantity * tier.price * vat)
    if (amt > 0) packChildren.push({ name: tier.range, amount: amt, percent: pct(amt) })
  }

  // 物流运输费 = 车辆配送费 + 人工搬运费 + 同园区搬迁费
  const logisticsTotal = p2 + pMh + pSamePark
  const logisticsChildren: CostSubItem[] = [
    { name: '车辆配送费', amount: p2, percent: pct(p2) },
    { name: '人工搬运费', amount: pMh, percent: pct(pMh) },
    { name: '同园区搬迁费', amount: pSamePark, percent: pct(pSamePark) },
  ]

  // 增值服务费
  const vasChildren: CostSubItem[] = valueAddedItems.value.map(item => {
    const amt = Math.round(item.quantity * item.unitPrice * vat)
    return { name: item.itemName || '未命名', amount: amt, percent: pct(amt) }
  })

  // 其他费用 = 专用设备租用 + 外部人工调用 + 专用设备采购
  const otherTotal = pRental + pLabor + pPurchase
  const otherChildren: CostSubItem[] = [
    { name: '专用设备租用', amount: pRental, percent: pct(pRental) },
    { name: '外部人工调用', amount: pLabor, percent: pct(pLabor) },
    { name: '专用设备采购', amount: pPurchase, percent: pct(pPurchase) },
  ]

  return [
    { name: '人工服务费', amount: laborTotal, percent: pct(laborTotal), color: '#06b6d4', children: laborChildren },
    { name: '包装耗材费', amount: p1, percent: pct(p1), color: '#3b82f6', children: packChildren },
    { name: '物流运输费', amount: logisticsTotal, percent: pct(logisticsTotal), color: '#8b5cf6', children: logisticsChildren },
    { name: '增值服务费', amount: p4, percent: pct(p4), color: '#f59e0b', children: vasChildren },
    { name: '其他费用', amount: otherTotal, percent: pct(otherTotal), color: '#ec4899', children: otherChildren },
    { name: '设备保险费', amount: p5, percent: pct(p5), color: '#eab308', children: [] },
    { name: '账期成本', amount: fundingCost, percent: pct(fundingCost), color: '#22c55e', children: [] },
    { name: '预估总毛利', amount: totalGrossProfit.value, percent: pct(totalGrossProfit.value), color: '#10b981', children: [] },
  ]
})

/** 设备申报总价值货币格式展示（千分位 + 两位小数） */
const formattedDeclaredValue = computed(() =>
  formatMoney(Number(declaredValue.value) || 0)
)
function onDeclaredValueFocus() {
  declaredValueInput.value = formatMoney(Number(declaredValue.value) || 0)
}
function onDeclaredValueInput(e: Event) {
  declaredValueInput.value = (e.target as HTMLInputElement).value
}
function onDeclaredValueBlur() {
  const raw = declaredValueInput.value
  declaredValueInput.value = null
  if (raw == null || String(raw).trim() === '') {
    declaredValue.value = 0
    return
  }
  const stripped = String(raw).replace(/,/g, '')
  const num = parseFloat(stripped)
  if (isNaN(num) || num < 0) {
    declaredValue.value = 0
    return
  }
  declaredValue.value = Math.round(num * 100) / 100
}

function formatMoney(n: number): string {
  return n.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatMoneyCompact(n: number): string {
  if (n >= 10000) return (n / 10000).toFixed(1) + '万'
  return n.toLocaleString('zh-CN', { maximumFractionDigits: 0 })
}

function resetForm() {
  laborCostItems.value = [
    { id: nextLaborId(), serviceType: '现场勘察', serviceDesc: '搬迁前设备状态记录与风险评估', quantity: 1, unitPrice: 990 },
    { id: nextLaborId(), serviceType: '项目管理', serviceDesc: '全程项目协调、进度把控与资源调度', quantity: 1, unitPrice: 1450 }
  ]
  valueAddedItems.value = [
    { id: nextValueAddedId(), itemName: '停机测试服务', serviceDesc: '搬迁前后系统连通性与压力测试', unit: '台', quantity: 10, unitPrice: 20 },
    { id: nextValueAddedId(), itemName: '设备上下架', serviceDesc: '服务器、存储等设备的标准上下架实施', unit: '台', quantity: 40, unitPrice: 15 },
    { id: nextValueAddedId(), itemName: '拆布垂直线缆', serviceDesc: '机柜内垂直线缆的拆除与敷设', unit: '根', quantity: 1, unitPrice: 6.5 },
    { id: nextValueAddedId(), itemName: '拆布水平线缆', serviceDesc: '机房水平线缆的拆除与敷设', unit: '根', quantity: 1, unitPrice: 18 }
  ]
  equipmentRentalItems.value = [createEmptyEquipmentRentalRow()]
  equipmentPurchaseItems.value = [createEmptyEquipmentPurchaseRow()]
  externalLaborItems.value = [createEmptyExternalLaborRow()]
  packagingTiers.value = DEFAULT_PACKAGING_TIERS.map((t) => ({ ...t }))
  packagingItems.value = [createDefaultPackagingItem()]
  syncPackagingFromEquipment()
  manualHandlingTiers.value = DEFAULT_MANUAL_HANDLING_TIERS.map((t) => ({ ...t }))
  manualHandlingItems.value = [createDefaultManualHandlingItem()]
  sameParkTiers.value = DEFAULT_SAME_PARK_TIERS.map((t) => ({ ...t }))
  sameParkItems.value = [createDefaultSameParkItem()]
  // 重置批次
  batchIdCounter = 0
  logisticsIdCounter = 0
  const defaultItem = createDefaultLogisticsItem()
  logisticsBatches.value = [{
    id: nextBatchId(),
    name: '第一批次',
    date: new Date().toISOString().split('T')[0],
    desc: '',
    items: [defaultItem]
  }]
  activeBatchId.value = logisticsBatches.value[0].id
  vehicleOverrides.value = {}
  globalParams.value = { vatRate: 6, paymentCycle: 0, profitRate: 0, fundingCostRate: 3 }
  if (vehicleOptions.value.length) {
    logisticsBatches.value[0].items[0].vehicleId = vehicleOptions.value[0].id
    logisticsBatches.value[0].items[0].kmPrice = parseRangeToMax(vehicleOptions.value[0].km_price)
  }
  insuranceRatePermille.value = 6
  ElMessage.success('已重置为默认配置')
}

function closeEquipmentNameDropdown() {
  equipmentNameDropdownId.value = null
  equipmentNameDropdownRowRef.value = null
  equipmentNameDropdownRect.value = null
}
onMounted(() => {
  loadVehicles()
  loadRelocationCompanyLogo()
  document.addEventListener('click', closeEquipmentNameDropdown)
})
onUnmounted(() => {
  document.removeEventListener('click', closeEquipmentNameDropdown)
})

// ---------- 生成正式报价单弹窗（与驻场预览报价单一致） ----------
const showQuotationView = ref(false)
const quotationContentRef = ref<HTMLElement | null>(null)
const quotationZoomLevel = ref(100)
const quotationMaximized = ref(false)
const quotationWindowSize = ref({ width: 1400, height: 800 })
const quotationCustomerSelect = ref('default')
const quotationPriceLayout = ref('with-tax')
const quotationTemplate = ref('classic')

const quotationWindowStyle = computed(() => {
  if (quotationMaximized.value) {
    return {
      left: '0px',
      top: '0px',
      width: '100vw',
      height: 'calc(100vh - 70px)',
      transform: 'none'
    }
  }
  return {
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    width: `${quotationWindowSize.value.width}px`,
    height: `${quotationWindowSize.value.height}px`
  }
})

function quotationZoomIn() {
  if (quotationZoomLevel.value < 150) quotationZoomLevel.value += 10
}
function quotationZoomOut() {
  if (quotationZoomLevel.value > 50) quotationZoomLevel.value -= 10
}
function toggleQuotationMaximize() {
  quotationMaximized.value = !quotationMaximized.value
}

const QUOTATION_COMPANY = reactive({ name: '源晨动力', address: '北京市海淀区高里掌路1号院11号楼3单元2层' })

// 搬迁报价单 Logo 相关
const relocationLogoInputRef = ref<HTMLInputElement | null>(null)
const relocationCustomLogoUrl = ref<string>('')

function triggerRelocationLogoUpload() {
  relocationLogoInputRef.value?.click()
}

function handleRelocationLogoUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 2MB')
    return
  }
  const reader = new FileReader()
  reader.onload = (e) => {
    relocationCustomLogoUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
  input.value = ''
}

// 从个人设置加载公司 Logo 作为默认
async function loadRelocationCompanyLogo() {
  try {
    const res = await axios.get(`${API_URL}/user-profile/companies`)
    if (res.data && res.data.length > 0) {
      const company = res.data[0]
      if (company.company_logo && !relocationCustomLogoUrl.value) {
        relocationCustomLogoUrl.value = company.company_logo
      }
      // 同步更新公司名称和地址
      if (company.company_name) QUOTATION_COMPANY.name = company.company_name
      if (company.company_address) QUOTATION_COMPANY.address = company.company_address
    }
  } catch (err) {
    // 静默失败，使用默认 Logo
  }
}

const QUOTATION_TERMS = [
  '服务范围：乙方根据甲方需求提供机房整体搬迁服务，包括设备清点、下线拆卸、包装运输、上架安装、系统恢复、测试验证及交付验收。',
  '甲方责任：甲方应提供搬运现场的配合人员，并确保迁入地的电力、网络等基础设施已就绪。'
]

const COST_NAME_DESC: Record<string, string> = {
  '人工服务费': '现场勘察、项目管理等人工服务。',
  '包装耗材费': '包装材料、耗材及按 U 数梯度计费。',
  '物流运输费': '车辆配送、人工搬运及同园区搬迁。',
  '增值服务费': '停机测试、设备上下架、线缆拆布等。',
  '其他费用': '专用设备租用、外部人工调用、专用设备采购。',
  '设备保险费': '搬迁过程中设备损坏保险。',
  '账期成本': '基于账期与资金成本率核算。',
  '预估总毛利': '按利润率核算的预估毛利。'
}

function generateOrderNo(): string {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const r = Math.floor(1000 + Math.random() * 9000)
  return `RLOC-${y}${m}${day}-${r}`
}

const quotationData = computed(() => {
  const vatRate = (globalParams.value.vatRate ?? 6) / 100
  const total = finalProjectAmount.value
  const items = costBreakdown.value
    .filter((x) => x.amount > 0)
    .map((x, i) => ({
      id: i + 1,
      title: x.name,
      desc: COST_NAME_DESC[x.name] || '',
      unit: '项',
      qty: 1,
      price: x.amount
    }))
  const subTotal = items.reduce((sum, it) => sum + it.qty * it.price, 0)
  return {
    companyName: QUOTATION_COMPANY.name,
    address: QUOTATION_COMPANY.address,
    customer: {
      name: quotationCustomerName.value || '客户',
      locationLines: quotationCustomerLocationLines.value
    },
    meta: {
      orderNo: quotationOrderNo.value,
      date: new Date().toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/'),
      validUntil: new Date(Date.now() + 30 * 24 * 60 * 60 * 1000).toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' }).replace(/\//g, '/')
    },
    items,
    subTotal,
    taxRate: vatRate,
    taxRatePercent: (vatRate * 100).toFixed(0),
    finalTotal: total,
    terms: QUOTATION_TERMS
  }
})

const quotationOrderNo = ref('')
const quotationCustomerName = ref('') // 可后续在报价单页或项目概况中绑定
const quotationCustomerLocationLines = ref<string[]>(['请填写客户所在地'])

// 将报价项按阶段分组
const groupedQuotationItems = computed(() => {
  const items = quotationData.value.items
  const groups = [
    { name: '准备阶段', items: [] as typeof items },
    { name: '物理搬迁', items: [] as typeof items },
    { name: '安装保障', items: [] as typeof items }
  ]

  // 根据名称分类到不同阶段
  const prepKeywords = ['勘察', '评估', '管理', '方案', '规划']
  const moveKeywords = ['搬迁', '运输', '包装', '拆卸', '上架', '下架', '物流']
  const installKeywords = ['安装', '联调', '测试', '保险', '验收']

  items.forEach(item => {
    const title = item.title || ''
    if (prepKeywords.some(k => title.includes(k))) {
      groups[0].items.push(item)
    } else if (moveKeywords.some(k => title.includes(k))) {
      groups[1].items.push(item)
    } else if (installKeywords.some(k => title.includes(k))) {
      groups[2].items.push(item)
    } else {
      // 默认放到物理搬迁
      groups[1].items.push(item)
    }
  })

  // 过滤掉空分组
  return groups.filter(g => g.items.length > 0)
})

watch(showQuotationView, (visible) => {
  if (visible) {
    quotationOrderNo.value = generateOrderNo()
    const origins = routeLocations.value.filter((l) => l.address?.trim())
    if (origins.length >= 2) {
      const from = origins[0].address?.trim() || ''
      const to = origins[origins.length - 1].address?.trim() || ''
      quotationCustomerLocationLines.value = [from, to].filter(Boolean).length ? [from, to] : ['请填写客户所在地']
    } else if (origins.length === 1) {
      quotationCustomerLocationLines.value = [origins[0].address?.trim() || '请填写客户所在地']
    } else {
      quotationCustomerLocationLines.value = ['请填写客户所在地']
    }
  }
})

function closeQuotationView() {
  showQuotationView.value = false
}

function handleQuotationPrint() {
  window.print()
}

async function handleExportQuotationPdf() {
  const el = quotationContentRef.value
  if (!el) {
    ElMessage.warning('无法获取报价单内容')
    return
  }
  try {
    ElMessage.info('正在生成 PDF…')
    const originalTransform = el.style.transform
    el.style.transform = 'scale(1)'
    const canvas = await html2canvas(el, {
      scale: 2,
      useCORS: true,
      logging: false,
      backgroundColor: '#ffffff'
    })
    el.style.transform = originalTransform
    const imgData = canvas.toDataURL('image/png')
    const pdf = new jsPDF({ unit: 'mm', format: 'a4' })
    const pageW = pdf.internal.pageSize.getWidth()
    const pageH = pdf.internal.pageSize.getHeight()
    const imgRatio = canvas.height / canvas.width
    const pageRatio = pageH / pageW
    const fitW = imgRatio > pageRatio ? pageH / imgRatio : pageW
    const fitH = imgRatio > pageRatio ? pageH : pageW * imgRatio
    pdf.addImage(imgData, 'PNG', 0, 0, fitW, fitH)
    const filename = `搬迁服务报价单_${quotationData.value.meta.orderNo}.pdf`
    pdf.save(filename)
    ElMessage.success('PDF 已导出')
  } catch (e) {
    console.error(e)
    ElMessage.error('导出 PDF 失败')
  }
}

function onGenerateQuote() {
  if (props.embedded) {
    activeTab.value = 4
  } else {
    showQuotationView.value = true
  }
}

function onExportExcel() {
  ElMessage.info('导出 Excel 明细功能待对接')
}

defineExpose({
  activeTab,
  onGenerateQuote,
})
</script>

<style scoped>
.relocation-calculator-page {
  padding: 0 1.5rem 1.5rem;
  min-height: 100%;
  background: #0f172a;
  color: #e2e8f0;
}

.relocation-calculator-page.embedded-mode {
  background: transparent;
  min-height: 0;
  height: 100%;
  overflow-y: auto;
  border-radius: 12px;
}

/* ---------- 内联报价视图（嵌入模式 tab4） ---------- */
.inline-quotation-view {
  margin-top: 1rem;
}

.inline-quotation-main {
  display: grid;
  grid-template-columns: 1fr 320px;
  gap: 1.5rem;
  min-height: 600px;
}

.inline-quotation-preview {
  display: flex;
  flex-direction: column;
  background: #111827;
  border: 1px solid #1e293b;
  border-radius: 12px;
  overflow: hidden;
}

.inline-quotation-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #1e293b;
  background: #0f172a;
  flex-shrink: 0;
}

.inline-quotation-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
}

.inline-quotation-actions {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.inline-quotation-scroll {
  flex: 1;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  justify-content: center;
  background: #1a1f2e;
}

.inline-quotation-sidebar {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  background: #111827;
  border: 1px solid #1e293b;
  border-radius: 12px;
  padding: 1.25rem;
  overflow-y: auto;
  max-height: 800px;
}

@media (max-width: 1200px) {
  .inline-quotation-main {
    grid-template-columns: 1fr;
  }
  .inline-quotation-sidebar {
    max-height: none;
  }
}

.page-header {
  margin-bottom: 1.5rem;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-bottom: 0.75rem;
  font-size: 0.875rem;
}

.breadcrumb-item {
  color: #94a3b8;
}

.breadcrumb-item.active {
  color: #f1f5f9;
  font-weight: 500;
}

.breadcrumb-separator {
  font-size: 1rem;
  color: #64748b;
}

.header-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  flex-wrap: wrap;
  gap: 1rem;
}

.page-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.ai-badge {
  font-size: 0.75rem;
  font-weight: 500;
  color: #38bdf8;
  background: rgba(56, 189, 248, 0.15);
  padding: 0.2rem 0.5rem;
  border-radius: 9999px;
}

.page-subtitle {
  font-size: 0.875rem;
  color: #94a3b8;
  margin: 0;
}

.header-buttons.actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.header-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background-color: #1e293b;
  border: 1px solid #334155;
  color: #cbd5e1;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.header-btn:hover {
  background-color: #334155;
  color: white;
}

.header-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.add-row-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  margin-left: auto;
  padding: 0.375rem 0.75rem;
  background-color: rgba(19, 91, 236, 0.15);
  border: 1px solid rgba(19, 91, 236, 0.4);
  border-radius: 0.5rem;
  color: #60a5fa;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.add-row-btn:hover {
  background-color: rgba(19, 91, 236, 0.25);
  border-color: rgba(19, 91, 236, 0.6);
}

.add-row-btn .material-symbols-outlined {
  font-size: 1rem;
}

.btn-icon {
  font-size: 1.1rem;
  vertical-align: middle;
  margin-right: 0.25rem;
}

.calculator-content {
  display: flex;
  gap: 2rem;
  max-width: 100%;
  width: 100%;
  margin: 0;
}

.left-section {
  flex: 1;
  min-width: 0;
}

.tabs-row {
  margin-bottom: 1.5rem;
}

.tabs {
  display: flex;
  gap: 2rem;
  border-bottom: 1px solid #1e293b;
}

.tab {
  background: none;
  border: none;
  border-bottom: 2px solid transparent;
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 700;
  padding: 0.75rem 0;
  cursor: pointer;
}

.tab:hover {
  color: #e2e8f0;
}

.tab.active {
  color: #f1f5f9;
  border-bottom-color: #38bdf8;
}

/* 搬迁路径配置 */
.route-config-section {
  margin-bottom: 1.5rem;
}

.route-config-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.route-config-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.25rem 0;
}

.route-config-icon {
  font-size: 1.25rem;
  color: #38bdf8;
}

.route-config-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.route-path-list {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.route-path-line {
  position: absolute;
  left: 1.4375rem;
  top: 2.5rem;
  bottom: 2.5rem;
  width: 2px;
  background: linear-gradient(to bottom, rgba(59, 130, 246, 0.5), #334155, rgba(16, 185, 129, 0.5));
  z-index: 0;
  pointer-events: none;
}

@media (max-width: 640px) {
  .route-path-line {
    display: none;
  }
}

.route-location-row {
  position: relative;
  z-index: 1;
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1rem;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  background: #0f172a;
  transition: border-color 0.2s, background 0.2s;
}

.route-location-row.confirmed {
  background: #1e293b;
  border-color: #334155;
}

.route-location-row.has-dropdown {
  z-index: 100;
}

.route-type-badge {
  width: 1.75rem;
  height: 1.75rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  border: 2px solid;
  background: #0f172a;
  font-size: 0.625rem;
  font-weight: 700;
}

.route-type-badge.origin {
  border-color: #3b82f6;
  color: #3b82f6;
}

.route-type-badge.destination {
  border-color: #10b981;
  color: #10b981;
}

.route-location-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.route-location-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}

.route-location-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.route-tier-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.625rem;
  font-weight: 700;
}

.route-tier-badge.tier-1 {
  background: rgba(168, 85, 247, 0.2);
  color: #c084fc;
  border: 1px solid rgba(168, 85, 247, 0.3);
}

.route-tier-badge.tier-remote {
  background: rgba(249, 115, 22, 0.2);
  color: #fb923c;
  border: 1px solid rgba(249, 115, 22, 0.3);
}

.route-tier-badge.tier-other {
  background: rgba(59, 130, 246, 0.2);
  color: #60a5fa;
  border: 1px solid rgba(59, 130, 246, 0.3);
}

.route-address-row {
  display: flex;
  gap: 0.5rem;
}

.route-address-input-wrap {
  position: relative;
  flex: 1;
  min-width: 0;
}

.route-address-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.625rem 2.5rem 0.625rem 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.route-address-input::placeholder {
  color: #64748b;
}

.route-address-input:focus {
  outline: none;
  border-color: #38bdf8;
}

.route-map-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  padding: 0.375rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  transition: color 0.2s;
}

.route-map-btn:hover {
  color: #38bdf8;
}

.route-map-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* 内联搜索下拉框 */
.route-inline-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 0.25rem;
  background: #1e293b;
  border: 1px solid #475569;
  border-radius: 0.5rem;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.5);
  z-index: 9999;
  max-height: 20rem;
  overflow-y: auto;
}

.route-inline-loading {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  color: #64748b;
  font-size: 0.8125rem;
}

.route-inline-loading .spinning {
  animation: spin 1s linear infinite;
  font-size: 1rem;
}

.route-inline-item {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.625rem 0.75rem;
  cursor: pointer;
  transition: background-color 0.15s;
}

.route-inline-item:hover {
  background: rgba(59, 130, 246, 0.15);
}

.route-inline-icon {
  flex-shrink: 0;
  font-size: 1rem;
  color: #3b82f6;
  margin-top: 0.125rem;
}

.route-inline-text {
  flex: 1;
  min-width: 0;
}

.route-inline-addr {
  font-size: 0.8125rem;
  color: #e2e8f0;
  line-height: 1.3;
  word-break: break-all;
}

.route-inline-meta {
  font-size: 0.6875rem;
  color: #64748b;
  margin-top: 0.125rem;
}

/* 选中地址显示样式 */
.route-selected-addr {
  max-width: 50%;
}

.route-selected-addr .place-icon {
  color: #3b82f6;
}

.route-selected-text {
  color: #94a3b8;
  font-size: 0.6875rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 20rem;
}

.route-confirmed-info {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
  font-size: 0.6875rem;
}

.route-info-item {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  color: #64748b;
}

.route-info-icon {
  font-size: 0.75rem;
}

.route-info-icon.success {
  color: #10b981;
}

.route-mono {
  font-family: ui-monospace, monospace;
  color: #cbd5e1;
}

.route-text {
  color: #cbd5e1;
}

.route-delete-btn {
  padding: 0.5rem;
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  transition: color 0.2s;
  flex-shrink: 0;
}

.route-delete-btn:hover {
  color: #f87171;
}

.route-delete-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* 地图弹窗 */
.route-map-overlay {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.8);
  backdrop-filter: blur(4px);
}

.route-map-modal {
  width: 100%;
  max-width: 42rem;
  background: #1e293b;
  border-radius: 1rem;
  border: 1px solid #334155;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.route-map-modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #334155;
  background: rgba(30, 41, 59, 0.5);
}

.route-map-modal-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.route-map-modal-title .material-symbols-outlined {
  color: #38bdf8;
}

.route-map-close {
  padding: 0.25rem;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  transition: color 0.2s;
}

.route-map-close:hover {
  color: #f1f5f9;
}

.route-map-modal-body {
  padding: 1rem;
  background: #0f172a;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.route-map-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
}

.route-map-search-icon {
  position: absolute;
  left: 0.75rem;
  font-size: 1.125rem;
  color: #64748b;
}

.route-map-search-input {
  width: 100%;
  box-sizing: border-box;
  padding: 0.625rem 1rem 0.625rem 2.5rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  color: #f1f5f9;
  font-size: 0.875rem;
  transition: border-color 0.2s;
}

.route-map-search-input:focus {
  outline: none;
  border-color: #38bdf8;
}

.route-map-preview {
  aspect-ratio: 16/10;
  background: #1e293b;
  border-radius: 0.75rem;
  border: 1px solid #334155;
  overflow: hidden;
  position: relative;
  min-height: 280px;
}

.route-map-inner {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  min-height: 280px;
}

.route-map-loading {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.85);
  color: #94a3b8;
  font-size: 0.875rem;
}

.route-map-tiles-hint {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  padding: 0.5rem;
  pointer-events: none;
  z-index: 10;
}

.route-map-tiles-hint-content {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  background: rgba(245, 158, 11, 0.9);
  color: #1e293b;
  font-size: 0.75rem;
  border-radius: 0.375rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
}

.route-map-tiles-hint-content .material-symbols-outlined {
  font-size: 1rem;
  flex-shrink: 0;
}

.route-map-confirm-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.5rem 0.75rem;
  margin-top: 0.5rem;
  background: rgba(34, 197, 94, 0.1);
  border: 1px solid rgba(34, 197, 94, 0.3);
  border-radius: 0.5rem;
}

.route-map-pending-text {
  font-size: 0.8125rem;
  color: #e2e8f0;
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.route-map-confirm-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: #22c55e;
  color: #fff;
  border: none;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  flex-shrink: 0;
}

.route-map-confirm-btn:hover {
  background: #16a34a;
}

.route-map-confirm-btn .material-symbols-outlined {
  font-size: 1rem;
}

.route-map-placeholder {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  color: #64748b;
  font-size: 0.75rem;
}

.route-map-placeholder-hint {
  font-size: 0.6875rem;
  color: #475569;
}

.route-map-pin {
  font-size: 2.5rem;
  color: #3b82f6;
}

.route-map-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 10rem;
  overflow-y: auto;
}

.route-map-results-hint {
  font-size: 0.8125rem;
  color: #64748b;
  padding: 0.5rem 0;
  margin: 0;
}

.route-map-results-title {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  color: #22c55e;
  padding: 0.25rem 0 0.5rem;
  margin: 0;
  font-weight: 500;
}

.route-map-results-title .material-symbols-outlined {
  font-size: 1rem;
}

.route-map-result-item {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  width: 100%;
  padding: 0.75rem;
  text-align: left;
  background: rgba(34, 197, 94, 0.05);
  border: 1px solid rgba(34, 197, 94, 0.2);
  border-radius: 0.5rem;
  color: inherit;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.route-map-result-item:hover {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.4);
}

.route-result-icon {
  font-size: 1.125rem;
  color: #22c55e;
  flex-shrink: 0;
}

.route-result-addr {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.route-result-meta {
  font-size: 0.625rem;
  color: #64748b;
  text-transform: uppercase;
  margin-top: 0.125rem;
}

.route-tip-box {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(249, 115, 22, 0.08);
  border: 1px solid rgba(249, 115, 22, 0.2);
  border-radius: 0.75rem;
}

.route-tip-icon {
  font-size: 1.125rem;
  color: #fb923c;
  flex-shrink: 0;
}

.route-tip-content {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.6;
}

.route-tip-title {
  color: #fb923c;
}

.route-tip-highlight {
  color: #e2e8f0;
}

.config-section {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.card.panel {
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1.5rem;
}

.card-title-row,
.title-with-icon {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.card-icon {
  font-size: 1.25rem;
  color: #94a3b8;
}

.card-icon.primary {
  color: #38bdf8;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0;
}

.config-grid.two-cols {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

/* 人工服务费 */
.labor-cost-panel,
.value-added-panel {
  padding: 1.5rem;
}

/* 其他费用 */
.other-cost-panel {
  padding: 0 0 1.5rem;
}
.other-cost-header {
  padding: 1rem 1.25rem 0;
  margin-bottom: 0;
}
.other-cost-tabs-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.75rem;
  padding: 0 1.25rem;
  border-bottom: 1px solid #2d3748;
  background-color: #151b26;
}
.other-cost-tabs {
  display: flex;
}
.other-cost-tab {
  padding: 0.75rem 1.25rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #92a4c9;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}
.other-cost-tab:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.05);
}
.other-cost-tab.active {
  color: #fff;
  border-bottom-color: #135bec;
  background-color: rgba(19, 91, 236, 0.08);
}
.other-cost-table-wrap {
  padding: 1.25rem;
  overflow-x: auto;
}

.equipment-name-cell {
  min-width: 0;
}
.equipment-name-combobox {
  position: relative;
  width: 100%;
}
.equipment-name-input {
  width: 100%;
  padding-right: 1.25rem;
  box-sizing: border-box;
}
.equipment-name-caret {
  position: absolute;
  right: 0.25rem;
  top: 50%;
  transform: translateY(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  pointer-events: auto;
  cursor: pointer;
  color: #94a3b8;
  padding: 0 0.125rem;
}
.equipment-name-caret:hover {
  color: #e2e8f0;
}
.equipment-name-caret .material-symbols-outlined {
  font-size: 0.875rem;
  font-variation-settings: 'FILL' 0, 'wght' 400, 'GRAD' 0, 'opsz' 20;
}
.equipment-name-dropdown {
  position: absolute;
  left: 0;
  right: 0;
  top: 100%;
  margin-top: 2px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  z-index: 10;
  overflow: hidden;
}
.equipment-name-dropdown-fixed {
  position: fixed;
  z-index: 9999;
}
.equipment-name-option {
  display: block;
  width: 100%;
  padding: 0.4rem 0.75rem;
  font-size: 0.8125rem;
  color: #e2e8f0;
  background: none;
  border: none;
  text-align: left;
  cursor: pointer;
  transition: background 0.15s;
}
.equipment-name-option:hover {
  background: rgba(56, 189, 248, 0.15);
  color: #fff;
}

.labor-cost-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.labor-cost-header .actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.labor-cost-table-wrap {
  overflow-x: auto;
}

.labor-cost-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.labor-cost-table thead tr {
  border-bottom: 1px solid #334155;
}

.labor-cost-table th {
  padding-bottom: 0.75rem;
  font-weight: 500;
  font-size: 0.6875rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.labor-cost-table th.col-type { width: 18%; }
.labor-cost-table th.col-desc { width: 28%; }
.labor-cost-table th.col-unit { width: 8%; text-align: center; }
.labor-cost-table th.col-qty { width: 10%; text-align: center; }
.labor-cost-table th.col-price { width: 12%; text-align: center; }
.labor-cost-table th.col-total { width: 14%; text-align: right; }
.labor-cost-table th.col-action { width: 3rem; }

.labor-cost-row {
  border-bottom: 1px solid rgba(51, 65, 85, 0.5);
}

.labor-cost-row td {
  padding: 0.75rem 0.5rem 0.75rem 0;
  vertical-align: middle;
}

.labor-cost-row td:first-child {
  padding-left: 0;
}

.labor-input {
  width: 100%;
  min-width: 0;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 0.25rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  padding: 0.375rem 0.5rem;
  transition: border-color 0.2s, box-shadow 0.2s;
}

.labor-input:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.3);
}

.labor-select {
  cursor: pointer;
  appearance: none;
}

.labor-input-num {
  width: 4rem;
  max-width: 100%;
  text-align: center;
}

.labor-input-readonly {
  display: inline-block;
  min-width: 3rem;
  cursor: default;
}

.unit-cell {
  text-align: center;
  color: #94a3b8;
  font-size: 0.875rem;
}

.qty-cell,
.price-cell {
  text-align: center;
}

.total-cell {
  text-align: right;
  font-weight: 700;
  color: #f1f5f9;
}

.action-cell {
  text-align: right;
  padding-right: 0;
}

.labor-cost-row .row-delete-btn {
  color: #64748b;
}

.labor-cost-row .row-delete-btn:hover {
  color: #f87171;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.field-label {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.input-with-suffix {
  display: flex;
  align-items: center;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: hidden;
}

.field-input {
  flex: 1;
  background: transparent;
  border: none;
  color: #f1f5f9;
  padding: 0.5rem 1rem;
  font-size: 0.875rem;
}

.field-input:focus {
  outline: none;
}

.input-suffix {
  padding: 0 0.75rem;
  font-size: 0.875rem;
  color: #64748b;
}

.packaging-section .card.panel {
  margin-bottom: 0;
}

.packaging-detail-table thead th {
  padding: 0.75rem 0.5rem 0.75rem 0;
  text-align: left;
  vertical-align: middle;
}

.packaging-detail-table thead th:first-child {
  padding-left: 0;
}

.packaging-detail-table thead th.col-unit,
.packaging-detail-table thead th.col-qty,
.packaging-detail-table thead th.col-price {
  text-align: center;
}

.packaging-detail-table thead th.col-total {
  text-align: right;
}

.packaging-detail-table .labor-cost-row td {
  vertical-align: middle;
}

.packaging-detail-table .qty-cell .labor-input-num {
  margin: 0 auto;
}

.packaging-tier-select {
  min-width: 6rem;
}

.packaging-summary-row {
  border-top: 1px solid #334155;
}
.packaging-summary-row td {
  padding: 0.75rem 0.5rem;
  font-size: 0.875rem;
}
.packaging-summary-row .summary-label {
  font-weight: 600;
  color: #94a3b8;
  text-align: right;
}
.packaging-summary-row .summary-qty {
  font-weight: 600;
  color: #e2e8f0;
  text-align: right;
}
.packaging-summary-row .summary-total {
  font-weight: 600;
  color: #38bdf8;
}

.packaging-section .actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.sync-equipment-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: #22c55e;
  background: rgba(34, 197, 94, 0.15);
  border: 1px solid rgba(34, 197, 94, 0.4);
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.sync-equipment-btn:hover {
  background: rgba(34, 197, 94, 0.25);
  border-color: #22c55e;
}
.sync-equipment-btn .material-symbols-outlined {
  font-size: 1rem;
}

.packaging-validation-alert {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.8125rem;
  color: #fbbf24;
  background: rgba(251, 191, 36, 0.1);
  border: 1px solid rgba(251, 191, 36, 0.3);
  border-radius: 0.5rem;
}
.packaging-validation-alert .alert-icon {
  font-size: 1.125rem;
  flex-shrink: 0;
}
.unknown-tier-row {
  background: rgba(251, 191, 36, 0.08) !important;
}
.unknown-tier-select {
  border-color: #f59e0b !important;
  color: #fbbf24 !important;
}

.packaging-tiers-title {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  margin-top: 1rem;
  margin-bottom: 0.75rem;
}

.packaging-section .section-title-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.section-hint {
  font-size: 0.75rem;
  color: #64748b;
}

.packaging-tiers {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 0.75rem;
}

.tier-card {
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  padding: 1rem;
  text-align: center;
  cursor: pointer;
  transition: border-color 0.2s, background 0.2s;
}

.tier-card:hover {
  border-color: #38bdf8;
}

.tier-card.selected {
  border-color: #38bdf8;
  background: rgba(56, 189, 248, 0.1);
}

.tier-range {
  font-size: 0.75rem;
  color: #94a3b8;
  margin: 0 0 0.25rem 0;
}

.tier-price-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  margin: 0;
}

.tier-price-prefix {
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
}

.tier-price-input {
  width: 4rem;
  text-align: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: #f1f5f9;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  padding: 0.25rem 0.5rem;
  -moz-appearance: textfield;
}

.tier-price-input::-webkit-outer-spin-button,
.tier-price-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.tier-price-input:focus {
  outline: none;
  border-color: #38bdf8;
}

.tier-label {
  font-size: 0.625rem;
  color: #64748b;
  margin: 0.25rem 0 0 0;
}

/* 车辆与物流配送：卡片头部（仅标题） */
.logistics-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #1e293b;
}
.logistics-card-header .header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.logistics-card-header .card-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
}

/* 标签栏：与人力硬成本（社保规则/公积金规则）一致 */
.logistics-tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #2d3748;
  background-color: #151b26;
  padding-right: 12px;
}

.logistics-header-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.split-batch-switch-label {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  user-select: none;
  color: #94a3b8;
  font-size: 0.875rem;
}

.split-batch-switch-label .switch-label-text {
  cursor: pointer;
}

.logistics-flat-layout {
  border: 1px solid #334155;
  border-radius: 0.75rem;
  overflow: hidden;
  background: #0f172a;
}

.logistics-tabs {
  display: flex;
}
.logistics-tab-btn {
  padding: 0.75rem 1.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #92a4c9;
  background: transparent;
  border: none;
  border-bottom: 2px solid transparent;
  cursor: pointer;
  transition: all 0.2s;
}
.logistics-tab-btn:hover {
  color: #fff;
  background-color: rgba(255, 255, 255, 0.05);
}
.logistics-tab-btn.active {
  color: #fff;
  border-bottom-color: #135bec;
  background-color: rgba(19, 91, 236, 0.08);
}

.logistics-tab-content {
  padding: 1.25rem;
  overflow-x: auto;
}

.logistics-panel .labor-cost-table-wrap {
  margin-bottom: 0;
}

/* 车辆与物流配送价格表：表头不换行，列宽保证单行显示 */
.logistics-detail-table thead th {
  white-space: nowrap;
}
.logistics-detail-table thead th.col-type {
  min-width: 10rem;
}
.logistics-detail-table thead th.col-route {
  width: auto;
  white-space: nowrap;
}
.logistics-detail-table .route-cell {
  vertical-align: middle;
}
.route-path-inline {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}
.route-path-link-select {
  appearance: none;
  -webkit-appearance: none;
  background: transparent;
  border: none;
  color: #38bdf8;
  font-size: inherit;
  font-weight: 500;
  cursor: pointer;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  min-width: 1.5em;
  text-align: center;
}
.route-path-link-select::-ms-expand {
  display: none;
}
.route-path-link-select:hover {
  color: #7dd3fc;
  background: rgba(56, 189, 248, 0.1);
}
.route-path-link-select.empty {
  color: #94a3b8;
}
.route-path-link-select.empty:hover {
  color: #cbd5e1;
}
.route-path-arrow {
  color: #64748b;
  font-size: 0.875rem;
  flex-shrink: 0;
  user-select: none;
}
.route-distance-loading {
  font-size: 0.75rem;
  color: #3b82f6;
  display: block;
  margin-top: 0.25rem;
}

/* ========== 批次管理布局 ========== */
.add-batch-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 0.5rem;
  color: #3b82f6;
  font-size: 0.75rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}
.add-batch-btn:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: #3b82f6;
}
.add-batch-btn .material-symbols-outlined {
  font-size: 0.875rem;
}

/* ===== 拆分批次：卡片式布局 ===== */
.batch-cards-layout {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

/* 单个批次卡片 */
.batch-card {
  background: rgba(22, 34, 46, 0.6);
  border-radius: 0.75rem;
  border: 1px solid #2e4b6b;
  overflow: hidden;
  transition: border-color 0.2s;
}
.batch-card.active {
  border-color: rgba(0, 122, 255, 0.5);
}

/* 批次卡片顶部：属性区域 */
.batch-card-top {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 1.25rem 1.5rem;
}

.batch-card-fields {
  flex: 1;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.75rem 1.5rem;
}
.batch-field {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}
.batch-field.batch-field-wide {
  grid-column: 1 / -1;
}
.batch-field-label {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.03em;
}
.batch-field-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: rgba(15, 25, 35, 0.5);
  border: 1px solid #2e4b6b;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.8125rem;
  box-sizing: border-box;
  transition: border-color 0.2s;
}
.batch-field-input:focus {
  outline: none;
  border-color: #007aff;
  box-shadow: 0 0 0 1px rgba(0, 122, 255, 0.3);
}

.batch-card-delete {
  padding: 0.5rem;
  background: transparent;
  border: none;
  color: #475569;
  cursor: pointer;
  border-radius: 0.375rem;
  transition: color 0.2s;
  flex-shrink: 0;
  margin-top: 1.25rem;
}
.batch-card-delete:hover:not(:disabled) {
  color: #ef4444;
}
.batch-card-delete:disabled {
  opacity: 0.3;
  cursor: not-allowed;
}
.batch-card-delete .material-symbols-outlined {
  font-size: 1.125rem;
}

/* 批次卡片：车型条目区域 */
.batch-card-items {
  padding: 0 1.5rem;
}
.batch-card-items-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding-bottom: 0.625rem;
  border-top: 1px solid rgba(46, 75, 107, 0.3);
  padding-top: 0.75rem;
}
.batch-card-items-title {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 600;
  color: #94a3b8;
}
.batch-card-items-title .material-symbols-outlined {
  font-size: 1rem;
  color: #64748b;
}

/* 批次卡片内单条车型 */
.batch-card-item-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.batch-card-item-row {
  display: flex;
  align-items: center;
  gap: 0.625rem;
  padding: 0.625rem 0.75rem;
  background: rgba(15, 25, 35, 0.3);
  border: 1px solid rgba(46, 75, 107, 0.3);
  border-radius: 0.5rem;
}
.bc-item-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  min-width: 0;
  flex-shrink: 1;
}
.bc-item-field:first-child {
  /* 车型列：自适应内容宽度，不过度拉伸 */
  flex: 0 1 auto;
}
.bc-item-field:nth-child(2) {
  /* 运输路径列：左侧留出间距避免与车型交叉 */
  flex: 0 1 auto;
  margin-left: 1rem;
}
.bc-item-label {
  font-size: 0.625rem;
  color: #64748b;
  font-weight: 500;
  white-space: nowrap;
}
.bc-item-nums {
  display: flex;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}
.bc-num-field {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  flex: 1;
  min-width: 0;
}
.bc-num-field.bc-num-narrow {
  flex: 0 0 3.5rem;
  max-width: 3.5rem;
}
.bc-item-total-field {
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  align-items: flex-end;
}
.bc-item-total-val {
  font-size: 0.875rem;
  font-weight: 700;
  color: #e2e8f0;
  font-family: ui-monospace, monospace;
  white-space: nowrap;
  line-height: 2rem;
}
.bc-item-delete {
  padding: 0.25rem;
  background: transparent;
  border: none;
  color: #475569;
  cursor: pointer;
  transition: color 0.2s;
  flex-shrink: 0;
}
.bc-item-delete:hover {
  color: #ef4444;
}
.bc-item-delete .material-symbols-outlined {
  font-size: 1rem;
}

/* 批次模式内的车型select：自适应宽度 */
.batch-card-item-row .vehicle-cell {
  gap: 0.375rem;
}
.batch-card-item-row .vehicle-select {
  flex: 0 1 auto;
  width: auto;
  min-width: 5rem;
  max-width: 10rem;
}
.batch-card-item-row .vehicle-icon {
  width: 1.75rem;
  height: 1.75rem;
}

/* 批次模式内的路径select */
.batch-card-item-row .route-path-inline {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  white-space: nowrap;
}
.batch-card-item-row .route-select {
  min-width: 3rem;
  max-width: 5rem;
}

/* 批次模式内的数值输入 */
.batch-card-item-row .num-input {
  width: 100%;
  min-width: 3rem;
}

/* 批次车辆表格 */
.batch-vehicle-table {
  /* 复用 labor-cost-table 的基础样式，仅覆盖列宽 */
}
.batch-vehicle-table thead th.col-type { width: 18%; }
.batch-vehicle-table thead th.col-desc { width: 28%; }
.batch-vehicle-table thead th.col-qty { width: 10%; text-align: center; }
.batch-vehicle-table thead th.col-price { width: 12%; text-align: center; }
.batch-vehicle-table thead th.col-total { width: 14%; text-align: right; }
.batch-vehicle-table thead th.col-action { width: 3rem; }

.batch-vehicle-table .route-path-inline {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.batch-vehicle-table .route-inline-select {
  flex: 1;
  min-width: 0;
  cursor: pointer;
}
.batch-vehicle-table .route-inline-select.empty {
  color: #64748b;
}
.batch-vehicle-table .route-arrow {
  color: #475569;
  font-size: 0.75rem;
  flex-shrink: 0;
}
.batch-vehicle-table .route-map-btn-small {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  margin-left: 0.125rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.25rem;
  color: #3b82f6;
  cursor: pointer;
  flex-shrink: 0;
}
.batch-vehicle-table .route-map-btn-small:hover {
  background: rgba(59, 130, 246, 0.25);
}
.batch-vehicle-table .route-map-btn-small .material-symbols-outlined {
  font-size: 0.75rem;
}

.batch-card-empty-cell {
  text-align: center !important;
  color: #475569 !important;
  font-size: 0.8125rem;
  padding: 1.5rem !important;
}

/* 批次卡片底部：费用小计 */
.batch-card-footer {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.75rem;
  padding: 0.875rem 1.5rem;
  margin-top: 0.75rem;
  background: rgba(15, 25, 35, 0.3);
  border-top: 1px solid rgba(46, 75, 107, 0.3);
}
.batch-card-footer-label {
  font-size: 0.75rem;
  color: #64748b;
}
.batch-card-footer-total {
  font-size: 1.25rem;
  font-weight: 700;
  color: #e2e8f0;
  font-family: ui-monospace, monospace;
}

/* 车辆条目区域 */
.vehicle-section {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.vehicle-section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #94a3b8;
}
.add-item-btn {
  font-size: 0.625rem;
  color: #3b82f6;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.add-item-btn:hover {
  text-decoration: underline;
}

/* 车辆条目列表 */
.vehicle-items {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* 车辆条目行 - 12列网格 */
.vehicle-item-row {
  display: grid;
  grid-template-columns: 3fr 2fr 2fr 2fr 2fr 1fr;
  gap: 0.75rem;
  align-items: center;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.3);
  border: 1px solid #1e293b;
  border-radius: 0.5rem;
}

.vi-name {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #fff;
}

.vi-icon {
  padding: 0.375rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.25rem;
  color: #3b82f6;
  display: flex;
  align-items: center;
  justify-content: center;
}
.vi-icon .material-symbols-outlined {
  font-size: 0.875rem;
}

.vi-select {
  flex: 1;
  background: transparent;
  border: none;
  color: #fff;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}
.vi-select:focus {
  outline: none;
}

.vi-field {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.25rem;
  font-size: 0.625rem;
  color: #64748b;
}

.vi-label {
  white-space: nowrap;
}

.vi-input {
  width: 3rem;
  padding: 0.25rem;
  background: rgba(0, 0, 0, 0.4);
  border: none;
  border-radius: 0.25rem;
  color: #fff;
  font-size: 0.75rem;
  text-align: center;
}
.vi-input:focus {
  outline: none;
}

.vi-unit {
  color: #64748b;
}

.vi-total {
  text-align: right;
  font-size: 0.75rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
  color: #34d399;
}

.vi-action {
  text-align: right;
}
.vi-delete {
  padding: 0.25rem;
  background: transparent;
  border: none;
  color: #475569;
  cursor: pointer;
  transition: color 0.2s;
}
.vi-delete:hover {
  color: #f87171;
}
.vi-delete .material-symbols-outlined {
  font-size: 0.875rem;
}

/* 空状态 */
.vehicle-empty {
  padding: 2rem;
  text-align: center;
  color: #475569;
  font-size: 0.875rem;
}
.vehicle-empty p {
  margin: 0;
}

/* 非批次模式的旧版grid布局 */
.batch-vehicles-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}
.batch-vehicles-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #e2e8f0;
  margin: 0;
}
.batch-vehicles-title .material-symbols-outlined {
  font-size: 1.125rem;
  color: #64748b;
}
.add-vehicle-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem;
  background: transparent;
  border: 1px solid #475569;
  border-radius: 0.5rem;
  color: #94a3b8;
  font-size: 0.8125rem;
  cursor: pointer;
  transition: all 0.2s;
}
.add-vehicle-btn:hover {
  border-color: #3b82f6;
  color: #3b82f6;
}
.add-vehicle-btn .material-symbols-outlined {
  font-size: 1rem;
}

.batch-table-header {
  display: grid;
  grid-template-columns: minmax(160px, 2fr) minmax(120px, 1.5fr) 3.5rem minmax(50px, 1fr) 3.5rem minmax(70px, 1fr) 2.5rem;
  gap: 0.75rem;
  padding: 0.5rem 1rem;
  font-size: 0.625rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}
.batch-table-header .col-total,
.batch-table-header .col-action {
  text-align: right;
}

.batch-vehicle-row {
  display: flex;
  flex-direction: column;
}

.batch-vehicle-card {
  display: grid;
  grid-template-columns: minmax(160px, 2fr) minmax(120px, 1.5fr) 3.5rem minmax(50px, 1fr) 3.5rem minmax(70px, 1fr) 2.5rem;
  gap: 0.75rem;
  align-items: center;
  padding: 0.875rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  transition: border-color 0.2s;
}
.batch-vehicle-card:hover {
  border-color: #475569;
}

.vehicle-cell {
  display: flex;
  align-items: center;
  gap: 0.625rem;
}
.vehicle-icon {
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.5rem;
  color: #3b82f6;
  flex-shrink: 0;
}
.vehicle-icon .material-symbols-outlined {
  font-size: 1rem;
}
.vehicle-select {
  flex: 1;
  min-width: 0;
  padding: 0.375rem 0.5rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  text-overflow: ellipsis;
  overflow: hidden;
}
.vehicle-select:focus {
  outline: none;
  border-color: #3b82f6;
}

.col-route {
  min-width: 0;
  overflow: hidden;
}
.col-route .route-path-inline {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  min-width: 0;
}
.route-select {
  padding: 0.25rem 0.375rem;
  background: transparent;
  border: none;
  color: #38bdf8;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  min-width: 2.5rem;
  max-width: 5rem;
  text-align: center;
  text-overflow: ellipsis;
  overflow: hidden;
}
.route-select:hover {
  color: #7dd3fc;
}
.route-select.empty {
  color: #64748b;
}
.route-arrow {
  color: #475569;
  font-size: 0.75rem;
}
.route-map-btn-small {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  margin-left: 0.25rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.3);
  border-radius: 0.25rem;
  color: #3b82f6;
  cursor: pointer;
  flex-shrink: 0;
}
.route-map-btn-small:hover {
  background: rgba(59, 130, 246, 0.25);
}
.route-map-btn-small .material-symbols-outlined {
  font-size: 0.75rem;
}
.route-loading {
  font-size: 0.625rem;
  color: #3b82f6;
  margin-top: 0.125rem;
}

.num-input {
  width: 100%;
  padding: 0.375rem 0.5rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.8125rem;
  text-align: center;
}
.num-input:focus {
  outline: none;
  border-color: #3b82f6;
}
/* 确保 grid 子项不溢出 */
.batch-vehicle-card > div {
  min-width: 0;
}

.col-total .total-value {
  font-size: 0.875rem;
  font-weight: 600;
  font-family: ui-monospace, monospace;
  color: #4ade80;
}

.col-action {
  display: flex;
  justify-content: flex-end;
}
.delete-btn {
  padding: 0.375rem;
  background: transparent;
  border: none;
  color: #475569;
  cursor: pointer;
  transition: color 0.2s;
}
.delete-btn:hover {
  color: #ef4444;
}
.delete-btn .material-symbols-outlined {
  font-size: 1rem;
}

.batch-vehicle-formula {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 1rem 0 3.5rem;
  font-size: 0.625rem;
  color: #64748b;
  font-style: italic;
}
.formula-dot {
  color: #475569;
}

/* 批次空状态 */
.batch-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  border: 2px dashed #334155;
  border-radius: 1rem;
  color: #475569;
}
.batch-empty .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 1rem;
  opacity: 0.3;
}
.batch-empty p {
  font-size: 0.875rem;
  margin: 0;
}

/* 车型信息卡片区域 */
.vehicle-info-cards {
  margin-top: 1rem;
  padding-top: 1rem;
  border-top: 1px solid #334155;
}
.vehicle-info-cards-header {
  margin-bottom: 0.75rem;
}
.vehicle-info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(14rem, 1fr));
  gap: 0.75rem;
}
.vehicle-info-card {
  padding: 0.875rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 0.625rem;
}
.vehicle-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.vehicle-card-icon {
  width: 1.75rem;
  height: 1.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 0.375rem;
  color: #3b82f6;
}
.vehicle-card-icon .material-symbols-outlined {
  font-size: 0.875rem;
}
.vehicle-card-name {
  font-size: 0.8125rem;
  font-weight: 600;
  color: #e2e8f0;
}
.vehicle-card-specs {
  font-size: 0.6875rem;
  color: #64748b;
  margin-bottom: 0.625rem;
}
.vehicle-spec-value {
  color: #94a3b8;
}
.vehicle-card-prices {
  display: flex;
  gap: 1rem;
}
.vehicle-price-item {
  flex: 1;
}
.vehicle-price-label {
  display: block;
  font-size: 0.625rem;
  color: #64748b;
  margin-bottom: 0.25rem;
}
.vehicle-price-input-wrap {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.price-prefix {
  font-size: 0.75rem;
  color: #64748b;
}
.vehicle-price-input {
  flex: 1;
  width: 100%;
  padding: 0.375rem 0.5rem;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.8125rem;
  text-align: right;
}
.vehicle-price-input:focus {
  outline: none;
  border-color: #3b82f6;
}

/* 运力不足提醒 */
.capacity-warning {
  display: flex;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  margin-top: 0.75rem;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 0.75rem;
}
.capacity-warning-icon {
  font-size: 1.25rem;
  color: #f59e0b;
  flex-shrink: 0;
  margin-top: 0.125rem;
}
.capacity-warning-body {
  flex: 1;
  min-width: 0;
}
.capacity-warning-title {
  font-size: 0.8125rem;
  font-weight: 700;
  color: #fbbf24;
  margin: 0 0 0.25rem;
}
.capacity-warning-desc {
  font-size: 0.75rem;
  color: #d1d5db;
  margin: 0 0 0.375rem;
  line-height: 1.5;
}
.capacity-warning-desc strong {
  color: #fbbf24;
}
.capacity-warning-list {
  margin: 0;
  padding: 0 0 0 1rem;
  font-size: 0.75rem;
  color: #9ca3af;
  line-height: 1.6;
}
.capacity-warning-list strong {
  color: #e2e8f0;
}
.capacity-short {
  color: #f87171;
  font-weight: 600;
}

/* 底部结算栏 */
.batch-summary-bar {
  display: flex;
  justify-content: flex-end;
  align-items: center;
  gap: 2rem;
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  background: #161e31;
  border-radius: 0.75rem;
  border: 1px solid #334155;
}
.batch-summary-stats {
  display: flex;
  gap: 1.5rem;
}
.summary-stat {
  text-align: right;
}
.stat-label {
  display: block;
  font-size: 0.625rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}
.stat-value {
  font-size: 0.9375rem;
  font-weight: 600;
  color: #e2e8f0;
}
.batch-summary-total {
  text-align: right;
  padding-left: 1.5rem;
  border-left: 1px solid #334155;
}
.total-label {
  display: block;
  font-size: 0.625rem;
  font-weight: 600;
  color: #3b82f6;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}
.batch-summary-total .total-value {
  font-size: 1.5rem;
  font-weight: 700;
  font-family: ui-monospace, monospace;
  color: #fff;
}
.total-currency {
  font-size: 1rem;
  font-weight: 400;
  color: #64748b;
  margin-right: 0.125rem;
}

/* 路线规划按钮（运输路径旁） */
.route-planning-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  padding: 0;
  margin-left: 0.375rem;
  background: rgba(59, 130, 246, 0.15);
  border: 1px solid rgba(59, 130, 246, 0.4);
  border-radius: 0.25rem;
  color: #3b82f6;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}
.route-planning-btn:hover {
  background: rgba(59, 130, 246, 0.25);
  border-color: #3b82f6;
  color: #60a5fa;
}
.route-planning-btn .material-symbols-outlined {
  font-size: 0.875rem;
}

/* 路线规划弹窗 */
.route-planning-modal {
  width: 100%;
  max-width: 56rem;
  background: #1e293b;
  border-radius: 1rem;
  border: 1px solid #334155;
  overflow: hidden;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.route-planning-body {
  padding: 1rem 1.25rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.route-planning-info {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.route-planning-endpoints {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  background: rgba(15, 23, 42, 0.5);
  border-radius: 0.5rem;
}

.route-endpoint {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 0;
}

.endpoint-marker {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  font-size: 0.75rem;
  font-weight: 600;
  border-radius: 50%;
  flex-shrink: 0;
}
.endpoint-marker.origin {
  background: #3b82f6;
  color: white;
}
.endpoint-marker.dest {
  background: #22c55e;
  color: white;
}

.endpoint-text {
  font-size: 0.8125rem;
  color: #e2e8f0;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.endpoint-arrow {
  color: #64748b;
  font-size: 1rem;
  flex-shrink: 0;
}

.route-policy-tabs {
  display: flex;
  gap: 0.5rem;
}

.route-policy-tab {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  background: transparent;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.route-policy-tab:hover {
  border-color: #3b82f6;
  color: #e2e8f0;
}
.route-policy-tab.active {
  background: #3b82f6;
  border-color: #3b82f6;
  color: white;
}

.route-planning-map-wrap {
  position: relative;
  height: 300px;
  background: #0f172a;
  border-radius: 0.5rem;
  overflow: hidden;
}

.route-planning-map {
  width: 100%;
  height: 100%;
}

.route-planning-loading {
  position: absolute;
  inset: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
  font-size: 0.875rem;
}

.route-planning-loading .spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.route-planning-results {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 180px;
  overflow-y: auto;
}

.route-planning-empty {
  padding: 1rem;
  text-align: center;
  color: #64748b;
  font-size: 0.875rem;
}

.route-result-card {
  padding: 0.875rem 1rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}
.route-result-card:hover {
  border-color: #3b82f6;
  background: rgba(59, 130, 246, 0.1);
}
.route-result-card.selected {
  border-color: #22c55e;
  background: rgba(34, 197, 94, 0.15);
  box-shadow: 0 0 0 2px rgba(34, 197, 94, 0.2);
}

.route-result-header {
  margin-bottom: 0.5rem;
}

.route-result-tag {
  display: inline-block;
  padding: 0.1875rem 0.625rem;
  font-size: 0.75rem;
  font-weight: 500;
  border-radius: 0.25rem;
  background: #334155;
  color: #94a3b8;
}
.route-result-tag.recommend {
  background: #3b82f6;
  color: white;
}

.route-result-info {
  display: flex;
  align-items: baseline;
  gap: 0.625rem;
  margin-bottom: 0.375rem;
}

.route-result-duration {
  font-size: 1.0625rem;
  font-weight: 700;
  color: #f1f5f9;
}

.route-result-divider {
  color: #475569;
  font-size: 0.875rem;
}

.route-result-distance {
  font-size: 1.0625rem;
  font-weight: 600;
  color: #4ade80;
}

.route-result-via {
  font-size: 0.8125rem;
  color: #94a3b8;
  line-height: 1.4;
}

.route-planning-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  padding-top: 0.5rem;
  border-top: 1px solid #334155;
}

.route-planning-cancel {
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  background: transparent;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}
.route-planning-cancel:hover {
  border-color: #64748b;
  color: #e2e8f0;
}

.route-planning-confirm {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  font-size: 0.8125rem;
  background: #22c55e;
  border: none;
  border-radius: 0.5rem;
  color: white;
  cursor: pointer;
  transition: all 0.2s;
}
.route-planning-confirm:hover:not(:disabled) {
  background: #16a34a;
}
.route-planning-confirm:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
.route-planning-confirm .material-symbols-outlined {
  font-size: 1rem;
}

.logistics-detail-table thead th.col-qty {
  min-width: 4rem;
}
.logistics-detail-table thead th.col-price {
  min-width: 7rem;
}
.logistics-detail-table thead th.col-total {
  min-width: 5rem;
}

.logistics-vehicle-select {
  min-width: 10rem;
}

/* 车型信息：表格式横向布局，单位空间内显示更多卡片 */
.vehicle-info-table-wrap {
  margin-top: 1rem;
  overflow-x: auto;
}

.vehicle-info-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.vehicle-info-table thead th {
  padding: 0.5rem 0.75rem;
  text-align: left;
  background: #1e293b;
  color: #94a3b8;
  font-weight: 600;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.vehicle-info-table thead th.col-vehicle-info {
  min-width: 12rem;
}

.vehicle-info-table thead th.col-start-price,
.vehicle-info-table thead th.col-km-price {
  width: 7rem;
  text-align: center;
}

.vehicle-info-table thead th.col-action {
  width: 4rem;
  text-align: center;
}

.vehicle-info-row td {
  padding: 0.5rem 0.75rem;
  vertical-align: middle;
  border-bottom: 1px solid #334155;
}

.vehicle-info-cell {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  min-height: 2.5rem;
}

.vehicle-info-icon {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.375rem;
  background: rgba(56, 189, 248, 0.15);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.vehicle-info-icon .material-symbols-outlined {
  font-size: 1.25rem;
  color: #38bdf8;
}

.vehicle-info-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
  min-width: 0;
}

.vehicle-info-name {
  font-weight: 700;
  color: #f1f5f9;
  font-size: 0.875rem;
  line-height: 1.3;
}

.vehicle-info-spec {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.3;
}

.vehicle-info-row .col-start-price,
.vehicle-info-row .col-km-price {
  text-align: center;
}

.vehicle-info-input {
  width: 5rem;
  max-width: 100%;
  box-sizing: border-box;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #f1f5f9;
  font-size: 0.8125rem;
  padding: 0.35rem 0.5rem;
  text-align: center;
  -moz-appearance: textfield;
}

.vehicle-info-input::-webkit-outer-spin-button,
.vehicle-info-input::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.vehicle-info-input:focus {
  outline: none;
  border-color: #38bdf8;
}

.vehicle-info-row .col-action {
  text-align: center;
}

.vehicle-detail-link {
  background: none;
  border: none;
  color: #38bdf8;
  font-size: 0.8125rem;
  cursor: pointer;
  padding: 0.25rem 0;
  text-decoration: none;
  transition: color 0.2s;
}

.vehicle-detail-link:hover {
  color: #7dd3fc;
  text-decoration: underline;
}

.logistics-list {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.logistics-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  background: rgba(15, 23, 42, 0.5);
  border: 1px solid #334155;
  border-radius: 0.5rem;
}

.logistics-info {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logistics-icon {
  width: 3rem;
  height: 3rem;
  border-radius: 0.5rem;
  background: rgba(100, 116, 139, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
}

.logistics-icon.primary {
  background: rgba(56, 189, 248, 0.15);
}

.logistics-icon .material-symbols-outlined {
  font-size: 1.5rem;
  color: #94a3b8;
}

.logistics-icon.primary .material-symbols-outlined {
  color: #38bdf8;
}

.logistics-name {
  font-size: 0.875rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0 0 0.125rem 0;
}

.logistics-desc {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.logistics-controls {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.stepper {
  display: flex;
  align-items: center;
  border: 1px solid #334155;
  border-radius: 0.25rem;
  overflow: hidden;
}

.stepper-btn {
  background: rgba(255, 255, 255, 0.05);
  border: none;
  color: #e2e8f0;
  padding: 0.25rem 0.75rem;
  cursor: pointer;
  font-size: 1rem;
}

.stepper-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.stepper-input {
  width: 2.5rem;
  text-align: center;
  background: transparent;
  border: none;
  color: #f1f5f9;
  font-size: 0.875rem;
  padding: 0.25rem 0;
}

.logistics-unit {
  font-size: 0.875rem;
  font-weight: 700;
  color: #f1f5f9;
  min-width: 5rem;
  text-align: right;
}

.insurance-panel .insurance-row {
  display: flex;
  align-items: center;
  gap: 2rem;
}

.insurance-total {
  flex: 1;
}

.insurance-total .total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0.25rem 0 0 0;
}

.insurance-total .input-with-prefix {
  display: flex;
  align-items: center;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: hidden;
  margin-top: 0.25rem;
}

.insurance-total .input-prefix {
  padding: 0.5rem 0.75rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: #94a3b8;
}

.insurance-total .declared-value-input {
  flex: 1;
  min-width: 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.insurance-rate-field {
  width: auto;
}

.insurance-rate-field .input-with-suffix {
  width: 6.5rem;
  max-width: 100%;
}

.insurance-premium {
  flex: 1;
}

.insurance-premium .total-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: #f1f5f9;
  margin: 0.25rem 0 0 0;
}

/* 1. 项目概况 */
.overview-section {
  margin-bottom: 1.5rem;
}

.overview-section:last-of-type {
  margin-bottom: 0;
}

.overview-input-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  margin-bottom: 1rem;
}

@media (max-width: 768px) {
  .overview-input-grid {
    grid-template-columns: 1fr;
  }
}

.upload-col,
.desc-col {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.upload-zone {
  border: 2px dashed #334155;
  border-radius: 0.75rem;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.3);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.upload-zone:hover,
.upload-zone-dragover {
  background: rgba(15, 23, 42, 0.5);
  border-color: #38bdf8;
}

.upload-icon {
  font-size: 2.5rem;
  color: #64748b;
  transition: color 0.2s;
}

.upload-zone:hover .upload-icon,
.upload-zone-dragover .upload-icon {
  color: #38bdf8;
}

.upload-text {
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
  margin: 0;
}

.upload-hint {
  font-size: 0.75rem;
  color: #64748b;
  margin: 0;
}

.upload-input-hidden {
  position: absolute;
  width: 0;
  height: 0;
  opacity: 0;
  pointer-events: none;
}

.upload-files-hint {
  font-size: 0.75rem;
  color: #38bdf8;
  margin: 0.25rem 0 0 0;
}

.overview-textarea {
  flex: 1;
  min-height: 140px;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  color: #e2e8f0;
  padding: 1rem;
  font-size: 0.875rem;
  resize: vertical;
  font-family: inherit;
}

.overview-textarea::placeholder {
  color: #64748b;
}

.overview-textarea:focus {
  outline: none;
  border-color: #38bdf8;
  box-shadow: 0 0 0 2px rgba(56, 189, 248, 0.2);
}

.overview-actions {
  display: flex;
  justify-content: flex-end;
  padding-top: 0.5rem;
}

.ai-glow-btn {
  background-color: #38bdf8;
  box-shadow: 0 0 15px rgba(56, 189, 248, 0.5);
  border: none;
  position: relative;
  overflow: hidden;
}

.ai-glow-btn::after {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: linear-gradient(45deg, transparent, rgba(255, 255, 255, 0.1), transparent);
  transform: rotate(45deg);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { transform: translateX(-100%) rotate(45deg); }
  100% { transform: translateX(100%) rotate(45deg); }
}

.breakdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.breakdown-subtitle {
  font-size: 0.75rem;
  color: #64748b;
}

.breakdown-table-wrap {
  overflow-x: auto;
}

.tech-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.875rem;
}

.tech-table th {
  background: #1a2b3c;
  color: #38bdf8;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #334155;
}

.tech-table td {
  padding: 0.75rem 1rem;
  color: #cbd5e1;
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.tech-table-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.tech-table .service-type {
  font-weight: 500;
  color: #38bdf8;
}

.tech-table .total-price {
  color: #38bdf8;
  font-weight: 700;
}

/* 2. 设备清单管理 */
.equipment-import-section .equipment-import-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.download-template-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.equipment-upload-zone {
  flex-direction: row;
  justify-content: center;
  gap: 1rem;
}

.equipment-upload-icon {
  font-size: 2.5rem;
}

.equipment-upload-text {
  text-align: left;
}

.equipment-upload-text .upload-hint {
  margin-top: 0.25rem;
}

.equipment-list-section {
  overflow: hidden;
  padding: 0;
  display: flex;
  flex-direction: column;
}

.equipment-list-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
  background: rgba(30, 41, 59, 0.6);
}

.equipment-list-title-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.equipment-list-title {
  margin: 0;
  font-size: 0.875rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.inline-edit-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 9999px;
  font-size: 0.6875rem;
  color: #94a3b8;
}

.inline-edit-dot {
  width: 0.375rem;
  height: 0.375rem;
  border-radius: 50%;
  background: #38bdf8;
}

.equipment-header-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.eq-source-select {
  padding: 0.4rem 0.625rem;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid #334155;
  border-radius: 0.375rem;
  color: #e2e8f0;
  font-size: 0.8125rem;
  cursor: pointer;
  outline: none;
  transition: border-color 0.2s;
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%2394a3b8' d='M3 5l3 3 3-3'/%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 0.5rem center;
  padding-right: 1.5rem;
}

.eq-source-select:focus {
  border-color: #38bdf8;
}

.eq-source-select option {
  background: #1e293b;
  color: #e2e8f0;
}

.clear-list-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
}

.equipment-table-wrap {
  overflow-x: auto;
}

.equipment-import-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.equipment-table th.col-brand { min-width: 6rem; }
.equipment-table th.col-model { min-width: 8rem; }
.equipment-table th.col-match-model { min-width: 10rem; }
.equipment-table th.col-type { min-width: 6rem; }
.equipment-table th.col-match-type { min-width: 10rem; }
.equipment-table th.col-u,
.equipment-table th.col-qty { min-width: 5rem; }
.equipment-table th.col-asset { min-width: 8rem; }
.equipment-table th.col-action { width: 4rem; text-align: center; }

/* ---- 原始导入表格 ---- */
.eq-original-table-section {
  overflow: hidden;
  padding: 0;
}
.eq-original-table-header {
  display: flex;
  align-items: center;
  padding: 0.75rem 1.5rem;
  border-bottom: 1px solid #334155;
  background: rgba(30, 41, 59, 0.6);
}
.eq-original-file-tag,
.eq-original-count-tag {
  display: inline-flex;
  align-items: center;
  padding: 0.125rem 0.5rem;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 9999px;
  font-size: 0.6875rem;
  color: #38bdf8;
  margin-left: 0.5rem;
}
.eq-original-count-tag {
  background: rgba(255, 255, 255, 0.05);
  border-color: rgba(255, 255, 255, 0.1);
  color: #94a3b8;
}
.eq-original-table-wrap {
  overflow-x: auto;
  max-height: 280px;
  overflow-y: auto;
}
.eq-original-table th {
  position: sticky;
  top: 0;
  z-index: 1;
  background: #1e293b;
  white-space: nowrap;
  font-size: 0.75rem;
  color: #94a3b8;
}
.eq-original-table td {
  white-space: nowrap;
  font-size: 0.8125rem;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* ---- 列映射表头 ---- */
.eq-header-dropdown-wrap {
  position: relative;
  cursor: pointer;
  user-select: none;
}
.eq-header-cell {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.eq-dropdown-icon {
  font-size: 1rem;
  color: #64748b;
  transition: transform 0.2s;
}
.eq-mapped-source {
  display: block;
  font-size: 0.625rem;
  color: #64748b;
  font-weight: 400;
  margin-top: 0.125rem;
}
.eq-mapped-source.mapped {
  color: #38bdf8;
}
.eq-mapping-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  min-width: 180px;
  max-height: 240px;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.eq-dd-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #334155;
  font-size: 0.75rem;
  color: #94a3b8;
}
.eq-dd-header button {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
}
.eq-dd-header button .material-symbols-outlined { font-size: 1rem; }
.eq-dd-options {
  overflow-y: auto;
  max-height: 200px;
}
.eq-dd-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  font-size: 0.8125rem;
  color: #cbd5e1;
  transition: background 0.15s;
}
.eq-dd-option:hover {
  background: rgba(56, 189, 248, 0.1);
}
.eq-dd-option.selected {
  color: #38bdf8;
}
.eq-dd-option .material-symbols-outlined {
  font-size: 1.125rem;
}

/* ---- 匹配型号列 ---- */
.eq-match-cell {
  display: flex;
  align-items: center;
  gap: 0.375rem;
}
.eq-matched-model {
  cursor: pointer;
  font-size: 0.8125rem;
  padding: 0.125rem 0.375rem;
  border-radius: 0.25rem;
  transition: background 0.15s;
  white-space: nowrap;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
}
.eq-matched-model:hover {
  background: rgba(255, 255, 255, 0.08);
}
.eq-matched-model.high-match { color: #4ade80; }
.eq-matched-model.mid-match { color: #facc15; }
.eq-matched-model.low-match { color: #fb923c; }
.eq-matched-model.no-match { color: #64748b; }

.eq-match-badge {
  font-size: 0.625rem;
  padding: 0.0625rem 0.375rem;
  border-radius: 9999px;
  font-weight: 600;
  white-space: nowrap;
}
.eq-match-badge.high { background: rgba(74, 222, 128, 0.15); color: #4ade80; }
.eq-match-badge.mid { background: rgba(250, 204, 21, 0.15); color: #facc15; }
.eq-match-badge.low { background: rgba(251, 146, 60, 0.15); color: #fb923c; }

.eq-clear-match-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0;
  display: flex;
  align-items: center;
  transition: color 0.15s;
}
.eq-clear-match-btn:hover { color: #f87171; }
.eq-clear-match-btn .material-symbols-outlined { font-size: 0.875rem; }

.eq-match-type-text {
  font-size: 0.75rem;
  color: #94a3b8;
  white-space: nowrap;
}
.eq-match-type-text.empty {
  color: #475569;
}

/* 行状态高亮 */
.eq-row-warning {
  border-left: 3px solid #facc15;
}
.eq-row-error {
  border-left: 3px solid #f87171;
}

/* 匹配中动画 */
.eq-matching-tag {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.25rem 0.75rem;
  background: rgba(56, 189, 248, 0.1);
  border: 1px solid rgba(56, 189, 248, 0.2);
  border-radius: 9999px;
  font-size: 0.6875rem;
  color: #38bdf8;
  margin-left: 0.5rem;
}
.eq-matching-spinner {
  width: 0.75rem;
  height: 0.75rem;
  border: 2px solid rgba(56, 189, 248, 0.2);
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: eq-spin 0.7s linear infinite;
}
@keyframes eq-spin { to { transform: rotate(360deg); } }

/* ---- 搜索弹窗 ---- */
.eq-search-overlay {
  position: fixed;
  inset: 0;
  z-index: 10000;
  background: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}
.eq-search-dialog {
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  background: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.75rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.5);
}
.eq-search-dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.25rem;
  border-bottom: 1px solid #1e293b;
}
.eq-search-dialog-header h3 {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
}
.eq-search-close-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  display: flex;
  transition: color 0.15s;
}
.eq-search-close-btn:hover { color: #f1f5f9; }
.eq-search-bar {
  padding: 0.75rem 1.25rem;
  border-bottom: 1px solid #1e293b;
}
.eq-search-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  background: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  outline: none;
  transition: border-color 0.2s;
}
.eq-search-input:focus {
  border-color: #38bdf8;
}
.eq-search-source-selector {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
  font-size: 0.75rem;
  color: #94a3b8;
}
.eq-search-source-selector label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  cursor: pointer;
}
.eq-search-source-selector input[type="radio"] {
  accent-color: #38bdf8;
}
.eq-search-results {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem;
  min-height: 100px;
  max-height: 400px;
}
.eq-search-loading,
.eq-search-empty {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #64748b;
  font-size: 0.875rem;
}
.eq-search-result-item {
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background 0.15s;
  border: 1px solid transparent;
}
.eq-search-result-item:hover {
  background: rgba(56, 189, 248, 0.08);
  border-color: rgba(56, 189, 248, 0.2);
}
.eq-result-main {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}
.eq-result-manufacturer {
  font-size: 0.75rem;
  color: #94a3b8;
  min-width: 4rem;
}
.eq-result-model {
  font-size: 0.875rem;
  color: #f1f5f9;
  font-weight: 500;
}
.eq-result-meta {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.25rem;
}
.eq-result-category {
  font-size: 0.6875rem;
  color: #64748b;
}
.eq-result-price {
  font-size: 0.75rem;
  color: #38bdf8;
  font-weight: 500;
}

.equipment-row:hover {
  background: rgba(255, 255, 255, 0.05);
}

.inline-input {
  width: 100%;
  min-width: 0;
  background: transparent;
  border: none;
  color: #e2e8f0;
  font-size: 0.875rem;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  transition: box-shadow 0.2s;
}

.inline-input:focus {
  outline: none;
  box-shadow: 0 0 0 1px rgba(56, 189, 248, 0.5);
}

.inline-input::placeholder {
  color: #64748b;
}

.inline-select {
  cursor: pointer;
  appearance: none;
  background: rgba(15, 23, 42, 0.5);
}

.row-delete-btn {
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 0.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: color 0.2s;
}

.row-delete-btn:hover {
  color: #f87171;
}

.row-delete-btn .material-symbols-outlined {
  font-size: 1.25rem;
}

.equipment-list-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1rem 1.5rem;
  border-top: 1px solid #334155;
  background: rgba(26, 43, 60, 0.3);
}

.equipment-stats {
  display: flex;
  gap: 2rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.stat-label {
  font-size: 0.625rem;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #f1f5f9;
}

.stat-value.primary {
  color: #38bdf8;
}

.stat-unit {
  font-size: 0.625rem;
  font-weight: 400;
  color: #94a3b8;
  margin-left: 0.125rem;
}

.add-row-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: #cbd5e1;
}

.add-row-btn:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.2);
  color: #f1f5f9;
}

.placeholder-tab {
  padding: 2rem;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  color: #94a3b8;
}

.right-dashboard {
  width: 26rem;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  /* 与左侧「人工服务费」上端对齐：预留与 tabs-row 等高的上边距 */
  padding-top: 4.5rem;
}

/* 右侧栏：参考驻场「实时测算结果」布局与样式 */
.summary-card {
  background-color: #1a202c;
  border-radius: 0.75rem;
  border: 1px solid rgba(19, 91, 236, 0.3);
  padding: 1.5rem;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.3);
  position: relative;
  overflow: hidden;
}

.glow-effect {
  position: absolute;
  top: 0;
  right: 0;
  width: 200px;
  height: 200px;
  background: radial-gradient(circle, rgba(19, 91, 236, 0.15) 0%, transparent 70%);
  border-radius: 50%;
  transform: translate(50%, -50%);
  pointer-events: none;
}

.summary-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
  margin-bottom: 1.5rem;
}

.summary-title .material-symbols-outlined {
  color: #135bec;
}

.global-params-section {
  padding: 1rem;
  margin-bottom: 1rem;
  background-color: rgba(35, 43, 59, 0.3);
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
}

.section-title {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.global-params-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 0.75rem;
}

.global-param-item {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.param-label {
  font-size: 0.6875rem;
  color: #94a3b8;
  white-space: nowrap;
}

.param-input {
  width: 100%;
  padding: 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.8125rem;
  text-align: center;
}

.param-input:focus {
  outline: none;
  border-color: #135bec;
}

.global-param-item .input-with-suffix {
  position: relative;
}

.global-param-item .input-suffix {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.6875rem;
}

.global-param-item .input-with-suffix .param-input {
  padding-right: 1.5rem;
}

.summary-numbers {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 1.5rem;
}

.main-price {
  background-color: rgba(35, 43, 59, 0.5);
  padding: 1rem;
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
  transition: border-color 0.2s;
}

.main-price:hover {
  border-color: rgba(19, 91, 236, 0.5);
}

.price-label {
  font-size: 0.75rem;
  color: #92a4c9;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.price-value {
  font-size: 1.875rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: baseline;
  gap: 0.25rem;
  letter-spacing: -0.025em;
}

.price-trend {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  margin-top: 0.25rem;
  font-size: 0.75rem;
  color: #22c55e;
}

.trend-icon {
  font-size: 1rem;
}

.sub-prices {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
}

.sub-price-item {
  background-color: rgba(35, 43, 59, 0.5);
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid #2d3748;
}

.sub-price-label {
  font-size: 0.625rem;
  color: #92a4c9;
  text-transform: uppercase;
  margin-bottom: 0.25rem;
}

.sub-price-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: white;
}

.sub-price-note {
  font-size: 0.625rem;
  color: #64748b;
  margin-top: 0.25rem;
  white-space: nowrap;
}

.breakdown-section {
  flex: 1;
  margin-bottom: 1rem;
}

.breakdown-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  margin-bottom: 0.75rem;
}

.breakdown-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.breakdown-item {
  display: block;
}

.breakdown-header {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: #cbd5e1;
  margin-bottom: 0.25rem;
  gap: 0.5rem;
}

.breakdown-name {
  flex: 1;
}

.breakdown-amount {
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
}

.breakdown-percent {
  font-size: 0.75rem;
  font-weight: 600;
  color: #cbd5e1;
  min-width: 40px;
  text-align: right;
}

.breakdown-bar {
  width: 100%;
  height: 0.5rem;
  background-color: #374151;
  border-radius: 0.25rem;
  overflow: hidden;
}

.breakdown-fill {
  height: 100%;
  border-radius: 0.25rem;
  transition: width 0.3s ease;
}

.breakdown-group {
  margin-bottom: 0.25rem;
}
.breakdown-item-group .breakdown-name {
  font-weight: 600;
}
.breakdown-children {
  padding-left: 0.75rem;
  margin-top: 0.25rem;
  margin-bottom: 0.375rem;
  border-left: 2px solid #334155;
}
.breakdown-sub-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.125rem 0;
  font-size: 0.6875rem;
  color: #64748b;
}
.breakdown-sub-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.breakdown-sub-amount {
  font-family: ui-monospace, monospace;
  font-size: 0.6875rem;
  color: #94a3b8;
  margin-left: 0.5rem;
  white-space: nowrap;
}

.summary-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 0.5rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: #135bec;
  color: white;
  font-weight: 700;
  border-radius: 0.5rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 0 15px rgba(19, 91, 236, 0.3);
}

.btn-primary:hover {
  background-color: #1d6bf3;
}

.btn-primary .material-symbols-outlined {
  font-size: 1.125rem;
}

.btn-secondary {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1rem;
  background-color: transparent;
  color: #94a3b8;
  font-weight: 500;
  border-radius: 0.5rem;
  border: 1px solid #374151;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: #4b5563;
  color: white;
}

.btn-secondary .material-symbols-outlined {
  font-size: 1.125rem;
}

.warning-card {
  padding: 1rem;
  border-radius: 0.75rem;
  background: rgba(234, 88, 12, 0.1);
  border: 1px solid rgba(234, 88, 12, 0.3);
  display: flex;
  gap: 0.75rem;
}

.warning-icon {
  font-size: 1.25rem;
  color: #f97316;
  flex-shrink: 0;
}

.warning-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #fdba74;
  margin: 0 0 0.25rem 0;
}

.warning-desc {
  font-size: 0.6875rem;
  color: #fed7aa;
  margin: 0;
  line-height: 1.4;
}

@media (max-width: 1024px) {
  .calculator-content {
    flex-direction: column;
  }
  .right-dashboard {
    width: 100%;
  }
  .packaging-tiers {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 640px) {
  .config-grid.two-cols {
    grid-template-columns: 1fr;
  }
  .insurance-row {
    flex-direction: column;
    align-items: flex-start !important;
  }
  .insurance-rate-field .input-with-suffix {
    width: 100%;
  }
}

/* ---------- 生成正式报价单弹窗 ---------- */
.relocation-quotation-overlay {
  position: fixed;
  top: 70px;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.8);
  z-index: 9999;
}

.relocation-quotation-window {
  position: fixed;
  background-color: #0b0e14;
  border: 1px solid #30363d;
  border-radius: 0.75rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.7);
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.relocation-quotation-window.maximized {
  border-radius: 0;
  border-left: none;
  border-right: none;
  border-bottom: none;
}

.relocation-quotation-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #30363d;
  background-color: #0b0e14;
}

.relocation-quotation-header-left {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.relocation-quotation-breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  color: #8b949e;
}

.relocation-quotation-breadcrumb-link {
  color: #8b949e;
}

.relocation-quotation-breadcrumb-current {
  color: #fff;
  font-weight: 500;
}

.relocation-quotation-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #fff;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0;
}

.relocation-quotation-badge {
  font-size: 0.7rem;
  font-weight: 400;
  color: #8b949e;
  background-color: #161b22;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  border: 1px solid #30363d;
}

.relocation-quotation-header-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.relocation-quotation-zoom {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.5rem;
  background-color: #161b22;
  border-radius: 0.5rem;
  border: 1px solid #30363d;
}

.relocation-quotation-zoom-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  color: #8b949e;
  cursor: pointer;
  transition: all 0.15s;
}

.relocation-quotation-zoom-btn:hover {
  background-color: rgba(255, 255, 255, 0.1);
  color: #fff;
}

.relocation-quotation-zoom-level {
  font-size: 0.7rem;
  color: #c9d1d9;
  font-family: monospace;
  min-width: 2.5rem;
  text-align: center;
}

.relocation-quotation-fullscreen-btn,
.relocation-quotation-close-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  background-color: transparent;
  border: none;
  border-radius: 0.375rem;
  color: #8b949e;
  cursor: pointer;
  transition: all 0.2s;
}

.relocation-quotation-fullscreen-btn:hover {
  background-color: #30363d;
  color: #fff;
}

.relocation-quotation-close-btn:hover {
  background-color: #dc2626;
  color: #fff;
}

/* 主内容区域：预览 + 侧边栏 */
.relocation-quotation-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

/* 文档预览区域 */
.relocation-quotation-preview-section {
  flex: 1;
  overflow: hidden;
  background-color: #1e2430;
}

.relocation-quotation-preview-scroll {
  height: 100%;
  overflow-y: auto;
  padding: 2rem;
  display: flex;
  justify-content: center;
}

.relocation-quotation-preview-scroll::-webkit-scrollbar {
  width: 6px;
}

.relocation-quotation-preview-scroll::-webkit-scrollbar-track {
  background: transparent;
}

.relocation-quotation-preview-scroll::-webkit-scrollbar-thumb {
  background: #30363d;
  border-radius: 10px;
}

.relocation-quotation-paper {
  background-color: #fff;
  color: #0f172a;
  width: 842px;
  min-height: 1190px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  border-radius: 2px;
  padding: 48px;
  transform-origin: top center;
  display: flex;
  flex-direction: column;
}

.relocation-quotation-paper-inner {
  flex: 1;
  display: flex;
  flex-direction: column;
}

/* 文档头部 */
.rq-doc-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 48px;
}

.rq-doc-header-left {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rq-doc-logo {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.rq-doc-logo .material-symbols-outlined {
  font-size: 28px;
  color: #067bf9;
}

.rq-doc-logo-text {
  font-size: 24px;
  font-weight: 700;
  letter-spacing: -0.025em;
}

.rq-doc-title {
  font-size: 28px;
  font-weight: 900;
  color: #1e293b;
  margin: 0;
}

.rq-doc-subtitle {
  font-size: 14px;
  color: #64748b;
  margin: 8px 0 0 0;
}

.rq-doc-header-right {
  text-align: right;
}

.rq-doc-status {
  display: inline-block;
  padding: 8px 16px;
  border: 2px solid #067bf9;
  color: #067bf9;
  font-weight: 700;
  border-radius: 8px;
  margin-bottom: 8px;
  font-size: 12px;
}

.rq-doc-date {
  font-size: 12px;
  color: #94a3b8;
  margin: 0;
}

/* 信息网格 */
.rq-info-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 32px;
  margin-bottom: 48px;
  padding-bottom: 32px;
  border-bottom: 1px solid #f1f5f9;
}

.rq-info-block {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rq-info-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #94a3b8;
  margin: 0 0 4px 0;
}

.rq-info-title {
  font-weight: 700;
  color: #0f172a;
  margin: 0;
  font-size: 14px;
}

.rq-info-text {
  font-size: 13px;
  color: #64748b;
  margin: 0;
}

.rq-info-highlight {
  font-weight: 500;
  color: #1e293b;
}

/* 报价表格 */
.rq-table-section {
  flex: 1;
  margin-bottom: 48px;
}

.rq-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
}

.rq-th {
  padding: 12px 8px;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
  border-bottom: 2px solid #0f172a;
}

.rq-th-right {
  text-align: right;
}

.rq-group-row {
  background-color: rgba(241, 245, 249, 0.5);
}

.rq-group-cell {
  padding: 12px 8px;
  font-size: 13px;
  font-weight: 700;
  color: #067bf9;
}

.rq-item-row {
  border-bottom: 1px solid #f1f5f9;
}

.rq-td {
  padding: 16px 8px;
  font-size: 13px;
  color: #334155;
}

.rq-td-name {
  font-weight: 500;
}

.rq-td-desc {
  font-size: 11px;
  color: #94a3b8;
}

.rq-td-right {
  text-align: right;
}

.rq-td-total {
  font-weight: 500;
}

/* 汇总区域 */
.rq-summary {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 48px;
}

.rq-summary-box {
  width: 256px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.rq-summary-row {
  display: flex;
  justify-content: space-between;
  font-size: 13px;
}

.rq-summary-label {
  color: #64748b;
}

.rq-summary-value {
  font-weight: 500;
  color: #0f172a;
}

.rq-summary-divider {
  height: 1px;
  background-color: #0f172a;
  margin: 8px 0;
}

.rq-summary-total-row {
  align-items: baseline;
}

.rq-summary-total-label {
  font-size: 14px;
  font-weight: 700;
  color: #0f172a;
}

.rq-summary-total-value {
  font-size: 24px;
  font-weight: 900;
  color: #067bf9;
}

/* 条款说明 */
.rq-terms {
  margin-top: auto;
  padding-top: 32px;
  border-top: 1px solid #f1f5f9;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 32px;
  font-size: 10px;
  color: #94a3b8;
}

.rq-terms-col {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.rq-terms-title {
  font-weight: 700;
  margin: 0 0 4px 0;
}

.rq-terms-list {
  margin: 0;
  padding-left: 16px;
}

.rq-terms-list li {
  margin-bottom: 2px;
}

.rq-terms-text {
  margin: 0;
  line-height: 1.5;
}

/* ========== 配置侧边栏 ========== */
.relocation-quotation-sidebar {
  width: 320px;
  background-color: #161b22;
  border-left: 1px solid #30363d;
  display: flex;
  flex-direction: column;
  padding: 24px;
  gap: 24px;
  overflow-y: auto;
}

.rq-sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.rq-sidebar-title {
  font-size: 18px;
  font-weight: 700;
  color: #fff;
  margin: 0;
}

.rq-sidebar-icon {
  color: #8b949e;
  cursor: pointer;
  transition: color 0.2s;
}

.rq-sidebar-icon:hover {
  color: #fff;
}

.rq-sidebar-section {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.rq-sidebar-label {
  font-size: 10px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: #8b949e;
}

.rq-sidebar-select-wrap {
  position: relative;
}

.rq-sidebar-select {
  width: 100%;
  padding: 10px 12px;
  padding-right: 36px;
  background-color: #0b0e14;
  border: 1px solid #30363d;
  border-radius: 8px;
  color: #fff;
  font-size: 13px;
  appearance: none;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.rq-sidebar-select:focus {
  border-color: #067bf9;
}

.rq-sidebar-select-icon {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  color: #8b949e;
  pointer-events: none;
  font-size: 20px;
}

.rq-sidebar-toggle-group {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
  padding: 4px;
  background-color: #0b0e14;
  border-radius: 8px;
}

.rq-sidebar-toggle-btn {
  padding: 8px 12px;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  background-color: transparent;
  color: #8b949e;
}

.rq-sidebar-toggle-btn:hover {
  color: #fff;
}

.rq-sidebar-toggle-btn.active {
  background-color: #067bf9;
  color: #fff;
  box-shadow: 0 4px 12px rgba(6, 123, 249, 0.3);
}

.rq-sidebar-templates {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.rq-sidebar-template {
  padding: 8px;
  border: 2px solid transparent;
  border-radius: 8px;
  background-color: #0b0e14;
  cursor: pointer;
  transition: all 0.2s;
}

.rq-sidebar-template:hover {
  border-color: #30363d;
}

.rq-sidebar-template.active {
  border-color: #067bf9;
  background-color: rgba(6, 123, 249, 0.1);
}

.rq-template-preview {
  width: 100%;
  aspect-ratio: 3/4;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  padding: 6px;
  gap: 4px;
}

.rq-template-classic {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.rq-template-classic .rq-tpl-bar {
  height: 8px;
  background-color: rgba(6, 123, 249, 0.2);
  border-radius: 99px;
}

.rq-template-classic .rq-tpl-line {
  height: 4px;
  width: 66%;
  background-color: #e2e8f0;
  border-radius: 99px;
}

.rq-template-classic .rq-tpl-body {
  flex: 1;
  border: 1px solid #f1f5f9;
  border-radius: 2px;
}

.rq-template-dark {
  background-color: #0f172a;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.rq-template-dark .rq-tpl-bar {
  height: 8px;
  background-color: #334155;
  border-radius: 99px;
}

.rq-template-dark .rq-tpl-line {
  height: 4px;
  width: 66%;
  background-color: #334155;
  border-radius: 99px;
}

.rq-template-dark .rq-tpl-body {
  flex: 1;
  border: 1px solid #334155;
  border-radius: 2px;
}

.rq-template-name {
  font-size: 10px;
  text-align: center;
  margin: 8px 0 0 0;
  color: #8b949e;
}

.rq-sidebar-template.active .rq-template-name {
  color: #fff;
}

/* 侧边栏底部 */
.rq-sidebar-footer {
  margin-top: auto;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rq-ai-suggestion {
  padding: 16px;
  background-color: rgba(6, 123, 249, 0.05);
  border: 1px solid rgba(6, 123, 249, 0.2);
  border-radius: 12px;
}

.rq-ai-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.rq-ai-header .material-symbols-outlined {
  font-size: 18px;
  color: #067bf9;
}

.rq-ai-title {
  font-size: 11px;
  font-weight: 700;
  color: #067bf9;
}

.rq-ai-text {
  font-size: 12px;
  color: #8b949e;
  line-height: 1.5;
  margin: 0;
}

.rq-sidebar-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.rq-action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.rq-action-btn .material-symbols-outlined {
  font-size: 18px;
}

.rq-action-secondary {
  background-color: #30363d;
  color: #fff;
}

.rq-action-secondary:hover {
  background-color: #484f58;
}

.rq-action-primary {
  background-color: #067bf9;
  color: #fff;
  padding: 16px;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(6, 123, 249, 0.3);
}

.rq-action-primary:hover {
  background-color: #0969da;
}

/* 弹窗过渡 */
.relocation-modal-enter-active,
.relocation-modal-leave-active {
  transition: opacity 0.2s ease;
}

.relocation-modal-enter-from,
.relocation-modal-leave-to {
  opacity: 0;
}

.relocation-modal-enter-from .relocation-quotation-window {
  opacity: 0;
  transform: translate(-50%, -45%);
}

.relocation-modal-leave-to .relocation-quotation-window:not(.maximized) {
  opacity: 0;
  transform: translate(-50%, -45%);
}

.relocation-modal-leave-to .relocation-quotation-window.maximized {
  opacity: 0;
}

@media print {
  .relocation-quotation-overlay {
    background: transparent !important;
    position: static !important;
    top: auto !important;
    left: auto !important;
    right: auto !important;
    bottom: auto !important;
  }
  .relocation-quotation-window {
    position: static !important;
    background: #fff !important;
    border: none !important;
    box-shadow: none !important;
    width: auto !important;
    height: auto !important;
    transform: none !important;
  }
  .relocation-quotation-header,
  .relocation-quotation-sidebar {
    display: none !important;
  }
  .relocation-quotation-preview-section {
    padding: 0 !important;
    background: #fff !important;
  }
  .relocation-quotation-paper {
    box-shadow: none !important;
  }

  /* 防止内容被分页截断 */
  .rq-doc-header,
  .rq-info-grid,
  .rq-info-block,
  .rq-table thead,
  .rq-table tbody tr,
  .rq-group-row,
  .rq-item-row,
  .rq-summary,
  .rq-terms {
    page-break-inside: avoid !important;
    break-inside: avoid !important;
  }
}

/* 用于PDF渲染时的防分页样式 */
.relocation-quotation-paper .rq-doc-header,
.relocation-quotation-paper .rq-info-grid,
.relocation-quotation-paper .rq-info-block,
.relocation-quotation-paper .rq-table thead,
.relocation-quotation-paper .rq-table tbody tr,
.relocation-quotation-paper .rq-summary,
.relocation-quotation-paper .rq-terms {
  break-inside: avoid;
  page-break-inside: avoid;
}
</style>
