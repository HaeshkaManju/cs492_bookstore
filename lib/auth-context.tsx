"use client"

import { createContext, useContext, useState, useEffect, ReactNode } from "react"

export type UserRole = "admin" | "employee" | "customer"

export interface User {
  id: string
  email: string
  first_name: string
  last_name: string
  role: UserRole
  is_active: boolean
}

export interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
}

interface LoginCredentials {
  email: string
  password: string
}

interface RegisterData {
  email: string
  password: string
  first_name: string
  last_name: string
}

interface AuthContextType extends AuthState {
  login: (credentials: LoginCredentials) => Promise<{ success: boolean; error?: string }>
  register: (data: RegisterData) => Promise<{ success: boolean; error?: string }>
  logout: () => void
  refreshToken: () => Promise<boolean>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

/**
 * =============================================================================
 * BACKEND TEAM CONFIGURATION
 * =============================================================================
 * 
 * API Endpoints Used (must match your FastAPI implementation):
 *   - POST /auth/login      -> { email, password } -> { access_token, refresh_token }
 *   - POST /auth/register   -> { email, password, first_name, last_name } -> { access_token, refresh_token }
 *   - GET  /auth/me         -> Authorization: Bearer <token> -> User object
 *   - POST /auth/refresh    -> { refresh_token } -> { access_token }
 * 
 * Expected User Object Shape:
 *   { id, email, first_name, last_name, role: "admin"|"employee"|"customer", is_active }
 * 
 * To Connect to Real Backend:
 *   1. Set NEXT_PUBLIC_DEMO_MODE=false in environment
 *   2. Set NEXT_PUBLIC_API_URL to your API (e.g., https://api.yourdomain.com/api/v1)
 * 
 * PRODUCTION NOTE: For better security, consider switching from localStorage to
 * httpOnly cookies for token storage. This requires backend changes to set cookies
 * on login response and include credentials in fetch requests.
 * =============================================================================
 */

// API base URL - configure this based on your backend deployment
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1"

// Demo mode - set NEXT_PUBLIC_DEMO_MODE=false to use real backend
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE !== "false"

// Demo users for testing
const DEMO_USERS: Record<string, { password: string; user: User }> = {
  "admin@bookstore.com": {
    password: "admin123",
    user: {
      id: "demo-admin-001",
      email: "admin@bookstore.com",
      first_name: "Admin",
      last_name: "User",
      role: "admin",
      is_active: true,
    },
  },
  "employee@bookstore.com": {
    password: "employee123",
    user: {
      id: "demo-employee-001",
      email: "employee@bookstore.com",
      first_name: "Employee",
      last_name: "Staff",
      role: "employee",
      is_active: true,
    },
  },
  "customer@bookstore.com": {
    password: "customer123",
    user: {
      id: "demo-customer-001",
      email: "customer@bookstore.com",
      first_name: "John",
      last_name: "Customer",
      role: "customer",
      is_active: true,
    },
  },
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<AuthState>({
    user: null,
    token: null,
    isAuthenticated: false,
    isLoading: true,
  })

  // Check for existing token on mount
  useEffect(() => {
    const checkAuth = async () => {
      const storedToken = localStorage.getItem("access_token")
      const storedUser = localStorage.getItem("user_data")
      
      // Demo mode: restore user from localStorage
      if (DEMO_MODE && storedUser) {
        try {
          const user = JSON.parse(storedUser)
          setState({
            user,
            token: storedToken || "demo-token",
            isAuthenticated: true,
            isLoading: false,
          })
          return
        } catch {
          localStorage.removeItem("user_data")
        }
      }
      
      if (storedToken && !DEMO_MODE) {
        try {
          const response = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              Authorization: `Bearer ${storedToken}`,
            },
          })
          if (response.ok) {
            const data = await response.json()
            setState({
              user: data.data || data,
              token: storedToken,
              isAuthenticated: true,
              isLoading: false,
            })
            return
          }
        } catch {
          // Token invalid or expired
          localStorage.removeItem("access_token")
          localStorage.removeItem("refresh_token")
        }
      }
      setState(prev => ({ ...prev, isLoading: false }))
    }
    checkAuth()
  }, [])

  const login = async (credentials: LoginCredentials): Promise<{ success: boolean; error?: string }> => {
    // Demo mode login
    if (DEMO_MODE) {
      const demoUser = DEMO_USERS[credentials.email.toLowerCase()]
      if (demoUser && demoUser.password === credentials.password) {
        localStorage.setItem("access_token", "demo-token-" + demoUser.user.id)
        localStorage.setItem("user_data", JSON.stringify(demoUser.user))
        setState({
          user: demoUser.user,
          token: "demo-token-" + demoUser.user.id,
          isAuthenticated: true,
          isLoading: false,
        })
        return { success: true }
      }
      return {
        success: false,
        error: "Invalid email or password. Try: admin@bookstore.com / admin123",
      }
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(credentials),
      })

      const data = await response.json()

      if (!response.ok) {
        return {
          success: false,
          error: data.error?.message || data.detail || "Invalid credentials",
        }
      }

      // Store tokens
      localStorage.setItem("access_token", data.access_token)
      if (data.refresh_token) {
        localStorage.setItem("refresh_token", data.refresh_token)
      }

      // Fetch user data
      const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${data.access_token}`,
        },
      })

      if (userResponse.ok) {
        const userData = await userResponse.json()
        setState({
          user: userData.data || userData,
          token: data.access_token,
          isAuthenticated: true,
          isLoading: false,
        })
      }

      return { success: true }
    } catch (error) {
      console.error("Login error:", error)
      return {
        success: false,
        error: "Unable to connect to server. Please try again.",
      }
    }
  }

  const register = async (data: RegisterData): Promise<{ success: boolean; error?: string }> => {
    // Demo mode registration
    if (DEMO_MODE) {
      const newUser: User = {
        id: "demo-" + Date.now(),
        email: data.email,
        first_name: data.first_name,
        last_name: data.last_name,
        role: "customer",
        is_active: true,
      }
      localStorage.setItem("access_token", "demo-token-" + newUser.id)
      localStorage.setItem("user_data", JSON.stringify(newUser))
      setState({
        user: newUser,
        token: "demo-token-" + newUser.id,
        isAuthenticated: true,
        isLoading: false,
      })
      return { success: true }
    }
    
    try {
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })

      const responseData = await response.json()

      if (!response.ok) {
        return {
          success: false,
          error: responseData.error?.message || responseData.detail || "Registration failed",
        }
      }

      // Auto-login after registration
      if (responseData.access_token) {
        localStorage.setItem("access_token", responseData.access_token)
        if (responseData.refresh_token) {
          localStorage.setItem("refresh_token", responseData.refresh_token)
        }

        const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
          headers: {
            Authorization: `Bearer ${responseData.access_token}`,
          },
        })

        if (userResponse.ok) {
          const userData = await userResponse.json()
          setState({
            user: userData.data || userData,
            token: responseData.access_token,
            isAuthenticated: true,
            isLoading: false,
          })
        }
      }

      return { success: true }
    } catch (error) {
      console.error("Registration error:", error)
      return {
        success: false,
        error: "Unable to connect to server. Please try again.",
      }
    }
  }

  const logout = () => {
    localStorage.removeItem("access_token")
    localStorage.removeItem("refresh_token")
    localStorage.removeItem("user_data")
    setState({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
    })
  }

  const refreshToken = async (): Promise<boolean> => {
    const storedRefreshToken = localStorage.getItem("refresh_token")
    if (!storedRefreshToken) return false

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ refresh_token: storedRefreshToken }),
      })

      if (response.ok) {
        const data = await response.json()
        localStorage.setItem("access_token", data.access_token)
        setState(prev => ({ ...prev, token: data.access_token }))
        return true
      }
    } catch {
      // Refresh failed
    }

    logout()
    return false
  }

  return (
    <AuthContext.Provider
      value={{
        ...state,
        login,
        register,
        logout,
        refreshToken,
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
