# Manual Model Download Instructions

If automatic download fails, please download the models manually:

## 1. GFPGANv1.4.pth (348 MB) ✓ Already Downloaded

- **URL**: https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth
- **Save to**: `models/GFPGANv1.4.pth`

## 2. RealESRGAN_x4plus.pth (64 MB) ❌ NEEDS DOWNLOAD

- **URL**: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth
- **Alternative URL**: https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.1/RealESRGAN_x4plus.pth
- **Save to**: `models/RealESRGAN_x4plus.pth`

### Steps to download manually:

1. Click the URL above in your browser
2. The file will start downloading
3. Move the downloaded file to the `models` folder in your project
4. Make sure it's named exactly `RealESRGAN_x4plus.pth`

## 3. adaface_ir101_webface12m.ckpt (250 MB) ❌ NEEDS DOWNLOAD

**IMPORTANT**: The GitHub release link is not working. Use Google Drive instead:

- **Google Drive URL**: https://drive.google.com/file/d/1BURBDplf2bXpmwKhledkVjnk5kSjCJen/view?usp=sharing
- **Alternative GitHub**: Check https://github.com/mk-minchul/AdaFace for updated links
- **Save to**: `models/adaface_ir101_webface12m.ckpt`

### Steps to download manually:

1. Click the Google Drive link above
2. Click "Download" button (you may need to click "Download anyway" if Google shows a virus warning)
3. Wait for the download to complete (~250 MB)
4. Move the downloaded file to the `models` folder in your project
5. Make sure it's named exactly `adaface_ir101_webface12m.ckpt`

### Alternative method using command line:

```powershell
# Install gdown if not already installed
pip install gdown

# Download from Google Drive
gdown 1BURBDplf2bXpmwKhledkVjnk5kSjCJen -O models/adaface_ir101_webface12m.ckpt
```

## Verification

After downloading, your `models` folder should contain:

```
models/
├── GFPGANv1.4.pth (349 MB)
├── RealESRGAN_x4plus.pth (64 MB)
└── adaface_ir101_webface12m.ckpt (250 MB)
```

Run this command to verify:

```powershell
Get-ChildItem models -Name
```

You should see all three files listed.

## After Manual Download

Once all models are downloaded, run:

```powershell
.\quickfix.ps1
```

This will initialize the database and register students.
