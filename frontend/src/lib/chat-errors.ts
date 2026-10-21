import { ApiError } from '@/lib/http'

export function describeChatError(error: unknown): string {
  if (error instanceof ApiError) {
    if (error.status === 401) {
      return 'Your session expired. Sign in again to continue.'
    }
    if (error.status === 403) {
      return 'You do not have access to this conversation.'
    }
    if (error.status === 404) {
      return 'This conversation no longer exists.'
    }
    if (error.isNetworkError) {
      return 'Could not reach the server. Check your connection and try again.'
    }
    return error.message
  }

  if (error instanceof Error && error.message) {
    return error.message
  }

  return 'Something went wrong while generating the answer.'
}
