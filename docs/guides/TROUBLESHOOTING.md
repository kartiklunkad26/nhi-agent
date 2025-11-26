# Troubleshooting "Failed to Fetch" Error

## Quick Fix Checklist

### 1. Is the API Server Running?

**Check if API server is running:**
```bash
curl http://localhost:8000/api/health
```

**If you get "Connection refused" or no response:**

Start the API server:
```bash
# Using uvx (no virtual environment)
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich \
    --with typer \
    python -m src.api_server

# Or using the helper script
./run_api_uvx.sh
```

**Verify it's running:**
```bash
# Should return JSON response
curl http://localhost:8000/api/health
```

**You should get JSON response:**
```json
{"status":"healthy","aws_configured":true,"openai_configured":true}
```

### 2. Check Browser Console

Open browser DevTools (F12) and check:
- **Console tab**: Look for detailed error messages
- **Network tab**: See if the request is being made and what error you get

Common errors:
- `Failed to fetch` = API server not running or CORS issue
- `CORS policy` = CORS configuration issue
- `404 Not Found` = Wrong API endpoint URL
- `500 Internal Server Error` = Backend error

### 3. Verify API URL

Check your frontend `.env` file in `ui/` directory:

```env
VITE_API_URL=http://localhost:8000
```

**If `.env` doesn't exist**, the frontend defaults to `http://localhost:8000`, which should work.

**Test the API URL manually:**
```bash
# From terminal
curl http://localhost:8000/api/health

# Should return:
# {"status":"healthy","aws_configured":true,...}
```

### 4. Check CORS Configuration

Verify your `.env` file in project root has:

```env
CORS_ORIGINS=http://localhost:8080
```

**If frontend is on a different port**, update it:
```env
CORS_ORIGINS=http://localhost:8080,http://localhost:3000
```

### 5. Port Conflicts

**Check if port 8000 is in use:**
```bash
# macOS/Linux
lsof -i :8000

# Windows
netstat -ano | findstr :8000
```

**If port is in use**, either:
- Stop the other process
- Change API_PORT in `.env`:
  ```env
  API_PORT=8001
  ```
- Update frontend `.env`:
  ```env
  VITE_API_URL=http://localhost:8001
  ```

### 6. Check API Server Logs

When you start the API server, look for:
- ✅ `Uvicorn running on http://0.0.0.0:8000` = Good
- ❌ `Address already in use` = Port conflict
- ❌ `ModuleNotFoundError` = Missing dependencies
- ❌ `ImportError` = Wrong Python path

### 7. Verify Dependencies

If using uvx, make sure all dependencies are listed:

```bash
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich \
    --with typer \
    python -m src.api_server
```

### 8. Test API Directly

**Test the API endpoint directly:**
```bash
# Health check
curl http://localhost:8000/api/health

# Search endpoint (should work even if AWS credentials are missing)
curl -X POST http://localhost:8000/api/identities/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

If curl works but browser doesn't, it's likely a CORS issue.

## Common Solutions

### Solution 1: API Server Not Started
```bash
# Start API server in one terminal
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich \
    --with typer \
    python -m src.api_server

# Start frontend in another terminal
cd ui && npm run dev
```

### Solution 2: CORS Issue
Add to `.env` in project root:
```env
CORS_ORIGINS=http://localhost:8080,http://127.0.0.1:8080
```

Restart API server.

### Solution 3: Wrong Port
Check what port frontend is actually using:
- Look at the Vite output: `Local: http://localhost:XXXX`
- Update `.env` CORS_ORIGINS to match

### Solution 4: Network/Firewall
- Try `http://127.0.0.1:8000` instead of `http://localhost:8000`
- Check if firewall is blocking localhost connections

## Debug Steps

1. **Start API server** and verify it's running:
   ```bash
   curl http://localhost:8000/api/health
   ```

2. **Check browser console** for detailed error

3. **Check Network tab** in DevTools to see the actual request

4. **Test API directly** with curl to isolate if it's a frontend issue

5. **Verify .env files** are correct and in the right locations

## Still Not Working?

Share:
1. Error message from browser console
2. Output from `curl http://localhost:8000/api/health`
3. API server startup logs
4. Browser Network tab screenshot (if possible)
