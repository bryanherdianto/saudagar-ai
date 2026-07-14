import type { InsightResponse } from "@/lib/types";
import { rupiah } from "@/lib/format";
import { Badge } from "./ui";
import { SparkIcon } from "./icons";

// The dashboard's signature "AI narrative" moment — a polarity-flipped dark
// card with lime-green text (DESIGN.md: hero-band-dark / card-feature-dark).
export function InsightPanel({ insight }: { insight: InsightResponse }) {
  const { headline, narrative, recommendations, metrics, ai_enabled } = insight;
  return (
    <div className="rounded-xl bg-ink p-7 text-primary">
      <div className="mb-4 flex items-center gap-2">
        <SparkIcon className="h-5 w-5" />
        <span className="text-xs font-semibold uppercase tracking-wider">
          Narasi Analitik AI
        </span>
        {!ai_enabled && (
          <span className="rounded-full bg-primary/15 px-2 py-0.5 text-[11px] font-semibold text-primary">
            mode demo
          </span>
        )}
      </div>

      <h2 className="font-display text-3xl leading-tight text-primary sm:text-4xl">
        {headline}
      </h2>
      <p className="mt-4 max-w-2xl text-base leading-relaxed text-canvas-soft">
        {narrative}
      </p>

      {recommendations.length > 0 && (
        <div className="mt-6">
          <p className="mb-2 text-sm font-semibold text-primary/80">
            Rekomendasi untukmu
          </p>
          <ul className="space-y-2">
            {recommendations.map((rec, i) => (
              <li
                key={i}
                className="flex items-start gap-3 text-sm text-canvas-soft"
              >
                <span className="mt-0.5 flex h-5 w-5 shrink-0 items-center justify-center rounded-full bg-primary text-xs font-bold text-on-primary">
                  {i + 1}
                </span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}

      {metrics.top_products.length > 0 && (
        <div className="mt-6 flex flex-wrap gap-2">
          {metrics.top_products.slice(0, 3).map((p) => (
            <Badge key={p.name} tone="positive">
              🔥 {p.name} · {rupiah(p.revenue)}
            </Badge>
          ))}
        </div>
      )}
    </div>
  );
}
