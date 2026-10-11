import Link from "next/link";

/** Landing: search + public discovery, no login wall (guest-first). */
export default function Landing() {
  return (
    <div style={{ padding: 24, maxWidth: 720, margin: "0 auto" }}>
      <h1>NEXUS</h1>
      <p>One platform, one identity, one map.</p>
      <form action="/explore" method="get">
        <input
          name="q"
          placeholder="Search places, products, posts…"
          style={{ width: "100%", padding: 12, borderRadius: 8 }}
          aria-label="Search NEXUS"
        />
      </form>
      <div style={{ display: "flex", gap: 12, marginTop: 24, flexWrap: "wrap" }}>
        <Link href="/explore">Explore the map</Link>
        <Link href="/dating">Dating</Link>
        <Link href="/market">Marketplace</Link>
        <Link href="/assets">Insight assets</Link>
      </div>
      <p style={{ marginTop: 32, color: "#64748b" }}>
        Browse freely — sign up only to save preferences, date, sell, create, or bid.
      </p>
    </div>
  );
}
