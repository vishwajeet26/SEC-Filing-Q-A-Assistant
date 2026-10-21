import { Loader2 } from 'lucide-react'

import { cn } from '@/lib/utils'

function Loader({ className }: { className?: string }) {
  return <Loader2 data-slot="loader" className={cn('size-4 animate-spin', className)} />
}

export { Loader }
