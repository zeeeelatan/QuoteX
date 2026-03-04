<template>
  <div class="document-recognition">
    <BranchPageHeader @open-product-database="openProductDatabaseModal" />

    <main class="main-container">
      <div class="page-header">
        <div class="header-content">
          <div class="breadcrumb">
            <a @click="navigateToHome" class="breadcrumb-link">首页</a>
            <span class="material-symbols-outlined">chevron_right</span>
            <span class="breadcrumb-current">智能识别</span>
          </div>
          <div class="title-row">
            <h1 class="page-title">智能文档识别</h1>
            <!-- 报价类型选择 -->
            <div class="quotation-type-selector">
              <span class="material-symbols-outlined">category</span>
              <select v-model="selectedQuotationType" class="quotation-type-dropdown">
                <option value="">请选择报价类型</option>
                <option v-for="category in productCategories" :key="category.id" :value="category.name">
                  {{ category.name }}
                </option>
              </select>
            </div>
          </div>
          <p class="page-description">上传 Excel、Word、PDF 或图片文件，系统将智能识别数据并转换为标准格式。</p>
        </div>
        <div class="header-right">
          <!-- Steps Progress -->
          <div class="steps-progress">
            <div class="step" :class="{ active: isRelocationMode ? relocationCalcRef?.activeTab === 1 : true }">
              <div class="step-number">1</div>
              <span class="step-label" @click="onStepClick(1)" style="cursor: pointer;">{{ stepLabels[0] }}</span>
            </div>
            <div class="step-divider"></div>
            <div class="step" :class="{ active: isRelocationMode && relocationCalcRef?.activeTab === 2 }">
              <div class="step-number">2</div>
              <span class="step-label" @click="onStepClick(2)" style="cursor: pointer;">{{ stepLabels[1] }}</span>
            </div>
            <div class="step-divider"></div>
            <div class="step" :class="{ active: isRelocationMode && relocationCalcRef?.activeTab === 3 }">
              <div class="step-number">3</div>
              <span class="step-label" @click="onStepClick(3)" style="cursor: pointer;">{{ stepLabels[2] }}</span>
            </div>
            <div class="step-divider"></div>
            <div class="step" :class="{ active: isRelocationMode && relocationCalcRef?.activeTab === 4 }">
              <div class="step-number">4</div>
              <span class="step-label" @click="onStepClick(4)" style="cursor: pointer;">{{ stepLabels[3] }}</span>
            </div>
          </div>
        </div>
      </div>

      <div class="content-grid" :class="{ 'onsite-mode': isEmbeddedMode }">
        <!-- 驻场服务报价模式：全宽嵌入驻场服务测算组件 -->
        <div v-if="isOnsiteMode" class="onsite-embed-section">
          <OnsiteServiceCalculator :embedded="true" />
        </div>

        <!-- 搬迁服务报价模式：全宽嵌入搬迁服务测算组件 -->
        <div v-if="isRelocationMode" class="onsite-embed-section">
          <RelocationServiceCalculator ref="relocationCalcRef" :embedded="true" />
        </div>

        <div v-show="!isEmbeddedMode" class="upload-section" :class="{ collapsed: isUploadSectionCollapsed }">
          <div class="upload-card">
            <div class="card-header">
              <h3 class="card-title">源文件</h3>
              <button class="collapse-btn" @click="toggleUploadSection" :title="isUploadSectionCollapsed ? '展开' : '隐藏'">
                <span class="material-symbols-outlined" :class="{ rotated: isUploadSectionCollapsed }">
                  chevron_left
                </span>
              </button>
            </div>

            <div class="upload-content" v-show="!isUploadSectionCollapsed">
              <input type="file" @change="handleFileChange" accept=".xlsx,.xls,.docx,.pdf,.png,.jpg,.jpeg,.bmp,.tiff" id="convert-file-input" style="display: none;" />
              <div class="upload-zone" @click="triggerFileInput">
                <div class="upload-icon-wrapper">
                  <span class="material-symbols-outlined">cloud_upload</span>
                </div>
                <p class="upload-title">点击或拖拽上传文件</p>
                <p class="upload-subtitle">支持 Excel、Word、PDF、图片 格式</p>
              </div>
              <!-- 文件解析中加载状态 -->
              <div v-if="isParsingDocument" class="parsing-overlay">
                <div class="parsing-spinner"></div>
                <p class="parsing-text">{{ parsingMessage }}</p>
              </div>

              <!-- Sheet selector for multi-sheet Excel files -->
              <div class="sheet-selector" v-if="sheetNames.length > 1">
                <h4 class="sheet-selector-title">
                  <span class="material-symbols-outlined">tab</span>
                  工作表 ({{ sheetNames.length }})
                </h4>
                <div class="sheet-tabs">
                  <button
                    v-for="sheet in sheetNames"
                    :key="sheet"
                    class="sheet-tab"
                    :class="{ active: sheet === currentSheetName }"
                    @click="switchSheet(sheet)"
                    :title="sheet"
                  >
                    <span class="sheet-tab-name">{{ sheet }}</span>
                    <span class="sheet-tab-rows" v-if="sheet === currentSheetName">{{ originalTableData.length }} 行</span>
                  </button>
                </div>
              </div>

              <div class="recent-uploads">
                <h4 class="recent-title">最近上传记录</h4>
                <div class="upload-list">
                  <!-- Show current file -->
                  <div
                    class="upload-item active"
                    v-if="originalTableData.length > 0 && currentFileName"
                    @click="triggerFileInput"
                  >
                    <div class="file-icon excel">
                      <span class="material-symbols-outlined">table_view</span>
                    </div>
                    <div class="file-info">
                      <p class="file-name">{{ currentFileName }}</p>
                      <p class="file-meta">{{ originalTableData.length }} 条数据 • {{ currentSheetName || '工作表1' }}</p>
                    </div>
                    <div class="file-action">
                      <button class="action-btn" @click.stop="resetData" title="删除">
                        <span class="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>
                  <!-- Show recent uploads (excluding current file) -->
                  <div
                    v-for="record in recentUploads.filter(r => r.fileName !== currentFileName)"
                    :key="record.id"
                    class="upload-item"
                    @click="loadRecentUpload(record)"
                  >
                    <div class="file-icon excel">
                      <span class="material-symbols-outlined">table_view</span>
                    </div>
                    <div class="file-info">
                      <p class="file-name">{{ record.fileName }}</p>
                      <p class="file-meta">{{ record.rowCount }} 条数据 • {{ formatTimestamp(record.timestamp) }}</p>
                    </div>
                    <div class="file-action">
                      <button
                        class="action-btn"
                        @click.stop="deleteRecentUpload(record.id, $event)"
                        title="删除"
                      >
                        <span class="material-symbols-outlined">delete</span>
                      </button>
                    </div>
                  </div>
                  <!-- Show empty state -->
                  <div class="upload-item" v-if="recentUploads.length === 0">
                    <div class="file-info" style="padding: 0.75rem 0;">
                      <p class="file-name" style="color: #6b7280;">暂无上传记录</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div v-show="!isEmbeddedMode" class="preview-section">
          <!-- 空状态：非维保服务报价 或 维保服务报价但未初始化表格 -->
          <div class="preview-card" v-if="originalTableData.length === 0 && !showManualEntryMode">
            <div class="empty-state">
              <span class="material-symbols-outlined empty-icon">description</span>
              <p class="empty-title">请上传Excel文件</p>
              <p class="empty-subtitle">支持拖拽上传或点击选择文件</p>
            </div>
          </div>

          <!-- 手动输入模式：维保服务报价 且 无导入数据 -->
          <div class="preview-card" v-else-if="showManualEntryMode">
            <div class="preview-header">
              <div class="header-info">
                <span class="item-count">手动输入模式</span>
                <span class="manual-entry-hint">可直接填写表格或上传Excel文件</span>
              </div>
              <div class="header-controls">
                <button class="control-btn add-row-btn" @click="addManualRow" title="添加行">
                  <span class="material-symbols-outlined">add</span>
                  添加行
                </button>
                <button class="control-btn" @click="resetData" title="清空数据">
                  <span class="material-symbols-outlined">refresh</span>
                </button>
                <button class="control-btn" @click="openFullscreenModal" title="全屏查看">
                  <span class="material-symbols-outlined">fullscreen</span>
                </button>
                <div class="divider"></div>
                <button class="export-btn" @click="exportConvertedData">
                  <span class="material-symbols-outlined">download</span>
                  导出 Excel
                </button>
              </div>
            </div>

            <!-- 仅显示转换后表格用于手动输入 -->
            <div class="manual-entry-view" @click="handleClickOutside">
              <div class="table-section converted-table excel-table-section manual-entry-table">
                <div class="table-section-header">
                  <h4 class="table-title-with-count">转换后表格 <span class="table-count">{{ convertedTableData.length }} 行</span></h4>
                  <div class="excel-toolbar">
                    <button class="toolbar-btn" @click="undo" title="撤销 (Ctrl+Z)" :disabled="!canUndo">
                      <span class="material-symbols-outlined">undo</span>
                    </button>
                    <button class="toolbar-btn" @click="redo" title="重做 (Ctrl+Y)" :disabled="!canRedo">
                      <span class="material-symbols-outlined">redo</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <button class="toolbar-btn" @click="copySelectedCells" title="复制 (Ctrl+C)" :disabled="selectedCells.size === 0">
                      <span class="material-symbols-outlined">content_copy</span>
                    </button>
                    <button class="toolbar-btn" @click="pasteFromClipboard" title="粘贴 (Ctrl+V)">
                      <span class="material-symbols-outlined">content_paste</span>
                    </button>
                    <button class="toolbar-btn" @click="clearSelectedCells" title="清空选中" :disabled="selectedCells.size === 0">
                      <span class="material-symbols-outlined">backspace</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <button class="toolbar-btn reset-btn" @click="resetToInitial" title="重置到初始状态" :disabled="initialTableData.length === 0">
                      <span class="material-symbols-outlined">restart_alt</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <span class="selection-info" v-if="selectedCells.size > 0">
                      已选 {{ selectedCells.size }} 格
                    </span>
                  </div>
                </div>
                <div class="table-wrapper excel-table-wrapper"
                     @mousedown="handleTableMouseDown"
                     @mousemove="handleTableMouseMove"
                     @mouseup="handleTableMouseUp"
                     @keydown="handleTableKeyDown"
                     tabindex="0"
                     ref="excelTableRef">
                  <table class="data-table excel-data-table">
                    <thead>
                      <tr>
                        <th v-for="(header, colIndex) in visibleColumns" :key="header" class="column-mapping-th">
                          <div class="header-with-dropdown">
                            <div class="header-label">
                              <span class="header-name">{{ header }}</span>
                            </div>
                            <span class="mapped-source manual-entry-field" :class="{ required: isRequiredField(header) }">
                              {{ getManualEntryFieldLabel(header) }}
                            </span>
                          </div>
                        </th>
                        <th class="actions-header">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in convertedTableData" :key="'row-' + rowIndex">
                        <td v-for="(header, colIndex) in visibleColumns"
                            :key="'cell-' + rowIndex + '-' + header"
                            :class="getCellClass(rowIndex, colIndex)"
                            :data-row="rowIndex"
                            :data-col="colIndex"
                            @mousedown.stop="handleCellMouseDown(rowIndex, colIndex, $event)"
                            @mouseenter="handleCellMouseEnter(rowIndex, colIndex)"
                            @dblclick="startCellEdit(rowIndex, colIndex)">
                          <!-- 序号列只读 -->
                          <span v-if="header === '序号'" class="table-cell-text">{{ rowIndex + 1 }}</span>
                          <!-- 编辑状态 -->
                          <input
                            v-else-if="isEditing(rowIndex, colIndex)"
                            type="text"
                            v-model="row[header]"
                            class="table-input editing"
                            @mousedown.stop
                            @click.stop
                            @blur="endCellEdit"
                            @keydown.enter="endCellEdit"
                            @keydown.tab.prevent="moveToNextCell"
                            @keydown.esc="endCellEdit"
                            ref="editInputRef"
                            autofocus
                          />
                          <!-- 普通显示状态 -->
                          <span v-else class="table-cell-text" :class="{ placeholder: !row[header] }">
                            {{ row[header] || getPlaceholderText(header) }}
                          </span>
                        </td>
                        <td class="actions-cell">
                          <button class="delete-row-btn" @click="deleteRow(rowIndex)" title="删除此行">
                            <span class="material-symbols-outlined">delete</span>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <!-- 手动输入模式底部操作栏 -->
            <div class="table-footer">
              <div class="footer-stats">
                <div class="stat-item">
                  <span class="stat-label">总项数</span>
                  <span class="stat-value">{{ convertedTableData.length }}</span>
                </div>
                <div class="stat-divider"></div>
                <div class="stat-item">
                  <span class="stat-label">总数量</span>
                  <span class="stat-value">{{ getTotalQuantity() }}</span>
                </div>
              </div>
              <div class="footer-action">
                <div class="action-buttons">
                  <button class="draft-btn" @click="saveAsDraft" :disabled="isSavingDraft" :title="'快捷键: Ctrl+S'">
                    <span class="material-symbols-outlined" v-if="!isSavingDraft">save</span>
                    <span class="material-symbols-outlined spinning" v-else>sync</span>
                    {{ isSavingDraft ? '保存中...' : '存为草稿' }}
                  </button>
                  <button class="next-btn" @click="goToSmartMatching">
                    下一步: 智能匹配
                    <span class="material-symbols-outlined">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>
          </div>

          <!-- 已导入数据模式 -->
          <div class="preview-card" v-else>
            <div class="preview-header">
              <div class="header-info">
                <span class="item-count">识别结果</span>
              </div>
              <div class="header-controls">
                <button class="control-btn" @click="resetData" title="清空数据">
                  <span class="material-symbols-outlined">refresh</span>
                </button>
                <button class="control-btn" @click="openFullscreenModal" title="全屏查看">
                  <span class="material-symbols-outlined">fullscreen</span>
                </button>
                <div class="divider"></div>
                <button class="export-btn" @click="exportConvertedData">
                  <span class="material-symbols-outlined">download</span>
                  导出 Excel
                </button>
              </div>
            </div>

            <!-- Split View: Original Table -->
            <div class="split-view" @click="handleClickOutside">
              <div class="table-section original-table">
                <h4 class="table-title-with-count">原始表格 <span class="table-count">已识别 {{ originalTableData.length }} 项</span></h4>
                <div class="table-wrapper">
                  <table class="data-table">
                    <thead>
                      <tr>
                        <th v-for="(header, index) in originalHeaders" :key="index" class="resizable-th">
                          {{ header }}
                        </th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in originalTableData" :key="rowIndex">
                        <td v-for="(header, colIndex) in originalHeaders" :key="colIndex">
                          {{ row[header] || '' }}
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>

              <!-- Converted Table with Excel-like features -->
              <div class="table-section converted-table excel-table-section">
                <div class="table-section-header">
                  <h4 class="table-title-with-count">转换后表格 <span class="table-count">已识别 {{ convertedTableData.length }} 项</span></h4>
                  <div class="excel-toolbar">
                    <button class="toolbar-btn" @click="undo" title="撤销 (Ctrl+Z)" :disabled="!canUndo">
                      <span class="material-symbols-outlined">undo</span>
                    </button>
                    <button class="toolbar-btn" @click="redo" title="重做 (Ctrl+Y)" :disabled="!canRedo">
                      <span class="material-symbols-outlined">redo</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <button class="toolbar-btn" @click="copySelectedCells" title="复制 (Ctrl+C)" :disabled="selectedCells.size === 0">
                      <span class="material-symbols-outlined">content_copy</span>
                    </button>
                    <button class="toolbar-btn" @click="pasteFromClipboard" title="粘贴 (Ctrl+V)">
                      <span class="material-symbols-outlined">content_paste</span>
                    </button>
                    <button class="toolbar-btn" @click="clearSelectedCells" title="清空选中" :disabled="selectedCells.size === 0">
                      <span class="material-symbols-outlined">backspace</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <button class="toolbar-btn reset-btn" @click="resetToInitial" title="重置到初始状态" :disabled="initialTableData.length === 0">
                      <span class="material-symbols-outlined">restart_alt</span>
                    </button>
                    <div class="toolbar-divider"></div>
                    <span class="selection-info" v-if="selectedCells.size > 0">
                      已选 {{ selectedCells.size }} 格
                    </span>
                  </div>
                </div>
                <div class="table-wrapper excel-table-wrapper" 
                     @mousedown="handleTableMouseDown"
                     @mousemove="handleTableMouseMove"
                     @mouseup="handleTableMouseUp"
                     @keydown="handleTableKeyDown"
                     tabindex="0"
                     ref="excelTableRef">
                  <table class="data-table excel-data-table">
                    <thead>
                      <tr>
                        <th v-for="(header, colIndex) in visibleColumns" :key="header" class="column-mapping-th">
                          <div class="header-with-dropdown" @click="toggleHeaderDropdown(header, $event)">
                            <div class="header-label">
                              <span class="header-name">{{ header }}</span>
                              <span class="material-symbols-outlined dropdown-icon">expand_more</span>
                            </div>
                            <span class="mapped-source" :class="{ mapped: columnMappings[header] }">
                              {{ getMappedOriginalHeader(header) }}
                            </span>
                            <!-- 下拉框 -->
                            <div
                              v-if="activeDropdownForColumn === header"
                              class="column-mapping-dropdown"
                              @click.stop
                            >
                              <div class="dropdown-header">
                                <span class="dropdown-title">选择对应列</span>
                                <button
                                  v-if="columnMappings[header]"
                                  class="clear-mapping-btn"
                                  @click="clearMapping(header)"
                                  title="清除映射"
                                >
                                  <span class="material-symbols-outlined">close</span>
                                </button>
                              </div>
                              <div class="dropdown-options">
                                <div
                                  v-for="originalHeader in originalHeaders"
                                  :key="originalHeader"
                                  class="dropdown-option"
                                  :class="{ selected: columnMappings[header] === originalHeader }"
                                  @click="selectOriginalHeader(header, originalHeader)"
                                >
                                  <span class="material-symbols-outlined option-icon">
                                    {{ columnMappings[header] === originalHeader ? 'check_circle' : 'radio_button_unchecked' }}
                                  </span>
                                  <span class="option-text">{{ originalHeader }}</span>
                                </div>
                                <div
                                  v-if="originalHeaders.length === 0"
                                  class="dropdown-empty"
                                >
                                  请先上传Excel文件
                                </div>
                              </div>
                            </div>
                          </div>
                        </th>
                        <th class="actions-header">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in convertedTableData" :key="'row-' + rowIndex">
                        <td v-for="(header, colIndex) in visibleColumns" 
                            :key="'cell-' + rowIndex + '-' + header"
                            :class="getCellClass(rowIndex, colIndex)"
                            :data-row="rowIndex"
                            :data-col="colIndex"
                            @mousedown.stop="handleCellMouseDown(rowIndex, colIndex, $event)"
                            @mouseenter="handleCellMouseEnter(rowIndex, colIndex)"
                            @dblclick="startCellEdit(rowIndex, colIndex)">
                          <!-- 序号列只读 -->
                          <span v-if="header === '序号'" class="table-cell-text">{{ rowIndex + 1 }}</span>
                          <!-- 编辑状态 -->
                          <input
                            v-else-if="isEditing(rowIndex, colIndex)"
                            type="text"
                            v-model="row[header]"
                            class="table-input editing"
                            @mousedown.stop
                            @click.stop
                            @blur="endCellEdit"
                            @keydown.enter="endCellEdit"
                            @keydown.tab.prevent="moveToNextCell"
                            @keydown.esc="endCellEdit"
                            ref="editInputRef"
                            autofocus
                          />
                          <!-- 普通显示状态 -->
                          <span v-else class="cell-content">{{ row[header] || '' }}</span>
                          <!-- 填充手柄 -->
                          <div 
                            v-if="isFillHandleCell(rowIndex, colIndex)" 
                            class="fill-handle"
                            @mousedown.stop="startFillDrag(rowIndex, colIndex, $event)">
                          </div>
                        </td>
                        <td class="actions-cell">
                          <button class="action-btn delete" @click="deleteRow(rowIndex)" title="删除">
                            <span class="material-symbols-outlined">delete</span>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                  <!-- 选择框覆盖层 -->
                  <div v-if="isSelecting" class="selection-overlay" :style="selectionBoxStyle"></div>
                  <!-- 填充预览 -->
                  <div v-if="isFillDragging" class="fill-preview" :style="fillPreviewStyle"></div>
                </div>
              </div>
            </div>

            <div class="table-footer">
              <div class="footer-stats">
                <div class="stat-item">
                  <span class="stat-label">总项数</span>
                  <span class="stat-value">{{ convertedTableData.length }}</span>
                </div>
                <div class="stat-divider"></div>
                <div class="stat-item">
                  <span class="stat-label">总数量</span>
                  <span class="stat-value">{{ getTotalQuantity() }}</span>
                </div>
              </div>
              <div class="footer-action">
                <div class="total-amount" v-if="getTotalAmount() > 0">
                  <p class="amount-label">预估总金额</p>
                  <p class="amount-value">¥{{ getTotalAmount().toFixed(2) }}</p>
                </div>
                <div class="action-buttons">
                  <button class="draft-btn" @click="saveAsDraft" :disabled="isSavingDraft" :title="'快捷键: Ctrl+S'">
                    <span class="material-symbols-outlined" v-if="!isSavingDraft">save</span>
                    <span class="material-symbols-outlined spinning" v-else>sync</span>
                    {{ isSavingDraft ? '保存中...' : '存为草稿' }}
                  </button>
                  <button class="next-btn" @click="goToSmartMatching">
                    下一步: 智能匹配
                    <span class="material-symbols-outlined">arrow_forward</span>
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </main>

    <!-- 全屏模态框 -->
    <Teleport to="body">
      <div v-if="isFullscreenModalOpen" class="fullscreen-modal" :class="{ maximized: isModalMaximized }">
        <div class="modal-container" :style="modalStyle" ref="modalRef">
          <!-- 模态框头部 -->
          <div class="modal-header" @mousedown="startDrag">
            <div class="modal-title">
              <span class="material-symbols-outlined">table_view</span>
              识别结果
              <span class="modal-count">共 {{ originalTableData.length }} 项</span>
            </div>
            <div class="modal-actions">
              <button class="modal-btn" @click="toggleMaximize" :title="isModalMaximized ? '还原' : '最大化'">
                <span class="material-symbols-outlined">{{ isModalMaximized ? 'fullscreen_exit' : 'fullscreen' }}</span>
              </button>
              <button class="modal-btn close-btn" @click="closeFullscreenModal" title="关闭">
                <span class="material-symbols-outlined">close</span>
              </button>
            </div>
          </div>
          
          <!-- 模态框内容 -->
          <div class="modal-content">
            <div class="modal-split-view">
              <!-- 原始表格 -->
              <div class="modal-table-section">
                <h4 class="modal-table-title">
                  原始表格 
                  <span class="modal-table-count">已识别 {{ originalTableData.length }} 项</span>
                </h4>
                <div class="modal-table-wrapper">
                  <table class="modal-data-table">
                    <thead>
                      <tr>
                        <th v-for="(header, index) in originalHeaders" :key="index">{{ header }}</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in originalTableData" :key="rowIndex">
                        <td v-for="(header, colIndex) in originalHeaders" :key="colIndex">{{ row[header] || '' }}</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
              
              <!-- 转换后表格 with Excel features -->
              <div class="modal-table-section converted modal-excel-section">
                <div class="modal-section-header">
                  <h4 class="modal-table-title">
                    转换后表格 
                    <span class="modal-table-count">已识别 {{ convertedTableData.length }} 项</span>
                  </h4>
                  <div class="modal-excel-toolbar">
                    <button class="modal-toolbar-btn" @click="undo" title="撤销 (Ctrl+Z)" :disabled="!canUndo">
                      <span class="material-symbols-outlined">undo</span>
                    </button>
                    <button class="modal-toolbar-btn" @click="redo" title="重做 (Ctrl+Y)" :disabled="!canRedo">
                      <span class="material-symbols-outlined">redo</span>
                    </button>
                    <div class="modal-toolbar-divider"></div>
                    <button class="modal-toolbar-btn" @click="copySelectedCells" title="复制 (Ctrl+C)" :disabled="selectedCells.size === 0">
                      <span class="material-symbols-outlined">content_copy</span>
                    </button>
                    <button class="modal-toolbar-btn" @click="pasteFromClipboard" title="粘贴 (Ctrl+V)">
                      <span class="material-symbols-outlined">content_paste</span>
                    </button>
                    <button class="modal-toolbar-btn" @click="clearSelectedCells" title="清空选中" :disabled="selectedCells.size === 0">
                      <span class="material-symbols-outlined">backspace</span>
                    </button>
                    <div class="modal-toolbar-divider"></div>
                    <button class="modal-toolbar-btn reset-btn" @click="resetToInitial" title="重置到初始状态" :disabled="initialTableData.length === 0">
                      <span class="material-symbols-outlined">restart_alt</span>
                    </button>
                    <div class="modal-toolbar-divider"></div>
                    <span class="modal-selection-info" v-if="selectedCells.size > 0">
                      已选 {{ selectedCells.size }} 格
                    </span>
                  </div>
                </div>
                <div class="modal-table-wrapper modal-excel-wrapper"
                     @mousedown="handleTableMouseDown"
                     @mousemove="handleTableMouseMove"
                     @mouseup="handleTableMouseUp"
                     @keydown="handleTableKeyDown"
                     tabindex="0"
                     ref="modalExcelTableRef">
                  <table class="modal-data-table converted-table modal-excel-table">
                    <thead>
                      <tr>
                        <th v-for="(header, colIndex) in visibleColumns" :key="header" class="modal-column-mapping-th">
                          <div class="modal-header-with-dropdown" @click="toggleHeaderDropdown(header, $event)">
                            <div class="modal-header-label">
                              <span class="modal-header-name">{{ header }}</span>
                              <span class="material-symbols-outlined modal-dropdown-icon">expand_more</span>
                            </div>
                            <span class="modal-mapped-source" :class="{ mapped: columnMappings[header] }">
                              {{ getMappedOriginalHeader(header) }}
                            </span>
                            <!-- 下拉框 -->
                            <div
                              v-if="activeDropdownForColumn === header"
                              class="modal-column-mapping-dropdown"
                              @click.stop
                            >
                              <div class="modal-dropdown-header">
                                <span class="modal-dropdown-title">选择对应列</span>
                                <button
                                  v-if="columnMappings[header]"
                                  class="modal-clear-mapping-btn"
                                  @click="clearMapping(header)"
                                  title="清除映射"
                                >
                                  <span class="material-symbols-outlined">close</span>
                                </button>
                              </div>
                              <div class="modal-dropdown-options">
                                <div
                                  v-for="originalHeader in originalHeaders"
                                  :key="originalHeader"
                                  class="modal-dropdown-option"
                                  :class="{ selected: columnMappings[header] === originalHeader }"
                                  @click="selectOriginalHeader(header, originalHeader)"
                                >
                                  <span class="material-symbols-outlined modal-option-icon">
                                    {{ columnMappings[header] === originalHeader ? 'check_circle' : 'radio_button_unchecked' }}
                                  </span>
                                  <span class="modal-option-text">{{ originalHeader }}</span>
                                </div>
                                <div v-if="originalHeaders.length === 0" class="modal-dropdown-empty">
                                  请先上传Excel文件
                                </div>
                              </div>
                            </div>
                          </div>
                        </th>
                        <th class="modal-actions-th">操作</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr v-for="(row, rowIndex) in convertedTableData" :key="'modal-row-' + rowIndex">
                        <td v-for="(header, colIndex) in visibleColumns" 
                            :key="'modal-cell-' + rowIndex + '-' + header" 
                            :class="getModalCellClass(rowIndex, colIndex)"
                            :data-row="rowIndex"
                            :data-col="colIndex"
                            @mousedown.stop="handleCellMouseDown(rowIndex, colIndex, $event)"
                            @mouseenter="handleCellMouseEnter(rowIndex, colIndex)"
                            @dblclick="startCellEdit(rowIndex, colIndex)">
                          <!-- 序号列只读 -->
                          <span v-if="header === '序号'" class="modal-cell-text">{{ rowIndex + 1 }}</span>
                          <!-- 编辑状态 -->
                          <input
                            v-else-if="isEditing(rowIndex, colIndex)"
                            type="text"
                            v-model="row[header]"
                            class="modal-table-input modal-editing"
                            @mousedown.stop
                            @click.stop
                            @blur="endCellEdit"
                            @keydown.enter="endCellEdit"
                            @keydown.tab.prevent="moveToNextCell"
                            @keydown.esc="endCellEdit"
                            autofocus
                          />
                          <!-- 普通显示状态 -->
                          <span v-else class="modal-cell-content">{{ row[header] || '' }}</span>
                          <!-- 填充手柄 -->
                          <div 
                            v-if="isFillHandleCell(rowIndex, colIndex)" 
                            class="modal-fill-handle"
                            @mousedown.stop="startFillDrag(rowIndex, colIndex, $event)">
                          </div>
                        </td>
                        <td class="modal-actions-cell">
                          <button class="modal-action-btn delete" @click="deleteRow(rowIndex)" title="删除">
                            <span class="material-symbols-outlined">delete</span>
                          </button>
                        </td>
                      </tr>
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 模态框底部 -->
          <div class="modal-footer">
            <div class="modal-stats">
              <div class="stat-item">
                <span class="stat-label">总项数</span>
                <span class="stat-value">{{ originalTableData.length }}</span>
              </div>
              <div class="stat-divider"></div>
              <div class="stat-item">
                <span class="stat-label">总数量</span>
                <span class="stat-value">{{ totalQuantity }}</span>
              </div>
            </div>
            <div class="modal-footer-actions">
              <button class="modal-export-btn" @click="exportConvertedData">
                <span class="material-symbols-outlined">download</span>
                导出 Excel
              </button>
              <button class="modal-close-btn" @click="closeFullscreenModal">
                返回
              </button>
            </div>
          </div>
          
          <!-- 调整大小手柄 -->
          <div v-if="!isModalMaximized" class="resize-handle resize-n" @mousedown="startResize('n', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-s" @mousedown="startResize('s', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-e" @mousedown="startResize('e', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-w" @mousedown="startResize('w', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-ne" @mousedown="startResize('ne', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-nw" @mousedown="startResize('nw', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-se" @mousedown="startResize('se', $event)"></div>
          <div v-if="!isModalMaximized" class="resize-handle resize-sw" @mousedown="startResize('sw', $event)"></div>
        </div>
        <div class="modal-backdrop" @click="closeFullscreenModal"></div>
      </div>
    </Teleport>

    <div class="background-effects">
      <div class="effect-blob effect-top"></div>
      <div class="effect-blob effect-bottom"></div>
    </div>

    <!-- 产品数据库弹窗 -->
    <ProductDatabaseModal :is-open="isProductDatabaseModalOpen" @close="closeProductDatabaseModal" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, shallowRef, nextTick, watch } from 'vue'
import { useRouter, onBeforeRouteLeave } from 'vue-router'
import * as XLSX from 'xlsx'
import { ElMessage } from 'element-plus'
import axios from 'axios'
import BranchPageHeader from '../components/BranchPageHeader.vue'
import ProductDatabaseModal from '../components/ProductDatabaseModal.vue'
import OnsiteServiceCalculator from '../components/pricing/OnsiteServiceCalculator.vue'
import RelocationServiceCalculator from '../components/pricing/RelocationServiceCalculator.vue'
import {
  PAGE_STATE_KEYS,
  FLOW_DATA_KEYS,
  savePageState,
  restorePageState,
  clearPageState,
  saveFlowData,
  clearFlowData,
  createNavigateWithState,
  createJumpNavigate,
  type DocumentRecognitionState
} from '../stores/quotationStore'
import {
  saveDraft,
  getCurrentDraftId,
  clearCurrentDraftId
} from '../utils/draftUtils'
import { useProductCategories, type ProductCategory } from '../stores/productCategoryStore'
import { getStorageKeyPrefix } from '../stores/authStore'

const router = useRouter()

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// UI State
const isUploadSectionCollapsed = ref(false)
const currentFileName = ref('')
const currentFileBase64 = ref('')  // 当前文件的base64数据，用于导出时保留原格式
const isSavingDraft = ref(false)

// 文档解析状态
const isParsingDocument = ref(false)
const parsingMessage = ref('正在解析文件...')

// 使用共享的产品分类 store（响应式，自动同步）
const { categories: productCategories } = useProductCategories()

// 报价类型选择
const selectedQuotationType = ref('维保服务报价')

// 产品数据库弹窗
const isProductDatabaseModalOpen = ref(false)

const openProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = true
}

const closeProductDatabaseModal = () => {
  isProductDatabaseModalOpen.value = false
}

onMounted(() => {
  loadRecentUploads()
  restorePageStateOnMount()
  window.addEventListener('keydown', handleKeyDown)
  // 如果是维保服务报价且没有数据，初始化手动输入表格
  if (selectedQuotationType.value === '维保服务报价' && originalTableData.value.length === 0 && convertedTableData.value.length === 0) {
    initManualEntryTable(5)
  }
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
})

// 全屏模态框状态
const isFullscreenModalOpen = ref(false)
const isModalMaximized = ref(false)
const modalRef = ref<HTMLElement | null>(null)
const modalPosition = ref({ x: 100, y: 50 })
const modalSize = ref({ width: 1200, height: 700 })
const isDragging = ref(false)
const isResizing = ref(false)
const resizeDirection = ref('')
const dragStart = ref({ x: 0, y: 0 })

// Data
// 使用 shallowRef 优化大数据量性能，只追踪数组引用变化而不追踪内部对象
const originalTableData = shallowRef<any[]>([])
const originalHeaders = ref<string[]>([])
const convertedTableData = shallowRef<any[]>([])

// Multi-sheet support
const workbookRef = ref<any>(null)  // Store the workbook object
const sheetNames = ref<string[]>([])  // All sheet names
const currentSheetName = ref<string>('')  // Currently selected sheet

// 非 Excel 文件解析结果缓存（用于多表格切换）
const parsedDocumentSheets = ref<Record<string, { headers: string[]; data: Record<string, any>[] }>>({})

// Column mapping state
const columnMappings = ref<Record<string, string>>({})  // 转换后表头 -> 原始表头的映射
const activeDropdownForColumn = ref<string | null>(null)  // 当前打开下拉框的列名

// Excel-like table state
const excelTableRef = ref<HTMLElement | null>(null)
const modalExcelTableRef = ref<HTMLElement | null>(null)
const editInputRef = ref<HTMLInputElement | null>(null)
const selectedCells = ref<Set<string>>(new Set())  // 格式: "rowIndex-colIndex"
const selectionStart = ref<{ row: number; col: number } | null>(null)
const selectionEnd = ref<{ row: number; col: number } | null>(null)
const isSelecting = ref(false)
const editingCell = ref<{ row: number; col: number } | null>(null)
const copiedCells = ref<{ data: string[][]; startRow: number; startCol: number } | null>(null)
const isFillDragging = ref(false)
const fillStartCell = ref<{ row: number; col: number } | null>(null)
const fillEndCell = ref<{ row: number; col: number } | null>(null)

// 撤销/重做历史记录
const historyStack = ref<any[][]>([])  // 历史记录栈
const historyIndex = ref(-1)  // 当前历史记录索引
const initialTableData = ref<any[]>([])  // 初始表格数据（用于重置）
const maxHistorySize = 50  // 最大历史记录数

// Recent uploads history
interface UploadRecord {
  id: string
  fileName: string
  fileData: string // Base64 encoded file data
  rowCount: number
  timestamp: number
}

const recentUploads = ref<UploadRecord[]>([])
const RECENT_UPLOADS_KEY = 'recentUploads'
const MAX_RECENT_UPLOADS = 3

// Load recent uploads from localStorage on mount
// (已在统一onMounted中处理)

// 键盘快捷键和外部点击处理已在统一onMounted/onUnmounted中处理

// Restore page state from sessionStorage
function restorePageStateOnMount() {
  const savedState = restorePageState<DocumentRecognitionState>(PAGE_STATE_KEYS.DOC_RECOGNITION)
  if (savedState && savedState.hasData) {
    // Restore all state
    originalTableData.value = savedState.originalTableData || []
    originalHeaders.value = savedState.originalHeaders || []
    convertedTableData.value = savedState.convertedTableData || []
    currentFileName.value = savedState.currentFileName || ''  // 恢复源文件名
    isUploadSectionCollapsed.value = savedState.isUploadSectionCollapsed || false
    // 恢复列映射状态
    columnMappings.value = savedState.columnMappings || {}
    // 恢复报价类型选择
    selectedQuotationType.value = savedState.selectedQuotationType || ''
  }
}

// Get current state for saving
function getCurrentState(): DocumentRecognitionState {
  return {
    originalTableData: originalTableData.value,
    originalHeaders: originalHeaders.value,
    convertedTableData: convertedTableData.value,
    convertedHeaders: [], // Will be computed
    currentFileName: currentFileName.value,
    visibleColumns: [],
    isUploadSectionCollapsed: isUploadSectionCollapsed.value,
    columnMappings: columnMappings.value,
    selectedQuotationType: selectedQuotationType.value,
    hasData: convertedTableData.value.length > 0
  }
}

// Automatically save state when leaving this page (for breadcrumb navigation restore)
onBeforeRouteLeave((to, from, next) => {
  // Always save state when leaving, so breadcrumb navigation can restore it
  if (convertedTableData.value.length > 0) {
    savePageState(PAGE_STATE_KEYS.DOC_RECOGNITION, getCurrentState())
    // Also save to flow data
    saveFlowData(FLOW_DATA_KEYS.CONVERTED_DATA, convertedTableData.value)
  }
  next()
})

function loadRecentUploads() {
  try {
    const key = getStorageKeyPrefix() + RECENT_UPLOADS_KEY
    const stored = localStorage.getItem(key)
    if (stored) {
      recentUploads.value = JSON.parse(stored)
    }
  } catch (error) {
    console.error('Failed to load recent uploads:', error)
    recentUploads.value = []
  }
}

function saveRecentUploads() {
  try {
    const key = getStorageKeyPrefix() + RECENT_UPLOADS_KEY
    localStorage.setItem(key, JSON.stringify(recentUploads.value))
  } catch (error) {
    console.error('Failed to save recent uploads:', error)
  }
}

function addToRecentUploads(fileName: string, fileData: string, rowCount: number) {
  const newRecord: UploadRecord = {
    id: Date.now().toString(),
    fileName,
    fileData,
    rowCount,
    timestamp: Date.now()
  }

  // Remove existing record with same file name
  recentUploads.value = recentUploads.value.filter(r => r.fileName !== fileName)

  // Add new record at the beginning
  recentUploads.value.unshift(newRecord)

  // Keep only MAX_RECENT_UPLOADS records
  if (recentUploads.value.length > MAX_RECENT_UPLOADS) {
    recentUploads.value = recentUploads.value.slice(0, MAX_RECENT_UPLOADS)
  }

  saveRecentUploads()
}

function deleteRecentUpload(id: string, event?: Event) {
  if (event) {
    event.stopPropagation()
  }
  recentUploads.value = recentUploads.value.filter(r => r.id !== id)
  saveRecentUploads()
}

function formatTimestamp(timestamp: number): string {
  const now = Date.now()
  const diff = now - timestamp

  const minutes = Math.floor(diff / 60000)
  const hours = Math.floor(diff / 3600000)
  const days = Math.floor(diff / 86400000)

  if (minutes < 1) return '刚刚'
  if (minutes < 60) return `${minutes}分钟前`
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`

  const date = new Date(timestamp)
  return `${date.getMonth() + 1}/${date.getDate()}`
}

async function loadRecentUpload(record: UploadRecord) {
  try {
    // Decode base64 to binary
    const binaryString = atob(record.fileData)
    const bytes = new Uint8Array(binaryString.length)
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i)
    }

    const workbook = XLSX.read(bytes, { type: 'array' })

    if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
      throw new Error('Excel文件中没有找到工作表')
    }

    // Store workbook and sheet names for multi-sheet support
    workbookRef.value = workbook
    sheetNames.value = workbook.SheetNames
    currentFileName.value = record.fileName
    currentFileBase64.value = record.fileData  // 保存当前文件的base64数据

    // Load the first sheet by default
    const firstSheet = workbook.SheetNames[0]
    currentSheetName.value = firstSheet
    loadSheetData(firstSheet)

  } catch (error) {
    console.error('Failed to load recent upload:', error)
    alert('加载文件失败: ' + (error as Error).message)
  }
}

// ---- 各报价类型的"转换后表格"标准表头配置 ----
interface QuotationTypeColumnConfig {
  targetHeaders: string[]
  visibleColumns: string[]
  manualEntryFieldMap: Record<string, { label: string; required: boolean }>
  fieldMappings: Record<string, string[]>
  defaults: Record<string, string>
}

const QUOTATION_TYPE_COLUMNS: Record<string, QuotationTypeColumnConfig> = {
  '维保服务报价': {
    targetHeaders: [
      "序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息",
      "设备数量", "城市", "机房地址", "服务级别", "服务周期",
      "服务周期单位", "服务范围", "单价", "备注", "设备原值单价",
      "特殊需求", "易损件类型", "耗材包数量"
    ],
    visibleColumns: [
      "序号", "厂商", "设备/软件型号", "设备/软件分类", "配置信息",
      "设备数量", "城市", "机房地址", "服务级别", "服务周期",
      "服务周期单位", "服务范围", "单价", "备注"
    ],
    manualEntryFieldMap: {
      '序号': { label: '自动生成', required: false },
      '厂商': { label: '设备品牌*', required: true },
      '设备/软件型号': { label: '设备型号*', required: true },
      '设备/软件分类': { label: '设备类型*', required: true },
      '配置信息': { label: '设备配置*', required: true },
      '设备数量': { label: '数量*', required: true },
      '城市': { label: '城市', required: false },
      '机房地址': { label: '机房地址', required: false },
      '服务级别': { label: '服务级别', required: false },
      '服务周期': { label: '服务周期', required: false },
      '服务周期单位': { label: '单位', required: false },
      '服务范围': { label: '服务范围', required: false },
      '单价': { label: '单价', required: false },
      '备注': { label: '备注', required: false },
    },
    fieldMappings: {
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
      '耗材包数量': ['耗材数量', '耗材包数量', '耗材包', 'consumable count'],
    },
    defaults: { '设备数量': '1', '服务周期': '1', '服务周期单位': '年', '服务范围': '维保服务', '服务级别': '7*24*NCR' },
  },
  'IT服务支持报价（单价框架 / 据实结算）': {
    targetHeaders: [
      "序号", "服务项", "服务内容描述", "工程师类型", "工程师能力级别",
      "服务地点", "服务模式", "数量", "单位"
    ],
    visibleColumns: [
      "序号", "服务项", "服务内容描述", "工程师类型", "工程师能力级别",
      "服务地点", "服务模式", "数量", "单位"
    ],
    manualEntryFieldMap: {
      '序号': { label: '自动生成', required: false },
      '服务项': { label: '服务项*', required: true },
      '服务内容描述': { label: '服务描述*', required: true },
      '工程师类型': { label: '工程师类型', required: false },
      '工程师能力级别': { label: '能力级别', required: false },
      '服务地点': { label: '服务地点', required: false },
      '服务模式': { label: '服务模式', required: false },
      '数量': { label: '数量*', required: true },
      '单位': { label: '单位', required: false },
    },
    fieldMappings: {
      '服务项': ['服务项', '服务项目', '服务名称', '项目名称', '项目', 'service item', 'service name'],
      '服务内容描述': ['服务内容描述', '服务内容', '服务描述', '内容描述', '描述', 'service description', 'description'],
      '工程师类型': ['工程师类型', '人员类型', '工程师', '技术人员类型', 'engineer type'],
      '工程师能力级别': ['工程师能力级别', '能力级别', '技能级别', '级别', '工程师级别', 'skill level', 'engineer level'],
      '服务地点': ['服务地点', '地点', '工作地点', '服务地址', '现场地址', 'service location', 'location'],
      '服务模式': ['服务模式', '服务方式', '模式', '响应方式', 'service mode'],
      '数量': ['数量', '人数', '台数', '次数', 'quantity', 'count', 'number'],
      '单位': ['单位', '计量单位', 'unit'],
    },
    defaults: { '数量': '1', '单位': '人天' },
  },
  '设备/备件采购报价': {
    targetHeaders: [
      "序号", "厂商", "设备/软件型号", "设备/软件类型", "产品配置信息",
      "产品成色", "数量", "单位", "保修方式", "质保周期", "到货时间", "到货地点"
    ],
    visibleColumns: [
      "序号", "厂商", "设备/软件型号", "设备/软件类型", "产品配置信息",
      "产品成色", "数量", "单位", "保修方式", "质保周期", "到货时间", "到货地点"
    ],
    manualEntryFieldMap: {
      '序号': { label: '自动生成', required: false },
      '厂商': { label: '厂商*', required: true },
      '设备/软件型号': { label: '型号*', required: true },
      '设备/软件类型': { label: '类型*', required: true },
      '产品配置信息': { label: '配置信息', required: false },
      '产品成色': { label: '成色', required: false },
      '数量': { label: '数量*', required: true },
      '单位': { label: '单位', required: false },
      '保修方式': { label: '保修方式', required: false },
      '质保周期': { label: '质保周期', required: false },
      '到货时间': { label: '到货时间', required: false },
      '到货地点': { label: '到货地点*', required: true },
    },
    fieldMappings: {
      '厂商': ['厂商', '厂商品牌', '品牌', '制造商', '生产商', 'manufacturer', 'vendor', 'brand'],
      '设备/软件型号': ['设备型号', '软件型号', '设备/软件型号', '型号', '产品型号', '产品名称', '设备名称', 'model', 'product model', 'part number', 'pn'],
      '设备/软件类型': ['设备类型', '软件类型', '设备/软件类型', '类型', '分类', '产品类型', '类别', 'type', 'category'],
      '产品配置信息': ['产品配置信息', '配置信息', '配置', '产品配置', '规格', '参数', '详细配置', 'configuration', 'spec'],
      '产品成色': ['产品成色', '成色', '新旧', '新旧程度', '品相', 'condition'],
      '数量': ['数量', '台数', '套数', '件数', '采购数量', 'quantity', 'qty', 'count'],
      '单位': ['单位', '计量单位', 'unit'],
      '保修方式': ['保修方式', '保修', '质保方式', '保修类型', 'warranty type', 'warranty'],
      '质保周期': ['质保周期', '质保期', '保修期', '保修周期', '质保时间', 'warranty period'],
      '到货时间': ['到货时间', '交货时间', '交期', '到货日期', '交货日期', '交付时间', 'delivery time', 'lead time'],
      '到货地点': ['到货地点', '交货地点', '收货地址', '交货地址', '送货地址', '目的地', 'delivery location', 'destination'],
    },
    defaults: { '数量': '1', '单位': '台' },
  },
}

// 默认配置（维保服务报价）
const DEFAULT_COLUMN_CONFIG = QUOTATION_TYPE_COLUMNS['维保服务报价']

// 获取当前报价类型的列配置
function getColumnConfig(): QuotationTypeColumnConfig {
  return QUOTATION_TYPE_COLUMNS[selectedQuotationType.value] || DEFAULT_COLUMN_CONFIG
}

const targetHeaders = ref([...DEFAULT_COLUMN_CONFIG.targetHeaders])
const visibleColumns = ref([...DEFAULT_COLUMN_CONFIG.visibleColumns])

// 是否为驻场服务报价模式（直接嵌入驻场服务测算组件）
const isOnsiteMode = computed(() => {
  return selectedQuotationType.value === '驻场服务报价'
})

// 是否为搬迁服务报价模式（直接嵌入搬迁服务测算组件）
const isRelocationMode = computed(() => {
  return selectedQuotationType.value === '搬迁服务报价'
})

// 搬迁服务组件引用
const relocationCalcRef = ref<InstanceType<typeof RelocationServiceCalculator> | null>(null)

// 是否为嵌入式模式（驻场或搬迁）
const isEmbeddedMode = computed(() => isOnsiteMode.value || isRelocationMode.value)

// 是否显示手动输入模式（有标准表头配置的报价类型 且 无导入数据时）
const showManualEntryMode = computed(() => {
  return !!QUOTATION_TYPE_COLUMNS[selectedQuotationType.value] && originalTableData.value.length === 0
})

// 是否显示转换后表格（有数据或手动输入模式）
const showConvertedTable = computed(() => {
  return originalTableData.value.length > 0 || (showManualEntryMode.value && convertedTableData.value.length > 0)
})

// 创建空行用于手动输入
function createEmptyRow(): Record<string, string> {
  const row: Record<string, string> = {}
  visibleColumns.value.forEach(col => {
    row[col] = ''
  })
  return row
}

// 初始化手动输入表格（添加默认空行）
function initManualEntryTable(rowCount: number = 5) {
  convertedTableData.value = []
  for (let i = 0; i < rowCount; i++) {
    convertedTableData.value.push(createEmptyRow())
  }
  // 初始化历史记录
  initialTableData.value = JSON.parse(JSON.stringify(convertedTableData.value))
  historyStack.value = [JSON.parse(JSON.stringify(convertedTableData.value))]
  historyIndex.value = 0
}

// 添加新行
function addManualRow() {
  saveToHistory()
  convertedTableData.value = [...convertedTableData.value, createEmptyRow()]
}

// 手动输入模式的必填字段映射（根据报价类型动态获取）
const manualEntryFieldMap = computed<Record<string, { label: string; required: boolean }>>(() => {
  return getColumnConfig().manualEntryFieldMap
})

// 判断是否为必填字段
function isRequiredField(header: string): boolean {
  return manualEntryFieldMap.value[header]?.required || false
}

// 获取手动输入模式下的字段标签
function getManualEntryFieldLabel(header: string): string {
  return manualEntryFieldMap.value[header]?.label || header
}

// 获取占位符文本
function getPlaceholderText(header: string): string {
  if (header === '序号') return ''
  const field = manualEntryFieldMap.value[header]
  if (field?.required) return '请输入...'
  return '可选'
}

// 监听报价类型变化，更新列配置并初始化手动输入表格
watch(selectedQuotationType, (newVal) => {
  // 更新列配置
  const config = getColumnConfig()
  targetHeaders.value = [...config.targetHeaders]
  visibleColumns.value = [...config.visibleColumns]

  // 有标准表头配置的类型且无导入数据时，自动初始化手动输入表格
  if (QUOTATION_TYPE_COLUMNS[newVal] && originalTableData.value.length === 0) {
    initManualEntryTable(5)
  }
})

// Toggle upload section
const toggleUploadSection = () => {
  isUploadSectionCollapsed.value = !isUploadSectionCollapsed.value
}

// 步骤标签：根据报价类型动态切换
const stepLabels = computed(() => {
  if (isRelocationMode.value) {
    return ['项目概况', '设备清单管理', '费用测算配置', '生成报价']
  }
  return ['导入数据', '智能匹配', '价格调整', '生成报价']
})

// 步骤点击处理
function onStepClick(step: number) {
  if (isRelocationMode.value) {
    // 搬迁模式：步骤1-3切换搬迁组件的标签页，步骤4打开报价单
    if (step <= 3) {
      if (relocationCalcRef.value) {
        relocationCalcRef.value.activeTab = step
      }
    } else {
      relocationCalcRef.value?.onGenerateQuote()
    }
    return
  }
  // 默认模式：跳转到对应页面
  if (step === 1) navigateToDocumentRecognition()
  else if (step === 2) navigateToSmartMatching()
  else if (step === 3) navigateToPriceAdjustment()
  else if (step === 4) navigateToQuotationGeneration()
}

// Navigation functions

// 面包屑导航：跳转到页面（不保存状态，由目标页面恢复自己的状态）
const navigateToHome = () => {
  router.push('/')
}

const navigateToDocumentRecognition = () => {
  // 当前页面，无需跳转
}

const navigateToSmartMatching = () => {
  // 面包屑跳转：直接跳转，由SmartMatching页面恢复自己的状态
  router.push('/smart-matching')
}

const navigateToPriceAdjustment = () => {
  // 面包屑跳转：直接跳转
  router.push('/price-adjustment')
}

const navigateToQuotationGeneration = () => {
  // 面包屑跳转：直接跳转
  router.push('/quotation-generation')
}

// 流程推进：保存当前状态并进入下一步（由"下一步"按钮调用）
const goToSmartMatching = () => {
  // 保存当前页面状态
  savePageState(PAGE_STATE_KEYS.DOC_RECOGNITION, getCurrentState())
  // 保存流程数据供下一页面使用
  if (convertedTableData.value.length > 0) {
    saveFlowData(FLOW_DATA_KEYS.CONVERTED_DATA, convertedTableData.value)
  }
  // 保存原始表格数据（用于导出Excel）- 包含表头和数据
  if (originalTableData.value.length > 0) {
    saveFlowData(FLOW_DATA_KEYS.ORIGINAL_TABLE_DATA, {
      headers: originalHeaders.value,
      data: originalTableData.value
    })
  }
  // 保存转换后表格数据（用于导出Excel）- 包含表头和数据
  if (convertedTableData.value.length > 0) {
    saveFlowData(FLOW_DATA_KEYS.CONVERTED_TABLE_DATA, {
      headers: visibleColumns.value,
      data: convertedTableData.value
    })
  }
  // 保存原始Excel文件数据（用于导出时保留原格式）
  if (currentFileBase64.value) {
    saveFlowData(FLOW_DATA_KEYS.ORIGINAL_EXCEL_FILE, currentFileBase64.value)
    saveFlowData(FLOW_DATA_KEYS.SELECTED_SHEET_NAME, currentSheetName.value)
    saveFlowData(FLOW_DATA_KEYS.ORIGINAL_FILE_NAME, currentFileName.value)
  }
  // 设置触发匹配标志，并清除SmartMatching的页面状态
  saveFlowData(FLOW_DATA_KEYS.TRIGGER_MATCHING, true)
  clearPageState(PAGE_STATE_KEYS.SMART_MATCHING)
  // 清除后续流程的旧数据
  clearFlowData(FLOW_DATA_KEYS.MATCHED_DATA)
  clearFlowData(FLOW_DATA_KEYS.ADJUSTED_DATA)
  clearFlowData(FLOW_DATA_KEYS.FINAL_DATA)
  router.push('/smart-matching')
}

// 存为草稿
async function saveAsDraft() {
  if (convertedTableData.value.length === 0) {
    ElMessage.warning('请先上传并处理数据后再保存草稿')
    return
  }

  isSavingDraft.value = true
  try {
    // 保存当前状态
    savePageState(PAGE_STATE_KEYS.DOC_RECOGNITION, getCurrentState())
    saveFlowData(FLOW_DATA_KEYS.CONVERTED_DATA, convertedTableData.value)
    saveFlowData(FLOW_DATA_KEYS.ORIGINAL_TABLE_DATA, {
      headers: originalHeaders.value,
      data: originalTableData.value
    })
    saveFlowData(FLOW_DATA_KEYS.CONVERTED_TABLE_DATA, {
      headers: visibleColumns.value,
      data: convertedTableData.value
    })

    // 获取当前草稿ID（如果有）
    const existingDraftId = getCurrentDraftId()

    // 保存草稿
    await saveDraft('doc_recognition', existingDraftId ?? undefined)

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

// Trigger file input
const triggerFileInput = () => {
  document.getElementById('convert-file-input')?.click()
}

// 支持的文件类型正则
const EXCEL_PATTERN = /\.(xlsx|xls)$/i
const SUPPORTED_FILE_PATTERN = /\.(xlsx|xls|docx|pdf|png|jpg|jpeg|bmp|tiff|tif|webp)$/i

// Handle file change
function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return

  // Check file type
  if (!file.name.match(SUPPORTED_FILE_PATTERN)) {
    ElMessage.error('不支持的文件格式。支持：Excel (.xlsx/.xls)、Word (.docx)、PDF、图片 (.png/.jpg)')
    return
  }

  currentFileName.value = file.name

  // Clear previous data
  originalTableData.value = []
  originalHeaders.value = []
  convertedTableData.value = []
  workbookRef.value = null
  sheetNames.value = []
  currentSheetName.value = ''

  // 根据文件类型选择不同的解析路径
  if (file.name.match(EXCEL_PATTERN)) {
    // Excel 文件：前端直接解析（保持原有逻辑）
    handleExcelFile(file)
  } else {
    // 非 Excel 文件：调用后端 /document/parse API 解析
    handleNonExcelFile(file)
  }
}

// Excel 文件前端解析（原有逻辑）
function handleExcelFile(file: File) {
  const reader = new FileReader()
  reader.onload = (e) => {
    try {
      const data = new Uint8Array(e.target?.result as ArrayBuffer)
      const workbook = XLSX.read(data, { type: 'array' })

      if (!workbook.SheetNames || workbook.SheetNames.length === 0) {
        throw new Error('Excel文件中没有找到工作表')
      }

      // Store workbook and sheet names for multi-sheet support
      workbookRef.value = workbook
      sheetNames.value = workbook.SheetNames

      // Load the first sheet by default
      const firstSheet = workbook.SheetNames[0]
      currentSheetName.value = firstSheet
      loadSheetData(firstSheet)

      // Convert file data to base64 and save to recent uploads
      const binaryString = Array.from(data, byte => String.fromCharCode(byte)).join('')
      const base64Data = btoa(binaryString)
      currentFileBase64.value = base64Data  // 保存当前文件的base64数据
      addToRecentUploads(file.name, base64Data, originalTableData.value.length)

    } catch (error) {
      console.error('Error reading Excel file:', error)
      ElMessage.error('读取Excel文件失败: ' + (error as Error).message)
    }
  }
  reader.readAsArrayBuffer(file)
}

// 非 Excel 文件后端解析（Word、PDF、图片）
async function handleNonExcelFile(file: File) {
  const fileTypeMap: Record<string, string> = {
    '.docx': 'Word 文档',
    '.pdf': 'PDF 文档',
    '.png': '图片', '.jpg': '图片', '.jpeg': '图片',
    '.bmp': '图片', '.tiff': '图片', '.tif': '图片', '.webp': '图片',
  }
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  const friendlyType = fileTypeMap[ext] || '文档'

  isParsingDocument.value = true
  parsingMessage.value = `正在解析${friendlyType}，请稍候...`

  try {
    const formData = new FormData()
    formData.append('file', file)

    const response = await axios.post(`${API_URL}/document/parse`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 120000, // 2 分钟超时（OCR 可能较慢）
    })

    const result = response.data
    if (!result.success || !result.sheets || result.sheets.length === 0) {
      throw new Error(result.message || '文件解析未返回有效数据')
    }

    // 将后端返回的 sheets 适配为前端所需格式
    const sheets = result.sheets as Array<{ name: string; headers: string[]; data: Record<string, any>[] }>

    // 设置 sheet 名称列表（多表格时允许切换）
    sheetNames.value = sheets.map(s => s.name)
    currentSheetName.value = sheets[0].name

    // 将解析结果存储到一个临时 Map 中，供 switchSheet 使用
    parsedDocumentSheets.value = {}
    for (const sheet of sheets) {
      parsedDocumentSheets.value[sheet.name] = {
        headers: sheet.headers,
        data: sheet.data,
      }
    }

    // 加载第一个表格的数据
    loadParsedSheetData(sheets[0].name)

    // 非 Excel 文件不保存 base64（无需保留原格式导出）
    currentFileBase64.value = ''

    ElMessage.success(result.message || `成功从${friendlyType}中提取了 ${sheets.reduce((sum: number, s: any) => sum + s.data.length, 0)} 行数据`)

    // 尝试使用 LLM 进行字段标准化（异步，不阻塞主流程）
    if (sheets.length > 0 && sheets[0].data.length > 0) {
      tryLLMStandardize(sheets[0].name, sheets[0].headers, sheets[0].data)
    }

  } catch (error: any) {
    console.error('文档解析失败:', error)
    const msg = error.response?.data?.detail || error.message || '文件解析失败'
    ElMessage.error(msg)
  } finally {
    isParsingDocument.value = false
  }
}

// LLM 字段标准化（后台异步，不阻塞用户操作）
async function tryLLMStandardize(sheetName: string, headers: string[], data: Record<string, any>[]) {
  try {
    const response = await axios.post(`${API_URL}/document/standardize`, {
      headers,
      data,
    }, { timeout: 120000 })

    const result = response.data
    if (result.success && result.standardized_headers && result.standardized_data) {
      // 更新缓存中的数据
      parsedDocumentSheets.value[sheetName] = {
        headers: result.standardized_headers,
        data: result.standardized_data,
      }
      // 如果当前正在查看这个表格，则刷新显示
      if (currentSheetName.value === sheetName) {
        loadParsedSheetData(sheetName)
      }
      ElMessage.success(result.message || '字段标准化完成')
    }
  } catch (err) {
    // LLM 标准化是可选增强，失败不影响主流程
    console.log('LLM 字段标准化跳过（LLM 服务可能不可用）:', err)
  }
}

// Load data from a specific sheet
function loadSheetData(sheetName: string) {
  if (!workbookRef.value) return

  const worksheet = workbookRef.value.Sheets[sheetName]

  if (!worksheet || !worksheet['!ref']) {
    originalHeaders.value = []
    originalTableData.value = []
    convertedTableData.value = []
    return
  }

  const range = XLSX.utils.decode_range(worksheet['!ref'])

  // Get headers
  const headers: string[] = []
  for (let c = range.s.c; c <= range.e.c; c++) {
    const cellAddress = XLSX.utils.encode_cell({ r: range.s.r, c })
    const cell = worksheet[cellAddress]
    let headerName = `列${c + 1}`
    if (cell && cell.v !== undefined && cell.v !== null) {
      headerName = String(cell.v)
    }
    headers.push(headerName)
  }

  // Parse data
  const jsonData: any[] = []
  for (let r = range.s.r + 1; r <= range.e.r; r++) {
    const row: any = {}
    let hasData = false

    for (let c = range.s.c; c <= range.e.c; c++) {
      const cellAddress = XLSX.utils.encode_cell({ r, c })
      const cell = worksheet[cellAddress]
      const headerName = headers[c - range.s.c]
      let cellValue = ''

      if (cell && cell.v !== undefined && cell.v !== null) {
        cellValue = String(cell.v)
        hasData = true
      }

      row[headerName] = cellValue
    }

    if (hasData) {
      jsonData.push(row)
    }
  }

  originalHeaders.value = headers
  originalTableData.value = jsonData

  // Convert data
  convertData(jsonData, headers)
}

// 加载从后端解析的文档表格数据（Word / PDF / 图片）
function loadParsedSheetData(sheetName: string) {
  const sheet = parsedDocumentSheets.value[sheetName]
  if (!sheet) {
    originalHeaders.value = []
    originalTableData.value = []
    convertedTableData.value = []
    return
  }

  originalHeaders.value = sheet.headers
  originalTableData.value = sheet.data

  // 复用已有的字段转换逻辑
  convertData(sheet.data, sheet.headers)
}

// Switch to a different sheet
function switchSheet(sheetName: string) {
  if (sheetName === currentSheetName.value) return
  currentSheetName.value = sheetName

  // 判断是 Excel 工作表还是后端解析的文档表格
  if (parsedDocumentSheets.value[sheetName]) {
    loadParsedSheetData(sheetName)
  } else {
    loadSheetData(sheetName)
  }
}

// Convert data function
function convertData(jsonData: any[], headers: string[]) {
  const config = getColumnConfig()
  const fieldMappings = config.fieldMappings

  const foundMappings: Record<string, string> = {}

  // Find mappings
  for (const [targetField, possibleFields] of Object.entries(fieldMappings)) {
    for (const originalHeader of headers) {
      const normalizedHeader = String(originalHeader).trim().toLowerCase()

      for (const possibleField of possibleFields) {
        if (normalizedHeader.includes(possibleField.toLowerCase())) {
          foundMappings[targetField] = originalHeader
          break
        }
      }

      if (foundMappings[targetField]) {
        break
      }
    }
  }

  // 保存自动识别的映射关系
  columnMappings.value = { ...foundMappings }

  // Generate converted data
  convertedTableData.value = jsonData.map((row, index) => {
    const convertedRow: any = {}

    targetHeaders.value.forEach(header => {
      convertedRow[header] = ''
    })

    // Apply mappings first
    for (const [targetHeader, sourceHeader] of Object.entries(foundMappings)) {
      if (row[sourceHeader] !== undefined) {
        convertedRow[targetHeader] = row[sourceHeader].toString()
      }
    }

    // Set 序号
    convertedRow['序号'] = String(index + 1)

    // Apply type-specific defaults
    for (const [field, defaultVal] of Object.entries(config.defaults)) {
      convertedRow[field] = convertedRow[field] || defaultVal
    }

    return convertedRow
  })

  // Final verification: ensure all 序号 are correctly sequential
  convertedTableData.value.forEach((row, index) => {
    row['序号'] = String(index + 1)
  })

  // 保存初始状态，用于重置功能
  saveInitialState()
}

// 根据映射关系重新生成转换后数据
// changedColumn: 手动修改映射的列名，只更新这一列的数据
function remapDataUsingMappings(changedColumn?: string) {
  if (originalTableData.value.length === 0) return

  // 如果是初次转换（没有指定变化的列），则生成完整数据
  if (!changedColumn) {
    convertedTableData.value = originalTableData.value.map((row, index) => {
      const convertedRow: any = {}

      // 初始化所有列为空
      targetHeaders.value.forEach(header => {
        convertedRow[header] = ''
      })

      // 应用手动选择的映射关系
      for (const [targetHeader, sourceHeader] of Object.entries(columnMappings.value)) {
        if (row[sourceHeader] !== undefined && row[sourceHeader] !== '') {
          convertedRow[targetHeader] = row[sourceHeader].toString()
        }
      }

      // 设置默认值
      convertedRow['序号'] = String(index + 1)
      const config = getColumnConfig()
      for (const [field, defaultVal] of Object.entries(config.defaults)) {
        convertedRow[field] = convertedRow[field] || defaultVal
      }

      return convertedRow
    })
  } else {
    // 只更新指定列的数据，保留其他列的现有数据
    const sourceHeader = columnMappings.value[changedColumn]
    if (sourceHeader) {
      convertedTableData.value.forEach((row, index) => {
        const originalRow = originalTableData.value[index]
        if (originalRow && originalRow[sourceHeader] !== undefined) {
          row[changedColumn] = originalRow[sourceHeader].toString()
        } else {
          row[changedColumn] = ''
        }
      })
    } else {
      // 清除了映射，将该列设为空值或默认值
      convertedTableData.value.forEach((row) => {
        if (changedColumn === '设备数量') {
          row[changedColumn] = row[changedColumn] || '1'
        } else if (changedColumn === '服务周期') {
          row[changedColumn] = row[changedColumn] || '1'
        } else if (changedColumn === '服务周期单位') {
          row[changedColumn] = row[changedColumn] || '年'
        } else if (changedColumn === '服务范围') {
          row[changedColumn] = row[changedColumn] || '维保服务'
        } else if (changedColumn === '服务级别') {
          row[changedColumn] = row[changedColumn] || '7*24*NCR'
        } else if (changedColumn !== '序号') {
          row[changedColumn] = ''
        }
      })
    }
  }
}

// 处理表头点击，显示/隐藏下拉框
function toggleHeaderDropdown(headerName: string, event: Event) {
  event.preventDefault()
  event.stopPropagation()

  // 如果点击的是当前已打开的列，则关闭
  if (activeDropdownForColumn.value === headerName) {
    activeDropdownForColumn.value = null
  } else {
    // 否则打开新的下拉框
    activeDropdownForColumn.value = headerName
  }
}

// 选择原始表头进行映射
function selectOriginalHeader(targetHeader: string, originalHeader: string) {
  columnMappings.value[targetHeader] = originalHeader
  activeDropdownForColumn.value = null
  // 只更新当前列的数据，保留其他列
  remapDataUsingMappings(targetHeader)
}

// 清除映射
function clearMapping(targetHeader: string) {
  delete columnMappings.value[targetHeader]
  activeDropdownForColumn.value = null
  // 只更新当前列的数据，保留其他列
  remapDataUsingMappings(targetHeader)
}

// 获取当前列映射的原始表头名称（用于显示）
function getMappedOriginalHeader(targetHeader: string): string {
  return columnMappings.value[targetHeader] || '未映射'
}

// 点击外部关闭下拉框
function handleClickOutside() {
  activeDropdownForColumn.value = null
}

// ========== Excel-like Table Functions ==========

// 获取单元格类名
const getCellClass = (row: number, col: number) => {
  const cellKey = `${row}-${col}`
  const classes: string[] = ['excel-cell']
  
  if (selectedCells.value.has(cellKey)) {
    classes.push('selected')
  }
  if (isEditing(row, col)) {
    classes.push('editing')
  }
  if (isCellInSelection(row, col)) {
    classes.push('in-selection')
  }
  if (isFillDragging.value && isCellInFillRange(row, col)) {
    classes.push('fill-preview-cell')
  }
  return classes.join(' ')
}

// 弹窗中单元格类名
const getModalCellClass = (row: number, col: number) => {
  const cellKey = `${row}-${col}`
  const classes: string[] = ['modal-excel-cell']
  
  if (selectedCells.value.has(cellKey)) {
    classes.push('selected')
  }
  if (isEditing(row, col)) {
    classes.push('editing')
  }
  if (isCellInSelection(row, col)) {
    classes.push('in-selection')
  }
  if (isFillDragging.value && isCellInFillRange(row, col)) {
    classes.push('fill-preview-cell')
  }
  return classes.join(' ')
}

// 检查单元格是否在选择范围内
const isCellInSelection = (row: number, col: number) => {
  if (!selectionStart.value || !selectionEnd.value) return false
  const minRow = Math.min(selectionStart.value.row, selectionEnd.value.row)
  const maxRow = Math.max(selectionStart.value.row, selectionEnd.value.row)
  const minCol = Math.min(selectionStart.value.col, selectionEnd.value.col)
  const maxCol = Math.max(selectionStart.value.col, selectionEnd.value.col)
  return row >= minRow && row <= maxRow && col >= minCol && col <= maxCol
}

// 检查单元格是否在填充范围内
const isCellInFillRange = (row: number, col: number) => {
  if (!fillStartCell.value || !fillEndCell.value) return false
  const minRow = Math.min(fillStartCell.value.row, fillEndCell.value.row)
  const maxRow = Math.max(fillStartCell.value.row, fillEndCell.value.row)
  const minCol = Math.min(fillStartCell.value.col, fillEndCell.value.col)
  const maxCol = Math.max(fillStartCell.value.col, fillEndCell.value.col)
  return row >= minRow && row <= maxRow && col >= minCol && col <= maxCol
}

// 检查是否是当前编辑的单元格
const isEditing = (row: number, col: number) => {
  return editingCell.value?.row === row && editingCell.value?.col === col
}

// 检查是否是填充手柄所在的单元格（选区的右下角）
const isFillHandleCell = (row: number, col: number) => {
  if (selectedCells.value.size === 0 || editingCell.value) return false
  // 序号列不显示填充手柄
  if (visibleColumns.value[col] === '序号') return false
  
  if (selectionStart.value && selectionEnd.value) {
    const maxRow = Math.max(selectionStart.value.row, selectionEnd.value.row)
    const maxCol = Math.max(selectionStart.value.col, selectionEnd.value.col)
    return row === maxRow && col === maxCol
  }
  return false
}

// 处理单元格鼠标按下
const handleCellMouseDown = (row: number, col: number, event: MouseEvent) => {
  // 序号列不可选择
  if (visibleColumns.value[col] === '序号') return
  
  // 如果点击的是正在编辑的单元格，允许正常的输入框操作（移动光标等）
  if (isEditing(row, col)) {
    // 不阻止事件，让输入框正常处理点击
    return
  }
  
  // 点击其他单元格时，先结束当前编辑
  if (editingCell.value) {
    endCellEdit()
  }
  
  if (event.shiftKey && selectionStart.value) {
    // Shift+点击 扩展选区
    selectionEnd.value = { row, col }
    updateSelectedCells()
  } else {
    // 普通点击 开始新选区
    selectionStart.value = { row, col }
    selectionEnd.value = { row, col }
    isSelecting.value = true
    updateSelectedCells()
  }
}

// 处理单元格鼠标进入（拖选）
const handleCellMouseEnter = (row: number, col: number) => {
  if (isSelecting.value && selectionStart.value) {
    selectionEnd.value = { row, col }
    updateSelectedCells()
  }
  if (isFillDragging.value) {
    fillEndCell.value = { row, col }
  }
}

// 处理表格鼠标按下
const handleTableMouseDown = (event: MouseEvent) => {
  // 点击表格空白区域时清除选择
  if ((event.target as HTMLElement).classList.contains('excel-table-wrapper')) {
    clearSelection()
  }
}

// 处理表格鼠标移动
const handleTableMouseMove = (event: MouseEvent) => {
  // 可以添加更多的拖选逻辑
}

// 处理表格鼠标松开
const handleTableMouseUp = () => {
  if (isSelecting.value) {
    isSelecting.value = false
  }
  if (isFillDragging.value) {
    applyFill()
    isFillDragging.value = false
    fillStartCell.value = null
    fillEndCell.value = null
  }
}

// 处理键盘事件
const handleTableKeyDown = (event: KeyboardEvent) => {
  // Ctrl+Z 撤销
  if ((event.ctrlKey || event.metaKey) && event.key === 'z' && !event.shiftKey) {
    event.preventDefault()
    undo()
  }
  // Ctrl+Y 或 Ctrl+Shift+Z 重做
  if ((event.ctrlKey || event.metaKey) && (event.key === 'y' || (event.key === 'z' && event.shiftKey))) {
    event.preventDefault()
    redo()
  }
  // Ctrl+C 复制
  if ((event.ctrlKey || event.metaKey) && event.key === 'c') {
    event.preventDefault()
    copySelectedCells()
  }
  // Ctrl+V 粘贴
  if ((event.ctrlKey || event.metaKey) && event.key === 'v') {
    event.preventDefault()
    pasteFromClipboard()
  }
  // Delete/Backspace 清空
  if (event.key === 'Delete' || event.key === 'Backspace') {
    if (!editingCell.value) {
      event.preventDefault()
      clearSelectedCells()
    }
  }
  // 方向键移动
  if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(event.key)) {
    if (!editingCell.value) {
      event.preventDefault()
      moveSelection(event.key, event.shiftKey)
    }
  }
  // Enter 开始编辑或移动到下一行
  if (event.key === 'Enter' && !editingCell.value) {
    event.preventDefault()
    if (selectionStart.value) {
      startCellEdit(selectionStart.value.row, selectionStart.value.col)
    }
  }
  // F2 开始编辑
  if (event.key === 'F2' && !editingCell.value && selectionStart.value) {
    event.preventDefault()
    startCellEdit(selectionStart.value.row, selectionStart.value.col)
  }
}

// 更新选中单元格集合
const updateSelectedCells = () => {
  selectedCells.value.clear()
  if (!selectionStart.value || !selectionEnd.value) return
  
  const minRow = Math.min(selectionStart.value.row, selectionEnd.value.row)
  const maxRow = Math.max(selectionStart.value.row, selectionEnd.value.row)
  const minCol = Math.min(selectionStart.value.col, selectionEnd.value.col)
  const maxCol = Math.max(selectionStart.value.col, selectionEnd.value.col)
  
  for (let r = minRow; r <= maxRow; r++) {
    for (let c = minCol; c <= maxCol; c++) {
      // 跳过序号列
      if (visibleColumns.value[c] !== '序号') {
        selectedCells.value.add(`${r}-${c}`)
      }
    }
  }
}

// 清除选择
const clearSelection = () => {
  selectedCells.value.clear()
  selectionStart.value = null
  selectionEnd.value = null
}

// 开始编辑单元格
const startCellEdit = (row: number, col: number) => {
  // 序号列不可编辑
  if (visibleColumns.value[col] === '序号') return
  editingCell.value = { row, col }
  // 聚焦输入框（同时支持主表格和全屏模态框）
  setTimeout(() => {
    // 先查找全屏模态框中的输入框
    let inputs = document.querySelectorAll('.modal-table-input.modal-editing')
    // 如果没找到，查找主表格中的输入框
    if (inputs.length === 0) {
      inputs = document.querySelectorAll('.table-input.editing')
    }
    if (inputs.length > 0) {
      (inputs[0] as HTMLInputElement).focus()
      ;(inputs[0] as HTMLInputElement).select()
    }
  }, 10)
}

// 结束编辑
const endCellEdit = () => {
  if (editingCell.value) {
    // 结束编辑时，防抖保存历史记录
    debouncedSaveHistory()
  }
  editingCell.value = null
}

// 移动到下一个单元格
const moveToNextCell = () => {
  if (!editingCell.value) return
  const { row, col } = editingCell.value
  endCellEdit()
  
  // 移动到右边单元格，如果是最后一列则移动到下一行第一个可编辑列
  let nextCol = col + 1
  let nextRow = row
  
  // 跳过序号列
  while (nextCol < visibleColumns.value.length && visibleColumns.value[nextCol] === '序号') {
    nextCol++
  }
  
  if (nextCol >= visibleColumns.value.length) {
    nextRow++
    nextCol = 0
    while (nextCol < visibleColumns.value.length && visibleColumns.value[nextCol] === '序号') {
      nextCol++
    }
  }
  
  if (nextRow < convertedTableData.value.length) {
    selectionStart.value = { row: nextRow, col: nextCol }
    selectionEnd.value = { row: nextRow, col: nextCol }
    updateSelectedCells()
    startCellEdit(nextRow, nextCol)
  }
}

// 移动选区
const moveSelection = (direction: string, extend: boolean) => {
  if (!selectionStart.value) return
  
  let newRow = selectionEnd.value?.row ?? selectionStart.value.row
  let newCol = selectionEnd.value?.col ?? selectionStart.value.col
  
  switch (direction) {
    case 'ArrowUp': newRow = Math.max(0, newRow - 1); break
    case 'ArrowDown': newRow = Math.min(convertedTableData.value.length - 1, newRow + 1); break
    case 'ArrowLeft': newCol = Math.max(0, newCol - 1); break
    case 'ArrowRight': newCol = Math.min(visibleColumns.value.length - 1, newCol + 1); break
  }
  
  // 跳过序号列
  while (visibleColumns.value[newCol] === '序号' && newCol < visibleColumns.value.length - 1) {
    newCol++
  }
  
  if (extend) {
    selectionEnd.value = { row: newRow, col: newCol }
  } else {
    selectionStart.value = { row: newRow, col: newCol }
    selectionEnd.value = { row: newRow, col: newCol }
  }
  updateSelectedCells()
}

// 复制选中单元格
const copySelectedCells = () => {
  if (!selectionStart.value || !selectionEnd.value) return
  
  const minRow = Math.min(selectionStart.value.row, selectionEnd.value.row)
  const maxRow = Math.max(selectionStart.value.row, selectionEnd.value.row)
  const minCol = Math.min(selectionStart.value.col, selectionEnd.value.col)
  const maxCol = Math.max(selectionStart.value.col, selectionEnd.value.col)
  
  const data: string[][] = []
  for (let r = minRow; r <= maxRow; r++) {
    const rowData: string[] = []
    for (let c = minCol; c <= maxCol; c++) {
      const header = visibleColumns.value[c]
      rowData.push(convertedTableData.value[r][header] || '')
    }
    data.push(rowData)
  }
  
  copiedCells.value = { data, startRow: minRow, startCol: minCol }
  
  // 同时复制到系统剪贴板
  const text = data.map(row => row.join('\t')).join('\n')
  navigator.clipboard.writeText(text).catch(() => {
    // 静默失败
  })
}

// 从剪贴板粘贴
const pasteFromClipboard = async () => {
  if (!selectionStart.value) return
  
  let hasChanges = false
  try {
    const text = await navigator.clipboard.readText()
    if (!text) return
    
    const rows = text.split('\n').map(row => row.split('\t'))
    const startRow = selectionStart.value.row
    const startCol = selectionStart.value.col
    
    rows.forEach((rowData, rowOffset) => {
      const targetRow = startRow + rowOffset
      if (targetRow >= convertedTableData.value.length) return
      
      rowData.forEach((cellData, colOffset) => {
        const targetCol = startCol + colOffset
        if (targetCol >= visibleColumns.value.length) return
        const header = visibleColumns.value[targetCol]
        // 跳过序号列
        if (header === '序号') return
        convertedTableData.value[targetRow][header] = cellData
        hasChanges = true
      })
    })
  } catch {
    // 使用内部复制的数据
    if (copiedCells.value && selectionStart.value) {
      const { data } = copiedCells.value
      const startRow = selectionStart.value.row
      const startCol = selectionStart.value.col
      
      data.forEach((rowData, rowOffset) => {
        const targetRow = startRow + rowOffset
        if (targetRow >= convertedTableData.value.length) return
        
        rowData.forEach((cellData, colOffset) => {
          const targetCol = startCol + colOffset
          if (targetCol >= visibleColumns.value.length) return
          const header = visibleColumns.value[targetCol]
          if (header === '序号') return
          convertedTableData.value[targetRow][header] = cellData
          hasChanges = true
        })
      })
    }
  }
  
  // 保存到历史记录
  if (hasChanges) {
    saveToHistory()
  }
}

// 清空选中单元格
const clearSelectedCells = () => {
  if (!selectionStart.value || !selectionEnd.value) return
  
  const minRow = Math.min(selectionStart.value.row, selectionEnd.value.row)
  const maxRow = Math.max(selectionStart.value.row, selectionEnd.value.row)
  const minCol = Math.min(selectionStart.value.col, selectionEnd.value.col)
  const maxCol = Math.max(selectionStart.value.col, selectionEnd.value.col)
  
  for (let r = minRow; r <= maxRow; r++) {
    for (let c = minCol; c <= maxCol; c++) {
      const header = visibleColumns.value[c]
      if (header !== '序号') {
        convertedTableData.value[r][header] = ''
      }
    }
  }
  // 保存到历史记录
  saveToHistory()
}

// 开始填充拖拽
const startFillDrag = (row: number, col: number, event: MouseEvent) => {
  event.preventDefault()
  isFillDragging.value = true
  
  if (selectionStart.value && selectionEnd.value) {
    fillStartCell.value = {
      row: Math.min(selectionStart.value.row, selectionEnd.value.row),
      col: Math.min(selectionStart.value.col, selectionEnd.value.col)
    }
    fillEndCell.value = { row, col }
  }
}

// 应用填充
const applyFill = () => {
  if (!fillStartCell.value || !fillEndCell.value || !selectionStart.value || !selectionEnd.value) return
  
  const srcMinRow = Math.min(selectionStart.value.row, selectionEnd.value.row)
  const srcMaxRow = Math.max(selectionStart.value.row, selectionEnd.value.row)
  const srcMinCol = Math.min(selectionStart.value.col, selectionEnd.value.col)
  const srcMaxCol = Math.max(selectionStart.value.col, selectionEnd.value.col)
  
  const fillMinRow = Math.min(fillStartCell.value.row, fillEndCell.value.row)
  const fillMaxRow = Math.max(fillStartCell.value.row, fillEndCell.value.row)
  const fillMinCol = Math.min(fillStartCell.value.col, fillEndCell.value.col)
  const fillMaxCol = Math.max(fillStartCell.value.col, fillEndCell.value.col)
  
  // 获取源数据
  const srcData: string[][] = []
  for (let r = srcMinRow; r <= srcMaxRow; r++) {
    const rowData: string[] = []
    for (let c = srcMinCol; c <= srcMaxCol; c++) {
      const header = visibleColumns.value[c]
      rowData.push(convertedTableData.value[r][header] || '')
    }
    srcData.push(rowData)
  }
  
  // 填充到目标区域
  const srcRowCount = srcData.length
  const srcColCount = srcData[0]?.length || 0
  
  for (let r = fillMinRow; r <= fillMaxRow; r++) {
    for (let c = fillMinCol; c <= fillMaxCol; c++) {
      // 跳过源区域
      if (r >= srcMinRow && r <= srcMaxRow && c >= srcMinCol && c <= srcMaxCol) continue
      
      const header = visibleColumns.value[c]
      if (header === '序号') continue
      
      const srcRowIndex = (r - fillMinRow) % srcRowCount
      const srcColIndex = (c - fillMinCol) % srcColCount
      
      if (srcData[srcRowIndex] && srcData[srcRowIndex][srcColIndex] !== undefined) {
        convertedTableData.value[r][header] = srcData[srcRowIndex][srcColIndex]
      }
    }
  }
  
  // 更新选区到填充区域
  selectionStart.value = { row: fillMinRow, col: fillMinCol }
  selectionEnd.value = { row: fillMaxRow, col: fillMaxCol }
  updateSelectedCells()
  // 保存到历史记录
  saveToHistory()
}

// 选择框样式计算
const selectionBoxStyle = computed(() => {
  // 这里可以添加框选的视觉效果样式
  return {}
})

// 填充预览样式计算
const fillPreviewStyle = computed(() => {
  // 填充预览的视觉效果
  return {}
})

// ========== 撤销/重做/重置功能 ==========

// 保存初始状态（在首次识别数据后调用）- 使用 function 声明以便提升
function saveInitialState() {
  initialTableData.value = JSON.parse(JSON.stringify(convertedTableData.value))
  // 清空历史记录，保存当前状态作为第一个历史
  historyStack.value = [JSON.parse(JSON.stringify(convertedTableData.value))]
  historyIndex.value = 0
}

// 保存当前状态到历史记录 - 使用 function 声明以便提升
function saveToHistory() {
  // 如果当前不在历史记录末尾，删除后面的记录
  if (historyIndex.value < historyStack.value.length - 1) {
    historyStack.value = historyStack.value.slice(0, historyIndex.value + 1)
  }
  
  // 添加新状态
  const currentState = JSON.parse(JSON.stringify(convertedTableData.value))
  historyStack.value.push(currentState)
  
  // 限制历史记录数量
  if (historyStack.value.length > maxHistorySize) {
    historyStack.value.shift()
  } else {
    historyIndex.value++
  }
}

// 在数据变更时自动保存历史（防抖处理）- 使用 function 声明以便提升
let historyTimer: ReturnType<typeof setTimeout> | null = null
function debouncedSaveHistory() {
  if (historyTimer) clearTimeout(historyTimer)
  historyTimer = setTimeout(() => {
    saveToHistory()
  }, 500)
}

// 检查是否可以撤销
const canUndo = computed(() => historyIndex.value > 0)

// 检查是否可以重做
const canRedo = computed(() => historyIndex.value < historyStack.value.length - 1)

// 撤销
const undo = () => {
  if (!canUndo.value) return
  historyIndex.value--
  convertedTableData.value = JSON.parse(JSON.stringify(historyStack.value[historyIndex.value]))
}

// 重做
const redo = () => {
  if (!canRedo.value) return
  historyIndex.value++
  convertedTableData.value = JSON.parse(JSON.stringify(historyStack.value[historyIndex.value]))
}

// 重置到初始状态
const resetToInitial = () => {
  if (initialTableData.value.length === 0) {
    alert('没有可重置的初始数据')
    return
  }
  if (!confirm('确定要将表格重置到初始识别状态吗？所有修改将丢失。')) return
  
  convertedTableData.value = JSON.parse(JSON.stringify(initialTableData.value))
  saveToHistory()
}

// Delete row
const deleteRow = (index: number) => {
  if (confirm('确定要删除这条数据吗？')) {
    convertedTableData.value.splice(index, 1)
    // 重新排序序号
    renumberRows()
    // 保存到历史记录
    saveToHistory()
  }
}

// Renumber rows after deletion
const renumberRows = () => {
  convertedTableData.value.forEach((row, index) => {
    row['序号'] = (index + 1).toString()
  })
}

// 计算总数量
const totalQuantity = computed(() => {
  return convertedTableData.value.reduce((sum, row) => {
    const qty = parseInt(row['设备数量'] || row['数量'] || '0', 10)
    return sum + (isNaN(qty) ? 0 : qty)
  }, 0)
})

// 模态框样式
const modalStyle = computed(() => {
  if (isModalMaximized.value) {
    return {}
  }
  return {
    left: `${modalPosition.value.x}px`,
    top: `${modalPosition.value.y}px`,
    width: `${modalSize.value.width}px`,
    height: `${modalSize.value.height}px`
  }
})

// 打开全屏模态框
const openFullscreenModal = () => {
  isFullscreenModalOpen.value = true
  // 居中显示
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  modalPosition.value = {
    x: Math.max(50, (viewportWidth - modalSize.value.width) / 2),
    y: Math.max(30, (viewportHeight - modalSize.value.height) / 2)
  }
}

// 关闭全屏模态框
const closeFullscreenModal = () => {
  isFullscreenModalOpen.value = false
  isModalMaximized.value = false
}

// 切换最大化
const toggleMaximize = () => {
  isModalMaximized.value = !isModalMaximized.value
}

// 拖动功能
const startDrag = (e: MouseEvent) => {
  if (isModalMaximized.value || (e.target as HTMLElement).closest('.modal-actions')) return
  isDragging.value = true
  dragStart.value = {
    x: e.clientX - modalPosition.value.x,
    y: e.clientY - modalPosition.value.y
  }
  document.addEventListener('mousemove', onDrag)
  document.addEventListener('mouseup', stopDrag)
}

const onDrag = (e: MouseEvent) => {
  if (!isDragging.value) return
  modalPosition.value = {
    x: Math.max(0, Math.min(window.innerWidth - 100, e.clientX - dragStart.value.x)),
    y: Math.max(0, Math.min(window.innerHeight - 50, e.clientY - dragStart.value.y))
  }
}

const stopDrag = () => {
  isDragging.value = false
  document.removeEventListener('mousemove', onDrag)
  document.removeEventListener('mouseup', stopDrag)
}

// 调整大小功能
const startResize = (direction: string, e: MouseEvent) => {
  e.preventDefault()
  isResizing.value = true
  resizeDirection.value = direction
  dragStart.value = { x: e.clientX, y: e.clientY }
  document.addEventListener('mousemove', onResize)
  document.addEventListener('mouseup', stopResize)
}

const onResize = (e: MouseEvent) => {
  if (!isResizing.value) return
  const dx = e.clientX - dragStart.value.x
  const dy = e.clientY - dragStart.value.y
  const minWidth = 600
  const minHeight = 400
  
  if (resizeDirection.value.includes('e')) {
    modalSize.value.width = Math.max(minWidth, modalSize.value.width + dx)
  }
  if (resizeDirection.value.includes('w')) {
    const newWidth = Math.max(minWidth, modalSize.value.width - dx)
    if (newWidth !== modalSize.value.width) {
      modalPosition.value.x += modalSize.value.width - newWidth
      modalSize.value.width = newWidth
    }
  }
  if (resizeDirection.value.includes('s')) {
    modalSize.value.height = Math.max(minHeight, modalSize.value.height + dy)
  }
  if (resizeDirection.value.includes('n')) {
    const newHeight = Math.max(minHeight, modalSize.value.height - dy)
    if (newHeight !== modalSize.value.height) {
      modalPosition.value.y += modalSize.value.height - newHeight
      modalSize.value.height = newHeight
    }
  }
  
  dragStart.value = { x: e.clientX, y: e.clientY }
}

const stopResize = () => {
  isResizing.value = false
  document.removeEventListener('mousemove', onResize)
  document.removeEventListener('mouseup', stopResize)
}

// Reset data
const resetData = () => {
  if (confirm('确定要清空所有数据吗？')) {
    originalTableData.value = []
    originalHeaders.value = []
    convertedTableData.value = []
    currentFileName.value = ''
    currentFileBase64.value = ''  // 清除文件base64数据
    // Clear multi-sheet state
    workbookRef.value = null
    sheetNames.value = []
    currentSheetName.value = ''
  }
}

// Export converted data
const exportConvertedData = () => {
  if (convertedTableData.value.length === 0) {
    alert('没有数据可导出')
    return
  }

  const ws = XLSX.utils.json_to_sheet(convertedTableData.value)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '转换后数据')
  XLSX.writeFile(wb, '转换后数据.xlsx')
}

// Get total quantity
const getTotalQuantity = () => {
  return convertedTableData.value.reduce((sum, row) => {
    const qty = parseInt(row['设备数量'] || row['数量']) || 0
    return sum + qty
  }, 0)
}

// Get total amount
const getTotalAmount = () => {
  return convertedTableData.value.reduce((sum, row) => {
    const qty = parseInt(row['设备数量'] || row['数量']) || 1
    const price = parseFloat(row['单价']) || 0
    return sum + (qty * price)
  }, 0)
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+SC:wght@400;500;700;900&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
@import url('https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:wght,FILL@100..700,0..1&display=swap');

.document-recognition {
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

.header-right {
  display: flex;
  align-items: center;
  gap: 1.5rem;
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
  position: relative;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.375rem 0.5rem;
  border-radius: 0.5rem;
  cursor: pointer;
  transition: background-color 0.2s;
}

.user-info:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.user-details {
  display: none;
  flex-direction: column;
}

/* 用户下拉箭头 */
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

.user-avatar {
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 9999px;
  background-color: #1e293b;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='%2364748b'%3E%3Cpath d='M12 12c2.21 0 4-1.79 4-4s-1.79-4-4-4-4 1.79-4 4 1.79 4 4 4zm0 2c-2.67 0-8 1.34-8 4v2h16v-2c0-2.66-5.33-4-8-4z'/%3E%3C/svg%3E");
  background-size: 60%;
  background-position: center;
  background-repeat: no-repeat;
  box-shadow: 0 0 0 2px #232f48;
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
  overflow: hidden;
  max-height: calc(100vh - 72px);
}

/* Page Header */
.page-header {
  display: flex;
  flex-direction: column;
  gap: 1rem;
  margin-bottom: 0.5rem;
  flex-shrink: 0;
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

/* 标题行 - 包含标题和报价类型选择器 */
.title-row {
  display: flex;
  align-items: center;
  gap: 2rem;
  margin-top: 0.25rem;
}

/* 报价类型选择器 - 参考"价格调整"页面filter-select样式 */
.quotation-type-selector {
  position: relative;
  display: flex;
  align-items: center;
}

.quotation-type-selector .material-symbols-outlined {
  position: absolute;
  left: 0.75rem;
  color: #94a3b8;
  font-size: 1.25rem;
  pointer-events: none;
}

.quotation-type-dropdown {
  padding: 0.5rem 2rem 0.5rem 2.5rem;
  background-color: #101622;
  border: 1px solid #232f48;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  cursor: pointer;
  outline: none;
  appearance: none;
  min-width: 200px;
}

.quotation-type-dropdown:focus {
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.3);
}

.quotation-type-dropdown option {
  background-color: #101622;
  color: white;
  padding: 0.5rem;
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

.step-label {
  font-size: 0.875rem;
  font-weight: 500;
  white-space: nowrap;
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

/* Content Grid */
.content-grid {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
  margin-top: 0.5rem;
  align-items: stretch;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

/* 驻场服务嵌入模式：全宽显示 */
.content-grid.onsite-mode {
  display: flex;
  flex-direction: column;
}

.onsite-embed-section {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  border-radius: 12px;
  border: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(11, 17, 32, 0.6);
}

.upload-section {
  grid-column: span 3;
  display: flex;
  flex-direction: column;
  gap: 1rem;
  transition: all 0.3s ease;
  min-height: 0;
  overflow: hidden;
}

.upload-section.collapsed {
  grid-column: span 1;
}

.upload-section.collapsed .upload-card {
  min-width: 3rem;
  width: 3rem;
  padding: 0.5rem;
}

.upload-section.collapsed .card-title {
  display: none;
}

.preview-section {
  grid-column: span 9;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  min-height: 0;
  overflow: hidden;
}

.upload-section.collapsed + .preview-section {
  grid-column: span 11;
}

/* Upload Card */
.upload-card {
  background-color: #1e232f;
  border-radius: 0.75rem;
  border: 1px solid #2a3447;
  padding: 1.5rem;
  display: flex;
  flex-direction: column;
  flex: 1;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 0;
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 1rem;
  gap: 0.5rem;
  flex-shrink: 0;
}

.upload-section.collapsed .card-header {
  margin-bottom: 0;
  justify-content: center;
}

/* Upload Content - scrollable area */
.upload-content {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.collapse-btn {
  position: absolute;
  right: 0.5rem;
  top: 0.5rem;
  background: rgba(19, 91, 236, 0.1);
  border: none;
  color: #135bec;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
}

.collapse-btn:hover {
  background-color: rgba(19, 91, 236, 0.2);
}

.upload-section.collapsed .collapse-btn {
  right: 0.5rem;
  top: 0.5rem;
}

.collapse-btn .material-symbols-outlined {
  font-size: 1.25rem;
  transition: transform 0.3s ease;
}

.collapse-btn .material-symbols-outlined.rotated {
  transform: rotate(180deg);
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: white;
}

/* Upload Zone */
.upload-zone {
  border: 2px dashed #2a3447;
  border-radius: 0.5rem;
  background-color: #151a23;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  flex: 0 0 auto;
  min-height: 160px;
}

.upload-zone:hover {
  border-color: #135bec;
}

.upload-icon-wrapper {
  width: 3rem;
  height: 3rem;
  border-radius: 9999px;
  background-color: rgba(19, 91, 236, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 1rem;
  transition: transform 0.3s;
}

.upload-zone:hover .upload-icon-wrapper {
  transform: scale(1.1);
}

.upload-icon-wrapper .material-symbols-outlined {
  font-size: 1.5rem;
  color: #135bec;
}

.upload-title {
  color: white;
  font-weight: 700;
  font-size: 1rem;
  margin-bottom: 0.5rem;
}

.upload-subtitle {
  color: #92a4c9;
  font-size: 0.875rem;
}

/* 文档解析加载状态 */
.parsing-overlay {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 2rem 1rem;
  background: rgba(19, 91, 236, 0.04);
  border: 1px dashed rgba(19, 91, 236, 0.3);
  border-radius: 0.75rem;
  margin-top: 0.75rem;
}

.parsing-spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(19, 91, 236, 0.15);
  border-top-color: #135bec;
  border-radius: 50%;
  animation: parsing-spin 0.8s linear infinite;
}

@keyframes parsing-spin {
  to { transform: rotate(360deg); }
}

.parsing-text {
  margin-top: 0.75rem;
  color: #5b7bb8;
  font-size: 0.875rem;
}

/* Sheet Selector for multi-sheet Excel files */
.sheet-selector {
  margin-top: 1rem;
  padding: 0.75rem;
  background: rgba(19, 91, 236, 0.05);
  border: 1px solid rgba(19, 91, 236, 0.2);
  border-radius: 0.5rem;
}

.sheet-selector-title {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.75rem;
  font-weight: 700;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
}

.sheet-selector-title .material-symbols-outlined {
  font-size: 1rem;
  color: #135bec;
}

.sheet-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 0.375rem;
}

.sheet-tab {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.625rem;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(51, 65, 85, 0.5);
  border-radius: 0.375rem;
  color: #94a3b8;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
  max-width: 140px;
}

.sheet-tab:hover {
  background: rgba(30, 41, 59, 0.8);
  border-color: rgba(51, 65, 85, 0.8);
  color: #e2e8f0;
}

.sheet-tab.active {
  background: #135bec;
  border-color: #135bec;
  color: white;
}

.sheet-tab-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 80px;
}

.sheet-tab-rows {
  font-size: 0.625rem;
  opacity: 0.8;
  white-space: nowrap;
}

/* Recent Uploads */
.recent-uploads {
  margin-top: 1rem;
  flex: 1;
  min-height: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.recent-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.75rem;
  flex-shrink: 0;
}

.upload-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  overflow-y: auto;
  overflow-x: hidden;
  flex: 1;
  min-height: 0;
  padding-right: 4px;
}

/* Enable scroll on hover */
.upload-list:hover {
  overflow-y: auto;
}

.upload-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  border: 1px solid transparent;
  transition: all 0.2s;
  cursor: pointer;
  opacity: 0.6;
}

.upload-item.active {
  background-color: #151a23;
  border-color: rgba(19, 91, 236, 0.5);
  opacity: 1;
}

.upload-item:hover {
  background-color: #151a23;
  border-color: #2a3447;
}

.file-icon {
  width: 2rem;
  height: 2rem;
  border-radius: 0.25rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.file-icon.excel {
  background-color: rgba(34, 197, 94, 0.1);
  color: #22c55e;
}

.file-icon .material-symbols-outlined {
  font-size: 1.125rem;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: white;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-meta {
  font-size: 0.75rem;
  color: #6b7280;
}

.file-action {
  opacity: 0;
  transition: opacity 0.2s;
}

.upload-item:hover .file-action {
  opacity: 1;
}

.upload-item.active .file-action {
  opacity: 1;
}

.action-btn {
  color: #9ca3af;
  background: transparent;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
}

.action-btn:hover {
  color: #ef4444;
}

/* Preview Card */
.preview-card {
  background-color: #1e232f;
  border-radius: 0.75rem;
  border: 1px solid #2a3447;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2);
  display: flex;
  flex-direction: column;
  height: 100%;
  min-height: 0;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 4rem 2rem;
  color: #6b7280;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.empty-title {
  font-size: 1.125rem;
  font-weight: 500;
  color: #9ca3af;
  margin-bottom: 0.5rem;
}

.empty-subtitle {
  font-size: 0.875rem;
  color: #6b7280;
}

/* 手动输入模式样式 */
.manual-entry-hint {
  font-size: 0.75rem;
  color: #6b7280;
  margin-left: 0.5rem;
  padding: 0.25rem 0.5rem;
  background-color: rgba(59, 130, 246, 0.1);
  border-radius: 0.25rem;
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.manual-entry-view {
  flex: 1;
  overflow: auto;
  padding: 1rem;
  min-height: 0;
}

.manual-entry-table {
  width: 100%;
}

.manual-entry-field {
  font-size: 0.7rem;
  color: #6b7280;
}

.manual-entry-field.required {
  color: #10b981;
}

.table-cell-text.placeholder {
  color: #4b5563;
  font-style: italic;
  font-size: 0.75rem;
}

.add-row-btn {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.375rem 0.75rem !important;
  background-color: rgba(59, 130, 246, 0.1) !important;
  border: 1px solid rgba(59, 130, 246, 0.3) !important;
  color: #60a5fa !important;
  border-radius: 0.375rem;
  font-size: 0.75rem;
  cursor: pointer;
  transition: all 0.2s;
}

.add-row-btn:hover {
  background-color: rgba(59, 130, 246, 0.2) !important;
  border-color: rgba(59, 130, 246, 0.5) !important;
}

.add-row-btn .material-symbols-outlined {
  font-size: 1rem;
}

.preview-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #2a3447;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  background-color: rgba(21, 26, 35, 0.5);
  flex-shrink: 0;
}

.header-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.confidence-badge {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background-color: rgba(59, 130, 246, 0.1);
  border: 1px solid rgba(59, 130, 246, 0.2);
}

.pulse-dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 9999px;
  background-color: #3b82f6;
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

.badge-text {
  font-size: 0.75rem;
  font-weight: 700;
  color: #3b82f6;
  text-transform: uppercase;
}

.item-count {
  font-size: 0.875rem;
  color: #9ca3af;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.control-btn {
  padding: 0.5rem;
  color: #9ca3af;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
}

.control-btn:hover {
  color: #135bec;
  background-color: #2a3447;
}

.divider {
  width: 1px;
  height: 1.5rem;
  background-color: #2a3447;
  margin: 0 0.25rem;
}

.export-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.25rem;
  background-color: #2a3447;
  color: white;
  border: none;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: background-color 0.2s;
}

.export-btn:hover {
  background-color: #324467;
}

.export-btn .material-symbols-outlined {
  font-size: 1rem;
}

/* Split View */
.split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  padding: 1rem;
  flex: 1;
  min-height: 0;
  overflow: hidden;
}

.table-section {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
}

.table-title-with-count {
  font-size: 0.875rem;
  font-weight: 600;
  color: #92a4c9;
  margin-bottom: 0.75rem;
  flex-shrink: 0;
}

.table-count {
  font-size: 0.75rem;
  font-weight: 700;
  color: #135bec;
  background-color: rgba(19, 91, 236, 0.1);
  padding: 0.125rem 0.5rem;
  border-radius: 9999px;
  margin-left: 0.5rem;
}

/* Table Wrapper */
.table-wrapper {
  flex: 1;
  overflow: hidden;
  border: 1px solid #2a3447;
  border-radius: 0.5rem;
  background-color: #151a23;
  min-height: 0;
}

/* Enable scroll on hover for tables */
.table-wrapper:hover {
  overflow-y: auto;
  overflow-x: auto;
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
}

.data-table th {
  padding: 0.75rem 0.5rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid #2a3447;
  white-space: nowrap;
}

/* Column Mapping Table Header */
.column-mapping-th {
  padding: 0 !important;
  vertical-align: top;
}

.header-with-dropdown {
  padding: 0.5rem;
  cursor: pointer;
  user-select: none;
  position: relative;
  transition: background-color 0.2s;
  border-radius: 0.25rem;
}

.header-with-dropdown:hover {
  background-color: rgba(19, 91, 236, 0.1);
}

.header-label {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.25rem;
}

.header-name {
  font-weight: 600;
  color: #e2e8f0;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.dropdown-icon {
  font-size: 1rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.header-with-dropdown:hover .dropdown-icon {
  color: #135bec;
}

.mapped-source {
  display: block;
  font-size: 0.625rem;
  color: #6b7280;
  margin-top: 0.125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.mapped-source.mapped {
  color: #22c55e;
}

/* Column Mapping Dropdown */
.column-mapping-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  z-index: 100;
  min-width: 200px;
  max-width: 280px;
  background-color: #1e232f;
  border: 1px solid #2a3447;
  border-radius: 0.5rem;
  box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.4);
  overflow: hidden;
  margin-top: 0.25rem;
  animation: dropdownFadeIn 0.15s ease-out;
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
  justify-content: space-between;
  padding: 0.5rem 0.75rem;
  border-bottom: 1px solid #2a3447;
  background-color: rgba(21, 26, 35, 0.5);
}

.dropdown-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: #92a4c9;
}

.clear-mapping-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  color: #ef4444;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: all 0.2s;
}

.clear-mapping-btn:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

.clear-mapping-btn .material-symbols-outlined {
  font-size: 1rem;
}

.dropdown-options {
  max-height: 240px;
  overflow-y: auto;
  padding: 0.25rem;
}

.dropdown-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.75rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: background-color 0.2s;
  font-size: 0.75rem;
}

.dropdown-option:hover {
  background-color: rgba(19, 91, 236, 0.1);
}

.dropdown-option.selected {
  background-color: rgba(19, 91, 236, 0.15);
}

.dropdown-option.selected .option-icon {
  color: #22c55e;
}

.dropdown-option .option-icon {
  font-size: 1rem;
  color: #6b7280;
  flex-shrink: 0;
}

.dropdown-option.selected .option-icon {
  color: #22c55e;
}

.option-text {
  color: #e2e8f0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-empty {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.75rem;
}

.resizable-th {
  position: relative;
}

.data-table td {
  padding: 0.5rem;
  border-bottom: 1px solid rgba(42, 52, 71, 0.5);
}

.table-input {
  width: 100%;
  background: transparent;
  border: 1px solid transparent;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  transition: all 0.2s;
}

.table-cell-text {
  display: inline-block;
  width: 100%;
  color: #9ca3af;
  cursor: default;
  font-weight: 600;
  padding: 0.25rem 0.5rem;
  font-size: 0.75rem;
}

.table-input.readonly-input {
  color: #9ca3af;
  cursor: default;
  font-weight: 600;
}

.table-input:focus {
  border-color: #135bec;
  outline: none;
  background-color: rgba(19, 91, 236, 0.05);
}

.table-input.readonly-input:focus {
  border-color: transparent;
  background-color: transparent;
}

.data-table tbody tr:hover {
  background-color: rgba(19, 91, 236, 0.05);
}

/* ========== Excel-like Table Styles ========== */
.excel-table-section {
  position: relative;
}

.table-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
}

.excel-toolbar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: #1a2332;
  padding: 0.375rem 0.75rem;
  border-radius: 6px;
  border: 1px solid #2a3447;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.15s;
}

.toolbar-btn:hover:not(:disabled) {
  background: #374151;
  color: #e5e7eb;
}

.toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.toolbar-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.toolbar-btn.reset-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.toolbar-divider {
  width: 1px;
  height: 1.25rem;
  background: #374151;
  margin: 0 0.25rem;
}

.selection-info {
  font-size: 0.75rem;
  color: #6b7280;
  padding: 0 0.5rem;
}

.excel-table-wrapper {
  position: relative;
  outline: none;
}

.excel-table-wrapper:focus {
  outline: 2px solid rgba(19, 91, 236, 0.3);
  outline-offset: 2px;
}

.excel-data-table {
  user-select: none;
}

.excel-cell {
  position: relative;
  padding: 0 !important;
  cursor: cell;
  border: 1px solid transparent;
  transition: background-color 0.1s;
}

.excel-cell .cell-content {
  display: block;
  padding: 0.625rem 0.75rem;
  min-height: 1.25rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.excel-cell .table-cell-text {
  display: block;
  padding: 0.625rem 0.75rem;
  color: #6b7280;
  font-size: 0.8125rem;
}

.excel-cell.selected {
  background: rgba(19, 91, 236, 0.15) !important;
  border-color: #135bec;
}

.excel-cell.in-selection {
  background: rgba(19, 91, 236, 0.1) !important;
}

.excel-cell.editing {
  padding: 0 !important;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.3);
}

.excel-cell.fill-preview-cell {
  background: rgba(16, 185, 129, 0.15) !important;
  border-color: #10b981;
}

.excel-cell .table-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: none;
  background: #1a2332;
  color: #e5e7eb;
  font-size: 0.8125rem;
  outline: none;
}

.excel-cell .table-input.editing {
  background: #111827;
}

/* 填充手柄 */
.fill-handle {
  position: absolute;
  right: -3px;
  bottom: -3px;
  width: 8px;
  height: 8px;
  background: #135bec;
  border: 1px solid #1a2332;
  cursor: crosshair;
  z-index: 10;
}

.fill-handle:hover {
  background: #1d4ed8;
  transform: scale(1.2);
}

/* 选择覆盖层 */
.selection-overlay {
  position: absolute;
  border: 2px dashed #135bec;
  background: rgba(19, 91, 236, 0.05);
  pointer-events: none;
  z-index: 5;
}

/* 填充预览 */
.fill-preview {
  position: absolute;
  border: 2px dashed #10b981;
  background: rgba(16, 185, 129, 0.05);
  pointer-events: none;
  z-index: 5;
}

/* 操作列表头 */
.actions-header {
  width: 60px;
  text-align: center;
}

.actions-cell {
  text-align: center;
}

.action-btn {
  padding: 0.25rem;
  background: transparent;
  border: none;
  border-radius: 0.25rem;
  cursor: pointer;
  transition: all 0.2s;
  color: #9ca3af;
}

.action-btn:hover {
  color: #ef4444;
}

.action-btn.delete:hover {
  background-color: rgba(239, 68, 68, 0.1);
}

/* Table Footer */
.table-footer {
  padding: 0.75rem 1.5rem;
  border-top: 1px solid #2a3447;
  background-color: #151a23;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 1rem;
  flex-shrink: 0;
}

.footer-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  font-size: 0.875rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
}

.stat-label {
  color: #92a4c9;
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 700;
}

.stat-value {
  color: white;
  font-family: monospace;
  font-size: 1.125rem;
  font-weight: 700;
}

.stat-divider {
  width: 1px;
  height: 2rem;
  background-color: #2a3447;
}

.footer-action {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1.5rem;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.draft-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: transparent;
  color: #92a4c9;
  font-weight: 600;
  font-size: 0.875rem;
  border: 1px solid #3e4c6b;
  cursor: pointer;
  transition: all 0.2s;
}

.draft-btn:hover:not(:disabled) {
  background-color: #2d3b59;
  color: white;
  border-color: #4e5c7b;
}

.draft-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.draft-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

.draft-btn .material-symbols-outlined.spinning {
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

.total-amount {
  text-align: right;
}

.amount-label {
  color: #92a4c9;
  font-size: 0.75rem;
  text-transform: uppercase;
  font-weight: 700;
}

.amount-value {
  font-size: 1.5rem;
  font-weight: 900;
  color: #135bec;
  font-family: monospace;
}

.next-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1.25rem;
  height: 2.5rem;
  border-radius: 0.5rem;
  background-color: #135bec;
  color: white;
  font-weight: 700;
  font-size: 0.875rem;
  border: none;
  cursor: pointer;
  box-shadow: 0 10px 15px -3px rgba(19, 91, 236, 0.25);
  transition: background-color 0.2s;
}

.next-btn:hover {
  background-color: #1e40af;
}

.next-btn .material-symbols-outlined {
  font-size: 1.125rem;
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

/* Scrollbar Styles */
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

/* Responsive */
@media (max-width: 1024px) {
  .content-grid {
    grid-template-columns: 1fr;
  }

  .upload-section,
  .preview-section {
    grid-column: span 1;
  }

  .nav-links {
    display: none;
  }
}

/* 全屏模态框样式 */
.fullscreen-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  z-index: 9999;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.modal-container {
  position: absolute;
  display: flex;
  flex-direction: column;
  background: #1a2332;
  border-radius: 12px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
  border: 1px solid #2a3447;
  overflow: hidden;
  z-index: 1;
}

.fullscreen-modal.maximized .modal-container {
  position: fixed;
  top: 0 !important;
  left: 0 !important;
  width: 100% !important;
  height: 100% !important;
  border-radius: 0;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: #111827;
  border-bottom: 1px solid #2a3447;
  cursor: move;
  user-select: none;
}

.modal-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
}

.modal-title .material-symbols-outlined {
  color: #135bec;
  font-size: 1.5rem;
}

.modal-count {
  font-size: 0.875rem;
  font-weight: 400;
  color: #6b7280;
  margin-left: 0.5rem;
}

.modal-actions {
  display: flex;
  gap: 0.5rem;
}

.modal-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  border: none;
  border-radius: 6px;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-btn:hover {
  background: #374151;
  color: white;
}

.modal-btn.close-btn:hover {
  background: #ef4444;
  color: white;
}

.modal-content {
  flex: 1;
  padding: 1.5rem;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.modal-split-view {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
  flex: 1;
  min-height: 0;
}

.modal-table-section {
  display: flex;
  flex-direction: column;
  background: #111827;
  border-radius: 8px;
  border: 1px solid #2a3447;
  overflow: hidden;
}

.modal-table-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.875rem 1rem;
  margin: 0;
  font-size: 0.9375rem;
  font-weight: 600;
  color: white;
  background: #1a2332;
  border-bottom: 1px solid #2a3447;
}

.modal-table-count {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #10b981;
}

.modal-table-wrapper {
  flex: 1;
  overflow-x: auto;
  overflow-y: auto;
}

/* Excel 表格的 wrapper 需要允许下拉框显示 */
.modal-excel-wrapper.modal-table-wrapper {
  overflow-x: auto;
  overflow-y: auto;
  position: relative;
}

.modal-data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.modal-data-table th {
  position: sticky;
  top: 0;
  background: #1a2332;
  padding: 0.75rem 1rem;
  text-align: left;
  font-weight: 500;
  color: #9ca3af;
  border-bottom: 1px solid #2a3447;
  white-space: nowrap;
  z-index: 10;
}

.modal-data-table td {
  padding: 0.75rem 1rem;
  color: #e5e7eb;
  border-bottom: 1px solid #1f2937;
  white-space: nowrap;
}

.modal-data-table tbody tr:hover {
  background: rgba(19, 91, 236, 0.1);
}

.modal-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem 1.5rem;
  background: #111827;
  border-top: 1px solid #2a3447;
}

.modal-stats {
  display: flex;
  align-items: center;
  gap: 1.5rem;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.stat-label {
  font-size: 0.75rem;
  color: #6b7280;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: 700;
  color: white;
}

.stat-divider {
  width: 1px;
  height: 2.5rem;
  background: #374151;
}

.modal-footer-actions {
  display: flex;
  gap: 0.75rem;
}

.modal-export-btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  border: none;
  border-radius: 6px;
  background: #374151;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-export-btn:hover {
  background: #4b5563;
}

.modal-close-btn {
  padding: 0.625rem 1.25rem;
  border: none;
  border-radius: 6px;
  background: #135bec;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-close-btn:hover {
  background: #1d4ed8;
}

/* 调整大小手柄 */
.resize-handle {
  position: absolute;
  z-index: 10;
}

.resize-n, .resize-s {
  left: 10px;
  right: 10px;
  height: 6px;
  cursor: ns-resize;
}

.resize-n { top: 0; }
.resize-s { bottom: 0; }

.resize-e, .resize-w {
  top: 10px;
  bottom: 10px;
  width: 6px;
  cursor: ew-resize;
}

.resize-e { right: 0; }
.resize-w { left: 0; }

.resize-ne, .resize-nw, .resize-se, .resize-sw {
  width: 12px;
  height: 12px;
}

.resize-ne { top: 0; right: 0; cursor: nesw-resize; }
.resize-nw { top: 0; left: 0; cursor: nwse-resize; }
.resize-se { bottom: 0; right: 0; cursor: nwse-resize; }
.resize-sw { bottom: 0; left: 0; cursor: nesw-resize; }

/* 弹窗中转换后表格的列映射样式 */
.modal-column-mapping-th {
  position: relative;
  cursor: pointer;
  z-index: 50;
}

.modal-header-with-dropdown {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  position: relative;
  z-index: 50;
}

.modal-header-label {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.modal-header-name {
  font-weight: 500;
  color: #e5e7eb;
}

.modal-dropdown-icon {
  font-size: 1rem;
  color: #6b7280;
  transition: transform 0.2s;
}

.modal-column-mapping-th:hover .modal-dropdown-icon {
  color: #135bec;
}

.modal-mapped-source {
  font-size: 0.75rem;
  font-weight: 400;
  color: #6b7280;
}

.modal-mapped-source.mapped {
  color: #10b981;
}

.modal-column-mapping-dropdown {
  position: absolute;
  top: 100%;
  left: 0;
  min-width: 200px;
  background: #1f2937;
  border: 1px solid #374151;
  border-radius: 8px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.4);
  z-index: 1000;
  overflow: hidden;
}

.modal-dropdown-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid #374151;
  background: #111827;
}

.modal-dropdown-title {
  font-size: 0.8125rem;
  font-weight: 500;
  color: #9ca3af;
}

.modal-clear-mapping-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-clear-mapping-btn:hover {
  background: #374151;
  color: #ef4444;
}

.modal-dropdown-options {
  max-height: 200px;
  overflow-y: auto;
}

.modal-dropdown-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.625rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
}

.modal-dropdown-option:hover {
  background: #374151;
}

.modal-dropdown-option.selected {
  background: rgba(19, 91, 236, 0.2);
}

.modal-option-icon {
  font-size: 1.125rem;
  color: #6b7280;
}

.modal-dropdown-option.selected .modal-option-icon {
  color: #135bec;
}

.modal-option-text {
  font-size: 0.875rem;
  color: #e5e7eb;
}

.modal-dropdown-empty {
  padding: 1rem;
  text-align: center;
  color: #6b7280;
  font-size: 0.875rem;
}

/* 弹窗表格可编辑单元格 */
.modal-editable-cell {
  padding: 0 !important;
}

.modal-table-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  border: none;
  background: transparent;
  color: #e5e7eb;
  font-size: 0.8125rem;
  outline: none;
  transition: background 0.2s;
}

.modal-table-input:focus {
  background: rgba(19, 91, 236, 0.15);
}

.modal-cell-text {
  display: block;
  padding: 0.625rem 0.75rem;
  color: #e5e7eb;
  font-size: 0.8125rem;
}

/* 弹窗操作列 */
.modal-actions-th {
  width: 60px;
  text-align: center;
}

.modal-actions-cell {
  text-align: center;
  padding: 0.5rem !important;
}

.modal-action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 1.75rem;
  height: 1.75rem;
  border: none;
  border-radius: 4px;
  background: transparent;
  color: #6b7280;
  cursor: pointer;
  transition: all 0.2s;
}

.modal-action-btn:hover {
  background: #374151;
  color: #9ca3af;
}

.modal-action-btn.delete:hover {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.modal-action-btn .material-symbols-outlined {
  font-size: 1.125rem;
}

/* 弹窗转换表格样式调整 */
.modal-data-table.converted-table th {
  padding: 0.5rem 0.75rem;
}

/* ========== 弹窗 Excel 表格样式 ========== */
.modal-excel-section {
  display: flex;
  flex-direction: column;
}

.modal-section-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.875rem 1rem;
  margin: 0;
  background: #1a2332;
  border-bottom: 1px solid #2a3447;
}

.modal-section-header .modal-table-title {
  padding: 0;
  border-bottom: none;
  background: transparent;
}

.modal-excel-toolbar {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  background: #111827;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  border: 1px solid #374151;
}

.modal-toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.5rem;
  height: 1.5rem;
  border: none;
  border-radius: 3px;
  background: transparent;
  color: #9ca3af;
  cursor: pointer;
  transition: all 0.15s;
}

.modal-toolbar-btn:hover:not(:disabled) {
  background: #374151;
  color: #e5e7eb;
}

.modal-toolbar-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.modal-toolbar-btn .material-symbols-outlined {
  font-size: 1rem;
}

.modal-toolbar-btn.reset-btn:hover:not(:disabled) {
  background: rgba(239, 68, 68, 0.2);
  color: #ef4444;
}

.modal-toolbar-divider {
  width: 1px;
  height: 1rem;
  background: #374151;
  margin: 0 0.125rem;
}

.modal-selection-info {
  font-size: 0.6875rem;
  color: #6b7280;
  padding: 0 0.25rem;
  white-space: nowrap;
}

.modal-excel-wrapper {
  position: relative;
  outline: none;
}

.modal-excel-wrapper:focus {
  outline: 2px solid rgba(19, 91, 236, 0.3);
  outline-offset: -2px;
}

.modal-excel-table {
  user-select: none;
}

/* 弹窗 Excel 单元格 */
.modal-excel-cell {
  position: relative;
  padding: 0 !important;
  cursor: cell;
  border: 1px solid transparent;
  transition: background-color 0.1s;
}

.modal-excel-cell .modal-cell-content {
  display: block;
  padding: 0.5rem 0.75rem;
  min-height: 1rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  color: #e5e7eb;
  font-size: 0.8125rem;
}

.modal-excel-cell .modal-cell-text {
  display: block;
  padding: 0.5rem 0.75rem;
  color: #6b7280;
  font-size: 0.8125rem;
}

.modal-excel-cell.selected {
  background: rgba(19, 91, 236, 0.2) !important;
  border-color: #135bec;
}

.modal-excel-cell.in-selection {
  background: rgba(19, 91, 236, 0.1) !important;
}

.modal-excel-cell.editing {
  padding: 0 !important;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.3);
}

.modal-excel-cell.fill-preview-cell {
  background: rgba(16, 185, 129, 0.15) !important;
  border-color: #10b981;
}

.modal-excel-cell .modal-table-input {
  width: 100%;
  padding: 0.5rem 0.75rem;
  border: none;
  background: transparent;
  color: #e5e7eb;
  font-size: 0.8125rem;
  outline: none;
}

.modal-excel-cell .modal-table-input.modal-editing {
  background: #111827;
}

/* 弹窗填充手柄 */
.modal-fill-handle {
  position: absolute;
  right: -3px;
  bottom: -3px;
  width: 7px;
  height: 7px;
  background: #135bec;
  border: 1px solid #1a2332;
  cursor: crosshair;
  z-index: 10;
}

.modal-fill-handle:hover {
  background: #1d4ed8;
  transform: scale(1.2);
}

/* 模态框响应式 */
@media (max-width: 1024px) {
  .modal-split-view {
    grid-template-columns: 1fr;
  }
}
</style>
