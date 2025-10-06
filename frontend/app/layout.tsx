import type { Metadata } from "next";
import { Work_Sans, Literata } from "next/font/google";
import "../globals.css";
import ClientBody from "./ClientBody";
import Script from "next/script";

const heading = Work_Sans({
  variable: "--font-heading",
  subsets: ["latin"],
});

const body = Literata({
  variable: "--font-body",
  subsets: ["latin"],
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Monthly Funding Digest",
  description: "Sleek, modern, serif-first monthly newsletter of Denmark startup funding.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={`${heading.variable} ${body.variable}`}>
      <head>
        <Script crossOrigin="anonymous" src="//unpkg.com/same-runtime/dist/index.global.js" />
      </head>
      <body suppressHydrationWarning className="antialiased">
        <ClientBody>{children}</ClientBody>
      </body>
    </html>
  );
}
