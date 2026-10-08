import os, json, httpx
from typing import Any
from .config import settings

class MCPClient:
    """
    Minimal Streamable HTTP MCP client.

    In production, use the official MCP client implementation matching the
    protocol version supported by your deployed AgentCore MCP runtime.
    This adapter keeps the application boundary small and typed.
    """
    def __init__(self, url: str | None = None):
        self.url = url or settings.mcp_url
        self.session_id: str | None = None

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        payload = {
            "jsonrpc": "2.0",
            "id": "eks-sre",
            "method": "tools/call",
            "params": {"name": name, "arguments": arguments},
        }
        headers = {"content-type": "application/json"}
        if self.session_id:
            headers["Mcp-Session-Id"] = self.session_id

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(self.url, json=payload, headers=headers)
            r.raise_for_status()
            if r.headers.get("mcp-session-id"):
                self.session_id = r.headers["mcp-session-id"]
            data = r.json()
            if "error" in data:
                raise RuntimeError(data["error"])
            return data.get("result", data)
