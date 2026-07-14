import Link from "next/link";

const FOOTER_LINKS = [
  { href: "/about", label: "Tentang Kami" },
  { href: "/terms-of-use", label: "Syarat & Ketentuan" },
  { href: "/privacy-policy", label: "Kebijakan Privasi" },
  { href: "/dashboard", label: "Dashboard" },
];

// Mirrors the dashboard footer treatment so every page closes consistently.
export function SiteFooter() {
  return (
    <footer className="border-t border-ink/10 px-6 pb-10 pt-8 text-sm text-mute">
      <div className="mx-auto flex max-w-300 flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <p>&copy; {new Date().getFullYear()}. Saudagar AI. All rights reserved.</p>
        <ul className="flex flex-wrap gap-x-6 gap-y-2">
          {FOOTER_LINKS.map((item) => (
            <li key={item.href}>
              <Link
                href={item.href}
                className="text-mute transition-colors hover:text-ink"
              >
                {item.label}
              </Link>
            </li>
          ))}
        </ul>
      </div>
    </footer>
  );
}