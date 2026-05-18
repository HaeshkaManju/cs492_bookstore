# Bookstore Application - Complete Setup Guide

This guide provides step-by-step instructions for setting up the development environment from scratch. Follow every step in order.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Step 1: Install Python](#step-1-install-python)
3. [Step 2: Install Node.js](#step-2-install-nodejs)
4. [Step 3: Install pnpm](#step-3-install-pnpm)
5. [Step 4: Clone the Repository](#step-4-clone-the-repository)
6. [Step 5: Set Up the Backend (Flask)](#step-5-set-up-the-backend-flask)
7. [Step 6: Set Up the Frontend (Next.js)](#step-6-set-up-the-frontend-nextjs)
8. [Step 7: Seed the Database](#step-7-seed-the-database)
9. [Step 8: Run the Application](#step-8-run-the-application)
10. [Step 9: Verify Everything Works](#step-9-verify-everything-works)
11. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, you need:

- **Windows 10 or later** (this guide is written for Windows)
- **Internet connection** (for downloading packages)
- **Administrator access** (for installing Node.js)
- **A terminal** (PowerShell or Windows Terminal)

> **Note for macOS/Linux users:** The commands differ slightly. Replace `winget` with `brew install` (macOS) or `sudo apt install` (Ubuntu). Path separators use `/` instead of `\`.

---

## Step 1: Install Python

The backend is built with Python 3.12+. If you already have Python installed, verify it:

```powershell
python --version
```

You should see `Python 3.12.x` or higher.

### If Python is not installed:

**Option A: Using winget (recommended)**
```powershell
winget install Python.Python.3.12
```

**Option B: Manual download**
1. Go to https://www.python.org/downloads/
2. Download Python 3.12.x (or latest 3.x)
3. Run the installer
4. **IMPORTANT:** Check the box that says "Add Python to PATH"
5. Click "Install Now"

### Verify installation:

Close and reopen your terminal, then run:
```powershell
python --version
pip --version
```

Both commands should return version numbers without errors.

---

## Step 2: Install Node.js

The frontend is built with Next.js, which requires Node.js.

### What is Node.js?

Node.js is a JavaScript runtime that allows you to run JavaScript outside of a web browser. Next.js (our frontend framework) requires it. npm (Node Package Manager) comes bundled with Node.js and is used to install JavaScript libraries.

### Installation Steps

**Option A: Using winget (recommended, Windows 10+)**
```powershell
winget install OpenJS.NodeJS.LTS
```

This installs the Long Term Support (LTS) version, which is the stable, recommended version.

**Option B: Manual download**
1. Go to https://nodejs.org/
2. Click the **LTS** (Long Term Support) button to download
3. Run the installer (.msi file)
4. Accept the license agreement
5. Keep all default options (including "Automatically install the necessary tools")
6. Click Install
7. Click Finish

### What gets installed:

| Component | Description |
|-----------|-------------|
| **Node.js** | JavaScript runtime (the engine that runs JavaScript) |
| **npm** | Node Package Manager (installs JavaScript libraries) |
| **Location** | Default: `C:\Program Files\nodejs\` |
| **PATH** | Automatically added to system PATH |

### Verify installation:

**IMPORTANT:** Close your terminal and open a new one after installing Node.js. The PATH changes only take effect in new terminal sessions.

```powershell
node --version
npm --version
```

You should see output like:
```
v24.15.0
11.12.1
```

### If `node` or `npm` is not found after installation:

1. Close ALL terminal windows
2. Open a brand new PowerShell window
3. If still not found, refresh your PATH manually:
   ```powershell
   $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
   ```
4. Try `node --version` again
5. If still not found, check if Node.js was added to your PATH:
   - Right-click "This PC" > Properties > Advanced system settings > Environment Variables
   - Look for `C:\Program Files\nodejs` in the "Path" variable under "System variables"
   - If it's missing, add it manually

---

## Step 3: Install pnpm

Our project uses **pnpm** as its package manager (instead of npm directly). pnpm is faster and more disk-efficient.

### What is pnpm?

pnpm stands for "performant npm". It's a drop-in replacement for npm that:
- Uses less disk space (shared package store)
- Installs packages faster
- Creates stricter dependency trees (no phantom dependencies)

### Installation:

```powershell
npm install -g pnpm
```

The `-g` flag installs it globally so you can use it from any directory.

### Verify installation:

```powershell
pnpm --version
```

You should see a version number like `11.1.3` or higher.

---

## Step 4: Clone the Repository

If you haven't already cloned the repository:

```powershell
cd C:\Users\YourName\Documents\GitHub
git clone https://github.com/your-org/cs492_bookstore.git
cd cs492_bookstore
```

If you already have the repository, navigate to it:

```powershell
cd C:\Users\DataA\Documents\GitHub\cs492_bookstore
```

---

## Step 5: Set Up the Backend (Flask)

The backend is a Flask (Python) REST API server.

### 5a. Navigate to the backend directory:

```powershell
cd bookstore
```

### 5b. Create a virtual environment (recommended):

A virtual environment keeps Python packages isolated from your system Python.

```powershell
python -m venv venv
```

### 5c. Activate the virtual environment:

```powershell
# Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Windows Command Prompt:
.\venv\Scripts\activate.bat

# macOS/Linux:
source venv/bin/activate
```

> **Note:** You'll see `(venv)` in your terminal prompt when the virtual environment is active. You need to activate it every time you open a new terminal for the backend.

> **Troubleshooting:** If you get a PowerShell execution policy error:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
> ```
> Then try activating again.

### 5d. Install Python dependencies:

```powershell
pip install -r requirements.txt
```

This installs Flask, SQLAlchemy, Flask-CORS, PyJWT, and all other required packages.

**Expected packages include:**

| Package | Purpose |
|---------|---------|
| Flask | Web framework |
| Flask-SQLAlchemy | Database ORM |
| Flask-Migrate | Database migrations |
| Flask-Login | Session authentication |
| Flask-WTF | Form handling & CSRF |
| Flask-CORS | Cross-origin resource sharing |
| PyJWT | JSON Web Token authentication |
| bcrypt | Password hashing |

### 5e. Verify backend setup:

```powershell
python -c "from app import create_app; app = create_app('development'); print('Backend setup OK')"
```

You should see `Backend setup OK`.

---

## Step 6: Set Up the Frontend (Next.js)

The frontend is a Next.js (React) application.

### 6a. Open a NEW terminal window

(Keep the backend terminal open if you activated a venv there)

### 6b. Navigate to the frontend directory:

```powershell
cd C:\Users\DataA\Documents\GitHub\cs492_bookstore\frontend
```

### 6c. Install JavaScript dependencies:

```powershell
pnpm install
```

This reads `pnpm-lock.yaml` and installs all required packages into `node_modules/`.

**Expected output:**
```
Packages: +186
Done in 14.7s using pnpm v11.1.3
```

### 6d. Configure the API URL:

The frontend needs to know where the backend API is running.

A `.env.local` file should already exist with:
```
NEXT_PUBLIC_API_URL=http://localhost:5000/api/v1
```

If it doesn't exist, create it:
```powershell
Set-Content -Path .env.local -Value "NEXT_PUBLIC_API_URL=http://localhost:5000/api/v1"
```

### 6e. Verify frontend setup:

```powershell
pnpm build
```

This should complete with output showing all routes:
```
Route (app)
┌ ○ /
├ ○ /admin
├ ○ /admin/orders
├ ○ /admin/sales
├ ○ /customer
├ ○ /customer/cart
├ ○ /login
└ ○ /register
```

---

## Step 7: Seed the Database

The seed script creates database tables and populates them with test data.

### From the bookstore directory:

```powershell
cd C:\Users\DataA\Documents\GitHub\cs492_bookstore\bookstore
python seed_database.py
```

### What this creates:

- **3 test user accounts** (admin, employee, customer)
- **8 rare books** (classic literature, first editions)
- **2 warehouses** (Main Warehouse, Climate Controlled Vault)
- **7 inventory entries** (with prices and conditions)
- **3 manufacturers/suppliers**
- **1 customer profile** with billing address

### Expected output:

```
============================================================
DATABASE SEED SCRIPT
============================================================

Creating database tables...
Creating test users...
  Created: admin@bookstore.com / admin (Admin)
  Created: employee@bookstore.com / employee (Employee)
  Created: customer@bookstore.com / customer (Customer)
  ...

DATABASE SEEDED SUCCESSFULLY!
============================================================
```

---

## Step 8: Run the Application

The application has **two parts** that must run simultaneously:

| Part | Technology | Port | What it does |
|------|-----------|------|-------------|
| **Backend** | Flask (Python) | 5000 | REST API, database, authentication |
| **Frontend** | Next.js (React) | 3000 | Web UI with navigation, pages, forms |

> **IMPORTANT:** `run.py` starts the **backend API only**. It shows a status page at http://localhost:5000 - that is NOT the app. The app with navigation is at http://localhost:3000.

### Quick Start (Both Servers at Once)

Double-click `start-dev.bat` in the project root folder. This opens two terminal windows automatically - one for each server.

### Manual Start (Two Terminals)

You need **two terminal windows** - one for the backend and one for the frontend.

### Terminal 1: Start the Backend

```powershell
cd C:\Users\DataA\Documents\GitHub\cs492_bookstore\bookstore

# If using a virtual environment:
.\venv\Scripts\Activate.ps1

python run.py
```

Expected output:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
```

The backend API is now running at **http://localhost:5000**

> **What you see at http://localhost:5000:** A status page showing "Bookstore API" with database connection status. This is normal - it's just the API server. The actual app interface is on port 3000.

### Terminal 2: Start the Frontend

```powershell
cd C:\Users\DataA\Documents\GitHub\cs492_bookstore\frontend
pnpm dev
```

Expected output:
```
 ▲ Next.js 16.2.6
 - Local: http://localhost:3000
```

The frontend is now running at **http://localhost:3000**

> **OPEN THIS URL IN YOUR BROWSER:** http://localhost:3000 - This is where you'll see the homepage with navigation, sign-in, and the full application interface.

---

## Step 9: Verify Everything Works

### 9a. Open your browser and test these URLs:

| URL | What you should see |
|-----|---------------------|
| http://localhost:3000 | **THE APP** - Homepage with "Discover Rare Books", featured books, Sign In button |
| http://localhost:5000 | Backend API status page (just shows server status, not the app) |
| http://localhost:3000/login | Login page with demo credentials |
| http://localhost:3000/register | Customer registration form |
| http://localhost:3000/admin | Admin inventory dashboard |
| http://localhost:3000/admin/sales | Sales records page |
| http://localhost:3000/admin/orders | Purchase orders page |
| http://localhost:3000/customer | Customer book catalog |
| http://localhost:3000/customer/cart | Shopping cart page |

### 9b. Test the API directly:

```powershell
# List books (public, no auth needed)
Invoke-RestMethod -Uri "http://localhost:5000/api/v1/books" -Method GET

# Login as admin
$body = '{"email":"admin@bookstore.com","password":"admin"}'
Invoke-RestMethod -Uri "http://localhost:5000/api/v1/auth/login" -Method POST -ContentType "application/json" -Body $body
```

### 9c. Test login in the browser:

1. Go to http://localhost:3000/login
2. Enter `admin@bookstore.com` and `admin`
3. Click "Sign In"
4. You should be redirected to the Admin dashboard

---

## Test Accounts

> **SECURITY WARNING:** These accounts use simple passwords for testing convenience. Never use this configuration in production!

| Role | Email | Password | Access Level |
|------|-------|----------|--------------|
| **Admin** | admin@bookstore.com | admin | Full system access |
| **Employee** | employee@bookstore.com | employee | Limited admin (sales, inventory view) |
| **Customer** | customer@bookstore.com | customer | Customer portal only |

### Role Permissions:

- **Admin:** Full access to all features, manage inventory, sales, purchase orders, users
- **Employee:** View inventory, create sales, view purchase orders, cannot manage users
- **Customer:** Browse catalog, add to cart, checkout, manage own profile

---

## Troubleshooting

### Problem: `python` is not recognized

**Solution:** Python is not in your PATH.
1. Reinstall Python and check "Add Python to PATH"
2. Or manually add `C:\Users\YourName\AppData\Local\Programs\Python\Python312` to your PATH

### Problem: `node` is not recognized

**Solution:** Node.js is not in your PATH.
1. Close ALL terminal windows and open a new one
2. If still broken, refresh PATH manually:
   ```powershell
   $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
   ```
3. Check if `C:\Program Files\nodejs` is in your system PATH (System Properties > Environment Variables)

### Problem: `pnpm` is not recognized

**Solution:** pnpm was installed globally but the npm bin directory isn't in PATH.
```powershell
npm install -g pnpm
```
Or refresh your PATH (same as Node.js above).

### Problem: `ModuleNotFoundError: No module named 'app'`

**Solution:** You're not running from the `bookstore/` directory.
```powershell
cd C:\Users\DataA\Documents\GitHub\cs492_bookstore\bookstore
python run.py
```

### Problem: `ModuleNotFoundError: No module named 'flask_cors'`

**Solution:** Missing Python package. Install all requirements:
```powershell
pip install -r requirements.txt
```

### Problem: Frontend shows "Using offline data"

**Solution:** The backend API is not running. Start it in another terminal:
```powershell
cd bookstore
python run.py
```
The frontend automatically falls back to sample data when the API is unavailable.

### Problem: CSRF token missing on API calls

**Solution:** This should not happen in the current setup (API is exempt from CSRF). If it does, make sure you're using the API at `/api/v1/` endpoints, not form submission endpoints.

### Problem: Database is empty / no test data

**Solution:** Run the seed script:
```powershell
cd bookstore
python seed_database.py
```

### Problem: Port 5000 or 3000 is already in use

**Solution:**
```powershell
# Find what's using the port
netstat -ano | findstr :5000
netstat -ano | findstr :3000

# Kill the process (replace PID with the number from above)
taskkill /PID <PID> /F
```

---

## Quick Reference

### Starting the application (two terminals needed):

```powershell
# OR just double-click: start-dev.bat  (starts both automatically)

# Terminal 1 - Backend (API, port 5000)
cd bookstore
.\venv\Scripts\Activate.ps1    # If using venv
python run.py

# Terminal 2 - Frontend (App UI, port 3000)
cd frontend
pnpm dev
```

> **Remember:** Open http://localhost:3000 in your browser - that's the app. Port 5000 is just the API.

### Stopping the application:

Press `Ctrl+C` in each terminal window.

### Resetting the database:

```powershell
cd bookstore
python seed_database.py
# Type "yes" when prompted
```

### Running tests:

```powershell
cd bookstore
python run_tests.py
# or
pytest tests/ -v
```

---

## Architecture Overview

```
Browser (http://localhost:3000)
    │
    ▼
┌─────────────────────────────┐
│   Next.js Frontend (React)  │  Port 3000
│   - Pages & Components      │
│   - API Client (lib/)       │
│   - Auth Context (lib/)     │
└──────────────┬──────────────┘
               │ HTTP requests
               ▼
┌─────────────────────────────┐
│   Flask Backend (REST API)  │  Port 5000
│   - /api/v1/* endpoints     │
│   - JWT Authentication      │
│   - Business Services       │
│   - Repositories            │
└──────────────┬──────────────┘
               │ SQLAlchemy ORM
               ▼
┌─────────────────────────────┐
│   SQLite Database           │  File: bookstore_dev.db
│   - Users, Books, Inventory │
│   - Invoices, POs, etc.    │
└─────────────────────────────┘
```
