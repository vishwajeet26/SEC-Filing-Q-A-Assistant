import { Fragment, type ReactNode } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'

import { CitationMarker } from '@/components/chat/CitationMarker'
import type { CitationPayload } from '@/lib/citations'
import { citationByIndex } from '@/lib/citations'

const MARKER = /(\[\d+\])/g

export function AssistantMarkdown({
  text,
  citations,
  onOpenCitation,
}: {
  text: string
  citations: CitationPayload[]
  onOpenCitation: (citation: CitationPayload) => void
}) {
  const segments = text.split(MARKER)

  const nodes: ReactNode[] = segments.map((segment, position) => {
    const marker = /^\[(\d+)\]$/.exec(segment)
    if (marker) {
      const index = Number(marker[1])
      return (
        <CitationMarker
          key={`${position}-${segment}`}
          index={index}
          citation={citationByIndex(citations, index)}
          onOpen={onOpenCitation}
        />
      )
    }
    if (!segment) return null
    return (
      <ReactMarkdown key={position} remarkPlugins={[remarkGfm]}>
        {segment}
      </ReactMarkdown>
    )
  })

  return <div className="text-[15px] leading-relaxed [&_p]:whitespace-pre-wrap [&_blockquote]:border-l-2 [&_blockquote]:pl-3 [&_blockquote]:text-foreground [&_strong]:font-semibold [&_em]:italic [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:list-decimal [&_ol]:pl-5">{nodes}</div>
}

export function AssistantMarkdownFragment({ text }: { text: string }) {
  const segments = text.split(MARKER)
  return (
    <Fragment>
      {segments.map((segment, position) => {
        const marker = /^\[(\d+)\]$/.exec(segment)
        if (marker) {
          return (
            <sup key={position} className="text-muted-foreground ml-0.5 text-[11px]">
              [{marker[1]}]
            </sup>
          )
        }
        if (!segment) return null
        return (
          <ReactMarkdown key={position} remarkPlugins={[remarkGfm]}>
            {segment}
          </ReactMarkdown>
        )
      })}
    </Fragment>
  )
}
