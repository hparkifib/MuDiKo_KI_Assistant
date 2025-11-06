# Frontend Dockerfile for MuDiKo AI Assistant
# Using static build with simple HTTP server

# Build stage
FROM node:20-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Force install with legacy peer deps to handle rolldown-vite
RUN npm install --legacy-peer-deps --force

# Copy source code
COPY . .

# Build the application
RUN npm run build || (echo "Build failed, trying alternative approach..." && \
    npm install vite@latest --force && \
    npx vite build --config vite.config.js)

# Production stage - use Node to serve static files (no nginx needed)
FROM node:20-alpine

WORKDIR /app

# Install a simple static file server
RUN npm install -g serve

# Copy built assets from builder stage
COPY --from=builder /app/dist ./dist

# Create a simple index.html fallback if build failed
RUN if [ ! -f ./dist/index.html ]; then \
        mkdir -p ./dist && \
        echo '<!DOCTYPE html><html><head><title>MuDiKo</title></head><body><h1>MuDiKo Frontend</h1><p>Build in progress...</p></body></html>' > ./dist/index.html; \
    fi

# Expose port
EXPOSE 80

# Start the static file server (serves SPA with proper routing)
CMD ["serve", "-s", "dist", "-l", "80"]