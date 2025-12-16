"""
MCP Connector - Bridge between Python and Cursor's MCP tools
"""
import json
import subprocess
from typing import Dict, Any, Optional
from pathlib import Path


class MCPConnector:
    """
    Connects to MCP servers configured in Cursor.
    
    Since Cursor's MCP tools run via npx/uvx commands, we'll use subprocess
    to invoke them directly with the same configuration from mcp.json.
    """
    
    def __init__(self, mcp_config_path: Optional[str] = None):
        """
        Initialize MCP connector.
        
        Args:
            mcp_config_path: Path to Cursor's mcp.json config file
        """
        if mcp_config_path is None:
            # Default to Cursor's MCP config location
            mcp_config_path = str(Path.home() / ".cursor" / "mcp.json")
        
        self.mcp_config_path = mcp_config_path
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load MCP server configuration from Cursor's mcp.json."""
        try:
            with open(self.mcp_config_path, 'r') as f:
                config = json.load(f)
                return config.get('mcpServers', {})
        except FileNotFoundError:
            print(f"Warning: MCP config not found at {self.mcp_config_path}")
            return {}
        except json.JSONDecodeError as e:
            print(f"Error parsing MCP config: {e}")
            return {}
    
    def call_mcp_tool(
        self, 
        server_name: str, 
        tool_name: str, 
        arguments: Dict[str, Any],
        timeout: int = 60
    ) -> Dict[str, Any]:
        """
        Call an MCP tool by communicating with the MCP server.
        
        Args:
            server_name: Name of the MCP server (e.g., 'airbnb', 'Aviationstack MCP')
            tool_name: Name of the tool to call
            arguments: Tool arguments as a dictionary
            timeout: Timeout in seconds
            
        Returns:
            Tool response as a dictionary
            
        Raises:
            RuntimeError: If the tool call fails
        """
        # Map user-facing names to config names
        server_key = server_name.lower().replace('user-', '').replace(' ', '-')
        
        if server_key not in self.config:
            # Try exact match
            server_key = server_name
            if server_key not in self.config:
                raise ValueError(f"MCP server '{server_name}' not found in config. Available: {list(self.config.keys())}")
        
        server_config = self.config[server_key]
        command = server_config['command']
        args = server_config.get('args', [])
        env = server_config.get('env', {})
        
        # Create MCP request payload
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            # Build subprocess command
            cmd = [command] + args
            
            # Prepare environment
            import os
            proc_env = os.environ.copy()
            proc_env.update(env)
            
            # For now, we'll use a simplified approach:
            # Since we can't directly communicate with MCP servers via subprocess easily,
            # we'll create a wrapper that simulates the MCP protocol.
            # In a real implementation, you'd use the MCP Python SDK or stdio communication.
            
            # Placeholder: Return mock structure for now
            # In production, this would actually call the MCP server
            result = self._call_via_mcp_protocol(
                command, args, env, tool_name, arguments, timeout
            )
            
            return result
            
        except subprocess.TimeoutExpired:
            raise RuntimeError(f"MCP tool call timed out after {timeout}s")
        except Exception as e:
            raise RuntimeError(f"Failed to call MCP tool: {str(e)}")
    
    def _call_via_mcp_protocol(
        self,
        command: str,
        args: list,
        env: dict,
        tool_name: str,
        arguments: dict,
        timeout: int
    ) -> Dict[str, Any]:
        """
        Call MCP tool using the Model Context Protocol over stdio.
        
        This is a simplified implementation. In production, use the official MCP Python SDK.
        """
        import os
        
        # Prepare environment
        proc_env = os.environ.copy()
        proc_env.update(env)
        
        # Create JSON-RPC request
        request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        try:
            # Start the MCP server process
            cmd = [command] + args
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=proc_env,
                text=True
            )
            
            # Send initialization handshake
            init_request = {
                "jsonrpc": "2.0",
                "id": 0,
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {
                        "name": "travel-agent",
                        "version": "1.0.0"
                    }
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.flush()
            
            # Read initialization response (skip for now, simplified)
            
            # Send the actual tool call
            process.stdin.write(json.dumps(request) + "\n")
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline()
            
            if not response_line:
                stderr = process.stderr.read()
                raise RuntimeError(f"No response from MCP server. Error: {stderr}")
            
            response = json.loads(response_line)
            
            # Clean up
            process.stdin.close()
            process.terminate()
            process.wait(timeout=5)
            
            # Check for errors
            if "error" in response:
                raise RuntimeError(f"MCP tool error: {response['error']}")
            
            # Return the result
            return response.get("result", {})
            
        except subprocess.TimeoutExpired:
            if 'process' in locals():
                process.kill()
            raise RuntimeError(f"MCP server timed out")
        except json.JSONDecodeError as e:
            raise RuntimeError(f"Invalid JSON response from MCP server: {e}")
        except Exception as e:
            raise RuntimeError(f"MCP call failed: {str(e)}")
    
    def list_available_servers(self) -> list:
        """List all configured MCP servers."""
        return list(self.config.keys())
    
    def get_server_info(self, server_name: str) -> Dict:
        """Get configuration for a specific MCP server."""
        server_key = server_name.lower().replace('user-', '').replace(' ', '-')
        return self.config.get(server_key, {})


# Global instance
_connector = None

def get_mcp_connector() -> MCPConnector:
    """Get or create the global MCP connector instance."""
    global _connector
    if _connector is None:
        _connector = MCPConnector()
    return _connector

