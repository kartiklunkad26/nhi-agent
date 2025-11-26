/**
 * API client for NHI Agent backend
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export interface IdentityResult {
  title: string;
  type: "vault" | "aws" | "api-key";
  description: string;
  status?: "active" | "expired" | "inactive";
  lastAccessed?: string;
  metadata?: Record<string, any>;
}

export interface SearchResponse {
  results: IdentityResult[];
  query: string;
  total: number;
}

export interface QueryResponse {
  query: string;
  answer: string;
  identities_summary: {
    total: number;
    aws: {
      users: number;
      roles: number;
      groups: number;
    };
    vault: number;
  };
}

/**
 * Make an API request (no authentication required)
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: response.statusText }));
    throw new Error(error.detail || `API request failed: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Search identities using a natural language query
 */
export async function searchIdentities(
  query: string,
  currentUser?: string | null,
  secureMode: boolean = false
): Promise<SearchResponse> {
  return apiRequest<SearchResponse>("/api/identities/search", {
    method: "POST",
    body: JSON.stringify({
      query,
      current_user: currentUser || undefined,
      secure_mode: secureMode
    }),
  });
}

/**
 * Ask a question about identities
 */
export async function queryIdentities(
  query: string,
  model: string = "gpt-4o-mini"
): Promise<QueryResponse> {
  return apiRequest<QueryResponse>("/api/query", {
    method: "POST",
    body: JSON.stringify({ query, model }),
  });
}

/**
 * Collect identities from AWS and Vault
 */
export async function collectIdentities(): Promise<{
  success: boolean;
  identities: any;
  summary: {
    total_count: number;
    aws_users: number;
    aws_roles: number;
    aws_groups: number;
    vault_identities: number;
  };
}> {
  return apiRequest("/api/identities/collect", {
    method: "POST",
  });
}

/**
 * Check API health
 */
export async function checkHealth(): Promise<{
  status: string;
  supabase_configured: boolean;
  openai_configured: boolean;
}> {
  return apiRequest("/api/health", {
    method: "GET",
  });
}

