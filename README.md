# NHI Agent

**NHI Agent** (Non-Human Identity Agent) is a full-stack application for managing and analyzing non-human identities across AWS IAM. It provides both a CLI tool and a web interface for searching, querying, and understanding your service accounts, IAM roles, and API keys.

## Features

- 🔐 **Identity Collection**: Discovers IAM users, roles, groups, and access keys via the AWS IAM MCP server (with on-demand boto3 fallbacks).
- 🛡️ **Dual Credential Modes**: Switch between admin-wide visibility and per-user secure mode for least-privilege demos.
- 🤖 **AI-Powered Analysis**: Uses OpenAI for natural-language search, summaries, and targeted security checks.
- 🌐 **Unified UI & CLI**: React/Vite frontend with audit logging plus a Typer CLI for automation.
- 📓 **Documented Workflows**: Quickstarts, troubleshooting guides, and architecture notes under `docs/`.

## Architecture

The application consists of three main components:

1. **Python Backend** (`src/`): MCP clients, identity collection, and AI analysis
2. **FastAPI Server** (`src/api_server.py`): REST API that bridges the UI and backend
3. **React Frontend** (`ui/`): Modern web interface for searching and querying identities

## Prerequisites

- Python 3.9 or higher
- Node.js 18+ and npm/yarn
- Access to AWS IAM (via AWS credentials)
- OpenAI API key (for question answering)
- `uvx` installed (for running AWS IAM MCP server)

## Installation

### Backend Setup

1. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Install AWS IAM MCP Server:
```bash
pip install awslabs.iam-mcp-server
# Or using uvx (recommended):
# uvx awslabs.iam-mcp-server@latest
```

### Frontend Setup

1. Navigate to the UI directory:
```bash
cd ui
```

2. Install dependencies:
```bash
npm install
# or
yarn install
```

### Environment Configuration

Create a `.env` file in the project root (see `.env.example`):

```env
# API Server Configuration
API_PORT=8000
CORS_ORIGINS=http://localhost:8080

# AWS Configuration
# Option 1: Use AWS Profile (recommended)
AWS_PROFILE=your-aws-profile
AWS_REGION=us-east-1

# Option 2: Use AWS Access Keys
# AWS_ACCESS_KEY_ID=your-access-key-id
# AWS_SECRET_ACCESS_KEY=your-secret-access-key
# AWS_REGION=us-east-1

# Option 3: (Secure Mode) per-user credentials
# AWS_USER_alice_KEY=...
# AWS_USER_alice_SECRET=...

# OpenAI Configuration (required for question answering)
OPENAI_API_KEY=your-openai-api-key
```

Create a `.env` file in the `ui/` directory (optional):

```env
# API Configuration (defaults to http://localhost:8000)
VITE_API_URL=http://localhost:8000
```

## Usage

### Running the Application

1. **Start the API Server** (in the project root):
```bash
python run_api.py
# Or directly:
uvicorn src.api_server:app --reload --host 0.0.0.0 --port 8000
```

2. **Start the Frontend** (in the `ui/` directory):
```bash
cd ui
npm run dev
```

3. **Access the Application**:
   - Web UI: http://localhost:8080
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

### CLI Usage

You can also use the CLI tool directly:

```bash
# Collect identities
python -m src.main collect --aws-profile default

# Ask questions
python -m src.main ask "How many admin users are there?" --file identities.json

# Run analysis
python -m src.main analyze --file identities.json

# Interactive mode
python -m src.main interactive --file identities.json
```

### Web Interface Usage

1. **Configure Credentials**: Set up your AWS credentials in the `.env` file
2. **Start the Servers**: Start both API and frontend servers (see above)
3. **Search Identities**: Use the search bar on the home page to find identities
4. **Ask Questions**: Use natural language queries like:
   - "Show all AWS IAM roles"
   - "List all IAM users"
   - "Find admin roles"

1. **Select a User (Optional)**: Use the "Logged in as" dropdown to simulate an IAM identity when testing secure mode.
2. **Toggle Modes**: The green/orange button switches between admin visibility (Part 1 demo) and user-specific visibility (Part 2 demo).
3. **Search Identities**: Use natural language queries such as:
   - "Show all AWS IAM roles"
   - "List users without MFA"
   - "Are my access keys the oldest?"
4. **Review Audit Log**: Each query is recorded per mode for storytelling and demonstrations.

## Documentation

All supplemental guides now live under [`docs/`](docs/):

- `docs/quickstarts/` – setup guides (`QUICKSTART_AWS_ONLY.md`, `QUICKSTART_UVX.md`, etc.)
- `docs/guides/` – troubleshooting, improvement log, start-up helpers
- `docs/architecture/` – high-level system overview and Mermaid diagram
- `docs/demos/` and `docs/reference/` – demo scripts, security notes, and MCP references

## API Endpoints

### Authentication
No authentication required - credentials are read from the `.env` file.

### Endpoints

- `POST /api/identities/collect` - Collect identities from AWS
- `POST /api/identities/search` - Search identities using natural language
- `POST /api/query` - Ask questions about identities
- `GET /api/health` - Health check

See http://localhost:8000/docs for full API documentation.

## Project Structure

```
nhi-agent/
├── src/                      # Python backend
│   ├── __init__.py
│   ├── mcp_client.py        # MCP client implementation
│   ├── identity_collector.py # Identity collection logic
│   ├── identity_analyzer.py  # AI-powered analysis & security checks
│   ├── main.py              # CLI entry point
│   └── api_server.py        # FastAPI REST API server
├── docs/                     # Documentation hub (quickstarts, guides, architecture)
├── ui/                       # React frontend (contexts, components, assets)
├── run_api.py                # API server startup script
├── run_api_uvx.sh/.bat       # uvx helper scripts
├── requirements.txt          # Python dependencies (pip/uv)
├── pyproject.toml            # Project metadata / packaging
└── README.md
```

### AWS IAM MCP Server

The AWS IAM MCP Server must be installed and configured. It can be run via:
- `uvx awslabs.iam-mcp-server@latest` (recommended)
- Or installed via pip: `pip install awslabs.iam-mcp-server`

Ensure your AWS credentials are configured (via `AWS_PROFILE`, `AWS_ACCESS_KEY_ID`/`AWS_SECRET_ACCESS_KEY`, or `~/.aws/credentials`).

> Looking for the old Vault demo? See `docs/reference/VAULT_MCP_SETUP.md` for the previous setup notes.

## Security Considerations

- **Credentials Storage**: Credentials are read from the `.env` file - never commit this file
- **Environment Variables**: Keep your `.env` file secure and never commit it to version control
- **AWS Credentials**: In production, consider using IAM roles instead of access keys
- **Local Development**: This setup is for local development - for production, implement proper authentication

## Development

### Backend Development

```bash
# Install in development mode
pip install -e .

# Run tests (when available)
pytest

# Format code
black src/
```

### Frontend Development

```bash
cd ui
npm run dev
```

## Troubleshooting

### API Server Issues

- **CORS errors**: Ensure `CORS_ORIGINS` in `.env` includes your frontend URL
- **Credential errors**: Verify AWS credentials are correctly set in `.env`
- **OpenAI errors**: Check that `OPENAI_API_KEY` is valid and has sufficient credits

### MCP Server Connection Issues

- Ensure `uvx` is installed: `pip install uvx` or install via [uv](https://github.com/astral-sh/uv)
- Verify AWS credentials are properly configured
- Check that MCP server commands are available in your PATH

### Frontend Issues

- **API connection errors**: Verify `VITE_API_URL` matches your API server URL (defaults to http://localhost:8000)
- **No results**: Check that credentials are configured in the backend `.env` file

## License

Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request.
