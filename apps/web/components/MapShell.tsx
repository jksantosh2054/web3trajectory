"use client";

import { useEffect, useRef } from "react";
import maplibregl from "maplibre-gl";
import "maplibre-gl/dist/maplibre-gl.css";

type Props = {
  center?: [number, number]; // [lng, lat] — Kathmandu default
  zoom?: number;
  children?: React.ReactNode;
};

/** Shared map shell: dating, marketplace, assets, navigation reuse this. */
export default function MapShell({ center = [85.324, 27.7172], zoom = 12, children }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const mapRef = useRef<maplibregl.Map | null>(null);

  useEffect(() => {
    if (!ref.current || mapRef.current) return;
    mapRef.current = new maplibregl.Map({
      container: ref.current,
      style: "https://demotiles.maplibre.org/style.json", // replaced by self-hosted tiles
      center,
      zoom,
    });
    return () => {
      mapRef.current?.remove();
      mapRef.current = null;
    };
  }, [center, zoom]);

  return (
    <div style={{ position: "relative", height: "100dvh" }}>
      <div ref={ref} style={{ position: "absolute", inset: 0 }} aria-label="Map" />
      <div style={{ position: "absolute", inset: 0, pointerEvents: "none" }}>
        <div style={{ pointerEvents: "auto" }}>{children}</div>
      </div>
    </div>
  );
}
