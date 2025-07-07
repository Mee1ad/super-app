# API Overview

## Introduction

LifeHub API is a comprehensive REST API for managing todo lists and shopping lists. Built with modern Python technologies including Esmerald framework and Edgy ORM, it provides a robust, scalable solution for personal and team productivity management.

## Key Features

### 🎯 Core Functionality
- **Todo Lists**: Create, manage, and organize tasks with priorities and due dates
- **Shopping Lists**: Track shopping items with prices, sources, and URLs
- **Real-time Updates**: WebSocket support for live collaboration
- **Search & Filter**: Powerful search across all content types
- **Bulk Operations**: Efficient batch processing for large datasets

### 🔧 Technical Features
- **RESTful Design**: Standard HTTP methods and status codes
- **JSON API**: Consistent request/response format
- **Pagination**: Efficient data retrieval with cursor-based pagination
- **Rate Limiting**: Fair usage policies with clear limits
- **CORS Support**: Cross-origin resource sharing enabled
- **OpenAPI 3.0**: Complete API specification with interactive docs

## Architecture

### Technology Stack
- **Framework**: Esmerald (ASGI-based)
- **ORM**: Edgy (async database operations)
- **Database**: PostgreSQL (primary), Redis (caching)
- **Authentication**: JWT tokens with refresh mechanism
- **Documentation**: OpenAPI 3.0 with Swagger UI

### API Structure
```
/api/v1/
├── /lists          # List management
├── /lists/{id}/tasks     # Task operations
├── /lists/{id}/items     # Shopping item operations
├── /search         # Global search
├── /auth           # Authentication
└── /webhooks       # Event notifications
```

## Data Models

### Core Entities
1. **List**: Container for tasks or shopping items
   - Types: `task`, `shopping`
   - Variants: `default`, `outlined`, `filled`

2. **Task**: Individual todo items
   - Properties: title, description, checked status, position
   - Features: due dates, priorities, tags

3. **ShoppingItem**: Shopping list entries
   - Properties: title, price, source, URL
   - Features: price tracking, source management

## Response Format

All API responses follow a consistent JSON structure:

```json
{
  "data": {
    // Response data here
  },
  "meta": {
    "timestamp": "2024-12-01T10:00:00Z",
    "version": "1.0.0"
  }
}
```

## Status Codes

- `200` - Success
- `201` - Created
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `422` - Validation Error
- `429` - Rate Limited
- `500` - Internal Server Error

## Rate Limits

- **Free Tier**: 1,000 requests/hour
- **Pro Tier**: 10,000 requests/hour
- **Enterprise**: Custom limits

Rate limit headers are included in all responses:
- `X-RateLimit-Limit`: Request limit per window
- `X-RateLimit-Remaining`: Remaining requests
- `X-RateLimit-Reset`: Reset time (Unix timestamp)

## Security

- **HTTPS Only**: All API calls must use HTTPS
- **JWT Authentication**: Bearer token authentication
- **CORS**: Configured for web applications
- **Input Validation**: Comprehensive request validation
- **SQL Injection Protection**: Parameterized queries

## Getting Started

1. **Sign Up**: Create an account at [lifehub.com](https://lifehub.com)
2. **Get API Key**: Generate your API key in the dashboard
3. **Make First Request**: Follow the [Getting Started Guide](./getting-started.md)
4. **Explore**: Use the interactive API docs at `/docs`

## Support & Community

- **Documentation**: This site and interactive API docs
- **SDKs**: Official libraries for Python, JavaScript, and more
- **Community**: Discord server for developers
- **Support**: Email support for technical issues

---

*For detailed endpoint documentation, see the [API Reference](./endpoints/).* 