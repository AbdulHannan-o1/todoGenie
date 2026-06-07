# Phase 4: Kubernetes Deployment - Troubleshooting Guide

## Overview
This document captures the issues encountered and solutions implemented during the Kubernetes deployment of the TodoGenie application, particularly focusing on Docker containerization challenges.

## Issue 1: Cypress Configuration TypeScript Error

### Problem
During the Docker build process, the Next.js build failed with the following error:
```
./cypress.config.ts:6:21
Type error: Parameter 'on' implicitly has an 'any' type.
```

### Root Cause
The Next.js 16 build process with the new bundler was attempting to compile the `cypress.config.ts` file during the build process, even though it's a test configuration file that should be excluded.

### Solution
1. **Fixed the TypeScript syntax**: Changed the cypress.config.ts file to use proper ES module syntax and removed the type annotations that were causing the issue
2. **Added .dockerignore**: Created a .dockerignore file to exclude Cypress-related files from the Docker build context
3. **Updated file**: Changed from CommonJS to ES module syntax

### Files Modified
- `cypress.config.ts` - Fixed syntax and converted to ES modules
- Created `.dockerignore` - Added Cypress files to exclusion list

## Issue 2: Next.js Page Params TypeScript Error

### Problem
The Next.js build failed with the following error:
```
./src/app/tasks/[id]/page.tsx:21:11
Type error: Property 'id' does not exist on type 'unknown'.
```

### Root Cause
Incorrect syntax in the page component where `React.use(params)` was being used instead of properly destructuring the `params` prop.

### Solution
Fixed the syntax in `/src/app/tasks/[id]/page.tsx` line 21:
- **Before**: `const { id } = React.use(params);`
- **After**: `const { id } = params;`

### Explanation
In Next.js App Router, the `params` prop is passed directly to the page component and doesn't need to be accessed through `React.use()`. The component should receive `{ params }` as props and then destructure the required parameters directly.

## Issue 3: Missing Standalone Output Directory

### Problem
Docker build failed with:
```
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
ERROR: "/app/.next/standalone": not found
```

### Root Cause
The Next.js build was not generating the standalone output directory because the `output: 'standalone'` configuration was not set in the Next.js configuration.

### Solution
Added `output: 'standalone'` to the next.config.ts file to enable the standalone output mode, which generates the required directory structure for the Docker image.

## Deployment Workflow

### Successful Docker Build Process
1. Create proper .dockerignore to exclude test files
2. Fix TypeScript issues in application code
3. Configure Next.js for standalone output
4. Build Docker images with multi-stage process
5. Load images into Minikube cluster
6. Deploy using Helm charts

### Key Configuration Changes
1. **Dockerfile**: Multi-stage build with proper layer optimization
2. **next.config.ts**: Added `output: 'standalone'` for proper output structure
3. **.dockerignore**: Excluded Cypress and other unnecessary files
4. **TypeScript fixes**: Corrected parameter destructuring in page components

## Kubernetes Deployment Structure

### Helm Chart Components
- **Backend Deployment**: FastAPI application with MCP tools
- **Frontend Deployment**: Next.js application with AI chat interface
- **PostgreSQL**: Database with persistent storage
- **Services**: Internal communication between components
- **Network Policies**: Security isolation
- **ConfigMaps/Secrets**: Configuration and sensitive data management

## Best Practices Identified

### Docker Build Optimization
- Use multi-stage builds to reduce image size
- Implement proper .dockerignore for build context
- Configure Next.js for standalone output
- Optimize layer caching with proper COPY ordering

### TypeScript/Next.js Development
- Proper parameter destructuring in App Router
- Use standalone output mode for containerization
- Exclude test files from build process
- Maintain type safety across all components

### Kubernetes Deployment
- Use Helm charts for deployment management
- Implement security best practices (Network Policies, RBAC)
- Use persistent volumes for database storage
- Configure proper health checks and resource limits

## Lessons Learned

1. **Test files can interfere with builds**: Cypress configuration files were being processed during Next.js builds
2. **Proper configuration is crucial**: Missing `output: 'standalone'` caused Docker build failures
3. **TypeScript strictness helps**: TypeScript caught errors before runtime
4. **Docker context matters**: Proper .dockerignore reduces build times and prevents issues
5. **Next.js App Router patterns**: Understanding the correct parameter handling is important

## Verification Steps

After implementing the fixes:
1. Docker images build successfully
2. Next.js application compiles without errors
3. TypeScript type checking passes
4. Standalone output directory is generated
5. Kubernetes deployment works with Helm charts