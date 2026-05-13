"use client"

import { BookOpen, ShoppingCart, Settings } from "lucide-react"
import Link from "next/link"
import { useStore } from "@/lib/store-context"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"

export function CustomerHeader() {
  const { cart } = useStore()
  const cartCount = cart.reduce((sum, item) => sum + item.quantity, 0)

  return (
    <header className="sticky top-0 z-50 border-b border-border bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        <Link href="/customer" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
            <BookOpen className="h-5 w-5 text-primary" />
          </div>
          <div>
            <h1 className="text-lg font-semibold text-foreground">Rare Books</h1>
            <p className="text-xs text-muted-foreground">Antiquarian Collection</p>
          </div>
        </Link>

        <nav className="flex items-center gap-4">
          <Link href="/admin">
            <Button variant="ghost" size="sm" className="text-muted-foreground hover:text-foreground">
              <Settings className="mr-2 h-4 w-4" />
              Admin
            </Button>
          </Link>
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
        </nav>
      </div>
    </header>
  )
}
