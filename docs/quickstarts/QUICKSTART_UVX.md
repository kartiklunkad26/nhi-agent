# Quick Start - Using uvx (No Virtual Environment Needed)

This is the fastest way to get started - no virtual environment, no pip installs, just run everything with `uvx`.

## Prerequisites

- Python 3.9+ installed
- Node.js 18+ installed
- OpenAI API key
- AWS credentials (optional, for AWS testing)
- Vault credentials (optional, for Vault testing)

## Step 1: Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip (if you have pip)
pip install uv

# Verify installation
uv --version
```

## Step 2: Frontend Setup

```bash
# Navigate to UI directory
cd ui

# Install Node.js dependencies
npm install
```

## Step 3: Configure Environment Variables

Create a `.env` file in the project root (same level as `requirements.txt`):

```env
# API Server Configuration
API_PORT=8000
CORS_ORIGINS=http://localhost:8080

# AWS Configuration (choose one option)
# Option 1: Use AWS Profile
AWS_PROFILE=default
AWS_REGION=us-east-1

# Option 2: Use AWS Access Keys
# AWS_ACCESS_KEY_ID=your-access-key-id
# AWS_SECRET_ACCESS_KEY=your-secret-access-key
# AWS_REGION=us-east-1

# Vault Configuration (optional - skip for AWS-only testing)
# VAULT_ADDR=https://your-vault-server.com
# VAULT_TOKEN=your-vault-token-here

# OpenAI Configuration (REQUIRED)
OPENAI_API_KEY=sk-your-openai-api-key-here
```

Create a `.env` file in the `ui/` directory (optional):

```env
# API URL (defaults to http://localhost:8000 if not set)
VITE_API_URL=http://localhost:8000
```

## Step 4: Start the API Server with uvx

In Terminal 1 (from project root):

```bash
# Run the API server directly with uvx
# No pip install or virtual environment needed!
uvx --with fastapi \
    --with "uvicorn[standard]" \
    --with python-dotenv \
    --with openai \
    --with boto3 \
    --with httpx \
    --with rich \
    --with typer \
        python -m src.api_server

# Or use a single line:
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv --with openai --with boto3 --with httpx --with rich --with typer  python -m src.api_server
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

**Note:** The first time you run this, `uvx` will download and cache the dependencies. Subsequent runs will be faster.

## Step 5: Start the Frontend

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

## Step 6: Verify Setup

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

Note: the response shows whether shared AWS credentials and your OpenAI key are configured. If either value is `false`, double-check your `.env` before continuing.

## Step 7: Test the Application

1. **Open your browser**: http://localhost:8080

2. **Try searching for AWS identities**:
   - "Show all AWS IAM roles"
   - "List all AWS users"
   - "What security concerns exist in my AWS identities?"
   - "Summarize all my AWS identities"
   
   **Note:** Skip Vault-related queries if you're only testing AWS.

## How It Works

- `uvx` downloads and caches Python packages on first use
- Dependencies are isolated per command invocation
- No global Python package pollution
- No virtual environment to manage
- Fast subsequent runs (after first download)

## Alternative: Using uvx for CLI Commands

You can also run CLI commands with uvx:

```bash
# Collect identities
uvx --with fastapi --with python-dotenv --with openai --with boto3 --with httpx --with rich --with typer     python -m src.main collect --aws-profile default

# Ask questions (requires identities.json file)
uvx --with fastapi --with python-dotenv --with openai --with boto3 --with httpx --with rich --with typer     python -m src.main ask "How many AWS roles do I have?" --file identities.json
```

## Troubleshooting

### uvx command too long?

Create a helper script `run-api.sh`:

```bash
#!/bin/bash
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

Make it executable:
```bash
chmod +x run-api.sh
./run-api.sh
```

Or create a simple alias in your shell config (`~/.bashrc` or `~/.zshrc`):

```bash
alias nhi-api='uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv --with openai --with boto3 --with httpx --with rich --with typer  python -m src.api_server'
```

Then just run:
```bash
nhi-api
```

### First run is slow?

This is normal! `uvx` downloads dependencies on first use. Subsequent runs are much faster as dependencies are cached.

### Permission errors?

Make sure `uv` is in your PATH. After installation, you may need to restart your terminal or run:

```bash
source ~/.bashrc  # or ~/.zshrc
```

### Still want to use virtual environment?

If you prefer traditional virtual environments, you can still use `uv` for faster package management:

```bash
uv venv
source .venv/bin/activate
uv pip install -r requirements.txt awslabs.iam-mcp-server
python run_api.py
```

## Benefits of This Approach

✅ **No virtual environment setup** - just run commands  
✅ **No global package pollution** - dependencies isolated per command  
✅ **Fast after first run** - dependencies are cached  
✅ **Simple cleanup** - just delete the cache if needed  
✅ **Works anywhere** - no need to activate environments  

## Next Steps

- Explore the API docs: http://localhost:8000/docs
- Try different search queries
- Test both AWS and Vault integration
- Use the CLI tool for automation
