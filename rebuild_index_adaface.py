"""
Rebuild FAISS index with AdaFace embeddings
This script processes all images in trainset/ and builds a new FAISS index with AdaFace
"""
import os
import cv2
import numpy as np
from pathlib import Path
from backend.models.adaface_model import AdaFaceModel
from backend.models.face_detection import FaceDetector
from backend.models.vector_db import FAISSVectorDB
from backend.config import settings

def rebuild_index():
    """Rebuild FAISS index with AdaFace embeddings"""
    
    print("=" * 70)
    print("Rebuilding FAISS Index with AdaFace Embeddings")
    print("=" * 70)
    
    # Initialize models
    print("\n1. Initializing AdaFace model...")
    adaface = AdaFaceModel(
        model_path=settings.adaface_model_path,
        device='cpu'
    )
    
    print("\n2. Initializing Face Detector...")
    face_detector = FaceDetector(device='cpu')
    
    print("\n3. Creating new FAISS index (512-D for AdaFace)...")
    vector_db = FAISSVectorDB(
        embedding_dim=512,  # AdaFace uses 512-D embeddings
        metric='cosine'
    )
    
    # Process trainset
    trainset_path = Path("./trainset")
    
    if not trainset_path.exists():
        print(f"Error: Trainset not found at {trainset_path}")
        return
    
    print(f"\n4. Processing images from {trainset_path}...")
    print("-" * 70)
    
    processed_count = 0
    error_count = 0
    
    # Iterate through student folders
    for student_folder in sorted(trainset_path.iterdir()):
        if not student_folder.is_dir():
            continue
        
        student_id = student_folder.name
        print(f"\n📁 Processing Student ID: {student_id}")
        
        # Process each image folder for this student
        image_folders = sorted([f for f in student_folder.iterdir() if f.is_dir()])
        
        for img_folder in image_folders:
            # Find first image in folder (prefer _script.jpg)
            image_files = list(img_folder.glob("*_script.jpg"))
            if not image_files:
                image_files = list(img_folder.glob("*.jpg")) + list(img_folder.glob("*.png"))
            
            if not image_files:
                continue
            
            image_path = image_files[0]
            
            try:
                # Load image
                image = cv2.imread(str(image_path))
                if image is None:
                    print(f"  ✗ Failed to load: {image_path.name}")
                    error_count += 1
                    continue
                
                # Detect and align face
                aligned_face, face_info = face_detector.detect_and_align(
                    image,
                    output_size=(112, 112)
                )
                
                if aligned_face is None:
                    print(f"  ✗ No face detected: {image_path.name}")
                    error_count += 1
                    continue
                
                # Extract AdaFace embedding
                embedding = adaface.extract_embedding(aligned_face)
                
                if embedding is None:
                    print(f"  ✗ Failed to extract embedding: {image_path.name}")
                    error_count += 1
                    continue
                
                # Add to FAISS index
                metadata = {
                    'name': f"Student {student_id}",
                    'department': get_department(student_id),
                    'image_path': str(image_path)
                }
                
                vector_db.add_embedding(
                    embedding=embedding,
                    student_id=student_id,
                    metadata=metadata
                )
                
                print(f"  ✓ Processed: {image_path.name} | Embedding shape: {embedding.shape}")
                processed_count += 1
                
            except Exception as e:
                print(f"  ✗ Error processing {image_path.name}: {e}")
                error_count += 1
    
    print("\n" + "=" * 70)
    print(f"✓ Index rebuild complete!")
    print(f"  - Processed: {processed_count} images")
    print(f"  - Errors: {error_count}")
    print(f"  - Total vectors: {vector_db.index.ntotal}")
    print("=" * 70)
    
    # Save index
    print("\n5. Saving FAISS index and metadata...")
    vector_db.save(
        index_path=settings.faiss_index_path,
        metadata_path=settings.faiss_metadata_path
    )
    
    print(f"✓ Saved to:")
    print(f"  - Index: {settings.faiss_index_path}")
    print(f"  - Metadata: {settings.faiss_metadata_path}")
    print("\n✅ Done! You can now use identification with AdaFace embeddings.\n")


def get_department(student_id: str) -> str:
    """Get department based on student ID"""
    departments = {
        '0001': 'Electrical Engineering',
        '0002': 'Mechanical Engineering',
        '0003': 'Civil Engineering',
        '0005': 'Electronics Engineering',
        '0006': 'Computer Science',
        '0007': 'Electrical Engineering',
        '0008': 'Mechanical Engineering',
        '0009': 'Civil Engineering',
        '0010': 'Information Technology',
        '0012': 'Computer Science',
        '0013': 'Electrical Engineering',
        '0014': 'Mechanical Engineering',
    }
    
    # Check if it's a known student ID from trainset
    if student_id in departments:
        return departments[student_id]
    
    # For custom registered students, default to CSE
    return 'Computer Science'


if __name__ == "__main__":
    rebuild_index()
