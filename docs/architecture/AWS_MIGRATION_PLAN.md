# AWS-Native Architecture Migration Plan

## Document Information
**Created:** 2025-11-21
**Status:** Planning
**Migration Strategy:** Incremental

## Executive Summary

This document outlines the migration of the NHI Agent from a local-first FastAPI application to an AWS-native, cloud-deployed platform. The migration preserves core functionality (MCP clients, identity collection, React UI) while transforming the deployment model and adding enterprise features (Okta authentication, AWS Secrets Manager integration, Bedrock AI orchestration).

## Current Architecture vs Target Architecture

### Current State (v0.1.0)

```
┌─────────────────────────────────────────┐
│   User (Browser/CLI)                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   FastAPI Server (localhost:8000)       │
│   - REST endpoints                      │
│   - CORS middleware                     │
│   - No authentication                   │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   IdentityCollector                     │
│   - MCP client orchestration            │
│   - Admin/secure mode switching         │
└──────────────┬──────────────────────────┘
               │
               ├──────────────────────────┐
               ▼                          ▼
┌──────────────────────┐   ┌──────────────────────┐
│  AWSMCPClient        │   │  IdentityAnalyzer    │
│  - IAM API calls     │   │  - OpenAI GPT-4      │
│  - Boto3 fallback    │   │  - Security checks   │
└──────────────────────┘   └──────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   AWS IAM MCP Server (uvx subprocess)   │
│   - JSON-RPC interface                  │
└─────────────────────────────────────────┘
```

**Deployment:** Local development only
**Data Storage:** In-memory/file-based
**Authentication:** None
**Frontend:** Vite dev server (localhost:8080)

### Target State (v0.2.0 - AWS-Native)

```
┌─────────────────────────────────────────┐
│   User (Browser)                        │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   CloudFront + S3 (Static React UI)     │
│   - HTTPS                               │
│   - CDN distribution                    │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│   API Gateway (REST)                    │
│   - Lambda authorizer (Okta)           │
│   - Request validation                  │
│   - Rate limiting                       │
└──────────────┬──────────────────────────┘
               │
               ├─────────────┬─────────────┬──────────────┐
               ▼             ▼             ▼              ▼
┌────────────────┐ ┌──────────────┐ ┌──────────┐ ┌──────────────┐
│ IAM Discovery  │ │ Secrets Mgr  │ │ Data     │ │ Bedrock      │
│ Lambda         │ │ Lambda       │ │ Processor│ │ Orchestrator │
│                │ │              │ │ Lambda   │ │ Lambda       │
└───────┬────────┘ └──────┬───────┘ └────┬─────┘ └──────┬───────┘
        │                 │               │              │
        └─────────────────┴───────────────┴──────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │         DynamoDB                        │
        │  - IdentitiesTable                      │
        │  - SecretsTable                         │
        │  - DiscoveryHistoryTable                │
        └─────────────────────────────────────────┘
                          │
                          ▼
        ┌─────────────────────────────────────────┐
        │   S3 Buckets                            │
        │   - Raw data exports                    │
        │   - Lambda layer packages               │
        │   - CloudTrail logs                     │
        └─────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   AWS Bedrock AgentCore                         │
│   - Discovery workflow orchestration            │
│   - Natural language analysis                   │
│   - Knowledge bases for identity context        │
└─────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────┐
│   Okta                                          │
│   - User authentication                         │
│   - OAuth 2.0 / OIDC                            │
│   - Token validation                            │
└─────────────────────────────────────────────────┘
```

**Deployment:** AWS (multi-region capable)
**Data Storage:** DynamoDB + S3
**Authentication:** Okta OAuth 2.0
**Frontend:** CloudFront + S3 static hosting

## Component Mapping

| Current Component | Status | Target Component | Notes |
|-------------------|--------|------------------|-------|
| `src/api_server.py` (FastAPI) | **Migrate** | Lambda functions + API Gateway | Split into multiple Lambdas |
| `src/identity_collector.py` | **Preserve + Adapt** | Lambda layer + handler | Core logic preserved, adapted for Lambda |
| `src/mcp_client.py` | **Preserve + Adapt** | Lambda layer | MCP clients work in Lambda with Layer |
| `src/identity_analyzer.py` | **Refactor** | Bedrock integration Lambda | Replace OpenAI with Bedrock |
| `src/main.py` (CLI) | **Remove** | N/A | Web-only interface |
| `ui/` (React/Vite) | **Preserve + Deploy** | S3 + CloudFront | Build and deploy static assets |
| In-memory data | **Replace** | DynamoDB | Persistent storage |
| `.env` credentials | **Replace** | IAM roles + Secrets Manager | Proper secret management |

## Technology Stack Changes

### Removed
- ❌ FastAPI, Uvicorn
- ❌ Typer, Rich (CLI dependencies)
- ❌ OpenAI Python SDK
- ❌ Vite dev server (local only)

### Added
- ✅ AWS CDK (Infrastructure as Code)
- ✅ AWS Lambda (compute)
- ✅ AWS API Gateway (REST API)
- ✅ AWS DynamoDB (data storage)
- ✅ AWS Bedrock (AI/ML)
- ✅ AWS Secrets Manager (credential storage)
- ✅ AWS S3 + CloudFront (frontend hosting)
- ✅ Okta SDK (authentication)
- ✅ boto3 (AWS SDK)

### Preserved
- ✅ React 18 + TypeScript
- ✅ Tailwind CSS + shadcn/ui
- ✅ MCP client implementation
- ✅ Core identity collection logic
- ✅ Security analysis algorithms

## Detailed Component Design

### 1. Lambda Functions

#### 1.1 IAM Discovery Lambda
**Purpose:** Discover and collect AWS IAM identities

**Handler:** `src/lambda/iam_discovery.py`

**Trigger:**
- API Gateway (`POST /api/identities/collect`)
- EventBridge scheduled rule (future)

**Functionality:**
- Instantiate `IdentityCollector` with IAM role credentials
- Call `collect_all_identities()`
- Store results in DynamoDB
- Return summary to API Gateway

**Environment Variables:**
- `IDENTITIES_TABLE_NAME`
- `AWS_REGION`
- `MCP_LAYER_PATH`

**Lambda Layer Dependencies:**
- MCP client code
- boto3 extensions

**IAM Permissions:**
- `iam:ListUsers`, `iam:ListRoles`, `iam:ListGroups`
- `iam:GetUser`, `iam:ListAccessKeys`
- `dynamodb:PutItem`, `dynamodb:Query`
- `s3:PutObject` (for exports)

**Timeout:** 5 minutes
**Memory:** 512 MB

#### 1.2 Secrets Manager Discovery Lambda
**Purpose:** Enumerate secrets from AWS Secrets Manager

**Handler:** `src/lambda/secrets_discovery.py`

**Trigger:**
- API Gateway (`POST /api/secrets/collect`)

**Functionality:**
- List all secrets in account
- Extract metadata (creation date, last accessed, rotation status)
- Store in DynamoDB `SecretsTable`
- Return summary

**Environment Variables:**
- `SECRETS_TABLE_NAME`
- `AWS_REGION`

**IAM Permissions:**
- `secretsmanager:ListSecrets`
- `secretsmanager:DescribeSecret`
- `dynamodb:PutItem`, `dynamodb:Query`

**Timeout:** 3 minutes
**Memory:** 256 MB

#### 1.3 Data Processor Lambda
**Purpose:** Process and enrich collected identity data

**Handler:** `src/lambda/data_processor.py`

**Trigger:**
- DynamoDB Stream (from IdentitiesTable)

**Functionality:**
- Enrich identity records with policy analysis
- Calculate risk scores
- Update metadata (tags, categories)
- Trigger Bedrock analysis for anomalies

**IAM Permissions:**
- `dynamodb:UpdateItem`, `dynamodb:Query`
- `bedrock:InvokeModel`
- `iam:GetPolicy`, `iam:GetPolicyVersion`

**Timeout:** 2 minutes
**Memory:** 512 MB

#### 1.4 Bedrock Orchestrator Lambda
**Purpose:** Coordinate Bedrock AgentCore for AI-powered analysis

**Handler:** `src/lambda/bedrock_orchestrator.py`

**Trigger:**
- API Gateway (`POST /api/identities/search`)

**Functionality:**
- Build context from DynamoDB identity data
- Invoke Bedrock AgentCore with user query
- Parse and structure Bedrock responses
- Return analysis results

**Environment Variables:**
- `BEDROCK_AGENT_ID`
- `BEDROCK_AGENT_ALIAS_ID`
- `IDENTITIES_TABLE_NAME`

**IAM Permissions:**
- `bedrock:InvokeAgent`
- `bedrock:Retrieve`
- `dynamodb:Query`, `dynamodb:Scan`

**Timeout:** 1 minute
**Memory:** 256 MB

#### 1.5 Okta Authorizer Lambda
**Purpose:** Validate Okta tokens for API Gateway

**Handler:** `src/lambda/okta_authorizer.py`

**Trigger:**
- API Gateway (Lambda authorizer)

**Functionality:**
- Extract JWT from Authorization header
- Validate token with Okta JWKS endpoint
- Check token expiration and signature
- Return IAM policy (Allow/Deny)

**Environment Variables:**
- `OKTA_DOMAIN`
- `OKTA_AUDIENCE`
- `OKTA_ISSUER`

**IAM Permissions:**
- None (outbound HTTPS only)

**Timeout:** 10 seconds
**Memory:** 128 MB

### 2. DynamoDB Tables

#### 2.1 IdentitiesTable
**Purpose:** Store discovered IAM identities

**Schema:**
```python
{
    "PK": "IDENTITY#<type>#<id>",  # e.g., "IDENTITY#USER#alice"
    "SK": "METADATA",
    "type": "user" | "role" | "group",
    "name": str,
    "arn": str,
    "createdDate": str (ISO 8601),
    "lastUsed": str (ISO 8601),
    "mfaEnabled": bool,
    "policies": [str],  # Policy ARNs
    "accessKeys": [
        {
            "accessKeyId": str,
            "status": "Active" | "Inactive",
            "createdDate": str,
            "lastUsed": str
        }
    ],
    "riskScore": int (0-100),
    "tags": [str],
    "discoveredAt": str (ISO 8601),
    "ttl": int (epoch timestamp for data expiration)
}
```

**Indexes:**
- GSI1: `type-lastUsed-index` (for filtering by type and sorting by last used)
- GSI2: `riskScore-index` (for security dashboard)

**Capacity:** On-demand (auto-scaling)

#### 2.2 SecretsTable
**Purpose:** Store discovered secrets from Secrets Manager

**Schema:**
```python
{
    "PK": "SECRET#<secretId>",
    "SK": "METADATA",
    "name": str,
    "arn": str,
    "description": str,
    "createdDate": str,
    "lastAccessedDate": str,
    "lastRotatedDate": str,
    "rotationEnabled": bool,
    "tags": [str],
    "discoveredAt": str,
    "ttl": int
}
```

**Indexes:**
- GSI1: `rotationEnabled-lastRotatedDate-index`

**Capacity:** On-demand

#### 2.3 DiscoveryHistoryTable
**Purpose:** Track discovery job history and audit log

**Schema:**
```python
{
    "PK": "JOB#<jobId>",
    "SK": "METADATA",
    "jobId": str (UUID),
    "jobType": "iam" | "secrets",
    "status": "running" | "completed" | "failed",
    "startedAt": str,
    "completedAt": str,
    "itemsDiscovered": int,
    "errors": [str],
    "triggeredBy": str (Okta user ID),
    "ttl": int
}
```

**Indexes:**
- GSI1: `status-startedAt-index`

**Capacity:** On-demand

### 3. API Gateway Design

**Type:** REST API
**Endpoint:** `https://api.nhi-discovery.example.com`

**Authentication:** Lambda authorizer (Okta JWT validation)

**Endpoints:**

```
POST /api/identities/collect
- Description: Trigger IAM identity discovery
- Lambda: iam_discovery
- Auth: Required
- Request: {}
- Response: { jobId, status, summary }

POST /api/secrets/collect
- Description: Trigger Secrets Manager discovery
- Lambda: secrets_discovery
- Auth: Required
- Request: {}
- Response: { jobId, status, summary }

GET /api/identities
- Description: List discovered identities
- Lambda: query_handler
- Auth: Required
- Query params: type, limit, offset, sort
- Response: { items: [...], total, nextToken }

POST /api/identities/search
- Description: AI-powered search
- Lambda: bedrock_orchestrator
- Auth: Required
- Request: { query: str }
- Response: { results: [...], query, total }

GET /api/identities/{id}
- Description: Get identity details
- Lambda: query_handler
- Auth: Required
- Response: { identity object }

GET /api/jobs/{jobId}
- Description: Get discovery job status
- Lambda: query_handler
- Auth: Required
- Response: { job object }

GET /api/health
- Description: Health check
- Lambda: health_check
- Auth: Not required
- Response: { status: "healthy" }
```

**CORS Configuration:**
```json
{
  "allowOrigins": ["https://nhi-discovery.example.com"],
  "allowMethods": ["GET", "POST", "OPTIONS"],
  "allowHeaders": ["Authorization", "Content-Type"],
  "exposeHeaders": ["X-Request-Id"]
}
```

**Rate Limiting:**
- 100 requests/minute per user (via API Gateway throttling)

### 4. Bedrock AgentCore Configuration

**Agent Name:** NHI-Discovery-Agent

**Foundation Model:**
- Primary: Anthropic Claude 3.5 Sonnet
- Fallback: Anthropic Claude 3 Haiku

**Knowledge Bases:**
1. **Identity Context KB**
   - Source: S3 bucket with IAM policy documentation
   - Embeddings: Titan Embeddings G1
   - Purpose: Provide context about AWS IAM permissions

2. **Security Best Practices KB**
   - Source: CIS AWS Foundations Benchmark docs
   - Purpose: Security analysis and recommendations

**Action Groups:**

#### Action Group 1: Identity Lookup
**Actions:**
- `list_identities` - Query DynamoDB for identities
- `get_identity_details` - Fetch specific identity
- `filter_by_type` - Filter by user/role/group

**Lambda:** `bedrock_action_handler.py`

#### Action Group 2: Risk Analysis
**Actions:**
- `calculate_risk_score` - Compute risk based on policies
- `identify_overprivileged` - Find excessive permissions
- `check_compliance` - Compare against best practices

**Lambda:** `bedrock_action_handler.py`

**Prompt Template:**
```
You are an expert AWS security analyst helping discover and analyze non-human identities.
Your goal is to provide insights about IAM users, roles, and access keys.

Available context:
- Identity inventory from DynamoDB
- AWS IAM policy documentation
- Security best practices

When answering queries:
1. Search relevant identities using available actions
2. Analyze security posture
3. Provide actionable recommendations
4. Highlight compliance gaps

User query: {{user_query}}
```

**Guardrails:**
- Content filtering for PII/credentials
- Block destructive operations (delete, modify)
- Read-only access enforcement

### 5. Okta Integration

**Authentication Flow:** OAuth 2.0 Authorization Code with PKCE

**Okta Application Configuration:**
- Type: Single Page Application (SPA)
- Grant types: Authorization Code
- Redirect URIs:
  - `https://nhi-discovery.example.com/callback`
  - `http://localhost:8080/callback` (dev)
- Token endpoint authentication: None (PKCE)
- Scopes: `openid`, `profile`, `email`

**Frontend Flow:**
1. User clicks "Sign In"
2. Redirect to Okta authorization endpoint
3. User authenticates with Okta
4. Okta redirects back with authorization code
5. Frontend exchanges code for access token (PKCE)
6. Frontend stores token in memory/sessionStorage
7. All API calls include `Authorization: Bearer <token>`

**Backend Validation (Lambda Authorizer):**
1. Extract token from `Authorization` header
2. Fetch Okta JWKS (cached for 1 hour)
3. Verify token signature
4. Check expiration, issuer, audience
5. Return IAM policy with user context
6. API Gateway caches authorization decision (5 minutes)

**Environment Variables:**
```bash
OKTA_DOMAIN=dev-12345.okta.com
OKTA_CLIENT_ID=<client_id>
OKTA_ISSUER=https://dev-12345.okta.com/oauth2/default
OKTA_AUDIENCE=api://nhi-discovery
```

### 6. MCP Client Adaptation for Lambda

**Challenge:** MCP clients spawn subprocesses, which need special handling in Lambda

**Solution: Lambda Layer + Optimized Execution**

**Lambda Layer Structure:**
```
/opt/
├── python/
│   ├── mcp_client/
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   └── aws_client.py
│   └── requirements.txt
└── bin/
    └── awslabs.iam-mcp-server (pre-packaged binary if possible)
```

**Adaptations:**

1. **Connection Reuse:**
   ```python
   # Global scope (outside handler)
   _mcp_client = None

   def get_mcp_client():
       global _mcp_client
       if _mcp_client is None or not _mcp_client.is_alive():
           _mcp_client = AWSMCPClient(...)
       return _mcp_client
   ```

2. **Timeout Handling:**
   - Set aggressive timeouts (30s) to avoid Lambda timeout
   - Implement graceful degradation to boto3

3. **Environment Configuration:**
   ```python
   # Lambda automatically provides AWS credentials via IAM role
   client = AWSMCPClient(use_lambda_credentials=True)
   ```

4. **Process Cleanup:**
   - Ensure subprocess cleanup in Lambda execution context
   - Use context managers for all MCP operations

**Alternative Approach (if subprocess issues persist):**
- Replace MCP with direct boto3 calls
- Preserve MCP interface but implement with boto3 backend
- Decision point: Test MCP in Lambda first

### 7. Frontend Migration

**Current:** Vite dev server (localhost:8080)
**Target:** S3 + CloudFront

**Build Process:**
```bash
cd ui
npm run build
# Generates ui/dist/ with static assets
```

**S3 Bucket Configuration:**
- Bucket name: `nhi-discovery-frontend-<env>`
- Static website hosting: Disabled (use CloudFront)
- Bucket policy: CloudFront OAI only
- Versioning: Enabled

**CloudFront Distribution:**
- Origin: S3 bucket (via OAI)
- Default root object: `index.html`
- Error pages: Redirect 404 → `/index.html` (SPA routing)
- Cache behavior:
  - `index.html`: No caching (Cache-Control: no-cache)
  - Assets (`/assets/*`): Long-term caching (1 year)
- TLS: ACM certificate for custom domain
- HTTP → HTTPS redirect

**Deployment Pipeline:**
```bash
# Build
npm run build

# Deploy to S3
aws s3 sync ui/dist/ s3://nhi-discovery-frontend-prod/ --delete

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E123... --paths "/*"
```

**Environment Configuration:**
Update `ui/.env.production`:
```bash
VITE_API_URL=https://api.nhi-discovery.example.com
VITE_OKTA_CLIENT_ID=<client_id>
VITE_OKTA_DOMAIN=dev-12345.okta.com
VITE_OKTA_ISSUER=https://dev-12345.okta.com/oauth2/default
```

**Code Changes Required:**

1. **API Client Update (`ui/src/lib/api.ts`):**
   ```typescript
   const API_BASE_URL = import.meta.env.VITE_API_URL;

   // Add Okta token to all requests
   const getAuthHeaders = () => {
     const token = sessionStorage.getItem('okta_access_token');
     return token ? { Authorization: `Bearer ${token}` } : {};
   };

   export async function searchIdentities(query: string) {
     const response = await fetch(`${API_BASE_URL}/api/identities/search`, {
       method: 'POST',
       headers: {
         'Content-Type': 'application/json',
         ...getAuthHeaders()
       },
       body: JSON.stringify({ query })
     });
     // ... handle response
   }
   ```

2. **Okta Integration (`ui/src/lib/okta.ts`):**
   ```typescript
   import { OktaAuth } from '@okta/okta-auth-js';

   export const oktaAuth = new OktaAuth({
     clientId: import.meta.env.VITE_OKTA_CLIENT_ID,
     issuer: import.meta.env.VITE_OKTA_ISSUER,
     redirectUri: window.location.origin + '/callback',
     scopes: ['openid', 'profile', 'email'],
     pkce: true
   });
   ```

3. **Remove Secure Mode Toggle:**
   - Okta provides user identity automatically
   - Remove `SecurityContext` and `SecurityModeToggle` component
   - All operations are user-scoped by default

4. **Add Authentication Guard:**
   ```typescript
   // ui/src/components/AuthGuard.tsx
   export function AuthGuard({ children }) {
     const { isAuthenticated, loading } = useOktaAuth();

     if (loading) return <LoadingSpinner />;
     if (!isAuthenticated) return <Navigate to="/login" />;

     return <>{children}</>;
   }
   ```

## Infrastructure as Code

**Tool:** AWS CDK (TypeScript)

**Project Structure:**
```
infrastructure/
├── bin/
│   └── nhi-discovery.ts          # CDK app entry point
├── lib/
│   ├── stacks/
│   │   ├── storage-stack.ts      # DynamoDB + S3
│   │   ├── compute-stack.ts      # Lambda functions
│   │   ├── api-stack.ts          # API Gateway
│   │   ├── bedrock-stack.ts      # Bedrock agent
│   │   ├── frontend-stack.ts     # S3 + CloudFront
│   │   └── monitoring-stack.ts   # CloudWatch dashboards
│   └── constructs/
│       ├── lambda-layer.ts       # MCP layer construct
│       └── okta-authorizer.ts    # Okta Lambda construct
├── package.json
├── tsconfig.json
└── cdk.json
```

**Stack Dependencies:**
```
StorageStack (DynamoDB, S3)
    ↓
ComputeStack (Lambdas)
    ↓
APIStack (API Gateway)
    ↓
FrontendStack (CloudFront)

BedrockStack (independent, referenced by ComputeStack)
MonitoringStack (depends on all stacks)
```

**Sample Stack (storage-stack.ts):**
```typescript
export class StorageStack extends Stack {
  public readonly identitiesTable: Table;
  public readonly secretsTable: Table;
  public readonly historyTable: Table;

  constructor(scope: Construct, id: string, props?: StackProps) {
    super(scope, id, props);

    // Identities Table
    this.identitiesTable = new Table(this, 'IdentitiesTable', {
      partitionKey: { name: 'PK', type: AttributeType.STRING },
      sortKey: { name: 'SK', type: AttributeType.STRING },
      billingMode: BillingMode.PAY_PER_REQUEST,
      timeToLiveAttribute: 'ttl',
      stream: StreamViewType.NEW_AND_OLD_IMAGES,
      pointInTimeRecovery: true
    });

    // GSI for type filtering
    this.identitiesTable.addGlobalSecondaryIndex({
      indexName: 'type-lastUsed-index',
      partitionKey: { name: 'type', type: AttributeType.STRING },
      sortKey: { name: 'lastUsed', type: AttributeType.STRING }
    });

    // ... other tables
  }
}
```

**Deployment Commands:**
```bash
cd infrastructure

# Bootstrap CDK (first time only)
cdk bootstrap aws://ACCOUNT_ID/us-east-1

# Synthesize CloudFormation templates
cdk synth

# Deploy to dev environment
cdk deploy --all --context env=dev

# Deploy to production
cdk deploy --all --context env=prod

# Destroy all resources
cdk destroy --all
```

**Environment Configuration:**
```json
// infrastructure/cdk.json
{
  "context": {
    "environments": {
      "dev": {
        "account": "123456789012",
        "region": "us-east-1",
        "oktaDomain": "dev-12345.okta.com",
        "domainName": "dev.nhi-discovery.example.com"
      },
      "prod": {
        "account": "987654321098",
        "region": "us-east-1",
        "oktaDomain": "prod.okta.com",
        "domainName": "nhi-discovery.example.com"
      }
    }
  }
}
```

## Migration Phases

### Phase 0: Preparation (Week 1)
**Goal:** Set up foundation and tooling

**Tasks:**
- [ ] Create `infrastructure/` directory with CDK project
- [ ] Set up AWS account and permissions
- [ ] Create Okta developer account and configure application
- [ ] Document current API contracts
- [ ] Create migration branch in Git

**Deliverables:**
- CDK project scaffolding
- Okta application configured
- AWS credentials configured

### Phase 1: Storage Layer (Week 1-2)
**Goal:** Create data persistence layer

**Tasks:**
- [ ] Define DynamoDB schemas (this document)
- [ ] Implement `StorageStack` in CDK
- [ ] Deploy DynamoDB tables to dev environment
- [ ] Create data access layer (DAL) module in `src/dal/`
- [ ] Write unit tests for DAL

**Deliverables:**
- DynamoDB tables deployed
- `src/dal/identities.py`, `src/dal/secrets.py`
- Test data loaded in dev

### Phase 2: Lambda Migration (Week 2-3)
**Goal:** Migrate backend logic to Lambda functions

**Tasks:**
- [ ] Create Lambda layer with MCP clients
- [ ] Implement IAM Discovery Lambda (`src/lambda/iam_discovery.py`)
- [ ] Test MCP clients in Lambda environment
- [ ] Implement Secrets Manager Lambda
- [ ] Implement Data Processor Lambda
- [ ] Deploy ComputeStack to dev

**Deliverables:**
- All Lambda functions deployed
- Lambda layer with MCP clients working
- Manual Lambda invocation tests passing

### Phase 3: API Gateway + Auth (Week 3-4)
**Goal:** Create authenticated API layer

**Tasks:**
- [ ] Implement Okta Lambda Authorizer
- [ ] Create API Gateway stack
- [ ] Define all REST endpoints
- [ ] Test Okta token validation
- [ ] Deploy APIStack to dev
- [ ] Test end-to-end API flows with Postman

**Deliverables:**
- API Gateway deployed with Okta auth
- Postman collection with authenticated requests
- API documentation updated

### Phase 4: Bedrock Integration (Week 4-5)
**Goal:** Replace OpenAI with AWS Bedrock

**Tasks:**
- [ ] Enable Bedrock in AWS account
- [ ] Create Bedrock agent configuration
- [ ] Set up knowledge bases (S3 + embeddings)
- [ ] Implement Bedrock Orchestrator Lambda
- [ ] Migrate IdentityAnalyzer logic to Bedrock action groups
- [ ] Test AI-powered search with Bedrock

**Deliverables:**
- Bedrock agent operational
- Search queries returning results
- Bedrock performance baseline

### Phase 5: Frontend Migration (Week 5-6)
**Goal:** Deploy React UI to CloudFront

**Tasks:**
- [ ] Install `@okta/okta-auth-js` and `@okta/okta-react`
- [ ] Implement Okta authentication in React
- [ ] Update API client to use API Gateway URLs
- [ ] Update all components to use new API
- [ ] Remove CLI-related UI features
- [ ] Build production bundle
- [ ] Deploy FrontendStack (S3 + CloudFront)
- [ ] Test UI end-to-end

**Deliverables:**
- React app deployed to CloudFront
- Okta login flow working
- All features functional in cloud

### Phase 6: Cleanup & Documentation (Week 6)
**Goal:** Remove legacy code and finalize documentation

**Tasks:**
- [ ] Remove `src/main.py` (CLI)
- [ ] Remove Typer, Rich from requirements
- [ ] Remove FastAPI local server code
- [ ] Update README.md with new architecture
- [ ] Update CLAUDE.md
- [ ] Create deployment runbook
- [ ] Create operations guide
- [ ] Tag release v0.2.0

**Deliverables:**
- Clean codebase without legacy components
- Complete documentation
- Production-ready release

### Phase 7: Monitoring & Optimization (Week 7+)
**Goal:** Ensure operational excellence

**Tasks:**
- [ ] Set up CloudWatch dashboards
- [ ] Configure alarms (Lambda errors, API 5xx, DynamoDB throttling)
- [ ] Enable X-Ray tracing
- [ ] Optimize Lambda cold starts
- [ ] Review and optimize costs
- [ ] Load testing
- [ ] Security audit

**Deliverables:**
- Monitoring dashboard operational
- Alarm runbook documented
- Performance benchmarks established

## Key Decision Points

### 1. MCP Client in Lambda
**Question:** Can MCP subprocess model work reliably in Lambda?

**Options:**
a) Keep MCP, optimize for Lambda (use Layer, connection reuse)
b) Replace MCP with boto3 for Lambda, keep MCP for local dev
c) Fully replace MCP with boto3 everywhere

**Decision:** **Option A** (test in Phase 2)
**Rationale:** Preserve investment in MCP integration, test viability first

**Fallback:** If MCP proves unreliable in Lambda, pivot to Option B

### 2. Infrastructure as Code Tool
**Question:** CDK or Terraform?

**Options:**
a) AWS CDK (TypeScript) - AWS-native, type-safe
b) Terraform - Multi-cloud, mature ecosystem

**Decision:** **AWS CDK**
**Rationale:**
- AWS-native project, no multi-cloud requirement
- Type safety and compile-time validation
- Better integration with AWS services
- Team familiar with TypeScript

### 3. Bedrock Agent Configuration
**Question:** How to structure Bedrock agent for identity analysis?

**Approach:**
- Start with single agent with multiple action groups
- Use knowledge bases for policy documentation
- Keep action groups focused (identity lookup, risk analysis)
- Iterate based on prompt performance

**Open Questions:**
- How to handle context window limits for large identity sets?
- Should we pre-process/summarize identities before passing to Bedrock?
- Bedrock agent response caching strategy?

### 4. Data Retention
**Question:** How long to retain identity discovery data?

**Proposal:**
- Active identities: Keep latest 30 days
- Historical identities: Archive to S3 after 30 days
- Discovery job logs: 90 days
- Use DynamoDB TTL for automatic cleanup

**Configuration:** Environment-specific (dev: 7 days, prod: 30 days)

### 5. Multi-Account Support
**Question:** When to add multi-account support?

**Decision:** **Not in Phase 1**
**Rationale:** Product doc specifies single account for MVP

**Future Approach:**
- Add AWS Organizations integration
- Deploy Lambda in management account
- Use cross-account IAM roles for discovery
- Add account selector in UI

### 6. Cost Optimization
**Question:** How to control costs in production?

**Strategies:**
- Use Lambda reserved concurrency limits
- DynamoDB on-demand with auto-scaling alerts
- S3 lifecycle policies for archives
- Bedrock request rate limiting
- CloudFront caching for static assets
- API Gateway throttling per user

**Budget Alerts:** Set up AWS Budgets with email notifications

## Risk Assessment

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| MCP clients fail in Lambda | High | Medium | Boto3 fallback, early testing in Phase 2 |
| Bedrock costs exceed budget | Medium | Medium | Request rate limiting, usage monitoring |
| Okta integration complexity | Medium | Low | Use official SDK, test early |
| DynamoDB throughput limits | High | Low | On-demand mode, monitoring |
| CloudFront cache invalidation delays | Low | Medium | Document for users, automate |
| Lambda cold starts impact UX | Medium | Medium | Provisioned concurrency for key functions |
| Knowledge base setup complexity | Medium | Medium | Use AWS documentation examples |

## Success Metrics

### Technical Metrics
- API response time p95 < 2 seconds
- Lambda cold start < 3 seconds
- UI load time < 2 seconds
- 99.9% API availability
- Zero critical security vulnerabilities

### Functional Metrics
- All current features working in cloud
- Okta authentication functional
- Bedrock search accuracy ≥ OpenAI baseline
- Secrets Manager integration complete
- Manual refresh working

### Cost Metrics
- Monthly AWS cost < $200 (dev)
- Monthly AWS cost < $500 (prod, estimated)

## Open Questions

1. **Bedrock Knowledge Base Setup:**
   - Where to source IAM policy documentation for knowledge base?
   - Embedding model selection (Titan vs Cohere)?
   - Knowledge base update frequency?

2. **Okta Configuration:**
   - Okta tenant details (dev vs prod)?
   - User provisioning strategy?
   - Group-based permissions in future?

3. **Multi-Region Strategy:**
   - Deploy to single region initially?
   - Which region (us-east-1)?
   - Future: Multi-region for HA?

4. **Monitoring & Alerting:**
   - Who receives CloudWatch alarms?
   - PagerDuty integration needed?
   - Logging retention policy?

5. **Secrets Manager Integration Scope:**
   - Enumerate all secrets or filter by tags?
   - Include secret values or metadata only?
   - Rotation analysis depth?

## Next Steps

1. **Immediate Actions:**
   - Review and approve this architecture document
   - Answer open questions above
   - Set up AWS account and Okta tenant
   - Create infrastructure CDK project
   - Start Phase 0 tasks

2. **First Sprint (Week 1):**
   - Implement DynamoDB schemas
   - Deploy StorageStack to dev
   - Test data access layer
   - Set up CI/CD pipeline basics

3. **Communication:**
   - Share this document with stakeholders
   - Schedule architecture review meeting
   - Create project tracking board
   - Set up weekly progress check-ins

## Appendix

### A. API Contract Mapping

| Current Endpoint | New Endpoint | Lambda | Changes |
|-----------------|--------------|--------|---------|
| `POST /api/identities/collect` | `POST /api/identities/collect` | iam_discovery | Add auth, return jobId |
| `POST /api/identities/search` | `POST /api/identities/search` | bedrock_orchestrator | Add auth, use Bedrock |
| `POST /api/query` | `POST /api/identities/search` | bedrock_orchestrator | Merge into search |
| `GET /api/health` | `GET /api/health` | health_check | Add service status checks |
| N/A | `POST /api/secrets/collect` | secrets_discovery | New endpoint |
| N/A | `GET /api/jobs/{jobId}` | query_handler | New endpoint |

### B. Environment Variables Migration

| Current (.env) | New (Lambda/SSM) | Notes |
|----------------|------------------|-------|
| `AWS_PROFILE` | IAM Role | Lambda execution role |
| `AWS_ACCESS_KEY_ID` | IAM Role | No hard-coded keys |
| `OPENAI_API_KEY` | N/A | Replaced by Bedrock |
| `API_PORT` | N/A | API Gateway manages |
| `CORS_ORIGINS` | SSM Parameter | CloudFront origin |
| N/A | `OKTA_DOMAIN` | New (SSM) |
| N/A | `OKTA_CLIENT_ID` | New (SSM) |
| N/A | `BEDROCK_AGENT_ID` | New (SSM) |
| N/A | `IDENTITIES_TABLE_NAME` | New (ENV) |

### C. Dependency Changes

**Removed:**
```
fastapi
uvicorn
typer
rich
openai
python-dotenv (partially)
```

**Added:**
```
aws-cdk-lib
boto3 (updated)
okta-jwt-verifier
aws-lambda-powertools
```

**Preserved:**
```
httpx
pydantic
```

### D. Testing Strategy

**Unit Tests:**
- Data access layer (DynamoDB operations)
- Lambda handler functions
- Okta token validation
- Bedrock response parsing

**Integration Tests:**
- API Gateway → Lambda flows
- DynamoDB Stream → Data Processor
- Bedrock agent invocation
- MCP client in Lambda

**E2E Tests:**
- Full user flow: Login → Search → View results
- Discovery job lifecycle
- Error handling (auth failures, Lambda timeouts)

**Load Tests:**
- API Gateway throughput
- Lambda concurrency limits
- DynamoDB capacity
- CloudFront cache hit ratio

**Tools:**
- pytest for unit/integration
- Locust for load testing
- Postman for API testing

---

**Document Version:** 1.0
**Last Updated:** 2025-11-21
**Next Review:** After Phase 2 completion
