# TodoGenie Helm Chart

This Helm chart deploys the TodoGenie application, which consists of a frontend (Next.js), backend (FastAPI), and PostgreSQL database.

## Prerequisites

- Kubernetes 1.19+
- Helm 3.0+
- PV provisioner support in the underlying infrastructure

## Installing the Chart

To install the chart with the release name `todogenie`:

```bash
helm install todogenie ./todogenie --namespace todogenie --create-namespace
```

## Uninstalling the Chart

To uninstall/delete the `todogenie` release:

```bash
helm delete todogenie --namespace todogenie
```

## Configuration

The following table lists the configurable parameters of the TodoGenie chart and their default values.

| Parameter | Description | Default |
|-----------|-------------|---------|
| `frontend.replicaCount` | Number of frontend pods | `1` |
| `frontend.image.repository` | Frontend image repository | `todogenie-frontend` |
| `frontend.image.tag` | Frontend image tag | `latest` |
| `frontend.service.type` | Frontend service type | `ClusterIP` |
| `frontend.service.port` | Frontend service port | `3000` |
| `backend.replicaCount` | Number of backend pods | `1` |
| `backend.image.repository` | Backend image repository | `todogenie-backend` |
| `backend.image.tag` | Backend image tag | `latest` |
| `backend.service.type` | Backend service type | `ClusterIP` |
| `backend.service.port` | Backend service port | `8000` |
| `postgresql.enabled` | Enable PostgreSQL dependency | `true` |
| `postgresql.auth.postgresPassword` | PostgreSQL password | `"postgres"` |
| `postgresql.auth.database` | PostgreSQL database name | `"todogenie_db"` |
| `ingress.enabled` | Enable ingress | `false` |
| `ingress.hosts[0].host` | Ingress hostname | `"todogenie.local"` |

## Custom Values Example

```yaml
frontend:
  replicaCount: 2
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

backend:
  replicaCount: 2
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

postgresql:
  auth:
    postgresPassword: "your_secure_password"
    database: "todogenie_production"
  primary:
    persistence:
      size: "20Gi"
```