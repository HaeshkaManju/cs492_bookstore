"use client"

import { createContext, useContext, useState, ReactNode } from "react"

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
  addToCart: (book: Book) => void
  removeFromCart: (bookId: string) => void
  updateCartQuantity: (bookId: string, quantity: number) => void
  clearCart: () => void
  cartTotal: number
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

export function StoreProvider({ children }: { children: ReactNode }) {
  const [books] = useState<Book[]>(sampleBooks)
  const [cart, setCart] = useState<CartItem[]>([])
  const [salesRecords] = useState<SalesRecord[]>(sampleSalesRecords)
  const [purchaseOrders] = useState<PurchaseOrder[]>(samplePurchaseOrders)

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
        addToCart,
        removeFromCart,
        updateCartQuantity,
        clearCart,
        cartTotal
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
