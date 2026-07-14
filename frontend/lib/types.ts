// Shared types mirroring the FastAPI response schemas.

export interface Product {
  id: number;
  name: string;
  sku: string | null;
  category: string;
  unit: string;
  price: number;
  cost: number;
  stock: number;
  low_stock_threshold: number;
  description: string;
  updated_at: string;
}

export interface Transaction {
  id: number;
  kind: "income" | "expense";
  category: string;
  description: string;
  amount: number;
  quantity: number;
  unit: string;
  product_name: string;
  source: string;
  created_at: string;
}

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatResponse {
  reply: string;
  actions: string[];
  ai_enabled: boolean;
}

export interface InsightMetrics {
  days: number;
  income: number;
  expense: number;
  profit: number;
  transaction_count: number;
  top_products: { name: string; revenue: number }[];
  low_stock: { name: string; stock: number; unit: string }[];
}

export interface InsightResponse {
  headline: string;
  narrative: string;
  recommendations: string[];
  metrics: InsightMetrics;
  ai_enabled: boolean;
}

export interface CatalogItem {
  language: string;
  title: string;
  description: string;
}

export interface CatalogResponse {
  items: CatalogItem[];
  ai_enabled: boolean;
}

export interface CustomerServiceResponse {
  reply: string;
  suggested_upsell: string | null;
  ai_enabled: boolean;
}
