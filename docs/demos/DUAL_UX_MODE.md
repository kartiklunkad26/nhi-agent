# Dual UX Mode: Insecure vs Secure

## Overview

The app now supports two security modes to demonstrate the difference between over-privileged and properly scoped credentials.

---

## Modes

### 🔓 Insecure Mode (Default)

**Credentials Used:** Admin AWS credentials (from `AWS_PROFILE` or `AWS_ACCESS_KEY_ID`)

**What You Can See:**
- All users in the AWS account
- All access keys across all users
- All roles and groups
- Full AWS IAM visibility

**Purpose:** Demonstrates the risk of over-privileged credentials

**Visual Indicators:**
- Orange "⚠️ Make it more secure" button
- Orange warning banner
- Alert triangle icon

---

### 🔒 Secure Mode

**Credentials Used:** User-specific credentials (from `AWS_USER_{username}_KEY`)

**What You Can See:**
- Only the selected user's data
- Only that user's access keys
- Limited to what that user's IAM permissions allow
- AWS IAM enforces the restriction

**Purpose:** Demonstrates principle of least privilege

**Visual Indicators:**
- Green "🔒 Secure Mode" button
- Green success banner
- Lock icon

---

## Setup Instructions

### Step 1: Configure .env File

Copy `.env.example` to `.env` and fill in your credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```bash
# ========== INSECURE MODE ==========
AWS_PROFILE=default
AWS_REGION=us-east-1

# ========== SECURE MODE ==========
# Each user needs their own credentials
AWS_USER_aws-admin-user_KEY=AKIA...
AWS_USER_aws-admin-user_SECRET=...

AWS_USER_terraform-user_KEY=AKIA...
AWS_USER_terraform-user_SECRET=...

# ... add more users as needed

# ========== Required ==========
OPENAI_API_KEY=sk-...
```

### Step 2: Create User-Specific Access Keys in AWS

For each IAM user, create access keys with minimal permissions:

1. **Go to AWS IAM Console**
2. **Select the user** (e.g., aws-admin-user)
3. **Security credentials tab** → Create access key
4. **Copy the Access Key ID and Secret Access Key**
5. **Add to .env** as shown above

### Step 3: Apply Minimal IAM Policy

Attach this policy to each user (replace `ACCOUNT_ID` and `USERNAME`):

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetUser",
        "iam:ListAccessKeys"
      ],
      "Resource": "arn:aws:iam::ACCOUNT_ID:user/USERNAME"
    }
  ]
}
```

**Example for aws-admin-user:**
```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "iam:GetUser",
        "iam:ListAccessKeys"
      ],
      "Resource": "arn:aws:iam::633497217610:user/aws-admin-user"
    }
  ]
}
```

This ensures each user can ONLY see their own data.

---

## Usage

### Toggle Between Modes

**In the UI header, click the security button:**
- Orange "⚠️ Make it more secure" → Switches to Secure Mode
- Green "🔒 Secure Mode" → Switches to Insecure Mode

**The toggle persists across page refreshes** (saved in localStorage).

---

## Example Scenarios

### Scenario 1: Insecure Mode

**Setup:**
- User selector: aws-admin-user
- Security mode: OFF (insecure)

**Query:** `list of users`

**Result:**
```
Found 5 users:
1. aws-admin-user
2. terraform-user
3. kartik-aws-user
4. test-user
5. demo-user
```

**Why:** Admin credentials can see all users.

---

### Scenario 2: Secure Mode

**Setup:**
- User selector: aws-admin-user
- Security mode: ON (secure)

**Query:** `list of users`

**Result:**
```
Found 1 user:
1. aws-admin-user
```

**Why:** Using aws-admin-user's credentials which only have permission to see themselves.

---

### Scenario 3: Secure Mode - Different User

**Setup:**
- User selector: terraform-user
- Security mode: ON (secure)

**Query:** `list of access keys`

**Result:**
```
Found 1 key:
1. AKIAZG73ANJFXYZ9876 (terraform-user) - Age: 45 days
```

**Why:** Using terraform-user's credentials which only see their own keys.

---

### Scenario 4: Comparative Query (Works in Both Modes)

**Setup:**
- User selector: aws-admin-user
- Security mode: Either ON or OFF

**Query:** `are my access keys the oldest`

**Result (Insecure Mode):**
```
✅ YES - You have the OLDEST access keys (960 days)

Ranking:
👉 1. aws-admin-user - 960 days
   2. terraform-user - 133 days
   3. kartik-aws-user - 45 days
```

**Result (Secure Mode):**
```
Error: Cannot compare - insufficient permissions to list other users
```

**Why:** In secure mode, the user can't see other users to compare against.

---

## Error Handling

### Missing User Credentials

**If you enable secure mode but haven't configured credentials:**

**Error Message:**
```
User-specific credentials not configured for aws-admin-user.
Set AWS_USER_aws-admin-user_KEY and AWS_USER_aws-admin-user_SECRET in .env
```

**Solution:** Add the credentials to your `.env` file.

---

### No User Selected

**If secure mode is enabled but no user is selected:**

**Behavior:** Falls back to insecure mode with admin credentials.

**Banner Shows:** Warning that no user is selected.

---

## Demo Script

### Show Insecure Mode (Over-privileged credentials)

1. **Open app** - Default is insecure mode
2. **Point out orange banner:** "Using admin credentials"
3. **Select any user:** aws-admin-user
4. **Query:** `list of users`
5. **Result:** Shows ALL 5 users
6. **Say:** "See? Even though I selected aws-admin-user, the admin credentials can see everyone. This is over-privileged."

---

### Switch to Secure Mode (Least privilege)

1. **Click:** "Make it more secure" button
2. **Point out change:** Button turns green, banner turns green
3. **Read banner:** "Using aws-admin-user's credentials with minimal permissions"
4. **Query:** `list of users`
5. **Result:** Shows ONLY aws-admin-user
6. **Say:** "Now we're using aws-admin-user's own credentials. AWS IAM enforces that they can only see themselves. This is the principle of least privilege."

---

### Switch Users in Secure Mode

1. **Switch user dropdown:** Select terraform-user
2. **Banner updates:** "Using terraform-user's credentials"
3. **Query:** `list of access keys`
4. **Result:** Shows only terraform-user's keys
5. **Say:** "Each user has their own credentials with minimal permissions. No cross-user access."

---

### Show Comparative Query Limitation

1. **Secure mode ON**
2. **User:** aws-admin-user
3. **Query:** `are my access keys the oldest`
4. **Result:** Error (can't see other users to compare)
5. **Switch back to insecure mode**
6. **Same query:** Now works (can see all users)
7. **Say:** "Some queries need broader access. That's the trade-off with least privilege."

---

## Technical Details

### Backend Implementation

**Credential Selection Logic:**
```python
if request.secure_mode and request.current_user:
    # Use user-specific credentials
    user_creds = get_user_credentials(request.current_user)
    collector = IdentityCollector(
        aws_access_key_id=user_creds["aws_access_key_id"],
        aws_secret_access_key=user_creds["aws_secret_access_key"]
    )
else:
    # Use admin credentials
    collector = IdentityCollector(
        aws_profile=credentials.get("aws_profile")
    )
```

### Frontend State

**SecurityContext:**
- Manages `secureMode` boolean state
- Persists to localStorage
- Provides to all components

**Mode Toggle:**
- Updates state
- Triggers re-render with new banner
- Next query uses new credentials

---

## Key Takeaways

✅ **Insecure Mode shows the risk:** Admin credentials = too much access

✅ **Secure Mode shows the fix:** User-specific credentials = least privilege

✅ **AWS IAM enforces security:** Not just UI filtering, but real IAM restrictions

✅ **Visual feedback:** Clear indicators of which mode you're in

✅ **Persistent:** Mode choice saved across sessions

✅ **Error handling:** Clear messages if credentials missing

---

## Troubleshooting

**Q: Secure mode doesn't limit results**

A: Check that the user-specific credentials in `.env` have the minimal IAM policy applied (not admin permissions).

**Q: Error about missing credentials**

A: Add `AWS_USER_{username}_KEY` and `AWS_USER_{username}_SECRET` to your `.env` file.

**Q: Mode doesn't persist after refresh**

A: Check browser localStorage - should have `nhi-agent-secure-mode` key.

**Q: Both modes show the same results**

A: You may be using the same credentials for both modes. Verify that user-specific credentials are different from admin credentials.

---

Good luck with your presentation! 🎤🔒
