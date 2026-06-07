# Kubernetes Security Skill

## Overview
This skill provides comprehensive guidance for implementing security best practices in Kubernetes deployments. It covers Network Policies, RBAC, Pod Security Standards, Secret management, and overall security hardening for Kubernetes applications.

## Implementation Approach

### Complete Kubernetes Security Implementation
The security implementation includes:
- Network Policy configuration for traffic control
- RBAC (Role-Based Access Control) setup
- Pod Security Standards enforcement
- Secret management for sensitive data
- Security Context configuration
- Admission controller integration
- Security monitoring and alerting

### Key Components
1. **Network Policies**: Traffic control between pods and namespaces
2. **RBAC**: Role-based access control for Kubernetes resources
3. **Pod Security Standards**: Security profiles for pod configurations
4. **Secret Management**: Secure handling of sensitive data
5. **Security Contexts**: Security configurations for pods and containers
6. **Admission Controllers**: Gatekeeper, OPA, or other security controllers

## Kubernetes Security Implementation

### Network Policy Implementation
- Ingress and Egress rule configuration
- Namespace isolation policies
- Pod-to-pod communication controls
- External traffic restrictions
- Multi-tier application security zones

### RBAC Configuration
- Role and ClusterRole creation
- RoleBinding and ClusterRoleBinding setup
- Service account permissions
- Least privilege principle implementation
- Permission audit and review processes

## Key Implementation Details

### Network Policy Template
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: application-network-policy
  namespace: application-namespace
spec:
  podSelector:
    matchLabels:
      app: application-name
  policyTypes:
    - Ingress
    - Egress
  ingress:
    # Allow inbound traffic from frontend to backend
    - from:
        - podSelector:
            matchLabels:
              app: frontend
      ports:
        - protocol: TCP
          port: 8000
    # Allow inbound traffic from same namespace
    - from:
        - namespaceSelector:
            matchLabels:
              name: application-namespace
      ports:
        - protocol: TCP
          port: 8000
  egress:
    # Allow outbound traffic to database
    - to:
        - podSelector:
            matchLabels:
              app: postgresql
      ports:
        - protocol: TCP
          port: 5432
    # Allow DNS resolution
    - to:
        - namespaceSelector:
            matchLabels:
              name: kube-system
      ports:
        - protocol: TCP
          port: 53
        - protocol: UDP
          port: 53
```

### RBAC Templates

#### Role Template
```
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  namespace: application-namespace
  name: pod-reader
rules:
- apiGroups: [""]
  resources: ["pods"]
  verbs: ["get", "watch", "list"]
```

#### RoleBinding Template
```
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: read-pods
  namespace: application-namespace
subjects:
- kind: User
  name: jane
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: pod-reader
  apiGroup: rbac.authorization.k8s.io
```

### Pod Security Standards Configuration
```
apiVersion: v1
kind: Namespace
metadata:
  name: application-namespace
  labels:
    pod-security.kubernetes.io/enforce: restricted
    pod-security.kubernetes.io/audit: restricted
    pod-security.kubernetes.io/warn: restricted
```

### Security Context Configuration
```
apiVersion: v1
kind: Pod
metadata:
  name: secured-pod
spec:
  securityContext:
    runAsNonRoot: true
    runAsUser: 1000
    runAsGroup: 3000
    fsGroup: 2000
  containers:
  - name: app-container
    image: my-app:1.0
    securityContext:
      allowPrivilegeEscalation: false
      readOnlyRootFilesystem: true
      runAsNonRoot: true
      runAsUser: 1000
      capabilities:
        drop:
        - ALL
```

### Secret Management Best Practices
- Use Kubernetes Secrets for sensitive data
- Implement external secret stores (HashiCorp Vault, AWS Secrets Manager)
- Rotate secrets regularly
- Limit secret access to necessary pods only
- Encrypt secrets at rest

## Security Considerations
- Implement defense in depth
- Follow the principle of least privilege
- Regular security audits and reviews
- Monitor security events and anomalies
- Keep Kubernetes and components updated
- Use trusted base images
- Implement runtime security monitoring

## Environment Configuration

### Security Context Best Practices
```
# Pod Security Context
podSecurityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 2000
  seccompProfile:
    type: RuntimeDefault

# Container Security Context
securityContext:
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
    - ALL
    add:
    - NET_BIND_SERVICE
```

### Admission Controller Configuration
```
# OPA/Gatekeeper Constraint Template
apiVersion: templates.gatekeeper.sh/v1beta1
kind: ConstraintTemplate
metadata:
  name: k8srequiredlabels
spec:
  crd:
    spec:
      names:
        kind: K8sRequiredLabels
  targets:
    - target: admission.k8s.gatekeeper.sh
      rego: |
        package k8srequiredlabels
        violation[{"msg": msg, "details": {"missing_labels": missing}}] {
          provided := {label | input.review.object.metadata.labels[label]}
          required := {label | label := input.parameters.labels[_]}
          missing := required - provided
          count(missing) > 0
          msg := sprintf("Missing required labels: %v", [missing])
        }
```

## Deployment Integration

### Helm Chart Security Integration
- Create NetworkPolicy templates
- Set up RBAC configuration in templates
- Configure security contexts in deployment templates
- Implement Pod Security Standards in namespace templates
- Add security scan configurations

### Security Monitoring Setup
```
# Security monitoring DaemonSet
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: security-agent
  namespace: kube-system
spec:
  selector:
    matchLabels:
      name: security-agent
  template:
    metadata:
      labels:
        name: security-agent
    spec:
      hostPID: true
      hostNetwork: true
      containers:
      - name: agent
        image: security-agent:latest
        securityContext:
          privileged: true
        volumeMounts:
        - name: root
          mountPath: /host
          readOnly: true
      volumes:
      - name: root
        hostPath:
          path: /
```

## Troubleshooting Tips

### Network Policy Issues
**Symptoms:** Pods cannot communicate, services unreachable
**Solutions:**
- Verify label selectors match pod labels
- Check policy ordering and precedence
- Validate ingress/egress rules
- Test connectivity with temporary policy
- Review namespace selectors

**Symptoms:** Unexpected traffic blocking
**Solutions:**
- Check default deny behavior
- Verify DNS resolution is allowed
- Test with minimal policy first
- Review egress rules for external access

### RBAC Issues
**Symptoms:** Permission denied errors
**Solutions:**
- Verify Role/ClusterRole exists
- Check RoleBinding/ClusterRoleBinding
- Validate subject mapping
- Confirm namespace context
- Test with broader permissions temporarily

### Pod Security Issues
**Symptoms:** Pods fail to start due to security policies
**Solutions:**
- Check Pod Security Standards level
- Verify security context configurations
- Review admission controller policies
- Test with restricted profile
- Validate container configurations

### Debugging Steps
1. Check NetworkPolicy configurations: `kubectl get networkpolicy -A`
2. Verify RBAC permissions: `kubectl auth can-i --list`
3. Review Pod Security Standards: `kubectl get ns --show-labels`
4. Examine security context: `kubectl describe pod <pod-name>`
5. Check admission controller logs
6. Review Kubernetes events: `kubectl get events -A`

## Best Practices

### Network Security Best Practices
- Default deny approach for Network Policies
- Principle of least privilege
- Namespace segregation for different trust levels
- Regular review of network rules
- Use CIDR blocks for external access
- Monitor network traffic patterns

### RBAC Best Practices
- Principle of least privilege
- Regular permission audits
- Use dedicated service accounts
- Role aggregation for complex permissions
- Group-based role assignments
- Periodic access reviews

### Pod Security Best Practices
- Run containers as non-root users
- Drop unnecessary capabilities
- Use read-only root filesystems
- Implement runtime security monitoring
- Regular security scanning
- Keep base images updated

## Future Improvements

### Advanced Security Features
- Service mesh security (Istio, Linkerd)
- Runtime security monitoring (Falco, Sysdig)
- Advanced admission controllers (Kyverno, OPA)
- Network encryption (Cilium, Calico)
- Zero-trust network architecture
- Advanced threat detection

### Compliance and Governance
- Security policy enforcement
- Audit logging and monitoring
- Compliance reporting
- Automated security remediation
- Security scorecards
- Regulatory compliance tools

## Testing Checklist

### Security Verification
- [ ] Network Policies are correctly implemented
- [ ] RBAC permissions are properly configured
- [ ] Pod Security Standards are enforced
- [ ] Security contexts are applied correctly
- [ ] Secrets are stored securely
- [ ] Admission controllers are functioning
- [ ] Security scanning passes
- [ ] Penetration testing results are acceptable