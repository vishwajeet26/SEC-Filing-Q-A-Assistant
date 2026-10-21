import { cn } from '@/lib/utils'

export function Logo({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      aria-hidden="true"
      className={cn('size-7 shrink-0', className)}
    >
      <rect width="32" height="32" rx="8" className="fill-foreground" />
      <path
        d="M9 8h8.5a6.5 6.5 0 0 1 0 13H14v4.5a1.5 1.5 0 0 1-3 0V9.5A1.5 1.5 0 0 1 9 8Zm5 3v7h3.5a3.5 3.5 0 0 0 0-7H14Z"
        className="fill-background"
      />
      <circle cx="23.5" cy="22.5" r="2.5" className="fill-background" />
    </svg>
  )
}

export function LogoWordmark({ className }: { className?: string }) {
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <Logo />
      <div className="leading-tight">
        <div className="text-sm font-semibold">Document Copilot</div>
        <div className="text-muted-foreground text-xs">Driftwood Capital research</div>
      </div>
    </div>
  )
}
