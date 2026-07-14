import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Tentang Kami | Saudagar.ai",
  description:
    "Saudagar.ai lahir dari keyakinan bahwa teknologi AI seharusnya melayani pelaku usaha kecil, bukan sebaliknya.",
};

const VALUES = [
  {
    title: "Sederhana dulu",
    body: "Teknologi paling baik adalah yang tidak membuat penggunanya merasa bodoh. Kami mengejar kesederhanaan di setiap sudut.",
    tone: "canvas" as const,
  },
  {
    title: "Bahasa penggunanya",
    body: "Bahasa Indonesia, istilah yang familiar, dan nada yang ramah. Bukan jargon korporat yang menjauhkan.",
    tone: "green" as const,
  },
  {
    title: "Harga yang masuk akal",
    body: "UMKM tidak punya anggaran enterprise. Layanan kami dirancang untuk terjangkau bahkan oleh warung pinggir jalan.",
    tone: "sage" as const,
  },
  {
    title: "Privasi adalah hak",
    body: "Data usaha Anda adalah milik Anda. Kami menjelaskan apa yang kami kumpulkan dan memberi Anda kendali penuh.",
    tone: "dark" as const,
  },
];

export default function About() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      <main>
        {/* Header band */}
        <section className="mx-auto max-w-300 px-6 py-16">
          <p className="text-xs font-semibold uppercase tracking-wider text-mute">
            Tentang Kami
          </p>
          <h1 className="mt-2 font-display text-4xl text-ink sm:text-5xl">
            Teknologi untuk yang berdagang
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-relaxed text-body">
            Saudagar.ai lahir dari keyakinan bahwa kecerdasan buatan seharusnya
            melayani pelaku usaha kecil. Kami membangun alat yang membuat
            pencatatan, mengangkat copywriting, dan menerjemahkan angka menjadi
            rekomendasi yang bisa ditindaklanjuti.
          </p>
        </section>

        {/* Founding story — dark card, mirrors InsightPanel */}
        <section className="mx-auto max-w-300 px-6 pb-16">
          <div className="rounded-xl bg-ink p-8 text-primary">
            <p className="text-xs font-semibold uppercase tracking-wider text-primary/80">
              Kisah Kami
            </p>
            <h2 className="mt-3 font-display text-2xl text-primary sm:text-3xl">
              Dari warung ke dashboard
            </h2>
            <p className="mt-4 leading-relaxed text-canvas-soft">
              Berawal dari obrolan dengan pemilik warung yang stres mencatat
              penjualan harian di buku bersampul. Kami bertanya: bagaimana jika
              pencatatan terasa seperti mengobrol? Dari pertanyaan itu tumbuh
              Saudagar.ai.
            </p>
          </div>
        </section>

        {/* Values grid */}
        <section className="bg-canvas-soft">
          <div className="mx-auto max-w-300 px-6 py-16">
            <div className="mb-8">
              <p className="text-xs font-semibold uppercase tracking-wider text-mute">
                Nilai-nilai Kami
              </p>
              <h2 className="font-display text-3xl text-ink">
                Yang kami pegang teguh
              </h2>
            </div>
            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              {VALUES.map((v) => (
                <div
                  key={v.title}
                  className={
                    "rounded-xl p-7 " +
                    (v.tone === "canvas"
                      ? "bg-canvas text-ink"
                      : v.tone === "green"
                        ? "bg-primary-pale text-ink"
                        : v.tone === "sage"
                          ? "bg-canvas-soft text-ink"
                          : "bg-ink text-primary")
                  }
                >
                  <h3
                    className={
                      "font-display text-xl " +
                      (v.tone === "dark" ? "text-primary" : "text-ink")
                    }
                  >
                    {v.title}
                  </h3>
                  <p
                    className={
                      "mt-2 text-sm leading-relaxed " +
                      (v.tone === "dark" ? "text-canvas-soft" : "text-body")
                    }
                  >
                    {v.body}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>

      <SiteFooter />
    </div>
  );
}
