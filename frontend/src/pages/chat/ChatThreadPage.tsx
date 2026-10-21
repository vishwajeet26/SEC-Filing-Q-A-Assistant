import { useChat } from '@ai-sdk/react'
import type { UIMessage } from 'ai'
import { useEffect, useRef, useState } from 'react'
import { useLocation, useNavigate, useParams } from 'react-router-dom'

import { ChatError } from '@/components/chat/ChatError'
import { ChatInput } from '@/components/chat/ChatInput'
import { MessageList } from '@/components/chat/MessageList'
import { PipelineStatus } from '@/components/chat/PipelineStatus'
import { SourcePassageSheet } from '@/components/chat/SourcePassageSheet'
import { Loader } from '@/components/ui/loader'
import { useChatTransport } from '@/hooks/useChatTransport'
import { useThreads } from '@/hooks/useThreads'
import { getThreadMessages } from '@/lib/chat'
import { describeChatError } from '@/lib/chat-errors'
import { type CitationPayload, type PipelineStatus as PipelineStatusState } from '@/lib/citations'
import { ApiError } from '@/lib/http'

function ChatThreadView({ threadId, initialMessages }: { threadId: string; initialMessages: UIMessage[] }) {
  const navigate = useNavigate()
  const location = useLocation()
  const { refresh } = useThreads()
  const [pipelineStatus, setPipelineStatus] = useState<PipelineStatusState | null>(null)
  const [selectedCitation, setSelectedCitation] = useState<CitationPayload | null>(null)
  const transport = useChatTransport(threadId, setPipelineStatus)

  const { messages, sendMessage, status, error } = useChat({
    id: threadId,
    messages: initialMessages,
    transport,
    onFinish: () => {
      setPipelineStatus(null)
      void refresh()
    },
  })

  function send(text: string) {
    setPipelineStatus(null)
    setSelectedCitation(null)
    void sendMessage({ text })
  }

  // Auto-send a starter prompt forwarded from the empty page, once.
  const initialPrompt = (location.state as { initialPrompt?: string } | null)?.initialPrompt
  const sentInitial = useRef(false)
  useEffect(() => {
    if (!initialPrompt || sentInitial.current) return
    sentInitial.current = true
    navigate(location.pathname, { replace: true, state: null })
    send(initialPrompt)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [initialPrompt])

  const isBusy = status === 'submitted' || status === 'streaming'
  const lastAssistantId = [...messages].reverse().find((message) => message.role === 'assistant')?.id

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="flex min-h-0 flex-1 flex-col">
        <MessageList
          messages={messages}
          streamingMessageId={isBusy ? lastAssistantId : undefined}
          onOpenCitation={setSelectedCitation}
        />
        {isBusy && pipelineStatus ? (
          <PipelineStatus status={pipelineStatus} className="mx-auto w-full max-w-3xl px-4 pb-2" />
        ) : null}
      </div>

      {error ? (
        <div className="mx-auto w-full max-w-3xl px-4 pb-2">
          <ChatError message={describeChatError(error)} />
        </div>
      ) : null}

      <ChatInput onSubmit={send} disabled={isBusy} />

      <SourcePassageSheet
        citation={selectedCitation}
        onOpenChange={(open) => {
          if (!open) setSelectedCitation(null)
        }}
      />
    </div>
  )
}

function ChatThreadLoader({ threadId }: { threadId: string }) {
  const navigate = useNavigate()
  const [initialMessages, setInitialMessages] = useState<UIMessage[] | null>(null)
  const [loadError, setLoadError] = useState<string | null>(null)
  const [reloadKey, setReloadKey] = useState(0)

  useEffect(() => {
    let mounted = true

    async function load() {
      setLoadError(null)

      try {
        const messages = await getThreadMessages(threadId)
        if (mounted) {
          setInitialMessages(messages)
        }
      } catch (cause) {
        if (!mounted) {
          return
        }

        if (cause instanceof ApiError && cause.status === 404) {
          navigate('/chats', { replace: true })
          return
        }

        if (cause instanceof ApiError && cause.status === 401) {
          navigate('/login', { replace: true })
          return
        }

        setLoadError(describeChatError(cause))
      }
    }

    void load()

    return () => {
      mounted = false
    }
  }, [threadId, navigate, reloadKey])

  if (loadError) {
    return (
      <div className="flex flex-1 items-center justify-center p-6">
        <div className="max-w-md space-y-3 text-center">
          <p className="text-destructive text-sm font-medium" role="alert">
            Could not load this conversation
          </p>
          <p className="text-muted-foreground text-sm">{loadError}</p>
          <button
            type="button"
            className="text-sm font-medium underline underline-offset-4"
            onClick={() => setReloadKey((value) => value + 1)}
          >
            Try again
          </button>
        </div>
      </div>
    )
  }

  if (initialMessages === null) {
    return (
      <div className="text-muted-foreground flex flex-1 items-center justify-center gap-2 p-6 text-sm">
        <Loader />
        Loading conversation…
      </div>
    )
  }

  return <ChatThreadView threadId={threadId} initialMessages={initialMessages} />
}

export function ChatThreadPage() {
  const { threadId } = useParams()

  if (!threadId) {
    return null
  }

  return <ChatThreadLoader key={threadId} threadId={threadId} />
}
