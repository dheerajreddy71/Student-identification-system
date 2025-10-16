"""
Re-register custom students with AdaFace embeddings
This script processes students from the database that aren't in trainset/
"""
import cv2
import numpy as np
from pathlib import Path
from backend.config import get_db
from backend.database.operations import StudentDB
from backend.models.adaface_model import AdaFaceModel
from backend.models.face_detection import FaceDetector
from backend.models.vector_db import FAISSVectorDB

print("=" * 70)
print("Re-registering Custom Students with AdaFace")
print("=" * 70)

# Initialize models
print("\n1. Loading AdaFace model...")
adaface = AdaFaceModel(
    model_path="./models/adaface_ir101_webface12m.ckpt",
    device="cpu"
)
print("✓ AdaFace loaded")

print("\n2. Loading face detector...")
detector = FaceDetector()
print("✓ Face detector loaded")

print("\n3. Loading FAISS index...")
vector_db = FAISSVectorDB(
    index_path="./data/faiss_index.bin",
    metadata_path="./data/faiss_metadata.json"
)
print(f"✓ FAISS loaded: {vector_db.index.ntotal} vectors, {vector_db.index.d}D")

# Get students from database
print("\n4. Getting custom registered students...")
db = next(get_db())
all_students = StudentDB.get_all_students(db)

# Filter custom students (not in trainset 0001-0014)
custom_students = [s for s in all_students if not any(
    s.student_id.startswith(str(i).zfill(4)) for i in range(1, 15)
)]

print(f"✓ Found {len(custom_students)} custom students to re-register")

# Process each custom student
successful = 0
failed = 0

for student in custom_students:
    print(f"\n📝 Processing: {student.name} (ID: {student.student_id})")
    
    # Check if photo exists
    photo_path = Path(student.photo_path)
    # Make path absolute if it's relative
    if not photo_path.is_absolute():
        photo_path = Path("C:/Users/byred/Desktop/Student Identification System") / photo_path
    
    if not photo_path.exists():
        print(f"  ✗ Photo not found: {photo_path}")
        failed += 1
        continue
    
    print(f"  📷 Loading from: {photo_path}")
    
    # Load image
    image = cv2.imread(str(photo_path))
    if image is None:
        print(f"  ✗ Failed to load image")
        failed += 1
        continue
    
    # Detect face
    faces = detector.detect_faces(image)
    if not faces or len(faces) == 0:
        print(f"  ✗ No face detected")
        failed += 1
        continue
    
    face = faces[0]
    x, y, w, h = face['box']
    
    # Extract and align face
    face_img = image[y:y+h, x:x+w]
    face_resized = cv2.resize(face_img, (112, 112))
    
    # Extract AdaFace embedding
    embedding = adaface.extract_embedding(face_resized)
    
    if embedding is None or embedding.shape[0] != 512:
        print(f"  ✗ Failed to extract embedding")
        failed += 1
        continue
    
    # Add to FAISS
    faiss_idx = vector_db.add_embedding(
        embedding,
        student.student_id,
        metadata={
            "name": student.name,
            "department": student.department,
            "year": student.year,
            "roll_number": student.roll_number
        }
    )
    
    # Update database with new FAISS index
    student.faiss_index = faiss_idx
    db.commit()
    
    print(f"  ✓ Re-registered with FAISS index: {faiss_idx}")
    print(f"  ✓ Embedding shape: {embedding.shape}")
    successful += 1

print("\n" + "=" * 70)
print(f"✅ Re-registration complete!")
print(f"  - Successful: {successful}")
print(f"  - Failed: {failed}")
print(f"  - Total vectors in FAISS: {vector_db.index.ntotal}")
print("=" * 70)

print("\n5. Saving updated FAISS index...")
vector_db.save()
print("✓ Saved!")

print("\n✅ Done! Custom students are now registered with AdaFace embeddings.")
