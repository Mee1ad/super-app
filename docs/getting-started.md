# Getting Started

## Quick Start Guide

Get up and running with the LifeHub API in minutes.

## Prerequisites

- A LifeHub account ([Sign up here](https://lifehub.com))
- Basic knowledge of HTTP and JSON
- Your preferred programming language or tool

## Step 1: Create Your Account

1. Visit [lifehub.com](https://lifehub.com)
2. Click "Sign Up" and create your account
3. Verify your email address

## Step 2: Generate Your API Token

1. Log into your LifeHub dashboard
2. Navigate to **Settings** → **API Tokens**
3. Click **Generate New Token**
4. Copy the token immediately (it won't be shown again)

**Important**: Keep your token secure and never share it publicly.

## Step 3: Make Your First Request

### Using cURL

```bash
curl -X GET \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  https://api.lifehub.com/v1/lists
```

### Using JavaScript/Node.js

```javascript
const axios = require('axios');

const api = axios.create({
  baseURL: 'https://api.lifehub.com/v1',
  headers: {
    'Authorization': `Bearer ${process.env.LIFEHUB_API_TOKEN}`,
    'Content-Type': 'application/json'
  }
});

// Get all lists
const response = await api.get('/lists');
console.log(response.data);
```

### Using Python

```python
import requests
import os

headers = {
    'Authorization': f'Bearer {os.environ["LIFEHUB_API_TOKEN"]}',
    'Content-Type': 'application/json'
}

response = requests.get(
    'https://api.lifehub.com/v1/lists',
    headers=headers
)

print(response.json())
```

## Step 4: Create Your First List

### Create a Todo List

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Todo List",
    "type": "task",
    "variant": "default"
  }' \
  https://api.lifehub.com/v1/lists
```

### Create a Shopping List

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Grocery Shopping",
    "type": "shopping",
    "variant": "outlined"
  }' \
  https://api.lifehub.com/v1/lists
```

## Step 5: Add Items to Your List

### Add a Task

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Learn LifeHub API",
    "description": "Read the documentation and try the examples"
  }' \
  https://api.lifehub.com/v1/lists/LIST_ID/tasks
```

### Add a Shopping Item

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Organic Bananas",
    "price": "$2.99",
    "source": "Whole Foods"
  }' \
  https://api.lifehub.com/v1/lists/LIST_ID/items
```

## Environment Setup

### Store Your Token Securely

#### Using Environment Variables

```bash
# Linux/macOS
export LIFEHUB_API_TOKEN="your_token_here"

# Windows (PowerShell)
$env:LIFEHUB_API_TOKEN="your_token_here"

# Windows (Command Prompt)
set LIFEHUB_API_TOKEN=your_token_here
```

#### Using .env File

Create a `.env` file in your project:

```env
LIFEHUB_API_TOKEN=your_token_here
```

Then load it in your application:

```javascript
// Node.js with dotenv
require('dotenv').config();
const token = process.env.LIFEHUB_API_TOKEN;
```

```python
# Python with python-dotenv
from dotenv import load_dotenv
load_dotenv()
token = os.environ["LIFEHUB_API_TOKEN"]
```

## Testing Your Setup

### Health Check

Test if the API is accessible:

```bash
curl https://api.lifehub.com/v1/ping
```

Expected response:
```json
{
  "message": "pong",
  "timestamp": "2024-12-01T10:00:00Z",
  "version": "1.0.0"
}
```

### Authentication Test

Test your authentication:

```bash
curl -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     https://api.lifehub.com/v1/lists
```

If successful, you'll get an array of lists (empty if you haven't created any yet).

## Common Issues

### 401 Unauthorized

**Problem**: Getting 401 errors
**Solution**: 
- Check that your token is correct
- Ensure you're using the `Bearer` prefix
- Verify the token hasn't expired

### 404 Not Found

**Problem**: Getting 404 errors
**Solution**:
- Check the URL is correct
- Ensure you're using the right HTTP method
- Verify the resource ID exists

### 422 Validation Error

**Problem**: Getting validation errors
**Solution**:
- Check required fields are provided
- Ensure field values meet length requirements
- Verify enum values are correct

## Next Steps

1. **Explore the API**: Use the interactive docs at `/docs`
2. **Read the Documentation**: Check out the [API Reference](./endpoints/)
3. **Join the Community**: Connect with other developers on [Discord](https://discord.gg/lifehub)
4. **Build Something**: Create your first integration

## Support

Need help? We're here for you:

- **Documentation**: [docs.lifehub.com](https://docs.lifehub.com)
- **Email**: [support@lifehub.com](mailto:support@lifehub.com)
- **Community**: [Discord](https://discord.gg/lifehub)
- **GitHub**: [API Examples](https://github.com/lifehub/api-examples)

---

*Ready to build? Check out the [API Reference](./endpoints/) for detailed endpoint documentation.* 