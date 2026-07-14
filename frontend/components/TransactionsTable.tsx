import type { Transaction } from "@/lib/types";
import { rupiah, dateTime } from "@/lib/format";
import { ArrowDownIcon, ArrowUpIcon } from "./icons";

export function TransactionsTable({
  transactions,
}: {
  transactions: Transaction[];
}) {
  if (transactions.length === 0) {
    return (
      <div className="rounded-xl bg-canvas p-10 text-center text-sm text-mute">
        Belum ada transaksi. Catat lewat asisten di sebelah!
      </div>
    );
  }

  return (
    <div className="overflow-hidden rounded-xl bg-canvas">
      <table className="w-full text-left text-sm">
        <thead className="sticky top-0 bg-canvas-soft text-xs uppercase tracking-wide text-mute">
          <tr>
            <th className="px-5 py-3 font-semibold">Transaksi</th>
            <th className="px-5 py-3 font-semibold">Kategori</th>
            <th className="px-5 py-3 text-right font-semibold">Nilai</th>
            <th className="px-5 py-3 text-right font-semibold">Waktu</th>
          </tr>
        </thead>
        <tbody>
          {transactions.map((t) => {
            const income = t.kind === "income";
            return (
              <tr
                key={t.id}
                className="border-b border-canvas-soft last:border-0"
              >
                <td className="px-5 py-3">
                  <div className="flex items-center gap-3">
                    <span
                      className={`flex h-8 w-8 shrink-0 items-center justify-center rounded-full ${
                        income
                          ? "bg-primary-pale text-positive-deep"
                          : "bg-negative-bg text-canvas"
                      }`}
                    >
                      {income ? (
                        <ArrowUpIcon className="h-4 w-4" />
                      ) : (
                        <ArrowDownIcon className="h-4 w-4" />
                      )}
                    </span>
                    <div>
                      <p className="font-medium text-ink">
                        {t.product_name || t.description || "Transaksi"}
                      </p>
                      {t.quantity > 0 && (
                        <p className="text-xs text-mute">
                          {t.quantity} {t.unit}
                        </p>
                      )}
                    </div>
                  </div>
                </td>
                <td className="px-5 py-3 text-body capitalize">{t.category}</td>
                <td
                  className={`px-5 py-3 text-right font-semibold ${
                    income ? "text-positive" : "text-negative"
                  }`}
                >
                  {income ? "+" : "−"}
                  {rupiah(t.amount)}
                </td>
                <td className="px-5 py-3 text-right text-xs text-mute">
                  {dateTime(t.created_at)}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
