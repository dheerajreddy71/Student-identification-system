"""
Module for classifying identification failures and providing user-friendly explanations
"""

import numpy as np
from typing import Dict, Optional


def classify_failure(
    face_detected: bool,
    face_info: Optional[Dict] = None,
    embedding: Optional[np.ndarray] = None,
    similarity: Optional[float] = None,
    threshold: float = 0.45
) -> Dict[str, str]:
    """
    Determine why identification failed and return a user-friendly explanation.
    
    Args:
        face_detected: Whether a face was detected
        face_info: Face detection information (box, confidence, keypoints)
        embedding: Extracted embedding vector (or None if extraction failed)
        similarity: Similarity score with best match (or None if no match)
        threshold: Similarity threshold for identification
        
    Returns:
        Dictionary with status, reason, and advice fields
    """
    
    # Case 1: No face detected at all
    if not face_detected:
        return {
            "status": "no_face",
            "reason": "No face detected in image.",
            "advice": "Ensure your face is clearly visible, frontal, and well-lit."
        }
    
    # Case 2: Face detected but too small
    if face_info and 'box' in face_info:
        w = face_info['box'][2]
        h = face_info['box'][3]
        
        if w < 50 or h < 50:
            return {
                "status": "face_too_small",
                "reason": f"Face detected but too small ({w}×{h} px).",
                "advice": "Move closer to the camera or use a higher resolution photo."
            }
    
    # Case 3: Embedding generation failed (None or near-zero norm)
    if embedding is None:
        return {
            "status": "embedding_failed",
            "reason": "Embedding generation failed (low-quality face).",
            "advice": "Image is too blurry or pixelated. Please retake the photo clearly."
        }
    
    # Check embedding quality
    if isinstance(embedding, np.ndarray):
        norm = np.linalg.norm(embedding)
        if norm < 1e-3:
            return {
                "status": "embedding_failed",
                "reason": f"Embedding norm too low ({norm:.6f}) - poor quality face.",
                "advice": "Image quality too poor for identification. Retake with better lighting and focus."
            }
    
    # Case 4: Valid embedding but similarity below threshold
    if similarity is not None and similarity < threshold:
        return {
            "status": "low_similarity",
            "reason": f"Face detected but similarity ({similarity:.3f}) below threshold ({threshold:.3f}).",
            "advice": "Try a clearer, frontal photo with consistent lighting. Photo may look very different from registration."
        }
    
    # Case 5: Unknown failure
    return {
        "status": "unknown",
        "reason": "Identification failed for unknown reason.",
        "advice": "Please retake the photo or contact administrator."
    }


def get_failure_statistics(results: list) -> Dict[str, int]:
    """
    Analyze failure reasons across multiple test results
    
    Args:
        results: List of result dictionaries with 'failure_reason' field
        
    Returns:
        Dictionary mapping failure reasons to counts
    """
    from collections import Counter
    
    # Extract failure reasons from failed results
    failure_reasons = [
        r.get('failure_reason', 'Unknown')
        for r in results
        if r.get('result') != 'correct_rank1' and 'failure_reason' in r
    ]
    
    return dict(Counter(failure_reasons))


def print_failure_breakdown(results: list):
    """
    Print a formatted breakdown of failure reasons
    
    Args:
        results: List of result dictionaries
    """
    stats = get_failure_statistics(results)
    
    if not stats:
        print("\n✅ No failures to analyze!")
        return
    
    print("\n" + "="*80)
    print("FAILURE BREAKDOWN BY REASON")
    print("="*80)
    
    total_failures = sum(stats.values())
    
    for reason, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
        percentage = (count / total_failures) * 100
        print(f"• {reason}")
        print(f"  Count: {count} ({percentage:.1f}% of failures)")
        print()
    
    print(f"Total failures: {total_failures}")
    print("="*80)
