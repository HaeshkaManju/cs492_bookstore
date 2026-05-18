"use client"

/**
 * Authentication Context
 * ======================
 * 
 * Task: FE-S2-001, FE-S2-002
 * 
 * Provides authentication state and methods throughout the app.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { api, User, clearTokens, getAccessToken } from "./api-client"

interface AuthContextType {
  user: User | null
  isLoading: boolean
  isAuthenticated: boolean
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string; role?: string }>
  register: (data: {
    email: string
    password: string
    first_name: string
    last_name: string
  }) => Promise<{ success: boolean; error?: string; role?: string }>
  logout: () => Promise<void>
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  const isAuthenticated = !!user

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = getAccessToken()
      if (token) {
        try {
          const response = await api.getCurrentUser()
          if (response.success && response.data) {
            setUser(response.data)
          } else {
            clearTokens()
          }
        } catch {
          clearTokens()
        }
      }
      setIsLoading(false)
    }
    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    try {
      const response = await api.login(email, password)
      if (response.success && response.data) {
        setUser(response.data.user)
        return { success: true, role: response.data.user.role }
      }
      return {
        success: false,
        error: response.error?.message || "Login failed"
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Login failed"
      }
    }
  }

  const register = async (data: {
    email: string
    password: string
    first_name: string
    last_name: string
  }) => {
    try {
      const response = await api.register(data)
      if (response.success && response.data) {
        setUser(response.data.user)
        return { success: true, role: response.data.user.role }
      }
      return {
        success: false,
        error: response.error?.message || "Registration failed"
      }
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : "Registration failed"
      }
    }
  }

  const logout = async () => {
    await api.logout()
    setUser(null)
  }

  const refreshUser = async () => {
    try {
      const response = await api.getCurrentUser()
      if (response.success && response.data) {
        setUser(response.data)
      }
    } catch {
      // Ignore errors
    }
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated,
        login,
        register,
        logout,
        refreshUser
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}

// HOC for protected routes
export function withAuth<P extends object>(
  Component: React.ComponentType<P>,
  options?: { requiredRole?: 'admin' | 'employee' | 'customer' }
) {
  return function AuthenticatedComponent(props: P) {
    const { user, isLoading, isAuthenticated } = useAuth()

    if (isLoading) {
      return (
        <div className="flex min-h-screen items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-primary"></div>
        </div>
      )
    }

    if (!isAuthenticated) {
      if (typeof window !== 'undefined') {
        window.location.href = '/login'
      }
      return null
    }

    if (options?.requiredRole && user?.role !== options.requiredRole) {
      if (options.requiredRole === 'admin' && user?.role !== 'admin') {
        if (typeof window !== 'undefined') {
          window.location.href = '/'
        }
        return null
      }
    }

    return <Component {...props} />
  }
}
