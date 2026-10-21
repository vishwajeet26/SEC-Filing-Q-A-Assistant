import type { UIMessage } from 'ai'

import { AssistantMessage } from '@/components/chat/AssistantMessage'
import { Logo } from '@/components/Logo'
import { cn } from '@/lib/utils'

export function MessageBubble({
  message,
  isStreaming,
  onOpenCitation,
}: {
  message: UIMessage
  isStreaming: boolean
  onOpenCitation: (citation: CitationPayloadLike) => void
}) {
  if (message.role === 'user') {
    return (
      <div className="flex justify-end">
        <div className="bg-secondary text-secondary-foreground max-w-[85%] rounded-2xl rounded-br-md px-4 py-2.5 text-[15px] leading-relaxed whitespace-pre-wrap">
          {message.parts
            .filter((part) => part.type === 'text')
            .map((part, index) => (
              <span key={index}>{part.text}</span>
            ))}
        </div>
      </div>
    )
  }

  return (
    <div className="flex gap-3">
      <Logo className="mt-0.5 size-7" />
      <div className={cn('min-w-0 flex-1 pt-1')}>
        <AssistantMessage message={message} isStreaming={isStreaming} onOpenCitation={onOpenCitation} />
      </div>
    </div>
  )
}

export type CitationPayloadLike = {
  citationIndex: number
  chunkId: string
  excerpt: string
  ticker: string
  companyName?: string
  form: string
  filingDate: string
  page?: string
  section?: string
}
