# Multi-stage build for optimized image
FROM node:18 AS frontend-builder

# Set working directory for frontend
WORKDIR /app/frontend

# Copy frontend files
COPY frontend/ .

# Install dependencies and build/export the Next.js app
RUN npm install
RUN npm run build
RUN npm run export

# Production-ready backend image
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    nginx \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js for runtime (if needed)
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs

# Set working directory
WORKDIR /app

# Copy backend requirements and install Python dependencies
COPY backend/requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy built frontend from the previous stage
COPY --from=frontend-builder /app/frontend/out /app/frontend/build

# Copy backend code
COPY backend/src/ /app/backend/src/
COPY backend/requirements.txt /app/backend/requirements.txt

# Configure nginx
RUN rm /etc/nginx/sites-enabled/default
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy supervisord configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directories
RUN mkdir -p /tmp && chmod 777 /tmp

# Expose port
EXPOSE 7860

# Start services
CMD ["supervisord", "-c", "/etc/supervisor/conf.d/supervisord.conf"]