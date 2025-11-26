# How to Start the API Server

## Problem: uvx command stops silently

If `uvx` stops without any output, it's likely because:
1. Dependencies aren't being loaded correctly
2. There's an import error that's being silently swallowed
3. uvx isn't finding the packages

## Solution 1: Use Virtual Environment (Most Reliable)

This is the most reliable way to run the API:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt awslabs.iam-mcp-server

# Run the API server
python run_api.py
```

## Solution 2: Install uv and use uv pip

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate

# Install dependencies (faster than pip)
uv pip install -r requirements.txt awslabs.iam-mcp-server

# Run the API server
python run_api.py
```

## Solution 3: Fix uvx command

If you want to use uvx, try this more explicit version:

```bash
# Make sure you're in the project root
cd /Users/kartiklunkad/workspace/nhi-agent

# Run with explicit Python path
uvx --python 3.9 \
    --with fastapi \
    --with "uvicorn[standard]" \
    --with python-dotenv \
    --with openai \
    --with boto3 \
    --with httpx \
    --with rich \
    --with typer \
    python -m src.api_server
```

## Solution 4: Check what's happening

Run with verbose output to see errors:

```bash
uvx --verbose \
    --with fastapi \
    --with "uvicorn[standard]" \
    --with python-dotenv \
    --with openai \
    --with boto3 \
    --with httpx \
    --with rich \
    --with typer \
        python -m src.api_server 2>&1 | tee api.log
```

Then check `api.log` for errors.

## Recommended: Use Virtual Environment

For reliability, I recommend using a virtual environment:

```bash
# Quick setup
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt awslabs.iam-mcp-server
python run_api.py
```

This is the most straightforward and reliable approach.
