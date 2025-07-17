import pytest
from unittest.mock import patch, MagicMock
from core.sentry import init_sentry
from core.sentry_utils import capture_error, capture_message, set_user, set_context, add_breadcrumb, with_sentry
import warnings

# Suppress Pydantic deprecation warnings for clean test output
warnings.filterwarnings("ignore", category=DeprecationWarning, module="pydantic")

class TestSentryInitialization:
    """Test Sentry initialization and configuration"""
    
    @patch('core.sentry.sentry_sdk.init')
    def test_sentry_init_with_dsn(self, mock_init):
        """Test Sentry initialization with DSN"""
        with patch('core.config.settings.sentry_dsn', 'https://test-dsn@sentry.io/test-project'):
            with patch('core.config.settings.sentry_environment', 'test'):
                init_sentry()
                mock_init.assert_called_once()
                call_args = mock_init.call_args
                assert call_args[1]['dsn'] == 'https://test-dsn@sentry.io/test-project'
                assert call_args[1]['environment'] == 'test'
    
    @patch('core.sentry.sentry_sdk.init')
    def test_sentry_init_without_dsn(self, mock_init):
        """Test Sentry initialization without DSN"""
        with patch('core.config.settings.sentry_dsn', None):
            init_sentry()
            mock_init.assert_not_called()
    
    @patch('core.sentry.sentry_sdk.init')
    def test_sentry_init_with_invalid_dsn(self, mock_init):
        """Test Sentry initialization with invalid DSN format"""
        with patch('core.config.settings.sentry_dsn', 'invalid-dsn-format'):
            init_sentry()
            mock_init.assert_not_called()

class TestSentryUtils:
    """Test Sentry utility functions"""
    
    @patch('core.sentry_utils.sentry_sdk.capture_exception')
    @patch('core.sentry_utils.sentry_sdk.set_context')
    def test_capture_error_with_context(self, mock_set_context, mock_capture):
        """Test error capture with context"""
        error = ValueError("Test error")
        context = {"test": "context"}
        
        capture_error(error, context)
        
        mock_set_context.assert_called_once_with("error_context", context)
        mock_capture.assert_called_once_with(error)
    
    @patch('core.sentry_utils.sentry_sdk.capture_exception')
    @patch('core.sentry_utils.sentry_sdk.set_context')
    def test_capture_error_without_context(self, mock_set_context, mock_capture):
        """Test error capture without context"""
        error = ValueError("Test error")
        
        capture_error(error)
        
        mock_set_context.assert_not_called()
        mock_capture.assert_called_once_with(error)
    
    @patch('core.sentry_utils.sentry_sdk.capture_message')
    def test_capture_message(self, mock_capture):
        """Test message capture"""
        message = "Test message"
        level = "warning"
        
        capture_message(message, level)
        
        mock_capture.assert_called_once_with(message, level)
    
    @patch('core.sentry_utils.sentry_sdk.set_user')
    def test_set_user(self, mock_set_user):
        """Test user context setting"""
        user_id = "user123"
        email = "test@example.com"
        username = "testuser"
        
        set_user(user_id, email, username)
        
        expected_user = {
            "id": user_id,
            "email": email,
            "username": username
        }
        mock_set_user.assert_called_once_with(expected_user)
    
    @patch('core.sentry_utils.sentry_sdk.set_context')
    def test_set_context(self, mock_set_context):
        """Test context setting"""
        name = "test_context"
        context = {"key": "value"}
        
        set_context(name, context)
        
        mock_set_context.assert_called_once_with(name, context)
    
    @patch('core.sentry_utils.sentry_sdk.add_breadcrumb')
    def test_add_breadcrumb(self, mock_add_breadcrumb):
        """Test breadcrumb addition"""
        message = "Test breadcrumb"
        category = "test_category"
        data = {"test": "data"}
        level = "info"
        
        add_breadcrumb(message, category, data, level)
        
        expected_breadcrumb = {
            "message": message,
            "level": level,
            "category": category,
            "data": data
        }
        mock_add_breadcrumb.assert_called_once_with(expected_breadcrumb)

class TestSentryDecorator:
    """Test Sentry decorator functionality"""
    
    @patch('core.sentry_utils.capture_error')
    def test_with_sentry_sync_function_success(self, mock_capture_error):
        """Test decorator with successful sync function"""
        @with_sentry
        def test_func():
            return "success"
        
        result = test_func()
        assert result == "success"
        mock_capture_error.assert_not_called()
    
    @patch('core.sentry_utils.capture_error')
    def test_with_sentry_sync_function_error(self, mock_capture_error):
        """Test decorator with sync function that raises error"""
        test_error = ValueError("Test error")
        
        @with_sentry
        def test_func():
            raise test_error
        
        with pytest.raises(ValueError):
            test_func()
        
        mock_capture_error.assert_called_once()
        call_args = mock_capture_error.call_args
        assert call_args[0][0] == test_error
        assert "function_name" in call_args[0][1]
    
    @pytest.mark.asyncio
    @patch('core.sentry_utils.capture_error')
    async def test_with_sentry_async_function_success(self, mock_capture_error):
        """Test decorator with successful async function"""
        @with_sentry
        async def test_func():
            return "success"
        
        result = await test_func()
        assert result == "success"
        mock_capture_error.assert_not_called()
    
    @pytest.mark.asyncio
    @patch('core.sentry_utils.capture_error')
    async def test_with_sentry_async_function_error(self, mock_capture_error):
        """Test decorator with async function that raises error"""
        test_error = ValueError("Test error")
        
        @with_sentry
        async def test_func():
            raise test_error
        
        with pytest.raises(ValueError):
            await test_func()
        
        mock_capture_error.assert_called_once()
        call_args = mock_capture_error.call_args
        assert call_args[0][0] == test_error
        assert "function_name" in call_args[0][1] 