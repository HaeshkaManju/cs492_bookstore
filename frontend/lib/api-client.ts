/**
 * API Client for Bookstore Backend
 * =================================
 * 
 * Task: INT-S2-001
 * 
 * Provides typed API calls to the Flask backend.
 * Handles authentication, error handling, and response parsing.
 */

// Configuration
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000/api/v1';

// Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  pagination?: {
    total: number;
    page: number;
    per_page: number;
    pages: number;
    has_next?: boolean;
    has_prev?: boolean;
  };
}

export interface AuthTokens {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  role: 'admin' | 'employee' | 'customer';
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface Book {
  id: string;
  isbn?: string;
  title: string;
  author: string;
  publisher?: string;
  year_published?: number;
  description?: string;
  category?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  total_quantity?: number;
  lowest_price?: number;
  in_stock?: boolean;
}

export interface Inventory {
  id: string;
  book_id: string;
  warehouse_id: string;
  condition: number;
  condition_label: string;
  quantity: number;
  acquisition_cost: number;
  list_price: number;
  reorder_level: number;
  location_code?: string;
  book_title?: string;
  book_author?: string;
  warehouse_name?: string;
  is_low_stock?: boolean;
  created_at: string;
  updated_at: string;
}

export interface Warehouse {
  id: string;
  name: string;
  location?: string;
  capacity: number;
  is_active: boolean;
  total_items?: number;
  utilization?: number;
  created_at: string;
}

export interface Customer {
  id: string;
  user_id: string;
  email: string;
  first_name: string;
  last_name: string;
  company_name?: string;
  phone?: string;
  credit_terms: string;
  is_active: boolean;
  created_at: string;
  addresses?: Address[];
}

export interface Address {
  id: string;
  customer_id: string;
  address_type: 'billing' | 'shipping';
  street: string;
  city: string;
  state?: string;
  zip_code: string;
  country: string;
  is_primary: boolean;
}

export interface Invoice {
  id: string;
  invoice_number: string;
  customer_id: string;
  created_by: string;
  status: 'draft' | 'sent' | 'paid' | 'cancelled';
  subtotal: number;
  payment_terms?: string;
  notes?: string;
  sent_at?: string;
  paid_at?: string;
  created_at: string;
  updated_at: string;
  lines?: InvoiceLine[];
  customer?: Customer;
}

export interface InvoiceLine {
  id: string;
  invoice_id: string;
  line_type: string;
  description: string;
  quantity: number;
  unit_price?: number;
  line_total?: number;
  is_pending: boolean;
}

export interface PurchaseOrder {
  id: string;
  po_number: string;
  manufacturer_id: string;
  created_by: string;
  status: 'draft' | 'submitted' | 'confirmed' | 'shipped' | 'received' | 'cancelled';
  total: number;
  notes?: string;
  created_at: string;
  updated_at: string;
  lines?: POLine[];
  manufacturer?: Manufacturer;
}

export interface POLine {
  id: string;
  po_id: string;
  description: string;
  quantity: number;
  unit_cost: number;
  line_total: number;
  received_quantity?: number;
}

export interface Manufacturer {
  id: string;
  name: string;
  contact_name?: string;
  email?: string;
  phone?: string;
  address?: string;
  is_active: boolean;
}

// Token Management
const TOKEN_KEY = 'bookstore_access_token';
const REFRESH_TOKEN_KEY = 'bookstore_refresh_token';

export function getAccessToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function getRefreshToken(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
}

export function setTokens(tokens: AuthTokens): void {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_TOKEN_KEY, tokens.refresh_token);
}

export function clearTokens(): void {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
}

// API Client Class
class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<ApiResponse<T>> {
    const url = `${this.baseUrl}${endpoint}`;
    
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
      ...options.headers,
    };

    const token = getAccessToken();
    if (token) {
      (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
      });

      const data = await response.json();

      if (!response.ok) {
        // Try to refresh token if unauthorized
        if (response.status === 401 && getRefreshToken()) {
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry the request with new token
            return this.request(endpoint, options);
          }
        }
        
        return {
          success: false,
          error: data.error || { code: 'ERROR', message: 'Request failed' },
        };
      }

      return data;
    } catch (error) {
      return {
        success: false,
        error: {
          code: 'NETWORK_ERROR',
          message: error instanceof Error ? error.message : 'Network error',
        },
      };
    }
  }

  private async refreshToken(): Promise<boolean> {
    const refreshToken = getRefreshToken();
    if (!refreshToken) return false;

    try {
      const response = await fetch(`${this.baseUrl}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      });

      if (response.ok) {
        const data = await response.json();
        if (data.success && data.data) {
          setTokens(data.data);
          return true;
        }
      }
    } catch {
      // Ignore refresh errors
    }

    clearTokens();
    return false;
  }

  // GET request
  async get<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'GET' });
  }

  // POST request
  async post<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // PUT request
  async put<T>(endpoint: string, body?: unknown): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  // DELETE request
  async delete<T>(endpoint: string): Promise<ApiResponse<T>> {
    return this.request<T>(endpoint, { method: 'DELETE' });
  }

  // =========================================================================
  // Auth API
  // =========================================================================

  async login(email: string, password: string): Promise<ApiResponse<AuthTokens & { user: User }>> {
    const response = await this.post<AuthTokens & { user: User }>('/auth/login', { email, password });
    if (response.success && response.data) {
      setTokens(response.data);
    }
    return response;
  }

  async register(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
  }): Promise<ApiResponse<AuthTokens & { user: User }>> {
    const response = await this.post<AuthTokens & { user: User }>('/auth/register', data);
    if (response.success && response.data) {
      setTokens(response.data);
    }
    return response;
  }

  async logout(): Promise<void> {
    await this.post('/auth/logout');
    clearTokens();
  }

  async getCurrentUser(): Promise<ApiResponse<User>> {
    return this.get<User>('/auth/me');
  }

  // =========================================================================
  // Books API
  // =========================================================================

  async getBooks(params?: {
    q?: string;
    category?: string;
    in_stock_only?: boolean;
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<Book[]>> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.category) searchParams.append('category', params.category);
    if (params?.in_stock_only !== undefined) searchParams.append('in_stock_only', String(params.in_stock_only));
    if (params?.page) searchParams.append('page', String(params.page));
    if (params?.per_page) searchParams.append('per_page', String(params.per_page));
    
    const query = searchParams.toString();
    return this.get<Book[]>(`/books${query ? `?${query}` : ''}`);
  }

  async getBook(id: string, includeInventory = true): Promise<ApiResponse<Book>> {
    return this.get<Book>(`/books/${id}?include_inventory=${includeInventory}`);
  }

  async createBook(data: Partial<Book>): Promise<ApiResponse<Book>> {
    return this.post<Book>('/books', data);
  }

  async updateBook(id: string, data: Partial<Book>): Promise<ApiResponse<Book>> {
    return this.put<Book>(`/books/${id}`, data);
  }

  async deleteBook(id: string): Promise<ApiResponse<void>> {
    return this.delete<void>(`/books/${id}`);
  }

  async getCategories(): Promise<ApiResponse<string[]>> {
    return this.get<string[]>('/books/categories');
  }

  // =========================================================================
  // Inventory API
  // =========================================================================

  async getInventory(params?: {
    q?: string;
    warehouse_id?: string;
    min_condition?: number;
    in_stock_only?: boolean;
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<Inventory[]>> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.warehouse_id) searchParams.append('warehouse_id', params.warehouse_id);
    if (params?.min_condition) searchParams.append('min_condition', String(params.min_condition));
    if (params?.in_stock_only !== undefined) searchParams.append('in_stock_only', String(params.in_stock_only));
    if (params?.page) searchParams.append('page', String(params.page));
    if (params?.per_page) searchParams.append('per_page', String(params.per_page));
    
    const query = searchParams.toString();
    return this.get<Inventory[]>(`/inventory${query ? `?${query}` : ''}`);
  }

  async getInventoryItem(id: string): Promise<ApiResponse<Inventory>> {
    return this.get<Inventory>(`/inventory/${id}`);
  }

  async addInventory(data: {
    book_id: string;
    warehouse_id: string;
    condition: number;
    quantity: number;
    acquisition_cost: number;
    list_price: number;
    reorder_level?: number;
    location_code?: string;
  }): Promise<ApiResponse<Inventory>> {
    return this.post<Inventory>('/inventory', data);
  }

  async adjustInventory(id: string, delta: number, reason?: string): Promise<ApiResponse<Inventory>> {
    return this.post<Inventory>(`/inventory/${id}/adjust`, { delta, reason });
  }

  async getLowStock(): Promise<ApiResponse<Inventory[]>> {
    return this.get<Inventory[]>('/inventory/low-stock');
  }

  async getInventoryValue(): Promise<ApiResponse<{ acquisition_value: string; list_value: string }>> {
    return this.get('/inventory/value');
  }

  async getWarehouses(): Promise<ApiResponse<Warehouse[]>> {
    return this.get<Warehouse[]>('/warehouses');
  }

  async createWarehouse(data: { name: string; location?: string; capacity?: number }): Promise<ApiResponse<Warehouse>> {
    return this.post<Warehouse>('/warehouses', data);
  }

  // =========================================================================
  // Invoices/Sales API
  // =========================================================================

  async getInvoices(params?: {
    q?: string;
    status?: string;
    customer_id?: string;
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<Invoice[]>> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.customer_id) searchParams.append('customer_id', params.customer_id);
    if (params?.page) searchParams.append('page', String(params.page));
    if (params?.per_page) searchParams.append('per_page', String(params.per_page));
    
    const query = searchParams.toString();
    return this.get<Invoice[]>(`/invoices${query ? `?${query}` : ''}`);
  }

  async getInvoice(id: string): Promise<ApiResponse<Invoice>> {
    return this.get<Invoice>(`/invoices/${id}`);
  }

  async createInvoice(data: {
    customer_id: string;
    created_by: string;
    payment_terms?: string;
    notes?: string;
  }): Promise<ApiResponse<Invoice>> {
    return this.post<Invoice>('/invoices', data);
  }

  async addInvoiceLine(invoiceId: string, data: {
    inventory_id?: string;
    request_id?: string;
    description?: string;
    quantity?: number;
    unit_price?: number;
  }): Promise<ApiResponse<InvoiceLine>> {
    return this.post<InvoiceLine>(`/invoices/${invoiceId}/lines`, data);
  }

  async removeInvoiceLine(invoiceId: string, lineId: string): Promise<ApiResponse<void>> {
    return this.delete<void>(`/invoices/${invoiceId}/lines/${lineId}`);
  }

  async sendInvoice(id: string): Promise<ApiResponse<Invoice>> {
    return this.post<Invoice>(`/invoices/${id}/send`);
  }

  async markInvoicePaid(id: string): Promise<ApiResponse<Invoice>> {
    return this.post<Invoice>(`/invoices/${id}/pay`);
  }

  async cancelInvoice(id: string): Promise<ApiResponse<Invoice>> {
    return this.post<Invoice>(`/invoices/${id}/cancel`);
  }

  async getInvoiceStats(): Promise<ApiResponse<Record<string, unknown>>> {
    return this.get('/invoices/stats');
  }

  // =========================================================================
  // Purchase Orders API
  // =========================================================================

  async getPurchaseOrders(params?: {
    q?: string;
    status?: string;
    manufacturer_id?: string;
    page?: number;
    per_page?: number;
  }): Promise<ApiResponse<PurchaseOrder[]>> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.status) searchParams.append('status', params.status);
    if (params?.manufacturer_id) searchParams.append('manufacturer_id', params.manufacturer_id);
    if (params?.page) searchParams.append('page', String(params.page));
    if (params?.per_page) searchParams.append('per_page', String(params.per_page));
    
    const query = searchParams.toString();
    return this.get<PurchaseOrder[]>(`/purchase-orders${query ? `?${query}` : ''}`);
  }

  async getPurchaseOrder(id: string): Promise<ApiResponse<PurchaseOrder>> {
    return this.get<PurchaseOrder>(`/purchase-orders/${id}`);
  }

  async createPurchaseOrder(data: {
    manufacturer_id: string;
    created_by: string;
    notes?: string;
  }): Promise<ApiResponse<PurchaseOrder>> {
    return this.post<PurchaseOrder>('/purchase-orders', data);
  }

  async addPOLine(poId: string, data: {
    description: string;
    quantity: number;
    unit_cost: number;
    book_id?: string;
    isbn?: string;
    expected_condition?: number;
  }): Promise<ApiResponse<POLine>> {
    return this.post<POLine>(`/purchase-orders/${poId}/lines`, data);
  }

  async submitPO(id: string): Promise<ApiResponse<PurchaseOrder>> {
    return this.post<PurchaseOrder>(`/purchase-orders/${id}/submit`);
  }

  async confirmPO(id: string): Promise<ApiResponse<PurchaseOrder>> {
    return this.post<PurchaseOrder>(`/purchase-orders/${id}/confirm`);
  }

  async receivePO(id: string): Promise<ApiResponse<PurchaseOrder>> {
    return this.post<PurchaseOrder>(`/purchase-orders/${id}/receive`);
  }

  async cancelPO(id: string): Promise<ApiResponse<PurchaseOrder>> {
    return this.post<PurchaseOrder>(`/purchase-orders/${id}/cancel`);
  }

  async getManufacturers(): Promise<ApiResponse<Manufacturer[]>> {
    return this.get<Manufacturer[]>('/manufacturers');
  }

  async createManufacturer(data: {
    name: string;
    contact_name?: string;
    email?: string;
    phone?: string;
    address?: string;
  }): Promise<ApiResponse<Manufacturer>> {
    return this.post<Manufacturer>('/manufacturers', data);
  }

  // =========================================================================
  // Customers API
  // =========================================================================

  async getCustomers(params?: {
    q?: string;
    active_only?: boolean;
  }): Promise<ApiResponse<Customer[]>> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.active_only !== undefined) searchParams.append('active_only', String(params.active_only));
    
    const query = searchParams.toString();
    return this.get<Customer[]>(`/customers${query ? `?${query}` : ''}`);
  }

  async getCustomer(id: string): Promise<ApiResponse<Customer>> {
    return this.get<Customer>(`/customers/${id}`);
  }

  async createCustomer(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    company_name?: string;
    phone?: string;
    credit_terms?: string;
  }): Promise<ApiResponse<Customer>> {
    return this.post<Customer>('/customers', data);
  }

  async updateCustomer(id: string, data: Partial<Customer>): Promise<ApiResponse<Customer>> {
    return this.put<Customer>(`/customers/${id}`, data);
  }

  async addCustomerAddress(customerId: string, data: Omit<Address, 'id' | 'customer_id'>): Promise<ApiResponse<Address>> {
    return this.post<Address>(`/customers/${customerId}/addresses`, data);
  }

  // =========================================================================
  // Users API (Admin)
  // =========================================================================

  async getUsers(params?: {
    q?: string;
    role?: string;
    active_only?: boolean;
  }): Promise<ApiResponse<User[]>> {
    const searchParams = new URLSearchParams();
    if (params?.q) searchParams.append('q', params.q);
    if (params?.role) searchParams.append('role', params.role);
    if (params?.active_only !== undefined) searchParams.append('active_only', String(params.active_only));
    
    const query = searchParams.toString();
    return this.get<User[]>(`/users${query ? `?${query}` : ''}`);
  }

  async createUser(data: {
    email: string;
    password: string;
    first_name: string;
    last_name: string;
    role?: string;
  }): Promise<ApiResponse<User>> {
    return this.post<User>('/users', data);
  }

  async updateUser(id: string, data: Partial<User>): Promise<ApiResponse<User>> {
    return this.put<User>(`/users/${id}`, data);
  }

  async deleteUser(id: string): Promise<ApiResponse<void>> {
    return this.delete<void>(`/users/${id}`);
  }
}

// Export singleton instance
export const api = new ApiClient();
export default api;
