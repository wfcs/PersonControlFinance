import { create } from "zustand"
import { persist } from "zustand/middleware"
import { setAccessToken, setRefreshToken, clearTokens } from "@/lib/auth"

export interface UserProfile {
  id: string
  email: string
  full_name: string
  tenant_id: string
}

interface AuthState {
  user: UserProfile | null
  isAuthenticated: boolean
  setUser: (user: UserProfile) => void
  setTokens: (accessToken: string, refreshToken: string) => void
  logout: () => void
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,

      setUser: (user: UserProfile) =>
        set({ user, isAuthenticated: true }),

      setTokens: (accessToken: string, refreshToken: string) => {
        setAccessToken(accessToken)
        setRefreshToken(refreshToken)
      },

      logout: () => {
        clearTokens()
        set({ user: null, isAuthenticated: false })
      },
    }),
    {
      name: "fincontrol-auth",
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
)
