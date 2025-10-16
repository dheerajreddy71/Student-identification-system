"""
Simple Face Recognition Model for CPU-only processing
Uses OpenCV's DNN face recognition with embeddings
"""

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple, Dict, List
import os
from sklearn.preprocessing import normalize

class SimpleFaceEncoder(nn.Module):
    """Simple CNN for face encoding"""
    
    def __init__(self, embedding_dim=128):
        super(SimpleFaceEncoder, self).__init__()
        
        # Simple CNN backbone
        self.conv1 = nn.Conv2d(3, 32, 3, padding=1)
        self.conv2 = nn.Conv2d(32, 64, 3, padding=1)
        self.conv3 = nn.Conv2d(64, 128, 3, padding=1)
        self.conv4 = nn.Conv2d(128, 256, 3, padding=1)
        
        self.pool = nn.MaxPool2d(2, 2)
        self.dropout = nn.Dropout(0.5)
        
        # Calculate the size after convolutions
        # Input: 112x112, after 4 pooling operations: 7x7
        self.fc1 = nn.Linear(256 * 7 * 7, 512)
        self.fc2 = nn.Linear(512, embedding_dim)
        
    def forward(self, x):
        # Input shape: (batch_size, 3, 112, 112)
        x = self.pool(F.relu(self.conv1(x)))  # 56x56
        x = self.pool(F.relu(self.conv2(x)))  # 28x28
        x = self.pool(F.relu(self.conv3(x)))  # 14x14
        x = self.pool(F.relu(self.conv4(x)))  # 7x7
        
        x = x.view(x.size(0), -1)  # Flatten
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = self.fc2(x)
        
        # L2 normalize embeddings
        x = F.normalize(x, p=2, dim=1)
        
        return x

class SimpleFaceRecognizer:
    """Simple face recognition system for CPU processing"""
    
    def __init__(self, device='cpu', embedding_dim=128):
        self.device = device
        self.embedding_dim = embedding_dim
        
        # Initialize model
        self.model = SimpleFaceEncoder(embedding_dim=embedding_dim)
        self.model.to(device)
        self.model.eval()
        
        # Initialize with random weights (in production, you'd train this)
        self._initialize_weights()
        
    def _initialize_weights(self):
        """Initialize model weights"""
        for m in self.model.modules():
            if isinstance(m, nn.Conv2d):
                nn.init.kaiming_normal_(m.weight, mode='fan_out', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight)
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
    
    def preprocess_face(self, face_image: np.ndarray) -> torch.Tensor:
        """
        Preprocess face image for recognition
        
        Args:
            face_image: Face image (BGR format from OpenCV)
            
        Returns:
            Preprocessed tensor
        """
        # Convert BGR to RGB
        face_rgb = cv2.cvtColor(face_image, cv2.COLOR_BGR2RGB)
        
        # Resize to 112x112
        face_resized = cv2.resize(face_rgb, (112, 112))
        
        # Normalize to [0, 1]
        face_normalized = face_resized.astype(np.float32) / 255.0
        
        # Convert to tensor and rearrange dimensions
        face_tensor = torch.from_numpy(face_normalized).permute(2, 0, 1)  # HWC -> CHW
        
        # Add batch dimension
        face_tensor = face_tensor.unsqueeze(0)
        
        return face_tensor.to(self.device)
    
    def extract_embedding(self, face_image: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face embedding
        
        Args:
            face_image: Face image (BGR format from OpenCV)
            
        Returns:
            Face embedding as numpy array
        """
        try:
            # Preprocess
            face_tensor = self.preprocess_face(face_image)
            
            # Extract embedding
            with torch.no_grad():
                embedding = self.model(face_tensor)
                embedding = embedding.cpu().numpy().flatten()
            
            return embedding
            
        except Exception as e:
            print(f"Error extracting embedding: {e}")
            return None
    
    def extract_embeddings_batch(self, face_images: List[np.ndarray]) -> List[Optional[np.ndarray]]:
        """
        Extract embeddings for multiple faces
        
        Args:
            face_images: List of face images
            
        Returns:
            List of embeddings
        """
        embeddings = []
        
        # Process in batches of 4 for CPU efficiency
        batch_size = 4
        for i in range(0, len(face_images), batch_size):
            batch = face_images[i:i + batch_size]
            
            try:
                # Preprocess batch
                batch_tensors = []
                for face_img in batch:
                    face_tensor = self.preprocess_face(face_img)
                    batch_tensors.append(face_tensor)
                
                # Stack tensors
                if batch_tensors:
                    batch_tensor = torch.cat(batch_tensors, dim=0)
                    
                    # Extract embeddings
                    with torch.no_grad():
                        batch_embeddings = self.model(batch_tensor)
                        batch_embeddings = batch_embeddings.cpu().numpy()
                    
                    # Add individual embeddings
                    for j in range(batch_embeddings.shape[0]):
                        embeddings.append(batch_embeddings[j])
                        
            except Exception as e:
                print(f"Error processing batch {i//batch_size}: {e}")
                # Add None for failed batch
                for _ in batch:
                    embeddings.append(None)
        
        return embeddings
    
    def compute_similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings
        
        Args:
            embedding1: First embedding
            embedding2: Second embedding
            
        Returns:
            Cosine similarity score
        """
        # Ensure embeddings are normalized
        embedding1 = normalize([embedding1])[0]
        embedding2 = normalize([embedding2])[0]
        
        # Compute cosine similarity
        similarity = np.dot(embedding1, embedding2)
        
        return float(similarity)
    
    def save_model(self, path: str):
        """Save model weights"""
        torch.save(self.model.state_dict(), path)
        print(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model weights"""
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path, map_location=self.device))
            print(f"Model loaded from {path}")
        else:
            print(f"Model file not found: {path}")

def create_simple_recognizer(device='cpu') -> SimpleFaceRecognizer:
    """Create a simple face recognizer"""
    return SimpleFaceRecognizer(device=device, embedding_dim=128)

if __name__ == "__main__":
    # Test the simple recognizer
    recognizer = create_simple_recognizer()
    print("Simple face recognizer created successfully!")
    
    # Test with a dummy image
    dummy_image = np.random.randint(0, 255, (112, 112, 3), dtype=np.uint8)
    embedding = recognizer.extract_embedding(dummy_image)
    
    if embedding is not None:
        print(f"Embedding shape: {embedding.shape}")
        print("✓ Simple face recognizer is working!")
    else:
        print("✗ Failed to extract embedding")