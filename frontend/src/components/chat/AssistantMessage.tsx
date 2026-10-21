import type { UIMessage } from 'ai'

import { AssistantMarkdown } from '@/components/chat/AssistantMarkdown'
import { CitationChip } from '@/components/chat/CitationChip'
import { citationsFromMessage, textFromMessage, type CitationPayload } from '@/lib/citations'

export function AssistantMessage({
  message,
  isStreaming,
  onOpenCitation,
}: {
  message: UIMessage
  isStreaming: boolean
  onOpenCitation: (citation: CitationPayload) => void
}) {
  const text = textFromMessage(message)
  const citations = citationsFromMessage(message)

  return (
    <div className="space-y-3">
      <AssistantMarkdown text={text} citations={citations} onOpenCitation={onOpenCitation} />

      {citations.length > 0 ? (
        <div className="flex flex-wrap gap-2 pt-1">
          {citations.map((citation) => (
            <CitationChip
              key={`${citation.citationIndex}-${citation.chunkId}`}
              citation={citation}
              onOpen={onOpenCitation}
            />
          ))}
        </div>
      ) : null}

      {isStreaming ? (
        <span className="text-muted-foreground inline-block h-4 w-2 animate-pulse rounded-[2px] bg-current align-middle" />
      ) : null}
    </div>
  )
}
