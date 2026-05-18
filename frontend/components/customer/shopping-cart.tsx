"use client"

import { Minus, Plus, Trash2, ShoppingBag, ArrowLeft, CreditCard } from "lucide-react"
import Link from "next/link"
import { useStore } from "@/lib/store-context"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

export function ShoppingCart() {
  const { cart, cartTotal, removeFromCart, updateCartQuantity, clearCart } = useStore()

  const shipping = cartTotal > 5000 ? 0 : 25
  const tax = cartTotal * 0.08
  const total = cartTotal + shipping + tax

  if (cart.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 text-center">
        <div className="rounded-full bg-secondary p-6">
          <ShoppingBag className="h-12 w-12 text-muted-foreground" />
        </div>
        <h2 className="mt-6 text-xl font-semibold text-foreground">Your cart is empty</h2>
        <p className="mt-2 text-muted-foreground">
          Browse our collection and find your next rare book treasure
        </p>
        <Link href="/customer">
          <Button className="mt-6 bg-primary text-primary-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Continue Shopping
          </Button>
        </Link>
      </div>
    )
  }

  return (
    <div className="grid gap-8 lg:grid-cols-3">
      {/* Cart Items */}
      <div className="lg:col-span-2">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-semibold text-foreground">Shopping Cart</h1>
          <Button variant="ghost" size="sm" onClick={clearCart} className="text-muted-foreground hover:text-destructive">
            <Trash2 className="mr-2 h-4 w-4" />
            Clear Cart
          </Button>
        </div>

        <div className="space-y-4">
          {cart.map((item) => (
            <Card key={item.book.id} className="border-border bg-card">
              <CardContent className="p-4">
                <div className="flex gap-4">
                  <div className="flex h-24 w-20 items-center justify-center rounded-lg bg-secondary/50">
                    <ShoppingBag className="h-8 w-8 text-primary/30" />
                  </div>
                  <div className="flex flex-1 flex-col justify-between">
                    <div>
                      <h3 className="font-semibold text-foreground">{item.book.title}</h3>
                      <p className="text-sm text-muted-foreground">{item.book.author}</p>
                      <p className="mt-1 text-xs text-muted-foreground">
                        Condition: {item.book.condition} • {item.book.year}
                      </p>
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 border-border"
                          onClick={() => updateCartQuantity(item.book.id, item.quantity - 1)}
                        >
                          <Minus className="h-3 w-3" />
                        </Button>
                        <span className="w-8 text-center text-sm text-foreground">{item.quantity}</span>
                        <Button
                          variant="outline"
                          size="icon"
                          className="h-8 w-8 border-border"
                          onClick={() => updateCartQuantity(item.book.id, item.quantity + 1)}
                          disabled={item.quantity >= item.book.quantity}
                        >
                          <Plus className="h-3 w-3" />
                        </Button>
                      </div>
                      <div className="flex items-center gap-4">
                        <p className="font-semibold text-primary">
                          ${(item.book.price * item.quantity).toLocaleString()}
                        </p>
                        <Button
                          variant="ghost"
                          size="icon"
                          className="h-8 w-8 text-muted-foreground hover:text-destructive"
                          onClick={() => removeFromCart(item.book.id)}
                        >
                          <Trash2 className="h-4 w-4" />
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>

        <Link href="/customer">
          <Button variant="ghost" className="mt-4 text-muted-foreground">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Continue Shopping
          </Button>
        </Link>
      </div>

      {/* Checkout Summary */}
      <div className="lg:col-span-1">
        <Card className="sticky top-24 border-border bg-card">
          <CardHeader>
            <CardTitle className="text-lg">Order Summary</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Subtotal ({cart.length} items)</span>
                <span className="text-foreground">${cartTotal.toLocaleString()}</span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Shipping</span>
                <span className="text-foreground">
                  {shipping === 0 ? "Free" : `$${shipping.toFixed(2)}`}
                </span>
              </div>
              <div className="flex justify-between text-sm">
                <span className="text-muted-foreground">Estimated Tax</span>
                <span className="text-foreground">${tax.toFixed(2)}</span>
              </div>
            </div>

            <Separator className="bg-border" />

            <div className="flex justify-between">
              <span className="font-semibold text-foreground">Total</span>
              <span className="text-xl font-bold text-primary">${total.toLocaleString()}</span>
            </div>

            {cartTotal < 5000 && (
              <p className="text-xs text-muted-foreground">
                Add ${(5000 - cartTotal).toLocaleString()} more for free shipping
              </p>
            )}

            <Separator className="bg-border" />

            <div className="space-y-3">
              <div>
                <Label htmlFor="promo" className="text-sm text-muted-foreground">
                  Promo Code
                </Label>
                <div className="mt-1 flex gap-2">
                  <Input
                    id="promo"
                    placeholder="Enter code"
                    className="bg-input border-border"
                  />
                  <Button variant="outline" className="border-border">
                    Apply
                  </Button>
                </div>
              </div>
            </div>
          </CardContent>
          <CardFooter className="flex flex-col gap-3">
            <Button className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
              <CreditCard className="mr-2 h-4 w-4" />
              Proceed to Checkout
            </Button>
            <p className="text-center text-xs text-muted-foreground">
              Secure checkout powered by Stripe
            </p>
          </CardFooter>
        </Card>
      </div>
    </div>
  )
}
