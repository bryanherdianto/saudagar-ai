// Design-system primitives mapped to the Wise-inspired tokens in globals.css.

import type { ButtonHTMLAttributes, ReactNode } from "react";

type ButtonVariant = "primary" | "secondary" | "tertiary" | "dark";

const buttonStyles: Record<ButtonVariant, string> = {
  // Lime-green CTA pill — the brand's conversion signature.
  primary:
    "bg-primary text-on-primary hover:bg-primary-active disabled:opacity-50",
  secondary: "bg-canvas-soft text-ink hover:bg-primary-pale disabled:opacity-50",
  tertiary:
    "bg-canvas text-ink border border-ink hover:bg-canvas-soft disabled:opacity-50",
  dark: "bg-ink text-primary hover:bg-ink/90 disabled:opacity-50",
};

export function Button({
  variant = "primary",
  className = "",
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
  children: ReactNode;
}) {
  return (
    <button
      className={`inline-flex items-center justify-center gap-2 rounded-xl px-6 py-3 text-base font-semibold transition-colors disabled:cursor-not-allowed ${buttonStyles[variant]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}

type CardTone = "canvas" | "sage" | "green" | "dark";

const cardTones: Record<CardTone, string> = {
  canvas: "bg-canvas text-ink",
  sage: "bg-canvas-soft text-ink",
  green: "bg-primary-pale text-ink",
  dark: "bg-ink text-primary",
};

export function Card({
  tone = "canvas",
  className = "",
  children,
}: {
  tone?: CardTone;
  className?: string;
  children: ReactNode;
}) {
  return (
    <div className={`rounded-xl p-6 ${cardTones[tone]} ${className}`}>
      {children}
    </div>
  );
}

type BadgeTone = "positive" | "negative" | "warning" | "neutral";

const badgeTones: Record<BadgeTone, string> = {
  positive: "bg-primary-pale text-positive-deep",
  negative: "bg-negative-bg text-canvas",
  warning: "bg-warning/20 text-warning-deep",
  neutral: "bg-canvas-soft text-body",
};

export function Badge({
  tone = "neutral",
  children,
}: {
  tone?: BadgeTone;
  children: ReactNode;
}) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-3 py-1 text-sm font-semibold ${badgeTones[tone]}`}
    >
      {children}
    </span>
  );
}

// A labelled section header used above panels.
export function SectionTitle({
  eyebrow,
  title,
  action,
}: {
  eyebrow?: string;
  title: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex items-end justify-between gap-4">
      <div>
        {eyebrow && (
          <p className="text-xs font-semibold uppercase tracking-wider text-mute">
            {eyebrow}
          </p>
        )}
        <h2 className="font-display text-2xl text-ink">{title}</h2>
      </div>
      {action}
    </div>
  );
}
