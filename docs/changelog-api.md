# Changelog API Documentation

## Overview

The Changelog API provides endpoints for managing and displaying changelog entries. The system uses a unified approach that tracks all users (both anonymous and authenticated) using hashed IP addresses and User-Agent strings for privacy protection.

## Key Features

- **Unified Tracking**: All users are tracked using hashed IP + User-Agent, regardless of authentication status
- **Privacy Protection**: IP addresses and User-Agent strings are hashed with salts before storage
- **Version-based Display**: Users only see changelog entries for versions they haven't seen before
- **Automatic Processing**: Git commits can be automatically processed into changelog entries using AI
- **Role-based Access**: Different permissions for viewing, publishing, and managing changelog entries

## Authentication & Permissions

The API uses role-based access control with the following permissions:

- `CHANGELOG_VIEW`: View changelog entries (public)
- `CHANGELOG_CREATE`: Create new changelog entries (admin/editor)
- `CHANGELOG_UPDATE`: Update existing entries (admin/editor)
- `CHANGELOG_DELETE`: Delete entries (admin/editor)
- `CHANGELOG_PUBLISH`: Publish draft entries (admin only)

## Core Endpoints

### 1. Get Changelog Status

Check if a user should see changelog based on their view history.

**Endpoint:** `GET /api/v1/changelog/status`

**Parameters:**
- `ip_address` (required): User's IP address
- `user_agent` or `userAgent` (required): User's browser User-Agent string

**Response:**
```json
{
  "should_show": true,
  "latest_version": "1.2.0",
  "user_version": "1.1.0",
  "has_new_content": true
}
```

### 2. Get Latest Changelog for User

Get the latest changelog entries for a user. **First checks if hashed data exists in the database - if it does, returns empty response immediately.**

**Endpoint:** `GET /api/v1/changelog/latest`

**Parameters:**
- `ip_address` (required): User's IP address
- `user_agent` or `userAgent` (required): User's browser User-Agent string
- `limit` (optional): Number of entries to return (default: 10)

**Response:**
```json
{
  "entries": [
    {
      "id": "uuid",
      "title": "New Feature Added",
      "description": "Description of the change",
      "change_type": "feature",
      "version": "1.2.0",
      "release_date": "2024-01-15T10:00:00Z",
      "is_breaking": false,
      "is_published": true
    }
  ],
  "total": 1,
  "latest_version": "1.2.0",
  "user_version": null,
  "has_new_content": true,
  "reason": "new_user"
}
```

**Empty Response (when user has seen changelog before):**
```json
{
  "entries": [],
  "total": 0,
  "latest_version": "1.2.0",
  "user_version": "1.2.0",
  "has_new_content": false,
  "reason": "user_already_seen"
}
```

**Reason Values:**
- `new_user`: User has never seen changelog before (shows entries)
- `user_already_seen`: User has seen changelog before (empty response)
- `no_latest_version`: No changelog entries exist
- `error`: An error occurred

### 3. Mark Changelog as Viewed

Mark that a user has viewed the changelog (updates their latest version seen).

**Endpoint:** `POST /api/v1/changelog/viewed`

**Request Body:**
```json
{
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Response:**
```json
{
  "message": "Changelog marked as viewed"
}
```

### 4. Debug User Views

Debug endpoint to check user views in database (development only).

**Endpoint:** `GET /api/v1/changelog/debug`

**Parameters:**
- `ip_address` (required): User's IP address
- `user_agent` or `userAgent` (required): User's browser User-Agent string

**Response:**
```json
{
  "ip_address": "192.168.1...",
  "user_agent": "Mozilla/5.0...",
  "hashed_ip": "a1b2c3d4...",
  "hashed_user_agent": "e5f6g7h8...",
  "latest_version": "1.2.0",
  "total_views": 1,
  "views": [
    {
      "id": "uuid",
      "latest_version_seen": "1.2.0",
      "view_count": 3,
      "first_seen": "2024-01-15T10:00:00Z",
      "last_seen": "2024-01-15T11:00:00Z"
    }
  ]
}
```

## Frontend Usage Examples

### React Example

```jsx
import React, { useState, useEffect } from 'react';

const ChangelogModal = () => {
  const [changelog, setChangelog] = useState(null);
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    checkChangelog();
  }, []);

  const checkChangelog = async () => {
    try {
      // Get user's IP and User-Agent
      const ipResponse = await fetch('https://api.ipify.org?format=json');
      const { ip } = await ipResponse.json();
      const userAgent = navigator.userAgent;

      // Check if user should see changelog
      const statusResponse = await fetch(
        `/api/v1/changelog/status?ip_address=${ip}&user_agent=${encodeURIComponent(userAgent)}`
      );
      const status = await statusResponse.json();

      if (status.should_show) {
        // Get changelog entries
        const changelogResponse = await fetch(
          `/api/v1/changelog/latest?ip_address=${ip}&user_agent=${encodeURIComponent(userAgent)}`
        );
        const changelogData = await changelogResponse.json();
        
        // Check the reason for the response
        if (changelogData.reason === 'new_user' && changelogData.entries.length > 0) {
          setChangelog(changelogData);
          setShowModal(true);
        } else if (changelogData.reason === 'user_already_seen') {
          console.log('User has already seen the changelog');
          // Don't show modal - user has seen it before
        } else {
          console.log('No new changelog content:', changelogData.reason);
        }
      }
    } catch (error) {
      console.error('Error checking changelog:', error);
    }
  };

  const markAsViewed = async () => {
    try {
      const ipResponse = await fetch('https://api.ipify.org?format=json');
      const { ip } = await ipResponse.json();
      const userAgent = navigator.userAgent;

      await fetch('/api/v1/changelog/viewed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ ip_address: ip, user_agent: userAgent })
      });

      setShowModal(false);
    } catch (error) {
      console.error('Error marking as viewed:', error);
    }
  };

  if (!showModal || !changelog) return null;

  return (
    <div className="changelog-modal">
      <div className="changelog-content">
        <h2>What's New in v{changelog.latest_version}</h2>
        <div className="changelog-entries">
          {changelog.entries.map(entry => (
            <div key={entry.id} className={`changelog-entry ${entry.change_type}`}>
              <h3>{entry.title}</h3>
              <p>{entry.description}</p>
              {entry.is_breaking && <span className="breaking-badge">Breaking Change</span>}
            </div>
          ))}
        </div>
        <button onClick={markAsViewed}>Got it!</button>
      </div>
    </div>
  );
};

export default ChangelogModal;
```

### Vue.js Example

```vue
<template>
  <div v-if="showModal" class="changelog-modal">
    <div class="changelog-content">
      <h2>What's New in v{{ changelog?.latest_version }}</h2>
      <div class="changelog-entries">
        <div 
          v-for="entry in changelog?.entries" 
          :key="entry.id" 
          :class="['changelog-entry', entry.change_type]"
        >
          <h3>{{ entry.title }}</h3>
          <p>{{ entry.description }}</p>
          <span v-if="entry.is_breaking" class="breaking-badge">Breaking Change</span>
        </div>
      </div>
      <button @click="markAsViewed">Got it!</button>
    </div>
  </div>
</template>

<script>
export default {
  data() {
    return {
      changelog: null,
      showModal: false
    };
  },
  async mounted() {
    await this.checkChangelog();
  },
  methods: {
    async checkChangelog() {
      try {
        // Get user's IP and User-Agent
        const ipResponse = await fetch('https://api.ipify.org?format=json');
        const { ip } = await ipResponse.json();
        const userAgent = navigator.userAgent;

        // Check if user should see changelog
        const statusResponse = await fetch(
          `/api/v1/changelog/status?ip_address=${ip}&user_agent=${encodeURIComponent(userAgent)}`
        );
        const status = await statusResponse.json();

        if (status.should_show) {
          // Get changelog entries
          const changelogResponse = await fetch(
            `/api/v1/changelog/latest?ip_address=${ip}&user_agent=${encodeURIComponent(userAgent)}`
          );
          const changelogData = await changelogResponse.json();
          
          // Check the reason for the response
          if (changelogData.reason === 'new_user' && changelogData.entries.length > 0) {
            this.changelog = changelogData;
            this.showModal = true;
          } else if (changelogData.reason === 'user_already_seen') {
            console.log('User has already seen the changelog');
            // Don't show modal - user has seen it before
          } else {
            console.log('No new changelog content:', changelogData.reason);
          }
        }
      } catch (error) {
        console.error('Error checking changelog:', error);
      }
    },
    async markAsViewed() {
      try {
        const ipResponse = await fetch('https://api.ipify.org?format=json');
        const { ip } = await ipResponse.json();
        const userAgent = navigator.userAgent;

        await fetch('/api/v1/changelog/viewed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ ip_address: ip, user_agent: userAgent })
        });

        this.showModal = false;
      } catch (error) {
        console.error('Error marking as viewed:', error);
      }
    }
  }
};
</script>
```

## CSS Styling

```css
.changelog-modal {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.changelog-content {
  background: white;
  border-radius: 8px;
  padding: 24px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.changelog-entries {
  margin: 20px 0;
}

.changelog-entry {
  padding: 16px;
  margin: 12px 0;
  border-radius: 6px;
  border-left: 4px solid #ddd;
}

.changelog-entry.feature {
  background: #f0f9ff;
  border-left-color: #3b82f6;
}

.changelog-entry.bugfix {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.changelog-entry.improvement {
  background: #f0fdf4;
  border-left-color: #22c55e;
}

.breaking-badge {
  background: #dc2626;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
  margin-left: 8px;
}

.changelog-content button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 500;
}

.changelog-content button:hover {
  background: #2563eb;
}
```

## Configuration

The system uses the following configuration settings:

```python
# In your settings file
IP_SALT = "your-secure-ip-salt-here"
USER_AGENT_SALT = "your-secure-ua-salt-here"
```

## Privacy Considerations

1. **Data Minimization**: Only hashed values are stored, never raw IP addresses or User-Agent strings
2. **Salt Protection**: Each hash uses a unique salt for additional security
3. **No Personal Data**: No personally identifiable information is stored
4. **Automatic Cleanup**: Consider implementing data retention policies
5. **Transparency**: Update your privacy policy to mention changelog tracking

## Best Practices

1. **Error Handling**: Always handle API errors gracefully in frontend code
2. **Loading States**: Show loading indicators while checking changelog status
3. **Fallback**: Provide fallback behavior if changelog API is unavailable
4. **Performance**: Cache changelog status to avoid repeated API calls
5. **Accessibility**: Ensure changelog modal is keyboard accessible and screen reader friendly
6. **Mobile**: Test changelog display on mobile devices
7. **Analytics**: Monitor changelog view rates and user engagement

## Troubleshooting

### Common Issues

1. **404 Errors**: Ensure you're using the correct endpoint paths
2. **Validation Errors**: Check that `ip_address` and `user_agent` parameters are provided
3. **Empty Responses**: This is normal if user has already seen the latest version
4. **Hash Mismatches**: Ensure salts are consistent across deployments

### Debug Endpoint

Use the debug endpoint to inspect user views in the database:

```bash
curl "http://localhost:8000/api/v1/changelog/debug?ip_address=192.168.1.1&user_agent=Mozilla/5.0..."
```

This will show you the hashed values and view history for debugging purposes. 