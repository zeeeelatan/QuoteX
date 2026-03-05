import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import NewRoot from './new/NewRoot.vue'
import router from './new/router'

document.documentElement.classList.add('dark')
createApp(NewRoot).use(ElementPlus).use(router).mount('#app')
