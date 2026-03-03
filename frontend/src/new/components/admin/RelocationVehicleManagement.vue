<template>
  <div class="relocation-vehicle-management">
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn btn-primary" @click="openAddDialog">
          <span class="material-symbols-outlined">add_circle</span>
          添加数据
        </button>
        <button class="btn btn-success" @click="triggerImport">
          <span class="material-symbols-outlined">upload</span>
          导入Excel
        </button>
        <button class="btn btn-danger" @click="confirmClear">
          <span class="material-symbols-outlined">delete_sweep</span>
          清空数据
        </button>
        <input
          ref="importInput"
          type="file"
          accept=".xlsx,.xls"
          style="display: none"
          @change="handleImportFile"
        />
      </div>
      <div class="toolbar-right">
        <span class="total-count">共 {{ list.length }} 条</span>
      </div>
    </div>

    <div class="table-container" :class="{ loading: loading }">
      <div v-if="loading" class="loading-overlay">
        <div class="loading-spinner"></div>
        <span>加载中...</span>
      </div>
      <div class="table-scroll">
        <table class="data-table">
          <thead>
            <tr>
              <th>序号</th>
              <th>车型分类</th>
              <th>车型名称</th>
              <th>车厢长(m)</th>
              <th>车厢宽(m)</th>
              <th>车厢高(m)</th>
              <th>容积(m³)</th>
              <th>载重(吨)</th>
              <th>可装1U(台)</th>
              <th>可装2U(台)</th>
              <th>可装机柜</th>
              <th>适用场景</th>
              <th>运输距离建议</th>
              <th>特殊驾照</th>
              <th>市区限行</th>
              <th>地库限高</th>
              <th>起步价(元)</th>
              <th>公里价(元/km)</th>
              <th>备注</th>
              <th class="text-center">操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="row in list" :key="row.id">
              <td>{{ row.seq_no ?? '-' }}</td>
              <td>{{ row.vehicle_category ?? '-' }}</td>
              <td>{{ row.vehicle_name ?? '-' }}</td>
              <td class="num-cell">{{ row.length_m ?? '-' }}</td>
              <td class="num-cell">{{ row.width_m ?? '-' }}</td>
              <td class="num-cell">{{ row.height_m ?? '-' }}</td>
              <td class="num-cell">{{ row.volume_m3 ?? '-' }}</td>
              <td class="num-cell">{{ row.load_ton ?? '-' }}</td>
              <td>{{ row.server_1u ?? '-' }}</td>
              <td>{{ row.server_2u ?? '-' }}</td>
              <td>{{ row.rack_count ?? '-' }}</td>
              <td class="desc-cell">{{ row.scenario ?? '-' }}</td>
              <td>{{ row.distance_advice ?? '-' }}</td>
              <td>{{ row.license_required ?? '-' }}</td>
              <td>{{ row.city_restrict ?? '-' }}</td>
              <td>{{ row.basement_limit ?? '-' }}</td>
              <td>{{ row.start_price ?? '-' }}</td>
              <td>{{ row.km_price ?? '-' }}</td>
              <td class="desc-cell">{{ row.remark ?? '-' }}</td>
              <td class="text-center">
                <button class="action-btn edit-btn" @click="openEditDialog(row)" title="编辑">
                  <span class="material-symbols-outlined">edit</span>
                </button>
                <button class="action-btn delete-btn" @click="confirmDelete(row)" title="删除">
                  <span class="material-symbols-outlined">delete</span>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <div v-if="!loading && list.length === 0" class="empty-state">
        <span class="material-symbols-outlined">local_shipping</span>
        <p>暂无机房搬迁车型数据，请导入 Excel 或添加数据</p>
      </div>
    </div>

    <!-- 添加/编辑弹窗 -->
    <el-dialog
      v-model="dialogVisible"
      :title="isEditMode ? '编辑数据' : '添加数据'"
      width="720px"
      :close-on-click-modal="false"
    >
      <el-form :model="formData" label-width="120px" class="form-dialog">
        <div class="form-section-title">基本信息</div>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="序号">
              <el-input-number v-model="formData.seq_no" :min="0" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="车型分类">
              <el-input v-model="formData.vehicle_category" placeholder="如：厢式货车" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="车型名称">
              <el-input v-model="formData.vehicle_name" placeholder="车型名称" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">车厢尺寸与载重</div>
        <el-row :gutter="16">
          <el-col :span="6">
            <el-form-item label="车厢长(m)">
              <el-input-number v-model="formData.length_m" :min="0" :precision="2" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="车厢宽(m)">
              <el-input-number v-model="formData.width_m" :min="0" :precision="2" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="车厢高(m)">
              <el-input-number v-model="formData.height_m" :min="0" :precision="2" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
          <el-col :span="6">
            <el-form-item label="容积(m³)">
              <el-input-number v-model="formData.volume_m3" :min="0" :precision="2" controls-position="right" style="width: 100%" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="载重量(吨)">
          <el-input-number v-model="formData.load_ton" :min="0" :precision="2" controls-position="right" style="width: 200px" />
        </el-form-item>
        <div class="form-section-title">装载能力</div>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-form-item label="可装1U(台)">
              <el-input v-model="formData.server_1u" placeholder="如：80" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="可装2U(台)">
              <el-input v-model="formData.server_2u" placeholder="如：40" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="可装机柜(个)">
              <el-input v-model="formData.rack_count" placeholder="如：2" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">场景与限制</div>
        <el-form-item label="适用场景">
          <el-input v-model="formData.scenario" type="textarea" :rows="2" placeholder="适用场景说明" />
        </el-form-item>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="运输距离建议">
              <el-input v-model="formData.distance_advice" placeholder="如：同城/跨城" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="是否需特殊驾照">
              <el-input v-model="formData.license_required" placeholder="如：B照" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="市区限行情况">
              <el-input v-model="formData.city_restrict" placeholder="限行说明" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="地库限高通过">
              <el-input v-model="formData.basement_limit" placeholder="如：2.2m" />
            </el-form-item>
          </el-col>
        </el-row>
        <div class="form-section-title">价格</div>
        <el-row :gutter="16">
          <el-col :span="12">
            <el-form-item label="参考起步价(元)">
              <el-input v-model="formData.start_price" placeholder="如：500" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="参考公里价(元/km)">
              <el-input v-model="formData.km_price" placeholder="如：8" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="备注">
          <el-input v-model="formData.remark" type="textarea" :rows="2" placeholder="备注" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="saveData">确定</el-button>
      </template>
    </el-dialog>

    <!-- 删除确认弹窗 -->
    <el-dialog
      v-model="deleteDialogVisible"
      title="确认删除"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>确定要删除这条机房搬迁车型数据吗？</p>
      <template #footer>
        <el-button @click="deleteDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="doDelete">确定</el-button>
      </template>
    </el-dialog>

    <!-- 清空确认弹窗 -->
    <el-dialog
      v-model="clearDialogVisible"
      title="确认清空"
      width="400px"
      :close-on-click-modal="false"
    >
      <p>确定要清空所有机房搬迁车型数据吗？此操作不可恢复。</p>
      <template #footer>
        <el-button @click="clearDialogVisible = false">取消</el-button>
        <el-button type="danger" @click="doClear">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { ElMessage } from 'element-plus'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const list = ref<any[]>([])
const loading = ref(false)
const importInput = ref<HTMLInputElement | null>(null)

const dialogVisible = ref(false)
const isEditMode = ref(false)
const currentEditId = ref<number | null>(null)
const formData = ref<Record<string, any>>({
  seq_no: null,
  vehicle_category: '',
  vehicle_name: '',
  length_m: null,
  width_m: null,
  height_m: null,
  volume_m3: null,
  load_ton: null,
  server_1u: '',
  server_2u: '',
  rack_count: '',
  scenario: '',
  distance_advice: '',
  license_required: '',
  city_restrict: '',
  basement_limit: '',
  start_price: '',
  km_price: '',
  remark: ''
})

const deleteDialogVisible = ref(false)
const clearDialogVisible = ref(false)
const itemToDelete = ref<any>(null)

function getEmptyForm() {
  return {
    seq_no: null,
    vehicle_category: '',
    vehicle_name: '',
    length_m: null,
    width_m: null,
    height_m: null,
    volume_m3: null,
    load_ton: null,
    server_1u: '',
    server_2u: '',
    rack_count: '',
    scenario: '',
    distance_advice: '',
    license_required: '',
    city_restrict: '',
    basement_limit: '',
    start_price: '',
    km_price: '',
    remark: ''
  }
}

function openAddDialog() {
  isEditMode.value = false
  currentEditId.value = null
  formData.value = getEmptyForm()
  dialogVisible.value = true
}

function openEditDialog(row: any) {
  isEditMode.value = true
  currentEditId.value = row.id
  formData.value = {
    seq_no: row.seq_no ?? null,
    vehicle_category: row.vehicle_category ?? '',
    vehicle_name: row.vehicle_name ?? '',
    length_m: row.length_m != null ? Number(row.length_m) : null,
    width_m: row.width_m != null ? Number(row.width_m) : null,
    height_m: row.height_m != null ? Number(row.height_m) : null,
    volume_m3: row.volume_m3 != null ? Number(row.volume_m3) : null,
    load_ton: row.load_ton != null ? Number(row.load_ton) : null,
    server_1u: row.server_1u ?? '',
    server_2u: row.server_2u ?? '',
    rack_count: row.rack_count ?? '',
    scenario: row.scenario ?? '',
    distance_advice: row.distance_advice ?? '',
    license_required: row.license_required ?? '',
    city_restrict: row.city_restrict ?? '',
    basement_limit: row.basement_limit ?? '',
    start_price: row.start_price ?? '',
    km_price: row.km_price ?? '',
    remark: row.remark ?? ''
  }
  dialogVisible.value = true
}

async function saveData() {
  try {
    const payload = { ...formData.value }
    if (isEditMode.value && currentEditId.value != null) {
      await axios.put(`${API_URL}/relocation-vehicle/${currentEditId.value}`, payload)
      ElMessage.success('更新成功')
    } else {
      await axios.post(`${API_URL}/relocation-vehicle/`, payload)
      ElMessage.success('添加成功')
    }
    dialogVisible.value = false
    await fetchList()
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '保存失败')
  }
}

function confirmDelete(row: any) {
  itemToDelete.value = row
  deleteDialogVisible.value = true
}

async function doDelete() {
  if (!itemToDelete.value) return
  try {
    await axios.delete(`${API_URL}/relocation-vehicle/${itemToDelete.value.id}`)
    ElMessage.success('删除成功')
    deleteDialogVisible.value = false
    itemToDelete.value = null
    await fetchList()
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '删除失败')
  }
}

function confirmClear() {
  clearDialogVisible.value = true
}

async function doClear() {
  try {
    await axios.delete(`${API_URL}/relocation-vehicle/clear`)
    ElMessage.success('已清空')
    clearDialogVisible.value = false
    await fetchList()
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '清空失败')
  }
}

async function fetchList() {
  loading.value = true
  try {
    const res = await axios.get(`${API_URL}/relocation-vehicle/`)
    list.value = res.data || []
  } catch (err) {
    console.error('加载机房搬迁车型数据失败:', err)
    ElMessage.error('加载失败')
  } finally {
    loading.value = false
  }
}

function triggerImport() {
  importInput.value?.click()
}

async function handleImportFile(e: Event) {
  const target = e.target as HTMLInputElement
  const file = target.files?.[0]
  if (!file) return
  loading.value = true
  try {
    const form = new FormData()
    form.append('file', file)
    const res = await axios.post(`${API_URL}/relocation-vehicle/import`, form, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    const msg = res.data?.message || `成功导入 ${res.data?.count ?? 0} 条`
    ElMessage.success(msg)
    await fetchList()
  } catch (err: any) {
    const detail = err?.response?.data?.detail
    ElMessage.error(typeof detail === 'string' ? detail : '导入失败')
  } finally {
    loading.value = false
  }
  target.value = ''
}

onMounted(() => {
  fetchList()
})
</script>

<style scoped>
.relocation-vehicle-management {
  display: flex;
  flex-direction: column;
  height: 100%;
  gap: 1rem;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 0.75rem;
}

.toolbar-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.toolbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.total-count {
  font-size: 0.875rem;
  color: #94a3b8;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background-color: #135bec;
  color: white;
}

.btn-primary:hover {
  background-color: #0d4fd6;
}

.btn-success {
  background-color: #22c55e;
  color: white;
}

.btn-success:hover {
  background-color: #16a34a;
}

.btn-danger {
  background-color: #ef4444;
  color: white;
}

.btn-danger:hover {
  background-color: #dc2626;
}

.text-center {
  text-align: center;
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  border-radius: 0.375rem;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
  margin: 0 0.125rem;
}

.action-btn .material-symbols-outlined {
  font-size: 1rem;
}

.edit-btn {
  background-color: rgba(19, 91, 236, 0.1);
  color: #135bec;
}

.edit-btn:hover {
  background-color: rgba(19, 91, 236, 0.2);
}

.delete-btn {
  background-color: rgba(239, 68, 68, 0.1);
  color: #ef4444;
}

.delete-btn:hover {
  background-color: rgba(239, 68, 68, 0.2);
}

.form-section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: #94a3b8;
  margin: 1rem 0 0.5rem;
  padding-bottom: 0.25rem;
}

.form-section-title:first-child {
  margin-top: 0;
}

.table-container {
  flex: 1;
  min-height: 0;
  position: relative;
  background: rgba(30, 41, 59, 0.5);
  border: 1px solid #334155;
  border-radius: 0.75rem;
  overflow: hidden;
}

.table-container.loading {
  pointer-events: none;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  background: rgba(15, 23, 42, 0.8);
  color: #94a3b8;
  z-index: 10;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 2px solid #334155;
  border-top-color: #38bdf8;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.table-scroll {
  overflow-x: auto;
  overflow-y: auto;
  max-height: 100%;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.8125rem;
}

.data-table th,
.data-table td {
  padding: 0.5rem 0.625rem;
  text-align: left;
  border-bottom: 1px solid #334155;
  white-space: nowrap;
}

.data-table th {
  background: #1e293b;
  color: #94a3b8;
  font-weight: 600;
  position: sticky;
  top: 0;
  z-index: 1;
}

.data-table td {
  color: #e2e8f0;
}

.data-table tbody tr:hover {
  background: rgba(56, 189, 248, 0.06);
}

.num-cell {
  text-align: right;
}

.desc-cell {
  max-width: 12rem;
  white-space: normal;
  word-break: break-word;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: #64748b;
}

.empty-state .material-symbols-outlined {
  font-size: 3rem;
  margin-bottom: 0.5rem;
}

.empty-state p {
  margin: 0;
  font-size: 0.875rem;
}
</style>
