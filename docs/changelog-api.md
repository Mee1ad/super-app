# Changelog API Documentation

## Overview

The Changelog API provides automated changelog generation using Git commits and DeepSeek AI. It fetches git commits, uses DeepSeek to humanize them into readable changelog entries, and tracks user views to show unread changes.

## Features

- **Automated Git Integration**: Fetches commits from the repository
- **AI-Powered Humanization**: Uses DeepSeek AI to convert technical commits into user-friendly changelog entries
- **Semantic Versioning**: Supports MAJOR.MINOR.PATCH versioning
- **Change Categorization**: Groups changes by type (Added, Changed, Fixed, Removed, etc.)
- **User View Tracking**: Tracks which changelog entries users have seen
- **Incremental Processing**: Only processes new commits since the last run
- **Breaking Change Detection**: Highlights breaking changes with ⚠️ or "Breaking:" prefix

## API Endpoints

### Get Changelog Entries
```
GET /api/v1/changelog
```

**Query Parameters:**
- `page` (int, default: 1): Page number
- `per_page` (int, default: 20, max: 100): Items per page
- `version` (string, optional): Filter by version
- `change_type` (string, optional): Filter by change type (added, changed, fixed, removed, deprecated, security)

**Response:**
```json
{
  "entries": [
    {
      "id": "uuid",
      "version": "1.2.0",
      "title": "Add user authentication",
      "description": "Implemented JWT-based authentication system with Google OAuth support",
      "change_type": "added",
      "is_breaking": false,
      "commit_hash": "abc123456789",
      "commit_date": "2024-01-15T10:30:00Z",
      "commit_message": "Add user authentication",
      "release_date": "2024-01-15T10:30:00Z",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "page": 1,
  "per_page": 20,
  "has_next": true,
  "has_prev": false
}
```

### Get Changelog Entry by ID
```
GET /api/v1/changelog/{entry_id}
```

**Response:**
```json
{
  "id": "uuid",
  "version": "1.2.0",
  "title": "Add user authentication",
  "description": "Implemented JWT-based authentication system with Google OAuth support",
  "change_type": "added",
  "is_breaking": false,
  "commit_hash": "abc123456789",
  "commit_date": "2024-01-15T10:30:00Z",
  "commit_message": "Add user authentication",
  "release_date": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

### Get Changelog Summary for Version
```
GET /api/v1/changelog/summary/{version}
```

**Response:**
```json
{
  "version": "1.2.0",
  "release_date": "2024-01-15T10:30:00Z",
  "total_changes": 15,
  "breaking_changes": 2,
  "changes_by_type": {
    "added": 8,
    "changed": 3,
    "fixed": 4
  },
  "entries": [...]
}
```

### Get Unread Changelog Entries
```
GET /api/v1/changelog/unread?user_identifier={identifier}
```

**Query Parameters:**
- `user_identifier` (string, required): User identifier (IP, user ID, or session)

**Response:**
```json
{
  "unread_count": 5,
  "latest_version": "1.2.0",
  "entries": [...]
}
```

### Mark Changelog Entry as Viewed
```
POST /api/v1/changelog/mark-viewed
```

**Request Body:**
```json
{
  "entry_id": "uuid",
  "user_identifier": "user-123"
}
```

**Response:**
```json
{
  "message": "Changelog entry marked as viewed"
}
```

### Process New Git Commits
```
POST /api/v1/changelog/process-commits
```

**Response:**
```json
{
  "message": "Successfully processed 3 new changelog entries",
  "created_count": 3
}
```

### Get Available Versions
```
GET /api/v1/changelog/versions
```

**Response:**
```json
{
  "versions": [
    {
      "version": "1.2.0",
      "release_date": "2024-01-15T10:30:00Z",
      "total_changes": 15,
      "breaking_changes": 2
    }
  ],
  "total_versions": 5
}
```

### Get Current Version
```
GET /api/v1/changelog/current-version
```

**Response:**
```json
{
  "version": "1.2.0",
  "source": "git_tags"
}
```

## Configuration

### Environment Variables

Add the following to your `.env` file:

```env
# DeepSeek AI API Key
DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

### Database Migration

Run the changelog migration to create the required tables:

```bash
python db/migrate_changelog.py
```

## Usage Examples

### Frontend Integration

```javascript
// Get unread changelog entries
const response = await fetch('/api/v1/changelog/unread?user_identifier=user-123');
const unreadData = await response.json();

if (unreadData.unread_count > 0) {
  // Show notification badge
  showNotificationBadge(unreadData.unread_count);
  
  // Display changelog modal
  showChangelogModal(unreadData.entries);
}

// Mark entry as viewed when user reads it
await fetch('/api/v1/changelog/mark-viewed', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    entry_id: 'entry-uuid',
    user_identifier: 'user-123'
  })
});
```

### Automated Processing

Set up a cron job or CI/CD pipeline to process new commits:

```bash
# Process new commits and create changelog entries
curl -X POST http://your-api/api/v1/changelog/process-commits
```

## Change Types

The API supports the following change types:

- **added**: New features or functionality
- **changed**: Changes to existing functionality
- **fixed**: Bug fixes
- **removed**: Removed features or functionality
- **deprecated**: Deprecated features (will be removed in future)
- **security**: Security-related changes

## Breaking Changes

Breaking changes are automatically detected and marked with:
- `is_breaking: true` in the API response
- ⚠️ emoji or "Breaking:" prefix in the title
- Special highlighting in the frontend

## Best Practices

1. **Regular Processing**: Run the process-commits endpoint regularly (e.g., on every deployment)
2. **User Identification**: Use consistent user identifiers (user ID, session ID, or IP)
3. **Version Management**: Use semantic versioning for your releases
4. **Commit Messages**: Write clear, descriptive commit messages for better AI processing
5. **Frontend Integration**: Show unread changelog notifications to keep users informed

## Error Handling

The API returns appropriate HTTP status codes:

- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Not found (entry not found)
- `500`: Internal server error

Error responses include a `detail` field with the error message:

```json
{
  "detail": "Failed to process commits: DeepSeek API error"
}
```

## Testing

Run the test script to verify functionality:

```bash
python test_changelog.py
```

This will test:
- Git service functionality
- DeepSeek service initialization
- Changelog service operations
- Database operations 