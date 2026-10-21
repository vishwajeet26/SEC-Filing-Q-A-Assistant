import { createClient } from '@supabase/supabase-js'

import { createDemoAuth } from '@/lib/demo-auth'
import { env, isDemoAuth } from '@/lib/env'

type SessionLike = {
  access_token: string
  user: { id: string; email: string }
}

export type AuthClient = {
  getSession(): Promise<{ data: { session: SessionLike | null } }>
  signInWithPassword(credentials: {
    email: string
    password: string
  }): Promise<{ data: { session: SessionLike | null }; error: { message: string } | null }>
  signUp(credentials: {
    email: string
    password: string
  }): Promise<{ data: { session: SessionLike | null }; error: { message: string } | null }>
  signOut(): Promise<{ error: { message: string } | null }>
  onAuthStateChange(
    callback: (event: string, session: SessionLike | null) => void,
  ): { data: { subscription: { unsubscribe(): void } } }
}

function buildAuthClient(): AuthClient {
  if (isDemoAuth) {
    return createDemoAuth() as unknown as AuthClient
  }
  const client = createClient(env.supabaseUrl, env.supabaseAnonKey)
  return client.auth as unknown as AuthClient
}

export const supabase = { auth: buildAuthClient() }
