"use client"

/**
 * Add Book Dialog
 * ===============
 * 
 * Task: FE-S2-003
 * 
 * Modal dialog for adding new books to inventory.
 */

import { useState } from "react"
import { Plus, BookOpen } from "lucide-react"
import { api } from "@/lib/api-client"
import { useStore } from "@/lib/store-context"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

interface AddBookDialogProps {
  onSuccess?: () => void
}

export function AddBookDialog({ onSuccess }: AddBookDialogProps) {
  const { refreshBooks } = useStore()
  const [open, setOpen] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState("")
  
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    isbn: "",
    publisher: "",
    year_published: "",
    description: "",
    category: "",
    // Inventory fields
    condition: "3",
    quantity: "1",
    acquisition_cost: "",
    list_price: "",
  })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setFormData(prev => ({
      ...prev,
      [e.target.name]: e.target.value
    }))
  }

  const handleSelectChange = (name: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  const resetForm = () => {
    setFormData({
      title: "",
      author: "",
      isbn: "",
      publisher: "",
      year_published: "",
      description: "",
      category: "",
      condition: "3",
      quantity: "1",
      acquisition_cost: "",
      list_price: "",
    })
    setError("")
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError("")
    setIsLoading(true)

    try {
      // First create the book
      const bookResponse = await api.createBook({
        title: formData.title,
        author: formData.author,
        isbn: formData.isbn || undefined,
        publisher: formData.publisher || undefined,
        year_published: formData.year_published ? parseInt(formData.year_published) : undefined,
        description: formData.description || undefined,
        category: formData.category || undefined,
      })

      if (!bookResponse.success || !bookResponse.data) {
        throw new Error(bookResponse.error?.message || "Failed to create book")
      }

      // If inventory fields are provided, add inventory
      if (formData.acquisition_cost && formData.list_price) {
        // Get first warehouse
        const warehousesResponse = await api.getWarehouses()
        if (warehousesResponse.success && warehousesResponse.data && warehousesResponse.data.length > 0) {
          await api.addInventory({
            book_id: bookResponse.data.id,
            warehouse_id: warehousesResponse.data[0].id,
            condition: parseInt(formData.condition),
            quantity: parseInt(formData.quantity),
            acquisition_cost: parseFloat(formData.acquisition_cost),
            list_price: parseFloat(formData.list_price),
          })
        }
      }

      // Refresh books list
      await refreshBooks()
      
      // Close dialog and reset
      setOpen(false)
      resetForm()
      onSuccess?.()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add book")
    }
    
    setIsLoading(false)
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        <Button className="bg-primary text-primary-foreground hover:bg-primary/90">
          <Plus className="mr-2 h-4 w-4" />
          Add New Book
        </Button>
      </DialogTrigger>
      <DialogContent className="bg-card border-border max-w-2xl max-h-[90vh] overflow-y-auto">
        <form onSubmit={handleSubmit}>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <BookOpen className="h-5 w-5" />
              Add New Book
            </DialogTitle>
            <DialogDescription>
              Add a new book to the catalog and optionally set initial inventory.
            </DialogDescription>
          </DialogHeader>
          
          <div className="grid gap-4 py-4">
            {error && (
              <div className="rounded-lg bg-destructive/10 p-3 text-sm text-destructive">
                {error}
              </div>
            )}
            
            {/* Book Info Section */}
            <div className="space-y-4">
              <h3 className="font-medium text-sm text-muted-foreground">Book Information</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="title">Title *</Label>
                  <Input
                    id="title"
                    name="title"
                    value={formData.title}
                    onChange={handleChange}
                    required
                    className="bg-input border-border"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="author">Author *</Label>
                  <Input
                    id="author"
                    name="author"
                    value={formData.author}
                    onChange={handleChange}
                    required
                    className="bg-input border-border"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="isbn">ISBN</Label>
                  <Input
                    id="isbn"
                    name="isbn"
                    value={formData.isbn}
                    onChange={handleChange}
                    placeholder="978-..."
                    className="bg-input border-border"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="year_published">Year Published</Label>
                  <Input
                    id="year_published"
                    name="year_published"
                    type="number"
                    value={formData.year_published}
                    onChange={handleChange}
                    placeholder="1925"
                    className="bg-input border-border"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="publisher">Publisher</Label>
                  <Input
                    id="publisher"
                    name="publisher"
                    value={formData.publisher}
                    onChange={handleChange}
                    className="bg-input border-border"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="category">Category</Label>
                  <Input
                    id="category"
                    name="category"
                    value={formData.category}
                    onChange={handleChange}
                    placeholder="American Literature"
                    className="bg-input border-border"
                  />
                </div>
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  name="description"
                  value={formData.description}
                  onChange={handleChange}
                  rows={3}
                  className="bg-input border-border"
                />
              </div>
            </div>
            
            {/* Inventory Section */}
            <div className="space-y-4 border-t border-border pt-4">
              <h3 className="font-medium text-sm text-muted-foreground">Initial Inventory (Optional)</h3>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="condition">Condition</Label>
                  <Select value={formData.condition} onValueChange={(v) => handleSelectChange("condition", v)}>
                    <SelectTrigger className="bg-input border-border">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="5">Mint</SelectItem>
                      <SelectItem value="4">Near Mint</SelectItem>
                      <SelectItem value="3">Very Good</SelectItem>
                      <SelectItem value="2">Good</SelectItem>
                      <SelectItem value="1">Fair</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="quantity">Quantity</Label>
                  <Input
                    id="quantity"
                    name="quantity"
                    type="number"
                    min="1"
                    value={formData.quantity}
                    onChange={handleChange}
                    className="bg-input border-border"
                  />
                </div>
              </div>
              
              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="acquisition_cost">Cost Price ($)</Label>
                  <Input
                    id="acquisition_cost"
                    name="acquisition_cost"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.acquisition_cost}
                    onChange={handleChange}
                    placeholder="25.00"
                    className="bg-input border-border"
                  />
                </div>
                
                <div className="space-y-2">
                  <Label htmlFor="list_price">List Price ($)</Label>
                  <Input
                    id="list_price"
                    name="list_price"
                    type="number"
                    step="0.01"
                    min="0"
                    value={formData.list_price}
                    onChange={handleChange}
                    placeholder="49.99"
                    className="bg-input border-border"
                  />
                </div>
              </div>
            </div>
          </div>
          
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => setOpen(false)}
              className="border-border"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              disabled={isLoading}
              className="bg-primary text-primary-foreground"
            >
              {isLoading ? "Adding..." : "Add Book"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
