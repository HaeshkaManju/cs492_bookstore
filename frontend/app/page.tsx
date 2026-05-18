import Link from "next/link"
import { BookOpen, Settings, ShoppingCart, ArrowRight } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background p-4">
      <div className="w-full max-w-4xl space-y-8">
        {/* Header */}
        <div className="text-center">
          <div className="mx-auto flex h-16 w-16 items-center justify-center rounded-xl bg-primary/10">
            <BookOpen className="h-8 w-8 text-primary" />
          </div>
          <h1 className="mt-6 text-4xl font-bold tracking-tight text-foreground">
            Rare Books
          </h1>
          <p className="mt-2 text-lg text-muted-foreground">
            Antiquarian Collection & Management System
          </p>
        </div>

        {/* Portal Cards */}
        <div className="grid gap-6 md:grid-cols-2">
          {/* Admin Portal */}
          <Card className="group relative overflow-hidden border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
            <CardHeader>
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-secondary">
                <Settings className="h-6 w-6 text-muted-foreground transition-colors group-hover:text-primary" />
              </div>
              <CardTitle className="mt-4 text-foreground">Admin Dashboard</CardTitle>
              <CardDescription className="text-muted-foreground">
                Manage inventory, track sales, and handle purchase orders
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
              </ul>
              <Link href="/admin">
                <Button className="mt-6 w-full bg-secondary text-secondary-foreground hover:bg-secondary/80">
                  Enter Admin Portal
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>

          {/* Customer Portal */}
          <Card className="group relative overflow-hidden border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
            <CardHeader>
              <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-primary/10">
                <ShoppingCart className="h-6 w-6 text-primary" />
              </div>
              <CardTitle className="mt-4 text-foreground">Customer Portal</CardTitle>
              <CardDescription className="text-muted-foreground">
                Browse our collection and purchase rare books
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
              </ul>
              <Link href="/customer">
                <Button className="mt-6 w-full bg-primary text-primary-foreground hover:bg-primary/90">
                  Start Shopping
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </CardContent>
          </Card>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-muted-foreground">
          © 2024 Rare Books Antiquarian Collection. All rights reserved.
        </p>
      </div>
    </div>
  )
}
