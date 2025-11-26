# Simple User Authentication

## Overview

The app now has simple user authentication implemented via a user selector dropdown. No passwords, no JWT tokens - just a dropdown to select which AWS IAM user you are.

---

## How It Works

### Frontend
1. **User Selector Dropdown** in the header
2. **Predefined Users** list matching AWS IAM usernames
3. **localStorage Persistence** - selection persists across page refreshes
4. **Auth Context** - Shares current user across components

### Backend
1. **Optional `current_user` Parameter** on search endpoint
2. **Context-Aware Queries** - Understands "my" queries

---

## Using the Feature

### Step 1: Select Your User

When you open the app, you'll see a dropdown in the header:

```
Logged in as: [aws-admin-user ▼]
```

Click the dropdown and select your AWS IAM username.

### Step 2: Search with "My" Queries

Now you can use queries like:
- `are my access keys the oldest`
- `are my keys the oldest amongst all users`

The app knows who "my" refers to based on your selection!

---

## Query Examples

### Without User Selected

**Query**: `are my access keys the oldest`

**Result**:
```
Title: User Identity Required
Description: Please select your AWS IAM user from the dropdown to check your access keys.
```

### With User Selected (aws-admin-user)

**Query**: `are my access keys the oldest`

**Result**:
```
Title: Access Key Age Check - aws-admin-user
Description: Your access keys are 960 days old.
             ✅ YES - You have the OLDEST access keys among all users.
             Next oldest: terraform-user (133 days old)

Key Age Ranking:
👉 1. aws-admin-user - 960 days old
   2. terraform-user - 133 days old
   3. kartik-aws-user - 45 days old
   4. test-user - 12 days old
```

### With User Selected (terraform-user)

**Query**: `are my access keys the oldest`

**Result**:
```
Title: Access Key Age Check - terraform-user
Description: Your access keys are 133 days old.
             ❌ NO - aws-admin-user has the oldest keys (960 days old).
             Your keys are 827 days newer.

Key Age Ranking:
   1. aws-admin-user - 960 days old
👉 2. terraform-user - 133 days old
   3. kartik-aws-user - 45 days old
```

---

## Available Users

The dropdown contains these predefined users:
- `aws-admin-user`
- `terraform-user`
- `kartik-aws-user`
- `test-user`
- `demo-user`

**Note**: These match the IAM usernames in your AWS account. Only users with access keys will show results.

---

## Technical Implementation

### Files Created

**Frontend:**
- `ui/src/contexts/AuthContext.tsx` - User state management
- `ui/src/components/UserSelector.tsx` - Dropdown component

**Backend:**
- Modified `src/api_server.py` - Added `current_user` parameter
- Modified `src/identity_analyzer.py` - Added `_check_my_keys_oldest()` method

### Data Flow

```
User selects "aws-admin-user" in dropdown
            ↓
Stored in localStorage + React state
            ↓
Passed to API with search query
            ↓
Backend receives current_user parameter
            ↓
Analyzer compares current_user's keys to all others
            ↓
Returns personalized result
```

---

## Customizing Available Users

To add/remove users, edit `ui/src/contexts/AuthContext.tsx`:

```typescript
const AVAILABLE_USERS = [
  'aws-admin-user',
  'terraform-user',
  'your-new-user',  // Add here
];
```

**Important**: Make sure the username exactly matches the IAM username in AWS!

---

## Future Enhancements

This is a simple version for demo purposes. For production, consider:

1. **Real Authentication** - JWT tokens, passwords
2. **Dynamic User List** - Fetch from AWS IAM instead of hardcoded
3. **Permissions** - Different users see different data
4. **Session Management** - Timeouts, logout
5. **Audit Logging** - Track who queries what

---

## Demo Script

### Show Simple Auth:

1. **Open app** - Dropdown shows in header
2. **Select user** - Choose "aws-admin-user"
3. **Run query** - Type: `are my access keys the oldest`
4. **See result** - Shows personalized ranking with 👉 pointer
5. **Switch user** - Select "terraform-user"
6. **Same query** - Now shows different result for different user
7. **Refresh page** - Selection persists!

### Key Points:

✅ No login page needed
✅ No passwords
✅ Simple dropdown
✅ Persists across refreshes
✅ Enables "my" queries

---

## Troubleshooting

### "User Identity Required" message

**Problem**: You typed a "my" query but no user is selected

**Solution**: Click the dropdown and select your AWS IAM username

### User not in dropdown

**Problem**: Your AWS IAM username isn't in the list

**Solution**: Edit `ui/src/contexts/AuthContext.tsx` and add your username to `AVAILABLE_USERS`

### "No Keys Found" result

**Problem**: The selected user doesn't have access keys

**Solution**: Select a different user, or create access keys for that IAM user in AWS

---

## Example Queries

Once you've selected a user, try these:

1. `are my access keys the oldest` - Age comparison
2. `list of users` - Still works (no user context needed)
3. `list of access keys` - Still works
4. `show me admin users` - Works with expanded permissions

**Note**: Only queries with "my" require user selection. All other queries work the same as before!
