import { Plus, MessageSquare, Trash2 } from 'lucide-react'
import { useState } from 'react'
import { useNavigate, useParams } from 'react-router-dom'

import { UserMenu } from '@/components/chat/UserMenu'
import { LogoWordmark } from '@/components/Logo'
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { useThreads } from '@/hooks/useThreads'
import { useSession } from '@/hooks/useSession'
import { isDemoAuth } from '@/lib/env'
import { formatRelativeTime } from '@/lib/format'
import { toast } from 'sonner'
import { cn } from '@/lib/utils'

export function ThreadSidebar() {
  const navigate = useNavigate()
  const { threadId } = useParams()
  const { threads, loading, removeThread } = useThreads()
  const session = useSession()
  const [pendingDelete, setPendingDelete] = useState<string | null>(null)

  function handleNewChat() {
    // The empty page creates the thread when a question is submitted.
    navigate('/chats')
  }

  async function handleDelete() {
    if (!pendingDelete) return
    const target = pendingDelete
    setPendingDelete(null)
    try {
      await removeThread(target)
      if (threadId === target) {
        navigate('/chats')
      }
    } catch {
      toast.error('Could not delete the chat')
    }
  }

  return (
    <aside className="bg-sidebar text-sidebar-foreground hidden w-72 shrink-0 flex-col border-r md:flex">
      <div className="flex h-14 items-center justify-between border-b px-4">
        <LogoWordmark />
      </div>

      <div className="p-3">
        <Button className="w-full justify-start gap-2" onClick={handleNewChat}>
          <Plus />
          New chat
        </Button>
      </div>

      <nav className="scrollbar-thin flex-1 space-y-0.5 overflow-y-auto px-3 pb-3">
        {loading ? (
          <div className="text-muted-foreground px-2 py-6 text-center text-xs">
            Loading chats…
          </div>
        ) : threads.length === 0 ? (
          <div className="text-muted-foreground px-2 py-6 text-center text-xs">
            No conversations yet.
            <br />
            Start a new chat to ask a question.
          </div>
        ) : (
          threads.map((thread) => {
            const active = thread.id === threadId
            return (
              <div
                key={thread.id}
                className={cn(
                  'group flex items-center gap-2 rounded-md px-2 py-2 text-sm transition-colors',
                  active
                    ? 'bg-sidebar-accent text-sidebar-accent-foreground'
                    : 'hover:bg-sidebar-accent/60',
                )}
              >
                <button
                  type="button"
                  className="flex min-w-0 flex-1 items-center gap-2 text-left"
                  onClick={() => navigate(`/chats/${thread.id}`)}
                >
                  <MessageSquare className="text-muted-foreground size-4 shrink-0" />
                  <span className="min-w-0 flex-1">
                    <span className="block truncate">{thread.title}</span>
                    <span className="text-muted-foreground block text-[11px]">
                      {formatRelativeTime(thread.updatedAt)}
                    </span>
                  </span>
                </button>
                <button
                  type="button"
                  aria-label="Delete chat"
                  className="text-muted-foreground hover:text-destructive hidden shrink-0 rounded p-1 group-hover:block"
                  onClick={() => setPendingDelete(thread.id)}
                >
                  <Trash2 className="size-3.5" />
                </button>
              </div>
            )
          })
        )}
      </nav>

      <div className="border-t p-3">
        {isDemoAuth ? (
          <Badge variant="secondary" className="mb-2 justify-center w-full font-normal">
            Demo mode · no API keys configured
          </Badge>
        ) : null}
        <UserMenu email={session?.user?.email ?? ''} />
      </div>

      <AlertDialog open={pendingDelete !== null} onOpenChange={(open) => !open && setPendingDelete(null)}>
        <AlertDialogContent>
          <AlertDialogHeader>
            <AlertDialogTitle>Delete this chat?</AlertDialogTitle>
            <AlertDialogDescription>
              The conversation and its messages will be removed. This cannot be undone.
            </AlertDialogDescription>
          </AlertDialogHeader>
          <AlertDialogFooter>
            <AlertDialogCancel>Cancel</AlertDialogCancel>
            <AlertDialogAction variant="destructive" onClick={handleDelete}>
              Delete
            </AlertDialogAction>
          </AlertDialogFooter>
        </AlertDialogContent>
      </AlertDialog>
    </aside>
  )
}
