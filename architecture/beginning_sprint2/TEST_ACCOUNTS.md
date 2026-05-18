# Test Accounts for Prototype

This document contains the test accounts for the bookstore prototype system. These accounts are created by the `seed_database.py` script for development and testing purposes.

> **SECURITY WARNING**: These accounts use simple passwords for testing convenience. Never use this configuration in production!

---

## Test Accounts

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| **Admin** | admin@bookstore.com | admin | Full system access |
| **Employee** | employee@bookstore.com | employee | Limited admin (sales, inventory view) |
| **Customer** | customer@bookstore.com | customer | Customer portal only |

---

## Role Permissions

### Admin
- Full access to all features
- Manage inventory (add, edit, delete books)
- Manage sales and invoices
- Create and manage purchase orders
- Manage users and employees
- Access all reports

### Employee
- View inventory
- Create and manage sales
- View purchase orders
- Cannot manage users
- Cannot delete inventory

### Customer
- Browse book catalog
- Add items to cart
- Checkout and purchase
- View order history
- Manage own profile and addresses

---

## How to Set Up Test Accounts

1. Navigate to the bookstore directory:
   ```bash
   cd bookstore
   ```

2. Run the seed script:
   ```bash
   python seed_database.py
   ```

3. The script will:
   - Create the database tables
   - Create the three test users
   - Add sample books, inventory, and warehouses
   - Add sample manufacturers

---

## Running the Application

### Backend (Flask API)
```bash
cd bookstore
pip install -r requirements.txt
python seed_database.py  # First time only
python run.py
```
API runs at: http://localhost:5000

### Frontend (Next.js)
```bash
cd frontend
pnpm install
pnpm dev
```
App runs at: http://localhost:3000

---

## API Endpoints for Authentication

### Login
```
POST /api/v1/auth/login
Content-Type: application/json

{
    "email": "admin@bookstore.com",
    "password": "admin"
}
```

### Register (Customer only)
```
POST /api/v1/auth/register
Content-Type: application/json

{
    "email": "newuser@example.com",
    "password": "securepassword",
    "first_name": "New",
    "last_name": "User"
}
```

### Get Current User
```
GET /api/v1/auth/me
Authorization: Bearer <access_token>
```

---

## Sample Data Included

The seed script creates:

- **8 rare books** including first editions and signed copies
- **2 warehouses** (Main Warehouse and Climate Controlled Vault)
- **7 inventory entries** with varying conditions and prices
- **3 manufacturers/suppliers** for purchase orders
- **1 customer profile** with billing address

---

## Quick Test URLs

After starting both servers:

| URL | Description |
|-----|-------------|
| http://localhost:3000 | Home page (portal selection) |
| http://localhost:3000/admin | Admin dashboard |
| http://localhost:3000/customer | Customer catalog |
| http://localhost:3000/login | Login page |
| http://localhost:3000/register | Registration page |
| http://localhost:5000/api/v1/books | Books API (public) |
| http://localhost:5000/api/v1/inventory | Inventory API (public) |
