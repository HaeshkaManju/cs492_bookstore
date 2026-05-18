"use client"

import { useState } from "react"
import { Search, Filter, MoreHorizontal, BookOpen, RefreshCw } from "lucide-react"
import { useStore } from "@/lib/store-context"
import { AddBookDialog } from "@/components/admin/add-book-dialog"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function InventoryPage() {
  const { books, isLoading, refreshBooks } = useStore()
  const [searchTitle, setSearchTitle] = useState("")
  const [searchAuthor, setSearchAuthor] = useState("")
  const [searchIsbn, setSearchIsbn] = useState("")
  const [conditionFilter, setConditionFilter] = useState<string>("all")

  const filteredBooks = books.filter((book) => {
    const matchesTitle = book.title.toLowerCase().includes(searchTitle.toLowerCase())
    const matchesAuthor = book.author.toLowerCase().includes(searchAuthor.toLowerCase())
    const matchesIsbn = book.isbn.toLowerCase().includes(searchIsbn.toLowerCase())
    const matchesCondition = conditionFilter === "all" || book.condition === conditionFilter
    return matchesTitle && matchesAuthor && matchesIsbn && matchesCondition
  })

  const totalValue = filteredBooks.reduce((sum, book) => sum + book.price * book.quantity, 0)
  const totalItems = filteredBooks.reduce((sum, book) => sum + book.quantity, 0)

  const getConditionColor = (condition: string) => {
    switch (condition) {
      case "Mint":
        return "bg-emerald-500/10 text-emerald-400 border-emerald-500/20"
      case "Near Mint":
        return "bg-green-500/10 text-green-400 border-green-500/20"
      case "Very Good":
        return "bg-blue-500/10 text-blue-400 border-blue-500/20"
      case "Good":
        return "bg-yellow-500/10 text-yellow-400 border-yellow-500/20"
      case "Fair":
        return "bg-orange-500/10 text-orange-400 border-orange-500/20"
      default:
        return "bg-muted text-muted-foreground"
    }
  }

  return (
    <div className="flex flex-col gap-6">
      {/* Header */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-foreground">Inventory</h1>
          <p className="text-sm text-muted-foreground">Manage your rare book collection</p>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="icon"
            onClick={() => refreshBooks()}
            disabled={isLoading}
            className="border-border"
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? 'animate-spin' : ''}`} />
          </Button>
          <AddBookDialog />
        </div>
      </div>

      {/* Stats */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Books</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{filteredBooks.length}</div>
            <p className="text-xs text-muted-foreground">Unique titles</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Items</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{totalItems}</div>
            <p className="text-xs text-muted-foreground">In stock</p>
          </CardContent>
        </Card>
        <Card className="border-border bg-card">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Inventory Value</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-primary">${totalValue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">Total estimated</p>
          </CardContent>
        </Card>
      </div>

      {/* Search Filters */}
      <Card className="border-border bg-card">
        <CardHeader className="pb-4">
          <div className="flex items-center gap-2">
            <Filter className="h-4 w-4 text-muted-foreground" />
            <CardTitle className="text-sm font-medium">Search & Filter</CardTitle>
          </div>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by title..."
                value={searchTitle}
                onChange={(e) => setSearchTitle(e.target.value)}
                className="pl-9 bg-input border-border"
              />
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by author..."
                value={searchAuthor}
                onChange={(e) => setSearchAuthor(e.target.value)}
                className="pl-9 bg-input border-border"
              />
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Search by ISBN..."
                value={searchIsbn}
                onChange={(e) => setSearchIsbn(e.target.value)}
                className="pl-9 bg-input border-border"
              />
            </div>
            <Select value={conditionFilter} onValueChange={setConditionFilter}>
              <SelectTrigger className="bg-input border-border">
                <SelectValue placeholder="Filter by condition" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Conditions</SelectItem>
                <SelectItem value="Mint">Mint</SelectItem>
                <SelectItem value="Near Mint">Near Mint</SelectItem>
                <SelectItem value="Very Good">Very Good</SelectItem>
                <SelectItem value="Good">Good</SelectItem>
                <SelectItem value="Fair">Fair</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </CardContent>
      </Card>

      {/* Table */}
      <Card className="border-border bg-card">
        <CardContent className="p-0">
          <Table>
            <TableHeader>
              <TableRow className="border-border hover:bg-transparent">
                <TableHead className="text-muted-foreground">Title</TableHead>
                <TableHead className="text-muted-foreground">Author</TableHead>
                <TableHead className="text-muted-foreground">ISBN</TableHead>
                <TableHead className="text-muted-foreground">Year</TableHead>
                <TableHead className="text-muted-foreground">Condition</TableHead>
                <TableHead className="text-muted-foreground">Qty</TableHead>
                <TableHead className="text-right text-muted-foreground">Price</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredBooks.map((book) => (
                <TableRow key={book.id} className="border-border hover:bg-muted/30">
                  <TableCell className="font-medium text-foreground">{book.title}</TableCell>
                  <TableCell className="text-muted-foreground">{book.author}</TableCell>
                  <TableCell className="font-mono text-xs text-muted-foreground">{book.isbn}</TableCell>
                  <TableCell className="text-muted-foreground">{book.year}</TableCell>
                  <TableCell>
                    <Badge variant="outline" className={getConditionColor(book.condition)}>
                      {book.condition}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-muted-foreground">{book.quantity}</TableCell>
                  <TableCell className="text-right font-medium text-primary">
                    ${book.price.toLocaleString()}
                  </TableCell>
                  <TableCell>
                    <DropdownMenu>
                      <DropdownMenuTrigger asChild>
                        <Button variant="ghost" size="icon" className="h-8 w-8">
                          <MoreHorizontal className="h-4 w-4" />
                        </Button>
                      </DropdownMenuTrigger>
                      <DropdownMenuContent align="end">
                        <DropdownMenuItem>Edit</DropdownMenuItem>
                        <DropdownMenuItem>View Details</DropdownMenuItem>
                        <DropdownMenuItem className="text-destructive">Delete</DropdownMenuItem>
                      </DropdownMenuContent>
                    </DropdownMenu>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
          {filteredBooks.length === 0 && (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <BookOpen className="h-12 w-12 text-muted-foreground/50" />
              <p className="mt-4 text-sm text-muted-foreground">No books found matching your search criteria</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
