# Routing — Valhalla + Nepal OSM extract (PROPOSED)

Self-hosted turn-by-turn routing so NEXUS has no third-party routing dependency.

## One-time tile build

```bash
# 1. Download the Nepal extract (Geofabrik)
wget https://download.geofabrik.de/asia/nepal-latest.osm.pbf -O nepal.osm.pbf

# 2. Build Valhalla tiles (inside the valhalla image)
docker run --rm -v $PWD:/data ghcr.io/valhalla/valhalla:3.5.0 \
  valhalla_build_tiles -c /conf/valhalla.json /data/nepal.osm.pbf

# 3. Point VALHALLA_TILE_DIR at the output and start the service
docker compose up routing
```

## API surface (via backend `/api/v1/geo/route`)

Backend proxies to Valhalla's `/route` with profiles `auto`/`bicycle`/`pedestrian`.
GPS traces are session-ephemeral — nothing persisted server-side.

## Status

PROPOSED (ADR-014). The Dockerfile pins the Valhalla image; tile baking and
the `valhalla.json` config are still to be added (NX-012 spike).
