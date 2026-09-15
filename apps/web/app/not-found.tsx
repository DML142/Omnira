import Link from "next/link";

import { translate } from "@/lib/i18n/en";

export default function NotFound() {
  return (
    <main className="min-h-dvh bg-background px-5 py-16 text-foreground sm:px-8">
      <section className="mx-auto max-w-xl border-l-2 border-accent bg-surface px-6 py-5">
        <h1 className="text-xl font-semibold tracking-[-0.02em]">
          {translate("notFound.title")}
        </h1>
        <p className="mt-3 text-sm leading-6 text-muted">
          {translate("notFound.description")}
        </p>
        <Link
          className="mt-6 inline-flex rounded-control bg-accent px-3 py-2 text-sm font-medium text-accent-foreground hover:bg-accent-hover focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-info"
          href="/"
        >
          {translate("notFound.homeLink")}
        </Link>
      </section>
    </main>
  );
}
