import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient, setTokenCookies, clearTokenCookies } from '@/lib/api/client'

interface User {
  id: string
  email: string
  full_name: string
  role: string
}

interface AuthState {
  user: User | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null

  login: (email: string, password: string) => Promise<void>
  logout: () => Promise<void>
  fetchMe: () => Promise<void>
  clearError: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: async (email, password) => {
        set({ isLoading: true, error: null })
        try {
          const { data } = await apiClient.post('/auth/login/', { email, password })
          setTokenCookies(data.access, data.refresh)
          set({ isAuthenticated: true, isLoading: false })
          await get().fetchMe()
        } catch (err: unknown) {
          const message =
            (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
            'Login failed. Check your credentials.'
          set({ error: message, isLoading: false, isAuthenticated: false })
          throw err
        }
      },

      logout: async () => {
        try {
          const refreshMatch =
            typeof document !== 'undefined'
              ? document.cookie.match(/(?:^|;\s*)refresh_token=([^;]*)/)
              : null
          const refreshToken = refreshMatch ? decodeURIComponent(refreshMatch[1]) : null
          if (refreshToken) {
            await apiClient.post('/auth/logout/', { refresh: refreshToken })
          }
        } catch {
          // Ignore logout API errors
        } finally {
          clearTokenCookies()
          set({ user: null, isAuthenticated: false })
        }
      },

      fetchMe: async () => {
        try {
          const { data } = await apiClient.get('/auth/me/')
          set({ user: data, isAuthenticated: true })
        } catch {
          set({ user: null, isAuthenticated: false })
        }
      },

      clearError: () => set({ error: null }),
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
)
