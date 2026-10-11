import type { Metadata, Viewport } from "next";
import "./globals.css";
import BottomNav from "@/components/BottomNav";

export const metadata: Metadata = {
  title: "NEXUS — Date · Market · Navigate · Create · Own the insight",
  description:
    "One platform, one identity, one map. Location-aware dating, marketplace, navigation, creator posts, and tradeable insight assets.",
  manifest: "/manifest.webmanifest",
};

export const viewport: Viewport = {
  themeColor: "#4F46E5",
  width: "device-width",
  initialScale: 1,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <main className="app-shell">{children}</main>
        <BottomNav />
      </body>
    </html>
  );
}
