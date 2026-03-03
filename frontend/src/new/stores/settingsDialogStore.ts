/**
 * 设置弹窗全局状态管理
 * 允许在任意页面以弹窗形式打开「系统设置」或「个人设置」，
 * 关闭后自动返回原来的页面，无需路由跳转。
 */
import { ref } from 'vue'

export type SettingsDialogType = 'system-settings' | 'personal-settings' | null

const activeSettingsDialog = ref<SettingsDialogType>(null)

/** 打开系统设置弹窗 */
export function openSystemSettings() {
  activeSettingsDialog.value = 'system-settings'
}

/** 打开个人设置弹窗 */
export function openPersonalSettings() {
  activeSettingsDialog.value = 'personal-settings'
}

/** 关闭设置弹窗 */
export function closeSettingsDialog() {
  activeSettingsDialog.value = null
}

/** 当前打开的弹窗类型（响应式） */
export const currentSettingsDialog = activeSettingsDialog
