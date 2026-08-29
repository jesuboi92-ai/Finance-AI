import create from 'zustand'
import { persist } from 'zustand/middleware'

interface User {
  id: string
  email: string
  username: string
  full_name: string
  role: string
  department?: string
  is_admin: boolean
}

interface AuthState {
  user: User | null
  access_token: string | null
  refresh_token: string | null
  setAuth: (user: User, access_token: string, refresh_token: string) => void
  logout: () => void
  isAuthenticated: () => boolean
}

export const useAuthStore = create<AuthState>(
  persist(
    (set, get) => ({
      user: null,
      access_token: null,
      refresh_token: null,
      setAuth: (user, access_token, refresh_token) =>
        set({ user, access_token, refresh_token }),
      logout: () => set({ user: null, access_token: null, refresh_token: null }),
      isAuthenticated: () => !!get().access_token,
    }),
    {
      name: 'auth-store',
    }
  )
)
