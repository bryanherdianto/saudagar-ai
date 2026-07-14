import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Kebijakan Privasi | Saudagar.ai",
  description:
    "Kebijakan privasi Saudagar.ai: data apa yang kami kumpulkan, bagaimana kami menggunakannya, dan hak Anda atas data tersebut.",
};

const SECTIONS = [
  {
    title: "1. Data yang kami kumpulkan",
    body: "Kami mengumpulkan informasi yang Anda berikan secara langsung serta data teknis dasar untuk menjaga layanan tetap berjalan.",
  },
  {
    title: "2. Bagaimana kami menggunakannya",
    body: "Data usaha Anda digunakan untuk menjalankan fitur pencatatan, menghasilkan insight dan rekomendasi AI, menyusun katalog, serta meningkatkan kualitas layanan. Kami tidak menjual data Anda kepada pihak ketiga.",
  },
  {
    title: "3. Penyimpanan & keamanan",
    body: "Data disimpan selama akun Anda aktif dan dienkripsi saat transit. Kami menerapkan kontrol akses yang wajar, namun tidak ada sistem yang sepenuhnya terjamin.",
  },
  {
    title: "4. Berbagi dengan pihak ketiga",
    body: "Kami hanya berbagi data bila diperlukan untuk menjalankan infrastruktur (mis. penyedia hosting, model AI) dan diwajibkan oleh hukum. Pihak ketiga tersebut terikat menjaga kerahasiaan data Anda.",
  },
  {
    title: "5. Hak Anda",
    body: "Anda berhak mengakses, memperbaiki, menghapus, dan mengekspor data usaha Anda. Permintaan dapat dikirim melalui kontak di bawah. Hapus akun berarti penghapusan data terkait dalam jangka waktu yang wajar.",
  },
];

export default function PrivacyPolicy() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      <main className="mx-auto max-w-300 px-6 py-16">
        <p className="text-xs font-semibold uppercase tracking-wider text-mute">
          Legal
        </p>
        <h1 className="mt-2 font-display text-4xl text-ink">Kebijakan Privasi</h1>
        <p className="mt-3 text-sm text-mute">
          Terakhir diperbarui: 14 Juli 2026
        </p>

        <div className="mt-10 space-y-8">
          {SECTIONS.map((s) => (
            <section key={s.title} className="rounded-xl bg-canvas p-6">
              <h2 className="font-display text-xl text-ink">{s.title}</h2>
              <p className="mt-2 text-sm leading-relaxed text-body">{s.body}</p>
            </section>
          ))}
        </div>
      </main>

      <SiteFooter />
    </div>
  );
}