import { createContext } from 'react'

import type { ThreadSummary } from '@/lib/chat'

export type ThreadsContextValue = {
  threads: ThreadSummary[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
  removeThread: (threadId: string) => Promise<void>
  renameLocal: (threadId: string, title: string) => void
}

export const ThreadsContext = createContext<ThreadsContextValue | null>(null)
