# Replicache Cookie/LastMutationID Synchronization Fix

## Problem Description
The frontend was receiving this error:
```
Error: name=todo-replicache-flat "pull" "requestID=r0a7kv2t8r1adkrhra-dd162a22-0" "handlePullResponse: cookie null did not change, but lastMutationIDChanges is not empty"
```

This occurred because the backend pull endpoint was returning `cookie: null` while also returning `lastMutationID` values, which violates Replicache's expectation that when the cookie doesn't change, there should be no `lastMutationIDChanges` in the response.

## Root Cause
The backend Replicache endpoints were returning `cookie: null` in both pull and push responses, but also returning `lastMutationIDChanges` with actual values. According to Replicache's protocol, when the cookie doesn't change, there should be no `lastMutationIDChanges`.

## Solution Implemented

### 1. Cookie Management Functions
Added two core functions in `apps/replicache/endpoints.py`:

```python
def create_cookie(user_id: str, client_id: str, last_mutation_id: int, client_name: str) -> str:
    """Create a cookie with current state information"""
    cookie_data = {
        "lastMutationID": last_mutation_id,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),  # milliseconds
        "userId": user_id,
        "clientId": client_id,
        "clientName": client_name
    }
    return json.dumps(cookie_data)

def parse_cookie(cookie: Optional[str]) -> Optional[Dict[str, Any]]:
    """Parse a cookie string into a dictionary"""
    if not cookie:
        return None
    try:
        return json.loads(cookie)
    except (json.JSONDecodeError, TypeError):
        logger.warning(f"Failed to parse cookie: {cookie}")
        return None
```

### 2. Updated Pull Endpoint
Modified the pull endpoint to:
- Create a proper cookie with current state information
- Return empty `lastMutationIDChanges` when no changes occur
- Parse incoming cookies for validation

```python
# Create cookie with current state
cookie = create_cookie(user_id, client_id, last_mutation_id, client_name)

# Check if we have any changes to report
has_changes = bool(last_mutation_id_changes) or bool(patch)

# If no changes, return empty lastMutationIDChanges to avoid Replicache error
if not has_changes:
    last_mutation_id_changes = {}

return {
    "lastMutationIDChanges": last_mutation_id_changes,
    "cookie": cookie,
    "patch": patch
}
```

### 3. Updated Push Endpoint
Modified the push endpoint to:
- Create a proper cookie with updated state information
- Parse incoming cookies for validation
- Return the updated cookie

```python
# Create cookie with updated state
cookie = create_cookie(user_id, client_id, last_mutation_id, client_name)

return {
    "lastMutationIDChanges": last_mutation_id_changes,
    "cookie": cookie
}
```

### 4. Cookie Structure
The cookie contains the following information:
```json
{
  "lastMutationID": 123,
  "timestamp": 1703123456789,
  "userId": "user123",
  "clientId": "client456",
  "clientName": "todo-replicache-flat"
}
```

### 5. Consistency Logic
- When no changes occur, `lastMutationIDChanges` is set to an empty object `{}`
- When changes occur, the cookie reflects the current state
- The cookie changes when the state changes (mutation ID increases)
- Timestamps ensure cookies are unique even with the same mutation ID

## Testing
Created comprehensive tests in `tests/test_replicache_cookie_sync.py` that verify:
- Cookie creation with proper structure
- Cookie parsing (valid and invalid cases)
- Cookie consistency logic
- Different cookies for different clients/users/names
- Timestamp updates

All tests pass successfully.

## Expected Response Format
The endpoints now return responses in this format:

**Pull Response:**
```json
{
  "lastMutationIDChanges": {},
  "cookie": "{\"lastMutationID\":123,\"timestamp\":1703123456789,\"userId\":\"user123\",\"clientId\":\"client456\",\"clientName\":\"todo-replicache-flat\"}",
  "patch": []
}
```

**Push Response:**
```json
{
  "lastMutationIDChanges": {"client456": 124},
  "cookie": "{\"lastMutationID\":124,\"timestamp\":1703123456789,\"userId\":\"user123\",\"clientId\":\"client456\",\"clientName\":\"todo-replicache-flat\"}"
}
```

## Benefits
1. **Fixes the Replicache error** - No more "cookie null did not change, but lastMutationIDChanges is not empty"
2. **Proper state tracking** - Cookies reflect the current state and change when state changes
3. **Consistency** - When no changes occur, no `lastMutationIDChanges` are returned
4. **Validation** - Incoming cookies can be parsed and validated
5. **Debugging** - Cookie structure provides useful debugging information

## Files Modified
- `apps/replicache/endpoints.py` - Added cookie functions and updated endpoints
- `tests/test_replicache_cookie_sync.py` - Added comprehensive tests

The fix ensures that Replicache's synchronization protocol is properly followed, eliminating the frontend error and providing robust state management. 