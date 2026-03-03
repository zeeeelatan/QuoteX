<template>
  <div class="personal-settings-page">
    <!-- Page Header -->
    <div class="page-header">
      <div class="header-left">
        <h1 class="page-title">个人资料与企业配置中心</h1>
        <p class="page-subtitle">管理您的个人账号、所属公司信息以及客户资料库</p>
      </div>
      <div class="header-actions">
        <button class="btn-cancel" @click="handleCancel">取消</button>
        <button class="btn-save" @click="handleSave">保存所有更改</button>
      </div>
    </div>

    <!-- Content Grid -->
    <div class="settings-grid">
      <!-- 账号基本资料 -->
      <section class="glass-card">
        <div class="card-header">
          <span class="material-symbols-outlined text-primary">badge</span>
          <h2 class="card-title">账号基本资料</h2>
        </div>
        <div class="avatar-section">
          <div class="avatar-wrapper">
            <div class="avatar" @click="triggerAvatarUpload">
              <img v-if="formData.avatar" :src="formData.avatar" alt="头像" />
              <span v-else class="material-symbols-outlined">person</span>
            </div>
            <button class="avatar-edit-btn" @click="triggerAvatarUpload">
              <span class="material-symbols-outlined">edit</span>
            </button>
            <input
              type="file"
              ref="avatarInputRef"
              accept="image/*"
              style="display: none;"
              @change="handleAvatarUpload"
            />
          </div>
          <div class="avatar-actions">
            <button class="btn-ai-avatar">
              <span class="material-symbols-outlined">auto_awesome</span>
              AI 生成头像
            </button>
            <p class="avatar-hint">AI 将根据您的职业形象生成专属商务头像</p>
          </div>
        </div>
        <div class="form-grid">
          <div class="form-group">
            <label class="form-label">姓名</label>
            <input type="text" v-model="formData.name" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">联系方式</label>
            <input type="text" v-model="formData.phone" class="form-input" placeholder="输入手机号或电话" />
          </div>
          <div class="form-group">
            <label class="form-label">所属部门</label>
            <input type="text" v-model="formData.department" class="form-input" />
          </div>
          <div class="form-group">
            <label class="form-label">当前职位</label>
            <input type="text" v-model="formData.position" class="form-input" />
          </div>
        </div>
      </section>

      <!-- 公司信息 -->
      <section class="glass-card">
        <div class="card-header">
          <div class="header-with-action">
            <div class="header-title-group">
              <span class="material-symbols-outlined text-primary">corporate_fare</span>
              <h2 class="card-title">公司信息</h2>
            </div>
            <button class="btn-add-company">
              <span class="material-symbols-outlined">add_business</span>
              添加新公司
            </button>
          </div>
        </div>
        <div class="form-stack">
          <!-- 公司 Logo 上传 -->
          <div class="form-group">
            <label class="form-label">公司 Logo</label>
            <div class="company-logo-upload-area">
              <div class="company-logo-preview" @click="triggerCompanyLogoUpload">
                <img v-if="companyData.companyLogo" :src="companyData.companyLogo" alt="公司Logo" class="company-logo-img" />
                <div v-else class="company-logo-placeholder">
                  <span class="material-symbols-outlined">add_photo_alternate</span>
                  <span class="placeholder-text">点击上传 Logo</span>
                </div>
              </div>
              <div class="company-logo-actions">
                <button type="button" class="btn-logo-upload" @click="triggerCompanyLogoUpload">
                  <span class="material-symbols-outlined">upload</span>
                  {{ companyData.companyLogo ? '更换 Logo' : '上传 Logo' }}
                </button>
                <button v-if="companyData.companyLogo" type="button" class="btn-logo-remove" @click="removeCompanyLogo">
                  <span class="material-symbols-outlined">delete</span>
                  移除
                </button>
              </div>
              <input
                type="file"
                ref="companyLogoInputRef"
                accept="image/*"
                style="display: none;"
                @change="handleCompanyLogoUpload"
              />
              <p class="logo-hint">建议上传 PNG/SVG 格式，尺寸不超过 400×200 像素，文件不超过 2MB。上传后将作为报价单默认 Logo。</p>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">公司名称</label>
            <input type="text" v-model="companyData.companyName" class="form-input" placeholder="输入公司全称" />
          </div>
          <div class="form-group">
            <label class="form-label">公司地址</label>
            <input type="text" v-model="companyData.companyAddress" class="form-input" placeholder="输入详细办公地址" />
          </div>
          <div class="form-group">
            <label class="form-label">官网地址</label>
            <input type="url" v-model="companyData.companyWebsite" class="form-input" placeholder="https://www.example.com" />
          </div>
        </div>
        <div class="info-tip">
          <span class="material-symbols-outlined">info</span>
          <p>您可以配置多个公司信息，在创建报价单时灵活切换主体。上传的公司 Logo 将在生成报价单时自动使用。</p>
        </div>
      </section>

      <!-- 业务权限与偏好 -->
      <section class="glass-card">
        <div class="card-header">
          <span class="material-symbols-outlined text-primary">account_tree</span>
          <h2 class="card-title">业务权限与偏好</h2>
        </div>
        <div class="permission-badge">
          <div class="badge-content">
            <p class="badge-label">报价权限等级</p>
            <p class="badge-value">{{ formData.permissionLevel }}</p>
          </div>
          <span class="material-symbols-outlined badge-icon">verified_user</span>
        </div>
        <div class="form-stack">
          <div class="form-group">
            <label class="form-label">所属销售区域</label>
            <select v-model="formData.salesRegion" class="form-select">
              <option value="east">华东大区 (East China)</option>
              <option value="south">华南大区 (South China)</option>
              <option value="north">华北大区 (North China)</option>
              <option value="intl">海外市场 (International)</option>
            </select>
          </div>
          <div class="form-group">
            <label class="form-label">默认计费币种</label>
            <div class="currency-buttons">
              <button
                class="currency-btn"
                :class="{ active: formData.currency === 'CNY' }"
                @click="formData.currency = 'CNY'"
              >CNY (¥)</button>
              <button
                class="currency-btn"
                :class="{ active: formData.currency === 'USD' }"
                @click="formData.currency = 'USD'"
              >USD ($)</button>
              <button
                class="currency-btn"
                :class="{ active: formData.currency === 'EUR' }"
                @click="formData.currency = 'EUR'"
              >EUR (€)</button>
            </div>
          </div>
        </div>
      </section>

      <!-- 安全与验证 -->
      <section class="glass-card">
        <div class="card-header">
          <span class="material-symbols-outlined text-primary">security_update_good</span>
          <h2 class="card-title">安全与验证</h2>
        </div>
        <div class="security-items">
          <div class="security-item">
            <div class="security-info">
              <span class="material-symbols-outlined">smartphone</span>
              <div>
                <p class="security-label">手机号绑定</p>
                <p class="security-value">{{ formData.phone }}</p>
              </div>
            </div>
            <button class="btn-link">更换手机</button>
          </div>
          <div class="security-item">
            <div class="security-info">
              <span class="material-symbols-outlined verified">verified</span>
              <div>
                <p class="security-label">公司邮箱验证</p>
                <p class="security-value">{{ formData.email }}</p>
              </div>
            </div>
            <span class="verified-badge">已验证</span>
          </div>
          <div class="password-section">
            <button class="btn-change-password">
              <span class="material-symbols-outlined">lock_reset</span>
              修改登录密码
            </button>
          </div>
        </div>
      </section>

      <!-- 个性化设置 -->
      <section class="glass-card">
        <div class="card-header">
          <span class="material-symbols-outlined text-primary">stylus_note</span>
          <h2 class="card-title">个性化设置</h2>
        </div>
        <div class="form-stack">
          <div class="form-group">
            <label class="form-label">报价单默认签名档</label>
            <div class="upload-area">
              <span class="material-symbols-outlined">upload_file</span>
              <p>点击或拖拽上传电子签名 (PNG/SVG)</p>
            </div>
          </div>
          <div class="form-group">
            <label class="form-label">常用客户快捷标签</label>
            <div class="tags-container">
              <span class="tag" v-for="tag in formData.tags" :key="tag">
                {{ tag }}
                <span class="material-symbols-outlined tag-close" @click="removeTag(tag)">close</span>
              </span>
              <button class="btn-add-tag">
                <span class="material-symbols-outlined">add</span>
                添加标签
              </button>
            </div>
          </div>
        </div>
      </section>

      <!-- 客户信息管理 -->
      <section class="glass-card full-width">
        <div class="card-header">
          <div class="header-with-action">
            <div class="header-title-group">
              <span class="material-symbols-outlined text-primary">groups_3</span>
              <h2 class="card-title">客户信息管理</h2>
            </div>
            <button class="btn-add-customer" @click="handleAddCustomer">
              <span class="material-symbols-outlined">person_add</span>
              新建客户
            </button>
          </div>
        </div>
        <div class="customer-form">
          <div class="form-group">
            <label class="form-label">客户名称</label>
            <input type="text" class="form-input" v-model="newCustomer.customer_name" placeholder="例如：未来科技集团" />
          </div>
          <div class="form-group">
            <label class="form-label">联系人</label>
            <input type="text" class="form-input" v-model="newCustomer.contact_person" placeholder="例如：李经理" />
          </div>
          <div class="form-group">
            <label class="form-label">联系方式</label>
            <input type="text" class="form-input" v-model="newCustomer.contact_phone" placeholder="电话或邮箱" />
          </div>
          <div class="form-group">
            <label class="form-label">客户地址</label>
            <input type="text" class="form-input" v-model="newCustomer.customer_address" placeholder="办公地址" />
          </div>
        </div>
        <div class="customer-table-wrapper">
          <table class="customer-table">
            <thead>
              <tr>
                <th>客户名称</th>
                <th>主要联系人</th>
                <th>联系方式</th>
                <th>最后更新</th>
                <th class="text-right">操作</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="customer in customers" :key="customer.id">
                <td class="customer-name">{{ customer.customer_name }}</td>
                <td>{{ customer.contact_person }}</td>
                <td>{{ customer.contact_phone }}</td>
                <td class="text-muted">{{ formatDate(customer.updated_at) }}</td>
                <td class="text-right">
                  <button class="btn-link" @click="handleDeleteCustomer(customer.id)">删除</button>
                </td>
              </tr>
              <tr v-if="customers.length === 0">
                <td colspan="5" class="text-center text-muted">暂无客户数据</td>
              </tr>
            </tbody>
          </table>
        </div>
      </section>
    </div>

    <!-- Footer -->
    <footer class="page-footer">
      <p>© 2024 智能AI报价系统 | 版本 v2.4.1-stable</p>
      <div class="footer-links">
        <a href="#">隐私权政策</a>
        <a href="#">使用条款</a>
        <a href="#">联系技术支持</a>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import axios from 'axios'

const API_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:5002'

const emit = defineEmits<{
  'go-home': []
}>()

// 头像上传相关
const avatarInputRef = ref<HTMLInputElement | null>(null)

function triggerAvatarUpload() {
  avatarInputRef.value?.click()
}

function handleAvatarUpload(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return

  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.warning('请选择图片文件')
    return
  }

  // 验证文件大小 (最大 2MB)
  if (file.size > 2 * 1024 * 1024) {
    ElMessage.warning('图片大小不能超过 2MB')
    return
  }

  // 将图片转为 base64
  const reader = new FileReader()
  reader.onload = (e) => {
    formData.avatar = e.target?.result as string
    ElMessage.success('头像已更新，请点击"保存所有更改"以保存')
  }
  reader.readAsDataURL(file)

  // 清空 input 以便可以再次选择相同文件
  input.value = ''
}

// 用户资料
const formData = reactive({
  id: 1,
  name: '',
  employeeId: '',
  department: '',
  position: '',
  avatar: '',
  salesRegion: 'east',
  currency: 'CNY',
  phone: '',
  email: '',
  emailVerified: 0,
  permissionLevel: '普通报价师',
  tags: [] as string[]
})

// 公司信息
const companyData = reactive({
  id: 0,
  companyName: '',
  companyAddress: '',
  companyWebsite: '',
  companyLogo: ''
})

// 公司 Logo 上传相关
const companyLogoInputRef = ref<HTMLInputElement | null>(null)

function triggerCompanyLogoUpload() {
  companyLogoInputRef.value?.click()
}

function handleCompanyLogoUpload(event: Event) {
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
    companyData.companyLogo = e.target?.result as string
    ElMessage.success('公司 Logo 已更新，请点击"保存所有更改"以保存')
  }
  reader.readAsDataURL(file)
  input.value = ''
}

function removeCompanyLogo() {
  companyData.companyLogo = ''
  ElMessage.info('公司 Logo 已移除，请点击"保存所有更改"以保存')
}

// 客户列表
const customers = ref<any[]>([])

// 新建客户表单
const newCustomer = reactive({
  customer_name: '',
  contact_person: '',
  contact_phone: '',
  customer_address: ''
})

// 加载用户资料
async function loadUserProfile() {
  try {
    const res = await axios.get(`${API_URL}/user-profile/`)
    const data = res.data
    formData.id = data.id
    formData.name = data.name || ''
    formData.employeeId = data.employee_id || ''
    formData.department = data.department || ''
    formData.position = data.position || ''
    formData.avatar = data.avatar || ''
    formData.salesRegion = data.sales_region || 'east'
    formData.currency = data.currency || 'CNY'
    formData.phone = data.phone || ''
    formData.email = data.email || ''
    formData.emailVerified = data.email_verified || 0
    formData.permissionLevel = data.permission_level || '普通报价师'
    // 解析 tags JSON
    if (data.tags) {
      try {
        formData.tags = JSON.parse(data.tags)
      } catch {
        formData.tags = []
      }
    }
  } catch (err) {
    console.error('加载用户资料失败', err)
  }
}

// 加载公司信息
async function loadCompanyInfo() {
  try {
    const res = await axios.get(`${API_URL}/user-profile/companies`)
    if (res.data && res.data.length > 0) {
      const company = res.data[0]
      companyData.id = company.id
      companyData.companyName = company.company_name || ''
      companyData.companyAddress = company.company_address || ''
      companyData.companyWebsite = company.company_website || ''
      companyData.companyLogo = company.company_logo || ''
    }
  } catch (err) {
    console.error('加载公司信息失败', err)
  }
}

// 加载客户列表
async function loadCustomers() {
  try {
    const res = await axios.get(`${API_URL}/user-profile/customers`)
    customers.value = res.data || []
  } catch (err) {
    console.error('加载客户列表失败', err)
  }
}

// 保存所有更改
async function handleSave() {
  try {
    // 保存用户资料
    await axios.put(`${API_URL}/user-profile/`, {
      name: formData.name,
      department: formData.department,
      position: formData.position,
      avatar: formData.avatar,
      sales_region: formData.salesRegion,
      currency: formData.currency,
      phone: formData.phone,
      email: formData.email,
      tags: JSON.stringify(formData.tags)
    })

    // 保存公司信息
    if (companyData.id) {
      await axios.put(`${API_URL}/user-profile/companies/${companyData.id}`, {
        company_name: companyData.companyName,
        company_address: companyData.companyAddress,
        company_website: companyData.companyWebsite,
        company_logo: companyData.companyLogo
      })
    } else {
      const res = await axios.post(`${API_URL}/user-profile/companies`, {
        user_id: formData.id,
        company_name: companyData.companyName,
        company_address: companyData.companyAddress,
        company_website: companyData.companyWebsite,
        company_logo: companyData.companyLogo
      })
      companyData.id = res.data.id
    }

    ElMessage.success('保存成功')
  } catch (err) {
    console.error('保存失败', err)
    ElMessage.error('保存失败，请重试')
  }
}

// 新建客户
async function handleAddCustomer() {
  if (!newCustomer.customer_name) {
    ElMessage.warning('请输入客户名称')
    return
  }

  try {
    await axios.post(`${API_URL}/user-profile/customers`, {
      customer_name: newCustomer.customer_name,
      contact_person: newCustomer.contact_person,
      contact_phone: newCustomer.contact_phone,
      customer_address: newCustomer.customer_address,
      user_id: formData.id
    })

    ElMessage.success('客户创建成功')

    // 清空表单
    newCustomer.customer_name = ''
    newCustomer.contact_person = ''
    newCustomer.contact_phone = ''
    newCustomer.customer_address = ''

    // 刷新列表
    await loadCustomers()
  } catch (err) {
    console.error('创建客户失败', err)
    ElMessage.error('创建客户失败，请重试')
  }
}

// 删除客户
async function handleDeleteCustomer(customerId: number) {
  try {
    await axios.delete(`${API_URL}/user-profile/customers/${customerId}`)
    ElMessage.success('客户已删除')
    await loadCustomers()
  } catch (err) {
    console.error('删除客户失败', err)
    ElMessage.error('删除失败，请重试')
  }
}

// 格式化日期
function formatDate(dateStr: string | null) {
  if (!dateStr) return '-'
  const date = new Date(dateStr)
  return date.toLocaleDateString('zh-CN')
}

function handleCancel() {
  emit('go-home')
}

function removeTag(tag: string) {
  const index = formData.tags.indexOf(tag)
  if (index > -1) {
    formData.tags.splice(index, 1)
  }
}

// 初始化加载数据
onMounted(async () => {
  await Promise.all([
    loadUserProfile(),
    loadCompanyInfo(),
    loadCustomers()
  ])
})
</script>

<style scoped>
.personal-settings-page {
  padding: 2rem 3rem;
  min-height: 100%;
  background: var(--bg-primary, #0f1923);
}

/* Page Header */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 2.5rem;
  gap: 1rem;
  flex-wrap: wrap;
}

.page-title {
  font-size: 1.875rem;
  font-weight: 900;
  color: #fff;
  letter-spacing: -0.025em;
  margin-bottom: 0.5rem;
}

.page-subtitle {
  color: #94a3b8;
  font-size: 0.875rem;
}

.header-actions {
  display: flex;
  gap: 0.75rem;
}

.btn-cancel {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  background: rgba(255, 255, 255, 0.05);
  color: #fff;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel:hover {
  background: rgba(255, 255, 255, 0.1);
}

.btn-save {
  padding: 0.625rem 1.5rem;
  border-radius: 0.5rem;
  background: #007AFF;
  color: #fff;
  font-weight: 700;
  border: none;
  cursor: pointer;
  transition: all 0.3s;
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.5);
}

.btn-save:hover {
  box-shadow: 0 0 20px rgba(0, 122, 255, 0.7);
  transform: translateY(-1px);
}

/* Settings Grid */
.settings-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1.5rem;
}

@media (max-width: 1024px) {
  .settings-grid {
    grid-template-columns: 1fr;
  }
}

/* Glass Card */
.glass-card {
  background: rgba(22, 34, 46, 0.8);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 1rem;
  padding: 1.5rem;
}

.glass-card.full-width {
  grid-column: 1 / -1;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.card-header .text-primary {
  color: #007AFF;
}

.card-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #fff;
}

.header-with-action {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.header-title-group {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

/* Avatar Section */
.avatar-section {
  display: flex;
  align-items: center;
  gap: 1.5rem;
  margin-bottom: 2rem;
}

.avatar-wrapper {
  position: relative;
}

.avatar {
  width: 7rem;
  height: 7rem;
  border-radius: 50%;
  border: 4px solid rgba(0, 122, 255, 0.3);
  overflow: hidden;
  background: #1e293b;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.avatar:hover {
  border-color: #007AFF;
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.4);
}

.avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar .material-symbols-outlined {
  font-size: 3rem;
  color: #64748b;
}

.avatar-edit-btn {
  position: absolute;
  bottom: -0.25rem;
  right: -0.25rem;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  background: #007AFF;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  border: 2px solid #0f1923;
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}

.avatar-edit-btn .material-symbols-outlined {
  font-size: 0.875rem;
}

.avatar-actions {
  flex: 1;
}

.btn-ai-avatar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 1rem;
  border-radius: 0.5rem;
  background: rgba(0, 122, 255, 0.2);
  color: #007AFF;
  border: 1px solid rgba(0, 122, 255, 0.3);
  font-size: 0.875rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-ai-avatar:hover {
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.5);
}

.btn-ai-avatar .material-symbols-outlined {
  font-size: 1rem;
}

.avatar-hint {
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
  margin-top: 0.75rem;
}

/* Form Styles */
.form-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
}

@media (max-width: 600px) {
  .form-grid {
    grid-template-columns: 1fr;
  }
}

.form-stack {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 0.375rem;
}

.form-label {
  font-size: 0.75rem;
  font-weight: 500;
  color: #94a3b8;
  margin-left: 0.25rem;
}

.form-input,
.form-select {
  width: 100%;
  padding: 0.625rem 0.75rem;
  background: #1A222D;
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  color: #fff;
  font-size: 0.875rem;
  transition: all 0.2s;
}

.form-input:focus,
.form-select:focus {
  outline: none;
  border-color: #007AFF;
  box-shadow: 0 0 0 2px rgba(0, 122, 255, 0.2);
}

.form-input.disabled {
  color: #64748b;
  cursor: not-allowed;
  opacity: 0.6;
}

.form-input::placeholder {
  color: #64748b;
}

/* Info Tip */
.info-tip {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: rgba(0, 122, 255, 0.05);
  border: 1px solid rgba(0, 122, 255, 0.1);
  margin-top: 1.5rem;
}

.info-tip .material-symbols-outlined {
  color: #007AFF;
  font-size: 1rem;
}

.info-tip p {
  font-size: 0.625rem;
  color: #94a3b8;
}

/* Permission Badge */
.permission-badge {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem;
  border-radius: 0.75rem;
  background: linear-gradient(to right, rgba(0, 122, 255, 0.1), transparent);
  border: 1px solid rgba(0, 122, 255, 0.2);
  margin-bottom: 1.5rem;
}

.badge-label {
  font-size: 0.75rem;
  color: #94a3b8;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: 0.25rem;
}

.badge-value {
  font-size: 1.125rem;
  font-weight: 700;
  color: #007AFF;
  letter-spacing: -0.025em;
}

.badge-icon {
  font-size: 1.875rem;
  color: rgba(0, 122, 255, 0.4);
}

/* Currency Buttons */
.currency-buttons {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 0.5rem;
}

.currency-btn {
  padding: 0.5rem;
  border-radius: 0.5rem;
  background: #1A222D;
  color: #cbd5e1;
  font-size: 0.75rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.2s;
}

.currency-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.currency-btn.active {
  background: #007AFF;
  color: #fff;
  border-color: #007AFF;
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.5);
}

/* Security Items */
.security-items {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.security-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem;
  border-radius: 0.75rem;
  background: #1A222D;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.security-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.security-info .material-symbols-outlined {
  color: #94a3b8;
}

.security-info .material-symbols-outlined.verified {
  color: #007AFF;
}

.security-label {
  font-size: 0.75rem;
  color: #64748b;
}

.security-value {
  font-size: 0.875rem;
  color: #fff;
  font-weight: 500;
}

.btn-link {
  background: none;
  border: none;
  color: #007AFF;
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-link:hover {
  text-decoration: underline;
}

.verified-badge {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  background: rgba(34, 197, 94, 0.2);
  color: #4ade80;
  font-size: 0.625rem;
  font-weight: 700;
}

.password-section {
  padding-top: 1rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
}

.btn-change-password {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem;
  border-radius: 0.5rem;
  background: #1A222D;
  color: #fff;
  font-size: 0.875rem;
  font-weight: 700;
  border: 1px solid rgba(255, 255, 255, 0.1);
  cursor: pointer;
  transition: all 0.3s;
}

.btn-change-password:hover {
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.3);
}

.btn-change-password .material-symbols-outlined {
  font-size: 1.125rem;
}

/* Upload Area */
.upload-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  border: 2px dashed rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
  background: #1A222D;
  cursor: pointer;
  transition: all 0.2s;
}

.upload-area:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(0, 122, 255, 0.5);
}

.upload-area .material-symbols-outlined {
  color: #64748b;
  margin-bottom: 0.5rem;
}

.upload-area:hover .material-symbols-outlined {
  color: #007AFF;
}

.upload-area p {
  font-size: 0.75rem;
  color: #94a3b8;
}

/* Tags */
.tags-container {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: rgba(0, 122, 255, 0.2);
  color: #007AFF;
  font-size: 0.625rem;
  font-weight: 700;
  border: 1px solid rgba(0, 122, 255, 0.3);
}

.tag-close {
  font-size: 0.75rem;
  cursor: pointer;
}

.btn-add-tag {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.25rem 0.75rem;
  border-radius: 9999px;
  background: #1A222D;
  color: #64748b;
  font-size: 0.625rem;
  font-weight: 700;
  border: 1px dashed rgba(255, 255, 255, 0.2);
  cursor: pointer;
  transition: all 0.2s;
}

.btn-add-tag:hover {
  border-color: rgba(0, 122, 255, 0.5);
  color: #007AFF;
}

.btn-add-tag .material-symbols-outlined {
  font-size: 0.75rem;
}

/* Add Buttons */
.btn-add-company,
.btn-add-customer {
  display: flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  border-radius: 0.5rem;
  background: rgba(0, 122, 255, 0.2);
  color: #007AFF;
  border: 1px solid rgba(0, 122, 255, 0.3);
  font-size: 0.75rem;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-add-company:hover,
.btn-add-customer:hover {
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.5);
}

.btn-add-company .material-symbols-outlined,
.btn-add-customer .material-symbols-outlined {
  font-size: 1rem;
}

.btn-add-customer {
  padding: 0.5rem 1.25rem;
  background: #007AFF;
  color: #fff;
  border: none;
  box-shadow: 0 0 15px rgba(0, 122, 255, 0.5);
}

/* Customer Form */
.customer-form {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1rem;
  margin-bottom: 2rem;
}

@media (max-width: 1024px) {
  .customer-form {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 600px) {
  .customer-form {
    grid-template-columns: 1fr;
  }
}

/* Customer Table */
.customer-table-wrapper {
  overflow: hidden;
  border-radius: 0.75rem;
  border: 1px solid rgba(255, 255, 255, 0.05);
  background: rgba(26, 34, 45, 0.5);
}

.customer-table {
  width: 100%;
  text-align: left;
  font-size: 0.875rem;
  border-collapse: collapse;
}

.customer-table thead {
  background: rgba(255, 255, 255, 0.1);
}

.customer-table th {
  padding: 0.75rem 1rem;
  font-weight: 600;
  color: #94a3b8;
}

.customer-table tbody tr {
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  transition: background 0.2s;
}

.customer-table tbody tr:hover {
  background: rgba(255, 255, 255, 0.05);
}

.customer-table td {
  padding: 1rem;
  color: #cbd5e1;
}

.customer-table .customer-name {
  color: #fff;
  font-weight: 500;
}

.customer-table .text-muted {
  color: #64748b;
}

.customer-table .text-center {
  text-align: center;
  padding: 2rem 1rem;
}

.customer-table .text-right {
  text-align: right;
}

/* Footer */
.page-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 2rem 0;
  margin-top: 3rem;
  border-top: 1px solid rgba(255, 255, 255, 0.05);
  color: #64748b;
  font-size: 0.75rem;
  flex-wrap: wrap;
  gap: 1rem;
}

.footer-links {
  display: flex;
  gap: 1.5rem;
}

.footer-links a {
  color: #64748b;
  text-decoration: none;
  transition: color 0.2s;
}

.footer-links a:hover {
  color: #cbd5e1;
}

/* 公司 Logo 上传区域 */
.company-logo-upload-area {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.company-logo-preview {
  width: 200px;
  height: 80px;
  border-radius: 0.5rem;
  border: 2px dashed rgba(148, 163, 184, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  overflow: hidden;
  transition: all 0.3s;
  background: rgba(15, 23, 42, 0.4);
}

.company-logo-preview:hover {
  border-color: rgba(0, 122, 255, 0.5);
  background: rgba(0, 122, 255, 0.05);
}

.company-logo-img {
  max-width: 100%;
  max-height: 100%;
  object-fit: contain;
}

.company-logo-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  color: #64748b;
}

.company-logo-placeholder .material-symbols-outlined {
  font-size: 1.5rem;
}

.company-logo-placeholder .placeholder-text {
  font-size: 0.75rem;
}

.company-logo-actions {
  display: flex;
  gap: 0.5rem;
}

.btn-logo-upload,
.btn-logo-remove {
  display: flex;
  align-items: center;
  gap: 0.25rem;
  padding: 0.35rem 0.75rem;
  border-radius: 0.375rem;
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid;
}

.btn-logo-upload {
  background: rgba(0, 122, 255, 0.15);
  color: #60a5fa;
  border-color: rgba(0, 122, 255, 0.3);
}
.btn-logo-upload:hover {
  background: rgba(0, 122, 255, 0.25);
}

.btn-logo-remove {
  background: rgba(239, 68, 68, 0.1);
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.3);
}
.btn-logo-remove:hover {
  background: rgba(239, 68, 68, 0.2);
}

.btn-logo-upload .material-symbols-outlined,
.btn-logo-remove .material-symbols-outlined {
  font-size: 1rem;
}

.logo-hint {
  font-size: 0.75rem;
  color: #64748b;
  line-height: 1.4;
}
</style>
