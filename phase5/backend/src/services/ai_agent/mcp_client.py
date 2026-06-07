"""
MCP Client for executing tools via the MCP server.

Uses HTTP client to call tools defined in MCP server.
"""
import httpx
from typing import Dict, Any, List, Optional


class MCPClient:
    """
    MCP Client for executing tools via the MCP server.

    Uses HTTP client to call tools defined in MCP server.
    """

    def __init__(self, base_url: str = "http://localhost:8001"):
        """
        Initialize MCP Client.

        Args:
            base_url: Base URL of the MCP server
        """
        self.base_url = base_url
        self._http_client: Optional[httpx.AsyncClient] = None
        self._connected = False

    async def connect(self) -> None:
        """
        Connect to the MCP server by initializing HTTP client.

        Raises:
            RuntimeError: If connection fails
        """
        if self._connected:
            return

        try:
            self._http_client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
            # Test connection by listing tools
            await self.list_tools()
            self._connected = True
        except Exception as e:
            raise RuntimeError(f"Failed to connect to MCP server at {self.base_url}: {e}")

    async def list_tools(self) -> List[Dict[str, Any]]:
        """
        List all available tools from MCP server.

        Returns:
            List of tool dictionaries with name, description, and input_schema

        Raises:
            RuntimeError: If not connected to MCP server
        """
        if not self._connected:
            await self.connect()

        if not self._http_client:
            raise RuntimeError("MCP client not initialized")

        try:
            response = await self._http_client.get("/tools")
            response.raise_for_status()
            data = response.json()
            return data.get("tools", [])
        except Exception as e:
            raise RuntimeError(f"Failed to list tools: {e}")

    async def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Call a specific tool via MCP server.

        Args:
            name: Name of the tool to call
            arguments: Tool arguments

        Returns:
            Tool execution result as dictionary

        Raises:
            RuntimeError: If not connected to MCP server or call fails
        """
        if not self._connected:
            await self.connect()

        if not self._http_client:
            raise RuntimeError("MCP client not initialized")

        try:
            response = await self._http_client.post(f"/tools/{name}", json=arguments)
            response.raise_for_status()
            data = response.json()
            return data.get("result", {})
        except httpx.HTTPStatusError as e:
            raise RuntimeError(f"Tool execution failed: {e.response.text}")
        except Exception as e:
            raise RuntimeError(f"Failed to call tool '{name}': {e}")

    async def close(self) -> None:
        """Close the MCP client connection."""
        if self._http_client:
            try:
                await self._http_client.aclose()
            except Exception:
                pass
            finally:
                self._http_client = None
                self._connected = False

    async def __aenter__(self):
        """Context manager entry."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()
