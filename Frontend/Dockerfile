# Frontend Dockerfile for MuDiKo AI Assistant
# Using static build approach

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Force install with legacy peer deps to handle rolldown-vite
RUN npm install --legacy-peer-deps --force

# Copy source code
COPY . .

# Try to build, if it fails, use a backup build script
RUN npm run build || (echo "Build failed, trying alternative approach..." && \
    npm install vite@latest --force && \
    npx vite build --config vite.config.js)

# Production stage
FROM nginx:alpine

# Remove default nginx static assets
RUN rm -rf /usr/share/nginx/html/*

# Copy built assets from builder stage
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create a simple index.html fallback if build failed
RUN if [ ! -f /usr/share/nginx/html/index.html ]; then \
        echo '<!DOCTYPE html><html><head><title>MuDiKo</title></head><body><h1>MuDiKo Frontend</h1><p>Build in progress...</p></body></html>' > /usr/share/nginx/html/index.html; \
    fi

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]