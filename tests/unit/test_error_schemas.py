import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from apps.todo.schemas import (
    ErrorResponse, ValidationErrorResponse, NotFoundErrorResponse,
    AuthErrorResponse, RateLimitErrorResponse
)


class TestErrorResponse:
    """Test base error response schema"""
    
    def test_error_response_valid(self):
        """Test creating a valid error response"""
        data = {
            "error": {
                "code": "TEST_ERROR",
                "message": "Test error message",
                "details": {"field": "test"}
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        error_response = ErrorResponse(**data)
        assert error_response.error["code"] == "TEST_ERROR"
        assert error_response.error["message"] == "Test error message"
        assert error_response.request_id == "req_1234567890abcdef"
        assert isinstance(error_response.timestamp, datetime)
    
    def test_error_response_missing_required_fields(self):
        """Test error response with missing required fields"""
        data = {
            "error": {"code": "TEST_ERROR"}
            # Missing request_id and timestamp
        }
        with pytest.raises(ValidationError):
            ErrorResponse(**data)


class TestValidationErrorResponse:
    """Test validation error response schema"""
    
    def test_validation_error_response_valid(self):
        """Test creating a valid validation error response"""
        data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": [
                    {
                        "field": "title",
                        "issue": "Field is required",
                        "value": None
                    }
                ]
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        validation_error = ValidationErrorResponse(**data)
        assert validation_error.error["code"] == "VALIDATION_ERROR"
        assert validation_error.error["message"] == "Validation failed"
        assert len(validation_error.error["details"]) == 1
        assert validation_error.error["details"][0]["field"] == "title"
    
    def test_validation_error_response_with_example(self):
        """Test validation error response with example data"""
        data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": [
                    {
                        "field": "email",
                        "issue": "Invalid email format",
                        "value": "invalid-email"
                    }
                ]
            },
            "request_id": "req_abcdef123456",
            "timestamp": datetime.now(timezone.utc)
        }
        validation_error = ValidationErrorResponse(**data)
        assert validation_error.error["code"] == "VALIDATION_ERROR"
        assert validation_error.error["details"][0]["field"] == "email"


class TestNotFoundErrorResponse:
    """Test not found error response schema"""
    
    def test_not_found_error_response_valid(self):
        """Test creating a valid not found error response"""
        data = {
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Resource not found",
                "details": {
                    "resource": "list",
                    "id": "550e8400-e29b-41d4-a716-446655440000"
                }
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        not_found_error = NotFoundErrorResponse(**data)
        assert not_found_error.error["code"] == "RESOURCE_NOT_FOUND"
        assert not_found_error.error["message"] == "Resource not found"
        assert not_found_error.error["details"]["resource"] == "list"
    
    def test_not_found_error_response_with_example(self):
        """Test not found error response with example data"""
        data = {
            "error": {
                "code": "RESOURCE_NOT_FOUND",
                "message": "Resource not found",
                "details": {
                    "resource": "task",
                    "id": "660e8400-e29b-41d4-a716-446655440000"
                }
            },
            "request_id": "req_abcdef123456",
            "timestamp": datetime.now(timezone.utc)
        }
        not_found_error = NotFoundErrorResponse(**data)
        assert not_found_error.error["code"] == "RESOURCE_NOT_FOUND"
        assert not_found_error.error["details"]["resource"] == "task"


class TestAuthErrorResponse:
    """Test authentication error response schema"""
    
    def test_auth_error_response_valid(self):
        """Test creating a valid authentication error response"""
        data = {
            "error": {
                "code": "AUTH_REQUIRED",
                "message": "Authentication required",
                "details": {
                    "header": "Authorization",
                    "format": "Bearer <token>"
                }
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        auth_error = AuthErrorResponse(**data)
        assert auth_error.error["code"] == "AUTH_REQUIRED"
        assert auth_error.error["message"] == "Authentication required"
        assert auth_error.error["details"]["header"] == "Authorization"
    
    def test_auth_error_response_with_example(self):
        """Test authentication error response with example data"""
        data = {
            "error": {
                "code": "AUTH_REQUIRED",
                "message": "Authentication required",
                "details": {
                    "header": "Authorization",
                    "format": "Bearer <token>",
                    "reason": "Token expired"
                }
            },
            "request_id": "req_abcdef123456",
            "timestamp": datetime.now(timezone.utc)
        }
        auth_error = AuthErrorResponse(**data)
        assert auth_error.error["code"] == "AUTH_REQUIRED"
        assert auth_error.error["details"]["reason"] == "Token expired"


class TestRateLimitErrorResponse:
    """Test rate limit error response schema"""
    
    def test_rate_limit_error_response_valid(self):
        """Test creating a valid rate limit error response"""
        data = {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded",
                "details": {
                    "limit": 1000,
                    "reset_time": "2024-12-01T11:00:00Z",
                    "retry_after": 3600
                }
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        rate_limit_error = RateLimitErrorResponse(**data)
        assert rate_limit_error.error["code"] == "RATE_LIMIT_EXCEEDED"
        assert rate_limit_error.error["message"] == "Rate limit exceeded"
        assert rate_limit_error.error["details"]["limit"] == 1000
        assert rate_limit_error.error["details"]["retry_after"] == 3600
    
    def test_rate_limit_error_response_with_example(self):
        """Test rate limit error response with example data"""
        data = {
            "error": {
                "code": "RATE_LIMIT_EXCEEDED",
                "message": "Rate limit exceeded",
                "details": {
                    "limit": 500,
                    "reset_time": "2024-12-01T12:00:00Z",
                    "retry_after": 1800,
                    "current_usage": 500
                }
            },
            "request_id": "req_abcdef123456",
            "timestamp": datetime.now(timezone.utc)
        }
        rate_limit_error = RateLimitErrorResponse(**data)
        assert rate_limit_error.error["code"] == "RATE_LIMIT_EXCEEDED"
        assert rate_limit_error.error["details"]["limit"] == 500
        assert rate_limit_error.error["details"]["current_usage"] == 500


class TestErrorResponseSerialization:
    """Test error response serialization"""
    
    def test_error_response_to_dict(self):
        """Test converting error response to dictionary"""
        timestamp = datetime.now(timezone.utc)
        data = {
            "error": {
                "code": "TEST_ERROR",
                "message": "Test error message",
                "details": {"field": "test"}
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": timestamp
        }
        error_response = ErrorResponse(**data)
        error_dict = error_response.model_dump()
        
        assert error_dict["error"]["code"] == "TEST_ERROR"
        assert error_dict["error"]["message"] == "Test error message"
        assert error_dict["request_id"] == "req_1234567890abcdef"
        assert error_dict["timestamp"] == timestamp
    
    def test_validation_error_response_to_dict(self):
        """Test converting validation error response to dictionary"""
        timestamp = datetime.now(timezone.utc)
        data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Validation failed",
                "details": [
                    {
                        "field": "title",
                        "issue": "Field is required",
                        "value": None
                    }
                ]
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": timestamp
        }
        validation_error = ValidationErrorResponse(**data)
        error_dict = validation_error.model_dump()
        
        assert error_dict["error"]["code"] == "VALIDATION_ERROR"
        assert len(error_dict["error"]["details"]) == 1
        assert error_dict["error"]["details"][0]["field"] == "title"
        assert error_dict["error"]["details"][0]["issue"] == "Field is required"


class TestErrorResponseValidation:
    """Test error response validation edge cases"""
    
    def test_error_response_empty_error_details(self):
        """Test error response with empty error details"""
        data = {
            "error": {
                "code": "TEST_ERROR",
                "message": "Test error message",
                "details": {}
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        error_response = ErrorResponse(**data)
        assert error_response.error["details"] == {}
    
    def test_validation_error_response_multiple_errors(self):
        """Test validation error response with multiple validation errors"""
        data = {
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Multiple validation errors",
                "details": [
                    {
                        "field": "title",
                        "issue": "Field is required",
                        "value": None
                    },
                    {
                        "field": "email",
                        "issue": "Invalid email format",
                        "value": "invalid-email"
                    }
                ]
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        validation_error = ValidationErrorResponse(**data)
        assert len(validation_error.error["details"]) == 2
        assert validation_error.error["details"][0]["field"] == "title"
        assert validation_error.error["details"][1]["field"] == "email"
    
    def test_error_response_without_optional_fields(self):
        """Test error response without optional fields in details"""
        data = {
            "error": {
                "code": "TEST_ERROR",
                "message": "Test error message",
                "details": {
                    "resource": "list"
                }
            },
            "request_id": "req_1234567890abcdef",
            "timestamp": datetime.now(timezone.utc)
        }
        error_response = ErrorResponse(**data)
        assert error_response.error["details"]["resource"] == "list" 