<template>
  <div class="home-container">
    <div v-if="activeFunction === 'convert'">
      <h1 class="text-3xl font-bold mb-6">智能识别</h1>
      <div class="upload-area mb-6">
        <input type="file" @change="handleConvertFileChange" accept=".xlsx,.xls" id="convert-file-input" />
        <button @click="triggerFileInput('convert')">选择Excel文件</button>
      </div>
      <div v-if="originalTableData.length > 0" class="split-view">
        <!-- 左侧原始表格 -->
        <div class="original-table">
          <h3 style="display: flex; justify-content: space-between; align-items: center;">
            <span>原始表格</span>
            <span v-if="originalTableData.length > 0" class="device-model-count">共导入设备型号：{{ getDeviceModelCount() }} 条</span>
          </h3>
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
                  <th v-for="header in visibleColumns" :key="header">
                    {{ header }}
                    <div class="resizer" @mousedown="startResize($event, 'converted', visibleColumns.indexOf(header))"></div>
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="(row, rowIndex) in convertedTableData" :key="rowIndex">
                  <td v-for="header in visibleColumns" :key="header">
                    <input type="text" v-model="row[header]" />
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
    
    <div v-else-if="activeFunction === 'match'">
      <h1 class="text-3xl font-bold mb-6">智能匹配</h1>
      <div class="upload-area mb-6">
        <input type="file" @change="handleFileChange" accept=".xlsx,.xls" id="match-file-input" />
        <button @click="triggerFileInput('match')">选择Excel文件</button>
      </div>
      <div v-if="tableData.length > 0" class="table-area">
        <div class="table-container">
          <table border="1">
            <thead>
              <tr>
                <th>厂商<div class="resizer" @mousedown="startResize($event, 'match', 0)"></div></th>
                <th>设备/软件型号<div class="resizer" @mousedown="startResize($event, 'match', 1)"></div></th>
                <th>设备/软件分类<div class="resizer" @mousedown="startResize($event, 'match', 2)"></div></th>
                <th>匹配型号<div class="resizer" @mousedown="startResize($event, 'match', 3)"></div></th>
                <th>匹配度<div class="resizer" @mousedown="startResize($event, 'match', 4)"></div></th>
                <th>单价<div class="resizer" @mousedown="startResize($event, 'match', 5)"></div></th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, index) in tableData" :key="index">
                <td>{{ item.manufacturer }}</td>
                <td>{{ item.model }}</td>
                <td>{{ item.deviceCategory }}</td>
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
    </div>
    
    <div v-if="activeFunction === 'search'">
      <h1 class="text-3xl font-bold mb-6">手动搜索</h1>
      <div class="search-container">
        <p>手动搜索功能开发中...</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, inject } from 'vue'
import * as XLSX from 'xlsx'

// 从父组件注入数据和方法
const activeFunction = inject('activeFunction', ref('convert'))
const originalTableData = inject('originalTableData', ref([]))
const originalHeaders = inject('originalHeaders', ref([]))
const convertedTableData = inject('convertedTableData', ref([]))
const visibleColumns = inject('visibleColumns', ref([]))
const tableData = inject('tableData', ref([]))
const activeModelIndex = inject('activeModelIndex', ref(-1))
const modelOptions = inject('modelOptions', ref([]))

// 方法
const handleConvertFileChange = inject('handleConvertFileChange', () => {})
const triggerFileInput = inject('triggerFileInput', () => {})
const startResize = inject('startResize', () => {})
const addRow = inject('addRow', () => {})
const exportConvertedData = inject('exportConvertedData', () => {})
const resetConvertData = inject('resetConvertData', () => {})
const sendToMatch = inject('sendToMatch', () => {})
const handleFileChange = inject('handleFileChange', () => {})
const openSearch = inject('openSearch', () => {})
const updateModelSelection = inject('updateModelSelection', () => {})
const exportData = inject('exportData', () => {})
const resetMatchData = inject('resetMatchData', () => {})
const generateQuotes = inject('generateQuotes', () => {})
const exportQuotes = inject('exportQuotes', () => {})
const resetQuotes = inject('resetQuotes', () => {})
const getDeviceModelCount = inject('getDeviceModelCount', () => 0)
</script>

<style scoped>
.home-container {
  padding: 20px;
}
</style> 