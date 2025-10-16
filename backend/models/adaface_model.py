"""
AdaFace model for robust face embedding generation
Handles quality-adaptive embeddings that work well with poor image quality
"""
import torch
import torch.nn as nn
import numpy as np
import cv2
from typing import Union, List, Optional
import os


class AdaFaceModel:
    """AdaFace face recognition model"""
    
    def __init__(self, model_path: str, device='cpu', embedding_size=512):
        """
        Initialize AdaFace model
        
        Args:
            model_path: Path to AdaFace checkpoint (.ckpt)
            device: 'cpu' or 'cuda'
            embedding_size: Dimension of embeddings (512 for AdaFace)
        """
        self.device = device
        self.embedding_size = embedding_size
        
        # Check if model exists
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"AdaFace model not found at {model_path}. "
                f"Please download from: "
                f"https://github.com/mk-minchul/AdaFace/releases/download/v1.0/adaface_ir101_webface12m.ckpt"
            )
        
        # Load model
        self.model = self._load_model(model_path)
        self.model.to(device)
        self.model.eval()
        
        print(f"✓ AdaFace loaded on {device}")
    
    def _load_model(self, model_path: str):
        """Load AdaFace model from checkpoint"""
        try:
            # Import AdaFace architecture
            from .adaface_architecture import build_model
            
            # Load checkpoint
            print(f"Loading checkpoint from {model_path}...")
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # Build model
            print("Building IR-101 architecture...")
            model = build_model('ir_101')
            
            # Load weights
            state_dict = checkpoint.get('state_dict', checkpoint)
            
            # Strip "model." prefix if present
            print(f"Processing {len(state_dict)} weights...")
            if any(key.startswith('model.') for key in state_dict.keys()):
                new_state_dict = {}
                for key, value in state_dict.items():
                    if key.startswith('model.'):
                        new_key = key[6:]  # Remove "model." prefix
                        new_state_dict[new_key] = value
                    else:
                        new_state_dict[key] = value
                state_dict = new_state_dict
            
            # Load with strict=False to ignore head weights
            print("Loading weights into model...")
            missing_keys, unexpected_keys = model.load_state_dict(state_dict, strict=False)
            
            if missing_keys:
                print(f"⚠ Missing keys: {len(missing_keys)} (this is OK if they're head weights)")
            if unexpected_keys:
                print(f"⚠ Unexpected keys: {len(unexpected_keys)} (skipped)")
            
            print("✓ AdaFace model loaded successfully")
            return model
            
        except Exception as e:
            print(f"Error loading model: {e}")
            # Fallback: Use custom implementation
            print("Using custom AdaFace implementation")
            return self._build_custom_model(model_path)
    
    def _build_custom_model(self, model_path: str):
        """Build custom AdaFace model"""
        from .adaface_architecture import IR_101, AdaFaceHead
        
        # Build backbone
        backbone = IR_101(input_size=(112, 112))
        
        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)
        
        # Load backbone weights
        if 'state_dict' in checkpoint:
            state_dict = checkpoint['state_dict']
        else:
            state_dict = checkpoint
        
        # Filter backbone weights
        backbone_dict = {k.replace('backbone.', ''): v for k, v in state_dict.items() 
                        if 'backbone' in k}
        backbone.load_state_dict(backbone_dict, strict=False)
        
        return backbone
    
    def preprocess(self, face_image: np.ndarray) -> torch.Tensor:
        """
        Preprocess face image for AdaFace
        
        Args:
            face_image: Face image (BGR format, any size)
            
        Returns:
            Preprocessed tensor (1, 3, 112, 112)
        """
        # Resize to 112x112
        face = cv2.resize(face_image, (112, 112))
        
        # Convert BGR to RGB
        face = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
        
        # Normalize to [0, 1]
        face = face.astype(np.float32) / 255.0
        
        # Normalize with ImageNet stats
        mean = np.array([0.5, 0.5, 0.5])
        std = np.array([0.5, 0.5, 0.5])
        face = (face - mean) / std
        
        # Convert to tensor (C, H, W)
        face = torch.from_numpy(face.transpose(2, 0, 1)).float()
        
        # Add batch dimension (1, C, H, W)
        face = face.unsqueeze(0)
        
        return face
    
    @torch.no_grad()
    def extract_embedding(self, face_image: np.ndarray, 
                         normalize: bool = True) -> np.ndarray:
        """
        Extract embedding from face image
        
        Args:
            face_image: Face image (BGR format)
            normalize: Whether to L2-normalize the embedding
            
        Returns:
            Embedding vector (512-D)
        """
        # Preprocess
        face_tensor = self.preprocess(face_image).to(self.device)
        
        # Extract embedding
        embedding = self.model(face_tensor)
        
        # Convert to numpy
        embedding = embedding.cpu().numpy().flatten()
        
        # Normalize
        if normalize:
            embedding = embedding / (np.linalg.norm(embedding) + 1e-8)
        
        return embedding
    
    @torch.no_grad()
    def extract_embeddings_batch(self, face_images: List[np.ndarray], 
                                normalize: bool = True) -> np.ndarray:
        """
        Extract embeddings from multiple face images
        
        Args:
            face_images: List of face images
            normalize: Whether to L2-normalize embeddings
            
        Returns:
            Embeddings array (N, 512)
        """
        if not face_images:
            return np.array([])
        
        # Preprocess all images
        face_tensors = [self.preprocess(face) for face in face_images]
        batch_tensor = torch.cat(face_tensors, dim=0).to(self.device)
        
        # Extract embeddings
        embeddings = self.model(batch_tensor)
        
        # Convert to numpy
        embeddings = embeddings.cpu().numpy()
        
        # Normalize
        if normalize:
            norms = np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8
            embeddings = embeddings / norms
        
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, 
                          embedding2: np.ndarray,
                          metric: str = 'cosine') -> float:
        """
        Compute similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            metric: 'cosine' or 'euclidean'
            
        Returns:
            Similarity score
        """
        if metric == 'cosine':
            # Cosine similarity
            similarity = np.dot(embedding1, embedding2)
            return float(similarity)
        
        elif metric == 'euclidean':
            # Euclidean distance (convert to similarity)
            distance = np.linalg.norm(embedding1 - embedding2)
            similarity = 1.0 / (1.0 + distance)
            return float(similarity)
        
        else:
            raise ValueError(f"Unknown metric: {metric}")
    
    def verify(self, face1: np.ndarray, face2: np.ndarray, 
              threshold: float = 0.45) -> tuple:
        """
        Verify if two faces belong to same person
        
        Args:
            face1: First face image
            face2: Second face image
            threshold: Similarity threshold
            
        Returns:
            (is_same_person, similarity_score)
        """
        # Extract embeddings
        emb1 = self.extract_embedding(face1)
        emb2 = self.extract_embedding(face2)
        
        # Compute similarity
        similarity = self.compute_similarity(emb1, emb2)
        
        # Compare with threshold
        is_same = similarity >= threshold
        
        return is_same, similarity


def load_adaface_model(model_path: str, device='cpu'):
    """
    Convenience function to load AdaFace model
    
    Args:
        model_path: Path to model checkpoint
        device: 'cpu' or 'cuda'
        
    Returns:
        AdaFaceModel instance
    """
    return AdaFaceModel(model_path, device)
