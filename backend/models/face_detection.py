"""
Face detection and alignment using MTCNN
"""
import numpy as np
import cv2
from mtcnn import MTCNN
from typing import Tuple, Optional, List, Dict
import torch
from PIL import Image


class FaceDetector:
    """MTCNN-based face detection and alignment"""
    
    def __init__(self, device='cpu'):
        """
        Initialize MTCNN detector
        
        Args:
            device: 'cpu' or 'cuda' (Note: this MTCNN version uses CPU only)
        """
        self.device = device
        # Initialize MTCNN with minimal parameters for maximum compatibility
        self.detector = MTCNN()
    
    def detect_faces(self, image: np.ndarray) -> Optional[Dict]:
        """
        Detect faces in image
        
        Args:
            image: Input image (BGR format from OpenCV)
            
        Returns:
            Dictionary with face information or None if no face detected
        """
        # Convert BGR to RGB
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect faces
        results = self.detector.detect_faces(rgb_image)
        
        if not results or len(results) == 0:
            return None
        
        # Get the most confident detection
        face = max(results, key=lambda x: x['confidence'])
        
        return {
            'box': face['box'],  # [x, y, width, height]
            'confidence': face['confidence'],
            'keypoints': face['keypoints']  # left_eye, right_eye, nose, mouth_left, mouth_right
        }
    
    def align_face(self, image: np.ndarray, face_info: Dict, 
                   output_size: Tuple[int, int] = (112, 112)) -> Optional[np.ndarray]:
        """
        Align face using facial landmarks (simplified for CPU)
        
        Args:
            image: Input image
            face_info: Face detection information from detect_faces
            output_size: Desired output size (width, height)
            
        Returns:
            Aligned face image or None
        """
        try:
            # Minimum face size check - prevent tiny faces from producing garbage embeddings
            MIN_FACE_DIM = 50  # pixels (minimum for reliable identification)
            
            # For simplicity, just crop the face without complex alignment
            # This avoids keypoint parsing issues and is more robust
            box = face_info['box']
            x, y, width, height = box
            
            # Check raw face size before processing
            if width < MIN_FACE_DIM or height < MIN_FACE_DIM:
                print(f"⚠️  Face too small ({width}×{height} px) - minimum {MIN_FACE_DIM} px required")
                return None
            
            h, w = image.shape[:2]
            
            # Add margin (20%)
            margin = int(width * 0.2)
            x = max(0, x - margin)
            y = max(0, y - margin)
            width = min(w - x, width + 2 * margin)
            height = min(h - y, height + 2 * margin)
            
            # Crop face
            face_crop = image[y:y+height, x:x+width]
            
            if face_crop.size == 0:
                return None
            
            # Choose interpolation based on whether we're upscaling or downscaling
            # INTER_CUBIC: better for upscaling small faces (preserves details)
            # INTER_AREA: better for downscaling large faces (reduces aliasing)
            src_h, src_w = face_crop.shape[:2]
            dst_w, dst_h = output_size
            if dst_w > src_w or dst_h > src_h:
                interp = cv2.INTER_CUBIC  # upscaling - preserve facial details
            else:
                interp = cv2.INTER_AREA   # downscaling - reduce artifacts
            
            aligned_face = cv2.resize(face_crop, output_size, interpolation=interp)
            
            return aligned_face
            
        except Exception as e:
            print(f"Warning: Face alignment failed: {e}")
            return None
    
    def detect_and_align(self, image: np.ndarray, 
                        output_size: Tuple[int, int] = (112, 112)) -> Tuple[Optional[np.ndarray], Optional[Dict]]:
        """
        Detect and align face in one step
        
        Args:
            image: Input image
            output_size: Desired output size
            
        Returns:
            Tuple of (aligned_face, face_info) or (None, None)
        """
        face_info = self.detect_faces(image)
        
        if face_info is None:
            return None, None
        
        aligned_face = self.align_face(image, face_info, output_size)
        
        return aligned_face, face_info
    
    def detect_multiple_faces(self, image: np.ndarray, 
                             output_size: Tuple[int, int] = (112, 112)) -> List[Tuple[np.ndarray, Dict]]:
        """
        Detect and align multiple faces
        
        Args:
            image: Input image
            output_size: Desired output size
            
        Returns:
            List of (aligned_face, face_info) tuples
        """
        rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Detect all faces
        detector_all = MTCNN(keep_all=True, device=self.device)
        results = detector_all.detect_faces(rgb_image)
        
        faces = []
        for face in results:
            face_info = {
                'box': face['box'],
                'confidence': face['confidence'],
                'keypoints': face['keypoints']
            }
            
            aligned_face = self.align_face(image, face_info, output_size)
            if aligned_face is not None:
                faces.append((aligned_face, face_info))
        
        return faces
    
    def estimate_quality(self, image: np.ndarray, face_info: Dict) -> float:
        """
        Estimate face image quality
        
        Args:
            image: Face image
            face_info: Face detection information
            
        Returns:
            Quality score (0-1)
        """
        scores = []
        
        # Detection confidence
        scores.append(face_info['confidence'])
        
        # Face size (larger is better, up to a point)
        box = face_info['box']
        face_area = box[2] * box[3]
        image_area = image.shape[0] * image.shape[1]
        size_ratio = min(face_area / image_area, 0.5) * 2  # Normalize to 0-1
        scores.append(size_ratio)
        
        # Sharpness (Laplacian variance)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        x, y, w, h = box
        face_gray = gray[y:y+h, x:x+w]
        laplacian_var = cv2.Laplacian(face_gray, cv2.CV_64F).var()
        sharpness = min(laplacian_var / 500, 1.0)  # Normalize
        scores.append(sharpness)
        
        # Brightness (check if face is well-lit)
        face_region = image[y:y+h, x:x+w]
        brightness = np.mean(face_region)
        brightness_score = 1 - abs(brightness - 128) / 128  # Optimal at 128
        scores.append(brightness_score)
        
        # Overall quality score
        quality = np.mean(scores)
        
        return quality
