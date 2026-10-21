import type { UIMessage } from 'ai'
import { useStickToBottom } from 'use-stick-to-bottom'

import { MessageBubble, type CitationPayloadLike } from '@/components/chat/MessageBubble'
import { cn } from '@/lib/utils'

export function MessageList({
  messages,
  streamingMessageId,
  onOpenCitation,
}: {
  messages: UIMessage[]
  streamingMessageId?: string
  onOpenCitation: (citation: CitationPayloadLike) => void
}) {
  const { scrollRef, contentRef } = useStickToBottom()

  return (
    <div ref={scrollRef} className="scrollbar-thin h-full overflow-y-auto">
      <div ref={contentRef} className="mx-auto flex w-full max-w-3xl flex-col gap-6 px-4 py-8">
        {messages.map((message) => (
          <MessageBubble
            key={message.id ?? Math.random()}
            message={message}
            isStreaming={message.id === streamingMessageId}
            onOpenCitation={onOpenCitation}
          />
        ))}
      </div>
    </div>
  )
}

export function messageListClassName() {
  return cn('min-h-0 flex-1')
}
