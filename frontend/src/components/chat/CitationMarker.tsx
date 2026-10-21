import type { CitationPayload } from '@/lib/citations'

export function CitationMarker({
  index,
  citation,
  onOpen,
}: {
  index: number
  citation?: CitationPayload
  onOpen: (citation: CitationPayload) => void
}) {
  if (!citation) {
    // Marker with no matching citation payload — render inert.
    return (
      <sup className="text-muted-foreground ml-0.5 text-[11px]">[{index}]</sup>
    )
  }

  return (
    <button
      type="button"
      onClick={() => onOpen(citation)}
      className="text-muted-foreground hover:bg-accent hover:text-accent-foreground ml-0.5 inline-flex h-4 min-w-4 translate-y-[-2px] items-center justify-center rounded-[4px] border px-[3px] align-super text-[10px] font-medium transition-colors"
      aria-label={`Open source ${citation.ticker} ${citation.form}`}
    >
      {index}
    </button>
  )
}
