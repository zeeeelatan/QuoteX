<template>
  <div class="system-settings">
    <div class="settings-grid">
      <!-- Database Status -->
      <div class="setting-card">
        <div class="card-header">
          <span class="material-symbols-outlined card-icon">storage</span>
          <div class="card-title">
            <h3>数据库状态</h3>
            <p>数据库连接和基本信息</p>
          </div>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <span class="stat-label">数据库状态</span>
            <span class="stat-value success">正常</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">数据库类型</span>
            <span class="stat-value">PostgreSQL</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">数据表数量</span>
            <span class="stat-value">{{ dbStats.tableCount || '-' }}</span>
          </div>
        </div>
      </div>

      <!-- Data Summary -->
      <div class="setting-card">
        <div class="card-header">
          <span class="material-symbols-outlined card-icon">bar_chart</span>
          <div class="card-title">
            <h3>数据统计</h3>
            <p>系统数据概览</p>
          </div>
        </div>
        <div class="card-body">
          <div class="stat-row">
            <span class="stat-label">维保费率</span>
            <span class="stat-value">{{ dbStats.rateCount || 0 }} 条</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">服务级别</span>
            <span class="stat-value">{{ dbStats.serviceLevelCount || 0 }} 条</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">GPU 价格</span>
            <span class="stat-value">{{ dbStats.gpuCount || 0 }} 条</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">备件数量</span>
            <span class="stat-value">{{ dbStats.sparePartCount || 0 }} 条</span>
          </div>
        </div>
      </div>

      <!-- API Configuration -->
      <div class="setting-card">
        <div class="card-header">
          <span class="material-symbols-outlined card-icon">api</span>
          <div class="card-title">
            <h3>API 配置</h3>
            <p>后端 API 服务配置</p>
          </div>
        </div>
        <div class="card-body">
          <div class="config-row">
            <span class="config-label">API 地址</span>
            <span class="config-value">{{ API_URL }}</span>
          </div>
          <div class="config-row">
            <span class="config-label">状态</span>
            <span class="status-badge success">运行中</span>
          </div>
        </div>
      </div>

      <!-- System Info -->
      <div class="setting-card">
        <div class="card-header">
          <span class="material-symbols-outlined card-icon">info</span>
          <div class="card-title">
            <h3>系统信息</h3>
            <p>版本和配置信息</p>
          </div>
        </div>
        <div class="card-body">
          <div class="config-row">
            <span class="config-label">系统版本</span>
            <span class="config-value">v1.0.0</span>
          </div>
          <div class="config-row">
            <span class="config-label">最后更新</span>
            <span class="config-value">2024-01-03</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Quick Actions -->
    <div class="quick-actions">
      <h3 class="section-title">快捷操作</h3>
      <div class="actions-grid">
        <button class="action-card" @click="refreshAllData">
          <span class="material-symbols-outlined">refresh</span>
          <span>刷新所有数据</span>
        </button>
        <button class="action-card" @click="exportAllData">
          <span class="material-symbols-outlined">download</span>
          <span>导出全部数据</span>
        </button>
        <button class="action-card warning" @click="clearCache">
          <span class="material-symbols-outlined">clear_all</span>
          <span>清除缓存</span>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import * as XLSX from 'xlsx'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

// State
const dbStats = ref({
  tableCount: 0,
  rateCount: 0,
  serviceLevelCount: 0,
  gpuCount: 0,
  sparePartCount: 0
})

// Load stats
async function loadStats() {
  try {
    const [rates, levels, gpus, parts] = await Promise.all([
      axios.get(`${API_URL}/maintenance_rates/`),
      axios.get(`${API_URL}/service-level/`),
      axios.get(`${API_URL}/gpu_prices/`),
      axios.get(`${API_URL}/spare_parts/`)
    ])

    dbStats.value = {
      tableCount: 4, // Main tables
      rateCount: rates.data?.length || 0,
      serviceLevelCount: levels.data?.length || 0,
      gpuCount: gpus.data?.length || 0,
      sparePartCount: parts.data?.length || 0
    }
  } catch (error) {
    console.error('Failed to load stats:', error)
  }
}

// Refresh all data
async function refreshAllData() {
  await loadStats()
  alert('数据已刷新')
}

// Export all data
async function exportAllData() {
  try {
    const [rates, levels, gpus, parts] = await Promise.all([
      axios.get(`${API_URL}/maintenance_rates/`),
      axios.get(`${API_URL}/service-level/`),
      axios.get(`${API_URL}/gpu_prices/`),
      axios.get(`${API_URL}/spare_parts/`)
    ])

    const wb = XLSX.utils.book_new()

    // 维保费率
    const rateData = rates.data.map((r: any) => ({
      '一级分类': r.primary_category || '',
      '二级分类': r.secondary_category || '',
      '三级分类': r.tertiary_category || '',
      '费率': (r.rate * 100).toFixed(2) + '%'
    }))
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(rateData), '维保费率')

    // 服务级别
    const levelData = levels.data.map((l: any) => ({
      '级别代码': l.level_code,
      '响应时间': l.response_time,
      '系数': l.coefficient,
      '描述': l.description || ''
    }))
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(levelData), '服务级别')

    // GPU 价格
    const gpuData = gpus.data.map((g: any) => ({
      '厂商': g.manufacturer,
      '系列': g.series,
      '型号': g.model,
      '显存(GB)': g.gpu_memory,
      'GPU价格': g.gpu_price || 0,
      '维保费率(%)': (g.gpu_rate * 100).toFixed(2)
    }))
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(gpuData), 'GPU价格')

    // 备件
    const partData = parts.data.map((p: any) => ({
      '厂商': p.manufacturer,
      '备件PN': p.part_pn,
      '描述': p.part_desc,
      '单价': p.unit_price || 0,
      '维修方式': p.repair_method || '',
      '维修周期': p.repair_period || ''
    }))
    XLSX.utils.book_append_sheet(wb, XLSX.utils.json_to_sheet(partData), '备件清单')

    XLSX.writeFile(wb, `系统数据备份_${new Date().toISOString().slice(0, 10)}.xlsx`)
  } catch (error) {
    console.error('Export failed:', error)
  }
}

// Clear cache
function clearCache() {
  if (confirm('确定要清除所有缓存吗？')) {
    localStorage.clear()
    sessionStorage.clear()
    alert('缓存已清除')
  }
}

onMounted(() => {
  loadStats()
})
</script>

<style scoped>
.system-settings {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  height: 100%;
}

.settings-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
}

.setting-card {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  overflow: hidden;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 1rem 1.5rem;
  border-bottom: 1px solid #334155;
}

.card-icon {
  font-size: 1.5rem;
  color: #135bec;
}

.card-title h3 {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
}

.card-title p {
  font-size: 0.875rem;
  color: #64748b;
  margin-top: 0.125rem;
}

.card-body {
  padding: 1rem 1.5rem;
}

.stat-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #334155;
}

.stat-row:last-child {
  border-bottom: none;
}

.stat-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.stat-value {
  font-size: 0.875rem;
  color: #f1f5f9;
  font-weight: 500;
}

.stat-value.success {
  color: #22c55e;
}

.config-row {
  display: flex;
  justify-content: space-between;
  padding: 0.5rem 0;
  border-bottom: 1px solid #334155;
}

.config-row:last-child {
  border-bottom: none;
}

.config-label {
  font-size: 0.875rem;
  color: #94a3b8;
}

.config-value {
  font-size: 0.875rem;
  color: #f1f5f9;
  font-family: monospace;
}

.status-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.status-badge.success {
  background-color: rgba(34, 197, 94, 0.15);
  color: #22c55e;
}

/* Quick Actions */
.quick-actions {
  background-color: #1e293b;
  border: 1px solid #334155;
  border-radius: 0.5rem;
  padding: 1.5rem;
}

.section-title {
  font-size: 1rem;
  font-weight: 600;
  color: #f1f5f9;
  margin-bottom: 1rem;
}

.actions-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 1rem;
}

.action-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem;
  background-color: #0f172a;
  border: 1px solid #334155;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.action-card:hover {
  background-color: #1e293b;
  border-color: #475569;
}

.action-card .material-symbols-outlined {
  font-size: 1.5rem;
  color: #94a3b8;
}

.action-card span {
  font-size: 0.875rem;
  color: #94a3b8;
}

.action-card.warning:hover .material-symbols-outlined {
  color: #ef4444;
}
</style>
