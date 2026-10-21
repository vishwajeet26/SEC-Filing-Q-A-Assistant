import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'

import { AuthLayout } from '@/components/AuthLayout'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { isDemoAuth } from '@/lib/env'
import { supabase } from '@/lib/supabase'

export function Login() {
  const navigate = useNavigate()
  const location = useLocation()
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState(false)

  const from = (location.state as { from?: string } | null)?.from ?? '/chats'

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault()
    if (pending) return
    setPending(true)
    setError(null)
    const { error } = await supabase.auth.signInWithPassword({ email, password })
    if (error) {
      setError(error.message)
      setPending(false)
      return
    }
    navigate(from, { replace: true })
  }

  return (
    <AuthLayout
      title="Sign in"
      subtitle="Use your Driftwood Capital email address."
      footer={
        <span>
          Need an account?{' '}
          <Link to="/signup" className="text-foreground underline underline-offset-4">
            Sign up
          </Link>
        </span>
      }
    >
      <form className="flex flex-col gap-4" onSubmit={handleSubmit}>
        <div className="flex flex-col gap-2">
          <Label htmlFor="email">Email</Label>
          <Input
            id="email"
            type="email"
            autoComplete="email"
            placeholder="analyst@driftwoodcapital.com"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
          />
        </div>
        <div className="flex flex-col gap-2">
          <Label htmlFor="password">Password</Label>
          <Input
            id="password"
            type="password"
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            minLength={6}
          />
        </div>

        {error ? (
          <p className="text-destructive text-sm" role="alert">
            {error}
          </p>
        ) : null}

        {isDemoAuth ? (
          <p className="text-muted-foreground rounded-md border border-dashed px-3 py-2 text-xs">
            Demo mode — no Supabase configured. Any email works; password must be
            6+ characters. Try <span className="font-mono">analyst@driftwoodcapital.com</span>.
          </p>
        ) : null}

        <Button type="submit" disabled={pending} className="mt-2">
          {pending ? 'Signing in…' : 'Sign in'}
        </Button>
      </form>
    </AuthLayout>
  )
}
