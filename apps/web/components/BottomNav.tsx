"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const TABS = [
  { href: "/explore", label: "Explore" },
  { href: "/feed", label: "Social" },
  { href: "/market", label: "Market" },
  { href: "/create", label: "Create" },
  { href: "/settings/preferences", label: "Me" },
];

export default function BottomNav() {
  const pathname = usePathname();
  return (
    <nav
      aria-label="Primary"
      style={{
        position: "fixed",
        bottom: 0,
        left: 0,
        right: 0,
        display: "flex",
        background: "#fff",
        borderTop: "1px solid #e2e8f0",
        zIndex: 50,
      }}
    >
      {TABS.map((t) => {
        const active = pathname === t.href || pathname.startsWith(t.href + "/");
        return (
          <Link
            key={t.href}
            href={t.href}
            aria-current={active ? "page" : undefined}
            style={{
              flex: 1,
              textAlign: "center",
              padding: "12px 0",
              color: active ? "var(--color-primary)" : "var(--color-muted)",
              fontWeight: active ? 600 : 400,
              textDecoration: "none",
            }}
          >
            {t.label}
          </Link>
        );
      })}
    </nav>
  );
}
