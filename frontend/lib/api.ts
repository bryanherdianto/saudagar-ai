// Thin client for the Saudagar.ai FastAPI backend.
//
// Authenticates every request by attaching a Clerk session token. The token
// getter is configured at runtime by the <TokenGate /> client component
// (mounted inside <ClerkProvider>), so this module stays framework-agnostic.
// When no getter is configured (server-side or pre-mount), requests go out
// without an Authorization header - the backend then returns 401 unless auth
// is disabled via CLERK_ISSUER.

import type {
  CatalogResponse,
  ChatMessage,
  ChatResponse,
  CustomerServiceResponse,
  InsightResponse,
  Product,
  Store,
  StoreStatus,
  TelegramLinkResponse,
  TelegramStatus,
  Transaction,
  User,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

// --- Auth token plumbing ---------------------------------------------------
let _tokenGetter: () => Promise<string | null> = async () => null;

/**
 * Wire a Clerk `getToken()` (or any async token provider) into the API client.
 * Called once on mount by <TokenGate /> after Clerk hydrates.
 */
export function configureTokenGetter(getter: () => Promise<string | null>): void {
  _tokenGetter = getter;
}

/** Optional X-Store-Id header for multi-store switching (defaults to the
 * user's only store when not set). */
let _activeStoreId: number | null = null;

export function setActiveStoreId(id: number | null): void {
  _activeStoreId = id;
}

export function getActiveStoreId(): number | null {
  return _activeStoreId;
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const token = await _tokenGetter().catch(() => null);

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    // ngrok's free tier intercepts browser requests with an HTML warning
    // page unless this header is present. Harmless for other hosts.
    "ngrok-skip-browser-warning": "true",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  if (_activeStoreId != null) headers["X-Store-Id"] = String(_activeStoreId);

  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers,
    cache: "no-store",
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; ai_enabled: boolean }>("/api/health"),

  me: () => request<User>("/api/me"),

  // --- Store ---
  getStore: () => request<StoreStatus>("/api/store"),
  createStore: (body: {
    name: string;
    category?: string;
    currency?: string;
    default_language?: string;
    notes?: string;
  }) =>
    request<Store>("/api/store", {
      method: "POST",
      body: JSON.stringify(body),
    }),
  updateStore: (body: Partial<{
    name: string;
    category: string;
    currency: string;
    default_language: string;
    notes: string;
  }>) =>
    request<Store>("/api/store", {
      method: "PATCH",
      body: JSON.stringify(body),
    }),

  listProducts: () => request<Product[]>("/api/products"),

  listTransactions: (limit = 50) =>
    request<Transaction[]>(`/api/transactions?limit=${limit}`),

  insights: (days = 7) =>
    request<InsightResponse>(`/api/insights?days=${days}`),

  chat: (message: string, history: ChatMessage[] = []) =>
    request<ChatResponse>("/api/chat", {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),

  customerService: (message: string, history: ChatMessage[] = []) =>
    request<CustomerServiceResponse>("/api/cs", {
      method: "POST",
      body: JSON.stringify({ message, history }),
    }),

  generateCatalog: (
    product_name: string,
    details: string,
    languages: string[],
    tone = "persuasive",
  ) =>
    request<CatalogResponse>("/api/catalog/generate", {
      method: "POST",
      body: JSON.stringify({ product_name, details, languages, tone }),
    }),

  // --- Telegram integration ---
  telegramLink: () =>
    request<TelegramLinkResponse>("/api/integrations/telegram/link", {
      method: "POST",
    }),
  telegramStatus: () =>
    request<TelegramStatus>("/api/integrations/telegram/status"),
  telegramDisconnect: () =>
    request<{ disconnected: boolean }>("/api/integrations/telegram/link", {
      method: "DELETE",
    }),
};