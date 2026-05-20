"use client"

import { useState } from "react"
import Link from "next/link"
import { BookOpen, ArrowLeft, Sparkles } from "lucide-react"
import { CustomerLoginForm } from "@/components/auth/customer-login-form"
import { CustomerRegisterForm } from "@/components/auth/customer-register-form"

export default function CustomerLoginPage() {
  const [isRegistering, setIsRegistering] = useState(false)

  return (
    <div className="flex min-h-screen">
      {/* Left Panel - Branding */}
      <div className="hidden lg:flex lg:w-1/2 flex-col justify-between bg-secondary p-12">
        <div>
          <Link href="/" className="flex items-center gap-3 text-foreground hover:opacity-80 transition-opacity">
            <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-primary/10">
              <BookOpen className="h-5 w-5 text-primary" />
            </div>
            <span className="text-xl font-semibold">Rare Books</span>
          </Link>
        </div>

        <div className="space-y-6">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-primary/10">
            <Sparkles className="h-8 w-8 text-primary" />
          </div>
          <div className="space-y-2">
            <h2 className="text-3xl font-bold text-foreground">
              {isRegistering ? "Join Our Collection" : "Welcome Back"}
            </h2>
            <p className="text-lg text-muted-foreground leading-relaxed max-w-md">
              {isRegistering
                ? "Create an account to browse our curated selection of rare and antiquarian books, track your orders, and build your personal collection."
                : "Sign in to continue browsing our exquisite collection of rare and antiquarian books from around the world."}
            </p>
          </div>
          <ul className="space-y-3 text-muted-foreground">
            <li className="flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Curated rare book collection
            </li>
            <li className="flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Authenticated first editions
            </li>
            <li className="flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Secure checkout process
            </li>
            <li className="flex items-center gap-3">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Order tracking and history
            </li>
          </ul>
        </div>

        <p className="text-sm text-muted-foreground">
          Trusted by collectors worldwide since 2024.
        </p>
      </div>

      {/* Right Panel - Login/Register Form */}
      <div className="flex w-full lg:w-1/2 flex-col bg-background">
        <div className="flex items-center justify-between p-6">
          <Link 
            href="/" 
            className="flex items-center gap-2 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back to home
          </Link>
          <Link 
            href="/admin/login" 
            className="text-sm text-muted-foreground hover:text-primary transition-colors"
          >
            Admin login
          </Link>
        </div>

        <div className="flex flex-1 items-center justify-center px-6 pb-12">
          <div className="w-full max-w-sm space-y-8">
            {/* Mobile Logo */}
            <div className="lg:hidden text-center">
              <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary/10">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
            </div>

            <div className="space-y-2 text-center">
              <h1 className="text-2xl font-bold tracking-tight text-foreground">
                {isRegistering ? "Create Account" : "Sign In"}
              </h1>
              <p className="text-muted-foreground">
                {isRegistering
                  ? "Enter your details to create your account"
                  : "Welcome back! Please enter your details"}
              </p>
            </div>

            {isRegistering ? (
              <CustomerRegisterForm onToggleLogin={() => setIsRegistering(false)} />
            ) : (
              <CustomerLoginForm onToggleRegister={() => setIsRegistering(true)} />
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
