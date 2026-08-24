from __future__ import annotations

import gzip
from pathlib import Path

import httpx
import pytest
import respx
from fastapi.testclient import TestClient
from pydantic import SecretStr, ValidationError

from papers_bridge.app import create_app
from papers_bridge.config import Settings


def test_settings_accept_comma_separated_collection_keys_from_environment(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    values = {
        "ZOTERO_USER_ID": "12345",
        "ZOTERO_API_KEY": "zotero-test-key",
        "ALLOWED_COLLECTION_KEYS": "COLLECTION1, COLLECTION2",
        "BRIDGE_BEARER_TOKEN": "b" * 32,
        "DOCLING_API_KEY": "d" * 32,
        "CACHE_DIR": str(tmp_path / "cache"),
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    configured = Settings()  # type: ignore[call-arg]

    assert configured.allowed_collection_keys == ("COLLECTION1", "COLLECTION2")


def test_health_is_public_but_data_routes_require_bearer_token(settings: Settings) -> None:
    app = create_app(settings)
    with TestClient(app) as client:
        assert client.get("/v1/health").json() == {"status": "ok"}
        response = client.get("/v1/collections")
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def test_authenticated_collections_reaches_zotero(settings: Settings) -> None:
    with respx.mock(assert_all_called=True) as router:
        router.get(
            "https://api.zotero.org/users/12345/collections",
            params={"limit": 100, "start": 0},
        ).mock(
            return_value=httpx.Response(
                200,
                content=gzip.compress(
                    b'[{"key":"COLLECTION1","data":{"name":"Reading"}}]'
                ),
                headers={"Content-Encoding": "gzip"},
            )
        )
        app = create_app(settings)
        with TestClient(app) as client:
            response = client.get(
                "/v1/collections",
                headers={"Authorization": f"Bearer {'b' * 32}"},
            )

    assert response.status_code == 200
    assert response.json() == [{"key": "COLLECTION1", "name": "Reading"}]


def test_malformed_keys_are_rejected_before_upstream_access(settings: Settings) -> None:
    app = create_app(settings)
    with TestClient(app) as client:
        response = client.get(
            "/v1/collections/not%2Fa%2Fkey/snapshot",
            headers={"Authorization": f"Bearer {'b' * 32}"},
        )
    assert response.status_code in {404, 422}


def test_public_item_contract_is_item_qualified(settings: Settings) -> None:
    app = create_app(settings)
    paths = {route.path for route in app.routes}
    assert "/v1/items/{item_key}" in paths
    assert "/v1/items/{item_key}/conversion" in paths
    assert not any("{collection_key}/items" in path for path in paths)


def test_blank_or_short_secrets_fail_before_the_service_starts() -> None:
    with pytest.raises(ValidationError):
        Settings(
            zotero_user_id="123",
            zotero_api_key=SecretStr(" "),
            allowed_collection_keys=("COLL1",),
            bridge_bearer_token=SecretStr(""),
            docling_api_key=SecretStr("short"),
        )


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("zotero_base_url", "http://api.zotero.org"),
        ("zotero_base_url", "https://api.zotero.org.evil.test"),
        ("docling_url", "http://127.0.0.1:5001"),
        ("docling_url", "https://docling.example.test"),
    ],
)
def test_upstream_origins_are_fixed_to_the_deployment_boundary(
    settings: Settings, field: str, value: str
) -> None:
    values = {
        **settings.model_dump(),
        "zotero_api_key": settings.zotero_api_key,
        "bridge_bearer_token": settings.bridge_bearer_token,
        "docling_api_key": settings.docling_api_key,
        field: value,
    }
    with pytest.raises(ValidationError):
        Settings(**values)
