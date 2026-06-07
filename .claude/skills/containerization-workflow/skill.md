# Containerization Workflow Skill

## Overview
This skill provides comprehensive guidance for containerizing applications using Docker with multi-stage builds and security best practices. It covers containerization for different technology stacks including Next.js, FastAPI, React, Express, and others.

## Implementation Approach

### Complete Containerization Workflow
The containerization process includes:
- Multi-stage build setup for optimized images
- Base image selection and security considerations
- Dependency management and layer optimization
- Security context configuration
- Environment variable handling
- Build optimization for size and security

### Key Components
1. **Multi-Stage Builds**: Optimized builds with separate build and runtime stages
2. **Base Image Selection**: Secure and appropriate base images
3. **Layer Optimization**: Efficient layer caching and organization
4. **Security Configuration**: Non-root users and minimal permissions
5. **Environment Management**: Proper environment variable handling

## Containerization Implementation

### Multi-Stage Build Process
- Separate build stage for compilation and dependency installation
- Runtime stage with minimal necessary components
- Efficient layer caching through proper ordering
- Clean separation of build and runtime dependencies
- Security-focused image construction

### Technology-Specific Containerization
- **Next.js Applications**: Optimized builds with standalone output
- **FastAPI Applications**: Lightweight Python base images with proper dependencies
- **React Applications**: Production builds with optimized static serving
- **Express Applications**: Node.js optimizations and dependency management

## Key Implementation Details

### Next.js Dockerfile Template
```
FROM node:20-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then yarn global add pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Build Next.js application
RUN npm run build

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV production

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT 3000
ENV HOSTNAME 0.0.0.0

CMD ["node", "server.js"]
```

### FastAPI Dockerfile Template
```
FROM python:3.11-slim AS base

# Install dependencies only when needed
FROM base AS deps
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from the deps stage
COPY --from=deps /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=deps /usr/local/bin /usr/local/bin

# Copy application source code
COPY . .

# Expose port for the application
EXPOSE 8000

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Security Configuration
- Use non-root users for running containers
- Implement minimal required permissions
- Use distroless or alpine base images when possible
- Regular security scanning of base images
- Minimize attack surface by removing unnecessary components

## Security Considerations
- Run containers as non-root users
- Use minimal base images (Alpine, distroless)
- Implement proper file permissions
- Limit container capabilities
- Use read-only root filesystem when possible
- Scan images for vulnerabilities

## Environment Configuration

### Multi-Stage Build Best Practices
```
# Stage 1: Dependencies
FROM node:18-alpine AS deps
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:18-alpine AS builder
WORKDIR /app
COPY . .
COPY --from=deps /app/node_modules ./node_modules
RUN npm run build

# Stage 3: Production
FROM node:18-alpine AS production
WORKDIR /app
COPY --from=builder /app/dist ./dist
COPY --from=deps --chown=node:node /app/node_modules ./node_modules
USER node
CMD ["node", "dist/index.js"]
```

### Environment Variables Handling
```
# Build-time arguments
ARG NODE_ENV=production
ENV NODE_ENV=$NODE_ENV

# Runtime environment variables
ENV PORT=3000
ENV HOSTNAME=0.0.0.0
```

## Troubleshooting Tips

### Build Issues
**Symptoms:** Build failures, missing dependencies
**Solutions:**
- Verify base image compatibility
- Check dependency installation order
- Ensure proper file permissions
- Validate multi-stage copy commands
- Check for architecture-specific dependencies

**Symptoms:** Large image sizes
**Solutions:**
- Implement multi-stage builds
- Optimize layer caching
- Remove unnecessary files
- Use .dockerignore appropriately
- Choose appropriate base images

### Runtime Issues
**Symptoms:** Container crashes, permission errors
**Solutions:**
- Verify non-root user configuration
- Check file permissions
- Validate entrypoint/command
- Ensure proper port exposure
- Verify environment variables

### Debugging Steps
1. Build with verbose output: `docker build --progress=plain`
2. Check intermediate layers: `docker history image:tag`
3. Run container interactively: `docker run -it image:tag /bin/sh`
4. Verify file permissions and ownership
5. Test with minimal configuration first

## Best Practices

### Dockerfile Best Practices
- Use specific base image tags
- Leverage layer caching with proper COPY ordering
- Use .dockerignore to exclude unnecessary files
- Implement multi-stage builds for optimization
- Use non-root users for security
- Minimize the number of layers
- Clean up package managers after installation

### Security Best Practices
- Regularly update base images
- Use minimal base images
- Implement read-only filesystems where possible
- Scan images for vulnerabilities
- Use signed images from trusted sources
- Limit container privileges and capabilities

## Future Improvements

### Advanced Features
- Docker BuildKit for improved build performance
- Squashed layers for smaller images
- Build caching strategies for CI/CD
- Multi-platform builds with buildx
- Image signing and verification

### Optimization Strategies
- Dependency layer caching
- Build context optimization
- Layer compression techniques
- Image vulnerability scanning
- Automated image updates

## Testing Checklist

### Build Verification
- [ ] Dockerfile builds successfully
- [ ] Multi-stage build works correctly
- [ ] Image size is optimized
- [ ] Dependencies are properly installed
- [ ] Security scan passes
- [ ] Non-root user configuration works
- [ ] Environment variables are set correctly
- [ ] Application starts without errors