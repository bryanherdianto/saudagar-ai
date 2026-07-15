"use client";

import { type ReactNode } from "react";
import { useAuth } from "@clerk/nextjs";
import { configureTokenGetter } from "@/lib/api";

/**
 * Wires Clerk's session token into the global API client.
 *
 * The getter is configured during *render* rather than in an effect. React
 * fires effects child-first, so an effect here would run *after* child pages'
 * effects — letting the dashboard's first `api.*` call fire before the token
 * getter is installed, which the backend rejects with 401. Configuring in
 * render guarantees the live getter is in place before any child effect runs
 * in the same commit. Setting a module-level variable is idempotent, so doing
 * it every render is safe.
 */
export function TokenGate({ children }: { children: ReactNode }) {
  const { getToken, isLoaded, isSignedIn } = useAuth();

  configureTokenGetter(async () => {
    if (!isLoaded || !isSignedIn) return null;
    return (await getToken()) ?? null;
  });

  return <>{children}</>;
}
