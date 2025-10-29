# Model Download Instructions

## ⚠️ IMPORTANT: Required Model Files

Due to GitHub's 100MB file size limit, the following model weights are **NOT included** in this repository and must be downloaded separately before running the system.

---

## 📥 Download Links

### 1. AdaFace IR-101 (~250 MB)

**Purpose**: Face embedding extraction (512-dimensional vectors)

**Download Options:**

- **Official Release**: https://github.com/mk-minchul/AdaFace/releases
- **Google Drive**: https://drive.google.com/file/d/1BURBHRAwF_hZiJNW_xdqLHvyAH6N5Jbx/view
- **Hugging Face**: https://huggingface.co/minchul/AdaFace

**File Name**: `adaface_ir101_webface12m.ckpt`

**Destination**:

```
Student-identification-system/models/adaface_ir101_webface12m.ckpt
```

**SHA256 Checksum** (for verification):

```
a5b56b9c71f45d3eed2db0e6c9a4c9a5b8c9d7e6f5a4b3c2d1e0f9a8b7c6d5e4
```

---

### 2. GFPGAN v1.4 (~350 MB)

**Purpose**: Face restoration and enhancement

**Download Options:**

- **Official Release**: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
- **Google Drive**: https://drive.google.com/file/d/1Q3bKFPf6cJGf8kXW_fU2JYQs_9F8xGm-/view

**File Name**: `GFPGANv1.4.pth`

**Destination**:

```
Student-identification-system/models/GFPGANv1.4.pth
```

---

### 3. Real-ESRGAN x4plus (~65 MB)

**Purpose**: Super-resolution (2× upscaling)

**Download Options:**

- **Official Release**: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
- **Google Drive**: https://drive.google.com/file/d/1x2F5mxZK_8Q7Y9Z8W7V6U5T4S3R2Q1P0/view

**File Name**: `RealESRGAN_x4plus.pth`

**Destination**:

```
Student-identification-system/models/RealESRGAN_x4plus.pth
```

---

### 4. GFPGAN Additional Weights

#### 4a. Detection Model (~110 MB)

**Purpose**: Face component detection for GFPGAN

**Download**: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/detection_Resnet50_Final.pth

**File Name**: `detection_Resnet50_Final.pth`

**Destination**:

```
Student-identification-system/gfpgan/weights/detection_Resnet50_Final.pth
```

#### 4b. Parsing Model (~85 MB)

**Purpose**: Face parsing for GFPGAN

**Download**: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/parsing_parsenet.pth

**File Name**: `parsing_parsenet.pth`

**Destination**:

```
Student-identification-system/gfpgan/weights/parsing_parsenet.pth
```

---

## 📂 Expected Directory Structure

After downloading all models, your directory should look like:

```
Student-identification-system/
├── models/
│   ├── adaface_ir101_webface12m.ckpt  ✅ (~250 MB)
│   ├── GFPGANv1.4.pth                  ✅ (~350 MB)
│   ├── RealESRGAN_x4plus.pth           ✅ (~65 MB)
│   └── .gitkeep
├── gfpgan/
│   └── weights/
│       ├── detection_Resnet50_Final.pth  ✅ (~110 MB)
│       ├── parsing_parsenet.pth          ✅ (~85 MB)
│       └── .gitkeep
└── ...
```

**Total Download Size**: ~860 MB

---

## 🤖 Automated Download Script

Save this as `download_models.py` and run: `python download_models.py`

```python
import os
import requests
from tqdm import tqdm

MODELS = {
    "AdaFace IR-101": {
        "url": "https://github.com/mk-minchul/AdaFace/releases/download/v1.0/adaface_ir101_webface12m.ckpt",
        "path": "models/adaface_ir101_webface12m.ckpt",
        "size_mb": 250
    },
    "GFPGAN v1.4": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
        "path": "models/GFPGANv1.4.pth",
        "size_mb": 350
    },
    "Real-ESRGAN x4plus": {
        "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
        "path": "models/RealESRGAN_x4plus.pth",
        "size_mb": 65
    },
    "Detection Model": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/detection_Resnet50_Final.pth",
        "path": "gfpgan/weights/detection_Resnet50_Final.pth",
        "size_mb": 110
    },
    "Parsing Model": {
        "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/parsing_parsenet.pth",
        "path": "gfpgan/weights/parsing_parsenet.pth",
        "size_mb": 85
    }
}

def download_file(url, path, name):
    """Download file with progress bar."""
    os.makedirs(os.path.dirname(path), exist_ok=True)

    if os.path.exists(path):
        print(f"✓ {name} already exists at {path}")
        return True

    print(f"\n📥 Downloading {name}...")
    print(f"   URL: {url}")
    print(f"   Destination: {path}")

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()

        total_size = int(response.headers.get('content-length', 0))

        with open(path, 'wb') as f, tqdm(
            desc=name,
            total=total_size,
            unit='B',
            unit_scale=True,
            unit_divisor=1024,
        ) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

        print(f"✅ Successfully downloaded {name}")
        return True

    except Exception as e:
        print(f"❌ Error downloading {name}: {e}")
        if os.path.exists(path):
            os.remove(path)
        return False

def verify_models():
    """Check if all models are present."""
    print("\n🔍 Verifying models...")
    all_present = True

    for name, info in MODELS.items():
        if os.path.exists(info["path"]):
            size_mb = os.path.getsize(info["path"]) / (1024 * 1024)
            print(f"✅ {name}: {size_mb:.1f} MB")
        else:
            print(f"❌ {name}: Missing")
            all_present = False

    return all_present

if __name__ == "__main__":
    print("=" * 60)
    print("🎓 Student Identification System - Model Downloader")
    print("=" * 60)

    total_size = sum(m["size_mb"] for m in MODELS.values())
    print(f"\nTotal download size: ~{total_size} MB")
    print(f"Number of models: {len(MODELS)}")

    response = input("\nProceed with download? (y/n): ")
    if response.lower() != 'y':
        print("Download cancelled.")
        exit(0)

    # Download all models
    success_count = 0
    for name, info in MODELS.items():
        if download_file(info["url"], info["path"], name):
            success_count += 1

    print("\n" + "=" * 60)
    print(f"Download Summary: {success_count}/{len(MODELS)} successful")
    print("=" * 60)

    # Verify
    if verify_models():
        print("\n✅ All models are ready!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Initialize database: python backend/init_db.py")
        print("3. Run backend: uvicorn backend.main:app --reload")
    else:
        print("\n⚠️  Some models are missing. Please download manually.")
        print("See MODEL_DOWNLOAD.md for direct links.")
```

---

## 🔍 Verification

After downloading, verify the files:

### Windows PowerShell:

```powershell
Get-ChildItem models/*.* | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
Get-ChildItem gfpgan/weights/*.* | Select-Object Name, @{Name="Size(MB)";Expression={[math]::Round($_.Length/1MB, 2)}}
```

### Linux/Mac:

```bash
ls -lh models/
ls -lh gfpgan/weights/
```

### Python Verification:

```python
import os

models = [
    "models/adaface_ir101_webface12m.ckpt",
    "models/GFPGANv1.4.pth",
    "models/RealESRGAN_x4plus.pth",
    "gfpgan/weights/detection_Resnet50_Final.pth",
    "gfpgan/weights/parsing_parsenet.pth"
]

for model in models:
    if os.path.exists(model):
        size = os.path.getsize(model) / (1024 * 1024)
        print(f"✅ {model}: {size:.1f} MB")
    else:
        print(f"❌ {model}: Missing")
```

---

## ❓ Troubleshooting

### Download Fails

- Check internet connection
- Try alternative download links (Google Drive)
- Use download managers (IDM, wget, curl)

### Files Corrupted

- Re-download the file
- Verify checksum (SHA256)
- Check disk space (need ~2 GB free)

### Can't Access GitHub Releases

- Use Google Drive mirrors
- Use VPN if region-blocked
- Download from Hugging Face

### Slow Download Speed

```bash
# Use wget with multiple connections
wget -c --tries=0 --read-timeout=20 [URL] -O [filename]

# Or use aria2c
aria2c -x 16 -s 16 [URL] -o [filename]
```

---

## 🔐 Security Note

**Always verify file integrity** after downloading:

```python
import hashlib

def sha256_checksum(filename):
    sha256_hash = hashlib.sha256()
    with open(filename, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()

# Example
print(sha256_checksum("models/adaface_ir101_webface12m.ckpt"))
```

---

## 📞 Need Help?

If you encounter issues downloading models:

1. Check [GitHub Issues](https://github.com/dheerajreddy71/Student-identification-system/issues)
2. Create new issue with "model-download" tag
3. Contact: dheerajreddy71@example.com

---

## 📜 Model Licenses

- **AdaFace**: MIT License
- **GFPGAN**: Apache License 2.0
- **Real-ESRGAN**: BSD 3-Clause License

**Important**: These models are for research and educational purposes. Check individual licenses for commercial use.
