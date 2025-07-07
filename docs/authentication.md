# Authentication

## Overview

LifeHub API uses JWT (JSON Web Token) authentication for secure access to protected endpoints. All API requests must include a valid authentication token in the Authorization header.

## Authentication Methods

### Bearer Token Authentication

The primary authentication method uses JWT Bearer tokens:

```http
Authorization: Bearer <your-jwt-token>
```

### API Key Authentication (Deprecated)

API keys are deprecated and will be removed in v2.0. Please migrate to JWT tokens.

## Getting Started

### 1. Create an Account

Sign up at [lifehub.com](https://lifehub.com) to create your account.

### 2. Generate API Token

1. Log into your LifeHub dashboard
2. Navigate to **Settings** → **API Tokens**
3. Click **Generate New Token**
4. Copy the token (it won't be shown again)

### 3. Use the Token

Include the token in your API requests:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     https://api.lifehub.com/v1/lists
```

## Token Management

### Token Structure

JWT tokens contain three parts:
- **Header**: Algorithm and token type
- **Payload**: Claims (user info, permissions, expiration)
- **Signature**: Verification signature

### Token Claims

```json
{
  "sub": "user_123456789",
  "email": "user@example.com",
  "permissions": ["read:lists", "write:lists"],
  "iat": 1640995200,
  "exp": 1641081600,
  "iss": "lifehub-api"
}
```

### Token Expiration

- **Access Tokens**: 24 hours
- **Refresh Tokens**: 30 days
- **API Tokens**: No expiration (until revoked)

## Security Best Practices

### 1. Secure Token Storage

```javascript
// ✅ Good: Store in secure environment variable
const token = process.env.LIFEHUB_API_TOKEN;

// ❌ Bad: Hardcode in source code
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";
```

### 2. Token Rotation

Rotate your tokens regularly:
- Generate new tokens every 90 days
- Revoke old tokens immediately
- Use different tokens for different environments

### 3. Scope Limitation

Request only the permissions you need:
- `read:lists` - Read-only access to lists
- `write:lists` - Full access to lists
- `admin:users` - User management (admin only)

### 4. HTTPS Only

Always use HTTPS for API requests:
```bash
# ✅ Good
curl https://api.lifehub.com/v1/lists

# ❌ Bad
curl http://api.lifehub.com/v1/lists
```

## Error Handling

### Common Authentication Errors

#### 401 Unauthorized
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

#### 401 Invalid Token
```json
{
  "error": {
    "code": "INVALID_TOKEN",
    "message": "Invalid or expired token",
    "details": {
      "reason": "token_expired"
    }
  }
}
```

#### 403 Insufficient Permissions
```json
{
  "error": {
    "code": "INSUFFICIENT_PERMISSIONS",
    "message": "Insufficient permissions for this resource",
    "details": {
      "required": "write:lists",
      "provided": "read:lists"
    }
  }
}
```

## Code Examples

### JavaScript/Node.js

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://api.lifehub.com/v1',
  headers: {
    'Authorization': `Bearer ${process.env.LIFEHUB_API_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Make authenticated request
const response = await api.get('/lists');
```

### Python

```python
import requests

headers = {
    'Authorization': f'Bearer {os.environ["LIFEHUB_API_TOKEN"]}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.lifehub.com/v1/lists',
    headers=headers
)
```

### cURL

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  https://api.lifehub.com/v1/lists
```

## Token Refresh

### Automatic Refresh

The API automatically handles token refresh when using the official SDKs.

### Manual Refresh

```javascript
// Check if token is expired
if (isTokenExpired(token)) {
  // Refresh token
  const newToken = await refreshToken(refreshToken);
  // Update stored token
  localStorage.setItem('lifehub_token', newToken);
}
```

## Rate Limiting

Authentication requests are subject to rate limiting:
- **Token Generation**: 10 requests per hour
- **Token Refresh**: 100 requests per hour
- **Failed Authentication**: 5 requests per minute

## Security Headers

The API includes security headers in all responses:

```http
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000; includeSubDomains
```

## Compliance

### GDPR Compliance

- Tokens can be revoked at any time
- User data is encrypted in transit and at rest
- Data retention policies are clearly defined

### SOC 2 Compliance

- Regular security audits
- Access logging and monitoring
- Incident response procedures

## Support

For authentication issues:

1. **Check Token Format**: Ensure proper Bearer token format
2. **Verify Token Validity**: Check if token is expired or revoked
3. **Review Permissions**: Ensure token has required permissions
4. **Contact Support**: Include request ID and error details

---

*For more information, see the [API Reference](./endpoints/) or contact [support@lifehub.com](mailto:support@lifehub.com).* 