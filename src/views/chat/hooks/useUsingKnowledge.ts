import { computed } from 'vue'
import { useMessage } from 'naive-ui'
import { t } from '@/locales'
import { useChatStore } from '@/store'

export function useUsingKnowledge() {
  const ms = useMessage()
  const chatStore = useChatStore()
  const usingKnowledge = computed<boolean>(() => chatStore.usingKnowledge)

  function toggleUsingKnowledge() {
    chatStore.setUsingKnowledge(!usingKnowledge.value)
    if (usingKnowledge.value)
      ms.success(t('chat.turnOnKnowledge'))
    else
      ms.warning(t('chat.turnOffKnowledge'))
  }

  return {
    usingKnowledge,
    toggleUsingKnowledge,
  }
}
