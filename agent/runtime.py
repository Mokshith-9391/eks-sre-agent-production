from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from .models import ChatRequest
from .config import settings
from .graph import graph

app = FastAPI(title="EKS SRE Agent", version="1.0.0")

@app.get("/ping")
async def ping():
    return {"status": "Healthy"}

@app.get("/", response_class=HTMLResponse)
async def ui():
    return """<!doctype html><html><body>
    <h2>EKS SRE Agent</h2>
    <p>Use POST /invocations with JSON: cluster, namespace, message.</p>
    </body></html>"""

@app.post("/invocations")
async def invocations(req: ChatRequest):
    if settings.allowed_clusters and req.cluster not in settings.allowed_clusters:
        raise HTTPException(403, "cluster not authorized")
    if settings.allowed_namespaces and req.namespace not in settings.allowed_namespaces:
        raise HTTPException(403, "namespace not authorized")
    result = await graph.ainvoke(req.model_dump())
    return {
        "incident": req.message,
        "cluster": req.cluster,
        "namespace": req.namespace,
        "result": result.get("diagnosis", {}),
        "evidence": result.get("evidence", []),
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)
