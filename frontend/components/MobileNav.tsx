"use client";

import { useState } from "react";
import Link from "next/link";
import { AuthControls } from "./AuthControls";

type NavItem = { href: string; label: string };

// Burger menu + dropdown panel for the site header on small screens.
export function MobileNav({ items }: { items: NavItem[] }) {
  const [open, setOpen] = useState(false);

  return (
    <div className="md:hidden">
      <button
        type="button"
        aria-label={open ? "Tutup menu" : "Buka menu"}
        aria-expanded={open}
        onClick={() => setOpen((prev) => !prev)}
        className="flex h-10 w-10 items-center justify-center rounded-xl text-ink transition-colors hover:bg-ink/5"
      >
        <svg
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          className="h-6 w-6"
        >
          {open ? (
            <path d="M6 6l12 12M18 6L6 18" />
          ) : (
            <path d="M4 7h16M4 12h16M4 17h16" />
          )}
        </svg>
      </button>

      {open && (
        <div className="absolute inset-x-0 top-full border-b border-ink/10 bg-canvas/95 backdrop-blur">
          <nav className="mx-auto flex max-w-300 flex-col gap-1 px-6 py-4">
            {items.map((item) => (
              <Link
                key={item.href}
                href={item.href}
                onClick={() => setOpen(false)}
                className="rounded-xl px-3 py-2.5 text-sm font-semibold text-body transition-colors hover:bg-ink/5 hover:text-ink"
              >
                {item.label}
              </Link>
            ))}
            <div className="mt-3 border-t border-ink/10 pt-4">
              <AuthControls />
            </div>
          </nav>
        </div>
      )}
    </div>
  );
}
