# Quick Fix: "Failed to Fetch" Error

## The Problem
The "failed to fetch" error means your frontend can't connect to the API server. This usually happens because **the API server isn't running**.

## Quick Solution

### Step 1: Start the API Server

Open a terminal and run:

```bash
# Navigate to project root
cd /Users/kartiklunkad/workspace/nhi-agent

# Start API server with uvx (quoted to handle square brackets)
uvx --with fastapi \
    --with "uvicorn[standard]" \
    --with python-dotenv \
    --with openai \
    --with boto3 \
    --with httpx \
    --with rich \
    --with typer \
    python -m src.api_server
```

**OR use the helper script:**
```bash
./run_api_uvx.sh
```

**You should see:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 2: Verify API is Running

In another terminal, test it:

```bash
curl http://localhost:8000/api/health
```

**You should get JSON response:**
```json
{"status":"healthy","aws_configured":true,"openai_configured":true}
```

### Step 3: Refresh Your Browser

Go back to http://localhost:8080 and try searching again.

## Fix for "no matches found: uvicorn[standard]"

This error happens because zsh (macOS default shell) interprets square brackets. **Solution: Quote the package name:**

```bash
# Use quotes around uvicorn[standard]
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich \
    --with typer     python -m src.api_server
```

**OR use the helper script:**
```bash
./run_api_uvx.sh
```

## If It Still Doesn't Work

### Check 1: Is Frontend Running?
```bash
# Make sure frontend is running on port 8080
cd ui
npm run dev
```

### Check 2: Verify Ports
- API server should be on port **8000**
- Frontend should be on port **8080**

### Check 3: Check Browser Console
1. Open DevTools (F12)
2. Go to Console tab
3. Look for the exact error message
4. Go to Network tab
5. Try the search again
6. See what request fails and what error it shows

### Check 4: Test API Directly
```bash
# Test search endpoint
curl -X POST http://localhost:8000/api/identities/search \
  -H "Content-Type: application/json" \
  -d '{"query": "test"}'
```

If this works but browser doesn't, it's likely a CORS issue.

## Common Issues

### Issue: Port 8000 Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Kill it or change API_PORT in .env
```

### Issue: Missing Dependencies
Make sure uvx has all dependencies (quoted):
```bash
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich \
    --with typer     python -m src.api_server
```

### Issue: CORS Error
Check your `.env` file has:
```env
CORS_ORIGINS=http://localhost:8080
```

## Still Stuck?

Run these commands and share the output:

```bash
# 1. Check if API is running
curl http://localhost:8000/api/health

# 2. Check ports
lsof -i :8000
lsof -i :8080

# 3. Check .env file
cat .env | grep -E "(API_PORT|CORS_ORIGINS|OPENAI)"
```
