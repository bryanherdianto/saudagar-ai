"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { InsightResponse, Product, Transaction } from "@/lib/types";
import { Sidebar } from "@/components/Sidebar";
import { StatCards } from "@/components/StatCards";
import { InsightPanel } from "@/components/InsightPanel";
import { ChatAssistant } from "@/components/ChatAssistant";
import { CsSimulator } from "@/components/CsSimulator";
import { CatalogGenerator } from "@/components/CatalogGenerator";
import { TransactionsTable } from "@/components/TransactionsTable";
import { ProductsTable } from "@/components/ProductsTable";
import { SectionTitle } from "@/components/ui";

export default function Dashboard() {
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [aiEnabled, setAiEnabled] = useState(true);
  const [offline, setOffline] = useState(false);
  const [loading, setLoading] = useState(true);

  const loadData = useCallback(async () => {
    try {
      const [ins, prods, txs] = await Promise.all([
        api.insights(7),
        api.listProducts(),
        api.listTransactions(50),
      ]);
      setInsight(ins);
      setProducts(prods);
      setTransactions(txs);
      setAiEnabled(ins.ai_enabled);
      setOffline(false);
    } catch {
      setOffline(true);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
  }, [loadData]);

  return (
    <div className="flex min-h-screen">
      <Sidebar aiEnabled={aiEnabled} />

      <main className="scroll-slim min-w-0 flex-1 overflow-x-hidden">
        {/* Top bar */}
        <header className="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-ink/10 bg-canvas/90 px-6 py-4 backdrop-blur">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-mute">
              Warung Bu Sari
            </p>
            <h1 className="font-display text-xl text-ink">Dashboard</h1>
          </div>
          <div className="flex items-center gap-3">
            <span
              className={`hidden items-center gap-2 rounded-full px-3 py-1.5 text-xs font-semibold sm:inline-flex ${
                aiEnabled
                  ? "bg-primary-pale text-positive-deep"
                  : "bg-warning/20 text-warning-deep"
              }`}
            >
              <span
                className={`h-2 w-2 rounded-full ${aiEnabled ? "bg-positive" : "bg-warning"}`}
              />
              {aiEnabled ? "Gemini aktif" : "Mode demo"}
            </span>
          </div>
        </header>

        <div className="mx-auto max-w-300 space-y-10 px-6 py-8">
          {offline && (
            <div className="rounded-xl border border-negative/30 bg-negative-bg px-6 py-4 text-sm text-canvas">
              Tidak dapat terhubung ke backend di{" "}
              <code className="font-mono">
                {process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000"}
              </code>
              . Jalankan server FastAPI, lalu muat ulang halaman.
            </div>
          )}

          {/* Ringkasan */}
          <section id="ringkasan" className="scroll-mt-20 space-y-6">
            {insight ? (
              <>
                <InsightPanel insight={insight} />
                <StatCards metrics={insight.metrics} />
              </>
            ) : (
              <SkeletonBlock loading={loading} />
            )}
          </section>

          {/* Asisten + Auto CS */}
          <section id="asisten" className="scroll-mt-20">
            <SectionTitle
              eyebrow="Karyawan Digital"
              title="Ngobrol untuk catat & layani"
            />
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <ChatAssistant onMutate={loadData} />
              <div id="layanan" className="scroll-mt-20">
                <CsSimulator />
              </div>
            </div>
          </section>

          {/* Katalog */}
          <section id="katalog" className="scroll-mt-20">
            <SectionTitle
              eyebrow="Copywriting Otomatis"
              title="Katalog & ekspor multi-bahasa"
            />
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <CatalogGenerator />
              <div className="rounded-xl bg-primary-pale p-7">
                <h3 className="font-display text-2xl text-ink">
                  Jangkau pasar lebih luas 🌏
                </h3>
                <p className="mt-3 text-body">
                  Cukup masukkan nama produk, AI menuliskan deskripsi yang menjual
                  dalam berbagai bahasa — siap disalin ke Shopee, Tokopedia, atau
                  marketplace global.
                </p>
                <ul className="mt-5 space-y-2 text-sm text-ink">
                  {[
                    "Deskripsi persuasif, bukan sekadar daftar bahan",
                    "Nada tulisan menyesuaikan produkmu",
                    "Salin sekali klik ke marketplace",
                  ].map((t) => (
                    <li key={t} className="flex items-center gap-2">
                      <span className="flex h-5 w-5 items-center justify-center rounded-full bg-primary text-xs font-bold text-on-primary">
                        ✓
                      </span>
                      {t}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* Inventaris + ledger */}
          <section id="inventaris" className="scroll-mt-20">
            <SectionTitle eyebrow="Data Toko" title="Stok & buku kas" />
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <div>
                <h3 className="mb-3 text-sm font-semibold text-body">
                  Katalog & Stok
                </h3>
                <ProductsTable products={products} />
              </div>
              <div>
                <h3 className="mb-3 text-sm font-semibold text-body">
                  Transaksi Terbaru
                </h3>
                <TransactionsTable transactions={transactions} />
              </div>
            </div>
          </section>

          <footer className="border-t border-ink/10 pt-6 text-center text-xs text-mute">
            Saudagar.ai — Sistem Asisten Usaha Dagang Pintar · Next.js + FastAPI +
            LangChain + Gemini
          </footer>
        </div>
      </main>
    </div>
  );
}

function SkeletonBlock({ loading }: { loading: boolean }) {
  return (
    <div className="rounded-xl bg-canvas p-10 text-center text-sm text-mute">
      {loading ? "Memuat data toko…" : "Data belum tersedia."}
    </div>
  );
}
