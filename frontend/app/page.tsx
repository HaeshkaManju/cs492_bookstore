"use client"

import Link from "next/link"
import { useRouter } from "next/navigation"
import { useAuth } from "@/lib/auth-context"
import { useStore } from "@/lib/store-context"
import {
  BookOpen,
  LogIn,
  LogOut,
  ShoppingCart,
  User,
  ShieldCheck,
  ArrowRight,
  Search,
  Star,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Badge } from "@/components/ui/badge"

export default function HomePage() {
  const { user, isAuthenticated, logout, isLoading } = useAuth()
  const { books } = useStore()
  const router = useRouter()

  const handleSignOut = async () => {
    await logout()
    router.push("/")
  }

  // Featured books - show a few from the catalog
  const featuredBooks = books.slice(0, 4)

  return (
    <div className="flex min-h-screen flex-col bg-background">
      {/* Navigation Bar */}
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
            <Link href="/customer">
              <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                <Search className="mr-2 h-4 w-4" />
                Browse Catalog
              </Button>
            </Link>

            {isAuthenticated && user ? (
              <>
                {user.role === "admin" || user.role === "employee" ? (
                  <Link href="/admin">
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                      <ShieldCheck className="mr-2 h-4 w-4" />
                      Admin Dashboard
                    </Button>
                  </Link>
                ) : (
                  <Link href="/customer/cart">
                    <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
                      <ShoppingCart className="mr-2 h-4 w-4" />
                      My Cart
                    </Button>
                  </Link>
                )}

                <div className="flex items-center gap-2 rounded-lg border border-border bg-card px-3 py-1.5">
                  <User className="h-4 w-4 text-muted-foreground" />
                  <div className="hidden sm:block">
                    <p className="text-xs font-medium text-foreground">
                      {user.first_name} {user.last_name}
                    </p>
                    <p className="text-[10px] text-muted-foreground capitalize">{user.role}</p>
                  </div>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={handleSignOut}
                  className="border-border text-muted-foreground hover:text-foreground"
                >
                  <LogOut className="mr-2 h-4 w-4" />
                  Sign Out
                </Button>
              </>
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

      {/* Hero Section */}
      <section className="relative overflow-hidden border-b border-border">
        <div className="absolute inset-0 bg-gradient-to-br from-primary/5 via-transparent to-primary/10" />
        <div className="container relative mx-auto px-4 py-20 md:py-28">
          <div className="mx-auto max-w-3xl text-center">
            <Badge variant="outline" className="mb-4 border-primary/30 text-primary">
              <Star className="mr-1 h-3 w-3" />
              Est. 2024 - Curated Rare Book Collection
            </Badge>
            <h1 className="text-4xl font-bold tracking-tight text-foreground md:text-5xl lg:text-6xl">
              Discover Rare &<br />
              Antiquarian Books
            </h1>
            <p className="mt-4 text-lg text-muted-foreground md:text-xl">
              First editions, signed copies, and museum-quality treasures
              from the world&apos;s finest literary collections.
            </p>
            <div className="mt-8 flex flex-col items-center gap-3 sm:flex-row sm:justify-center">
              <Link href="/customer">
                <Button size="lg" className="bg-primary text-primary-foreground w-full sm:w-auto">
                  Browse Collection
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
              {!isAuthenticated && (
                <Link href="/login">
                  <Button size="lg" variant="outline" className="border-border w-full sm:w-auto">
                    <LogIn className="mr-2 h-4 w-4" />
                    Sign In to Your Account
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </div>
      </section>

      {/* Featured Books */}
      {featuredBooks.length > 0 && (
        <section className="container mx-auto px-4 py-16">
          <div className="mb-8 flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-foreground">Featured Collection</h2>
              <p className="mt-1 text-sm text-muted-foreground">
                Hand-picked selections from our rare book vault
              </p>
            </div>
            <Link href="/customer">
              <Button variant="ghost" className="text-primary">
                View All
                <ArrowRight className="ml-1 h-4 w-4" />
              </Button>
            </Link>
          </div>
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {featuredBooks.map((book) => (
              <Card
                key={book.id}
                className="group border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg"
              >
                <CardHeader className="pb-2">
                  <div className="flex h-32 items-center justify-center rounded-lg bg-secondary/50">
                    <BookOpen className="h-12 w-12 text-primary/30" />
                  </div>
                </CardHeader>
                <CardContent>
                  <h3 className="font-semibold text-foreground line-clamp-1">{book.title}</h3>
                  <p className="mt-1 text-sm text-muted-foreground">{book.author}</p>
                  <div className="mt-3 flex items-center justify-between">
                    <p className="text-lg font-bold text-primary">
                      ${book.price.toLocaleString()}
                    </p>
                    <Badge variant="outline" className="text-xs">
                      {book.condition}
                    </Badge>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>
      )}

      {/* Portal Access Cards */}
      {!isAuthenticated && (
        <section className="border-t border-border bg-muted/30">
          <div className="container mx-auto px-4 py-16">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-2xl font-bold text-foreground">Access Your Portal</h2>
              <p className="mt-2 text-muted-foreground">
                Sign in to manage inventory, track orders, or shop for rare books
              </p>
            </div>
            <div className="mt-8 grid gap-6 md:grid-cols-2">
              {/* Staff Portal */}
              <Card className="group border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg">
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary">
                    <ShieldCheck className="h-6 w-6 text-muted-foreground transition-colors group-hover:text-primary" />
                  </div>
                  <CardTitle className="mt-4 text-foreground">Staff Portal</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    For administrators and employees
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Inventory management with advanced search
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Sales records and revenue tracking
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Purchase order management
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      User administration
                    </li>
                  </ul>
                  <Link href="/login">
                    <Button className="mt-6 w-full bg-secondary text-secondary-foreground hover:bg-secondary/80">
                      Sign In as Staff
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>

              {/* Customer Portal */}
              <Card className="group border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg">
                <CardHeader>
                  <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                    <ShoppingCart className="h-6 w-6 text-primary" />
                  </div>
                  <CardTitle className="mt-4 text-foreground">Customer Portal</CardTitle>
                  <CardDescription className="text-muted-foreground">
                    Browse and purchase rare books
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-2 text-sm text-muted-foreground">
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Browse curated rare book catalog
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Add items to shopping cart
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Secure checkout process
                    </li>
                    <li className="flex items-center gap-2">
                      <span className="h-1.5 w-1.5 rounded-full bg-primary" />
                      Order history and tracking
                    </li>
                  </ul>
                  <Link href="/register">
                    <Button className="mt-6 w-full bg-primary text-primary-foreground hover:bg-primary/90">
                      Create Account
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>
      )}

      {/* Signed-in user quick access */}
      {isAuthenticated && user && (
        <section className="border-t border-border bg-muted/30">
          <div className="container mx-auto px-4 py-16">
            <div className="mx-auto max-w-2xl text-center">
              <h2 className="text-2xl font-bold text-foreground">
                Welcome back, {user.first_name}!
              </h2>
              <p className="mt-2 text-muted-foreground">
                You&apos;re signed in as <Badge variant="outline" className="capitalize ml-1">{user.role}</Badge>
              </p>
            </div>
            <div className="mt-8 flex justify-center">
              {user.role === "admin" || user.role === "employee" ? (
                <Link href="/admin">
                  <Button size="lg" className="bg-primary text-primary-foreground">
                    <ShieldCheck className="mr-2 h-5 w-5" />
                    Go to Admin Dashboard
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              ) : (
                <Link href="/customer">
                  <Button size="lg" className="bg-primary text-primary-foreground">
                    <ShoppingCart className="mr-2 h-5 w-5" />
                    Continue Shopping
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
              )}
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="border-t border-border bg-muted/50">
        <div className="container mx-auto px-4 py-8">
          <div className="flex flex-col items-center justify-between gap-4 md:flex-row">
            <div className="flex items-center gap-3">
              <BookOpen className="h-5 w-5 text-primary" />
              <p className="text-sm text-muted-foreground">
                Rare Books Antiquarian Collection
              </p>
            </div>
            <div className="flex gap-6 text-sm text-muted-foreground">
              <Link href="/customer" className="hover:text-foreground">
                Catalog
              </Link>
              <Link href="/login" className="hover:text-foreground">
                Sign In
              </Link>
              <Link href="/register" className="hover:text-foreground">
                Register
              </Link>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
