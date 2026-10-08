#!/usr/bin/env bash
set -euo pipefail
python -m mcp_server.server &
MCP_PID=$!
trap 'kill $MCP_PID' EXIT
MCP_URL=http://localhost:8000/mcp python -m agent.runtime
