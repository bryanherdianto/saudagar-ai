"use client";

import { useRef, useState } from "react";
import { api } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import { Button } from "./ui";
import { ChatIcon, SendIcon } from "./icons";

const SUGGESTIONS = [
  "Laku 15 porsi nasi goreng ayam",
  "Beli telur 2 kg harganya 55 ribu",
  "Stok es teh manis berapa?",
  "Ringkasan penjualan minggu ini",
];

type Bubble = ChatMessage & { actions?: string[] };

// The "karyawan digital" chat
export function ChatAssistant({ onMutate }: { onMutate?: () => void }) {
  const [messages, setMessages] = useState<Bubble[]>([
    {
      role: "assistant",
      content:
        'Halo! Saya Saudagar.ai, karyawan digitalmu. Cerita saja transaksinya, nanti saya catat. Contoh: "Hari ini laku 15 porsi nasi goreng ayam, lalu beli telur 2 kg 55 ribu."',
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  async function send(text: string) {
    const trimmed = text.trim();
    if (!trimmed || loading) return;

    const history: ChatMessage[] = messages.map(({ role, content }) => ({
      role,
      content,
    }));
    setMessages((m) => [...m, { role: "user", content: trimmed }]);
    setInput("");
    setLoading(true);

    try {
      const res = await api.chat(trimmed, history);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, actions: res.actions },
      ]);
      if (res.actions.length > 0) onMutate?.();
    } catch {
      setMessages((m) => [
        ...m,
        {
          role: "assistant",
          content:
            "Maaf, tidak bisa terhubung ke server. Pastikan backend berjalan di " +
            (process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000") +
            ".",
        },
      ]);
    } finally {
      setLoading(false);
      requestAnimationFrame(() => {
        scrollRef.current?.scrollTo({
          top: scrollRef.current.scrollHeight,
          behavior: "smooth",
        });
      });
    }
  }

  return (
    <div className="flex h-full min-h-130 flex-col rounded-xl bg-canvas">
      <div className="flex items-center gap-3 border-b border-canvas-soft px-3 sm:px-6 py-4">
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-on-primary">
          <ChatIcon className="h-5 w-5" />
        </span>
        <div>
          <p className="font-display text-lg leading-none text-ink">
            Asisten Saudagar
          </p>
          <p className="text-xs text-mute pt-1">
            Catat keuangan & stok dari obrolan
          </p>
        </div>
      </div>

      <div
        ref={scrollRef}
        className="scroll-slim flex-1 space-y-4 overflow-y-auto px-3 sm:px-6 py-5"
      >
        {messages.map((m, i) => (
          <div
            key={i}
            className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
          >
            <div
              className={`max-w-[85%] rounded-xl px-4 py-3 text-sm leading-relaxed ${
                m.role === "user"
                  ? "bg-ink text-canvas-soft"
                  : "bg-canvas-soft text-ink"
              }`}
            >
              <p className="whitespace-pre-wrap">{m.content}</p>
              {m.actions && m.actions.length > 0 && (
                <div className="mt-2 space-y-1 border-t border-ink/10 pt-2">
                  {m.actions.map((a, j) => (
                    <p
                      key={j}
                      className="flex items-start gap-1.5 text-xs text-positive-deep"
                    >
                      {a}
                    </p>
                  ))}
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex justify-start">
            <div className="rounded-xl bg-canvas-soft px-4 py-3 text-sm text-mute">
              <span className="inline-flex gap-1">
                <span className="animate-bounce">●</span>
                <span className="animate-bounce [animation-delay:0.15s]">
                  ●
                </span>
                <span className="animate-bounce [animation-delay:0.3s]">●</span>
              </span>
            </div>
          </div>
        )}
      </div>

      <div className="border-t border-canvas-soft px-3 sm:px-6 py-4">
        <div className="mb-3 flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              disabled={loading}
              className="rounded-full border border-ink/15 px-3 py-1 text-xs text-body transition-colors hover:bg-canvas-soft disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="flex items-center gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Tulis pesan..."
            className="min-w-0 flex-1 rounded-md border border-ink/20 bg-canvas px-4 py-3 text-sm text-ink outline-none placeholder:text-mute focus:border-ink"
          />
          <Button type="submit" disabled={loading || !input.trim()}>
            <SendIcon className="h-4 w-4" />
          </Button>
        </form>
      </div>
    </div>
  );
}
