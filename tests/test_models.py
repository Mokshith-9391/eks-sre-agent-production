from agent.models import ChatRequest

def test_request():
    x = ChatRequest(cluster="prod", namespace="payments", message="why is pod pending?")
    assert x.cluster == "prod"
