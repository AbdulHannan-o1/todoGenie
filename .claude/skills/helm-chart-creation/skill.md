# Helm Chart Creation Skill

## Overview
This skill provides comprehensive guidance for creating production-ready Helm charts for full-stack applications. It covers the complete chart structure including deployments, services, configurations, security, and database integration.

## Implementation Approach

### Complete Helm Chart Development Workflow
The Helm chart creation process includes:
- Chart structure setup with proper organization
- Template creation for all Kubernetes resources
- Value configuration for flexibility
- Security implementation with best practices
- Dependency management for external components

### Key Components
1. **Chart Structure**: Organized directory structure with proper files
2. **Template Templates**: Kubernetes resource templates (deployments, services, etc.)
3. **Value Configuration**: Flexible configuration through values.yaml
4. **Helper Functions**: Reusable templates and naming conventions
5. **Dependency Management**: External chart dependencies (PostgreSQL, etc.)

## Helm Chart Creation Implementation

### Chart Structure
- `Chart.yaml`: Chart metadata and dependencies
- `values.yaml`: Default configuration values
- `templates/`: Kubernetes resource templates
  - Deployments for application services
  - Services for internal communication
  - ConfigMaps for configuration
  - Secrets for sensitive data
  - Network Policies for security
  - Service Accounts for RBAC
  - Ingress for external access
- `_helpers.tpl`: Template helper functions
- `NOTES.txt`: Post-installation notes

### Template Development Process
- Create deployment templates with proper labels and selectors
- Implement service templates for internal communication
- Develop ConfigMap templates for application configuration
- Create Secret templates for sensitive data management
- Implement Network Policy templates for security
- Set up Service Account templates for RBAC

## Key Implementation Details

### Chart Metadata (Chart.yaml)
```
apiVersion: v2
name: application-name
description: A Helm chart for the application
type: application
version: 0.1.0
appVersion: "1.0.0"

dependencies:
  - name: postgresql
    version: "12.x.x"
    repository: "https://charts.bitnami.com/bitnami"
    condition: postgresql.enabled
```

### Value Configuration (values.yaml)
```
# Frontend configuration
frontend:
  replicaCount: 1
  image:
    repository: frontend-image
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 3000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

# Backend configuration
backend:
  replicaCount: 1
  image:
    repository: backend-image
    tag: latest
    pullPolicy: IfNotPresent
  service:
    type: ClusterIP
    port: 8000
  resources:
    limits:
      cpu: 500m
      memory: 512Mi
    requests:
      cpu: 100m
      memory: 128Mi

# PostgreSQL configuration
postgresql:
  enabled: true
  auth:
    postgresPassword: "postgres"
    database: "app_database"
  primary:
    persistence:
      enabled: true
      size: 8Gi
```

### Template Structure
- Use proper Helm template functions and conventions
- Implement consistent labeling strategy
- Follow security best practices in templates
- Use helper functions for reusable elements
- Implement proper conditional logic

## Security Considerations
- Pod Security Context configuration
- Network Policy implementation
- RBAC with minimal required permissions
- Secret management for sensitive data
- Resource limits to prevent abuse

## Environment Configuration

### Security Context Configuration
```
securityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001

podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1001
  fsGroup: 1001
```

### Resource Limits Configuration
```
resources:
  limits:
    cpu: 500m
    memory: 512Mi
  requests:
    cpu: 100m
    memory: 128Mi
```

## Helper Templates (_helpers.tpl)
```
{{- define "app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{- define "app.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- if contains $name .Release.Name }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}
{{- end }}

{{- define "app.labels" -}}
helm.sh/chart: {{ include "app.chart" . }}
{{ include "app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}
```

## Troubleshooting Tips

### Chart Validation Issues
**Symptoms:** Helm lint or install failures
**Solutions:**
- Validate template syntax with `helm lint`
- Check for proper indentation in YAML files
- Verify template function syntax
- Ensure all referenced values exist in values.yaml

**Symptoms:** Incorrect resource generation
**Solutions:**
- Use `helm template` to preview generated resources
- Check conditional logic in templates
- Verify helper function definitions
- Test with dry-run: `helm install --dry-run`

### Dependency Issues
**Symptoms:** Missing or incorrect dependencies
**Solutions:**
- Run `helm dependency update` to fetch dependencies
- Verify repository URLs in Chart.yaml
- Check dependency versions are available
- Ensure dependencies are properly configured

### Debugging Steps
1. Validate chart: `helm lint ./chart-directory`
2. Preview templates: `helm template test-release ./chart-directory`
3. Dry run installation: `helm install --dry-run test-release ./chart-directory`
4. Check generated resources for correctness
5. Verify all values are properly substituted

## Best Practices

### Template Best Practices
- Use helper functions for repeated elements
- Implement proper labeling strategy
- Follow security best practices
- Use conditional logic appropriately
- Implement proper error handling

### Value Configuration Best Practices
- Provide sensible defaults
- Use hierarchical structure for organization
- Document all configurable parameters
- Use consistent naming conventions
- Group related settings logically

## Future Improvements

### Advanced Features
- Custom resource definitions (CRDs)
- Helm hooks for lifecycle management
- Advanced conditionals and loops
- Chart testing with ct (Chart Testing)
- Automated chart publishing workflows

### Security Enhancements
- Pod Security Standards implementation
- Advanced Network Policy configurations
- Security context hardening
- Admission controller integration
- Vulnerability scanning integration

## Testing Checklist

### Chart Validation
- [ ] Helm lint passes without errors
- [ ] Template generation works correctly
- [ ] All resources render properly
- [ ] Values are properly substituted
- [ ] Conditional logic works as expected
- [ ] Dependencies are properly included
- [ ] Security configurations are applied
- [ ] Resource limits are set appropriately