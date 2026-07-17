<template>
  <div class="smart-matching">
    <BranchPageHeader @open-product-database="openProductDatabaseModal" />

    <main class="main-container">
      <div class="page-header">
        <div class="header-content">
          <div class="breadcrumb">
            <a @click="navigateToHome" class="breadcrumb-link">首页</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <span class="breadcrumb-current">智能匹配</span>
          </div>
          <h1 class="page-title">智能匹配</h1>
          <p class="page-description">系统自动匹配设备型号并计算价格，低置信度条目建议人工复核。</p>
        </div>
        <div class="header-right">
          <div class="steps-progress">
            <div class="step completed">
              <div class="step-number">1</div>
              <span class="step-label" @click="navigateToDocumentRecognition" style="cursor: pointer;">导入数据</span>
            </div>
            <div class="step-divider"></div>
            <div class="step active">
              <div class="step-number">2</div>
              <span class="step-label" @click="navigateToSmartMatching" style="cursor: pointer;">智能匹配</span>
            </div>
            <div class="step-divider"></div>
            <div class="step">
              <div class="step-number">3</div>
              <span class="step-label" @click="navigateToPriceAdjustment" style="cursor: pointer;">价格调整</span>
            </div>
            <div class="step-divider"></div>
            <div class="step">
              <div class="step-number">4</div>
              <span class="step-label" @click="navigateToQuotationGeneration" style="cursor: pointer;">生成报价</span>
            </div>
          </div>
        </div>
      </div>

      <!-- Empty State -->
      <div class="empty-state" v-if="tableData.length === 0 && !loading">
        <div class="empty-content">
          <span class="material-symbols-outlined empty-icon">device_search</span>
          <p class="empty-title">暂无数据</p>
          <p class="empty-subtitle">请先在"导入数据"页面上传Excel文件</p>
          <button class="btn-primary" @click="navigateToDocumentRecognition">
            <span class="material-symbols-outlined">upload_file</span>
            前往导入数据
          </button>
        </div>
      </div>

      <!-- Matching Progress -->
      <div class="matching-progress" v-if="matchingInProgress">
        <div class="progress-content">
          <span class="material-symbols-outlined progress-icon">sync</span>
          <div class="progress-info">
            <p class="progress-title">正在智能匹配中...</p>
            <p class="progress-status">已处理 {{ matchingCompleted }} / {{ matchingTotal }} 条数据</p>
          </div>
          <div class="progress-bar-wrapper">
            <div class="progress-bar" :style="{ width: matchingProgress + '%' }"></div>
          </div>
          <span class="progress-percent">{{ matchingProgress }}%</span>
          <button class="stop-matching-btn" @click="stopMatching" title="停止匹配">
            <span class="material-symbols-outlined">stop</span>
            停止
          </button>
        </div>
      </div>

      <!-- Stats Cards -->
      <div class="stats-grid" v-if="tableData.length > 0">
        <div class="stat-card">
          <span class="stat-label">导入总行数</span>
          <div class="stat-content">
            <span class="stat-value">{{ tableData.length }}</span>
            <span class="material-symbols-outlined stat-icon">list_alt</span>
          </div>
        </div>

        <div class="stat-card success">
          <div class="stat-bar"></div>
          <span class="stat-label">成功匹配 (高置信度)</span>
          <div class="stat-content">
            <span class="stat-value">{{ highConfidenceCount }}</span>
            <span class="material-symbols-outlined stat-icon">check_circle</span>
          </div>
        </div>

        <div class="stat-card warning">
          <div class="stat-bar"></div>
          <div class="stat-header">
            <span class="stat-label">需人工复核 (低置信度)</span>
            <span class="stat-badge" v-if="lowConfidenceCount > 0">待复核</span>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ lowConfidenceCount }}</span>
            <span class="material-symbols-outlined stat-icon">warning</span>
          </div>
        </div>

        <div class="stat-card error">
          <div class="stat-bar"></div>
          <div class="stat-header">
            <span class="stat-label">未匹配</span>
            <span class="stat-badge" v-if="unmatchedCount > 0">需处理</span>
          </div>
          <div class="stat-content">
            <span class="stat-value">{{ unmatchedCount }}</span>
            <span class="material-symbols-outlined stat-icon">error</span>
          </div>
        </div>
      </div>

      <!-- Data Table -->
      <div class="table-container" v-if="tableData.length > 0">
        <div class="sheet-tabs-bar" v-if="sheetNames.length > 1">
          <button
            v-for="sheet in sheetNames"
            :key="sheet"
            class="sheet-tab-btn"
            :class="{ active: sheet === activeSheetName }"
            @click="switchSheet(sheet)"
          >
            <span>{{ sheet }}</span>
            <span class="sheet-tab-count">{{ sheetGroups[sheet]?.length || 0 }}</span>
          </button>
        </div>
        <div class="table-header">
          <div class="table-controls-left">
            <div class="quote-mode-toggle">
              <span class="material-symbols-outlined">tune</span>
              <label class="mode-option" :class="{ active: quoteMode === 'standard' }">
                <input type="radio" value="standard" v-model="quoteMode" />
                <span>标准口径</span>
              </label>
              <label class="mode-option" :class="{ active: quoteMode === 'lenovo' }">
                <input type="radio" value="lenovo" v-model="quoteMode" />
                <span>联想框架</span>
              </label>
            </div>
            <div class="filter-select">
              <span class="material-symbols-outlined">filter_list</span>
              <select v-model="filterStatus">
                <option value="all">显示全部状态</option>
                <option value="low">仅显示低置信度</option>
                <option value="unmatched">仅显示未匹配</option>
                <option value="matched">仅显示已匹配</option>
                <template v-if="quoteMode === 'lenovo'">
                  <option value="lenovo_endtype_unmatched">端型未匹配</option>
                  <option value="lenovo_method_manual">手动命名方式</option>
                  <option value="lenovo_method_exact">精确命名方式</option>
                </template>
              </select>
            </div>
            <div class="data-source-select" v-if="quoteMode === 'standard'">
              <span class="material-symbols-outlined">storage</span>
              <select v-model="dataSource">
                <option value="datacenter">数据中心设备</option>
                <option value="office">办公设备</option>
                <option value="hybrid">混合模式</option>
              </select>
            </div>
            <button
              v-if="quoteMode === 'lenovo'"
              class="lenovo-config-btn"
              @click="showLenovoConfig = true"
              title="联想框架报价默认参数"
            >
              <span class="material-symbols-outlined">settings_applications</span>
              <span>联想配置</span>
            </button>
            <div class="pricing-params-dropdown" v-click-outside="closePricingParamsDropdown">
              <button class="pricing-params-btn" @click="togglePricingParamsDropdown" :class="{ active: showPricingParamsDropdown }">
                <span class="material-symbols-outlined">tune</span>
                <span>调价参数</span>
                <span class="material-symbols-outlined dropdown-arrow">expand_more</span>
              </button>
              <div class="pricing-params-panel" v-if="showPricingParamsDropdown">
                <div class="params-panel-header">
                  <span class="params-panel-title">调价参数设置</span>
                  <span class="params-panel-desc">启用后将在报价计算时应用</span>
                </div>
                <div class="params-list">
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">workspace_premium</span>
                      <div class="param-text">
                        <span class="param-name">服务模式</span>
                        <span class="param-desc">金牌/银牌/铜牌服务费率</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.serviceMode" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">schedule</span>
                      <div class="param-text">
                        <span class="param-name">时效因子</span>
                        <span class="param-desc">SLA服务级别系数</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.slaFactor" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">memory</span>
                      <div class="param-text">
                        <span class="param-name">硬件折旧系数</span>
                        <span class="param-desc">设备年折旧率调整</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.hardwareDepreciation" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                  <div class="param-item">
                    <div class="param-info">
                      <span class="material-symbols-outlined param-icon">public</span>
                      <div class="param-text">
                        <span class="param-name">区域调节系数</span>
                        <span class="param-desc">地区价格系数</span>
                      </div>
                    </div>
                    <label class="param-switch">
                      <input type="checkbox" v-model="pricingParams.regionalAdjustment" />
                      <span class="switch-slider"></span>
                    </label>
                  </div>
                </div>
                <div class="params-panel-footer">
                  <button class="params-reset-btn" @click="resetPricingParams">重置为默认</button>
                  <button class="params-apply-btn" @click="applyPricingParams">应用设置</button>
                </div>
              </div>
            </div>
            <button
              class="dedupe-btn"
              :class="{ active: dedupeEnabled }"
              @click="toggleDedupe"
              :title="dedupeEnabled ? '已开启去重：相同「原始品牌型号」仅展示一条，再次点击恢复全部' : '开启后相同「原始品牌型号」仅展示一条，便于快速报价'"
            >
              <span class="material-symbols-outlined">filter_alt</span>
              <span>去重</span>
              <span v-if="dedupeEnabled && dedupeHiddenCount > 0" class="dedupe-count">-{{ dedupeHiddenCount }}</span>
            </button>
          </div>
          <div class="table-controls-right">
            <button class="btn-danger" @click="deleteSelectedRows" :disabled="selectedRows.size === 0">
              <span class="material-symbols-outlined">delete</span>
              删除
              <span v-if="selectedRows.size > 0" class="delete-count">({{ selectedRows.size }})</span>
            </button>
            <button class="btn-secondary" @click="startMatching" :disabled="matchingInProgress">
              <span class="material-symbols-outlined">refresh</span>
              重新匹配
            </button>
            <button class="btn-primary" @click="exportData">
              <span class="material-symbols-outlined">download</span>
              导出数据
            </button>
          </div>
        </div>

        <div class="table-wrapper" ref="tableWrapperRef">
          <table class="data-table">
            <thead>
              <tr>
                <th class="col-checkbox">
                  <label class="custom-checkbox" @click="toggleSelectAll">
                    <span class="checkbox-circle" :class="{ 'checked': isAllSelected, 'indeterminate': isPartialSelected }">
                      <span class="material-symbols-outlined" v-if="isAllSelected">check</span>
                      <span class="material-symbols-outlined" v-else-if="isPartialSelected">remove</span>
                    </span>
                  </label>
                </th>
                <th class="col-index">序号</th>
                <th class="col-manufacturer">厂商</th>
                <th class="col-model">原始品牌型号</th>
                <th class="col-category">分类</th>
                <th class="col-service-level">服务级别</th>
                <template v-if="quoteMode === 'standard'">
                  <th class="col-match">匹配型号</th>
                  <th class="col-confidence">置信度</th>
                  <th class="col-price">原始单价</th>
                  <th class="col-coefficient">服务系数</th>
                  <th class="col-adjusted-price">调整后单价</th>
                </template>
                <template v-else>
                  <th class="col-match">匹配型号</th>
                  <th class="col-end-type">端型</th>
                  <th class="col-sub-category">子类</th>
                  <th class="col-match-method">命中方式</th>
                  <th class="col-price">单价</th>
                  <th class="col-adjusted-price">总价</th>
                </template>
                <th class="col-actions">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="topPadding > 0" :style="{ height: topPadding + 'px' }" class="virtual-spacer"><td></td></tr>
              <tr
                v-for="(item, i) in visibleItems"
                :key="item._uid"
                :style="{ height: ROW_HEIGHT + 'px' }"
                :class="{
                  'warning-row': item.matchRate > 0 && item.matchRate < 70,
                  'error-row': !item.matchedModel || item.matchRate === 0
                }"
              >
                <td class="col-checkbox">
                  <label class="custom-checkbox" @click="toggleRowSelection(item)">
                    <span class="checkbox-circle" :class="{ 'checked': isRowSelected(item) }">
                      <span class="material-symbols-outlined" v-if="isRowSelected(item)">check</span>
                    </span>
                  </label>
                </td>
                <td class="col-index">{{ startIndex + i + 1 }}</td>
                <td class="col-manufacturer">{{ item.manufacturer || '-' }}</td>
                <td class="col-model">
                  <span class="original-model">{{ item.originalBrandModel || '-' }}</span>
                </td>
                <td class="col-category">
                  <template v-if="quoteMode === 'lenovo'">
                    {{ item.lenovo_device_category || item.lenovo_matched_device_category || item.deviceCategory || '-' }}
                  </template>
                  <template v-else>{{ item.deviceCategory || '-' }}</template>
                </td>
                <td class="col-service-level">{{ getEffectiveServiceLevel(item) || '-' }}</td>
                <template v-if="quoteMode === 'standard'">
                  <td class="col-match">
                    <div class="match-cell-wrapper">
                    <span
                      class="matched-model"
                      :class="{
                        'high-match': item.matchRate >= 70,
                        'mid-match': item.matchRate >= 50 && item.matchRate < 70,
                        'low-match': item.matchRate > 0 && item.matchRate < 50,
                        'no-match': !item.matchedModel || item.matchRate === 0
                      }"
                      @click="openSearch(item)"
                      :title="'点击修改匹配型号'"
                    >
                      {{ item.matchedModel || '未匹配' }}
                    </span>
                      <button
                        v-if="item.matchedModel"
                        class="clear-match-btn"
                        @click.stop="clearMatchResult(item)"
                        title="清空匹配结果"
                      >
                        <span class="material-symbols-outlined">close</span>
                      </button>
                    </div>
                  </td>
                  <td class="col-confidence">
                    <span
                      class="confidence-badge"
                      :class="{
                        'high': item.matchRate >= 70,
                        'mid': item.matchRate >= 50 && item.matchRate < 70,
                        'low': item.matchRate > 0 && item.matchRate < 50,
                        'none': !item.matchedModel || item.matchRate === 0
                      }"
                    >
                      {{ item.matchRate ? Math.round(item.matchRate) + '%' : '-' }}
                    </span>
                  </td>
                  <td class="col-price">{{ item.originalPrice ? '¥' + item.originalPrice.toFixed(2) : '-' }}</td>
                  <td class="col-coefficient">
                    <span v-if="item.serviceLevelCoefficient !== 1" class="coefficient-value">
                      {{ item.serviceLevelCoefficient.toFixed(2) }}
                    </span>
                    <span v-else>-</span>
                  </td>
                  <td class="col-adjusted-price">{{ item.price ? '¥' + item.price.toFixed(2) : '-' }}</td>
                </template>
                <template v-else>
                  <td class="col-match">
                    <div class="match-cell-wrapper">
                      <span
                        class="matched-model"
                        :class="{
                          'high-match': item.lenovo_match_method === 'exact' || item.lenovo_match_method === 'manual',
                          'mid-match': item.lenovo_match_method === 'fuzzy' || item.lenovo_match_method === 'pattern',
                          'no-match': !item.lenovo_match_method || item.lenovo_match_method === 'none'
                        }"
                        @click="openLenovoSearch(item)"
                        :title="'点击修改匹配型号'"
                      >
                        {{ lenovoDisplayModel(item) }}
                      </span>
                      <button
                        v-if="item.lenovo_manual_lock_model"
                        class="clear-match-btn"
                        @click.stop="clearLenovoManualLock(item)"
                        title="清除手动锁定"
                      >
                        <span class="material-symbols-outlined">close</span>
                      </button>
                    </div>
                  </td>
                  <td class="col-end-type">
                    <div class="end-type-cell-wrapper">
                      <span
                        class="lenovo-end-type-badge clickable"
                        :class="{ 'manual-locked': item.lenovo_manual_end_type, 'empty': !item.lenovo_end_type }"
                        @click="openEndTypeDropdown(item, $event)"
                        title="点击修改端型（同型号其他行同步生效）"
                      >
                        {{ item.lenovo_end_type || '点击选择' }}
                        <span class="material-symbols-outlined dropdown-icon">expand_more</span>
                      </span>
                      <button
                        v-if="item.lenovo_manual_end_type"
                        class="clear-match-btn"
                        @click.stop="clearLenovoManualEndType(item)"
                        title="清除手动锁定的端型"
                      >
                        <span class="material-symbols-outlined">close</span>
                      </button>
                    </div>
                  </td>
                  <td class="col-sub-category">{{ item.lenovo_sub_category || '-' }}</td>
                  <td class="col-match-method">
                    <span class="match-method-badge" :class="'method-' + (item.lenovo_match_method || 'none')">
                      {{ formatLenovoMethod(item.lenovo_match_method) }}
                    </span>
                  </td>
                  <td class="col-price">{{ item.lenovo_unit_price ? '¥' + Number(item.lenovo_unit_price).toFixed(2) : '-' }}</td>
                  <td class="col-adjusted-price">{{ item.lenovo_total_price ? '¥' + Number(item.lenovo_total_price).toFixed(2) : '-' }}</td>
                </template>
                <td class="col-actions">
                  <button
                    v-if="quoteMode === 'standard'"
                    class="action-btn edit"
                    @click="openSearch(item)"
                    title="修改匹配"
                  >
                    <span class="material-symbols-outlined">edit</span>
                  </button>
                  <button
                    v-else
                    class="action-btn edit"
                    @click="openLenovoRowEditor(item, startIndex + i)"
                    title="修改联想参数"
                  >
                    <span class="material-symbols-outlined">tune</span>
                  </button>
                </td>
              </tr>
              <tr v-if="bottomPadding > 0" :style="{ height: bottomPadding + 'px' }" class="virtual-spacer"><td></td></tr>
            </tbody>
          </table>
        </div>

        <div class="table-footer">
          <span class="footer-text">显示 {{ filteredTableData.length }} 条数据，共 {{ tableData.length }} 条</span>
        </div>
      </div>
    </main>

    <!-- 联想框架默认参数对话框 -->
    <div class="dialog-overlay" v-if="showLenovoConfig" @click="showLenovoConfig = false">
      <div class="dialog-content lenovo-config-dialog" @click.stop>
        <div class="dialog-header">
          <h3 class="dialog-title">联想框架报价 - 默认参数</h3>
          <button class="dialog-close" @click="showLenovoConfig = false">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <p class="lenovo-config-tip">这些默认值会应用到所有行；每行可单独覆盖。</p>
          <div class="lenovo-form-grid">
            <div class="lenovo-form-item">
              <label>设备大类</label>
              <select v-model="lenovoDefaults.device_category">
                <option value="磁带库">磁带库</option>
                <option value="光纤交换机">光纤交换机 (FC)</option>
                <option value="IB交换机">IB 交换机</option>
                <option value="网络设备">网络设备</option>
                <option value="服务器">服务器</option>
                <option value="存储">存储</option>
                <option value="小型机">小型机</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>默认 SLA</label>
              <input v-model="lenovoDefaults.sla" placeholder="例：7*24*NCD" />
            </div>
            <div class="lenovo-form-item">
              <label>磁带库驱动器配置</label>
              <select v-model="lenovoDefaults.drive_config">
                <option value="LTO5">LTO5</option>
                <option value="LTO6">LTO6</option>
                <option value="LTO7">LTO7</option>
                <option value="LTO8">LTO8</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>网络子类（device_category=网络设备 时）</label>
              <select v-model="lenovoDefaults.sub_category">
                <option value="网络交换机">网络交换机</option>
                <option value="路由器">路由器</option>
                <option value="无线控制器">无线控制器</option>
                <option value="无线AP">无线 AP</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>服务器：含 SSD</label>
              <select v-model="lenovoDefaults.includes_ssd">
                <option :value="false">不含</option>
                <option :value="true">含</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>服务器：报价类型</label>
              <select v-model="lenovoDefaults.package_type">
                <option value="备件维保">备件维保</option>
                <option value="整包">整包</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>服务器/小机：含硬盘不返还</label>
              <select v-model="lenovoDefaults.includes_disk">
                <option :value="false">不含</option>
                <option :value="true">含</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>存储：含硬盘不回收</label>
              <select v-model="lenovoDefaults.includes_disk_no_return">
                <option :value="false">不含</option>
                <option :value="true">含</option>
              </select>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showLenovoConfig = false">关闭</button>
          <button class="btn-primary" @click="applyLenovoDefaultsToAll">应用到所有行</button>
        </div>
      </div>
    </div>

    <!-- 联想单行参数编辑对话框 -->
    <div class="dialog-overlay" v-if="showLenovoRowEditor !== null" @click="showLenovoRowEditor = null">
      <div class="dialog-content lenovo-config-dialog" @click.stop v-if="lenovoRowDraft">
        <div class="dialog-header">
          <h3 class="dialog-title">编辑联想参数（第 {{ lenovoEditorRowNumber }} 行）</h3>
          <button class="dialog-close" @click="showLenovoRowEditor = null">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="lenovo-form-grid">
            <div class="lenovo-form-item">
              <label>设备大类</label>
              <select v-model="lenovoRowDraft.device_category">
                <option value="磁带库">磁带库</option>
                <option value="光纤交换机">光纤交换机 (FC)</option>
                <option value="IB交换机">IB 交换机</option>
                <option value="网络设备">网络设备</option>
                <option value="服务器">服务器</option>
                <option value="存储">存储</option>
                <option value="小型机">小型机</option>
              </select>
            </div>
            <div class="lenovo-form-item">
              <label>SLA</label>
              <input v-model="lenovoRowDraft.sla" />
            </div>
            <div class="lenovo-form-item" v-if="lenovoRowDraft.device_category === '磁带库'">
              <label>驱动器配置</label>
              <select v-model="lenovoRowDraft.drive_config">
                <option value="LTO5">LTO5</option>
                <option value="LTO6">LTO6</option>
                <option value="LTO7">LTO7</option>
                <option value="LTO8">LTO8</option>
              </select>
            </div>
            <div class="lenovo-form-item" v-if="lenovoRowDraft.device_category === '网络设备'">
              <label>子类</label>
              <select v-model="lenovoRowDraft.sub_category">
                <option value="网络交换机">网络交换机</option>
                <option value="路由器">路由器</option>
                <option value="无线控制器">无线控制器</option>
                <option value="无线AP">无线 AP</option>
              </select>
            </div>
            <template v-if="lenovoRowDraft.device_category === '服务器'">
              <div class="lenovo-form-item">
                <label>含 SSD</label>
                <select v-model="lenovoRowDraft.includes_ssd">
                  <option :value="false">不含</option>
                  <option :value="true">含</option>
                </select>
              </div>
              <div class="lenovo-form-item">
                <label>报价类型</label>
                <select v-model="lenovoRowDraft.package_type">
                  <option value="备件维保">备件维保</option>
                  <option value="整包">整包</option>
                </select>
              </div>
              <div class="lenovo-form-item">
                <label>含硬盘不返还</label>
                <select v-model="lenovoRowDraft.includes_disk">
                  <option :value="false">不含</option>
                  <option :value="true">含</option>
                </select>
              </div>
            </template>
            <div class="lenovo-form-item" v-if="lenovoRowDraft.device_category === '小型机'">
              <label>含硬盘不返还</label>
              <select v-model="lenovoRowDraft.includes_disk">
                <option :value="false">不含</option>
                <option :value="true">含</option>
              </select>
            </div>
            <div class="lenovo-form-item" v-if="lenovoRowDraft.device_category === '存储'">
              <label>含硬盘不回收</label>
              <select v-model="lenovoRowDraft.includes_disk_no_return">
                <option :value="false">不含</option>
                <option :value="true">含</option>
              </select>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="showLenovoRowEditor = null">取消</button>
          <button class="btn-primary" @click="saveLenovoRowEditor">保存并重新报价</button>
        </div>
      </div>
    </div>

    <!-- Search Dialog -->
    <div class="dialog-overlay" v-if="showSearchDialog" @click="closeSearchDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3 class="dialog-title">手动搜索设备</h3>
          <button class="dialog-close" @click="closeSearchDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <!-- 数据源选择 -->
          <div class="search-source-selector">
            <label class="source-label">数据来源：</label>
            <div class="source-options">
              <label class="source-option">
                <input
                  type="radio"
                  name="searchDataSource"
                  value="datacenter"
                  v-model="searchDataSource"
                  @change="onSearchDataSourceChange"
                />
                <span class="source-radio"></span>
                <span class="source-name">数据中心设备</span>
              </label>
              <label class="source-option">
                <input
                  type="radio"
                  name="searchDataSource"
                  value="office"
                  v-model="searchDataSource"
                  @change="onSearchDataSourceChange"
                />
                <span class="source-radio"></span>
                <span class="source-name">办公设备</span>
              </label>
              <label class="source-option">
                <input
                  type="radio"
                  name="searchDataSource"
                  value="hybrid"
                  v-model="searchDataSource"
                  @change="onSearchDataSourceChange"
                />
                <span class="source-radio"></span>
                <span class="source-name">混合模式</span>
              </label>
            </div>
          </div>

          <div class="search-input-group">
            <span class="material-symbols-outlined">search</span>
            <input
              ref="searchInputRef"
              type="text"
              v-model="searchQuery"
              @input="handleSearchInput"
              placeholder="输入设备型号搜索..."
              class="search-input-field"
            />
          </div>
          <div class="search-results" v-if="searchLoading">
            <div class="search-loading">
              <span class="material-symbols-outlined loading-icon">sync</span>
              <span>搜索中...</span>
            </div>
          </div>
          <div class="search-results" v-else-if="searchResults.length > 0">
            <div class="results-header">找到 {{ totalResults }} 条结果</div>
            <div class="results-list">
              <div
                v-for="result in searchResults"
                :key="result.id"
                class="result-item"
                @click="selectSearchResult(result)"
              >
                <div class="result-info">
                  <div class="result-model">{{ result.model_number || result.model }}</div>
                  <div class="result-details">
                    {{ result.manufacturer }} • {{ result.primary_category }} >
                    {{ result.secondary_category }} > {{ result.tertiary_category }}
                  </div>
                </div>
                <div class="result-price" v-if="result.device_price">
                  ¥{{ result.device_price.toFixed(2) }}
                </div>
              </div>
            </div>
            <div class="results-pagination" v-if="totalResults > pageSize">
              <button
                class="page-btn"
                :disabled="searchPage === 1"
                @click="changeSearchPage(searchPage - 1)"
              >
                <span class="material-symbols-outlined">chevron_left</span>
              </button>
              <span class="page-info">第 {{ searchPage }} 页</span>
              <button
                class="page-btn"
                :disabled="searchPage * pageSize >= totalResults"
                @click="changeSearchPage(searchPage + 1)"
              >
                <span class="material-symbols-outlined">chevron_right</span>
              </button>
            </div>
          </div>
          <div class="search-results" v-else-if="searchQuery && searchQuery.length >= 2">
            <div class="no-results">
              <span class="material-symbols-outlined">search_off</span>
              <span>未找到匹配的设备</span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeSearchDialog">取消</button>
        </div>
      </div>
    </div>

    <!-- 联想框架"匹配型号"搜索弹窗 -->
    <div class="dialog-overlay" v-if="showLenovoSearchDialog" @click="closeLenovoSearchDialog">
      <div class="dialog-content" @click.stop>
        <div class="dialog-header">
          <h3 class="dialog-title">搜索联想框架机型</h3>
          <button class="dialog-close" @click="closeLenovoSearchDialog">
            <span class="material-symbols-outlined">close</span>
          </button>
        </div>
        <div class="dialog-body">
          <div class="search-input-group">
            <span class="material-symbols-outlined">search</span>
            <input
              ref="lenovoSearchInputRef"
              type="text"
              v-model="lenovoSearchQuery"
              @input="handleLenovoSearchInput"
              placeholder="输入型号/品牌/系列搜索..."
              class="search-input-field"
            />
          </div>
          <div class="search-results" v-if="lenovoSearchLoading">
            <div class="search-loading">
              <span class="material-symbols-outlined loading-icon">sync</span>
              <span>搜索中...</span>
            </div>
          </div>
          <div class="search-results" v-else-if="lenovoSearchResults.length > 0">
            <div class="results-header">找到 {{ lenovoSearchResults.length }} 条结果</div>
            <div class="results-list">
              <div
                v-for="result in lenovoSearchResults"
                :key="result.id"
                class="result-item"
                @click="selectLenovoSearchResult(result)"
              >
                <div class="result-info">
                  <div class="result-model">{{ result.model }}</div>
                  <div class="result-details">
                    {{ result.brand || '-' }}
                    <span v-if="result.series"> • {{ result.series }}</span>
                    • {{ result.device_category }}
                    <span v-if="result.sub_category"> / {{ result.sub_category }}</span>
                    • 端型: <strong>{{ result.end_type }}</strong>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="search-results" v-else-if="lenovoSearchQuery && lenovoSearchQuery.length >= 1">
            <div class="no-results">
              <span class="material-symbols-outlined">search_off</span>
              <span>未找到对应机型</span>
            </div>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn-secondary" @click="closeLenovoSearchDialog">取消</button>
        </div>
      </div>
    </div>

    <!-- 联想框架"对应关系"批量确认弹窗（点"下一步：价格调整"时触发） -->
    <Teleport to="body">
      <div v-if="showPendingAliasesDialog" class="alias-batch-overlay" @click.self="closePendingAliasesDialog">
        <div class="alias-batch-dialog">
          <div class="alias-batch-header">
            <div>
              <h3>确认本次手动调整的对应关系</h3>
              <p class="alias-batch-tip">
                本次共调整了 <strong>{{ pendingAliases.length }}</strong> 条「原始品牌型号 → 标准记录」对应关系。
                选中后写入机型库，下次再遇到相同的「原始品牌型号」将直接命中，无需再次手动。
              </p>
            </div>
            <button class="alias-batch-close" @click="closePendingAliasesDialog">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>

          <div class="alias-batch-body">
            <table class="alias-batch-table">
              <thead>
                <tr>
                  <th class="col-check">
                    <label class="batch-checkbox" @click.prevent="toggleAllAliasesSelected">
                      <span class="cb-circle" :class="{ checked: isAllAliasesSelected, indeterminate: isPartialAliasesSelected }">
                        <span class="material-symbols-outlined" v-if="isAllAliasesSelected">check</span>
                        <span class="material-symbols-outlined" v-else-if="isPartialAliasesSelected">remove</span>
                      </span>
                    </label>
                  </th>
                  <th class="col-raw">原始品牌型号</th>
                  <th class="col-arrow">→</th>
                  <th class="col-model">标准型号</th>
                  <th class="col-endtype">端型</th>
                  <th class="col-cat">大类</th>
                  <th class="col-rows">影响行数</th>
                  <th class="col-src">来源</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="alias in pendingAliases" :key="alias.id"
                    :class="{ selected: selectedAliasIds.has(alias.id) }"
                    @click="toggleAliasSelected(alias.id)">
                  <td class="col-check">
                    <label class="batch-checkbox" @click.prevent.stop="toggleAliasSelected(alias.id)">
                      <span class="cb-circle" :class="{ checked: selectedAliasIds.has(alias.id) }">
                        <span class="material-symbols-outlined" v-if="selectedAliasIds.has(alias.id)">check</span>
                      </span>
                    </label>
                  </td>
                  <td class="col-raw mono">{{ alias.rawBrandModel }}</td>
                  <td class="col-arrow">→</td>
                  <td class="col-model mono">{{ alias.model }}</td>
                  <td class="col-endtype"><span class="alias-end-badge">{{ alias.end_type }}</span></td>
                  <td class="col-cat">{{ alias.device_category }}</td>
                  <td class="col-rows">{{ alias.affected_rows }}</td>
                  <td class="col-src">
                    <span class="alias-src-badge" :class="alias.source">
                      {{ alias.source === 'end-type' ? '端型选择' : '匹配型号' }}
                    </span>
                  </td>
                </tr>
              </tbody>
            </table>
            <div v-if="pendingAliases.length === 0" class="empty-state">
              <span class="material-symbols-outlined">inventory_2</span>
              <p>暂无对应关系</p>
            </div>
          </div>

          <div class="alias-batch-footer">
            <div class="footer-info">已选 {{ selectedAliasIds.size }} / {{ pendingAliases.length }}</div>
            <div class="footer-actions">
              <button class="btn-danger" :disabled="selectedAliasIds.size === 0 || pendingAliasesProcessing" @click="removePendingAliases">
                <span class="material-symbols-outlined">delete_sweep</span>
                移除选中
              </button>
              <button class="btn-secondary" :disabled="pendingAliasesProcessing" @click="skipAllPendingAliases">
                全部跳过
              </button>
              <button class="btn-primary" :disabled="selectedAliasIds.size === 0 || pendingAliasesProcessing" @click="confirmSelectedAliases">
                <span class="material-symbols-outlined" v-if="pendingAliasesProcessing">sync</span>
                <span class="material-symbols-outlined" v-else>check_circle</span>
                {{ pendingAliasesProcessing ? '写入中...' : `记住选中（${selectedAliasIds.size}）` }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- 联想"端型"下拉浮层（Teleport 到 body 避免表格 overflow 截断） -->
    <Teleport to="body">
      <div
        v-if="endTypeDropdownVisible"
        class="end-type-dropdown"
        :style="{ top: endTypeDropdownPosition.top, left: endTypeDropdownPosition.left }"
        @click.stop
      >
        <div class="dropdown-title">选择端型</div>
        <div class="dropdown-list">
          <div v-if="endTypeLoading" class="dropdown-loading">
            <span class="material-symbols-outlined spinning">sync</span>
            <span>加载中...</span>
          </div>
          <template v-else>
            <div
              v-for="opt in endTypeOptions"
              :key="opt"
              class="dropdown-option"
              :class="{ active: endTypeDropdownTarget?.lenovo_end_type === opt }"
              @click="selectEndType(opt)"
            >
              <span>{{ opt }}</span>
              <span v-if="endTypeDropdownTarget?.lenovo_end_type === opt" class="material-symbols-outlined">check</span>
            </div>
            <div v-if="endTypeOptions.length === 0" class="dropdown-empty">该设备大类暂无可选端型</div>
          </template>
        </div>
      </div>
      <div v-if="endTypeDropdownVisible" class="end-type-dropdown-mask" @click="closeEndTypeDropdown"></div>
    </Teleport>

    <!-- Sticky Bottom Bar -->
    <div class="bottom-bar" v-if="tableData.length > 0">
      <div class="bottom-content">
        <div class="bottom-info" v-if="lowConfidenceCount > 0 || unmatchedCount > 0">
          <span class="material-symbols-outlined">info</span>
          <span>还有 <strong>{{ lowConfidenceCount + unmatchedCount }}</strong> 个条目需要处理</span>
        </div>
        <div class="bottom-info" v-else>
          <span class="material-symbols-outlined" style="color: #22c55e;">check_circle</span>
          <span>所有条目已完成匹配</span>
        </div>
        <div class="bottom-actions">
          <button class="btn-back" @click="navigateToDocumentRecognition">
            <span class="material-symbols-outlined">arrow_back</span>
            上一步
          </button>
          <div class="action-buttons">
            <button class="btn-draft" @click="saveAsDraft" :disabled="isSavingDraft" :title="'快捷键: Ctrl+S'">
              <span class="material-symbols-outlined" v-if="!isSavingDraft">save</span>
              <span class="material-symbols-outlined spinning" v-else>sync</span>
              {{ isSavingDraft ? '保存中...' : '存为草稿' }}
            </button>
            <button class="btn-next" @click="goToPriceAdjustment" :disabled="isNavigating">
              <span class="material-symbols-outlined spinning" v-if="isNavigating">sync</span>
              <span v-else>下一步: 价格调整</span>
              <span class="material-symbols-outlined" v-if="!isNavigating">arrow_forward</span>
          </button>
          </div>
        </div>
      </div>
    </div>

    <div class="background-effects">
      <div class="effect-blob effect-top"></div>
      <div class="effect-blob effect-bottom"></div>
    </div>

    <!-- 产品数据库弹窗 -->
    <ProductDatabaseModal :is-open="isProductDatabaseModalOpen" @close="closeProductDatabaseModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick, shallowRef, triggerRef, watch } from 'vue'
import { useRouter, onBeforeRouteUpdate, onBeforeRouteLeave } from 'vue-router'
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'
import BranchPageHeader from '../components/BranchPageHeader.vue'
import ProductDatabaseModal from '../components/ProductDatabaseModal.vue'
import {
  PAGE_STATE_KEYS,
  FLOW_DATA_KEYS,
  savePageState,
  restorePageState,
  clearPageState,
  saveFlowData,
  clearFlowData,
  getFlowData,
  setNavigationMode,
  cleanupOldFlowData,
  type SmartMatchingState
} from '../stores/quotationStore'
import {
  saveDraft,
  getCurrentDraftId
} from '../utils/draftUtils'
import { useVirtualList } from '../composables/useVirtualList'

const router = useRouter()

// v-click-outside directive
const vClickOutside = {
  mounted(el: any, binding: any) {
    el._clickOutside = (event: MouseEvent) => {
      if (!(el === event.target || el.contains(event.target as Node))) {
        binding.value(event)
      }
    }
    document.addEventListener('click', el._clickOutside)
  },
  unmounted(el: any) {
    document.removeEventListener('click', el._clickOutside)
  }
}

// API Base URL
const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
// 使用 shallowRef 优化大数据量性能，只追踪数组引用变化而不追踪内部对象
const tableData = shallowRef<any[]>([])
const sheetGroups = ref<Record<string, any[]>>({})
const activeSheetName = ref('')
const sheetNames = computed(() => Object.keys(sheetGroups.value))
const loading = ref(false)
const isSavingDraft = ref(false)
const isNavigating = ref(false)
const matchingInProgress = ref(false)
const matchingTotal = ref(0)
const matchingCompleted = ref(0)
// 匹配运行代号：每次启动匹配自增，老的在途任务据此自我终止（用于切换去重时安全重启）
const matchGeneration = ref(0)
const matchingProgress = computed(() => {
  if (!matchingTotal.value) return 0
  return Math.floor((matchingCompleted.value / matchingTotal.value) * 100)
})

// Filter
const filterStatus = ref<
  'all' | 'low' | 'unmatched' | 'matched'
  // 联想框架专用筛选
  | 'lenovo_endtype_unmatched' | 'lenovo_method_manual' | 'lenovo_method_exact'
>('all')

// 去重展示开关：点亮后「原始品牌型号」相同的行仅展示一条（不删除数据，仅折叠展示）
// 便于报价时只看唯一型号；关闭后恢复展示全部行。
const dedupeEnabled = ref(false)
function toggleDedupe() {
  dedupeEnabled.value = !dedupeEnabled.value
}

// 点亮「去重」即自动触发一次重新匹配：按去重后的唯一「原始品牌型号」匹配，
// 结果回填到同值的所有行（关闭去重不重匹，因结果已应用到全部行）。
watch(dedupeEnabled, async (on) => {
  if (!on) return
  if (matchingInProgress.value) {
    // 终止正在进行的全量匹配（matchGeneration 自增使旧任务自我退出），再以去重方式重启
    stopMatching()
    await nextTick()
  }
  if (flattenSheetGroups().length === 0) return
  startMatching()
})

// Row selection for deletion（uid 化，避免 O(n²) indexOf）
const selectedRows = ref<Set<string>>(new Set())

// 表格滚动容器引用（用于虚拟滚动）
const tableWrapperRef = ref<HTMLElement | null>(null)
const ROW_HEIGHT = 56

// 行 uid 自增器
let _rowUidCounter = 0
function genRowUid(): string {
  return `r${++_rowUidCounter}`
}

// 给 sheetGroups 里没有 _uid 的旧行补 uid（处理从持久化状态恢复的旧数据）
function ensureRowUidsInSheetGroups(groups: Record<string, any[]>) {
  for (const sheetName of Object.keys(groups || {})) {
    const rows = groups[sheetName] || []
    for (const row of rows) {
      if (!row._uid) row._uid = genRowUid()
    }
  }
}

// Data source
const dataSource = ref<'datacenter' | 'office' | 'hybrid'>('datacenter')

// ============ 报价口径 ============
type QuoteMode = 'standard' | 'lenovo'
const quoteMode = ref<QuoteMode>('standard')

interface LenovoParams {
  device_category: string
  sla: string
  drive_config: string
  sub_category: string
  includes_ssd: boolean
  package_type: string
  includes_disk: boolean
  includes_disk_no_return: boolean
}

// 联想模式下"空 SLA"的默认值（同时也是"标准口径的空 SLA 占位符 7*24*NCR"被认为是空时的回填值）
const LENOVO_DEFAULT_SLA = '7*24*NCD'

const lenovoDefaults = ref<LenovoParams>({
  device_category: '服务器',
  sla: LENOVO_DEFAULT_SLA,
  drive_config: 'LTO7',
  sub_category: '网络交换机',
  includes_ssd: false,
  package_type: '整包',
  includes_disk: false,
  includes_disk_no_return: false,
})

/** 行在当前报价口径下生效的"服务级别"——用于表格展示 + 报价请求
 *
 * - 标准口径：用行内 serviceLevel（来自源数据 / 智能识别阶段）
 * - 联想框架：用行内 lenovo_sla（单行编辑覆盖）> 联想配置默认 SLA > 兜底
 *   联想模式不沿用源导入时自动填充的 SLA，避免被智能识别阶段的默认值（如 7*24*NBD）干扰
 */
function getEffectiveServiceLevel(row: any): string {
  if (quoteMode.value === 'lenovo') {
    return row?.lenovo_sla
      || lenovoDefaults.value.sla
      || LENOVO_DEFAULT_SLA
  }
  return (row?.serviceLevel ?? '').toString()
}

const showLenovoConfig = ref(false)
const showLenovoRowEditor = ref<any | null>(null)
const lenovoEditorRowNumber = ref<number>(0)
const lenovoRowDraft = ref<LenovoParams | null>(null)

// 行"分类"列 → 联想 device_category / sub_category 映射
const LENOVO_CATEGORY_MAP: Record<string, { device_category: string; sub_category?: string }> = {
  '磁带存储': { device_category: '磁带库' },
  '磁带库': { device_category: '磁带库' },
  '磁带机': { device_category: '磁带库' },
  '光纤交换机': { device_category: '光纤交换机' },
  'FC光纤交换机': { device_category: '光纤交换机' },
  'IB交换机': { device_category: 'IB交换机' },
  'IB光纤交换机': { device_category: 'IB交换机' },
  '网络交换机': { device_category: '网络设备', sub_category: '网络交换机' },
  '交换机': { device_category: '网络设备', sub_category: '网络交换机' },
  '路由器': { device_category: '网络设备', sub_category: '路由器' },
  '无线控制器': { device_category: '网络设备', sub_category: '无线控制器' },
  '无线AP': { device_category: '网络设备', sub_category: '无线AP' },
  '网络设备': { device_category: '网络设备' },
  '服务器': { device_category: '服务器' },
  'x86服务器': { device_category: '服务器' },
  '存储': { device_category: '存储' },
  'NAS存储': { device_category: '存储' },
  'SAN存储': { device_category: '存储' },
  '小型机': { device_category: '小型机' },
}

function autoDetectLenovoCategory(row: any): { device_category?: string; sub_category?: string } {
  const cat = String(row?.category || row?.deviceCategory || '').trim()
  if (!cat) return {}
  if (cat in LENOVO_CATEGORY_MAP) return LENOVO_CATEGORY_MAP[cat]
  for (const [key, val] of Object.entries(LENOVO_CATEGORY_MAP)) {
    if (cat.includes(key)) return val
  }
  return {}
}

// 剥离品牌前缀：HP-MSL3040 → MSL3040；惠普 MSL3040 → MSL3040
const LENOVO_BRAND_PREFIXES = [
  'HPE', 'HP', 'IBM', 'DELL EMC', 'DELL|EMC', 'DELL', 'EMC', 'Lenovo', '联想',
  'Huawei', '华为', 'Cisco', 'H3C', 'Brocade', 'Inspur', '浪潮',
  'Sugon', '曙光', 'Mellanox', '迈络思', '惠普', '慧与', 'NetApp',
  '昆腾', 'Quantum', 'Macroson', '宏杉', 'Foxconn', 'SuperMicro', '超微',
]

function stripBrandPrefix(model: string): string {
  if (!model) return ''
  let m = String(model).trim()
  // 反复剥离，处理 "HP-Lenovo-XXX" 这种叠加情况
  for (let i = 0; i < 3; i++) {
    let changed = false
    for (const b of LENOVO_BRAND_PREFIXES) {
      const esc = b.replace(/[-/\\^$*+?.()|[\]{}]/g, '\\$&')
      const re = new RegExp(`^${esc}[-_\\s/]+`, 'i')
      if (re.test(m)) {
        m = m.replace(re, '').trim()
        changed = true
        break
      }
    }
    if (!changed) break
  }
  return m
}

// 匹配型号显示：未命中（命中方式为 none/空）时显示"未匹配"，
// 不沿用后端透传回来的原始输入型号，避免误以为已命中。
function lenovoDisplayModel(item: any): string {
  const m = item?.lenovo_match_method
  if (!m || m === 'none') return '未匹配'
  return item.lenovo_matched_model || '未匹配'
}

function formatLenovoMethod(method: string | undefined): string {
  switch (method) {
    case 'exact': return '精确'
    case 'fuzzy': return '模糊'
    case 'pattern': return '兜底'
    case 'manual': return '手动'
    case 'none': return '未命中'
    default: return '-'
  }
}

function getRowLenovoParams(row: any): LenovoParams {
  // 优先级与 buildLenovoQuoteRequest 完全一致：
  //   行内手动覆盖 > 自动识别（行的"分类"列） > 联想配置全局默认
  const auto = autoDetectLenovoCategory(row)
  return {
    device_category:
      row.lenovo_device_category || auto.device_category || lenovoDefaults.value.device_category,
    // 服务级别走和表格展示一致的口径函数：联想模式下只受联想配置 / 单行覆盖控制，
    // 不受智能识别阶段自动填充的 SLA 影响
    sla: getEffectiveServiceLevel(row),
    drive_config: row.lenovo_drive_config || lenovoDefaults.value.drive_config,
    sub_category:
      row.lenovo_sub_category_input || auto.sub_category || lenovoDefaults.value.sub_category,
    includes_ssd: row.lenovo_includes_ssd ?? lenovoDefaults.value.includes_ssd,
    package_type: row.lenovo_package_type || lenovoDefaults.value.package_type,
    includes_disk: row.lenovo_includes_disk ?? lenovoDefaults.value.includes_disk,
    includes_disk_no_return: row.lenovo_includes_disk_no_return ?? lenovoDefaults.value.includes_disk_no_return,
  }
}

function applyLenovoDefaultsToAll() {
  showLenovoConfig.value = false
  // 联想模式下且有数据 → 直接用新默认参数重新跑一遍报价
  if (
    quoteMode.value === 'lenovo'
    && !matchingInProgress.value
    && flattenSheetGroups().length > 0
  ) {
    runLenovoBulkQuote()
  } else {
    ElMessage.success('已更新默认参数')
  }
}

function openLenovoRowEditor(item: any, displayIndex: number) {
  if (!item) return
  lenovoRowDraft.value = getRowLenovoParams(item)
  showLenovoRowEditor.value = item
  lenovoEditorRowNumber.value = displayIndex + 1
}

function saveLenovoRowEditor() {
  const row = showLenovoRowEditor.value
  if (!row || !lenovoRowDraft.value) return
  const draft = lenovoRowDraft.value
  row.lenovo_device_category = draft.device_category
  row.lenovo_sla = draft.sla
  row.lenovo_drive_config = draft.drive_config
  row.lenovo_sub_category_input = draft.sub_category
  row.lenovo_includes_ssd = draft.includes_ssd
  row.lenovo_package_type = draft.package_type
  row.lenovo_includes_disk = draft.includes_disk
  row.lenovo_includes_disk_no_return = draft.includes_disk_no_return
  syncActiveSheetGroup()
  // 重新报价单行
  quoteLenovoRows([row])
  showLenovoRowEditor.value = null
  lenovoRowDraft.value = null
}

// Pricing params dropdown
const showPricingParamsDropdown = ref(false)
const pricingParams = ref({
  serviceMode: true,
  slaFactor: true,
  hardwareDepreciation: false,
  regionalAdjustment: false
})

// Search dialog
const showSearchDialog = ref(false)
const activeModelRow = ref<any | null>(null)

// 联想框架"匹配型号"搜索弹窗
const showLenovoSearchDialog = ref(false)
const lenovoSearchTargetRow = ref<any | null>(null)
const lenovoSearchQuery = ref('')
const lenovoSearchResults = ref<any[]>([])
const lenovoSearchLoading = ref(false)
const lenovoSearchInputRef = ref<HTMLInputElement | null>(null)
let lenovoSearchTimeout: NodeJS.Timeout | null = null

// 联想框架"对应关系"批量确认队列
// 用户在端型列 / 匹配型号搜索弹窗里每次手动调整产生的「raw → 标准记录」对应关系，
// 都不立即弹窗，统一缓存到此队列，点"下一步：价格调整"前一次性批量确认。
interface PendingAliasItem {
  id: string                          // 去重 key: rawBrandModel + '|' + lower(device_category) + '|' + lower(model)
  rawBrandModel: string               // 用户上传的「原始品牌型号」
  device_category: string             // 联想大类
  brand: string                       // 标准记录的 brand
  model: string                       // 标准记录的 model
  end_type: string                    // 端型
  sub_category: string | null
  source: 'end-type' | 'manual-match' // 触发来源（用于备注）
  affected_rows: number               // 同 rawBrandModel 行数
}

const pendingAliases = ref<PendingAliasItem[]>([])

function queuePendingAlias(item: PendingAliasItem) {
  if (!item.id || !item.rawBrandModel || !item.model || !item.end_type) return
  const idx = pendingAliases.value.findIndex(x => x.id === item.id)
  if (idx >= 0) {
    pendingAliases.value[idx] = item   // 覆盖（用户反复调整同一型号时，保留最后一次）
  } else {
    pendingAliases.value.push(item)
  }
}

// 批量确认弹窗状态
const showPendingAliasesDialog = ref(false)
const selectedAliasIds = ref<Set<string>>(new Set())
const pendingAliasesProcessing = ref(false)
let _pendingAliasesResolver: ((action: 'navigate' | 'cancel') => void) | null = null

// 联想框架"端型"下拉
const endTypeDropdownVisible = ref(false)
const endTypeDropdownPosition = ref({ top: '0px', left: '0px' })
const endTypeDropdownTarget = ref<any | null>(null)
const endTypeOptions = ref<string[]>([])
const endTypeOptionsCache = ref<Record<string, string[]>>({})
const endTypeLoading = ref(false)
const searchQuery = ref('')
const searchResults = ref<any[]>([])
const searchLoading = ref(false)
const totalResults = ref(0)
const searchPage = ref(1)

// 产品数据库弹窗
const isProductDatabaseModalOpen = ref(false)

const openProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = true
}

const closeProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = false
}
const pageSize = 20
const searchInputRef = ref<HTMLInputElement | null>(null)
// 搜索对话框中的数据源选择（只对该次搜索有效）
const searchDataSource = ref<'datacenter' | 'office' | 'hybrid'>('datacenter')
let searchTimeout: NodeJS.Timeout | null = null

// Service levels cache (to avoid repeated API calls)
const serviceLevelsCache = ref<any[] | null>(null)

// AbortController for cancelling matching requests
const abortController = ref<AbortController | null>(null)
const shouldStop = ref(false)

// Maintenance rates cache (for manual price calculation)
const maintenanceRatesCache = ref<any[] | null>(null)

// Track manual adjustments (记录手动调整的匹配结果)
const manualAdjustments = ref<any[]>([])

// Stats
const highConfidenceCount = computed(() =>
  tableData.value.filter(item => item.matchRate >= 70).length
)
const lowConfidenceCount = computed(() =>
  tableData.value.filter(item => item.matchRate > 0 && item.matchRate < 70).length
)
const unmatchedCount = computed(() =>
  tableData.value.filter(item => !item.matchedModel || item.matchRate === 0).length
)

function flattenSheetGroups() {
  syncActiveSheetGroup()
  return sheetNames.value.flatMap(sheetName => sheetGroups.value[sheetName] || [])
}

function setSheetGroupsFromRows(rows: any[]) {
  const previousActiveSheet = activeSheetName.value
  const groups: Record<string, any[]> = {}
  rows.forEach((row) => {
    const sheetName = row.sheetName || row._sheetName || '默认工作表'
    if (!groups[sheetName]) groups[sheetName] = []
    groups[sheetName].push({
      ...row,
      _uid: row._uid || genRowUid(),
      sheetName,
      sourceRowIndex: Number.isFinite(Number(row.sourceRowIndex ?? row._sheetRowIndex))
        ? Number(row.sourceRowIndex ?? row._sheetRowIndex)
        : groups[sheetName].length
    })
  })
  sheetGroups.value = groups
  activeSheetName.value = previousActiveSheet && groups[previousActiveSheet]
    ? previousActiveSheet
    : Object.keys(groups)[0] || ''
  tableData.value = activeSheetName.value ? (groups[activeSheetName.value] || []) : []
}

function syncActiveSheetGroup() {
  if (!activeSheetName.value) return
  sheetGroups.value = {
    ...sheetGroups.value,
    [activeSheetName.value]: tableData.value
  }
}

function switchSheet(sheetName: string) {
  if (sheetName === activeSheetName.value) return
  syncActiveSheetGroup()
  activeSheetName.value = sheetName
  tableData.value = sheetGroups.value[sheetName] || []
  selectedRows.value = new Set()
  filterStatus.value = 'all'
}

function createMatchingRow(row: any, index: number, sheetName = row.sheetName || row._sheetName || '') {
  return {
    _uid: genRowUid(),
    manufacturer: row['厂商'] || '',
    model: row['设备/软件型号'] || '',
    originalBrandModel: `${row['厂商'] || ''}-${row['设备/软件型号'] || ''}`,
    originalManufacturer: row['厂商'] || '',
    category: row['设备/软件分类'] || '',
    deviceCategory: '',
    serviceLevel: row['服务级别'] || '7*24*NCR',
    city: row['城市'] || '',
    quantity: parseInt(row['设备数量']) || 1,
    servicePeriod: row['服务周期'] || '1',
    servicePeriodUnit: normalizeServicePeriodUnit(row['服务周期单位']),
    sheetName,
    sourceRowIndex: Number.isFinite(Number(row._sheetRowIndex ?? row.sourceRowIndex))
      ? Number(row._sheetRowIndex ?? row.sourceRowIndex)
      : index,
    matchedModel: '',
    matchRate: 0,
    matchedManufacturer: '',
    matchedSeries: '',
    originalPrice: null as number | null,
    price: null as number | null,
    serviceLevelCoefficient: 1,
    matchedServiceLevel: null,
    confirmed: false,
    primary_category: '',
    secondary_category: '',
    tertiary_category: '',
    device_price: null as number | null,
    rate: 0
  }
}

function setSheetGroupsFromConvertedSheets(sheetTables: Array<{ sheetName: string; data: any[] }>) {
  const groups: Record<string, any[]> = {}
  sheetTables.forEach((sheet) => {
    const sheetName = sheet.sheetName || '默认工作表'
    groups[sheetName] = (sheet.data || []).map((row, index) => createMatchingRow(row, index, sheetName))
  })
  sheetGroups.value = groups
  activeSheetName.value = Object.keys(groups)[0] || ''
  tableData.value = activeSheetName.value ? (groups[activeSheetName.value] || []) : []
}

// 按状态筛选后的数据（去重前）
const statusFilteredData = computed(() => {
  if (filterStatus.value === 'all') return tableData.value
  if (filterStatus.value === 'low') return tableData.value.filter(item => item.matchRate > 0 && item.matchRate < 70)
  if (filterStatus.value === 'unmatched') return tableData.value.filter(item => !item.matchedModel || item.matchRate === 0)
  if (filterStatus.value === 'matched') return tableData.value.filter(item => item.matchRate >= 70)
  // 联想框架专用筛选
  if (filterStatus.value === 'lenovo_endtype_unmatched') return tableData.value.filter(item => !item.lenovo_end_type)
  if (filterStatus.value === 'lenovo_method_manual') return tableData.value.filter(item => item.lenovo_match_method === 'manual')
  if (filterStatus.value === 'lenovo_method_exact') return tableData.value.filter(item => item.lenovo_match_method === 'exact')
  return tableData.value
})

// Filtered table data —— 在状态筛选基础上叠加「去重展示」
const filteredTableData = computed(() => {
  const base = statusFilteredData.value
  if (!dedupeEnabled.value) return base
  // 「原始品牌型号」相同仅保留首条；空值不参与折叠（各自保留，避免误隐藏不同的未匹配行）
  const seen = new Set<string>()
  const result: typeof base = []
  for (const item of base) {
    const key = (item.originalBrandModel || '').trim()
    if (key) {
      if (seen.has(key)) continue
      seen.add(key)
    }
    result.push(item)
  }
  return result
})

// 去重折叠掉的行数（用于按钮上提示）
const dedupeHiddenCount = computed(() => statusFilteredData.value.length - filteredTableData.value.length)

// 虚拟滚动切片
const { visibleItems, topPadding, bottomPadding, startIndex } =
  useVirtualList(filteredTableData, ROW_HEIGHT, tableWrapperRef)

// Selection computed properties —— 基于 _uid，无 indexOf
const isAllSelected = computed(() => {
  const list = filteredTableData.value
  if (list.length === 0) return false
  for (let i = 0; i < list.length; i++) {
    if (!selectedRows.value.has(list[i]._uid)) return false
  }
  return true
})

const isPartialSelected = computed(() => {
  const list = filteredTableData.value
  if (list.length === 0) return false
  let count = 0
  for (let i = 0; i < list.length; i++) {
    if (selectedRows.value.has(list[i]._uid)) count++
  }
  return count > 0 && count < list.length
})

// O(1) 选中判断
function isRowSelected(item: any): boolean {
  return !!item && selectedRows.value.has(item._uid)
}

// Toggle single row selection（按 item 传入）
function toggleRowSelection(item: any) {
  if (!item || !item._uid) return
  const newSet = new Set(selectedRows.value)
  if (newSet.has(item._uid)) {
    newSet.delete(item._uid)
  } else {
    newSet.add(item._uid)
  }
  selectedRows.value = newSet
}

// Toggle all rows selection
function toggleSelectAll() {
  const list = filteredTableData.value
  if (isAllSelected.value) {
    const newSet = new Set(selectedRows.value)
    for (let i = 0; i < list.length; i++) newSet.delete(list[i]._uid)
    selectedRows.value = newSet
  } else {
    const newSet = new Set(selectedRows.value)
    for (let i = 0; i < list.length; i++) newSet.add(list[i]._uid)
    selectedRows.value = newSet
  }
}

// Delete selected rows
function deleteSelectedRows() {
  if (selectedRows.value.size === 0) {
    ElMessage.warning('请先选择要删除的数据')
    return
  }

  ElMessageBox.confirm(
    `确定要删除选中的 ${selectedRows.value.size} 条数据吗？删除后的数据将不进行下一步的流转。`,
    '确认删除',
    {
      confirmButtonText: '确定删除',
      cancelButtonText: '取消',
      type: 'warning',
    }
  ).then(() => {
    const deletedCount = selectedRows.value.size
    // 用 _uid 过滤被删除的行
    const newData = tableData.value.filter(item => !selectedRows.value.has(item._uid))
    tableData.value = newData
    syncActiveSheetGroup()

    // Clear selection
    selectedRows.value = new Set()

    // Update page state
    savePageState(PAGE_STATE_KEYS.SMART_MATCHING, getCurrentState())

    ElMessage.success(`已删除 ${deletedCount} 条数据`)
  }).catch(() => {
    // User cancelled
  })
}

// Clear selection when filter changes
watch(filterStatus, () => {
  selectedRows.value = new Set()
})

/**
 * 切到联想框架口径时自动触发一次联想报价
 *
 * - 表格里没数据 / 正在匹配 → 不触发，避免重复
 * - 所有行已有联想价 → 跳过（用户可点顶部"重新匹配"强制再跑）
 * - 否则立刻调用 /lenovo/bulk-quote
 */
watch(quoteMode, async (mode, prev) => {
  if (mode !== 'lenovo' || prev === mode) return
  if (matchingInProgress.value) return
  const rows = flattenSheetGroups()
  if (rows.length === 0) return
  const allHaveLenovoPrice = rows.every(r => Number(r?.lenovo_unit_price) > 0)
  if (allHaveLenovoPrice) return
  await runLenovoBulkQuote()
})

// 离开联想框架模式时，重置联想专用筛选，避免在标准口径下隐藏全部数据
watch(quoteMode, (mode) => {
  const lenovoOnlyFilters = ['lenovo_endtype_unmatched', 'lenovo_method_manual', 'lenovo_method_exact']
  if (mode !== 'lenovo' && lenovoOnlyFilters.includes(filterStatus.value)) {
    filterStatus.value = 'all'
  }
})

// Navigation
const navigateToHome = () => router.push('/')
const navigateToDocumentRecognition = () => router.push('/document-recognition')
const navigateToSmartMatching = () => {
  // 当前页面，无需跳转
}
const navigateToPriceAdjustment = () => {
  // 面包屑跳转：直接跳转，由目标页面恢复自己的状态
  router.push('/price-adjustment')
}
const navigateToQuotationGeneration = () => router.push('/quotation-generation')

// 流程推进：保存当前状态并进入下一步
const goToPriceAdjustment = async () => {
  // 防止重复点击
  if (isNavigating.value) {
    return
  }

  // 如果本次会话累计了"待确认对应关系"，先弹窗让用户批量处理
  if (quoteMode.value === 'lenovo' && pendingAliases.value.length > 0) {
    const action = await openPendingAliasesDialog()
    if (action === 'cancel') {
      // 用户关闭弹窗（不点跳过也不点记住）→ 停留在当前页继续编辑
      return
    }
  }

  isNavigating.value = true
  const allRows = flattenSheetGroups()
  ElMessage.info(`正在处理 ${allRows.length} 条数据，请稍候...`)

  try {
  // 发送手动调整数据到后端
  console.log('准备发送手动调整数据:', manualAdjustments.value)
  if (manualAdjustments.value.length > 0) {
    try {
      const response = await axios.post(`${API_URL}/manual-matching-override/batch`, manualAdjustments.value)
      console.log(`已成功发送 ${manualAdjustments.value.length} 条手动调整记录到后端`, response.data)
      // 清空已发送的记录
      manualAdjustments.value = []
    } catch (error) {
      console.error('发送手动调整数据失败:', error)
        ElMessage.warning('部分手动调整数据保存失败，但将继续跳转')
    }
  } else {
    console.log('没有手动调整数据需要发送')
  }

    // 先清理旧数据以释放空间
    cleanupOldFlowData('match')

    // 使用 nextTick 确保 DOM 更新后再保存数据，避免阻塞 UI
    await nextTick()

    // 尝试保存当前页面状态（使用 try-catch 包裹，失败不影响流程）
    try {
  savePageState(PAGE_STATE_KEYS.SMART_MATCHING, getCurrentState())
    } catch (error) {
      console.warn('Failed to save page state, continuing with flow data only:', error)
    }

    // 保存流程数据供下一页面使用（这是关键数据，必须成功）
    // 使用异步方式保存，避免阻塞
    await new Promise<void>((resolve) => {
      // 使用 setTimeout 将数据保存操作放到下一个事件循环，避免阻塞 UI
      setTimeout(() => {
        try {
  saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, allRows)
  saveFlowData(FLOW_DATA_KEYS.MATCHED_SHEET_GROUPS, sheetGroups.value)
          console.log(`Flow data saved successfully: ${allRows.length} items`)
          resolve()
        } catch (error) {
          console.error('Failed to save flow data:', error)
          ElMessage.error('数据保存失败，请重试或减少数据量')
          isNavigating.value = false
          throw error
        }
      }, 0)
    })

  // 设置导航模式为 'flow'（流程推进），触发下一页面的重新加载逻辑
  setNavigationMode('flow')
    
    // 使用 nextTick 确保数据保存完成后再跳转
    await nextTick()

    // 清掉本页残留提示，避免与价格调整页弹窗叠加
    ElMessage.closeAll()
    
    // 跳转到价格调整页面
  router.push('/price-adjustment')
  } catch (error) {
    console.error('跳转失败:', error)
    ElMessage.error('跳转失败，请重试')
    isNavigating.value = false
  }
}

// 存为草稿
async function saveAsDraft() {
  if (flattenSheetGroups().length === 0) {
    ElMessage.warning('请先完成数据匹配后再保存草稿')
    return
  }

  isSavingDraft.value = true
  try {
    // 保存当前状态
    savePageState(PAGE_STATE_KEYS.SMART_MATCHING, getCurrentState())
    saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, flattenSheetGroups())
    saveFlowData(FLOW_DATA_KEYS.MATCHED_SHEET_GROUPS, sheetGroups.value)

    // 获取当前草稿ID（如果有）
    const existingDraftId = getCurrentDraftId()

    // 保存草稿
    await saveDraft('smart_matching', existingDraftId ?? undefined)

    ElMessage.success('草稿保存成功')
  } catch (error) {
    console.error('保存草稿失败:', error)
    ElMessage.error('保存草稿失败，请重试')
  } finally {
    isSavingDraft.value = false
  }
}

// 键盘快捷键处理
function handleKeyDown(event: KeyboardEvent) {
  // Ctrl+S 或 Cmd+S 保存草稿
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    saveAsDraft()
  }
}

// Get current state for saving
function getCurrentState(): SmartMatchingState {
  return {
    tableData: flattenSheetGroups(),
    sheetGroups: sheetGroups.value,
    activeSheetName: activeSheetName.value,
    dataSource: dataSource.value,
    filterStatus: filterStatus.value,
    hasData: tableData.value.length > 0
  }
}

// Load data from sessionStorage
onMounted(async () => {
  // Check if we should trigger new matching (from "下一步" button)
  const triggerMatching = getFlowData<boolean>(FLOW_DATA_KEYS.TRIGGER_MATCHING)

  if (triggerMatching === true) {
    // Clear the trigger flag
    clearFlowData(FLOW_DATA_KEYS.TRIGGER_MATCHING)
    // Clear any existing page state to force fresh matching
    clearPageState(PAGE_STATE_KEYS.SMART_MATCHING)
    // Load data and trigger matching
    await loadData(true)
    return
  }

  // First try to restore page state (breadcrumb navigation or page refresh)
  const savedState = restorePageState<SmartMatchingState>(PAGE_STATE_KEYS.SMART_MATCHING)
  if (savedState && savedState.hasData) {
    // Restore page state - do NOT trigger matching
    if (savedState.sheetGroups && Object.keys(savedState.sheetGroups).length > 0) {
      ensureRowUidsInSheetGroups(savedState.sheetGroups)
      sheetGroups.value = savedState.sheetGroups
      activeSheetName.value = savedState.activeSheetName || Object.keys(savedState.sheetGroups)[0]
      tableData.value = sheetGroups.value[activeSheetName.value] || []
    } else {
      setSheetGroupsFromRows(savedState.tableData || [])
    }
    dataSource.value = savedState.dataSource || 'datacenter'
    filterStatus.value = savedState.filterStatus || 'all'
    console.log('Restored saved state:', tableData.value.length, 'items')
    return  // 已有数据，不继续检查
  }

  // Second: check for matched data from flow (from "next step" navigation)
    const matchedData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
    if (matchedData && matchedData.length > 0) {
      // Restore matched data without triggering matching
      setSheetGroupsFromRows(matchedData)
    console.log('Restored matched data:', tableData.value.length, 'items')
    return  // 已有数据，不继续检查
  }

  // Third: only trigger matching if explicitly requested (from "下一步" button)
  // Do NOT auto-trigger matching on breadcrumb navigation or page refresh
  console.log('No saved data found, not triggering automatic matching')

  // 添加键盘快捷键监听
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  // 移除键盘快捷键监听
  window.removeEventListener('keydown', handleKeyDown)
})

// Handle navigation when component is already mounted (breadcrumb navigation)
onBeforeRouteUpdate((to, from, next) => {
  // 当从其他页面（如"价格调整"）返回"智能匹配"时
  // 需要先保存源页面的状态，然后恢复本页面的状态
  if (to.path === '/smart-matching' && from.path !== '/smart-matching') {
    // 从其他页面返回：恢复智能匹配的保存状态
    const savedState = restorePageState<SmartMatchingState>(PAGE_STATE_KEYS.SMART_MATCHING)
    if (savedState && savedState.hasData && savedState.tableData && savedState.tableData.length > 0) {
      // 恢复页面状态 - 不触发匹配
      if (savedState.sheetGroups && Object.keys(savedState.sheetGroups).length > 0) {
        sheetGroups.value = savedState.sheetGroups
        activeSheetName.value = savedState.activeSheetName || Object.keys(savedState.sheetGroups)[0]
        tableData.value = sheetGroups.value[activeSheetName.value] || []
      } else {
        setSheetGroupsFromRows(savedState.tableData)
      }
      dataSource.value = savedState.dataSource || 'datacenter'
      filterStatus.value = savedState.filterStatus || 'all'
      console.log('Breadcrumb navigation: restored SmartMatching state with', tableData.value.length, 'items')
      next()
      return
    }

    // 如果没有保存的页面状态，尝试从流程数据加载
      const matchedData = getFlowData<any[]>(FLOW_DATA_KEYS.MATCHED_DATA)
      if (matchedData && matchedData.length > 0) {
        setSheetGroupsFromRows(matchedData)
      console.log('Breadcrumb navigation: restored flow data with', tableData.value.length, 'items')
      next()
      return
      }

    console.log('Breadcrumb navigation: no saved data found')
  }
  next()
})

// Automatically save state when leaving this page (for breadcrumb navigation restore)
onBeforeRouteLeave((to, from, next) => {
  // 离开页面时始终保存状态，以便面包屑导航可以恢复
  if (tableData.value.length > 0) {
    const currentState = getCurrentState()

    // 尝试保存页面状态（用于面包屑返回时恢复）
    try {
      savePageState(PAGE_STATE_KEYS.SMART_MATCHING, currentState)
      console.log('SmartMatching state saved:', currentState.tableData.length, 'items')
    } catch (error) {
      console.error('Failed to save SmartMatching state:', error)
    }

    // 同时保存流程数据（供下一步使用）
    try {
    const allRows = flattenSheetGroups()
    saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, allRows)
    saveFlowData(FLOW_DATA_KEYS.MATCHED_SHEET_GROUPS, sheetGroups.value)
      console.log('SmartMatching flow data saved:', allRows.length, 'items')
    } catch (error) {
      console.error('Failed to save SmartMatching flow data:', error)
      // 如果保存失败，可能是 sessionStorage 容量不足
      // 清理一些旧数据后重试
      try {
        // 清除 CONVERTED_DATA（已经匹配完成，不再需要原始数据）
        clearFlowData(FLOW_DATA_KEYS.CONVERTED_DATA)
        const allRows = flattenSheetGroups()
        saveFlowData(FLOW_DATA_KEYS.MATCHED_DATA, allRows)
        saveFlowData(FLOW_DATA_KEYS.MATCHED_SHEET_GROUPS, sheetGroups.value)
        console.log('SmartMatching flow data saved after cleanup:', allRows.length, 'items')
      } catch (retryError) {
        console.error('Failed to save flow data even after cleanup:', retryError)
      }
    }
  }
  next()
})

async function loadData(triggerMatching: boolean = false) {
  try {
    const storedSheets = getFlowData<Array<{ sheetName: string; data: any[] }>>(FLOW_DATA_KEYS.CONVERTED_SHEET_TABLES)
    if (storedSheets && storedSheets.length > 0) {
      setSheetGroupsFromConvertedSheets(storedSheets)
      console.log('Loaded converted sheet groups:', storedSheets.map(sheet => `${sheet.sheetName}:${sheet.data?.length || 0}`).join(', '))

      if (triggerMatching) {
        nextTick(() => {
          startMatching()
        })
      }
      return
    }

    const stored = getFlowData<any[]>(FLOW_DATA_KEYS.CONVERTED_DATA)
    if (stored && stored.length > 0) {
      // Initialize table data from converted data
      const rows = stored.map((row, index) => createMatchingRow(row, index))
      setSheetGroupsFromRows(rows)

      // Only auto start matching if explicitly requested (e.g., from "下一步" button)
      if (triggerMatching) {
        nextTick(() => {
          startMatching()
        })
      }
    }
  } catch (error) {
    console.error('Failed to load converted data:', error)
  }
}

// Start matching
async function startMatching() {
  if (matchingInProgress.value || flattenSheetGroups().length === 0) return
  syncActiveSheetGroup()

  // 联想口径：走独立的批量报价分支
  if (quoteMode.value === 'lenovo') {
    await runLenovoBulkQuote()
    return
  }

  matchingInProgress.value = true
  matchingTotal.value = flattenSheetGroups().length
  matchingCompleted.value = 0
  shouldStop.value = false
  abortController.value = new AbortController()

  // Load service levels once at the start (cache for all rows)
  // Use legacy API to get data with service_level field
  if (!serviceLevelsCache.value) {
    try {
      const response = await axios.get(`${API_URL}/service-level/legacy/`)
      serviceLevelsCache.value = response.data || []
    } catch (error) {
      console.error('Failed to load service levels:', error)
      serviceLevelsCache.value = []
    }
  }

  // Load maintenance rates for manual price calculation
  if (!maintenanceRatesCache.value) {
    try {
      const response = await axios.get(`${API_URL}/maintenance_rates/`)
      maintenanceRatesCache.value = response.data || []
    } catch (error) {
      console.error('Failed to load maintenance rates:', error)
      maintenanceRatesCache.value = []
    }
  }

  // 使用分批并发匹配，实时更新进度
  const myGen = await individualMatching()

  // 仅当本轮仍是最新时才收尾，避免在"切换去重→重启匹配"时误关掉新一轮
  if (matchGeneration.value === myGen) {
    matchingInProgress.value = false
    abortController.value = null
  }
}

// 把 /match/ 响应的「型号匹配结果」写入某一行（不含服务级别价格）
function applyMatchResultToRow(row: any, data: any) {
  row.matchedModel = data.matched_model || ''
  row.matchRate = data.match_rate || 0
  // 原始单价 = 设备价格 × 费率（未含税）
  row.originalPrice = (data.device_price || 0) * (data.rate || 0)
  row.deviceCategory = data.device_category || data.category || ''
  row.device_price = data.device_price || null
  row.primary_category = data.primary_category || ''
  row.secondary_category = data.secondary_category || ''
  row.tertiary_category = data.tertiary_category || ''
  row.rate = data.rate || 0
  // 保存匹配到的厂商和系列信息，供价格调整模块使用
  row.matchedManufacturer = data.manufacturer || ''
  row.matchedSeries = data.device_series || ''
  // 用匹配到的厂商更新显示（与手动匹配逻辑一致）；后端无返回则保留原始值
  if (data.manufacturer) row.manufacturer = data.manufacturer
}

function isCancelError(error: any) {
  return error?.name === 'CanceledError' || error?.code === 'ERR_CANCELED' || error?.message?.includes('cancel')
}

// Individual matching - 分批并发匹配，实时更新进度
// 去重开启时：相同「原始品牌型号」只匹配一次，结果回填到该值的所有行，避免重复匹配以提速。
async function individualMatching() {
  const concurrency = 10
  const myGen = ++matchGeneration.value  // 本次运行代号
  const matchItems = flattenSheetGroups()

  // 构造匹配任务单元：去重时按「原始品牌型号」分组（一组一次匹配），否则每行一组
  let units: any[][]
  if (dedupeEnabled.value) {
    const groups = new Map<string, any[]>()
    const order: string[] = []
    for (const it of matchItems) {
      const key = (it.originalBrandModel || '').trim()
      // 空值各自独立匹配，避免误合并不同的未匹配行
      const gk = key ? `k:${key}` : `u:${it._uid}`
      if (!groups.has(gk)) { groups.set(gk, []); order.push(gk) }
      groups.get(gk)!.push(it)
    }
    units = order.map(gk => groups.get(gk)!)
  } else {
    units = matchItems.map(it => [it])
  }

  // 进度按任务单元计（去重时即唯一型号数）
  matchingTotal.value = units.length
  matchingCompleted.value = 0

  let current = 0
  const total = units.length

  // 视图刷新节流：每次 setSheetGroupsFromRows 都会全量重建 sheetGroups（可能 2 万+ 行），
  // 频繁调用会卡死主线程，故限制为最多每 200ms 一次 + 收尾强制刷新一次。
  let lastViewRefresh = 0
  function refreshView(force = false) {
    if (matchGeneration.value !== myGen) return
    const now = Date.now()
    if (!force && now - lastViewRefresh < 200) return
    lastViewRefresh = now
    setSheetGroupsFromRows(matchItems)
    if (activeSheetName.value) tableData.value = sheetGroups.value[activeSheetName.value] || []
    triggerRef(tableData)
  }

  async function worker() {
    // 代号变化（被新一轮匹配取代）时立即退出，避免新旧任务并发写入
    while (current < total && !shouldStop.value && matchGeneration.value === myGen) {
      const rows = units[current++]
      const rep = rows[0]  // 同组代表行，用它发起一次匹配

      try {
        const response = await axios.post(`${API_URL}/match/`, {
          manufacturer: rep.manufacturer,
          model: rep.model,
          category: rep.category,
          source: dataSource.value
        }, {
          signal: abortController.value?.signal
        })

        if (matchGeneration.value !== myGen) return  // 已被新一轮取代，丢弃结果

        if (response.data) {
          // 同组（同一原始品牌型号）匹配结果与原始单价相同；服务价格只与 serviceLevel 有关，
          // 故按"不同 serviceLevel"只算一次，避免对超大组逐行 await 造成 microtask 风暴卡死。
          const priceCache = new Map<string, { adjustedPrice: number; coefficient: number; matchedLevel: any }>()
          let processed = 0
          for (const row of rows) {
            applyMatchResultToRow(row, response.data)
            const sl = row.serviceLevel || ''
            if (row.originalPrice && sl) {
              let pi = priceCache.get(sl)
              if (!pi) {
                pi = await calculateServiceLevelPrice(row.originalPrice, sl)
                if (matchGeneration.value !== myGen) return
                priceCache.set(sl, pi)
              }
              row.price = pi.adjustedPrice
              row.serviceLevelCoefficient = pi.coefficient
              row.matchedServiceLevel = pi.matchedLevel
            }
            // 超大组：每 2000 行让出主线程一次，保持页面响应（避免假死）
            if (++processed % 2000 === 0) {
              await new Promise(r => setTimeout(r, 0))
              if (matchGeneration.value !== myGen) return
            }
          }
        }
      } catch (error: any) {
        if (isCancelError(error)) {
          console.log('Matching was stopped by user')
          return
        }
        console.error('Match failed for item:', rep.model, error)
        // 失败时也要设置默认值
        for (const row of rows) {
          row.matchedModel = ''
          row.matchRate = 0
        }
      } finally {
        // 进度按单元推进；视图刷新走节流，避免频繁全量重建
        if (matchGeneration.value === myGen) {
          matchingCompleted.value++
          refreshView()
        }
      }
    }
  }

  const workers = Array(Math.min(concurrency, total)).fill(0).map(() => worker())
  await Promise.all(workers)
  refreshView(true)  // 收尾强制刷新一次，确保显示最终结果
  return myGen
}

// Stop matching
function stopMatching() {
  if (abortController.value) {
    abortController.value.abort()
    abortController.value = null
  }
  shouldStop.value = true
  matchingInProgress.value = false
  console.log('Matching stopped by user')
}

// ============ 联想框架报价 ============

function buildLenovoQuoteRequest(row: any) {
  // getRowLenovoParams 内部已含 "手动覆盖 > 自动识别 > 全局默认" 三层
  const p = getRowLenovoParams(row)
  const device_category = p.device_category
  const sub_category = p.sub_category

  // 手动锁定型号 > 原始型号全文（供后端语义抽取）> 剥离品牌前缀兜底
  // 后端会用标准口径同款 extract_fields 拆出 core / core_with_series 再匹配，
  // 因此这里尽量传完整原文，而不是只传剥品牌后的短串。
  const lockedModel = row.lenovo_manual_lock_model || ''
  const lockedBrand = row.lenovo_manual_lock_brand || ''
  const rawModel = String(row.model || '').trim()
  const rawBrandModel = String(row.originalBrandModel || '').trim()
  const effectiveModel = lockedModel || rawModel || stripBrandPrefix(rawModel)
  const effectiveBrand = lockedBrand || row.manufacturer || undefined

  return {
    device_category,
    brand: effectiveBrand,
    model: effectiveModel,
    sla: p.sla,
    quantity: Number(row.quantity) || 1,
    drive_config: device_category === '磁带库' ? p.drive_config : undefined,
    sub_category: device_category === '网络设备' ? sub_category : undefined,
    includes_ssd: device_category === '服务器' ? p.includes_ssd : undefined,
    package_type: device_category === '服务器' ? p.package_type : undefined,
    includes_disk:
      device_category === '服务器' || device_category === '小型机' ? p.includes_disk : undefined,
    includes_disk_no_return: device_category === '存储' ? p.includes_disk_no_return : undefined,
    // 用户手动锁定端型 → 跳过后端自动判定
    force_end_type: row.lenovo_manual_end_type || undefined,
    // alias 快查键 + 语义抽取第二路输入：完整「原始品牌型号」
    alias_key: rawBrandModel || undefined,
  }
}

function applyLenovoResultToRow(row: any, result: any) {
  row.lenovo_end_type = result.end_type || ''
  row.lenovo_sub_category = result.sub_category || ''
  // 手动锁定优先级最高：自动报价不覆盖 manual 标记
  if (row.lenovo_match_method !== 'manual') {
    row.lenovo_match_method = result.match_method || 'none'
  }
  row.lenovo_unit_price = result.unit_price ?? null
  row.lenovo_total_price = result.total_price ?? null
  row.lenovo_status = result.status
  row.lenovo_message = result.message || ''
  row.lenovo_classification_id = result.matched_classification_id ?? null
  row.lenovo_pattern_id = result.matched_pattern_id ?? null
  row.lenovo_matched_brand = result.matched_brand ?? null
  row.lenovo_matched_model = result.matched_model ?? null
  row.lenovo_matched_device_category = result.matched_device_category ?? null
}

async function quoteLenovoRows(rows: any[]) {
  if (!rows || rows.length === 0) return

  const payload = { items: rows.map(buildLenovoQuoteRequest) }
  try {
    const resp = await axios.post(`${API_URL}/lenovo/bulk-quote`, payload)
    const results = resp.data?.results || []
    rows.forEach((row, k) => {
      if (results[k]) applyLenovoResultToRow(row, results[k])
    })
    syncActiveSheetGroup()
    triggerRef(tableData)
  } catch (e: any) {
    console.error('Lenovo quote failed:', e)
    ElMessage.error(`联想报价失败：${e?.response?.data?.detail || e?.message || '未知错误'}`)
  }
}

async function runLenovoBulkQuote() {
  const allRows = flattenSheetGroups()
  if (allRows.length === 0) return

  const myGen = ++matchGeneration.value  // 本次运行代号
  matchingInProgress.value = true
  matchingCompleted.value = 0
  shouldStop.value = false

  // 构造任务单元：去重点亮时按「原始品牌型号」分组，每组只取代表行报价；
  // 否则每行一个单元（行为同原逻辑）。
  let units: any[][]
  if (dedupeEnabled.value) {
    const groups = new Map<string, any[]>()
    const order: string[] = []
    for (const r of allRows) {
      const key = (r.originalBrandModel || '').trim()
      // 空值各自独立，避免误并不同的未匹配行
      const gk = key ? `k:${key}` : `u:${r._uid}`
      if (!groups.has(gk)) { groups.set(gk, []); order.push(gk) }
      groups.get(gk)!.push(r)
    }
    units = order.map(gk => groups.get(gk)!)
  } else {
    units = allRows.map(r => [r])
  }

  matchingTotal.value = units.length

  // 切批：每批 200 个单元避免单请求过大
  const batchSize = 200
  try {
    for (let i = 0; i < units.length; i += batchSize) {
      if (shouldStop.value || matchGeneration.value !== myGen) break
      const batchUnits = units.slice(i, i + batchSize)
      // 每组用代表行发起报价
      const payload = { items: batchUnits.map(u => buildLenovoQuoteRequest(u[0])) }
      const resp = await axios.post(`${API_URL}/lenovo/bulk-quote`, payload)
      if (matchGeneration.value !== myGen) break  // 已被新一轮取代，丢弃结果
      const results = resp.data?.results || []
      batchUnits.forEach((u, k) => {
        const result = results[k]
        if (!result) return
        // 匹配型号/端型/单价等结果回填到同「原始品牌型号」全组
        for (const row of u) {
          applyLenovoResultToRow(row, result)
          // 总价按各行自身数量单独重算（同型号单价相同，数量可不同）
          if (u.length > 1 && result.unit_price != null) {
            row.lenovo_total_price = result.unit_price * (Number(row.quantity) || 1)
          }
        }
      })
      matchingCompleted.value += batchUnits.length
      // 关键：循环内不再触发整表重渲染（避免每批锁死主线程）。
    }
    // 全部完成后一次性同步 sheetGroups + 当前 tab 视图
    // 已被新一轮取代则不收尾（让最新一轮接管视图与状态）
    if (matchGeneration.value !== myGen) return
    setSheetGroupsFromRows(allRows)
    if (activeSheetName.value) tableData.value = sheetGroups.value[activeSheetName.value] || []
    triggerRef(tableData)
    ElMessage.success(
      dedupeEnabled.value
        ? `联想框架报价完成：${units.length} 个去重型号，已应用到 ${allRows.length} 条`
        : `联想框架报价完成，共 ${allRows.length} 条`
    )
  } catch (e: any) {
    console.error('Lenovo bulk-quote failed:', e)
    ElMessage.error(`联想报价失败：${e?.response?.data?.detail || e?.message || '未知错误'}`)
  } finally {
    // 仅当本轮仍是最新时才复位进行中标记，避免误关新一轮
    if (matchGeneration.value === myGen) matchingInProgress.value = false
  }
}

// Pricing params dropdown functions
function togglePricingParamsDropdown() {
  showPricingParamsDropdown.value = !showPricingParamsDropdown.value
}

function closePricingParamsDropdown() {
  showPricingParamsDropdown.value = false
}

function resetPricingParams() {
  pricingParams.value = {
    serviceMode: true,
    slaFactor: true,
    hardwareDepreciation: false,
    regionalAdjustment: false
  }
  console.log('Pricing params reset to default')
}

function applyPricingParams() {
  console.log('Applying pricing params:', pricingParams.value)
  // TODO: 实现应用逻辑
  closePricingParamsDropdown()
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

// Calculate service level price (uses cached service levels)
// 匹配规则：使用 serviceLevel 值（如 "7*24*2"）与后台"服务级别"管理中的 "响应时效" 字段进行模糊匹配
// 例如 "7*24*2" 应匹配到 "响应时效" 为 "7*24*2（2小时工程师和备件到达）" 的记录
// 如果匹配不到，使用 "7*24*NCR" 作为默认值
async function calculateServiceLevelPrice(basePrice: number, serviceLevel: string) {
  try {
    const levels = serviceLevelsCache.value || []
    const inputLevel = (serviceLevel || '7*24*NCR').trim()

    // 通过 response_time 字段进行模糊匹配
    // 查找 response_time 包含 inputLevel 的记录
    let matchedLevel = levels.find((l: any) => {
      const responseTime = (l.response_time || '').trim()
      return responseTime.includes(inputLevel)
    })

    // 如果没有匹配到，尝试使用默认值 "7*24*NCR"
    if (!matchedLevel && inputLevel !== '7*24*NCR') {
      matchedLevel = levels.find((l: any) => {
        const responseTime = (l.response_time || '').trim()
        return responseTime.includes('7*24*NCR')
      })
    }

    // 如果还是匹配不到，使用默认系数 1.0
    const coefficient = matchedLevel ? (Number(matchedLevel.coefficient) || 1) : 1.0
    const adjustedPrice = basePrice * coefficient

    return {
      adjustedPrice,
      coefficient,
      matchedLevel: matchedLevel || null
    }
  } catch (error) {
    console.error('Failed to calculate service level price:', error)
    return {
      adjustedPrice: basePrice,
      coefficient: 1.0,
      matchedLevel: null
    }
  }
}

// Parse service level (e.g., "7*24*3" -> { hours: 24, type: 'NCR' })
function parseServiceLevel(level: string) {
  const parts = level.split('*')
  if (parts.length >= 3) {
    return {
      hours: parseInt(parts[1]) || 24,
      type: parts[2]
    }
  }
  return { hours: 24, type: 'NCR' }
}

// 模糊匹配服务周期单位
function normalizeServicePeriodUnit(value: string): string {
  if (!value) return '年'
  const normalized = value.toString().trim()
  if (normalized.includes('年')) return '年'
  if (normalized.includes('月')) return '月'
  if (normalized.includes('天')) return '天'
  // 默认为年
  return '年'
}

// Open search dialog
function openSearch(item: any) {
  if (!item) return
  activeModelRow.value = item
  showSearchDialog.value = true
  searchPage.value = 1
  // 重置搜索数据源为当前行的数据源
  searchDataSource.value = item.dataSource || 'datacenter'
  // Use original model for search (not the matched one)
  searchQuery.value = item.model || ''
  handleSearchInput()

  nextTick(() => {
    searchInputRef.value?.focus()
  })
}

// Close search dialog
function closeSearchDialog() {
  showSearchDialog.value = false
  activeModelRow.value = null
  searchQuery.value = ''
  searchResults.value = []
}

// Clear match result - 清空匹配结果，恢复到"未匹配"状态
function clearMatchResult(item: any) {
  if (item) {
    // 重置匹配相关字段
    item.matchedModel = ''
    item.matchRate = 0
    item.matchedManufacturer = ''
    item.matchedSeries = ''
    item.originalPrice = 0
    item.price = 0
    item.serviceLevelCoefficient = 1
    item.deviceCategory = ''
    // 使用 shallowRef 时需要手动触发更新
    triggerRef(tableData)
  }
}

// ============ 联想框架：匹配型号 手动搜索 ============

function openLenovoSearch(item: any) {
  if (!item) return
  lenovoSearchTargetRow.value = item
  // 初始关键词：用原始 model 或当前已匹配的 lenovo_matched_model
  lenovoSearchQuery.value = item.lenovo_matched_model || stripBrandPrefix(item.model || '') || (item.model || '')
  showLenovoSearchDialog.value = true
  performLenovoSearch()
  nextTick(() => lenovoSearchInputRef.value?.focus())
}

function closeLenovoSearchDialog() {
  showLenovoSearchDialog.value = false
  lenovoSearchTargetRow.value = null
  lenovoSearchQuery.value = ''
  lenovoSearchResults.value = []
}

function handleLenovoSearchInput() {
  if (lenovoSearchTimeout) clearTimeout(lenovoSearchTimeout)
  lenovoSearchTimeout = setTimeout(() => performLenovoSearch(), 250)
}

async function performLenovoSearch() {
  const kw = (lenovoSearchQuery.value || '').trim()
  if (!kw) {
    lenovoSearchResults.value = []
    return
  }
  lenovoSearchLoading.value = true
  try {
    // 设备大类：行内手动覆盖 > 行内自动识别 > 全局默认；为空时不限制
    const row = lenovoSearchTargetRow.value
    const cat = row ? getRowLenovoParams(row).device_category : ''
    const resp = await axios.get(`${API_URL}/lenovo/search-classification`, {
      params: { keyword: kw, device_category: cat || undefined, limit: 50 },
    })
    lenovoSearchResults.value = resp.data || []
  } catch (e: any) {
    console.error('Lenovo classification search failed:', e)
    lenovoSearchResults.value = []
  } finally {
    lenovoSearchLoading.value = false
  }
}

async function selectLenovoSearchResult(result: any) {
  const targetRow = lenovoSearchTargetRow.value
  if (!targetRow || !result) return

  // 改「匹配型号」按"原始品牌型号"同步：同一上传输入的行应用同一标准机型
  // （注意与端型不同：端型由"匹配型号"决定，故 selectEndType 按匹配型号同步）
  const targetOriginalBrandModel = targetRow.originalBrandModel || ''
  const allRows = flattenSheetGroups()
  const sameRows = targetOriginalBrandModel
    ? allRows.filter(r => (r.originalBrandModel || '') === targetOriginalBrandModel)
    : [targetRow]

  // 把命中机型作为"手动锁定"，后端按这个 brand+model 重新查价（命中 exact）
  // 并把端型 / 子类 等结果一并应用到所有同名"原始品牌型号"的行
  for (const r of sameRows) {
    r.lenovo_manual_lock_brand = result.brand || ''
    r.lenovo_manual_lock_model = result.model || ''
    r.lenovo_matched_brand = result.brand || ''
    r.lenovo_matched_model = result.model || ''
    r.lenovo_end_type = result.end_type || ''
    r.lenovo_sub_category = result.sub_category || ''
    r.lenovo_match_method = 'manual'
    r.lenovo_classification_id = result.id
    // 同步联想设备大类为命中机型的大类（如"存储"），否则会沿用原始自动识别（如"服务器"），
    // 导致分类显示不对、端型下拉仍按服务器端型加载。lenovo_device_category 会被
    // getRowLenovoParams 作为最高优先级，驱动端型选项与查价。
    if (result.device_category) {
      r.lenovo_device_category = result.device_category
      r.lenovo_matched_device_category = result.device_category
    }
  }

  closeLenovoSearchDialog()

  // 立即按手动锁定值批量重新查价
  try {
    await quoteLenovoRows(sameRows)
  } finally {
    setSheetGroupsFromRows(allRows)
    if (activeSheetName.value) tableData.value = sheetGroups.value[activeSheetName.value] || []
    triggerRef(tableData)
    const endTypeNote = result.end_type ? `，端型「${result.end_type}」` : ''
    ElMessage.success(
      `已为 ${sameRows.length} 个同型号条目应用匹配型号「${result.model}」${endTypeNote}`
    )
  }

  // 如果机型库 result 已有 end_type，入队待批量确认（不再立即弹窗）
  if (result.end_type) {
    queueAliasFromManualMatch(targetRow, result, sameRows.length)
  }
}

/**
 * 用户在「匹配型号」搜索弹窗里手动选了机型库中已有 end_type 的记录
 * → 把「原始品牌型号 → 标准记录」入队等待批量确认
 */
function queueAliasFromManualMatch(row: any, result: any, affectedCount: number) {
  const rawBrandModel = row?.originalBrandModel || ''
  if (!rawBrandModel || !result?.model || !result?.end_type) return
  queuePendingAlias({
    id: `${rawBrandModel}|${(result.device_category || '').toLowerCase()}|${(result.model || '').toLowerCase()}`,
    rawBrandModel,
    device_category: result.device_category,
    brand: result.brand || '',
    model: result.model,
    end_type: result.end_type,
    sub_category: result.sub_category || null,
    source: 'manual-match',
    affected_rows: affectedCount,
  })
}

// ============ 批量确认弹窗：打开、关闭、确认、跳过 ============

function openPendingAliasesDialog(): Promise<'navigate' | 'cancel'> {
  // 默认全选所有待确认项
  selectedAliasIds.value = new Set(pendingAliases.value.map(a => a.id))
  showPendingAliasesDialog.value = true
  return new Promise(resolve => {
    _pendingAliasesResolver = resolve
  })
}

function closePendingAliasesDialog() {
  showPendingAliasesDialog.value = false
  if (_pendingAliasesResolver) {
    _pendingAliasesResolver('cancel')
    _pendingAliasesResolver = null
  }
}

const isAllAliasesSelected = computed(() => {
  return pendingAliases.value.length > 0
    && selectedAliasIds.value.size === pendingAliases.value.length
})
const isPartialAliasesSelected = computed(() => {
  const n = selectedAliasIds.value.size
  return n > 0 && n < pendingAliases.value.length
})

function toggleAllAliasesSelected() {
  if (isAllAliasesSelected.value) {
    selectedAliasIds.value = new Set()
  } else {
    selectedAliasIds.value = new Set(pendingAliases.value.map(a => a.id))
  }
}

function toggleAliasSelected(id: string) {
  const next = new Set(selectedAliasIds.value)
  if (next.has(id)) next.delete(id)
  else next.add(id)
  selectedAliasIds.value = next
}

// 从队列中移除选中（"批量删除选中"按钮）
function removePendingAliases() {
  if (selectedAliasIds.value.size === 0) return
  pendingAliases.value = pendingAliases.value.filter(a => !selectedAliasIds.value.has(a.id))
  selectedAliasIds.value = new Set()
}

// 全部跳过：不写库，但允许导航
function skipAllPendingAliases() {
  pendingAliases.value = []
  selectedAliasIds.value = new Set()
  showPendingAliasesDialog.value = false
  if (_pendingAliasesResolver) {
    _pendingAliasesResolver('navigate')
    _pendingAliasesResolver = null
  }
}

// 记住选中：批量调 upsert，完成后清空队列并允许导航
async function confirmSelectedAliases() {
  if (selectedAliasIds.value.size === 0) return
  pendingAliasesProcessing.value = true
  const toWrite = pendingAliases.value.filter(a => selectedAliasIds.value.has(a.id))
  let success = 0
  let failed = 0
  try {
    // 串行 upsert（保持简单 + 显式错误处理）
    for (const item of toWrite) {
      try {
        await axios.post(`${API_URL}/lenovo/framework-models/upsert`, {
          device_category: item.device_category,
          brand: item.brand,
          model: item.model,
          end_type: item.end_type,
          sub_category: item.sub_category || null,
          alias_raw: item.rawBrandModel,
          notes: item.source === 'end-type'
            ? '由用户在「智能匹配」端型列手动确认后批量回写'
            : '由用户在「匹配型号」搜索弹窗手动确认后批量回写',
        })
        success++
      } catch (e) {
        console.error('Upsert failed for', item, e)
        failed++
      }
    }
    if (failed > 0) {
      ElMessage.warning(`已记住 ${success} 条，${failed} 条失败（详见控制台）`)
    } else {
      ElMessage.success(`已记住 ${success} 条对应关系到机型库`)
    }
  } finally {
    pendingAliasesProcessing.value = false
    pendingAliases.value = []
    selectedAliasIds.value = new Set()
    showPendingAliasesDialog.value = false
    if (_pendingAliasesResolver) {
      _pendingAliasesResolver('navigate')
      _pendingAliasesResolver = null
    }
  }
}

function clearLenovoManualLock(item: any) {
  if (!item) return
  item.lenovo_manual_lock_brand = ''
  item.lenovo_manual_lock_model = ''
  item.lenovo_match_method = 'none'  // 让 quoteLenovoRows 后续覆盖
  // 立即用原始 model 重新跑自动报价
  quoteLenovoRows([item]).then(() => triggerRef(tableData))
}

// ============ 联想框架：端型 下拉选择 ============

async function ensureEndTypeOptions(category: string) {
  if (!category) {
    endTypeOptions.value = []
    return
  }
  if (endTypeOptionsCache.value[category]) {
    endTypeOptions.value = endTypeOptionsCache.value[category]
    return
  }
  endTypeLoading.value = true
  try {
    const resp = await axios.get(`${API_URL}/lenovo/end-types`, {
      params: { device_category: category },
    })
    const list = (resp.data as string[]) || []
    endTypeOptionsCache.value[category] = list
    endTypeOptions.value = list
  } catch (e) {
    console.error('Load lenovo end types failed:', e)
    endTypeOptions.value = []
  } finally {
    endTypeLoading.value = false
  }
}

async function openEndTypeDropdown(item: any, event: MouseEvent) {
  event.stopPropagation()
  if (!item) return
  const target = event.currentTarget as HTMLElement
  const rect = target.getBoundingClientRect()
  endTypeDropdownPosition.value = {
    top: rect.bottom + 4 + 'px',
    left: rect.left + 'px',
  }
  endTypeDropdownTarget.value = item
  endTypeDropdownVisible.value = true
  const cat = getRowLenovoParams(item).device_category
  await ensureEndTypeOptions(cat)
}

function closeEndTypeDropdown() {
  endTypeDropdownVisible.value = false
  endTypeDropdownTarget.value = null
}

async function selectEndType(endType: string) {
  const targetRow = endTypeDropdownTarget.value
  if (!targetRow || !endType) return closeEndTypeDropdown()

  // 端型由「匹配型号」决定：同一「匹配型号」的所有行同步应用最新端型
  // （二次调整时同样会再次覆盖同型号全部行，保持一致）
  const targetMatchedModel = (targetRow.lenovo_matched_model || '').trim()

  const allRows = flattenSheetGroups()
  const sameRows = targetMatchedModel
    ? allRows.filter(r => (r.lenovo_matched_model || '').trim() === targetMatchedModel)
    : [targetRow]

  // 应用端型锁定
  for (const r of sameRows) {
    r.lenovo_manual_end_type = endType
    r.lenovo_end_type = endType
    r.lenovo_match_method = 'manual'
  }

  // 保留 dialog 关闭前的快照
  const snapshotRow = targetRow
  closeEndTypeDropdown()

  // 重新批量报价（buildLenovoQuoteRequest 会传 force_end_type）
  try {
    await quoteLenovoRows(sameRows)
  } finally {
    setSheetGroupsFromRows(allRows)
    if (activeSheetName.value) tableData.value = sheetGroups.value[activeSheetName.value] || []
    triggerRef(tableData)
    ElMessage.success(`已为 ${sameRows.length} 个同型号条目设置端型：${endType}`)
  }

  // 把对应关系入队，等用户点"下一步：价格调整"时统一弹窗批量确认
  queueAliasFromEndTypeChange(snapshotRow, endType, sameRows.length)
}

/**
 * 用户在「端型」下拉里手动选了端型 → 把「原始品牌型号 → 标准记录」入队
 * （不立即弹窗，统一在 goToPriceAdjustment 前批量确认）
 */
function queueAliasFromEndTypeChange(row: any, endType: string, affectedCount: number) {
  if (!row) return
  const p = getRowLenovoParams(row)
  const device_category = p.device_category
  const brand = row.lenovo_matched_brand || row.manufacturer || ''
  const model = row.lenovo_matched_model || stripBrandPrefix(row.model || '') || row.model || ''
  const rawBrandModel = row.originalBrandModel || ''
  if (!rawBrandModel || !model || !endType) return
  queuePendingAlias({
    id: `${rawBrandModel}|${device_category.toLowerCase()}|${model.toLowerCase()}`,
    rawBrandModel,
    device_category,
    brand,
    model,
    end_type: endType,
    sub_category: p.sub_category || null,
    source: 'end-type',
    affected_rows: affectedCount,
  })
}

function clearLenovoManualEndType(item: any) {
  if (!item) return
  // 与 selectEndType 一致：按「匹配型号」同步清除同型号全部行的手动端型
  const targetMatchedModel = (item.lenovo_matched_model || '').trim()
  const allRows = flattenSheetGroups()
  const sameRows = targetMatchedModel
    ? allRows.filter(r => (r.lenovo_matched_model || '').trim() === targetMatchedModel)
    : [item]
  for (const r of sameRows) {
    r.lenovo_manual_end_type = ''
    r.lenovo_match_method = 'none'
  }
  quoteLenovoRows(sameRows).then(() => {
    setSheetGroupsFromRows(allRows)
    if (activeSheetName.value) tableData.value = sheetGroups.value[activeSheetName.value] || []
    triggerRef(tableData)
  })
}

// Handle search input
function handleSearchInput() {
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }

  searchTimeout = setTimeout(() => {
    performSearch()
  }, 300)
}

// Perform search
async function performSearch() {
  if (!searchQuery.value || searchQuery.value.length < 1) {
    searchResults.value = []
    totalResults.value = 0
    return
  }

  // Load maintenance rates if not already loaded (needed for price calculation)
  if (!maintenanceRatesCache.value) {
    try {
      const response = await axios.get(`${API_URL}/maintenance_rates/`)
      maintenanceRatesCache.value = response.data || []
    } catch (error) {
      console.error('Failed to load maintenance rates:', error)
      maintenanceRatesCache.value = []
    }
  }

  searchLoading.value = true

  try {
    const params = new URLSearchParams()
    params.append('model', searchQuery.value)
    // 使用搜索对话框中的数据源，而不是全局数据源
    params.append('source', searchDataSource.value)
    params.append('limit', pageSize.toString())
    params.append('offset', ((searchPage.value - 1) * pageSize).toString())

    const response = await axios.get(`${API_URL}/devices/search/?${params}`)
    searchResults.value = response.data.data || response.data || []
    totalResults.value = response.data.total || searchResults.value.length
  } catch (error) {
    console.error('Search failed:', error)
    searchResults.value = []
    totalResults.value = 0
  } finally {
    searchLoading.value = false
  }
}

// Change search page
function changeSearchPage(page: number) {
  searchPage.value = page
  performSearch()
}

// 数据源改变时重新搜索
function onSearchDataSourceChange() {
  // 重置页码并重新搜索
  searchPage.value = 1
  if (searchQuery.value && searchQuery.value.length >= 1) {
    performSearch()
  }
}

// Select search result
async function selectSearchResult(result: any) {
  const activeRow = activeModelRow.value
  if (!activeRow) return

  const selectedModel = result.model_number || result.model
  const devicePrice = result.device_price || 0

  // Find maintenance rate by categories (for manual price calculation)
  const rate = findMaintenanceRate(
    result.primary_category || '',
    result.secondary_category || '',
    result.tertiary_category || ''
  )

  // 原始单价 = 设备价格 × 费率（未含税）
  const originalPrice = devicePrice * rate
  const originalModel = activeRow.model  // 原始型号（来自Excel"设备/软件型号"列）
  const originalManufacturer = activeRow.originalManufacturer || ''  // 原始厂商（来自Excel"厂商"列，永不修改）

  console.log('手动匹配 - 原始值:', { originalManufacturer, originalModel })
  console.log('手动匹配 - 匹配值:', { manufacturer: result.manufacturer, model: result.model_number || result.model })

  // Find all rows with the same original model
  const matchedIndexes: number[] = []
  tableData.value.forEach((item, idx) => {
    if (item.model === originalModel) {
      matchedIndexes.push(idx)
    }
  })

  // Update all matched rows
  for (const idx of matchedIndexes) {
    // Calculate similarity for each row
    const similarity = calculateSimilarity(tableData.value[idx].model, selectedModel)

    tableData.value[idx].matchedModel = selectedModel
    tableData.value[idx].matchRate = similarity
    tableData.value[idx].originalPrice = originalPrice
    tableData.value[idx].deviceCategory = result.tertiary_category || result.device_category || ''
    tableData.value[idx].manufacturer = result.manufacturer || tableData.value[idx].manufacturer
    tableData.value[idx].device_price = devicePrice
    tableData.value[idx].primary_category = result.primary_category || ''
    tableData.value[idx].secondary_category = result.secondary_category || ''
    tableData.value[idx].tertiary_category = result.tertiary_category || ''
    tableData.value[idx].rate = rate
    tableData.value[idx].matchedManufacturer = result.manufacturer || ''
    tableData.value[idx].matchedSeries = result.device_series || ''
    tableData.value[idx].manuallyAdjusted = true  // 标记为手动调整

    // Recalculate service level price for each row
    if (originalPrice && tableData.value[idx].serviceLevel) {
      const priceInfo = await calculateServiceLevelPrice(originalPrice, tableData.value[idx].serviceLevel)
      tableData.value[idx].price = priceInfo.adjustedPrice
      tableData.value[idx].serviceLevelCoefficient = priceInfo.coefficient
      tableData.value[idx].matchedServiceLevel = priceInfo.matchedLevel
    }

    // 记录手动调整数据（传入原始厂商和型号，来自Excel）
    // 使用循环外捕获的原始值，确保所有行使用相同的原始厂商和型号
    saveManualAdjustment(
      originalManufacturer,  // 原始厂商（来自Excel"厂商"列）
      originalModel,  // 原始型号（来自Excel"设备/软件型号"列）
      result
    )
  }

  // 使用 shallowRef 时需要手动触发更新
  syncActiveSheetGroup()
  triggerRef(tableData)
  closeSearchDialog()
}

// Save manual adjustment record
function saveManualAdjustment(
  originalManufacturer: string,  // 原始厂商（来自Excel"厂商"列）
  originalModel: string,  // 原始型号（来自Excel"设备/软件型号"列）
  searchResult: any  // 手动选择的匹配结果
) {
  // 检查是否已存在相同的原始厂商+型号组合
  const existingIndex = manualAdjustments.value.findIndex(
    item =>
      item.original_manufacturer === originalManufacturer &&
      item.original_model === originalModel
  )

  const adjustment = {
    original_manufacturer: originalManufacturer,  // 来自Excel"厂商"列
    original_model: originalModel,  // 来自Excel"设备/软件型号"列
    matched_manufacturer: searchResult.manufacturer || originalManufacturer,
    matched_model_number: searchResult.model_number || searchResult.model,
    device_price: searchResult.device_price || null,
    primary_category: searchResult.primary_category || '',
    secondary_category: searchResult.secondary_category || '',
    tertiary_category: searchResult.tertiary_category || '',
    device_category: searchResult.tertiary_category || searchResult.device_category || '',
    data_source: dataSource.value
  }

  if (existingIndex >= 0) {
    // 更新现有记录
    manualAdjustments.value[existingIndex] = adjustment
    console.log('更新手动调整记录:', adjustment)
  } else {
    // 添加新记录
    manualAdjustments.value.push(adjustment)
    console.log('添加手动调整记录:', adjustment)
    console.log('当前手动调整记录总数:', manualAdjustments.value.length)
  }
}

// Calculate similarity between two strings
function calculateSimilarity(str1: string, str2: string): number {
  if (!str1 || !str2) return 0
  const s1 = str1.toLowerCase().replace(/[^a-z0-9]/g, '')
  const s2 = str2.toLowerCase().replace(/[^a-z0-9]/g, '')
  if (s1 === s2) return 100

  const longer = s1.length > s2.length ? s1 : s2
  const shorter = s1.length > s2.length ? s2 : s1

  if (longer.length === 0) return 100

  const costs = []
  for (let i = 0; i <= longer.length; i++) {
    let lastValue = i
    for (let j = 0; j <= shorter.length; j++) {
      if (i === 0) {
        costs[j] = j
      } else if (j > 0) {
        let newValue = costs[j - 1]
        if (longer.charAt(i - 1) !== shorter.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1
        }
        costs[j - 1] = lastValue
        lastValue = newValue
      }
    }
    if (i > 0) costs[shorter.length] = lastValue
  }

  const editDistance = costs[shorter.length]
  return Math.max(0, Math.round((1 - editDistance / longer.length) * 100))
}

// Export data
async function exportData() {
  const isLenovo = quoteMode.value === 'lenovo'
  const exportDataItems = tableData.value.map(item => {
    if (isLenovo) {
      const params = getRowLenovoParams(item)
      return {
        '厂商': item.manufacturer,
        '设备/软件型号': item.model,
        '设备大类': params.device_category,
        '子类': item.lenovo_sub_category || params.sub_category || '-',
        'SLA': params.sla,
        '驱动器配置': params.device_category === '磁带库' ? params.drive_config : '-',
        '含SSD': params.device_category === '服务器' ? (params.includes_ssd ? '是' : '否') : '-',
        '报价类型': params.device_category === '服务器' ? params.package_type : '-',
        '含硬盘不返还': params.device_category === '服务器' || params.device_category === '小型机'
          ? (params.includes_disk ? '是' : '否') : '-',
        '含硬盘不回收': params.device_category === '存储' ? (params.includes_disk_no_return ? '是' : '否') : '-',
        '端型': item.lenovo_end_type || '-',
        '命中方式': formatLenovoMethod(item.lenovo_match_method),
        '数量': Number(item.quantity) || 1,
        '单价': item.lenovo_unit_price ? `¥${Number(item.lenovo_unit_price).toFixed(2)}` : '-',
        '总价': item.lenovo_total_price ? `¥${Number(item.lenovo_total_price).toFixed(2)}` : '-',
        '状态': item.lenovo_status || '-',
        '说明': item.lenovo_message || '',
      }
    }
    return {
      '厂商': item.manufacturer,
      '设备/软件型号': item.model,
      '设备/软件分类': item.deviceCategory,
      '服务级别': item.serviceLevel,
      '匹配型号': item.matchedModel || '未匹配',
      '置信度': item.matchRate ? `${Math.round(item.matchRate)}%` : '0%',
      '原始单价': item.originalPrice ? `¥${item.originalPrice.toFixed(2)}` : '-',
      '服务系数': item.serviceLevelCoefficient !== 1 ? item.serviceLevelCoefficient.toFixed(2) : '-',
      '调整后单价': item.price ? `¥${item.price.toFixed(2)}` : '-'
    }
  })

  // Use XLSX to export - 处理不同的模块导出格式
  const xlsxModule = await import('xlsx')
  const XLSX = xlsxModule.default || xlsxModule
  const ws = XLSX.utils.json_to_sheet(exportDataItems)
  const wb = XLSX.utils.book_new()
  const sheetName = isLenovo ? '联想框架报价结果' : '匹配结果'
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  const fileName = isLenovo ? '联想框架报价结果.xlsx' : '智能匹配结果.xlsx'
  XLSX.writeFile(wb, fileName)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.smart-matching {
  font-family: "Noto Sans SC", sans-serif;
  background-color: #101622;
  color: white;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  position: relative;
}

/* Header Styles */
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid #232f48;
  background-color: #101622;
  padding: 1rem 1.5rem;
  position: sticky;
  top: 0;
  z-index: 50;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.logo-link {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  text-decoration: none;
  transition: opacity 0.2s;
}

.logo-link:hover {
  opacity: 0.8;
}

.logo-wrapper {
  width: 2rem;
  height: 2rem;
  color: #135bec;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(19, 91, 236, 0.1);
  border-radius: 0.5rem;
}

.header-title {
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.015em;
}

.nav-links {
  display: none;
  flex: 1;
  justify-content: center;
  gap: 2.5rem;
}

@media (min-width: 768px) {
.nav-links {
  display: flex;
  }
}

.nav-link {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  text-decoration: none;
  transition: color 0.2s;
}

.nav-link:hover, .nav-link.active {
  color: #135bec;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.icon-btn {
  position: relative;
  color: #94a3b8;
  background: transparent;
  border: none;
  cursor: pointer;
  transition: color 0.2s;
}

.icon-btn:hover {
  color: #135bec;
}

.notification-dot {
  position: absolute;
  top: 0;
  right: 0;
  width: 0.5rem;
  height: 0.5rem;
  background-color: #ef4444;
  border-radius: 9999px;
}

.divider {
  height: 2rem;
  width: 1px;
  background-color: #232f48;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  background-image: url("/images/homepage/page-bg.jpg");
  background-size: cover;
  background-position: center;
  ring: 2px solid #232f48;
}

.user-details {
  display: none;
  flex-direction: column;
}

@media (min-width: 1024px) {
  .user-details {
    display: flex;
  }
}

.user-name {
  font-size: 0.875rem;
  font-weight: 500;
  line-height: 1;
}

.user-role {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

/* Main Container */
.main-container {
  flex: 1;
  width: 100%;
  max-width: 1600px;
  margin: 0 auto;
  padding: 1rem 2.5rem;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 1rem;
}

@media (min-width: 768px) {
  .page-header {
    flex-direction: row;
    justify-content: space-between;
    align-items: center;
  }
}

.header-content {
  display: flex;
  flex-direction: column;
}

.header-right {
  display: flex;
  align-items: center;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #92a4c9;
}

.breadcrumb-link {
  color: inherit;
  text-decoration: none;
  transition: color 0.2s;
  cursor: pointer;
}

.breadcrumb-link:hover {
  color: #135bec;
  text-decoration: underline;
}

.breadcrumb-current {
  color: white;
  font-weight: 500;
}

.breadcrumb .material-symbols-outlined {
  font-size: 1rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  letter-spacing: -0.025em;
  margin-top: 0.25rem;
}

.page-description {
  color: #92a4c9;
  font-size: 1rem;
  margin-top: 0.25rem;
}

/* Steps Progress */
.steps-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background-color: #1a2332;
  padding: 0.5rem;
  border-radius: 0.5rem;
  border: 1px solid #232f48;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.step {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  opacity: 0.5;
  transition: opacity 0.2s;
}

.step:hover {
  opacity: 0.8;
}

.step.active {
  color: #135bec;
  opacity: 1;
}

.step.completed {
  opacity: 0.5;
}

.step-number {
  width: 1.5rem;
  height: 1.5rem;
  border-radius: 9999px;
  background-color: #475569;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.75rem;
  font-weight: 700;
  flex-shrink: 0;
  color: white;
}

.step.active .step-number {
  background-color: #135bec;
  color: white;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.25);
}

.step.completed .step-number {
  background-color: #22c55e;
  color: white;
}

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
  cursor: pointer;
}

.step.active .step-label {
  font-weight: 700;
}

.step-label:hover {
  text-decoration: underline;
}

.step-divider {
  height: 1px;
  width: 1rem;
  background-color: #475569;
  flex-shrink: 0;
}

/* Empty State */
.empty-state {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 6rem 2rem;
  background-color: #1a2332;
  border-radius: 0.75rem;
  border: 1px solid #232f48;
}

.empty-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.empty-icon {
  font-size: 5rem;
  color: #475569;
  margin-bottom: 1.5rem;
}

.empty-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 1rem;
  color: #92a4c9;
  margin-bottom: 2rem;
}

.btn-primary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  background-color: #135bec;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background-color: #1e40af;
}

/* Matching Progress */
.matching-progress {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.progress-content {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.progress-icon {
  font-size: 2rem;
  color: #135bec;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.progress-info {
  flex: 1;
}

.progress-title {
  font-size: 1rem;
  font-weight: 600;
  color: white;
  margin-bottom: 0.25rem;
}

.progress-status {
  font-size: 0.875rem;
  color: #92a4c9;
}

.progress-bar-wrapper {
  flex: 1;
  height: 0.5rem;
  background-color: #232f48;
  border-radius: 9999px;
  overflow: hidden;
}

.progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #135bec, #3b82f6);
  border-radius: 9999px;
  transition: width 0.3s ease;
}

.progress-percent {
  font-size: 1.125rem;
  font-weight: 700;
  color: #135bec;
  min-width: 3.5rem;
  text-align: right;
}

.stop-matching-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background-color: #ef4444;
  color: white;
  border: none;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  white-space: nowrap;
}

.stop-matching-btn:hover {
  background-color: #dc2626;
  transform: scale(1.02);
}

.stop-matching-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Stats Grid */
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.stat-card {
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.75rem;
  padding: 1.25rem;
  display: flex;
  flex-direction: column;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
  position: relative;
  overflow: hidden;
  cursor: pointer;
  transition: border-color 0.2s;
}

.stat-card:hover {
  border-color: #324467;
}

.stat-bar {
  position: absolute;
  right: 0;
  top: 0;
  height: 100%;
  width: 4px;
}

.stat-card.success .stat-bar {
  background-color: #22c55e;
}

.stat-card.warning .stat-bar {
  background-color: #eab308;
}

.stat-card.error .stat-bar {
  background-color: #ef4444;
}

.stat-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.stat-label {
  color: #94a3b8;
  font-size: 0.875rem;
  font-weight: 500;
  margin-bottom: 0.5rem;
}

.stat-badge {
  background-color: rgba(234, 179, 8, 0.1);
  color: #eab308;
  font-size: 0.625rem;
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.stat-card.error .stat-badge {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.stat-content {
  display: flex;
  align-items: flex-end;
  justify-content: space-between;
}

.stat-value {
  font-size: 1.875rem;
  font-weight: 700;
  font-family: "Space Grotesk", "Noto Sans SC", sans-serif;
}

.stat-card.success .stat-value {
  color: #22c55e;
}

.stat-card.warning .stat-value {
  color: #eab308;
}

.stat-card.error .stat-value {
  color: #ef4444;
}

.stat-icon {
  color: #475569;
  font-size: 1.5rem;
}

.stat-card.success .stat-icon {
  color: rgba(34, 197, 94, 0.2);
}

.stat-card.warning .stat-icon {
  color: rgba(234, 179, 8, 0.2);
}

.stat-card.error .stat-icon {
  color: rgba(239, 68, 68, 0.2);
}

/* Table Container */
.table-container {
  display: flex;
  flex-direction: column;
  background-color: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.75rem;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
}

.sheet-tabs-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  padding: 0.75rem 1rem 0;
}

.sheet-tab-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  height: 32px;
  padding: 0 0.75rem;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  background: rgba(15, 23, 42, 0.7);
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.8125rem;
}

.sheet-tab-btn.active {
  border-color: #135bec;
  background: #135bec;
  color: #fff;
}

.sheet-tab-count {
  min-width: 20px;
  padding: 0 0.375rem;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.12);
  font-size: 0.7rem;
}

.table-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #2a3447;
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  justify-content: space-between;
  align-items: center;
  background-color: rgba(21, 26, 35, 0.5);
}

.table-controls-left,
.table-controls-right {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.filter-select,
.data-source-select {
  position: relative;
  display: flex;
  align-items: center;
}

.filter-select .material-symbols-outlined,
.data-source-select .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.filter-select select,
.data-source-select select {
  padding: 0.5rem 2rem 0.5rem 2.5rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
  appearance: none;
}

.filter-select select:focus,
.data-source-select select:focus {
  border-color: #135bec;
}

/* Pricing Params Dropdown */
.pricing-params-dropdown {
  position: relative;
}

.pricing-params-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.pricing-params-btn:hover {
  border-color: #3b4d6a;
  background-color: #161d2d;
}

.pricing-params-btn.active {
  border-color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.pricing-params-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.pricing-params-btn .dropdown-arrow {
  font-size: 1rem;
  transition: transform 0.2s;
}

.pricing-params-btn.active .dropdown-arrow {
  transform: rotate(180deg);
}

/* 去重切换按钮 */
.dedupe-btn {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 0.875rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: #e2e8f0;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
  transition: all 0.2s;
}

.dedupe-btn:hover {
  border-color: #3b4d6a;
  background-color: #161d2d;
}

.dedupe-btn.active {
  border-color: #135bec;
  background-color: #135bec;
  color: #ffffff;
  box-shadow: 0 0 0 1px rgba(19, 91, 236, 0.4), 0 2px 8px rgba(19, 91, 236, 0.35);
}

.dedupe-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.dedupe-count {
  font-size: 0.75rem;
  font-weight: 600;
  padding: 0.05rem 0.35rem;
  border-radius: 0.5rem;
  background-color: rgba(255, 255, 255, 0.25);
  color: #ffffff;
}

.pricing-params-panel {
  position: absolute;
  top: calc(100% + 0.5rem);
  right: 0;
  width: 320px;
  background-color: #1a2332;
  border: 1px solid #3b4d6a;
  border-radius: 0.75rem;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.4);
  z-index: 100;
  overflow: hidden;
}

.params-panel-header {
  padding: 1rem;
  border-bottom: 1px solid #2a3447;
  background-color: rgba(19, 91, 236, 0.05);
}

.params-panel-title {
  display: block;
  font-size: 0.9375rem;
  font-weight: 600;
  color: #f1f5f9;
}

.params-panel-desc {
  display: block;
  font-size: 0.75rem;
  color: #94a3b8;
  margin-top: 0.25rem;
}

.params-list {
  padding: 0.75rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.param-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.625rem 0.75rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  transition: all 0.2s;
}

.param-item:hover {
  border-color: #3b4d6a;
  background-color: #161d2d;
}

.param-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.param-icon {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: rgba(19, 91, 236, 0.15);
  border-radius: 0.375rem;
  color: #60a5fa;
  font-size: 1.125rem;
}

.param-text {
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.param-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: #f1f5f9;
}

.param-desc {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Switch Toggle */
.param-switch {
  position: relative;
  display: inline-block;
  width: 40px;
  height: 22px;
  flex-shrink: 0;
}

.param-switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.switch-slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #374151;
  border-radius: 22px;
  transition: all 0.3s;
}

.switch-slider:before {
  content: '';
  position: absolute;
  height: 18px;
  width: 18px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  border-radius: 50%;
  transition: all 0.3s;
}

.param-switch input:checked + .switch-slider {
  background-color: #135bec;
}

.param-switch input:checked + .switch-slider:before {
  transform: translateX(18px);
}

.params-panel-footer {
  padding: 0.75rem 1rem;
  border-top: 1px solid #2a3447;
  display: flex;
  gap: 0.5rem;
  justify-content: flex-end;
  background-color: rgba(21, 26, 35, 0.5);
}

.params-reset-btn,
.params-apply-btn {
  padding: 0.5rem 0.875rem;
  border-radius: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
}

.params-reset-btn {
  background-color: transparent;
  color: #94a3b8;
  border: 1px solid #374151;
}

.params-reset-btn:hover {
  background-color: #374151;
  color: #e2e8f0;
}

.params-apply-btn {
  background-color: #135bec;
  color: white;
}

.params-apply-btn:hover {
  background-color: #1d4ed8;
}

.btn-secondary {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #cbd5e1;
  background: transparent;
  border: 1px solid #232f48;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover:not(:disabled) {
  background-color: rgba(100, 116, 139, 0.1);
}

.btn-secondary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-danger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  color: #fca5a5;
  background: transparent;
  border: 1px solid #ef4444;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-danger:hover:not(:disabled) {
  background-color: rgba(239, 68, 68, 0.15);
  color: #f87171;
}

.btn-danger:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  color: #9ca3af;
  border-color: #4b5563;
}

.delete-count {
  font-size: 0.75rem;
  color: inherit;
}

/* Custom Circular Checkbox */
.custom-checkbox {
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
}

.checkbox-circle {
  width: 1.25rem;
  height: 1.25rem;
  border-radius: 50%;
  border: 2px solid #64748b;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  background: transparent;
}

.checkbox-circle:hover {
  border-color: #94a3b8;
}

.checkbox-circle.checked {
  border-color: #3b82f6;
  background: #3b82f6;
}

.checkbox-circle.indeterminate {
  border-color: #3b82f6;
  background: transparent;
}

.checkbox-circle .material-symbols-outlined {
  font-size: 0.875rem;
  color: #fff;
}

.checkbox-circle.indeterminate .material-symbols-outlined {
  color: #3b82f6;
}

/* Table Wrapper */
.table-wrapper {
  flex: 1;
  overflow: auto;
  position: relative;
  min-height: 400px;
  /* 虚拟滚动需要可计算的容器高度（clientHeight） */
  height: calc(100vh - 360px);
  max-height: calc(100vh - 360px);
}

/* 虚拟列表 spacer 行：去除任何边距 / padding，避免影响行高度计算 */
.data-table tbody tr.virtual-spacer {
  background: transparent !important;
  border: none !important;
  transition: none;
}
.data-table tbody tr.virtual-spacer td {
  padding: 0;
  border: none;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  text-align: left;
  font-size: 0.75rem;
}

.data-table thead {
  position: sticky;
  top: 0;
  z-index: 10;
  background-color: #1e232f;
  box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
}

.data-table th {
  padding: 1rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #2a3447;
  white-space: nowrap;
}

.col-checkbox { width: 3rem; text-align: center; }
.col-index { width: 3.5rem; text-align: center; }
.col-manufacturer { width: 10rem; }
.col-model { width: 14rem; }
.col-category { width: 10rem; }
.col-service-level { width: 8rem; }
.col-match { width: 14rem; }
.col-confidence { width: 5rem; text-align: center; }
.col-price { width: 7rem; text-align: right; }
.col-coefficient { width: 7rem; text-align: center; }
.col-adjusted-price { width: 7rem; text-align: right; }
.col-actions { width: 6rem; text-align: center; }

.data-table tbody tr {
  transition: background-color 0.2s;
  border-bottom: 1px solid rgba(35, 47, 72, 0.5);
}

.data-table tbody tr:hover {
  background-color: rgba(255, 255, 255, 0.02);
}

.data-table tbody tr.warning-row {
  background-color: rgba(234, 179, 8, 0.05);
  border-left: 3px solid #eab308;
}

.data-table tbody tr.error-row {
  background-color: rgba(239, 68, 68, 0.05);
  border-left: 3px solid #ef4444;
}

.data-table td {
  padding: 0.75rem 0.5rem;
}

.original-model {
  color: #cbd5e1;
}

.matched-model {
  cursor: pointer;
  font-weight: 500;
  transition: color 0.2s;
}

.matched-model.high-match {
  color: #22c55e;
}

.matched-model.mid-match {
  color: #eab308;
}

.matched-model.low-match {
  color: #f97316;
}

.matched-model.no-match {
  color: #94a3b8;
  font-style: italic;
}

.matched-model:hover {
  text-decoration: underline;
}

/* 匹配单元格包装器 */
.match-cell-wrapper {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.clear-match-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.25rem;
  height: 1.25rem;
  padding: 0;
  background-color: transparent;
  border: 1px solid #475569;
  border-radius: 0.25rem;
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
  opacity: 0.6;
}

.clear-match-btn:hover {
  background-color: rgba(239, 68, 68, 0.15);
  border-color: #ef4444;
  color: #ef4444;
  opacity: 1;
}

.clear-match-btn .material-symbols-outlined {
  font-size: 0.875rem;
}

.confidence-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 600;
  min-width: 3rem;
}

.confidence-badge.high {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
  border: 1px solid rgba(34, 197, 94, 0.2);
}

.confidence-badge.mid {
  background-color: rgba(234, 179, 8, 0.1);
  color: #eab308;
  border: 1px solid rgba(234, 179, 8, 0.2);
}

.confidence-badge.low {
  background-color: rgba(249, 115, 22, 0.1);
  color: #f97316;
  border: 1px solid rgba(249, 115, 22, 0.2);
}

.confidence-badge.none {
  background-color: rgba(148, 163, 184, 0.1);
  color: #94a3b8;
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.coefficient-value {
  color: #135bec;
  font-weight: 500;
}

.service-level-info {
  color: #92a4c9;
  font-size: 0.7rem;
}

.action-btn {
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #9ca3af;
  margin: 0 0.125rem;
}

.action-btn.edit:hover {
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
}

.action-btn.confirm:hover {
  color: #22c55e;
  background-color: rgba(34, 197, 94, 0.1);
}

/* Table Footer */
.table-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #2a3447;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background-color: #1e232f;
}

.footer-text {
  font-size: 0.875rem;
  color: #94a3b8;
}

/* Bottom Bar */
.bottom-bar {
  position: sticky;
  bottom: 0;
  z-index: 50;
  background-color: #1a2332;
  border-top: 1px solid #232f48;
  padding: 1rem;
  box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.1);
}

.bottom-content {
  max-width: 1600px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.bottom-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  color: #94a3b8;
}

.bottom-info .material-symbols-outlined {
  color: #eab308;
}

.bottom-info strong {
  color: white;
}

.bottom-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.btn-draft {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border-radius: 0.5rem;
  background-color: transparent;
  color: #92a4c9;
  font-weight: 600;
  font-size: 0.875rem;
  border: 1px solid #3e4c6b;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-draft:hover:not(:disabled) {
  background-color: #2d3b59;
  color: white;
  border-color: #4e5c7b;
}

.btn-draft:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-draft .material-symbols-outlined {
  font-size: 1.125rem;
}

.btn-draft .material-symbols-outlined.spinning {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

.btn-back,
.btn-next {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  font-size: 0.875rem;
  font-weight: 500;
  transition: all 0.2s;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.btn-back {
  border: 1px solid #232f48;
  background: transparent;
  color: white;
}

.btn-back:hover {
  background-color: rgba(100, 116, 139, 0.1);
}

.btn-next {
  background-color: #135bec;
  color: white;
  border: none;
  font-weight: 700;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.25);
}

.btn-next:hover {
  background-color: #1d6bf5;
}

/* Search Dialog */
.dialog-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.dialog-content {
  background-color: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.75rem;
  width: 90%;
  max-width: 600px;
  max-height: 80vh;
  display: flex;
  flex-direction: column;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
}

.dialog-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.5rem;
  border-bottom: 1px solid #2a3447;
}

.dialog-title {
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
}

.dialog-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.dialog-close:hover {
  background-color: rgba(100, 116, 139, 0.1);
  color: white;
}

.dialog-body {
  padding: 1.5rem;
  overflow-y: auto;
  flex: 1;
}

/* 搜索对话框中的数据源选择器 */
.search-source-selector {
  margin-bottom: 1rem;
  padding: 0.75rem 1rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
}

.search-source-selector .source-label {
  display: block;
  color: #94a3b8;
  font-size: 0.875rem;
  margin-bottom: 0.5rem;
}

.search-source-selector .source-options {
  display: flex;
  gap: 1.5rem;
}

.source-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  position: relative;
}

.source-option input[type="radio"] {
  position: absolute;
  opacity: 0;
  width: 0;
  height: 0;
}

.source-radio {
  width: 16px;
  height: 16px;
  border: 2px solid #475569;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.source-option:hover .source-radio {
  border-color: #22c55e;
}

.source-option input[type="radio"]:checked ~ .source-radio {
  background-color: #22c55e;
  border-color: #22c55e;
}

.source-option input[type="radio"]:checked ~ .source-radio::after {
  content: '';
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background-color: white;
}

.source-option input[type="radio"]:focus ~ .source-name {
  color: #22c55e;
}

.source-name {
  color: #cbd5e1;
  font-size: 0.875rem;
  user-select: none;
}

.search-input-group {
  position: relative;
  display: flex;
  align-items: center;
  margin-bottom: 1rem;
}

.search-input-group .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.search-input-field {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 2.75rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  outline: none;
}

.search-input-field:focus {
  border-color: #135bec;
}

.search-results {
  margin-top: 1rem;
}

.search-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #94a3b8;
}

.loading-icon {
  animation: spin 1s linear infinite;
}

.results-header {
  font-size: 0.875rem;
  color: #94a3b8;
  margin-bottom: 0.75rem;
}

.results-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.result-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: #1a2332;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.result-item:hover {
  background-color: #232f48;
  border-color: #135bec;
}

.result-info {
  flex: 1;
}

.result-model {
  font-weight: 500;
  color: #135bec;
  margin-bottom: 0.25rem;
}

.result-details {
  font-size: 0.75rem;
  color: #94a3b8;
}

.result-price {
  font-size: 0.875rem;
  font-weight: 600;
  color: #22c55e;
}

.no-results {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  color: #94a3b8;
}

.no-results .material-symbols-outlined {
  font-size: 2rem;
}

.results-pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  margin-top: 1rem;
}

.page-btn {
  background: transparent;
  border: 1px solid #232f48;
  color: #94a3b8;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.page-btn:hover:not(:disabled) {
  background-color: #232f48;
  color: white;
}

.page-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.page-info {
  font-size: 0.875rem;
  color: #94a3b8;
}

.dialog-footer {
  padding: 1rem 1.5rem;
  border-top: 1px solid #2a3447;
  display: flex;
  justify-content: flex-end;
}

/* Background Effects */
.background-effects {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: -1;
  overflow: hidden;
}

.effect-blob {
  position: absolute;
  border-radius: 9999px;
  filter: blur(100px);
}

.effect-top {
  top: -10%;
  right: -5%;
  width: 500px;
  height: 500px;
  background-color: rgba(19, 91, 236, 0.05);
}

.effect-bottom {
  bottom: -10%;
  left: -5%;
  width: 600px;
  height: 600px;
  background-color: rgba(37, 99, 235, 0.05);
  filter: blur(120px);
}

/* Scrollbar */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #1e232f;
}

::-webkit-scrollbar-thumb {
  background: #324467;
  border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
  background: #4b6189;
}

/* 联想框架报价：模式切换 / 列 / 对话框 */
.quote-mode-toggle {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  background: rgba(20, 30, 48, 0.6);
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.5rem;
  color: #c7d3e6;
}

.quote-mode-toggle .mode-option {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.6rem;
  border-radius: 0.35rem;
  cursor: pointer;
  font-size: 0.85rem;
  color: #8aa0c0;
  transition: all 0.15s;
}

.quote-mode-toggle .mode-option input[type="radio"] {
  display: none;
}

.quote-mode-toggle .mode-option.active {
  background: #2563eb;
  color: #fff;
  font-weight: 600;
}

.lenovo-config-btn {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  padding: 0.4rem 0.85rem;
  background: rgba(20, 30, 48, 0.6);
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.5rem;
  color: #c7d3e6;
  cursor: pointer;
  font-size: 0.85rem;
}

.lenovo-config-btn:hover {
  background: rgba(37, 99, 235, 0.15);
  border-color: #2563eb;
  color: #fff;
}

.col-end-type { width: 5rem; text-align: center; }
.col-sub-category { width: 7rem; text-align: center; }
.col-match-method { width: 6rem; text-align: center; }

.lenovo-end-type-badge {
  display: inline-block;
  padding: 0.15rem 0.55rem;
  border-radius: 0.35rem;
  background: rgba(37, 99, 235, 0.18);
  color: #74a8ff;
  font-weight: 600;
  font-size: 0.8rem;
}

.match-method-badge {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  border-radius: 0.35rem;
  font-size: 0.75rem;
}
.match-method-badge.method-exact { background: rgba(34, 197, 94, 0.18); color: #4ade80; }
.match-method-badge.method-fuzzy { background: rgba(234, 179, 8, 0.18); color: #facc15; }
.match-method-badge.method-pattern { background: rgba(168, 85, 247, 0.18); color: #c084fc; }
.match-method-badge.method-none { background: rgba(239, 68, 68, 0.18); color: #f87171; }

.lenovo-config-dialog {
  max-width: 720px;
}

.lenovo-config-tip {
  color: #8aa0c0;
  margin: 0 0 1rem 0;
  font-size: 0.85rem;
}

.lenovo-form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.85rem 1.2rem;
}

.lenovo-form-item {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

.lenovo-form-item label {
  font-size: 0.8rem;
  color: #8aa0c0;
}

.lenovo-form-item input,
.lenovo-form-item select {
  padding: 0.5rem 0.75rem;
  background: rgba(20, 30, 48, 0.8);
  border: 1px solid rgba(75, 97, 137, 0.4);
  border-radius: 0.4rem;
  color: #e3eaf5;
  font-size: 0.88rem;
}

.text-muted { color: #6b7d96; }

/* Responsive */
@media (max-width: 1024px) {
  .nav-links {
    display: none;
  }

  .table-container {
    overflow-x: auto;
  }
}

/* 联想框架"端型"列：单元格 wrapper */
.end-type-cell-wrapper {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}
.lenovo-end-type-badge.clickable {
  cursor: pointer;
  user-select: none;
  display: inline-flex;
  align-items: center;
  gap: 2px;
  transition: filter 0.15s, box-shadow 0.15s;
}
.lenovo-end-type-badge.clickable:hover {
  filter: brightness(1.15);
  box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.45);
}
.lenovo-end-type-badge.empty {
  color: #94a3b8;
  background: rgba(148, 163, 184, 0.12) !important;
  border: 1px dashed rgba(148, 163, 184, 0.4);
}
.lenovo-end-type-badge.manual-locked {
  outline: 1px solid #22c55e;
}
.lenovo-end-type-badge .dropdown-icon {
  font-size: 1rem;
  opacity: 0.7;
}
</style>

<!-- 端型下拉浮层（Teleport 到 body，需要 non-scoped 样式） -->
<style>
.end-type-dropdown-mask {
  position: fixed;
  inset: 0;
  z-index: 1999;
}
.end-type-dropdown {
  position: fixed;
  z-index: 2000;
  min-width: 160px;
  background: #1e232f;
  border: 1px solid #334155;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
  padding: 8px 0;
  color: #e2e8f0;
  font-family: "Noto Sans SC", sans-serif;
  font-size: 0.8rem;
}
.end-type-dropdown .dropdown-title {
  padding: 4px 12px 8px;
  font-size: 0.7rem;
  font-weight: 600;
  letter-spacing: 0.05em;
  color: #94a3b8;
  text-transform: uppercase;
  border-bottom: 1px solid #2a3447;
  margin-bottom: 4px;
}
.end-type-dropdown .dropdown-list {
  max-height: 280px;
  overflow-y: auto;
}
.end-type-dropdown .dropdown-option {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  cursor: pointer;
  transition: background 0.12s;
}
.end-type-dropdown .dropdown-option:hover {
  background: rgba(96, 165, 250, 0.12);
}
.end-type-dropdown .dropdown-option.active {
  background: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}
.end-type-dropdown .dropdown-option .material-symbols-outlined {
  font-size: 1rem;
}
.end-type-dropdown .dropdown-loading,
.end-type-dropdown .dropdown-empty {
  padding: 16px;
  text-align: center;
  color: #94a3b8;
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}
.end-type-dropdown .spinning {
  animation: spin 1s linear infinite;
}
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* ============ 对应关系批量确认弹窗 ============ */
.alias-batch-overlay {
  position: fixed;
  inset: 0;
  z-index: 2050;
  background: rgba(15, 23, 42, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  font-family: "Noto Sans SC", sans-serif;
}
.alias-batch-dialog {
  background: #1e232f;
  border: 1px solid #334155;
  border-radius: 10px;
  width: min(1100px, 100%);
  max-height: 85vh;
  display: flex;
  flex-direction: column;
  color: #e2e8f0;
  box-shadow: 0 20px 50px rgba(0, 0, 0, 0.5);
}
.alias-batch-header {
  padding: 1.25rem 1.5rem 1rem;
  border-bottom: 1px solid #2a3447;
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 1rem;
}
.alias-batch-header h3 {
  margin: 0 0 6px;
  font-size: 1rem;
  font-weight: 600;
}
.alias-batch-tip {
  margin: 0;
  color: #94a3b8;
  font-size: 0.78rem;
  line-height: 1.5;
}
.alias-batch-tip strong { color: #fbbf24; }
.alias-batch-close {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  display: inline-flex;
  align-items: center;
  padding: 4px;
}
.alias-batch-close:hover { color: #f87171; }

.alias-batch-body {
  flex: 1;
  overflow: auto;
  padding: 0 1.5rem;
  min-height: 200px;
}
.alias-batch-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.78rem;
}
.alias-batch-table thead {
  position: sticky;
  top: 0;
  background: #1e232f;
  z-index: 1;
}
.alias-batch-table th {
  padding: 0.6rem 0.5rem;
  font-weight: 600;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  font-size: 0.7rem;
  text-align: left;
  border-bottom: 1px solid #2a3447;
  white-space: nowrap;
}
.alias-batch-table td {
  padding: 0.55rem 0.5rem;
  border-bottom: 1px solid rgba(35, 47, 72, 0.5);
  vertical-align: middle;
}
.alias-batch-table tbody tr {
  cursor: pointer;
  transition: background 0.12s;
}
.alias-batch-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.03);
}
.alias-batch-table tbody tr.selected {
  background: rgba(34, 197, 94, 0.08);
}
.alias-batch-table .col-check { width: 36px; text-align: center; }
.alias-batch-table .col-arrow { width: 24px; text-align: center; color: #64748b; }
.alias-batch-table .col-rows { width: 78px; text-align: center; }
.alias-batch-table .col-src { width: 110px; }
.alias-batch-table .col-endtype { width: 90px; }
.alias-batch-table .col-cat { width: 110px; }
.alias-batch-table .mono { font-family: monospace; color: #cbd5e1; }

/* checkbox circle */
.batch-checkbox {
  display: inline-flex;
  cursor: pointer;
  user-select: none;
}
.cb-circle {
  width: 18px;
  height: 18px;
  border-radius: 4px;
  border: 1.5px solid #475569;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: #0f1525;
  transition: all 0.12s;
}
.cb-circle.checked {
  background: #22c55e;
  border-color: #22c55e;
}
.cb-circle.indeterminate {
  background: #3b82f6;
  border-color: #3b82f6;
}
.cb-circle .material-symbols-outlined {
  font-size: 14px;
  color: #ffffff;
}

.alias-end-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.7rem;
  background: rgba(34, 197, 94, 0.18);
  color: #22c55e;
}
.alias-src-badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 0.68rem;
}
.alias-src-badge.end-type { background: rgba(59, 130, 246, 0.18); color: #60a5fa; }
.alias-src-badge.manual-match { background: rgba(245, 158, 11, 0.18); color: #fbbf24; }

.alias-batch-body .empty-state {
  padding: 3rem;
  text-align: center;
  color: #64748b;
}

.alias-batch-footer {
  padding: 0.9rem 1.5rem 1.1rem;
  border-top: 1px solid #2a3447;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-wrap: wrap;
}
.alias-batch-footer .footer-info {
  color: #94a3b8;
  font-size: 0.8rem;
}
.alias-batch-footer .footer-actions {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.alias-batch-footer button {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 6px;
  border: 1px solid transparent;
  cursor: pointer;
  font-size: 0.8rem;
  transition: filter 0.12s;
}
.alias-batch-footer button .material-symbols-outlined { font-size: 16px; }
.alias-batch-footer button:disabled { opacity: 0.45; cursor: not-allowed; }
.alias-batch-footer .btn-primary { background: #3b82f6; color: white; }
.alias-batch-footer .btn-primary:not(:disabled):hover { filter: brightness(1.1); }
.alias-batch-footer .btn-secondary {
  background: #1e232f; color: #e2e8f0; border-color: #2a3447;
}
.alias-batch-footer .btn-secondary:not(:disabled):hover { background: #2a3447; }
.alias-batch-footer .btn-danger {
  background: rgba(239, 68, 68, 0.15);
  color: #fca5a5;
  border-color: rgba(239, 68, 68, 0.4);
}
.alias-batch-footer .btn-danger:not(:disabled):hover { background: rgba(239, 68, 68, 0.25); }
.alias-batch-footer .spinning {
  animation: spin 1s linear infinite;
}
</style>
