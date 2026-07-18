"use client";

// Telegram account-linking card.
//
// Flow: [Hubungkan Telegram] → backend mints a short-lived deep link →
// open t.me in a new tab → user taps Start in Telegram → the bot's webhook
// binds chat_id → store_id → this card polls /status until it flips to
// connected (or the link expires). No Telegram credentials ever touch the
// website; the deep-link token is the only secret and it dies in minutes.

import { useCallback, useEffect, useRef, useState } from "react";
import { api } from "@/lib/api";
import type { TelegramStatus } from "@/lib/types";
import { TelegramIcon } from "./icons";
import { Badge, Button, Card } from "./ui";

// Poll every 3s for up to 2 minutes after the deep link is opened.
const POLL_INTERVAL_MS = 3_000;
const POLL_TIMEOUT_MS = 120_000;

type Phase = "loading" | "idle" | "connecting" | "connected" | "unavailable";

export function TelegramConnection() {
  const [phase, setPhase] = useState<Phase>("loading");
  const [status, setStatus] = useState<TelegramStatus | null>(null);
  const [error, setError] = useState<string | null>(null);
  const pollTimer = useRef<ReturnType<typeof setInterval> | null>(null);

  const stopPolling = useCallback(() => {
    if (pollTimer.current) {
      clearInterval(pollTimer.current);
      pollTimer.current = null;
    }
  }, []);

  const refresh = useCallback(async (): Promise<TelegramStatus | null> => {
    try {
      const s = await api.telegramStatus();
      setStatus(s);
      return s;
    } catch (err) {
      // 503 = integration not configured on the server; anything else we
      // surface as a soft failure and leave the card in idle.
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("503")) setPhase("unavailable");
      return null;
    }
  }, []);

  // Initial status check on mount.
  useEffect(() => {
    let cancelled = false;
    (async () => {
      const s = await refresh();
      if (cancelled) return;
      if (s) setPhase(s.connected ? "connected" : "idle");
    })();
    return () => {
      cancelled = true;
      stopPolling();
    };
  }, [refresh, stopPolling]);

  const connect = useCallback(async () => {
    setError(null);
    try {
      const link = await api.telegramLink();
      // Open Telegram in a new tab; the user confirms there.
      window.open(link.deep_link, "_blank", "noopener,noreferrer");
      setPhase("connecting");

      // Poll until connected or the window closes on timeout.
      stopPolling();
      const startedAt = Date.now();
      pollTimer.current = setInterval(async () => {
        const s = await refresh();
        if (s?.connected) {
          stopPolling();
          setPhase("connected");
        } else if (Date.now() - startedAt > POLL_TIMEOUT_MS) {
          stopPolling();
          setPhase("idle");
          setError(
            "Belum terdeteksi. Jika sudah menekan Start di Telegram, muat ulang halaman ini.",
          );
        }
      }, POLL_INTERVAL_MS);
    } catch (err) {
      const msg = err instanceof Error ? err.message : String(err);
      if (msg.includes("503")) {
        setPhase("unavailable");
      } else {
        setError("Gagal membuat tautan. Coba lagi sebentar lagi.");
      }
    }
  }, [refresh, stopPolling]);

  const disconnect = useCallback(async () => {
    setError(null);
    try {
      await api.telegramDisconnect();
      setStatus({ connected: false, telegram_username: null, connected_at: null });
      setPhase("idle");
    } catch {
      setError("Gagal memutuskan koneksi. Coba lagi.");
    }
  }, []);

  if (phase === "unavailable") {
    return (
      <Card tone="sage">
        <CardHeader />
        <p className="mt-3 text-sm text-body">
          Integrasi Telegram belum aktif di server. Hubungi administrator untuk
          mengaktifkannya.
        </p>
      </Card>
    );
  }

  return (
    <Card tone="sage">
      <div className="flex items-start justify-between gap-4">
        <CardHeader />
        {phase === "connected" && <Badge tone="positive">Terhubung</Badge>}
      </div>

      {phase === "loading" && (
        <p className="mt-3 text-sm text-mute">Memeriksa status koneksi…</p>
      )}

      {phase === "idle" && (
        <div className="mt-3 space-y-4">
          <p className="text-sm text-body">
            Hubungkan akun Telegram untuk mencatat penjualan, mengecek stok, dan
            bertanya ke asisten langsung dari chat — data toko tetap satu dengan
            dashboard ini.
          </p>
          <Button onClick={connect}>
            <TelegramIcon className="h-5 w-5" />
            Hubungkan Telegram
          </Button>
        </div>
      )}

      {phase === "connecting" && (
        <div className="mt-3 space-y-2">
          <p className="text-sm text-body">
            Buka Telegram lalu tekan <strong>Start</strong> untuk konfirmasi.
            Halaman ini akan diperbarui otomatis.
          </p>
          <p className="text-xs text-mute">Menunggu konfirmasi dari Telegram…</p>
        </div>
      )}

      {phase === "connected" && (
        <div className="mt-3 space-y-4">
          <p className="text-sm text-body">
            Terhubung
            {status?.telegram_username ? (
              <>
                {" "}
                sebagai{" "}
                <span className="font-semibold text-ink">
                  @{status.telegram_username}
                </span>
              </>
            ) : null}
            . Kirim pesan ke bot untuk mencatat transaksi dari mana saja.
          </p>
          <Button variant="tertiary" onClick={disconnect}>
            Putuskan Koneksi
          </Button>
        </div>
      )}

      {error && <p className="mt-3 text-sm text-warning-deep">{error}</p>}
    </Card>
  );
}

function CardHeader() {
  return (
    <div className="flex items-center gap-3">
      <span className="flex h-10 w-10 items-center justify-center rounded-full bg-primary-pale text-ink">
        <TelegramIcon className="h-5 w-5" />
      </span>
      <div>
        <h3 className="font-display text-lg text-ink">Telegram</h3>
        <p className="text-xs text-mute">Asisten toko di aplikasi chat</p>
      </div>
    </div>
  );
}
