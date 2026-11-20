import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_login_rate_limiting(async_client: AsyncClient):
    """Verify that exceeding 5 login attempts per minute returns HTTP 429."""
    for i in range(5):
        response = await async_client.post(
            "/api/v1/auth/login",
            data={"username": "admin", "password": "wrongpassword"}
        )
        assert response.status_code == 401

    # 6th attempt should be blocked by slowapi rate limiter
    blocked_response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "wrongpassword"}
    )
    assert blocked_response.status_code == 429
    assert "Rate limit exceeded" in blocked_response.text