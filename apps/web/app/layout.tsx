import type { Metadata } from "next";

import { translate } from "@/lib/i18n/en";

import "./globals.css";

export const metadata: Metadata = {
  title: translate("metadata.title"),
  description: translate("metadata.description"),
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
