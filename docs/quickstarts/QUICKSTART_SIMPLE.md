# Quick Start - Simple (No Virtual Environment)

For quick testing, you can skip the virtual environment and install dependencies globally.

## Step 1: Install Dependencies Globally

```bash
# Install Python dependencies (globally)
pip install -r requirements.txt

# Install AWS IAM MCP Server
pip install awslabs.iam-mcp-server

# Vault MCP Server will use npx automatically (no install needed)
# Or install globally if you prefer:
# npm install -g @hashicorp/vault-mcp-server
```

## Step 2: Frontend Setup

```bash
cd ui
npm install
```

## Step 3: Configure Environment

Create `.env` in the project root:

```env
API_PORT=8000
CORS_ORIGINS=http://localhost:8080

# AWS Configuration
AWS_PROFILE=default
AWS_REGION=us-east-1

# Vault Configuration (optional)
VAULT_ADDR=https://your-vault-server.com
VAULT_TOKEN=your-vault-token

# OpenAI Configuration (required)
OPENAI_API_KEY=your-openai-key
```

## Step 4: Start the Application

**Terminal 1 - API Server:**
```bash
python run_api.py
# Or:
uvicorn src.api_server:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd ui
npm run dev
```

## Step 5: Test

1. Open http://localhost:8080
2. Search for identities: "Show all AWS IAM roles"

## Note

⚠️ **Warning**: Installing packages globally can cause conflicts with other Python projects. Use a virtual environment for production or if you have multiple Python projects.

## If You Run Into Issues

If you get import errors or conflicts, switch to using a virtual environment:

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```
