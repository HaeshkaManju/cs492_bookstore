"use client"

/**
 * Store Context
 * =============
 * 
 * Task: INT-S2-002
 * 
 * Provides store state with API integration.
 * Falls back to sample data when API is unavailable.
 */

import { createContext, useContext, useState, useEffect, ReactNode } from "react"
import { api, Book as ApiBook, Inventory, Invoice, PurchaseOrder as ApiPO } from "./api-client"

export interface Book {
  id: string
  title: string
  author: string
  isbn: string
  price: number
  condition: "Mint" | "Near Mint" | "Very Good" | "Good" | "Fair"
  year: number
  quantity: number
  description: string
  category: string
}

export interface CartItem {
  book: Book
  quantity: number
}

export interface SalesRecord {
  id: string
  bookId: string
  bookTitle: string
  customer: string
  quantity: number
  total: number
  date: string
  status: "Completed" | "Pending" | "Refunded"
}

export interface PurchaseOrder {
  id: string
  supplier: string
  items: { title: string; quantity: number; cost: number }[]
  total: number
  date: string
  status: "Pending" | "Approved" | "Received" | "Cancelled"
}

interface StoreContextType {
  books: Book[]
  cart: CartItem[]
  salesRecords: SalesRecord[]
  purchaseOrders: PurchaseOrder[]
  isLoading: boolean
  error: string | null
  addToCart: (book: Book) => void
  removeFromCart: (bookId: string) => void
  updateCartQuantity: (bookId: string, quantity: number) => void
  clearCart: () => void
  cartTotal: number
  refreshBooks: () => Promise<void>
  refreshSales: () => Promise<void>
  refreshOrders: () => Promise<void>
}

const StoreContext = createContext<StoreContextType | undefined>(undefined)

const sampleBooks: Book[] = [
  {
    id: "1",
    title: "The Great Gatsby",
    author: "F. Scott Fitzgerald",
    isbn: "978-0743273565",
    price: 1250.00,
    condition: "Near Mint",
    year: 1925,
    quantity: 2,
    description: "First edition, exceptional condition with original dust jacket.",
    category: "American Literature"
  },
  {
    id: "2",
    title: "Pride and Prejudice",
    author: "Jane Austen",
    isbn: "978-0141439518",
    price: 3500.00,
    condition: "Very Good",
    year: 1813,
    quantity: 1,
    description: "Early edition, leather-bound with gilt edges.",
    category: "British Literature"
  },
  {
    id: "3",
    title: "Moby-Dick",
    author: "Herman Melville",
    isbn: "978-0142437247",
    price: 2800.00,
    condition: "Good",
    year: 1851,
    quantity: 3,
    description: "Rare early American edition with illustrations.",
    category: "American Literature"
  },
  {
    id: "4",
    title: "To Kill a Mockingbird",
    author: "Harper Lee",
    isbn: "978-0446310789",
    price: 4500.00,
    condition: "Mint",
    year: 1960,
    quantity: 1,
    description: "First edition, first printing. Signed by author.",
    category: "American Literature"
  },
  {
    id: "5",
    title: "1984",
    author: "George Orwell",
    isbn: "978-0451524935",
    price: 1800.00,
    condition: "Very Good",
    year: 1949,
    quantity: 4,
    description: "First UK edition with original dust jacket.",
    category: "Dystopian Fiction"
  },
  {
    id: "6",
    title: "The Catcher in the Rye",
    author: "J.D. Salinger",
    isbn: "978-0316769488",
    price: 2200.00,
    condition: "Near Mint",
    year: 1951,
    quantity: 2,
    description: "First edition, excellent condition.",
    category: "American Literature"
  },
  {
    id: "7",
    title: "Frankenstein",
    author: "Mary Shelley",
    isbn: "978-0486282114",
    price: 5500.00,
    condition: "Good",
    year: 1818,
    quantity: 1,
    description: "Third edition with annotations.",
    category: "Gothic Literature"
  },
  {
    id: "8",
    title: "The Adventures of Sherlock Holmes",
    author: "Arthur Conan Doyle",
    isbn: "978-0140439083",
    price: 3200.00,
    condition: "Very Good",
    year: 1892,
    quantity: 2,
    description: "First edition with original illustrations by Sidney Paget.",
    category: "Mystery"
  }
]

const sampleSalesRecords: SalesRecord[] = [
  {
    id: "SR001",
    bookId: "1",
    bookTitle: "The Great Gatsby",
    customer: "John Smith",
    quantity: 1,
    total: 1250.00,
    date: "2024-01-15",
    status: "Completed"
  },
  {
    id: "SR002",
    bookId: "4",
    bookTitle: "To Kill a Mockingbird",
    customer: "Emily Brown",
    quantity: 1,
    total: 4500.00,
    date: "2024-01-14",
    status: "Completed"
  },
  {
    id: "SR003",
    bookId: "5",
    bookTitle: "1984",
    customer: "Michael Chen",
    quantity: 2,
    total: 3600.00,
    date: "2024-01-13",
    status: "Pending"
  },
  {
    id: "SR004",
    bookId: "2",
    bookTitle: "Pride and Prejudice",
    customer: "Sarah Wilson",
    quantity: 1,
    total: 3500.00,
    date: "2024-01-12",
    status: "Completed"
  },
  {
    id: "SR005",
    bookId: "6",
    bookTitle: "The Catcher in the Rye",
    customer: "David Lee",
    quantity: 1,
    total: 2200.00,
    date: "2024-01-11",
    status: "Refunded"
  }
]

const samplePurchaseOrders: PurchaseOrder[] = [
  {
    id: "PO001",
    supplier: "Antiquarian Books Ltd",
    items: [
      { title: "War and Peace - First Edition", quantity: 2, cost: 3500.00 },
      { title: "Anna Karenina - First Edition", quantity: 1, cost: 2800.00 }
    ],
    total: 9800.00,
    date: "2024-01-10",
    status: "Approved"
  },
  {
    id: "PO002",
    supplier: "Heritage Book Dealers",
    items: [
      { title: "The Odyssey - Illustrated", quantity: 3, cost: 1200.00 },
      { title: "The Iliad - Leather Bound", quantity: 2, cost: 1500.00 }
    ],
    total: 6600.00,
    date: "2024-01-08",
    status: "Pending"
  },
  {
    id: "PO003",
    supplier: "Rare Finds Inc",
    items: [
      { title: "Don Quixote - 1885 Edition", quantity: 1, cost: 4500.00 }
    ],
    total: 4500.00,
    date: "2024-01-05",
    status: "Received"
  }
]

// Map condition number to label
const conditionMap: Record<number, Book['condition']> = {
  5: "Mint",
  4: "Near Mint",
  3: "Very Good",
  2: "Good",
  1: "Fair"
}

// Transform API inventory to frontend Book format
function inventoryToBook(inv: Inventory): Book {
  return {
    id: inv.id,
    title: inv.book_title || 'Unknown',
    author: inv.book_author || 'Unknown',
    isbn: '',
    price: inv.list_price,
    condition: conditionMap[inv.condition] || "Good",
    year: 0,
    quantity: inv.quantity,
    description: '',
    category: ''
  }
}

export function StoreProvider({ children }: { children: ReactNode }) {
  const [books, setBooks] = useState<Book[]>(sampleBooks)
  const [cart, setCart] = useState<CartItem[]>([])
  const [salesRecords, setSalesRecords] = useState<SalesRecord[]>(sampleSalesRecords)
  const [purchaseOrders, setPurchaseOrders] = useState<PurchaseOrder[]>(samplePurchaseOrders)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch books/inventory from API
  const refreshBooks = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const response = await api.getInventory({ in_stock_only: true, per_page: 100 })
      if (response.success && response.data) {
        const apiBooks = response.data.map(inventoryToBook)
        if (apiBooks.length > 0) {
          setBooks(apiBooks)
        }
      }
    } catch (err) {
      console.warn('Failed to fetch from API, using sample data')
      setError('Using offline data')
    }
    setIsLoading(false)
  }

  // Fetch sales/invoices from API
  const refreshSales = async () => {
    try {
      const response = await api.getInvoices({ per_page: 50 })
      if (response.success && response.data && response.data.length > 0) {
        const records: SalesRecord[] = response.data.map((inv: Invoice) => ({
          id: inv.invoice_number,
          bookId: inv.id,
          bookTitle: `Invoice ${inv.invoice_number}`,
          customer: inv.customer_id,
          quantity: 1,
          total: inv.subtotal,
          date: inv.created_at.split('T')[0],
          status: inv.status === 'paid' ? 'Completed' : inv.status === 'cancelled' ? 'Refunded' : 'Pending'
        }))
        setSalesRecords(records)
      }
    } catch {
      console.warn('Failed to fetch sales, using sample data')
    }
  }

  // Fetch purchase orders from API
  const refreshOrders = async () => {
    try {
      const response = await api.getPurchaseOrders({ per_page: 50 })
      if (response.success && response.data && response.data.length > 0) {
        const orders: PurchaseOrder[] = response.data.map((po: ApiPO) => ({
          id: po.po_number,
          supplier: po.manufacturer?.name || 'Unknown',
          items: po.lines?.map(l => ({ title: l.description, quantity: l.quantity, cost: l.unit_cost })) || [],
          total: po.total,
          date: po.created_at.split('T')[0],
          status: po.status === 'received' ? 'Received' : 
                  po.status === 'confirmed' || po.status === 'submitted' ? 'Approved' :
                  po.status === 'cancelled' ? 'Cancelled' : 'Pending'
        }))
        setPurchaseOrders(orders)
      }
    } catch {
      console.warn('Failed to fetch orders, using sample data')
    }
  }

  // Initial data load
  useEffect(() => {
    refreshBooks()
    refreshSales()
    refreshOrders()
  }, [])

  const addToCart = (book: Book) => {
    setCart(prev => {
      const existing = prev.find(item => item.book.id === book.id)
      if (existing) {
        return prev.map(item =>
          item.book.id === book.id
            ? { ...item, quantity: item.quantity + 1 }
            : item
        )
      }
      return [...prev, { book, quantity: 1 }]
    })
  }

  const removeFromCart = (bookId: string) => {
    setCart(prev => prev.filter(item => item.book.id !== bookId))
  }

  const updateCartQuantity = (bookId: string, quantity: number) => {
    if (quantity <= 0) {
      removeFromCart(bookId)
      return
    }
    setCart(prev =>
      prev.map(item =>
        item.book.id === bookId ? { ...item, quantity } : item
      )
    )
  }

  const clearCart = () => {
    setCart([])
  }

  const cartTotal = cart.reduce((sum, item) => sum + item.book.price * item.quantity, 0)

  return (
    <StoreContext.Provider
      value={{
        books,
        cart,
        salesRecords,
        purchaseOrders,
        isLoading,
        error,
        addToCart,
        removeFromCart,
        updateCartQuantity,
        clearCart,
        cartTotal,
        refreshBooks,
        refreshSales,
        refreshOrders
      }}
    >
      {children}
    </StoreContext.Provider>
  )
}

export function useStore() {
  const context = useContext(StoreContext)
  if (context === undefined) {
    throw new Error("useStore must be used within a StoreProvider")
  }
  return context
}
