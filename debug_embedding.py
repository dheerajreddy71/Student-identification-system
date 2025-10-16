#!/usr/bin/env python3
"""
Debug script to check embedding dimensions
"""
import os
import sys
import numpy as np
import cv2

# Add backend to path
sys.path.append('backend')

from backend.config import Settings
from backend.services.preprocessing_pipeline import PreprocessingPipeline
from backend.models.vector_db import FAISSVectorDB

# Initialize
settings = Settings()
print(f"Config embedding_dimension: {settings.embedding_dimension}")

# Test preprocessing pipeline
pipeline = PreprocessingPipeline()
print("Testing embedding extraction...")

# Find a test image
test_image = None
for root, dirs, files in os.walk("trainset"):
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png')):
            test_image = os.path.join(root, file)
            break
    if test_image:
        break

if test_image:
    print(f"Using test image: {test_image}")
    
    # Load image properly
    image = cv2.imread(test_image)
    if image is None:
        print("Failed to load image!")
        sys.exit(1)
    
    # Extract embedding
    embedding, metrics = pipeline.extract_embedding(image)
    
    if embedding is None:
        print("Failed to extract embedding!")
        sys.exit(1)
        
    print(f"Extracted embedding shape: {embedding.shape}")
    print(f"Embedding dimension: {embedding.shape[0]}")
    print(f"Processing metrics: {metrics}")
    
    # Test FAISS initialization
    print("\nTesting FAISS initialization...")
    vector_db = FAISSVectorDB(embedding_dim=settings.embedding_dimension)
    print(f"FAISS index dimension: {vector_db.index.d}")
    print(f"Expected dimension: {settings.embedding_dimension}")
    
    # Check if they match
    if embedding.shape[0] != vector_db.index.d:
        print(f"MISMATCH! Embedding: {embedding.shape[0]}, FAISS: {vector_db.index.d}")
    else:
        print("Dimensions match!")
        
else:
    print("No test image found!")