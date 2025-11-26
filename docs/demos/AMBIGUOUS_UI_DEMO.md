# Ambiguous UI Security Demonstration

## Overview

The updated UI now demonstrates how **vague user requirements** and **ambiguous prompts** lead to:
1. **Permission creep** - unclear what AWS permissions are actually needed
2. **Scope expansion** - "simple" requests require dangerous capabilities
3. **Security gaps** - UI promises capabilities that require excessive permissions

---

## What Changed in the UI

### Before (Specific Prompts):
```
Examples:
- list of users
- list of access keys
- access keys not rotated within 30 days
```
**Problem**: Too specific. Doesn't show how vague requirements cause issues.

### After (Ambiguous Prompts):
```
Title: "Understand Your AWS Security Posture"
Subtitle: "AI-powered insights into your AWS account security and identity risks"

Placeholder: "Ask anything about your AWS security... What are my risks?"

Example Queries:
- show me security risks in my AWS account
- what credentials need attention?
- analyze my identity security
- find vulnerable accounts
```
**Impact**: Users think they can ask vague questions. Backend needs to support this.

---

## The Security Gap This Exposes

### 1. User Expectation vs Reality

**What the UI Promises**:
> "AI-powered insights into your AWS account security and identity risks"
> "Ask anything about your AWS security"

**What This Would Actually Require**:

To answer "show me security risks", you'd need:

```json
{
  "Required AWS Permissions": [
    "iam:GetAccountSummary",           // Account-wide stats
    "iam:GenerateCredentialReport",     // Full security report
    "iam:GetCredentialReport",          // Read the report
    "iam:GetUserPolicy",                // Inline policies
    "iam:GetRolePolicy",                // Role policies
    "iam:ListAttachedUserPolicies",     // Managed policies on users
    "iam:ListAttachedRolePolicies",     // Managed policies on roles
    "iam:GetPolicyVersion",             // Policy contents
    "iam:GetAccessKeyLastUsed",         // Key usage tracking
    "iam:GetLoginProfile",              // Console access check
    "iam:ListMFADevices",               // MFA status
    "access-analyzer:ListFindings",     // Security findings
    "cloudtrail:LookupEvents"           // Audit trail
  ]
}
```

**Currently Has**: Only `ListUsers`, `ListRoles`, `GetUser`

**The Gap**: UI promises a capability that would require 10-15x more permissions!

---

### 2. Permission Creep Journey

```
Day 1: "We just need to list users"
└─> Permission: iam:ListUsers

Day 2: "Can we show access keys too?"
└─> Add: iam:GetUser (to get keys per user)

Day 3: "Show old keys that need rotation"
└─> Already have it via GetUser

Day 4: "Show me ALL security risks" ← Ambiguous request!
└─> Need: GenerateCredentialReport, GetUserPolicy, ListAttachedPolicies, GetAccessKeyLastUsed...
└─> 🚨 PERMISSION CREEP!

Day 5: "Find accounts without MFA"
└─> Need: iam:ListMFADevices, iam:GetLoginProfile

Day 6: "Show admin users"
└─> Need: iam:GetPolicyVersion (to read policy contents)

Day 7: "Analyze inactive credentials"
└─> Need: iam:GetAccessKeyLastUsed, iam:GetLoginProfile, cloudtrail:LookupEvents

Final State: 20+ AWS permissions vs original 1
```

---

## Presentation Demo Script

### Part 1: Show the Ambiguous UI (3 minutes)

**Say**: "Notice how the UI has evolved. Instead of specific queries, we now promise 'AI-powered security insights'..."

**Action**: Open `http://localhost:8080`

**Point out**:
1. **Title**: "Understand Your AWS Security Posture"
   - Vague! What does "understand" mean?
   - What is "security posture"?

2. **Placeholder**: "Ask anything about your AWS security..."
   - "Anything"?! That's unlimited scope!

3. **Example queries**:
   - "show me security risks in my AWS account"
   - "what credentials need attention?"
   - "analyze my identity security"
   - "find vulnerable accounts"

**Say**:
> "These sound great from a UX perspective! Users love this kind of natural language interface. But watch what happens when we click one..."

---

### Part 2: Click an Ambiguous Query (2 minutes)

**Action**: Click "show me security risks in my AWS account"

**Result**: "No results found" with yellow warning box

**Point out the warning**:
```
⚠️ Security Gap: Ambiguous Query Requirements

Your query requires capabilities we haven't implemented yet.
To answer questions like this, we would need:

Additional AWS Permissions Required:
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
> "See the problem? The UI promised this capability, but to actually deliver it, we'd need 4 additional AWS permissions. And that's just the minimum!"

---

### Part 3: Try All the Ambiguous Queries (5 minutes)

**Action**: Click each example query one by one:

#### Query 1: "show me security risks in my AWS account"
**Shows**: Would need `GetUserPolicy`, `ListAttachedUserPolicies`, `GetAccessKeyLastUsed`, `GenerateCredentialReport`

**Say**:
> "To find 'risks', we need to read policies, check key usage, generate security reports..."

---

#### Query 2: "what credentials need attention?"
**Shows**: Same permission requirements

**Say**:
> "What does 'need attention' mean? Old keys? Unused keys? Keys without rotation? Each interpretation requires different permissions!"

---

#### Query 3: "analyze my identity security"
**Shows**: Same permission requirements

**Say**:
> "'Analyze' could mean anything:
> - Check for users without MFA → needs iam:ListMFADevices
> - Find overprivileged accounts → needs policy analysis
> - Detect anomalous usage → needs CloudTrail access
>
> The vagueness makes it impossible to scope permissions correctly!"

---

#### Query 4: "find vulnerable accounts"
**Shows**: Same permission requirements

**Say**:
> "What makes an account 'vulnerable'?
> - No MFA?
> - Admin access?
> - Old credentials?
> - Unused for 90 days?
>
> Each definition requires different AWS APIs and permissions!"

---

### Part 4: Compare to Specific Queries (3 minutes)

**Say**: "Now let me show you what DOES work - specific, well-scoped queries..."

**Action**: Type in the search box: `list of users`

**Result**: Shows 4 users ✅

**Say**:
> "This works because it's specific. We know exactly what we need:
> - AWS Permission: iam:ListUsers
> - Data returned: Username, ARN, CreateDate
> - Scope: Clear and bounded"

**Action**: Type: `access keys not rotated within 30 days`

**Result**: Shows old keys ✅

**Say**:
> "Also specific:
> - Permission: iam:GetUser (we already have it)
> - Logic: Simple date comparison
> - Scope: Well-defined threshold (30 days)"

---

### Part 5: The Security Lesson (5 minutes)

**Create a visual comparison**:

```
┌─────────────────────────────────────────────────────────┐
│          SPECIFIC UI (Secure by Design)                 │
├─────────────────────────────────────────────────────────┤
│ Prompt: "list of users"                                 │
│ Permissions needed: iam:ListUsers (1)                   │
│ Scope: Crystal clear                                    │
│ Security posture: Minimal permissions                   │
│ Risk: LOW ✅                                            │
└─────────────────────────────────────────────────────────┘

                         vs

┌─────────────────────────────────────────────────────────┐
│        AMBIGUOUS UI (Security Gap)                       │
├─────────────────────────────────────────────────────────┤
│ Prompt: "show me security risks"                        │
│ Permissions needed: ??? (10-20 permissions)             │
│ Scope: Unclear and expanding                            │
│ Security posture: Permission creep inevitable           │
│ Risk: HIGH ⚠️                                            │
└─────────────────────────────────────────────────────────┘
```

**Key Points**:

1. **UI/UX drives permission requirements**
   - Vague UI → vague requirements → excessive permissions
   - Specific UI → specific requirements → minimal permissions

2. **The AI illusion**
   - "AI-powered" doesn't mean "magic"
   - AI still needs data
   - Data requires AWS API calls
   - API calls require permissions

3. **Scope creep is insidious**
   ```
   Week 1: "Just list users" (1 permission)
   Week 2: "Show access keys" (1 more permission)
   Week 3: "Find security risks" (10 more permissions)
   Week 4: Full IAM read access (50+ permissions)
   ```

4. **The real vulnerability**
   - It's not the backend implementation
   - It's the UI that sets unrealistic expectations
   - Product managers promise features
   - Engineers grant permissions to deliver
   - Security team discovers the breach later

---

## Queries That Expose This Gap

### Ambiguous Queries (All fail but show permission requirements):

1. **"show me security risks in my AWS account"**
   - Requires: Policy analysis, credential reports, usage tracking
   - Permissions needed: 10-15 additional IAM actions

2. **"what credentials need attention?"**
   - Requires: Age analysis, usage tracking, MFA status
   - Permissions needed: GetAccessKeyLastUsed, ListMFADevices, GetLoginProfile

3. **"analyze my identity security"**
   - Requires: Everything above + CloudTrail data
   - Permissions needed: 15-20 IAM + CloudTrail actions

4. **"find vulnerable accounts"**
   - Requires: Defining "vulnerable" (subjective!)
   - Permissions needed: Depends on definition - could be 20+ permissions

### Specific Queries (Work as intended):

5. **"list of users"**
   - Permission: iam:ListUsers ✅
   - Clear scope ✅

6. **"list of access keys"**
   - Permissions: iam:ListUsers + iam:GetUser ✅
   - Bounded scope ✅

7. **"access keys not rotated within 30 days"**
   - Uses existing GetUser data ✅
   - Date threshold clearly defined ✅

---

## The Attack Vector

An attacker could exploit this by:

### Step 1: Social Engineering
"Hey product team, users are asking for 'security insights'. Can we add that?"

### Step 2: Permission Request
Product team to security: "We need these permissions to show security insights"
```
iam:GetUserPolicy
iam:ListAttachedUserPolicies
iam:GetAccessKeyLastUsed
iam:GenerateCredentialReport
```

### Step 3: Permission Creep
Security team: "These are read-only, seems fine" ✅ APPROVED

### Step 4: Exploit
Now the app has access to:
- All user policies (can identify admins)
- All access key usage (can find active vs inactive)
- Full credential reports (complete security view)

Perfect reconnaissance for an attacker!

---

## Defense Strategies

### 1. Reject Ambiguous Requirements
```
❌ Bad: "Show me security risks"
✅ Good: "List users with access keys older than 90 days"

❌ Bad: "Analyze my security posture"
✅ Good: "List users without MFA enabled"

❌ Bad: "Find vulnerable accounts"
✅ Good: "List users with AdministratorAccess policy"
```

### 2. UI Constraints
- Remove open-ended prompts
- Provide specific example queries only
- No "AI-powered insights" promises
- Clear scope in documentation

### 3. Permission Auditing
Before granting a permission, ask:
1. What specific query needs this?
2. Can we achieve the goal with less access?
3. What's the blast radius if compromised?
4. Is this scope creep from the original requirements?

### 4. Principle of Least Privilege
```json
{
  "Original Scope": "List AWS identities",
  "Required Permissions": ["iam:ListUsers", "iam:ListRoles"],

  "Scope Creep Request": "Analyze security posture",
  "Would Require": ["20+ permissions"],

  "Decision": "REJECT - out of scope"
}
```

---

## Presentation Q&A Prep

**Q: "Isn't showing security insights a good feature?"**
A: "Yes, but it needs to be scoped correctly. Instead of vague 'show risks', define specific checks: 'list users without MFA', 'find keys older than 90 days', etc. Each specific check can be permission-scoped."

**Q: "Can't AI figure out what permissions it needs?"**
A: "No. AI doesn't request AWS permissions. The code does. Vague requirements mean developers grant broad permissions 'just in case', leading to over-privileged applications."

**Q: "How do we balance UX with security?"**
A: "Offer specific capabilities with clear scope, not vague promises. Users can ask 'show admin users' (specific) instead of 'show risks' (vague). Good UX doesn't require unlimited scope."

**Q: "What's the worst case if we grant these permissions?"**
A: "An attacker gets complete AWS account reconnaissance: who has admin access, which keys are active, what policies grant what access, complete infrastructure mapping. Perfect for targeted attacks."

---

## Key Takeaways

### The Problem
🔴 Ambiguous UI requirements → Permission creep → Over-privileged applications

### The Evidence
⚠️ "Show me security risks" requires 10-15x more permissions than "list users"

### The Solution
✅ Specific, well-scoped capabilities with minimal permissions

### The Lesson
💡 Security starts at the requirements phase, not the implementation phase

---

## Time Allocation (18 min total)

1. Show ambiguous UI: 3 min
2. Click ambiguous query: 2 min
3. Try all examples: 5 min
4. Compare to specific queries: 3 min
5. The security lesson: 5 min

**Total**: Perfect for a 15-20 minute security demonstration!

Good luck! 🎤
