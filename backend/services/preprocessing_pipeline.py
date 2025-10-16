"""
Complete preprocessing pipeline:
Input image → MTCNN detect → GFPGAN restore → (optional Real-ESRGAN) → AdaFace embed → FAISS search
"""
import cv2
import numpy as np
from typing import Optional, Dict, Tuple
import time
from pathlib import Path

from backend.models.face_detection import FaceDetector
from backend.models.face_restoration import FaceRestorer, SuperResolutionEnhancer
from backend.models.adaface_model import AdaFaceModel
from backend.models.vector_db import FAISSVectorDB
from backend.config import settings


class PreprocessingPipeline:
    """Complete preprocessing pipeline for face recognition with intelligent enhancement"""
    
    def __init__(self, 
                 device: str = 'cpu',
                 use_gfpgan: bool = True,
                 use_realesrgan: bool = True):
        """
        Initialize preprocessing pipeline with enhancement capabilities
        
        Args:
            device: 'cpu' or 'cuda'
            use_gfpgan: Whether to use GFPGAN for face restoration (default: True)
            use_realesrgan: Whether to use Real-ESRGAN for super-resolution (default: True)
        
        Note:
            Enhancement is intelligently applied only when needed (quality < 70%)
            to balance quality improvement with processing speed.
        """
        self.device = device
        self.use_gfpgan = use_gfpgan
        self.use_realesrgan = use_realesrgan
        
        print("Initializing preprocessing pipeline...")
        
        # Initialize face detector
        self.face_detector = FaceDetector(device=device)
        
        # Initialize enhancement models if requested
        if self.use_gfpgan:
            try:
                from ..config import settings
                print("Initializing GFPGAN face restorer...")
                self.face_restorer = FaceRestorer(
                    model_path=settings.gfpgan_model_path,
                    device=device,
                    upscale=2
                )
                print("✓ GFPGAN initialized successfully")
            except Exception as e:
                print(f"Warning: GFPGAN initialization failed: {e}")
                self.use_gfpgan = False
        
        if self.use_realesrgan:
            try:
                from ..config import settings
                print("Initializing Real-ESRGAN super resolution...")
                self.sr_enhancer = SuperResolutionEnhancer(
                    model_path=settings.realesrgan_model_path,
                    device=device,
                    scale=4
                )
                print("✓ Real-ESRGAN initialized successfully")
            except Exception as e:
                print(f"Warning: Real-ESRGAN initialization failed: {e}")
                self.use_realesrgan = False
        
        # Initialize face recognizer (using AdaFace pre-trained model)
        # Note: FAISS index was built with AdaFace 512-D embeddings
        from ..models.adaface_model import AdaFaceModel
        self.face_recognizer = AdaFaceModel(
            model_path=settings.adaface_model_path,
            device=device
        )
        print("✓ AdaFace initialized (512-D embeddings)")
        
        print("Pipeline initialized successfully (CPU-only mode)")
    
    def preprocess_image(self, image: np.ndarray, 
                        enhance: bool = True) -> Tuple[Optional[np.ndarray], Dict]:
        """
        Complete preprocessing pipeline
        
        Args:
            image: Input image (BGR format)
            enhance: Whether to apply enhancement (GFPGAN + Real-ESRGAN)
            
        Returns:
            (preprocessed_face, metrics)
        """
        metrics = {
            'face_detected': False,
            'face_confidence': 0.0,
            'image_quality': 0.0,
            'enhanced': False,
            'super_resolved': False,
            'enhancement_needed': False
        }
        
        start_time = time.time()
        
        # Step 1: Face detection and alignment
        aligned_face, face_info = self.face_detector.detect_and_align(
            image,
            output_size=(112, 112)
        )
        
        if aligned_face is None:
            metrics['detection_time'] = float(time.time() - start_time)
            return None, metrics
        
        metrics['face_detected'] = True
        metrics['face_confidence'] = float(face_info['confidence'])  # Ensure native Python float
        
        # Estimate quality
        quality_score = self.face_detector.estimate_quality(image, face_info)
        metrics['image_quality'] = float(quality_score)  # Ensure native Python float
        
        # Intelligent enhancement decision
        # Only enhance if quality is below threshold (0.7) or image is very small
        quality_threshold = 0.7
        enhancement_needed = bool(quality_score < quality_threshold)  # Force to Python bool
        metrics['enhancement_needed'] = enhancement_needed
        
        metrics['detection_time'] = float(time.time() - start_time)
        
        # Step 2: Optional super-resolution (for very low-res images)
        if enhance and enhancement_needed and self.use_realesrgan:
            sr_start = time.time()
            
            if self.sr_enhancer.should_enhance(aligned_face, threshold=64):
                try:
                    aligned_face = self.sr_enhancer.enhance(aligned_face, outscale=2)
                    # Resize back to 112x112 after upscaling
                    aligned_face = cv2.resize(aligned_face, (112, 112))
                    metrics['super_resolved'] = True
                    print(f"Applied super-resolution enhancement (quality: {quality_score:.3f})")
                except Exception as e:
                    print(f"Warning: Super-resolution failed: {e}")
            
            metrics['sr_time'] = float(time.time() - sr_start)
        
        # Step 3: Face restoration with GFPGAN (only for poor quality images)
        if enhance and enhancement_needed and self.use_gfpgan:
            restore_start = time.time()
            
            try:
                # Store original quality
                original_quality = quality_score
                
                restored_face = self.face_restorer.restore(
                    aligned_face,
                    aligned=True,
                    weight=0.5  # Balance between input and restored
                )
                # Validate restored face
                if restored_face is not None and restored_face.size > 0:
                    aligned_face = restored_face
                    metrics['enhanced'] = True
                    
                    # Assess quality improvement
                    # Note: We're using a simple brightness/contrast metric here
                    # For a full quality comparison, you'd need the face_info with new detections
                    enhanced_quality = self.face_detector.estimate_quality(
                        cv2.resize(aligned_face, (224, 224)),  # Resize for quality check
                        {'box': [0, 0, 224, 224], 'confidence': 1.0}
                    )
                    quality_improvement = float(enhanced_quality - original_quality)
                    metrics['quality_improvement'] = quality_improvement
                    metrics['enhanced_quality'] = float(enhanced_quality)
                    
                    print(f"Applied GFPGAN enhancement: {original_quality:.3f} → {enhanced_quality:.3f} (Δ{quality_improvement:+.3f})")
                else:
                    print(f"Warning: GFPGAN returned invalid image, using original")
            except Exception as e:
                print(f"Warning: Face restoration failed: {e}")
            
            metrics['restore_time'] = float(time.time() - restore_start)
        
        # Log enhancement decision
        if enhance and not enhancement_needed:
            print(f"Skipped enhancement - good quality image (quality: {quality_score:.3f})")
        elif not enhance:
            print(f"Enhancement disabled (quality: {quality_score:.3f})")
        
        # Validate image before final resize
        if aligned_face is None or aligned_face.size == 0:
            print("Error: Face image is invalid after enhancement")
            metrics['detection_time'] = float(time.time() - start_time)
            return None, metrics
        
        # Final resize to ensure correct dimensions
        aligned_face = cv2.resize(aligned_face, (112, 112))
        
        metrics['total_preprocessing_time'] = float(time.time() - start_time)
        
        # Convert numpy types to native Python types for JSON serialization
        processed_metrics = {}
        for key, value in metrics.items():
            if isinstance(value, np.bool_):
                processed_metrics[key] = bool(value)
            elif isinstance(value, (np.integer, np.int32, np.int64)):
                processed_metrics[key] = int(value)
            elif isinstance(value, (np.floating, np.float32, np.float64)):
                processed_metrics[key] = float(value)
            elif hasattr(value, 'item'):  # other numpy scalars
                processed_metrics[key] = value.item()
            elif isinstance(value, bool):
                processed_metrics[key] = value  # native bool is fine
            elif isinstance(value, (int, float, str)):
                processed_metrics[key] = value  # native types are fine
            else:
                # Force conversion for any remaining numpy types
                try:
                    processed_metrics[key] = value.item() if hasattr(value, 'item') else value
                except:
                    processed_metrics[key] = str(value)  # fallback to string
        
        return aligned_face, processed_metrics
    
    def extract_embedding(self, image: np.ndarray, 
                         enhance: bool = True) -> Tuple[Optional[np.ndarray], Dict]:
        """
        Complete pipeline: preprocess + extract embedding
        
        Args:
            image: Input image
            enhance: Whether to apply enhancement
            
        Returns:
            (embedding, metrics)
        """
        # Preprocess
        preprocessed_face, metrics = self.preprocess_image(image, enhance)
        
        if preprocessed_face is None:
            return None, metrics
        
        # Extract embedding
        embed_start = time.time()
        embedding = self.face_recognizer.extract_embedding(preprocessed_face)
        metrics['embedding_time'] = time.time() - embed_start
        
        metrics['total_time'] = time.time() - (time.time() - metrics['total_preprocessing_time'])
        
        return embedding, metrics
    
    def process_for_registration(self, image_path: str) -> Tuple[Optional[np.ndarray], Optional[np.ndarray], Dict]:
        """
        Process image for student registration
        
        Args:
            image_path: Path to image file
            
        Returns:
            (embedding, preprocessed_face, metrics)
        """
        # Load image
        image = cv2.imread(str(image_path))
        
        if image is None:
            return None, None, {'error': 'Could not load image'}
        
        # Preprocess
        preprocessed_face, metrics = self.preprocess_image(image, enhance=True)
        
        if preprocessed_face is None:
            return None, None, metrics
        
        # Extract embedding
        embed_start = time.time()
        embedding = self.face_recognizer.extract_embedding(preprocessed_face)
        metrics['embedding_time'] = time.time() - embed_start
        
        return embedding, preprocessed_face, metrics
    
    def process_batch(self, images: list, enhance: bool = True) -> Tuple[np.ndarray, list]:
        """
        Process multiple images in batch
        
        Args:
            images: List of images (BGR format)
            enhance: Whether to apply enhancement
            
        Returns:
            (embeddings, metrics_list)
        """
        preprocessed_faces = []
        metrics_list = []
        
        # Preprocess all images
        for image in images:
            face, metrics = self.preprocess_image(image, enhance)
            if face is not None:
                preprocessed_faces.append(face)
                metrics_list.append(metrics)
            else:
                metrics_list.append(metrics)
        
        if not preprocessed_faces:
            return np.array([]), metrics_list
        
        # Extract embeddings in batch
        embed_start = time.time()
        embeddings = self.face_recognizer.extract_embeddings_batch(preprocessed_faces)
        embed_time = time.time() - embed_start
        
        # Update metrics
        for metrics in metrics_list:
            if metrics.get('face_detected'):
                metrics['embedding_time'] = embed_time / len(preprocessed_faces)
        
        return embeddings, metrics_list


class RecognitionPipeline:
    """Complete recognition pipeline including FAISS search"""
    
    def __init__(self,
                 preprocessing_pipeline: PreprocessingPipeline,
                 vector_db: FAISSVectorDB,
                 threshold: float = 0.45):
        """
        Initialize recognition pipeline
        
        Args:
            preprocessing_pipeline: Preprocessing pipeline instance
            vector_db: FAISS vector database
            threshold: Similarity threshold
        """
        self.preprocessing = preprocessing_pipeline
        self.vector_db = vector_db
        self.threshold = threshold
    
    def identify_student(self, image: np.ndarray, 
                        enhance: bool = True,
                        top_k: int = 5) -> Dict:
        """
        Identify student from image
        
        Args:
            image: Input image (BGR format)
            enhance: Whether to apply enhancement
            top_k: Number of top matches to return
            
        Returns:
            Recognition result dictionary
        """
        start_time = time.time()
        
        # Extract embedding
        embedding, metrics = self.preprocessing.extract_embedding(image, enhance)
        
        if embedding is None:
            return {
                'success': False,
                'error': 'No face detected',
                'metrics': metrics
            }
        
        # Search in FAISS
        search_start = time.time()
        matches = self.vector_db.search_with_threshold(
            embedding,
            threshold=self.threshold,
            k=top_k
        )
        metrics['search_time'] = time.time() - search_start
        
        # Prepare result
        result = {
            'success': len(matches) > 0,
            'matches': matches,
            'best_match': matches[0] if matches else None,
            'metrics': metrics,
            'total_time': time.time() - start_time
        }
        
        return result
    
    def verify_student(self, image: np.ndarray, 
                      student_id: str,
                      enhance: bool = True) -> Dict:
        """
        Verify if image belongs to specific student
        
        Args:
            image: Input image
            student_id: Student ID to verify against
            enhance: Whether to apply enhancement
            
        Returns:
            Verification result
        """
        # Identify
        result = self.identify_student(image, enhance, top_k=1)
        
        if not result['success']:
            return {
                'verified': False,
                'reason': 'No face detected or no match found',
                'metrics': result['metrics']
            }
        
        best_match = result['best_match']
        
        # Check if matched student is the target
        verified = best_match['student_id'] == student_id
        
        return {
            'verified': verified,
            'matched_student_id': best_match['student_id'],
            'similarity': best_match['similarity'],
            'threshold': self.threshold,
            'metrics': result['metrics']
        }


def create_pipeline(device: str = 'cpu') -> Tuple[PreprocessingPipeline, RecognitionPipeline]:
    """
    Create complete pipeline instances (CPU-optimized)
    
    Args:
        device: 'cpu' or 'cuda'
        
    Returns:
        (preprocessing_pipeline, recognition_pipeline)
    """
    # Initialize preprocessing with enhancement enabled
    preprocessing = PreprocessingPipeline(
        device=device,
        use_gfpgan=True,  # Enable GFPGAN face restoration
        use_realesrgan=True  # Enable Real-ESRGAN super resolution
    )
    
    # Initialize vector database
    vector_db = FAISSVectorDB(
        embedding_dim=128,  # Simple recognizer uses 128-dim embeddings
        index_path=settings.faiss_index_path,
        metadata_path=settings.faiss_metadata_path,
        metric='cosine'
    )
    
    # Initialize recognition
    recognition = RecognitionPipeline(
        preprocessing_pipeline=preprocessing,
        vector_db=vector_db,
        threshold=settings.similarity_threshold
    )
    
    return preprocessing, recognition
