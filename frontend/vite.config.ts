import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  // 前端请求用的 base URL：开发时用 /api 走代理，否则直连后端
  const apiTarget = env.VITE_API_BASE_URL || 'http://localhost:5002'
  // 代理 target 必须是完整 URL，不能是相对路径 /api，否则 Vite 解析会报错
  const proxyTarget =
    env.VITE_PROXY_TARGET ||
    (apiTarget.startsWith('http') ? apiTarget : 'http://localhost:5002')

  return {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, './src')
      }
    },
    plugins: [vue()],
    server: {
      host: '0.0.0.0',
      port: 3008,
      strictPort: true,
      cors: true,
      proxy: {
        '/api': {
          target: proxyTarget,
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, ''),
        }
      }
    },
    build: {
      outDir: 'dist',
      assetsDir: 'assets',
      sourcemap: false,
      minify: false,
      rollupOptions: {
        output: {
          manualChunks: {
            'vendor': ['vue', 'axios'],
            'xlsx': ['xlsx'],
          }
        }
      },
      chunkSizeWarningLimit: 1000,
    },
    define: {
      'process.env.NODE_ENV': JSON.stringify(mode),
      // 兼容老代码偶尔读取 process.env.VITE_API_BASE_URL 的情况
      'process.env.VITE_API_BASE_URL': JSON.stringify(apiTarget)
    }
  }
})