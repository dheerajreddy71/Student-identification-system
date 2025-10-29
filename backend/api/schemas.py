"""
Pydantic schemas for API requests and responses
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class StudentBase(BaseModel):
    """Base student schema"""
    student_id: str = Field(..., description="Unique student identifier")
    name: str = Field(..., description="Student full name")
    department: str = Field(..., description="Department name")
    year: int = Field(..., ge=1, le=10, description="Year of study")
    roll_number: str = Field(..., description="Roll number")
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentCreate(StudentBase):
    """Schema for creating a new student"""
    pass


class StudentUpdate(BaseModel):
    """Schema for updating student information"""
    name: Optional[str] = None
    department: Optional[str] = None
    year: Optional[int] = Field(None, ge=1, le=10)
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class StudentResponse(StudentBase):
    """Schema for student response"""
    id: int
    faiss_index: int
    photo_path: Optional[str]
    registered_at: datetime
    updated_at: Optional[datetime]
    is_active: bool
    
    class Config:
        from_attributes = True


class PaginatedStudentsResponse(BaseModel):
    """Schema for paginated students response"""
    students: List[StudentResponse]
    total: int
    page: int
    limit: int
    total_pages: int


class IdentificationResult(BaseModel):
    """Schema for identification result"""
    success: bool
    student: Optional[StudentResponse] = None
    similarity: Optional[float] = None
    confidence: Optional[float] = None
    matches: Optional[List[Dict[str, Any]]] = None
    processing_time: float
    metrics: Dict[str, Any]


class VerificationResult(BaseModel):
    """Schema for verification result"""
    verified: bool
    student_id: str
    similarity: Optional[float] = None
    threshold: float
    processing_time: float


class RegistrationResponse(BaseModel):
    """Schema for registration response"""
    success: bool
    student: Optional[StudentResponse] = None
    message: str
    metrics: Dict[str, Any]


class UserLogin(BaseModel):
    """Schema for user login"""
    username: str
    password: str


class UserCreate(BaseModel):
    """Schema for creating new user"""
    username: str
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: str = "user"


class Token(BaseModel):
    """Schema for authentication token"""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data"""
    username: Optional[str] = None


class SystemStats(BaseModel):
    """Schema for system statistics"""
    total_students: int
    total_identifications: int
    success_rate: float
    average_latency: Dict[str, float]
    database_size: int


class IdentificationLogResponse(BaseModel):
    """Schema for identification log"""
    id: int
    student_id: Optional[str]
    similarity_score: Optional[float]
    success: bool
    total_time: float
    timestamp: datetime
    
    class Config:
        from_attributes = True
