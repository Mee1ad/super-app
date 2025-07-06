# CORS Troubleshooting Guide

## Overview
This guide helps prevent and resolve CORS (Cross-Origin Resource Sharing) issues in the LifeHub API.

## Current Configuration
- **Allowed Origins**: `http://localhost:3000`, `http://127.0.0.1:3000`
- **Allowed Methods**: GET, POST, PUT, DELETE, OPTIONS, PATCH
- **Allowed Headers**: All headers (`*`)
- **Credentials**: Enabled

## Prevention Measures

### 1. Pre-Startup Validation
Run the validation script before starting the server:
```bash
python scripts/validate_cors.py
```

### 2. Automated Testing
Run CORS tests to ensure configuration works:
```bash
pytest tests/test_cors.py -v
```

### 3. Version Compatibility Check
Ensure your Esmerald version supports CORSConfig:
```bash
python -c "from esmerald import CORSConfig; print('CORSConfig available')"
```

## Common Issues & Solutions

### Issue 1: ModuleNotFoundError for CORSConfig
**Error**: `ModuleNotFoundError: No module named 'esmerald.config'`

**Solution**: 
- Use direct import: `from esmerald import CORSConfig`
- Check Esmerald version: `pip show esmerald`

### Issue 2: AttributeError with model_dump
**Error**: `AttributeError: 'dict' object has no attribute 'model_dump'`

**Solution**:
- Use `CORSConfig` class instead of dict
- Ensure proper import: `from esmerald import CORSConfig`

### Issue 3: CORS Headers Missing
**Error**: `No 'Access-Control-Allow-Origin' header is present`

**Solution**:
1. Verify CORS configuration in `main.py`
2. Check if `cors_config` is properly set
3. Restart the server after changes

### Issue 4: Frontend Still Blocked
**Error**: CORS policy blocks requests from frontend

**Solution**:
1. Verify frontend origin is in `allow_origins`
2. Check browser console for specific CORS errors
3. Test with curl/Postman to isolate issue

## Testing CORS Configuration

### Manual Testing
```bash
# Test preflight request
curl -X OPTIONS http://localhost:8000/api/lists \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: Content-Type" \
  -v

# Test actual request
curl -X GET http://localhost:8000/api/lists \
  -H "Origin: http://localhost:3000" \
  -v
```

### PowerShell Testing
```powershell
# Test preflight
Invoke-WebRequest -Uri "http://localhost:8000/api/lists" -Method OPTIONS -Headers @{
    "Origin"="http://localhost:3000"
    "Access-Control-Request-Method"="GET"
}

# Test actual request
Invoke-WebRequest -Uri "http://localhost:8000/api/lists" -Method GET -Headers @{
    "Origin"="http://localhost:3000"
}
```

## Configuration Files

### main.py
```python
from esmerald import Esmerald, Gateway, get, CORSConfig

cors_config = CORSConfig(
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*"],
    max_age=3600,
)

app = Esmerald(
    # ... routes ...
    cors_config=cors_config,
    # ... other config ...
)
```

## Environment-Specific Issues

### Development
- Use `http://localhost:3000` for frontend
- Ensure both frontend and backend are running
- Check for port conflicts

### Production
- Update `allow_origins` with production domains
- Consider using environment variables
- Implement proper security headers

## Debugging Steps

1. **Check Server Logs**: Look for CORS-related errors
2. **Browser DevTools**: Check Network tab for CORS headers
3. **Validation Script**: Run `python scripts/validate_cors.py`
4. **Test Endpoints**: Use curl/Postman to test API directly
5. **Check Versions**: Ensure compatible versions of all packages

## Emergency Fallback

If CORS issues persist, use this minimal configuration:
```python
from esmerald import Esmerald, Gateway, get

app = Esmerald(
    routes=[...],
    cors_config={
        "allow_origins": ["*"],  # WARNING: Only for development
        "allow_credentials": False,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
)
```

## Support

If issues persist:
1. Check this troubleshooting guide
2. Run validation scripts
3. Review server logs
4. Test with minimal configuration
5. Check Esmerald documentation for your version 