#!/usr/bin/env python3
"""
Register students from trainset folder structure
trainset/DEPT/STUDENT_ID/photos.jpg
Structure: CSE/CSE001/photo1.jpg, ECE/ECE001/photo1.jpg, etc.

Note: Student details should be provided in a CSV file or manually entered.
This script only processes the facial embeddings from photos.
"""
import os
import cv2
import numpy as np
import json
from pathlib import Path
from backend.models.adaface_model import AdaFaceModel
from backend.models.face_detection import FaceDetector
from backend.models.vector_db import FAISSVectorDB
from backend.config import settings, get_db
from backend.database.operations import StudentDB
from backend.database.models import Student

def load_student_info():
    """
    Load student information from students_info.json
    Format: {
        "CSE001": {
            "name": "John Doe",
            "email": "john@university.edu",
            "phone": "+91-9876543210",
            "year": 2,
            "address": "Hostel A, Room 101"
        }
    }
    """
    info_file = Path("./trainset/students_info.json")
    if info_file.exists():
        with open(info_file, 'r') as f:
            return json.load(f)
    return {}

def extract_student_name_from_id(student_id):
    """Extract name from student ID folder or use ID as placeholder"""
    return student_id.replace('_', ' ').title()

print("="*70)
print("Student Registration System")
print("="*70)

# Load student information
print("\n1. Loading student information...")
student_info = load_student_info()
if student_info:
    print(f"Loaded info for {len(student_info)} students from students_info.json")
else:
    print("No students_info.json found. Using default values from folder structure.")

# Clear database
print("\n2. Clearing existing student records...")
db = next(get_db())
try:
    deleted = db.query(Student).delete()
    db.commit()
    print(f"Deleted {deleted} students")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()

# Load models
print("\n3. Loading AdaFace model...")
adaface = AdaFaceModel(model_path=settings.adaface_model_path, device='cpu')
print("✓ AdaFace model loaded")

print("\n4. Loading Face Detector...")
detector = FaceDetector(device='cpu')
print("✓ Face detector loaded")

print("\n5. Creating FAISS vector database...")
vector_db = FAISSVectorDB(embedding_dim=512, metric='cosine')
print("✓ FAISS database ready")

# Process trainset
print("\n6. Processing student photos from trainset/...")
trainset = Path("./trainset")

processed = 0
failed = 0
students_data = []

for dept_folder in sorted(trainset.iterdir()):
    if not dept_folder.is_dir():
        continue
    
    dept = dept_folder.name
    print(f"\n{dept}:")
    
    for student_folder in sorted(dept_folder.iterdir()):
        if not student_folder.is_dir():
            continue
        
        student_id = student_folder.name
        images = list(student_folder.glob("*.jpg")) + list(student_folder.glob("*.png"))
        
        if not images:
            print(f"  {student_id} ... No images")
            failed += 1
            continue
        
        # Process each image for this student
        embeddings = []
        for img_path in images:
            try:
                # Load image
                img = cv2.imread(str(img_path))
                if img is None:
                    print(f"    - {img_path.name}: Failed to load")
                    continue
                
                # Detect face in the image (returns single dict or None)
                face = detector.detect_faces(img)
                if not face or 'box' not in face:
                    print(f"    - {img_path.name}: No face detected")
                    continue
                
                # Extract face coordinates
                x, y, w, h = face['box']
                
                # Extract face region
                face_img = img[y:y+h, x:x+w]
                
                # Resize to 112x112 for AdaFace
                face_resized = cv2.resize(face_img, (112, 112))
                
                # Extract embedding
                emb = adaface.extract_embedding(face_resized)
                
                # Validate embedding
                if emb is not None and emb.shape[0] == 512:
                    embeddings.append(emb)
                    print(f"    - {img_path.name}: OK (embedding extracted)")
                else:
                    print(f"    - {img_path.name}: Invalid embedding")
                    
            except Exception as e:
                print(f"    - {img_path.name}: Error - {str(e)}")
                continue
        
        # Check if we got any valid embeddings
        if not embeddings:
            print(f"  {student_id} ... FAILED (no valid embeddings from {len(images)} images)")
            failed += 1
            continue
        
        # Average embeddings from multiple images for robust representation
        final_emb = np.mean(embeddings, axis=0) if len(embeddings) > 1 else embeddings[0]
        
        # Normalize embedding (important for cosine similarity)
        final_emb = final_emb / np.linalg.norm(final_emb)
        
        # Get student details from info file or use defaults
        if student_id in student_info:
            info = student_info[student_id]
            student_name = info.get('name', extract_student_name_from_id(student_id))
            year = info.get('year', 1)
            email = info.get('email', f"{student_id.lower()}@{dept.lower()}.university.edu")
            phone = info.get('phone', '')
            address = info.get('address', '')
        else:
            student_name = extract_student_name_from_id(student_id)
            year = 1
            email = f"{student_id.lower()}@{dept.lower()}.university.edu"
            phone = ''
            address = ''
        
        idx = vector_db.add_embedding(
            final_emb,
            student_id,
            metadata={
                "name": student_name,
                "department": dept,
                "year": year,
                "roll_number": student_id
            }
        )
        
        students_data.append({
            "student_id": student_id,
            "name": student_name,
            "department": dept,
            "year": year,
            "roll_number": student_id,
            "faiss_index": idx,
            "photo_path": str(student_folder.relative_to(Path("."))),
            "email": email,
            "phone": phone,
            "address": address
        })
        
        print(f"  {student_id} ({student_name}) ... SUCCESS ({len(embeddings)}/{len(images)} images, FAISS idx: {idx})")
        processed += 1

print(f"\n{'='*70}")
print(f"Processing Complete: {processed} successful | {failed} failed")
print(f"{'='*70}")

# Save FAISS
print("\n7. Saving FAISS vector database...")
vector_db.save("./data/faiss_index.bin", "./data/faiss_metadata.json")
print("✓ FAISS database saved")

# Insert into DB
print("\n8. Inserting students into database...")
inserted = 0
for data in students_data:
    try:
        StudentDB.create_student(db, data)
        inserted += 1
    except Exception as e:
        print(f"Error: {data['student_id']} - {e}")

db.commit()
print(f"✓ Successfully registered {inserted} students")

print(f"\n{'='*70}")
print("REGISTRATION COMPLETE!")
print(f"{'='*70}")
print(f"Total Embeddings in FAISS: {vector_db.index.ntotal}")
print(f"Students in Database: {inserted}")
print(f"Success Rate: {processed}/{processed+failed} ({100*processed/(processed+failed):.1f}%)")
print(f"{'='*70}")
print("\nNext steps:")
print("1. Start the backend server")
print("2. Use the web interface to identify students")
print("3. Update student details as needed")
print(f"{'='*70}")
