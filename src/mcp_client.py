"""
MCP Client for interacting with AWS and Vault MCP servers.
"""

import json
import subprocess
import os
from typing import Dict, List, Any, Optional
from pathlib import Path


class MCPClient:
    """Client for communicating with MCP servers via stdio."""
    
    def __init__(self, server_command: List[str], env: Optional[Dict[str, str]] = None):
        """
        Initialize MCP client.
        
        Args:
            server_command: Command to run the MCP server (e.g., ["uvx", "awslabs.iam-mcp-server@latest"])
            env: Environment variables for the server process
        """
        self.server_command = server_command
        self.env = env or {}
        self.process = None
        self.request_id = 0
        
    def _next_request_id(self) -> int:
        """Get the next request ID."""
        self.request_id += 1
        return self.request_id
    
    def _initialize(self):
        """Initialize the MCP server connection."""
        if self.process is not None:
            return
        
        # Start the server process
        full_env = {**os.environ, **self.env}
        self.process = subprocess.Popen(
            self.server_command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=full_env,
            text=True,
            bufsize=0  # Unbuffered
        )
        
        # Initialize the MCP protocol
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "nhi-agent",
                    "version": "0.1.0"
                }
            }
        }
        
        init_json = json.dumps(init_request) + "\n"
        self.process.stdin.write(init_json)
        self.process.stdin.flush()
        
        # Read initialization response
        response_line = self.process.stdout.readline()
        if not response_line:
            raise ConnectionError("No response from MCP server during initialization")
        
        response = json.loads(response_line)
        if "error" in response:
            raise RuntimeError(f"MCP server initialization error: {response['error']}")
        
        # Send initialized notification
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        notif_json = json.dumps(initialized_notification) + "\n"
        self.process.stdin.write(notif_json)
        self.process.stdin.flush()
    
    def _send_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Send a JSON-RPC request to the MCP server."""
        self._initialize()
        
        request = {
            "jsonrpc": "2.0",
            "id": self._next_request_id(),
            "method": method,
            "params": params
        }
        
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json)
        self.process.stdin.flush()
        
        # Read response (may need to skip notification messages)
        while True:
            response_line = self.process.stdout.readline()
            if not response_line:
                raise ConnectionError("No response from MCP server")
            
            response = json.loads(response_line)
            
            # Skip notifications (they don't have an id)
            if "id" not in response:
                continue
            
            # Check if this is the response to our request
            if "error" in response:
                raise RuntimeError(f"MCP server error: {response['error']}")
            
            return response.get("result", {})
    
    def list_tools(self) -> List[Dict[str, Any]]:
        """List available tools from the MCP server."""
        response = self._send_request("tools/list", {})
        tools = response.get("tools", [])
        # Handle different response formats
        if isinstance(tools, list):
            return tools
        return []
    
    def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool on the MCP server."""
        response = self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments if arguments else {}
        })
        # Handle different response formats
        content = response.get("content", [])
        if isinstance(content, list) and len(content) > 0:
            # Extract text from content items
            if isinstance(content[0], dict) and "text" in content[0]:
                # Try to parse JSON text content
                text_content = content[0]["text"]
                try:
                    return json.loads(text_content)
                except json.JSONDecodeError:
                    return text_content
            return content
        return content if content else []
    
    def list_resources(self) -> List[Dict[str, Any]]:
        """List available resources from the MCP server."""
        response = self._send_request("resources/list", {})
        return response.get("resources", [])
    
    def read_resource(self, uri: str) -> Any:
        """Read a resource from the MCP server."""
        response = self._send_request("resources/read", {"uri": uri})
        return response.get("contents", [])
    
    def close(self):
        """Close the connection to the MCP server."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None


class AWSMCPClient(MCPClient):
    """Client for AWS IAM MCP Server."""

    def __init__(
        self,
        aws_profile: Optional[str] = None,
        aws_region: Optional[str] = None,
        aws_access_key_id: Optional[str] = None,
        aws_secret_access_key: Optional[str] = None
    ):
        """
        Initialize AWS MCP client.

        Args:
            aws_profile: AWS profile name
            aws_region: AWS region (default: us-east-1)
            aws_access_key_id: AWS access key ID (alternative to profile)
            aws_secret_access_key: AWS secret access key (alternative to profile)
        """
        command = ["uvx", "awslabs.iam-mcp-server@latest"]
        env = {
            "FASTMCP_LOG_LEVEL": "ERROR"
        }

        # Store credentials for direct boto3 usage
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_profile = aws_profile
        self.aws_region = aws_region or "us-east-1"

        # Prioritize explicit credentials over profile
        if aws_access_key_id and aws_secret_access_key:
            env["AWS_ACCESS_KEY_ID"] = aws_access_key_id
            env["AWS_SECRET_ACCESS_KEY"] = aws_secret_access_key
        elif aws_profile:
            env["AWS_PROFILE"] = aws_profile

        if aws_region:
            env["AWS_REGION"] = aws_region
        else:
            env["AWS_REGION"] = "us-east-1"

        super().__init__(command, env)

    def _parse_aws_list_response(self, result: Any, key: str) -> List[Dict[str, Any]]:
        """
        Parse AWS IAM list response that might be wrapped in various formats.

        AWS IAM responses often come as:
        - [{"Users": [...]}] or [{"Roles": [...]}]
        - {"Users": [...]} or {"Roles": [...]}
        - [...] (direct list)

        Args:
            result: Raw result from MCP call_tool
            key: The key to look for (e.g., "Users", "Roles", "Groups")

        Returns:
            List of identity objects
        """
        if not result:
            return []

        # If result is a list, check first element
        if isinstance(result, list):
            if len(result) == 0:
                return []

            first_elem = result[0]

            # Check if first element is a dict containing our key
            if isinstance(first_elem, dict) and key in first_elem:
                return first_elem[key]

            # Check for lowercase version of key
            key_lower = key.lower()
            if isinstance(first_elem, dict) and key_lower in first_elem:
                return first_elem[key_lower]

            # If first element looks like an identity object (has expected fields)
            identity_fields = ["UserName", "RoleName", "GroupName", "Arn", "UserId", "RoleId"]
            if isinstance(first_elem, dict) and any(field in first_elem for field in identity_fields):
                return result

            # Otherwise return the list as-is
            return result

        # If result is a dict
        elif isinstance(result, dict):
            # Check for the key (case-sensitive)
            if key in result:
                return result[key]

            # Check for lowercase key
            key_lower = key.lower()
            if key_lower in result:
                return result[key_lower]

            # If dict looks like a single identity object, wrap in list
            identity_fields = ["UserName", "RoleName", "GroupName", "Arn", "UserId", "RoleId"]
            if any(field in result for field in identity_fields):
                return [result]

        return []
    
    def list_iam_users(self) -> List[Dict[str, Any]]:
        """List all IAM users."""
        try:
            tools = self.list_tools()
            # Look for user-related tools
            user_tools = [
                t for t in tools
                if "user" in t.get("name", "").lower()
                and ("list" in t.get("name", "").lower() or "get" in t.get("name", "").lower())
            ]

            if user_tools:
                # Try the first matching tool
                tool_name = user_tools[0]["name"]

                # Create minimal MCP context for tools that require it
                ctx = {
                    "content": [],
                    "isError": False
                }

                # Try with ctx parameter first (some MCP servers require it)
                try:
                    result = self.call_tool(tool_name, {"ctx": ctx})
                    return self._parse_aws_list_response(result, "Users")
                except:
                    # Fallback: try without ctx
                    result = self.call_tool(tool_name, {})
                    return self._parse_aws_list_response(result, "Users")

            # Fallback: try common tool names
            for tool_name in ["list_users", "iam_list_users", "aws_list_users"]:
                try:
                    # Try with ctx
                    ctx = {"content": [], "isError": False}
                    result = self.call_tool(tool_name, {"ctx": ctx})
                    if result:
                        return self._parse_aws_list_response(result, "Users")
                except:
                    # Try without ctx
                    try:
                        result = self.call_tool(tool_name, {})
                        if result:
                            return self._parse_aws_list_response(result, "Users")
                    except:
                        continue
        except Exception as e:
            print(f"Error in list_iam_users: {e}")
        return []
    
    def list_iam_roles(self) -> List[Dict[str, Any]]:
        """List all IAM roles."""
        try:
            tools = self.list_tools()
            # Look for role-related tools
            role_tools = [
                t for t in tools
                if "role" in t.get("name", "").lower()
                and ("list" in t.get("name", "").lower() or "get" in t.get("name", "").lower())
            ]

            if role_tools:
                result = self.call_tool(role_tools[0]["name"], {})
                # Parse AWS IAM response format
                return self._parse_aws_list_response(result, "Roles")

            # Fallback: try common tool names
            for tool_name in ["list_roles", "iam_list_roles", "aws_list_roles"]:
                try:
                    result = self.call_tool(tool_name, {})
                    if result:
                        return self._parse_aws_list_response(result, "Roles")
                except:
                    continue
        except Exception as e:
            print(f"Error in list_iam_roles: {e}")
        return []

    def get_user_details(self, user_name: str) -> Dict[str, Any]:
        """Get detailed information about a specific IAM user including access keys."""
        try:
            # Use get_user tool which returns comprehensive user info including access keys
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_user", {"ctx": ctx, "user_name": user_name})
            return result if result else {}
        except Exception as e:
            print(f"Error getting user details for {user_name}: {e}")
            return {}

    def list_all_access_keys(self) -> List[Dict[str, Any]]:
        """List all access keys for all IAM users."""
        all_keys = []
        try:
            users = self.list_iam_users()

            for user in users:
                user_name = user.get("UserName") or user.get("user_name") or user.get("name")
                if user_name:
                    # Get detailed user info which includes access keys
                    user_details = self.get_user_details(user_name)

                    # Extract access keys from user details
                    # The response format may vary, so check multiple possible locations
                    access_keys = []

                    # Check if access_keys is directly in the response
                    if isinstance(user_details, dict):
                        access_keys = user_details.get("access_keys", [])
                        if not access_keys:
                            access_keys = user_details.get("AccessKeys", [])
                        if not access_keys:
                            # Check if it's wrapped in a User object
                            user_obj = user_details.get("User", {})
                            if isinstance(user_obj, dict):
                                access_keys = user_obj.get("access_keys", [])
                                if not access_keys:
                                    access_keys = user_obj.get("AccessKeys", [])

                    # Process each access key
                    for key in access_keys:
                        if isinstance(key, dict):
                            # Add user information to the key
                            key["UserName"] = user_name
                            key["_user_info"] = user
                            all_keys.append(key)

        except Exception as e:
            print(f"Error listing all access keys: {e}")

        return all_keys

    def get_identity_details(self) -> Dict[str, Any]:
        """Get all identity information from AWS."""
        identities = {
            "users": [],
            "roles": [],
            "groups": [],
            "access_keys": []
        }

        try:
            identities["users"] = self.list_iam_users()
        except Exception as e:
            print(f"Error fetching AWS users: {e}")

        try:
            identities["roles"] = self.list_iam_roles()
        except Exception as e:
            print(f"Error fetching AWS roles: {e}")

        try:
            identities["access_keys"] = self.list_all_access_keys()
        except Exception as e:
            print(f"Error fetching AWS access keys: {e}")

        return identities

    def get_single_user_identity_details(self, username: str) -> Dict[str, Any]:
        """
        Get identity information for a single specific user.
        Use this when credentials only allow access to a specific user (least privilege).

        This method ONLY uses iam:GetUser and iam:ListAccessKeys directly via boto3,
        bypassing MCP tools which try to fetch additional data requiring more permissions.

        Args:
            username: The IAM username to get details for

        Returns:
            Dict with users, roles, groups, and access_keys for this specific user
        """
        identities = {
            "users": [],
            "roles": [],
            "groups": [],
            "access_keys": []
        }

        try:
            # Use boto3 IAM client directly for minimal permissions
            import boto3

            # Create IAM client with the same credentials as MCP client
            if self.aws_access_key_id and self.aws_secret_access_key:
                iam = boto3.client(
                    'iam',
                    aws_access_key_id=self.aws_access_key_id,
                    aws_secret_access_key=self.aws_secret_access_key,
                    region_name=self.aws_region
                )
            else:
                # Fall back to profile or default credentials
                iam = boto3.client('iam', region_name=self.aws_region)

            # Call iam:GetUser directly
            user_response = iam.get_user(UserName=username)
            user_obj = user_response.get("User", {})
            if user_obj:
                identities["users"].append(user_obj)

            # Call iam:ListAccessKeys directly
            keys_response = iam.list_access_keys(UserName=username)
            access_keys = keys_response.get("AccessKeyMetadata", [])

            # Add user information to each key
            for key in access_keys:
                if isinstance(key, dict):
                    key["UserName"] = username
                    key["user_name"] = username
                    key["_user_info"] = user_obj
                    # Normalize create_date field
                    if "CreateDate" in key:
                        key["create_date"] = key["CreateDate"]
                    identities["access_keys"].append(key)

        except Exception as e:
            print(f"Error fetching identity details for user {username}: {e}")
            import traceback
            traceback.print_exc()

        # Note: In least privilege mode, users typically can't list roles/groups
        # So we leave those empty

        return identities

    # ========== Expanded Permission Methods ==========
    # These methods require additional IAM permissions beyond the minimal set

    def list_user_policies(self, user_name: str) -> List[str]:
        """
        List inline policies for a user.
        Requires: iam:ListUserPolicies
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("list_user_policies", {"ctx": ctx, "user_name": user_name})

            # Parse response - could be {"PolicyNames": [...]} or direct list
            if isinstance(result, dict):
                return result.get("PolicyNames", result.get("policy_names", []))
            elif isinstance(result, list):
                return result
            return []
        except Exception as e:
            print(f"Error listing user policies for {user_name}: {e}")
            return []

    def get_user_policy(self, user_name: str, policy_name: str) -> Dict[str, Any]:
        """
        Get inline policy document for a user.
        Requires: iam:GetUserPolicy
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_user_policy", {
                "ctx": ctx,
                "user_name": user_name,
                "policy_name": policy_name
            })
            return result if isinstance(result, dict) else {}
        except Exception as e:
            print(f"Error getting user policy {policy_name} for {user_name}: {e}")
            return {}

    def list_attached_user_policies(self, user_name: str) -> List[Dict[str, Any]]:
        """
        List managed policies attached to a user.
        Requires: iam:ListAttachedUserPolicies
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("list_attached_user_policies", {
                "ctx": ctx,
                "user_name": user_name
            })

            # Parse response
            if isinstance(result, dict):
                return result.get("AttachedPolicies", result.get("attached_policies", []))
            elif isinstance(result, list):
                return result
            return []
        except Exception as e:
            print(f"Error listing attached policies for {user_name}: {e}")
            return []

    def get_policy(self, policy_arn: str) -> Dict[str, Any]:
        """
        Get policy metadata.
        Requires: iam:GetPolicy
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_policy", {
                "ctx": ctx,
                "policy_arn": policy_arn
            })

            if isinstance(result, dict):
                return result.get("Policy", result)
            return {}
        except Exception as e:
            print(f"Error getting policy {policy_arn}: {e}")
            return {}

    def get_policy_version(self, policy_arn: str, version_id: str = "v1") -> Dict[str, Any]:
        """
        Get policy document version.
        Requires: iam:GetPolicyVersion
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_policy_version", {
                "ctx": ctx,
                "policy_arn": policy_arn,
                "version_id": version_id
            })

            if isinstance(result, dict):
                return result.get("PolicyVersion", result)
            return {}
        except Exception as e:
            print(f"Error getting policy version {version_id} for {policy_arn}: {e}")
            return {}

    def list_mfa_devices(self, user_name: str) -> List[Dict[str, Any]]:
        """
        List MFA devices for a user.
        Requires: iam:ListMFADevices
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("list_mfa_devices", {
                "ctx": ctx,
                "user_name": user_name
            })

            if isinstance(result, dict):
                return result.get("MFADevices", result.get("mfa_devices", []))
            elif isinstance(result, list):
                return result
            return []
        except Exception as e:
            print(f"Error listing MFA devices for {user_name}: {e}")
            return []

    def get_login_profile(self, user_name: str) -> Dict[str, Any]:
        """
        Get console login profile for a user.
        Requires: iam:GetLoginProfile
        Returns empty dict if user doesn't have console access.
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_login_profile", {
                "ctx": ctx,
                "user_name": user_name
            })

            if isinstance(result, dict):
                return result.get("LoginProfile", result)
            return {}
        except Exception as e:
            # Users without console access will throw NoSuchEntity error
            # This is expected, so don't print error
            return {}

    def get_access_key_last_used(self, access_key_id: str) -> Dict[str, Any]:
        """
        Get last usage info for an access key.
        Requires: iam:GetAccessKeyLastUsed
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_access_key_last_used", {
                "ctx": ctx,
                "access_key_id": access_key_id
            })

            if isinstance(result, dict):
                return result.get("AccessKeyLastUsed", result.get("access_key_last_used", result))
            return {}
        except Exception as e:
            print(f"Error getting access key last used for {access_key_id}: {e}")
            return {}

    def generate_credential_report(self) -> bool:
        """
        Generate credential report (async operation).
        Requires: iam:GenerateCredentialReport
        Returns True if generation started successfully.
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("generate_credential_report", {"ctx": ctx})

            if isinstance(result, dict):
                state = result.get("State", result.get("state", ""))
                return state in ["STARTED", "INPROGRESS", "COMPLETE"]
            return False
        except Exception as e:
            print(f"Error generating credential report: {e}")
            return False

    def get_credential_report(self) -> Dict[str, Any]:
        """
        Get credential report content.
        Requires: iam:GetCredentialReport
        Note: Must call generate_credential_report first and wait for completion.
        """
        try:
            ctx = {"content": [], "isError": False}
            result = self.call_tool("get_credential_report", {"ctx": ctx})

            if isinstance(result, dict):
                # The report content is base64 encoded CSV
                import base64
                content = result.get("Content", result.get("content", ""))
                if content:
                    try:
                        decoded = base64.b64decode(content).decode('utf-8')
                        return {"content": decoded, "raw": result}
                    except:
                        return {"content": content, "raw": result}
            return {}
        except Exception as e:
            print(f"Error getting credential report: {e}")
            return {}


class VaultMCPClient(MCPClient):
    """Client for Vault MCP Server."""

    def __init__(self, vault_address: Optional[str] = None, vault_token: Optional[str] = None):
        """
        Initialize Vault MCP client.

        Args:
            vault_address: Vault server address
            vault_token: Vault authentication token
        """
        # Try multiple possible commands for Vault MCP server
        # Option 1: Using Docker (recommended - most reliable)
        # Option 2: Using npx (if installed via npm)
        # Option 3: Using uvx (if available)
        # Option 4: Direct binary (if installed globally)
        import shutil

        env = {}
        if vault_address:
            env["VAULT_ADDR"] = vault_address
        if vault_token:
            env["VAULT_TOKEN"] = vault_token

        # Try Docker first (most reliable option)
        if shutil.which("docker"):
            # Check if the vault-mcp image is available
            try:
                import subprocess
                result = subprocess.run(
                    ["docker", "images", "-q", "ashgw/vault-mcp:latest"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout.strip():
                    # Image exists, use Docker
                    command = [
                        "docker", "run", "--rm", "-i",
                        "-e", f"VAULT_ADDR={vault_address}" if vault_address else "VAULT_ADDR=",
                        "-e", f"VAULT_TOKEN={vault_token}" if vault_token else "VAULT_TOKEN=",
                        "ashgw/vault-mcp:latest"
                    ]
                    # Don't pass env to parent since we're setting them in docker run
                    env = {}
                    super().__init__(command, env)
                    return
            except:
                pass

        # Fallback to other methods
        vault_commands = [
            ["npx", "-y", "@hashicorp/vault-mcp-server"],
            ["uvx", "@hashicorp/vault-mcp-server@latest"],
            ["vault-mcp-server"],
        ]

        command = None
        for cmd in vault_commands:
            if shutil.which(cmd[0]):
                command = cmd
                break

        if not command:
            # Default to Docker if available, otherwise npx
            if shutil.which("docker"):
                command = [
                    "docker", "run", "--rm", "-i",
                    "-e", f"VAULT_ADDR={vault_address}" if vault_address else "VAULT_ADDR=",
                    "-e", f"VAULT_TOKEN={vault_token}" if vault_token else "VAULT_TOKEN=",
                    "ashgw/vault-mcp:latest"
                ]
                env = {}
            else:
                command = ["npx", "-y", "@hashicorp/vault-mcp-server"]

        super().__init__(command, env)
    
    def list_identities(self) -> List[Dict[str, Any]]:
        """List all identities from Vault."""
        try:
            identities = []

            # The Vault MCP server uses resources for listing, not tools
            # Tools like create_secret, read_secret require specific arguments
            # Resources like vault://secrets and vault://policies are for listing

            try:
                resources = self.list_resources()

                # Process each resource
                for resource in resources:
                    try:
                        uri = resource.get("uri", "")
                        name = resource.get("name", "")

                        # Read the resource content
                        content = self.read_resource(uri)

                        # Parse the content
                        if isinstance(content, list):
                            for item in content:
                                if isinstance(item, dict):
                                    # Extract text content if it's wrapped
                                    if "text" in item:
                                        try:
                                            import json
                                            text_data = json.loads(item["text"])
                                            if isinstance(text_data, list):
                                                # Add metadata about the source
                                                for entry in text_data:
                                                    if isinstance(entry, dict):
                                                        entry["_source"] = name or uri
                                                        identities.append(entry)
                                                    elif isinstance(entry, str):
                                                        identities.append({
                                                            "name": entry,
                                                            "type": "secret" if "secret" in uri else "policy",
                                                            "_source": name or uri
                                                        })
                                            elif isinstance(text_data, dict):
                                                text_data["_source"] = name or uri
                                                identities.append(text_data)
                                        except:
                                            # If not JSON, treat as plain text
                                            identities.append({
                                                "content": item["text"],
                                                "_source": name or uri
                                            })
                                    else:
                                        item["_source"] = name or uri
                                        identities.append(item)
                                elif isinstance(item, str):
                                    identities.append({
                                        "name": item,
                                        "_source": name or uri
                                    })
                        elif isinstance(content, dict):
                            content["_source"] = name or uri
                            identities.append(content)

                    except Exception as resource_error:
                        print(f"Error reading resource {resource.get('uri')}: {resource_error}")
                        continue

            except Exception as resource_error:
                print(f"Error listing resources: {resource_error}")

            # Only try tools that are specifically for listing (don't require arguments)
            # Most Vault MCP tools require arguments, so we skip them
            try:
                tools = self.list_tools()
                list_tools = [
                    t for t in tools
                    if t.get("name", "").lower().startswith("list_") and
                    "list" in t.get("name", "").lower()
                ]

                for tool in list_tools:
                    try:
                        tool_name = tool.get("name")
                        # Only try if the tool has no required parameters
                        schema = tool.get("inputSchema", {})
                        required = schema.get("required", [])

                        if not required:  # Only call if no required params
                            result = self.call_tool(tool_name, {})
                            if isinstance(result, list):
                                identities.extend(result)
                            elif isinstance(result, dict):
                                for key in ["identities", "entities", "secrets", "keys", "data", "items"]:
                                    if key in result and isinstance(result[key], list):
                                        identities.extend(result[key])
                                        break
                    except Exception as tool_error:
                        # Silently skip tools that fail
                        continue
            except:
                pass

            return identities if identities else []
        except Exception as e:
            print(f"Error fetching Vault identities: {e}")
            return []

