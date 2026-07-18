"use client";

import { SignInButton, SignUpButton, Show, UserButton } from "@clerk/nextjs";

// Client-side auth controls for the site header. Shows sign-in/sign-up buttons
// when signed out, and a user button when signed in - following the Clerk
// pattern from the setup guide.
export function AuthControls() {
  return (
    <div className="flex items-center gap-3">
      <Show when="signed-out">
        <SignInButton>
          <button className="text-sm font-semibold text-body transition-colors hover:text-ink">
            Masuk
          </button>
        </SignInButton>
        <SignUpButton>
          <button className="inline-flex items-center justify-center rounded-xl bg-primary px-5 py-2.5 text-sm font-semibold text-on-primary transition-colors hover:bg-primary-active">
            Daftar
          </button>
        </SignUpButton>
      </Show>
      <Show when="signed-in">
        <UserButton
          appearance={{
            elements: {
              avatarBox: "h-9 w-9",
            },
          }}
        />
      </Show>
    </div>
  );
}
