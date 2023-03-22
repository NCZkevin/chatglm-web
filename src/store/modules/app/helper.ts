import { ss } from '@/utils/storage'

const LOCAL_NAME = 'appSetting'

export type Theme = 'light' | 'dark' | 'auto'

export type Language = 'zh-CN' | 'en-US' | 'ja-JP'

export type focusTextarea = true

export interface AppState {
  siderCollapsed: boolean
  theme: Theme
  language: Language
  focusTextarea: focusTextarea
}

export function defaultSetting(): AppState {
  return { siderCollapsed: false, theme: 'dark', language: 'zh-CN', focusTextarea: true }
}

export function getLocalSetting(): AppState {
  const localSetting: AppState | undefined = ss.get(LOCAL_NAME)
  return { ...defaultSetting(), ...localSetting }
}

export function setLocalSetting(setting: AppState): void {
  ss.set(LOCAL_NAME, setting)
}
