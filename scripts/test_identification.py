"""
Test the complete identification pipeline
"""
import sys
import os
import cv2
import time
from pathlib import Path
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.preprocessing_pipeline import create_pipeline
from backend.config import settings


def test_identification(image_path, enhance=True):
    """
    Test student identification on a single image
    
    Args:
        image_path: Path to test image
        enhance: Whether to apply enhancement
    """
    print("=" * 70)
    print("Student Identification System - Test")
    print("=" * 70)
    print()
    
    # Check if image exists
    if not os.path.exists(image_path):
        print(f"Error: Image not found: {image_path}")
        return
    
    # Load image
    print(f"Loading image: {image_path}")
    image = cv2.imread(image_path)
    
    if image is None:
        print("Error: Could not load image")
        return
    
    print(f"Image size: {image.shape[1]}x{image.shape[0]}")
    print()
    
    # Initialize pipeline
    print("Initializing pipeline...")
    preprocessing, recognition = create_pipeline(device=settings.device)
    print("✓ Pipeline initialized")
    print()
    
    # Test identification
    print("Processing image...")
    start_time = time.time()
    
    result = recognition.identify_student(image, enhance=enhance, top_k=3)
    
    total_time = time.time() - start_time
    
    print("=" * 70)
    print("Results")
    print("=" * 70)
    print()
    
    if not result['success']:
        print("✗ No match found or no face detected")
        print()
        print("Metrics:")
        for key, value in result['metrics'].items():
            print(f"  {key}: {value}")
        return
    
    # Display best match
    best_match = result['best_match']
    print("✓ Student Identified!")
    print()
    print(f"Student ID:   {best_match['student_id']}")
    print(f"Name:         {best_match['metadata'].get('name', 'N/A')}")
    print(f"Department:   {best_match['metadata'].get('department', 'N/A')}")
    print(f"Similarity:   {best_match['similarity']:.4f}")
    print(f"Threshold:    {recognition.threshold}")
    print()
    
    # Display all matches
    if len(result['matches']) > 1:
        print("Other matches:")
        for i, match in enumerate(result['matches'][1:], 1):
            print(f"  {i}. {match['student_id']} - {match['similarity']:.4f}")
        print()
    
    # Display metrics
    print("Processing Metrics:")
    print(f"  Face detected:     {result['metrics'].get('face_detected', False)}")
    print(f"  Face confidence:   {result['metrics'].get('face_confidence', 0):.4f}")
    print(f"  Image quality:     {result['metrics'].get('image_quality', 0):.4f}")
    print(f"  Enhanced:          {result['metrics'].get('enhanced', False)}")
    print(f"  Super-resolved:    {result['metrics'].get('super_resolved', False)}")
    print()
    
    print("Timing:")
    print(f"  Preprocessing:     {result['metrics'].get('total_preprocessing_time', 0):.3f}s")
    print(f"  Embedding:         {result['metrics'].get('embedding_time', 0):.3f}s")
    print(f"  FAISS search:      {result['metrics'].get('search_time', 0):.3f}s")
    print(f"  Total:             {result['total_time']:.3f}s")
    print()
    
    print("=" * 70)


def test_batch(test_dir, enhance=True):
    """
    Test on multiple images
    
    Args:
        test_dir: Directory containing test images
        enhance: Whether to apply enhancement
    """
    test_path = Path(test_dir)
    
    if not test_path.exists():
        print(f"Error: Test directory not found: {test_dir}")
        return
    
    # Find all images
    image_files = list(test_path.glob("*.jpg")) + list(test_path.glob("*.png"))
    
    if not image_files:
        print(f"No images found in {test_dir}")
        return
    
    print(f"Testing on {len(image_files)} images...")
    print()
    
    # Initialize pipeline
    preprocessing, recognition = create_pipeline(device=settings.device)
    
    # Statistics
    stats = {
        'total': len(image_files),
        'success': 0,
        'no_face': 0,
        'no_match': 0,
        'total_time': 0
    }
    
    # Test each image
    for image_file in image_files:
        print(f"Testing {image_file.name}...", end=" ")
        
        image = cv2.imread(str(image_file))
        if image is None:
            print("✗ Could not load")
            continue
        
        result = recognition.identify_student(image, enhance=enhance)
        stats['total_time'] += result['total_time']
        
        if not result['metrics'].get('face_detected'):
            print("✗ No face detected")
            stats['no_face'] += 1
        elif not result['success']:
            print("✗ No match found")
            stats['no_match'] += 1
        else:
            match = result['best_match']
            print(f"✓ {match['student_id']} ({match['similarity']:.3f})")
            stats['success'] += 1
    
    # Print summary
    print()
    print("=" * 70)
    print("Batch Test Summary")
    print("=" * 70)
    print(f"Total images:      {stats['total']}")
    print(f"Successful:        {stats['success']} ({stats['success']/stats['total']*100:.1f}%)")
    print(f"No face detected:  {stats['no_face']}")
    print(f"No match found:    {stats['no_match']}")
    print(f"Average time:      {stats['total_time']/stats['total']:.3f}s per image")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Test student identification")
    parser.add_argument(
        "image_path",
        type=str,
        help="Path to test image or directory"
    )
    parser.add_argument(
        "--no-enhance",
        action="store_true",
        help="Disable GFPGAN and Real-ESRGAN enhancement"
    )
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Test on all images in directory"
    )
    
    args = parser.parse_args()
    
    if args.batch:
        test_batch(args.image_path, enhance=not args.no_enhance)
    else:
        test_identification(args.image_path, enhance=not args.no_enhance)


if __name__ == "__main__":
    main()
