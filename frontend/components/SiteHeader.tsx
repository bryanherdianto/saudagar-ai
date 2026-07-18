import Link from "next/link";
import { AuthControls } from "./AuthControls";

const NAV = [
  { href: "/", label: "Beranda" },
  { href: "/about", label: "Tentang" },
  { href: "/terms-of-use", label: "Syarat" },
  { href: "/privacy-policy", label: "Privasi" },
];

// Marketing top nav - sticky, canvas-backed, mirrors the dashboard header
// treatment (border-b + backdrop-blur) so the whole site feels cohesive.
export function SiteHeader() {
  return (
    <header className="sticky top-0 z-50 border-b border-ink/10 bg-canvas/90 backdrop-blur">
      <div className="mx-auto flex max-w-300 items-center justify-between gap-4 px-6 py-4">
        <Link href="/" className="flex items-center gap-2">
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img src="/logo.svg" alt="Saudagar.ai" className="h-8 w-auto" />
          <span className="font-display ml-1 text-lg text-ink">
            Saudagar.ai
          </span>
        </Link>

        <nav className="flex items-center gap-6">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className="text-sm font-semibold text-body transition-colors hover:text-ink"
            >
              {item.label}
            </Link>
          ))}
          <AuthControls />
        </nav>
      </div>
    </header>
  );
}
