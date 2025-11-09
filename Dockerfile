# Multi-stage build for XML to SQL Converter Web GUI

# Stage 1: Build frontend
FROM node:18-alpine AS frontend-builder
WORKDIR /app/web_frontend

# Copy package files
COPY web_frontend/package*.json ./
RUN npm install

# Copy frontend source and build
COPY web_frontend/ ./
RUN npm run build

# Stage 2: Python backend
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy Python project files
COPY pyproject.toml ./
COPY src/ ./src/

# Install Python dependencies
RUN pip install --no-cache-dir -e .

# Copy built frontend from builder stage
COPY --from=frontend-builder /app/web_frontend/dist ./web_frontend/dist

# Create directory for SQLite database (persistent volume)
RUN mkdir -p /app/data

# Expose port
EXPOSE 8000

# Set environment variables
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["uvicorn", "xml_to_sql.web.main:app", "--host", "0.0.0.0", "--port", "8000"]

