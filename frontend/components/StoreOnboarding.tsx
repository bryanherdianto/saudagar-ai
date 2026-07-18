"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import { Button } from "./ui";

/**
 * Inline onboarding form rendered in place of the dashboard when the
 * authenticated user has not created a store yet. On success, calls
 * `onCreated(store)` so the parent can refresh data.
 */
export function StoreOnboarding({
  onCreated,
}: {
  onCreated: (storeName: string) => void;
}) {
  const [name, setName] = useState("");
  const [category, setCategory] = useState("");
  const [currency, setCurrency] = useState("IDR");
  const [defaultLanguage, setDefaultLanguage] = useState("id");
  const [notes, setNotes] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || busy) return;
    setBusy(true);
    setError(null);
    try {
      const store = await api.createStore({
        name,
        category,
        currency,
        default_language: defaultLanguage,
        notes,
      });
      onCreated(store.name);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Gagal membuat toko.");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl rounded-xl bg-canvas p-8 shadow-sm">
      <h2 className="font-display text-2xl text-ink">Buat toko pertamamu</h2>
      <p className="mt-2 text-sm text-body">
        Satu pengguna hanya boleh memiliki satu toko. Lengkapi profil toko di
        bawah ini.
      </p>
      <form onSubmit={submit} className="mt-6 space-y-4">
        <Field label="Nama toko" required>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
            placeholder="Warung Bu Sari"
            className="w-full rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm outline-none focus:border-ink"
          />
        </Field>
        <div className="grid grid-cols-2 gap-4">
          <Field label="Kategori usaha">
            <input
              value={category}
              onChange={(e) => setCategory(e.target.value)}
              placeholder="Warung Makan"
              className="w-full rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm outline-none focus:border-ink"
            />
          </Field>
          <Field label="Mata uang">
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm outline-none focus:border-ink"
            >
              <option value="IDR">IDR</option>
              <option value="MYR">MYR</option>
              <option value="USD">USD</option>
            </select>
          </Field>
        </div>
        <Field label="Bahasa default">
          <select
            value={defaultLanguage}
            onChange={(e) => setDefaultLanguage(e.target.value)}
            className="w-full rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm outline-none focus:border-ink"
          >
            <option value="id">Bahasa Indonesia</option>
            <option value="en">English</option>
            <option value="ms">Bahasa Melayu</option>
          </select>
        </Field>
        <Field label="Catatan / aturan toko">
          <textarea
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={3}
            placeholder="Buka 08.00-21.00, selalu tawarkan es teh…"
            className="w-full rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm outline-none focus:border-ink"
          />
        </Field>

        {error && (
          <p className="rounded-md bg-negative-bg px-4 py-2 text-sm text-canvas">
            {error}
          </p>
        )}

        <Button type="submit" disabled={busy || !name.trim()}>
          {busy ? "Membuat…" : "Buat toko"}
        </Button>
      </form>
    </div>
  );
}

function Field({
  label,
  required,
  children,
}: {
  label: string;
  required?: boolean;
  children: React.ReactNode;
}) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-xs font-semibold uppercase tracking-wider text-mute">
        {label}
        {required ? " *" : ""}
      </span>
      {children}
    </label>
  );
}