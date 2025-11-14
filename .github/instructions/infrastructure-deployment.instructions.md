---
description: Infrastructure, deployment, and IaC conventions for Docker, Kubernetes, Terraform, and CI/CD
applyTo: "IaC/**"
---

# Infrastructure and Deployment

## Overview
This project uses a multi-stage deployment strategy:
- **Local Development**: Docker Compose with hot-reload and local overrides
- **Production**: Azure Kubernetes Service (AKS) with Helm chart deployment
- **Infrastructure Provisioning**: Terraform for Azure resources (Resource Group, ACR, AKS)
- **CI/CD**: GitHub Actions for build, test, push, and deploy automation

## Container Architecture

### Application Containers
- **api** (port 5000): Python Flask + Socket.IO API server
  - Production: gunicorn with eventlet worker for WebSocket support
  - Health endpoint: `GET /api/health`
  - Image: Built from `IaC/Dockerfile.api`
  
- **agent** (port 7000): Background worker for async tasks and model warmup
  - Health endpoint: `GET /health`
  - Image: Built from `IaC/Dockerfile.agent`
  
- **frontend** (port 80): React SPA served by Nginx
  - Health endpoint: `GET /healthz`
  - Image: Built from `frontend/Dockerfile`

### Dockerfile Best Practices
- **Multi-stage builds**: Separate build and runtime stages to minimize image size
- **Non-root user**: Create and switch to non-root user (e.g., `appuser` with UID 1001)
- **Layer optimization**: Order instructions from least to most frequently changing (system deps → Python deps → app code)
- **Health checks**: Define HEALTHCHECK instruction matching application health endpoint
- **Security**: No secrets in layers; use build args or runtime env vars
- **Python specifics**:
  - Set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`
  - Use `pip install --no-cache-dir` to reduce layer size
  - Set `PYTHONPATH=/app/src` for absolute imports

### Port and Probe Alignment
**CRITICAL**: Ensure consistency across all layers:
- Dockerfile `EXPOSE` directive
- Container `HEALTHCHECK` command path
- docker-compose.yml port mappings
- Helm chart `containerPort`, `service.port`, and probe paths
- Application server binding (e.g., `0.0.0.0:5000`)

**Example alignment**:
```yaml
# Dockerfile.api
EXPOSE 5000
HEALTHCHECK CMD curl -f http://localhost:5000/api/health || exit 1

# docker-compose.yml
services:
  api:
    ports: ["5000:5000"]

# Helm values.yaml
api:
  containerPort: 5000
  livenessProbe:
    httpGet:
      path: /api/health
      port: 5000
```

## Docker Compose Conventions

### Local Override Pattern
- **Upstream file**: `docker-compose.yml` — committed, dev-friendly defaults
- **Local overrides**: `docker-compose.override.yml` — gitignored, user-specific tweaks
- **Environment-specific**: `docker-compose.k8s-local.override.yml` — testing K8s-like configs locally

### Compose Best Practices
- **Service dependencies**: Use `depends_on` to define startup order
- **Environment files**: Load `.env` via `env_file: .env` for centralized config
- **Networks**: Define explicit networks (`appnet`) for service isolation
- **Volume mounts**: Use named volumes for persistence; avoid host path mounts in production patterns
- **Windows gotcha**: Port ranges 27017-27018 may be reserved; use alternate host ports (e.g., `27034:27017`)

### Development Workflow
```powershell
# Start all services with rebuild
docker-compose up --build

# Start specific services
docker-compose up api frontend

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f api

# Stop and remove
docker-compose down

# Clean volumes (CAUTION: data loss)
docker-compose down -v
```

## Helm Chart Structure

### Chart Organization (`helm/dp-stock/`)
```
dp-stock/
├── Chart.yaml           # Chart metadata
├── values.yaml          # Default values (dev-friendly)
├── values.local.yaml    # Local K8s overrides
├── values.production.yaml  # Production overrides
└── templates/
    ├── _helpers.tpl     # Template helpers
    ├── deployment-api.yaml
    ├── deployment-agent.yaml
    ├── deployment-frontend.yaml
    ├── service-api.yaml
    ├── service-frontend.yaml
    ├── ingress.yaml     # Optional ingress routing
    └── configmap.yaml   # Non-sensitive config
```

### Helm Values Conventions
- **Image management**:
  ```yaml
  api:
    image:
      repository: yourregistry.azurecr.io/dp-stock/api
      tag: "1.0.0"  # Override in CI with commit SHA or release tag
      pullPolicy: IfNotPresent
  ```
- **Environment-specific values**:
  - `values.yaml` — Defaults for local/dev (low resources, no ingress)
  - `values.production.yaml` — Production overrides (replicas: 3, resource limits, ingress enabled)
- **Resource limits**: Always set requests and limits in production values
  ```yaml
  api:
    resources:
      requests: { memory: "256Mi", cpu: "100m" }
      limits: { memory: "512Mi", cpu: "500m" }
  ```

### Helm Deployment Commands
```powershell
# Install or upgrade (local)
helm upgrade --install dp-stock ./helm/dp-stock -f ./helm/dp-stock/values.local.yaml

# Install with production values
helm upgrade --install dp-stock ./helm/dp-stock -f ./helm/dp-stock/values.production.yaml

# Override image tag (CI pattern)
helm upgrade --install dp-stock ./helm/dp-stock --set api.image.tag=$env:GITHUB_SHA

# Dry run to validate
helm upgrade --install dp-stock ./helm/dp-stock --dry-run --debug

# Uninstall
helm uninstall dp-stock
```

### Probe Configuration Best Practices
- **Startup probes**: For slow-starting applications (model loading); higher failure threshold
  ```yaml
  startupProbe:
    httpGet: { path: /api/health, port: 5000 }
    initialDelaySeconds: 10
    periodSeconds: 5
    failureThreshold: 30  # Allow up to 150s for startup
  ```
- **Liveness probes**: Detect deadlocks; restart on failure
  ```yaml
  livenessProbe:
    httpGet: { path: /api/health, port: 5000 }
    initialDelaySeconds: 15
    periodSeconds: 30
    failureThreshold: 3
  ```
- **Readiness probes**: Remove from load balancer when unhealthy
  ```yaml
  readinessProbe:
    httpGet: { path: /api/health, port: 5000 }
    initialDelaySeconds: 5
    periodSeconds: 10
  ```

## Terraform Infrastructure Provisioning

### Resources Managed (`infra/terraform/`)
- **Resource Group**: Container for all Azure resources
- **Azure Container Registry (ACR)**: Private image registry with admin disabled
- **Azure Kubernetes Service (AKS)**: Managed K8s cluster with SystemAssigned identity, OIDC, Azure CNI
- **Role Assignment**: Grant AKS kubelet identity `AcrPull` role on ACR

### Terraform Workflow
```powershell
cd IaC\infra\terraform

# Initialize providers
terraform init

# Validate configuration
terraform validate

# Plan changes (dry run)
terraform plan -out=tfplan

# Apply changes
terraform apply tfplan

# Destroy infrastructure (CAUTION)
terraform destroy
```

### Terraform Best Practices
- **State management**: Use remote backend (Azure Storage Account) for team collaboration
  ```hcl
  terraform {
    backend "azurerm" {
      resource_group_name  = "tfstate-rg"
      storage_account_name = "tfstatestorageacct"
      container_name       = "tfstate"
      key                  = "dp-stock.tfstate"
    }
  }
  ```
- **Variables**: Define in `variables.tf`; provide via `terraform.tfvars` or env vars (`TF_VAR_*`)
- **Outputs**: Expose ACR login server, AKS name, resource group for CI/CD consumption
- **Ignore changes**: Use lifecycle `ignore_changes` for dynamic fields (e.g., node_count autoscaling)
- **Security**:
  - Never enable ACR admin user; use managed identities or service principals
  - Use RBAC for AKS access; avoid cluster admin certificates
  - Enable Azure Policy and network policies for production

### Infrastructure as Code Principles
- **Idempotency**: Resources can be applied multiple times without side effects
- **Version control**: Commit all `.tf` files; gitignore `*.tfstate`, `.terraform/`, `*.tfvars` (if sensitive)
- **Documentation**: Update `IaC/README.md` when adding/changing resources
- **Environment separation**: Use workspaces or separate state files per environment (dev, staging, prod)

## CI/CD Pipeline Conventions

### GitHub Actions Workflows (`ci-cd/`)
- **github-pr-ci.yml**: PR validation (build, test, lint, security scan, Docker build without push)
- **build-push-images.yml**: Build and push images to ACR on merge to main or release tag
- **deploy-to-aks.yml**: Deploy Helm chart to AKS with environment-specific values

### CI/CD Best Practices
- **Authentication**: Use OIDC with federated credentials; avoid long-lived secrets
  ```yaml
  - name: Azure Login
    uses: azure/login@v1
    with:
      client-id: ${{ secrets.AZURE_CLIENT_ID }}
      tenant-id: ${{ secrets.AZURE_TENANT_ID }}
      subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
  ```
- **Image tagging strategy**:
  - PR builds: `pr-${{ github.sha }}`
  - Main branch: `${{ github.sha }}`, `latest`
  - Release tags: `${{ github.ref_name }}`, `v1.0.0`
- **Secrets management**: Store in GitHub Secrets; inject via workflow env vars
- **Multi-stage jobs**: Separate build, test, push, deploy for parallelization and rollback
- **Artifact caching**: Cache npm/pip dependencies to speed up builds
- **Smoke tests**: Run basic health checks after deployment before marking as success
  ```yaml
  - name: Smoke Test
    run: |
      sleep 30  # Allow pods to start
      kubectl get pods
      curl -f http://<ingress-url>/api/health || exit 1
  ```

### Deployment Promotion Strategy
- **No rebuild between environments**: Tag same image digest with environment labels
- **Environment values files**: Use Helm value overrides per environment
  ```yaml
  helm upgrade --install dp-stock ./helm/dp-stock \
    -f ./helm/dp-stock/values.production.yaml \
    --set api.image.tag=${{ github.sha }}
  ```
- **Rollback mechanism**: Helm rollback command or GitOps revert
  ```powershell
  helm rollback dp-stock 1  # Rollback to revision 1
  ```

## Security Best Practices

### Container Security
- **Base images**: Use official, slim images (e.g., `python:3.11-slim`, `nginx:alpine`)
- **Vulnerability scanning**: Run Trivy or similar scanner in CI before push
  ```yaml
  - name: Scan image
    run: |
      docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
        aquasec/trivy image --severity HIGH,CRITICAL dp-stock/api:${{ github.sha }}
  ```
- **No secrets in layers**: Use multi-stage builds; pass secrets via build args (with `--secret` flag) or runtime env vars
- **Minimal attack surface**: Remove build tools and unnecessary packages in final stage

### Kubernetes Security
- **RBAC**: Apply least-privilege service accounts; avoid default namespace
- **Network policies**: Restrict pod-to-pod communication to necessary paths
- **Pod security standards**: Use restricted or baseline profiles (no privileged containers)
- **Secrets management**: Use Azure Key Vault with CSI driver or External Secrets Operator
- **Image pull secrets**: Use managed identity integration with ACR; avoid ImagePullSecrets with hardcoded credentials

### Cloud Security
- **Managed identities**: Use SystemAssigned or UserAssigned identities for Azure resource access
- **Private endpoints**: Use private AKS clusters and ACR private endpoints for production
- **Audit logging**: Enable Azure Monitor and Azure Policy for compliance
- **Encryption**: Enable encryption at rest for AKS node pools and ACR

## Monitoring and Observability

### Logging
- **Container stdout/stderr**: All logs to stdout; captured by Kubernetes
- **Structured logging**: JSON format for easier parsing
- **Log aggregation**: Use Azure Log Analytics or ELK stack
- **Retention**: Define retention policies per environment (30 days dev, 90+ days prod)

### Metrics
- **Application metrics**: Expose Prometheus-compatible `/metrics` endpoint
- **Resource metrics**: CPU, memory, disk from Kubernetes metrics server
- **Custom metrics**: Business KPIs (requests/sec, model latency, cache hit rate)

### Tracing
- **Distributed tracing**: Use OpenTelemetry or Azure Application Insights
- **Correlation IDs**: Pass through all service calls for request tracking

### Alerting
- **Critical alerts**: Pod restarts, OOM kills, health check failures, high latency
- **Notification channels**: Slack, email, PagerDuty for production incidents
- **Runbooks**: Document remediation steps for common alerts

## Disaster Recovery and High Availability

### Backup Strategy
- **Database**: Automated MongoDB backups with point-in-time restore
- **Configuration**: Version-controlled in Git (Helm values, Terraform state)
- **Container images**: Immutable tags stored in ACR with retention policy

### High Availability
- **Multi-replica deployments**: Run 3+ replicas per service in production
- **Pod disruption budgets**: Ensure minimum replicas during updates
  ```yaml
  apiVersion: policy/v1
  kind: PodDisruptionBudget
  metadata:
    name: api-pdb
  spec:
    minAvailable: 2
    selector:
      matchLabels:
        app: api
  ```
- **Multi-zone AKS**: Distribute nodes across availability zones
- **Health probes**: Configure liveness and readiness to auto-heal unhealthy pods

### Rollback and Recovery
- **Helm rollback**: Revert to previous release revision
- **Blue-green deployments**: Run old and new versions simultaneously; switch traffic
- **Canary deployments**: Gradual rollout with traffic splitting (Istio, Linkerd)
- **Database migrations**: Use forward-compatible schemas; test rollback procedures

## Performance Optimization

### Container Optimization
- **Layer caching**: Order Dockerfile instructions to maximize cache hits
- **Image size**: Remove build artifacts; use slim base images
- **Startup time**: Pre-warm models in agent container; use startup probes

### Kubernetes Optimization
- **Resource requests**: Set accurate CPU/memory requests for bin packing efficiency
- **Horizontal Pod Autoscaler**: Scale replicas based on CPU/memory or custom metrics
  ```yaml
  apiVersion: autoscaling/v2
  kind: HorizontalPodAutoscaler
  metadata:
    name: api-hpa
  spec:
    scaleTargetRef:
      apiVersion: apps/v1
      kind: Deployment
      name: api
    minReplicas: 2
    maxReplicas: 10
    metrics:
      - type: Resource
        resource:
          name: cpu
          target: { type: Utilization, averageUtilization: 70 }
  ```
- **Cluster Autoscaler**: Add/remove nodes based on pending pods

### Cloud Optimization
- **Node pools**: Use different VM sizes for different workloads (CPU-intensive vs memory-intensive)
- **Spot instances**: Use Azure Spot VMs for dev/test to reduce costs
- **Resource tagging**: Tag resources for cost allocation and governance

## Troubleshooting Guide

### Docker Compose Issues
- **Port conflicts**: Change host port in `docker-compose.override.yml`
- **Windows reserved ports**: Use ports outside 27017-27018 range (e.g., 27034)
- **Build cache issues**: Use `docker-compose build --no-cache` to force rebuild
- **Network issues**: Ensure all services on same network; check DNS resolution with `docker exec`

### Kubernetes Issues
- **ImagePullBackOff**: Check ACR authentication, image tag exists, network connectivity
  ```powershell
  kubectl describe pod <pod-name>
  kubectl logs <pod-name>
  az acr repository list --name <acr-name>
  ```
- **CrashLoopBackOff**: Check application logs, health probe configuration, resource limits
  ```powershell
  kubectl logs <pod-name> --previous  # Logs from previous crashed container
  ```
- **Pending pods**: Check node resources, pod disruption budgets, scheduler events
  ```powershell
  kubectl describe pod <pod-name>
  kubectl top nodes
  ```

### Terraform Issues
- **State lock**: Another process holds lock; wait or force-unlock (CAUTION)
- **Resource conflicts**: Use `terraform import` to adopt existing resources
- **Provider version mismatch**: Lock versions in `versions.tf`; run `terraform init -upgrade`

### Helm Issues
- **Release not found**: Check namespace with `helm list -A`
- **Values not applied**: Verify `-f` file path; use `--debug` to inspect rendered templates
- **Template errors**: Use `helm template` to render without deploying; check syntax

## References
- Docker Compose: https://docs.docker.com/compose/
- Kubernetes: https://kubernetes.io/docs/
- Helm: https://helm.sh/docs/
- Terraform: https://developer.hashicorp.com/terraform/docs
- Azure AKS: https://learn.microsoft.com/azure/aks/
- GitHub Actions: https://docs.github.com/actions
