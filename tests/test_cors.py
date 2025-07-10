"""
CORS Configuration Tests
Tests to ensure CORS is properly configured and working
"""
import pytest
from esmerald.testclient import EsmeraldTestClient
from main import app


def test_cors_preflight_request(test_client):
    """Test CORS preflight request returns proper headers"""
    response = test_client.options(
        "/ping",
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


def test_cors_actual_request(test_client):
    """Test CORS headers are present in actual requests"""
    response = test_client.get(
        "/ping",
        headers={"Origin": "http://localhost:3000"}
    )
    
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_cors_credentials_support(test_client):
    """Test CORS credentials are properly configured"""
    response = test_client.options(
        "/ping",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    
    assert response.status_code == 200
    assert "access-control-allow-credentials" in response.headers
    assert response.headers["access-control-allow-credentials"] == "true"


def test_cors_multiple_origins(test_client):
    """Test CORS works with multiple allowed origins"""
    # Test localhost:3000
    response1 = test_client.get(
        "/ping",
        headers={"Origin": "http://localhost:3000"}
    )
    assert response1.headers["access-control-allow-origin"] == "http://localhost:3000"
    
    # Test 127.0.0.1:3000
    response2 = test_client.get(
        "/ping",
        headers={"Origin": "http://127.0.0.1:3000"}
    )
    assert response2.headers["access-control-allow-origin"] == "http://127.0.0.1:3000"


def test_cors_disallowed_origin(test_client):
    """Test CORS blocks disallowed origins"""
    response = test_client.get(
        "/ping",
        headers={"Origin": "http://malicious-site.com"}
    )
    
    # Should still return 200 but without CORS headers
    assert response.status_code == 200
    assert "access-control-allow-origin" not in response.headers


def test_cors_methods_support(test_client):
    """Test CORS supports all required HTTP methods"""
    methods = ["GET", "POST", "PUT", "DELETE", "PATCH"]
    
    for method in methods:
        response = test_client.options(
            "/ping",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": method,
            }
        )
        
        assert response.status_code == 200
        assert "access-control-allow-methods" in response.headers
        allowed_methods = response.headers["access-control-allow-methods"]
        assert method in allowed_methods


def test_cors_headers_support(test_client):
    """Test CORS supports required headers"""
    response = test_client.options(
        "/ping",
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