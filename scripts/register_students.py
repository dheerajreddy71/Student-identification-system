"""
Register all students from trainset directory
"""
import sys
import os
import cv2
import json
from pathlib import Path
from tqdm import tqdm
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.config import settings, SessionLocal
from backend.database.operations import StudentDB
from backend.services.preprocessing_pipeline import create_pipeline
from backend.models.vector_db import FAISSVectorDB


def parse_student_id(folder_name):
    """Parse student ID from folder name (e.g., '0001' from '0001')"""
    return folder_name


def get_best_image(student_folder):
    """
    Select the best image from student folder (searches recursively)
    Priority: *_script.jpg > largest file > first image
    """
    # Search recursively for images
    images = list(student_folder.rglob("*.jpg")) + list(student_folder.rglob("*.png"))
    
    if not images:
        return None
    
    # Check for script image (ID card photo)
    script_images = [img for img in images if 'script' in img.name.lower()]
    if script_images:
        return script_images[0]
    
    # Return largest image (usually better quality)
    return max(images, key=lambda p: p.stat().st_size)


def extract_student_info(student_id, image_path):
    """
    Extract student information
    In production, this would query from actual student database
    """
    # Default information (customize based on your data source)
    departments = [
        "Computer Science", "Electrical Engineering", "Mechanical Engineering",
        "Civil Engineering", "Information Technology", "Electronics Engineering"
    ]
    
    dept_idx = int(student_id) % len(departments)
    
    return {
        "student_id": student_id,
        "name": f"Student {student_id}",  # Replace with actual name
        "department": departments[dept_idx],
        "year": (int(student_id) % 4) + 1,
        "roll_number": f"ROLL-{student_id}",
        "email": f"student{student_id}@university.edu",
        "phone": f"+1-555-{student_id}",
        "address": f"{student_id} University Ave"
    }


def register_students_from_trainset(trainset_path, batch_size=10, skip_existing=True):
    """
    Register all students from trainset directory
    
    Args:
        trainset_path: Path to trainset directory
        batch_size: Number of students to process in parallel
        skip_existing: Skip students already registered
    """
    trainset_path = Path(trainset_path)
    
    if not trainset_path.exists():
        print(f"Error: Trainset directory not found: {trainset_path}")
        return
    
    print("=" * 70)
    print("Student Registration from Trainset")
    print("=" * 70)
    print()
    
    # Initialize pipelines
    print("Initializing preprocessing pipeline...")
    preprocessing, _ = create_pipeline(device=settings.device)
    
    # Initialize vector database
    print("Initializing FAISS vector database...")
    vector_db = FAISSVectorDB(
        embedding_dim=settings.embedding_dimension,
        index_path=settings.faiss_index_path,
        metadata_path=settings.faiss_metadata_path,
        metric='cosine'
    )
    
    # Get database session
    db = SessionLocal()
    
    # Find all student folders
    student_folders = sorted([f for f in trainset_path.iterdir() if f.is_dir()])
    print(f"Found {len(student_folders)} student folders\n")
    
    # Statistics
    stats = {
        'total': len(student_folders),
        'registered': 0,
        'skipped': 0,
        'failed': 0,
        'no_face': 0,
        'no_image': 0
    }
    
    # Process each student
    print("Processing students...")
    print()
    
    for student_folder in tqdm(student_folders, desc="Registering students"):
        student_id = parse_student_id(student_folder.name)
        
        try:
            # Check if already registered
            if skip_existing:
                existing = StudentDB.get_student_by_id(db, student_id)
                if existing:
                    stats['skipped'] += 1
                    continue
            
            # Get best image
            image_path = get_best_image(student_folder)
            
            if image_path is None:
                tqdm.write(f"WARNING: No images found for student {student_id}")
                stats['no_image'] += 1
                continue
            
            # Load image
            image = cv2.imread(str(image_path))
            if image is None:
                tqdm.write(f"WARNING: Could not load image for student {student_id}")
                stats['failed'] += 1
                continue
            
            # Process image
            embedding, preprocessed_face, metrics = preprocessing.process_for_registration(
                str(image_path)
            )
            
            if embedding is None:
                tqdm.write(f"WARNING: No face detected for student {student_id}")
                stats['no_face'] += 1
                continue
            
            # Get student info
            student_info = extract_student_info(student_id, image_path)
            
            # Add to FAISS
            faiss_idx = vector_db.add_embedding(
                embedding,
                student_id,
                metadata={
                    "name": student_info["name"],
                    "department": student_info["department"],
                    "image_path": str(image_path)
                }
            )
            
            # Add to database
            student_data = {
                **student_info,
                "faiss_index": faiss_idx,
                "photo_path": str(image_path)
            }
            
            student = StudentDB.create_student(db, student_data)
            stats['registered'] += 1
            
            # Save periodically
            if stats['registered'] % 10 == 0:
                vector_db.save()
                db.commit()
        
        except Exception as e:
            import traceback
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            tqdm.write(f"ERROR processing student {student_id}: {error_msg}")
            stats['failed'] += 1
            continue
    
    # Final save
    print("\nSaving database...")
    vector_db.save()
    db.commit()
    db.close()
    
    # Print statistics
    print()
    print("=" * 70)
    print("Registration Complete!")
    print("=" * 70)
    print(f"Total students:        {stats['total']}")
    print(f"Successfully registered: {stats['registered']}")
    print(f"Skipped (existing):    {stats['skipped']}")
    print(f"Failed (error):        {stats['failed']}")
    print(f"No face detected:      {stats['no_face']}")
    print(f"No images found:       {stats['no_image']}")
    print("=" * 70)
    print()
    print(f"FAISS index saved to: {settings.faiss_index_path}")
    print(f"Metadata saved to: {settings.faiss_metadata_path}")
    
    # Save registration report
    report_path = "data/registration_report.json"
    with open(report_path, 'w') as f:
        json.dump(stats, f, indent=2)
    print(f"Registration report saved to: {report_path}")


def main():
    parser = argparse.ArgumentParser(description="Register students from trainset")
    parser.add_argument(
        "--data_dir",
        type=str,
        default="trainset",
        help="Path to trainset directory"
    )
    parser.add_argument(
        "--batch_size",
        type=int,
        default=10,
        help="Batch size for processing"
    )
    parser.add_argument(
        "--skip_existing",
        action="store_true",
        default=True,
        help="Skip already registered students"
    )
    
    args = parser.parse_args()
    
    register_students_from_trainset(
        trainset_path=args.data_dir,
        batch_size=args.batch_size,
        skip_existing=args.skip_existing
    )


if __name__ == "__main__":
    main()
