"use client";

import { useEffect, useRef, useState } from "react";

// Full-bleed decorative background for the homepage hero. Fades from fully
// transparent to a subtle ~20% opacity once the image actually loads.
//
// The image is server-rendered, so the browser often finishes loading it
// before React hydrates and attaches `onLoad` — in that race the `load` event
// is missed and the img would stay stuck at opacity-0. We guard against that by
// checking `img.complete` on mount, which covers already-cached/fast loads;
// `onLoad` still covers the slow-connection case.
export function HeroVisual() {
  const [loaded, setLoaded] = useState(false);
  const imgRef = useRef<HTMLImageElement>(null);

  useEffect(() => {
    const img = imgRef.current;
    if (img?.complete && img.naturalWidth > 0) {
      setLoaded(true);
    }
  }, []);

  return (
    <img
      ref={imgRef}
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
