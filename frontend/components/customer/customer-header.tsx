"use client"

import { BookOpen, ShoppingCart, LogIn, LogOut, User, Home } from "lucide-react"
import Link from "next/link"
import { useRouter } from "next/navigation"
import { useStore } from "@/lib/store-context"
import { useAuth } from "@/lib/auth-context"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function CustomerHeader() {
  const { cart } = useStore()
  const { user, isAuthenticated, logout } = useAuth()
  const router = useRouter()
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  const handleSignOut = async () => {
    await logout()
    router.push("/")
  }

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <BookOpen className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">Rare Books</h1>
            <p className="text-xs text-muted-foreground">Antiquarian Collection</p>
          </div>
        </Link>

        <nav className="flex items-center gap-3">
          <Link href="/">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              <Home className="mr-2 h-4 w-4" />
              Home
            </Button>
          </Link>

          {isAuthenticated && (user?.role === "admin" || user?.role === "employee") && (
            <Link href="/admin">
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                Admin
              </Button>
            </Link>
          )}

          <Link href="/customer/cart">
            <Button variant="outline" size="sm" className="relative border-border">
              <ShoppingCart className="mr-2 h-4 w-4" />
              Cart
              {cartCount > 0 && (
                <Badge className="absolute -right-2 -top-2 h-5 w-5 rounded-full bg-primary p-0 text-xs text-primary-foreground">
                  {cartCount}
                </Badge>
              )}
            </Button>
          </Link>

          {isAuthenticated && user ? (
            <div className="flex items-center gap-2">
              <div className="hidden sm:flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5">
                <User className="h-3 w-3 text-muted-foreground" />
                <span className="text-xs font-medium text-foreground">
                  {user.first_name}
                </span>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={handleSignOut}
                className="text-muted-foreground hover:text-foreground"
              >
                <LogOut className="mr-2 h-4 w-4" />
                Sign Out
              </Button>
            </div>
          ) : (
            <Link href="/login">
              <Button size="sm" className="bg-primary text-primary-foreground">
                <LogIn className="mr-2 h-4 w-4" />
                Sign In
              </Button>
            </Link>
          )}
        </nav>
      </div>
    </header>
  )
}
