"""
Analyze identities and answer questions about them using LLM.
"""

from typing import Dict, List, Any, Optional
import json
from openai import OpenAI


class IdentityAnalyzer:
    """Analyzes identities and answers questions about them."""

    def __init__(self, openai_api_key: Optional[str] = None, identity_collector=None):
        """
        Initialize identity analyzer.

        Args:
            openai_api_key: OpenAI API key (or set OPENAI_API_KEY env var)
            identity_collector: IdentityCollector instance for enriched data queries
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.identities_data: Optional[Dict[str, Any]] = None
        self.identity_collector = identity_collector
    
    def load_identities(self, identities: Dict[str, Any]):
        """Load identities data for analysis."""
        self.identities_data = identities
    
    def _create_context(self) -> str:
        """Create context string from identities data."""
        if not self.identities_data:
            return "No identities loaded."
        
        context_parts = []
        
        # AWS identities
        aws = self.identities_data.get("aws", {})
        if aws:
            context_parts.append("## AWS Identities")
            if aws.get("users"):
                context_parts.append(f"Users ({len(aws['users'])}):")
                for user in aws["users"][:10]:  # Limit to first 10 for context
                    context_parts.append(f"  - {json.dumps(user, indent=2)}")
                if len(aws["users"]) > 10:
                    context_parts.append(f"  ... and {len(aws['users']) - 10} more users")

            if aws.get("roles"):
                context_parts.append(f"Roles ({len(aws['roles'])}):")
                for role in aws["roles"][:10]:
                    context_parts.append(f"  - {json.dumps(role, indent=2)}")
                if len(aws["roles"]) > 10:
                    context_parts.append(f"  ... and {len(aws['roles']) - 10} more roles")

            if aws.get("groups"):
                context_parts.append(f"Groups ({len(aws['groups'])}):")
                for group in aws["groups"][:10]:
                    context_parts.append(f"  - {json.dumps(group, indent=2)}")
                if len(aws["groups"]) > 10:
                    context_parts.append(f"  ... and {len(aws['groups']) - 10} more groups")

            if aws.get("access_keys"):
                context_parts.append(f"Access Keys ({len(aws['access_keys'])}):")
                for key in aws["access_keys"][:10]:
                    context_parts.append(f"  - {json.dumps(key, indent=2)}")
                if len(aws["access_keys"]) > 10:
                    context_parts.append(f"  ... and {len(aws['access_keys']) - 10} more access keys")

        return "\n".join(context_parts)
    
    def ask_question(self, question: str, model: str = "gpt-4o-mini") -> str:
        """
        Ask a question about the identities.
        
        Args:
            question: The question to ask
            model: OpenAI model to use
            
        Returns:
            Answer to the question
        """
        if not self.identities_data:
            return "No identities loaded. Please collect identities first."
        
        context = self._create_context()
        
        system_prompt = """You are an identity management expert analyzing identity data from AWS systems.
Your task is to answer questions about these identities, their metadata, relationships, and any security concerns.
Be thorough, accurate, and provide specific examples when relevant."""

        user_prompt = f"""Context about identities:
{context}

Question: {question}

Please analyze the identity data above and provide a comprehensive answer to the question."""

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"Error answering question: {e}"
    
    def analyze_security_concerns(self) -> str:
        """Analyze and report on security concerns in the identities."""
        return self.ask_question(
            "What security concerns or risks do you see in these identities? "
            "Consider issues like overly permissive policies, unused identities, or misconfigurations."
        )
    
    def summarize_identities(self) -> str:
        """Generate a summary of all identities."""
        return self.ask_question(
            "Provide a comprehensive summary of all identities, including counts by type, "
            "key metadata, and notable patterns or relationships."
        )
    
    def search_identities(self, query: str, max_results: int = 20, current_user: Optional[str] = None, secure_mode: bool = False) -> List[Dict[str, Any]]:
        """
        Search for identities matching a query using AI.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            current_user: Optional AWS IAM username of current user for "my" queries
            secure_mode: Whether using user-specific credentials (least privilege mode)

        Returns:
            List of identity results in IdentityResult format
        """
        if not self.identities_data:
            return []
        
        # Collect all identities
        all_identities = []

        # AWS users
        aws_users = self.identities_data.get("aws", {}).get("users", [])
        for user in aws_users:
            # Handle both PascalCase and snake_case field names
            user_name = (user.get("UserName") or user.get("user_name") or
                        user.get("name") or "Unknown")
            all_identities.append({
                "title": user_name,
                "type": "aws",
                "description": f"AWS IAM User: {user_name}",
                "status": "active",
                "metadata": user,
                "source": "aws",
                "category": "user",
                "owner": user_name  # Track which user this belongs to
            })

        # AWS roles
        aws_roles = self.identities_data.get("aws", {}).get("roles", [])
        for role in aws_roles:
            # Handle both PascalCase and snake_case field names
            role_name = (role.get("RoleName") or role.get("role_name") or
                        role.get("name") or "Unknown")
            all_identities.append({
                "title": role_name,
                "type": "aws",
                "description": f"AWS IAM Role: {role_name}",
                "status": "active",
                "metadata": role,
                "source": "aws",
                "category": "role",
                "owner": None  # Roles don't belong to specific users in AWS
            })

        # AWS groups
        aws_groups = self.identities_data.get("aws", {}).get("groups", [])
        for group in aws_groups:
            # Handle both PascalCase and snake_case field names
            group_name = (group.get("GroupName") or group.get("group_name") or
                         group.get("name") or "Unknown")
            all_identities.append({
                "title": group_name,
                "type": "aws",
                "description": f"AWS IAM Group: {group_name}",
                "status": "active",
                "metadata": group,
                "source": "aws",
                "category": "group",
                "owner": None  # Groups don't belong to specific users
            })

        # AWS access keys
        aws_keys = self.identities_data.get("aws", {}).get("access_keys", [])
        for key in aws_keys:
            key_id = key.get("access_key_id") or key.get("AccessKeyId") or "Unknown"
            user_name = key.get("UserName") or key.get("user_name") or "Unknown"
            create_date = key.get("create_date") or key.get("CreateDate") or ""
            status = key.get("status") or key.get("Status") or "Unknown"

            # Calculate age of key
            age_info = ""
            if create_date:
                from datetime import datetime, timezone
                try:
                    if isinstance(create_date, str):
                        # Try parsing ISO format
                        create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    else:
                        create_dt = create_date

                    # Make timezone-aware if it isn't already
                    if create_dt.tzinfo is None:
                        create_dt = create_dt.replace(tzinfo=timezone.utc)

                    now = datetime.now(timezone.utc)
                    age_days = (now - create_dt).days
                    age_info = f" (Age: {age_days} days)"

                    # Mark as old if not rotated in 90 days
                    if age_days > 90:
                        status = f"{status} - OLD"
                except Exception as e:
                    print(f"Error calculating age for key {key_id}: {e}")

            all_identities.append({
                "title": f"{key_id} ({user_name})",
                "type": "aws",
                "description": f"AWS Access Key: {key_id} for user {user_name}{age_info}",
                "status": status.lower(),
                "metadata": key,
                "source": "aws",
                "category": "access_key",
                "lastAccessed": str(create_date) if create_date else None,
                "owner": user_name  # Track which user owns this key
            })

        if not all_identities:
            return []
        
        # Use AI to find relevant identities
        # Create a summary of all identities for the LLM
        identity_summary = []
        for idx, identity in enumerate(all_identities):
            identity_summary.append({
                "index": idx,
                "title": identity["title"],
                "type": identity["type"],
                "category": identity["category"],
                "description": identity["description"],
                "metadata_summary": self._summarize_metadata(identity["metadata"])
            })
        
        # Simple keyword-based search as fallback
        query_lower = query.lower()
        query_words = query_lower.split()

        # ========== EXPANDED PERMISSION QUERIES ==========
        # These require additional IAM permissions
        # Note: Comparative queries need ALL user data, so they run BEFORE filtering

        # "My Access Keys" Queries (requires current_user)
        # This is a COMPARATIVE query - needs all users' data to compare
        if any(phrase in query_lower for phrase in ["my access key", "my keys"]):
            if current_user:
                if any(phrase in query_lower for phrase in ["oldest", "old"]):
                    # Check if in secure mode - comparative queries require seeing all users
                    if secure_mode:
                        return [{
                            "title": "Insufficient Permissions",
                            "type": "error",
                            "description": "Cannot perform this action as you don't have permissions for it. This query requires listing all users, which is not available with user-specific credentials.",
                            "status": "error",
                            "metadata": {},
                            "source": "system",
                            "category": "error"
                        }]
                    # Don't filter - need all users for comparison
                    return self._check_my_keys_oldest(current_user)
            else:
                # Return message asking user to select their identity
                return [{
                    "title": "User Identity Required",
                    "type": "info",
                    "description": "Please select your AWS IAM user from the dropdown to check your access keys.",
                    "status": "info",
                    "metadata": {},
                    "source": "system",
                    "category": "info"
                }]

        # Policy/Permission Analysis Queries
        if any(phrase in query_lower for phrase in ["admin access", "administrator", "overprivileged", "admin users"]):
            results = self._search_admin_users()
            # Filter by current_user if provided
            if current_user and results:
                results = [r for r in results if r.get("owner") == current_user or r.get("title") == current_user]
            return results

        # MFA Queries
        if any(phrase in query_lower for phrase in ["without mfa", "no mfa", "mfa status", "missing mfa"]):
            results = self._search_users_without_mfa()
            # Filter by current_user if provided
            if current_user and results:
                results = [r for r in results if r.get("owner") == current_user or r.get("title") == current_user]
            return results

        # Security Posture Queries
        if any(phrase in query_lower for phrase in ["security risk", "vulnerable", "at risk", "security posture"]):
            results = self._search_security_risks()
            # Filter by current_user if provided
            if current_user and results:
                results = [r for r in results if r.get("owner") == current_user or r.get("title") == current_user]
            return results

        # Usage/Activity Queries
        if any(phrase in query_lower for phrase in ["inactive user", "unused", "not used", "last used"]):
            results = self._search_inactive_identities()
            # Filter by current_user if provided
            if current_user and results:
                results = [r for r in results if r.get("owner") == current_user]
            return results

        # Check for specific category filters with better pattern matching
        # Determine if query is asking for a specific category
        requested_category = None

        # Check for users (but not "use" or other partial matches)
        if any(phrase in query_lower for phrase in [" user", "users", "^user"]) and "role" not in query_lower:
            requested_category = "user"
        # Check for roles
        elif any(phrase in query_lower for phrase in [" role", "roles"]) and "user" not in query_lower:
            requested_category = "role"
        # Check for groups
        elif any(phrase in query_lower for phrase in [" group", "groups"]):
            requested_category = "group"
        # Check for access keys
        elif any(phrase in query_lower for phrase in ["access key", "access_key", "accesskey"]):
            requested_category = "access_key"

        # If a specific category is requested, filter by that category
        if requested_category:
            filtered = [id for id in all_identities if id["category"] == requested_category]

            # Apply user filtering if current_user is provided
            if current_user:
                # For users category, only show the current user
                if requested_category == "user":
                    filtered = [id for id in filtered if id.get("owner") == current_user or id.get("title") == current_user]
                # For access_keys, only show keys owned by current user
                elif requested_category == "access_key":
                    filtered = [id for id in filtered if id.get("owner") == current_user]
                # For roles, don't filter (roles aren't owned by users in AWS)
                # But we could filter to only show roles the user can assume if we had that data

            # Special handling for "not rotated" queries
            if "not rotated" in query_lower or "old" in query_lower or "expired" in query_lower:
                if requested_category == "access_key":
                    # Extract days threshold if mentioned
                    import re
                    days_match = re.search(r'(\d+)\s*days?', query_lower)
                    days_threshold = int(days_match.group(1)) if days_match else 30

                    # Filter for old keys
                    from datetime import datetime, timezone
                    old_filtered = []
                    for key_item in filtered:
                        create_date = key_item.get("metadata", {}).get("create_date") or key_item.get("metadata", {}).get("CreateDate")
                        if create_date:
                            try:
                                if isinstance(create_date, str):
                                    create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                                else:
                                    create_dt = create_date
                                now = datetime.now(timezone.utc)
                                age_days = (now - create_dt).days
                                if age_days >= days_threshold:
                                    old_filtered.append(key_item)
                            except:
                                pass
                    return old_filtered[:max_results]
            return filtered[:max_results]

        # If no category matched, return empty results
        # Only the specific supported queries will work
        return []
    
    # ========== EXPANDED PERMISSION QUERY HANDLERS ==========

    def _check_my_keys_oldest(self, current_user: str) -> List[Dict[str, Any]]:
        """
        Check if the current user's access keys are the oldest among all users.

        Args:
            current_user: AWS IAM username of the current user

        Returns:
            List with single result indicating if user has oldest keys
        """
        if not self.identities_data:
            return []

        from datetime import datetime, timezone

        # Collect all users with their oldest access key age
        user_key_ages = {}  # {username: oldest_key_age_days}

        aws_keys = self.identities_data.get("aws", {}).get("access_keys", [])

        for key in aws_keys:
            user_name = key.get("UserName") or key.get("user_name")
            create_date = key.get("create_date") or key.get("CreateDate")
            key_id = key.get("access_key_id") or key.get("AccessKeyId") or key.get("key_id")

            if user_name and create_date:
                try:
                    if isinstance(create_date, str):
                        create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    else:
                        create_dt = create_date

                    # Make timezone-aware if it isn't already
                    if create_dt.tzinfo is None:
                        create_dt = create_dt.replace(tzinfo=timezone.utc)

                    age_days = (datetime.now(timezone.utc) - create_dt).days

                    # Track the oldest key for each user
                    if user_name not in user_key_ages or age_days > user_key_ages[user_name]["age_days"]:
                        user_key_ages[user_name] = {
                            "age_days": age_days,
                            "key_id": key_id,
                            "create_date": create_date
                        }
                except Exception as e:
                    print(f"Error processing key for {user_name}: {e}")
                    import traceback
                    traceback.print_exc()

        if not user_key_ages:
            return [{
                "title": "No Access Keys Found",
                "type": "info",
                "description": "No access keys found in the system to compare.",
                "status": "info",
                "metadata": {},
                "source": "system",
                "category": "info"
            }]

        # Check if current user has any keys
        if current_user not in user_key_ages:
            return [{
                "title": f"No Keys Found - {current_user}",
                "type": "info",
                "description": f"User '{current_user}' does not have any access keys.",
                "status": "warning",
                "metadata": {},
                "source": "system",
                "category": "info"
            }]

        # Sort users by key age (descending)
        sorted_users = sorted(user_key_ages.items(), key=lambda x: x[1]["age_days"], reverse=True)

        # Get current user's info
        current_user_info = user_key_ages[current_user]
        current_user_age = current_user_info["age_days"]

        # Check if current user has the oldest
        oldest_user = sorted_users[0][0]
        oldest_age = sorted_users[0][1]["age_days"]

        is_oldest = (current_user == oldest_user)

        # Build description
        if is_oldest:
            if len(sorted_users) > 1:
                second_oldest = sorted_users[1]
                description = (
                    f"Your access keys are {current_user_age} days old. "
                    f"✅ YES - You have the OLDEST access keys among all users. "
                    f"Next oldest: {second_oldest[0]} ({second_oldest[1]['age_days']} days old)"
                )
            else:
                description = (
                    f"Your access keys are {current_user_age} days old. "
                    f"✅ YES - You have the OLDEST access keys (you are the only user with keys)."
                )
            status = "oldest"
        else:
            description = (
                f"Your access keys are {current_user_age} days old. "
                f"❌ NO - {oldest_user} has the oldest keys ({oldest_age} days old). "
                f"Your keys are {oldest_age - current_user_age} days newer."
            )
            status = "not-oldest"

        # Add ranking info
        ranking_lines = ["\n\nKey Age Ranking:"]
        for idx, (username, info) in enumerate(sorted_users[:5], 1):
            marker = "👉 " if username == current_user else "   "
            ranking_lines.append(f"{marker}{idx}. {username} - {info['age_days']} days old")

        if len(sorted_users) > 5:
            ranking_lines.append(f"   ... and {len(sorted_users) - 5} more users")

        description += "".join(ranking_lines)

        return [{
            "title": f"Access Key Age Check - {current_user}",
            "type": "aws",
            "description": description,
            "status": status,
            "metadata": {
                "current_user": current_user,
                "current_user_age_days": current_user_age,
                "is_oldest": is_oldest,
                "oldest_user": oldest_user,
                "oldest_age_days": oldest_age,
                "ranking": sorted_users[:10]  # Top 10
            },
            "source": "aws",
            "category": "access_key"
        }]

    def _search_admin_users(self) -> List[Dict[str, Any]]:
        """
        Search for users with admin access.
        Requires: iam:ListAttachedUserPolicies, iam:GetPolicy, iam:GetPolicyVersion
        """
        if not self.identity_collector:
            return []

        try:
            enriched_users = self.identity_collector.collect_enriched_user_data()
            admin_users = []

            for user in enriched_users:
                user_name = user.get("UserName") or user.get("user_name")
                is_admin = False

                # Check attached policies for AdministratorAccess
                for policy in user.get("attached_policies", []):
                    policy_name = policy.get("PolicyName", "")
                    if "Administrator" in policy_name or "admin" in policy_name.lower():
                        is_admin = True
                        break

                # Check inline policies (would need to parse JSON to detect admin)
                if user.get("inline_policies", []):
                    # If user has inline policies, they might be overprivileged
                    # For now, mark as potential admin if they have inline policies with "admin" in name
                    for policy_name in user.get("inline_policies", []):
                        if "admin" in policy_name.lower():
                            is_admin = True
                            break

                if is_admin:
                    admin_users.append({
                        "title": user_name,
                        "type": "aws",
                        "description": f"AWS IAM User with Admin Access: {user_name}",
                        "status": "admin",
                        "metadata": user,
                        "source": "aws",
                        "category": "user",
                        "owner": user_name  # Add owner for filtering
                    })

            return admin_users

        except Exception as e:
            print(f"Error searching admin users: {e}")
            return []

    def _search_users_without_mfa(self) -> List[Dict[str, Any]]:
        """
        Search for users without MFA enabled.
        Requires: iam:ListMFADevices, iam:GetLoginProfile
        """
        if not self.identity_collector:
            return []

        try:
            enriched_users = self.identity_collector.collect_enriched_user_data()
            no_mfa_users = []

            for user in enriched_users:
                user_name = user.get("UserName") or user.get("user_name")
                has_console = user.get("has_console_access", False)
                has_mfa = user.get("has_mfa", False)

                # Only flag users who have console access but no MFA
                if has_console and not has_mfa:
                    no_mfa_users.append({
                        "title": user_name,
                        "type": "aws",
                        "description": f"AWS IAM User without MFA (Console Access Enabled): {user_name}",
                        "status": "warning",
                        "metadata": user,
                        "source": "aws",
                        "category": "user",
                        "owner": user_name  # Add owner for filtering
                    })

            return no_mfa_users

        except Exception as e:
            print(f"Error searching users without MFA: {e}")
            return []

    def _search_security_risks(self) -> List[Dict[str, Any]]:
        """
        Search for security risks (combines multiple checks).
        Requires: Multiple expanded permissions
        """
        risks = []

        # Get users without MFA
        no_mfa = self._search_users_without_mfa()
        risks.extend(no_mfa)

        # Get admin users (potential risk if misconfigured)
        admin_users = self._search_admin_users()
        for admin in admin_users:
            admin["description"] = f"High-privilege account: {admin['title']}"
            admin["status"] = "high-privilege"
        risks.extend(admin_users)

        # Get old access keys
        old_keys_results = self.search_identities("access keys not rotated within 90 days")
        for key in old_keys_results:
            key["description"] = f"Old access key: {key['title']}"
            key["status"] = "old-credential"
        risks.extend(old_keys_results)

        return risks

    def _search_inactive_identities(self) -> List[Dict[str, Any]]:
        """
        Search for inactive identities (unused access keys, inactive users).
        Requires: iam:GetAccessKeyLastUsed
        """
        if not self.identity_collector:
            return []

        try:
            enriched_users = self.identity_collector.collect_enriched_user_data()
            inactive_items = []

            from datetime import datetime, timezone, timedelta

            for user in enriched_users:
                user_name = user.get("UserName") or user.get("user_name")

                # Check for unused access keys (never used or not used in 90 days)
                for key in user.get("access_keys_enriched", []):
                    key_id = key.get("access_key_id") or key.get("AccessKeyId")
                    last_used_info = key.get("last_used", {})
                    last_used_date = last_used_info.get("LastUsedDate") or last_used_info.get("last_used_date")

                    is_inactive = False
                    reason = ""

                    if not last_used_date:
                        is_inactive = True
                        reason = "Never used"
                    else:
                        try:
                            if isinstance(last_used_date, str):
                                last_used_dt = datetime.fromisoformat(last_used_date.replace('Z', '+00:00'))
                            else:
                                last_used_dt = last_used_date

                            days_since_use = (datetime.now(timezone.utc) - last_used_dt).days
                            if days_since_use > 90:
                                is_inactive = True
                                reason = f"Not used in {days_since_use} days"
                        except:
                            pass

                    if is_inactive:
                        inactive_items.append({
                            "title": f"{key_id} ({user_name})",
                            "type": "aws",
                            "description": f"Inactive Access Key: {key_id} for {user_name} - {reason}",
                            "status": "inactive",
                            "metadata": key,
                            "source": "aws",
                            "category": "access_key",
                            "owner": user_name  # Add owner for filtering
                        })

            return inactive_items

        except Exception as e:
            print(f"Error searching inactive identities: {e}")
            return []

    def _summarize_metadata(self, metadata: Dict[str, Any]) -> str:
        """Create a summary string from metadata for search."""
        summary_parts = []

        # Extract key fields (handle both PascalCase and snake_case)
        if isinstance(metadata, dict):
            for key in ["UserName", "user_name", "RoleName", "role_name", "GroupName", "group_name",
                       "name", "Arn", "arn", "Path", "path", "Description", "description"]:
                if key in metadata and metadata[key]:
                    summary_parts.append(f"{key}: {metadata[key]}")

        return " | ".join(summary_parts[:5])  # Limit to first 5 fields

    def get_old_access_keys(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get access keys that haven't been rotated within the specified number of days.

        Args:
            days: Number of days threshold (default: 90)

        Returns:
            List of access keys older than the specified threshold
        """
        if not self.identities_data:
            return []

        from datetime import datetime, timezone

        old_keys = []
        aws_keys = self.identities_data.get("aws", {}).get("access_keys", [])

        for key in aws_keys:
            create_date = key.get("create_date") or key.get("CreateDate")
            if create_date:
                try:
                    if isinstance(create_date, str):
                        create_dt = datetime.fromisoformat(create_date.replace('Z', '+00:00'))
                    else:
                        create_dt = create_date

                    now = datetime.now(timezone.utc)
                    age_days = (now - create_dt).days

                    if age_days >= days:
                        key_copy = key.copy()
                        key_copy["age_days"] = age_days
                        old_keys.append(key_copy)
                except Exception as e:
                    print(f"Error parsing date for key {key.get('AccessKeyId')}: {e}")

        return old_keys




