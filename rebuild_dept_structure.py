#!/usr/bin/env python3
"""
Rebuild FAISS index with department structure
trainset/DEPT/STUDENT_ID/photos.jpg
Structure: AGRI/ag1/ag1_1.jpg, CSE/cse1/cse1_1.jpg, etc.
"""
import os
import cv2
import numpy as np
import random
from pathlib import Path
from backend.models.adaface_model import AdaFaceModel
from backend.models.face_detection import FaceDetector
from backend.models.vector_db import FAISSVectorDB
from backend.config import settings, get_db
from backend.database.operations import StudentDB
from backend.database.models import Student

# Random name generator
FIRST_NAMES = [
    "Aarav", "Vivaan", "Aditya", "Arjun", "Sai", "Vihaan", "Krishna", "Ayaan",
    "Ananya", "Diya", "Aadhya", "Avni", "Sara", "Pari", "Isha", "Mira",
    "Rohan", "Karan", "Rudra", "Reyansh", "Aarush", "Dhruv", "Pranav", "Dev",
    "Priya", "Riya", "Pooja", "Sneha", "Kavya", "Nisha", "Simran", "Tanvi",
    "Rahul", "Amit", "Raj", "Vikram", "Nikhil", "Sanjay", "Suresh", "Anil",
    "Divya", "Meera", "Lakshmi", "Radha", "Sita", "Gita", "Kamala", "Uma"
]

LAST_NAMES = [
    "Sharma", "Verma", "Gupta", "Kumar", "Singh", "Patel", "Reddy", "Nair",
    "Iyer", "Menon", "Pillai", "Rao", "Joshi", "Desai", "Mehta", "Shah",
    "Agarwal", "Bansal", "Chopra", "Kapoor", "Malhotra", "Khanna", "Bhatia",
    "Sethi", "Arora", "Jindal", "Goel", "Mittal", "Singhal", "Garg"
]

def generate_student_name():
    """Generate random Indian student name"""
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def generate_email(student_id, dept):
    """Generate email from student ID"""
    return f"{student_id}@{dept.lower()}.university.edu"

def generate_phone():
    """Generate random Indian phone number"""
    return f"+91-{random.randint(70000,99999)}{random.randint(10000,99999)}"

print("="*70)
print("Rebuilding with Department Structure")
print("="*70)

# Clear database
print("\n1. Clearing database...")
db = next(get_db())
try:
    deleted = db.query(Student).delete()
    db.commit()
    print(f"Deleted {deleted} students")
except Exception as e:
    print(f"Error: {e}")
    db.rollback()

# Load models
print("\n2. Loading AdaFace...")
adaface = AdaFaceModel(model_path=settings.adaface_model_path, device='cpu')
print("OK")

print("\n3. Loading Face Detector...")
detector = FaceDetector(device='cpu')
print("OK")

print("\n4. Creating FAISS index...")
vector_db = FAISSVectorDB(embedding_dim=512, metric='cosine')
print("OK")

# Process trainset
print("\n5. Processing trainset...")
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
        
        # Generate student details
        student_name = generate_student_name()
        year = random.randint(1, 4)  # Random year between 1-4
        
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
            "email": generate_email(student_id, dept),
            "phone": generate_phone(),
            "address": f"Hostel Block-{random.choice(['A','B','C','D'])}, Room {random.randint(101,599)}"
        })
        
        print(f"  {student_id} ({student_name}) ... SUCCESS ({len(embeddings)}/{len(images)} images, FAISS idx: {idx})")
        processed += 1

print(f"\n{'='*70}")
print(f"Processed: {processed} | Failed: {failed}")
print(f"{'='*70}")

# Save FAISS
print("\n6. Saving FAISS...")
vector_db.save("./data/faiss_index.bin", "./data/faiss_metadata.json")
print("OK")

# Insert into DB
print("\n7. Inserting into database...")
inserted = 0
for data in students_data:
    try:
        StudentDB.create_student(db, data)
        inserted += 1
    except Exception as e:
        print(f"Error: {data['student_id']} - {e}")

db.commit()
print(f"Inserted {inserted} students")

print(f"\n{'='*70}")
print("COMPLETE!")
print(f"FAISS: {vector_db.index.ntotal} vectors")
print(f"Database: {inserted} students")
print(f"{'='*70}")
