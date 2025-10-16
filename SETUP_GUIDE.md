# Complete Setup Guide - Student Identification System

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher (for frontend)
- 8GB RAM minimum (16GB recommended)
- GPU with CUDA support (optional, for faster processing)
- Windows/Linux/macOS

## 🚀 Quick Start Guide

### Step 1: Environment Setup

```powershell
# Navigate to project directory
cd "C:\Users\byred\Desktop\Student Identification System"

# Create Python virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate  # Windows PowerShell
# source venv/bin/activate  # Linux/Mac

# Upgrade pip
python -m pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Download Pretrained Models

Download the following models and place them in the `models` directory:

1. **GFPGAN v1.4** (~348 MB)

   - URL: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
   - Save as: `models/GFPGANv1.4.pth`

2. **Real-ESRGAN x4plus** (~64 MB)

   - URL: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/RealESRGAN_x4plus.pth
   - Save as: `models/RealESRGAN_x4plus.pth`

3. **AdaFace IR-101** (~250 MB)
   - URL: https://github.com/mk-minchul/AdaFace/releases/download/v1.0/adaface_ir101_webface12m.ckpt
   - Save as: `models/adaface_ir101_webface12m.ckpt`

**OR** use the automated download script:

```powershell
python scripts/download_models.py
```

### Step 3: Configuration

```powershell
# Copy environment template
copy .env.example .env

# Edit .env file with your settings
# Important: Change SECRET_KEY and ENCRYPTION_KEY for production
```

**Key Configuration Options:**

```
DATABASE_URL=sqlite:///./student_identification.db
DEVICE=cpu  # Change to 'cuda' if you have GPU
SIMILARITY_THRESHOLD=0.45
```

### Step 4: Initialize Database

```powershell
python backend/init_db.py
```

This will:

- Create database tables
- Set up directory structure
- Create admin user (username: `admin`, password: `admin123`)

⚠️ **IMPORTANT**: Change admin password after first login!

### Step 5: Register Students from Trainset

```powershell
python scripts/register_students.py --data_dir trainset
```

This process will:

- Process all student folders in trainset
- Extract faces and generate embeddings
- Store in FAISS vector database
- Create student records in database

**Expected time**: ~30 seconds per student on CPU, ~5 seconds on GPU

### Step 6: Start Backend Server

```powershell
cd backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Backend will be available at: http://localhost:8000

**API Documentation**: http://localhost:8000/docs

### Step 7: Start Frontend (Optional)

In a new terminal:

```powershell
cd frontend
npm install
npm run dev
```

Frontend will be available at: http://localhost:3000

## 🧪 Testing the System

### Test Single Image

```powershell
python scripts/test_identification.py "trainset/0001/0001_0000255/0000001.jpg"
```

### Test Batch Processing

```powershell
python scripts/test_identification.py "trainset/0001/0001_0000255" --batch
```

### Expected Output

```
==================================================================
Student Identification System - Test
==================================================================

Loading image: trainset/0001/0001_0000255/0000001.jpg
Image size: 640x480

Initializing pipeline...
✓ Pipeline initialized

Processing image...
==================================================================
Results
==================================================================

✓ Student Identified!

Student ID:   0001
Name:         Student 0001
Department:   Computer Science
Similarity:   0.8542
Threshold:    0.45

Processing Metrics:
  Face detected:     True
  Face confidence:   0.9823
  Image quality:     0.7654
  Enhanced:          True
  Super-resolved:    False

Timing:
  Preprocessing:     1.234s
  Embedding:         0.456s
  FAISS search:      0.012s
  Total:             1.702s

==================================================================
```

## 📊 API Usage Examples

### 1. User Authentication

```python
import requests

# Login
response = requests.post(
    "http://localhost:8000/api/auth/login",
    json={"username": "admin", "password": "admin123"}
)
token = response.json()["access_token"]

# Use token in subsequent requests
headers = {"Authorization": f"Bearer {token}"}
```

### 2. Register Student

```python
import requests

files = {"photo": open("student_photo.jpg", "rb")}
data = {
    "student_id": "STU001",
    "name": "John Doe",
    "department": "Computer Science",
    "year": 2,
    "roll_number": "CS2023001",
    "email": "john@university.edu"
}

response = requests.post(
    "http://localhost:8000/api/students/register",
    files=files,
    data=data,
    headers=headers
)
```

### 3. Identify Student

```python
import requests

files = {"photo": open("unknown_student.jpg", "rb")}
data = {"enhance": "true", "top_k": "3"}

response = requests.post(
    "http://localhost:8000/api/students/identify",
    files=files,
    data=data,
    headers=headers
)

result = response.json()
if result["success"]:
    print(f"Identified: {result['student']['name']}")
    print(f"Similarity: {result['similarity']:.2%}")
```

## 🔧 Troubleshooting

### Issue: "No face detected"

**Solutions**:

- Ensure image has clear, visible face
- Check image quality (not too dark or blurry)
- Try with `enhance=true` to apply GFPGAN restoration

### Issue: "Low similarity score"

**Solutions**:

- Adjust `SIMILARITY_THRESHOLD` in `.env` (default: 0.45)
- Re-register with better quality photo
- Check if multiple people in reference image

### Issue: "Slow processing"

**Solutions**:

- Use GPU: Set `DEVICE=cuda` in `.env`
- Disable Real-ESRGAN for faster processing (edit pipeline config)
- Process in batches for better efficiency

### Issue: "Model not found"

**Solutions**:

- Verify models are in `models/` directory
- Check filenames match exactly
- Re-download models using download script

### Issue: "Memory error"

**Solutions**:

- Reduce batch size in configuration
- Use CPU instead of GPU if GPU memory insufficient
- Process students in smaller batches during registration

## ⚡ Performance Optimization

### For CPU (No GPU Available)

1. Use smaller batch sizes
2. Disable Real-ESRGAN if not needed
3. Process during off-peak hours

### For GPU

1. Set `DEVICE=cuda` in `.env`
2. Install CUDA-compatible PyTorch:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```
3. Use larger batch sizes for efficiency

### Production Deployment

1. Use PostgreSQL instead of SQLite
2. Enable caching for embeddings
3. Use load balancer for multiple instances
4. Deploy with Docker for consistency

## 🐳 Docker Deployment

```powershell
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

Services:

- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- PostgreSQL: localhost:5432

## 📈 System Monitoring

Access system statistics at:

- API: http://localhost:8000/api/stats
- Frontend: http://localhost:3000 (Statistics tab)

Metrics include:

- Total students registered
- Identification success rate
- Average processing latency
- Recent identification logs

## 🔐 Security Recommendations

1. **Change default credentials**:

   - Admin password
   - SECRET_KEY in .env
   - ENCRYPTION_KEY in .env

2. **Use HTTPS in production**

3. **Implement rate limiting**

4. **Regular database backups**

5. **Restrict API access** with proper authentication

## 📝 Important Notes

- System requires ONE clear photo per student (ID card recommended)
- Works with poor quality query images (CCTV, mobile, etc.)
- Threshold of 0.45 balances accuracy and false positives
- Processing time: <4s CPU, <0.5s GPU per image
- Target accuracy: >97% with single reference image

## 🆘 Support

For issues or questions:

1. Check troubleshooting section above
2. Review logs in `logs/system.log`
3. Check API documentation at http://localhost:8000/docs

## 📚 Additional Resources

- GFPGAN: https://github.com/TencentARC/GFPGAN
- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN
- AdaFace: https://github.com/mk-minchul/AdaFace
- FAISS: https://github.com/facebookresearch/faiss
- FastAPI: https://fastapi.tiangolo.com/
