"use client";

import { useState } from "react";
import { api } from "@/lib/api";
import type { ChatMessage } from "@/lib/types";
import { Button } from "./ui";
import { HeadsetIcon, SendIcon } from "./icons";

type Bubble = ChatMessage & { upsell?: string | null };

// Simulates the auto customer-service + sales engine: play the buyer, watch
// the AI answer & upsell using the store's live catalog (RAG-grounded).
export function CsSimulator() {
  const [messages, setMessages] = useState<Bubble[]>([
    {
      role: "assistant",
      content:
        "Halo kak, selamat datang di Warung Bu Sari! Ada yang bisa dibantu? 😊",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

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
      const res = await api.customerService(trimmed, history);
      setMessages((m) => [
        ...m,
        { role: "assistant", content: res.reply, upsell: res.suggested_upsell },
      ]);
    } catch {
      setMessages((m) => [
        ...m,
        { role: "assistant", content: "Maaf, server sedang tidak tersedia." },
      ]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex h-full min-h-[420px] flex-col rounded-xl bg-canvas">
      <div className="flex items-center gap-3 border-b border-canvas-soft px-6 py-4">
        <span className="flex h-9 w-9 items-center justify-center rounded-full bg-accent-cyan/20 text-ink">
          <HeadsetIcon className="h-5 w-5" />
        </span>
        <div>
          <p className="font-display text-lg leading-none text-ink">
            Auto CS & Sales
          </p>
          <p className="text-xs text-mute">Jadilah pembeli — lihat AI melayani & up-selling</p>
        </div>
      </div>

      <div className="scroll-slim flex-1 space-y-3 overflow-y-auto px-6 py-4">
        {messages.map((m, i) => (
          <div key={i}>
            <div
              className={`flex ${m.role === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[85%] rounded-xl px-4 py-2.5 text-sm ${
                  m.role === "user"
                    ? "bg-ink text-canvas-soft"
                    : "bg-canvas-soft text-ink"
                }`}
              >
                {m.content}
              </div>
            </div>
            {m.upsell && (
              <div className="mt-1.5 flex justify-start">
                <div className="max-w-[85%] rounded-xl border border-dashed border-primary bg-primary-pale px-4 py-2 text-xs text-ink">
                  💡 Up-sell: {m.upsell}
                </div>
              </div>
            )}
          </div>
        ))}
        {loading && <p className="px-1 text-xs text-mute">mengetik…</p>}
      </div>

      <form
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
        className="flex items-center gap-2 border-t border-canvas-soft px-6 py-4"
      >
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Tanya sebagai pembeli… “nasi gorengnya ready kak?”"
          className="flex-1 rounded-md border border-ink/20 bg-canvas px-4 py-2.5 text-sm text-ink outline-none placeholder:text-mute focus:border-ink"
        />
        <Button type="submit" variant="dark" disabled={loading || !input.trim()}>
          <SendIcon className="h-4 w-4" />
        </Button>
      </form>
    </div>
  );
}
