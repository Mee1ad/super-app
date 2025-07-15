# Anonymous Changelog Tracking System

This document describes the best practice implementation for tracking anonymous user changelog views with enhanced privacy protection and version-based logic.

## Overview

The anonymous changelog tracking system allows the application to:
- Track which anonymous users have seen changelog entries
- Show changelog only when there's new content
- Return empty changelog when user has seen the latest version
- Protect user privacy through separate hashed IP and user agent fields
- Provide analytics on changelog engagement

## Key Features

### Enhanced Privacy-First Design
- **Separate Hashed Fields**: Uses separate SHA-256 hashes for IP address and user agent
- **Individual Salts**: Each field has its own configurable salt for additional security
- **No Personal Data**: Never stores raw IP addresses or user agents
- **Composite Unique Constraint**: Uses combination of hashed IP and user agent for uniqueness

### Version-Based Logic
- **Latest Version Tracking**: Tracks the latest version seen by each anonymous user
- **Smart Display**: Only shows changelog when there's new content
- **Empty Response**: Returns empty changelog when user has seen latest version

### Analytics Support
- **View Count**: Tracks how many times each anonymous user has viewed changelog
- **Timestamps**: Records first and last seen times
- **Performance Indexes**: Optimized database queries with composite indexes

## API Endpoints

### 1. Get Anonymous Changelog Status

**Endpoint**: `GET /api/v1/changelog/anonymous/status`

**Query Parameters**:
- `ip_address` (string, required): User's IP address
- `user_agent` (string, required): User's browser user agent

**Response**:
```json
{
  "should_show": true,
  "latest_version": "1.2.0",
  "user_version": "1.1.0",
  "has_new_content": true
}
```

**Use Cases**:
- Check if user should see changelog notification
- Determine if there's new content available
- Get version comparison information

### 2. Get Latest Changelog for Anonymous User

**Endpoint**: `GET /api/v1/changelog/anonymous/latest`

**Query Parameters**:
- `ip_address` (string, required): User's IP address
- `user_agent` (string, required): User's browser user agent
- `limit` (integer, optional): Maximum entries to return (default: 10)

**Response**:
```json
{
  "entries": [
    {
      "id": "uuid",
      "version": "1.2.0",
      "title": "New Feature Added",
      "description": "Description of the new feature",
      "change_type": "added",
      "is_breaking": false,
      "release_date": "2024-01-15T10:00:00Z",
      "is_published": true
    }
  ],
  "total": 1,
  "latest_version": "1.2.0",
  "user_version": "1.1.0",
  "has_new_content": true
}
```

**Behavior**:
- Returns empty `entries` array if user has seen latest version
- Returns latest changelog entries if user hasn't seen them
- Includes version comparison information

### 3. Mark Anonymous Changelog as Viewed

**Endpoint**: `POST /api/v1/changelog/anonymous/viewed`

**Request Body**:
```json
{
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0..."
}
```

**Response**:
```json
{
  "message": "Anonymous changelog marked as viewed"
}
```

**Use Cases**:
- Call when user opens/closes changelog modal
- Update user's latest version seen
- Track engagement metrics

## Frontend Implementation

### React Example

```jsx
import React, { useState, useEffect } from 'react';

const ChangelogNotification = () => {
  const [changelog, setChangelog] = useState(null);
  const [showModal, setShowModal] = useState(false);
  
  // Get user's IP and user agent
  const getUserInfo = async () => {
    try {
      const response = await fetch('https://api.ipify.org?format=json');
      const data = await response.json();
      return {
        ip_address: data.ip,
        user_agent: navigator.userAgent
      };
    } catch (error) {
      console.error('Failed to get user info:', error);
      return null;
    }
  };
  
  // Check if user should see changelog
  const checkChangelogStatus = async () => {
    const userInfo = await getUserInfo();
    if (!userInfo) return;
    
    try {
      const response = await fetch(
        `/api/v1/changelog/anonymous/status?ip_address=${userInfo.ip_address}&user_agent=${encodeURIComponent(userInfo.user_agent)}`
      );
      const status = await response.json();
      
      if (status.should_show) {
        // Get changelog entries
        const changelogResponse = await fetch(
          `/api/v1/changelog/anonymous/latest?ip_address=${userInfo.ip_address}&user_agent=${encodeURIComponent(userInfo.user_agent)}`
        );
        const changelogData = await changelogResponse.json();
        setChangelog(changelogData);
      }
    } catch (error) {
      console.error('Failed to check changelog status:', error);
    }
  };
  
  // Mark as viewed
  const markAsViewed = async () => {
    const userInfo = await getUserInfo();
    if (!userInfo) return;
    
    try {
      await fetch('/api/v1/changelog/anonymous/viewed', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userInfo)
      });
      setShowModal(false);
    } catch (error) {
      console.error('Failed to mark as viewed:', error);
    }
  };
  
  useEffect(() => {
    checkChangelogStatus();
  }, []);
  
  if (!changelog || !changelog.has_new_content) {
    return null;
  }
  
  return (
    <>
      {/* Notification Badge */}
      <button 
        onClick={() => setShowModal(true)}
        className="changelog-notification"
      >
        <span className="badge">New</span>
        What's New in v{changelog.latest_version}
      </button>
      
      {/* Changelog Modal */}
      {showModal && (
        <div className="changelog-modal">
          <div className="modal-content">
            <h2>What's New in v{changelog.latest_version}</h2>
            <div className="changelog-entries">
              {changelog.entries.map(entry => (
                <div key={entry.id} className={`entry ${entry.change_type}`}>
                  <h3>{entry.title}</h3>
                  <p>{entry.description}</p>
                  {entry.is_breaking && (
                    <span className="breaking-badge">⚠️ Breaking Change</span>
                  )}
                </div>
              ))}
            </div>
            <button onClick={markAsViewed}>Got it!</button>
          </div>
        </div>
      )}
    </>
  );
};

export default ChangelogNotification;
```

### Vue.js Example

```vue
<template>
  <div>
    <!-- Notification Badge -->
    <button 
      v-if="changelog && changelog.has_new_content"
      @click="showModal = true"
      class="changelog-notification"
    >
      <span class="badge">New</span>
      What's New in v{{ changelog.latest_version }}
    </button>
    
    <!-- Changelog Modal -->
    <div v-if="showModal" class="changelog-modal">
      <div class="modal-content">
        <h2>What's New in v{{ changelog.latest_version }}</h2>
        <div class="changelog-entries">
          <div 
            v-for="entry in changelog.entries" 
            :key="entry.id"
            :class="['entry', entry.change_type]"
          >
            <h3>{{ entry.title }}</h3>
            <p>{{ entry.description }}</p>
            <span v-if="entry.is_breaking" class="breaking-badge">
              ⚠️ Breaking Change
            </span>
          </div>
        </div>
        <button @click="markAsViewed">Got it!</button>
      </div>
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
    await this.checkChangelogStatus();
  },
  
  methods: {
    async getUserInfo() {
      try {
        const response = await fetch('https://api.ipify.org?format=json');
        const data = await response.json();
        return {
          ip_address: data.ip,
          user_agent: navigator.userAgent
        };
      } catch (error) {
        console.error('Failed to get user info:', error);
        return null;
      }
    },
    
    async checkChangelogStatus() {
      const userInfo = await this.getUserInfo();
      if (!userInfo) return;
      
      try {
        const response = await fetch(
          `/api/v1/changelog/anonymous/status?ip_address=${userInfo.ip_address}&user_agent=${encodeURIComponent(userInfo.user_agent)}`
        );
        const status = await response.json();
        
        if (status.should_show) {
          const changelogResponse = await fetch(
            `/api/v1/changelog/anonymous/latest?ip_address=${userInfo.ip_address}&user_agent=${encodeURIComponent(userInfo.user_agent)}`
          );
          this.changelog = await changelogResponse.json();
        }
      } catch (error) {
        console.error('Failed to check changelog status:', error);
      }
    },
    
    async markAsViewed() {
      const userInfo = await this.getUserInfo();
      if (!userInfo) return;
      
      try {
        await fetch('/api/v1/changelog/anonymous/viewed', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(userInfo)
        });
        this.showModal = false;
      } catch (error) {
        console.error('Failed to mark as viewed:', error);
      }
    }
  }
};
</script>
```

## CSS Styling

```css
/* Notification Badge */
.changelog-notification {
  position: relative;
  padding: 8px 16px;
  background: #007bff;
  color: white;
  border: none;
  border-radius: 20px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}

.changelog-notification .badge {
  background: #dc3545;
  color: white;
  padding: 2px 6px;
  border-radius: 10px;
  font-size: 10px;
  font-weight: bold;
}

/* Modal */
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

.modal-content {
  background: white;
  padding: 24px;
  border-radius: 8px;
  max-width: 600px;
  max-height: 80vh;
  overflow-y: auto;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.modal-content h2 {
  margin: 0 0 20px 0;
  color: #333;
  border-bottom: 2px solid #007bff;
  padding-bottom: 10px;
}

/* Changelog Entries */
.changelog-entries {
  margin-bottom: 20px;
}

.entry {
  padding: 16px;
  margin-bottom: 16px;
  border-radius: 6px;
  border-left: 4px solid #007bff;
  background: #f8f9fa;
}

.entry.added {
  border-left-color: #28a745;
  background: #f8fff9;
}

.entry.changed {
  border-left-color: #ffc107;
  background: #fffef8;
}

.entry.fixed {
  border-left-color: #17a2b8;
  background: #f8fdff;
}

.entry.removed {
  border-left-color: #dc3545;
  background: #fff8f8;
}

.entry.deprecated {
  border-left-color: #6c757d;
  background: #f8f9fa;
}

.entry.security {
  border-left-color: #fd7e14;
  background: #fff8f5;
}

.entry h3 {
  margin: 0 0 8px 0;
  color: #333;
  font-size: 16px;
}

.entry p {
  margin: 0;
  color: #666;
  line-height: 1.5;
}

.breaking-badge {
  display: inline-block;
  background: #dc3545;
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  margin-top: 8px;
}

/* Modal Button */
.modal-content button {
  background: #007bff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.modal-content button:hover {
  background: #0056b3;
}
```

## Configuration

### Environment Variables

Add to your `.env` file:

```bash
# Salt for IP address hashing (change in production)
ANONYMOUS_IP_SALT=your_secure_random_ip_salt_here

# Salt for user agent hashing (change in production)
ANONYMOUS_USER_AGENT_SALT=your_secure_random_ua_salt_here
```

### Security Considerations

1. **Separate Salts**: Use different salts for IP and user agent hashing
2. **Salt Configuration**: Always change the default salts in production
3. **HTTPS Only**: Use HTTPS to protect user data in transit
4. **Rate Limiting**: Implement rate limiting on anonymous endpoints
5. **Data Retention**: Consider implementing data retention policies
6. **GDPR Compliance**: Ensure compliance with privacy regulations
7. **Salt Rotation**: Consider rotating salts periodically for enhanced security

## Database Schema

```sql
CREATE TABLE anonymous_changelog_views (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hashed_ip VARCHAR(64) NOT NULL,
    hashed_user_agent VARCHAR(64) NOT NULL,
    latest_version_seen VARCHAR(20) NOT NULL,
    first_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_seen TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    view_count INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(hashed_ip, hashed_user_agent)
);

-- Indexes for performance
CREATE INDEX idx_anonymous_changelog_views_hashed_ip 
ON anonymous_changelog_views(hashed_ip);

CREATE INDEX idx_anonymous_changelog_views_hashed_ua 
ON anonymous_changelog_views(hashed_user_agent);

CREATE INDEX idx_anonymous_changelog_views_composite 
ON anonymous_changelog_views(hashed_ip, hashed_user_agent);

CREATE INDEX idx_anonymous_changelog_views_last_seen 
ON anonymous_changelog_views(last_seen);
```

## Best Practices

1. **Call Status Endpoint First**: Check if user should see changelog before fetching entries
2. **Handle Errors Gracefully**: Don't break user experience if changelog service fails
3. **Cache User Info**: Cache IP address and user agent to avoid repeated API calls
4. **Progressive Enhancement**: Show changelog as enhancement, not critical feature
5. **Analytics Integration**: Track changelog engagement for product insights
6. **A/B Testing**: Test different changelog presentation styles
7. **Accessibility**: Ensure changelog modal is keyboard navigable and screen reader friendly

## Migration Guide

1. Run the database migration: `python -m db.migrate_incremental`
2. Update your frontend to use the new endpoints
3. Test with different user agents and IP addresses
4. Monitor database performance and adjust indexes if needed
5. Update your privacy policy to mention anonymous tracking 