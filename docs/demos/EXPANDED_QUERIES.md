# Expanded Query Support

## Overview

The backend now supports expanded queries that require additional AWS IAM permissions beyond the minimal set. These queries are **implemented in the backend but NOT shown in the UI** - users must manually type them to demonstrate permission creep.

---

## Minimal Permission Queries (Original - 3 queries)

These work with minimal IAM permissions:

### 1. List of Users
**Query**: `list of users`
**Permissions Required**: `iam:ListUsers`
**Returns**: All IAM users

### 2. List of Access Keys
**Query**: `list of access keys`
**Permissions Required**: `iam:ListUsers`, `iam:GetUser`
**Returns**: All access keys across all users

### 3. Access Keys Not Rotated
**Query**: `access keys not rotated within 30 days` (or any number of days)
**Permissions Required**: `iam:ListUsers`, `iam:GetUser`
**Returns**: Access keys older than the specified threshold

---

## Expanded Permission Queries (New - Requires Additional Permissions)

### 4. Admin Users
**Queries**:
- `show me admin users`
- `list users with admin access`
- `who has administrator access`

**Permissions Required**:
- `iam:ListUsers`
- `iam:ListAttachedUserPolicies`
- `iam:ListUserPolicies`

**Returns**: Users with admin policies (AdministratorAccess or policies containing "admin")

**Permission Creep**: +2 permissions (policy reading)

---

### 5. Users Without MFA
**Queries**:
- `show me users without mfa`
- `list users with no mfa`
- `who is missing mfa`

**Permissions Required**:
- `iam:ListUsers`
- `iam:ListMFADevices`
- `iam:GetLoginProfile`

**Returns**: Users with console access but no MFA enabled

**Permission Creep**: +2 permissions (MFA and login profile checking)

---

### 6. Security Risks
**Queries**:
- `show me security risks`
- `what are my security vulnerabilities`
- `find vulnerable accounts`

**Permissions Required**:
- `iam:ListUsers`
- `iam:GetUser`
- `iam:ListAttachedUserPolicies`
- `iam:ListUserPolicies`
- `iam:ListMFADevices`
- `iam:GetLoginProfile`

**Returns**: Combined results of:
- Users without MFA
- Admin users (high-privilege accounts)
- Old access keys (90+ days)

**Permission Creep**: +4 permissions (comprehensive security audit)

---

### 7. Inactive Identities
**Queries**:
- `show me inactive users`
- `list unused access keys`
- `what credentials are not being used`

**Permissions Required**:
- `iam:ListUsers`
- `iam:GetUser`
- `iam:GetAccessKeyLastUsed`

**Returns**: Access keys that:
- Have never been used, OR
- Haven't been used in 90+ days

**Permission Creep**: +1 permission (usage tracking)

---

## Permission Comparison

### Original Scope (3 permissions)
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iam:ListUsers",
      "iam:GetUser",
      "iam:ListRoles"
    ],
    "Resource": "*"
  }]
}
```

### Expanded Scope (9 permissions - 3x increase)
```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": [
      "iam:ListUsers",
      "iam:GetUser",
      "iam:ListRoles",
      "iam:ListAttachedUserPolicies",
      "iam:ListUserPolicies",
      "iam:GetPolicy",
      "iam:GetPolicyVersion",
      "iam:ListMFADevices",
      "iam:GetLoginProfile",
      "iam:GetAccessKeyLastUsed"
    ],
    "Resource": "*"
  }]
}
```

---

## Testing the Expanded Queries

### Without Expanded Permissions

If you try these queries without granting the additional permissions, you'll get:
- **Empty results** (queries will fail silently)
- **Error messages** in the API server logs showing permission denied

### With Expanded Permissions

1. Update your AWS IAM policy to include the expanded permissions
2. Restart the API server
3. Manually type the expanded queries in the search box
4. Results will show enriched data (MFA status, policy info, usage data)

---

## Demo Script for Presentation

### Step 1: Show Minimal Queries Working
1. Search: `list of users` → Shows 4 users ✅
2. Search: `list of access keys` → Shows 4 keys ✅
3. Search: `access keys not rotated within 30 days` → Shows old keys ✅

### Step 2: Show Permission Creep
1. Manually type: `show me admin users`
   - **Without permissions**: Empty results or error
   - **With permissions**: Shows users with admin policies

2. Manually type: `show me users without mfa`
   - **Without permissions**: Empty results or error
   - **With permissions**: Shows users needing MFA

3. Manually type: `show me security risks`
   - **Without permissions**: Empty results or error
   - **With permissions**: Shows comprehensive security audit

### Step 3: Demonstrate Permission Escalation
Show how one "reasonable" request leads to 3x permission expansion:

```
Product Manager: "Can we show security risks?"
                      ↓
Engineer: "Sure, we just need a few more permissions..."
                      ↓
Security Team: "Wait, you now have access to:
                - All user policies
                - All MFA status
                - All login profiles
                - All key usage data
                This is 3x the original scope!"
```

---

## Key Takeaways for Presentation

1. **Scope Creep is Real**: Going from "list users" to "show risks" requires 3x more permissions
2. **Vague Requirements = Permission Bloat**: "Security risks" is too broad to scope properly
3. **Attack Surface Grows**: Each new permission is a potential exploit vector
4. **Defense in Depth Needed**: Backend has the capability, but needs auth/authz controls to prevent abuse

---

## Implementation Details

### Backend Files Modified:
- **src/mcp_client.py**: Added 9 new methods for expanded IAM operations
- **src/identity_collector.py**: Added `collect_enriched_user_data()` method
- **src/identity_analyzer.py**: Added 4 query handlers for expanded queries
- **src/api_server.py**: Updated to pass collector to analyzer

### Query Detection Logic:
The analyzer uses keyword matching to detect query types:
- "admin" → Admin user search
- "mfa" → MFA status search
- "risk" or "vulnerable" → Security risk search
- "inactive" or "unused" → Usage tracking search

### Error Handling:
- If permissions are missing, methods return empty results
- Errors are logged but not exposed to UI
- This creates a "silent failure" that's hard to debug (intentional for demo)
