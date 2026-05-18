import { CustomerHeader } from "@/components/customer/customer-header"

export default function CustomerLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen bg-background">
      <CustomerHeader />
      <main className="container mx-auto px-4 py-8">{children}</main>
    </div>
  )
}
