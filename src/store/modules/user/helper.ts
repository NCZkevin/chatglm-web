import { ss } from '@/utils/storage'

const LOCAL_NAME = 'userStorage'

export interface UserInfo {
  avatar: string
  name: string
  description: string
  chatgpt_top_p: number
  chatgpt_memory: number
  chatgpt_max_length: number
  chatgpt_temperature: number
}

export interface UserState {
  userInfo: UserInfo
}

export function defaultSetting(): UserState {
  return {
    userInfo: {
      avatar: 'https://api.multiavatar.com/0.8481955987976837.svg',
      name: 'ChatGLM Web',

      description: '',
      chatgpt_top_p: 100,
      chatgpt_memory: 50,
      chatgpt_max_length: 2048,
      chatgpt_temperature: 0.8,
    },
  }
}

export function getLocalState(): UserState {
  const localSetting: UserState | undefined = ss.get(LOCAL_NAME)
  return { ...defaultSetting(), ...localSetting }
}

export function setLocalState(setting: UserState): void {
  ss.set(LOCAL_NAME, setting)
}
