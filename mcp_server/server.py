import os
from mcp.server.fastmcp import FastMCP
from .eks import cluster_health, workload_evidence, events

REGION = os.getenv("AWS_REGION", "us-east-1")

mcp = FastMCP("eks-sre-tools", stateless_http=True)

@mcp.tool()
def get_cluster_health(cluster: str, namespace: str = "default") -> dict:
    """Read-only EKS control-plane/cluster health evidence."""
    return cluster_health(cluster, REGION)

@mcp.tool()
def get_workload_evidence(cluster: str, namespace: str = "default") -> dict:
    """Read-only workload/pod/deployment evidence."""
    return workload_evidence(cluster, namespace, REGION)

@mcp.tool()
def get_events(cluster: str, namespace: str = "default") -> dict:
    """Read-only recent Kubernetes events."""
    return {"events": events(cluster, namespace, REGION)}

if __name__ == "__main__":
    # FastMCP's HTTP server uses the MCP streamable HTTP endpoint.
    mcp.run(transport="streamable-http", host="0.0.0.0", port=8000)
