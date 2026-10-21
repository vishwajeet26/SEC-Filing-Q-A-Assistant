import type { ReactNode } from 'react'
import { Navigate, useLocation } from 'react-router-dom'

import { Loader } from '@/components/ui/loader'
import { useSession } from '@/hooks/useSession'

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const session = useSession()
  const location = useLocation()

  if (session === undefined) {
    return (
      <div className="bg-background flex min-h-svh items-center justify-center">
        <Loader className="text-muted-foreground size-6" />
      </div>
    )
  }

  if (session === null) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />
  }

  return <>{children}</>
}
