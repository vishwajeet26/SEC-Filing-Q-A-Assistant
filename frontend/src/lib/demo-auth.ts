import { env } from '@/lib/env'

/**
 * Minimal local auth client that mirrors the `supabase.auth` surface the app
 * consumes. Sessions come from the backend's demo endpoints as locally-signed
 * JWTs. Only active when Supabase env vars are unset.
 */

export type DemoUser = { id: string; email: string }

export type DemoSession = {
  access_token: string
  user: DemoUser
}

const STORAGE_KEY = 'document-copilot-demo-session'

type AuthChangeEvent =
  | 'INITIAL_SESSION'
  | 'SIGNED_IN'
  | 'SIGNED_OUT'

type Listener = (event: AuthChangeEvent, session: DemoSession | null) => void

function loadSession(): DemoSession | null {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as DemoSession) : null
  } catch {
    return null
  }
}

async function post(path: string, body: Record<string, string>) {
  const response = await fetch(`${env.apiBaseUrl}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!response.ok) {
    const detail = await response.json().catch(() => null)
    throw new Error(
      (detail && typeof detail.detail === 'string' && detail.detail) ||
        `Authentication failed (${response.status})`,
    )
  }
  return (await response.json()) as { accessToken: string; user: DemoUser }
}

export function createDemoAuth() {
  const listeners = new Set<Listener>()
  let session = loadSession()

  function notify(event: AuthChangeEvent) {
    for (const listener of listeners) {
      listener(event, session)
    }
  }

  return {
    async getSession() {
      session = loadSession()
      return { data: { session } }
    },

    async signInWithPassword(credentials: { email: string; password: string }) {
      const result = await post('/auth/demo/signin', credentials)
      session = { access_token: result.accessToken, user: result.user }
      window.localStorage.setItem(STORAGE_KEY, JSON.stringify(session))
      notify('SIGNED_IN')
      return { data: { session }, error: null }
    },

    async signUp(credentials: { email: string; password: string }) {
      return this.signInWithPassword(credentials)
    },

    async signOut() {
      session = null
      window.localStorage.removeItem(STORAGE_KEY)
      notify('SIGNED_OUT')
      return { error: null }
    },

    onAuthStateChange(callback: Listener) {
      listeners.add(callback)
      callback('INITIAL_SESSION', loadSession())
      return {
        data: {
          subscription: {
            unsubscribe() {
              listeners.delete(callback)
            },
          },
        },
      }
    },
  }
}
