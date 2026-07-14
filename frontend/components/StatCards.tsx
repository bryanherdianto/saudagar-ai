import type { InsightMetrics } from "@/lib/types";
import { rupiah } from "@/lib/format";
import { ArrowDownIcon, ArrowUpIcon, BoxIcon, ReceiptIcon } from "./icons";

function Stat({
  label,
  value,
  sub,
  icon,
  tone = "canvas",
}: {
  label: string;
  value: string;
  sub?: string;
  icon: React.ReactNode;
  tone?: "canvas" | "green" | "dark";
}) {
  const toneClass =
    tone === "dark"
      ? "bg-ink text-primary"
      : tone === "green"
        ? "bg-primary-pale text-ink"
        : "bg-canvas text-ink";
  return (
    <div className={`rounded-xl p-5 ${toneClass}`}>
      <div className="mb-3 flex items-center justify-between">
        <span className="text-sm font-semibold uppercase opacity-70">
          {label}
        </span>
        <span className="opacity-70">{icon}</span>
      </div>
      <p className="font-display text-3xl leading-none">{value}</p>
      {sub && <p className="mt-2 text-sm opacity-70">{sub}</p>}
    </div>
  );
}

export function StatCards({ metrics }: { metrics: InsightMetrics }) {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-4">
      <Stat
        label="Pemasukan"
        value={rupiah(metrics.income)}
        sub={`${metrics.days} hari terakhir`}
        icon={<ArrowUpIcon className="h-5 w-5" />}
        tone="green"
      />
      <Stat
        label="Pengeluaran"
        value={rupiah(metrics.expense)}
        sub={`${metrics.transaction_count} transaksi`}
        icon={<ArrowDownIcon className="h-5 w-5" />}
      />
      <Stat
        label="Laba Bersih"
        value={rupiah(metrics.profit)}
        sub={metrics.profit >= 0 ? "Untung" : "Perlu perhatian"}
        icon={<ReceiptIcon className="h-5 w-5" />}
        tone="dark"
      />
      <Stat
        label="Stok Menipis"
        value={`${metrics.low_stock.length} item`}
        sub={
          metrics.low_stock.length
            ? metrics.low_stock
                .slice(0, 2)
                .map((p) => p.name)
                .join(", ")
            : "Semua aman"
        }
        icon={<BoxIcon className="h-5 w-5" />}
      />
    </div>
  );
}
