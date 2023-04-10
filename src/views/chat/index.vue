<script setup lang='ts'>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { NButton, NInput, useDialog, useMessage } from 'naive-ui'
import Recorder from 'recorder-core/recorder.mp3.min'
import html2canvas from 'html2canvas'
import { Message } from './components'
import { useScroll } from './hooks/useScroll'
import { useChat } from './hooks/useChat'
import { useCopyCode } from './hooks/useCopyCode'
import { useUsingContext } from './hooks/useUsingContext'
import { useUsingKnowledge } from './hooks/useUsingKnowledge'
import { HoverButton, SvgIcon } from '@/components/common'
import { useBasicLayout } from '@/hooks/useBasicLayout'
import { useAppStore, useChatStore, useUserStore } from '@/store'
import { fetchAudioChatAPIProcess, fetchChatAPIProcess } from '@/api'
import { t } from '@/locales'

let controller = new AbortController()

const route = useRoute()
const dialog = useDialog()
const ms = useMessage()

const chatStore = useChatStore()
const userStore = useUserStore()
const appStore = useAppStore()

const userInfo = computed(() => userStore.userInfo)
const focusTextarea = computed(() => appStore.focusTextarea)

useCopyCode()
const { isMobile } = useBasicLayout()
const { addChat, updateChat, updateChatSome, getChatByUuidAndIndex } = useChat()
const { scrollRef, scrollToBottom } = useScroll()
const { usingContext, toggleUsingContext } = useUsingContext()
const { usingKnowledge, toggleUsingKnowledge } = useUsingKnowledge()

const { uuid } = route.params as { uuid: string }

const dataSources = computed(() => chatStore.getChatByUuid(+uuid))
const conversationList = computed(() => dataSources.value.filter(item => (!item.inversion && !item.error)))

const prompt = ref<string>('')
const isAudioPrompt = ref<boolean>(false)
const loading = ref<boolean>(false)
const recProtectionPeriod = ref<boolean>(false)
const sendingRecord = ref<boolean>(false)
const recording = ref<boolean>(false)
const audioMode = ref<boolean>(false)
const actionVisible = ref<boolean>(true)

// 未知原因刷新页面，loading 状态不会重置，手动重置
dataSources.value.forEach((item, index) => {
  if (item.loading)
    updateChatSome(+uuid, index, { loading: false })
})

function isServerError(responseText: string) {
  if (responseText.startsWith('ChatGptWebServerError:'))
    return true

  return false
}
function getServerErrorType(responseText: string) {
  if (responseText.startsWith('ChatGptWebServerError:'))
    return responseText.split(':')[1]

  return ''
}

function handleSubmit() {
  onConversation()
}

let rec = new Recorder()
const recOpen = function (success: Function) {
  rec = Recorder({
    type: 'mp3',
    sampleRate: 16000,
    bitRate: 16,
    onProcess() {
    },
  })

  rec.open(() => {
    success && success()
    // },function(msg:string,isUserNotAllow:boolean){
  }, () => {
    dialog.warning({
      title: t('chat.openMicrophoneFailedTitle'),
      content: t('chat.openMicrophoneFailedText'),
    })
  })
}

function _recStart() { // 打开了录音后才能进行start、stop调用
  rec.start()
  recording.value = true
  isAudioPrompt.value = true

  // temporarily disable rec button
  recProtectionPeriod.value = true
  setTimeout(() => {
    recProtectionPeriod.value = false
  }, 2000)

  addChat(
    +uuid,
    {
      dateTime: new Date().toLocaleString(),
      text: t('chat.recordingInProgress'),
      loading: true,
      inversion: true,
      error: false,
      conversationOptions: null,
      requestOptions: { prompt: '', options: null },
    },
    t('chat.newChat'),
  )
  scrollToBottom()
}

async function recStart() {
  if (recording.value || loading.value)
    return

  recOpen(() => {
    _recStart()
  })
}

async function recStop() {
  if (!rec) {
    recording.value = false
    return
  }

  sendingRecord.value = true

  // rec.stop(async function(blob:Blob,duration:any){
  rec.stop(async (blob: Blob) => {
    rec.close()
    rec = null

    recording.value = false
    if (!blob)
      return

    controller = new AbortController()

    let options: Chat.ConversationRequest = {}
    const lastContext = conversationList.value[conversationList.value.length - 1]?.conversationOptions

    if (lastContext && usingContext.value)
      options = { ...lastContext }

    const formData = new FormData()
    formData.append('audio', blob, 'recording.mp3')

    try {
      await fetchAudioChatAPIProcess<Chat.ConversationResponse>({
        formData,
        options,
        onDownloadProgress: ({ event }) => {
          const xhr = event.target
          let { responseText } = xhr
          responseText = removeDataPrefix(responseText)
          prompt.value = responseText
          isAudioPrompt.value = true

          // 如果解析音频消息出错，就显示something wrong
          const isError = isServerError(responseText)
          if (isError) {
            updateChat(
              +uuid,
              dataSources.value.length - 1,
              {
                dateTime: new Date().toLocaleString(),
                text: t(`server.${getServerErrorType(responseText)}`),
                inversion: false,
                error: true,
                loading: false,
                requestOptions: { prompt: '', ...options },
              },
            )
            scrollToBottom()

            loading.value = false
            sendingRecord.value = false

            return
          }

          onConversation()
        },
      })
    }
    catch (error: any) {
      const errorMessage = error?.message ?? t('common.wrong')

      if (error.message === 'canceled') {
        updateChatSome(
          +uuid,
          dataSources.value.length - 1,
          {
            loading: false,
          },
        )
        scrollToBottom()
        return
      }

      const currentChat = getChatByUuidAndIndex(+uuid, dataSources.value.length - 1)

      if (currentChat?.text && currentChat.text !== '') {
        updateChatSome(
          +uuid,
          dataSources.value.length - 1,
          {
            text: `${currentChat.text}\n[${errorMessage}]`,
            error: false,
            loading: false,
          },
        )
        return
      }

      updateChat(
        +uuid,
        dataSources.value.length - 1,
        {
          dateTime: new Date().toLocaleString(),
          text: errorMessage,
          inversion: false,
          error: true,
          loading: false,
          conversationOptions: null,
          requestOptions: { prompt: '', options: { ...options } },
        },
      )
      scrollToBottom()
    }
    finally {
      recording.value = false
    }
    // },function(msg:string){
  }, () => {
    // console.log("rec error:"+msg);
    rec.close()
    rec = null
  })
}

function removeDataPrefix(str: string) {
  if (str && str.startsWith('data: '))
    return str.slice(6)

  return str
}

async function onConversation() {
  const message = prompt.value

  if (loading.value)
    return

  if (!message || message.trim() === '')
    return

  controller = new AbortController()

  if (isAudioPrompt.value) {
    updateChat(
      +uuid,
      dataSources.value.length - 1,
      {
        dateTime: new Date().toLocaleString(),
        text: message ?? '',
        inversion: true,
        error: false,
        loading: false,
        conversationOptions: null,
        requestOptions: { prompt: message, options: null },
      },
    )
  }
  else {
    addChat(
      +uuid,
      {
        dateTime: new Date().toLocaleString(),
        text: message,
        inversion: true,
        error: false,
        conversationOptions: null,
        requestOptions: { prompt: message, options: null },
      },
      t('chat.newChat'),
    )
  }
  scrollToBottom()

  isAudioPrompt.value = false

  loading.value = true
  prompt.value = ''

  let options: Chat.ConversationRequest = {}
  const lastContext = conversationList.value[conversationList.value.length - 1]?.conversationOptions

  if (lastContext && usingContext.value)
    options = { ...lastContext }

  addChat(
    +uuid,
    {
      dateTime: new Date().toLocaleString(),
      text: '',
      loading: true,
      inversion: false,
      error: false,
      conversationOptions: null,
      requestOptions: { prompt: message, options: { ...options } },
    },
    t('chat.newChat'),
  )
  scrollToBottom()

  try {
    await fetchChatAPIProcess<Chat.ConversationResponse>({
      prompt: message,
      memory: userInfo.value.chatgpt_memory,
      top_p: userInfo.value.chatgpt_top_p,
      max_length: userInfo.value.chatgpt_max_length,
      temperature: userInfo.value.chatgpt_temperature,
      is_knowledge: usingKnowledge.value,
      options,
      signal: controller.signal,
      onDownloadProgress: ({ event }) => {
        const xhr = event.target
        let { responseText } = xhr
        responseText = removeDataPrefix(responseText)

        const isError = isServerError(responseText)
        if (isError) {
          updateChat(
            +uuid,
            dataSources.value.length - 1,
            {
              dateTime: new Date().toLocaleString(),
              text: t(`server.${getServerErrorType(responseText)}`),
              inversion: false,
              error: true,
              loading: false,
              requestOptions: { prompt: message, ...options },
            },
          )
          scrollToBottom()
          return
        }

        // SSE response format "data: xxx"
        const lastIndex = responseText.lastIndexOf('data: ')
        let chunk = responseText
        if (lastIndex !== -1)
          chunk = responseText.substring(lastIndex)

        chunk = removeDataPrefix(chunk)
        try {
          const data = JSON.parse(chunk)
          updateChat(
            +uuid,
            dataSources.value.length - 1,
            {
              dateTime: new Date().toLocaleString(),
              text: data.text ?? '',
              inversion: false,
              error: false,
              loading: false,
              conversationOptions: { conversationId: data.conversationId, parentMessageId: data.id },
              requestOptions: { prompt: message, options: { ...options } },
            },
          )
          scrollToBottom()
        }
        catch (error) {
          //
        }
      },
    })
  }
  catch (error: any) {
    const errorMessage = error?.message ?? t('common.wrong')

    if (error.message === 'canceled') {
      updateChatSome(
        +uuid,
        dataSources.value.length - 1,
        {
          loading: false,
        },
      )
      scrollToBottom()
      return
    }

    const currentChat = getChatByUuidAndIndex(+uuid, dataSources.value.length - 1)

    if (currentChat?.text && currentChat.text !== '') {
      updateChatSome(
        +uuid,
        dataSources.value.length - 1,
        {
          text: `${currentChat.text}\n[${errorMessage}]`,
          error: false,
          loading: false,
        },
      )
      return
    }

    updateChat(
      +uuid,
      dataSources.value.length - 1,
      {
        dateTime: new Date().toLocaleString(),
        text: errorMessage,
        inversion: false,
        error: true,
        loading: false,
        conversationOptions: null,
        requestOptions: { prompt: message, options: { ...options } },
      },
    )
    scrollToBottom()
  }
  finally {
    loading.value = false
    sendingRecord.value = false
  }
}

async function onRegenerate(index: number) {
  if (loading.value)
    return

  controller = new AbortController()

  const { requestOptions } = dataSources.value[index]

  const message = requestOptions?.prompt ?? ''

  let options: Chat.ConversationRequest = {}

  if (requestOptions.options)
    options = { ...requestOptions.options }

  loading.value = true

  updateChat(
    +uuid,
    index,
    {
      dateTime: new Date().toLocaleString(),
      text: '',
      inversion: false,
      error: false,
      loading: true,
      conversationOptions: null,
      requestOptions: { prompt: message, ...options },
    },
  )

  try {
    await fetchChatAPIProcess<Chat.ConversationResponse>({
      prompt: message,
      memory: userInfo.value.chatgpt_memory,
      top_p: userInfo.value.chatgpt_top_p,
      max_length: userInfo.value.chatgpt_max_length,
      temperature: userInfo.value.chatgpt_temperature,
      is_knowledge: usingKnowledge.value,
      options,
      signal: controller.signal,
      onDownloadProgress: ({ event }) => {
        const xhr = event.target
        let { responseText } = xhr
        responseText = removeDataPrefix(responseText)

        const isError = isServerError(responseText)
        if (isError) {
          updateChat(
            +uuid,
            dataSources.value.length - 1,
            {
              dateTime: new Date().toLocaleString(),
              text: t(`server.${getServerErrorType(responseText)}`),
              inversion: false,
              error: true,
              loading: false,
              requestOptions: { prompt: message, ...options },
            },
          )
          scrollToBottom()
          return
        }

        // SSE response format "data: xxx"
        const lastIndex = responseText.lastIndexOf('data: ')
        let chunk = responseText
        if (lastIndex !== -1)
          chunk = responseText.substring(lastIndex)

        chunk = removeDataPrefix(chunk)
        try {
          const data = JSON.parse(chunk)
          updateChat(
            +uuid,
            index,
            {
              dateTime: new Date().toLocaleString(),
              text: data.text ?? '',
              inversion: false,
              error: false,
              loading: false,
              conversationOptions: { conversationId: data.conversationId, parentMessageId: data.id },
              requestOptions: { prompt: message, ...options },
            },
          )
        }
        catch (error) {
          //
        }
      },
    })
  }
  catch (error: any) {
    if (error.message === 'canceled') {
      updateChatSome(
        +uuid,
        index,
        {
          loading: false,
        },
      )
      return
    }

    const errorMessage = error?.message ?? t('common.wrong')

    updateChat(
      +uuid,
      index,
      {
        dateTime: new Date().toLocaleString(),
        text: errorMessage,
        inversion: false,
        error: true,
        loading: false,
        conversationOptions: null,
        requestOptions: { prompt: message, ...options },
      },
    )
  }
  finally {
    loading.value = false
  }
}

watch(
  focusTextarea,
  () => {
    setTimeout(() => {
      const textarea = document.documentElement.querySelector('.n-input__textarea-el') as HTMLInputElement
      if (textarea)
        textarea.focus()
    }, 0)
  },
)

function handleExport() {
  if (loading.value)
    return

  const d = dialog.warning({
    title: t('chat.exportImage'),
    content: t('chat.exportImageConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: async () => {
      try {
        d.loading = true
        const ele = document.getElementById('image-wrapper')
        const canvas = await html2canvas(ele as HTMLDivElement, {
          useCORS: true,
        })
        const imgUrl = canvas.toDataURL('image/png')
        const tempLink = document.createElement('a')
        tempLink.style.display = 'none'
        tempLink.href = imgUrl
        tempLink.setAttribute('download', 'chat-shot.png')
        if (typeof tempLink.download === 'undefined')
          tempLink.setAttribute('target', '_blank')

        document.body.appendChild(tempLink)
        tempLink.click()
        document.body.removeChild(tempLink)
        window.URL.revokeObjectURL(imgUrl)
        d.loading = false
        ms.success(t('chat.exportSuccess'))
        Promise.resolve()
      }
      catch (error: any) {
        ms.error(t('chat.exportFailed'))
      }
      finally {
        d.loading = false
      }
    },
  })
}

function handleDelete(index: number) {
  if (loading.value)
    return

  dialog.warning({
    title: t('chat.deleteMessage'),
    content: t('chat.deleteMessageConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: () => {
      chatStore.deleteChatByUuid(+uuid, index)
    },
  })
}

function handleClear() {
  if (loading.value)
    return

  dialog.warning({
    title: t('chat.clearChat'),
    content: t('chat.clearChatConfirm'),
    positiveText: t('common.yes'),
    negativeText: t('common.no'),
    onPositiveClick: () => {
      chatStore.clearChatByUuid(+uuid, t('chat.newChat'))
    },
  })
}

function handleEnter(event: KeyboardEvent) {
  if (!isMobile.value) {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      handleSubmit()
    }
  }
  else {
    if (event.key === 'Enter' && event.ctrlKey) {
      event.preventDefault()
      handleSubmit()
    }
  }
}

function handleStop() {
  if (loading.value) {
    controller.abort()
    loading.value = false
  }
}

function handleRec() {
  if (recording.value === true)
    recStop()
  else
    recStart()
}

function onInputFocus() {
  if (isMobile.value)
    actionVisible.value = false
}
function onInputBlur() {
  if (isMobile.value)
    actionVisible.value = true
}

const placeholder = computed(() => {
  if (isMobile.value)
    return t('chat.placeholderMobile')
  return t('chat.placeholder')
})

const buttonDisabled = computed(() => {
  return loading.value || !prompt.value || prompt.value.trim() === ''
})

const recButtonDisabled = computed(() => {
  return recProtectionPeriod.value || sendingRecord.value
})

const wrapClass = computed(() => {
  if (isMobile.value)
    return ['pt-14']
  return []
})

const footerClass = computed(() => {
  let classes = ['p-4']
  if (isMobile.value)
    classes = ['sticky', 'left-0', 'bottom-0', 'right-0', 'p-2', 'overflow-hidden']
  return classes
})

onMounted(() => {
  scrollToBottom()
})

onUnmounted(() => {
  if (loading.value)
    controller.abort()
})
</script>

<template>
  <div class="flex flex-col w-full h-full" :class="wrapClass">
    <main class="flex-1 overflow-hidden">
      <div
        id="scrollRef"
        ref="scrollRef"
        class="h-full overflow-hidden overflow-y-auto"
      >
        <div
          id="image-wrapper"
          class="w-full max-w-screen-xl m-auto dark:bg-[#101014]"
          :class="[isMobile ? 'p-2' : 'p-4']"
        >
          <template v-if="!dataSources.length">
            <div class="flex items-center justify-center mt-4 text-center text-neutral-300">
              <SvgIcon icon="ri:bubble-chart-fill" class="mr-2 text-3xl" />
              <span>ChatGLM Web</span>
            </div>
          </template>
          <template v-else>
            <div>
              <Message
                v-for="(item, index) of dataSources"
                :key="index"
                :date-time="item.dateTime"
                :text="item.text"
                :inversion="item.inversion"
                :error="item.error"
                :loading="item.loading"
                @regenerate="onRegenerate(index)"
                @delete="handleDelete(index)"
              />
              <div class="sticky bottom-0 left-0 flex justify-center">
                <NButton v-if="loading" type="warning" @click="handleStop">
                  <template #icon>
                    <SvgIcon icon="ri:stop-circle-line" />
                  </template>
                  {{ $t('chat.stopResponding') }}
                </NButton>
              </div>
            </div>
          </template>
        </div>
      </div>
    </main>
    <footer :class="footerClass">
      <div class="w-full max-w-screen-xl m-auto">
        <div class="flex items-center justify-between space-x-2">
          <div v-if="actionVisible" class="flex items-center space-x-2">
            <HoverButton @click="handleClear">
              <span class="text-xl text-[#4f555e] dark:text-white">
                <SvgIcon icon="ri:delete-bin-line" />
              </span>
            </HoverButton>
            <HoverButton v-if="!isMobile" @click="handleExport">
              <span class="text-xl text-[#4f555e] dark:text-white">
                <SvgIcon icon="ri:download-2-line" />
              </span>
            </HoverButton>
            <HoverButton v-if="!isMobile" @click="toggleUsingContext">
              <span class="text-xl" :class="{ 'text-[#4b9e5f]': usingContext, 'text-[#a8071a]': !usingContext }">
                <SvgIcon icon="ri:chat-history-line" />
              </span>
            </HoverButton>
            <HoverButton v-if="!isMobile" @click="toggleUsingKnowledge">
              <span class="text-xl" :class="{ 'text-[#4b9e5f]': usingKnowledge, 'text-[#a8071a]': !usingKnowledge }">
                <SvgIcon icon="carbon:ibm-watson-knowledge-catalog" />
              </span>
            </HoverButton>
            <!-- <HoverButton
              v-if="!audioMode"
              @click="audioMode = !audioMode"
            >
              <span class="text-xl text-[#4f555e] dark:text-white">
                <SvgIcon icon="ph:microphone-bold" />
              </span>
            </HoverButton>
            <HoverButton
              v-else
              @click="audioMode = !audioMode"
            >
              <span class="text-xl text-[#4f555e] dark:text-white">
                <SvgIcon icon="material-symbols:keyboard" />
              </span>
            </HoverButton> -->
          </div>
          <NInput
            v-if="!audioMode"
            v-model:value="prompt"
            autofocus
            type="textarea"
            :autosize="{ minRows: 1.4, maxRows: 10 }"
            :placeholder="placeholder"
            @keypress="handleEnter"
            @focus="onInputFocus"
            @blur="onInputBlur"
          />
          <!-- <NButton
            v-if="audioMode"
            :disabled="recButtonDisabled"
            style="flex-grow: 2;"
            type="default"
            @click="handleRec"
          >
            <span v-if="recording">{{ $t('chat.clickToSend') }}</span>
            <span v-if="!recording">{{ $t('chat.clickToTalk') }}</span>
          </NButton> -->
          <NButton
            type="primary"
            :disabled="buttonDisabled" @click="handleSubmit"
          >
            <template #icon>
              <span class="dark:text-black">
                <SvgIcon icon="ri:send-plane-fill" />
              </span>
            </template>
          </NButton>
        </div>
      </div>
    </footer>
  </div>
</template>
