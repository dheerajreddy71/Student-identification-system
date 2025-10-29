"""
FastAPI main application
"""
from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import cv2
import numpy as np
from typing import List, Optional
import io
from PIL import Image
import os
from datetime import datetime

from backend.config import get_db, settings, Base, engine
from backend.api import schemas
from backend.database.operations import StudentDB, IdentificationLogDB, UserDB, SystemMetricsDB
from backend.database.models import Student
from backend.services.preprocessing_pipeline import create_pipeline
from backend.utils.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    decode_access_token
)
from backend.utils.photo_validator import PhotoValidator
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Create database tables
Base.metadata.create_all(bind=engine)

# Initialize FastAPI app
app = FastAPI(
    title="Student Identification System",
    description="AI-Powered Student Identification using GFPGAN + AdaFace + FAISS",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipelines (lazy loading for memory efficiency)
preprocessing_pipeline = None
recognition_pipeline = None
security = HTTPBearer()


def get_pipelines():
    """Get or initialize pipelines (lazy loaded to reduce startup memory)"""
    global preprocessing_pipeline, recognition_pipeline
    
    if preprocessing_pipeline is None or recognition_pipeline is None:
        import gc
        gc.collect()  # Clear memory before loading heavy models
        
        preprocessing_pipeline, recognition_pipeline = create_pipeline(
            device=settings.device
        )
    
    return preprocessing_pipeline, recognition_pipeline


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security),
                    db: Session = Depends(get_db)):
    """Verify JWT token and get current user"""
    token = credentials.credentials
    payload = decode_access_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = UserDB.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user


def load_image_from_upload(upload_file: UploadFile) -> np.ndarray:
    """Load image from uploaded file"""
    contents = upload_file.file.read()
    nparr = np.frombuffer(contents, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    if image is None:
        raise HTTPException(status_code=400, detail="Invalid image file")
    
    return image


# ============= Health Check =============

@app.get("/")
@app.get("/health")
def health_check():
    """Health check endpoint for deployment monitoring"""
    return {
        "status": "healthy",
        "service": "Student Identification System",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


# ============= Authentication Endpoints =============

@app.post("/api/auth/register", response_model=schemas.Token)
def register_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if username exists
    existing_user = UserDB.get_user_by_username(db, user.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    UserDB.create_user(
        db,
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        full_name=user.full_name,
        role=user.role
    )
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/api/auth/login", response_model=schemas.Token)
def login(user_login: schemas.UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = UserDB.get_user_by_username(db, user_login.username)
    
    if not user or not verify_password(user_login.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )
    
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    
    # Update last login
    UserDB.update_last_login(db, user_login.username)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.username})
    
    return {"access_token": access_token, "token_type": "bearer"}


# ============= Student Management Endpoints =============

@app.post("/api/students/register", response_model=schemas.RegistrationResponse)
async def register_student(
    student_id: str = Form(...),
    name: str = Form(...),
    department: str = Form(...),
    year: int = Form(...),
    roll_number: str = Form(...),
    email: Optional[str] = Form(None),
    phone: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    photos: List[UploadFile] = File(..., description="Multiple photos of the student"),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Register a new student with multiple photos"""
    
    # Check if student already exists
    existing = StudentDB.get_student_by_id(db, student_id)
    if existing:
        raise HTTPException(status_code=400, detail="Student ID already registered")
    
    existing_roll = StudentDB.get_student_by_roll(db, roll_number)
    if existing_roll:
        raise HTTPException(status_code=400, detail="Roll number already registered")
    
    # Validate we have at least one photo
    if not photos or len(photos) == 0:
        raise HTTPException(status_code=400, detail="At least one photo is required")
    
    # Initialize photo validator
    photo_validator = PhotoValidator(device=settings.device)
    
    # Validate first photo quality before processing
    first_photo_bytes = photos[0].file.read()
    photos[0].file.seek(0)
    
    # Save to temp file for validation
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
        tmp.write(first_photo_bytes)
        tmp_path = tmp.name
    
    try:
        is_valid, message, details = photo_validator.validate_photo(tmp_path)
        
        if not is_valid:
            # Return validation failure with recommendations
            recommendations = photo_validator.get_recommendations(details)
            raise HTTPException(
                status_code=400, 
                detail=f"{message}\n\nRecommendations:\n{recommendations}"
            )
        
        print(f"✅ Photo validation passed: {message}")
        
    finally:
        # Clean up temp file
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)
    
    # Get pipelines
    preprocessing, recognition = get_pipelines()
    
    # Process all photos and extract embeddings
    embeddings = []
    saved_photo_paths = []
    all_metrics = []
    
    for idx, photo in enumerate(photos):
        # Read file contents
        file_contents = photo.file.read()
        photo.file.seek(0)
        
        # Load image from bytes
        nparr = np.frombuffer(file_contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            continue  # Skip invalid images
        
        # Extract embedding
        embedding, metrics = preprocessing.extract_embedding(image, enhance=True)
        
        if embedding is not None:
            embeddings.append(embedding)
            all_metrics.append(metrics)
            
            # Save photo in trainset with department structure
            photo_path = save_uploaded_file(photo, student_id, department, file_contents, idx + 1)
            saved_photo_paths.append(photo_path)
    
    # Check if we got at least one valid embedding
    if not embeddings:
        return schemas.RegistrationResponse(
            success=False,
            student=None,
            message="No face detected in any of the photos",
            metrics=all_metrics[0] if all_metrics else {}
        )
    
    # Average embeddings from multiple photos for robust representation
    final_embedding = np.mean(embeddings, axis=0) if len(embeddings) > 1 else embeddings[0]
    
    # Normalize embedding
    final_embedding = final_embedding / np.linalg.norm(final_embedding)
    
    # Add to FAISS
    vector_db = recognition.vector_db
    faiss_idx = vector_db.add_embedding(
        final_embedding,  # Use averaged embedding
        student_id,
        metadata={
            "name": name,
            "department": department,
            "year": year,
            "roll_number": roll_number
        }
    )
    
    # Save to database (store first photo path as primary)
    student_data = {
        "student_id": student_id,
        "name": name,
        "department": department,
        "year": year,
        "roll_number": roll_number,
        "email": email,
        "phone": phone,
        "address": address,
        "faiss_index": faiss_idx,
        "photo_path": saved_photo_paths[0] if saved_photo_paths else f"trainset/{department}/{student_id}"
    }
    
    student = StudentDB.create_student(db, student_data)
    
    # Save FAISS index
    vector_db.save()
    
    # Prepare success message
    success_message = f"Student registered successfully with {len(embeddings)} photo(s)"
    
    return schemas.RegistrationResponse(
        success=True,
        student=schemas.StudentResponse.model_validate(student),
        message=success_message,
        metrics=all_metrics[0] if all_metrics else {}
    )


@app.post("/api/students/identify", response_model=schemas.IdentificationResult)
async def identify_student(
    photo: UploadFile = File(...),
    enhance: bool = Form(True),
    top_k: int = Form(5),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Identify a student from photo"""
    # Initialize safe default result that will always be a valid dict
    result = {
        'success': False,
        'metrics': {},
        'total_time': 0.0,
        'matches': [],
        'best_match': None
    }
    
    try:
        start_time = datetime.utcnow()
        
        # Load image
        image = load_image_from_upload(photo)
        
        # Get pipelines
        _, recognition = get_pipelines()
        
        if recognition is None:
            result['error'] = "Recognition pipeline not initialized"
        else:
            # Identify with comprehensive error handling
            try:
                identification_result = recognition.identify_student(image, enhance=enhance, top_k=top_k)
                
                if identification_result is not None and isinstance(identification_result, dict):
                    # Update result with valid identification result
                    result.update(identification_result)
                else:
                    result['error'] = "Invalid identification result"
                    
            except Exception as e:
                print(f"Error in recognition.identify_student: {e}")
                result['error'] = f'Identification failed: {str(e)}'
        
    except Exception as e:
        print(f"Fatal error in identify_student endpoint: {e}")
        result['error'] = f'Endpoint error: {str(e)}'
    
    # Get student details if identified (with safe access)
    student_response = None
    try:
        if result.get('success') and result.get('best_match'):
            best_match = result.get('best_match')
            if isinstance(best_match, dict) and 'student_id' in best_match:
                student_id = best_match['student_id']
                if student_id:
                    student = StudentDB.get_student_by_id(db, student_id)
                    if student:
                        student_response = schemas.StudentResponse.model_validate(student)
    except Exception as e:
        print(f"Error getting student details: {e}")
    
    # Calculate total processing time
    end_time = datetime.utcnow()
    total_time = (end_time - start_time).total_seconds()
    
    # Log the identification attempt
    try:
        metrics = result.get('metrics', {})
        best_match = result.get('best_match') or {}
        
        log_data = {
            'student_id': best_match.get('student_id') if isinstance(best_match, dict) else None,
            'success': result.get('success', False),
            'similarity_score': best_match.get('similarity') if isinstance(best_match, dict) else None,
            'threshold_used': 0.45,  # Default threshold
            'preprocessing_time': metrics.get('preprocessing_time', 0.0),
            'embedding_time': metrics.get('embedding_time', 0.0),
            'search_time': metrics.get('search_time', 0.0),
            'total_time': total_time,
            'face_detected': metrics.get('face_detected', False),
            'face_confidence': metrics.get('face_confidence', 0.0),
            'image_quality_score': metrics.get('image_quality', 0.0)
        }
        IdentificationLogDB.create_log(db, log_data)
    except Exception as e:
        print(f"Error creating identification log: {e}")
    
    # Create safe response with guaranteed valid values
    try:
        best_match = result.get('best_match') or {}
        similarity = best_match.get('similarity') if isinstance(best_match, dict) else None
        
        return schemas.IdentificationResult(
            success=result.get('success', False),
            student=student_response,
            similarity=similarity,
            confidence=similarity,
            matches=result.get('matches', []),
            processing_time=result.get('total_time', 0.0),
            metrics=result.get('metrics', {})
        )
    except Exception as e:
        print(f"Error creating response: {e}")
        # Fallback response that should never fail
        return schemas.IdentificationResult(
            success=False,
            student=None,
            similarity=None,
            confidence=None,
            matches=[],
            processing_time=0.0,
            metrics={"error": str(e)}
        )


@app.get("/api/students", response_model=schemas.PaginatedStudentsResponse)
def list_students(
    page: int = 1,
    limit: int = 50,
    search: str = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all students with pagination and search"""
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get students with search if provided
    if search:
        students = StudentDB.search_students(db, search)
        total = len(students)
        # Apply pagination to search results
        students = students[skip:skip + limit]
    else:
        total = StudentDB.count_students(db)
        students = StudentDB.get_all_students(db, skip=skip, limit=limit)
    
    # Calculate pagination info
    total_pages = (total + limit - 1) // limit  # Ceiling division
    
    return schemas.PaginatedStudentsResponse(
        students=[schemas.StudentResponse.model_validate(s) for s in students],
        total=total,
        page=page,
        limit=limit,
        total_pages=total_pages
    )


@app.get("/api/students/{student_id}", response_model=schemas.StudentResponse)
def get_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get student details"""
    student = StudentDB.get_student_by_id(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return schemas.StudentResponse.model_validate(student)


@app.put("/api/students/{student_id}", response_model=schemas.StudentResponse)
def update_student(
    student_id: str,
    student_update: schemas.StudentUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update student information"""
    update_data = student_update.model_dump(exclude_unset=True)
    student = StudentDB.update_student(db, student_id, update_data)
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return schemas.StudentResponse.model_validate(student)


@app.delete("/api/students/{student_id}")
def delete_student(
    student_id: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete student (soft delete)"""
    success = StudentDB.delete_student(db, student_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {"message": "Student deleted successfully"}


# ============= Statistics Endpoints =============

@app.get("/api/stats", response_model=schemas.SystemStats)
def get_system_stats(db: Session = Depends(get_db), current_user = Depends(get_current_user)):
    """Get system statistics"""
    from backend.database.models import IdentificationLog
    
    total_students = StudentDB.count_students(db)
    success_rate = IdentificationLogDB.get_success_rate(db, hours=24)
    avg_latency = IdentificationLogDB.get_average_latency(db, hours=24)
    
    _, recognition = get_pipelines()
    db_stats = recognition.vector_db.get_statistics()
    
    return schemas.SystemStats(
        total_students=total_students,
        total_identifications=db.query(IdentificationLog).count(),
        success_rate=success_rate,
        average_latency=avg_latency,
        database_size=db_stats['total_vectors']
    )


@app.get("/api/logs", response_model=List[schemas.IdentificationLogResponse])
def get_identification_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent identification logs"""
    logs = IdentificationLogDB.get_recent_logs(db, limit=limit)
    return [schemas.IdentificationLogResponse.model_validate(log) for log in logs]


@app.delete("/api/logs/{log_id}")
def delete_identification_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a specific identification log"""
    from backend.database.models import IdentificationLog
    
    log = db.query(IdentificationLog).filter(IdentificationLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")
    
    db.delete(log)
    db.commit()
    return {"message": "Log deleted successfully"}


@app.delete("/api/logs")
def delete_all_logs(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete all identification logs"""
    from backend.database.models import IdentificationLog
    
    count = db.query(IdentificationLog).delete()
    db.commit()
    return {"message": f"Deleted {count} log(s) successfully"}


# ============= Utility Functions =============

def save_uploaded_file(upload_file: UploadFile, student_id: str, department: str, file_contents: bytes, photo_index: int = 1) -> str:
    """
    Save uploaded file in trainset with department structure
    Format: trainset/DEPARTMENT/STUDENT_ID/STUDENT_ID_N.jpg
    """
    # Create directory structure: trainset/DEPT/STUDENT_ID/
    student_dir = os.path.join("trainset", department, student_id)
    os.makedirs(student_dir, exist_ok=True)
    
    # Save with format: STUDENT_ID_1.jpg, STUDENT_ID_2.jpg, etc.
    file_path = os.path.join(student_dir, f"{student_id}_{photo_index}.jpg")
    
    with open(file_path, "wb") as f:
        f.write(file_contents)
    
    return file_path


# ============= Health Check =============

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
