// Locale-aware formatting helpers (Indonesian Rupiah + relative dates).

export function rupiah(value: number): string {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    maximumFractionDigits: 0,
  }).format(value);
}

export function compactRupiah(value: number): string {
  if (Math.abs(value) >= 1_000_000)
    return `Rp${(value / 1_000_000).toFixed(1)}jt`;
  if (Math.abs(value) >= 1_000) return `Rp${Math.round(value / 1_000)}rb`;
  return `Rp${Math.round(value)}`;
}

export function relativeTime(iso: string): string {
  const then = new Date(iso).getTime();
  const diffMs = Date.now() - then;
  const mins = Math.round(diffMs / 60000);
  if (mins < 1) return "baru saja";
  if (mins < 60) return `${mins} menit lalu`;
  const hrs = Math.round(mins / 60);
  if (hrs < 24) return `${hrs} jam lalu`;
  const days = Math.round(hrs / 24);
  return `${days} hari lalu`;
}
