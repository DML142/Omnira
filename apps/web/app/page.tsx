import { translate } from "@/lib/i18n/en";

export default function Home() {
  return (
    <main className="min-h-dvh bg-background px-5 py-6 text-foreground sm:px-8 sm:py-8">
      <div className="mx-auto w-full max-w-4xl">
        <header className="flex items-center gap-3 border-b border-border pb-5">
          <span
            aria-hidden="true"
            className="h-3 w-3 rounded-[2px] bg-accent"
          />
          <span className="text-sm font-semibold tracking-[-0.01em]">
            {translate("brand.name")}
          </span>
        </header>

        <section className="grid gap-10 py-14 sm:py-20 lg:grid-cols-[minmax(0,1fr)_19rem] lg:items-start lg:gap-16">
          <div className="max-w-2xl">
            <h1 className="text-balance text-3xl font-semibold leading-tight tracking-[-0.035em] sm:text-4xl">
              {translate("home.positioning")}
            </h1>
            <p className="mt-5 max-w-xl text-sm leading-6 text-muted sm:text-[15px]">
              {translate("home.summary")}
            </p>
          </div>

          <aside className="border-l-2 border-accent bg-surface px-5 py-4">
            <div className="flex items-center gap-2.5">
              <span
                aria-hidden="true"
                className="h-2 w-2 rounded-full bg-warning"
              />
              <h2 className="text-sm font-medium">
                {translate("workspace.status")}
              </h2>
            </div>
            <p className="mt-3 text-sm leading-5 text-muted">
              {translate("workspace.description")}
            </p>
            <p className="mt-2 text-xs leading-5 text-muted">
              {translate("workspace.detail")}
            </p>
          </aside>
        </section>
      </div>
    </main>
  );
}
