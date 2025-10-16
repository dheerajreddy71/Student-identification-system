"""
Download pretrained models for the system
"""
import os
import sys
import urllib.request
from pathlib import Path
from tqdm import tqdm


class DownloadProgressBar(tqdm):
    """Progress bar for downloads"""
    def update_to(self, b=1, bsize=1, tsize=None):
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)


def download_file(url, output_path):
    """Download file with progress bar"""
    with DownloadProgressBar(unit='B', unit_scale=True, miniters=1, desc=output_path) as t:
        urllib.request.urlretrieve(url, filename=output_path, reporthook=t.update_to)


def download_models():
    """Download all required pretrained models"""
    
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    
    models = {
        "GFPGANv1.4.pth": {
            "url": "https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth",
            "size": "~348 MB"
        },
        "RealESRGAN_x4plus.pth": {
            "url": "https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth",
            "size": "~64 MB"
        },
        "adaface_ir101_webface12m.ckpt": {
            "url": "https://huggingface.co/VishalMishraTss/AdaFace/resolve/main/adaface_ir101_webface12m.ckpt",
            "size": "~250 MB"
        }
    }
    
    print("=" * 70)
    print("Downloading Pretrained Models")
    print("=" * 70)
    print()
    print("Total download size: ~662 MB")
    print("This may take several minutes depending on your connection speed")
    print()
    
    for model_name, info in models.items():
        model_path = models_dir / model_name
        
        if model_path.exists():
            print(f"✓ {model_name} already exists, skipping")
            continue
        
        print(f"Downloading {model_name} ({info['size']})...")
        
        try:
            if info.get('use_gdown', False):
                # Try using gdown for Google Drive downloads
                try:
                    import gdown
                    gdown.download(info['url'], str(model_path), quiet=False)
                    print(f"✓ Downloaded {model_name}")
                    print()
                except ImportError:
                    print("⚠ gdown not installed. Installing now...")
                    os.system(f"{sys.executable} -m pip install gdown")
                    import gdown
                    gdown.download(info['url'], str(model_path), quiet=False)
                    print(f"✓ Downloaded {model_name}")
                    print()
            else:
                download_file(info['url'], str(model_path))
                print(f"✓ Downloaded {model_name}")
                print()
        except Exception as e:
            print(f"✗ Failed to download {model_name}: {e}")
            if 'google.com' in info['url']:
                print(f"  Try downloading manually from Google Drive:")
                print(f"  https://drive.google.com/file/d/1BURBDplf2bXpmwKhledkVjnk5kSjCJen/view")
            else:
                print(f"  Please download manually from: {info['url']}")
            print()
    
    print("=" * 70)
    print("Model Download Complete!")
    print("=" * 70)
    print()
    print("Downloaded models:")
    for model_name in models.keys():
        model_path = models_dir / model_name
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            print(f"✓ {model_name} ({size_mb:.1f} MB)")
        else:
            print(f"✗ {model_name} - NOT DOWNLOADED")
    print()


if __name__ == "__main__":
    download_models()
