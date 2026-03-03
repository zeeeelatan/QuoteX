<template>
  <div class="onsite-calculator-page">
    <!-- Header -->
    <div class="page-header">
      <div class="breadcrumb">
        <span class="breadcrumb-item">首页</span>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-item">报价工具</span>
        <span class="material-symbols-outlined breadcrumb-separator">chevron_right</span>
        <span class="breadcrumb-item active">驻场服务报价测算</span>
      </div>
      <div class="header-actions-row">
        <div>
          <h1 class="page-title">
            驻场服务报价工具
            <span class="ai-badge">AI 辅助模式开启</span>
          </h1>
          <p class="page-subtitle">基于城市、岗位、社保规则的多维度精细化成本分析模型</p>
        </div>
        <div class="header-buttons">
          <button class="header-btn" @click="showHistory">
            <span class="material-symbols-outlined">history</span>
            历史记录
          </button>
          <button class="header-btn" @click="resetForm">
            <span class="material-symbols-outlined">restart_alt</span>
            重置
          </button>
        </div>
      </div>
    </div>

    <!-- Main Content -->
    <div class="calculator-content">
      <!-- Left Column: Inputs & Config -->
      <div class="left-column">
        <!-- Section 1: Position Rows (多岗位小计) -->
        <div class="card">
          <div class="card-header">
            <span class="material-symbols-outlined card-icon">groups</span>
            <h3 class="card-title">岗位小计测算</h3>
            <button class="add-row-btn" @click="addPositionRow">
              <span class="material-symbols-outlined">add</span>
              叠加
            </button>
          </div>

          <!-- Table Header -->
          <div class="position-table-header">
            <div class="col-header col-seq">序号</div>
            <div class="col-header col-city">目标城市</div>
            <div class="col-header col-position">岗位职级</div>
            <div class="col-header col-salary">税前月薪</div>
            <div class="col-header">税后工资</div>
            <div class="col-header col-count">人员数量</div>
            <div class="col-header col-cycle">服务周期</div>
            <div class="col-header col-subtotal">金额小计</div>
            <div class="col-header col-action">操作</div>
          </div>

          <!-- Position Rows -->
          <div class="position-rows">
            <div v-for="(row, index) in positionRows" :key="row.id" class="position-row">
              <div class="col-seq">{{ index + 1 }}</div>
              <div class="col-city">
                <div class="autocomplete-wrapper">
                  <input
                    type="text"
                    class="row-input autocomplete-input"
                    :value="isDropdownOpen(row.id, 'city') ? getSearchQuery(row.id, 'city') : getCityDisplayValue(row)"
                    :title="getCityDisplayValue(row)"
                    @focus="onCityFocus(row, row.id, $event)"
                    @input="onCityInput(row, row.id, ($event.target as HTMLInputElement).value)"
                    @blur="onCityBlur(row, row.id)"
                    placeholder="请选择城市"
                  />
                  <Teleport to="body">
                    <div
                      v-show="isDropdownOpen(row.id, 'city')"
                      class="autocomplete-dropdown"
                      :style="getDropdownStyle(row.id, 'city')"
                    >
                      <div
                        v-for="city in getFilteredCities(row.id)"
                        :key="city.value"
                        class="autocomplete-item"
                        @mousedown.stop="selectCity(row.id, city.value, index)"
                      >
                        {{ city.label }}
                      </div>
                      <div v-if="getFilteredCities(row.id).length === 0" class="autocomplete-empty">
                        无匹配结果
                      </div>
                    </div>
                  </Teleport>
                </div>
              </div>
              <div class="col-position">
                <div class="autocomplete-wrapper">
                  <input
                    type="text"
                    class="row-input autocomplete-input"
                    :value="isDropdownOpen(row.id, 'position') ? getSearchQuery(row.id, 'position') : getPositionDisplayValue(row)"
                    :title="getPositionDisplayValue(row)"
                    @focus="onPositionFocus(row, row.id, $event)"
                    @input="onPositionInput(row, row.id, ($event.target as HTMLInputElement).value)"
                    @blur="onPositionBlur(row, row.id)"
                    placeholder="请选择岗位"
                  />
                  <Teleport to="body">
                    <div
                      v-show="isDropdownOpen(row.id, 'position')"
                      class="autocomplete-dropdown autocomplete-dropdown-wide"
                      :style="getDropdownStyle(row.id, 'position')"
                    >
                      <div
                        v-for="pos in getFilteredPositions(row.id)"
                        :key="pos.id"
                        class="autocomplete-item"
                        @mousedown.stop="selectPosition(row.id, pos.id, index)"
                      >
                        {{ pos.name }}
                      </div>
                      <div v-if="getFilteredPositions(row.id).length === 0" class="autocomplete-empty">
                        无匹配结果
                      </div>
                    </div>
                  </Teleport>
                </div>
              </div>
              <div class="col-salary">
                <div class="input-with-prefix">
                  <span class="input-prefix">¥</span>
                  <input v-model.number="row.salary" class="row-input" type="number" @input="onSalaryChange(index)" />
                </div>
              </div>
              <div class="col-salary">
                <div class="input-with-prefix">
                  <span class="input-prefix">¥</span>
                  <input v-model.number="row.afterTaxSalary" class="row-input" type="number" @input="onAfterTaxSalaryChange(index)" />
                </div>
              </div>
              <div class="col-count">
                <div class="input-with-suffix">
                  <input v-model.number="row.personnelCount" class="row-input" type="number" min="1" @input="calculateRow(index)" />
                  <span class="input-suffix">人</span>
                </div>
              </div>
              <div class="col-cycle">
                <div class="input-with-suffix">
                  <input v-model.number="row.serviceCycleCount" class="row-input" type="number" min="1" @input="calculateRow(index)" />
                  <select v-model="row.cycleUnit" class="cycle-unit-select" @change="calculateRow(index)">
                    <option value="month">月</option>
                    <option value="year">年</option>
                    <option value="day">天</option>
                  </select>
                </div>
              </div>
              <div class="col-subtotal">
                <span class="subtotal-value">{{ formatCurrency(row.subtotal) }}</span>
              </div>
              <div class="col-action">
                <button class="delete-btn" @click="removePositionRow(index)" :disabled="positionRows.length === 1">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </div>
            </div>
          </div>

          <!-- Total Subtotal -->
          <div class="total-subtotal">
            <span class="total-label">合计金额:</span>
            <span class="total-value">{{ formatCurrency(baseSubtotal) }}</span>
          </div>
        </div>

        <!-- Section 2: Other Cost Params -->
        <div class="card flex-cost-card">
          <div class="card-header flex-cost-header">
            <div class="header-left">
              <span class="material-symbols-outlined card-icon">tune</span>
              <h3 class="card-title">
                灵活人力成本（月度）
                <span class="card-title-amount">{{ formatCurrency(riskCostMonthly) }}</span>
              </h3>
            </div>
            <div class="header-right">
              <div class="global-mode-switch">
                <label class="switch-label">全局调整</label>
                <label class="switch">
                  <input type="checkbox" v-model="flexCostGlobalMode" />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="row-filter">
                <label class="filter-label">筛选岗位序号:</label>
                <select v-model="selectedFlexRowIndex" class="filter-select">
                  <option v-for="(row, index) in positionRows" :key="row.id" :value="index">
                    序号 {{ index + 1 }} - {{ row.city ? getCityName(row.city) : '请选择' }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <table class="mgmt-table">
            <thead>
              <tr>
                <th>科目</th>
                <th>税前月薪</th>
                <th>比例</th>
                <th>金额</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td class="mgmt-name-cell">风险金</td>
                <td class="mgmt-salary-cell">{{ formatCurrency(selectedFlexRowSalary) }}</td>
                <td class="mgmt-rate-cell">
                  <div class="rate-input-wrapper">
                    <input
                      v-model.number="selectedFlexRowRiskRatio"
                      class="rate-input"
                      type="number"
                      step="0.1"
                      min="0"
                    />
                    <span class="rate-symbol">%</span>
                  </div>
                </td>
                <td class="mgmt-amount-cell">{{ formatCurrency(selectedFlexRowRiskAmount) }}</td>
              </tr>
            </tbody>
            <tfoot>
              <tr class="mgmt-total-row">
                <td>灵活人力成本小计（当前岗位月度）</td>
                <td>-</td>
                <td>-</td>
                <td class="mgmt-total-amount">{{ formatCurrency(selectedFlexRowRiskAmount) }}</td>
              </tr>
              <tr class="mgmt-total-row">
                <td>灵活人力成本小计（全部岗位总计）</td>
                <td>-</td>
                <td>-</td>
                <td class="mgmt-total-amount">{{ formatCurrency(riskCostMonthly) }}</td>
              </tr>
            </tfoot>
          </table>
        </div>

        <!-- Section 3: Rules & Config -->
        <div class="card rules-card">
          <div class="card-header rules-header">
            <div class="header-left">
              <span class="material-symbols-outlined card-icon">tune</span>
              <h3 class="card-title">
                人力硬成本（月度）
                <span class="card-title-amount">{{ formatCurrency(hardCostMonthly) }}</span>
              </h3>
            </div>
            <div class="header-right">
              <div class="vertical-actions">
                <button class="add-row-btn" @click="resetAllHardCostToDefault">
                  <span class="material-symbols-outlined">restart_alt</span>
                  全部恢复默认
                </button>
                <div class="global-mode-switch">
                  <label class="switch-label">全局调整</label>
                  <label class="switch">
                    <input type="checkbox" v-model="hardCostGlobalMode" />
                    <span class="slider"></span>
                  </label>
                </div>
              </div>
              <div class="row-filter">
                <label class="filter-label">筛选岗位序号:</label>
                <select v-model="selectedRowIndex" class="filter-select" @change="onSelectedRowChange">
                  <option v-for="(row, index) in positionRows" :key="row.id" :value="index">
                    序号 {{ index + 1 }} - {{ row.city ? getCityName(row.city) : '请选择' }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <!-- Tabs -->
          <div class="tabs-container">
            <div class="tabs">
              <button
                v-for="tab in ruleTabs"
                :key="tab.key"
                class="tab-btn"
                :class="{ active: activeTab === tab.key }"
                @click="activeTab = tab.key"
              >
                {{ tab.label }}
              </button>
            </div>
            <button class="add-row-btn" @click="resetHardCostToDefault">
              <span class="material-symbols-outlined">restart_alt</span>
              恢复默认
            </button>
          </div>
          <!-- Tab Content -->
          <div class="tab-content">
            <table v-if="activeTab === 'social'" class="rules-table">
              <thead>
                <tr>
                  <th>险种</th>
                  <th>计算基数</th>
                  <th>企业比例</th>
                  <th>个人比例</th>
                  <th>社保成本（公司）</th>
                  <th>社保成本（个人）</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in selectedRowSocialRules" :key="item.type">
                  <td class="type-cell">{{ item.type }}</td>
                  <td class="calc-base-cell">
                    <input
                      v-if="item.type === '工伤保险'"
                      v-model.number="item.calcBase"
                      class="calc-base-input"
                      type="number"
                      min="0"
                      @input="onCalcBaseChange('social', idx)"
                    />
                    <input
                      v-else
                      v-model.number="item.calcBase"
                      class="calc-base-input readonly-input"
                      type="number"
                      readonly
                    />
                  </td>
                  <td class="corp-rate">
                    <input v-model.number="item.corpRate" class="rate-edit-input" type="number" step="0.01" min="0" @input="onRateChange('social', idx)" />
                    <span class="rate-percent">%</span>
                  </td>
                  <td>
                    <input v-model.number="item.indivRate" class="rate-edit-input" type="number" step="0.01" min="0" @input="onRateChange('social', idx)" />
                    <span class="rate-percent">%</span>
                  </td>
                  <td class="cost-corp">{{ formatCurrency(calculateSocialCost(item.calcBase, item.corpRate)) }}</td>
                  <td class="cost-indiv">{{ formatCurrency(calculateSocialCost(item.calcBase, item.indivRate)) }}</td>
                </tr>
                <tr class="summary-row">
                  <td colspan="4" class="summary-label">社保成本小计（当前岗位月度）</td>
                  <td class="summary-value">{{ formatCurrency(selectedSocialCorpTotal) }}</td>
                  <td class="summary-value">{{ formatCurrency(selectedSocialIndivTotal) }}</td>
                </tr>
                <tr class="summary-row">
                  <td colspan="4" class="summary-label">社保成本小计（全部岗位总计）</td>
                  <td class="summary-value">{{ formatCurrency(allRowsSocialCorpTotal) }}</td>
                  <td class="summary-value">{{ formatCurrency(allRowsSocialIndivTotal) }}</td>
                </tr>
              </tbody>
            </table>
            <table v-else-if="activeTab === 'fund'" class="rules-table">
              <thead>
                <tr>
                  <th>项目</th>
                  <th>计算基数</th>
                  <th>企业比例</th>
                  <th>个人比例</th>
                  <th>公积金成本（公司）</th>
                  <th>公积金成本（个人）</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in selectedRowFundRules" :key="item.type">
                  <td class="type-cell">{{ item.type }}</td>
                  <td class="calc-base-cell">
                    <input
                      v-model.number="item.calcBase"
                      class="calc-base-input readonly-input"
                      type="number"
                      readonly
                    />
                  </td>
                  <td class="corp-rate">
                    <input v-model.number="item.corpRate" class="rate-edit-input" type="number" step="0.01" min="0" @input="onRateChange('fund', idx)" />
                    <span class="rate-percent">%</span>
                  </td>
                  <td>
                    <input v-model.number="item.indivRate" class="rate-edit-input" type="number" step="0.01" min="0" @input="onRateChange('fund', idx)" />
                    <span class="rate-percent">%</span>
                  </td>
                  <td class="cost-corp">{{ formatCurrency(calculateSocialCost(item.calcBase, item.corpRate)) }}</td>
                  <td class="cost-indiv">{{ formatCurrency(calculateSocialCost(item.calcBase, item.indivRate)) }}</td>
                </tr>
                <tr class="summary-row">
                  <td colspan="4" class="summary-label">公积金成本小计（当前岗位月度）</td>
                  <td class="summary-value">{{ formatCurrency(selectedFundCorpTotal) }}</td>
                  <td class="summary-value">{{ formatCurrency(selectedFundIndivTotal) }}</td>
                </tr>
                <tr class="summary-row">
                  <td colspan="4" class="summary-label">公积金成本小计（全部岗位总计）</td>
                  <td class="summary-value">{{ formatCurrency(allRowsFundCorpTotal) }}</td>
                  <td class="summary-value">{{ formatCurrency(allRowsFundIndivTotal) }}</td>
                </tr>
              </tbody>
            </table>
            <div v-else-if="activeTab === 'mgmt'" class="mgmt-rules">
              <table class="mgmt-table">
                <thead>
                  <tr>
                    <th>科目</th>
                    <th>税前月薪</th>
                    <th>比例</th>
                    <th>金额</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in selectedRowMgmtRules" :key="item.name">
                    <td class="mgmt-name-cell">{{ item.name }}</td>
                    <td class="mgmt-salary-cell">{{ formatCurrency(selectedRowSalary) }}</td>
                    <td class="mgmt-rate-cell">
                      <div class="rate-input-wrapper">
                        <input
                          v-model.number="item.rateValue"
                          class="rate-input"
                          type="number"
                          step="0.01"
                          min="0"
                          @input="onMgmtRateChange(idx)"
                        />
                        <span class="rate-symbol">%</span>
                      </div>
                    </td>
                    <td class="mgmt-amount-cell">{{ formatCurrency(item.amount) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="mgmt-total-row">
                    <td>管理分摊小计（当前岗位月度）</td>
                    <td>-</td>
                    <td>-</td>
                    <td class="mgmt-total-amount">{{ formatCurrency(selectedMgmtTotalAmount) }}</td>
                  </tr>
                  <tr class="mgmt-total-row">
                    <td>管理分摊小计（全部岗位总计）</td>
                    <td>-</td>
                    <td>-</td>
                    <td class="mgmt-total-amount">{{ formatCurrency(allRowsMgmtTotal) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
            <div class="update-info">
              <span class="material-symbols-outlined info-icon">info</span>
              <span>数据最后更新: 2024-01-15 (AI自动同步)</span>
            </div>
          </div>
        </div>

        <!-- Section 4: Optional Cost -->
        <div class="card optional-cost-card">
          <div class="card-header rules-header">
            <div class="header-left">
              <span class="material-symbols-outlined card-icon">add_circle</span>
              <h3 class="card-title">
                可选人力成本
                <span class="card-title-amount">{{ formatCurrency(optionalCostMonthly) }}</span>
              </h3>
            </div>
            <div class="header-right">
              <button class="add-row-btn" @click="clearAllOptionalCosts">
                <span class="material-symbols-outlined">delete_sweep</span>
                全部清空金额
              </button>
              <div class="global-mode-switch">
                <label class="switch-label">全局调整</label>
                <label class="switch">
                  <input type="checkbox" v-model="optionalCostGlobalMode" />
                  <span class="slider"></span>
                </label>
              </div>
              <div class="row-filter">
                <label class="filter-label">筛选岗位序号:</label>
                <select v-model="selectedOptionalRowIndex" class="filter-select">
                  <option v-for="(row, index) in positionRows" :key="row.id" :value="index">
                    序号 {{ index + 1 }} - {{ row.city ? getCityName(row.city) : '请选择' }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <!-- Tabs -->
          <div class="tabs-container">
            <div class="tabs">
              <button
                v-for="tab in optionalCostTabs"
                :key="tab.key"
                class="tab-btn"
                :class="{ active: activeOptionalTab === tab.key }"
                @click="activeOptionalTab = tab.key"
              >
                {{ tab.label }}
              </button>
            </div>
            <button class="add-row-btn" @click="clearSelectedOptionalCosts">
              <span class="material-symbols-outlined">backspace</span>
              清空金额
            </button>
          </div>
          <!-- Tab Content (Reusing existing components) -->
          <div class="tab-content">
            <div v-if="activeOptionalTab === 'ops'" class="ops-rules">
              <table class="ops-table">
                <thead>
                  <tr>
                    <th>成本项</th>
                    <th>成本分类</th>
                    <th>测算依据</th>
                    <th>月度金额/人</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in selectedRowOpsCosts" :key="item.name">
                    <td class="ops-name-cell">{{ item.name }}</td>
                    <td class="ops-category-cell">{{ item.category }}</td>
                    <td class="ops-basis-cell">{{ item.basis }}</td>
                    <td class="ops-amount-cell">
                      <input
                        :value="item.amount"
                        @input="onOpsCostAmountChange(idx, ($event.target as HTMLInputElement).value)"
                        class="amount-input"
                        type="number"
                        min="0"
                        step="0.01"
                      />
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="ops-total-row">
                    <td>运营成本小计（当前岗位月度）</td>
                    <td>-</td>
                    <td>-</td>
                    <td class="ops-total-amount">{{ formatCurrency(selectedRowOpsCostTotal) }}</td>
                  </tr>
                  <tr class="ops-total-row">
                    <td>运营成本小计（全部岗位总计）</td>
                    <td>-</td>
                    <td colspan="2" class="ops-total-amount">{{ formatCurrency(allRowsOpsCostTotal) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
            <div v-if="activeOptionalTab === 'ondemand'" class="ondemand-rules">
              <table class="ondemand-table">
                <thead>
                  <tr>
                    <th>成本项</th>
                    <th>描述</th>
                    <th>测算依据</th>
                    <th>月度金额/人</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in selectedRowOnDemandCosts" :key="item.name">
                    <td class="ondemand-name-cell">{{ item.name }}</td>
                    <td class="ondemand-desc-cell">{{ item.desc }}</td>
                    <td class="ondemand-basis-cell">{{ item.basis }}</td>
                    <td class="ondemand-amount-cell">
                      <input
                        :value="item.amount"
                        @input="onOnDemandCostAmountChange(idx, ($event.target as HTMLInputElement).value)"
                        class="amount-input"
                        type="number"
                        min="0"
                      />
                    </td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="ondemand-total-row">
                    <td>按需成本小计（当前岗位月度）</td>
                    <td>-</td>
                    <td>-</td>
                    <td class="ondemand-total-amount">{{ formatCurrency(selectedRowOnDemandCostTotal) }}</td>
                  </tr>
                  <tr class="ondemand-total-row">
                    <td>按需成本小计（全部岗位总计）</td>
                    <td>-</td>
                    <td colspan="2" class="ondemand-total-amount">{{ formatCurrency(allRowsOnDemandCostTotal) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
            <div v-if="activeOptionalTab === 'contingency'" class="contingency-rules">
              <table class="contingency-table">
                <thead>
                  <tr>
                    <th>内容</th>
                    <th>离职率</th>
                    <th>周期（天）</th>
                    <th>人员数量</th>
                    <th>人天单价</th>
                    <th>金额</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="(item, idx) in selectedRowContingencyCosts" :key="item.name">
                    <td class="contingency-name-cell">{{ item.name }}</td>
                    <td class="contingency-rate-cell">
                      <div v-if="item.name === '离职交接期成本'" class="input-with-suffix">
                        <input
                          v-model.number="item.turnoverRate"
                          @input="calculateContingencyCostForRow(item, positionRows[selectedOptionalRowIndex])"
                          @change="onContingencyRateChange(idx)"
                          class="rate-input"
                          type="number"
                          min="0"
                          step="0.1"
                        />
                        <span class="input-suffix">%</span>
                      </div>
                      <span v-else class="readonly-value">-</span>
                    </td>
                    <td class="contingency-days-cell">
                      <input
                        v-model.number="item.days"
                        @input="calculateContingencyCostForRow(item, positionRows[selectedOptionalRowIndex])"
                        @change="onContingencyDaysChange(idx)"
                        class="days-input"
                        type="number"
                        min="0"
                        step="0.5"
                      />
                    </td>
                    <td class="contingency-personnel-cell">
                      <span class="readonly-value">{{ positionRows[selectedOptionalRowIndex]?.personnelCount || 0 }}</span>
                    </td>
                    <td class="contingency-unit-price-cell">
                      <div class="readonly-unit-price">{{ formatCurrency((positionRows[selectedOptionalRowIndex]?.salary || 0) / 22) }}</div>
                    </td>
                    <td class="contingency-amount-cell">{{ formatCurrency(item.amount) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="contingency-total-row">
                    <td>机动成本小计（当前）</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td class="contingency-total-amount">{{ formatCurrency(selectedRowContingencyCost) }}</td>
                  </tr>
                  <tr class="contingency-total-row">
                    <td>机动成本小计（全部岗位总计）</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td>-</td>
                    <td class="contingency-total-amount">{{ formatCurrency(allRowsContingencyCostTotal) }}</td>
                  </tr>
                </tfoot>
              </table>
            </div>
          </div>
        </div>
      </div>

      <!-- Right Column: Real-time Summary (Sticky) -->
      <div class="right-column">
        <div class="summary-card">
          <!-- Decorative background glow -->
          <div class="glow-effect"></div>

          <h3 class="summary-title">
            <span class="material-symbols-outlined">calculate</span>
            实时测算结果
          </h3>

          <!-- Global Params Section -->
          <div class="global-params-section">
            <h4 class="section-title">全局参数</h4>
            <div class="global-params-grid">
              <div class="global-param-item">
                <label class="param-label">增值税率</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.vatRate"
                    class="param-input"
                    type="number"
                    @input="calculateAll"
                  />
                  <span class="input-suffix">%</span>
                </div>
              </div>
              <div class="global-param-item">
                <label class="param-label">账期</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.paymentCycle"
                    class="param-input"
                    type="number"
                  />
                  <span class="input-suffix">天</span>
                </div>
              </div>
              <div class="global-param-item">
                <label class="param-label">利润率</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.profitRate"
                    class="param-input"
                    type="number"
                    min="0"
                    @input="calculateAll"
                  />
                  <span class="input-suffix">%</span>
                </div>
              </div>
              <div class="global-param-item">
                <label class="param-label">年化资金成本率</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.fundingCostRate"
                    class="param-input"
                    type="number"
                    min="0"
                    @input="calculateAll"
                  />
                  <span class="input-suffix">%</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Summary Numbers -->
          <div class="summary-numbers">
            <div class="main-price highlight">
              <p class="price-label">项目总额</p>
              <div class="price-value">
                {{ formatCurrency(finalProjectAmount) }}
              </div>
              <div class="price-trend">
                <span class="material-symbols-outlined trend-icon">receipt_long</span>
                含利润率及增值税
              </div>
            </div>

            <div class="sub-prices">
              <div class="sub-price-item">
                <p class="sub-price-label">岗位小计总额</p>
                <div class="sub-price-value">{{ formatCurrency(positionSubtotal) }}</div>
                <div class="sub-price-note">共 {{ totalPersonnel }} 人 / {{ totalCycles }}</div>
              </div>
              <div class="sub-price-item">
                <p class="sub-price-label">预估总毛利</p>
                <div class="sub-price-value">{{ formatCurrency(totalGrossProfit) }}</div>
                <div class="sub-price-note">利润率: {{ totalMargin }}%</div>
              </div>
            </div>
          </div>

          <!-- Breakdown Chart -->
          <div class="breakdown-section">
            <h4 class="breakdown-title">成本构成</h4>
            <div class="breakdown-list">
              <div class="breakdown-item" v-for="item in costBreakdown" :key="item.name">
                <div class="breakdown-header">
                  <span class="breakdown-name">{{ item.name }}</span>
                  <span class="breakdown-amount">{{ formatCurrency(item.amount) }}</span>
                  <span class="breakdown-percent">{{ item.percent }}%</span>
                </div>
                <div class="breakdown-bar">
                  <div class="breakdown-fill" :style="{ width: item.percent + '%', backgroundColor: item.color }"></div>
                </div>
              </div>
            </div>
          </div>

          <!-- AI Insight Box -->
          <div class="ai-insight">
            <div class="insight-header">
              <span class="material-symbols-outlined ai-icon">auto_awesome</span>
              <span class="insight-title">AI 优化建议</span>
            </div>
            <p class="insight-text">
              {{ aiInsight }}
            </p>
          </div>

          <!-- Actions -->
          <div class="summary-actions">
            <button class="btn-primary" @click="startCalculation">
              预览报价单
              <span class="material-symbols-outlined">arrow_forward</span>
            </button>
            <button class="btn-secondary" @click="exportQuotation">
              <span class="material-symbols-outlined">download</span>
              导出报价单
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Mobile Sticky Footer -->
    <div class="mobile-footer">
      <div class="mobile-summary">
        <p class="mobile-label">单人服务费</p>
        <p class="mobile-price">¥ {{ formatNumberCompact(totalSubtotal) }}</p>
      </div>
      <button class="mobile-calc-btn">测算</button>
    </div>

    <!-- 预览报价单弹窗 -->
    <QuotationPreviewModal
      :is-open="isPreviewModalOpen"
      :data="previewData"
      @close="closePreviewModal"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'
import { ElMessage } from 'element-plus'
import QuotationPreviewModal from '../QuotationPreviewModal.vue'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// Router
const router = useRouter()

// Preview Modal State
const isPreviewModalOpen = ref(false)
const previewData = ref<any>({
  positionRows: [],
  globalParams: {},
  customerName: '',
  customerAddress: '',
  projectName: ''
})

// Position row interface
interface PositionRow {
  id: string
  city: string
  position: string
  salary: number
  afterTaxSalary: number
  personnelCount: number
  cycleUnit: 'month' | 'year' | 'day'
  serviceCycleCount: number
  subtotal: number
  unitPrice: number
  // Individual rules for this row
  socialRules: SocialRuleItem[]
  fundRules: FundRuleItem[]
  mgmtRules: MgmtRuleItem[]
  // Risk ratio for this row (percentage, e.g., 8.6 means 8.6%)
  riskRatio: number
  // Optional costs for this row (monthly amount per person)
  opsCosts: OpsCostItem[]
  onDemandCosts: OnDemandCostItem[]
  contingencyCosts: ContingencyCostItem[]
}

// Social rule item
interface SocialRuleItem {
  type: string
  minBase: number
  maxBase: number
  corpRate: number
  indivRate: number
  calcBase: number
}

// Fund rule item
interface FundRuleItem {
  type: string
  minBase: number
  maxBase: number
  corpRate: number
  indivRate: number
  calcBase: number
}

// Management rule item
interface MgmtRuleItem {
  name: string
  rateValue: number
  rate: string
  amount: number
}

// Default social rules template
const getDefaultSocialRules = (): SocialRuleItem[] => [
  { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: 0 },
  { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: 0 },
  { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: 0 },
  { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: 0 },
  { type: '生育保险', minBase: 7310, maxBase: 36549, corpRate: 1, indivRate: 0, calcBase: 0 },
  { type: '残保金', minBase: 7310, maxBase: 36549, corpRate: 1.5, indivRate: 0, calcBase: 0 }
]

// Default fund rules template
const getDefaultFundRules = (): FundRuleItem[] => [
  { type: '住房公积金', minBase: 7310, maxBase: 36549, corpRate: 7, indivRate: 7, calcBase: 0 }
]

// Default management rules template
const getDefaultMgmtRules = (): MgmtRuleItem[] => [
  { name: '招聘分摊', rateValue: 0, rate: '0.00%', amount: 0 },
  { name: 'PM分摊', rateValue: 0, rate: '0.00%', amount: 0 },
  { name: '管理分摊', rateValue: 0, rate: '0.00%', amount: 0 }
]

// Operations cost item interface
interface OpsCostItem {
  name: string
  category: string
  basis: string
  amount: number  // Monthly amount per person
}

// On-demand cost item interface
interface OnDemandCostItem {
  name: string
  desc: string
  basis: string
  amount: number  // Monthly amount per person
}

// Contingency cost item interface
interface ContingencyCostItem {
  name: string
  turnoverRate: number  // 离职率 (%)
  days: number  // 天数
  personnel: number  // 人员数量 (display only)
  unitPrice: number  // 人天单价 (display only)
  amount: number  // 金额
}

// Default operations cost template (月度金额/人)
const getDefaultOpsCosts = (): OpsCostItem[] => [
  { name: '福利费', category: '运营成本', basis: '根据客户要求的特殊类团建费用', amount: 0 },
  { name: '体检费', category: '运营成本', basis: '每年体检费用均摊到月', amount: 0 },
  { name: '运维工具', category: '运营成本', basis: 'ITSM及账号使用', amount: 0 },
  { name: '工装', category: '运营成本', basis: '工作服', amount: 0 },
  { name: '办公固资', category: '运营成本', basis: '根据项目要求进行配置', amount: 0 },
  { name: '专项活动', category: '运营成本', basis: '根据项目要求进行配置，最高1200元/人/年，没有则不填写', amount: 0 },
  { name: '交通工具', category: '运营成本', basis: '按需填写，如给客户做IT活动日等以及客户要求组织的活动', amount: 0 },
  { name: '房屋租赁', category: '运营成本', basis: '如租车、购车', amount: 0 },
  { name: '备品/备件 A类', category: '运营成本', basis: '指事先经过交付备案并被允许发生的房屋租赁费用', amount: 0 },
  { name: '备品/备件 B类', category: '运营成本', basis: '按合同要求，我方必须提供对应设备的备品/备件，因税率不同分税立项为A类，公对公采购（13%税）', amount: 0 },
  { name: '邮寄费', category: '运营成本', basis: '按合同要求，我方必须提供对应设备的备品/备件，因税率不同分税立项为B类，公对公采购（6%税）', amount: 0 },
  { name: '客户关怀', category: '运营成本', basis: '因公邮寄产生的相关费用，年预算不能超过2000', amount: 0 }
]

// Default on-demand cost template (月度金额/人)
const getDefaultOnDemandCosts = (): OnDemandCostItem[] => [
  { name: '差旅', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '加班费', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '餐费', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '交通费', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '团建', desc: '人工机动成本', basis: '根据客户要求的特殊类团建费用', amount: 0 },
  { name: '二线（固定）', desc: '人工机动成本', basis: '明确的二线支持费用', amount: 0 }
]

// Default contingency cost template (月度金额/人)
const getDefaultContingencyCosts = (): ContingencyCostItem[] => [
  { name: '离职交接期成本', turnoverRate: 2, days: 0, personnel: 0, unitPrice: 0, amount: 0 },
  { name: '休假备份成本', turnoverRate: 0, days: 0, personnel: 0, unitPrice: 0, amount: 0 }
]

// Position rows (multi-line support)
const positionRows = ref<PositionRow[]>([
  {
    id: '1',
    city: '',
    position: '',
    salary: 0,
    afterTaxSalary: 0,
    personnelCount: 1,
    cycleUnit: 'month',
    serviceCycleCount: 12,
    subtotal: 0,
    unitPrice: 0,
    socialRules: getDefaultSocialRules(),
    fundRules: getDefaultFundRules(),
    mgmtRules: getDefaultMgmtRules(),
    riskRatio: 8.6,
    opsCosts: getDefaultOpsCosts(),
    onDemandCosts: getDefaultOnDemandCosts(),
    contingencyCosts: getDefaultContingencyCosts()
  }
])

// Selected row index for filtering rules display (人力硬成本)
const selectedRowIndex = ref(0)

// Selected row index for flexible cost (灵活人力成本)
const selectedFlexRowIndex = ref(0)

// Selected row index for optional cost (可选人力成本)
const selectedOptionalRowIndex = ref(0)

// Global mode switches for each section (全局模式开关)
// When enabled, changes apply to all positions instead of just the selected one
const flexCostGlobalMode = ref(false)  // 灵活人力成本全局模式
const hardCostGlobalMode = ref(false)  // 人力硬成本全局模式
const optionalCostGlobalMode = ref(false)  // 可选人力成本全局模式

// Global parameters (VAT rate and payment cycle)
const globalParams = ref({
  vatRate: 6,
  paymentCycle: 0,
  profitRate: 0,
  fundingCostRate: 3  // 年化资金成本率，默认 3%
})

// City options - fetched from backend
const cityOptions = ref<Array<{ label: string; value: string }>>([])

// Autocomplete state
const openDropdowns = ref<Record<string, boolean>>({})
const searchQueries = ref<Record<string, string>>({})
const dropdownPositions = ref<Record<string, { top: number; left: number; width: number }>>({})

// Toggle dropdown
function toggleDropdown(rowId: string, field: string) {
  const key = `${rowId}-${field}`
  openDropdowns.value[key] = !openDropdowns.value[key]
}

// Update dropdown position
function updateDropdownPosition(rowId: string, field: string, event: FocusEvent) {
  const target = event.target as HTMLInputElement
  const rect = target.getBoundingClientRect()
  const key = `${rowId}-${field}`
  dropdownPositions.value[key] = {
    top: rect.bottom + window.scrollY + 4,
    left: rect.left + window.scrollX,
    width: rect.width
  }
}

// Close dropdown
function closeDropdown(rowId: string, field: string) {
  const key = `${rowId}-${field}`
  openDropdowns.value[key] = false
}

// Check if dropdown is open
function isDropdownOpen(rowId: string, field: string): boolean {
  const key = `${rowId}-${field}`
  return openDropdowns.value[key] || false
}

// Get search query
function getSearchQuery(rowId: string, field: string): string {
  const key = `${rowId}-${field}`
  return searchQueries.value[key] || ''
}

// Set search query
function setSearchQuery(rowId: string, field: string, query: string) {
  const key = `${rowId}-${field}`
  searchQueries.value[key] = query
}

// Get filtered cities
function getFilteredCities(rowId: string) {
  const query = getSearchQuery(rowId, 'city').toLowerCase()
  if (!query) return cityOptions.value
  return cityOptions.value.filter(city => city.label.toLowerCase().includes(query))
}

// Get filtered positions
function getFilteredPositions(rowId: string) {
  const query = getSearchQuery(rowId, 'position').toLowerCase()
  if (!query) return availablePositions.value
  return availablePositions.value.filter(pos => pos.name.toLowerCase().includes(query))
}

// Select city
function selectCity(rowId: string, cityValue: string, index: number) {
  const row = positionRows.value[index]
  if (row) {
    row.city = cityValue
    setSearchQuery(rowId, 'city', '')
    closeDropdown(rowId, 'city')
    onRowCityChange(index)
  }
}

// Select position
function selectPosition(rowId: string, positionId: string | number, index: number) {
  const row = positionRows.value[index]
  if (row) {
    row.position = positionId
    setSearchQuery(rowId, 'position', '')
    closeDropdown(rowId, 'position')
    onRowPositionChange(index)
  }
}

// Get display text for city
function getCityDisplayValue(row: PositionRow): string {
  // When dropdown is open, show the search query for typing
  if (isDropdownOpen(row.id, 'city')) {
    return getSearchQuery(row.id, 'city') || row.city || ''
  }
  // When dropdown is closed, show the city value (either selected or custom input)
  if (!row.city) return ''
  // If it's a predefined option, show the label
  const city = cityOptions.value.find(c => c.value === row.city)
  return city ? city.label : row.city
}

// Get display text for position
function getPositionDisplayValue(row: PositionRow): string {
  // When dropdown is open, show the search query for typing
  if (isDropdownOpen(row.id, 'position')) {
    return getSearchQuery(row.id, 'position') || row.position || ''
  }
  // When dropdown is closed, show the position value (either selected or custom input)
  if (!row.position) return ''
  // If it's a predefined option, show the name
  const pos = availablePositions.value.find(p => p.id === row.position)
  return pos ? pos.name : row.position
}

// Handle city input focus - set current city as search query and open dropdown
function onCityFocus(row: PositionRow, rowId: string, event: FocusEvent) {
  const currentDisplay = getCityDisplayValue(row)
  setSearchQuery(rowId, 'city', currentDisplay)
  openDropdowns.value[`${rowId}-city`] = true
  updateDropdownPosition(rowId, 'city', event)
}

// Handle position input focus - set current position as search query and open dropdown
function onPositionFocus(row: PositionRow, rowId: string, event: FocusEvent) {
  const currentDisplay = getPositionDisplayValue(row)
  setSearchQuery(rowId, 'position', currentDisplay)
  openDropdowns.value[`${rowId}-position`] = true
  updateDropdownPosition(rowId, 'position', event)
}

// Handle city input - update search query
function onCityInput(row: PositionRow, rowId: string, value: string) {
  setSearchQuery(rowId, 'city', value)
}

// Handle position input - update search query
function onPositionInput(row: PositionRow, rowId: string, value: string) {
  setSearchQuery(rowId, 'position', value)
}

// Handle city blur - save custom input value
function onCityBlur(row: PositionRow, rowId: string) {
  const searchQuery = getSearchQuery(rowId, 'city')
  const oldCity = row.city
  if (searchQuery) {
    // Check if it matches any city option
    const matchedCity = cityOptions.value.find(c => c.label === searchQuery || c.value === searchQuery)
    if (matchedCity) {
      row.city = matchedCity.value
    } else {
      // Use custom input as the city value
      row.city = searchQuery
    }
  }
  closeDropdown(rowId, 'city')
  setSearchQuery(rowId, 'city', '')
  // If city changed, reload social insurance rules
  if (oldCity !== row.city) {
    const index = positionRows.value.findIndex(r => r.id === row.id)
    if (index !== -1) {
      onRowCityChange(index)
    }
  }
}

// Handle position blur - save custom input value
function onPositionBlur(row: PositionRow, rowId: string) {
  const searchQuery = getSearchQuery(rowId, 'position')
  if (searchQuery) {
    // Check if it matches any position option
    const matchedPos = availablePositions.value.find(p => p.name === searchQuery || p.id === searchQuery)
    if (matchedPos) {
      row.position = matchedPos.id
    } else {
      // Use custom input as the position value
      row.position = searchQuery
    }
  }
  closeDropdown(rowId, 'position')
  setSearchQuery(rowId, 'position', '')
}

// Get dropdown position style
function getDropdownStyle(rowId: string, field: string) {
  const key = `${rowId}-${field}`
  const pos = dropdownPositions.value[key]
  if (!pos) return {}
  return {
    top: `${pos.top}px`,
    left: `${pos.left}px`,
    width: `${pos.width}px`
  }
}

// Next row ID counter
let nextRowId = 2

// Tabs
const activeTab = ref('social')
const ruleTabs = [
  { key: 'social', label: '社保规则' },
  { key: 'fund', label: '公积金规则' },
  { key: 'mgmt', label: '管理分摊' }
]

// Optional cost tabs
const activeOptionalTab = ref('ops')
const optionalCostTabs = [
  { key: 'ops', label: '运营成本' },
  { key: 'ondemand', label: '按需成本' },
  { key: 'contingency', label: '机动成本' }
]

// Position data
const availablePositions = ref<any[]>([])

// City social rules cache
const citySocialRulesCache = ref<Record<string, any>>({})

// Rules data
const socialRules = ref([
  { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: 0 },
  { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: 0 },
  { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: 0 },
  { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: 0 },
  { type: '生育保险', minBase: 7310, maxBase: 36549, corpRate: 1, indivRate: 0, calcBase: 0 },
  { type: '残保金', minBase: 7310, maxBase: 36549, corpRate: 1.5, indivRate: 0, calcBase: 0 }
])

const fundRules = ref([
  { type: '住房公积金', minBase: 7310, maxBase: 36549, corpRate: 7, indivRate: 7, calcBase: 0 }
])

const opsRules = ref([
  { name: '招聘成本', value: '月薪的 15%' },
  { name: '培训成本', value: '月薪的 3%' },
  { name: '办公场地分摊', value: '¥500/人/月' },
  { name: '设备折旧', value: '¥200/人/月' }
])

// Operations cost data
const opsCosts = ref([
  { name: '福利费', category: '运营成本', basis: '根据客户要求的特殊类团建费用', amount: 0 },
  { name: '体检费', category: '运营成本', basis: '每年体检费用均摊到月', amount: 0 },
  { name: '运维工具', category: '运营成本', basis: 'ITSM及账号使用', amount: 0 },
  { name: '工装', category: '运营成本', basis: '工作服', amount: 0 },
  { name: '办公固资', category: '运营成本', basis: '根据项目要求进行配置', amount: 0 },
  { name: '专项活动', category: '运营成本', basis: '根据项目要求进行配置，最高1200元/人/年，没有则不填写', amount: 0 },
  { name: '交通工具', category: '运营成本', basis: '按需填写，如给客户做IT活动日等以及客户要求组织的活动', amount: 0 },
  { name: '房屋租赁', category: '运营成本', basis: '如租车、购车', amount: 0 },
  { name: '备品/备件 A类', category: '运营成本', basis: '指事先经过交付备案并被允许发生的房屋租赁费用', amount: 0 },
  { name: '备品/备件 B类', category: '运营成本', basis: '按合同要求，我方必须提供对应设备的备品/备件，因税率不同分税立项为A类，公对公采购（13%税）', amount: 0 },
  { name: '邮寄费', category: '运营成本', basis: '按合同要求，我方必须提供对应设备的备品/备件，因税率不同分税立项为B类，公对公采购（6%税）', amount: 0 },
  { name: '客户关怀', category: '运营成本', basis: '因公邮寄产生的相关费用，年预算不能超过2000', amount: 0 }
])

// Computed - Selected row's operations costs
const selectedRowOpsCosts = computed(() => {
  return positionRows.value[selectedOptionalRowIndex.value]?.opsCosts || getDefaultOpsCosts()
})

// Computed - Selected row's operations cost total (monthly per person)
const selectedRowOpsCostTotal = computed(() => {
  return selectedRowOpsCosts.value.reduce((sum, item) => {
    const amount = Number(item.amount) || 0
    if (!isFinite(amount) || amount < 0) return sum
    return sum + amount
  }, 0)
})

// Computed - Operations cost total (all rows: monthly × personnelCount × serviceCycle)
const opsCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowOpsCosts = row.opsCosts || getDefaultOpsCosts()
    const rowTotal = rowOpsCosts.reduce((s, item) => {
      const amount = Number(item.amount) || 0
      if (!isFinite(amount) || amount < 0) return s
      return s + amount
    }, 0)
    
    // Get service cycle in months
    const serviceCycleCount = row.serviceCycleCount || 1
    let serviceCycle = serviceCycleCount
    if (row.cycleUnit === 'year') {
      serviceCycle = serviceCycleCount * 12
    } else if (row.cycleUnit === 'day') {
      serviceCycle = serviceCycleCount / 30
    }
    
    const personnelCount = row.personnelCount || 1
    // Total = monthly amount × personnelCount × serviceCycle
    return sum + (rowTotal * personnelCount * serviceCycle)
  }, 0)
})

// Computed - All rows operations cost total (全部岗位运营成本总计，不包含服务周期)
// 只累加所有岗位的月度金额，用于显示
const allRowsOpsCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowOpsCosts = row.opsCosts || getDefaultOpsCosts()
    const rowTotal = rowOpsCosts.reduce((s, item) => {
      const amount = Number(item.amount) || 0
      if (!isFinite(amount) || amount < 0) return s
      return s + amount
    }, 0)
    return sum + rowTotal
  }, 0)
})

const mgmtRules = ref([
  { name: '招聘分摊', rateValue: 0, rate: '0.00%', amount: 0 },
  { name: 'PM分摊', rateValue: 0, rate: '0.00%', amount: 0 },
  { name: '管理分摊', rateValue: 0, rate: '0.00%', amount: 0 }
])

// Computed - Management total amount
const mgmtTotalAmount = computed(() => {
  return mgmtRules.value.reduce((sum, item) => sum + item.amount, 0)
})

// Calculate management amount based on rate
// Formula: 比例 × 筛选岗位序号的税前月薪
function calculateMgmtAmount(item: any) {
  const rate = item.rateValue || 0
  item.rate = rate.toFixed(2) + '%'
  const salary = selectedRowSalary.value || 0
  item.amount = salary * (rate / 100)
}

// Computed - Selected row's social rules
const selectedRowSocialRules = computed(() => {
  return positionRows.value[selectedRowIndex.value]?.socialRules || getDefaultSocialRules()
})

// Computed - Selected row's fund rules
const selectedRowFundRules = computed(() => {
  return positionRows.value[selectedRowIndex.value]?.fundRules || getDefaultFundRules()
})

// Computed - Selected row's management rules
const selectedRowMgmtRules = computed(() => {
  return positionRows.value[selectedRowIndex.value]?.mgmtRules || getDefaultMgmtRules()
})

// Computed - Selected row's salary (for mgmt rules display)
const selectedRowSalary = computed(() => {
  return positionRows.value[selectedRowIndex.value]?.salary || 0
})

// Computed - Selected row social corp total
const selectedSocialCorpTotal = computed(() => {
  return selectedRowSocialRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)
})

// Computed - Selected row social indiv total
const selectedSocialIndivTotal = computed(() => {
  return selectedRowSocialRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.indivRate)
  }, 0)
})

// Computed - Selected row fund corp total
const selectedFundCorpTotal = computed(() => {
  return selectedRowFundRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)
})

// Computed - Selected row fund indiv total
const selectedFundIndivTotal = computed(() => {
  return selectedRowFundRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.indivRate)
  }, 0)
})

// Computed - Selected row mgmt total amount
const selectedMgmtTotalAmount = computed(() => {
  return selectedRowMgmtRules.value.reduce((sum, item) => sum + item.amount, 0)
})

// Computed - All rows social corp total (全部岗位社保成本公司部分总计)
const allRowsSocialCorpTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowTotal = (row.socialRules || []).reduce((s: number, item: any) => {
      return s + calculateSocialCost(item.calcBase, item.corpRate)
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Computed - All rows social indiv total (全部岗位社保成本个人部分总计)
const allRowsSocialIndivTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowTotal = (row.socialRules || []).reduce((s: number, item: any) => {
      return s + calculateSocialCost(item.calcBase, item.indivRate)
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Computed - All rows fund corp total (全部岗位公积金成本公司部分总计)
const allRowsFundCorpTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowTotal = (row.fundRules || []).reduce((s: number, item: any) => {
      return s + calculateSocialCost(item.calcBase, item.corpRate)
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Computed - All rows fund indiv total (全部岗位公积金成本个人部分总计)
const allRowsFundIndivTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowTotal = (row.fundRules || []).reduce((s: number, item: any) => {
      return s + calculateSocialCost(item.calcBase, item.indivRate)
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Computed - All rows mgmt total (全部岗位管理分摊总计)
const allRowsMgmtTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowTotal = (row.mgmtRules || []).reduce((s: number, item: any) => {
      return s + item.amount
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Reset hard cost to default values for the selected row
async function resetHardCostToDefault() {
  const row = positionRows.value[selectedRowIndex.value]
  if (!row) return

  const salary = row.salary || 0
  const city = row.city

  // Reset management rules to default
  row.mgmtRules = getDefaultMgmtRules()

  if (city) {
    // Clear the cache for this city to force reload from backend
    delete citySocialRulesCache.value[city]
    
    // Reload from backend
    const cityName = getCityName(city)
    try {
      const response = await axios.get(`${API_URL}/city-social-insurance/`, {
        params: { city: cityName }
      })

      let data = null
      if (response.data && response.data.length > 0) {
        data = response.data[0]
      } else {
        // If city not found, try to get the default city's data
        const defaultResponse = await axios.get(`${API_URL}/city-social-insurance/`, {
          params: { city: '默认' }
        })
        if (defaultResponse.data && defaultResponse.data.length > 0) {
          data = defaultResponse.data[0]
        }
      }

      if (data) {
        const injuryBase = data.injury_base || salary

        // Helper function to round rate
        const roundRate = (rate: number | null | undefined, defaultValue: number) => {
          if (rate === null || rate === undefined) return defaultValue
          return Math.round(rate * 100 * 100) / 100
        }

        // Restore social rules from backend data
        row.socialRules = [
          { type: '养老保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_pension_rate, 16), indivRate: roundRate(data.indiv_pension_rate, 8), calcBase: salary },
          { type: '医疗保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_medical_rate, 10), indivRate: roundRate(data.indiv_medical_rate, 2), calcBase: salary },
          { type: '失业保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_unemployment_rate, 0.5), indivRate: roundRate(data.indiv_unemployment_rate, 0.5), calcBase: salary },
          { type: '工伤保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_injury_rate, 0.16), indivRate: 0, calcBase: injuryBase },
          { type: '生育保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_maternity_rate, 1), indivRate: 0, calcBase: salary },
          { type: '残保金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_disability_rate, 1.5), indivRate: 0, calcBase: salary }
        ]

        // Restore fund rules from backend data
        row.fundRules = [
          { type: '住房公积金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_fund_rate, 7), indivRate: roundRate(data.indiv_fund_rate, 7), calcBase: salary }
        ]

        // Update cache
        citySocialRulesCache.value[city] = {
          socialRules: row.socialRules,
          fundRules: row.fundRules,
          injuryBase: injuryBase
        }

        ElMessage.success('已恢复为默认值')
      }
    } catch (error) {
      console.error('Failed to reset to default:', error)
      ElMessage.error('恢复默认值失败')
    }
  } else {
    // No city selected, use hardcoded defaults
    const injuryBase = salary > 0 ? salary : 0
    row.socialRules = [
      { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: salary },
      { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: salary },
      { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: salary },
      { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: injuryBase },
      { type: '生育保险', minBase: 7310, maxBase: 36549, corpRate: 1, indivRate: 0, calcBase: salary },
      { type: '残保金', minBase: 7310, maxBase: 36549, corpRate: 1.5, indivRate: 0, calcBase: salary }
    ]
    row.fundRules = [
      { type: '住房公积金', minBase: 7310, maxBase: 36549, corpRate: 7, indivRate: 7, calcBase: salary }
    ]
    ElMessage.success('已恢复为默认值')
  }

  // Recalculate the row
  calculateRow(selectedRowIndex.value)
}

// Reset hard cost to default values for ALL rows
async function resetAllHardCostToDefault() {
  // Helper function to round rate
  const roundRate = (rate: number | null | undefined, defaultValue: number) => {
    if (rate === null || rate === undefined) return defaultValue
    return Math.round(rate * 100 * 100) / 100
  }

  // Clear all city cache to force reload from backend
  citySocialRulesCache.value = {}

  let successCount = 0
  let failCount = 0

  for (let i = 0; i < positionRows.value.length; i++) {
    const row = positionRows.value[i]
    const salary = row.salary || 0
    const city = row.city

    // Reset management rules to default
    row.mgmtRules = getDefaultMgmtRules()

    if (city) {
      // Reload from backend
      const cityName = getCityName(city)
      try {
        const response = await axios.get(`${API_URL}/city-social-insurance/`, {
          params: { city: cityName }
        })

        let data = null
        if (response.data && response.data.length > 0) {
          data = response.data[0]
        } else {
          // If city not found, try to get the default city's data
          const defaultResponse = await axios.get(`${API_URL}/city-social-insurance/`, {
            params: { city: '默认' }
          })
          if (defaultResponse.data && defaultResponse.data.length > 0) {
            data = defaultResponse.data[0]
          }
        }

        if (data) {
          const injuryBase = data.injury_base || salary

          // Restore social rules from backend data
          row.socialRules = [
            { type: '养老保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_pension_rate, 16), indivRate: roundRate(data.indiv_pension_rate, 8), calcBase: salary },
            { type: '医疗保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_medical_rate, 10), indivRate: roundRate(data.indiv_medical_rate, 2), calcBase: salary },
            { type: '失业保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_unemployment_rate, 0.5), indivRate: roundRate(data.indiv_unemployment_rate, 0.5), calcBase: salary },
            { type: '工伤保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_injury_rate, 0.16), indivRate: 0, calcBase: injuryBase },
            { type: '生育保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_maternity_rate, 1), indivRate: 0, calcBase: salary },
            { type: '残保金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_disability_rate, 1.5), indivRate: 0, calcBase: salary }
          ]

          // Restore fund rules from backend data
          row.fundRules = [
            { type: '住房公积金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_fund_rate, 7), indivRate: roundRate(data.indiv_fund_rate, 7), calcBase: salary }
          ]

          // Update cache
          citySocialRulesCache.value[city] = {
            socialRules: row.socialRules,
            fundRules: row.fundRules,
            injuryBase: injuryBase
          }

          successCount++
        }
      } catch (error) {
        console.error(`Failed to reset row ${i + 1} to default:`, error)
        failCount++
      }
    } else {
      // No city selected, use hardcoded defaults
      const injuryBase = salary > 0 ? salary : 0
      row.socialRules = [
        { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: salary },
        { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: salary },
        { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: salary },
        { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: injuryBase },
        { type: '生育保险', minBase: 7310, maxBase: 36549, corpRate: 1, indivRate: 0, calcBase: salary },
        { type: '残保金', minBase: 7310, maxBase: 36549, corpRate: 1.5, indivRate: 0, calcBase: salary }
      ]
      row.fundRules = [
        { type: '住房公积金', minBase: 7310, maxBase: 36549, corpRate: 7, indivRate: 7, calcBase: salary }
      ]
      successCount++
    }

    // Recalculate the row
    calculateRow(i)
  }

  if (failCount === 0) {
    ElMessage.success(`已恢复全部 ${successCount} 个岗位的默认值`)
  } else {
    ElMessage.warning(`成功恢复 ${successCount} 个岗位，失败 ${failCount} 个`)
  }
}

// Clear optional costs for the selected row
function clearSelectedOptionalCosts() {
  const row = positionRows.value[selectedOptionalRowIndex.value]
  if (!row) return

  // Clear ops costs
  if (row.opsCosts) {
    row.opsCosts.forEach(item => {
      item.amount = 0
    })
  }

  // Clear on-demand costs
  if (row.onDemandCosts) {
    row.onDemandCosts.forEach(item => {
      item.amount = 0
    })
  }

  // Clear contingency costs
  if (row.contingencyCosts) {
    row.contingencyCosts.forEach(item => {
      item.days = 0
      item.amount = 0
    })
  }

  ElMessage.success(`已清空岗位 ${selectedOptionalRowIndex.value + 1} 的可选成本金额`)
}

// Clear optional costs for ALL rows
function clearAllOptionalCosts() {
  positionRows.value.forEach((row, index) => {
    // Clear ops costs
    if (row.opsCosts) {
      row.opsCosts.forEach(item => {
        item.amount = 0
      })
    }

    // Clear on-demand costs
    if (row.onDemandCosts) {
      row.onDemandCosts.forEach(item => {
        item.amount = 0
      })
    }

    // Clear contingency costs
    if (row.contingencyCosts) {
      row.contingencyCosts.forEach(item => {
        item.days = 0
        item.amount = 0
      })
    }
  })

  ElMessage.success(`已清空全部 ${positionRows.value.length} 个岗位的可选成本金额`)
}

// Handle rate change event
function onRateChange(type: 'social' | 'fund', index: number) {
  // Get current row and the changed rule
  const currentRow = positionRows.value[selectedRowIndex.value]
  if (!currentRow) return

  const rules = type === 'social' ? currentRow.socialRules : currentRow.fundRules
  const changedRule = rules[index]

  // If global mode is enabled, sync the changed rate to all other positions
  if (hardCostGlobalMode.value) {
    positionRows.value.forEach(row => {
      if (row.id !== currentRow.id) {
        const targetRules = type === 'social' ? row.socialRules : row.fundRules
        if (targetRules[index]) {
          targetRules[index].corpRate = changedRule.corpRate
          targetRules[index].indivRate = changedRule.indivRate
        }
      }
    })
  }

  // Recalculate all rows' subtotals
  calculateAll()
}

// Handle calc base change event (manual edit)
function onCalcBaseChange(type: 'social' | 'fund', index: number) {
  // Recalculate the selected row's subtotal when calcBase is manually changed
  const row = positionRows.value[selectedRowIndex.value]
  if (row) {
    calculateRow(selectedRowIndex.value)
  }
}

// Handle mgmt rate change event
function onMgmtRateChange(index: number) {
  const currentRow = positionRows.value[selectedRowIndex.value]
  if (!currentRow) return

  const item = currentRow.mgmtRules[index]
  const rate = item.rateValue || 0
  item.rate = rate.toFixed(2) + '%'
  item.amount = currentRow.salary * (rate / 100)

  // If global mode is enabled, sync the changed rate to all other positions
  if (hardCostGlobalMode.value) {
    positionRows.value.forEach(row => {
      if (row.id !== currentRow.id && row.mgmtRules[index]) {
        const targetItem = row.mgmtRules[index]
        targetItem.rateValue = rate
        targetItem.rate = rate.toFixed(2) + '%'
        targetItem.amount = row.salary * (rate / 100)
      }
    })
  }

  // Recalculate all rows' subtotals
  calculateAll()
}

// Handle selected row change event
function onSelectedRowChange() {
  updateSelectedRowCalcBase()
  // Recalculate mgmt rules amounts based on new row's salary
  const row = positionRows.value[selectedRowIndex.value]
  if (!row) return
  row.mgmtRules.forEach((item: any) => {
    calculateMgmtAmount(item)
  })
}

// Update selected row's calcBase values
function updateSelectedRowCalcBase() {
  const row = positionRows.value[selectedRowIndex.value]
  if (!row) return

  const salary = row.salary || 0

  // Update social rules calcBase
  row.socialRules.forEach((item: any) => {
    if (item.type === '工伤保险') {
      // If salary is 0, set injury calcBase to 0 as well
      if (salary === 0) {
        item.calcBase = 0
      } else if (row.city) {
        // Load injury_base from city data only when city is selected
        loadCityInjuryBase(row.city).then(injuryBase => {
          item.calcBase = injuryBase || salary
        })
      } else {
        // If no city selected, use salary as fallback
        item.calcBase = salary
      }
    } else {
      item.calcBase = salary
    }
  })

  // Update fund rules calcBase
  row.fundRules.forEach((item: any) => {
    item.calcBase = salary
  })
}

// Load injury_base for a city
async function loadCityInjuryBase(city: string): Promise<number> {
  const cityName = getCityName(city)
  try {
    const response = await axios.get(`${API_URL}/city-social-insurance/`, {
      params: { city: cityName }
    })
    if (response.data && response.data.length > 0) {
      return response.data[0].injury_base || 0
    } else {
      // If city not found, try to get the default city's injury_base
      console.log(`City "${cityName}" not found for injury_base, using default values`)
      const defaultResponse = await axios.get(`${API_URL}/city-social-insurance/`, {
        params: { city: '默认' }
      })
      if (defaultResponse.data && defaultResponse.data.length > 0) {
        return defaultResponse.data[0].injury_base || 0
      }
    }
  } catch (error) {
    console.error('Failed to load injury_base:', error)
  }
  return 0
}

// On-demand cost data (kept for backward compatibility)
const onDemandCosts = ref([
  { name: '差旅', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '加班费', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '餐费', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '交通费', desc: '人工机动成本', basis: '', amount: 0 },
  { name: '团建', desc: '人工机动成本', basis: '根据客户要求的特殊类团建费用', amount: 0 },
  { name: '二线（固定）', desc: '人工机动成本', basis: '明确的二线支持费用', amount: 0 }
])

// Computed - Selected row's on-demand costs
const selectedRowOnDemandCosts = computed(() => {
  return positionRows.value[selectedOptionalRowIndex.value]?.onDemandCosts || getDefaultOnDemandCosts()
})

// Computed - Selected row's on-demand cost total (monthly per person)
const selectedRowOnDemandCostTotal = computed(() => {
  return selectedRowOnDemandCosts.value.reduce((sum, item) => {
    const amount = Number(item.amount) || 0
    if (!isFinite(amount) || amount < 0) return sum
    return sum + amount
  }, 0)
})

// Computed - Selected row's contingency costs
const selectedRowContingencyCosts = computed(() => {
  return positionRows.value[selectedOptionalRowIndex.value]?.contingencyCosts || getDefaultContingencyCosts()
})

// Computed - Selected row's contingency cost total (当前岗位月度)
const selectedRowContingencyCost = computed(() => {
  const row = positionRows.value[selectedOptionalRowIndex.value]
  if (!row) return 0

  const personnel = row.personnelCount || 0
  const unitPrice = (row.salary || 0) / 22 // 当前岗位的人天单价

  return selectedRowContingencyCosts.value.reduce((sum, item) => {
    if (item.name === '离职交接期成本') {
      return sum + ((item.turnoverRate || 0) / 100) * (item.days || 0) * personnel * unitPrice
    } else {
      // 休假备份成本不使用离职率
      return sum + (item.days || 0) * personnel * unitPrice
    }
  }, 0)
})

// Calculate contingency cost for a specific row
// 离职交接期成本: 离职率 × 周期(天) × 人员数量 × 人天单价
// 休假备份成本: 周期(天) × 人员数量 × 人天单价 (不使用离职率)
function calculateContingencyCostForRow(item: ContingencyCostItem, row: PositionRow) {
  const personnel = row.personnelCount || 0
  const unitPrice = (row.salary || 0) / 22

  if (item.name === '离职交接期成本') {
    item.amount = ((item.turnoverRate || 0) / 100) * (item.days || 0) * personnel * unitPrice
  } else {
    // 休假备份成本不使用离职率
    item.amount = (item.days || 0) * personnel * unitPrice
  }
  item.personnel = personnel
  item.unitPrice = unitPrice
}

// Handle ops cost amount change with global mode support
function onOpsCostAmountChange(index: number, value: string) {
  const currentRow = positionRows.value[selectedOptionalRowIndex.value]
  if (!currentRow) return

  const amount = Number(value) || 0
  currentRow.opsCosts[index].amount = amount

  // If global mode is enabled, sync the changed amount to all other positions
  if (optionalCostGlobalMode.value) {
    positionRows.value.forEach(row => {
      if (row.id !== currentRow.id && row.opsCosts[index]) {
        row.opsCosts[index].amount = amount
      }
    })
  }
}

// Handle on-demand cost amount change with global mode support
function onOnDemandCostAmountChange(index: number, value: string) {
  const currentRow = positionRows.value[selectedOptionalRowIndex.value]
  if (!currentRow) return

  const amount = Number(value) || 0
  currentRow.onDemandCosts[index].amount = amount

  // If global mode is enabled, sync the changed amount to all other positions
  if (optionalCostGlobalMode.value) {
    positionRows.value.forEach(row => {
      if (row.id !== currentRow.id && row.onDemandCosts[index]) {
        row.onDemandCosts[index].amount = amount
      }
    })
  }
}

// Handle contingency turnover rate change with global mode support
// Called on @change event (after user finishes editing)
function onContingencyRateChange(index: number) {
  if (!optionalCostGlobalMode.value) return

  const currentRow = positionRows.value[selectedOptionalRowIndex.value]
  if (!currentRow) return

  const rate = currentRow.contingencyCosts[index].turnoverRate || 0

  // Sync the changed rate to all other positions
  positionRows.value.forEach(row => {
    if (row.id !== currentRow.id && row.contingencyCosts[index]) {
      row.contingencyCosts[index].turnoverRate = rate
      calculateContingencyCostForRow(row.contingencyCosts[index], row)
    }
  })
}

// Handle contingency days change with global mode support
// Called on @change event (after user finishes editing)
function onContingencyDaysChange(index: number) {
  if (!optionalCostGlobalMode.value) return

  const currentRow = positionRows.value[selectedOptionalRowIndex.value]
  if (!currentRow) return

  const days = currentRow.contingencyCosts[index].days || 0

  // Sync the changed days to all other positions
  positionRows.value.forEach(row => {
    if (row.id !== currentRow.id && row.contingencyCosts[index]) {
      row.contingencyCosts[index].days = days
      calculateContingencyCostForRow(row.contingencyCosts[index], row)
    }
  })
}

// Watch for changes in selectedOptionalRowIndex to recalculate contingency costs for the selected row
watch(selectedOptionalRowIndex, (newIndex) => {
  const row = positionRows.value[newIndex]
  if (row && row.contingencyCosts) {
    row.contingencyCosts.forEach(item => {
      calculateContingencyCostForRow(item, row)
    })
  }
})

// Computed - On-demand cost total (all rows: monthly × personnelCount × serviceCycle)
const onDemandCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowOnDemandCosts = row.onDemandCosts || getDefaultOnDemandCosts()
    const rowTotal = rowOnDemandCosts.reduce((s, item) => {
      const amount = Number(item.amount) || 0
      if (!isFinite(amount) || amount < 0) return s
      return s + amount
    }, 0)
    
    // Get service cycle in months
    const serviceCycleCount = row.serviceCycleCount || 1
    let serviceCycle = serviceCycleCount
    if (row.cycleUnit === 'year') {
      serviceCycle = serviceCycleCount * 12
    } else if (row.cycleUnit === 'day') {
      serviceCycle = serviceCycleCount / 30
    }
    
    const personnelCount = row.personnelCount || 1
    // Total = monthly amount × personnelCount × serviceCycle
    return sum + (rowTotal * personnelCount * serviceCycle)
  }, 0)
})

// Computed - All rows on-demand cost total (全部岗位按需成本总计，不包含服务周期)
// 只累加所有岗位的月度金额，用于显示
const allRowsOnDemandCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowOnDemandCosts = row.onDemandCosts || getDefaultOnDemandCosts()
    const rowTotal = rowOnDemandCosts.reduce((s, item) => {
      const amount = Number(item.amount) || 0
      if (!isFinite(amount) || amount < 0) return s
      return s + amount
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Computed - Contingency cost total (全部岗位总计)
// 计算所有岗位的机动成本总计
const contingencyCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowContingencyCosts = row.contingencyCosts || getDefaultContingencyCosts()
    const personnel = row.personnelCount || 0
    const unitPrice = (row.salary || 0) / 22 // 当前岗位的人天单价

    const rowTotal = rowContingencyCosts.reduce((s, item) => {
      let itemAmount = 0
      if (item.name === '离职交接期成本') {
        itemAmount = ((item.turnoverRate || 0) / 100) * (item.days || 0) * personnel * unitPrice
      } else {
        // 休假备份成本不使用离职率
        itemAmount = (item.days || 0) * personnel * unitPrice
      }
      return s + itemAmount
    }, 0)

    // Get service cycle in months
    const serviceCycleCount = row.serviceCycleCount || 1
    let serviceCycle = serviceCycleCount
    if (row.cycleUnit === 'year') {
      serviceCycle = serviceCycleCount * 12
    } else if (row.cycleUnit === 'day') {
      serviceCycle = serviceCycleCount / 30
    }

    // Total = row monthly total × serviceCycle
    return sum + (rowTotal * serviceCycle)
  }, 0)
})

// Computed - All rows contingency cost total (全部岗位机动成本总计，不包含服务周期)
// 只累加所有岗位的月度金额，用于显示
const allRowsContingencyCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const rowContingencyCosts = row.contingencyCosts || getDefaultContingencyCosts()
    const personnel = row.personnelCount || 0
    const unitPrice = (row.salary || 0) / 22 // 当前岗位的人天单价

    const rowTotal = rowContingencyCosts.reduce((s, item) => {
      let itemAmount = 0
      if (item.name === '离职交接期成本') {
        itemAmount = ((item.turnoverRate || 0) / 100) * (item.days || 0) * personnel * unitPrice
      } else {
        // 休假备份成本不使用离职率
        itemAmount = (item.days || 0) * personnel * unitPrice
      }
      return s + itemAmount
    }, 0)
    return sum + rowTotal
  }, 0)
})

// Base subtotal across all rows (without tax and profit)
const baseSubtotal = computed(() => {
  return positionRows.value.reduce((sum, row) => sum + row.subtotal, 0)
})

// Risk cost monthly: sum of (salary * riskRatio) for each row (per-person per-month)
// Not affected by personnelCount or serviceCycle
const riskCostMonthly = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    const salary = row.salary || 0
    const riskRatio = (row.riskRatio || 0) / 100
    // Monthly risk cost per person = salary * riskRatio
    return sum + (salary * riskRatio)
  }, 0)
})

// Get selected row's risk ratio for the flex cost section
const selectedFlexRowRiskRatio = computed({
  get: () => positionRows.value[selectedFlexRowIndex.value]?.riskRatio ?? 8.6,
  set: (value: number) => {
    if (flexCostGlobalMode.value) {
      // Global mode: apply to all positions
      positionRows.value.forEach(row => {
        row.riskRatio = value
      })
    } else {
      // Single position mode: apply only to selected position
      if (positionRows.value[selectedFlexRowIndex.value]) {
        positionRows.value[selectedFlexRowIndex.value].riskRatio = value
      }
    }
  }
})

// Get selected row's salary for the flex cost section
const selectedFlexRowSalary = computed(() => {
  return positionRows.value[selectedFlexRowIndex.value]?.salary || 0
})

// Get selected row's risk amount for the flex cost section
// Formula: 税前月薪 × 风险金比例%
const selectedFlexRowRiskAmount = computed(() => {
  const salary = selectedFlexRowSalary.value
  const riskRatio = (selectedFlexRowRiskRatio.value || 0) / 100
  return salary * riskRatio
})

// Hard cost monthly: sum of (socialCostCorp + fundCostCorp + mgmtCost) for each row (per-person per-month)
// Not affected by personnelCount or serviceCycle
// Uses item.calcBase to match the UI display (社保成本小计 + 公积金成本小计 + 管理分摊合计)
const hardCostMonthly = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    // Calculate social insurance cost (company only) - use item.calcBase
    const socialCorpTotal = (row.socialRules || []).reduce((s: number, item: any) => {
      return s + calculateSocialCost(item.calcBase, item.corpRate)
    }, 0)

    // Calculate housing fund cost (company only) - use item.calcBase
    const fundCorpTotal = (row.fundRules || []).reduce((s: number, item: any) => {
      return s + calculateSocialCost(item.calcBase, item.corpRate)
    }, 0)

    // Management cost total
    const mgmtTotal = (row.mgmtRules || []).reduce((s: number, item: any) => {
      return s + item.amount
    }, 0)

    // Monthly cost per person (社保+公积金+管理费用)
    return sum + (socialCorpTotal + fundCorpTotal + mgmtTotal)
  }, 0)
})

// Optional cost monthly (per-person per-month): sum of ops + onDemand + contingency for each row
// Not affected by personnelCount or serviceCycle
// 公式：运营成本小计（全部岗位总计）+ 按需成本小计（全部岗位总计）+ 机动成本小计（全部岗位总计）
const optionalCostMonthly = computed(() => {
  return allRowsOpsCostTotal.value + allRowsOnDemandCostTotal.value + allRowsContingencyCostTotal.value
})

// Computed - Total project amount (without tax and profit)
// Formula: 岗位小计测算合计 + 风险金成本 + 运营成本小计 + 按需成本小计 + 机动成本小计
const totalSubtotal = computed(() => {
  return baseSubtotal.value + riskCostMonthly.value + opsCostTotal.value + onDemandCostTotal.value + contingencyCostTotal.value
})

// Computed - Position subtotal (sum of all row subtotals, with VAT only, no profit)
const positionSubtotal = computed(() => {
  const vatMultiplier = 1 + (globalParams.value.vatRate ?? 6) / 100
  return baseSubtotal.value * vatMultiplier
})

// Computed - Base project amount (without funding cost)
// Formula: totalSubtotal × (1 + 利润率) × (1 + 增值税率)
const baseProjectAmount = computed(() => {
  const profitMultiplier = 1 + (globalParams.value.profitRate || 0) / 100
  const vatMultiplier = 1 + (globalParams.value.vatRate ?? 6) / 100
  return totalSubtotal.value * profitMultiplier * vatMultiplier
})

// Computed - Funding cost rate for the payment cycle
// Formula: 年化资金成本率 × (账期天数 / 365)
const fundingCostRateForCycle = computed(() => {
  const fundingCostRate = (globalParams.value.fundingCostRate || 0) / 100
  const paymentCycle = globalParams.value.paymentCycle || 0
  return fundingCostRate * (paymentCycle / 365)
})

// Computed - Final project amount (including funding cost)
// 由于账期成本 = 项目总额 × 账期成本率，存在循环依赖
// 数学推导：P = B + P × r => P = B / (1 - r)
// 其中 P = 最终项目总额，B = 基础项目金额，r = 账期成本率
const finalProjectAmount = computed(() => {
  const rate = fundingCostRateForCycle.value
  if (rate >= 1) return baseProjectAmount.value // 防止除以0或负数
  return baseProjectAmount.value / (1 - rate)
})

// Computed - Funding cost (账期成本)
// Formula: finalProjectAmount × 年化资金成本率 × (账期天数 / 365)
const fundingCost = computed(() => {
  return finalProjectAmount.value * fundingCostRateForCycle.value
})

// Computed - Total personnel
const totalPersonnel = computed(() => {
  return positionRows.value.reduce((sum, row) => sum + (row.personnelCount || 0), 0)
})

// Computed - Total cycles (display text)
const totalCycles = computed(() => {
  const cycles = positionRows.value.map(row => {
    return `${row.serviceCycleCount}${getRowCycleUnitText(row.cycleUnit)}`
  })
  return cycles.join(' + ')
})

// Computed - Total gross profit (with tax and profit)
// Formula: totalSubtotal × 利润率 × (1 + 增值税率)
const totalGrossProfit = computed(() => {
  const profitRate = (globalParams.value.profitRate || 0) / 100
  const vatMultiplier = 1 + (globalParams.value.vatRate ?? 6) / 100
  return totalSubtotal.value * profitRate * vatMultiplier
})

// Computed - Total margin percentage (using global profit rate parameter)
const totalMargin = computed(() => {
  return (globalParams.value.profitRate || 0).toFixed(1)
})

// Computed - Total deal amount (with VAT)
const totalDealAmount = computed(() => {
  const vatRate = (globalParams.value.vatRate || 0) / 100
  return totalSubtotal.value * (1 + vatRate)
})

// Cost breakdown
// 计算公式：各部分金额 / 项目总额 × 100
// 使用项目总额作为分母，所有项占比之和为 100%
const costBreakdown = computed(() => {
  const vatMultiplier = 1 + (globalParams.value.vatRate ?? 6) / 100
  const projectTotal = finalProjectAmount.value

  // 1. 人力管理成本 = 岗位小计测算合计 × (1+增值税率)
  const hardCostAmount = baseSubtotal.value * vatMultiplier
  const hardCostPercent = projectTotal > 0 ? Math.round(hardCostAmount / projectTotal * 100) : 0

  // 2. 按需运营机动成本 = 可选人力成本合计 × (1+增值税率)
  const optionalCostAmount = (opsCostTotal.value + onDemandCostTotal.value + contingencyCostTotal.value) * vatMultiplier
  const opsMgmtPercent = projectTotal > 0 ? Math.round(optionalCostAmount / projectTotal * 100) : 0

  // 3. 风险金 = 风险金成本 × (1+增值税率)
  const riskAmount = riskCostMonthly.value * vatMultiplier
  const riskPercent = projectTotal > 0 ? Math.round(riskAmount / projectTotal * 100) : 0

  // 4. 账期成本 = 项目总额 × 年化资金成本率 × (账期天数 / 365)
  const fundingCostAmount = fundingCost.value
  const fundingCostPercent = projectTotal > 0 ? Math.round(fundingCostAmount / projectTotal * 100) : 0

  // 5. 预估总毛利 = 成本总额 × 利润率 × (1+增值税率)
  const profitAmount = totalGrossProfit.value
  // 使用补足法确保总和为 100%
  const profitPercent = projectTotal > 0 ? (100 - hardCostPercent - opsMgmtPercent - riskPercent - fundingCostPercent) : 0

  return [
    { name: '人力管理成本', percent: hardCostPercent, amount: hardCostAmount, color: '#3b82f6' },
    { name: '按需运营机动成本', percent: opsMgmtPercent, amount: optionalCostAmount, color: '#a855f7' },
    { name: '风险金', percent: riskPercent, amount: riskAmount, color: '#eab308' },
    { name: '账期成本', percent: fundingCostPercent, amount: fundingCostAmount, color: '#22c55e' },
    { name: '预估总毛利', percent: profitPercent, amount: profitAmount, color: '#10b981' }
  ]
})

// AI Insight
const aiInsight = computed(() => {
  const margin = parseFloat(totalMargin.value)
  if (margin < 15) {
    return '当前利润率偏低，建议适当上调至 18% 以上以覆盖运营风险。'
  } else if (margin < 22) {
    return '当前报价在同岗位中略低于平均水平 (P40)。建议适当上调利润率至 22% 以覆盖潜在的人员流失风险。'
  } else {
    return '当前报价策略较为合理，利润率处于健康区间。建议关注项目执行过程中的成本控制。'
  }
})

// Calculate social insurance/fund cost for a single item
// rate is stored as percentage number (e.g., 7 for 7%, 16 for 16%)
function calculateSocialCost(calcBase: number, rate: number): number {
  return (calcBase || 0) * ((rate || 0) / 100)
}

// Computed - Total social insurance cost for company
const socialCostCorpTotal = computed(() => {
  return socialRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)
})

// Computed - Total social insurance cost for individual
const socialCostIndivTotal = computed(() => {
  return socialRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.indivRate)
  }, 0)
})

// Computed - Total social insurance cost (company + individual)
const socialTotal = computed(() => {
  return socialCostCorpTotal.value + socialCostIndivTotal.value
})

// Computed - Total housing fund cost for company
const fundCostCorpTotal = computed(() => {
  return fundRules.value.reduce((sum, item) => {
    return sum + (item.calcBase * item.corpRate)
  }, 0)
})

// Computed - Total housing fund cost for individual
const fundCostIndivTotal = computed(() => {
  return fundRules.value.reduce((sum, item) => {
    return sum + (item.calcBase * item.indivRate)
  }, 0)
})

// Computed - Total housing fund cost (company + individual)
const fundTotal = computed(() => {
  return fundCostCorpTotal.value + fundCostIndivTotal.value
})

// Methods
function getRowCycleUnitText(cycleUnit: string): string {
  const unitMap: Record<string, string> = {
    month: '月',
    year: '年',
    day: '天'
  }
  return unitMap[cycleUnit] || '月'
}

function getCityName(cityKey: string): string {
  // If the value is already a Chinese name (contains Chinese characters), return directly
  if (/[\u4e00-\u9fa5]/.test(cityKey)) {
    return cityKey
  }

  const cityMap: Record<string, string> = {
    shanghai: '上海',
    beijing: '北京',
    shenzhen: '深圳',
    hangzhou: '杭州',
    guangzhou: '广州',
    chengdu: '成都',
    nanjing: '南京',
    wuhan: '武汉'
  }
  return cityMap[cityKey] || cityKey || ''
}

function getCurrentCityName(): string {
  // Use the first row's city for display
  if (positionRows.value.length > 0 && positionRows.value[0].city) {
    return getCityName(positionRows.value[0].city)
  }
  return ''
}

function formatNumber(num: number): string {
  return (num || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatNumberCompact(num: number): string {
  if (num >= 10000) {
    return (num / 10000).toFixed(1) + 'w'
  }
  return Math.round(num).toLocaleString('zh-CN')
}

function formatCurrency(num: number): string {
  const value = num || 0
  return '¥ ' + value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatCurrencyCompact(num: number): string {
  if (num >= 1000000) {
    return '¥ ' + (num / 1000000).toFixed(2) + 'M'
  } else if (num >= 10000) {
    return '¥ ' + (num / 10000).toFixed(2) + 'w'
  }
  return '¥ ' + (num || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

// Calculate a single row's subtotal
// New formula: 税前月薪 + 社保成本（公司）+ 公积金成本（公司）+ 管理分摊合计
// Note: Only company portion, excludes individual portion
// Uses the row's own rules (each row can have different city and custom rates)
function calculateRowSubtotal(row: PositionRow): number {
  const salary = row.salary || 0

  // Use the row's own rules
  const currentSocialRules = row.socialRules || getDefaultSocialRules()
  const currentFundRules = row.fundRules || getDefaultFundRules()
  const currentMgmtRules = row.mgmtRules || getDefaultMgmtRules()

  // Calculate social insurance cost (company only) for this row
  const socialCorpTotalForRow = currentSocialRules.reduce((sum: number, item: any) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)

  // Calculate housing fund cost (company only) for this row
  const fundCorpTotalForRow = currentFundRules.reduce((sum: number, item: any) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)

  // Management cost total - using row's own mgmt rules
  const mgmtTotalForRow = currentMgmtRules.reduce((sum: number, item: any) => {
    return sum + item.amount
  }, 0)

  // Monthly subtotal per person: 税前月薪 + 社保（公司）+ 公积金（公司）+ 管理分摊合计
  const monthlySubtotalPerPerson = salary + socialCorpTotalForRow + fundCorpTotalForRow + mgmtTotalForRow

  // Round to 2 decimal places to match display precision
  const roundedMonthlySubtotal = Math.round(monthlySubtotalPerPerson * 100) / 100

  // Calculate total based on personnel and cycle
  const personnelCount = row.personnelCount || 1
  const serviceCycleCount = row.serviceCycleCount || 1

  let totalMonths = serviceCycleCount
  if (row.cycleUnit === 'year') {
    totalMonths = serviceCycleCount * 12
  } else if (row.cycleUnit === 'day') {
    totalMonths = serviceCycleCount / 30
  }

  return roundedMonthlySubtotal * personnelCount * totalMonths
}

// Calculate profit for a row
// Using global profit rate parameter
function calculateRowProfit(row: PositionRow): number {
  const profitRate = (globalParams.value.profitRate || 0) / 100
  return row.subtotal * profitRate
}

// Calculate a specific row
function calculateRow(index: number, skipAfterTaxCalc = false) {
  const row = positionRows.value[index]
  const salary = row.salary || 0

  // Update calcBase for this row's rules when salary changes
  row.socialRules.forEach((item: any) => {
    if (item.type !== '工伤保险') {
      item.calcBase = salary
    } else {
      // For 工伤保险, if salary is 0, set calcBase to 0
      if (salary === 0) {
        item.calcBase = 0
      } else if (row.city && item.calcBase === 0) {
        // If salary changed from 0 to non-zero and city is selected, reload injury_base
        loadCityInjuryBase(row.city).then(injuryBase => {
          item.calcBase = injuryBase || salary
        })
      }
      // Otherwise, keep the existing value (loaded from city data)
    }
  })
  row.fundRules.forEach((item: any) => {
    item.calcBase = salary
  })

  row.subtotal = calculateRowSubtotal(row)

  // Auto-calculate after-tax salary if not manually editing
  if (!skipAfterTaxCalc) {
    const socialIndivTotal = row.socialRules.reduce((sum: number, item: any) => {
      return sum + calculateSocialCost(item.calcBase, item.indivRate)
    }, 0)
    const fundIndivTotal = row.fundRules.reduce((sum: number, item: any) => {
      return sum + calculateSocialCost(item.calcBase, item.indivRate)
    }, 0)
    row.afterTaxSalary = Math.round((salary - socialIndivTotal - fundIndivTotal) * 100) / 100
    if (row.afterTaxSalary < 0) row.afterTaxSalary = 0
  }

  // Recalculate contingency costs for this row if it's the currently selected row
  if (index === selectedOptionalRowIndex.value && row.contingencyCosts) {
    row.contingencyCosts.forEach(item => {
      calculateContingencyCostForRow(item, row)
    })
  }
}

// Handle salary change - auto-calculate after-tax salary
function onSalaryChange(index: number) {
  calculateRow(index, false)
}

// Handle after-tax salary change - reverse calculate salary
function onAfterTaxSalaryChange(index: number) {
  const row = positionRows.value[index]
  const afterTaxSalary = row.afterTaxSalary || 0

  if (afterTaxSalary <= 0) {
    row.salary = 0
    calculateRow(index, true)
    return
  }

  // Calculate total individual deduction rate (percentage)
  // Social insurance individual rates
  const socialIndivRateTotal = row.socialRules.reduce((sum: number, item: any) => {
    return sum + (item.indivRate || 0)
  }, 0)
  // Fund individual rate
  const fundIndivRateTotal = row.fundRules.reduce((sum: number, item: any) => {
    return sum + (item.indivRate || 0)
  }, 0)
  // Total deduction rate (as decimal, e.g., 17.5% -> 0.175)
  const totalDeductionRate = (socialIndivRateTotal + fundIndivRateTotal) / 100

  // Reverse calculate salary using the formula:
  // afterTaxSalary = salary * (1 - totalDeductionRate)
  // salary = afterTaxSalary / (1 - totalDeductionRate)
  const denominator = 1 - totalDeductionRate
  if (denominator <= 0) {
    // Invalid rate configuration, fallback to direct assignment
    row.salary = afterTaxSalary
  } else {
    row.salary = Math.round((afterTaxSalary / denominator) * 100) / 100
  }

  // Update calcBase for all rules to match the new salary
  const newSalary = row.salary
  row.socialRules.forEach((item: any) => {
    if (item.type !== '工伤保险') {
      item.calcBase = newSalary
    }
  })
  row.fundRules.forEach((item: any) => {
    item.calcBase = newSalary
  })

  // Recalculate the row (skip after-tax calc to avoid loop)
  calculateRow(index, true)
}

// Calculate all rows
function calculateAll() {
  positionRows.value.forEach((row, index) => {
    calculateRow(index)
  })
  // Recalculate contingency costs for all rows when personnel or salary changes
  positionRows.value.forEach(row => {
    if (row.contingencyCosts) {
      row.contingencyCosts.forEach(item => {
        calculateContingencyCostForRow(item, row)
      })
    }
  })
}

// Add a new position row
function addPositionRow() {
  positionRows.value.push({
    id: String(nextRowId++),
    city: '',
    position: '',
    salary: 0,
    afterTaxSalary: 0,
    personnelCount: 1,
    cycleUnit: 'month',
    serviceCycleCount: 12,
    subtotal: 0,
    unitPrice: 0,
    socialRules: getDefaultSocialRules(),
    fundRules: getDefaultFundRules(),
    mgmtRules: getDefaultMgmtRules(),
    riskRatio: 8.6,
    opsCosts: getDefaultOpsCosts(),
    onDemandCosts: getDefaultOnDemandCosts(),
    contingencyCosts: getDefaultContingencyCosts()
  })
}

// Remove a position row
function removePositionRow(index: number) {
  if (positionRows.value.length > 1) {
    positionRows.value.splice(index, 1)
  }
}

// Handle city change for a specific row
async function onRowCityChange(index: number) {
  const row = positionRows.value[index]
  // Load city rules into this row's own rules
  await loadCitySocialRulesForRow(row, row.city)
  // If this row is the selected one, update the display
  if (index === selectedRowIndex.value) {
    updateSelectedRowCalcBase()
  }
  calculateRow(index)
}

// Load city social rules for a specific row
async function loadCitySocialRulesForRow(row: PositionRow, city: string) {
  const salary = row.salary || 0

  // If city is not selected, use default values
  if (!city) {
    const injuryBase = salary > 0 ? salary : 0
    row.socialRules = [
      { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: salary },
      { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: salary },
      { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: salary },
      { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: injuryBase },
      { type: '生育保险', minBase: 7310, maxBase: 36549, corpRate: 1, indivRate: 0, calcBase: salary },
      { type: '残保金', minBase: 7310, maxBase: 36549, corpRate: 1.5, indivRate: 0, calcBase: salary }
    ]
    row.fundRules = [
      { type: '住房公积金', minBase: 7310, maxBase: 36549, corpRate: 7, indivRate: 7, calcBase: salary }
    ]
    return
  }

  const cityName = getCityName(city)

  try {
    const response = await axios.get(`${API_URL}/city-social-insurance/`, {
      params: { city: cityName }
    })
    let data = null

    if (response.data && response.data.length > 0) {
      data = response.data[0]
    } else {
      // If city not found, try to get the default city's data
      console.log(`City "${cityName}" not found, using default values`)
      const defaultResponse = await axios.get(`${API_URL}/city-social-insurance/`, {
        params: { city: '默认' }
      })
      if (defaultResponse.data && defaultResponse.data.length > 0) {
        data = defaultResponse.data[0]
      }
    }

    if (data) {
      // When salary is 0, injuryBase should also be 0
      const injuryBase = (salary > 0 && data.injury_base) ? data.injury_base : salary

      // Helper function to round rate to avoid floating point precision issues
      const roundRate = (rate: number | null | undefined, defaultValue: number) => {
        if (rate === null || rate === undefined) return defaultValue
        return Math.round(rate * 100 * 100) / 100  // Convert to percentage and round to 2 decimal places
      }

      // Update row's social rules
      // Note: 工伤保险和生育保险的个人比例固定为0（个人不缴纳）
      row.socialRules = [
        { type: '养老保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_pension_rate, 16), indivRate: roundRate(data.indiv_pension_rate, 8), calcBase: salary },
        { type: '医疗保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_medical_rate, 10), indivRate: roundRate(data.indiv_medical_rate, 2), calcBase: salary },
        { type: '失业保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_unemployment_rate, 0.5), indivRate: roundRate(data.indiv_unemployment_rate, 0.5), calcBase: salary },
        { type: '工伤保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_injury_rate, 0.16), indivRate: 0, calcBase: injuryBase },
        { type: '生育保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_maternity_rate, 1), indivRate: 0, calcBase: salary },
        { type: '残保金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_disability_rate, 1.5), indivRate: 0, calcBase: salary }
      ]

      // Update row's fund rules
      row.fundRules = [
        { type: '住房公积金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: Math.round(data.corp_fund_rate * 100 * 100) / 100 || 7, indivRate: Math.round(data.indiv_fund_rate * 100 * 100) / 100 || 7, calcBase: salary }
      ]
    }
  } catch (error) {
    console.error('Failed to load city social insurance rules:', error)
  }
}

// Handle position change for a specific row
function onRowPositionChange(index: number) {
  const row = positionRows.value[index]
  const position = availablePositions.value.find(p => p.id === row.position)
  if (position && position.salary) {
    row.salary = position.salary
    calculateRow(index)
  }
}

// Update the rules displayed in the "Rules & Config" section based on first row's city
async function updateDisplayRules(city: string) {
  const rules = await loadCitySocialRules(city)
  if (rules) {
    // Get the salary from the first position row
    const salary = positionRows.value[0]?.salary || 0

    // Update calcBase for each social rule
    rules.socialRules.forEach((item: any) => {
      if (item.type === '工伤保险') {
        // Use injury_base from city data
        item.calcBase = rules.injuryBase || salary
      } else {
        // Use salary from position row
        item.calcBase = salary
      }
    })

    // Update calcBase for fund rules
    rules.fundRules.forEach((item: any) => {
      item.calcBase = salary
    })

    socialRules.value = rules.socialRules
    fundRules.value = rules.fundRules
  }
}

// Load social insurance rules for a city
async function loadCitySocialRules(city: string) {
  const cityName = getCityName(city)

  // Check cache first
  if (citySocialRulesCache.value[city]) {
    return citySocialRulesCache.value[city]
  }

  try {
    const response = await axios.get(`${API_URL}/city-social-insurance/`, {
      params: { city: cityName }
    })

    let data = null

    if (response.data && response.data.length > 0) {
      data = response.data[0]
    } else {
      // If city not found, try to get the default city's data
      console.log(`City "${cityName}" not found, using default values`)
      const defaultResponse = await axios.get(`${API_URL}/city-social-insurance/`, {
        params: { city: '默认' }
      })
      if (defaultResponse.data && defaultResponse.data.length > 0) {
        data = defaultResponse.data[0]
      }
    }

    if (data) {
      const salary = positionRows.value[0]?.salary || 0
      const injuryBase = data.injury_base || salary

      // Helper function to round rate to avoid floating point precision issues
      const roundRate = (rate: number | null | undefined, defaultValue: number) => {
        if (rate === null || rate === undefined) return defaultValue
        return Math.round(rate * 100 * 100) / 100  // Convert to percentage and round to 2 decimal places
      }

      // Note: 工伤保险和生育保险的个人比例固定为0（个人不缴纳）
      const rules = {
        socialRules: [
          { type: '养老保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_pension_rate, 16), indivRate: roundRate(data.indiv_pension_rate, 8), calcBase: salary },
          { type: '医疗保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_medical_rate, 10), indivRate: roundRate(data.indiv_medical_rate, 2), calcBase: salary },
          { type: '失业保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_unemployment_rate, 0.5), indivRate: roundRate(data.indiv_unemployment_rate, 0.5), calcBase: salary },
          { type: '工伤保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_injury_rate, 0.16), indivRate: 0, calcBase: injuryBase },
          { type: '生育保险', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_maternity_rate, 1), indivRate: 0, calcBase: salary },
          { type: '残保金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_disability_rate, 1.5), indivRate: 0, calcBase: salary }
        ],
        fundRules: [
          { type: '住房公积金', minBase: data.lower_limit, maxBase: data.upper_limit, corpRate: roundRate(data.corp_fund_rate, 7), indivRate: roundRate(data.indiv_fund_rate, 7), calcBase: salary }
        ],
        injuryBase: injuryBase
      }

      // Cache the rules
      citySocialRulesCache.value[city] = rules

      return rules
    }
  } catch (error) {
    console.error('Failed to load city social insurance rules:', error)
  }
  return null
}

// Fetch available cities from backend
async function fetchCities() {
  try {
    console.log('正在获取城市数据...', `${API_URL}/city-social-insurance/`)
    const response = await axios.get(`${API_URL}/city-social-insurance/`)
    console.log('城市社保数据响应:', response.data)
    
    if (!response.data || response.data.length === 0) {
      console.warn('城市社保基准数据为空，请在后台"城市社保基准"模块中导入数据')
      ElMessage.warning('城市数据为空，请在后台系统"城市社保基准"模块中导入数据')
      return
    }
    
    // Extract unique cities
    const uniqueCities = new Map<string, string>()
    response.data.forEach((item: any) => {
      if (item.city && item.city !== '默认') {
        uniqueCities.set(item.city, item.city)
      }
    })
    // Convert to array and sort alphabetically
    cityOptions.value = Array.from(uniqueCities.entries())
      .map(([key, value]) => ({ label: key, value: key }))
      .sort((a, b) => a.label.localeCompare(b.label, 'zh-CN'))
    
    console.log(`成功加载 ${cityOptions.value.length} 个城市选项`)
  } catch (error: any) {
    console.error('获取城市数据失败:', error)
    if (error.response) {
      console.error('响应状态:', error.response.status, '响应数据:', error.response.data)
    }
    ElMessage.error('获取城市数据失败，请检查后端服务是否正常运行')
  }
}

// Fetch available positions
async function fetchPositions() {
  try {
    console.log('正在获取岗位职级数据...', `${API_URL}/outsourced-personnel/`)
    const response = await axios.get(`${API_URL}/outsourced-personnel/`)
    console.log('外包人员岗位数据响应:', response.data)
    
    if (!response.data || response.data.length === 0) {
      console.warn('外包人员岗位数据为空，请在后台"外包人员岗位"模块中导入数据')
      ElMessage.warning('岗位职级数据为空，请在后台系统"外包人员岗位"模块中导入数据')
      return
    }
    
    availablePositions.value = response.data.map((item: any) => {
      // Build display name: 岗位-级别-子类型
      let displayName = item.position
      if (item.level) {
        displayName += `-${item.level}`
      }
      if (item.subtype) {
        displayName += `-${item.subtype}`
      }
      return {
        id: item.id,
        name: displayName,
        position: item.position,
        level: item.level,
        subtype: item.subtype,
        salary: item.tier1_city_salary
      }
    })
    
    console.log(`成功加载 ${availablePositions.value.length} 个岗位选项`)
  } catch (error: any) {
    console.error('获取岗位职级数据失败:', error)
    if (error.response) {
      console.error('响应状态:', error.response.status, '响应数据:', error.response.data)
    }
    ElMessage.error('获取岗位职级数据失败，请检查后端服务是否正常运行')
  }
}

function showHistory() {
  ElMessage.info('历史记录功能开发中...')
}

function resetForm() {
  positionRows.value = [
    {
      id: String(Date.now()),
      city: '',
      position: '',
      salary: 0,
      afterTaxSalary: 0,
      personnelCount: 1,
      cycleUnit: 'month',
      serviceCycleCount: 12,
      subtotal: 0,
      unitPrice: 0,
      socialRules: getDefaultSocialRules(),
      fundRules: getDefaultFundRules(),
      mgmtRules: getDefaultMgmtRules(),
      riskRatio: 8.6,
      opsCosts: getDefaultOpsCosts(),
      onDemandCosts: getDefaultOnDemandCosts()
    }
  ]
  globalParams.value = {
    vatRate: 6,
    paymentCycle: 0,
    riskRatio: 8.6,
    profitRate: 0,
    fundingCostRate: 3
  }
  // Reset selected row indices
  selectedRowIndex.value = 0
  selectedFlexRowIndex.value = 0
  selectedOptionalRowIndex.value = 0
  calculateAll()
}

function showCalcDetails() {
  ElMessage.info('计算详情弹窗开发中...')
}

async function startCalculation() {
  // 计算每个岗位在总成本中的占比，用于分配 finalProjectAmount
  const totalBase = baseSubtotal.value || 1  // 防止除以0

  // 加载用户资料和公司信息
  let userProfile = { name: '', phone: '', department: '' }
  let companyInfo = { company_name: '', company_address: '' }

  try {
    const [profileRes, companiesRes] = await Promise.all([
      axios.get(`${API_URL}/user-profile/`),
      axios.get(`${API_URL}/user-profile/companies`)
    ])

    if (profileRes.data) {
      userProfile = {
        name: profileRes.data.name || '',
        phone: profileRes.data.phone || '',
        department: profileRes.data.department || ''
      }
    }

    if (companiesRes.data && companiesRes.data.length > 0) {
      companyInfo = companiesRes.data[0]
    }
  } catch (err) {
    console.error('加载用户资料失败', err)
  }

  // Prepare preview data
  previewData.value = {
    positionRows: positionRows.value.map(row => {
      // 获取岗位名称：如果 position 是 ID，查找对应的名称；否则直接使用 position 值
      let positionName = row.position
      if (row.position) {
        const pos = availablePositions.value.find(p => p.id === row.position || p.id === Number(row.position))
        if (pos) {
          positionName = pos.name
        }
      }

      // 获取城市名称
      let cityName = row.city
      if (row.city) {
        const city = cityOptions.value.find(c => c.value === row.city)
        if (city) {
          cityName = city.label
        }
      }

      // 计算该岗位的占比，用于分配最终金额
      const rowRatio = (row.subtotal || 0) / totalBase

      return {
        ...row,
        position: positionName,  // 使用岗位名称而非 ID
        city: cityName,          // 使用城市名称
        socialRules: JSON.parse(JSON.stringify(row.socialRules)),
        fundRules: JSON.parse(JSON.stringify(row.fundRules)),
        mgmtRules: JSON.parse(JSON.stringify(row.mgmtRules)),
        rowRatio: rowRatio       // 该岗位在总成本中的占比
      }
    }),
    globalParams: globalParams.value,
    customerName: '客户名称',
    customerAddress: '客户地址',
    projectName: '项目名称',
    // 报价公司信息（从个人设置读取）
    quoteCompanyInfo: {
      companyName: companyInfo.company_name || '报价公司名称',
      contactName: userProfile.name || '联系人',
      contactPhone: userProfile.phone || '',
      department: userProfile.department || ''
    },
    // 传递已计算好的金额，避免预览报价单重新计算
    calculatedAmounts: {
      finalProjectAmount: finalProjectAmount.value,      // 项目总额（最终价格）
      baseSubtotal: baseSubtotal.value,                  // 岗位小计合计
      totalSubtotal: totalSubtotal.value,                // 总成本（含风险金等，不含利润税）
      baseProjectAmount: baseProjectAmount.value,        // 基础项目金额（含利润税，不含账期）
      vatRate: globalParams.value.vatRate ?? 6           // 增值税率
    }
  }
  // Open modal
  isPreviewModalOpen.value = true
}

function closePreviewModal() {
  isPreviewModalOpen.value = false
}

function exportQuotation() {
  ElMessage.info('导出功能开发中...')
}

// Close all dropdowns when clicking outside
function handleClickOutside(event: MouseEvent) {
  const target = event.target as HTMLElement
  // Check if click is inside an autocomplete wrapper or its dropdown
  if (target.closest('.autocomplete-wrapper') || target.closest('.autocomplete-dropdown')) {
    return
  }
  // Close all dropdowns
  openDropdowns.value = {}
}

onMounted(async () => {
  await fetchPositions()
  await fetchCities()
  // Load city rules for each row
  for (let i = 0; i < positionRows.value.length; i++) {
    await loadCitySocialRulesForRow(positionRows.value[i], positionRows.value[i].city)
  }
  // Initialize calcBase values
  updateSelectedRowCalcBase()
  calculateAll()

  // Add click outside handler
  document.addEventListener('click', handleClickOutside)
})

// Cleanup click outside handler on unmount
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.onsite-calculator-page {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  background-color: #0B1120;
  color: white;
  overflow-y: auto;
}

/* Header */
.page-header {
  padding: 1.5rem 2rem;
  background-color: #0f172a;
  border-bottom: 1px solid #1e293b;
}

.breadcrumb {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.breadcrumb-item {
  color: #64748b;
}

.breadcrumb-item.active {
  color: #f8fafc;
  font-weight: 500;
}

.breadcrumb-separator {
  font-size: 0.75rem;
  color: #475569;
}

.header-actions-row {
  display: flex;
  justify-content: space-between;
  align-items: flex-end;
  gap: 2rem;
}

.page-title {
  font-size: 1.75rem;
  font-weight: 700;
  color: white;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.ai-badge {
  font-size: 0.75rem;
  font-weight: 400;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background-color: rgba(19, 91, 236, 0.1);
  border: 1px solid rgba(19, 91, 236, 0.2);
  color: #60a5fa;
}

.page-subtitle {
  color: #94a3b8;
  font-size: 0.875rem;
  margin-top: 0.5rem;
}

.header-buttons {
  display: flex;
  gap: 0.75rem;
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

/* Main Content */
.calculator-content {
  display: flex;
  gap: 1.5rem;
  padding: 1.5rem 2rem;
  flex: 1;
}

.left-column {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  flex: 1;
  min-width: 0;
}

.right-column {
  width: 380px;
  min-width: 380px;
  flex-shrink: 0;
}

/* Card */
.card {
  background-color: #1a202c;
  border-radius: 0.75rem;
  border: 1px solid #2d3748;
  padding: 1.25rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 1.25rem;
  padding-bottom: 0.75rem;
  border-bottom: 1px solid #2d3748;
  position: relative;
}

.rules-header,
.flex-cost-header {
  display: flex;
  justify-content: space-between;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.card-icon {
  color: #135bec;
  font-size: 1.25rem;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: white;
}

.card-title-amount {
  font-size: 0.875rem;
  font-weight: 700;
  color: #135bec;
  padding: 0.25rem 0.5rem;
  background-color: rgba(19, 91, 236, 0.1);
  border-radius: 0.375rem;
}

/* Add Row Button */
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

/* Hide number input spinners (up/down arrows) */
input[type="number"]::-webkit-outer-spin-button,
input[type="number"]::-webkit-inner-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

input[type="number"] {
  -moz-appearance: textfield;
}

/* Position Table */
.position-table-header {
  display: grid;
  grid-template-columns: 0.5fr 1fr 1fr 1.2fr 1.2fr 0.8fr 1fr 1fr 50px;
  gap: 0.5rem;
  padding: 0.75rem 0.5rem;
  background-color: #151b26;
  border-radius: 0.5rem;
  margin-bottom: 0.5rem;
}

.col-header {
  font-size: 0.6875rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  text-align: center;
}

.position-rows {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
}

.position-row {
  display: grid;
  grid-template-columns: 0.5fr 1fr 1fr 1.2fr 1.2fr 0.8fr 1fr 1fr 50px;
  gap: 0.5rem;
  padding: 0.5rem;
  background-color: rgba(35, 43, 59, 0.3);
  border-radius: 0.5rem;
  align-items: center;
  transition: background-color 0.2s;
}

.position-row:hover {
  background-color: rgba(35, 43, 59, 0.5);
}

.col-seq {
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  color: #60a5fa;
}

.row-select,
.row-input {
  width: 100%;
  padding: 0.375rem 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.8125rem;
  text-align: center;
}

.row-select {
  appearance: none;
  cursor: pointer;
}

/* Autocomplete component styles */
.autocomplete-wrapper {
  position: relative;
  width: 100%;
}

.autocomplete-input {
  cursor: text;
}

.autocomplete-input::placeholder {
  color: #64748b;
}

.autocomplete-dropdown {
  position: fixed;
  max-height: 200px;
  overflow-y: auto;
  background-color: #1a202c;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  margin-top: 0.25rem;
  z-index: 9999;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.5);
}

.autocomplete-dropdown-wide {
  min-width: 250px;
  max-width: 350px;
}

.autocomplete-item {
  padding: 0.5rem 0.75rem;
  cursor: pointer;
  color: #cbd5e1;
  font-size: 0.8125rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.autocomplete-item:hover {
  background-color: rgba(19, 91, 236, 0.2);
  color: white;
}

.autocomplete-empty {
  padding: 0.5rem 0.75rem;
  color: #64748b;
  font-size: 0.8125rem;
  text-align: center;
}

/* Scrollbar for autocomplete dropdown */
.autocomplete-dropdown::-webkit-scrollbar {
  width: 6px;
}

.autocomplete-dropdown::-webkit-scrollbar-track {
  background: #0f172a;
}

.autocomplete-dropdown::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 3px;
}

.autocomplete-dropdown::-webkit-scrollbar-thumb:hover {
  background: #475569;
}

.row-select:focus,
.row-input:focus {
  outline: none;
  border-color: #135bec;
}

.row-select option {
  background-color: #1a202c;
}

.input-with-prefix,
.input-with-suffix {
  position: relative;
  display: flex;
  align-items: center;
}

.input-prefix,
.input-suffix {
  position: absolute;
  color: #64748b;
  font-size: 0.6875rem;
}

.input-prefix {
  left: 0.5rem;
}

.input-with-prefix .row-input {
  padding-left: 1.25rem;
}

.input-suffix {
  right: 0.5rem;
}

.input-with-suffix .row-input {
  padding-right: 1.25rem;
}

/* Cycle unit select (styled as text) */
.cycle-unit-select {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  background-color: transparent;
  border: none;
  color: #64748b;
  font-size: 0.6875rem;
  cursor: pointer;
  padding: 0 0.25rem;
  appearance: none;
  -webkit-appearance: none;
  -moz-appearance: none;
}

.cycle-unit-select:focus {
  outline: none;
}

.cycle-unit-select:hover {
  color: #135bec;
}

.subtotal-value {
  font-size: 0.875rem;
  font-weight: 700;
  color: #135bec;
  text-align: center;
}

.delete-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  padding: 0;
  background-color: transparent;
  border: 1px solid #ef4444;
  border-radius: 0.375rem;
  color: #ef4444;
  cursor: pointer;
  transition: all 0.2s;
}

.delete-btn:hover:not(:disabled) {
  background-color: #ef4444;
  color: white;
}

.delete-btn:disabled {
  opacity: 0.3;
  cursor: not-allowed;
  border-color: #475569;
  color: #475569;
}

.delete-btn .material-symbols-outlined {
  font-size: 1rem;
}

/* Total Subtotal */
.total-subtotal {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  margin-top: 0.75rem;
  background: linear-gradient(135deg, #1e293b, #131b2e);
  border: 1px solid rgba(19, 91, 236, 0.3);
  border-radius: 0.5rem;
}

.total-label {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
}

.total-value {
  font-size: 1.25rem;
  font-weight: 700;
  color: #135bec;
}

.current-city-tag {
  font-size: 0.75rem;
  color: #64748b;
  background-color: #0f172a;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.row-filter {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.filter-label {
  font-size: 0.75rem;
  color: #92a4c9;
}

.filter-select {
  padding: 0.375rem 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: white;
  font-size: 0.8125rem;
  cursor: pointer;
  min-width: 150px;
}

.filter-select:focus {
  outline: none;
  border-color: #135bec;
}

/* Vertical actions container */
.vertical-actions {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

/* Global mode switch styles */
.global-mode-switch {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  background-color: #232b3b;
  border-radius: 0.375rem;
}

.switch-label {
  font-size: 0.75rem;
  color: #92a4c9;
  white-space: nowrap;
}

.switch {
  position: relative;
  display: inline-block;
  width: 36px;
  height: 20px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #3c4457;
  transition: 0.3s;
  border-radius: 20px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 2px;
  bottom: 2px;
  background-color: white;
  transition: 0.3s;
  border-radius: 50%;
}

input:checked + .slider {
  background-color: #135bec;
}

input:checked + .slider:before {
  transform: translateX(16px);
}

/* Focus styles for accessibility */
.switch input:focus + .slider {
  box-shadow: 0 0 1px #135bec;
}

.filter-select option {
  background-color: #1a202c;
}

/* Form Grid */
.form-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1.25rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.label-with-tag {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.label-with-link {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.tag-recommended {
  font-size: 0.625rem;
  padding: 0.125rem 0.25rem;
  border-radius: 0.25rem;
  background-color: rgba(234, 179, 8, 0.1);
  border: 1px solid rgba(234, 179, 8, 0.3);
  color: #eab308;
}

.link-text {
  font-size: 0.75rem;
  color: #135bec;
  cursor: pointer;
}

.link-text:hover {
  text-decoration: underline;
}

.select-wrapper,
.input-with-prefix,
.input-with-suffix {
  position: relative;
}

.form-select,
.form-input {
  width: 100%;
  padding: 0.625rem 0.75rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.5rem;
  color: white;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-select {
  appearance: none;
  cursor: pointer;
}

.form-select:focus,
.form-input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.form-select option {
  background-color: #1a202c;
}

.select-arrow {
  position: absolute;
  right: 0.625rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  pointer-events: none;
  font-size: 1.25rem;
}

.input-prefix,
.input-suffix {
  position: absolute;
  color: #64748b;
  font-size: 0.875rem;
}

.input-prefix {
  left: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
}

.input-with-prefix .form-input {
  padding-left: 2rem;
}

.input-suffix {
  right: 0.75rem;
  top: 50%;
  transform: translateY(-50%);
}

.input-with-suffix .form-input {
  padding-right: 2rem;
}

/* Rules Card */
.rules-card {
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.tabs-container {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #2d3748;
  background-color: #151b26;
  padding-right: 12px;
}

.tabs {
  display: flex;
}

.tab-btn {
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

.tab-btn:hover {
  color: white;
  background-color: rgba(255, 255, 255, 0.05);
}

.tab-btn.active {
  color: white;
  border-bottom-color: #135bec;
  background-color: rgba(19, 91, 236, 0.05);
}

.tab-content {
  padding: 1.25rem;
  overflow-x: auto;
  flex: 1;
}

.rules-table {
  width: 100%;
  font-size: 0.875rem;
  text-align: left;
  table-layout: fixed;
}

.rules-table thead {
  background-color: #1f293a;
}

.rules-table th {
  padding: 0.75rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  white-space: nowrap;
}

.rules-table th:first-child {
  border-radius: 0.5rem 0 0 0;
  width: 100px;
}

.rules-table th:nth-child(2) {
  width: 130px;
}

.rules-table th:nth-child(3) {
  width: 110px;
}

.rules-table th:nth-child(4) {
  width: 110px;
}

.rules-table th:last-child {
  border-radius: 0 0.5rem 0 0;
}

.rules-table tbody {
  background-color: rgba(35, 43, 59, 0.3);
}

.rules-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #1e293b;
  white-space: nowrap;
}

.rules-table tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.type-cell {
  font-weight: 500;
  color: white;
}

.calc-base-cell {
  color: #60a5fa;
  font-weight: 500;
}

.calc-base-input {
  width: 100%;
  min-width: 100px;
  padding: 0.375rem 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: #60a5fa;
  font-size: 0.8125rem;
  text-align: right;
}

.calc-base-input:focus {
  outline: none;
  border-color: #135bec;
}

.readonly-input {
  background-color: #1a202c;
  color: #64748b;
  cursor: not-allowed;
}

.corp-rate {
  color: #60a5fa;
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.rate-edit-input {
  width: 60px;
  padding: 0.25rem 0.375rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.25rem;
  color: #60a5fa;
  font-size: 0.8125rem;
  text-align: center;
}

.rate-edit-input:focus {
  outline: none;
  border-color: #135bec;
}

.rate-percent {
  font-size: 0.75rem;
  color: #64748b;
}

.cost-corp {
  color: #4ade80;
  font-weight: 500;
}

.cost-indiv {
  color: #fbbf24;
}

.summary-row {
  background-color: rgba(96, 165, 250, 0.15);
  font-weight: 600;
}

.summary-label {
  text-align: right;
  color: #60a5fa;
}

.summary-value {
  color: #4ade80;
}

.total-row {
  background-color: rgba(74, 222, 128, 0.15);
  font-weight: 600;
}

.total-label {
  text-align: right;
  color: #4ade80;
}

.total-value {
  color: #4ade80;
  text-align: center;
}

.ops-rules {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.ops-item {
  display: flex;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background-color: rgba(35, 43, 59, 0.3);
  border-radius: 0.5rem;
}

.ops-name {
  color: white;
  font-weight: 500;
}

.ops-value {
  color: #94a3b8;
}

/* Management Table */
.mgmt-table {
  width: 100%;
  font-size: 0.875rem;
  text-align: left;
  table-layout: fixed;
}

.mgmt-table thead {
  background-color: #1f293a;
}

.mgmt-table th {
  padding: 0.75rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  white-space: nowrap;
  text-align: center;
  vertical-align: middle;
}

.mgmt-table th:first-child {
  border-radius: 0.5rem 0 0 0;
  width: 100px;
}

.mgmt-table th:nth-child(2) {
  width: 130px;
}

.mgmt-table th:nth-child(3) {
  width: 110px;
}

.mgmt-table th:last-child {
  border-radius: 0 0.5rem 0 0;
}

.mgmt-table tbody {
  background-color: rgba(35, 43, 59, 0.3);
}

.mgmt-table td {
  padding: 0.75rem;
  border-bottom: 1px solid #1e293b;
  white-space: nowrap;
  text-align: center;
  vertical-align: middle;
}

.mgmt-table tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.mgmt-name-cell {
  font-weight: 500;
  color: white;
}

.mgmt-salary-cell {
  color: #94a3b8;
}

.mgmt-rate-cell {
  color: #60a5fa;
}

.rate-input-wrapper {
  position: relative;
  display: inline-block;
  width: 80px;
}

.rate-input {
  width: 100%;
  padding: 0.375rem 1.5rem 0.375rem 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: #60a5fa;
  font-size: 0.875rem;
  font-weight: 600;
  text-align: right;
  transition: all 0.2s;
}

.rate-input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.rate-symbol {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 0.75rem;
  pointer-events: none;
}

.mgmt-amount-cell {
  color: #94a3b8;
  text-align: right;
}

.mgmt-table tfoot {
  background-color: #1a202c;
}

.mgmt-total-row {
  border-top: 2px solid #2d3748;
}

.mgmt-total-row td {
  padding: 0.75rem 1rem;
  font-weight: 600;
}

.mgmt-total-amount {
  color: #135bec;
  text-align: right;
}

/* On-demand Cost Table */
.ondemand-rules {
  width: 100%;
}

.ondemand-table {
  width: 100%;
  font-size: 0.8125rem;
  text-align: left;
}

.ondemand-table thead {
  background-color: #1f293a;
}

.ondemand-table th {
  padding: 0.625rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
}

.ondemand-table th:first-child {
  border-radius: 0.5rem 0 0 0;
}

.ondemand-table th:last-child {
  border-radius: 0 0.5rem 0 0;
}

.ondemand-table tbody {
  background-color: rgba(35, 43, 59, 0.3);
}

.ondemand-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #1e293b;
}

.ondemand-table tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.ondemand-name-cell {
  font-weight: 500;
  color: white;
  white-space: nowrap;
}

.ondemand-desc-cell {
  color: #94a3b8;
}

.ondemand-basis-cell {
  color: #64748b;
  font-size: 0.75rem;
  max-width: 200px;
}

.ondemand-amount-cell {
  text-align: right;
  width: 120px;
}

.amount-input {
  width: 100%;
  max-width: 120px;
  padding: 0.375rem 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: #94a3b8;
  font-size: 0.8125rem;
  text-align: right;
  transition: all 0.2s;
}

.amount-input:focus {
  outline: none;
  border-color: #135bec;
  box-shadow: 0 0 0 2px rgba(19, 91, 236, 0.2);
}

.ondemand-table tfoot {
  background-color: #1a202c;
}

.ondemand-total-row {
  border-top: 2px solid #2d3748;
}

.ondemand-total-row td {
  padding: 0.625rem 0.75rem;
  font-weight: 600;
}

.ondemand-total-amount {
  color: #135bec;
  text-align: right;
}

/* Operations Cost Table */
.ops-rules {
  width: 100%;
}

.ops-table {
  width: 100%;
  font-size: 0.8125rem;
  text-align: left;
}

.ops-table thead {
  background-color: #1f293a;
}

.ops-table th {
  padding: 0.625rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
}

.ops-table th:first-child {
  border-radius: 0.5rem 0 0 0;
}

.ops-table th:last-child {
  border-radius: 0 0.5rem 0 0;
}

.ops-table tbody {
  background-color: rgba(35, 43, 59, 0.3);
}

.ops-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #1e293b;
}

.ops-table tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.ops-name-cell {
  font-weight: 500;
  color: white;
  white-space: nowrap;
}

.ops-category-cell {
  color: #94a3b8;
}

.ops-basis-cell {
  color: #64748b;
  font-size: 0.75rem;
  max-width: 250px;
}

.ops-amount-cell {
  text-align: right;
  width: 120px;
}

.ops-table tfoot {
  background-color: #1a202c;
}

.ops-total-row {
  border-top: 2px solid #2d3748;
}

.ops-total-row td {
  padding: 0.625rem 0.75rem;
  font-weight: 600;
}

.ops-total-amount {
  color: #135bec;
  text-align: right;
}

/* Contingency Cost Table */
.contingency-rules {
  width: 100%;
}

.contingency-table {
  width: 100%;
  font-size: 0.8125rem;
  text-align: left;
}

.contingency-table thead {
  background-color: #1f293a;
}

.contingency-table th {
  padding: 0.625rem 0.75rem;
  font-size: 0.6875rem;
  font-weight: 600;
  color: #92a4c9;
  text-transform: uppercase;
  text-align: center;
  vertical-align: middle;
}

.contingency-table th:first-child {
  border-radius: 0.5rem 0 0 0;
}

.contingency-table th:last-child {
  border-radius: 0 0.5rem 0 0;
}

.contingency-table tbody {
  background-color: rgba(35, 43, 59, 0.3);
}

.contingency-table td {
  padding: 0.625rem 0.75rem;
  border-bottom: 1px solid #1e293b;
  text-align: center;
  vertical-align: middle;
}

.contingency-table tr:hover {
  background-color: rgba(255, 255, 255, 0.05);
}

.contingency-name-cell {
  font-weight: 500;
  color: white;
  white-space: nowrap;
}

.contingency-rate-cell,
.contingency-days-cell,
.contingency-personnel-cell {
  width: 100px;
}

.rate-input,
.days-input,
.personnel-input {
  width: 80px;
  padding: 0.375rem 0.5rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: #94a3b8;
  font-size: 0.8125rem;
  text-align: center;
}

.days-input:focus,
.personnel-input:focus {
  outline: none;
  border-color: #135bec;
}

.contingency-unit-price-cell {
  width: 140px;
}

.unit-price-input {
  width: 100%;
  padding: 0.375rem 0.75rem 0.375rem 1.25rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.375rem;
  color: #94a3b8;
  font-size: 0.8125rem;
  text-align: right;
}

.unit-price-input:focus {
  outline: none;
  border-color: #135bec;
}

/* Readonly styles for contingency table */
.readonly-value {
  display: inline-block;
  padding: 0.375rem 0.5rem;
  color: #94a3b8;
  font-size: 0.8125rem;
  text-align: center;
}

.readonly-unit-price {
  padding: 0.375rem 0.75rem;
  color: #94a3b8;
  font-size: 0.8125rem;
  text-align: center;
}

.contingency-amount-cell {
  color: #94a3b8;
  text-align: right;
  font-weight: 600;
  width: 140px;
  white-space: nowrap;
}

.contingency-table tfoot {
  background-color: #1a202c;
}

.contingency-total-row {
  border-top: 2px solid #2d3748;
}

.contingency-total-row td {
  padding: 0.625rem 0.75rem;
  font-weight: 600;
  text-align: center;
  vertical-align: middle;
}

.contingency-total-amount {
  color: #135bec;
  text-align: right;
  width: 140px;
  white-space: nowrap;
}

.update-info {
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
  margin-top: 1rem;
  font-size: 0.75rem;
  color: #64748b;
}

.info-icon {
  font-size: 0.875rem;
}

/* Project Params */
.project-params {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.param-input {
  width: 100%;
}

/* Summary Card */
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

/* Global Params Section */
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

/* Readonly cost display */
.readonly-cost-display {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
  padding: 0.625rem 0.75rem;
  background-color: #232b3b;
  border: 1px solid #2d3748;
  border-radius: 0.5rem;
}

.cost-value {
  font-size: 1rem;
  font-weight: 700;
  color: #135bec;
}

.cost-formula {
  font-size: 0.6875rem;
  color: #64748b;
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

.price-symbol {
  font-size: 1rem;
  color: #64748b;
  font-weight: 400;
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

.sub-price-item.highlight {
  border-color: rgba(19, 91, 236, 0.3);
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

.sub-price-item.highlight .sub-price-value {
  color: #135bec;
}

.sub-price-note {
  font-size: 0.625rem;
  color: #64748b;
  margin-top: 0.25rem;
}

/* Breakdown */
.breakdown-section {
  flex: 1;
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

/* AI Insight */
.ai-insight {
  margin-top: 1rem;
  background: linear-gradient(135deg, #1e293b, #131b2e);
  border: 1px solid rgba(19, 91, 236, 0.2);
  border-radius: 0.5rem;
  padding: 0.75rem;
}

.insight-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.ai-icon {
  color: #135bec;
  font-size: 1.125rem;
}

.insight-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: white;
}

.insight-text {
  font-size: 0.6875rem;
  color: #94a3b8;
  line-height: 1.5;
  margin: 0;
}

/* Actions */
.summary-actions {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  margin-top: 1.5rem;
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

/* Mobile Footer */
.mobile-footer {
  display: none;
}

/* Scrollbar */
.onsite-calculator-page::-webkit-scrollbar {
  width: 8px;
}

.onsite-calculator-page::-webkit-scrollbar-track {
  background: #0f172a;
}

.onsite-calculator-page::-webkit-scrollbar-thumb {
  background: #374151;
  border-radius: 4px;
}

.onsite-calculator-page::-webkit-scrollbar-thumb:hover {
  background: #4a5568;
}

/* Responsive */
@media (max-width: 1024px) {
  .form-grid {
    grid-template-columns: repeat(2, 1fr);
  }

  .calculator-content {
    flex-direction: column;
  }

  .right-column {
    width: 100%;
    min-width: 0;
  }
}

@media (max-width: 768px) {
  .page-header {
    padding: 1rem;
  }

  .header-actions-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .page-title {
    font-size: 1.25rem;
  }

  .calculator-content {
    padding: 1rem;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .right-column {
    display: none;
  }

  .mobile-footer {
    display: flex;
    position: fixed;
    bottom: 0;
    left: 0;
    right: 0;
    background-color: #1a202c;
    border-top: 1px solid #2d3748;
    padding: 1rem;
    justify-content: space-between;
    align-items: center;
    z-index: 100;
  }

  .mobile-label {
    font-size: 0.75rem;
    color: #92a4c9;
  }

  .mobile-price {
    font-size: 1.25rem;
    font-weight: 700;
    color: white;
  }

  .mobile-calc-btn {
    padding: 0.5rem 1.5rem;
    background-color: #135bec;
    color: white;
    font-weight: 700;
    border-radius: 0.5rem;
    border: none;
    cursor: pointer;
  }
}
</style>
