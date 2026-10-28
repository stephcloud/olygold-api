from httpx import AsyncClient


async def test_health_returns_ok(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_rejects_post(client: AsyncClient) -> None:
    response = await client.post("/health")

    assert response.status_code == 405


async def test_cors_allows_configured_origin(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"Origin": "http://localhost:3000"})

    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


async def test_cors_ignores_unknown_origin(client: AsyncClient) -> None:
    response = await client.get("/health", headers={"Origin": "https://evil.example.com"})

    assert "access-control-allow-origin" not in response.headers
