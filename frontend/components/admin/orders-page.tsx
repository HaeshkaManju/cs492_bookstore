"use client"

import { useStore } from "@/lib/store-context"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion"
import { Package, Plus, Clock, CheckCircle, XCircle, Truck } from "lucide-react"

export function OrdersPage() {
  const { purchaseOrders } = useStore()

  const pendingOrders = purchaseOrders.filter((o) => o.status === "Pending").length
  const totalPending = purchaseOrders
    .filter((o) => o.status === "Pending" || o.status === "Approved")
    .reduce((sum, o) => sum + o.total, 0)

  const getStatusColor = (status: string) => {
    switch (status) {
      case "Pending":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
      case "Approved":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20"
      case "Received":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      case "Cancelled":
        return "bg-red-500/10 text-red-400 border-red-500/20"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Pending":
        return <Clock className="h-4 w-4 text-yellow-400" />
      case "Approved":
        return <CheckCircle className="h-4 w-4 text-blue-400" />
      case "Received":
        return <Truck className="h-4 w-4 text-emerald-400" />
      case "Cancelled":
        return <XCircle className="h-4 w-4 text-red-400" />
      default:
        return null
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Purchase Orders</h1>
          <p className="text-sm text-muted-foreground">Manage supplier orders and acquisitions</p>
        </div>
        <Button className="w-fit bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          New Purchase Order
        </Button>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Orders</CardTitle>
            <Package className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{purchaseOrders.length}</div>
            <p className="text-xs text-muted-foreground">All time</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Pending Orders</CardTitle>
            <Clock className="h-4 w-4 text-yellow-400" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-400">{pendingOrders}</div>
            <p className="text-xs text-muted-foreground">Awaiting approval</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Outstanding Value</CardTitle>
            <Package className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">${totalPending.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Pending + Approved</p>
          </CardContent>
        </Card>
      </div>

      {/* Orders List */}
      <Card className="border-border bg-card">
        <CardHeader>
          <CardTitle className="text-lg font-medium">Orders</CardTitle>
        </CardHeader>
        <CardContent>
          <Accordion type="single" collapsible className="w-full">
            {purchaseOrders.map((order) => (
              <AccordionItem key={order.id} value={order.id} className="border-border">
                <AccordionTrigger className="hover:no-underline">
                  <div className="flex w-full items-center justify-between pr-4">
                    <div className="flex items-center gap-4">
                      {getStatusIcon(order.status)}
                      <div className="text-left">
                        <div className="font-medium text-foreground">{order.id}</div>
                        <div className="text-sm text-muted-foreground">{order.supplier}</div>
                      </div>
                    </div>
                    <div className="flex items-center gap-4">
                      <Badge variant="outline" className={getStatusColor(order.status)}>
                        {order.status}
                      </Badge>
                      <div className="text-right">
                        <div className="font-medium text-primary">${order.total.toLocaleString()}</div>
                        <div className="text-xs text-muted-foreground">
                          {new Date(order.date).toLocaleDateString()}
                        </div>
                      </div>
                    </div>
                  </div>
                </AccordionTrigger>
                <AccordionContent>
                  <div className="pt-4">
                    <Table>
                      <TableHeader>
                        <TableRow className="border-border hover:bg-transparent">
                          <TableHead className="text-muted-foreground">Item</TableHead>
                          <TableHead className="text-muted-foreground">Quantity</TableHead>
                          <TableHead className="text-right text-muted-foreground">Cost</TableHead>
                        </TableRow>
                      </TableHeader>
                      <TableBody>
                        {order.items.map((item, index) => (
                          <TableRow key={index} className="border-border hover:bg-muted/30">
                            <TableCell className="font-medium text-foreground">{item.title}</TableCell>
                            <TableCell className="text-muted-foreground">{item.quantity}</TableCell>
                            <TableCell className="text-right text-muted-foreground">
                              ${item.cost.toLocaleString()}
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                    <div className="mt-4 flex justify-end gap-2">
                      {order.status === "Pending" && (
                        <>
                          <Button variant="outline" size="sm" className="border-border">
                            Cancel
                          </Button>
                          <Button size="sm" className="bg-primary text-primary-foreground">
                            Approve
                          </Button>
                        </>
                      )}
                      {order.status === "Approved" && (
                        <Button size="sm" className="bg-emerald-600 text-white hover:bg-emerald-700">
                          Mark as Received
                        </Button>
                      )}
                    </div>
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        </CardContent>
      </Card>
    </div>
  )
}
