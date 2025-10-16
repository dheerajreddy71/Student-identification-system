"""
Database models for student information and system logs
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from backend.config import Base
import datetime


class Student(Base):
    """Student information model"""
    __tablename__ = "students"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), unique=True, index=True, nullable=False)
    name = Column(String(200), nullable=False)
    department = Column(String(100), nullable=False)
    year = Column(Integer, nullable=False)
    roll_number = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(200))
    phone = Column(String(20))
    address = Column(Text)
    
    # Face data
    faiss_index = Column(Integer, unique=True, index=True, nullable=False)  # Position in FAISS index
    photo_path = Column(String(500))  # Original photo path
    embedding_hash = Column(String(64))  # Hash of embedding for verification
    
    # Metadata
    registered_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "name": self.name,
            "department": self.department,
            "year": self.year,
            "roll_number": self.roll_number,
            "email": self.email,
            "phone": self.phone,
            "address": self.address,
            "faiss_index": self.faiss_index,
            "photo_path": self.photo_path,
            "registered_at": self.registered_at.isoformat() if self.registered_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }


class IdentificationLog(Base):
    """Log of identification attempts"""
    __tablename__ = "identification_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String(50), index=True)  # Matched student (if any)
    similarity_score = Column(Float)
    threshold_used = Column(Float)
    success = Column(Boolean)
    query_image_path = Column(String(500))
    
    # Processing metrics
    preprocessing_time = Column(Float)  # seconds
    embedding_time = Column(Float)
    search_time = Column(Float)
    total_time = Column(Float)
    
    # Image quality metrics
    face_detected = Column(Boolean)
    face_confidence = Column(Float)
    image_quality_score = Column(Float)
    
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "student_id": self.student_id,
            "similarity_score": self.similarity_score,
            "threshold_used": self.threshold_used,
            "success": self.success,
            "query_image_path": self.query_image_path,
            "preprocessing_time": self.preprocessing_time,
            "embedding_time": self.embedding_time,
            "search_time": self.search_time,
            "total_time": self.total_time,
            "face_detected": self.face_detected,
            "face_confidence": self.face_confidence,
            "image_quality_score": self.image_quality_score,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None
        }


class SystemMetrics(Base):
    """System performance metrics"""
    __tablename__ = "system_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_type = Column(String(50), index=True)  # 'accuracy', 'latency', 'throughput'
    metric_value = Column(Float)
    metric_unit = Column(String(20))  # 's', 'ms', '%', 'count'
    metric_metadata = Column(JSON)  # Additional context (renamed from metadata to avoid SQLAlchemy conflict)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())


class User(Base):
    """System users for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    email = Column(String(200), unique=True, index=True)
    hashed_password = Column(String(200), nullable=False)
    full_name = Column(String(200))
    role = Column(String(50), default="user")  # 'admin', 'user', 'viewer'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True))
