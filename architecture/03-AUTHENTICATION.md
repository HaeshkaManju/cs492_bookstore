# Authentication & Authorization Architecture

**Related Stories:** US-003  
**Related Tasks:** S1-15 to S1-21

---

## 1. Overview

The authentication system provides:
- Unified login for all user types
- Role-based access control (RBAC)
- JWT-based stateless authentication
- Secure credential storage with bcrypt

---

## 2. Authentication Flow

```
┌──────────┐     POST /auth/login      ┌──────────────┐
│  Client  │ ─────────────────────────► │   FastAPI    │
│          │   { email, password }      │   Backend    │
└──────────┘                            └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │   Validate   │
                                        │  Credentials │
                                        └──────────────┘
                                               │
                                               ▼
                                        ┌──────────────┐
                                        │ Generate JWT │
                                        │   Token      │
                                        └──────────────┘
                                               │
                                               ▼
┌──────────┐     { access_token }       ┌──────────────┐
│  Client  │ ◄───────────────────────── │   FastAPI    │
│          │     expires_in: 3600       │   Backend    │
└──────────┘                            └──────────────┘
      │
      │ Store token
      ▼
┌──────────┐  Authorization: Bearer xxx  ┌──────────────┐
│  Client  │ ──────────────────────────► │  Protected   │
│          │   GET /api/inventory        │   Endpoint   │
└──────────┘                             └──────────────┘
```

---

## 3. User Roles (S1-15)

### 3.1 Role Definitions

| Role | Description | Interface Access |
|------|-------------|------------------|
| **admin** | Store owner/manager | Admin Portal (full access) |
| **employee** | Store staff | Admin Portal (limited) |
| **customer** | Public user | Customer Portal only |

### 3.2 Role-Based Access Control Matrix

| Resource/Action | Admin | Employee | Customer |
|-----------------|:-----:|:--------:|:--------:|
| **Inventory** | | | |
| View all inventory | ✓ | ✓ | Browse only |
| Add/Edit books | ✓ | ✓ | ✗ |
| Delete books | ✓ | ✗ | ✗ |
| View warehouse details | ✓ | ✓ | ✗ |
| **Sales** | | | |
| Process in-store sale | ✓ | ✓ | ✗ |
| View all sales records | ✓ | ✓ | ✗ |
| Generate reports | ✓ | ✓ | ✗ |
| **Purchase Orders** | | | |
| Create PO | ✓ | ✓ | ✗ |
| Submit PO | ✓ | ✗ | ✗ |
| Receive shipment | ✓ | ✓ | ✗ |
| **Users** | | | |
| Manage employees | ✓ | ✗ | ✗ |
| Manage customers | ✓ | ✓ | ✗ |
| **Customer Actions** | | | |
| Browse catalog | ✓ | ✓ | ✓ |
| Place order | ✓ | ✓ | ✓ |
| View own orders | ✓ | ✓ | Own only |

---

## 4. JWT Token Structure

### 4.1 Token Payload

```json
{
  "sub": "user-uuid-here",
  "email": "user@example.com",
  "role": "admin",
  "iat": 1714924800,
  "exp": 1714928400
}
```

| Claim | Description |
|-------|-------------|
| sub | User ID (UUID) |
| email | User email |
| role | User role for RBAC |
| iat | Issued at timestamp |
| exp | Expiration (1 hour from issue) |

### 4.2 Token Configuration

| Setting | Value | Rationale |
|---------|-------|-----------|
| Algorithm | HS256 | Symmetric, sufficient for single-service |
| Access Token TTL | 1 hour | Balance security/usability |
| Refresh Token TTL | 7 days | Extended session support |
| Secret Key | 256-bit random | Stored in environment variable |

---

## 5. Implementation Details

### 5.1 Password Hashing (S1-18)

```python
# backend/app/core/security.py

from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import jwt
from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm="HS256")
```

### 5.2 RBAC Middleware (S1-19)

```python
# backend/app/api/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.core.config import settings
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    # Fetch user from database
    user = await User.get(user_id)
    if user is None:
        raise credentials_exception
    return user

def require_role(allowed_roles: list[str]):
    async def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return current_user
    return role_checker
```

### 5.3 Route Protection (S1-20)

```python
# backend/app/api/routes/inventory.py

from fastapi import APIRouter, Depends
from app.api.dependencies import require_role

router = APIRouter(prefix="/inventory", tags=["inventory"])

@router.get("/")
async def list_inventory(
    user = Depends(require_role(["admin", "employee"]))
):
    # Only admin and employee can access
    pass

@router.delete("/{book_id}")
async def delete_book(
    book_id: str,
    user = Depends(require_role(["admin"]))  # Admin only
):
    pass
```

---

## 6. API Endpoints

### 6.1 Authentication Routes

| Method | Endpoint | Description | Task Ref |
|--------|----------|-------------|----------|
| POST | /auth/register | Create new user account | S1-16 |
| POST | /auth/login | Authenticate and get token | S1-17 |
| POST | /auth/refresh | Refresh access token | S1-17 |
| POST | /auth/logout | Invalidate refresh token | S1-17 |
| GET | /auth/me | Get current user profile | S1-17 |
| PUT | /auth/password | Change password | S1-18 |

### 6.2 Registration Flow (S1-16, S1-21)

```
Customer Registration (Public)
──────────────────────────────
POST /auth/register
{
  "email": "customer@example.com",
  "password": "SecurePass123",
  "first_name": "John",
  "last_name": "Doe"
}
→ Creates user with role="customer"
→ Returns access_token

Employee Creation (Admin Only)
──────────────────────────────
POST /admin/users
Authorization: Bearer <admin_token>
{
  "email": "employee@bookstore.com",
  "password": "TempPass123",
  "first_name": "Jane",
  "last_name": "Smith",
  "role": "employee"
}
→ Creates user with specified role
→ Returns user object (no token)
```

---

## 7. Security Controls

| Control | Implementation | Reference |
|---------|----------------|-----------|
| Password Storage | bcrypt with cost factor 12 | S1-18 |
| Token Expiry | 1-hour access, 7-day refresh | S1-17 |
| Input Validation | Pydantic schemas, server-side | DoD Security |
| SQL Injection | SQLAlchemy ORM, parameterized | DoD Security |
| XSS Prevention | Output encoding, CSP headers | DoD Security |
| CSRF | SameSite cookies for web | DoD Security |
| Rate Limiting | 100 req/min per IP (public) | DoD Security |
| Audit Logging | Log all auth events | DoD Security |
| HTTPS | TLS 1.3 required | DoD Security |

---

## 8. Session Management

### 8.1 Token Storage (Frontend)

| Context | Storage | Considerations |
|---------|---------|----------------|
| Admin Portal | httpOnly cookie | CSRF protection needed |
| Customer Portal | httpOnly cookie | CSRF protection needed |
| Mobile (future) | Secure storage | Platform-specific |

### 8.2 Logout Handling

- Access tokens are stateless (cannot be revoked)
- Refresh tokens stored in database, can be revoked
- On logout: delete refresh token from DB, clear client storage

---

## Next Document: [04-INVENTORY-MODULE.md](04-INVENTORY-MODULE.md)
