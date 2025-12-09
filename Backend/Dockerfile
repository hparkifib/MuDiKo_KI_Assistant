# Backend Dockerfile for MuDiKo AI Assistant
FROM python:3.11-slim

# Install system dependencies for audio processing and health checks
RUN apt-get update && apt-get install -y \
    libsndfile1 \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set working directory to parent of app
WORKDIR /workspace

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code - kopiert Backend/app nach /workspace/app
COPY app/ ./app/

# Create uploads directory with proper permissions
RUN mkdir -p app/Uploads && chmod 755 app/Uploads

# Expose port
EXPOSE 5000

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV FLASK_ENV=production
ENV PYTHONPATH=/workspace

# Run the application
CMD ["python", "-m", "app.main"]
