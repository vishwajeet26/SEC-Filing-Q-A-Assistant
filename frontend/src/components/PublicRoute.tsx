import type { ReactNode } from 'react'
import { Navigate } from 'react-router-dom'

import { Loader } from '@/components/ui/loader'
import { useSession } from '@/hooks/useSession'

export function PublicRoute({ children }: { children: ReactNode }) {
  const session = useSession()

  if (session === undefined) {
    return (
      <div className="bg-background flex min-h-svh items-center justify-center">
        <Loader className="text-muted-foreground size-6" />
      </div>
    )
  }

  if (session !== null) {
    return <Navigate to="/chats" replace />
  }

  return <>{children}</>
}
