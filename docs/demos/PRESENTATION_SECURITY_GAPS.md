# Security Gaps Demonstration for Presentation

## Executive Summary

The NHI Agent app demonstrates **3 critical security gaps** that expose authorization vulnerabilities:

1. **Over-Privileged Credentials** - Access to 29 AWS IAM operations when only 3 are needed
2. **Excessive Data Exposure** - Access Key IDs and sensitive metadata leaked
3. **Bypassable UI Controls** - Backend has destructive capabilities despite read-only UI

---

## Demo Script for Presentation

### Part 1: Show Normal Operation (2 minutes)

**Say**: "Let me show you how the app works as intended..."

1. Open UI: `http://localhost:8080`
2. Click "list of users" → Shows 4 users ✅
3. Click "list of access keys" → Shows 4 keys with ages ✅
4. Click "access keys not rotated within 30 days" → Shows 2 old keys ⚠️

**Say**: "Great! The UI is working perfectly. It only supports these 5 safe, read-only queries."

---

### Part 2: Reveal the Security Gaps (5 minutes)

#### Gap #1: Over-Privileged Backend

**Say**: "But here's the problem - let me show you what's REALLY happening under the hood..."

**Action**: Run the security test
```bash
python3 test_permission_escalation.py
```

**Point out**:
```
⚠️ WRITE/MODIFY Tools (15) - DANGEROUS:
   • create_access_key      ← Can create new credentials!
   • delete_user            ← Can delete users!
   • attach_user_policy     ← Can grant admin access!
   • create_user            ← Can create backdoor accounts!
```

**Say**:
> "The UI only exposes 5 read-only queries, but the backend AWS credentials have access to **15 dangerous write operations**. If someone bypasses the UI or exploits the backend, they could:
> - Create new access keys for admin users
> - Delete users
> - Attach admin policies
> - Create backdoor accounts"

---

#### Gap #2: Sensitive Data Leakage

**Say**: "Even the 'safe' queries expose too much data..."

**Action**: Search for "list of access keys" and open browser DevTools → Network tab

**Point out the response**:
```json
{
  "title": "AKIAZG73ANJFBYCF7FG7 (aws-admin-user)",
  "description": "AWS Access Key: AKIAZG73ANJFBYCF7FG7 for user aws-admin-user (Age: 133 days)",
  "metadata": {
    "access_key_id": "AKIAZG73ANJFBYCF7FG7",  ← Half of credential pair!
    "status": "Active",
    "create_date": "2025-06-27T02:22:18+00:00",
    "UserName": "aws-admin-user",
    "_user_info": {
      "arn": "arn:aws:iam::633497217610:user/aws-admin-user"  ← AWS Account ID leaked!
    }
  }
}
```

**Say**:
> "Notice what's exposed:
> - **Access Key IDs** - Half of the credential pair. Not the secret, but still reconnaissance intel.
> - **AWS Account ID** - Buried in the ARN: `633497217610`. This is your AWS account number!
> - **User metadata** - Who has keys, when they were created, usage patterns."

---

#### Gap #3: Backend Has Destructive Capabilities

**Say**: "The scariest part? The backend can execute destructive operations..."

**Show the code** (src/mcp_client.py:89-120):
```python
def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
    """Call a tool on the MCP server."""
    # NO VALIDATION - can call ANY tool!
    response = self._send_request("tools/call", {
        "name": tool_name,
        "arguments": arguments
    })
```

**Demonstrate hypothetical attack**:
```python
# If attacker modifies the code or gains access:
client = AWSMCPClient()

# Create backdoor access key for admin
client.call_tool("create_access_key", {
    "user_name": "aws-admin-user"
})
# → Returns NEW access key + secret key!
```

**Say**:
> "There's NO validation in the MCP client. It will execute ANY IAM operation that the AWS credentials permit. The UI filtering is just a facade - it can be bypassed with direct API calls or code modification."

---

### Part 3: Show the Risk (2 minutes)

**Create a visual diagram**:

```
┌─────────────────────────────────────────────────┐
│  User's Intent: Read-only access to 5 queries   │
│  ✓ list users                                   │
│  ✓ list roles                                   │
│  ✓ list groups                                  │
│  ✓ list access keys                             │
│  ✓ access keys not rotated                      │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  UI Layer: Filters to 5 safe queries           │
│  (Can be bypassed)                              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  API Layer: No validation                       │
│  Accepts any query                              │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  MCP Client: No tool filtering                  │
│  Can call 29 IAM operations                     │
└─────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────┐
│  AWS Credentials: Full IAM permissions          │
│  ⚠️  create_access_key                          │
│  ⚠️  delete_user                                 │
│  ⚠️  attach_user_policy                          │
│  ⚠️  create_user                                 │
│  ⚠️  + 11 more destructive operations            │
└─────────────────────────────────────────────────┘
```

**Say**: "Defense in depth is broken at every layer."

---

### Part 4: Queries That Expose the Gaps (3 minutes)

**Safe queries (currently working but exposing too much)**:

1. **"list of access keys"**
   - **Permission needed**: `iam:GetUser` (for EVERY user)
   - **Exposes**: Access Key IDs, Account ID, password usage
   - **Risk**: Complete credential mapping

2. **"list of users"**
   - **Permission needed**: `iam:ListUsers`
   - **Exposes**: User ARNs with Account ID
   - **Risk**: Account enumeration

**Dangerous queries (blocked by UI but backend supports)**:

3. **Try searching**: "create access key for aws-admin-user"
   - **UI Response**: "No results found" ✅
   - **Backend Capability**: Could actually execute if UI bypassed ⚠️
   - **Would require**: `iam:CreateAccessKey`
   - **Impact**: Backdoor admin credentials

4. **Try searching**: "delete user terraform-user"
   - **UI Response**: "No results found" ✅
   - **Backend Capability**: Could execute ⚠️
   - **Would require**: `iam:DeleteUser`
   - **Impact**: Service disruption

**Say**:
> "The UI correctly blocks these dangerous queries. But if an attacker:
> - Modifies the Python backend code
> - Calls the API directly
> - Exploits a code injection vulnerability
>
> They could execute ANY of these 29 IAM operations!"

---

### Part 5: Attack Demo (3 minutes)

**Live demonstration**:

```bash
# 1. Show available write operations
python3 test_permission_escalation.py | grep "WRITE/MODIFY"

# Output shows:
⚠️  WRITE/MODIFY Tools (15) - DANGEROUS:
   • create_access_key
   • delete_user
   • attach_user_policy
   ...
```

**Explain hypothetical attack chain**:

```
Step 1: Attacker gains access to the server
   └─> Via: SSH compromise, code injection, insider threat

Step 2: Enumerate all users
   └─> Query: "list of users"
   └─> Result: aws-admin-user, terraform-user, etc.

Step 3: Identify high-value targets
   └─> Admin users with recent activity

Step 4: Execute privilege escalation
   └─> Python code: client.call_tool("create_access_key", {"user_name": "aws-admin-user"})
   └─> Returns: NEW Access Key ID + Secret Access Key

Step 5: Authenticate with new credentials
   └─> aws configure --profile hacked
   └─> Full admin access to AWS account

Step 6: Persist and exfiltrate
   └─> Create additional backdoor users
   └─> Attach admin policies
   └─> Access production data
```

---

## Recommended Fixes (For Q&A)

When asked "How would you fix this?", here's your answer:

### 1. Apply Principle of Least Privilege
**Current**: Credentials likely have `IAMReadOnlyAccess` or `IAMFullAccess`
**Should be**: Custom minimal policy

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iam:ListUsers",
      "iam:ListRoles",
      "iam:ListGroups"
    ],
    "Resource": "*"
  }]
}
```

### 2. Add Tool Whitelist in MCP Client
```python
# src/mcp_client.py

ALLOWED_TOOLS = ['list_users', 'list_roles', 'list_groups']

def call_tool(self, tool_name: str, arguments: Dict[str, Any]):
    if tool_name not in ALLOWED_TOOLS:
        raise PermissionError(f"Tool '{tool_name}' not permitted")
    return self._send_request("tools/call", {...})
```

### 3. Remove Sensitive Data from Responses
```python
def sanitize_key_response(key: Dict) -> Dict:
    return {
        "user": key.get("UserName"),
        "status": key.get("status"),
        "age_days": calculate_age(key.get("create_date"))
        # DO NOT return: access_key_id, ARN, account ID
    }
```

### 4. Add Defense in Depth
- ✅ Authentication (OAuth/SAML)
- ✅ Authorization (RBAC - who can see what)
- ✅ Rate limiting (prevent enumeration)
- ✅ Audit logging (CloudTrail + app-level)
- ✅ Input validation (prevent injection)

---

## Key Takeaways for Presentation

### The Good
✅ App demonstrates focused use case (5 queries)
✅ Clean UI/UX
✅ Works as intended for read-only operations

### The Bad
⚠️ Over-privileged credentials (29 operations vs 3 needed)
⚠️ Excessive data exposure (Key IDs, Account ID)
⚠️ No authentication or authorization

### The Ugly
💀 Backend can execute destructive operations
💀 UI filtering can be bypassed
💀 No audit trail
💀 Complete account takeover possible

### The Fix
🔒 Minimal IAM permissions
🔒 Tool whitelisting
🔒 Data sanitization
🔒 Defense in depth

---

## Questions You Might Get

**Q: "Is this app safe to use in production?"**
A: "Not without significant security hardening. It's a proof-of-concept that demonstrates the identity search capability, but would need authentication, authorization, minimal permissions, and audit logging before production use."

**Q: "How did you discover these vulnerabilities?"**
A: "By thinking like an attacker. I asked: 'What permissions does this REALLY need vs what does it HAVE?' Then tested what operations the backend could execute."

**Q: "Could someone actually exploit this?"**
A: "Yes. Anyone with access to the server or API could bypass the UI filtering. The credentials have the power to create admin access keys, which would be a complete account compromise."

**Q: "What's the worst-case scenario?"**
A: "An attacker gains access to the server, uses the MCP client to create admin access keys, authenticates with those keys, and has full control of your AWS account - can delete resources, access data, rack up charges, etc."

---

## Time Allocation (15 min total)

- Normal operation demo: 2 min
- Reveal security gaps: 5 min
- Show the risk: 2 min
- Queries that expose gaps: 3 min
- Attack demo: 3 min

Good luck with your presentation! 🎤
