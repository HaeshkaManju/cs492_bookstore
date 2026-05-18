"use client"

import { useState } from "react"
import { Search, BookOpen, ShoppingCart, Filter } from "lucide-react"
import { useStore, Book } from "@/lib/store-context"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardFooter, CardHeader } from "@/components/ui/card"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"

export function BookCatalog() {
  const { books, addToCart } = useStore()
  const [search, setSearch] = useState("")
  const [categoryFilter, setCategoryFilter] = useState<string>("all")
  const [sortBy, setSortBy] = useState<string>("title")

  const categories = [...new Set(books.map((book) => book.category))]

  const filteredBooks = books
    .filter((book) => {
      const matchesSearch =
        book.title.toLowerCase().includes(search.toLowerCase()) ||
        book.author.toLowerCase().includes(search.toLowerCase())
      const matchesCategory = categoryFilter === "all" || book.category === categoryFilter
      return matchesSearch && matchesCategory && book.quantity > 0
    })
    .sort((a, b) => {
      switch (sortBy) {
        case "price-low":
          return a.price - b.price
        case "price-high":
          return b.price - a.price
        case "year":
          return a.year - b.year
        case "title":
        default:
          return a.title.localeCompare(b.title)
      }
    })

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
      {/* Hero Section */}
      <div className="rounded-xl bg-gradient-to-br from-card via-card to-primary/5 p-8 border border-border">
        <h1 className="text-3xl font-bold text-foreground">Discover Rare Books</h1>
        <p className="mt-2 text-muted-foreground">
          Explore our curated collection of first editions, signed copies, and antiquarian treasures
        </p>
      </div>

      {/* Filters */}
      <div className="flex flex-col gap-4 md:flex-row md:items-center">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Search by title or author..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="pl-9 bg-input border-border"
          />
        </div>
        <div className="flex gap-2">
          <Select value={categoryFilter} onValueChange={setCategoryFilter}>
            <SelectTrigger className="w-[180px] bg-input border-border">
              <Filter className="mr-2 h-4 w-4" />
              <SelectValue placeholder="Category" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Categories</SelectItem>
              {categories.map((cat) => (
                <SelectItem key={cat} value={cat}>
                  {cat}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          <Select value={sortBy} onValueChange={setSortBy}>
            <SelectTrigger className="w-[150px] bg-input border-border">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="title">Title A-Z</SelectItem>
              <SelectItem value="price-low">Price: Low to High</SelectItem>
              <SelectItem value="price-high">Price: High to Low</SelectItem>
              <SelectItem value="year">Oldest First</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      {/* Results Count */}
      <p className="text-sm text-muted-foreground">
        Showing {filteredBooks.length} of {books.length} books
      </p>

      {/* Book Grid */}
      <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
        {filteredBooks.map((book) => (
          <BookCard key={book.id} book={book} onAddToCart={addToCart} getConditionColor={getConditionColor} />
        ))}
      </div>

      {filteredBooks.length === 0 && (
        <div className="flex flex-col items-center justify-center py-16 text-center">
          <BookOpen className="h-16 w-16 text-muted-foreground/30" />
          <h3 className="mt-4 text-lg font-medium text-foreground">No books found</h3>
          <p className="mt-2 text-sm text-muted-foreground">
            Try adjusting your search or filter criteria
          </p>
        </div>
      )}
    </div>
  )
}

function BookCard({
  book,
  onAddToCart,
  getConditionColor,
}: {
  book: Book
  onAddToCart: (book: Book) => void
  getConditionColor: (condition: string) => string
}) {
  return (
    <Card className="group flex flex-col border-border bg-card transition-all hover:border-primary/30 hover:shadow-lg hover:shadow-primary/5">
      <CardHeader className="pb-3">
        <div className="flex items-start justify-between gap-2">
          <Badge variant="outline" className={getConditionColor(book.condition)}>
            {book.condition}
          </Badge>
          <span className="text-xs text-muted-foreground">{book.year}</span>
        </div>
      </CardHeader>
      <CardContent className="flex-1 pb-3">
        <div className="mb-3 flex h-32 items-center justify-center rounded-lg bg-secondary/50">
          <BookOpen className="h-16 w-16 text-primary/30" />
        </div>
        <h3 className="font-semibold text-foreground line-clamp-2">{book.title}</h3>
        <p className="mt-1 text-sm text-muted-foreground">{book.author}</p>
        <p className="mt-2 text-xs text-muted-foreground">{book.category}</p>
      </CardContent>
      <CardFooter className="flex items-center justify-between border-t border-border pt-4">
        <div>
          <p className="text-lg font-bold text-primary">${book.price.toLocaleString()}</p>
          <p className="text-xs text-muted-foreground">{book.quantity} in stock</p>
        </div>
        <div className="flex gap-2">
          <Dialog>
            <DialogTrigger asChild>
              <Button variant="outline" size="sm" className="border-border">
                Details
              </Button>
            </DialogTrigger>
            <DialogContent className="bg-card border-border">
              <DialogHeader>
                <DialogTitle className="text-foreground">{book.title}</DialogTitle>
                <DialogDescription className="text-muted-foreground">
                  by {book.author} ({book.year})
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-4">
                <div className="flex h-48 items-center justify-center rounded-lg bg-secondary/50">
                  <BookOpen className="h-24 w-24 text-primary/30" />
                </div>
                <div className="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">ISBN</p>
                    <p className="font-mono text-foreground">{book.isbn}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Condition</p>
                    <Badge variant="outline" className={getConditionColor(book.condition)}>
                      {book.condition}
                    </Badge>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Category</p>
                    <p className="text-foreground">{book.category}</p>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Available</p>
                    <p className="text-foreground">{book.quantity} copies</p>
                  </div>
                </div>
                <div>
                  <p className="text-muted-foreground">Description</p>
                  <p className="text-sm text-foreground">{book.description}</p>
                </div>
                <div className="flex items-center justify-between border-t border-border pt-4">
                  <p className="text-2xl font-bold text-primary">${book.price.toLocaleString()}</p>
                  <Button onClick={() => onAddToCart(book)} className="bg-primary text-primary-foreground">
                    <ShoppingCart className="mr-2 h-4 w-4" />
                    Add to Cart
                  </Button>
                </div>
              </div>
            </DialogContent>
          </Dialog>
          <Button
            size="sm"
            onClick={() => onAddToCart(book)}
            className="bg-primary text-primary-foreground hover:bg-primary/90"
          >
            <ShoppingCart className="h-4 w-4" />
          </Button>
        </div>
      </CardFooter>
    </Card>
  )
}
