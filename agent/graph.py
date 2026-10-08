from typing import TypedDict, Any
from langgraph.graph import StateGraph, START, END
from langchain_aws import ChatBedrockConverse
from .config import settings
from .prompts import SYSTEM_PROMPT
from .mcp_client import MCPClient

class State(TypedDict, total=False):
    cluster: str
    namespace: str
    message: str
    evidence: list[dict[str, Any]]
    diagnosis: dict[str, Any]

async def collect_evidence(state: State):
    c = MCPClient()
    args = {"cluster": state["cluster"], "namespace": state["namespace"]}
    evidence = []
    for tool in ("get_cluster_health", "get_workload_evidence", "get_events"):
        try:
            evidence.append({"tool": tool, "data": await c.call_tool(tool, args)})
        except Exception as exc:
            evidence.append({"tool": tool, "error": str(exc)})
    return {"evidence": evidence}

async def reason(state: State):
    llm = ChatBedrockConverse(
        model=settings.model_id,
        region_name=settings.aws_region,
        temperature=0,
    )
    prompt = (
        SYSTEM_PROMPT
        + "\nUser incident:\n" + state["message"]
        + "\nCluster: " + state["cluster"]
        + "\nNamespace: " + state["namespace"]
        + "\nEvidence:\n" + str(state.get("evidence", []))
        + "\nReturn a concise JSON-like diagnosis with incident, severity, "
          "root_cause, confidence, evidence, recommended_actions, "
          "actions_taken, approval_required."
    )
    response = await llm.ainvoke(prompt)
    return {"diagnosis": {"text": response.content}}

builder = StateGraph(State)
builder.add_node("collect_evidence", collect_evidence)
builder.add_node("reason", reason)
builder.add_edge(START, "collect_evidence")
builder.add_edge("collect_evidence", "reason")
builder.add_edge("reason", END)
graph = builder.compile()
