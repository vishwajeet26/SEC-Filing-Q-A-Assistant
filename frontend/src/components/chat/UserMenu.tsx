import { ChevronsUpDown, LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Avatar, AvatarFallback } from '@/components/ui/avatar'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import { supabase } from '@/lib/supabase'

function initials(email: string): string {
  const handle = email.split('@')[0] ?? ''
  return handle.slice(0, 2).toUpperCase() || 'DC'
}

export function UserMenu({ email }: { email: string }) {
  const navigate = useNavigate()

  async function handleSignOut() {
    await supabase.auth.signOut()
    navigate('/login', { replace: true })
  }

  return (
    <DropdownMenu>
      <DropdownMenuTrigger className="hover:bg-sidebar-accent/60 flex w-full items-center gap-2 rounded-md px-2 py-2 text-left text-sm transition-colors outline-none">
        <Avatar className="size-7">
          <AvatarFallback>{initials(email)}</AvatarFallback>
        </Avatar>
        <span className="min-w-0 flex-1 truncate">{email || 'Signed in'}</span>
        <ChevronsUpDown className="text-muted-foreground size-3.5 shrink-0" />
      </DropdownMenuTrigger>
      <DropdownMenuContent align="start" className="w-56">
        <DropdownMenuLabel className="text-muted-foreground font-normal">
          {email}
        </DropdownMenuLabel>
        <DropdownMenuSeparator />
        <DropdownMenuItem variant="destructive" onClick={handleSignOut}>
          <LogOut />
          Sign out
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}
