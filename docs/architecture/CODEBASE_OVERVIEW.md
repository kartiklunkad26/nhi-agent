# Codebase Overview

## Project Summary
NHI Agent (Vault42 demo) is a full-stack system for exploring non-human identities in AWS. It talks to the AWS IAM Model Context Protocol (MCP) server to gather IAM users, roles, groups, and access keys, enriches them with additional metadata, and exposes the data through a FastAPI backend, a React/TypeScript UI, and a Typer-based CLI. OpenAI provides natural-language search, analysis, and security insights. The platform supports two operating modes:

- **Admin mode** (insecure): uses shared admin credentials to view the entire tenant.
- **Secure mode**: uses per-user access keys (for example `AWS_USER_alice_KEY` / `AWS_USER_alice_SECRET`) to enforce least-privilege views and tailored analysis.

## Repository Layout
| Path | Purpose |
| --- | --- |
| `src/api_server.py` | FastAPI service exposing collection/search/query endpoints, secure-mode credential routing, response schemas. |
| `src/identity_collector.py` | Bridges `AWSMCPClient` (and boto3 fallbacks) to gather IAM identities and enriched user data (MFA, policies, access-key usage). |
| `src/identity_analyzer.py` | Builds AI-ready context, handles OpenAI-powered queries, specialized security checks, and category filtering. |
| `src/mcp_client.py` | JSON-RPC wrapper for MCP servers. `AWSMCPClient` normalizes IAM responses and offers helper methods; Vault support remains scaffolded. |
| `src/main.py` | CLI (`typer`) for collect, ask, analyze, and interactive sessions. |
| `ui/` | React + Vite frontend (contexts, security toggle, user selector, audit log, results table, styling). |
| `requirements.txt`, `pyproject.toml` | Python dependency manifests. |
| `docs/` | Quickstarts, troubleshooting guides, architecture notes, and demo scripts. |

## Backend Architecture
### API Server (`src/api_server.py`)
- Loads env configuration (`AWS_PROFILE`, admin keys, per-user keys) via `dotenv`.
- Endpoints:
  - `POST /api/identities/collect`: collects and summarizes AWS identities (users/roles/groups/access_keys).
  - `POST /api/identities/search`: AI-assisted search with `secure_mode` + `current_user` controls.
  - `POST /api/query`: free-form question answering with summary metadata.
  - `GET /api/health`: readiness + configuration signal.
- Secure mode flow:
  1. When `secure_mode=true` and `current_user` is supplied, the server loads `AWS_USER_<user>_KEY`/`SECRET`, instantiates `IdentityCollector` with explicit keys, and calls `collect_all_identities(single_user=...)`.
  2. Otherwise it uses shared credentials (profile or admin keys) and collects the entire tenant.
- All responses go through `IdentityAnalyzer`, which receives a reference to the collector for on-demand enrichment.

### Identity Collection (`src/identity_collector.py`)
- Constructor accepts profile or explicit keys; detects least-privilege mode.
- Core methods:
  - `collect_all_identities(single_user=None)`: returns IAM users/roles/groups/access_keys plus a total count, using either full collection or single-user collection.
  - `collect_single_user_aws_identities`: direct boto3 `GetUser` + `ListAccessKeys` to minimize required permissions.
  - `collect_enriched_user_data`: optional enrichment (attached policies, inline policies, MFA devices, login profile, access-key last used) used by advanced analyzer queries; requires expanded IAM permissions.

### MCP Clients (`src/mcp_client.py`)
- `MCPClient` handles stdio JSON-RPC lifecycle (initialize, send request, read response, skip notifications).
- `AWSMCPClient` features:
  - Launches AWS IAM MCP server via `uvx awslabs.iam-mcp-server@latest` (injects either profile or explicit keys).
  - Normalizes varied JSON structures from MCP tools (`_parse_aws_list_response`).
  - Provides helpers: `list_iam_users`, `list_iam_roles`, `list_all_access_keys`, `get_user_details`, `list_attached_user_policies`, `list_mfa_devices`, etc.
  - Uses boto3 fallbacks for least-privilege use cases (single-user collection).
- Vault client logic remains but is currently dormant; re-enable when Vault workflows return.

### Identity Analyzer (`src/identity_analyzer.py`)
- Maintains the AI integration:
  - `_create_context` composes the prompt context including users/roles/groups/access keys.
  - `search_identities(query, max_results, current_user, secure_mode)`: AI-driven filtering with keyword fallback; understands category queries, security checks (MFA, admin access), rotation queries, and user-specific checks (for example, "my keys oldest").
  - Specialized helper methods (`_search_admin_users`, `_search_users_without_mfa`, `_search_security_risks`, `_search_inactive_identities`, `_check_my_keys_oldest`).
  - `get_old_access_keys`, `summarize_identities`, `analyze_security_concerns` for reporting.
- Accepts an `IdentityCollector` instance to fetch enriched data on-demand.

### CLI (`src/main.py`)
- Typer commands for rapid testing:
  - `collect`: fetches identities and writes `identities.json` (with summary table output via Rich).
  - `ask`, `analyze`, `interactive`: AI-driven analysis flows using the shared Analyzer logic.

## Frontend (`ui/`)
- React + Vite + shadcn UI.
- Key building blocks:
  - **Contexts**: `AuthContext` (pre-defined IAM usernames), `SecurityContext` (secure-mode toggle persisted to localStorage).
  - **Components**: `SearchBar`, `UserSelector`, `SecurityModeToggle`, `ResultsTable`, `AuditLog`.
  - **Index page** orchestrates search execution, displays results, and maintains an audit log split by mode.
- API client (`ui/src/lib/api.ts`) calls backend endpoints and forwards `current_user` & `secure_mode`.

## Configuration & Credentials
- Backend `.env` variables:
  - Shared credentials: `AWS_PROFILE` or `AWS_ACCESS_KEY_ID` / `AWS_SECRET_ACCESS_KEY`.
  - Per-user credentials (secure mode): `AWS_USER_<username>_KEY`, `AWS_USER_<username>_SECRET`.
  - `OPENAI_API_KEY`, `API_PORT`, `CORS_ORIGINS`.
- Frontend `.env` (optional): `VITE_API_URL` to override backend host.
- Quick-start docs provide ready-made env templates for AWS-only or uvx-based runs.

## Data Flow
1. User issues a search or query (UI or CLI).
2. API server selects credentials (admin vs user) and runs `IdentityCollector`.
3. Collector gathers IAM data via MCP/boto3.
4. `IdentityAnalyzer` builds context, runs specialized checks or OpenAI prompts, and returns structured identity objects.
5. UI renders results (tables, badges) and records audit entries; CLI prints Rich tables or panels.

## Operational Guides
- `QUICKSTART_AWS_ONLY.md`, `QUICKSTART_UVX.md`, `QUICKSTART_SIMPLE.md`: tailored setup paths.
- `TROUBLESHOOTING.md`, `QUICK_FIX.md`: debug "failed to fetch" and uvx quoting issues.
- `START_API.md`: fallback when uvx stops silently (recommends venv).
- `IMPROVEMENTS.md`: change log + backlog of enhancements.

## Future Enhancements (from docs & comments)
- Re-enable Vault support when ready.
- Switch OpenAI prompts to structured outputs for deterministic parsing.
- Cache identity responses per credential set.
- Expand analyzer coverage (policy parsing, role assumption mapping), add tests for secure-mode scoping.

## Quick Commands
- Start API (uvx): `./run_api_uvx.sh`
- Start API (venv): `source venv/bin/activate && python run_api.py`
- Start UI: `cd ui && npm run dev`
- Health check: `curl http://localhost:8000/api/health`
- CLI collect: `python -m src.main collect --aws-profile default`

Refer to this document when onboarding teammates, presenting the architecture, or planning future work.
