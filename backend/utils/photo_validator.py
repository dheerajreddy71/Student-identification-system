"""
Photo validation module for registration quality checks
Ensures photos meet minimum quality requirements before registration
"""
import cv2
import numpy as np
from typing import Tuple, Dict, Optional
from backend.models.face_detection import FaceDetector


# Quality thresholds
MIN_FACE_SIZE = 100  # pixels (minimum for reliable identification)
RECOMMENDED_FACE_SIZE = 200  # pixels (optimal for best results)
MIN_IMAGE_SIZE = 300  # pixels (minimum image dimension)
MAX_IMAGE_SIZE = 4000  # pixels (maximum to prevent memory issues)
MIN_BRIGHTNESS = 40  # out of 255
MAX_BRIGHTNESS = 215  # out of 255
MIN_SHARPNESS = 100  # Laplacian variance threshold


class PhotoValidator:
    """Validates photos meet quality requirements for registration"""
    
    def __init__(self, device: str = 'cpu'):
        """
        Initialize photo validator
        
        Args:
            device: 'cpu' or 'cuda'
        """
        self.detector = FaceDetector(device=device)
    
    def validate_photo(self, image_path: str) -> Tuple[bool, str, Dict]:
        """
        Comprehensive photo validation for registration
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (is_valid, message, details)
            - is_valid: True if photo meets all requirements
            - message: User-friendly explanation
            - details: Dictionary with validation metrics
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return False, "Could not load image. Please check the file.", {}
        
        details = {}
        h, w = image.shape[:2]
        details['image_width'] = w
        details['image_height'] = h
        
        # Check 1: Image size
        if w < MIN_IMAGE_SIZE or h < MIN_IMAGE_SIZE:
            return False, \
                   f"Image too small ({w}×{h} px). Minimum: {MIN_IMAGE_SIZE}×{MIN_IMAGE_SIZE} px.", \
                   details
        
        if w > MAX_IMAGE_SIZE or h > MAX_IMAGE_SIZE:
            return False, \
                   f"Image too large ({w}×{h} px). Maximum: {MAX_IMAGE_SIZE}×{MAX_IMAGE_SIZE} px.", \
                   details
        
        # Check 2: Face detection
        faces = self.detector.detect_faces(image)
        if not faces:
            return False, \
                   "No face detected. Ensure your face is clearly visible and frontal.", \
                   details
        
        # Get primary face (largest)
        face = max(faces, key=lambda f: f['box'][2] * f['box'][3])
        face_w = face['box'][2]
        face_h = face['box'][3]
        
        details['face_width'] = face_w
        details['face_height'] = face_h
        details['face_confidence'] = face['confidence']
        
        # Check 3: Multiple faces warning
        if len(faces) > 1:
            return False, \
                   f"Multiple faces detected ({len(faces)}). Please ensure only one person is in the photo.", \
                   details
        
        # Check 4: Face size (critical for quality)
        if face_w < MIN_FACE_SIZE or face_h < MIN_FACE_SIZE:
            return False, \
                   f"Face too small ({face_w}×{face_h} px). Minimum: {MIN_FACE_SIZE}×{MIN_FACE_SIZE} px. Please move closer to the camera.", \
                   details
        
        # Check 5: Face detection confidence
        if face['confidence'] < 0.95:
            return False, \
                   f"Face detection confidence too low ({face['confidence']:.2f}). Please ensure clear, frontal face with good lighting.", \
                   details
        
        # Check 6: Image quality metrics
        quality_checks = self._check_image_quality(image, face)
        details.update(quality_checks)
        
        # Brightness check
        if quality_checks['brightness'] < MIN_BRIGHTNESS:
            return False, \
                   f"Image too dark (brightness: {quality_checks['brightness']:.0f}/255). Please improve lighting.", \
                   details
        
        if quality_checks['brightness'] > MAX_BRIGHTNESS:
            return False, \
                   f"Image too bright (brightness: {quality_checks['brightness']:.0f}/255). Please reduce lighting or move away from bright light.", \
                   details
        
        # Sharpness check
        if quality_checks['sharpness'] < MIN_SHARPNESS:
            return False, \
                   f"Image too blurry (sharpness: {quality_checks['sharpness']:.0f}). Please ensure camera is focused and steady.", \
                   details
        
        # All checks passed - provide quality assessment
        if face_w >= RECOMMENDED_FACE_SIZE and face_h >= RECOMMENDED_FACE_SIZE:
            quality = "Excellent"
        elif face_w >= MIN_FACE_SIZE * 1.5 and face_h >= MIN_FACE_SIZE * 1.5:
            quality = "Good"
        else:
            quality = "Acceptable"
        
        message = f"✅ Photo validation passed! Quality: {quality} (Face: {face_w}×{face_h} px)"
        
        return True, message, details
    
    def _check_image_quality(self, image: np.ndarray, face_info: Dict) -> Dict:
        """
        Check various image quality metrics
        
        Args:
            image: Input image
            face_info: Face detection information
            
        Returns:
            Dictionary with quality metrics
        """
        # Extract face region
        x, y, w, h = face_info['box']
        face_crop = image[y:y+h, x:x+w]
        
        # Convert to grayscale for analysis
        gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
        
        # 1. Brightness (mean pixel value)
        brightness = np.mean(gray)
        
        # 2. Sharpness (Laplacian variance - higher = sharper)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        sharpness = laplacian.var()
        
        # 3. Contrast (standard deviation of pixel values)
        contrast = np.std(gray)
        
        # 4. Dynamic range (max - min pixel value)
        dynamic_range = gray.max() - gray.min()
        
        return {
            'brightness': float(brightness),
            'sharpness': float(sharpness),
            'contrast': float(contrast),
            'dynamic_range': float(dynamic_range)
        }
    
    def get_recommendations(self, details: Dict) -> str:
        """
        Generate recommendations based on validation details
        
        Args:
            details: Validation details dictionary
            
        Returns:
            User-friendly recommendations string
        """
        recommendations = []
        
        if 'face_width' in details:
            face_w = details['face_width']
            if face_w < MIN_FACE_SIZE * 1.5:
                recommendations.append("• Move closer to the camera for better face detail")
        
        if 'brightness' in details:
            brightness = details['brightness']
            if brightness < 80:
                recommendations.append("• Improve lighting - use natural light or brighter room")
            elif brightness > 180:
                recommendations.append("• Reduce lighting - avoid direct sunlight or bright lamps")
        
        if 'sharpness' in details:
            sharpness = details['sharpness']
            if sharpness < 150:
                recommendations.append("• Ensure camera is focused and steady")
                recommendations.append("• Clean camera lens if necessary")
        
        if 'contrast' in details:
            contrast = details['contrast']
            if contrast < 30:
                recommendations.append("• Improve contrast - ensure good lighting and avoid flat backgrounds")
        
        if not recommendations:
            recommendations.append("• Photo quality is good!")
        
        return "\n".join(recommendations)


def quick_validate(image_path: str) -> Tuple[bool, str]:
    """
    Quick validation - just checks face presence and size
    
    Args:
        image_path: Path to image file
        
    Returns:
        Tuple of (is_valid, message)
    """
    validator = PhotoValidator()
    is_valid, message, _ = validator.validate_photo(image_path)
    return is_valid, message
