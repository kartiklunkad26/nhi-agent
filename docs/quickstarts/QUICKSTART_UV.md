# Quick Start - Using uv (Fast Alternative to pip)

`uv` is a fast Python package installer and resolver written in Rust. It's much faster than pip and can be used as a drop-in replacement.

## Install uv

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# Or via pip
pip install uv
```

## Option 1: Using uv with Virtual Environment

```bash
# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (much faster than pip!)
uv pip install -r requirements.txt

# Install AWS IAM MCP Server
uv pip install awslabs.iam-mcp-server

# Vault MCP Server uses uvx automatically
# (No separate install needed)
```

## Option 2: Using uvx for Everything

`uvx` can run Python packages directly without installing them globally:

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Run the API server using uvx (no install needed!)
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich --with typer \
    python -m src.api_server

# Or use uvx to run the CLI tool
uvx --with fastapi --with "uvicorn[standard]" --with python-dotenv \
    --with openai --with boto3 --with httpx --with rich --with typer \
    python -m src.main collect
```

## Option 3: Using uv sync (Recommended)

Create a `pyproject.toml` and use `uv sync`:

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync dependencies (creates venv and installs everything)
uv sync

# Activate the environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Run the app
python run_api.py
```

## Simplest Approach: uv pip install

```bash
# Install uv
pip install uv  # or use the install script above

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (replaces pip install)
uv pip install -r requirements.txt awslabs.iam-mcp-server

# Run the app
python run_api.py
```

## For AWS IAM MCP Server

You're already using `uvx` for this:
```bash
# Already handled in the code - it uses:
uvx awslabs.iam-mcp-server@latest
```

## For Vault MCP Server

The code will try `uvx` automatically:
```bash
# Already handled in the code - it tries:
uvx @hashicorp/vault-mcp-server@latest
```

## Complete uv Setup

```bash
# 1. Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Create venv and install dependencies
uv venv
source .venv/bin/activate

# 3. Install all dependencies
uv pip install -r requirements.txt awslabs.iam-mcp-server

# 4. Configure .env file (same as before)

# 5. Run the app
python run_api.py
```

## Benefits of uv

- ⚡ **Much faster** than pip (10-100x faster)
- 🔒 **Better dependency resolution**
- 📦 **Works as drop-in replacement** for pip
- 🚀 **Built-in virtual environment management**

## Quick Comparison

| Task | pip | uv |
|------|-----|-----|
| Install dependencies | `pip install -r requirements.txt` | `uv pip install -r requirements.txt` |
| Create venv | `python -m venv venv` | `uv venv` |
| Run tool | `pip install tool && tool` | `uvx tool` |

## Notes

- `uv pip install` is the direct replacement for `pip install`
- `uvx` is for running tools (like `npx` for Node.js)
- You can mix `uv` and `pip` - they're compatible
- `uv` is much faster, especially for large dependency trees
