{
  key: 'service-level',
  icon: () => h(SettingOutlined),
  label: '服务级别管理',
  path: '/admin/service-level'
} 

const menuItems = ref([
  {
    key: 'smart-recognition',
    icon: () => h(FileTextOutlined),
    label: '智能识别',
    path: '/admin/smart-recognition'
  },
  {
    key: 'smart-matching',
    icon: () => h(SearchOutlined),
    label: '智能匹配',
    path: '/admin/smart-matching'
  },
  {
    key: 'quotation',
    icon: () => h(DollarOutlined),
    label: '生成报价单',
    path: '/admin/quotation'
  },
  {
    key: 'manual-search',
    icon: () => h(SearchOutlined),
    label: '手动搜索',
    path: '/admin/manual-search'
  },
  {
    key: 'admin-management',
    icon: () => h(SettingOutlined),
    label: '后台管理',
    children: [
      {
        key: 'rate-management',
        label: '费率管理',
        path: '/admin/rate-management'
      },
      {
        key: 'service-level',
        label: '服务级别管理',
        path: '/admin/service-level'
      }
    ]
  }
]); 