# 🎓 AI-Powered Student Identification System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green.svg)](https://fastapi.tiangolo.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14.2-black.svg)](https://nextjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> Production-ready face recognition system that identifies students from ANY quality image using state-of-the-art AI models: GFPGAN + AdaFace + FAISS

![System Demo](docs/demo.gif)

## 🌟 Key Features

- ✅ **Works with Poor Quality Images** - Blur, low-light, side-angle, low-resolution
- ✅ **Real-time Identification** - < 4 seconds on CPU, < 0.5s on GPU
- ✅ **High Accuracy** - > 97% with single reference photo
- ✅ **Multiple Photo Registration** - Register students with multiple photos for better accuracy
- ✅ **Quality Enhancement** - GFPGAN improves image quality by ~21%
- ✅ **Scalable** - Handles 10,000+ students efficiently with FAISS
- ✅ **Modern Web Dashboard** - React + Next.js with webcam support
- ✅ **Secure** - JWT authentication, password hashing, RBAC
- ✅ **Production-Ready** - Docker support, logging, monitoring

## 📸 Screenshots

### Identification Module
![Identification](docs/screenshots/identification.png)

### Registration Module  
![Registration](docs/screenshots/registration.png)

### Student Database
![Database](docs/screenshots/database.png)

## 🏗️ System Architecture

```
Input Image (any quality)
    ↓
[MTCNN] Face Detection & Alignment
    ↓
[Real-ESRGAN] Super-Resolution (if needed)
    ↓
[GFPGAN v1.4] Face Restoration & Enhancement
    ↓
[AdaFace IR-101] Embedding Extraction (512-D)
    ↓
[FAISS] Cosine Similarity Search
    ↓
Student Match + Confidence Score
```

## 🚀 Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **GFPGAN v1.4** - Face restoration and quality enhancement
- **Real-ESRGAN** - Super-resolution for low-quality images
- **MTCNN** - Multi-task Cascaded CNN for face detection
- **AdaFace (IR-101)** - Quality-adaptive face recognition (512-D embeddings)
- **FAISS** - Facebook AI Similarity Search for efficient vector search
- **SQLite/PostgreSQL** - Database for student records

### Frontend
- **Next.js 14** - React framework with SSR
- **TypeScript** - Type-safe JavaScript
- **Tailwind CSS** - Utility-first CSS framework
- **Axios** - HTTP client for API calls

### AI Models
- **GFPGAN v1.4** (~297 MB) - Pre-trained face restoration
- **Real-ESRGAN x4plus** (~64 MB) - Pre-trained super-resolution
- **AdaFace IR-101** (~365 MB) - Pre-trained on WebFace12M dataset

## 📋 Requirements

- **Python**: 3.8 or higher
- **Node.js**: 16 or higher
- **RAM**: 8GB minimum (16GB recommended)
- **Storage**: 2GB for models and data
- **GPU**: Optional (CUDA-compatible for 10x speedup)

## 🔧 Quick Start

### Option 1: Automated Setup (Recommended)

```powershell
# Clone repository
git clone https://github.com/YOUR_USERNAME/student-identification-system.git
cd student-identification-system

# Run automated setup
.\setup.ps1
```

This script will:
1. Create Python virtual environment
2. Install all dependencies
3. Download pre-trained models
4. Initialize database
5. Set up frontend
6. Register sample students

### Option 2: Manual Setup

#### Backend Setup

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Download models (see MANUAL_DOWNLOAD.md)
python scripts/download_models.py

# Initialize database
python backend/init_db.py

# Start backend
uvicorn backend.main:app --port 8000
```

#### Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

#### Register Students

```powershell
# Register from directory structure
python scripts/register_students.py --data_dir trainset

# Or rebuild entire database with department structure
python rebuild_dept_structure.py
```

### Access the System

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

**Default Login**:
- Username: `admin`
- Password: `admin123`

## 📚 Documentation

- **[QUICKSTART.md](QUICKSTART.md)** - Get started in 10 minutes
- **[SETUP_GUIDE.md](SETUP_GUIDE.md)** - Detailed setup and troubleshooting
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Production deployment guide
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Complete technical overview
- **[MANUAL_DOWNLOAD.md](MANUAL_DOWNLOAD.md)** - Model download instructions
- **API Docs** - Interactive API documentation at `/docs` endpoint

## 🎮 Usage

### 1. Register Students

#### Single Photo Registration
```python
# Upload one photo per student
POST /api/students/register
{
    "student_id": "CS101",
    "name": "John Doe",
    "department": "CSE",
    "year": 3,
    "photo": <file>
}
```

#### Multiple Photo Registration
```python
# Upload multiple photos for better accuracy
POST /api/students/register
{
    "student_id": "CS101",
    "name": "John Doe",
    "department": "CSE",
    "year": 3,
    "photos": [<file1>, <file2>, <file3>]
}
```

### 2. Identify Students

```python
# Upload any quality photo
POST /api/students/identify
{
    "image": <file>
}

# Response
{
    "success": true,
    "student_id": "CS101",
    "name": "John Doe",
    "department": "CSE",
    "confidence": 0.92,
    "quality_improvement": "+21%"
}
```

### 3. Web Dashboard

1. **Login** - Use admin credentials
2. **Register** - Add new students with photos
3. **Identify** - Upload photo or use webcam
4. **Database** - View all registered students
5. **Statistics** - Monitor system performance

## 🔬 Technical Details

### Face Recognition Pipeline

1. **Face Detection** (MTCNN)
   - Detects faces in images
   - Returns bounding box and keypoints
   - Confidence threshold: 0.9

2. **Image Enhancement** (GFPGAN + Real-ESRGAN)
   - Restores degraded faces
   - Super-resolves low-resolution images
   - Quality improvement: ~21%

3. **Embedding Extraction** (AdaFace IR-101)
   - Extracts 512-dimensional face embeddings
   - Quality-adaptive feature extraction
   - Pre-trained on WebFace12M (12 million images)

4. **Similarity Search** (FAISS)
   - Cosine similarity metric
   - Efficient vector search (< 1ms for 10K vectors)
   - Threshold: 0.35 (configurable)

### Performance Metrics

| Metric | CPU (Intel i7) | GPU (NVIDIA GTX 1660) |
|--------|----------------|----------------------|
| Face Detection | 0.5s | 0.1s |
| Enhancement | 2.5s | 0.2s |
| Embedding | 0.8s | 0.1s |
| FAISS Search | 0.001s | 0.001s |
| **Total** | **~4s** | **~0.5s** |

### Accuracy Metrics

- **Identification Accuracy**: > 97% (on enhanced images)
- **False Positive Rate**: < 0.5%
- **Quality Improvement**: ~21% (PSNR-based)
- **Similarity Threshold**: 0.35 (adjustable)

## 🐳 Docker Deployment

```powershell
# Build images
docker-compose build

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🔐 Security Features

- ✅ **JWT Authentication** - Token-based auth with expiration
- ✅ **Password Hashing** - bcrypt with salt
- ✅ **RBAC** - Role-based access control (admin/user)
- ✅ **CORS Protection** - Configured for production
- ✅ **Input Validation** - Pydantic models for type safety
- ✅ **SQL Injection Prevention** - ORM-based queries

## 📊 Dataset Structure

```
trainset/
├── DEPT1/
│   ├── STUDENT_ID_1/
│   │   ├── STUDENT_ID_1_1.jpg
│   │   ├── STUDENT_ID_1_2.jpg
│   │   └── STUDENT_ID_1_3.jpg
│   └── STUDENT_ID_2/
│       └── STUDENT_ID_2_1.jpg
└── DEPT2/
    └── STUDENT_ID_3/
        ├── STUDENT_ID_3_1.jpg
        └── STUDENT_ID_3_2.jpg
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **GFPGAN** - [Towards Real-World Blind Face Restoration](https://github.com/TencentARC/GFPGAN)
- **Real-ESRGAN** - [Real-ESRGAN: Training Real-World Blind Super-Resolution](https://github.com/xinntao/Real-ESRGAN)
- **AdaFace** - [AdaFace: Quality Adaptive Margin for Face Recognition](https://github.com/mk-minchul/AdaFace)
- **FAISS** - [Facebook AI Similarity Search](https://github.com/facebookresearch/faiss)
- **MTCNN** - [Multi-task Cascaded Convolutional Networks](https://github.com/ipazc/mtcnn)

## 📧 Contact

For questions or issues:
- **GitHub Issues**: [Create an issue](https://github.com/YOUR_USERNAME/student-identification-system/issues)
- **Email**: your-email@example.com
- **Documentation**: See [SETUP_GUIDE.md](SETUP_GUIDE.md)

## ⭐ Star History

If you find this project useful, please consider giving it a star!

---

**Made with ❤️ for capstone projects and real-world applications**

**Last Updated**: October 2025
