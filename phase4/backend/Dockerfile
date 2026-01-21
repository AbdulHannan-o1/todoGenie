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

# Final stage setup
FROM base AS runtime
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

# Create non-root user with UID 1001 to match security context
RUN groupadd -g 1001 appgroup && \
    adduser --uid 1001 --gid 1001 --disabled-password --gecos '' appuser

# Change ownership of files to the app user
RUN chown -R 1001:1001 /app

# Ensure the startup scripts have proper permissions
RUN chmod +x /app/start_server.py && chmod +x /app/start_backend.py

# Switch to the non-root user
USER 1001

# Expose port 8000 for the backend
EXPOSE 8000

# Set working directory to /app and run the application using the proper startup script
WORKDIR /app
CMD ["python", "/app/start_backend.py"]