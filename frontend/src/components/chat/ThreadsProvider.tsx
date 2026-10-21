import { useCallback, useEffect, useState, type ReactNode } from 'react'

import { deleteThread, listThreads } from '@/lib/chat'
import { describeChatError } from '@/lib/chat-errors'
import { ThreadsContext, type ThreadsContextValue } from '@/contexts/threads-context'

export function ThreadsProvider({ children }: { children: ReactNode }) {
  const [threads, setThreads] = useState<ThreadsContextValue['threads']>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const refresh = useCallback(async () => {
    try {
      setError(null)
      const next = await listThreads()
      setThreads(next)
    } catch (cause) {
      setError(describeChatError(cause))
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void refresh()
  }, [refresh])

  const removeThread = useCallback(
    async (threadId: string) => {
      await deleteThread(threadId)
      setThreads((current) => current.filter((thread) => thread.id !== threadId))
    },
    [],
  )

  const renameLocal = useCallback((threadId: string, title: string) => {
    setThreads((current) =>
      current.map((thread) => (thread.id === threadId ? { ...thread, title } : thread)),
    )
  }, [])

  const value: ThreadsContextValue = {
    threads,
    loading,
    error,
    refresh,
    removeThread,
    renameLocal,
  }

  return <ThreadsContext.Provider value={value}>{children}</ThreadsContext.Provider>
}
