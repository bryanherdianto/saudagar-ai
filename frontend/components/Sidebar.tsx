"use client";

import { BoxIcon, ChartIcon, ChatIcon, HeadsetIcon, TagIcon } from "./icons";

const NAV = [
  { id: "ringkasan", label: "Ringkasan", icon: ChartIcon },
  { id: "asisten", label: "Asisten", icon: ChatIcon },
  { id: "layanan", label: "Auto CS", icon: HeadsetIcon },
  { id: "katalog", label: "Katalog AI", icon: TagIcon },
  { id: "inventaris", label: "Stok & Ledger", icon: BoxIcon },
];

export function Sidebar({ aiEnabled }: { aiEnabled: boolean }) {
  return (
    <aside className="sticky top-0 hidden h-screen w-64 shrink-0 flex-col border-r border-ink/10 bg-canvas p-6 lg:flex">
      <div className="mb-8 flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-lg font-black text-on-primary">
          S
        </span>
        <span className="font-display text-xl text-ink">Saudagar.ai</span>
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

      <div className="rounded-xl bg-canvas-soft p-4">
        <div className="mb-1 flex items-center gap-2">
          <span
            className={`h-2 w-2 rounded-full ${aiEnabled ? "bg-positive" : "bg-warning"}`}
          />
          <span className="text-xs font-semibold text-ink">
            {aiEnabled ? "AI Aktif" : "Mode Demo"}
          </span>
        </div>
        <p className="text-xs text-mute">
          {aiEnabled
            ? "Gemini terhubung. Semua fitur AI aktif."
            : "Tambahkan GEMINI_API_KEY di backend untuk mengaktifkan AI penuh."}
        </p>
      </div>
    </aside>
  );
}
