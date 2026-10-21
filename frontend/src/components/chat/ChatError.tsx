import { AlertTriangle, RotateCcw } from 'lucide-react'

import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Button } from '@/components/ui/button'

export function ChatError({ message, onRetry }: { message: string; onRetry?: () => void }) {
  return (
    <Alert variant="destructive" className="mx-auto w-full max-w-3xl">
      <AlertTriangle />
      <AlertTitle>The answer failed</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      {onRetry ? (
        <Button variant="outline" size="sm" className="mt-2" onClick={onRetry}>
          <RotateCcw />
          Retry
        </Button>
      ) : null}
    </Alert>
  )
}
