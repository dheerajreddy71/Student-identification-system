#!/usr/bin/env python3
"""
Quick quality analysis on existing test results.
Analyzes correlation between image quality and identification success.
"""
import os
import json
import cv2
import numpy as np
from pathlib import Path
import pandas as pd
from collections import defaultdict
from backend.models.face_detection import FaceDetector

def calculate_blur_score(image: np.ndarray, face_box: tuple = None) -> float:
    """Calculate image sharpness using Laplacian variance."""
    if face_box:
        x, y, w, h = face_box
        image = image[y:y+h, x:x+w]
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return laplacian.var()

def calculate_brightness(image: np.ndarray, face_box: tuple = None) -> float:
    """Calculate average brightness."""
    if face_box:
        x, y, w, h = face_box
        image = image[y:y+h, x:x+w]
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(gray)

def calculate_contrast(image: np.ndarray, face_box: tuple = None) -> float:
    """Calculate image contrast (standard deviation of pixel values)."""
    if face_box:
        x, y, w, h = face_box
        image = image[y:y+h, x:x+w]
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.std(gray)

def classify_quality(face_size: int, blur_score: float, brightness: float, contrast: float) -> str:
    """
    Classify image quality based on multiple factors.
    
    Quality Criteria:
    - High: face ≥100px, blur>150, brightness 80-180, contrast>40
    - Medium: face ≥60px, blur>50, brightness 40-200, contrast>25
    - Low: everything else
    """
    # High quality criteria
    if (face_size >= 100 and blur_score > 150 and 
        80 <= brightness <= 180 and contrast > 40):
        return "High"
    
    # Medium quality criteria
    elif (face_size >= 60 and blur_score > 50 and 
          40 <= brightness <= 200 and contrast > 25):
        return "Medium"
    
    # Low quality
    else:
        return "Low"

def get_quality_issues(face_size: int, blur_score: float, brightness: float, contrast: float) -> list:
    """Identify specific quality issues."""
    issues = []
    
    if face_size < 50:
        issues.append("face_too_small")
    elif face_size < 100:
        issues.append("face_small")
    
    if blur_score < 50:
        issues.append("very_blurry")
    elif blur_score < 100:
        issues.append("slightly_blurry")
    
    if brightness < 60:
        issues.append("too_dark")
    elif brightness > 200:
        issues.append("too_bright")
    
    if contrast < 25:
        issues.append("low_contrast")
    
    return issues

def analyze_existing_results():
    """Analyze existing test results with quality metrics."""
    print("=" * 70)
    print("QUALITY vs ACCURACY CORRELATION ANALYSIS")
    print("=" * 70)
    print()
    
    # Load existing test results
    results_file = "test_results/holdout_test_results.json"
    if not os.path.exists(results_file):
        print(f"❌ Results file not found: {results_file}")
        print("Please run test_with_holdout.py first.")
        return
    
    with open(results_file, 'r') as f:
        test_data = json.load(f)
    
    # Extract per-image results
    test_results = test_data.get('per_image_results', [])
    
    print(f"📊 Loaded {len(test_results)} test results")
    print("🔍 Analyzing image quality...")
    print()
    
    # Initialize face detector
    face_detector = FaceDetector()
    
    # Analyze each image
    enriched_results = []
    quality_stats = {"High": {"correct": 0, "total": 0},
                    "Medium": {"correct": 0, "total": 0},
                    "Low": {"correct": 0, "total": 0}}
    issue_stats = defaultdict(lambda: {"correct": 0, "total": 0})
    
    # Base path for test images
    test_dir = "test_dataset"
    
    for i, result in enumerate(test_results, 1):
        if i % 100 == 0:
            print(f"Progress: {i}/{len(test_results)}")
        
        # Construct image path
        dept = result['department']
        filename = result['filename']
        student_id = result['true_id']
        image_path = os.path.join(test_dir, dept, student_id, filename)
        
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            continue
        
        # Detect face
        try:
            faces = face_detector.detector.detect_faces(image)
            if not faces or len(faces) == 0:
                # No face detected
                result['face_size'] = 0
                result['blur_score'] = 0
                result['brightness'] = calculate_brightness(image)
                result['contrast'] = 0
                result['quality'] = "Low"
                result['quality_issues'] = ["no_face"]
            else:
                face = faces[0]
                x, y, w, h = face['box']
                face_size = min(w, h)
                
                # Calculate quality metrics
                blur_score = calculate_blur_score(image, (x, y, w, h))
                brightness = calculate_brightness(image, (x, y, w, h))
                contrast = calculate_contrast(image, (x, y, w, h))
                quality = classify_quality(face_size, blur_score, brightness, contrast)
                issues = get_quality_issues(face_size, blur_score, brightness, contrast)
                
                result['face_size'] = face_size
                result['blur_score'] = round(blur_score, 2)
                result['brightness'] = round(brightness, 2)
                result['contrast'] = round(contrast, 2)
                result['quality'] = quality
                result['quality_issues'] = issues
        
        except Exception as e:
            # Error processing image
            result['face_size'] = 0
            result['blur_score'] = 0
            result['brightness'] = 0
            result['contrast'] = 0
            result['quality'] = "Low"
            result['quality_issues'] = ["processing_error"]
        
        enriched_results.append(result)
        
        # Update statistics
        quality = result['quality']
        is_correct = (result['result'] == 'correct_rank1')
        
        quality_stats[quality]['total'] += 1
        if is_correct:
            quality_stats[quality]['correct'] += 1
        
        # Issue statistics
        for issue in result.get('quality_issues', []):
            issue_stats[issue]['total'] += 1
            if is_correct:
                issue_stats[issue]['correct'] += 1
    
    print()
    print("=" * 70)
    print("📊 QUALITY vs ACCURACY CORRELATION")
    print("=" * 70)
    print()
    
    # Display quality-based accuracy
    print("┌─────────────────────────────────────────────────────────────────┐")
    print("│  Quality Level  │  Total Images  │  Correct  │  Accuracy      │")
    print("├─────────────────────────────────────────────────────────────────┤")
    
    for quality in ["High", "Medium", "Low"]:
        stats = quality_stats[quality]
        total = stats['total']
        correct = stats['correct']
        accuracy = (correct / total * 100) if total > 0 else 0
        
        # Quality indicator
        if quality == "High":
            indicator = "🟢"
        elif quality == "Medium":
            indicator = "🟡"
        else:
            indicator = "🔴"
        
        print(f"│  {indicator} {quality:8s}    │     {total:5d}      │   {correct:5d}   │    {accuracy:5.2f}%    │")
    
    print("└─────────────────────────────────────────────────────────────────┘")
    print()
    
    # Display issue-based analysis
    print("=" * 70)
    print("🔍 QUALITY ISSUES vs ACCURACY")
    print("=" * 70)
    print()
    
    # Sort by frequency
    sorted_issues = sorted(issue_stats.items(), key=lambda x: x[1]['total'], reverse=True)
    
    print("┌───────────────────────────────────────────────────────────────────┐")
    print("│  Quality Issue        │  Count  │  Correct  │  Accuracy       │")
    print("├───────────────────────────────────────────────────────────────────┤")
    
    for issue, stats in sorted_issues[:10]:  # Top 10 issues
        total = stats['total']
        correct = stats['correct']
        accuracy = (correct / total * 100) if total > 0 else 0
        
        issue_name = issue.replace("_", " ").title()
        print(f"│  {issue_name:20s} │  {total:5d}  │   {correct:5d}   │    {accuracy:5.2f}%     │")
    
    print("└───────────────────────────────────────────────────────────────────┘")
    print()
    
    # Key insights
    print("=" * 70)
    print("💡 KEY INSIGHTS")
    print("=" * 70)
    print()
    
    high_acc = (quality_stats["High"]["correct"] / quality_stats["High"]["total"] * 100) if quality_stats["High"]["total"] > 0 else 0
    med_acc = (quality_stats["Medium"]["correct"] / quality_stats["Medium"]["total"] * 100) if quality_stats["Medium"]["total"] > 0 else 0
    low_acc = (quality_stats["Low"]["correct"] / quality_stats["Low"]["total"] * 100) if quality_stats["Low"]["total"] > 0 else 0
    
    print(f"✅ High Quality Images:   {high_acc:.2f}% accuracy ({quality_stats['High']['correct']}/{quality_stats['High']['total']})")
    print(f"⚠️  Medium Quality Images: {med_acc:.2f}% accuracy ({quality_stats['Medium']['correct']}/{quality_stats['Medium']['total']})")
    print(f"❌ Low Quality Images:    {low_acc:.2f}% accuracy ({quality_stats['Low']['correct']}/{quality_stats['Low']['total']})")
    print()
    
    if high_acc > 90:
        print("🎯 CONCLUSION: Model performs EXCELLENTLY on high-quality images!")
        print("   Failures are primarily due to poor image quality, not algorithm weakness.")
    
    print()
    
    # Save enriched results
    output_dir = "test_results"
    os.makedirs(output_dir, exist_ok=True)
    
    # JSON output
    json_file = os.path.join(output_dir, "quality_analysis.json")
    with open(json_file, 'w') as f:
        json.dump({
            'summary': {
                'total_images': len(enriched_results),
                'quality_breakdown': quality_stats,
                'issue_breakdown': dict(issue_stats)
            },
            'results': enriched_results
        }, f, indent=2)
    
    print(f"💾 Saved detailed results: {json_file}")
    
    # CSV output
    csv_file = os.path.join(output_dir, "quality_analysis.csv")
    df = pd.DataFrame(enriched_results)
    df.to_csv(csv_file, index=False)
    print(f"💾 Saved CSV: {csv_file}")
    print()

if __name__ == "__main__":
    analyze_existing_results()
