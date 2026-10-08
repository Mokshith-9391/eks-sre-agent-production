import os
from pydantic import BaseModel

class Settings(BaseModel):
    aws_region: str = os.getenv("AWS_REGION", "us-east-1")
    model_id: str = os.getenv("BEDROCK_MODEL_ID", "amazon.nova-pro-v1:0")
    mcp_url: str = os.getenv("MCP_URL", "http://localhost:8000/mcp")
    max_log_bytes: int = int(os.getenv("MAX_LOG_BYTES", "12000"))
    allowed_clusters: set[str] = set(filter(None, os.getenv("ALLOWED_CLUSTERS", "").split(",")))
    allowed_namespaces: set[str] = set(filter(None, os.getenv("ALLOWED_NAMESPACES", "").split(",")))

settings = Settings()
