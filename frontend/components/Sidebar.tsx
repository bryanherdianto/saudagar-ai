"use client";

import {
  BoxIcon,
  ChartIcon,
  ChatIcon,
  ReceiptIcon,
  TagIcon,
  TelegramIcon,
} from "./icons";

const NAV = [
  { id: "ringkasan", label: "Ringkasan", icon: ChartIcon },
  { id: "asisten", label: "Asisten", icon: ChatIcon },
  { id: "katalog", label: "Katalog AI", icon: TagIcon },
  { id: "stok", label: "Stok", icon: BoxIcon },
  { id: "ledger", label: "Buku Kas", icon: ReceiptIcon },
  { id: "integrasi", label: "Integrasi", icon: TelegramIcon },
];

export function Sidebar() {
  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-ink/10 bg-canvas p-6 lg:flex">
      <div className="mb-8 flex items-center gap-2">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img src="/logo.svg" alt="Saudagar.ai" className="h-9 w-auto" />
        <span className="font-display ml-2 text-xl text-ink">Saudagar.ai</span>
      </div>

      <nav className="flex-1 space-y-1">
        {NAV.map(({ id, label, icon: Icon }) => (
          <a
            key={id}
            href={`#${id}`}
            className="flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold text-body transition-colors hover:bg-canvas-soft hover:text-ink"
          >
            <Icon className="h-5 w-5" />
            {label}
          </a>
        ))}
      </nav>
    </aside>
  );
}
