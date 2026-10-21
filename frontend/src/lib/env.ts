function readEnv(name: keyof ImportMetaEnv): string {
  const value = import.meta.env[name]
  return typeof value === 'string' ? value.trim() : ''
}

export const env = {
  // Empty string means same-origin (dev proxy or co-hosted deployment).
  apiBaseUrl: readEnv('VITE_API_BASE_URL').replace(/\/$/, ''),
  supabaseUrl: readEnv('VITE_SUPABASE_URL'),
  supabaseAnonKey: readEnv('VITE_SUPABASE_ANON_KEY'),
} as const

export const isDemoAuth = env.supabaseUrl === '' || env.supabaseAnonKey === ''
