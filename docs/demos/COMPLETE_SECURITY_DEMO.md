# Complete Security Demonstration Guide
## Exposing Authorization & Permission Gaps in NHI Agent

---

## Executive Summary

This demo showcases **3 layers of security vulnerabilities**:

1. **UI Layer**: Ambiguous prompts promise capabilities beyond the app's scope
2. **Backend Layer**: Over-privileged credentials (29 operations vs 3 needed)
3. **Architecture Layer**: No defense-in-depth (authentication, authorization, auditing)

**Demo Time**: 20 minutes
**Impact**: Shows how vague requirements → permission creep → security breaches

---

## Pre-Demo Setup (5 minutes before)

```bash
# 1. Start the API server
cd /Users/kartiklunkad/workspace/nhi-agent
python3 run_api.py

# 2. Start the UI (in another terminal)
cd ui
npm run dev

# 3. Verify both are running
# API: http://localhost:8000/docs
# UI: http://localhost:8080

# 4. Have these files ready to show:
# - test_permission_escalation.py (backend demo)
# - AMBIGUOUS_UI_DEMO.md (UI demo reference)
# - PRESENTATION_SECURITY_GAPS.md (talking points)
```

---

## Act 1: The Illusion (5 minutes)
### "Look how nice this app is!"

### Show the UI Working

**Open**: `http://localhost:8080`

**First Impression**:
- Clean, modern interface ✅
- AI-powered security insights ✨
- Natural language search 🎯

**Say**:
> "This is the NHI Agent - a tool for understanding your AWS security posture. Notice the modern UX: you can ask questions in natural language like 'show me security risks' or 'find vulnerable accounts'. Very user-friendly!"

**Demo**: Type `list of users` → Shows 4 users

**Say**:
> "Great! It works. Let's try another..."

**Demo**: Type `list of access keys` → Shows 4 access keys with ages

**Say**:
> "Perfect! And we can even find old credentials..."

**Demo**: Type `access keys not rotated within 30 days` → Shows 2 old keys

**Say**:
> "Excellent! We found keys that are 133 and 960 days old. This seems like a useful security tool!"

---

## Act 2: The Cracks Appear (7 minutes)
### "But wait... what's this?"

### Try an Ambiguous Query

**Say**: "Now, the UI suggests I can ask about 'security risks'. Let me try that..."

**Demo**: Click "show me security risks in my AWS account"

**Result**: Yellow warning box appears!

**Read aloud**:
```
⚠️ Security Gap: Ambiguous Query Requirements

Your query requires capabilities we haven't implemented yet.
To answer questions like this, we would need:

⚠️ iam:GetUserPolicy - Read inline policies
⚠️ iam:ListAttachedUserPolicies - See permission levels
⚠️ iam:GetAccessKeyLastUsed - Track key usage
⚠️ iam:GenerateCredentialReport - Analyze security posture

🚨 Security Risk
Vague requirements like "show me risks" lead to permission creep.
We'd need read access to policies, credential reports, and usage data -
far beyond our original scope of just listing identities.
```

**Say**:
> "Wait... the UI PROMISED this feature. It's right there in the examples! But to actually deliver it, we'd need 4-10 additional AWS permissions. This is the first gap: **The UI promises capabilities beyond its design scope.**"

### Show Permission Creep

**Create a slide/diagram**:
```
Original Requirement: "List AWS users"
└─> Permission: iam:ListUsers (1 permission)

Feature Request: "Show access keys"
└─> Added: iam:GetUser (2 permissions)

Feature Request: "Find old keys"
└─> No new permission (uses GetUser)

UI Promise: "Show me security risks"
└─> Would Need: 10-15 NEW permissions ⚠️
    - iam:GetUserPolicy
    - iam:ListAttachedUserPolicies
    - iam:GetAccessKeyLastUsed
    - iam:GenerateCredentialReport
    - iam:ListMFADevices
    - iam:GetLoginProfile
    - ... and more

Final State: 20+ permissions (vs original 1)
```

**Key Point**:
> "The UI became a liability. By promising vague capabilities like 'AI-powered insights' and 'security risk analysis', it created pressure to grant excessive permissions."

---

## Act 3: The Hidden Danger (8 minutes)
### "It gets worse..."

### Run the Security Audit

**Say**: "That was the UI problem. But the real danger is in the backend. Let me show you..."

**Run**:
```bash
python3 test_permission_escalation.py
```

**Show the output** (pause at each section):

#### Section 1: Available Tools
```
⚠️ WRITE/MODIFY Tools (15) - DANGEROUS:
   • create_access_key      ← Can create admin credentials!
   • delete_user            ← Can delete accounts!
   • attach_user_policy     ← Can grant admin access!
   • create_user
   • delete_access_key
   • ...
```

**Say**:
> "Look at this! The backend has access to 15 DANGEROUS write operations. The UI only exposes 5 safe, read-only queries. But if someone bypasses the UI - through API calls, code modification, or exploitation - they can execute ANY of these operations!"

#### Section 2: Data Exposure
```
📊 Data Exposed:
   • ARN (reveals Account ID): arn:aws:iam::633497217610:user/...
   • ⚠️ AWS Account ID Leaked: 633497217610
   • Access Keys: 2 found
     - Key ID: AKIAZG73ANJFBYCF7FG7 (⚠️ Half of credential pair)
```

**Say**:
> "Even the 'safe' queries leak sensitive information:
> - AWS Account ID: `633497217610` - your account number
> - Access Key IDs: Half of your credentials
> - This is perfect reconnaissance data for an attacker!"

#### Section 3: Attack Scenario
```
[3] POTENTIAL ATTACK SCENARIO
If attacker gains code execution access, they could:
   Step 1: Enumerate all users
   Step 2: Identify admin users
   Step 3: Call create_access_key tool:
   >>> client.call_tool('create_access_key', {'user_name': 'aws-admin-user'})
   Step 4: Retrieve NEW credentials (Access Key + Secret Key)
   Step 5: Authenticate as admin
   Step 6: Complete account takeover
```

**Say**:
> "The attack path is clear:
> 1. Gain access to the server (SSH, code injection, insider)
> 2. Use the MCP client to create admin access keys
> 3. Authenticate with the new credentials
> 4. Full AWS account control
>
> The UI filtering is just a facade. It can be bypassed."

#### Section 4: Permission Analysis
```
🚨 What the app ACTUALLY has access to:
   • All READ tools (ListUsers, GetUser, ListRoles, etc.)
   • All WRITE tools (CreateUser, DeleteUser, CreateAccessKey, etc.)
   • Total: 29 IAM operations available

⚡ Risk Level: HIGH
   - Over-privileged credentials
   - No operation filtering in MCP client
   - UI filtering can be bypassed
```

**Say**:
> "Gap #2: **The backend is over-privileged by 10x.**
>
> We only need 3 operations:
> - iam:ListUsers
> - iam:ListRoles
> - iam:ListGroups
>
> But we have 29 operations, including destructive ones!"

---

## Act 4: The Triple Threat (3 minutes)
### "Three layers of failure"

**Create a diagram**:

```
┌──────────────────────────────────────────────────────┐
│  LAYER 1: UI (Promises Too Much)                     │
├──────────────────────────────────────────────────────┤
│  Ambiguous prompts:                                  │
│  • "Show me security risks"                          │
│  • "Analyze my AWS security"                         │
│  • "Find vulnerable accounts"                        │
│                                                       │
│  🚨 Problem: Vague requirements → permission creep   │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 2: Backend (Too Many Permissions)             │
├──────────────────────────────────────────────────────┤
│  AWS Credentials have access to:                     │
│  • 29 IAM operations                                 │
│  • Including: CreateAccessKey, DeleteUser, etc.      │
│                                                       │
│  🚨 Problem: Over-privileged by 10x                  │
└──────────────────────────────────────────────────────┘
                      ↓
┌──────────────────────────────────────────────────────┐
│  LAYER 3: Architecture (No Defense in Depth)         │
├──────────────────────────────────────────────────────┤
│  Missing:                                            │
│  • Authentication (anyone can access)                │
│  • Authorization (no RBAC)                           │
│  • Audit logging (no trail)                          │
│  • Rate limiting (enumeration possible)              │
│  • Input validation (injection risk)                 │
│                                                       │
│  🚨 Problem: Single point of failure                 │
└──────────────────────────────────────────────────────┘
                      ↓
                 BREACH! 💀
```

**Say**:
> "This is a perfect storm:
> 1. UI promises vague capabilities
> 2. Backend gets excessive permissions to deliver
> 3. No security controls to prevent abuse
>
> Any breach at any layer compromises the entire AWS account."

---

## Act 5: The Specific Queries (2 minutes)
### "Here's how it should work"

**Show working queries**:

1. `list of users` - Works ✅
   - Permission: iam:ListUsers
   - Scope: Clear

2. `list of access keys` - Works ✅
   - Permission: iam:GetUser
   - Scope: Bounded

3. `access keys not rotated within 30 days` - Works ✅
   - Logic: Date comparison
   - Threshold: Defined (30 days)

**Say**:
> "These work because they're SPECIFIC:
> - Clear scope
> - Defined output
> - Minimal permissions
> - No ambiguity
>
> Compare to: 'show me security risks' - what does that even mean?"

---

## Summary & Takeaways (2 minutes)

### The Three Gaps

1. **UI Gap**: Ambiguous prompts → permission creep
   - Example: "Show security risks" requires 10-15 permissions
   - Fix: Specific capabilities only

2. **Backend Gap**: Over-privileged credentials → attack surface
   - Has: 29 operations (including CreateAccessKey)
   - Needs: 3 operations (ListUsers, ListRoles, ListGroups)
   - Fix: Minimal IAM policy

3. **Architecture Gap**: No defense in depth → single point of failure
   - Missing: Auth, authz, audit, rate limiting
   - Fix: Security controls at every layer

### The Root Cause

```
Vague Requirements
     ↓
Unclear Permission Needs
     ↓
"Better grant broad access just in case"
     ↓
Over-Privileged Application
     ↓
Single Exploit → Full Compromise
```

### The Fix

```
Specific Requirements
     ↓
Clear Permission Needs
     ↓
Minimal IAM Policy
     ↓
Defense in Depth
     ↓
Breach Containment
```

---

## Demo Queries Summary

### Queries That Work (Specific):
1. ✅ `list of users`
2. ✅ `list of roles`
3. ✅ `list of groups`
4. ✅ `list of access keys`
5. ✅ `access keys not rotated within 30 days`

### Queries That Expose UI Gaps (Ambiguous):
6. ❌ `show me security risks in my AWS account`
   - Shows: Permission requirements (10-15 new permissions)
   - Demonstrates: UI promise vs reality gap

7. ❌ `what credentials need attention?`
   - Shows: Vague requirements
   - Demonstrates: Impossible to scope permissions

8. ❌ `analyze my identity security`
   - Shows: Unlimited scope
   - Demonstrates: Permission creep

9. ❌ `find vulnerable accounts`
   - Shows: Subjective criteria
   - Demonstrates: Unclear requirements

### Queries That Would Expose Backend Gaps (If implemented):
10. ⚠️ `create access key for admin user` (blocked by UI, backend could do it)
11. ⚠️ `delete user terraform-user` (blocked by UI, backend could do it)

---

## Questions & Answers

**Q: Is this app production-ready?**
A: "No. It's a proof-of-concept that demonstrates the capability, but needs significant security hardening: minimal permissions, authentication, authorization, audit logging, and specific (not vague) features."

**Q: What's the worst-case scenario?**
A: "An attacker gains server access, uses the over-privileged credentials to create admin access keys via the MCP client, authenticates with those keys, and has full control of your AWS account."

**Q: How do you prevent this?**
A: "Three things:
1. **Specific requirements** - No vague promises like 'show risks'
2. **Minimal permissions** - Only grant exactly what's needed
3. **Defense in depth** - Auth, authz, audit at every layer"

**Q: Isn't this just a demo? Why does it matter?**
A: "This is exactly how real breaches happen:
- Product team promises 'AI insights'
- Engineers grant broad permissions to deliver
- Security discovers the issue after breach
- By then, it's too late"

**Q: What should we do differently?**
A: "Start with security requirements:
- Define specific capabilities (not vague insights)
- Scope exact permissions needed for each
- Implement controls before features
- Audit regularly for permission creep"

---

## Materials Needed

### Code
- ✅ `test_permission_escalation.py` - Backend security test
- ✅ Updated UI with ambiguous prompts
- ✅ Working API server

### Documentation
- ✅ `AMBIGUOUS_UI_DEMO.md` - UI gap details
- ✅ `PRESENTATION_SECURITY_GAPS.md` - Backend gap details
- ✅ `security_audit.md` - Technical analysis
- ✅ `COMPLETE_SECURITY_DEMO.md` - This file

### Visuals (Create these)
- Permission creep diagram
- Three-layer failure diagram
- Specific vs ambiguous comparison table

---

## Time Breakdown (20 minutes)

| Section | Time | Content |
|---------|------|---------|
| Act 1: The Illusion | 5 min | Show working app |
| Act 2: The Cracks | 7 min | Ambiguous UI problems |
| Act 3: The Hidden Danger | 8 min | Backend over-privileged |
| Act 4: Triple Threat | 3 min | All layers failing |
| Act 5: The Right Way | 2 min | Specific queries |
| Summary | 2 min | Key takeaways |

**Total**: ~27 minutes (trim as needed)

---

## Success Metrics

After this demo, your audience should understand:

✅ Vague requirements → permission creep
✅ UI promises drive backend permissions
✅ Over-privileged credentials = attack vector
✅ Defense in depth is mandatory
✅ Specific > Ambiguous (always)

Good luck with your presentation! 🎤🔒
