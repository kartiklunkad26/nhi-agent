# Quick Start Guide

Get NHI Agent up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.9+ installed
- [ ] Node.js 18+ installed
- [ ] OpenAI API key
- [ ] AWS credentials (optional, for testing)
- [ ] Vault credentials (optional, for testing)

## Step 1: Backend Setup

**Option A: Using pip (traditional)**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install AWS IAM MCP Server
pip install awslabs.iam-mcp-server
```

**Option B: Using uv (faster - recommended)**
```bash
# Install uv first (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or: pip install uv

# Create virtual environment
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (much faster than pip!)
uv pip install -r requirements.txt awslabs.iam-mcp-server
```

**Note:** Vault MCP Server uses `npx` or `uvx` automatically - no separate install needed.

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

# AWS Configuration (use one option)
AWS_PROFILE=your-aws-profile
AWS_REGION=us-east-1
# OR
# AWS_ACCESS_KEY_ID=your-access-key-id
# AWS_SECRET_ACCESS_KEY=your-secret-access-key

# Vault Configuration (optional)
VAULT_ADDR=https://your-vault-server.com
VAULT_TOKEN=your-vault-token

# OpenAI Configuration (required)
OPENAI_API_KEY=your-openai-key
```

Create `.env` in the `ui/` directory (optional):

```env
VITE_API_URL=http://localhost:8000
```

## Step 5: Start the Application

**Terminal 1 - API Server:**
```bash
python run_api.py
```

**Terminal 2 - Frontend:**
```bash
cd ui
npm run dev
```

## Step 4: Access the Application

1. Open http://localhost:8080
2. Start searching identities using the search bar!
3. The app will use credentials from your `.env` file

## Troubleshooting

**API not connecting?**
- Check that the API server is running on port 8000
- Verify `VITE_API_URL` in `ui/.env`

**No identities found?**
- Make sure AWS credentials are configured in the `.env` file (either `AWS_PROFILE` or access keys)
- If secure mode, verify `AWS_USER_<username>_KEY/SECRET` pairs exist for the selected user
- Check API server logs for errors

## Next Steps

- Read the full [project README](../../README.md) for detailed documentation
- Explore the API docs at http://localhost:8000/docs
- Try the CLI tool: `python -m src.main collect`
