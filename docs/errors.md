# Error Handling

## Overview

LifeHub API uses standard HTTP status codes and provides detailed error messages to help you identify and resolve issues quickly. All error responses follow a consistent format.

## Error Response Format

All error responses include a standard structure:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field": "title",
      "issue": "Field is required"
    },
    "request_id": "req_1234567890abcdef",
    "timestamp": "2024-12-01T10:00:00Z"
  }
}
```

## HTTP Status Codes

### 2xx Success
- **200 OK** - Request successful
- **201 Created** - Resource created successfully
- **204 No Content** - Request successful, no response body

### 4xx Client Errors
- **400 Bad Request** - Invalid request syntax or parameters
- **401 Unauthorized** - Authentication required or failed
- **403 Forbidden** - Authenticated but not authorized
- **404 Not Found** - Resource not found
- **409 Conflict** - Resource conflict (e.g., duplicate entry)
- **422 Unprocessable Entity** - Validation errors
- **429 Too Many Requests** - Rate limit exceeded

### 5xx Server Errors
- **500 Internal Server Error** - Unexpected server error
- **502 Bad Gateway** - Upstream service error
- **503 Service Unavailable** - Service temporarily unavailable

## Common Error Codes

### Authentication Errors

#### `AUTH_REQUIRED`
- **Status**: 401
- **Message**: "Authentication required"
- **Solution**: Include valid Authorization header

```json
{
  "error": {
    "code": "AUTH_REQUIRED",
    "message": "Authentication required",
    "details": {
      "header": "Authorization",
      "format": "Bearer <token>"
    }
  }
}
```

#### `INVALID_TOKEN`
- **Status**: 401
- **Message**: "Invalid or expired token"
- **Solution**: Refresh your authentication token

#### `INSUFFICIENT_PERMISSIONS`
- **Status**: 403
- **Message**: "Insufficient permissions for this resource"
- **Solution**: Check your account permissions

### Validation Errors

#### `VALIDATION_ERROR`
- **Status**: 422
- **Message**: "Validation failed"
- **Details**: Field-specific validation errors

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Validation failed",
    "details": [
      {
        "field": "title",
        "issue": "Field is required",
        "value": null
      },
      {
        "field": "email",
        "issue": "Invalid email format",
        "value": "invalid-email"
      }
    ]
  }
}
```

### Resource Errors

#### `RESOURCE_NOT_FOUND`
- **Status**: 404
- **Message**: "Resource not found"
- **Details**: Resource type and ID

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Resource not found",
    "details": {
      "resource": "task",
      "id": "550e8400-e29b-41d4-a716-446655440000"
    }
  }
}
```

#### `RESOURCE_CONFLICT`
- **Status**: 409
- **Message**: "Resource conflict"
- **Details**: Conflict description

### Rate Limiting

#### `RATE_LIMIT_EXCEEDED`
- **Status**: 429
- **Message**: "Rate limit exceeded"
- **Headers**: Rate limit information

```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded",
    "details": {
      "limit": 1000,
      "reset_time": "2024-12-01T11:00:00Z",
      "retry_after": 3600
    }
  }
}
```

## Field-Specific Validation Rules

### List Fields
- **title**: Required, 1-255 characters
- **type**: Required, must be "task" or "shopping"
- **variant**: Optional, must be "default", "outlined", or "filled"

### Task Fields
- **title**: Required, 1-255 characters
- **description**: Optional, max 1000 characters
- **checked**: Boolean, defaults to false
- **position**: Integer, defaults to 0

### Shopping Item Fields
- **title**: Required, 1-255 characters
- **url**: Optional, valid URL format, max 500 characters
- **price**: Optional, max 50 characters
- **source**: Optional, max 255 characters

## UUID Format Validation

All UUID parameters must follow the standard format:
```
xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
```

Example valid UUID: `550e8400-e29b-41d4-a716-446655440000`

## Error Handling Best Practices

### 1. Always Check Status Codes
```javascript
const response = await fetch('/api/v1/lists', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}` },
  body: JSON.stringify(data)
});

if (!response.ok) {
  const error = await response.json();
  console.error('API Error:', error.error.message);
}
```

### 2. Handle Rate Limiting
```javascript
if (response.status === 429) {
  const retryAfter = response.headers.get('Retry-After');
  await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
  // Retry request
}
```

### 3. Validate Input Before Sending
```javascript
// Validate required fields
if (!data.title || data.title.length > 255) {
  throw new Error('Invalid title');
}
```

### 4. Use Request IDs for Support
```javascript
const error = await response.json();
console.log('Request ID:', error.error.request_id);
// Include this ID when contacting support
```

## Retry Logic

### Automatic Retries
- **5xx errors**: Retry with exponential backoff
- **429 errors**: Retry after `Retry-After` header
- **Network errors**: Retry up to 3 times

### Manual Retry Example
```javascript
async function retryRequest(fn, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429) {
        const retryAfter = error.headers.get('Retry-After') || 60;
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
      } else if (error.status >= 500 && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
      } else {
        throw error;
      }
    }
  }
}
```

## Support

When contacting support, include:
- **Request ID**: From error response
- **HTTP Status Code**: From response
- **Error Code**: From error response
- **Request Details**: Method, URL, headers, body
- **Timestamp**: When the error occurred

---

*For more information, see the [API Reference](./endpoints/) or contact [support@lifehub.com](mailto:support@lifehub.com).* 