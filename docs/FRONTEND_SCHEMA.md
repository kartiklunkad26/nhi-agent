# Frontend Data Schema (TypeScript)

The frontend uses **TypeScript interfaces** for type safety. Here's the complete data schema:

---

## 1. **API Communication Types** (`lib/api.ts`)

### **IdentityResult**
Represents a single identity search result.

```typescript
interface IdentityResult {
  title: string;                                    // Identity name/ID
  type: "vault" | "aws" | "api-key";               // Identity source type
  description: string;                              // Human-readable description
  status?: "active" | "expired" | "inactive";      // Current status (optional)
  lastAccessed?: string;                            // ISO timestamp (optional)
  metadata?: Record<string, any>;                   // Additional metadata (optional)
}
```

**Example:**
```json
{
  "title": "aws-admin-user",
  "type": "aws",
  "description": "IAM user with AdministratorAccess policy",
  "status": "active",
  "lastAccessed": "2025-01-15T10:30:00Z",
  "metadata": {
    "has_mfa": false,
    "access_keys_count": 2
  }
}
```

---

### **SearchResponse**
Response from identity search API.

```typescript
interface SearchResponse {
  results: IdentityResult[];                        // Array of search results
  query: string;                                    // Original search query
  total: number;                                    // Total result count
}
```

**Example:**
```json
{
  "results": [
    {
      "title": "user-without-mfa",
      "type": "aws",
      "description": "IAM user missing MFA",
      "status": "active"
    }
  ],
  "query": "Show users without MFA",
  "total": 1
}
```

---

### **QueryResponse**
Response from general question API.

```typescript
interface QueryResponse {
  query: string;                                    // Original question
  answer: string;                                   // AI-generated answer
  identities_summary: {
    total: number;                                  // Total identities found
    aws: {
      users: number;                                // AWS IAM user count
      roles: number;                                // AWS IAM role count
      groups: number;                               // AWS IAM group count
    };
    vault: number;                                  // Vault identity count
  };
}
```

**Example:**
```json
{
  "query": "How many admin users are there?",
  "answer": "There are 3 admin users in your AWS account.",
  "identities_summary": {
    "total": 15,
    "aws": {
      "users": 10,
      "roles": 3,
      "groups": 2
    },
    "vault": 0
  }
}
```

---

### **CollectIdentitiesResponse**
Response from identity collection API.

```typescript
interface CollectIdentitiesResponse {
  success: boolean;                                 // Collection success flag
  identities: any;                                  // Raw identity data
  summary: {
    total_count: number;                            // Total identities
    aws_users: number;                              // AWS user count
    aws_roles: number;                              // AWS role count
    aws_groups: number;                             // AWS group count
    vault_identities: number;                       // Vault identity count
  };
}
```

---

### **HealthResponse**
API health check response.

```typescript
interface HealthResponse {
  status: string;                                   // "healthy" or error
  supabase_configured: boolean;                     // Supabase connection status
  openai_configured: boolean;                       // OpenAI API key status
}
```

---

## 2. **Component Props Interfaces**

### **SearchBarProps**
Props for the SearchBar component.

```typescript
interface SearchBarProps {
  onSearch: (query: string) => void;               // Search callback function
  isLoading?: boolean;                             // Loading state (optional)
}
```

---

### **ResultsTableProps**
Props for the ResultsTable component.

```typescript
interface ResultsTableProps {
  results: ResultItem[];                           // Array of results to display
}
```

**ResultItem** (extended from IdentityResult):
```typescript
interface ResultItem {
  title: string;                                   // Identity name
  type: "vault" | "aws" | "api-key" | "error" | "info"; // Type (includes error/info)
  description: string;                             // Description
  status?: "active" | "expired" | "inactive" | "error" | "info"; // Status
  lastAccessed?: string;                           // Last access timestamp
}
```

---

## 3. **React Context Types**

### **AuthContextType**
User authentication and selection context.

```typescript
interface AuthContextType {
  currentUser: string | null;                      // Selected AWS IAM username
  setCurrentUser: (user: string | null) => void;  // Update current user
  availableUsers: string[];                        // List of available IAM users
}
```

**Available Users (Hardcoded):**
```typescript
const AVAILABLE_USERS = [
  'aws-admin-user',
  'terraform-user',
  'kartik-aws-user',
  'test-user',
  'demo-user'
];
```

**LocalStorage Key:** `nhi-agent-current-user`

---

### **SecurityContextType**
Security mode toggle context.

```typescript
interface SecurityContextType {
  secureMode: boolean;                             // Secure mode enabled?
  setSecureMode: (mode: boolean) => void;         // Toggle secure mode
}
```

**LocalStorage Key:** `nhi-agent-secure-mode`

**Values:**
- `false` = Admin Mode (uses shared admin credentials)
- `true` = Secure Mode (uses per-user credentials)

---

## 4. **Integration Types**

### **Integration**
Represents a cloud provider integration.

```typescript
interface Integration {
  id: string;                                      // Unique integration ID
  name: string;                                    // Display name (e.g., "AWS IAM")
  provider: string;                                // Provider name (e.g., "Amazon Web Services")
  status: "connected" | "disconnected";            // Connection status
  description: string;                             // Integration description
  icon: React.ReactNode;                           // Icon component
  lastSync?: Date;                                 // Last sync timestamp (optional)
}
```

**Example:**
```typescript
{
  id: "1",
  name: "AWS IAM",
  provider: "Amazon Web Services",
  status: "connected",
  description: "Collect and analyze IAM users, roles, groups, and access keys from your AWS account.",
  icon: <Cloud className="h-6 w-6" />,
  lastSync: new Date(Date.now() - 1000 * 60 * 15)  // 15 minutes ago
}
```

---

## 5. **Page Component State**

### **Dashboard Page State**

```typescript
// Dashboard.tsx internal state
{
  hasIntegration: boolean;                         // Show integration or main view
  isLoading: boolean;                              // Search in progress
  results: IdentityResult[];                       // Current search results
  lastQuery: string;                               // Last executed query
  currentUser: string | null;                      // From AuthContext
  secureMode: boolean;                             // From SecurityContext
}
```

---

## 6. **UI Display Constants**

### **Type Icons Mapping**
```typescript
const icons = {
  vault: Shield,
  aws: Cloud,
  "api-key": Key,
  error: AlertTriangle,
  info: Info,
};
```

### **Type Labels Mapping**
```typescript
const typeLabels = {
  vault: "Vault",
  aws: "AWS",
  "api-key": "API Key",
  error: "Error",
  info: "Info",
};
```

### **Status Colors Mapping**
```typescript
const statusColors = {
  active: "bg-green-500/10 text-green-600 border-green-500/20",
  expired: "bg-red-500/10 text-red-600 border-red-500/20",
  inactive: "bg-gray-500/10 text-gray-600 border-gray-500/20",
  error: "bg-red-500/10 text-red-600 border-red-500/20",
  info: "bg-blue-500/10 text-blue-600 border-blue-500/20",
};
```

---

## 7. **LocalStorage Schema**

The frontend persists data in browser localStorage:

```typescript
// Key: "nhi-agent-current-user"
// Value: string (username) or null
localStorage.getItem('nhi-agent-current-user'); // "aws-admin-user" | null

// Key: "nhi-agent-secure-mode"
// Value: "true" | "false"
localStorage.getItem('nhi-agent-secure-mode');  // "true" | "false"
```

---

## 8. **API Request Payloads**

### **Search Request**
```typescript
{
  query: string;                                   // Natural language query
  current_user?: string;                           // AWS IAM username (optional)
  secure_mode: boolean;                            // Use secure credentials
}
```

### **Query Request**
```typescript
{
  query: string;                                   // Question to ask
  model: string;                                   // OpenAI model (default: "gpt-4o-mini")
}
```

---

## Key Architecture Notes:

1. **No client-side database** - All data is fetched from the backend API in real-time
2. **Type-safe with TypeScript** - All interfaces enforce strict typing
3. **React Context for global state** - Auth and Security contexts provide app-wide state
4. **LocalStorage for persistence** - User preferences persist across sessions
5. **Stateless search** - No caching of search results; re-fetches on every query
6. **Component composition** - Reusable components with clearly defined prop interfaces

This schema ensures type safety throughout the frontend and provides a clear contract between the UI and the backend API.

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     User Interaction                         │
│                   (Dashboard Component)                      │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ User types query and clicks Search
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   SearchBar Component                        │
│  - Manages query state                                       │
│  - Calls onSearch(query) callback                            │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Triggers handleSearch()
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Dashboard handleSearch()                    │
│  - Reads currentUser from AuthContext                        │
│  - Reads secureMode from SecurityContext                     │
│  - Calls searchIdentities(query, currentUser, secureMode)    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ API Call
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                   lib/api.ts Module                          │
│  - Constructs POST request to /api/identities/search         │
│  - Sends { query, current_user, secure_mode }               │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ HTTP Request
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend API Server                          │
│  - Processes search request                                  │
│  - Returns SearchResponse                                    │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Response: SearchResponse
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                  Dashboard Component                         │
│  - Updates results state with IdentityResult[]               │
│  - Updates lastQuery state                                   │
│  - Shows toast notification                                  │
└────────────────────────┬─────────────────────────────────────┘
                         │
                         │ Pass results to child component
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                 ResultsTable Component                       │
│  - Renders table with IdentityResult[] data                  │
│  - Shows type icons, status badges, descriptions             │
└─────────────────────────────────────────────────────────────┘
```

---

**Last Updated:** 2025-11-25
**Version:** 0.1.0
**Related Files:**
- `ui/src/lib/api.ts` - API client and type definitions
- `ui/src/contexts/AuthContext.tsx` - User authentication context
- `ui/src/contexts/SecurityContext.tsx` - Security mode context
- `ui/src/components/SearchBar.tsx` - Search input component
- `ui/src/components/ResultsTable.tsx` - Results display component
- `ui/src/pages/Dashboard.tsx` - Main dashboard page
