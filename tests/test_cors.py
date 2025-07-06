"""
CORS Configuration Tests
Tests to ensure CORS is properly configured and working
"""
import pytest
from httpx import AsyncClient
from main import app


@pytest.mark.asyncio
async def test_cors_preflight_request():
    """Test CORS preflight request returns proper headers"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/lists",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"
        assert "access-control-allow-methods" in response.headers
        assert "access-control-allow-headers" in response.headers


@pytest.mark.asyncio
async def test_cors_actual_request():
    """Test CORS headers are present in actual requests"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/lists",
            headers={"Origin": "http://localhost:3000"}
        )
        
        assert response.status_code == 200
        assert "access-control-allow-origin" in response.headers
        assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


@pytest.mark.asyncio
async def test_cors_credentials_support():
    """Test CORS credentials are properly configured"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/lists",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-credentials" in response.headers
        assert response.headers["access-control-allow-credentials"] == "true"


@pytest.mark.asyncio
async def test_cors_multiple_origins():
    """Test CORS works with multiple allowed origins"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        # Test localhost:3000
        response1 = await client.get(
            "/api/lists",
            headers={"Origin": "http://localhost:3000"}
        )
        assert response1.headers["access-control-allow-origin"] == "http://localhost:3000"
        
        # Test 127.0.0.1:3000
        response2 = await client.get(
            "/api/lists",
            headers={"Origin": "http://127.0.0.1:3000"}
        )
        assert response2.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


@pytest.mark.asyncio
async def test_cors_disallowed_origin():
    """Test CORS blocks disallowed origins"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get(
            "/api/lists",
            headers={"Origin": "http://malicious-site.com"}
        )
        
        # Should still return 200 but without CORS headers
        assert response.status_code == 200
        assert "access-control-allow-origin" not in response.headers


@pytest.mark.asyncio
async def test_cors_methods_support():
    """Test CORS supports all required HTTP methods"""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    
    async with AsyncClient(app=app, base_url="http://test") as client:
        for method in methods:
            response = await client.options(
                "/api/lists",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": method,
                }
            )
            
            assert response.status_code == 200
            assert "access-control-allow-methods" in response.headers
            allowed_methods = response.headers["access-control-allow-methods"]
            assert method in allowed_methods


@pytest.mark.asyncio
async def test_cors_headers_support():
    """Test CORS supports required headers"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.options(
            "/api/lists",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type, Authorization",
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-headers" in response.headers
        allowed_headers = response.headers["access-control-allow-headers"]
        assert "Content-Type" in allowed_headers
        assert "Authorization" in allowed_headers 