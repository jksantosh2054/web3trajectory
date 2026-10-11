# Valhalla routing engine (PROPOSED — see README for tile build steps).
# Tiles are built at image build time from the Nepal OSM extract and baked in,
# or mounted via the valhalla_tiles volume at runtime.
FROM ghcr.io/valhalla/valhalla:3.5.0 AS base

# Placeholder: tile build happens in README steps; the runtime just serves.
EXPOSE 8002
CMD ["valhalla_service", "/conf/valhalla.json", "1"]
