<template>
  <Teleport to="body">
    <Transition name="settings-dialog">
      <div v-if="currentSettingsDialog" class="settings-dialog-overlay" @click.self="closeSettingsDialog">
        <div class="settings-dialog-container">
          <div class="settings-dialog-header">
            <button class="settings-dialog-close" @click="closeSettingsDialog">
              <span class="material-symbols-outlined">close</span>
            </button>
          </div>
          <div class="settings-dialog-body">
            <SystemSettings
              v-if="currentSettingsDialog === 'system-settings'"
              @go-home="closeSettingsDialog"
            />
            <PersonalSettings
              v-if="currentSettingsDialog === 'personal-settings'"
              @go-home="closeSettingsDialog"
            />
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
import { watch } from 'vue'
import SystemSettings from '../views/SystemSettings.vue'
import PersonalSettings from '../views/PersonalSettings.vue'
import { currentSettingsDialog, closeSettingsDialog } from '../stores/settingsDialogStore'

// 弹窗打开时禁止背景滚动
watch(currentSettingsDialog, (val) => {
  if (val) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.settings-dialog-overlay {
  position: fixed;
  inset: 0;
  z-index: 99990;
  background-color: rgba(0, 0, 0, 0.6);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
}

.settings-dialog-container {
  position: relative;
  width: 92vw;
  max-width: 1200px;
  height: 90vh;
  background-color: #0f1623;
  border: 1px solid #232f48;
  border-radius: 1rem;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.settings-dialog-header {
  position: absolute;
  top: 0.75rem;
  right: 0.75rem;
  z-index: 10;
}

.settings-dialog-close {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 0.5rem;
  border: 1px solid #232f48;
  background-color: rgba(15, 22, 35, 0.9);
  color: #94a3b8;
  cursor: pointer;
  transition: all 0.2s;
}

.settings-dialog-close:hover {
  color: #ffffff;
  background-color: rgba(239, 68, 68, 0.2);
  border-color: rgba(239, 68, 68, 0.4);
}

.settings-dialog-body {
  flex: 1;
  overflow-y: auto;
  padding: 0;
}

/* 让内嵌的设置页面适应弹窗容器 */
.settings-dialog-body :deep(.system-settings-page),
.settings-dialog-body :deep(.personal-settings-page) {
  min-height: 100%;
}

/* 隐藏内嵌设置页面的返回按钮（弹窗已有关闭按钮） */
.settings-dialog-body :deep(.back-btn) {
  display: none;
}

/* 动画 */
.settings-dialog-enter-active,
.settings-dialog-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.settings-dialog-enter-active .settings-dialog-container,
.settings-dialog-leave-active .settings-dialog-container {
  transition: transform 0.25s ease;
}

.settings-dialog-enter-from,
.settings-dialog-leave-to {
  opacity: 0;
}

.settings-dialog-enter-from .settings-dialog-container {
  transform: scale(0.95) translateY(1rem);
}

.settings-dialog-leave-to .settings-dialog-container {
  transform: scale(0.95) translateY(1rem);
}
</style>
