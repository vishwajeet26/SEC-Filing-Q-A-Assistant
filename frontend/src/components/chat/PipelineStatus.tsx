import { Loader } from '@/components/ui/loader'
import type { PipelineStatus as PipelineStatusValue } from '@/lib/citations'
import { cn } from '@/lib/utils'

export function PipelineStatus({
  status,
  className,
}: {
  status: PipelineStatusValue
  className?: string
}) {
  return (
    <div
      className={cn(
        'text-muted-foreground flex items-center gap-2 px-1 text-xs',
        className,
      )}
      role="status"
      aria-live="polite"
    >
      <Loader className="size-3" />
      <span className="animate-pulse">{status.message}</span>
    </div>
  )
}
