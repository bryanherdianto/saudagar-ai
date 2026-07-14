// Thin client for the Saudagar.ai FastAPI backend.

import type {
  CatalogResponse,
  ChatMessage,
  ChatResponse,
  CustomerServiceResponse,
  InsightResponse,
  Product,
  Transaction,
} from "./types";

export const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    cache: "no-store",
    ...init,
  });
  if (!res.ok) {
    const detail = await res.text().catch(() => res.statusText);
    throw new Error(`API ${res.status}: ${detail}`);
  }
  return res.json() as Promise<T>;
}

export const api = {
  health: () => request<{ status: string; ai_enabled: boolean }>("/api/health"),

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
};
