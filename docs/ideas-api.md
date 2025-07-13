# Ideas API Documentation

## Overview

The Ideas API provides endpoints for managing ideas with categories and tags. It allows users to create, read, update, and delete ideas, as well as organize them using predefined categories.

## Features

- **Category Management**: Predefined categories with emojis for organizing ideas
- **Idea CRUD Operations**: Full create, read, update, delete functionality
- **Search & Filtering**: Search ideas by title and filter by category
- **Pagination**: Support for paginated results
- **Tagging System**: Add tags to ideas for better organization

## Database Schema

### Categories Table
```sql
CREATE TABLE categories (
    id VARCHAR(50) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    emoji VARCHAR(10) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Ideas Table
```sql
CREATE TABLE ideas (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    category_id VARCHAR(50) NOT NULL REFERENCES categories(id),
    tags JSONB DEFAULT '[]',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## API Endpoints

### Categories

#### GET /api/categories
Retrieve all available categories.

**Response:**
```json
{
  "categories": [
    {
      "id": "project",
      "name": "Project",
      "emoji": "🚀",
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

### Ideas

#### GET /api/ideas
Retrieve all ideas with optional filtering and pagination.

**Query Parameters:**
- `search` (optional): Search term to filter ideas by title
- `category` (optional): Category ID to filter ideas
- `page` (optional): Page number (default: 1)
- `limit` (optional): Items per page (default: 20, max: 100)

**Response:**
```json
{
  "ideas": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Build a habit tracker app",
      "description": "Simple app to track daily habits with streaks and analytics",
      "category": "project",
      "category_id": "project",
      "tags": ["react", "typescript", "productivity"],
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    }
  ],
  "meta": {
    "total": 1,
    "page": 1,
    "limit": 20,
    "pages": 1
  }
}
```

#### POST /api/ideas
Create a new idea.

**Request Body:**
```json
{
  "title": "Build a habit tracker app",
  "description": "Simple app to track daily habits with streaks and analytics",
  "category": "project",
  "tags": ["react", "typescript", "productivity"]
}
```

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Build a habit tracker app",
  "description": "Simple app to track daily habits with streaks and analytics",
  "category": "project",
  "category_id": "project",
  "tags": ["react", "typescript", "productivity"],
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-01T10:00:00Z"
}
```

#### GET /api/ideas/{idea_id}
Retrieve a specific idea by ID.

**Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Build a habit tracker app",
  "description": "Simple app to track daily habits with streaks and analytics",
  "category": "project",
  "category_id": "project",
  "tags": ["react", "typescript", "productivity"],
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-01T10:00:00Z"
}
```

#### PUT /api/ideas/{idea_id}
Update an existing idea.

**Request Body:**
```json
{
  "title": "Build an improved habit tracker app",
  "description": "Enhanced app to track daily habits with streaks, analytics, and reminders",
  "tags": ["react", "typescript", "productivity", "notifications"]
}
```

#### DELETE /api/ideas/{idea_id}
Delete an idea.

**Response:**
```json
{
  "message": "Idea deleted successfully"
}
```

## Predefined Categories

The system comes with the following predefined categories:

| ID | Name | Emoji |
|----|------|-------|
| project | Project | 🚀 |
| article | Article | 📝 |
| shopping | Shopping | 🛒 |
| learning | Learning | 📚 |
| personal | Personal | 👤 |
| work | Work | 💼 |

## Error Handling

The API uses standard HTTP status codes:

- `200`: Success
- `201`: Created
- `400`: Bad Request
- `401`: Unauthorized
- `404`: Not Found
- `422`: Validation Error
- `429`: Rate Limit Exceeded
- `500`: Internal Server Error

## Usage Examples

### Frontend Integration

Replace hardcoded data with API calls:

```javascript
// Instead of hardcoded categories
const categories = [
  { id: "project", name: "Project", emoji: "🚀" },
  // ...
];

// Use API call
const response = await fetch('/api/categories');
const { categories } = await response.json();

// Instead of hardcoded ideas
const ideas = [
  { id: 1, title: "Build a habit tracker app", /* ... */ },
  // ...
];

// Use API call with filtering
const response = await fetch('/api/ideas?category=project&search=habit');
const { ideas, meta } = await response.json();
```

### Creating a New Idea

```javascript
const newIdea = {
  title: "Learn React Hooks",
  description: "Study and practice React Hooks for better component management",
  category: "learning",
  tags: ["react", "javascript", "frontend"]
};

const response = await fetch('/api/ideas', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify(newIdea)
});

const createdIdea = await response.json();
```

## Migration

To set up the Ideas API:

1. Run the migration script:
   ```bash
   python db/migrate_ideas.py
   ```

2. This will:
   - Create the necessary database tables
   - Seed the predefined categories
   - Add sample ideas

## Testing

Test the API functionality:

```bash
python test_ideas_api.py
```

This will verify:
- Category creation and retrieval
- Idea creation and retrieval
- Filtering functionality
- Database connectivity 