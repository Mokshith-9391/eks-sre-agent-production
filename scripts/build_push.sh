#!/usr/bin/env bash
set -euo pipefail
: "${AWS_REGION:?}"
ACCOUNT_ID="$(aws sts get-caller-identity --query Account --output text)"
REGISTRY="${ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"
TAG="${1:-$(git rev-parse --short HEAD)}"
aws ecr get-login-password --region "$AWS_REGION" | docker login --username AWS --password-stdin "$REGISTRY"
docker buildx build --platform linux/arm64 -f Dockerfile.agent -t "$REGISTRY/eks-sre-agent:$TAG" --push .
docker buildx build --platform linux/arm64 -f Dockerfile.mcp -t "$REGISTRY/eks-sre-mcp:$TAG" --push .
echo "$REGISTRY/eks-sre-agent:$TAG"
echo "$REGISTRY/eks-sre-mcp:$TAG"
