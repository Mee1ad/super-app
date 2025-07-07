# Best Practices

## Overview

This guide provides best practices for integrating with the LifeHub API effectively, securely, and efficiently.

## Authentication & Security

### 1. Secure Token Management

**✅ Good Practices:**
```javascript
// Store tokens in environment variables
const token = process.env.LIFEHUB_API_TOKEN;

// Use secure token rotation
const refreshToken = async () => {
  const newToken = await api.post('/auth/refresh', { refresh_token });
  process.env.LIFEHUB_API_TOKEN = newToken.access_token;
};
```

**❌ Avoid:**
```javascript
// Never hardcode tokens
const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...";

// Don't store tokens in localStorage for production
localStorage.setItem('token', token);
```

### 2. HTTPS Only

Always use HTTPS for production requests:

```javascript
// ✅ Good
const api = axios.create({
  baseURL: 'https://api.lifehub.com/v1'
});

// ❌ Bad
const api = axios.create({
  baseURL: 'http://api.lifehub.com/v1'
});
```

### 3. Token Scope Limitation

Request only the permissions you need:

```javascript
// Request minimal permissions
const scopes = ['read:lists', 'write:lists'];
const token = await generateToken(scopes);
```

## Error Handling

### 1. Comprehensive Error Handling

```javascript
const handleApiError = async (response) => {
  if (!response.ok) {
    const error = await response.json();
    
    switch (response.status) {
      case 401:
        // Handle authentication errors
        await refreshToken();
        break;
      case 429:
        // Handle rate limiting
        const retryAfter = response.headers.get('Retry-After');
        await new Promise(resolve => setTimeout(resolve, retryAfter * 1000));
        break;
      case 422:
        // Handle validation errors
        console.error('Validation errors:', error.error.details);
        break;
      default:
        // Handle other errors
        console.error('API Error:', error.error.message);
    }
  }
};
```

### 2. Retry Logic

Implement exponential backoff for retries:

```javascript
const retryWithBackoff = async (fn, maxRetries = 3) => {
  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      if (error.status === 429) {
        const retryAfter = error.headers.get('Retry-After') || Math.pow(2, i) * 1000;
        await new Promise(resolve => setTimeout(resolve, retryAfter));
      } else if (error.status >= 500 && i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, Math.pow(2, i) * 1000));
      } else {
        throw error;
      }
    }
  }
};
```

## Data Management

### 1. Efficient Pagination

```javascript
const getAllLists = async () => {
  const allLists = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await api.get('/lists', {
      params: { page, limit: 100 }
    });
    
    allLists.push(...response.data.data);
    hasMore = response.data.meta.page < response.data.meta.pages;
    page++;
  }
  
  return allLists;
};
```

### 2. Batch Operations

Use bulk operations when possible:

```javascript
// ✅ Good: Bulk reorder
await api.put(`/lists/${listId}/tasks/reorder`, {
  item_ids: [task1Id, task2Id, task3Id]
});

// ❌ Avoid: Individual updates
for (const taskId of taskIds) {
  await api.put(`/lists/${listId}/tasks/${taskId}`, { position: i++ });
}
```

### 3. Optimistic Updates

Implement optimistic updates for better UX:

```javascript
const toggleTask = async (taskId, optimisticChecked) => {
  // Optimistically update UI
  updateTaskInUI(taskId, { checked: optimisticChecked });
  
  try {
    // Make API call
    const response = await api.put(`/lists/${listId}/tasks/${taskId}/toggle`);
    // Update with actual response
    updateTaskInUI(taskId, response.data);
  } catch (error) {
    // Revert on error
    updateTaskInUI(taskId, { checked: !optimisticChecked });
    throw error;
  }
};
```

## Performance Optimization

### 1. Request Caching

Implement intelligent caching:

```javascript
const cache = new Map();

const getListWithCache = async (listId) => {
  const cacheKey = `list_${listId}`;
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < 5 * 60 * 1000) {
    return cached.data;
  }
  
  const response = await api.get(`/lists/${listId}`);
  cache.set(cacheKey, {
    data: response.data,
    timestamp: Date.now()
  });
  
  return response.data;
};
```

### 2. Debounced Search

```javascript
const debouncedSearch = debounce(async (query) => {
  if (query.length < 2) return;
  
  const response = await api.get('/search', {
    params: { q: query }
  });
  
  updateSearchResults(response.data);
}, 300);
```

### 3. Efficient Data Fetching

```javascript
// ✅ Good: Fetch only what you need
const getListSummary = async (listId) => {
  const response = await api.get(`/lists/${listId}`, {
    params: { fields: 'id,title,type,task_count' }
  });
  return response.data;
};

// ❌ Avoid: Fetching unnecessary data
const getListSummary = async (listId) => {
  const response = await api.get(`/lists/${listId}/tasks`);
  return {
    id: listId,
    task_count: response.data.length
  };
};
```

## Code Organization

### 1. API Client Structure

```javascript
// api/client.js
class LifeHubAPI {
  constructor(token) {
    this.client = axios.create({
      baseURL: 'https://api.lifehub.com/v1',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
      }
    });
    
    this.setupInterceptors();
  }
  
  setupInterceptors() {
    this.client.interceptors.response.use(
      response => response,
      error => this.handleError(error)
    );
  }
  
  async handleError(error) {
    if (error.response?.status === 401) {
      await this.refreshToken();
      return this.client.request(error.config);
    }
    throw error;
  }
  
  // List methods
  async getLists(params = {}) {
    return this.client.get('/lists', { params });
  }
  
  async createList(data) {
    return this.client.post('/lists', data);
  }
  
  // Task methods
  async getTasks(listId, params = {}) {
    return this.client.get(`/lists/${listId}/tasks`, { params });
  }
  
  async createTask(listId, data) {
    return this.client.post(`/lists/${listId}/tasks`, data);
  }
}
```

### 2. Type Safety

```typescript
// types/api.ts
interface List {
  id: string;
  title: string;
  type: 'task' | 'shopping';
  variant: 'default' | 'outlined' | 'filled';
  created_at: string;
  updated_at: string;
}

interface Task {
  id: string;
  list_id: string;
  title: string;
  description?: string;
  checked: boolean;
  variant: 'default' | 'outlined' | 'filled';
  position: number;
  created_at: string;
  updated_at: string;
}

interface APIResponse<T> {
  data: T;
  meta?: {
    total: number;
    page: number;
    limit: number;
  };
}
```

## Testing

### 1. Unit Testing

```javascript
// tests/api.test.js
describe('LifeHub API', () => {
  let api;
  
  beforeEach(() => {
    api = new LifeHubAPI('test-token');
  });
  
  test('should create a list', async () => {
    const mockResponse = { data: { id: '123', title: 'Test List' } };
    jest.spyOn(api.client, 'post').mockResolvedValue(mockResponse);
    
    const result = await api.createList({ title: 'Test List', type: 'task' });
    
    expect(result.data.title).toBe('Test List');
    expect(api.client.post).toHaveBeenCalledWith('/lists', {
      title: 'Test List',
      type: 'task'
    });
  });
});
```

### 2. Integration Testing

```javascript
// tests/integration.test.js
describe('API Integration', () => {
  test('should create list and add tasks', async () => {
    // Create list
    const list = await api.createList({
      title: 'Integration Test List',
      type: 'task'
    });
    
    // Add task
    const task = await api.createTask(list.data.id, {
      title: 'Test Task'
    });
    
    // Verify
    const tasks = await api.getTasks(list.data.id);
    expect(tasks.data).toHaveLength(1);
    expect(tasks.data[0].title).toBe('Test Task');
  });
});
```

## Monitoring & Logging

### 1. Request Logging

```javascript
const api = axios.create({
  baseURL: 'https://api.lifehub.com/v1',
  headers: { 'Authorization': `Bearer ${token}` }
});

api.interceptors.request.use(config => {
  console.log(`[API] ${config.method.toUpperCase()} ${config.url}`);
  return config;
});

api.interceptors.response.use(
  response => {
    console.log(`[API] ${response.status} ${response.config.url}`);
    return response;
  },
  error => {
    console.error(`[API] Error ${error.response?.status} ${error.config?.url}:`, error.message);
    throw error;
  }
);
```

### 2. Performance Monitoring

```javascript
const measureApiCall = async (name, apiCall) => {
  const start = performance.now();
  try {
    const result = await apiCall();
    const duration = performance.now() - start;
    console.log(`[API] ${name} completed in ${duration.toFixed(2)}ms`);
    return result;
  } catch (error) {
    const duration = performance.now() - start;
    console.error(`[API] ${name} failed after ${duration.toFixed(2)}ms:`, error);
    throw error;
  }
};
```

## Common Patterns

### 1. CRUD Operations

```javascript
class ListManager {
  constructor(api) {
    this.api = api;
  }
  
  async create(title, type = 'task') {
    return this.api.createList({ title, type });
  }
  
  async read(id) {
    return this.api.getList(id);
  }
  
  async update(id, data) {
    return this.api.updateList(id, data);
  }
  
  async delete(id) {
    return this.api.deleteList(id);
  }
  
  async list(params = {}) {
    return this.api.getLists(params);
  }
}
```

### 2. Event-Driven Updates

```javascript
class ListSync {
  constructor(api) {
    this.api = api;
    this.listeners = new Map();
  }
  
  on(event, callback) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, []);
    }
    this.listeners.get(event).push(callback);
  }
  
  emit(event, data) {
    const callbacks = this.listeners.get(event) || [];
    callbacks.forEach(callback => callback(data));
  }
  
  async createList(data) {
    const result = await this.api.createList(data);
    this.emit('list:created', result.data);
    return result;
  }
}
```

## Security Checklist

- [ ] Use HTTPS for all API calls
- [ ] Store tokens securely (environment variables)
- [ ] Implement token rotation
- [ ] Request minimal permissions
- [ ] Validate all input data
- [ ] Handle errors gracefully
- [ ] Log security events
- [ ] Keep dependencies updated
- [ ] Use rate limiting on client side
- [ ] Implement proper CORS handling

## Performance Checklist

- [ ] Implement request caching
- [ ] Use pagination for large datasets
- [ ] Optimize bundle size
- [ ] Use compression (gzip)
- [ ] Implement retry logic
- [ ] Monitor API response times
- [ ] Use bulk operations when possible
- [ ] Implement optimistic updates
- [ ] Debounce search requests
- [ ] Cache frequently accessed data

---

*For more detailed information, see the [API Reference](./endpoints/) or contact [support@lifehub.com](mailto:support@lifehub.com).* 