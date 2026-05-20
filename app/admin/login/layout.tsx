import { AuthProvider } from "@/lib/auth-context"

export default function AdminLoginLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <AuthProvider>
      {children}
    </AuthProvider>
  )
}
