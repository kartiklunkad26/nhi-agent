"""
Collect identities from AWS MCP servers.
"""

from typing import Dict, List, Any, Optional
from .mcp_client import AWSMCPClient


class IdentityCollector:
    """Collects identities from multiple sources."""

    def __init__(
        self,
        aws_profile: Optional[str] = None,
        aws_region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None,
        vault_address: Optional[str] = None,
        vault_token: Optional[str] = None
    ):
        """
        Initialize identity collector.

        Args:
            aws_profile: AWS profile name
            aws_region: AWS region
            aws_access_key_id: AWS access key ID (for user-specific credentials)
            aws_secret_access_key: AWS secret access key (for user-specific credentials)
            vault_address: Vault server address (deprecated - not used)
            vault_token: Vault authentication token (deprecated - not used)
        """
        self.aws_client: Optional[AWSMCPClient] = None

        if aws_access_key_id and aws_secret_access_key:
            # Use explicit credentials (secure mode)
            try:
                self.aws_client = AWSMCPClient(
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_region=aws_region or "us-east-1"
                )
            except Exception as e:
                print(f"Warning: Could not initialize AWS MCP client with access keys: {e}")
        elif aws_profile or aws_region:
            # Use profile (insecure mode)
            try:
                self.aws_client = AWSMCPClient(aws_profile=aws_profile, aws_region=aws_region)
            except Exception as e:
                print(f"Warning: Could not initialize AWS MCP client: {e}")

    def collect_aws_identities(self) -> Dict[str, Any]:
        """Collect identities from AWS."""
        if not self.aws_client:
            return {"users": [], "roles": [], "groups": []}

        try:
            return self.aws_client.get_identity_details()
        except Exception as e:
            print(f"Error collecting AWS identities: {e}")
            return {"users": [], "roles": [], "groups": []}

    def collect_single_user_aws_identities(self, username: str) -> Dict[str, Any]:
        """
        Collect identities for a single specific AWS user.
        Use this when credentials only allow access to a specific user (least privilege).

        Args:
            username: The IAM username to collect data for

        Returns:
            Dict with users, roles, groups, and access_keys for this specific user
        """
        if not self.aws_client:
            return {"users": [], "roles": [], "groups": [], "access_keys": []}

        try:
            return self.aws_client.get_single_user_identity_details(username)
        except Exception as e:
            print(f"Error collecting AWS identities for user {username}: {e}")
            return {"users": [], "roles": [], "groups": [], "access_keys": []}

    def collect_enriched_user_data(self) -> List[Dict[str, Any]]:
        """
        Collect enriched user data including policies, MFA status, and access key usage.
        This requires expanded IAM permissions.
        """
        if not self.aws_client:
            return []

        enriched_users = []

        try:
            users = self.aws_client.list_iam_users()

            for user in users:
                user_name = user.get("UserName") or user.get("user_name")
                if not user_name:
                    continue

                enriched_user = user.copy()

                # Get attached managed policies
                try:
                    attached_policies = self.aws_client.list_attached_user_policies(user_name)
                    enriched_user["attached_policies"] = attached_policies
                except:
                    enriched_user["attached_policies"] = []

                # Get inline policies
                try:
                    inline_policies = self.aws_client.list_user_policies(user_name)
                    enriched_user["inline_policies"] = inline_policies
                except:
                    enriched_user["inline_policies"] = []

                # Get MFA devices
                try:
                    mfa_devices = self.aws_client.list_mfa_devices(user_name)
                    enriched_user["mfa_devices"] = mfa_devices
                    enriched_user["has_mfa"] = len(mfa_devices) > 0
                except:
                    enriched_user["mfa_devices"] = []
                    enriched_user["has_mfa"] = False

                # Get console login profile
                try:
                    login_profile = self.aws_client.get_login_profile(user_name)
                    enriched_user["has_console_access"] = bool(login_profile)
                    enriched_user["login_profile"] = login_profile
                except:
                    enriched_user["has_console_access"] = False
                    enriched_user["login_profile"] = {}

                # Get access keys with last used info
                try:
                    user_details = self.aws_client.get_user_details(user_name)
                    access_keys = user_details.get("access_keys", [])

                    for key in access_keys:
                        key_id = key.get("access_key_id") or key.get("AccessKeyId")
                        if key_id:
                            try:
                                last_used = self.aws_client.get_access_key_last_used(key_id)
                                key["last_used"] = last_used
                            except:
                                key["last_used"] = {}

                    enriched_user["access_keys_enriched"] = access_keys
                except:
                    enriched_user["access_keys_enriched"] = []

                enriched_users.append(enriched_user)

        except Exception as e:
            print(f"Error collecting enriched user data: {e}")

        return enriched_users

    def collect_all_identities(self, single_user: str = None) -> Dict[str, Any]:
        """
        Collect all identities from all sources.

        Args:
            single_user: If provided, only collect data for this specific user (for least privilege mode)

        Returns:
            Dict with aws identities and total count
        """
        if single_user:
            # Single user mode - use least privilege collection
            result = {
                "aws": self.collect_single_user_aws_identities(single_user),
                "total_count": 0
            }
        else:
            # Full mode - collect all identities
            result = {
                "aws": self.collect_aws_identities(),
                "total_count": 0
            }

        # Calculate total count
        aws_count = (
            len(result["aws"].get("users", [])) +
            len(result["aws"].get("roles", [])) +
            len(result["aws"].get("groups", [])) +
            len(result["aws"].get("access_keys", []))
        )
        result["total_count"] = aws_count

        return result

    def close(self):
        """Close all client connections."""
        if self.aws_client:
            self.aws_client.close()





