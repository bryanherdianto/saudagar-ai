"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { CatalogItem } from "@/lib/types";
import { Button } from "./ui";
import { TagIcon } from "./icons";

const LANGUAGES = [
  { code: "id", label: "Indonesia" },
  { code: "en", label: "English" },
  { code: "ms", label: "Melayu" },
  { code: "zh", label: "中文" },
  { code: "ja", label: "日本語" },
  { code: "ar", label: "العربية" },
];

export function CatalogGenerator() {
  const [name, setName] = useState("");
  const [details, setDetails] = useState("");
  const [langs, setLangs] = useState<string[]>(["id", "en"]);
  const [items, setItems] = useState<CatalogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState<string | null>(null);

  function toggleLang(code: string) {
    setLangs((prev) =>
      prev.includes(code) ? prev.filter((c) => c !== code) : [...prev, code],
    );
  }

  async function generate() {
    if (!name.trim() || langs.length === 0 || loading) return;
    setLoading(true);
    setItems([]);
    try {
      const res = await api.generateCatalog(name.trim(), details.trim(), langs);
      setItems(res.items);
    } catch {
      setItems([
        {
          language: "id",
          title: "Gagal terhubung",
          description: "Pastikan backend berjalan lalu coba lagi.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  function copy(item: CatalogItem) {
    const text = `${item.title}\n\n${item.description}`;
    navigator.clipboard?.writeText(text);
    setCopied(item.language);
    setTimeout(() => setCopied(null), 1500);
  }

  return (
    <div className="rounded-xl bg-canvas p-6">
      <div className="mb-4 flex items-center gap-2">
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary-pale text-ink">
          <TagIcon className="h-5 w-5" />
        </span>
        <div>
          <p className="font-display text-lg leading-none text-ink">
            Katalog Multi-Bahasa
          </p>
          <p className="text-xs text-mute">Deskripsi produk siap tempel ke marketplace</p>
        </div>
      </div>

      <div className="space-y-3">
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Nama produk, mis. Keripik Singkong Pedas"
          className="w-full rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm text-ink outline-none placeholder:text-mute focus:border-ink"
        />
        <textarea
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          placeholder="Detail / keunggulan (opsional): pedas, renyah, kemasan 250gr…"
          rows={2}
          className="w-full resize-none rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm text-ink outline-none placeholder:text-mute focus:border-ink"
        />
        <div className="flex flex-wrap gap-2">
          {LANGUAGES.map((l) => {
            const active = langs.includes(l.code);
            return (
              <button
                key={l.code}
                onClick={() => toggleLang(l.code)}
                className={`rounded-full px-3 py-1 text-xs font-semibold transition-colors ${
                  active
                    ? "bg-primary text-on-primary"
                    : "border border-ink/15 text-body hover:bg-canvas-soft"
                }`}
              >
                {l.label}
              </button>
            );
          })}
        </div>
        <Button
          onClick={generate}
          disabled={loading || !name.trim() || langs.length === 0}
          className="w-full"
        >
          {loading ? "Membuat deskripsi…" : "Buat Deskripsi ✨"}
        </Button>
      </div>

      {items.length > 0 && (
        <div className="mt-5 space-y-3">
          {items.map((item) => (
            <div key={item.language} className="rounded-lg bg-canvas-soft p-4">
              <div className="mb-1 flex items-center justify-between">
                <span className="text-xs font-semibold uppercase text-mute">
                  {item.language}
                </span>
                <button
                  onClick={() => copy(item)}
                  className="text-xs font-semibold text-positive-deep hover:underline"
                >
                  {copied === item.language ? "Tersalin ✓" : "Salin"}
                </button>
              </div>
              <p className="font-semibold text-ink">{item.title}</p>
              <p className="mt-1 text-sm text-body">{item.description}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
