import { ArrowUp } from 'lucide-react'
import { useEffect, useRef, useState } from 'react'

import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { cn } from '@/lib/utils'

export function ChatInput({
  onSubmit,
  disabled,
  placeholder = 'Ask about the filings…',
  autoFocus = true,
  className,
}: {
  onSubmit: (value: string) => void
  disabled?: boolean
  placeholder?: string
  autoFocus?: boolean
  className?: string
}) {
  const [value, setValue] = useState('')
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (autoFocus) {
      textareaRef.current?.focus()
    }
  }, [autoFocus])

  function submit() {
    const trimmed = value.trim()
    if (!trimmed || disabled) return
    onSubmit(trimmed)
    setValue('')
  }

  return (
    <div className={cn('mx-auto w-full max-w-3xl px-4 pb-4', className)}>
      <form
        className="bg-card focus-within:border-foreground/30 relative flex items-end gap-2 rounded-2xl border p-2 pl-4 shadow-sm transition-colors"
        onSubmit={(event) => {
          event.preventDefault()
          submit()
        }}
      >
        <Textarea
          ref={textareaRef}
          value={value}
          onChange={(event) => setValue(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter' && !event.shiftKey) {
              event.preventDefault()
              submit()
            }
          }}
          placeholder={placeholder}
          rows={1}
          className="max-h-48 min-h-9 resize-none border-0 p-0 py-1.5 shadow-none focus-visible:ring-0 dark:bg-transparent text-[15px]"
          disabled={disabled}
        />
        <Button
          type="submit"
          size="icon"
          className="shrink-0 rounded-xl"
          disabled={disabled || value.trim().length === 0}
          aria-label="Send message"
        >
          <ArrowUp />
        </Button>
      </form>
      <p className="text-muted-foreground mt-2 text-center text-[11px]">
        Answers are grounded in the SEC filing corpus. Verify citations before relying on them.
      </p>
    </div>
  )
}
