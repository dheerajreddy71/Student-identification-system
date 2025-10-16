""""""

Rebuild FAISS index with department-based structureRebuild FAISS index with department-based structure

Structure: trainset/DEPT/STUDENT_ID/photos.jpgThis script:

Where STUDENT_ID is the folder name (varies by department)1. Deletes all existing students from database and FAISS

"""2. Processes trainset with new structure: trainset/DEPT/STUDENT_ID/

import os3. Builds new FAISS index with AdaFace embeddings

import cv2"""

import numpy as npimport os

from pathlib import Pathimport cv2

from backend.models.adaface_model import AdaFaceModelimport numpy as np

from backend.models.face_detection import FaceDetectorfrom pathlib import Path

from backend.models.vector_db import FAISSVectorDBfrom backend.models.adaface_model import AdaFaceModel

from backend.config import settings, get_dbfrom backend.models.face_detection import FaceDetector

from backend.database.operations import StudentDBfrom backend.models.vector_db import FAISSVectorDB

from backend.database.models import Studentfrom backend.config import settings, get_db

from backend.database.operations import StudentDB

print("=" * 70)from backend.database.models import Student

print("Rebuilding System with Department Structure")

print("=" * 70)print("=" * 70)

print("Rebuilding System with Department Structure")

# Step 1: Clear existing databaseprint("=" * 70)

print("\n1. Clearing existing students from database...")

db = next(get_db())# Step 1: Clear existing database

try:print("\n1. Clearing existing students from database...")

    deleted_count = db.query(Student).delete()db = next(get_db())

    db.commit()try:

    print(f"OK Deleted {deleted_count} students from database")    # Delete all students

except Exception as e:    deleted_count = db.query(Student).delete()

    print(f"Error clearing database: {e}")    db.commit()

    db.rollback()    print(f"✓ Deleted {deleted_count} students from database")

except Exception as e:

# Step 2: Initialize models    print(f"✗ Error clearing database: {e}")

print("\n2. Initializing AdaFace model...")    db.rollback()

adaface = AdaFaceModel(

    model_path=settings.adaface_model_path,# Step 2: Initialize models

    device='cpu'print("\n2. Initializing AdaFace model...")

)adaface = AdaFaceModel(

print("OK AdaFace loaded")    model_path=settings.adaface_model_path,

    device='cpu'

print("\n3. Initializing Face Detector..."))

face_detector = FaceDetector(device='cpu')print("✓ AdaFace loaded")

print("OK Face detector loaded")

print("\n3. Initializing Face Detector...")

print("\n4. Creating new FAISS index (512-D for AdaFace)...")face_detector = FaceDetector(device='cpu')

vector_db = FAISSVectorDB(print("✓ Face detector loaded")

    embedding_dim=512,

    metric='cosine'print("\n4. Creating new FAISS index (512-D for AdaFace)...")

)vector_db = FAISSVectorDB(

print("OK FAISS index created")    embedding_dim=512,

    metric='cosine'

# Step 3: Process trainset)

trainset_path = Path("./trainset")print("✓ FAISS index created")



if not trainset_path.exists():# Step 3: Process trainset with department structure

    print(f"\nError: Trainset not found at {trainset_path}")trainset_path = Path("./trainset")

    exit(1)

if not trainset_path.exists():

print(f"\n5. Processing trainset: {trainset_path}")    print(f"\n✗ Error: Trainset not found at {trainset_path}")

print("   Structure: trainset/DEPARTMENT/STUDENT_ID/photos.jpg")    exit(1)

print("-" * 70)

print(f"\n5. Processing trainset from {trainset_path}...")

processed_count = 0print("   Structure: trainset/DEPARTMENT/STUDENT_ID/")

error_count = 0print("-" * 70)

students_data = []

processed_count = 0

# Iterate through department folderserror_count = 0

for dept_folder in sorted(trainset_path.iterdir()):students_data = []

    if not dept_folder.is_dir():

        continue# Iterate through department folders

    for dept_folder in sorted(trainset_path.iterdir()):

    department = dept_folder.name    if not dept_folder.is_dir():

    print(f"\nDepartment: {department}")        continue

        

    # Get all student ID folders in this department    department = dept_folder.name

    student_folders = sorted([f for f in dept_folder.iterdir() if f.is_dir()])    print(f"\n📂 Department: {department}")

        

    for student_folder in student_folders:    # Iterate through student ID folders in this department

        # The folder name IS the student ID    student_folders = sorted([f for f in dept_folder.iterdir() if f.is_dir()])

        student_id = student_folder.name    

            for student_folder in student_folders:

        # Find all image files in this student's folder        student_id = student_folder.name

        image_files = list(student_folder.glob("*.jpg")) + list(student_folder.glob("*.png"))        print(f"  👤 Processing Student: {student_id}", end=" ... ")

                

        if not image_files:        # Find all images for this student (directly in student_id folder)

            print(f"  {student_id} ... No images")        image_files = list(student_folder.glob("*_script.jpg"))

            error_count += 1        if not image_files:

            continue            image_files = list(student_folder.glob("*.jpg")) + list(student_folder.glob("*.png"))

                

        # Process images to extract embeddings        # Filter out hidden/system files

        embeddings = []        image_files = [f for f in image_files if not f.name.startswith('.')]

        valid_images = 0        

                if not image_files:

        for image_path in image_files:            print(f"    ✗ No images found")

            try:            error_count += 1

                # Load image            continue

                image = cv2.imread(str(image_path))        

                if image is None:        # Process first image (or all images for better representation)

                    continue        embeddings = []

                        

                # Detect faces        for image_path in image_files[:5]:  # Process up to 5 images per student

                faces = face_detector.detect_faces(image)            try:

                if not faces or len(faces) == 0:                # Load image

                    continue                image = cv2.imread(str(image_path))

                                if image is None:

                # Get the largest face                    continue

                face = max(faces, key=lambda f: f['box'][2] * f['box'][3])                

                x, y, w, h = face['box']                # Detect and align face

                                faces = face_detector.detect_faces(image)

                # Extract and resize face                if not faces or len(faces) == 0:

                face_img = image[y:y+h, x:x+w]                    continue

                face_resized = cv2.resize(face_img, (112, 112))                

                                # Get largest face

                # Extract AdaFace embedding                face = max(faces, key=lambda f: f['box'][2] * f['box'][3])

                embedding = adaface.extract_embedding(face_resized)                x, y, w, h = face['box']

                                

                if embedding is not None and embedding.shape[0] == 512:                # Extract face region

                    embeddings.append(embedding)                face_img = image[y:y+h, x:x+w]

                    valid_images += 1                

                                # Resize to 112x112 for AdaFace

            except Exception as e:                face_resized = cv2.resize(face_img, (112, 112))

                continue                

                        # Extract embedding

        if not embeddings:                embedding = adaface.extract_embedding(face_resized)

            print(f"  {student_id} ... Failed (no face detected)")                

            error_count += 1                if embedding is not None and embedding.shape[0] == 512:

            continue                    embeddings.append(embedding)

                        

        # Average embeddings if multiple valid images            except Exception as e:

        if len(embeddings) > 1:                continue

            final_embedding = np.mean(embeddings, axis=0)        

        else:        if not embeddings:

            final_embedding = embeddings[0]            print(f"✗ Failed")

                    error_count += 1

        # Normalize embedding            continue

        final_embedding = final_embedding / np.linalg.norm(final_embedding)        

                # Average embeddings if multiple images

        # Add to FAISS        final_embedding = np.mean(embeddings, axis=0) if len(embeddings) > 1 else embeddings[0]

        faiss_idx = vector_db.add_embedding(        

            final_embedding,        # Add to FAISS

            student_id,        faiss_idx = vector_db.add_embedding(

            metadata={            final_embedding,

                "name": f"Student {student_id}",            student_id,

                "department": department,            metadata={

                "year": 1,                "name": f"Student {student_id}",

                "roll_number": student_id                "department": department,

            }                "year": 1,  # Default, will be updated later

        )                "roll_number": student_id

                    }

        # Store for database insertion        )

        students_data.append({        

            "student_id": student_id,        # Store student data for database insertion

            "name": f"Student {student_id}",        students_data.append({

            "department": department,            "student_id": student_id,

            "year": 1,            "name": f"Student {student_id}",

            "roll_number": student_id,            "department": department,

            "faiss_index": faiss_idx,            "year": 1,

            "photo_path": str(student_folder.relative_to(Path("."))),            "roll_number": student_id,

            "email": f"{student_id}@university.edu",            "faiss_index": faiss_idx,

            "phone": None,            "photo_path": str(student_folder.relative_to(Path("."))),

            "address": None            "email": f"{student_id}@university.edu",

        })            "phone": None,

                    "address": None

        print(f"  {student_id} ... OK ({valid_images} images, FAISS: {faiss_idx})")        })

        processed_count += 1        

        print(f"✓ OK ({len(embeddings)} imgs, FAISS:{faiss_idx})")

print("\n" + "=" * 70)        processed_count += 1

print(f"Processing complete!")

print(f"  Successful: {processed_count}")print("\n" + "=" * 70)

print(f"  Failed: {error_count}")print(f"✅ Processing complete!")

print(f"  Total vectors: {vector_db.index.ntotal}")print(f"  - Successful: {processed_count}")

print("=" * 70)print(f"  - Failed: {error_count}")

print(f"  - Total vectors in FAISS: {vector_db.index.ntotal}")

# Step 4: Save FAISS indexprint("=" * 70)

print("\n6. Saving FAISS index...")

vector_db.save(# Step 4: Save FAISS index

    index_path="./data/faiss_index.bin",print("\n6. Saving FAISS index...")

    metadata_path="./data/faiss_metadata.json"vector_db.save(

)    index_path="./data/faiss_index.bin",

print("OK FAISS index saved")    metadata_path="./data/faiss_metadata.json"

)

# Step 5: Insert into databaseprint("✓ FAISS index saved")

print("\n7. Inserting students into database...")

inserted = 0# Step 5: Insert students into database

for student_data in students_data:print("\n7. Inserting students into database...")

    try:inserted = 0

        student = StudentDB.create_student(db, student_data)for student_data in students_data:

        inserted += 1    try:

    except Exception as e:        student = StudentDB.create_student(db, **student_data)

        print(f"Error inserting {student_data['student_id']}: {e}")        inserted += 1

    except Exception as e:

db.commit()        print(f"✗ Failed to insert {student_data['student_id']}: {e}")

print(f"OK Inserted {inserted} students")

db.commit()

print("\n" + "=" * 70)print(f"✓ Inserted {inserted} students into database")

print("REBUILD COMPLETE!")

print("=" * 70)print("\n" + "=" * 70)

print(f"\nFinal Summary:")print("✅ REBUILD COMPLETE!")

print(f"  Students in FAISS: {vector_db.index.ntotal}")print("=" * 70)

print(f"  Students in Database: {inserted}")print(f"\nSummary:")

print(f"  Structure: trainset/DEPT/STUDENT_ID/")print(f"  - Students in FAISS: {vector_db.index.ntotal}")

print("\nSystem ready!")print(f"  - Students in Database: {inserted}")

print(f"  - Department Structure: trainset/DEPT/STUDENT_ID/")
print("\n✅ System ready for identification with department-based structure!")
