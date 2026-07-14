"use client";

import { useCallback, useEffect, useState } from "react";
import { api } from "@/lib/api";
import type { InsightResponse, Product, Transaction } from "@/lib/types";
import { Sidebar } from "@/components/Sidebar";
import { StatCards } from "@/components/StatCards";
import { InsightPanel } from "@/components/InsightPanel";
import { ChatAssistant } from "@/components/ChatAssistant";
import { CatalogGenerator } from "@/components/CatalogGenerator";
import { TransactionsTable } from "@/components/TransactionsTable";
import { ProductsTable } from "@/components/ProductsTable";
import { SectionTitle } from "@/components/ui";

export default function Dashboard() {
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
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
      <Sidebar />

      <main className="scroll-slim min-w-0 flex-1 overflow-x-hidden">
        {/* Top bar */}
        <header className="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-ink/10 bg-canvas/90 px-6 py-4 backdrop-blur">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-mute">
              Warung Bu Sari
            </p>
            <h1 className="font-display text-xl text-ink">Dashboard</h1>
          </div>
        </header>

        <div className="mx-auto max-w-300 space-y-10 px-6 py-8">
          {offline && (
            <div className="rounded-xl border border-negative/30 bg-negative-bg px-6 py-4 text-sm text-canvas">
              Tidak dapat terhubung ke backend di{" "}
              <code className="font-mono">
                {process.env.NEXT_PUBLIC_API_BASE_URL ??
                  "http://localhost:8000"}
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

          {/* Asisten */}
          <section id="asisten" className="scroll-mt-20">
            <SectionTitle
              eyebrow="Karyawan Digital"
              title="Ngobrol untuk catat transaksi"
            />
            <ChatAssistant onMutate={loadData} />
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
                  Jangkau pasar lebih luas
                </h3>
                <p className="mt-3 text-body">
                  Cukup masukkan nama produk, AI menuliskan deskripsi yang
                  menjual dalam berbagai bahasa.
                </p>
                <ul className="mt-5 space-y-2 text-sm text-ink">
                  {[
                    "Deskripsi persuasif, bukan sekadar daftar bahan",
                    "Nada tulisan menyesuaikan produkmu",
                    "Salin sekali klik ke marketplace",
                  ].map((t) => (
                    <li key={t} className="flex items-center gap-2">
                      <span className="h-2 w-2 shrink-0 rounded-full bg-primary" />
                      {t}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </section>

          {/* Stok */}
          <section id="stok" className="scroll-mt-20">
            <SectionTitle eyebrow="Data Toko" title="Katalog & stok" />
            <ProductsTable products={products} />
          </section>

          {/* Buku Kas */}
          <section id="ledger" className="scroll-mt-20">
            <SectionTitle eyebrow="Data Toko" title="Buku kas" />
            <TransactionsTable transactions={transactions} />
          </section>

          <footer className="border-t border-ink/10 pt-6 text-center text-xs text-mute">
            &copy; {new Date().getFullYear()}. Saudagar AI. All rights reserved.
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
