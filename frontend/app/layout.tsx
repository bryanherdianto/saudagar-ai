import type { Metadata } from "next";
import { Manrope, Inter } from "next/font/google";
import "./globals.css";

// Inter — the brand's utility face (body, labels, UI).
const inter = Inter({
  variable: "--font-inter",
  subsets: ["latin"],
});

// Manrope — open-source stand-in for the proprietary heavy display face.
const manrope = Manrope({
  variable: "--font-manrope",
  subsets: ["latin"],
  weight: ["600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Saudagar.ai | Asisten Usaha Dagang Pintar",
  description:
    "Karyawan digital untuk UMKM: catat keuangan & stok lewat obrolan dan pahami bisnismu dengan insight AI.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="id"
      className={`${inter.variable} ${manrope.variable} h-full antialiased`}
    >
      <body className="min-h-full">{children}</body>
    </html>
  );
}
