# Deployment Guide - Face Recognition System

## Prerequisites

### System Requirements
- Python 3.9+
- Node.js 18+
- Git with Git LFS
- 8GB+ RAM
- 10GB+ free disk space

### Required Accounts
- GitHub account
- (Optional) Cloud hosting account (Render, Railway, AWS, etc.)

---

## Step 1: Download Large Model Files

Since model files are stored with Git LFS, you need to download them separately:

### Download Links:
1. **AdaFace IR-101** (~250MB)
   - Download from: https://github.com/mk-minchul/AdaFace
   - Place in: `models/adaface_ir101_webface12m.ckpt`

2. **GFPGAN v1.4** (~350MB)
   - Download from: https://github.com/TencentARC/GFPGAN/releases
   - Place in: `models/GFPGANv1.4.pth`

3. **Real-ESRGAN** (~65MB)
   - Download from: https://github.com/xinntao/Real-ESRGAN/releases
   - Place in: `models/RealESRGAN_x4plus.pth`

4. **GFPGAN Additional Weights**
   - detection_Resnet50_Final.pth (~110MB)
   - parsing_parsenet.pth (~85MB)
   - Place in: `gfpgan/weights/`

### Model Directory Structure:
```
models/
├── adaface_ir101_webface12m.ckpt
├── GFPGANv1.4.pth
├── RealESRGAN_x4plus.pth
└── .gitkeep

gfpgan/weights/
├── detection_Resnet50_Final.pth
├── parsing_parsenet.pth
└── .gitkeep
```

---

## Step 2: Local Setup

### Clone Repository
```bash
git clone https://github.com/dheerajreddy71/Student-identification-system.git
cd Student-identification-system
```

### Install Git LFS (if not already installed)
```bash
# Windows (using Chocolatey)
choco install git-lfs

# Or download from: https://git-lfs.github.com/
git lfs install
```

### Pull LFS files
```bash
git lfs pull
```

### Backend Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python backend/init_db.py

# Create admin user
python scripts/create_admin.py
```

### Frontend Setup
```bash
cd frontend
npm install
cd ..
```

---

## Step 3: Environment Configuration

Create `.env` file in project root:

```env
# Database
DATABASE_URL=sqlite:///./students.db

# JWT Secret (generate with: openssl rand -hex 32)
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Paths
MODEL_PATH=./models
PHOTOS_PATH=./photos
TRAINSET_PATH=./trainset

# CORS (adjust for production)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com
```

Frontend `.env.local` in `frontend/` directory:

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Step 4: Register Students

Place student photos in this structure:
```
trainset/
├── CSE/
│   ├── CSE001/
│   │   ├── photo1.jpg
│   │   ├── photo2.jpg
│   │   └── photo3.jpg
│   └── CSE002/
├── ECE/
└── MECH/
```

Run registration:
```bash
python scripts/register_students.py
```

---

## Step 5: Run Locally

### Terminal 1 - Backend
```bash
cd "c:\Users\byred\Desktop\Student Identification System"
venv\Scripts\activate
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Access at: `http://localhost:3000`

---

## Step 6: Deploy to Cloud

### Option A: Render.com (Recommended for beginners)

1. **Create Render Account**: https://render.com

2. **Deploy Backend**:
   - Create New Web Service
   - Connect GitHub repository
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn backend.main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.9+
   - Add environment variables from `.env`

3. **Deploy Frontend**:
   - Create New Static Site
   - Build Command: `cd frontend && npm install && npm run build`
   - Publish Directory: `frontend/out`
   - Add `NEXT_PUBLIC_API_URL` pointing to backend URL

4. **Upload Models**:
   - Use Render's persistent disk or S3
   - Update `MODEL_PATH` environment variable

### Option B: Railway.app

1. **Create Railway Account**: https://railway.app

2. **Deploy Backend**:
   ```bash
   railway login
   railway init
   railway up
   ```

3. **Add PostgreSQL** (recommended for production):
   ```bash
   railway add postgresql
   ```

4. **Configure Environment Variables** in Railway dashboard

### Option C: AWS/Azure/GCP

See detailed cloud deployment guides in `docs/` folder.

---

## Step 7: Production Checklist

### Security
- [ ] Change default SECRET_KEY
- [ ] Enable HTTPS/SSL
- [ ] Restrict CORS origins
- [ ] Use strong admin passwords
- [ ] Enable rate limiting
- [ ] Add API authentication

### Database
- [ ] Migrate from SQLite to PostgreSQL for production
- [ ] Setup database backups
- [ ] Add database connection pooling

### Performance
- [ ] Enable response caching
- [ ] Add CDN for static files
- [ ] Optimize model loading (lazy loading)
- [ ] Consider GPU deployment for speed

### Monitoring
- [ ] Add error logging (Sentry, LogRocket)
- [ ] Setup uptime monitoring
- [ ] Configure alerts
- [ ] Add analytics

### Data
- [ ] Backup FAISS index regularly
- [ ] Backup student photos
- [ ] Document data retention policy
- [ ] Ensure GDPR compliance

---

## Troubleshooting

### Models Not Loading
```bash
# Check if models exist
ls models/
ls gfpgan/weights/

# Re-download if missing (see Step 1)
```

### Database Errors
```bash
# Reset database
rm students.db
python backend/init_db.py
```

### FAISS Index Errors
```bash
# Rebuild FAISS index
rm data/faiss_index.bin data/faiss_metadata.json
python scripts/register_students.py
```

### Port Already in Use
```bash
# Windows - Kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9
```

### Memory Errors
- Reduce batch size in registration
- Enable lazy model loading
- Use GPU if available
- Increase system RAM

---

## Model Download Automation Script

Create `download_models.py`:

```python
import requests
import os
from tqdm import tqdm

MODELS = {
    "adaface": {
        "url": "https://github.com/mk-minchul/AdaFace/releases/download/v1.0/adaface_ir101_webface12m.ckpt",
        "path": "models/adaface_ir101_webface12m.ckpt"
    },
    "gfpgan": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
        "path": "models/GFPGANv1.4.pth"
    },
    "realesrgan": {
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "path": "models/RealESRGAN_x4plus.pth"
    }
}

def download_file(url, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    
    print(f"Downloading {os.path.basename(path)}...")
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    with open(path, 'wb') as f, tqdm(
        total=total_size, unit='B', unit_scale=True
    ) as pbar:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            pbar.update(len(chunk))
    
    print(f"✓ Downloaded to {path}")

if __name__ == "__main__":
    for name, info in MODELS.items():
        if not os.path.exists(info["path"]):
            download_file(info["url"], info["path"])
        else:
            print(f"✓ {name} already exists")
```

Run: `python download_models.py`

---

## Support

For issues, please check:
1. GitHub Issues: https://github.com/dheerajreddy71/Student-identification-system/issues
2. Documentation: README.md
3. Project Report: FINAL_YEAR_PROJECT_REPORT.md

---

## License

This project is for educational purposes. Model weights are subject to their respective licenses.

**AdaFace**: MIT License
**GFPGAN**: Apache 2.0
**Real-ESRGAN**: BSD 3-Clause
