import base64, boto3
from kubernetes import client as k8s

def eks_clients(cluster: str, region: str):
    eks = boto3.client("eks", region_name=region)
    desc = eks.describe_cluster(name=cluster)["cluster"]
    token = boto3.session.Session(region_name=region).client("eks").get_token(name=cluster)["token"]
    cfg = k8s.Configuration()
    cfg.host = desc["endpoint"]
    cfg.verify_ssl = True
    cfg.ssl_ca_cert = "/tmp/eks-ca.crt"
    with open(cfg.ssl_ca_cert, "wb") as f:
        f.write(base64.b64decode(desc["certificateAuthority"]["data"]))
    cfg.api_key = {"authorization": token}
    cfg.api_key_prefix = {"authorization": "Bearer"}
    api = k8s.ApiClient(cfg)
    return eks, api

def cluster_health(cluster: str, region: str):
    eks, _ = eks_clients(cluster, region)
    d = eks.describe_cluster(name=cluster)["cluster"]
    return {
        "name": d["name"],
        "status": d["status"],
        "version": d.get("version"),
        "platform_version": d.get("platformVersion"),
        "endpoint_public_access": d.get("resourcesVpcConfig", {}).get("endpointPublicAccess"),
        "endpoint_private_access": d.get("resourcesVpcConfig", {}).get("endpointPrivateAccess"),
        "health": d.get("health", {}),
    }

def workload_evidence(cluster: str, namespace: str, region: str):
    _, api = eks_clients(cluster, region)
    core = k8s.CoreV1Api(api)
    apps = k8s.AppsV1Api(api)
    pods = core.list_namespaced_pod(namespace=namespace).items
    deployments = apps.list_namespaced_deployment(namespace=namespace).items
    out = []
    for p in pods[:50]:
        out.append({
            "pod": p.metadata.name,
            "phase": p.status.phase,
            "node": p.spec.node_name,
            "restarts": sum((cs.restart_count or 0) for cs in (p.status.container_statuses or [])),
            "container_states": [
                {
                    "name": cs.name,
                    "ready": cs.ready,
                    "restart_count": cs.restart_count,
                    "state": str(cs.state),
                    "last_state": str(cs.last_state),
                } for cs in (p.status.container_statuses or [])
            ],
        })
    return {
        "pods": out,
        "deployments": [
            {
                "name": d.metadata.name,
                "desired": d.spec.replicas,
                "available": d.status.available_replicas,
                "ready": d.status.ready_replicas,
                "updated": d.status.updated_replicas,
            } for d in deployments
        ],
    }

def events(cluster: str, namespace: str, region: str):
    _, api = eks_clients(cluster, region)
    core = k8s.CoreV1Api(api)
    ev = core.list_namespaced_event(namespace=namespace).items
    ev.sort(key=lambda x: x.last_timestamp or x.event_time or x.first_timestamp, reverse=True)
    return [
        {
            "type": e.type,
            "reason": e.reason,
            "message": e.message,
            "object": getattr(e.involved_object, "name", None),
            "kind": getattr(e.involved_object, "kind", None),
            "count": e.count,
        } for e in ev[:100]
    ]
