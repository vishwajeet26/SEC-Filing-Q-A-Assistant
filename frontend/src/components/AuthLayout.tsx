import type { ReactNode } from 'react'
import { Link } from 'react-router-dom'

import { Logo, LogoWordmark } from '@/components/Logo'
import { Badge } from '@/components/ui/badge'

export function AuthLayout({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string
  subtitle: string
  children: ReactNode
  footer?: ReactNode
}) {
  return (
    <div className="bg-background flex min-h-svh flex-col">
      <header className="border-b">
        <div className="mx-auto flex h-14 w-full max-w-6xl items-center px-4">
          <Link to="/login" className="flex items-center gap-2">
            <Logo />
            <span className="text-sm font-semibold">Document Copilot</span>
          </Link>
        </div>
      </header>

      <main className="mx-auto flex w-full max-w-6xl flex-1 flex-col items-center justify-center gap-8 px-4 py-10 lg:flex-row lg:gap-16">
        <section className="hidden max-w-md flex-col gap-6 lg:flex">
          <LogoWordmark className="scale-110 origin-left" />
          <h1 className="text-3xl font-semibold tracking-tight">
            Ask the filings. Get cited answers.
          </h1>
          <p className="text-muted-foreground">
            Document Copilot reads Driftwood's curated corpus of SEC 10-K filings
            so analysts can skip the intake work and go straight to insight.
            Every answer cites the exact source passage.
          </p>
          <ul className="text-muted-foreground space-y-2 text-sm">
            <li className="flex items-center gap-2">
              <span className="bg-foreground size-1.5 rounded-full" />
              Hybrid search across Apple, Microsoft, NVIDIA, Amazon and Alphabet
            </li>
            <li className="flex items-center gap-2">
              <span className="bg-foreground size-1.5 rounded-full" />
              Inline citations with source passages and surrounding context
            </li>
            <li className="flex items-center gap-2">
              <span className="bg-foreground size-1.5 rounded-full" />
              Fails clearly when the corpus cannot support an answer
            </li>
          </ul>
          <Badge variant="outline" className="w-fit text-muted-foreground">
            Internal tool · Driftwood Capital
          </Badge>
        </section>

        <section className="w-full max-w-sm">
          <div className="flex flex-col gap-6">
            <div className="flex flex-col gap-1 lg:hidden">
              <Logo className="size-8" />
            </div>
            <div className="flex flex-col gap-1">
              <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
              <p className="text-muted-foreground text-sm">{subtitle}</p>
            </div>
            {children}
          </div>
        </section>
      </main>

      {footer ? (
        <footer className="border-t">
          <div className="text-muted-foreground mx-auto flex h-12 w-full max-w-6xl items-center px-4 text-xs">
            {footer}
          </div>
        </footer>
      ) : null}
    </div>
  )
}
