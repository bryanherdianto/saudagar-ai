import type { Product } from "@/lib/types";
import { rupiah } from "@/lib/format";
import { Badge } from "./ui";

export function ProductsTable({ products }: { products: Product[] }) {
  if (products.length === 0) {
    return (
      <div className="rounded-xl bg-canvas p-10 text-center text-sm text-mute">
        Katalog masih kosong.
      </div>
    );
  }

  return (
    <div className="overflow-x-auto rounded-xl bg-canvas">
      <table className="w-full min-w-120 text-left text-sm">
        <thead className="sticky top-0 bg-canvas-soft text-xs uppercase tracking-wide text-mute">
          <tr>
            <th className="px-5 py-3 font-semibold">Produk</th>
            <th className="px-5 py-3 text-right font-semibold">Harga</th>
            <th className="px-5 py-3 text-right font-semibold">Stok</th>
          </tr>
        </thead>
        <tbody>
          {products.map((p) => {
            const low = p.stock <= p.low_stock_threshold;
            return (
              <tr
                key={p.id}
                className="border-b border-canvas-soft last:border-0"
              >
                <td className="px-5 py-3">
                  <p className="font-medium text-ink">{p.name}</p>
                  <p className="text-xs text-mute">{p.category || "-"}</p>
                </td>
                <td className="px-5 py-3 text-right text-body">
                  {rupiah(p.price)}
                  <span className="text-mute">/{p.unit}</span>
                </td>
                <td className="px-5 py-3 text-right">
                  {low ? (
                    <Badge tone="negative">
                      {p.stock} {p.unit} · menipis
                    </Badge>
                  ) : (
                    <Badge tone="positive">
                      {p.stock} {p.unit}
                    </Badge>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
