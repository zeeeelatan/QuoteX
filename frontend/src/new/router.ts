import { createRouter, createWebHistory } from 'vue-router'
import NewHome from './views/NewHome.vue'
import HomePage from './views/HomePage.vue'
import DocumentRecognition from './views/DocumentRecognition.vue'
import SmartMatching from './views/SmartMatching.vue'
import PriceAdjustment from './views/PriceAdjustment.vue'
import QuotationGeneration from './views/QuotationGeneration.vue'
import ProductDatabase from './views/ProductDatabase.vue'
import AdminLogin from './views/AdminLogin.vue'
import AdminDashboard from './views/AdminDashboard.vue'
import QuoteHistory from './views/QuoteHistory.vue'
import QuoteManagement from './views/QuoteManagement.vue'
import OnsiteServiceCalculator from './components/pricing/OnsiteServiceCalculator.vue'
import { openSystemSettings } from './stores/settingsDialogStore'
const router = createRouter({
  history: createWebHistory('/'),
  routes: [
    {
      path: '/',
      name: 'HomePage',
      component: HomePage,
    },
    {
      path: '/home',
      name: 'NewHome',
      component: NewHome,
    },
    {
      path: '/document-recognition',
      name: 'DocumentRecognition',
      component: DocumentRecognition,
    },
    {
      path: '/smart-matching',
      name: 'SmartMatching',
      component: SmartMatching,
    },
    {
      path: '/price-adjustment',
      name: 'PriceAdjustment',
      component: PriceAdjustment,
    },
    {
      path: '/quotation-generation',
      name: 'QuotationGeneration',
      component: QuotationGeneration,
    },
    {
      path: '/product-database',
      name: 'ProductDatabase',
      component: ProductDatabase,
    },
    {
      path: '/quote-history',
      name: 'QuoteHistory',
      component: QuoteHistory,
    },
    {
      path: '/quote-management',
      name: 'QuoteManagement',
      component: QuoteManagement,
    },
    {
      // /system-settings 不再是独立页面，重定向到首页并以弹窗形式打开
      path: '/system-settings',
      name: 'SystemSettings',
      redirect: () => {
        openSystemSettings()
        return '/'
      },
    },
    {
      path: '/onsite-calculator',
      name: 'OnsiteServiceCalculator',
      component: OnsiteServiceCalculator,
    },
    // Admin routes
    {
      path: '/admin',
      name: 'AdminLogin',
      component: AdminLogin,
    },
    {
      path: '/admin/dashboard',
      name: 'AdminDashboard',
      component: AdminDashboard,
    },
    {
      path: '/:pathMatch(.*)*',
      redirect: '/',
    },
  ],
})

export default router







