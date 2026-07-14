import type { Metadata } from "next";
import { SiteHeader } from "@/components/SiteHeader";
import { SiteFooter } from "@/components/SiteFooter";

export const metadata: Metadata = {
  title: "Syarat & Ketentuan | Saudagar.ai",
  description:
    "Syarat dan ketentuan penggunaan layanan Saudagar.ai untuk pelaku usaha dagang.",
};

const SECTIONS = [
  {
    title: "1. Penerimaan syarat",
    body: "Dengan mengakses dan menggunakan Saudagar.ai, Anda menyetujui untuk terikat oleh syarat dan ketentuan ini. Jika Anda tidak menyetujui salah satu bagian, mohon untuk tidak menggunakan layanan kami.",
  },
  {
    title: "2. Akun & tanggung jawab",
    body: "Anda bertanggung jawab menjaga kerahasiaan kredensial akun serta seluruh aktivitas yang terjadi di dalamnya. Beritahu kami segera bila terjadi penggunaan yang tidak sah atas akun Anda.",
  },
  {
    title: "3. Penggunaan yang sah",
    body: "Anda setuju menggunakan layanan hanya untuk kegiatan usaha yang sah. Dilarang menyalahgunakan, mengganggu, atau mencoba mengakses bagian sistem di luar yang disediakan untuk Anda.",
  },
  {
    title: "4. Data & konten pengguna",
    body: "Hak atas data usaha yang Anda masukkan tetap menjadi milik Anda. Kami memprosesnya sebagaimana dijelaskan dalam Kebijakan Privasi, dan tidak akan menjual data Anda kepada pihak ketiga.",
  },
  {
    title: "5. Layanan & ketersediaan",
    body: "Kami berupaya menjaga layanan tetap tersedia, namun tidak menjamin layanan bebas hambatan tanpa gangguan. Fitur dapat berubah, diperbarui, atau dihentikan sewaktu-waktu dengan pemberitahuan sebelumnya.",
  },
  {
    title: "6. Perubahan syarat",
    body: "Syarat ini dapat diperbarui dari waktu ke waktu. Perubahan akan diumumkan di halaman ini, dan penggunaan berkelanjutan dianggap sebagai persetujuan terhadap versi terbaru.",
  },
];

export default function TermsOfUse() {
  return (
    <div className="min-h-screen">
      <SiteHeader />

      <main className="mx-auto max-w-300 px-6 py-16">
        <p className="text-xs font-semibold uppercase tracking-wider text-mute">
          Legal
        </p>
        <h1 className="mt-2 font-display text-4xl text-ink">Syarat &amp; Ketentuan</h1>
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