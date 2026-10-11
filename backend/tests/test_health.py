"""Smoke tests: app boots, routers register, privacy helpers behave."""
from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from app.services.privacy import apply_suppression, check_cohort_minimum, teaser_band
from app.services.settlement import SimulatedSettlement, get_settlement_adapter

client = TestClient(app)


def test_healthz() -> None:
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_openapi_routes_present() -> None:
    paths = {route.path for route in app.routes}
    for expected in (
        "/api/v1/dating/pool",
        "/api/v1/dating/proposals",
        "/api/v1/market/listings",
        "/api/v1/orders",
        "/api/v1/assets",
        "/api/v1/auctions/{auction_id}/bids",
        "/api/v1/vault",
        "/api/v1/studio/posts/{post_id}/analytics",
    ):
        assert expected in paths, f"missing route {expected}"


def test_cohort_minimum() -> None:
    assert check_cohort_minimum(30) is True
    assert check_cohort_minimum(29) is False


def test_suppression() -> None:
    released, suppressed = apply_suppression(
        [
            {"bucket_id": "ktm", "distinct_actors": 120},
            {"bucket_id": "pkr", "distinct_actors": 12},
        ]
    )
    assert [b["bucket_id"] for b in released] == ["ktm"]
    assert suppressed == ["pkr"]


def test_teaser_band_never_exact() -> None:
    assert teaser_band(4321) == "1k–5k views"
    assert "4321" not in teaser_band(4321)


def test_simulated_settlement_factory() -> None:
    adapter = get_settlement_adapter()
    assert isinstance(adapter, SimulatedSettlement)
