import { ExternalLink, Loader2, X } from 'lucide-react'
import { useEffect, useState } from 'react'

import { Badge } from '@/components/ui/badge'
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from '@/components/ui/sheet'
import { Button } from '@/components/ui/button'
import { type CitationContext, getCitationContext } from '@/lib/chat'
import { describeChatError } from '@/lib/chat-errors'
import { type CitationPayload, citationHeader } from '@/lib/citations'
import { cn } from '@/lib/utils'

export function SourcePassageSheet({
  citation,
  onOpenChange,
}: {
  citation: CitationPayload | null
  onOpenChange: (open: boolean) => void
}) {
  const [context, setContext] = useState<CitationContext | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!citation) {
      setContext(null)
      setError(null)
      return
    }
    let cancelled = false
    setLoading(true)
    setError(null)
    setContext(null)
    getCitationContext(citation.chunkId)
      .then((result) => {
        if (!cancelled) setContext(result)
      })
      .catch((cause) => {
        if (!cancelled) setError(describeChatError(cause))
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })
    return () => {
      cancelled = true
    }
  }, [citation])

  return (
    <Sheet open={citation !== null} onOpenChange={onOpenChange}>
      <SheetContent className="w-full sm:max-w-lg">
        {citation ? (
          <>
            <SheetHeader className="relative">
              <SheetClose asChild>
                <Button
                  variant="ghost"
                  size="icon-sm"
                  aria-label="Close source passage"
                  className="absolute top-4 right-4"
                >
                  <X />
                </Button>
              </SheetClose>
              <SheetTitle className="text-base pr-8">
                {citationHeader(citation)}
              </SheetTitle>
              <SheetDescription>
                {citation.section ? `Section: ${citation.section}` : 'Source passage'}
                {citation.page ? ` · Page ${citation.page}` : ''}
              </SheetDescription>
              {context?.sourceUrl ? (
                <a
                  href={context.sourceUrl}
                  target="_blank"
                  rel="noreferrer"
                  className="text-muted-foreground hover:text-foreground inline-flex items-center gap-1 text-xs underline underline-offset-4"
                >
                  Open filing on SEC EDGAR
                  <ExternalLink className="size-3" />
                </a>
              ) : null}
            </SheetHeader>

            <div className="scrollbar-thin flex-1 space-y-4 overflow-y-auto px-6 pb-8">
              {loading ? (
                <div className="text-muted-foreground flex items-center gap-2 text-sm">
                  <Loader2 className="size-4 animate-spin" />
                  Loading source context…
                </div>
              ) : null}

              {error ? (
                <div className="text-destructive rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm">
                  {error}
                </div>
              ) : null}

              {context?.table ? (
                <div className="rounded-lg border">
                  <div className="border-b px-3 py-2 text-xs font-medium">
                    {context.table.title ?? `Table ${context.table.tableIndex + 1}`}
                    {context.table.units ? (
                      <span className="text-muted-foreground"> ({context.table.units})</span>
                    ) : null}
                  </div>
                  <pre className="text-muted-foreground overflow-x-auto px-3 py-2 font-mono text-[11px] leading-relaxed">
                    {context.table.markdown}
                  </pre>
                </div>
              ) : null}

              {context?.chunks.map((chunk) => (
                <div
                  key={chunk.chunkId}
                  className={cn(
                    'rounded-lg border px-3 py-2.5 text-[13px] leading-relaxed',
                    chunk.role === 'anchor'
                      ? 'border-foreground/25 bg-secondary/50'
                      : 'bg-card text-muted-foreground',
                  )}
                >
                  <div className="mb-1.5 flex items-center gap-2">
                    <Badge
                      variant={chunk.role === 'anchor' ? 'default' : 'secondary'}
                      className="text-[10px]"
                    >
                      {chunk.role === 'anchor'
                        ? 'Cited passage'
                        : chunk.role === 'previous'
                          ? 'Before'
                          : 'After'}
                    </Badge>
                    <span className="text-muted-foreground font-mono text-[10px]">
                      chunk {chunk.chunkIndex}
                    </span>
                  </div>
                  <p className="whitespace-pre-wrap">{chunk.text}</p>
                </div>
              ))}
            </div>
          </>
        ) : null}
      </SheetContent>
    </Sheet>
  )
}
