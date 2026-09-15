export const en = {
  "metadata.title": "Omnira",
  "metadata.description":
    "Commerce operations and inventory orchestration for growing brands.",
  "brand.name": "Omnira",
  "home.positioning":
    "Commerce operations and inventory orchestration for growing brands.",
  "home.summary":
    "Keep orders, stock, and connected stores in sync from one workspace.",
  "workspace.status": "Workspace unavailable",
  "workspace.description": "The workspace is not available yet.",
  "workspace.detail": "No live commerce data is connected.",
  "notFound.title": "Page not found",
  "notFound.description": "The page you requested is not available.",
  "notFound.homeLink": "Return to Omnira",
} as const;

export type TranslationKey = keyof typeof en;

export function translate(key: TranslationKey): string {
  return en[key];
}
