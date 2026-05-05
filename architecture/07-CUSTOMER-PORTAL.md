# Customer Portal Module

**Related Stories:** US-008  
**Related Tasks:** Sprint 4+ (Post-Sprint 3)

---

## 1. Overview

The Customer Portal provides a public-facing interface for customers to:
- Browse and search the book catalog
- Add items to a shopping cart
- Complete checkout with shipping and billing
- Create and manage customer accounts
- View order history and track status

---

## 2. Definition of Done Reference

From the project DoD (Section 4.4):
> - Customer shall access public-facing interface without admin credentials
> - Customer shall select items and add to virtual shopping cart
> - Customer shall proceed through checkout process
> - Customer shall receive order confirmation
> - Customer shall create account and view order history
> - Admin shall see customer orders in processing queue

---

## 3. Customer Journey Flow

```
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Browse    │───►│   Search    │───►│   View      │
│   Catalog   │    │   Results   │    │   Book      │
└─────────────┘    └─────────────┘    └──────┬──────┘
                                             │
                                             ▼
┌─────────────┐    ┌─────────────┐    ┌─────────────┐
│   Order     │◄───│  Checkout   │◄───│   Cart      │
│   Confirm   │    │   Process   │    │   Review    │
└─────────────┘    └─────────────┘    └─────────────┘
                          │
                          ▼
                   ┌─────────────┐
                   │  Account    │
                   │  Dashboard  │
                   └─────────────┘
```

---

## 4. Feature Specifications

### 4.1 Catalog Browsing (Public)

| Feature | Description |
|---------|-------------|
| Home Page | Featured books, categories, search |
| Category Browse | Filter by genre/category |
| Search | Title, author, ISBN search |
| Book Details | Full description, price, availability |
| No Login Required | Browse without account |

### 4.2 Shopping Cart

| Feature | Description |
|---------|-------------|
| Add to Cart | From catalog or book detail |
| Cart Persistence | Session storage (guest), DB (logged in) |
| Quantity Update | Increase/decrease, max = available stock |
| Remove Items | Individual or clear all |
| Cart Summary | Subtotal, estimated tax |

### 4.3 Checkout Process

| Step | Fields | Validation |
|------|--------|------------|
| 1. Login/Register | Email, password (optional guest) | Required for account features |
| 2. Shipping | Name, address, city, state, zip | Required, address validation |
| 3. Billing | Same as shipping option, card details | Required |
| 4. Review | All order details | Confirm totals |
| 5. Confirmation | Order number, email sent | Success page |

### 4.4 Customer Account

| Feature | Description |
|---------|-------------|
| Registration | Email, password, name |
| Login | Email + password → JWT |
| Profile | Update name, email, password |
| Addresses | Save multiple shipping addresses |
| Payment Methods | Save cards (tokenized) |
| Order History | View past orders |
| Order Tracking | Current order status |

---

## 5. UI Components

### 5.1 Catalog / Home Page

```
┌─────────────────────────────────────────────────────────────────┐
│  🏠 Rare Bookstore                    [🔍 Search] [Cart (3)] 🔒 │
├─────────────────────────────────────────────────────────────────┤
│  Categories: [Fiction] [Non-Fiction] [Rare] [Technical] [All]   │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────┐            │
│  │ [Book   │  │ [Book   │  │ [Book   │  │ [Book   │            │
│  │  Cover] │  │  Cover] │  │  Cover] │  │  Cover] │            │
│  │         │  │         │  │         │  │         │            │
│  │ Title   │  │ Title   │  │ Title   │  │ Title   │            │
│  │ Author  │  │ Author  │  │ Author  │  │ Author  │            │
│  │ $49.99  │  │ $29.99  │  │ $99.99  │  │ $19.99  │            │
│  │[Add Cart│  │[Add Cart│  │[Add Cart│  │[Add Cart│            │
│  └─────────┘  └─────────┘  └─────────┘  └─────────┘            │
│                                                                 │
│  [< Prev]  Page 1 of 50  [Next >]                              │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Book Detail Page

```
┌─────────────────────────────────────────────────────────────────┐
│  ← Back to Catalog                                              │
├───────────────────────┬─────────────────────────────────────────┤
│                       │  Clean Code                             │
│    ┌─────────────┐    │  by Robert C. Martin                    │
│    │             │    │                                         │
│    │  [Book      │    │  ★★★★☆ (24 reviews)                    │
│    │   Cover]    │    │                                         │
│    │             │    │  Price: $49.99                          │
│    │             │    │  Availability: ● In Stock               │
│    └─────────────┘    │                                         │
│                       │  Qty: [1 ▼]   [Add to Cart]             │
│                       │                                         │
├───────────────────────┴─────────────────────────────────────────┤
│  Description                                                    │
│  ─────────────────────────────────────────────────────────────  │
│  Even bad code can function. But if code isn't clean, it can   │
│  bring a development organization to its knees...              │
│                                                                 │
│  Details                                                        │
│  ISBN: 978-0-13-235088-4                                       │
│  Publisher: Prentice Hall                                      │
│  Category: Programming                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 5.3 Shopping Cart

```
┌─────────────────────────────────────────────────────────────────┐
│  Your Shopping Cart (3 items)                                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌────────┐                                                     │
│  │[Cover] │  Clean Code                    Qty: [2 ▼]  $99.98  │
│  └────────┘  Robert C. Martin                      [Remove]     │
│                                                                 │
│  ┌────────┐                                                     │
│  │[Cover] │  JavaScript: The Good Parts   Qty: [1 ▼]  $29.99  │
│  └────────┘  Douglas Crockford                     [Remove]     │
├─────────────────────────────────────────────────────────────────┤
│                                         Subtotal:     $129.97   │
│                                         Est. Tax:      $10.72   │
│                                         ─────────────────────   │
│                                         Est. Total:   $140.69   │
├─────────────────────────────────────────────────────────────────┤
│  [Continue Shopping]                      [Proceed to Checkout] │
└─────────────────────────────────────────────────────────────────┘
```

### 5.4 Checkout Flow

```
┌─────────────────────────────────────────────────────────────────┐
│  Checkout    ① Shipping ──── ② Billing ──── ③ Review ──── Done │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Shipping Address                                               │
│  ─────────────────────────────────────────────────────────────  │
│  Name:        [John Doe                    ]                    │
│  Address:     [123 Main Street             ]                    │
│  City:        [Austin           ]  State: [TX ▼]               │
│  ZIP:         [78701    ]  Country: [United States ▼]          │
│                                                                 │
│  ☐ Save this address for future orders                         │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│  [Back to Cart]                           [Continue to Billing] │
└─────────────────────────────────────────────────────────────────┘
```

### 5.5 Order Confirmation

```
┌─────────────────────────────────────────────────────────────────┐
│                     ✓ Order Confirmed!                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Order Number: ORD-2026-001234                                 │
│  Date: May 5, 2026                                             │
│                                                                 │
│  A confirmation email has been sent to john.doe@email.com      │
│                                                                 │
│  ┌────────────────────────────────────────────────────────┐    │
│  │  ITEMS                                                  │    │
│  │  2× Clean Code                              $99.98     │    │
│  │  1× JavaScript: The Good Parts              $29.99     │    │
│  │                                                        │    │
│  │  Subtotal:                                 $129.97     │    │
│  │  Shipping:                                   $5.99     │    │
│  │  Tax:                                       $10.72     │    │
│  │  ───────────────────────────────────────────────────   │    │
│  │  TOTAL:                                    $146.68     │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                 │
│  [Track Order]                      [Continue Shopping]         │
└─────────────────────────────────────────────────────────────────┘
```

---

## 6. API Endpoints

### 6.1 Public Endpoints (No Auth)

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/catalog | Browse catalog with pagination |
| GET | /api/catalog/search | Search books |
| GET | /api/catalog/{book_id} | Get book details |
| GET | /api/catalog/categories | List categories |

### 6.2 Cart Endpoints

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | /api/cart | Get current cart | Optional |
| POST | /api/cart/items | Add item to cart | Optional |
| PUT | /api/cart/items/{id} | Update quantity | Optional |
| DELETE | /api/cart/items/{id} | Remove item | Optional |
| DELETE | /api/cart | Clear cart | Optional |

### 6.3 Checkout Endpoints (Auth Required)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/checkout/validate | Validate cart for checkout |
| POST | /api/checkout/shipping | Set shipping address |
| POST | /api/checkout/billing | Set billing/payment |
| POST | /api/checkout/complete | Complete order |
| GET | /api/checkout/confirmation/{id} | Get confirmation |

### 6.4 Customer Account Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/customers/register | Create account |
| GET | /api/customers/me | Get profile |
| PUT | /api/customers/me | Update profile |
| GET | /api/customers/me/orders | Order history |
| GET | /api/customers/me/orders/{id} | Order details |
| GET | /api/customers/me/addresses | Saved addresses |
| POST | /api/customers/me/addresses | Add address |

---

## 7. Request/Response Schemas

```python
# backend/app/schemas/customer.py

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime
from enum import Enum

class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class CartItemCreate(BaseModel):
    book_id: UUID
    quantity: int

class CartItemResponse(BaseModel):
    id: UUID
    book_id: UUID
    book_title: str
    book_isbn: str
    book_price: Decimal
    quantity: int
    line_total: Decimal
    available_quantity: int

class CartResponse(BaseModel):
    items: List[CartItemResponse]
    subtotal: Decimal
    estimated_tax: Decimal
    estimated_total: Decimal

class AddressCreate(BaseModel):
    name: str
    street: str
    city: str
    state: str
    zip_code: str
    country: str = "United States"

class CheckoutRequest(BaseModel):
    shipping_address: AddressCreate
    billing_address: Optional[AddressCreate] = None
    same_as_shipping: bool = True
    payment_token: str  # Tokenized payment from frontend

class OrderLineResponse(BaseModel):
    book_id: UUID
    book_title: str
    quantity: int
    unit_price: Decimal
    line_total: Decimal

class OrderResponse(BaseModel):
    id: UUID
    order_number: str
    status: OrderStatus
    line_items: List[OrderLineResponse]
    subtotal: Decimal
    shipping_cost: Decimal
    tax_amount: Decimal
    total: Decimal
    shipping_address: AddressCreate
    created_at: datetime
    estimated_delivery: Optional[datetime]

class CustomerRegister(BaseModel):
    email: EmailStr
    password: str
    first_name: str
    last_name: str
```

---

## 8. Cart Service Implementation

```python
# backend/app/services/cart_service.py

from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from uuid import UUID

class CartService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_or_create_cart(
        self, 
        session_id: Optional[str] = None,
        customer_id: Optional[UUID] = None
    ) -> Cart:
        """Get existing cart or create new one."""
        if customer_id:
            # Logged-in user - persistent cart
            cart = await self.db.execute(
                select(Cart).where(Cart.customer_id == customer_id)
            )
            cart = cart.scalar_one_or_none()
        elif session_id:
            # Guest user - session-based cart
            cart = await self.db.execute(
                select(Cart).where(Cart.session_id == session_id)
            )
            cart = cart.scalar_one_or_none()
        
        if not cart:
            cart = Cart(
                customer_id=customer_id,
                session_id=session_id
            )
            self.db.add(cart)
            await self.db.commit()
        
        return cart
    
    async def add_item(
        self, cart: Cart, book_id: UUID, quantity: int
    ) -> CartItem:
        # Check stock availability
        available = await self.check_availability(book_id)
        if quantity > available:
            raise InsufficientStockError(book_id, available)
        
        # Check if item already in cart
        existing = await self.get_cart_item(cart.id, book_id)
        if existing:
            existing.quantity += quantity
            if existing.quantity > available:
                existing.quantity = available
        else:
            book = await self.db.get(Book, book_id)
            existing = CartItem(
                cart_id=cart.id,
                book_id=book_id,
                quantity=quantity,
                unit_price=book.list_price
            )
            self.db.add(existing)
        
        await self.db.commit()
        return existing
    
    async def merge_carts(
        self, session_cart: Cart, customer_id: UUID
    ) -> Cart:
        """Merge guest cart into customer cart on login."""
        customer_cart = await self.get_or_create_cart(
            customer_id=customer_id
        )
        
        for item in session_cart.items:
            await self.add_item(
                customer_cart, item.book_id, item.quantity
            )
        
        # Delete session cart
        await self.db.delete(session_cart)
        await self.db.commit()
        
        return customer_cart
```

---

## 9. Order Processing

```python
class OrderService:
    async def create_order(
        self, db: AsyncSession,
        customer_id: UUID,
        checkout: CheckoutRequest
    ) -> OrderResponse:
        async with db.begin():
            # 1. Get cart and validate
            cart = await self.cart_service.get_cart(customer_id)
            if not cart.items:
                raise EmptyCartError()
            
            # 2. Validate stock for all items
            for item in cart.items:
                available = await self.check_stock(db, item.book_id)
                if available < item.quantity:
                    raise InsufficientStockError(item.book_id)
            
            # 3. Create order
            order = Order(
                customer_id=customer_id,
                status=OrderStatus.PENDING,
                shipping_address_id=await self.create_address(
                    checkout.shipping_address
                )
            )
            db.add(order)
            await db.flush()
            
            # 4. Create order lines and reserve inventory
            subtotal = Decimal("0.00")
            for item in cart.items:
                line = OrderLine(
                    order_id=order.id,
                    book_id=item.book_id,
                    quantity=item.quantity,
                    unit_price=item.unit_price
                )
                db.add(line)
                subtotal += item.quantity * item.unit_price
                
                # Reserve inventory
                await self.reserve_inventory(
                    db, item.book_id, item.quantity
                )
            
            # 5. Calculate totals
            order.subtotal = subtotal
            order.shipping_cost = self.calculate_shipping(checkout)
            order.tax_amount = self.calculate_tax(subtotal)
            order.total = (
                subtotal + order.shipping_cost + order.tax_amount
            )
            
            # 6. Process payment (external service)
            payment_result = await self.payment_service.charge(
                checkout.payment_token, order.total
            )
            if not payment_result.success:
                raise PaymentFailedError(payment_result.error)
            
            # 7. Generate order number
            order.order_number = await self.generate_order_number(db)
            order.status = OrderStatus.PROCESSING
            
            # 8. Clear cart
            await self.cart_service.clear_cart(customer_id)
            
            # 9. Send confirmation email
            await self.email_service.send_order_confirmation(order)
            
            await db.commit()
            return order
```

---

## 10. Admin Integration

Customer orders appear in Admin dashboard for processing:
- New orders queue with status "Processing"
- Same inventory and sales record logic as in-store
- Status updates trigger customer email notifications

---

## 11. Testing Requirements

| Test Case | Description | Type |
|-----------|-------------|------|
| CUST-001 | Browse catalog without login | Integration |
| CUST-002 | Add items to cart as guest | Integration |
| CUST-003 | Cart merges on login | Integration |
| CUST-004 | Checkout reserves inventory | Integration |
| CUST-005 | Order confirmation email sent | Integration |
| CUST-006 | Order history shows past orders | Integration |
| CUST-007 | Out-of-stock prevents add to cart | Unit |
| CUST-008 | Payment failure rolls back | Integration |

---

## Next Document: [08-API-REFERENCE.md](08-API-REFERENCE.md)
