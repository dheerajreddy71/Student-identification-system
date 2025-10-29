#!/usr/bin/env python3
"""
Split trainset into training and testing sets
For each student, move some images to test folder
"""
import os
import shutil
from pathlib import Path
import random
import json

# Configuration
TRAINSET_DIR = "trainset"
TEST_DIR = "test_dataset"
TRAIN_BACKUP_DIR = "trainset_backup"
TEST_IMAGES_PER_STUDENT = 2  # Number of images to hold out for testing

def backup_trainset():
    """Create backup of original trainset"""
    if os.path.exists(TRAIN_BACKUP_DIR):
        print(f"✓ Backup already exists at {TRAIN_BACKUP_DIR}")
        return
    
    print(f"📦 Creating backup of trainset...")
    shutil.copytree(TRAINSET_DIR, TRAIN_BACKUP_DIR)
    print(f"   ✅ Backup created at {TRAIN_BACKUP_DIR}")

def prepare_test_split():
    """
    Split dataset into train and test
    Move some images from each student folder to test_dataset
    """
    print("\n" + "="*70)
    print("📊 PREPARING TRAIN-TEST SPLIT")
    print("="*70)
    
    # Create backup first
    backup_trainset()
    
    # Create test directory
    os.makedirs(TEST_DIR, exist_ok=True)
    
    stats = {
        'total_students': 0,
        'students_with_test': 0,
        'total_train_images': 0,
        'total_test_images': 0,
        'skipped_students': [],
        'test_mapping': {}
    }
    
    # Process each department
    for dept in os.listdir(TRAINSET_DIR):
        dept_path = os.path.join(TRAINSET_DIR, dept)
        if not os.path.isdir(dept_path):
            continue
        
        print(f"\n📁 Processing department: {dept}")
        dept_test_path = os.path.join(TEST_DIR, dept)
        os.makedirs(dept_test_path, exist_ok=True)
        
        # Process each student
        for student_id in os.listdir(dept_path):
            student_train_path = os.path.join(dept_path, student_id)
            if not os.path.isdir(student_train_path):
                continue
            
            stats['total_students'] += 1
            
            # Get all images
            images = [f for f in os.listdir(student_train_path) 
                     if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            
            if len(images) < 2:
                print(f"   ⚠️  {student_id}: Only {len(images)} image(s) - skipping test split")
                stats['skipped_students'].append({
                    'student_id': student_id,
                    'department': dept,
                    'reason': f'Only {len(images)} images'
                })
                stats['total_train_images'] += len(images)
                continue
            
            # Determine how many to move to test
            num_test = min(TEST_IMAGES_PER_STUDENT, len(images) - 1)  # Keep at least 1 for training
            
            # Randomly select test images
            random.seed(42)  # Reproducible split
            random.shuffle(images)
            test_images = images[:num_test]
            train_images = images[num_test:]
            
            # Create test directory for this student
            student_test_path = os.path.join(dept_test_path, student_id)
            os.makedirs(student_test_path, exist_ok=True)
            
            # Move test images
            moved_count = 0
            for img in test_images:
                src = os.path.join(student_train_path, img)
                dst = os.path.join(student_test_path, img)
                try:
                    shutil.move(src, dst)
                    moved_count += 1
                except Exception as e:
                    print(f"      ❌ Error moving {img}: {e}")
            
            if moved_count > 0:
                stats['students_with_test'] += 1
                stats['total_test_images'] += moved_count
                stats['total_train_images'] += len(train_images)
                stats['test_mapping'][student_id] = {
                    'department': dept,
                    'train_images': len(train_images),
                    'test_images': moved_count,
                    'test_files': test_images
                }
                print(f"   ✅ {student_id}: {len(train_images)} train, {moved_count} test")
    
    # Save statistics
    with open('test_split_info.json', 'w') as f:
        json.dump(stats, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("📊 SPLIT SUMMARY")
    print("="*70)
    print(f"Total Students: {stats['total_students']}")
    print(f"Students with Test Data: {stats['students_with_test']}")
    print(f"Students Skipped: {len(stats['skipped_students'])}")
    print(f"\nTotal Training Images: {stats['total_train_images']}")
    print(f"Total Test Images: {stats['total_test_images']}")
    print(f"\n✅ Split complete! Info saved to test_split_info.json")
    
    if stats['skipped_students']:
        print(f"\n⚠️  Skipped {len(stats['skipped_students'])} students (insufficient images)")
    
    print("\n" + "="*70)
    print("NEXT STEPS:")
    print("="*70)
    print("1. Run: python scripts/register_students.py --data_dir trainset")
    print("   (This will register students with NEW embeddings from remaining images)")
    print("\n2. Run: python test_with_holdout.py")
    print("   (This will test on held-out images)")
    print("="*70)
    
    return stats

if __name__ == "__main__":
    prepare_test_split()
