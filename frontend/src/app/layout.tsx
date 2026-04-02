import type { Metadata } from "next";
import { Mulish, Ruda, Gentium_Plus } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/providers";

const mulish = Mulish({
  variable: "--font-sans",
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700"],
  display: "swap",
});

const ruda = Ruda({
  variable: "--font-heading-h1",
  subsets: ["latin"],
  weight: ["400", "500", "600", "700", "800", "900"],
  display: "swap",
});

const gentiumPlus = Gentium_Plus({
  variable: "--font-heading-h2",
  subsets: ["latin"],
  weight: ["400", "700"],
  style: ["normal", "italic"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "FinControl",
  description: "Controle financeiro pessoal e empresarial",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="pt-BR"
      className={`${mulish.variable} ${ruda.variable} ${gentiumPlus.variable} h-full antialiased`}
    >
      <body className="min-h-full flex flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
