"""
Face restoration using GFPGAN v1.4
"""
import cv2
import numpy as np
import torch
from typing import Optional
import os


class FaceRestorer:
    """GFPGAN-based face restoration"""
    
    def __init__(self, model_path: str, device='cpu', upscale=2):
        """
        Initialize GFPGAN model
        
        Args:
            model_path: Path to GFPGANv1.4.pth
            device: 'cpu' or 'cuda'
            upscale: Upscaling factor (1, 2, 4)
        """
        self.device = device
        self.upscale = upscale
        
        # Import GFPGAN
        try:
            from gfpgan import GFPGANer
        except ImportError:
            raise ImportError("Please install GFPGAN: pip install gfpgan")
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"GFPGAN model not found at {model_path}. "
                f"Please download from: "
                f"https://github.com/TencentARC/GFPGAN/releases/download/v1.3.0/GFPGANv1.4.pth"
            )
        
        # Initialize GFPGAN
        self.restorer = GFPGANer(
            model_path=model_path,
            upscale=upscale,
            arch='clean',
            channel_multiplier=2,
            bg_upsampler=None,  # Don't upscale background
            device=device
        )
        
        print(f"✓ GFPGAN loaded on {device}")
    
    def restore(self, face_image: np.ndarray, 
                aligned: bool = True,
                weight: float = 0.5) -> np.ndarray:
        """
        Restore face image
        
        Args:
            face_image: Input face image (BGR format)
            aligned: Whether face is already aligned
            weight: Balance between input and restored (0=input, 1=restored)
            
        Returns:
            Restored face image
        """
        if face_image is None or face_image.size == 0:
            raise ValueError("Invalid input image")
        
        # Store original size
        original_h, original_w = face_image.shape[:2]
        
        # GFPGAN works better with larger images (at least 512x512)
        # If input is small, upscale it first
        if original_h < 512 or original_w < 512:
            upscale_factor = max(512 / original_h, 512 / original_w)
            new_h = int(original_h * upscale_factor)
            new_w = int(original_w * upscale_factor)
            face_image_upscaled = cv2.resize(face_image, (new_w, new_h), interpolation=cv2.INTER_CUBIC)
        else:
            face_image_upscaled = face_image
            upscale_factor = 1.0
        
        # Run restoration
        try:
            # GFPGAN enhance returns: cropped_faces (list), restored_faces (list), restored_img
            output = self.restorer.enhance(
                face_image_upscaled,
                has_aligned=aligned,
                only_center_face=True,
                paste_back=False,
                weight=weight
            )
            
            # Extract the results
            if isinstance(output, tuple) and len(output) >= 2:
                cropped_faces, restored_faces = output[0], output[1]
                
                # Get the first restored face from the list
                if isinstance(restored_faces, list) and len(restored_faces) > 0:
                    result = restored_faces[0]
                elif isinstance(cropped_faces, list) and len(cropped_faces) > 0:
                    result = cropped_faces[0]
                    print("Warning: Using cropped face instead of restored")
                else:
                    print("Warning: GFPGAN returned empty lists, using original")
                    return face_image
            else:
                print("Warning: GFPGAN returned unexpected format, using original")
                return face_image
            
            # Validate result
            if result is None or not isinstance(result, np.ndarray) or result.size == 0:
                print("Warning: GFPGAN result is invalid, using original")
                return face_image
            
            # Resize back to original dimensions if needed
            if result.shape[:2] != (original_h, original_w):
                result = cv2.resize(result, (original_w, original_h), interpolation=cv2.INTER_CUBIC)
            
            return result
            
        except Exception as e:
            print(f"Warning: GFPGAN enhance failed: {e}, using original")
            import traceback
            traceback.print_exc()
            return face_image
    
    def restore_batch(self, face_images: list, 
                     aligned: bool = True,
                     weight: float = 0.5) -> list:
        """
        Restore multiple face images
        
        Args:
            face_images: List of face images
            aligned: Whether faces are already aligned
            weight: Balance between input and restored
            
        Returns:
            List of restored face images
        """
        restored_faces = []
        
        for face_image in face_images:
            try:
                restored = self.restore(face_image, aligned, weight)
                restored_faces.append(restored)
            except Exception as e:
                print(f"Warning: Failed to restore face: {e}")
                # Return original if restoration fails
                restored_faces.append(face_image)
        
        return restored_faces
    
    def assess_quality(self, original: np.ndarray, restored: np.ndarray) -> dict:
        """
        Assess quality improvement
        
        Args:
            original: Original face image
            restored: Restored face image
            
        Returns:
            Dictionary with quality metrics
        """
        # Resize to same size if needed
        if original.shape != restored.shape:
            original = cv2.resize(original, (restored.shape[1], restored.shape[0]))
        
        # Convert to grayscale
        gray_orig = cv2.cvtColor(original, cv2.COLOR_BGR2GRAY)
        gray_rest = cv2.cvtColor(restored, cv2.COLOR_BGR2GRAY)
        
        # Sharpness (Laplacian variance)
        sharpness_orig = cv2.Laplacian(gray_orig, cv2.CV_64F).var()
        sharpness_rest = cv2.Laplacian(gray_rest, cv2.CV_64F).var()
        
        # Contrast (standard deviation)
        contrast_orig = np.std(gray_orig)
        contrast_rest = np.std(gray_rest)
        
        # Brightness
        brightness_orig = np.mean(gray_orig)
        brightness_rest = np.mean(gray_rest)
        
        return {
            'sharpness_improvement': sharpness_rest / (sharpness_orig + 1e-6),
            'contrast_improvement': contrast_rest / (contrast_orig + 1e-6),
            'brightness_orig': brightness_orig,
            'brightness_rest': brightness_rest,
            'quality_score': (sharpness_rest / 100 + contrast_rest / 50) / 2  # Normalized
        }


class SuperResolutionEnhancer:
    """Real-ESRGAN super-resolution enhancement"""
    
    def __init__(self, model_path: str, device='cpu', scale=4):
        """
        Initialize Real-ESRGAN
        
        Args:
            model_path: Path to RealESRGAN model
            device: 'cpu' or 'cuda'
            scale: Upscaling factor
        """
        self.device = device
        self.scale = scale
        
        try:
            from basicsr.archs.rrdbnet_arch import RRDBNet
            from realesrgan import RealESRGANer
        except ImportError:
            raise ImportError("Please install Real-ESRGAN: pip install realesrgan")
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Real-ESRGAN model not found at {model_path}. "
                f"Please download from: "
                f"https://github.com/xinntao/Real-ESRGAN/releases/download/v0.2.5.0/RealESRGAN_x4plus.pth"
            )
        
        # Initialize model
        model = RRDBNet(
            num_in_ch=3,
            num_out_ch=3,
            num_feat=64,
            num_block=23,
            num_grow_ch=32,
            scale=scale
        )
        
        self.upsampler = RealESRGANer(
            scale=scale,
            model_path=model_path,
            model=model,
            tile=0,  # No tiling for small face images
            tile_pad=10,
            pre_pad=0,
            half=False,  # Use full precision
            device=device
        )
        
        print(f"✓ Real-ESRGAN loaded on {device}")
    
    def enhance(self, image: np.ndarray, outscale: Optional[int] = None) -> np.ndarray:
        """
        Upscale image using Real-ESRGAN
        
        Args:
            image: Input image (BGR format)
            outscale: Output scale factor (if different from model scale)
            
        Returns:
            Upscaled image
        """
        if image is None or image.size == 0:
            raise ValueError("Invalid input image")
        
        # Check if image is too small and needs enhancement
        min_dim = min(image.shape[0], image.shape[1])
        
        if min_dim < 64:  # Very low resolution
            outscale = outscale or self.scale
        else:
            outscale = outscale or 2  # Less aggressive for decent quality
        
        # Enhance
        enhanced, _ = self.upsampler.enhance(image, outscale=outscale)
        
        return enhanced
    
    def should_enhance(self, image: np.ndarray, threshold: int = 64) -> bool:
        """
        Determine if image needs super-resolution
        
        Args:
            image: Input image
            threshold: Minimum dimension threshold
            
        Returns:
            True if enhancement is recommended
        """
        min_dim = min(image.shape[0], image.shape[1])
        return min_dim < threshold
