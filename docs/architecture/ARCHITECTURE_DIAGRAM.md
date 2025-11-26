# Architecture Diagram

```mermaid
graph TB
  subgraph Browser
    U[User]
    UI[React / Vite Frontend]
    U --> UI
  end

  subgraph Backend
    UI -->|HTTPS (REST)| API[FastAPI Server]
    API -->|AI queries| OA[OpenAI API]

    subgraph CredentialModes
      direction TB
      Admin[Admin Credentials\n(AWS_PROFILE or access keys)]
      SecureMode[Per-User Credentials\nAWS_USER_<user>_KEY/SECRET]
    end

    Admin -.->|Default| API
    SecureMode -.->|secure_mode=true| API

    API -->|collect/search| Collector[IdentityCollector]
    Collector -->|MCP| MCP[AWSMCPClient]
    MCP -->|JSON-RPC| AWSServer[awslabs.iam-mcp-server]
  end

  AWSServer -->|IAM API| AWS[(AWS IAM)]
  Collector -->|Fallback\n(boto3)| AWS

  subgraph Outputs
    API -->|JSON| UI
    UI -->|Audit entries| Audit[Client Audit Log]
  end
```

## Diagram Notes
- **Frontend** runs in the browser, providing search UI, secure-mode toggle, user selector, and audit log.
- **FastAPI server** selects credentials (admin vs per-user) and routes requests through `IdentityCollector`.
- `IdentityCollector` talks to the **AWS IAM MCP server** (`awslabs.iam-mcp-server`) via `AWSMCPClient` (JSON-RPC). For least-privilege single-user collection, it falls back to boto3 and direct IAM APIs.
- **OpenAI** powers natural-language search and question/answer workflows implemented in `IdentityAnalyzer`.
- Results flow back to the frontend where they are rendered in tables, cards, or exported through the CLI.
```
