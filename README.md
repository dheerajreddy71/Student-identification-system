# 🎓 Student Identification System

**Quality-Adaptive Face Recognition System for Educational Institutions**

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.1-009688.svg)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14.2.3-black.svg)](https://nextjs.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> A state-of-the-art face recognition system that adapts to image quality, achieving 86.8% accuracy on real-world student datasets.

---

## 🌟 Features

### 🔍 **Smart Recognition**
- **Quality-Adaptive Pipeline**: Automatically enhances poor-quality images
- **Multi-Photo Registration**: Averages embeddings from multiple photos for robustness
- **Real-Time Processing**: 2-4 seconds per identification on CPU
- **High Accuracy**: 86.8% overall accuracy, 93.2% on high-quality images

### 🛠️ **Technical Highlights**
- **AdaFace IR-101**: 512-D embeddings with quality-adaptive margins
- **GFPGAN**: Face restoration for degraded images
- **Real-ESRGAN**: 2× super-resolution for low-resolution faces
- **MTCNN**: Multi-task cascaded face detection
- **FAISS**: Fast similarity search (30ms for 1,000+ students)

### 📊 **Complete Management**
- Student registration with multi-photo support
- Real-time identification with confidence scores
- Detailed analytics and reporting
- Department-wise organization
- Audit logging and metrics tracking

---

## 🚀 Quick Start

### Prerequisites
```bash
Python 3.9+
Node.js 18+
Git with Git LFS
8GB+ RAM
```

### Installation

1. **Clone Repository**
```bash
git clone https://github.com/dheerajreddy71/Student-identification-system.git
cd Student-identification-system
```

2. **Download Model Weights**

⚠️ **IMPORTANT**: Due to GitHub file size limits, model weights must be downloaded separately.

| Model | Size | Download Link | Destination |
|-------|------|---------------|-------------|
| AdaFace IR-101 | 250MB | [Download](https://github.com/mk-minchul/AdaFace/releases) | `models/adaface_ir101_webface12m.ckpt` |
| GFPGAN v1.4 | 350MB | [Download](https://github.com/TencentARC/GFPGAN/releases) | `models/GFPGANv1.4.pth` |
| Real-ESRGAN | 65MB | [Download](https://github.com/xinntao/Real-ESRGAN/releases) | `models/RealESRGAN_x4plus.pth` |

3. **Backend Setup**
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
```

4. **Frontend Setup**
```bash
cd frontend
npm install
cd ..
```

5. **Create Admin User**
```bash
python scripts/create_admin.py
```

6. **Run Application**

**Terminal 1 - Backend:**
```bash
uvicorn backend.main:app --reload --port 8000
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

Access at: **http://localhost:3000**

---

## 📁 Project Structure

```
Student-identification-system/
├── backend/                    # FastAPI backend
│   ├── api/                   # API endpoints
│   ├── models/                # ML models & database models
│   ├── services/              # Business logic
│   ├── utils/                 # Utilities
│   └── main.py               # Entry point
├── frontend/                  # Next.js frontend
│   ├── app/                   # Pages
│   ├── components/            # React components
│   └── lib/                   # Utilities
├── models/                    # Model weights (download separately)
│   ├── adaface_ir101_webface12m.ckpt
│   ├── GFPGANv1.4.pth
│   └── RealESRGAN_x4plus.pth
├── gfpgan/weights/           # GFPGAN additional weights
├── scripts/                   # Utility scripts
│   ├── register_students.py  # Bulk registration
│   └── create_admin.py       # Admin creation
├── trainset/                  # Student photos (not in repo)
├── data/                      # FAISS index & metadata
├── requirements.txt           # Python dependencies
└── README.md                 # This file
```

---

## 🎯 Usage

### 1. Register Students

Place photos in this structure:
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

### 2. Identify Students

- Upload photo through web interface
- System detects face, assesses quality
- Conditionally enhances if needed
- Returns student details with confidence score

### 3. View Analytics

- Access Statistics module for insights
- View identification logs
- Monitor success rates and processing times

---

## 🔬 Technical Architecture

### Pipeline Flow
```
Input Image
    ↓
[MTCNN Detection] → Face detected? → No → ❌ Failure
    ↓ Yes
[Quality Assessment] → Q = 0.3×sharpness + 0.2×brightness + ...
    ↓
Q < 0.7? → Yes → [GFPGAN + Real-ESRGAN Enhancement]
    ↓ No
[AdaFace Embedding] → 512-D vector
    ↓
[L2 Normalization]
    ↓
[FAISS Search] → Cosine similarity > 0.45?
    ↓ Yes
✅ Identified: Student Details + Confidence
```

### Quality Metrics
- **Sharpness**: Laplacian variance (weight: 0.3)
- **Brightness**: Mean pixel intensity (weight: 0.2)
- **Contrast**: Std deviation (weight: 0.2)
- **Face Size**: Area ratio (weight: 0.15)
- **Confidence**: MTCNN score (weight: 0.15)

### Models Used
| Model | Purpose | Parameters | Input/Output |
|-------|---------|------------|--------------|
| MTCNN | Face Detection | 3 cascaded CNNs | Image → BBox + Landmarks |
| Real-ESRGAN | Super-Resolution | 23 RRDB blocks | 112×112 → 224×224 |
| GFPGAN | Face Restoration | U-Net + StyleGAN2 | Degraded → Clean |
| AdaFace IR-101 | Embedding | 42M params | 112×112 → 512-D |
| FAISS | Similarity Search | IndexFlatIP | 512-D → Top-K matches |

---

## 📊 Performance

| Metric | Value |
|--------|-------|
| **Overall Accuracy** | 86.8% |
| **High-Quality Images** | 93.2% |
| **Low-Quality Images** | 58.5% → 78.2% (with enhancement) |
| **Processing Time** | 2.4s avg (CPU) |
| **FAISS Search** | 30ms (1,014 students) |
| **Dataset Size** | 1,014 students, 12 departments |

### Ablation Study
| Configuration | Accuracy |
|---------------|----------|
| Always Enhance | 87.2% (2.7s avg) |
| Never Enhance | 79.3% (0.9s avg) |
| **Adaptive (Q<0.7)** | **86.8% (1.8s avg)** ✅ |

---

## 🔧 Configuration

### Environment Variables (`.env`)
```env
DATABASE_URL=sqlite:///./students.db
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
MODEL_PATH=./models
PHOTOS_PATH=./photos
TRAINSET_PATH=./trainset
ALLOWED_ORIGINS=http://localhost:3000
```

### Frontend (`.env.local`)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## 🚢 Deployment

See **[DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)** for detailed instructions on:
- Cloud deployment (Render, Railway, AWS)
- Production configuration
- Security best practices
- Scaling strategies

**Quick Deploy Options:**
- [![Deploy on Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com)
- [![Deploy on Railway](https://railway.app/button.svg)](https://railway.app)

---



## 🛠️ Development

### Run Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format
black backend/ scripts/

# Lint
pylint backend/ scripts/
```

### API Documentation
Access interactive API docs at: `http://localhost:8000/docs`

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

---

## ⚠️ Known Limitations

- **Extreme Degradation**: <30×30 pixel faces or JPEG quality <15 fail
- **Occlusion**: >50% face coverage reduces accuracy significantly
- **Pose Variation**: Extreme profiles (>45° rotation) struggle
- **Demographic Bias**: Training data imbalances may affect fairness
- **Spoofing**: No liveness detection (vulnerable to photo attacks)

---

## 🔮 Future Enhancements

- [ ] Liveness detection (blink/movement analysis)
- [ ] Multi-view fusion (frontal + profile)
- [ ] Continual learning for appearance changes
- [ ] GPU acceleration for real-time processing
- [ ] Mobile app integration
- [ ] Federated learning for privacy
- [ ] 3D face recognition
- [ ] Mask detection and handling

---

## 📄 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file.

**Model Licenses:**
- AdaFace: MIT License
- GFPGAN: Apache 2.0
- Real-ESRGAN: BSD 3-Clause
- MTCNN: MIT License

---

## 👥 Authors

- **Dheeraj Reddy** - [GitHub](https://github.com/dheerajreddy71)

---

## 🙏 Acknowledgments

- [AdaFace](https://github.com/mk-minchul/AdaFace) by Minchul Kim et al.
- [GFPGAN](https://github.com/TencentARC/GFPGAN) by Tencent ARC Lab
- [Real-ESRGAN](https://github.com/xinntao/Real-ESRGAN) by Xintao Wang et al.
- [MTCNN](https://github.com/ipazc/mtcnn) by Iván de Paz Centeno
- [FAISS](https://github.com/facebookresearch/faiss) by Facebook AI Research

---

## 📞 Support

- 📧 Email: byreddydherajreddy@gmail.com
- 🐛 Issues: [GitHub Issues](https://github.com/dheerajreddy71/Student-identification-system/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/dheerajreddy71/Student-identification-system/discussions)

---

<div align="center">
  <p>Made with ❤️ for educational institutions</p>
  <p>⭐ Star this repo if you find it helpful!</p>
</div>
