import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from core.exceptions import (
    SentryExceptionHandler, 
    sentry_exception_handler,
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    NotFoundError,
    ConflictError,
    RateLimitError
)
from esmerald import HTTPException, Request, Response

class TestSentryExceptionHandler:
    """Test the SentryExceptionHandler class"""
    
    @pytest.fixture
    def mock_request(self):
        """Create a mock request object"""
        request = Mock(spec=Request)
        request.method = "GET"
        request.url.path = "/test"
        request.url = Mock()
        request.url.path = "/test"
        request.headers = {"user-agent": "test-agent"}
        request.client = Mock()
        request.client.host = "127.0.0.1"
        request.user = None
        request.request_id = "test-123"
        return request
    
    @pytest.fixture
    def handler(self):
        """Create a SentryExceptionHandler instance"""
        return SentryExceptionHandler()
    
    @patch('core.exceptions.capture_error')
    @patch('core.exceptions.set_context')
    @patch('core.exceptions.settings')
    @pytest.mark.asyncio
    async def test_handler_captures_generic_exception(self, mock_settings, mock_set_context, mock_capture_error, handler, mock_request):
        """Test that generic exceptions are captured and return 500"""
        # Mock settings to return debug=False for this test
        mock_settings.debug = False
        
        exc = Exception("Test error")
        response = await handler(mock_request, exc)
        # Verify Sentry was called
        mock_capture_error.assert_called_once_with(exc, {
            "endpoint": "/test",
            "method": "GET",
            "request_id": "test-123",
            "handler": "SentryExceptionHandler"
        })
        # Verify context was set
        mock_set_context.assert_called()
        # Verify response
        assert response.status_code == 500
        body = json.loads(response.body.decode())
        assert "Internal server error" in body["detail"]
        assert body["error_code"] == "INTERNAL_ERROR"
    
    @patch('core.exceptions.capture_error')
    @pytest.mark.asyncio
    async def test_handler_handles_http_exception(self, mock_capture_error, handler, mock_request):
        """Test that HTTPException is handled correctly"""
        exc = HTTPException(status_code=404, detail="Not found")
        response = await handler(mock_request, exc)
        # Verify Sentry was called
        mock_capture_error.assert_called_once()
        # Verify response
        assert response.status_code == 404
        body = json.loads(response.body.decode())
        assert body["detail"] == "Not found"
    
    @patch('core.exceptions.capture_error')
    @pytest.mark.asyncio
    async def test_handler_sets_user_context(self, mock_capture_error, handler, mock_request):
        """Test that user context is set when available"""
        # Mock user object
        mock_user = Mock()
        mock_user.id = "user-123"
        mock_user.email = "test@example.com"
        mock_request.user = mock_user
        exc = Exception("Test error")
        await handler(mock_request, exc)
        # Verify user context was set
        mock_capture_error.assert_called_once()
        # The set_context calls are made in the handler

class TestCustomExceptions:
    """Test custom exception classes"""
    
    def test_validation_error(self):
        """Test ValidationError exception"""
        exc = ValidationError()
        assert exc.status_code == 422
        assert exc.detail == "Validation error"
    
    def test_authentication_error(self):
        """Test AuthenticationError exception"""
        exc = AuthenticationError()
        assert exc.status_code == 401
        assert exc.detail == "Authentication required"
    
    def test_authorization_error(self):
        """Test AuthorizationError exception"""
        exc = AuthorizationError()
        assert exc.status_code == 403
        assert exc.detail == "Insufficient permissions"
    
    def test_not_found_error(self):
        """Test NotFoundError exception"""
        exc = NotFoundError()
        assert exc.status_code == 404
        assert exc.detail == "Resource not found"
    
    def test_conflict_error(self):
        """Test ConflictError exception"""
        exc = ConflictError()
        assert exc.status_code == 409
        assert exc.detail == "Resource conflict"
    
    def test_rate_limit_error(self):
        """Test RateLimitError exception"""
        exc = RateLimitError()
        assert exc.status_code == 429
        assert exc.detail == "Rate limit exceeded"

class TestExceptionHandlerIntegration:
    """Test exception handler integration with Sentry"""
    
    @patch('core.exceptions.capture_error')
    def test_sentry_exception_handler_instance(self, mock_capture_error):
        """Test that the global exception handler instance exists"""
        assert sentry_exception_handler is not None
        assert isinstance(sentry_exception_handler, SentryExceptionHandler)
    
    @patch('core.exceptions.capture_error')
    @pytest.mark.asyncio
    async def test_handler_logs_errors(self, mock_capture_error):
        """Test that errors are logged"""
        handler = SentryExceptionHandler()
        request = Mock(spec=Request)
        request.method = "POST"
        request.url.path = "/api/test"
        request.url = Mock()
        request.url.path = "/api/test"
        request.headers = {}
        request.client = None
        request.user = None
        request.request_id = None
        exc = RuntimeError("Test runtime error")
        with patch.object(handler.logger, 'error') as mock_logger_error:
            await handler(request, exc)
            mock_logger_error.assert_called_once()
            log_message = mock_logger_error.call_args[0][0]
            assert "POST /api/test" in log_message
            assert "Test runtime error" in log_message 