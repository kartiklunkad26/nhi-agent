# Vault MCP Server Setup Guide

This guide explains how to set up and use the Vault MCP (Model Context Protocol) server to collect Vault identities.

## Prerequisites

- ✅ Docker Desktop installed and running
- ✅ Access to a Vault server
- ✅ Valid Vault token with appropriate permissions

## What Was Installed

1. **Docker Desktop** - Container runtime for running the Vault MCP server
2. **Vault MCP Server Image** (`ashgw/vault-mcp:latest`) - Community-maintained MCP server for HashiCorp Vault

## Configuration

The Vault MCP server is configured via environment variables in your `.env` file:

```bash
# Vault Configuration
VAULT_ADDR=http://your-vault-server:8200
VAULT_TOKEN=hvs.your-vault-token
```

## How It Works

The NHI Agent uses a **Docker-based Vault MCP server** to communicate with your Vault instance:

1. **VaultMCPClient** (`src/mcp_client.py`) automatically detects Docker and runs the MCP server
2. The Docker container (`ashgw/vault-mcp:latest`) acts as an MCP protocol bridge
3. It communicates with your Vault server using the configured credentials
4. The MCP server exposes tools and resources for querying Vault

### Available Tools

The Vault MCP server provides these tools:

- **create_secret** - Create or update a secret in Vault KV v2
- **read_secret** - Read a secret from Vault KV v2
- **delete_secret** - Soft-delete a secret in Vault KV v2
- **create_policy** - Create or update a Vault policy

### Available Resources

- **vault://secrets** - List top-level KV v2 secret keys under the 'secret' mount
- **vault://policies** - List all Vault ACL policy names

## Usage

### Collect Vault Identities

```python
from src.identity_collector import IdentityCollector
import os

# Initialize collector
collector = IdentityCollector(
    vault_address=os.getenv('VAULT_ADDR'),
    vault_token=os.getenv('VAULT_TOKEN')
)

# Collect Vault identities
vault_identities = collector.collect_vault_identities()
print(f"Found {len(vault_identities)} Vault identities")

# Clean up
collector.close()
```

### Collect All Identities (AWS + Vault)

```python
# Collect from all sources
all_identities = collector.collect_all_identities()
print(f"Total identities: {all_identities['total_count']}")
print(f"AWS users: {len(all_identities['aws']['users'])}")
print(f"AWS roles: {len(all_identities['aws']['roles'])}")
print(f"Vault identities: {len(all_identities['vault'])}")
```

### Via CLI

```bash
# Collect identities from Vault
.venv/bin/python -m src.main collect \
  --vault-addr $VAULT_ADDR \
  --vault-token $VAULT_TOKEN \
  --output vault_identities.json

# Collect from both AWS and Vault
.venv/bin/python -m src.main collect \
  --aws-profile default \
  --vault-addr $VAULT_ADDR \
  --vault-token $VAULT_TOKEN \
  --output all_identities.json
```

### Via API Server

```bash
# Start the API server
.venv/bin/python run_api.py

# Collect identities
curl -X POST http://localhost:8000/api/identities/collect \
  -H "Content-Type: application/json" \
  -d '{
    "vault_address": "'$VAULT_ADDR'",
    "vault_token": "'$VAULT_TOKEN'"
  }'
```

## Troubleshooting

### Docker Container Not Starting

```bash
# Check if Docker is running
docker ps

# Check if the image is available
docker images | grep vault-mcp

# Pull the image manually if needed
docker pull ashgw/vault-mcp:latest
```

### Connection Issues

```bash
# Test Vault connectivity directly
vault status -address=$VAULT_ADDR

# Verify your token works
vault token lookup -address=$VAULT_ADDR $VAULT_TOKEN
```

### No Identities Found

If you're getting 0 identities, check:

1. **Token Permissions** - Your token needs `list` and `read` capabilities on:
   - `secret/metadata/*` (for KV v2 secrets)
   - `sys/policies/acl` (for policies)

2. **Vault Mounts** - The MCP server looks for secrets under the `secret/` mount (KV v2)

3. **Empty Vault** - Your Vault might not have any secrets yet

Example policy for Vault token:

```hcl
# Allow listing and reading secrets
path "secret/metadata/*" {
  capabilities = ["list", "read"]
}

path "secret/data/*" {
  capabilities = ["read"]
}

# Allow listing policies
path "sys/policies/acl" {
  capabilities = ["list", "read"]
}
```

### Manual Docker Run

You can test the Vault MCP server manually:

```bash
docker run --rm -i \
  -e VAULT_ADDR=$VAULT_ADDR \
  -e VAULT_TOKEN=$VAULT_TOKEN \
  ashgw/vault-mcp:latest
```

Then send JSON-RPC requests to test:

```json
{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"test","version":"1.0.0"}}}
```

## Architecture

```
┌──────────────────┐
│  NHI Agent API   │
└────────┬─────────┘
         │
┌────────▼──────────────┐
│  IdentityCollector    │
└────────┬──────────────┘
         │
┌────────▼──────────────┐
│  VaultMCPClient       │
│  (mcp_client.py)      │
└────────┬──────────────┘
         │
┌────────▼──────────────┐
│  Docker Container     │
│  ashgw/vault-mcp      │
│  (MCP Server)         │
└────────┬──────────────┘
         │
         │ Vault API
         │
┌────────▼──────────────┐
│  Your Vault Server    │
│  (AWS ELB endpoint)   │
└───────────────────────┘
```

## Next Steps

1. **Verify Vault Permissions** - Ensure your token has adequate read permissions
2. **Add Secrets to Vault** - Populate your Vault with test secrets if it's empty
3. **Test Full Collection** - Run `collector.collect_all_identities()` to gather AWS + Vault data
4. **Use the API** - Start the API server and test via the UI
5. **AI Analysis** - Use the IdentityAnalyzer to query and analyze collected identities

## Additional Resources

- [Vault MCP Server GitHub](https://github.com/rccyx/vault-mcp)
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)
- [HashiCorp Vault Documentation](https://developer.hashicorp.com/vault/docs)
