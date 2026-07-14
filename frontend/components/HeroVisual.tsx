"use client";

import { useState } from "react";

// Full-bleed decorative background for the homepage hero. Fades from fully
// transparent to a subtle ~20% opacity once the image actually loads — the
// transition is driven by `onLoad` so it plays for slow connections and
// cached images alike (React fires onLoad for both).
export function HeroVisual() {
  const [loaded, setLoaded] = useState(false);

  return (
    <img
      src="/gerobak.webp"
      alt=""
      aria-hidden
      onLoad={() => setLoaded(true)}
      className={
        "pointer-events-none absolute inset-0 h-full w-full object-cover transition-opacity duration-700 ease-out " +
        (loaded ? "opacity-20" : "opacity-0")
      }
    />
  );
}
