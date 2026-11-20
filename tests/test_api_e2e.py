import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_health_check(async_client: AsyncClient):
    """Test public health endpoint."""
    response = await async_client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "online"


@pytest.mark.asyncio
async def test_auth_login_success(async_client: AsyncClient):
    """Test successful user login and JWT token generation."""
    response = await async_client.post(
        "/api/v1/auth/login",
        data={"username": "admin", "password": "admin123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_agent_run_unauthorized(async_client: AsyncClient):
    """Test that agent execution requires authentication."""
    response = await async_client.post(
        "/api/v1/agent/run",
        json={"prompt": "Check stock for 6204-2RS", "thread_id": "test_thread"}
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_tasks_export_quote_flow(async_client: AsyncClient, auth_headers: dict):
    """Test dispatching background Celery quote export tasks."""
    response = await async_client.post(
        "/api/v1/tasks/export-quote",
        headers=auth_headers,
        json={"item_code": "6204-2RS", "quantity": 50, "customer_tier": "VIP"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "task_id" in data
    assert data["status"] == "processing"