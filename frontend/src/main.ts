import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import NewRoot from './new/NewRoot.vue'
import router from './new/router'
import { initAxiosAuth } from './new/stores/authStore'

document.documentElement.classList.add('dark')
// 启动时把 localStorage 里的 token 装回 axios 默认 Authorization 头，
// 避免页面刷新后所有 API 都因缺 token 而 401
initAxiosAuth()
createApp(NewRoot).use(ElementPlus).use(router).mount('#app')
