# Data Model: Kubernetes Deployment for TodoGenie Application

## Kubernetes Resources

### 1. Application Deployment
**Entity**: ApplicationDeployment
- **Fields**:
  - name: string (application name)
  - replicas: integer (desired number of pods)
  - image: string (container image reference)
  - env: array of EnvironmentVariable objects
  - resources: ResourceRequirements object
  - healthChecks: HealthCheckConfig object

**Relationships**:
- Contains multiple pods
- Connected to Service for network access

### 2. Network Service
**Entity**: NetworkService
- **Fields**:
  - name: string (service name)
  - selector: map of labels to match pods
  - ports: array of Port objects
  - type: enum (ClusterIP, NodePort, LoadBalancer)

**Relationships**:
- Routes traffic to ApplicationDeployment pods
- May be exposed via Ingress

### 3. Persistent Storage
**Entity**: PersistentStorage
- **Fields**:
  - name: string (storage identifier)
  - size: string (storage capacity)
  - storageClass: string (storage type)
  - accessModes: array of strings (ReadWriteOnce, ReadOnlyMany, etc.)

**Relationships**:
- Used by StatefulSet for database persistence
- Referenced by PersistentVolumeClaim

### 4. Configuration Object
**Entity**: ConfigurationObject
- **Fields**:
  - name: string (config name)
  - data: map of key-value pairs (configuration data)
  - type: enum (ConfigMap, Secret)

**Relationships**:
- Mounted as volumes or environment variables in Deployments
- Referenced by Pod templates

## Validation Rules

### 1. Deployment Validation
- replicas must be >= 0 and <= 100
- image must follow valid container registry format
- resource requests must be <= resource limits

### 2. Service Validation
- port numbers must be in valid range (1-65535)
- service type must be one of allowed values
- selector labels must match deployment labels

### 3. Storage Validation
- size must be specified with valid units (Gi, Mi, etc.)
- storage class must exist in cluster
- access modes must be compatible with storage provisioner

## State Transitions

### 1. Pod Lifecycle
- Pending → Running → Terminating → Deleted
- Running → Failed (on crash) → Restarting (based on restartPolicy)

### 2. Service Availability
- Created → Pending → Active → Terminating
- Active → Unhealthy (when no ready endpoints) → Active (when endpoints restored)

## Infrastructure Components

### 1. Database StatefulSet
- Persistent identity across restarts
- Ordered deployment and scaling
- Dedicated persistent storage per pod

### 2. Application Deployment
- Replica management
- Rolling updates
- Horizontal scaling capability

### 3. Ingress Controller
- External traffic routing
- TLS termination
- Load balancing