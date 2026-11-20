import pytest
from httpx import AsyncClient, ASGITransport
from app.core.limiter import limiter
from app.main import app
from app.core.security import create_access_token

@pytest.fixture(autouse=True)
def reset_rate_limiters():
    """Reset rate limiter state before every test run."""
    limiter.reset()
    yield
    
@pytest.fixture
async def async_client():
    """Provides an async HTTP client connected to the FastAPI ASGI app."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        yield client

@pytest.fixture
def auth_headers():
    """Generates valid Bearer authentication headers for a mock user."""
    token = create_access_token(data={"sub": "admin", "role": "admin"})
    return {"Authorization": f"Bearer {token}"}