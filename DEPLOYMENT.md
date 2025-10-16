# Deployment Guide

## 🚀 Deployment Options

This guide covers multiple deployment strategies for the Student Identification System.

## Table of Contents
1. [GitHub Setup](#github-setup)
2. [Local Production Deployment](#local-production-deployment)
3. [Docker Deployment](#docker-deployment)
4. [Cloud Deployment (AWS/Azure/GCP)](#cloud-deployment)
5. [Environment Configuration](#environment-configuration)

---

## 1. GitHub Setup

### Prerequisites
- Git installed on your system
- GitHub account created
- Repository created on GitHub

### Step 1: Initialize Git Repository

```powershell
cd "C:\Users\byred\Desktop\Student Identification System"

# Initialize git (if not already initialized)
git init

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: AI-Powered Student Identification System with GFPGAN + AdaFace + FAISS"
```

### Step 2: Connect to GitHub

```powershell
# Add remote repository (replace with your GitHub repo URL)
git remote add origin https://github.com/YOUR_USERNAME/student-identification-system.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 3: Large Files Management

**Important**: Model files are too large for GitHub (>100MB). Users need to download them separately.

The `.gitignore` already excludes:
- `models/*.ckpt` - AdaFace checkpoint (~365 MB)
- `models/*.pth` - GFPGAN models (~297 MB)
- `trainset/` - Training images
- `data/faiss_index.bin` - FAISS index
- `*.db` - SQLite database

Create a `MANUAL_DOWNLOAD.md` with download links (already exists in your project).

---

## 2. Local Production Deployment

### Step 1: Environment Setup

Create production `.env` file:

```bash
# Backend Configuration
DATABASE_URL=sqlite:///./student_identification.db
SECRET_KEY=your-super-secret-production-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Model Paths
GFPGAN_MODEL_PATH=./models/GFPGANv1.4.pth
REAL_ESRGAN_MODEL_PATH=./models/RealESRGAN_x4plus.pth
ADAFACE_MODEL_PATH=./models/adaface_ir101_webface12m.ckpt

# Performance
DEVICE=cpu
EMBEDDING_DIMENSION=512
SIMILARITY_THRESHOLD=0.35

# Frontend
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Step 2: Backend Production Server

```powershell
# Install production server
pip install gunicorn

# Start with gunicorn (Linux/Mac)
gunicorn backend.main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# Windows: Use uvicorn with workers
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Step 3: Frontend Production Build

```powershell
cd frontend

# Install dependencies
npm install

# Create production build
npm run build

# Start production server
npm start
```

### Step 4: Reverse Proxy (Nginx - Optional)

```nginx
# /etc/nginx/sites-available/student-identification
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header Host $host;
    }
}
```

---

## 3. Docker Deployment

### Step 1: Build Docker Images

```powershell
# Build backend
docker build -f Dockerfile.backend -t student-id-backend .

# Build frontend
docker build -f Dockerfile.frontend -t student-id-frontend .
```

### Step 2: Run with Docker Compose

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Docker Compose Configuration (docker-compose.yml)

```yaml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    volumes:
      - ./models:/app/models
      - ./data:/app/data
      - ./trainset:/app/trainset
    environment:
      - DATABASE_URL=sqlite:///./data/student_identification.db
      - SECRET_KEY=${SECRET_KEY}
    restart: unless-stopped

  frontend:
    build:
      context: ./frontend
      dockerfile: ../Dockerfile.frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://localhost:8000
    depends_on:
      - backend
    restart: unless-stopped
```

---

## 4. Cloud Deployment

### AWS Deployment (EC2 + S3)

#### Step 1: Launch EC2 Instance
- Instance Type: t3.xlarge (4 vCPU, 16GB RAM)
- OS: Ubuntu 22.04 LTS
- Storage: 50GB SSD
- Security Groups: Open ports 80, 443, 8000, 3000

#### Step 2: Setup on EC2

```bash
# SSH into instance
ssh -i your-key.pem ubuntu@your-ec2-ip

# Install dependencies
sudo apt update
sudo apt install python3.10 python3-pip nodejs npm nginx -y

# Clone repository
git clone https://github.com/YOUR_USERNAME/student-identification-system.git
cd student-identification-system

# Setup Python environment
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Download models (see MANUAL_DOWNLOAD.md)
python scripts/download_models.py

# Setup frontend
cd frontend
npm install
npm run build

# Configure Nginx
sudo cp deployment/nginx.conf /etc/nginx/sites-available/student-id
sudo ln -s /etc/nginx/sites-available/student-id /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

#### Step 3: S3 for Model Storage (Optional)

```bash
# Upload models to S3
aws s3 cp models/ s3://your-bucket/models/ --recursive

# Download on server
aws s3 sync s3://your-bucket/models/ ./models/
```

### Azure Deployment

Use Azure App Service or Azure Container Instances:

```bash
# Login to Azure
az login

# Create resource group
az group create --name student-id-rg --location eastus

# Deploy container
az container create \
  --resource-group student-id-rg \
  --name student-id-backend \
  --image student-id-backend:latest \
  --cpu 4 --memory 16 \
  --ports 8000
```

### Google Cloud Platform (GCP)

```bash
# Build and push to GCR
gcloud builds submit --tag gcr.io/YOUR_PROJECT/student-id-backend

# Deploy to Cloud Run
gcloud run deploy student-id-backend \
  --image gcr.io/YOUR_PROJECT/student-id-backend \
  --platform managed \
  --region us-central1 \
  --memory 16Gi \
  --cpu 4
```

---

## 5. Environment Configuration

### Production Environment Variables

Create `.env.production`:

```bash
# Security
SECRET_KEY=generate-strong-random-key-here
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Database
DATABASE_URL=postgresql://user:password@localhost/student_id
# Or SQLite for smaller deployments
# DATABASE_URL=sqlite:///./student_identification.db

# Models (local or cloud storage)
GFPGAN_MODEL_PATH=/app/models/GFPGANv1.4.pth
REAL_ESRGAN_MODEL_PATH=/app/models/RealESRGAN_x4plus.pth
ADAFACE_MODEL_PATH=/app/models/adaface_ir101_webface12m.ckpt

# Performance
DEVICE=cuda  # or 'cpu' if no GPU
WORKERS=4

# Frontend
NEXT_PUBLIC_API_URL=https://api.your-domain.com
```

### Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Use HTTPS (SSL certificate)
- [ ] Enable CORS only for trusted domains
- [ ] Set strong database passwords
- [ ] Regular security updates
- [ ] Implement rate limiting
- [ ] Enable logging and monitoring
- [ ] Backup database regularly

---

## 6. Performance Optimization

### Backend Optimization

```python
# backend/config.py - Production settings
class Settings(BaseSettings):
    # Use GPU if available
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    
    # Optimize batch processing
    batch_size: int = 32
    
    # Enable model caching
    cache_embeddings: bool = True
    
    # Logging
    log_level: str = "INFO"
```

### Frontend Optimization

```javascript
// frontend/next.config.js
module.exports = {
  compress: true,
  images: {
    domains: ['localhost', 'your-domain.com'],
  },
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  }
}
```

---

## 7. Monitoring & Maintenance

### Health Check Endpoints

```python
# Backend health check
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "models_loaded": True,
        "database_connected": True
    }
```

### Logging Setup

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### Backup Strategy

```bash
# Daily database backup
0 2 * * * /usr/bin/sqlite3 /app/student_identification.db ".backup '/backup/student_id_$(date +\%Y\%m\%d).db'"

# Weekly model backup
0 3 * * 0 tar -czf /backup/models_$(date +\%Y\%m\%d).tar.gz /app/models/
```

---

## 8. Troubleshooting

### Common Issues

**Issue**: Out of memory errors
**Solution**: 
- Reduce batch size
- Use CPU instead of GPU for smaller deployments
- Increase server RAM

**Issue**: Slow identification
**Solution**:
- Use GPU (10x faster)
- Enable embedding caching
- Optimize FAISS index

**Issue**: Model download fails
**Solution**:
- Download models manually from provided links
- Use alternative mirror sites
- Contact repository maintainer

---

## 9. Post-Deployment Checklist

- [ ] All services running
- [ ] Health check endpoints responding
- [ ] SSL certificate installed
- [ ] Firewall configured
- [ ] Backups scheduled
- [ ] Monitoring enabled
- [ ] Documentation updated
- [ ] Team trained on system
- [ ] Maintenance plan established

---

## Support

For deployment issues or questions:
- GitHub Issues: [Create an issue](https://github.com/YOUR_USERNAME/student-identification-system/issues)
- Email: your-email@example.com
- Documentation: See [SETUP_GUIDE.md](SETUP_GUIDE.md)

---

**Last Updated**: October 2025
