<template>
  <div class="onsite-calculator-page" :class="{ 'embedded-mode': embedded, 'korea-mode': isKorea }">
    <!-- Header (hidden when embedded) -->
    <div v-if="!embedded" class="page-header">
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
          <label class="header-btn country-select-btn" title="切换驻场报价国家">
            <span class="material-symbols-outlined">public</span>
            <span>国家选择</span>
            <select v-model="selectedCountry" @change="onCountryChange">
              <option value="china">中国大陆</option>
              <option value="korea">韩国</option>
            </select>
          </label>
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
            <div class="col-header col-salary">税前月薪{{ isKorea ? '（KRW）' : '' }}</div>
            <div v-if="!isKorea" class="col-header">税后工资</div>
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
                    @click="onCityClick(row, row.id, $event)"
                    @input="onCityInput(row, row.id, $event)"
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
                    @click="onPositionClick(row, row.id, $event)"
                    @input="onPositionInput(row, row.id, $event)"
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
                  <span class="input-prefix">{{ costCurrencySymbol }}</span>
                  <input
                    v-model.number="row.salary"
                    class="row-input"
                    type="number"
                    :min="getSalaryMin(row)"
                    :max="getSalaryMax(row)"
                    :title="getSalaryRangeTitle(row)"
                    @input="onSalaryChange(index)"
                    @blur="enforceSalaryBounds(index)"
                  />
                </div>
                <div
                  v-if="row.salarySource && row.salarySource !== 'exact' && row.salarySource !== 'manual'"
                  class="salary-source-hint"
                  :title="getSalarySourceTitle(row)"
                >
                  参考值{{ row.salarySourceCity ? `（${row.salarySourceCity}）` : '' }}
                </div>
                <div
                  v-if="getSalaryRangeTitle(row)"
                  class="salary-range-hint"
                  :title="getSalaryRangeTitle(row)"
                >
                  {{ getSalaryRangeTitle(row) }}
                </div>
              </div>
              <div v-if="!isKorea" class="col-salary">
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
                其他成本构成（月度）
                <span class="card-title-amount">{{ formatCurrency(otherCostMonthly) }}</span>
              </h3>
            </div>
            <div class="header-right">
              <div class="other-cost-actions">
                <button
                  class="add-row-btn suggest-value-btn"
                  :class="{ active: suggestedValuesApplied }"
                  :title="suggestedValuesApplied ? '再次点击清空所有建议值' : '点击填充所有建议值'"
                  @click="toggleSuggestedOtherCostValues"
                >
                  <span class="material-symbols-outlined">auto_fix_high</span>
                  应用建议值
                </button>
                <div class="global-mode-switch">
                  <label class="switch-label">全局调整</label>
                  <label class="switch">
                    <input type="checkbox" v-model="otherCostGlobalMode" />
                    <span class="slider"></span>
                  </label>
                </div>
              </div>
              <div class="row-filter">
                <label class="filter-label">筛选岗位序号:</label>
                <select v-model="selectedOtherCostRowIndex" class="filter-select">
                  <option v-for="(row, index) in positionRows" :key="row.id" :value="index">
                    序号 {{ index + 1 }} - {{ row.city ? getCityName(row.city) : '请选择' }}
                  </option>
                </select>
              </div>
            </div>
          </div>
          <div class="other-cost-groups">
            <section
              v-for="group in selectedRowOtherCostGroups"
              :key="group.category"
              class="other-cost-group"
              :class="{ collapsed: isOtherCostGroupCollapsed(group.category) }"
            >
              <div class="other-cost-group-header">
                <div class="other-cost-group-title">
                  <button
                    class="collapse-toggle-btn"
                    type="button"
                    :aria-label="isOtherCostGroupCollapsed(group.category) ? `展开${group.category}` : `折叠${group.category}`"
                    :title="isOtherCostGroupCollapsed(group.category) ? '展开明细' : '折叠明细'"
                    @click="toggleOtherCostGroup(group.category)"
                  >
                    <span class="material-symbols-outlined">
                      {{ isOtherCostGroupCollapsed(group.category) ? 'keyboard_arrow_right' : 'keyboard_arrow_down' }}
                    </span>
                  </button>
                  <h4>{{ group.category }}</h4>
                </div>
                <span>{{ formatCurrency(group.total) }}</span>
              </div>
              <table v-show="!isOtherCostGroupCollapsed(group.category)" class="mgmt-table other-cost-table">
                <thead>
                  <tr>
                    <th>成本项目</th>
                    <th>计算方式</th>
                    <th>测算依据</th>
                    <th>输入值/比例</th>
                    <th>月度金额/人</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="entry in group.items" :key="`${entry.item.category}-${entry.item.name}`">
                    <td class="mgmt-name-cell" :title="entry.item.name">{{ entry.item.name }}</td>
                    <td class="mgmt-salary-cell" :title="entry.item.calculation">{{ entry.item.calculation }}</td>
                    <td class="mgmt-salary-cell" :title="entry.item.basis">{{ entry.item.basis }}</td>
                    <td class="mgmt-rate-cell">
                      <div class="rate-input-wrapper">
                        <input
                          :value="entry.item.value"
                          @input="onOtherCostValueChange(entry.index, ($event.target as HTMLInputElement).value)"
                          class="rate-input"
                          type="number"
                          :step="getOtherCostStep(entry.item)"
                        />
                        <span class="rate-symbol">{{ getOtherCostValueSuffix(entry.item) }}</span>
                      </div>
                    </td>
                    <td class="mgmt-amount-cell">{{ formatCurrency(entry.item.amount) }}</td>
                  </tr>
                </tbody>
                <tfoot>
                  <tr class="mgmt-total-row">
                    <td colspan="4">{{ group.category }}小计（当前岗位月度）</td>
                    <td class="mgmt-total-amount">{{ formatCurrency(group.total) }}</td>
                  </tr>
                </tfoot>
              </table>
            </section>

            <div class="other-cost-grand-total">
              <div>
                <span>其他成本小计（当前岗位月度）</span>
                <strong>{{ formatCurrency(selectedRowOtherCostTotal) }}</strong>
              </div>
              <div>
                <span>其他成本小计（全部岗位月度）</span>
                <strong>{{ formatCurrency(otherCostMonthly) }}</strong>
              </div>
            </div>
          </div>
        </div>

        <!-- Section 3: Rules & Config -->
        <div class="card rules-card">
          <div class="card-header rules-header">
            <div class="header-left">
              <span class="material-symbols-outlined card-icon">tune</span>
              <h3 class="card-title">
                人力成本（月度）
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
                  <th v-if="!isKorea">个人比例</th>
                  <th>社保成本（公司）</th>
                  <th v-if="!isKorea">社保成本（个人）</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(item, idx) in selectedRowSocialRules" :key="item.type">
                  <td class="type-cell">{{ item.type }}</td>
                  <td class="calc-base-cell">
                    <input
                      v-if="item.type === '工伤保险' && !isKorea"
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
                  <td v-if="!isKorea">
                    <input v-model.number="item.indivRate" class="rate-edit-input" type="number" step="0.01" min="0" @input="onRateChange('social', idx)" />
                    <span class="rate-percent">%</span>
                  </td>
                  <td class="cost-corp">{{ formatCurrency(calculateSocialCost(item.calcBase, item.corpRate)) }}</td>
                  <td v-if="!isKorea" class="cost-indiv">{{ formatCurrency(calculateSocialCost(item.calcBase, item.indivRate)) }}</td>
                </tr>
                <tr class="summary-row">
                  <td :colspan="isKorea ? 3 : 4" class="summary-label">{{ isKorea ? '雇主保险小计' : '社保成本小计' }}（当前岗位月度）</td>
                  <td class="summary-value">{{ formatCurrency(selectedSocialCorpTotal) }}</td>
                  <td v-if="!isKorea" class="summary-value">{{ formatCurrency(selectedSocialIndivTotal) }}</td>
                </tr>
                <tr class="summary-row">
                  <td :colspan="isKorea ? 3 : 4" class="summary-label">{{ isKorea ? '雇主保险小计' : '社保成本小计' }}（全部岗位总计）</td>
                  <td class="summary-value">{{ formatCurrency(allRowsSocialCorpTotal) }}</td>
                  <td v-if="!isKorea" class="summary-value">{{ formatCurrency(allRowsSocialIndivTotal) }}</td>
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
              <span>{{ isKorea ? '韩国规则：NPS基数上限 6,170,000 KRW；比例可手动调整' : '数据最后更新: 2024-01-15 (AI自动同步)' }}</span>
            </div>
          </div>
        </div>

        <!-- Section 4: Optional Cost -->
        <div v-if="false" class="card optional-cost-card">
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
              <div v-if="!isKorea" class="global-param-item">
                <label class="param-label">账期</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.paymentCycle"
                    class="param-input"
                    type="number"
                    @input="calculateAll"
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
              <div v-if="!isKorea" class="global-param-item">
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
              <div v-if="isKorea" class="global-param-item">
                <label class="param-label">我方管理费率</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.managementRate"
                    class="param-input"
                    type="number"
                    min="0"
                    @input="calculateAll"
                  />
                  <span class="input-suffix">%</span>
                </div>
              </div>
              <div v-if="isKorea" class="global-param-item">
                <label class="param-label">KRW/CNY 汇率</label>
                <div class="input-with-suffix">
                  <input
                    v-model.number="globalParams.exchangeRate"
                    class="param-input exchange-rate-input"
                    type="number"
                    min="0"
                    step="0.000001"
                    @input="calculateAll"
                  />
                  <span class="input-suffix">CNY</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Summary Numbers -->
          <div class="summary-numbers">
            <div class="main-price highlight">
              <p class="price-label">项目总额</p>
              <div class="price-value">
                {{ formatQuoteCurrency(finalProjectAmount) }}
              </div>
              <div class="price-trend">
                <span class="material-symbols-outlined trend-icon">receipt_long</span>
                含利润率及增值税
              </div>
            </div>

            <div class="sub-prices">
              <div class="sub-price-item">
                <p class="sub-price-label">岗位小计总额</p>
                <div class="sub-price-value">{{ formatQuoteCurrency(positionSubtotal) }}</div>
                <div class="sub-price-note">共 {{ totalPersonnel }} 人 / {{ totalCycles }}</div>
              </div>
              <div class="sub-price-item">
                <p class="sub-price-label">预估总毛利</p>
                <div class="sub-price-value">{{ formatQuoteCurrency(totalGrossProfit) }}</div>
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
                  <span class="breakdown-amount">{{ formatQuoteCurrency(item.amount) }}</span>
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
      :mode="previewModalMode"
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

const props = withDefaults(defineProps<{
  embedded?: boolean
}>(), {
  embedded: false
})

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'
type CountryMode = 'china' | 'korea'

const selectedCountry = ref<CountryMode>('china')
const isKorea = computed(() => selectedCountry.value === 'korea')
const costCurrencySymbol = computed(() => isKorea.value ? '₩' : '¥')

// Router
const router = useRouter()

// Preview Modal State
const isPreviewModalOpen = ref(false)
const previewModalMode = ref<'preview' | 'export'>('preview')
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
  country?: CountryMode
  city: string
  position: string
  salary: number
  // 薪资来源：exact=城市精确命中 / provincial_capital=省会参考 / national_baseline=全国基准 / manual=手动输入
  salarySource?: string
  salarySourceCity?: string
  salaryManuallyEdited?: boolean
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
  otherCosts: OtherCostItem[]
}

interface PositionOption {
  id: number
  name: string
  position: string
  level: string
  levelRank: number
  sequenceType: string
  category: string
  systemSalaryMax: number | null
  systemSalaryMin: number | null
  city?: string
  monthlySalaryKrw?: number
}

// Social rule item
interface SocialRuleItem {
  type: string
  minBase: number
  maxBase: number
  corpRate: number
  indivRate: number
  calcBase: number
  // 工伤保险专用：城市独立工伤基数（无则按月薪封顶取值）
  injuryBaseFixed?: number
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

interface CityHardCostRules {
  socialRules: SocialRuleItem[]
  fundRules: FundRuleItem[]
  injuryBase: number
}

// Management rule item
interface MgmtRuleItem {
  name: string
  rateValue: number
  rate: string
  amount: number
}

type OtherCostFormula =
  | 'fixed'
  | 'salaryRate'
  | 'fixedMonthlySpread'
  | 'benchReserve'
  | 'fundingOccupancy'
  | 'badDebtReserve'
  | 'laborDisputeReserve'
  | 'severance'
  | 'koreaBaseRate'

interface OtherCostItem {
  category: string
  name: string
  formula: OtherCostFormula
  calculation: string
  basis: string
  value: number
  amount: number
}

// Default social rules template
const getDefaultSocialRules = (): SocialRuleItem[] => [
  { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: 0 },
  { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: 0 },
  { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: 0 },
  { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: 0 },
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

const OTHER_COST_MONTHLY_FACTOR = 1.33

const getDefaultKoreaSocialRules = (salary = 0): SocialRuleItem[] => [
  { type: '国民年金（NPS）', minBase: 0, maxBase: 6170000, corpRate: 4.5, indivRate: 0, calcBase: clampBase(salary, 0, 6170000) },
  { type: '国民健康保险（NHI）', minBase: 0, maxBase: 0, corpRate: 4.004, indivRate: 0, calcBase: salary },
  { type: '就业保险', minBase: 0, maxBase: 0, corpRate: 0.9, indivRate: 0, calcBase: salary },
  { type: '工伤保险', minBase: 0, maxBase: 0, corpRate: 0.73, indivRate: 0, calcBase: salary }
]

const getDefaultKoreaOtherCosts = (): OtherCostItem[] => [
  { category: '员工直接成本', name: '退职金月摊销', formula: 'severance', calculation: '税前月薪÷12', basis: '无论项目周期长短均按月预提', value: 12, amount: 0 },
  { category: '韩国EOR/挂靠公司服务费', name: 'EOR管理服务费', formula: 'salaryRate', calculation: '税前月薪×EOR费率', basis: '韩国当地EOR公司服务费', value: 12, amount: 0 },
  { category: '汇率风险及跨境费用', name: '汇率风险缓冲', formula: 'koreaBaseRate', calculation: '直接成本基数×缓冲比例', basis: '对冲KRW/CNY汇率波动风险', value: 3, amount: 0 },
  { category: '汇率风险及跨境费用', name: '跨境汇款手续费', formula: 'koreaBaseRate', calculation: '直接成本基数×手续费率', basis: '服务贸易外汇通道手续费', value: 0.5, amount: 0 }
]

// 2025 版驻场服务其他成本模板，对应 Excel「实际报价测算」成本构成 rows 35-78。
const getDefaultOtherCosts = (): OtherCostItem[] => [
  { category: '直接人力成本', name: '月度福利费', formula: 'fixed', calculation: '固定金额', basis: '餐补', value: 0, amount: 0 },
  { category: '直接人力成本', name: '通讯交通补贴', formula: 'fixed', calculation: '固定金额', basis: '通讯、交通等补贴', value: 0, amount: 0 },
  { category: '直接人力成本', name: '商业保险/雇主责任险（医疗10W，身故100W，身残按照比例支付）', formula: 'fixed', calculation: '固定金额', basis: '每人每月（每月固定金额根据保额计算）', value: 0, amount: 0 },
  { category: '直接人力成本', name: '商业保险/意外险10W', formula: 'fixed', calculation: '固定金额', basis: '每人每月（每月固定金额根据保额计算）', value: 0, amount: 0 },
  { category: '直接人力成本', name: '体检费摊销', formula: 'fixed', calculation: '年度体检费/12（年度体检费600）', basis: '按12个月摊销', value: 0, amount: 0 },
  { category: '直接人力成本', name: '节日福利摊销', formula: 'fixed', calculation: '年度节日福利/12（中秋/端午/春节等，全年累加总金额）', basis: '按12个月摊销', value: 0, amount: 0 },
  { category: '直接人力成本', name: '加班费', formula: 'fixed', calculation: '根据项目实际情况按工时计算', basis: '每人每月', value: 0, amount: 0 },
  { category: '直接人力成本', name: '其他员工福利/补贴', formula: 'fixed', calculation: '固定金额', basis: '每人每月', value: 0, amount: 0 },
  { category: '人员获取成本', name: '招聘成本摊销', formula: 'salaryRate', calculation: '税前工资×招聘成本比例系数', basis: '系数取值范围1.5%-5%，建议取值1.5%（包含背调测评费用）', value: 0, amount: 0 },
  { category: '人员获取成本', name: '内推奖金摊销', formula: 'fixed', calculation: '内推奖金/摊销月数/项目人数', basis: '内推奖金/内推奖金摊销月数,无则填0/建议12个月', value: 0, amount: 0 },
  { category: '人员获取成本', name: '入职体检费用摊销', formula: 'fixedMonthlySpread', calculation: '个人入职单次体检费用/12', basis: '建议摊销12个月，无则填0', value: 0, amount: 0 },
  { category: '人员稳定成本', name: '人员替换/空档风险', formula: 'salaryRate', calculation: '税前工资×空档风险比例系数', basis: '取值范围2%-5%，建议取值2%', value: 0, amount: 0 },
  { category: '人员稳定成本', name: '待岗成本储备', formula: 'benchReserve', calculation: '税前工资×待岗概率×2/12', basis: '待岗概率5%；待岗2月；项目周期12月（可按项目调整待岗概率及公式中月数）', value: 0, amount: 0 },
  { category: '人员稳定成本', name: '项目交接期成本/TT期成本人员成本', formula: 'fixed', calculation: '计划总费用/人数/摊销月数', basis: '每人每月', value: 0, amount: 0 },
  { category: '人员稳定成本', name: '培训成本摊销', formula: 'salaryRate', calculation: '税前工资×培训比例系数', basis: '培训系数建议取值1%，取值范围是0.5%-5%', value: 0, amount: 0 },
  { category: '交付管理成本', name: 'PM/交付管理分摊', formula: 'salaryRate', calculation: '税前工资×系数', basis: '建议1.5%-8%', value: 0, amount: 0 },
  { category: '交付管理成本', name: '质量管理成本', formula: 'salaryRate', calculation: '税前工资×质量管理比例系数', basis: '质量管理比例,质量检查、交付管理,建议取值范围0.5-1.5%（PMO）', value: 0, amount: 0 },
  { category: '交付管理成本', name: 'SLA/KPI管理成本', formula: 'fixed', calculation: '根据实际项目计算', basis: '根据实际项目计算', value: 0, amount: 0 },
  { category: '后台职能成本', name: 'HR分摊', formula: 'salaryRate', calculation: '税前工资×HR比例系数', basis: 'HR管理分摊比例，取值范围1-3%，建议取值1.5%', value: 0, amount: 0 },
  { category: '后台职能成本', name: '财务分摊', formula: 'salaryRate', calculation: '税前工资×财务比例系数', basis: '财务分摊比例，取值范围0.05%-1%，建议取值0.05%', value: 0, amount: 0 },
  { category: '后台职能成本', name: '法务分摊', formula: 'salaryRate', calculation: '税前工资×法务比例系数', basis: '法务分摊比例，风险处理，取值范围0.05%-1%，建议取值0.05%', value: 0, amount: 0 },
  { category: '后台职能成本', name: '行政分摊', formula: 'salaryRate', calculation: '税前工资×行政比例系数', basis: '行政分摊比例，取值范围0.05%-1%，建议取值0.05%', value: 0, amount: 0 },
  { category: '后台职能成本', name: 'IT系统/OA/账号/邮箱分摊', formula: 'fixed', calculation: '固定金额', basis: '每人每月', value: 0, amount: 0 },
  { category: '后台职能成本', name: '总部综合管理费', formula: 'salaryRate', calculation: '税前工资×总部管理费比例', basis: '总部综合管理费比例，取值范围0.05%-1%，建议取值0.05%', value: 0, amount: 0 },
  { category: '商务客户成本', name: '销售/客户维护分摊', formula: 'salaryRate', calculation: '税前工资×摊销系数', basis: '建议取值0.5%，取值范围0.5%-5%/或此项可根据项目情况计入销售成本', value: 0, amount: 0 },
  { category: '设备办公成本', name: '电脑折旧', formula: 'fixed', calculation: '电脑金额/折旧月数', basis: '单人电脑设备金额/一般24-36个月', value: 0, amount: 0 },
  { category: '设备办公成本', name: '软件授权', formula: 'fixed', calculation: '月度授权费', basis: '软件授权月费', value: 0, amount: 0 },
  { category: '设备办公成本', name: '办公用品', formula: 'fixed', calculation: '月摊销', basis: '办公用品月摊销', value: 0, amount: 0 },
  { category: '设备办公成本', name: '工位/办公场地', formula: 'fixed', calculation: '月摊销', basis: '工位/办公场地月摊销，如客户提供工位可填0', value: 0, amount: 0 },
  { category: '差旅异地成本', name: '差旅摊销（交通、食宿、差旅补贴）', formula: 'fixed', calculation: '项目差旅总预算/人数/摊销月数', basis: '每人每月', value: 0, amount: 0 },
  { category: '差旅异地成本', name: '团建员工关怀摊销', formula: 'fixed', calculation: '费用总预算/人数/摊销月数', basis: '每人每月', value: 0, amount: 0 },
  { category: '资金风险成本', name: '资金占用成本', formula: 'fundingOccupancy', calculation: '月成本×账期×年化利率/12', basis: '账期3个月；年化利率3.5%', value: 0, amount: 0 },
  { category: '资金风险成本', name: '坏账风险准备', formula: 'badDebtReserve', calculation: '月成本×坏账比例', basis: '建议取值0.5%，取值范围0.5%-3%', value: 0, amount: 0 },
  { category: '资金风险成本', name: '劳动纠纷风险准备', formula: 'laborDisputeReserve', calculation: '税前工资×劳动风险比例', basis: '建议取值8.33%，取值范围8.33%-16.6%/月或月薪/12', value: 0, amount: 0 },
  { category: '资金风险成本', name: '赔付/违约风险准备', formula: 'salaryRate', calculation: '阶段成本×违约风险比例', basis: '赔付/违约风险比例，无则填0，按照实际项目计算', value: 0, amount: 0 }
]

function createPositionRow(country: CountryMode, option?: PositionOption): PositionRow {
  const salary = country === 'korea' ? (option?.monthlySalaryKrw || 0) : 0
  return {
    id: String(nextRowId++),
    country,
    city: country === 'korea' ? (option?.city || '首尔') : '',
    position: option ? String(option.id) : '',
    salary,
    afterTaxSalary: 0,
    personnelCount: 1,
    cycleUnit: 'month',
    serviceCycleCount: 12,
    subtotal: 0,
    unitPrice: 0,
    socialRules: country === 'korea' ? getDefaultKoreaSocialRules(salary) : getDefaultSocialRules(),
    fundRules: country === 'korea' ? [] : getDefaultFundRules(),
    mgmtRules: getDefaultMgmtRules(),
    riskRatio: 8.6,
    opsCosts: getDefaultOpsCosts(),
    onDemandCosts: getDefaultOnDemandCosts(),
    contingencyCosts: getDefaultContingencyCosts(),
    otherCosts: country === 'korea' ? getDefaultKoreaOtherCosts() : getDefaultOtherCosts()
  }
}

// Position rows (multi-line support)
const positionRows = ref<PositionRow[]>([
  {
    id: '1',
    country: 'china',
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
    contingencyCosts: getDefaultContingencyCosts(),
    otherCosts: getDefaultOtherCosts()
  }
])

// Selected row index for filtering rules display (人力成本)
const selectedRowIndex = ref(0)

// Selected row index for flexible cost (灵活人力成本)
const selectedFlexRowIndex = ref(0)

// Selected row index for optional cost (可选人力成本)
const selectedOptionalRowIndex = ref(0)
const selectedOtherCostRowIndex = ref(0)

// Global mode switches for each section (全局模式开关)
// When enabled, changes apply to all positions instead of just the selected one
const flexCostGlobalMode = ref(false)  // 灵活人力成本全局模式
const hardCostGlobalMode = ref(false)  // 人力成本全局模式
const optionalCostGlobalMode = ref(false)  // 可选人力成本全局模式
const otherCostGlobalMode = ref(false)  // 其他成本全局模式

// Global parameters (VAT rate and payment cycle)
const globalParams = ref({
  vatRate: 6,
  paymentCycle: 90,
  profitRate: 0,
  fundingCostRate: 3.5,  // 年化资金成本率，默认 3.5%
  managementRate: 0,
  exchangeRate: 1
})

const countryGlobalParams: Record<CountryMode, typeof globalParams.value> = {
  china: { vatRate: 6, paymentCycle: 90, profitRate: 0, fundingCostRate: 3.5, managementRate: 0, exchangeRate: 1 },
  korea: { vatRate: 6, paymentCycle: 0, profitRate: 8, fundingCostRate: 0, managementRate: 12, exchangeRate: 0.004403 }
}

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
function updateDropdownPosition(rowId: string, field: string, event: Event) {
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
  const pos = availablePositions.value.find(p => p.id === Number(row.position))
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

// Handle city input click - reopen dropdown if it was closed while input kept focus
// (e.g. after selecting an option the input may stay focused, so no focus event fires on the next click)
function onCityClick(row: PositionRow, rowId: string, event: MouseEvent) {
  if (isDropdownOpen(rowId, 'city')) return
  const currentDisplay = getCityDisplayValue(row)
  setSearchQuery(rowId, 'city', currentDisplay)
  openDropdowns.value[`${rowId}-city`] = true
  updateDropdownPosition(rowId, 'city', event)
}

// Handle city input - update search query.
// If the dropdown is closed while the user edits (any missed open trigger),
// open it first; otherwise the rerender would restore the old display value.
function onCityInput(row: PositionRow, rowId: string, event: Event) {
  const value = (event.target as HTMLInputElement).value
  if (!isDropdownOpen(rowId, 'city')) {
    openDropdowns.value[`${rowId}-city`] = true
    updateDropdownPosition(rowId, 'city', event)
  }
  setSearchQuery(rowId, 'city', value)
}

// Handle position input click - reopen dropdown if it was closed while input kept focus
// (e.g. after selecting an option the input may stay focused, so no focus event fires on the next click)
function onPositionClick(row: PositionRow, rowId: string, event: MouseEvent) {
  if (isDropdownOpen(rowId, 'position')) return
  const currentDisplay = getPositionDisplayValue(row)
  setSearchQuery(rowId, 'position', currentDisplay)
  openDropdowns.value[`${rowId}-position`] = true
  updateDropdownPosition(rowId, 'position', event)
}

// Handle position input - update search query.
// If the dropdown is closed while the user edits (any missed open trigger),
// open it first; otherwise the rerender would restore the old display value.
function onPositionInput(row: PositionRow, rowId: string, event: Event) {
  const value = (event.target as HTMLInputElement).value
  if (!isDropdownOpen(rowId, 'position')) {
    openDropdowns.value[`${rowId}-position`] = true
    updateDropdownPosition(rowId, 'position', event)
  }
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
    const oldPosition = row.position
    if (matchedPos) {
      row.position = matchedPos.id
    } else {
      // Use custom input as the position value
      row.position = searchQuery
    }
    // 命中标准岗位且发生变化时联动取薪
    if (matchedPos && oldPosition !== row.position) {
      const index = positionRows.value.findIndex(r => r.id === row.id)
      if (index !== -1) {
        onRowPositionChange(index)
      }
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
const ruleTabs = computed(() => isKorea.value
  ? [{ key: 'social', label: '韩国雇主保险规则' }]
  : [
      { key: 'social', label: '社保规则' },
      { key: 'fund', label: '公积金规则' }
    ]
)

// Optional cost tabs
const activeOptionalTab = ref('ops')
const optionalCostTabs = [
  { key: 'ops', label: '运营成本' },
  { key: 'ondemand', label: '按需成本' },
  { key: 'contingency', label: '机动成本' }
]

// Position data
const availablePositions = ref<PositionOption[]>([])

function getPositionSalaryBounds(row: PositionRow): { min: number | null; max: number | null } {
  const position = availablePositions.value.find(item => item.id === Number(row.position))
  if (!position) return { min: null, max: null }

  const min = position.systemSalaryMin == null ? Number.NaN : Number(position.systemSalaryMin)
  const max = position.systemSalaryMax == null ? Number.NaN : Number(position.systemSalaryMax)
  return {
    min: Number.isFinite(min) && min >= 0 ? min : null,
    max: Number.isFinite(max) && max >= 0 ? max : null
  }
}

function getSalaryMin(row: PositionRow): number | undefined {
  return getPositionSalaryBounds(row).min ?? undefined
}

function getSalaryMax(row: PositionRow): number | undefined {
  return getPositionSalaryBounds(row).max ?? undefined
}

function getSalaryRangeTitle(row: PositionRow): string {
  const { min, max } = getPositionSalaryBounds(row)
  if (min == null && max == null) return ''
  if (min != null && max != null) {
    return `允许范围 ¥${formatNumber(min)} - ¥${formatNumber(max)}`
  }
  return min != null
    ? `最低 ¥${formatNumber(min)}`
    : `最高 ¥${formatNumber(max as number)}`
}

function clampSalaryToPositionBounds(
  row: PositionRow,
  enforceMinimum: boolean,
  notify = false
): boolean {
  const { min, max } = getPositionSalaryBounds(row)
  const currentSalary = Number(row.salary) || 0
  let nextSalary = Math.max(0, currentSalary)

  if (max != null && nextSalary > max) nextSalary = max
  if (enforceMinimum && min != null && nextSalary < min) nextSalary = min

  if (nextSalary === currentSalary) return false
  row.salary = nextSalary
  if (notify) {
    ElMessage.warning(`税前月薪已调整为岗位允许范围：${getSalaryRangeTitle(row)}`)
  }
  return true
}

// City social rules cache
const citySocialRulesCache = ref<Record<string, any>>({})

// Rules data
const socialRules = ref([
  { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: 0 },
  { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: 0 },
  { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: 0 },
  { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: 0 },
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

const selectedRowOtherCosts = computed(() => {
  const row = positionRows.value[selectedOtherCostRowIndex.value]
  if (!row) return getDefaultOtherCosts()
  recalculateOtherCostsForRow(row)
  return row.otherCosts || getDefaultOtherCosts()
})

const chinaOtherCostCategoryOrder = [
  '直接人力成本',
  '人员获取成本',
  '人员稳定成本',
  '交付管理成本',
  '后台职能成本',
  '商务客户成本',
  '设备办公成本',
  '差旅异地成本',
  '资金风险成本'
]

const koreaOtherCostCategoryOrder = [
  '员工直接成本',
  '韩国EOR/挂靠公司服务费',
  '汇率风险及跨境费用'
]

const otherCostCategoryOrder = computed(() =>
  isKorea.value ? koreaOtherCostCategoryOrder : chinaOtherCostCategoryOrder
)

const collapsedOtherCostGroups = ref<Record<string, boolean>>(
  Object.fromEntries(
    [...chinaOtherCostCategoryOrder, ...koreaOtherCostCategoryOrder]
      .map(category => [category, true])
  )
)

// Excel「实际报价测算」T 列（取值默认值）；比例在页面中按百分数录入。
const otherCostWorkbookDefaultValues: Record<string, number> = {
  '商业保险/雇主责任险（医疗10W，身故100W，身残按照比例支付）': 180,
  '商业保险/意外险10W': 10,
  体检费摊销: 50,
  节日福利摊销: 33,
  招聘成本摊销: 0.5,
  '人员替换/空档风险': 2,
  'PM/交付管理分摊': 1.5,
  坏账风险准备: 0.5,
  劳动纠纷风险准备: 8.33
}

const koreaOtherCostDefaultValues: Record<string, number> = {
  退职金月摊销: 12,
  EOR管理服务费: 12,
  汇率风险缓冲: 3,
  跨境汇款手续费: 0.5
}

function isOtherCostGroupCollapsed(category: string): boolean {
  return collapsedOtherCostGroups.value[category] !== false
}

function toggleOtherCostGroup(category: string) {
  collapsedOtherCostGroups.value[category] = !isOtherCostGroupCollapsed(category)
}

const selectedRowOtherCostGroups = computed(() => {
  const entries = selectedRowOtherCosts.value.map((item, index) => ({ item, index }))
  return otherCostCategoryOrder.value
    .map(category => {
      const items = entries.filter(entry => entry.item.category === category)
      const total = items.reduce((sum, entry) => sum + (Number(entry.item.amount) || 0), 0)
      return { category, items, total }
    })
    .filter(group => group.items.length > 0)
})

const selectedRowOtherCostTotal = computed(() => {
  const row = positionRows.value[selectedOtherCostRowIndex.value]
  if (!row) return 0
  return getOtherCostTotalForRow(row)
})

const otherCostMonthly = computed(() => {
  return positionRows.value.reduce((sum, row) => sum + getOtherCostTotalForRow(row), 0)
})

const otherCostTotal = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    return sum + getOtherCostTotalForRow(row) * (row.personnelCount || 1) * getServiceMonths(row)
  }, 0)
})

function getOtherCostCategoryTotalForRow(row: PositionRow, category: string): number {
  recalculateOtherCostsForRow(row)
  return (row.otherCosts || [])
    .filter(item => item.category === category)
    .reduce((sum, item) => sum + (Number(item.amount) || 0), 0)
}

// Reset hard cost to default values for the selected row
async function resetHardCostToDefault() {
  const row = positionRows.value[selectedRowIndex.value]
  if (!row) return

  const salary = row.salary || 0
  const city = row.city

  if (row.country === 'korea') {
    row.socialRules = getDefaultKoreaSocialRules(salary)
    row.fundRules = []
    calculateRow(selectedRowIndex.value)
    ElMessage.success('已恢复韩国雇主保险默认值')
    return
  }

  // Reset management rules to default
  row.mgmtRules = getDefaultMgmtRules()

  if (city) {
    // Clear the cache for this city to force reload from backend
    delete citySocialRulesCache.value[city]

    try {
      const data = await fetchCitySocialInsuranceData(city)

      if (data) {
        const rules = buildCityHardCostRules(data, salary)
        applyHardCostRulesToRow(row, rules)

        // Update cache
        citySocialRulesCache.value[city] = rules

        ElMessage.success('已恢复为默认值')
      }
    } catch (error) {
      console.error('Failed to reset to default:', error)
      ElMessage.error('恢复默认值失败')
    }
  } else {
    // No city selected, use hardcoded defaults
    const injuryBase = clampBase(salary, 7310, 36549)
    row.socialRules = [
      { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: salary },
      { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: salary },
      { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: salary },
      { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: injuryBase },
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
  if (isKorea.value) {
    positionRows.value.forEach((row, index) => {
      row.socialRules = getDefaultKoreaSocialRules(row.salary || 0)
      row.fundRules = []
      calculateRow(index)
    })
    ElMessage.success(`已恢复全部 ${positionRows.value.length} 个岗位的韩国雇主保险默认值`)
    return
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
      try {
        const data = await fetchCitySocialInsuranceData(city)

        if (data) {
          const rules = buildCityHardCostRules(data, salary)
          applyHardCostRulesToRow(row, rules)

          // Update cache
          citySocialRulesCache.value[city] = rules

          successCount++
        }
      } catch (error) {
        console.error(`Failed to reset row ${i + 1} to default:`, error)
        failCount++
      }
    } else {
      // No city selected, use hardcoded defaults
      const injuryBase = clampBase(salary, 7310, 36549)
      row.socialRules = [
        { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: salary },
        { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: salary },
        { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: salary },
        { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: injuryBase },
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

function getOtherCostValueSuffix(item: OtherCostItem): string {
  if ([
    'salaryRate',
    'benchReserve',
    'badDebtReserve',
    'laborDisputeReserve',
    'koreaBaseRate'
  ].includes(item.formula)) {
    return '%'
  }
  if (item.formula === 'fundingOccupancy') {
    return '自动'
  }
  if (item.formula === 'severance') {
    return '月'
  }
  return isKorea.value ? 'KRW' : '元'
}

function getOtherCostStep(item: OtherCostItem): string {
  return getOtherCostValueSuffix(item) === '%' ? '0.01' : '0.01'
}

function onOtherCostValueChange(index: number, value: string) {
  const currentRow = positionRows.value[selectedOtherCostRowIndex.value]
  if (!currentRow || !currentRow.otherCosts[index]) return

  const amount = Number(value)
  currentRow.otherCosts[index].value = Number.isFinite(amount) ? amount : 0
  recalculateOtherCostsForRow(currentRow)
  currentRow.subtotal = calculateRowSubtotal(currentRow)

  if (otherCostGlobalMode.value) {
    positionRows.value.forEach(row => {
      if (row.id !== currentRow.id && row.otherCosts?.[index]) {
        row.otherCosts[index].value = currentRow.otherCosts[index].value
        recalculateOtherCostsForRow(row)
        row.subtotal = calculateRowSubtotal(row)
      }
    })
  }
}

// 建议值开关状态：点亮=已填充建议值，再次点击清空并熄灭
const suggestedValuesApplied = ref(false)

function toggleSuggestedOtherCostValues() {
  const currentRow = positionRows.value[selectedOtherCostRowIndex.value]
  if (!currentRow?.otherCosts) return

  const applying = !suggestedValuesApplied.value

  const applyToRow = (row: PositionRow) => {
    row.otherCosts?.forEach(item => {
      const defaults = isKorea.value ? koreaOtherCostDefaultValues : otherCostWorkbookDefaultValues
      item.value = applying ? (defaults[item.name] ?? 0) : 0
    })
    recalculateOtherCostsForRow(row)
    row.subtotal = calculateRowSubtotal(row)
  }

  applyToRow(currentRow)

  if (otherCostGlobalMode.value) {
    positionRows.value.forEach(row => {
      if (row.id !== currentRow.id) {
        applyToRow(row)
      }
    })
  }

  suggestedValuesApplied.value = applying
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
      item.calcBase = injuryCalcBase(item, salary)
    } else {
      item.calcBase = clampBase(salary, item.minBase, item.maxBase)
    }
  })

  // Update fund rules calcBase
  row.fundRules.forEach((item: any) => {
    item.calcBase = clampBase(salary, item.minBase, item.maxBase)
  })
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

// Hard cost monthly: sum of (socialCostCorp + fundCostCorp) for each row (per-person per-month)
// Not affected by personnelCount or serviceCycle
// Uses item.calcBase to match the UI display (社保成本小计 + 公积金成本小计)
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

    // Monthly cost per person (社保+公积金)
    return sum + (socialCorpTotal + fundCorpTotal)
  }, 0)
})

// Optional cost monthly (per-person per-month): sum of ops + onDemand + contingency for each row
// Not affected by personnelCount or serviceCycle
// 公式：运营成本小计（全部岗位总计）+ 按需成本小计（全部岗位总计）+ 机动成本小计（全部岗位总计）
const optionalCostMonthly = computed(() => {
  return allRowsOpsCostTotal.value + allRowsOnDemandCostTotal.value + allRowsContingencyCostTotal.value
})

// Computed - Total project amount (without tax and profit)
// Formula: 单人月成本（工资+社保公司+公积金公司+其他成本）× 人数 × 周期
const totalSubtotal = computed(() => {
  if (!isKorea.value) return baseSubtotal.value
  return baseSubtotal.value * (globalParams.value.exchangeRate || 0)
})

// Computed - Position subtotal (sum of all row subtotals, without tax and profit)
const positionSubtotal = computed(() => {
  return totalSubtotal.value
})

// Computed - Base project amount (without VAT)
// Formula: totalSubtotal × (1 + 利润率)
const baseProjectAmount = computed(() => {
  const profitMultiplier = 1 + (globalParams.value.profitRate || 0) / 100
  if (!isKorea.value) return totalSubtotal.value * profitMultiplier
  const managementMultiplier = 1 + (globalParams.value.managementRate || 0) / 100
  return totalSubtotal.value * managementMultiplier * profitMultiplier
})

// Computed - Funding cost rate for the payment cycle
// Formula: 年化资金成本率 × (账期天数 / 365)
const fundingCostRateForCycle = computed(() => {
  const fundingCostRate = (globalParams.value.fundingCostRate || 0) / 100
  const paymentCycle = globalParams.value.paymentCycle || 0
  return fundingCostRate * (paymentCycle / 365)
})

// Computed - Final project amount
// Formula: 未税报价 × (1 + 增值税率)
const finalProjectAmount = computed(() => {
  const vatMultiplier = 1 + (globalParams.value.vatRate ?? 6) / 100
  return baseProjectAmount.value * vatMultiplier
})

// Computed - Funding cost now lives inside the 2025 other-cost template.
const fundingCost = computed(() => {
  return positionRows.value.reduce((sum, row) => {
    return sum + getOtherCostCategoryTotalForRow(row, '资金风险成本') * (row.personnelCount || 1) * getServiceMonths(row)
  }, 0)
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

// Computed - Total gross profit (without VAT)
// Formula: totalSubtotal × 利润率
const totalGrossProfit = computed(() => {
  const profitRate = (globalParams.value.profitRate || 0) / 100
  const profitBase = isKorea.value
    ? totalSubtotal.value * (1 + (globalParams.value.managementRate || 0) / 100)
    : totalSubtotal.value
  return profitBase * profitRate
})

// Computed - Total margin percentage (using global profit rate parameter)
const totalMargin = computed(() => {
  return (globalParams.value.profitRate || 0).toFixed(1)
})

// Computed - Total deal amount (with VAT)
const totalDealAmount = computed(() => {
  return finalProjectAmount.value
})

// Cost breakdown
// 计算公式：各部分金额 / 项目总额 × 100
// 使用项目总额作为分母，所有项占比之和为 100%
const costBreakdown = computed(() => {
  const projectTotal = finalProjectAmount.value
  const exchangeRate = isKorea.value ? (globalParams.value.exchangeRate || 0) : 1
  const salaryAmountKrw = positionRows.value.reduce((sum, row) => {
    return sum + (row.salary || 0) * (row.personnelCount || 1) * getServiceMonths(row)
  }, 0)
  const socialFundAmountKrw = positionRows.value.reduce((sum, row) => {
    const social = (row.socialRules || []).reduce((s: number, item: any) => s + calculateSocialCost(item.calcBase, item.corpRate), 0)
    const fund = (row.fundRules || []).reduce((s: number, item: any) => s + calculateSocialCost(item.calcBase, item.corpRate), 0)
    return sum + (social + fund) * (row.personnelCount || 1) * getServiceMonths(row)
  }, 0)
  const salaryAmount = salaryAmountKrw * exchangeRate
  const socialFundAmount = socialFundAmountKrw * exchangeRate
  const otherAmount = otherCostTotal.value * exchangeRate
  const managementAmount = isKorea.value
    ? totalSubtotal.value * (globalParams.value.managementRate || 0) / 100
    : 0
  const profitAmount = totalGrossProfit.value
  const taxAmount = finalProjectAmount.value - baseProjectAmount.value

  const percent = (amount: number) => projectTotal > 0 ? Math.round(amount / projectTotal * 100) : 0

  const items = [
    { name: '税前工资', percent: percent(salaryAmount), amount: salaryAmount, color: '#3b82f6' },
    { name: isKorea.value ? '雇主保险' : '社保公积金（公司）', percent: percent(socialFundAmount), amount: socialFundAmount, color: '#14b8a6' },
    { name: '其他成本构成', percent: percent(otherAmount), amount: otherAmount, color: '#a855f7' },
  ]
  if (isKorea.value) {
    items.push({ name: '我方管理费', percent: percent(managementAmount), amount: managementAmount, color: '#0ea5e9' })
  }
  items.push(
    { name: '预估总毛利', percent: percent(profitAmount), amount: profitAmount, color: '#10b981' },
    { name: '增值税', percent: percent(taxAmount), amount: taxAmount, color: '#f59e0b' }
  )
  return items
})

// AI Insight
const aiInsight = computed(() => {
  if (isKorea.value) {
    return '韩国报价已分别计入EOR服务费、汇率风险、跨境手续费、我方管理费及国内开票税费。'
  }
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
  const amount = (calcBase || 0) * ((rate || 0) / 100)
  return isKorea.value ? Math.round(amount) : amount
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
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)
})

// Computed - Total housing fund cost for individual
const fundCostIndivTotal = computed(() => {
  return fundRules.value.reduce((sum, item) => {
    return sum + calculateSocialCost(item.calcBase, item.indivRate)
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

function roundBackendRate(rate: number | null | undefined, defaultValue: number) {
  if (rate === null || rate === undefined) return defaultValue
  const normalized = Math.abs(rate) <= 1 ? rate * 100 : rate
  return Math.round(normalized * 100) / 100
}

function getFundLowerLimit(data: any) {
  return data.fund_lower_limit ?? data.lower_limit
}

function getFundUpperLimit(data: any) {
  return data.fund_upper_limit ?? data.upper_limit
}

function getFundDefaultRate(data: any, defaultValue = 7) {
  return roundBackendRate(data.fund_default_rate ?? data.corp_fund_rate ?? data.indiv_fund_rate, defaultValue)
}

async function fetchCitySocialInsuranceData(city: string) {
  const cityName = getCityName(city)
  if (!cityName) return null

  try {
    const response = await axios.get(`${API_URL}/city-social-insurance/city/${encodeURIComponent(cityName)}`)
    return response.data || null
  } catch (error) {
    try {
      const response = await axios.get(`${API_URL}/city-social-insurance/`, {
        params: { city: cityName }
      })
      if (response.data && response.data.length > 0) {
        return response.data[0]
      }
    } catch (listError) {
      console.error(`Failed to load city social insurance data for ${cityName}:`, listError)
    }
  }

  try {
    const defaultResponse = await axios.get(`${API_URL}/city-social-insurance/city/${encodeURIComponent('默认')}`)
    return defaultResponse.data || null
  } catch {
    return null
  }
}

function buildCityHardCostRules(data: any, salary: number): CityHardCostRules {
  const socialMin = Number(data?.lower_limit) || 0
  const socialMax = Number(data?.upper_limit) || 0
  const socialBase = clampBase(salary, socialMin, socialMax)
  // 工伤基数：优先取城市独立工伤基数（同样受社保上下限封顶），否则与其他险种一致用封顶后月薪
  const injuryBaseFixed = Number(data?.injury_base) || 0
  const injuryBase = injuryBaseFixed > 0
    ? clampBase(injuryBaseFixed, socialMin, socialMax)
    : socialBase
  const fundMin = Number(getFundLowerLimit(data)) || 0
  const fundMax = Number(getFundUpperLimit(data)) || 0
  const fundBase = clampBase(salary, fundMin, fundMax)
  const fundRate = getFundDefaultRate(data, 7)

  return {
    socialRules: [
      { type: '养老保险', minBase: socialMin, maxBase: socialMax, corpRate: roundBackendRate(data?.corp_pension_rate, 16), indivRate: roundBackendRate(data?.indiv_pension_rate, 8), calcBase: socialBase },
      { type: '医疗保险', minBase: socialMin, maxBase: socialMax, corpRate: roundBackendRate(data?.corp_medical_rate, 10), indivRate: roundBackendRate(data?.indiv_medical_rate, 2), calcBase: socialBase },
      { type: '失业保险', minBase: socialMin, maxBase: socialMax, corpRate: roundBackendRate(data?.corp_unemployment_rate, 0.5), indivRate: roundBackendRate(data?.indiv_unemployment_rate, 0.5), calcBase: socialBase },
      { type: '工伤保险', minBase: socialMin, maxBase: socialMax, corpRate: roundBackendRate(data?.corp_injury_rate, 0.16), indivRate: 0, calcBase: injuryBase, injuryBaseFixed },
      { type: '残保金', minBase: socialMin, maxBase: socialMax, corpRate: roundBackendRate(data?.corp_disability_rate, 0), indivRate: roundBackendRate(data?.indiv_disability_rate, 0), calcBase: socialBase }
    ],
    fundRules: [
      { type: '住房公积金', minBase: fundMin, maxBase: fundMax, corpRate: fundRate, indivRate: fundRate, calcBase: fundBase }
    ],
    injuryBase
  }
}

function applyHardCostRulesToRow(row: PositionRow, rules: CityHardCostRules) {
  row.socialRules = JSON.parse(JSON.stringify(rules.socialRules))
  row.fundRules = JSON.parse(JSON.stringify(rules.fundRules))
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
  if (isKorea.value) {
    return '₩ ' + Math.round(value).toLocaleString('ko-KR')
  }
  return '¥ ' + value.toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatQuoteCurrency(num: number): string {
  return '¥ ' + (num || 0).toLocaleString('zh-CN', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })
}

function formatCurrencyCompact(num: number): string {
  if (num >= 1000000) {
    return '¥ ' + (num / 1000000).toFixed(2) + 'M'
  } else if (num >= 10000) {
    return '¥ ' + (num / 10000).toFixed(2) + 'w'
  }
  return '¥ ' + (num || 0).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function getServiceMonths(row: PositionRow): number {
  const serviceCycleCount = row.serviceCycleCount || 1
  if (row.cycleUnit === 'year') return serviceCycleCount * 12
  if (row.cycleUnit === 'day') return serviceCycleCount / 30
  return serviceCycleCount
}

function clampBase(value: number, minBase: number, maxBase: number): number {
  const salary = Number(value) || 0
  if (salary <= 0) return 0
  const min = Number(minBase) || 0
  const max = Number(maxBase) || 0
  if (max > 0) return Math.min(Math.max(salary, min), max)
  return Math.max(salary, min)
}

// 工伤保险计算基数：优先取城市独立工伤基数，否则用月薪；两者均按社保上下限封顶
function injuryCalcBase(item: any, salary: number): number {
  const fixed = Number(item?.injuryBaseFixed) || 0
  if (fixed > 0) return clampBase(fixed, item.minBase, item.maxBase)
  return clampBase(salary, item.minBase, item.maxBase)
}

function calculateOtherCostItem(item: OtherCostItem, row: PositionRow): number {
  const salary = row.salary || 0
  const value = Number(item.value) || 0
  const monthlyCost = salary * OTHER_COST_MONTHLY_FACTOR

  switch (item.formula) {
    case 'severance':
      return value > 0 ? salary / value : 0
    case 'koreaBaseRate': {
      const socialCost = (row.socialRules || []).reduce(
        (sum, rule) => sum + calculateSocialCost(rule.calcBase, rule.corpRate),
        0
      )
      const severanceMonths = Number(
        row.otherCosts?.find(cost => cost.formula === 'severance')?.value
      ) || 12
      const eorRate = Number(
        row.otherCosts?.find(cost => cost.name === 'EOR管理服务费')?.value
      ) || 0
      const koreaDirectBase = salary
        + socialCost
        + Math.round(salary / severanceMonths)
        + Math.round(salary * eorRate / 100)
      return koreaDirectBase * (value / 100)
    }
    case 'salaryRate':
      return salary * (value / 100)
    case 'fixedMonthlySpread':
      return value / 12
    case 'benchReserve':
      return salary * (value / 100) * 2 / 12
    case 'fundingOccupancy': {
      if (value <= 0) return 0
      const paymentMonths = (globalParams.value.paymentCycle || 0) / 30
      const annualRate = (globalParams.value.fundingCostRate || 0) / 100
      return monthlyCost * paymentMonths * annualRate / 12
    }
    case 'badDebtReserve':
      return monthlyCost * (value / 100)
    case 'laborDisputeReserve':
      return salary * (value / 100)
    case 'fixed':
    default:
      return value
  }
}

function recalculateOtherCostsForRow(row: PositionRow) {
  if (!row.otherCosts) {
    row.otherCosts = row.country === 'korea' ? getDefaultKoreaOtherCosts() : getDefaultOtherCosts()
  }
  row.otherCosts.forEach(item => {
    const amount = calculateOtherCostItem(item, row)
    item.amount = row.country === 'korea'
      ? Math.round(amount)
      : Math.round(amount * 100) / 100
  })
}

function getOtherCostTotalForRow(row: PositionRow): number {
  recalculateOtherCostsForRow(row)
  return (row.otherCosts || []).reduce((sum, item) => sum + (Number(item.amount) || 0), 0)
}

// Calculate a single row's subtotal
// New formula: 税前月薪 + 社保成本（公司）+ 公积金成本（公司）+ 其他成本合计
// Note: Only company portion, excludes individual portion
// Uses the row's own rules (each row can have different city and custom rates)
function calculateRowSubtotal(row: PositionRow): number {
  const salary = row.salary || 0

  // Use the row's own rules
  const currentSocialRules = row.socialRules || getDefaultSocialRules()
  const currentFundRules = row.fundRules || getDefaultFundRules()

  // Calculate social insurance cost (company only) for this row
  const socialCorpTotalForRow = currentSocialRules.reduce((sum: number, item: any) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)

  // Calculate housing fund cost (company only) for this row
  const fundCorpTotalForRow = currentFundRules.reduce((sum: number, item: any) => {
    return sum + calculateSocialCost(item.calcBase, item.corpRate)
  }, 0)

  const otherCostTotalForRow = getOtherCostTotalForRow(row)

  // Monthly subtotal per person: 税前月薪 + 社保（公司）+ 公积金（公司）+ 其他成本合计
  const monthlySubtotalPerPerson = salary + socialCorpTotalForRow + fundCorpTotalForRow + otherCostTotalForRow

  // Round to 2 decimal places to match display precision
  const roundedMonthlySubtotal = Math.round(monthlySubtotalPerPerson * 100) / 100

  // Calculate total based on personnel and cycle
  const personnelCount = row.personnelCount || 1
  const totalMonths = getServiceMonths(row)

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
    if (item.type === '工伤保险') {
      item.calcBase = injuryCalcBase(item, salary)
    } else {
      item.calcBase = clampBase(salary, item.minBase, item.maxBase)
    }
  })
  row.fundRules.forEach((item: any) => {
    item.calcBase = clampBase(salary, item.minBase, item.maxBase)
  })

  recalculateOtherCostsForRow(row)
  row.subtotal = calculateRowSubtotal(row)

  // Auto-calculate after-tax salary if not manually editing
  if (row.country === 'korea') {
    row.afterTaxSalary = 0
  } else if (!skipAfterTaxCalc) {
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
  const row = positionRows.value[index]
  if (row) {
    // 用户手动修改薪资后，城市/岗位联动不再自动覆盖
    row.salaryManuallyEdited = true
    row.salarySource = 'manual'
    row.salarySourceCity = undefined
    // 输入过程中只即时限制最高值；最低值在输入完成后校正，避免影响连续输入。
    clampSalaryToPositionBounds(row, false, true)
  }
  calculateRow(index, false)
}

function enforceSalaryBounds(index: number) {
  const row = positionRows.value[index]
  if (!row) return
  clampSalaryToPositionBounds(row, true, true)
  calculateRow(index, false)
}

// Handle after-tax salary change - reverse calculate salary
function onAfterTaxSalaryChange(index: number) {
  const row = positionRows.value[index]
  // 反推税前视为手动定薪
  row.salaryManuallyEdited = true
  row.salarySource = 'manual'
  row.salarySourceCity = undefined
  const afterTaxSalary = row.afterTaxSalary || 0

  if (afterTaxSalary <= 0) {
    row.salary = 0
    const adjusted = clampSalaryToPositionBounds(row, true, true)
    calculateRow(index, adjusted ? false : true)
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

  const salaryAdjusted = clampSalaryToPositionBounds(row, true, true)

  // Update calcBase for all rules to match the new salary
  const newSalary = row.salary
  row.socialRules.forEach((item: any) => {
    if (item.type !== '工伤保险') {
      item.calcBase = clampBase(newSalary, item.minBase, item.maxBase)
    }
  })
  row.fundRules.forEach((item: any) => {
    item.calcBase = clampBase(newSalary, item.minBase, item.maxBase)
  })

  // Recalculate the row (skip after-tax calc to avoid loop)
  calculateRow(index, salaryAdjusted ? false : true)
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
  const defaultOption = isKorea.value ? availablePositions.value[0] : undefined
  const row = createPositionRow(selectedCountry.value, defaultOption)
  positionRows.value.push(row)
  calculateRow(positionRows.value.length - 1)
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
  if (row.country === 'korea') {
    await refreshRowSalary(index)
    row.socialRules = getDefaultKoreaSocialRules(row.salary)
    row.fundRules = []
    calculateRow(index)
    return
  }
  // 城市变化时按 岗位+城市 重新取薪（未手动改薪时）
  await refreshRowSalary(index)
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

  if (row.country === 'korea') {
    row.socialRules = getDefaultKoreaSocialRules(salary)
    row.fundRules = []
    return
  }

  // If city is not selected, use default values
  if (!city) {
    const injuryBase = clampBase(salary, 7310, 36549)
    row.socialRules = [
      { type: '养老保险', minBase: 7310, maxBase: 36549, corpRate: 16, indivRate: 8, calcBase: salary },
      { type: '医疗保险', minBase: 7310, maxBase: 36549, corpRate: 10, indivRate: 2, calcBase: salary },
      { type: '失业保险', minBase: 7310, maxBase: 36549, corpRate: 0.5, indivRate: 0.5, calcBase: salary },
      { type: '工伤保险', minBase: 7310, maxBase: 36549, corpRate: 0.16, indivRate: 0, calcBase: injuryBase },
      { type: '残保金', minBase: 7310, maxBase: 36549, corpRate: 1.5, indivRate: 0, calcBase: salary }
    ]
    row.fundRules = [
      { type: '住房公积金', minBase: 7310, maxBase: 36549, corpRate: 7, indivRate: 7, calcBase: salary }
    ]
    return
  }

  try {
    const data = await fetchCitySocialInsuranceData(city)

    if (data) {
      const rules = buildCityHardCostRules(data, salary)
      applyHardCostRulesToRow(row, rules)
      citySocialRulesCache.value[city] = rules
    }
  } catch (error) {
    console.error('Failed to load city social insurance rules:', error)
  }
}

// Handle position change for a specific row
async function onRowPositionChange(index: number) {
  const row = positionRows.value[index]
  const position = availablePositions.value.find(p => p.id === Number(row.position))
  if (!position) return
  // 重新选择岗位后恢复自动取薪
  row.salaryManuallyEdited = false
  if (row.country === 'korea') {
    row.city = position.city || row.city || '首尔'
    row.salary = position.monthlySalaryKrw || 0
    row.salarySource = 'exact'
    row.salarySourceCity = position.city
    row.socialRules = getDefaultKoreaSocialRules(row.salary)
    row.fundRules = []
    calculateRow(index)
    return
  }
  const result = await fetchPositionSalary(position.id, row.city || '')
  if (result && result.salary != null) {
    row.salary = result.salary
    clampSalaryToPositionBounds(row, true)
    row.salarySource = result.source
    row.salarySourceCity = result.source_city || undefined
    // 薪资变化后刷新该行社保基数
    await loadCitySocialRulesForRow(row, row.city)
    if (index === selectedRowIndex.value) {
      updateSelectedRowCalcBase()
    }
  }
  calculateRow(index)
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
        item.calcBase = injuryCalcBase(item, salary)
      } else {
        // Use salary from position row
        item.calcBase = clampBase(salary, item.minBase, item.maxBase)
      }
    })

    // Update calcBase for fund rules
    rules.fundRules.forEach((item: any) => {
      item.calcBase = clampBase(salary, item.minBase, item.maxBase)
    })

    socialRules.value = rules.socialRules
    fundRules.value = rules.fundRules
  }
}

// Load social insurance rules for a city
async function loadCitySocialRules(city: string) {
  // Check cache first
  if (citySocialRulesCache.value[city]) {
    return citySocialRulesCache.value[city]
  }

  try {
    const data = await fetchCitySocialInsuranceData(city)

    if (data) {
      const salary = positionRows.value[0]?.salary || 0
      const rules = buildCityHardCostRules(data, salary)

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
    console.log('正在获取岗位职级数据...', `${API_URL}/job-positions/options`)
    const response = await axios.get(`${API_URL}/job-positions/options`)

    if (!response.data || response.data.length === 0) {
      console.warn('岗位职级数据为空，请在后台"驻场人员岗位薪资"模块中导入数据')
      ElMessage.warning('岗位职级数据为空，请在后台系统"驻场人员岗位薪资"模块中导入数据')
      return
    }

    availablePositions.value = response.data.map((item: any) => {
      // Build display name: 岗位名称 - 级别
      const displayName = `${item.position_name} - ${item.level_name}`
      return {
        id: item.id,
        name: displayName,
        position: item.position_name,
        level: item.level_name,
        levelRank: item.level_rank,
        sequenceType: item.sequence_type,
        category: item.category,
        systemSalaryMax: item.system_salary_max == null ? null : Number(item.system_salary_max),
        systemSalaryMin: item.system_salary_min == null ? null : Number(item.system_salary_min)
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

async function fetchKoreaPositions() {
  try {
    const response = await axios.get(`${API_URL}/korea-job-salaries/options`)
    availablePositions.value = response.data.map((item: any) => ({
      id: item.id,
      name: item.position_name,
      position: item.position_name,
      level: '',
      levelRank: 1,
      sequenceType: '韩国',
      category: '驻场服务',
      systemSalaryMax: null,
      systemSalaryMin: null,
      city: item.city,
      monthlySalaryKrw: Number(item.monthly_salary_krw)
    }))
    const uniqueCities = new Set<string>(
      availablePositions.value.map(item => item.city || '').filter(Boolean)
    )
    cityOptions.value = Array.from(uniqueCities).map(city => ({ label: city, value: city }))
  } catch (error: any) {
    console.error('获取韩国岗位薪资失败:', error)
    ElMessage.error(error.response?.data?.detail || '获取韩国岗位薪资失败')
    availablePositions.value = []
    cityOptions.value = []
  }
}

// Query salary for a position in a city (with fallback chain on backend)
async function fetchPositionSalary(positionId: number, city: string): Promise<{ salary: number | null, source: string, source_city: string | null } | null> {
  try {
    const response = await axios.get(`${API_URL}/job-positions/${positionId}/salary`, {
      params: { city: city || '' }
    })
    return response.data
  } catch (error) {
    console.error('获取岗位薪资失败:', error)
    return null
  }
}

// Refresh row salary based on position + city (two-factor lookup)
async function refreshRowSalary(index: number) {
  const row = positionRows.value[index]
  if (!row) return
  // 用户手动改过薪资后不再自动覆盖
  if (row.salaryManuallyEdited) return
  const position = availablePositions.value.find(p => p.id === Number(row.position))
  if (!position) return

  if (row.country === 'korea') {
    const koreaPosition = availablePositions.value.find(
      item => item.id === Number(row.position) && (!row.city || item.city === row.city)
    ) || position
    row.salary = koreaPosition.monthlySalaryKrw || 0
    row.salarySource = 'exact'
    row.salarySourceCity = koreaPosition.city
    row.socialRules = getDefaultKoreaSocialRules(row.salary)
    calculateRow(index)
    return
  }

  const result = await fetchPositionSalary(position.id, row.city || '')
  if (result && result.salary != null) {
    row.salary = result.salary
    clampSalaryToPositionBounds(row, true)
    row.salarySource = result.source
    row.salarySourceCity = result.source_city || undefined
  }
}

// Salary source hint tooltip
function getSalarySourceTitle(row: PositionRow): string {
  if (row.salarySource === 'provincial_capital') {
    return `该城市暂无薪资数据，参考同省省会 ${row.salarySourceCity || ''} 的薪资`
  }
  if (row.salarySource === 'national_baseline') {
    return `该城市暂无薪资数据，参考全国基准（${row.salarySourceCity || '北京/上海'} 均值）`
  }
  return ''
}

let activeCountryState: CountryMode = 'china'
const countryRowSnapshots: Partial<Record<CountryMode, PositionRow[]>> = {}

function clonePositionRows(rows: PositionRow[]): PositionRow[] {
  return JSON.parse(JSON.stringify(rows))
}

function resetSelectedIndexes() {
  selectedRowIndex.value = 0
  selectedFlexRowIndex.value = 0
  selectedOptionalRowIndex.value = 0
  selectedOtherCostRowIndex.value = 0
  activeTab.value = 'social'
  suggestedValuesApplied.value = isKorea.value
}

async function onCountryChange() {
  const nextCountry = selectedCountry.value
  countryRowSnapshots[activeCountryState] = clonePositionRows(positionRows.value)
  countryGlobalParams[activeCountryState] = { ...globalParams.value }

  if (nextCountry === 'korea') {
    await fetchKoreaPositions()
  } else {
    await Promise.all([fetchPositions(), fetchCities()])
  }

  globalParams.value = { ...countryGlobalParams[nextCountry] }
  const savedRows = countryRowSnapshots[nextCountry]
  positionRows.value = savedRows
    ? clonePositionRows(savedRows)
    : [createPositionRow(nextCountry, nextCountry === 'korea' ? availablePositions.value[0] : undefined)]
  activeCountryState = nextCountry
  resetSelectedIndexes()
  calculateAll()
}

function resetForm() {
  positionRows.value = [
    createPositionRow(selectedCountry.value, isKorea.value ? availablePositions.value[0] : undefined)
  ]
  globalParams.value = { ...countryGlobalParams[selectedCountry.value] }
  countryRowSnapshots[selectedCountry.value] = clonePositionRows(positionRows.value)
  resetSelectedIndexes()
  calculateAll()
}

function showCalcDetails() {
  ElMessage.info('计算详情弹窗开发中...')
}

async function startCalculation() {
  previewModalMode.value = 'preview'
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
    country: selectedCountry.value,
    costCurrency: isKorea.value ? 'KRW' : 'CNY',
    quoteCurrency: 'CNY',
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
        otherCosts: JSON.parse(JSON.stringify(row.otherCosts || [])),
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
      baseProjectAmount: baseProjectAmount.value,        // 未税报价（含利润，不含增值税）
      otherCostTotal: otherCostTotal.value,              // 其他成本合计
      grossProfit: totalGrossProfit.value,               // 预估毛利
      vatRate: globalParams.value.vatRate ?? 6,          // 增值税率
      costTotalKrw: isKorea.value ? baseSubtotal.value : null,
      exchangeRate: isKorea.value ? globalParams.value.exchangeRate : null,
      managementRate: isKorea.value ? globalParams.value.managementRate : null
    }
  }
  // Open modal
  isPreviewModalOpen.value = true
}

function closePreviewModal() {
  isPreviewModalOpen.value = false
  previewModalMode.value = 'preview'
}

function exportQuotation() {
  previewModalMode.value = 'export'
  startCalculation()
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

/* Embedded mode: remove outer padding/background, fit parent container */
.onsite-calculator-page.embedded-mode {
  background-color: transparent;
  min-height: 0;
  height: 100%;
  border-radius: 12px;
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
  flex-shrink: 0;
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

.country-select-btn {
  flex-shrink: 0;
  white-space: nowrap;
}

.country-select-btn select {
  width: 7rem;
  min-width: 7rem;
  padding-right: 1.5rem;
  border: 0;
  outline: 0;
  background: transparent;
  color: #ffffff;
  font: inherit;
  cursor: pointer;
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

.left-column > .card:first-child {
  order: 1;
}

.rules-card {
  order: 2;
}

.flex-cost-card {
  order: 3;
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

.korea-mode .position-table-header,
.korea-mode .position-row {
  grid-template-columns: 0.5fr 1fr 1.2fr 1.35fr 0.8fr 1fr 1fr 50px;
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

.salary-source-hint {
  margin-top: 2px;
  font-size: 0.625rem;
  line-height: 1.2;
  color: #d97706;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: help;
}

.salary-range-hint {
  margin-top: 2px;
  font-size: 0.625rem;
  line-height: 1.2;
  color: #7dd3fc;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  cursor: help;
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

.other-cost-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.suggest-value-btn {
  white-space: nowrap;
  background-color: rgba(100, 116, 139, 0.15);
  border-color: rgba(100, 116, 139, 0.4);
  color: #94a3b8;
}

.suggest-value-btn:hover {
  background-color: rgba(100, 116, 139, 0.25);
  color: #cbd5e1;
}

.suggest-value-btn.active {
  background-color: rgba(19, 91, 236, 0.25);
  border-color: #135bec;
  color: #60a5fa;
}

.suggest-value-btn.active:hover {
  background-color: rgba(19, 91, 236, 0.35);
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

.other-cost-groups {
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}

.other-cost-group {
  border: 1px solid #263247;
  border-radius: 0.5rem;
  overflow: hidden;
  background-color: rgba(15, 23, 42, 0.35);
}

.other-cost-group-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.85rem 1rem;
  background-color: #151b26;
  border-bottom: 1px solid #263247;
}

.other-cost-group.collapsed .other-cost-group-header {
  border-bottom: 0;
}

.other-cost-group-title {
  display: flex;
  align-items: center;
  gap: 0.45rem;
  min-width: 0;
}

.collapse-toggle-btn {
  width: 24px;
  height: 24px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  flex: 0 0 24px;
  padding: 0;
  border: 1px solid #30415d;
  border-radius: 0.25rem;
  background-color: #1d2636;
  color: #8fb5ff;
  cursor: pointer;
  transition: all 0.18s ease;
}

.collapse-toggle-btn:hover {
  border-color: #3b82f6;
  color: #bfdbfe;
  background-color: #23314a;
}

.collapse-toggle-btn .material-symbols-outlined {
  font-size: 1.1rem;
  line-height: 1;
}

.other-cost-group-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 700;
  color: #f8fafc;
}

.other-cost-group-header span {
  font-size: 0.95rem;
  font-weight: 700;
  color: #60a5fa;
  white-space: nowrap;
}

.other-cost-table {
  table-layout: fixed;
  width: 100%;
}

.other-cost-table th:first-child {
  width: 18%;
}

.other-cost-table th:nth-child(2) {
  width: 22%;
}

/* 第3列（测算依据）占用剩余宽度，覆盖 .mgmt-table 基类的固定 110px */
.other-cost-table th:nth-child(3) {
  width: auto;
}

.other-cost-table th:nth-child(4) {
  width: 112px;
}

.other-cost-table th:last-child {
  width: 110px;
}

/* 统一左对齐；超长文字单行省略，悬停通过 title 查看全文 */
.other-cost-table th,
.other-cost-table td {
  text-align: left;
}

.other-cost-table td {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.45;
}

.other-cost-table .mgmt-amount-cell,
.other-cost-table .mgmt-total-amount {
  text-align: left;
}

.other-cost-grand-total {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 0.75rem;
}

.other-cost-grand-total > div {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.9rem 1rem;
  border: 1px solid #263247;
  border-radius: 0.5rem;
  background-color: #151b26;
}

.other-cost-grand-total span {
  color: #92a4c9;
  font-weight: 600;
}

.other-cost-grand-total strong {
  color: #135bec;
  font-size: 1rem;
  white-space: nowrap;
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

.korea-mode .global-params-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
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

.global-param-item .input-with-suffix .exchange-rate-input {
  padding-right: 2.75rem;
  padding-left: 0.35rem;
  font-size: 0.75rem;
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
    align-items: stretch;
    gap: 1rem;
  }

  .header-buttons {
    width: 100%;
    flex-wrap: wrap;
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
