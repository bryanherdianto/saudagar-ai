"use client";

import { useCallback, useEffect, useState } from "react";
import { useAuth } from "@clerk/nextjs";
import { api } from "@/lib/api";
import type { InsightResponse, Product, Store, Transaction } from "@/lib/types";
import { Sidebar } from "@/components/Sidebar";
import { StatCards } from "@/components/StatCards";
import { InsightPanel } from "@/components/InsightPanel";
import { ChatAssistant } from "@/components/ChatAssistant";
import { CatalogGenerator } from "@/components/CatalogGenerator";
import { TransactionsTable } from "@/components/TransactionsTable";
import { ProductsTable } from "@/components/ProductsTable";
import { StoreOnboarding } from "@/components/StoreOnboarding";
import { TelegramConnection } from "@/components/TelegramConnection";
import { AuthControls } from "@/components/AuthControls";
import { SectionTitle } from "@/components/ui";

type StoreState = "loading" | "none" | "ready";

export default function Dashboard() {
  const [insight, setInsight] = useState<InsightResponse | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [offline, setOffline] = useState(false);
  const [loading, setLoading] = useState(true);
  const [store, setStore] = useState<Store | null>(null);
  const [storeState, setStoreState] = useState<StoreState>("loading");
  const { isLoaded, isSignedIn } = useAuth();

  const loadData = useCallback(async () => {
    try {
      const status = await api.getStore();
      if (!status.has_store || !status.store) {
        setStore(null);
        setStoreState("none");
        setInsight(null);
        setProducts([]);
        setTransactions([]);
        setOffline(false);
        setLoading(false);
        return;
      }
      setStore(status.store);
      setStoreState("ready");

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
    // Wait for Clerk to hydrate before fetching - otherwise the request fires
    // without a session token and the backend rejects it with 401. Re-runs
    // when the sign-in state settles so data loads as soon as auth is ready.
    if (!isLoaded) return;
    // loadData is async and only calls setState after its awaits resolve, so
    // it cannot cascade renders synchronously — the rule is over-cautious here.
    // eslint-disable-next-line react-hooks/set-state-in-effect
    loadData();
  }, [isLoaded, isSignedIn, loadData]);

  // Live refresh for changes made outside this tab (e.g. a sale recorded via
  // the Telegram bot): re-fetch the cheap store data - products and
  // transactions, NOT insights (each insights call runs the LLM) - every 30s
  // while the tab is visible, and immediately when the tab regains focus.
  useEffect(() => {
    if (storeState !== "ready") return;
    const refreshLive = async () => {
      if (document.hidden) return;
      try {
        const [prods, txs] = await Promise.all([
          api.listProducts(),
          api.listTransactions(50),
        ]);
        setProducts(prods);
        setTransactions(txs);
      } catch {
        // Transient failure - the next tick or a manual reload will catch up.
      }
    };
    const id = setInterval(refreshLive, 30_000);
    window.addEventListener("focus", refreshLive);
    return () => {
      clearInterval(id);
      window.removeEventListener("focus", refreshLive);
    };
  }, [storeState]);

  if (storeState === "none") {
    return (
      <div className="flex min-h-screen">
        <Sidebar />
        <main className="scroll-slim min-w-0 flex-1 overflow-x-hidden">
          <header className="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-ink/10 bg-canvas/90 px-6 py-4 backdrop-blur">
            <div>
              <p className="text-xs font-semibold uppercase tracking-wider text-mute">
                Selamat datang
              </p>
              <h1 className="font-display text-xl text-ink">Mulai dengan toko</h1>
            </div>
            <AuthControls />
          </header>
          <div className="mx-auto max-w-300 px-6 py-10">
            <StoreOnboarding
              onCreated={() => {
                setStoreState("loading");
                setLoading(true);
                loadData();
              }}
            />
          </div>
        </main>
      </div>
    );
  }

  return (
    <div className="flex min-h-screen">
      <Sidebar />

      <main className="scroll-slim min-w-0 flex-1 overflow-x-hidden">
        {/* Top bar */}
        <header className="sticky top-0 z-10 flex items-center justify-between gap-4 border-b border-ink/10 bg-canvas/90 px-6 py-4 backdrop-blur">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-mute">
              {store ? store.name : "Toko"}
            </p>
            <h1 className="font-display text-xl text-ink">Dashboard</h1>
          </div>
          <AuthControls />
        </header>

        <div className="mx-auto max-w-300 space-y-10 px-6 py-8">
          {offline && (
            <div className="rounded-xl border border-negative/30 bg-negative-bg px-6 py-4 text-sm text-canvas">
              Tidak dapat terhubung ke backend di{" "}
              <code className="font-mono">
                {process.env.NEXT_PUBLIC_API_BASE_URL ??
                  "http://localhost:8000"}
              </code>
              . Jalankan server FastAPI, lalu refresh halaman.
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
              <div className="rounded-xl bg-primary-pale p-4 sm:p-7">
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

          {/* Integrasi */}
          <section id="integrasi" className="scroll-mt-20">
            <SectionTitle
              eyebrow="Aplikasi Terhubung"
              title="Integrasi"
            />
            <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
              <TelegramConnection />
            </div>
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