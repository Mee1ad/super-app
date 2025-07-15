# Changelog User API

This document describes the API endpoints for:
- Fetching the latest changelog entries for a user
- Marking changelog entries as seen (viewed) by the user

---

## 1. Get Latest Changelog Entries (for User)

**Endpoint:**
```http
GET /api/v1/changelog/latest?limit=10
Authorization: Bearer <access_token>
```

**Description:**
- Returns the most recent published changelog entries (latest version) for the user to view.
- No user-specific filtering is applied; all users see the same latest changelog.

**Query Parameters:**
- `limit` (optional): Maximum number of entries to return (default: 10)

**Response Example:**
```json
{
  "entries": [
    {
      "id": "entry-uuid",
      "title": "New Feature Added",
      "description": "Added user authentication system",
      "version": "1.2.0",
      "change_type": "added",
      "is_published": true,
      "release_date": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 5,
  "latest_version": "1.2.0"
}
```

**Usage Notes:**
- Call this endpoint when you want to show the latest changelog to the user (e.g., in a modal or notification).
- You can use the `version` or `release_date` fields to determine if the user has already seen this version.

---

## 2. Mark Changelog Entry as Seen (Viewed)

**Endpoint:**
```http
POST /api/v1/changelog/mark-viewed
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "entry_id": "entry-uuid",
  "user_identifier": "user-uuid-or-username"
}
```

**Description:**
- Records that the user has seen (viewed) a specific changelog entry.
- The `user_identifier` can be the user's ID, username, or email (should be unique per user).

**Request Body:**
- `entry_id` (string): The ID of the changelog entry the user has seen
- `user_identifier` (string): The unique identifier for the user

**Response Example:**
```json
{
  "message": "Changelog entry marked as viewed"
}
```

**Usage Notes:**
- Call this endpoint after the user closes the changelog modal or marks an entry as read.
- You can call it for each entry, or for all entries in the latest version.
- This allows you to track which users have seen which changelog entries (for analytics or notification purposes).

---

## 3. Example Workflow

1. **Frontend fetches latest changelog:**
    - `GET /api/v1/changelog/latest?limit=10`
2. **User views the changelog modal/page.**
3. **Frontend marks entries as seen:**
    - For each entry (or all at once), call `POST /api/v1/changelog/mark-viewed` with the user's identifier.

---

## 4. Security & Permissions
- Both endpoints require a valid JWT access token in the `Authorization` header.
- Only authenticated users can mark changelog entries as seen.

---

## 5. Example Frontend Usage (JavaScript)

```javascript
// Fetch latest changelog
const response = await fetch('/api/v1/changelog/latest?limit=10', {
  headers: { 'Authorization': `Bearer ${accessToken}` }
});
const data = await response.json();

// Mark as seen
await fetch('/api/v1/changelog/mark-viewed', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${accessToken}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    entry_id: entryId,
    user_identifier: userId
  })
});
```

---

## 6. Summary Table

| Endpoint                              | Method | Description                        |
|---------------------------------------|--------|------------------------------------|
| `/api/v1/changelog/latest`            | GET    | Get latest changelog entries       |
| `/api/v1/changelog/mark-viewed`       | POST   | Mark changelog entry as seen       | 