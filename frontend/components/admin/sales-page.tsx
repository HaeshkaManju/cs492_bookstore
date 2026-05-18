"use client"

import { useStore } from "@/lib/store-context"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import { TrendingUp, DollarSign, ShoppingBag, RefreshCcw } from "lucide-react"

export function SalesPage() {
  const { salesRecords } = useStore()

  const totalRevenue = salesRecords
    .filter((r) => r.status === "Completed")
    .reduce((sum, record) => sum + record.total, 0)

  const pendingRevenue = salesRecords
    .filter((r) => r.status === "Pending")
    .reduce((sum, record) => sum + record.total, 0)

  const refundedAmount = salesRecords
    .filter((r) => r.status === "Refunded")
    .reduce((sum, record) => sum + record.total, 0)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Completed":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      case "Pending":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
      case "Refunded":
        return "bg-red-500/10 text-red-400 border-red-500/20"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-semibold text-foreground">Sales Records</h1>
        <p className="text-sm text-muted-foreground">Track and manage your sales history</p>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Sales</CardTitle>
            <ShoppingBag className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{salesRecords.length}</div>
            <p className="text-xs text-muted-foreground">All time transactions</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Revenue</CardTitle>
            <DollarSign className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">${totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Completed sales</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pending</CardTitle>
            <TrendingUp className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">${pendingRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Awaiting completion</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Refunded</CardTitle>
            <RefreshCcw className="h-4 w-4 text-red-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-400">${refundedAmount.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Returned value</p>
          </CardContent>
        </Card>
      </div>

      {/* Sales Table */}
      <Card className="border-border bg-card">
        <CardHeader>
          <CardTitle className="text-lg font-medium">Recent Transactions</CardTitle>
        </CardHeader>
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-muted-foreground">Order ID</TableHead>
                <TableHead className="text-muted-foreground">Book</TableHead>
                <TableHead className="text-muted-foreground">Customer</TableHead>
                <TableHead className="text-muted-foreground">Date</TableHead>
                <TableHead className="text-muted-foreground">Qty</TableHead>
                <TableHead className="text-muted-foreground">Status</TableHead>
                <TableHead className="text-right text-muted-foreground">Total</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {salesRecords.map((record) => (
                <TableRow key={record.id} className="border-border hover:bg-muted/30">
                  <TableCell className="font-mono text-xs text-muted-foreground">
                    {record.id}
                  </TableCell>
                  <TableCell className="font-medium text-foreground">{record.bookTitle}</TableCell>
                  <TableCell className="text-muted-foreground">{record.customer}</TableCell>
                  <TableCell className="text-muted-foreground">
                    {new Date(record.date).toLocaleDateString()}
                  </TableCell>
                  <TableCell className="text-muted-foreground">{record.quantity}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getStatusColor(record.status)}>
                      {record.status}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-right font-medium text-primary">
                    ${record.total.toLocaleString()}
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  )
}
