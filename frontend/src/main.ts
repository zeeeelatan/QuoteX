import { createApp } from 'vue'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'

async function bootstrap() {
  const pathname = window.location.pathname || '/'
  const isNew = pathname === '/new' || pathname.startsWith('/new/')

  if (isNew) {
    // 新版页面默认启用深色背景（与 dist 行为保持一致）
    document.documentElement.classList.add('dark')

    const [{ default: NewRoot }, { default: router }] = await Promise.all([
      import('./new/NewRoot.vue'),
      import('./new/router'),
    ])

    createApp(NewRoot).use(ElementPlus).use(router).mount('#app')
  } else {
    document.documentElement.classList.remove('dark')

    const { default: App } = await import('./App.vue')
    createApp(App).use(ElementPlus).mount('#app')
  }
}

bootstrap()