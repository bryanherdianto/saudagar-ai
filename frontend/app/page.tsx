import Link from "next/link";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";
import { HeroVisual } from "@/components/HeroVisual";
import { ChatIcon, TagIcon, SparkIcon } from "@/components/icons";

const FEATURES = [
  {
    icon: ChatIcon,
    title: "Catat lewat obrolan",
    body: "Ceritakan penjualan atau pengeluaranmu, Saudagar mencatatnya secara otomatis. Tidak perlu repot buka buku kas.",
    tone: "canvas" as const,
  },
  {
    icon: TagIcon,
    title: "Katalog & copywriting AI",
    body: "Masukkan nama produk, AI menulis deskripsi persuasif dalam berbagai bahasa siap salin ke marketplace.",
    tone: "green" as const,
  },
  {
    icon: SparkIcon,
    title: "Insight bisnis cerdas",
    body: "Pahami produk terlaris, tren pendapatan, dan rekomendasi langkah berikutnya lewat narasi AI yang mudah dibaca.",
    tone: "sage" as const,
  },
];

const STEPS = [
  {
    title: "Ngobrol dengan asisten",
    body: 'Kirim pesan seperti chat: "Tadi jual 3 kopi susu, 25 ribu per gelas". Saudagar mencatat sebagai transaksi.',
  },
  {
    title: "Saudagar merapikan data",
    body: "Setiap pesan diubah menjadi stok, transaksi, dan katalog yang terstruktur.",
  },
  {
    title: "Pahami bisnismu",
    body: "Lihat ringkasan, narasi AI, dan rekomendasi langsung di dashboard. Ambil keputusan lebih cepat.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      {/* Hero — polarity-flipped dark band, mirrors InsightPanel */}
      <section className="relative overflow-hidden bg-ink text-primary">
        <HeroVisual />
        <div className="relative z-10 mx-auto max-w-300 px-6 py-20 sm:py-28">
          <p className="text-xs font-semibold uppercase tracking-wider text-primary/80">
            Asisten Usaha Dagang Pintar
          </p>
          <h1 className="mt-4 font-display text-4xl leading-tight sm:text-5xl">
            Karyawan digital untuk UMKM Indonesia
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-canvas-soft">
            Catat keuangan &amp; stok lewat obrolan, hasilkan katalog
            marketplace dalam sekali klik, dan pahami bisnismu dengan insight
            AI. Semua dalam satu tempat.
          </p>
          <div className="mt-8 flex flex-wrap gap-4">
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 text-base font-semibold text-on-primary transition-colors hover:bg-primary-active"
            >
              Masuk Dashboard
            </Link>
            <Link
              href="/about"
              className="inline-flex items-center justify-center rounded-xl border border-primary/40 px-6 py-3 text-base font-semibold text-primary transition-colors hover:bg-primary/10"
            >
              Pelajari lebih lanjut
            </Link>
          </div>
        </div>
      </section>

      {/* Fitur */}
      <section className="mx-auto max-w-300 px-6 py-16">
        <div className="mb-8">
          <p className="text-xs font-semibold uppercase tracking-wider text-mute">
            Fitur
          </p>
          <h2 className="font-display text-3xl text-ink">
            Semua yang butuh untuk jualan
          </h2>
        </div>
        <div className="grid grid-cols-1 gap-6 md:grid-cols-3">
          {FEATURES.map((f) => (
            <div
              key={f.title}
              className={
                "rounded-xl p-7 " +
                (f.tone === "canvas"
                  ? "bg-canvas text-ink"
                  : f.tone === "green"
                    ? "bg-primary-pale text-ink"
                    : "bg-canvas-soft text-ink")
              }
            >
              <f.icon className="h-7 w-7" />
              <h3 className="mt-4 font-display text-xl text-ink">{f.title}</h3>
              <p className="mt-2 text-sm leading-relaxed text-body">{f.body}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Cara kerja — numbered, mirrors InsightPanel recommendation list */}
      <section className="bg-canvas-soft">
        <div className="mx-auto max-w-300 px-6 py-16">
          <div className="mb-8">
            <p className="text-xs font-semibold uppercase tracking-wider text-mute">
              Cara Kerja
            </p>
            <h2 className="font-display text-3xl text-ink">
              Tiga langkah saja
            </h2>
          </div>
          <ol className="space-y-5">
            {STEPS.map((s, i) => (
              <li
                key={s.title}
                className="flex items-start gap-4 rounded-xl bg-canvas p-6"
              >
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-primary text-sm font-bold text-on-primary">
                  {i + 1}
                </span>
                <div>
                  <h3 className="font-display text-lg text-ink">{s.title}</h3>
                  <p className="mt-1 text-sm leading-relaxed text-body">
                    {s.body}
                  </p>
                </div>
              </li>
            ))}
          </ol>
        </div>
      </section>

      {/* Closing CTA — dark band */}
      <section className="bg-ink text-primary">
        <div className="mx-auto max-w-300 px-6 py-16">
          <div className="flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
            <div>
              <h2 className="font-display text-3xl">Siap mencatat jualanmu?</h2>
              <p className="mt-2 text-canvas-soft">
                Mulai gratis. Cukup obrolkan transaksi pertamamu.
              </p>
            </div>
            <Link
              href="/dashboard"
              className="inline-flex items-center justify-center rounded-xl bg-primary px-6 py-3 text-base font-semibold text-on-primary transition-colors hover:bg-primary-active"
            >
              Buka Dashboard
            </Link>
          </div>
        </div>
      </section>

      <SiteFooter />
    </div>
  );
}
