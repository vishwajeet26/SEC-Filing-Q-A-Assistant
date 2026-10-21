import { FileText } from 'lucide-react'

import type { CitationPayload } from '@/lib/citations'
import { citationSubtitle } from '@/lib/citations'
import { cn } from '@/lib/utils'

export function CitationChip({
  citation,
  onOpen,
}: {
  citation: CitationPayload
  onOpen: (citation: CitationPayload) => void
}) {
  const subtitle = citationSubtitle(citation)

  return (
    <button
      type="button"
      onClick={() => onOpen(citation)}
      className={cn(
        'group flex max-w-full items-start gap-2.5 rounded-lg border bg-card px-3 py-2 text-left transition-colors hover:bg-accent',
      )}
    >
      <span className="bg-secondary text-secondary-foreground mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-md text-[11px] font-semibold">
        {citation.citationIndex}
      </span>
      <span className="min-w-0">
        <span className="flex items-center gap-1.5 text-[13px] font-medium">
          <FileText className="size-3.5 shrink-0" />
          <span className="truncate">
            {citation.ticker} · {citation.form} · {citation.filingDate}
          </span>
        </span>
        {subtitle ? (
          <span className="text-muted-foreground mt-0.5 block truncate text-xs">
            {subtitle}
          </span>
        ) : null}
      </span>
    </button>
  )
}
