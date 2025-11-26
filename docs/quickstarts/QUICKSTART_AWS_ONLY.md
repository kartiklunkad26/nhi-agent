# Quick Start - AWS Only Testing (No Vault)

Simplified testing instructions focusing only on AWS IAM identities.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed (for frontend)
- OpenAI API key
- AWS credentials configured

## Step 1: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv

# Verify installation
uv --version
```

## Step 2: Setup Frontend

```bash
cd ui
npm install
```

## Step 3: Configure Environment Variables

Create a `.env` file in the project root (same level as `requirements.txt`):

```env
# API Server Configuration
API_PORT=8000
CORS_ORIGINS=http://localhost:8080

# AWS Configuration (choose one option)
# Option 1: Use AWS Profile (recommended if you have AWS CLI configured)
AWS_PROFILE=default
AWS_REGION=us-east-1

# Option 2: Use AWS Access Keys directly
# AWS_ACCESS_KEY_ID=your-access-key-id
# AWS_SECRET_ACCESS_KEY=your-secret-access-key
# AWS_REGION=us-east-1

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here

# Vault Configuration - NOT NEEDED (skip this)
# VAULT_ADDR=
# VAULT_TOKEN=
```

Create a `.env` file in the `ui/` directory (optional):

```env
# API URL (defaults to http://localhost:8000 if not set)
VITE_API_URL=http://localhost:8000
```

## Step 4: Verify AWS Credentials

Before starting, make sure your AWS credentials work:

```bash
# Test AWS CLI (if using AWS Profile)
aws sts get-caller-identity

# Or verify environment variables are set
echo $AWS_ACCESS_KEY_ID
echo $AWS_SECRET_ACCESS_KEY
```

## Step 5: Start the API Server with uvx

In Terminal 1 (from project root):

```bash
# Run the API server directly with uvx
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich \
    --with typer     python -m src.api_server

# Or use the helper script:
# ./run_api_uvx.sh  (macOS/Linux)
# run_api_uvx.bat   (Windows)
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Note:** The first time you run this, `uvx` will download and cache the dependencies. This may take a minute or two.

## Step 6: Start the Frontend

In Terminal 2 (from `ui/` directory):

```bash
cd ui
npm run dev
```

You should see:
```
VITE v5.x.x  ready in XXX ms
➜  Local:   http://localhost:8080/
```

## Step 7: Verify Setup

Check the API health endpoint:

```bash
curl http://localhost:8000/api/health
```

Or visit: http://localhost:8000/api/health

Expected response:
```json
{
  "status": "healthy",
  "aws_configured": true,
  "openai_configured": true
}
```

Note: the response shows whether shared AWS credentials and your OpenAI key are configured. If either value is `false`, double-check your `.env` file before continuing.

## Step 8: Test AWS Identities

### Test 1: Search for AWS IAM Roles

In the web UI search bar (http://localhost:8080), type:
```
Show all AWS IAM roles
```

**Expected Result:**
- List of AWS IAM roles displayed as cards
- Each card shows role name, type ("aws"), and metadata

### Test 2: Search for AWS Users

In the web UI search bar, type:
```
List all AWS IAM users
```

**Expected Result:**
- List of AWS IAM users displayed
- Shows user names and associated metadata

### Test 3: Ask AWS Security Question

In the web UI search bar, type:
```
What security concerns exist in my AWS identities?
```

**Expected Result:**
- AI analysis of security risks in your AWS identities
- Specific recommendations
- Potential issues identified

### Test 4: Get Identity Summary

In the web UI search bar, type:
```
Summarize all my AWS identities
```

**Expected Result:**
- Overview of all AWS identities
- Counts by type (users, roles, groups)
- Key patterns and relationships

### Test 5: Specific Query

In the web UI search bar, type:
```
How many IAM roles do I have and what are their purposes?
```

**Expected Result:**
- Count of IAM roles
- Description of each role's purpose
- Analysis of role usage

## Step 9: Test API Endpoints Directly

### Test 1: Health Check

```bash
curl http://localhost:8000/api/health
```

### Test 2: Collect AWS Identities

```bash
curl -X POST http://localhost:8000/api/identities/collect \
  -H "Content-Type: application/json"
```

**Expected Response:**
```json
{
  "success": true,
  "identities": {
    "aws": {
      "users": [...],
      "roles": [...],
      "groups": [...]
    },
    "vault": [],
    "total_count": 25
  },
  "summary": {
    "total_count": 25,
    "aws_users": 10,
    "aws_roles": 15,
    "aws_groups": 0,
    "vault_identities": 0
  }
}
```

Note: `vault` will be empty and `vault_identities` will be 0, which is expected.

### Test 3: Search Identities

```bash
curl -X POST http://localhost:8000/api/identities/search \
  -H "Content-Type: application/json" \
  -d '{"query": "Show all AWS IAM roles"}'
```

### Test 4: Ask a Question

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How many AWS IAM users do I have?", "model": "gpt-4o-mini"}'
```

## Troubleshooting

### AWS MCP Server Not Working

If you see errors about AWS MCP server:

```bash
# Verify uvx can run the AWS MCP server
uvx awslabs.iam-mcp-server@latest --help

# Check AWS credentials
aws sts get-caller-identity

# Verify AWS region is set
echo $AWS_REGION
```

### "No identities found"

1. **Check AWS credentials in `.env`:**
   ```bash
   cat .env | grep AWS
   ```

2. **Test AWS credentials manually:**
   ```bash
   # If using AWS Profile
   aws iam list-users --profile default
   
   # If using access keys
   export AWS_ACCESS_KEY_ID=your-key
   export AWS_SECRET_ACCESS_KEY=your-secret
   aws iam list-users
   ```

3. **Check API server logs** for MCP connection errors

### API Connection Errors

```bash
# Verify API server is running
curl http://localhost:8000/api/health

# Check if port 8000 is in use
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows
```

### OpenAI API Errors

```bash
# Verify API key is set
cat .env | grep OPENAI_API_KEY

# Test API key (if you have curl)
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

## What You'll See

- ✅ AWS IAM users, roles, and groups
- ✅ AI-powered analysis of your AWS identities
- ✅ Security risk assessments
- ✅ Natural language search and querying
- ❌ No Vault identities (expected - we're not using Vault)

## Expected Results

After completing these tests, you should be able to:

- ✅ Collect identities from AWS IAM
- ✅ Search AWS identities using natural language
- ✅ Get AI-powered analysis of your AWS identities
- ✅ Identify security concerns in AWS configurations
- ✅ Query AWS identity metadata

## Next Steps

1. Explore the API docs: http://localhost:8000/docs
2. Try more complex AWS queries
3. Review security recommendations
4. Use the CLI tool for automation

## Adding Vault Later

If you want to add Vault testing later, just:

1. Add to `.env`:
   ```env
   VAULT_ADDR=https://your-vault-server.com
   VAULT_TOKEN=your-vault-token
   ```

2. Restart the API server

3. The app will automatically collect from both AWS and Vault!
