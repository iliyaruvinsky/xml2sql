# Web GUI Deployment Guide

This guide explains how to deploy the XML to SQL Converter web interface for both testing (standalone) and production (cloud) environments.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Standalone Server (Testing)](#standalone-server-testing)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment](#cloud-deployment)
5. [Troubleshooting](#troubleshooting)

## Prerequisites

### For Standalone Server

- Python 3.11 or higher
- Node.js 18+ and npm (for building frontend)
- pip (Python package manager)

### For Docker Deployment

- Docker 20.10+
- Docker Compose 2.0+ (optional, for docker-compose)

### For Cloud Deployment

- Cloud provider account (Heroku, AWS, Azure, GCP, etc.)
- Docker support (recommended) or platform-specific requirements

## Standalone Server (Testing)

The standalone server is ideal for local testing and development.

### Step 1: Install Dependencies

```bash
# Install Python dependencies
pip install -e .

# Navigate to frontend directory
cd web_frontend

# Install Node.js dependencies
npm install
```

### Step 2: Build Frontend

```bash
# From web_frontend directory
npm run build
```

This creates the `dist/` directory with production-ready frontend files.

### Step 3: Run the Server

```bash
# From project root
python run_server.py
```

Or using uvicorn directly:

```bash
uvicorn xml_to_sql.web.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 4: Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

The web interface will be available with:
- Single file conversion
- Batch conversion
- Configuration options
- Conversion history
- SQL preview and download

### Development Mode (Hot Reload)

For development with automatic reloading:

**Terminal 1 - Backend:**
```bash
uvicorn xml_to_sql.web.main:app --host 0.0.0.0 --port 8000 --reload
```

**Terminal 2 - Frontend:**
```bash
cd web_frontend
npm run dev
```

Access the frontend at `http://localhost:5173` (it will proxy API requests to the backend).

## Docker Deployment

Docker provides a consistent environment for both testing and production.

### Step 1: Build Docker Image

```bash
docker build -t xml-to-sql:latest .
```

### Step 2: Run Container

**Basic run:**
```bash
docker run -d \
  --name xml-to-sql \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  xml-to-sql:latest
```

**Using docker-compose (recommended):**
```bash
docker-compose up -d
```

### Step 3: Access the Application

Open your browser and navigate to:

```
http://localhost:8000
```

### Data Persistence

The SQLite database (`conversions.db`) is stored in the `./data` directory, which is mounted as a volume. This ensures conversion history persists across container restarts.

### Viewing Logs

```bash
# Docker run
docker logs -f xml-to-sql

# Docker Compose
docker-compose logs -f
```

### Stopping the Container

```bash
# Docker run
docker stop xml-to-sql
docker rm xml-to-sql

# Docker Compose
docker-compose down
```

## Cloud Deployment

### Option 1: Heroku

**Prerequisites:**
- Heroku CLI installed
- Heroku account

**Steps:**

1. Create `Procfile` in project root:
```
web: uvicorn xml_to_sql.web.main:app --host 0.0.0.0 --port $PORT
```

2. Create `runtime.txt`:
```
python-3.11.0
```

3. Login to Heroku:
```bash
heroku login
```

4. Create app:
```bash
heroku create your-app-name
```

5. Deploy:
```bash
git push heroku main
```

**Note:** Heroku uses ephemeral filesystem, so SQLite database will reset on each restart. Consider using PostgreSQL addon for production.

### Option 2: AWS (ECS/Fargate)

1. Build and push Docker image to ECR:
```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com
docker build -t xml-to-sql .
docker tag xml-to-sql:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/xml-to-sql:latest
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/xml-to-sql:latest
```

2. Create ECS task definition and service
3. Configure load balancer and security groups
4. Use RDS or EFS for persistent storage

### Option 3: Azure Container Instances

```bash
# Build and push to Azure Container Registry
az acr build --registry <registry-name> --image xml-to-sql:latest .

# Deploy container instance
az container create \
  --resource-group <resource-group> \
  --name xml-to-sql \
  --image <registry-name>.azurecr.io/xml-to-sql:latest \
  --dns-name-label <dns-label> \
  --ports 8000
```

### Option 4: Google Cloud Run

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/xml-to-sql

# Deploy to Cloud Run
gcloud run deploy xml-to-sql \
  --image gcr.io/<project-id>/xml-to-sql \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

## Configuration

### Environment Variables

You can configure the application using environment variables:

- `DATABASE_PATH`: Path to SQLite database file (default: `conversions.db` in project root)
- `CORS_ORIGINS`: Comma-separated list of allowed CORS origins (default: `*` for development)
- `MAX_UPLOAD_SIZE`: Maximum file upload size in bytes (default: 10MB)

### Database Location

By default, the SQLite database is created at:
- Standalone: `conversions.db` in project root
- Docker: `/app/data/conversions.db` (mounted volume)

To change the database location, modify `src/xml_to_sql/web/database/db.py`:

```python
DB_PATH = Path(os.getenv("DATABASE_PATH", "conversions.db"))
```

## Troubleshooting

### Frontend Not Loading

**Problem:** Blank page or 404 errors

**Solutions:**
1. Ensure frontend is built: `cd web_frontend && npm run build`
2. Check that `web_frontend/dist` directory exists
3. Verify FastAPI is serving static files correctly
4. Check browser console for errors

### Database Errors

**Problem:** SQLite database errors

**Solutions:**
1. Ensure database directory is writable
2. Check disk space
3. Verify file permissions (Docker: check volume mount permissions)
4. Delete `conversions.db` to reset (will lose history)

### Port Already in Use

**Problem:** `Address already in use` error

**Solutions:**
1. Change port in `run_server.py` or docker-compose.yml
2. Kill process using port 8000:
   ```bash
   # Linux/Mac
   lsof -ti:8000 | xargs kill
   
   # Windows
   netstat -ano | findstr :8000
   taskkill /PID <PID> /F
   ```

### CORS Errors

**Problem:** CORS errors in browser console

**Solutions:**
1. For production, update CORS origins in `src/xml_to_sql/web/main.py`:
   ```python
   allow_origins=["https://yourdomain.com"]
   ```
2. For development, ensure frontend dev server proxy is configured correctly

### File Upload Fails

**Problem:** File upload returns 400 or 500 error

**Solutions:**
1. Check file is valid XML
2. Verify file size is within limits
3. Check server logs for detailed error messages
4. Ensure `python-multipart` is installed

### Conversion Errors

**Problem:** XML conversion fails

**Solutions:**
1. Verify XML file is a valid SAP HANA calculation view XML
2. Check server logs for parsing errors
3. Ensure all required dependencies are installed
4. Test with sample XML files from `Source (XML Files)/` directory

## Security Considerations

### Production Deployment

1. **CORS Configuration:** Restrict CORS origins to your domain
2. **File Size Limits:** Set appropriate `MAX_UPLOAD_SIZE`
3. **HTTPS:** Always use HTTPS in production
4. **Authentication:** Consider adding authentication for production use
5. **Database:** For production, consider PostgreSQL instead of SQLite
6. **Rate Limiting:** Implement rate limiting for API endpoints

### Example Production CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["*"],
)
```

## Next Steps

After deployment:

1. Test with sample XML files
2. Verify conversion history is working
3. Test batch conversion
4. Check download functionality
5. Monitor server logs for errors

## Support

For issues or questions:
- Check the main [README.md](README.md)
- Review [DEVELOPER_GUIDE.md](DEVELOPER_GUIDE.md)
- Check server logs for detailed error messages

