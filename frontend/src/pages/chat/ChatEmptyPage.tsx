import { Sparkles } from 'lucide-react'
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { ChatInput } from '@/components/chat/ChatInput'
import { LogoWordmark } from '@/components/Logo'
import { Loader } from '@/components/ui/loader'
import { useThreads } from '@/hooks/useThreads'
import { createThread } from '@/lib/chat'
import { EXAMPLE_QUESTIONS } from '@/lib/suggestions'
import { toast } from 'sonner'

export function ChatEmptyPage() {
  const navigate = useNavigate()
  const { refresh } = useThreads()
  const [creating, setCreating] = useState(false)

  async function startChat(question: string) {
    if (creating) return
    setCreating(true)
    try {
      const thread = await createThread()
      await refresh()
      navigate(`/chats/${thread.id}`, { state: { initialPrompt: question } })
    } catch {
      toast.error('Could not start the chat')
      setCreating(false)
    }
  }

  return (
    <div className="flex h-full flex-col">
      <div className="flex flex-1 flex-col items-center justify-center gap-8 px-4">
        <div className="flex flex-col items-center gap-3 text-center">
          <LogoWordmark />
          <h1 className="text-2xl font-semibold tracking-tight">
            What do you want to know from the filings?
          </h1>
          <p className="text-muted-foreground max-w-md text-sm">
            Ask a question about any 10-K in the corpus. Answers quote the source
            passages and link every claim to a citation.
          </p>
        </div>

        <div className="grid w-full max-w-2xl gap-2 sm:grid-cols-2">
          {EXAMPLE_QUESTIONS.map((question) => (
            <button
              key={question}
              type="button"
              disabled={creating}
              onClick={() => startChat(question)}
              className="bg-card hover:bg-accent group flex min-h-20 items-start gap-3 rounded-xl border p-3.5 text-left text-[13px] leading-snug transition-colors"
            >
              <Sparkles className="text-muted-foreground group-hover:text-foreground mt-0.5 size-4 shrink-0" />
              <span>{question}</span>
            </button>
          ))}
        </div>

        {creating ? (
          <div className="text-muted-foreground flex items-center gap-2 text-xs">
            <Loader className="size-3" />
            Starting chat…
          </div>
        ) : null}
      </div>

      <ChatInput onSubmit={startChat} disabled={creating} />
    </div>
  )
}
